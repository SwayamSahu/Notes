# src/email_assistant/email_assistant_hitl_memory_outlook.py
"""Outlook-integrated Email Assistant with Human-in-the-Loop and Memory.

This module implements a sophisticated email assistant agent that:

1. **Triage Stage**: Analyzes incoming emails to classify them as:
   - "respond": Emails that need a response
   - "ignore": Spam, marketing, or irrelevant emails
   - "notify": Important emails that need human review

2. **Response Stage**: Generates appropriate responses using AI:
   - Drafts emails, calendar invitations, or questions
   - Integrates with Microsoft Graph API for real email processing
   - Uses memory to learn from user feedback

3. **Human-in-the-Loop (HITL)**: Allows users to:
   - Review and approve generated responses before sending
   - Edit drafts before they're sent
   - Provide feedback that improves future responses
   - Ignore suggestions and update preferences

4. **Memory System**: Learns from user interactions:
   - Triage preferences: What types of emails to respond to
   - Response preferences: How to write emails
   - Calendar preferences: Meeting scheduling patterns

The workflow uses LangGraph to orchestrate the multi-step process, storing intermediate
states and allowing interrupts for human feedback.
"""

from typing import Literal

from langchain.chat_models import init_chat_model

from langgraph.graph import StateGraph, START, END
from langgraph.store.base import BaseStore
from langgraph.types import interrupt, Command

from email_assistant.tools import get_tools, get_tools_by_name
from email_assistant.tools.outlook.prompt_templates import OUTLOOK_TOOLS_PROMPT
from email_assistant.tools.outlook.outlook_tools import mark_as_read
from email_assistant.prompts import (
    triage_system_prompt,
    triage_user_prompt,
    agent_system_prompt_hitl_memory,
    default_triage_instructions,
    default_background,
    default_response_preferences,
    default_cal_preferences,
    MEMORY_UPDATE_INSTRUCTIONS,
    MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT,
)
from email_assistant.schemas import State, RouterSchema, StateInput, UserPreferences
from email_assistant.utils import parse_outlook, format_for_display, format_outlook_markdown
from dotenv import load_dotenv

load_dotenv(".env")

# ============================================================================
# Tool and Model Initialization
# ============================================================================

# Get tools with Outlook tools
# This includes: send_email_tool, schedule_meeting_tool, check_calendar_tool, Question (ask user), and Done
tools = get_tools(
    ["send_email_tool", "schedule_meeting_tool", "check_calendar_tool", "Question", "Done"],
    include_outlook=True,
)
tools_by_name = get_tools_by_name(tools)

# Initialize the LLM for use with router / structured output
# Temperature 0.0 ensures deterministic responses
llm = init_chat_model("openai:gpt-4.1", temperature=0.0)
llm_router = llm.with_structured_output(RouterSchema)

# Initialize the LLM, enforcing tool use (of any available tools) for agent
# bind_tools ensures the LLM will call one of the available tools
llm = init_chat_model("openai:gpt-4.1", temperature=0.0)
llm_with_tools = llm.bind_tools(tools, tool_choice="required")

# ============================================================================
# Memory Management Functions
# ============================================================================

def get_memory(store, namespace, default_content=None):
    """
    Retrieve memory from the store or initialize with default if it doesn't exist.
    
    This function implements a "lazy initialization" pattern - if memory hasn't been
    stored yet, it creates it with sensible defaults. This allows the agent to learn
    and improve as it interacts with users.
    
    Args:
        store: LangGraph BaseStore instance to search for existing memory
        namespace: Tuple defining the memory namespace, e.g. ("email_assistant", "triage_preferences")
        default_content: Default content to use if memory doesn't exist
        
    Returns:
        str: The content of the memory profile, either from existing memory or the default
    """
    # Search for existing memory with namespace and key
    user_preferences = store.get(namespace, "user_preferences")
    
    # If memory exists, return its content (the value)
    if user_preferences:
        return user_preferences.value
    
    # If memory doesn't exist, add it to the store and return the default content
    else:
        # Namespace, key, value
        store.put(namespace, "user_preferences", default_content)
        user_preferences = default_content
    
    # Return the default content
    return user_preferences 

