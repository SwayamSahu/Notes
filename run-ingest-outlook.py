
import json
import uuid
import hashlib
import asyncio
import argparse
import os
import time
import msal
from pathlib import Path
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from langgraph_sdk import get_client
import requests

load_dotenv()

# Setup paths
_ROOT = Path(__file__).parent.absolute()
_SECRETS_DIR = _ROOT / ".secrets"
TOKEN_PATH = _SECRETS_DIR / "token.json"

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

# ════════════════════════════════════════════════════════════════════════════
# EMAIL CONTENT EXTRACTION FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

def extract_message_part(message: dict) -> str:
    """Extract content from an Outlook message.
    
    Outlook messages have a simpler structure than Gmail:
    - Body is directly in message["body"]["content"]
    - ContentType indicates if it's Text or HTML
    
    This function extracts the main content:
    
    Priority:
    1. If Text, return plain text
    2. If HTML, return HTML content (can be stripped if needed)
    3. Fallback to empty string
    
    Args:
        message: Full Outlook message object from Graph API
        
    Returns:
        str: Extracted email content, empty string if no content found
    """
    body = message.get("body", {})
    content_type = body.get("contentType", "").lower()
    content = body.get("content", "")
    
    # For text content, return as-is
    if content_type == "text":
        return content
    
    # For HTML, return HTML (assistant can handle it)
    if content_type == "html":
        return content
    
    return ""

def load_outlook_credentials():
    """Load Outlook credentials from environment variables or local file.
    
    This function implements a flexible credential loading strategy to support
    different deployment environments:
    
    1. **Local Development**: Reads from .secrets/token.json file
    2. **Cloud Deployment**: Reads from OUTLOOK_TOKEN environment variable
    3. **Fallback Chain**: Tries environment variable first, then local file
    
    The credential file/variable should contain JSON with OAuth2 token data:
    {
        "access_token": "...",
        "refresh_token": "...",
        "expires_at": 1234567890,
        "expires_in": 3600,
        ...
    }
    
    Returns:
        access_token string: Valid access token for Graph API
        or None if credentials can't be loaded from any source
    """
    token_data = None
    
    # 1. Try environment variable first (preferred for cloud deployments)
    env_token = os.getenv("OUTLOOK_TOKEN")
    if env_token:
        try:
            token_data = json.loads(env_token)
            print("Using OUTLOOK_TOKEN environment variable")
        except Exception as e:
            print(f"Could not parse OUTLOOK_TOKEN environment variable: {str(e)}")
    
    # 2. Try local file as fallback (preferred for local development)
    if token_data is None:
        if TOKEN_PATH.exists():
            try:
                with open(TOKEN_PATH, "r") as f:
                    token_data = json.load(f)
                print(f"Using token from {TOKEN_PATH}")
            except Exception as e:
                print(f"Could not load token from {TOKEN_PATH}: {str(e)}")
        else:
            print(f"Token file not found at {TOKEN_PATH}")
    
    # If we couldn't get token data from any source, return None
    if token_data is None:
        print("Could not find valid token data in any location")
        return None
    
    try:
        # Get or refresh access token
        now = int(time.time())
        expires_at = token_data.get("expires_at", 0)
        
        if expires_at < now + 300:  # Refresh if <5min left
            if not token_data.get("refresh_token"):
                print("No refresh_token available")
                return None
            
            if not os.getenv("OUTLOOK_CLIENT_ID") or not os.getenv("OUTLOOK_TENANT_ID"):
                print("Missing OUTLOOK_CLIENT_ID or OUTLOOK_TENANT_ID for refresh")
                return None
            
            app = msal.PublicClientApplication(
                os.getenv("OUTLOOK_CLIENT_ID"),
                authority=f"https://login.microsoftonline.com/{os.getenv('OUTLOOK_TENANT_ID')}"
            )
            
            result = app.acquire_token_by_refresh_token(
                token_data["refresh_token"],
                scopes=token_data.get("scope", ["Mail.ReadWrite", "Mail.Send", "Calendars.ReadWrite", "offline_access"])
            )
            
            if "access_token" in result:
                expires_at = int(time.time()) + result["expires_in"]
                token_data.update({
                    "access_token": result["access_token"],
                    "refresh_token": result.get("refresh_token", token_data["refresh_token"]),
                    "expires_at": expires_at,
                    "expires_in": result["expires_in"],
                })
                # Save updated token
                with open(TOKEN_PATH, "w") as f:
                    json.dump(token_data, f, indent=2)
                print("Token refreshed and saved")
            else:
                print("Token refresh failed")
                return None
        
        return token_data["access_token"]
    except Exception as e:
        print(f"Error creating access token: {str(e)}")
        return None

