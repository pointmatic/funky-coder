#!/usr/bin/env python3

# This file creates a simple agent that generates a Python function with documentation using LiteLLM completion.
# In the initial prompt, the agent only generates the function to fulfill the user's request.
# In subsequent prompts the user can request documentation (function description, parameter descriptions, return value description, example usage, and edge cases). 
# The user can also request test cases for the function (basic functionality, edge cases, error cases, performance, security, concurrency, various input scenarios)
# 
# Requirements:
# - LiteLLM completion
# - Python 3.x
# - OpenAI API key
# - Maintain conversation context
# - Use a simple agent class to handle the conversation
# - Print each step of the conversation
# - Save the final version to a Python file
# - Simple text-based interface

import os
import re
import dotenv
from litellm import completion
from typing import List, Dict, Any
from dotenv import load_dotenv
import json

EXPECTED_API_KEY_NAME = "OPENAI_API_KEY"

class FunkyCoder:
    def __init__(self, api_key: str, system_message: str, model: str = "openai/gpt-4o", max_tokens: int = 1500, temperature: float = 0.7):
        """
        Initialize the FunkyCoder with API key and configuration settings.
        
        Args:
            api_key: OpenAI API key
            system_message: Initial system instructions for the agent
            model: LLM model to use
            max_tokens: Maximum tokens for completion
            temperature: Temperature for completion (0-1)
        """
        self.__conversation = [{"role": "system", "content": system_message}]
        self.__api_key = api_key
        self.__model = model
        self.__max_tokens = max_tokens
        self.__temperature = temperature

    def prompt(self, user_input: str) -> str:
        """
        Send a prompt to the LLM and get a response.
        
        Args:
            user_input: The user's input text
            
        Returns:
            The assistant's response
        """
        self.__conversation.append({"role": "user", "content": user_input})
        try:
            response = completion(
                messages = self.__conversation,
                model = self.__model,
                temperature = self.__temperature,
                max_tokens = self.__max_tokens,
                top_p = 1,
                frequency_penalty = 0,
                presence_penalty = 0
            )
            assistant_response = response.choices[0].message.content
            self.__conversation.append({"role": "assistant", "content": assistant_response})
            return assistant_response
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(error_msg)
            return error_msg
    
    def save_to_file(self, filename: str):
        """
        Save the entire conversation to a file.
        
        Args:
            filename: Path to the output file
        """
        try:
            with open(filename, "w") as file:
                for message in self.__conversation:
                    role = message["role"]
                    content = message["content"]
                    file.write(f"=== {role.upper()} ===\n{content}\n\n")
            print(f"Conversation saved to {filename}")
        except Exception as e:
            print(f"Error saving file: {str(e)}")
    
    def extract_code(self) -> str:
        """
        Extract Python code from the conversation.
        
        Returns:
            String containing all Python code found in the conversation
        """
        code_blocks = []
        pattern = r"```python\n(.*?)```"
        
        for message in self.__conversation:
            if message["role"] == "assistant":
                matches = re.findall(pattern, message["content"], re.DOTALL)
                code_blocks.extend(matches)
        
#        return "\n\n".join(code_blocks)
        # Return the last code block (string) if multiple are found
        return code_blocks[-1:][0] if code_blocks else None
    
    def save_code_to_file(self, filename: str) -> bool:
        """
        Extract code from the conversation and save it to a Python file.
        
        Args:
            filename: Path to the output Python file
            
        Returns:
            True if successful, False otherwise
        """
        code = self.extract_code()
        if not code:
            print("No code found in the conversation.")
            return False
            
        try:
            with open(filename, "w") as file:
                file.write(code)
            print(f"Code saved to {filename}")
            return True
        except Exception as e:
            print(f"Error saving code: {str(e)}")
            return False
    
    def reset_conversation(self, keep_system_message: bool = True):
        """
        Reset the conversation history.
        
        Args:
            keep_system_message: Whether to keep the system message
        """
        system_message = self.__conversation[0] if keep_system_message else None
        self.__conversation = [system_message] if system_message else []
        print("Conversation reset.")
    
    def show_history(self):
        """Print the conversation history."""
        for idx, message in enumerate(self.__conversation):
            role = message["role"]
            if role == "system":
                continue
            print(f"\n--- Message {idx} ({role}) ---")
            print(message["content"])

def is_valid_filename(filename: str) -> bool:
    """
    Check if the filename is valid.
    
    Args:
        filename: The filename to check
        
    Returns:
        True if valid, False otherwise
    """
    invalid_chars = r'<>:"/\\|?*'
    return not any(char in filename for char in invalid_chars)

def show_help():
    print("""
Welcome to the Simple Agent!
          
This agent generates Python functions. 
Continue to give Simple Agent instructions until you are satisfied with the final code.
Plus, you can ask the agent to generate documentation and test cases.
          
Use the '>' character to signal a system command (instead of instructions for Simple Agent).

System Commands: 
'>help' to show this message
'>exit' to quit, 
'>save <filename>' to save conversation
'>code <filename>' to extract and save the last block code
'>history' to show conversation history
'>clear' to clear the screen
'>reset' to reset conversation

Examples: 
>save my_conversation.txt
>code my_code.py
>exit

Let's work on a Python function together! I'm here to do the coding.""")
        
def main():
    load_dotenv(override=True)
    api_key = os.environ.get(EXPECTED_API_KEY_NAME)
    if not api_key:
        print(f"Error: {EXPECTED_API_KEY_NAME} environment variable not set.")
        return

    system_message = """You are a helpful assistant that generates Python functions with documentation and test cases.
When asked to write a function, first write the function code with minimal comments.
When asked for documentation or tests, improve the existing function accordingly."""

    # Create the agent
    agent = FunkyCoder(api_key, system_message)
    is_first_user_input = True

    # Start the conversation
    
    while True:
        if is_first_user_input:
            show_help()
            is_first_user_input = False
            
        user_input = input("\nYou: ")

        # check for commands
        if user_input.startswith(">"):
            command = user_input[1:].strip()
            if command.lower() == "help":
                show_help()
                continue
            if command.lower() == "exit" or command.lower() == "quit":
                break # exit the loop
            elif command.lower().startswith("save "):
                filename = command[5:].strip()
                agent.save_to_file(filename)
                continue
            elif command.lower().startswith("code "):
                filename = command[5:].strip()
                agent.save_code_to_file(filename)
                continue
            elif command.lower() == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                continue
            elif command.lower() == "history":
                agent.show_history()
                continue
            elif command.lower() == "reset":
                agent.reset_conversation()
                continue
        else:
            response = agent.prompt(user_input)
            print(f"\nAgent: {response}")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()