def update_memory(store, namespace, messages):
    """
    Update memory profile in the store based on user feedback.
    
    This function allows the agent to "learn" from user interactions. When a user
    edits a response, ignores a suggestion, or provides feedback, this function
    updates the stored preferences so future responses are better aligned with
    user preferences.
    
    Args:
        store: LangGraph BaseStore instance to update memory
        namespace: Tuple defining the memory namespace, e.g. ("email_assistant", "triage_preferences")
        messages: List of messages to update the memory with (usually includes user feedback)
    """

    # Get the existing memory
    user_preferences = store.get(namespace, "user_preferences")
    
    # Initialize LLM with structured output for updating preferences
    # This ensures the updated memory is well-structured and consistent
    llm = init_chat_model("openai:gpt-4.1", temperature=0.0).with_structured_output(UserPreferences)
    
    # Call the LLM to intelligently update the memory based on the feedback messages
    # The MEMORY_UPDATE_INSTRUCTIONS tells the LLM how to incorporate user feedback
    result = llm.invoke(
        [
            {"role": "system", "content": MEMORY_UPDATE_INSTRUCTIONS.format(current_profile=user_preferences.value, namespace=namespace)},
        ] + messages
    )
    
    # Save the updated memory to the store for future use
    store.put(namespace, "user_preferences", result.user_preferences)


# ============================================================================
# Workflow Nodes (LangGraph Steps)
# ============================================================================

def triage_router(state: State, store: BaseStore) -> Command[Literal["triage_interrupt_handler", "response_agent", "__end__"]]:
    """
    First step: Analyze email content to decide if we should respond, notify, or ignore.

    The triage step prevents the assistant from wasting time on:
    - Marketing emails and spam
    - Company-wide announcements
    - Messages meant for other teams
    
    This uses the user's learned triage preferences to make more accurate decisions over time.
    
    Returns:
        Command directing the workflow to:
        - "response_agent": If the email needs a response
        - "triage_interrupt_handler": If the email needs human review
        - "__end__": If the email should be ignored
    """
    
    # Parse the email input
    author, to, subject, email_thread, email_id = parse_outlook(state["email_input"])
    user_prompt = triage_user_prompt.format(
        author=author, to=to, subject=subject, email_thread=email_thread
    )

    # Create email markdown for Agent Inbox in case of notification  
    email_markdown = format_outlook_markdown(subject, author, to, email_thread, email_id)

    # Search for existing triage_preferences memory (or use defaults if none exist)
    triage_instructions = get_memory(store, ("email_assistant", "triage_preferences"), default_triage_instructions)

    # Format system prompt with background and triage instructions
    system_prompt = triage_system_prompt.format(
        background=default_background,
        triage_instructions=triage_instructions,
    )

    # Run the router LLM - it will classify the email
    result = llm_router.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )

    # Decision
    classification = result.classification

    # Process the classification decision
    if classification == "respond":
        print("📧 Classification: RESPOND - This email requires a response")
        # Next node
        goto = "response_agent"
        # Update the state
        update = {
            "classification_decision": result.classification,
            "messages": [{"role": "user",
                            "content": f"Respond to the email: {email_markdown}"
                        }],
        }
        
    elif classification == "ignore":
        print("🚫 Classification: IGNORE - This email can be safely ignored")

        # Next node
        goto = END
        # Update the state
        update = {
            "classification_decision": classification,
        }

    elif classification == "notify":
        print("🔔 Classification: NOTIFY - This email contains important information") 

        # Next node
        goto = "triage_interrupt_handler"
        # Update the state
        update = {
            "classification_decision": classification,
        }

    else:
        raise ValueError(f"Invalid classification: {classification}")
    
    return Command(goto=goto, update=update)

