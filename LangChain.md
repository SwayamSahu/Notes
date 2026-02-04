This script is designed to guide students from foundational knowledge of LangChain to implementing advanced techniques and deployment strategies, drawing comprehensively from the provided sources.

---------

## **LangChain Mastery: From Beginner to AI Engineer**

### **Section 1: Foundation and Core Concepts (Beginner)**

| Slide | Title | Script/Content Points | Source Citations |
| :--- | :--- | :--- | :--- |
| 1 | **Title Slide** | **Title:** LangChain Mastery: From Beginner to AI Engineer. **Subtitle:** Building LLM-Powered Applications using LangChain and LCEL. | [All Sources] |
| 2 | **What is LangChain?** | **LangChain is an open-source framework designed to simplify the creation of applications using Large Language Models (LLMs)**. The name "LangChain" stands for Language Models Chain. | |
| 3 | **Why Use LangChain?** | **1. LLM Flexibility:** It provides a common framework where switching between LLM providers (like GPT, Llama, or Gemini) is easy, preventing complex code overhauls if API costs change or a better model emerges. **2. External Integration:** It helps integrate LLMs with external data, computation, and tools (e.g., reading proprietary data or querying the latest information from the internet). **3. Modular Workflow:** It offers tools for effective prompt management, memory handling, and chaining LLMs together for reusable, efficient workflows. | |
| 4 | **The LangChain Ecosystem** | LangChain is a generic framework designed to handle whatever LLM models come in the future. The broader ecosystem includes components for observability and deployment. **Key Components Overview:** **Models/LLMs** (the interface to the language model), **Prompt Templates** (structuring inputs to the model), **Chains** (sequencing steps/actions), **Agents and Tools** (enabling decision-making and interaction with the world), **Retrieval/Indexes** (handling external data via vectors), and **Memory** (persisting state). | |

### **Section 2: Building Blocks (Intermediate)**

| Slide | Title | Script/Content Points | Source Citations |
| :--- | :--- | :--- | :--- |
| 5 | **Models and LLM Integration** | **Model Agnostic:** LangChain integrates with various LLMs (e.g., OpenAI, Hugging Face, Ollama for local models). **Access:** LLMs are typically accessed through a Chat Model interface. Packages are usually named following a convention like `langchain-openai` or `langchain-google-vertexai`. **Setup:** The first step is setting up the API key (e.g., `OPENAI_API_KEY`) and initializing the model. **Temperature Control:** This controls the randomness/creativity of the output (value typically 0 to 1). **Set to 0** for precision (e.g., summarization, calculation). **Set higher** (e.g., 0.7-1) for creative tasks (e.g., poetry, storytelling). | |
| 6 | **Prompt Templates and Messages** | **Goal:** To construct a prompt by transforming raw user input, ready to be passed to the LLM. **Dynamic Templates:** Templates use placeholders (e.g., `{language}`, `{topic}`) which are filled with user input values upon invocation. **Message Structure:** Communication uses `Message` objects, each having a `role` and `content`. **Roles:** **System Message:** Directs the LLM's personality or behavior (e.g., "You are a helpful assistant"). **Human Message:** Represents the user input. **AI Message:** Represents the model's response. | |
| 7 | **Basic Chains and Runnables** | **Chains:** Define sequences of operations where the output of one step becomes the input of the next. **Runnables:** Any task, action, or function that can be performed in the chain. **LCEL (LangChain Expression Language):** This is the **recommended, modern way** to compose chains. It uses the simple chainable syntax with the **pipe operator `|`**. **Example:** `prompt_template \| llm \| StrOutputParser()`. **Note:** The older `LLMChain` class is deprecated; use the pipe operator instead. | |
| 8 | **Custom Logic with RunnableLambda** | **Runnable Lambda:** Allows you to embed arbitrary Python functions or custom logic as a step (a runnable) in an LCEL chain. This is useful for formatting or when existing LangChain components don't provide the needed functionality. **Custom Example:** Using a runnable lambda to print the title of a movie generated in a previous step. **Chaining Types (High Level):** **Sequential/Extended Chaining:** Tasks run one after the other. **Parallel Chaining:** Tasks run concurrently (e.g., translating text to multiple languages at once). **Conditional Chaining/Routing:** The next step is chosen based on a condition. | |

### **Section 3: Essential Applications (Intermediate to Advanced)**

