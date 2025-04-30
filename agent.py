import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from tools import save_memory, TOOLS

# Load environment variables
load_dotenv()

def agent(messages, user_id="1234"):
    """
    Process messages through the OpenAI model and handle tool calls.
    
    Args:
        messages (list): List of message objects with role and content
        user_id (str): The unique identifier for the user, used for memory storage/retrieval
        
    Returns:
        str: The assistant's response or result of a tool call
    """
    # Initialize the OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Extract the last user message for context
    last_user_message = ""
    for msg in reversed(messages):
        if msg["role"] == "user":
            last_user_message = msg["content"]
            break
    
    # Automatically save important interactions to memory
    if last_user_message and len(last_user_message) > 5:
        # Save this interaction to memory without altering the conversation flow
        try:
            # Only save substantial messages that likely contain meaningful content
            if len(last_user_message.split()) > 3:
                memory_text = f"User said: {last_user_message}"
                save_memory(memory_text, user_id=user_id)
        except Exception as e:
            # Silently handle any errors to not disrupt the conversation
            print(f"Memory saving error (non-critical): {str(e)}")
    
    # Make a ChatGPT API call with tool calling
    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # You can change this to another model if needed
        tools=TOOLS,  # Here we pass the tools to the LLM
        messages=messages
    )
    
    # Get the response from the LLM
    response = completion.choices[0].message
    
    # Automatically save the assistant's response if it's substantial
    if response.content and len(response.content) > 20:
        try:
            memory_text = f"Assistant responded: {response.content[:200]}..."
            save_memory(memory_text, user_id=user_id)
        except Exception as e:
            # Silently handle any errors to not disrupt the conversation
            print(f"Memory saving error (non-critical): {str(e)}")
    
    # Parse the response to get the tool call arguments
    if response.tool_calls:
        # Process each tool call
        for tool_call in response.tool_calls:
            # Get the tool call arguments
            tool_call_arguments = json.loads(tool_call.function.arguments)
            
            # Handle different tool calls
            if tool_call.function.name == "save_memory":
                # Instead of returning the save_memory result, silently save the memory
                try:
                    save_memory(tool_call_arguments["memory"], user_id=user_id)
                    print(f"Memory saved: {tool_call_arguments['memory'][:50]}...")
                except Exception as e:
                    print(f"Error saving memory: {str(e)}")
                
                # Make a follow-up call to get a proper response from the assistant
                # First add a system message explaining the memory was saved successfully
                follow_up_messages = messages.copy()
                follow_up_messages.append({
                    "role": "system", 
                    "content": "The memory has been saved successfully. Please continue the conversation normally without mentioning the memory saving."
                })
                
                # Request a new response that's actually for the user
                new_completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=follow_up_messages
                )
                
                # Return the new, user-friendly response
                return new_completion.choices[0].message.content
    
    # If there are no tool calls, return the response content
    return response.content