def triage_interrupt_handler(state: State, store: BaseStore) -> Command[Literal["response_agent", "__end__"]]:
    """
    Handle emails classified as "notify" by interrupting the workflow for human review.
    
    This node sends the email to the Agent Inbox for human review and waits for feedback.
    The human can decide to:
    - "response": Respond to the email with custom feedback
    - "ignore": Ignore the email and update preferences to avoid similar emails
    
    Returns:
        Command directing to either response_agent or END based on human decision
    """
    
    # Parse the email input
    author, to, subject, email_thread, email_id = parse_outlook(state["email_input"])

    # Create email markdown for Agent Inbox in case of notification  
    email_markdown = format_outlook_markdown(subject, author, to, email_thread, email_id)

    # Create messages
    messages = [{"role": "user",
                "content": f"Email to notify user about: {email_markdown}"
                }]

    # Create interrupt request for Agent Inbox
    # This allows the human to see the email and decide what to do
    request = {
        "action_request": {
            "action": f"Email Assistant: {state['classification_decision']}",
            "args": {}
        },
        "config": {
            "allow_ignore": True,  # User can ignore the email
            "allow_respond": True,  # User can respond to the email
            "allow_edit": False,   # User can't edit at this stage
            "allow_accept": False, # No pre-generated action to accept
        },
        # Email to show in Agent Inbox
        "description": email_markdown,
    }

    # Send to Agent Inbox and wait for response
    # This is a blocking call - execution pauses until the human responds
    response = interrupt([request])[0]

    # If user provides feedback, go to response agent and use feedback to respond to email   
    if response["type"] == "response":
        # Add feedback to messages 
        user_input = response["args"]
        messages.append({"role": "user",
                        "content": f"User wants to reply to the email. Use this feedback to respond: {user_input}"
                        })
        # Update memory with feedback
        update_memory(store, ("email_assistant", "triage_preferences"), [{
            "role": "user",
            "content": f"The user decided to respond to the email, so update the triage preferences to capture this."
        }] + messages)

        goto = "response_agent"

    # If user ignores email, go to END
    elif response["type"] == "ignore":
        # Make note of the user's decision to ignore the email
        messages.append({"role": "user",
                        "content": f"The user decided to ignore the email even though it was classified as notify. Update triage preferences to capture this."
                        })
        # Update memory with feedback 
        update_memory(store, ("email_assistant", "triage_preferences"), messages)
        goto = END

    # Catch all other responses
    else:
        raise ValueError(f"Invalid response: {response}")

    # Update the state 
    update = {
        "messages": messages,
    }

    return Command(goto=goto, update=update)

def llm_call(state: State, store: BaseStore):
    """
    Call the LLM to generate a response to the email.
    
    This node uses the full LLM with all available tools. The LLM will decide
    which tool to use (send_email, schedule_meeting, question, etc.) based on
    the email content and the user's preferences stored in memory.
    
    Returns:
        Updated state with the LLM's response (which includes tool calls)
    """
    
    # Search for existing cal_preferences memory (or use defaults)
    cal_preferences = get_memory(store, ("email_assistant", "cal_preferences"), default_cal_preferences)
    
    # Search for existing response_preferences memory (or use defaults)
    response_preferences = get_memory(store, ("email_assistant", "response_preferences"), default_response_preferences)

    # Call the LLM with all tools available
    # The LLM will generate a response with tool calls if needed
    return {
        "messages": [
            llm_with_tools.invoke(
                [
                    {"role": "system", "content": agent_system_prompt_hitl_memory.format(
                        tools_prompt=OUTLOOK_TOOLS_PROMPT,
                        background=default_background,
                        response_preferences=response_preferences,  # Learned email writing style
                        cal_preferences=cal_preferences  # Learned calendar preferences
                    )}
                ]
                + state["messages"]
            )
        ]
    }
    