| Slide | Title | Script/Content Points | Source Citations |
| :--- | :--- | :--- | :--- |
| 9 | **Conversational Memory** | **Function:** Persists the state (history) between calls, allowing the LLM to "remember" previous interactions for coherent conversation. **Modern Implementation:** Use `RunnableWithMessageHistory` to manage context in up-to-date LangChain. **Memory Types:** **1. Buffer Memory:** Stores the entire conversation history (simple, but costs increase rapidly). **2. Buffer Window Memory:** Stores only the last *K* messages or interactions. **3. Summary Memory:** Uses an LLM to compress the conversation into a summary, reducing the token count while retaining context. | |
| 10 | **RAG Pipeline: Overview** | **Retrieval Augmented Generation (RAG):** A popular paradigm that connects LLMs to external, up-to-date, or proprietary data sources to improve response accuracy. **Core Steps (Data Injection/Indexing):** 1. **Load Data Source:** Using **Document Loaders** (e.g., `TextLoader`, `PyPDFLoader`, `WebBaseLoader`) to ingest documents (PDFs, URLs, TXT, databases). 2. **Transform/Split:** Breaking large documents into smaller **chunks** using **Text Splitters** (e.g., `RecursiveCharacterTextSplitter`) to ensure the data fits the LLM's context window. 3. **Embed:** Converting chunks into numerical **vector embeddings** that capture semantic meaning. 4. **Store:** Saving the vectors in a **Vector Store** (e.g., ChromaDB, FAISS). | |
| 11 | **RAG Pipeline: Retrieval and Generation** | **Retrievers:** An interface that takes an unstructured query and retrieves relevant documents from the Vector Store. You obtain a retriever interface by calling `.as_retriever()` on the Vector Store. **Document Chain (e.g., `create_stuff_document_chain`):** This chain takes the list of retrieved documents, formats them into a prompt (context), and passes that prompt to the LLM. **Retrieval Chain (`create_retrieval_chain`):** Combines the Retriever and the Document Chain. The user inquiry is passed to the retriever, relevant documents are fetched, and then passed to the LLM via the document chain to generate the final response based on the provided context. | |
| 12 | **Advanced RAG Chains (Map Reduce & Refine)** | When multiple documents are retrieved, additional methods are needed to manage the context. **Stuff Chain (`chain_type="stuff"`):** Puts all relevant documents directly into the LLM context (simple, works if context fits). **Map-Reduce Chain:** Sends chunks individually to an LLM to generate initial summaries/answers ("map"), then sends all outputs to a final LLM call to combine them into one definitive answer ("reduce"). **Refine Chain:** Iteratively processes chunks. The output from the first chunk is sent along with the second chunk and the original question to the LLM to generate a refined answer, continuing until all chunks are processed. | |

### **Section 4: Advanced Concepts (Advanced)**

| Slide | Title | Script/Content Points | Source Citations |
| :--- | :--- | :--- | :--- |
| 13 | **Agents and Tools Deep Dive** | **Agents:** Use the LLM as a reasoning engine to select a sequence of actions (tools) to achieve a goal. **Tools:** Functions that agents can call (e.g., `GoogleSearch`, `WikipediaQueryRun`, custom functions). **Tool Construction:** Tools should be defined with clear **docstrings** (explaining when/how to use the tool), clear parameter names, and type annotations. **ReAct Loop:** The core pattern for iterative execution: **Reasoning** (LLM decides the next step) -> **Action** (Tool call based on LLM output) -> **Observation** (Tool results). This sequence is managed by the **Agent Executor**. **Multi-Search Agents:** Agents can leverage multiple tools (e.g., Wikipedia, Arxiv, and custom retrievers) simultaneously to answer complex, multi-source queries. | |
| 14 | **Structured Output and Tool Choices** | **Forcing Structured Output:** Agents can be forced to respond in a structured format (e.g., JSON) using the structured output feature, which internally relies on a forced tool call. **Final Answer Tool:** A recommended advanced pattern where the final answer is deliberately returned via a custom "Final Answer" tool, ensuring reliability and structured output. **Tool Choice Configuration:** Setting `tool_choice=any` or `required` forces the LLM to use a tool, preventing the model from writing directly into the content field when a tool is expected. | |
| 15 | **Observability (LangSmith)** | **LangSmith** is the MLOps module within the LangChain ecosystem focused on observability. **Purpose:** Debugging, monitoring, testing, and tracking the performance, latency, cost, and token usage of LLM applications. **Tracing:** LangSmith automatically tracks the sequence of LLM calls, tool uses, and steps taken by chains and agents (known as "traces") with minimal setup. This allows engineers to visualize the iterative ReAct loop of an agent. | |
| 16 | **Streaming and Async** | **Streaming:** An essential UX feature that returns tokens (or agent intermediate steps) one by one in real-time. It prevents the user from waiting for a long response, significantly improving user experience. Streaming can show the agent’s thoughts, such as when a tool is being used, a crucial feature for complex agentic interfaces. **Async (Asynchronous Code):** Crucial for API scalability and performance. Using async methods (e.g., `a.stream`, `a.invoke`) allows the application to continue running other tasks while waiting for LLM API calls, which often involve latency. | |
| 17 | **Deployment (LangServe) & End-to-End** | **LangServe:** A component used to deploy LangChain chains as REST APIs, often leveraging Fast API. It simplifies the process of making LLM services accessible via URLs and routes. **Creating Routes:** Routes can be defined to handle different functionalities, such as using one route for an OpenAI model (e.g., generating an essay) and another route for an Ollama/Llama 2 model (e.g., generating a poem). **End-to-End Project:** Combining concepts like asynchronous custom agents, streaming, tools (like Serper API for web search), LCEL, and memory to build a fully functional, real-world chat application. | |


