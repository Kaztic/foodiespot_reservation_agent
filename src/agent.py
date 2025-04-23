import os
import json
import google.generativeai as genai
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

# Import tool definitions
from tools import TOOL_SCHEMAS, TOOL_MAP

# Load environment variables
load_dotenv()

# Configure the Gemini API
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in a .env file.")

genai.configure(api_key=API_KEY)

class FoodieSpotAgent:
    """FoodieSpot AI Reservation Agent class that handles interactions with Gemini API."""
    
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        """
        Initialize the agent with Gemini model.
        
        Args:
            model_name: Name of the Gemini model to use
        """
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        self.chat = None
        self.system_prompt = self._create_system_prompt()
        self._start_conversation()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt for the Gemini model."""
        return """
        You are FoodieSpot's friendly, helpful, and conversational AI reservation assistant.

        GOALS:
        - Assist users in finding suitable restaurants based on their stated preferences (e.g., cuisine, location, ambiance like "romantic").
        - Provide detailed information about specific restaurants when asked.
        - Check reservation availability accurately.
        - Make reservations smoothly, confirming all details.

        INTERACTION STYLE:
        - Be warm, friendly, and natural in your responses. Avoid robotic or overly formal language.
        - Maintain context throughout the conversation. Refer back to previously mentioned details (like cuisine or location) to show you're following along.
        - Ask clarifying questions ONE AT A TIME if essential information is missing (e.g., if location is needed, just ask for location). Don't ask for everything at once.
        - If the user expresses clear intent to book or check availability for a specific restaurant, gather the necessary details (date, time, party size) efficiently.
        - Once you have the restaurant, date, time, and party size, use the `check_availability` tool.
        - **Booking Flow:** If `check_availability` is successful:
            1. State clearly that the time slot IS available.
            2. Immediately ask for the user's name and phone number required to complete the booking.
            3. Once name and phone are provided, use the `make_reservation` tool.
            4. Confirm the successful booking details (confirmation code, etc.) or relay any unlikely error from the `make_reservation` tool gracefully.
            *Avoid redundant confirmations like "Is that okay?" or "Shall I proceed?" between checking availability and asking for booking details.*
        - If `check_availability` fails, inform the user and suggest checking a different time, date, or offer alternative restaurants using `list_restaurants`.
        - If the user provides a vague time like 'anytime' or 'evening', try checking a common time first (e.g., 7 PM). If unavailable, you can check another nearby time (e.g., 8 PM) OR explicitly ask the user to choose from the restaurant's opening hours (which you can get via `get_restaurant_details` if needed).
        - If a user's request is ambiguous, offer specific examples or ask for clarification (e.g., "I can look for romantic places! Any preferred type of food or area?").

        TOOL USAGE:
        - Rely exclusively on the provided tools (`list_restaurants`, `get_restaurant_details`, `check_availability`, `make_reservation`) to answer questions and perform actions.
        - Do NOT make up information about restaurants, availability, or reservations.
        - Analyze the user's request carefully to select the correct tool and parameters.
        - If the user provides information like `cuisine`, `location`, `party_size`, `date`, `time`, or descriptive text (like `romantic`), use those details as arguments for the relevant tool.

        ERROR HANDLING:
        - If a tool execution fails or returns an error (e.g., tool not found, data manager error), do NOT mention the specific error or "tool" to the user. Instead, provide a polite, generic apology and suggest rephrasing or trying again. Examples:
            - "I'm sorry, I seem to be having a little trouble processing that. Could you perhaps try rephrasing your request?"
            - "Apologies, I couldn't retrieve that information right now. Maybe we can try searching in a different way?"
            - "Oops! Something went wrong on my end. Let's try that again, shall we?"
        - If essential information is missing and the user isn't providing it after a prompt, gently explain what's needed or offer to search more broadly.

        Example clarifying question flows:
        User: "I want Thai food."
        Assistant: "Thai sounds delicious! Which neighborhood or area are you interested in?"
        User: "Surprise me."
        Assistant: "Okay, I can show you some popular Thai options across different areas if you'd like?"

        Remember, your primary goal is a smooth, helpful, and pleasant reservation experience for the user.
        """
    
    def _start_conversation(self):
        """Start a new conversation with the model."""
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.4,
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048
        )
        
        # Initialize the chat with the system prompt (tools passed in send_message)
        self.chat = self.model.start_chat(
            history=[{"role": "user", "parts": [self.system_prompt]}]
            # tools=[{"function_declarations": TOOL_SCHEMAS}] # Keep tools removed here
        )
    
    def _execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool function based on the tool call from Gemini.
        
        Args:
            tool_call: Dictionary containing tool call information
            
        Returns:
            Tool execution results
        """
        function_name = tool_call["name"]
        function_args = tool_call["args"]
        
        # Get the actual function from the tool map
        tool_function = TOOL_MAP.get(function_name)
        
        if not tool_function:
            return {
                "error": True,
                "message": f"Tool '{function_name}' not found."
            }
        
        try:
            # Execute the tool function
            result = tool_function(**function_args)
            return result
        except Exception as e:
            print(f"--- Error executing tool '{function_name}': {e} ---") # Log the actual error
            # Return an error dictionary that the LLM can understand and rephrase
            return {
                "error": True,
                "message": f"An error occurred while trying to execute the {function_name} action."
            }
    
    async def process_message(self, user_message: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Process a user message, interact with Gemini API, and handle any tool calls.
        """
        tool_execution_logs = []
        
        try:
            # Log history before sending user message
            print(f"--- History before User Send: {repr(self.chat.history)} ---")
            send_args = {
                "content": user_message,
                "generation_config": self.generation_config,
                "tools": [{"function_declarations": TOOL_SCHEMAS}]
            }
            print(f"--- Args for User Send: {send_args} ---")
            response = self.chat.send_message(**send_args)
            
            final_response_text = "" # Initialize text accumulator
            function_call_to_process = None # Initialize variable to hold a valid function call

            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                print(f"--- Full Candidate: {repr(candidate)} ---") 
                
                if hasattr(candidate, 'content') and candidate.content and hasattr(candidate.content, 'parts'):
                    # Iterate through parts to identify text and valid function calls
                    for part in candidate.content.parts:
                        # Check for a VALID function call (must exist and have a non-empty name)
                        if getattr(part, 'function_call', None) and part.function_call.name:
                            print(f"--- Valid function_call found in part: {repr(part)} ---")
                            function_call_to_process = part.function_call
                            # If we find a valid function call, prioritize it over any text in this turn
                            final_response_text = "" # Clear any accumulated text from this turn
                            break # Process only the first valid function call found
                        # Check for text part
                        elif getattr(part, 'text', None):
                             print(f"--- Text part found: {part.text} ---")
                             # Only accumulate text if we haven't found a function call yet
                             if function_call_to_process is None:
                                 final_response_text += part.text

            # === Processing Logic ===
            # Check if a valid function call needs processing
            if function_call_to_process:
                print(f"--- Processing function call: {function_call_to_process.name} ---")
                function_call = function_call_to_process # Use the identified function call
                
                # --- Start copied logic for function call processing --- 
                tool_args = {}
                try:
                    # Handle MapComposite object directly
                    if function_call.args:
                        tool_args = dict(function_call.args)
                    else:
                        tool_args = {}
                except Exception as convert_err: 
                    print(f"--- Error converting function_call.args to dict: {convert_err} ---")
                    tool_args = {} 

                tool_call = {
                    "name": function_call.name,
                    "args": tool_args
                }
                print(f"--- Executing tool_call: {tool_call} ---") 
                
                tool_result = self._execute_tool(tool_call)
                print(f"--- Tool result: {repr(tool_result)} ---") 
                print(f"--- Tool result type: {type(tool_result)} ---") 

                tool_execution_logs.append({
                    "tool_call": tool_call,
                    "result": tool_result
                })
                
                serialized_result = None
                try:
                    serialized_result = json.dumps(tool_result) 
                except TypeError as type_err:
                    print(f"--- TypeError serializing tool_result: {type_err} ---")
                    serialized_result = json.dumps({"error": True, "message": "Failed to serialize tool result"})

                user_feedback_message = f"Tool '{function_call.name}' executed. Result: {serialized_result}"
                tool_response_message = {
                    "role": "user", 
                    "parts": [user_feedback_message]
                }
                print(f"--- Appending to history (as user): {tool_response_message} ---") 

                self.chat.history.append(tool_response_message)
                
                follow_up_response = None
                try:
                    print(f"--- History before Follow-up Send: {repr(self.chat.history)} ---")
                    send_args_followup = {
                        "content": "OK.",
                        "generation_config": self.generation_config,
                        "tools": [{"function_declarations": TOOL_SCHEMAS}]
                    }
                    print(f"--- Args for Follow-up Send: {send_args_followup} ---")
                    follow_up_response = self.chat.send_message(**send_args_followup)
                    print(f"--- Follow-up response object: {repr(follow_up_response)} ---") 
                except Exception as send_err:
                    print(f"--- Error DURING follow-up send_message: {send_err} ---")
                    raise send_err 

                try:
                    final_response_text = "" # Reset for the follow-up response
                    if follow_up_response and hasattr(follow_up_response, 'candidates') and follow_up_response.candidates and \
                       hasattr(follow_up_response.candidates[0], 'content'):
                        print("--- Processing follow-up response parts ---")
                        for follow_part in follow_up_response.candidates[0].content.parts:
                            if hasattr(follow_part, 'text') and follow_part.text:
                                final_response_text += follow_part.text
                    else:
                        print("--- Follow-up response has no processable content ---")
                        final_response_text = "OK. What next?" # Default if follow-up is empty
                except Exception as proc_err:
                    print(f"--- Error PROCESSING follow-up response: {proc_err} ---")
                    final_response_text = "I encountered an issue processing the tool result. How can I help further?" # Fallback text
                # --- End copied logic for function call processing --- 

            else:
                # No valid function call was found, use the accumulated text from the initial response
                print(f"--- No valid function call found, using initial text: {repr(final_response_text)} ---")

            # Final checks before returning
            print(f"--- Final response text before return: {repr(final_response_text)} ---") 
            if not final_response_text or "cannot fulfill this request" in final_response_text.lower():
                print("--- Detected potentially unhelpful response, providing fallback. ---")
                return "I'm sorry, I couldn't quite process that. Could you please try rephrasing your request?", tool_execution_logs
            
            return final_response_text, tool_execution_logs
        
        except Exception as e:
            print(f"--- Error in process_message: {e} ---") 
            error_message = "I seem to be having some technical difficulties at the moment. Please try again in a little bit!"
            return error_message, [] 