def interrupt_handler(state: State, store: BaseStore) -> Command[Literal["llm_call", "__end__"]]:
    """
    Handle tool calls by interrupting for human review and approval.
    
    This is the core of the human-in-the-loop functionality. Before executing
    critical actions (sending emails, scheduling meetings), we send them to
    the Agent Inbox for human approval. The human can:
    - "accept": Execute the action as-is
    - "edit": Modify the action before execution
    - "ignore": Don't execute this action
    - "response": Provide feedback to improve future actions
    
    Returns:
        Command with tool execution results or feedback messages
    """
    
    # Store messages
    result = []

    # Go to the LLM call node next
    goto = "llm_call"

    # Iterate over the tool calls in the last message
    # (the LLM may have generated multiple tool calls)
    for tool_call in state["messages"][-1].tool_calls:
        
        # Allowed tools for HITL
        # These tools require human approval before execution
        hitl_tools = ["send_email_tool", "schedule_meeting_tool", "Question"]
        
        # If tool is not in our HITL list, execute it directly without interruption
        # (e.g., check_calendar_tool is safe to run without review)
        if tool_call["name"] not in hitl_tools:

            # Execute search_memory and other tools without interruption
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append({"role": "tool", "content": observation, "tool_call_id": tool_call["id"]})
            continue
            
        # Get original email from email_input in state
        # This provides context in the Agent Inbox
        email_input = state["email_input"]
        author, to, subject, email_thread, email_id = parse_outlook(email_input)
        original_email_markdown = format_outlook_markdown(subject, author, to, email_thread, email_id)
        
        # Format tool call for display and prepend the original email
        tool_display = format_for_display(tool_call)
        description = original_email_markdown + tool_display

        # Configure what actions are allowed in Agent Inbox based on the tool
        if tool_call["name"] == "send_email_tool":
            config = {
                "allow_ignore": True,  # User can ignore the draft
                "allow_respond": True,  # User can provide feedback
                "allow_edit": True,  # User can edit before sending
                "allow_accept": True,  # User can approve and send
            }
        elif tool_call["name"] == "schedule_meeting_tool":
            config = {
                "allow_ignore": True,
                "allow_respond": True,
                "allow_edit": True,
                "allow_accept": True,
            }
        elif tool_call["name"] == "Question":
            config = {
                "allow_ignore": True,
                "allow_respond": True,  # User provides answer to the question
                "allow_edit": False,  # Can't edit a question
                "allow_accept": False,  # No action to accept
            }
        else:
            raise ValueError(f"Invalid tool call: {tool_call['name']}")

        # Create the interrupt request for Agent Inbox
        request = {
            "action_request": {
                "action": tool_call["name"],
                "args": tool_call["args"]
            },
            "config": config,
            "description": description,
        }

        # Send to Agent Inbox and wait for response
        # Execution pauses here until the human responds
        response = interrupt([request])[0]

        # Handle the responses 
        if response["type"] == "accept":

            # Execute the tool with original args
            tool = tools_by_name[tool_call["name"]]
            observation = tool.invoke(tool_call["args"])
            result.append({"role": "tool", "content": observation, "tool_call_id": tool_call["id"]})
                        
        elif response["type"] == "edit":

            # Tool selection 
            tool = tools_by_name[tool_call["name"]]
            initial_tool_call = tool_call["args"]
            
            # Get edited args from Agent Inbox
            edited_args = response["args"]["args"]

            # Update the AI message's tool call with edited content (reference to the message in the state)
            ai_message = state["messages"][-1] # Get the most recent message from the state
            current_id = tool_call["id"] # Store the ID of the tool call being edited
            
            # Create a new list of tool calls by filtering out the one being edited and adding the updated version
            # This avoids modifying the original list directly (immutable approach)
            updated_tool_calls = [tc for tc in ai_message.tool_calls if tc["id"] != current_id] + [
                {"type": "tool_call", "name": tool_call["name"], "args": edited_args, "id": current_id}
            ]

            # Create a new copy of the message with updated tool calls rather than modifying the original
            # This ensures state immutability and prevents side effects in other parts of the code
            result.append(ai_message.model_copy(update={"tool_calls": updated_tool_calls}))

            # Save feedback in memory and update the write_email tool call with the edited content from Agent Inbox
            if tool_call["name"] == "send_email_tool":
                
                # Execute the tool with edited args
                observation = tool.invoke(edited_args)
                
                # Add only the tool response message
                result.append({"role": "tool", "content": observation, "tool_call_id": current_id})

                # This is new: update the memory with user's edit preferences
                # This helps the LLM learn to write emails more like the user's style
                update_memory(store, ("email_assistant", "response_preferences"), [{
                    "role": "user",
                    "content": f"User edited the email response. Here is the initial email generated by the assistant: {initial_tool_call}. Here is the edited email: {edited_args}. Follow all instructions above, and remember: {MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT}."
                }])
            
            # Save feedback in memory and update the schedule_meeting tool call with the edited content from Agent Inbox
            elif tool_call["name"] == "schedule_meeting_tool":
                
                # Execute the tool with edited args
                observation = tool.invoke(edited_args)
                
                # Add only the tool response message
                result.append({"role": "tool", "content": observation, "tool_call_id": current_id})

                # This is new: update the memory with user's calendar preferences
                # This helps the LLM learn to schedule meetings more like the user's style
                update_memory(store, ("email_assistant", "cal_preferences"), [{
                    "role": "user",
                    "content": f"User edited the calendar invitation. Here is the initial calendar invitation generated by the assistant: {initial_tool_call}. Here is the edited calendar invitation: {edited_args}. Follow all instructions above, and remember: {MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT}."
                }])
            
            # Catch all other tool calls
            else:
                raise ValueError(f"Invalid tool call: {tool_call['name']}")

        elif response["type"] == "ignore":

            if tool_call["name"] == "send_email_tool":
                # Don't execute the tool, and tell the agent how to proceed
                result.append({"role": "tool", "content": "User ignored this email draft. Ignore this email and end the workflow.", "tool_call_id": tool_call["id"]})
                # Go to END
                goto = END
                # This is new: update the memory with user's decision to ignore
                # This helps the LLM improve triage - it learns what emails NOT to respond to
                update_memory(store, ("email_assistant", "triage_preferences"), state["messages"] + result + [{
                    "role": "user",
                    "content": f"The user ignored the email draft. That means they did not want to respond to the email. Update the triage preferences to ensure emails of this type are not classified as respond. Follow all instructions above, and remember: {MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT}."
                }])

            elif tool_call["name"] == "schedule_meeting_tool":
                # Don't execute the tool, and tell the agent how to proceed
                result.append({"role": "tool", "content": "User ignored this calendar meeting draft. Ignore this email and end the workflow.", "tool_call_id": tool_call["id"]})
                # Go to END
                goto = END
                # This is new: update the memory with user's decision to ignore
                update_memory(store, ("email_assistant", "triage_preferences"), state["messages"] + result + [{
                    "role": "user",
                    "content": f"The user ignored the calendar meeting draft. That means they did not want to schedule a meeting for this email. Update the triage preferences to ensure emails of this type are not classified as respond. Follow all instructions above, and remember: {MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT}."
                }])

            elif tool_call["name"] == "Question":
                # Don't execute the tool, and tell the agent how to proceed
                result.append({"role": "tool", "content": "User ignored this question. Ignore this email and end the workflow.", "tool_call_id": tool_call["id"]})
                # Go to END
                goto = END
                # This is new: update the memory with user's decision to ignore
                update_memory(store, ("email_assistant", "triage_preferences"), state["messages"] + result + [{
                    "role": "user",
                    "content": f"The user ignored the Question. That means they did not want to answer the question or deal with this email. Update the triage preferences to ensure emails of this type are not classified as respond. Follow all instructions above, and remember: {MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT}."
                }])

            else:
                raise ValueError(f"Invalid tool call: {tool_call['name']}")

        elif response["type"] == "response":
            # User provided feedback
            user_feedback = response["args"]
            if tool_call["name"] == "send_email_tool":
                # Don't execute the tool, and add a message with the user feedback to incorporate into the email
                result.append({"role": "tool", "content": f"User gave feedback, which can we incorporate into the email. Feedback: {user_feedback}", "tool_call_id": tool_call["id"]})
                # This is new: update the memory with user's feedback
                # This helps improve future email drafts
                update_memory(store, ("email_assistant", "response_preferences"), state["messages"] + result + [{
                    "role": "user",
                    "content": f"User gave feedback, which we can use to update the response preferences. Follow all instructions above, and remember: {MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT}."
                }])

            elif tool_call["name"] == "schedule_meeting_tool":
                # Don't execute the tool, and add a message with the user feedback to incorporate into the email
                result.append({"role": "tool", "content": f"User gave feedback, which can we incorporate into the meeting request. Feedback: {user_feedback}", "tool_call_id": tool_call["id"]})
                # This is new: update the memory with user's feedback
                # This helps improve future meeting scheduling
                update_memory(store, ("email_assistant", "cal_preferences"), state["messages"] + result + [{
                    "role": "user",
                    "content": f"User gave feedback, which we can use to update the calendar preferences. Follow all instructions above, and remember: {MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT}."
                }])

            elif tool_call["name"] == "Question":
                # Don't execute the tool, and add a message with the user feedback to incorporate into the email
                result.append({"role": "tool", "content": f"User answered the question, which can we can use for any follow up actions. Feedback: {user_feedback}", "tool_call_id": tool_call["id"]})

            else:
                raise ValueError(f"Invalid tool call: {tool_call['name']}")

    # Update the state 
    update = {
        "messages": result,
    }

    return Command(goto=goto, update=update)