========================

Refer: https://www.geeksforgeeks.org/artificial-intelligence/introduction-to-langchain/

Refer: https://www.python-engineer.com/posts/langchain-crash-course/

Refer: https://docs.langchain.com/oss/python/langchain/overview


Introduction to LangChain

LangChain is an open-source framework designed to simplify the creation of applications using large language models (LLMs). It provides a standard interface for integrating with other tools and end-to-end chains for common applications. It helps AI developers connect LLMs such as GPT-4 with external data and computation. This framework comes for both Python and JavaScript.

Key benefits include:
1 Modular Workflow: Simplifies chaining LLMs together for reusable and efficient workflows.
2 Prompt Management: Offers tools for effective prompt engineering and memory handling.
3 Ease of Integration: Streamlines the process of building LLM-powered applications.

Key Components of LangChain

Lets see various components of Langchain:
1. Chains: Chains define sequences of actions, where each step can involve querying an LLM, manipulating data or interacting with external tools. There are two types:
1 Simple Chains: A single LLM invocation.
2 Multi-step Chains: Multiple LLMs or actions combined, where each step can take the output from the previous step.
2. Prompt Management: LangChain facilitates managing and customizing prompts passed to the LLM. Developers can use PromptTemplates to define how inputs and outputs are formatted before being passed to the model. It also simplifies tasks like handling dynamic variables and prompt engineering, making it easier to control the LLM's behavior.
3. Agents: Agents are autonomous systems within LangChain that take actions based on input data. They can call external APIs or query databases dynamically, making decisions based on the situation. These agents leverage LLMs for decision-making, allowing them to respond intelligently to changing input.
4. Vector Database: LangChain integrates with a vector database which is used to store and search high-dimensional vector representations of data. This is important for performing similarity searches, where the LLM converts a query into a vector and compares it against the vectors in the database to retrieve relevant information.
Vector database plays a key role in tasks like document retrieval, knowledge base integration or context-based search providing the model with dynamic, real-time data to enhance responses.
5. Models: LangChain is model-agnostic meaning it can integrate with different LLMs such as OpenAI's GPT, Hugging Face models, DeepSeek R1 and more. This flexibility allows developers to choose the best model for their use case while benefiting from LangChain’s architecture.
6. Memory Management: LangChain supports memory management allowing the LLM to "remember" context from previous interactions. This is especially useful for creating conversational agents that need context across multiple inputs. The memory allows the model to handle sequential conversations, keeping track of prior exchanges to ensure the system responds appropriately.


How LangChain Works?
LangChain follows a structured pipeline that integrates user queries, data retrieval and response generation into seamless workflow.

1. User Query
The process begins when a user submits a query or request.

For example, a user might ask, “What’s the weather like today?” This query serves as the input to the LangChain pipeline.

