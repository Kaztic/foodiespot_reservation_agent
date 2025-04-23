import streamlit as st
import asyncio
import os
import json
from datetime import datetime
from agent import FoodieSpotAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check for API key
if not os.getenv("GEMINI_API_KEY"):
    st.error("GEMINI_API_KEY environment variable not set. Please set it in a .env file.")
    st.stop()

# Set page config
st.set_page_config(
    page_title="FoodieSpot Restaurant Reservation Agent",
    page_icon="🍽️",
    layout="centered"
)

# Initialize agent
@st.cache_resource
def get_agent():
    return FoodieSpotAgent()

agent = get_agent()

# App title and description
st.title("🍽️ FoodieSpot Restaurant Reservation Agent")
st.markdown("""
Welcome to FoodieSpot! I can help you:
- Find restaurants based on cuisine, location, or preferences
- Get details about specific restaurants
- Check availability for reservations
- Make reservations for you

Just let me know what you're looking for!
""")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add a welcome message
    welcome_message = {
        "role": "assistant",
        "content": "Hi there! I'm FoodieSpot's AI assistant. How can I help you today? Looking for a restaurant recommendation or would you like to make a reservation?"
    }
    st.session_state.messages.append(welcome_message)

# Initialize tool execution log
if "tool_logs" not in st.session_state:
    st.session_state.tool_logs = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Process user input
async def process_user_input(user_input):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display user message
    with st.chat_message("user"):
        st.write(user_input)
    
    # Show typing indicator while processing
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.write("Thinking...")
        
        # Process the message with agent
        response, tool_logs = await agent.process_message(user_input)
        
        # Store tool logs for debugging
        if tool_logs:
            st.session_state.tool_logs.extend(tool_logs)
        
        # Replace the typing indicator with the actual response
        message_placeholder.write(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Function to run async functions in Streamlit
def run_async(coroutine):
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(coroutine)

# Chat input
user_input = st.chat_input("Type your message here...")
if user_input:
    run_async(process_user_input(user_input))

# Debug section (collapsed by default)
with st.expander("Debug Information", expanded=False):
    if st.session_state.tool_logs:
        st.write("Tool Execution Logs:")
        for idx, log in enumerate(st.session_state.tool_logs):
            st.write(f"### Tool Call {idx+1}")
            st.write("Function:", log["tool_call"]["name"])
            st.write("Arguments:", json.dumps(log["tool_call"]["args"], indent=2))
            st.write("Result:", json.dumps(log["result"], indent=2))
            st.write("---")
    else:
        st.write("No tool calls made yet.")

# Add a button to clear chat history
if st.sidebar.button("Clear Chat History"):
    st.session_state.messages = []
    st.session_state.tool_logs = []
    agent = get_agent() # Re-initialize agent
    agent._start_conversation() # Start a fresh conversation state
    st.rerun() # Use st.rerun() instead of experimental_rerun

# Sidebar with examples
st.sidebar.title("Example Queries")
st.sidebar.markdown("""
Try asking:
- "I'm looking for an Italian restaurant downtown"
- "What are some good Thai places?"
- "Tell me about Pasta Paradise"
- "I'd like to make a reservation at Sushi Sensation for 4 people tomorrow at 7pm"
- "Are there any family-friendly restaurants in Midtown?"
- "I want a romantic place for dinner"
""")

# Add info about the app
st.sidebar.markdown("---")
st.sidebar.header("About FoodieSpot")
st.sidebar.info("""
FoodieSpot is a restaurant reservation system powered by AI.
This app demonstrates the use of the Gemini API for conversational AI
with a robust tool calling architecture.

Get your own Gemini API key at [Google AI Studio](https://makersuite.google.com/).
""")

# Show current date/time for reference
current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
st.sidebar.write(f"Current date/time: {current_time}")

# Add a footer
st.markdown("---")
st.caption("FoodieSpot Restaurant Reservation Agent • Powered by Gemini AI") 