# Conditional edge function
def should_continue(state: State, store: BaseStore) -> Literal["interrupt_handler", "mark_as_read_node"]:
    """
    Route to tool handler, or mark as read if Done tool was called.
    
    This conditional logic determines whether to:
    - "interrupt_handler": Process the next tool call (may loop multiple times)
    - "mark_as_read_node": End the workflow (Done tool was called)
    """
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        for tool_call in last_message.tool_calls: 
            if tool_call["name"] == "Done":
                # TODO: Here, we could update the background memory with the email-response for follow up actions. 
                return "mark_as_read_node"
            else:
                return "interrupt_handler"

def mark_as_read_node(state: State):
    """Mark the processed email as read in Outlook."""
    email_input = state["email_input"]
    author, to, subject, email_thread, email_id = parse_outlook(email_input)
    mark_as_read(email_id)

# ============================================================================
# Build the Response Agent Workflow
# ============================================================================

# Build workflow
agent_builder = StateGraph(State)

# Add nodes - with store parameter
agent_builder.add_node("llm_call", llm_call)
agent_builder.add_node("interrupt_handler", interrupt_handler)
agent_builder.add_node("mark_as_read_node", mark_as_read_node)

# Add edges
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges(
    "llm_call",
    should_continue,
    {
        "interrupt_handler": "interrupt_handler",
        "mark_as_read_node": "mark_as_read_node",
    },
)
agent_builder.add_edge("interrupt_handler", "llm_call")  # Loop back for ReAct
agent_builder.add_edge("mark_as_read_node", END)

