import sys
from pathlib import Path
from openai import OpenAI
from IPython.display import display, Markdown
from IPython.core.display import HTML
from ipywidgets import widgets
import numpy as np
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
import asyncio
from ipywidgets import widgets
from IPython.display import display

def get_api_key():
    """Retrieve the OpenAI API key from a hidden file."""
    home_dir = Path.home()
    key_file = home_dir / ".secrets" / "openai_api_key.txt"

    if not key_file.exists():
        raise FileNotFoundError(
            f"API Key file not found at {key_file}. "
            "Please ensure the key is saved correctly."
        )

    with key_file.open("r") as f:
        api_key = f.read().strip()

    if not api_key:
        raise ValueError("API Key file is empty. Provide a valid API key.")

    return api_key


class ChatGPTAnalyzer:
    def __init__(self, yaml_content):
        """Initialize the analyzer with YAML content."""
        try:
            self.api_key = get_api_key()
            print("OpenAI API Key retrieved successfully.")
        except (FileNotFoundError, ValueError) as e:
            print(e)
            sys.exit(1)  # Exit with an error code

        self.yaml_content = yaml_content
        self.messages = [
            {
                "role": "system",
                "content": f"You are an expert in analyzing YAML files for system design. Here is the YAML file:\n---\n{self.yaml_content}\n---",
            }
        ]

    def _construct_prompt(self, user_prompt):
        """Construct the full prompt with YAML content."""
        return f"""
The following is a YAML file describing a system design component in Capella:
---
{self.yaml_content}
---
{user_prompt}
Please format the response in .html format.
"""

    def initial_prompt(self, user_prompt):
        """Set the initial user prompt in the conversation."""
        user_prompt = user_prompt + " Format the response in .html format."
        self.messages.append({"role": "user", "content": user_prompt})

    def follow_up_prompt(self, user_prompt):
        """Add a follow-up prompt continuing the conversation."""
        self.messages.append({"role": "user", "content": user_prompt})

    def get_response(self):
        """Send messages to ChatGPT and get a response."""
        try:
            client = OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                messages=self.messages,
                model="gpt-4o",
            )
            assistant_message = response.choices[0].message.content
            self.messages.append({"role": "assistant", "content": assistant_message})

            soup = BeautifulSoup(assistant_message, "html.parser")

            # Remove <script> and <style> tags
            for tag in soup(["script", "style"]):
                tag.decompose()

            # Render the cleaned HTML
            assistant_message = str(soup)
            return assistant_message

        except Exception as e:
            return f"Error communicating with OpenAI API: {e}"

    def interactive_chat(self):
        """Start an interactive chat session."""
        print("Starting interactive chat...")
        while True:
            user_prompt = input("Enter your prompt (or type 'exit' to quit): ")

            if user_prompt.lower() == "exit":
                print("Exiting...")
                break

            self.follow_up_prompt(user_prompt)
            response = self.get_response()

            display(Markdown(f"**Your Prompt:**\n\n{user_prompt}\n"))
            if "<table" in response or "<html" in response:
                display(HTML(response))  # Render HTML
            else:
                display(Markdown(f"**ChatGPT Response:**\n\n{response}\n"))