def extract_email_data(message):
    """Extract key information from an Outlook message into standardized format.
    
    This function processes a raw Outlook message and extracts all relevant data
    needed for the LangGraph email assistant to process the email. It standardizes
    the data into a consistent format regardless of email structure.
    
    Extraction steps:
    1. Parse all fields: Subject, From, To, ReceivedDateTime
    2. Extract email body using extract_message_part() helper
    3. Collect metadata: Outlook message ID, conversation ID
    4. Return standardized EmailData dictionary
    
    Args:
        message: Full Outlook message object from Graph API
        
    Returns:
        dict: Standardized email data with keys:
            - from_email: Sender email address and name
            - to_email: Recipient email address
            - subject: Email subject line
            - page_content: Email body (extracted)
            - id: Outlook message ID (for tracking)
            - thread_id: Outlook conversation ID (groups related emails)
            - send_time: Email send timestamp (ISO format)
    """
    
    # Extract key fields from the message
    # Outlook uses direct dict structure: message["subject"], message["from"]["emailAddress"]["address"], etc.
    subject = message.get('subject', 'No Subject')
    from_email = message.get("from", {}).get("emailAddress", {}).get("address", 'Unknown Sender')
    to_email = ", ".join(
        [r["emailAddress"]["address"] for r in message.get("toRecipients", [])]
    )
    date = message.get('receivedDateTime', 'Unknown Date')
    
    # Extract message content using the content extraction helper
    content = extract_message_part(message)
    
    # Create standardized email data object for LangGraph consumption
    email_data = {
        "from_email": from_email,
        "to_email": to_email,
        "subject": subject,
        "page_content": content,
        "id": message['id'],
        "thread_id": message['conversationId'],
        "send_time": date
    }
    
    return email_data

# ════════════════════════════════════════════════════════════════════════════
# LANGGRAPH INGESTION FUNCTIONS
# ════════════════════════════════════════════════════════════════════════════