# Compile the agent
response_agent = agent_builder.compile()


# ============================================================================
# Build the Overall Workflow
# ============================================================================

# Build overall workflow with store and checkpointer
# This is the main entry point for processing emails
overall_workflow = StateGraph(State, input=StateInput)

overall_workflow.add_node("triage_router", triage_router)
overall_workflow.add_node("triage_interrupt_handler", triage_interrupt_handler)
overall_workflow.add_node("response_agent", response_agent)
overall_workflow.add_node("mark_as_read_node", mark_as_read_node)

overall_workflow.add_edge(START, "triage_router")
overall_workflow.add_edge("mark_as_read_node", END)


# Compile the final email assistant workflow
# This is the entry point for using the assistant
email_assistant = overall_workflow.compile()





# """Outlook-integrated Email Assistant with Human-in-the-Loop and Memory.

# This module mirrors the Gmail assistant but integrates with Microsoft Graph
# for Outlook Mail and Calendar.

# Features:
# - Triage classification (respond / ignore / notify)
# - AI response generation
# - Calendar scheduling
# - Human-in-the-loop approval
# - Memory learning (triage, response style, calendar preferences)
# - Marks processed emails as read in Outlook
# """

# from typing import Literal

# from langchain.chat_models import init_chat_model
# from langgraph.graph import StateGraph, START, END
# from langgraph.store.base import BaseStore
# from langgraph.types import interrupt, Command