2. Vector Representation and Similarity Search
Once the query is received, LangChain converts it into a vector representation using embeddings. This vector captures the semantic meaning of the query.
The vector is then used to perform a similarity search in a vector database. The goal is to find the most relevant information or context stored in the database that matches the user's query.
3. Fetching Relevant Information
Based on the similarity search, LangChain retrieves the most relevant data or context from the database. This step ensures that the language model has access to accurate and contextually appropriate information to generate a meaningful response.

4. Generating a Response
The retrieved information is passed to the language model (e.g., OpenAI's GPT, Anthropic's Claude or others). The LLM processes the input and generates a response or takes an action based on the provided data.

For example, if the query is about the weather, the LLM might generate a response like, “Today’s weather is sunny with a high of 75°F.”

The formatted response is returned to the user as the final output. The user receives a clear, accurate and contextually relevant answer to their query.

Step-by-Step Implementation
Let's implement a model using LangChain and OpenAI API:

Step 1: Install the dependencies
We will install all the required dependencies for our model.

langchain: the core LangChain framework (chains, prompts, tools, memory, etc.).
langchain-openai: OpenAI model wrapper for LangChain (GPT-3.5, GPT-4, etc.).
python-dotenv: to securely manage our API keys inside a .env file.

!pip install langchain langchain-openai python-dotenv
Step 2: Import Libraries
We will import all the required libraries.

os: interact with environment variables.
load_dotenv: loads .env file values into our environment.
OpenAI: lets us call OpenAI’s GPT models in LangChain.
PromptTemplate: define structured prompts with placeholders.
StrOutputParser: ensures model response is returned as clean string text.

import os
from dotenv import load_dotenv
from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
Step 3: Load API Key
We need to load the OpenAI API Key, but first we create a .env file to store our API key.


OPENAI_API_KEY = your_openai_api_key_here
Now we use the os.getenv() function to securely fetch the API key.


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
Step 4: Initialize the OpenAI LLM
We initialize the LLM model:

temperature=0.7: controls creativity (0 = deterministic, 1 = very creative).
openai_api_key=api_key: authenticates with OpenAI.

llm = OpenAI(
    temperature=0.7,
    openai_api_key=api_key
)
Step 5: Run a Simple Prompt
We will check by running a simple prompt.

.invoke(): sends prompt to LLM and returns text output.

prompt = "Suggest me a skill that is in demand?"
response = llm.invoke(prompt)
print(" Suggested Skill:\n", response)
Output:

Screenshot-2025-08-21-173401
Output
Step 6: Create a Prompt Template
We create a dynamic prompt where {year} can be replaced with input values.


template = "Give me 3 career skills that are in high demand in {year}."
prompt_template = PromptTemplate.from_template(template)
Step 7: Build a Chain with LCEL
LCEL (LangChain Expression Language): It’s a new way to compose LLM workflows using a simple, chainable syntax with the | (pipe) operator.

1. prompt_template

Fills placeholders (like {year}) with actual inputs.
Example: "Give me 3 career skills in 2025."
2. llm

Sends the formatted prompt to the OpenAI model.
Example input: "Give me 3 career skills in 2025."
Example output: "1. Data Analytics\n2. AI/ML\n3. Cybersecurity"
3. StrOutputParser()

Cleans up and ensures the LLM’s response is returned as a string.

chain = prompt_template | llm | StrOutputParser()
Step 8: Run the Chain
We run the chain to fetch results.

.invoke({"year": "2025"}) replaces {year} with 2025 in the prompt.
Final formatted prompt: "Give me 3 career skills that are in high demand in 2025."

response = chain.invoke({"year": "2025"})
print("\n Career Skills in 2025:\n", response)
Output:

Output

Applications of LangChain

Let's see the applications of LangChain:

Chatbots and Virtual Assistants: They can be designed to remember past interactions, connect with external APIs and deliver more natural, context-aware conversations.
Document Question Answering: Users can query PDFs, research papers, contracts or enterprise documentation and get precise answers instead of manually searching.
Knowledge Management Systems: They help organize and retrieve company knowledge by linking LLMs with structured and unstructured data, enabling intelligent search, summarization and recommendations.
Workflow Automation: Complex multi-step processes like customer support ticket resolution, report generation or CRM updates can be automated seamlessly.
Data Analysis and Business Intelligence (BI): Natural language queries can be translated into SQL, turning raw data into insights, charts or business reports with minimal effort.

The LangChain framework is a great interface to develop interesting AI-powered applications and from personal assistants to prompt management as well as automating tasks. So, keep learning and keep developing powerful applications.