async def ingest_email_to_langgraph(email_data, graph_name, url="http://127.0.0.1:2024"):
    """Ingest an email to LangGraph for agent processing.
    
    This function takes extracted email data and feeds it into a running LangGraph
    deployment. It handles:
    1. Thread management (create new or retrieve existing)
    2. Run cleanup (delete previous runs to avoid state accumulation)
    3. Email submission to the graph workflow
    
    The function converts Outlook conversation IDs (which can be strings) into
    consistent UUIDs for the LangGraph system, ensuring thread continuity.
    
    Args:
        email_data: Dictionary containing extracted email information
                   Required keys: from_email, to_email, subject, page_content, id, thread_id
        graph_name: Name of the LangGraph deployment to use
                   Example: "email_assistant_hitl_memory_outlook"
        url: URL of the LangGraph deployment
            Default: http://127.0.0.1:2024 (local development)
    
    Returns:
        tuple: (thread_id, run) containing:
            - thread_id: UUID string for the LangGraph thread
            - run: Run object with execution details
    """
    # Connect to LangGraph server
    client = get_client(url=url)
    
    # Create a consistent UUID for the thread
    # This ensures the same Outlook conversation always maps to the same LangGraph thread
    # Uses MD5 hash to convert Outlook's string conversation IDs to UUID format
    raw_thread_id = email_data["thread_id"]
    thread_id = str(
        uuid.UUID(hex=hashlib.md5(raw_thread_id.encode("UTF-8")).hexdigest())
    )
    print(f"Outlook conversation ID: {raw_thread_id} → LangGraph thread ID: {thread_id}")
    
    thread_exists = False
    try:
        # Try to get existing thread info
        # If the thread already exists in LangGraph, we retrieve it
        thread_info = await client.threads.get(thread_id)
        thread_exists = True
        print(f"Found existing thread: {thread_id}")
    except Exception as e:
        # If thread doesn't exist, create it
        # This happens on the first email for a new Outlook conversation
        print(f"Creating new thread: {thread_id}")
        thread_info = await client.threads.create(thread_id=thread_id)
    
    # If thread exists, clean up previous runs to avoid state accumulation
    if thread_exists:
        try:
            # List all runs for this thread
            # Each run represents one execution of the workflow
            runs = await client.runs.list(thread_id)
            
            # Delete all previous runs to avoid state accumulation
            # This ensures fresh processing without old state interference
            for run_info in runs:
                run_id = run_info.id
                print(f"Deleting previous run {run_id} from thread {thread_id}")
                try:
                    await client.runs.delete(thread_id, run_id)
                except Exception as e:
                    print(f"Failed to delete run {run_id}: {str(e)}")
        except Exception as e:
            print(f"Error listing/deleting runs: {str(e)}")
    
    # Update thread metadata with current email ID for tracking
    await client.threads.update(thread_id, metadata={"email_id": email_data["id"]})
    
    # Create a fresh run for this email
    # The run executes the LangGraph workflow with the email as input
    print(f"Creating run for thread {thread_id} with graph {graph_name}")
    
    run = await client.runs.create(
        thread_id,
        graph_name,
        # Transform email data into the format expected by the workflow
        input={"email_input": {
            "from": email_data["from_email"],
            "to": email_data["to_email"],
            "subject": email_data["subject"],
            "body": email_data["page_content"],
            "id": email_data["id"]
        }},
        # Use rollback strategy if anything fails
        multitask_strategy="rollback",
    )
    
    print(f"Run created successfully with thread ID: {thread_id}")
    
    return thread_id, run

# ════════════════════════════════════════════════════════════════════════════
# MAIN EMAIL FETCHING AND PROCESSING WORKFLOW
# ════════════════════════════════════════════════════════════════════════════