# from email_assistant.tools import get_tools, get_tools_by_name
# from email_assistant.tools.outlook.prompt_templates import OUTLOOK_TOOLS_PROMPT
# from email_assistant.tools.outlook.outlook_tools import mark_as_read
# from email_assistant.prompts import (
#     triage_system_prompt,
#     triage_user_prompt,
#     agent_system_prompt_hitl_memory,
#     default_triage_instructions,
#     default_background,
#     default_response_preferences,
#     default_cal_preferences,
#     MEMORY_UPDATE_INSTRUCTIONS,
#     MEMORY_UPDATE_INSTRUCTIONS_REINFORCEMENT,
# )
# from email_assistant.schemas import State, RouterSchema, StateInput, UserPreferences
# from email_assistant.utils import (
#     parse_outlook,
#     format_for_display,
#     format_outlook_markdown,
# )
# from dotenv import load_dotenv

# load_dotenv(".env")

# # ============================================================================
# # Tool + Model Setup
# # ============================================================================

# tools = get_tools(
#     ["send_email_tool", "schedule_meeting_tool", "check_calendar_tool", "Question", "Done"],
#     include_outlook=True,
# )
# tools_by_name = get_tools_by_name(tools)

# llm_router = init_chat_model("openai:gpt-4.1", temperature=0.0).with_structured_output(RouterSchema)

# llm = init_chat_model("openai:gpt-4.1", temperature=0.0)
# llm_with_tools = llm.bind_tools(tools, tool_choice="required")

# # ============================================================================
# # Memory Utilities (Same As Gmail)
# # ============================================================================

# def get_memory(store, namespace, default_content=None):
#     user_preferences = store.get(namespace, "user_preferences")
#     if user_preferences:
#         return user_preferences.value
#     store.put(namespace, "user_preferences", default_content)
#     return default_content


# def update_memory(store, namespace, messages):
#     user_preferences = store.get(namespace, "user_preferences")

#     llm = init_chat_model("openai:gpt-4.1", temperature=0.0).with_structured_output(UserPreferences)

#     result = llm.invoke(
#         [
#             {
#                 "role": "system",
#                 "content": MEMORY_UPDATE_INSTRUCTIONS.format(
#                     current_profile=user_preferences.value,
#                     namespace=namespace,
#                 ),
#             }
#         ]
#         + messages
#     )

#     store.put(namespace, "user_preferences", result.user_preferences)


# # ============================================================================
# # TRIAGE STAGE
# # ============================================================================

# def triage_router(
#     state: State, store: BaseStore
# ) -> Command[Literal["triage_interrupt_handler", "response_agent", "__end__"]]:

#     author, to, subject, email_thread, email_id = parse_outlook(state["email_input"])

#     user_prompt = triage_user_prompt.format(
#         author=author,
#         to=to,
#         subject=subject,
#         email_thread=email_thread,
#     )

#     email_markdown = format_outlook_markdown(subject, author, to, email_thread, email_id)

#     triage_instructions = get_memory(
#         store,
#         ("email_assistant", "triage_preferences"),
#         default_triage_instructions,
#     )

#     system_prompt = triage_system_prompt.format(
#         background=default_background,
#         triage_instructions=triage_instructions,
#     )

#     result = llm_router.invoke(
#         [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt},
#         ]
#     )

#     classification = result.classification

