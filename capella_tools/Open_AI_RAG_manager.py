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
from IPython.core.display import Javascript
from jupyter_ui_poll import ui_events
import time
import ast
import re
import networkx as nx
import plotly.graph_objects as go
from pyvis.network import Network
import nbformat
from docx import Document
import PyPDF2

Network(notebook=True)

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
    ALLOWED_EXTENSIONS = {'.yaml', '.yml', '.txt', '.xml', '.json', '.html', '.pdf', '.docx'}
    TEXT_BASED_EXTS = {'.yaml', '.yml', '.txt', '.xml', '.json', '.html'}
    PDF_EXTS = {'.pdf'}
    DOCX_EXTS = {'.docx'}
    def __init__(self, yaml_content):
        """Initialize the analyzer with YAML content."""
        try:
            self.api_key = get_api_key()
            print("OpenAI API Key retrieved successfully.")
        except (FileNotFoundError, ValueError) as e:
            print(e)
            sys.exit(1)  # Exit with an error code

        self.yaml_content = yaml_content
        self.chat_active = True  # ✅ Flag to manage chat session
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
        display(Markdown(f"**Your prompt:** {user_prompt}"))


    def follow_up_prompt(self, user_prompt):
        """Add a follow-up prompt continuing the conversation."""
        self.messages.append({"role": "user", "content": user_prompt})
        display(Markdown(f"**Your prompt:** {user_prompt}"))

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
            if "<table" in assistant_message or "<html" in assistant_message:
                display(HTML(assistant_message))
            else:
                display(Markdown(f"**ChatGPT Response:**\n\n{assistant_message}\n"))
            return assistant_message
            
        except Exception as e:
            return f"Error communicating with OpenAI API: {e}"

    
    def interactive_chat(self):
        """Start an enhanced interactive chat session using `jupyter_ui_poll`."""
        print("Starting interactive chat...")
    
        chat_history = widgets.Output()
        user_input = widgets.Textarea(
            placeholder="Type your prompt...",
            rows=3,
            layout=widgets.Layout(width="100%", border="2px solid #4A90E2", border_radius="8px",
                                  padding="12px", background_color="#F7F9FC", 
                                  box_shadow="3px 3px 10px rgba(0, 0, 0, 0.1)")
        )
    
        send_button = widgets.Button(description="Execute", button_style="primary")
        exit_button = widgets.Button(description="Exit", button_style="danger")
    
        # File picker from current directory
        file_list = [f for f in os.listdir(os.getcwd())
             if os.path.isfile(f) and os.path.splitext(f)[1].lower() in self.ALLOWED_EXTENSIONS]
        file_dropdown = widgets.Dropdown(
            options=[""] + file_list,
            description="Load file:",
            layout=widgets.Layout(width="auto")
        )
    
        def load_file(_):
            filename = file_dropdown.value
            if not filename:
                return
    
            ext = os.path.splitext(filename)[1].lower()
            if ext not in self.ALLOWED_EXTENSIONS:
                with chat_history:
                    display(Markdown(f"⚠️ **Unsupported file type `{ext}`. Allowed types:** {', '.join(self.ALLOWED_EXTENSIONS)}"))
                return
    
            try:
                if ext in self.TEXT_BASED_EXTS:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                elif ext in self.PDF_EXTS:
                    with open(filename, 'rb') as f:
                        reader = PyPDF2.PdfReader(f)
                        content = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
                elif ext in   self.DOCX_EXTS:
                    doc = Document(filename)
                    content = "\n".join([p.text for p in doc.paragraphs])
                else:
                    content = ""
    
                self.messages.append({
                    "role": "user",
                    "content": f"File `{filename}` was added for analysis:\n---\n{content}\n---"
                })
    
                with chat_history:
                    display(Markdown(f"✅ **File `{filename}` was added and appended for analysis.**"))
 
            except Exception as e:
                with chat_history:
                    display(Markdown(f"❌ Error reading `{filename}`: {str(e)}"))
    
        file_dropdown.observe(load_file, names="value")
    
        def send_message(_):
            prompt = user_input.value.strip()
            if not prompt:
                return
    
            with chat_history:
                self.follow_up_prompt(prompt)
                display(Markdown(f"**Generating a response..** "))
                chatbot_response = self.get_response()
                
    
            user_input.value = ""
    
        def exit_chat(_):
            self.chat_active = False
    
        send_button.on_click(send_message)
        exit_button.on_click(exit_chat)
    
        display(chat_history, user_input,
                widgets.HBox([send_button, exit_button]),
                file_dropdown)
    
        print("Waiting for chat interactions...")
        with ui_events() as poll:
            while self.chat_active:
                poll(10)
                time.sleep(1)




    def generate_pyvis_graph_from_relations(self, relations, output_file="graph.html"):
        """
        Generate a draggable, labeled, arrowed graph using PyVis with tighter spacing.
        """
        net = Network(height="750px", width="100%", directed=True, notebook=True, cdn_resources="in_line")

        
        # Optional tighter layout (or skip for default)
        net.set_options("""
        var options = {
          "physics": {
            "barnesHut": {
              "springLength": 90
            }
          },
          "edges": {
            "arrows": {"to": {"enabled": true}},
            "font": {"size": 14, "align": "middle"},
            "color": {"color": "gray"}
          }
        }
        """)
    
        added_nodes = set()
        for src, tgt, lbl in relations:
            for node in (src, tgt):
                if node not in added_nodes:
                    net.add_node(node, label=node, shape="ellipse")
                    added_nodes.add(node)
            net.add_edge(src, tgt, label=lbl)
        net.show(output_file)


    def analyze_and_generate_graph(self):
        """
        Analyze YAML content, extract relations, and generate a graph.
        If extraction fails, fallback to text summary display.
        """
        special_prompt = """
Analyze the YAML content and extract relationships suitable for a graph.

- Each relationship should be a tuple: (source, target, label).
- Use simple labels like 'abstract type of','property value group','property value','constrains','linked model element',"region','states','transitions','outgoing transition','incoming transtion','do function','entry function','exits function','triggers','source state','destination state','after function','source','target','involves','exchange items','exchanges','allocated to', 'involving','components','deployed to','port','state machine','entities', 'elements of'.
- Use ref_id to navigate primary_id but do not list them in tuples.
- Output ONLY a Python list of these tuples.
- No explanation, no extra text, just the list in Python syntax.
"""

        print("Sending prompt to extract graphable relations...")
        self.initial_prompt(special_prompt)

        relations_text = self.get_response()

        try:
            print("Relations Text:",relations_text)
            cleaned_text = re.sub(r"^```[a-zA-Z]*\n", "", relations_text.strip())
            cleaned_text = cleaned_text.replace("```", "").strip()
            relations = ast.literal_eval(cleaned_text)
            #print("Relations:",relations)
            if isinstance(relations, list) and all(isinstance(r, tuple) for r in relations):
                #print("Relations extracted successfully. Drawing graph...")
                #self.generate_interactive_graph_from_relation(relations)
                self.generate_pyvis_graph_from_relations(relations)
            else:
                print("Relations:",relations_text)
                raise ValueError("Extracted data is not a valid list of tuples.")
        except Exception as e:
            print(f"Failed to parse structured relations ({e}). Falling back to text summary.")

            # Fallback: Ask for a textual summary instead
            fallback_prompt = """
Please summarize the key conclusions from the YAML content in a short bullet list.
Format it nicely for .html display.
"""
            self.initial_prompt(fallback_prompt)
            fallback_response = self.get_response()

            # Display the fallback Markdown
            display(HTML(f"Fallback Summary:**\n\n{fallback_response}"))
            