async def fetch_and_process_emails(args):
    """Fetch emails from Outlook and process them through LangGraph.
    
    This is the main orchestration function that:
    1. Loads Outlook credentials
    2. Builds Outlook service connection
    3. Constructs search query based on arguments
    4. Fetches matching emails
    5. Extracts data from each email
    6. Submits each to LangGraph for processing
    
    The function respects all command-line filters:
    - Time filter (--minutes-since): Only emails from last N minutes
    - Read status (--include-read): Whether to process already-read emails
    - Early stop (--early): Stop after first email (useful for testing)
    - Rerun (--rerun): Reprocess already-processed emails
    
    Args:
        args: Parsed command-line arguments with:
            - email: Target email address for filtering
            - minutes_since: Time window in minutes
            - include_read: Include already-read emails flag
            - graph_name: LangGraph deployment name
            - url: LangGraph server URL
            - early: Stop after processing one email
            - rerun: Reprocess already-processed emails
            
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Load Outlook credentials from environment or local file
    access_token = load_outlook_credentials()
    if not access_token:
        print("Failed to load Outlook credentials")
        return 1
    
    # Headers for Graph API requests    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    # Track how many emails we successfully process
    processed_count = 0
    
    try:
        # ════════════════════════════════════════════════════════════
        # STEP 1: Build Outlook Search Query
        # ════════════════════════════════════════════════════════════
        
        email_address = args.email
        
        # Construct Outlook search query using OData filters
        filters = []
        
        # Add time constraint if specified
        if args.minutes_since > 0:
            cutoff = (
                datetime.now(timezone.utc) - timedelta(minutes=args.minutes_since)
            ).strftime('%Y-%m-%dT%H:%M:%SZ')
            filters.append(f"receivedDateTime ge {cutoff}")
            
        # Only include unread emails unless --include-read is specified
        # This helps focus on new messages that need responses
        if not args.include_read:
            filters.append("isRead eq false")
            
        # # Add sender/recipient filter
        # if args.email:
        #     filters.append(
        #         f"(from/emailAddress/address eq '{args.email}' "
        #         f"or toRecipients/any(r: r/emailAddress/address eq '{args.email}'))"
        #     )

        # Add sender/recipient filter
        if args.email:
            # For now, filter by sender only (toRecipients/any has known syntax issues with Microsoft Graph)
            # This can be expanded to include recipient filtering if needed
            filters.append(
                f"from/emailAddress/address eq '{args.email}'"
            )
        
        filter_query = ""
        if filters:
            filter_query = "$filter=" + " and ".join(filters)
            
        url = f"{GRAPH_BASE}/me/messages?{filter_query}&$orderby=receivedDateTime desc"
        
        print(f"Outlook search query: {url}")
        
        # ════════════════════════════════════════════════════════════
        # STEP 2: Execute Search and Get Matching Emails
        # ════════════════════════════════════════════════════════════
        
        # Execute the search query against Outlook with pagination
        messages = []
        while url:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                print(response.text)
                return 1
            
            data = response.json()
            messages.extend(data.get("value", []))
            url = data.get("@odata.nextLink")
        
        if not messages:
            print("No emails found matching the criteria")
            return 0
            
        print(f"Found {len(messages)} emails")
        
        # ════════════════════════════════════════════════════════════
        # STEP 3: Process Each Email
        # ════════════════════════════════════════════════════════════
        
        # Process each email found by the search
        for i, message in enumerate(messages):
            # Stop early if requested (useful for testing)
            if args.early and i > 0:
                print(f"Early stop after processing {i} emails")
                break
                
            # Check if we should reprocess this email
            if not args.rerun:
                # TODO: Add check for already processed emails
                # This would track which emails have been processed
                pass
                
            # Extract email data into standardized format
            email_data = extract_email_data(message)
            
            print(f"\nProcessing email {i+1}/{len(messages)}:")
            print(f"From: {email_data['from_email']}")
            print(f"Subject: {email_data['subject']}")
            
            # Send email to LangGraph for agent processing
            thread_id, run = await ingest_email_to_langgraph(
                email_data, 
                args.graph_name,
                url=args.url
            )
            
            processed_count += 1
            
        print(f"\nProcessed {processed_count} emails successfully")
        return 0
        
    except Exception as e:
        print(f"Error processing emails: {str(e)}")
        return 1

def parse_args():
    """Parse command line arguments for the ingestion script.
    
    This function defines all available command-line options for controlling
    the email ingestion behavior. Users can customize:
    - Which emails to fetch (time range, read status)
    - Which LangGraph deployment to use
    - Testing/debugging options (early stop, rerun)
    
    Returns:
        argparse.Namespace: Parsed arguments object with attributes for each flag
    """
    parser = argparse.ArgumentParser(description="Simple Outlook ingestion for LangGraph with reliable tracing")
    
    parser.add_argument(
        "--email", 
        type=str, 
        required=True,
        help="Email address to fetch messages for"
    )
    parser.add_argument(
        "--minutes-since", 
        type=int, 
        default=120,
        help="Only retrieve emails newer than this many minutes"
    )
    parser.add_argument(
        "--graph-name", 
        type=str, 
        default="email_assistant_hitl_memory_outlook",
        help="Name of the LangGraph to use"
    )
    parser.add_argument(
        "--url", 
        type=str, 
        default="http://127.0.0.1:2024",
        help="URL of the LangGraph deployment"
    )
    parser.add_argument(
        "--early", 
        action="store_true",
        help="Early stop after processing one email"
    )
    parser.add_argument(
        "--include-read",
        action="store_true",
        help="Include emails that have already been read"
    )
    parser.add_argument(
        "--rerun", 
        action="store_true",
        help="Process the same emails again even if already processed"
    )
    parser.add_argument(
        "--skip-filters",
        action="store_true",
        help="Skip filtering of emails"
    )
    return parser.parse_args()

# ════════════════════════════════════════════════════════════════════════════
# SCRIPT ENTRY POINT
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Get and parse command line arguments
    # This allows users to customize behavior via CLI flags
    args = parse_args()
    
    # Run the main async email fetching and processing workflow
    # asyncio.run() handles the async event loop setup and cleanup
    exit(asyncio.run(fetch_and_process_emails(args)))