#     if classification == "respond":
#         return Command(
#             goto="response_agent",
#             update={
#                 "classification_decision": classification,
#                 "messages": [
#                     {
#                         "role": "user",
#                         "content": f"Respond to the email: {email_markdown}",
#                     }
#                 ],
#             },
#         )

#     elif classification == "ignore":
#         return Command(goto=END, update={"classification_decision": classification})

#     elif classification == "notify":
#         return Command(
#             goto="triage_interrupt_handler",
#             update={"classification_decision": classification},
#         )

#     raise ValueError(f"Invalid classification: {classification}")


# def triage_interrupt_handler(
#     state: State, store: BaseStore
# ) -> Command[Literal["response_agent", "__end__"]]:

#     author, to, subject, email_thread, email_id = parse_outlook(state["email_input"])
#     email_markdown = format_outlook_markdown(subject, author, to, email_thread, email_id)

#     request = {
#         "action_request": {
#             "action": f"Email Assistant: {state['classification_decision']}",
#             "args": {},
#         },
#         "config": {
#             "allow_ignore": True,
#             "allow_respond": True,
#             "allow_edit": False,
#             "allow_accept": False,
#         },
#         "description": email_markdown,
#     }

#     response = interrupt([request])[0]

#     if response["type"] == "response":
#         update_memory(
#             store,
#             ("email_assistant", "triage_preferences"),
#             [
#                 {
#                     "role": "user",
#                     "content": "User chose to respond to a notify-classified email.",
#                 }
#             ],
#         )
#         return Command(goto="response_agent", update={"messages": []})

#     elif response["type"] == "ignore":
#         update_memory(
#             store,
#             ("email_assistant", "triage_preferences"),
#             [
#                 {
#                     "role": "user",
#                     "content": "User ignored a notify-classified email.",
#                 }
#             ],
#         )
#         return Command(goto=END, update={})

#     raise ValueError("Invalid response")


# # ============================================================================
# # RESPONSE AGENT (Same Logic As Gmail)
# # ============================================================================

# def llm_call(state: State, store: BaseStore):

#     cal_preferences = get_memory(
#         store, ("email_assistant", "cal_preferences"), default_cal_preferences
#     )

#     response_preferences = get_memory(
#         store,
#         ("email_assistant", "response_preferences"),
#         default_response_preferences,
#     )

#     return {
#         "messages": [
#             llm_with_tools.invoke(
#                 [
#                     {
#                         "role": "system",
#                         "content": agent_system_prompt_hitl_memory.format(
#                             tools_prompt=OUTLOOK_TOOLS_PROMPT,
#                             background=default_background,
#                             response_preferences=response_preferences,
#                             cal_preferences=cal_preferences,
#                         ),
#                     }
#                 ]
#                 + state["messages"]
#             )
#         ]
#     }


# # ============================================================================
# # MARK AS READ (Outlook)
# # ============================================================================

# def mark_as_read_node(state: State):
#     author, to, subject, email_thread, email_id = parse_outlook(state["email_input"])
#     mark_as_read(email_id)


# # ============================================================================
# # RESPONSE AGENT GRAPH
# # ============================================================================

# agent_builder = StateGraph(State)

# agent_builder.add_node("llm_call", llm_call)
# agent_builder.add_node("mark_as_read_node", mark_as_read_node)

# agent_builder.add_edge(START, "llm_call")
# agent_builder.add_edge("mark_as_read_node", END)

# response_agent = agent_builder.compile()

# # ============================================================================
# # OVERALL WORKFLOW
# # ============================================================================

# overall_workflow = StateGraph(State, input=StateInput)

# overall_workflow.add_node("triage_router", triage_router)
# overall_workflow.add_node("triage_interrupt_handler", triage_interrupt_handler)
# overall_workflow.add_node("response_agent", response_agent)
# overall_workflow.add_node("mark_as_read_node", mark_as_read_node)

# overall_workflow.add_edge(START, "triage_router")
# overall_workflow.add_edge("mark_as_read_node", END)

# email_assistant = overall_workflow.compile()
