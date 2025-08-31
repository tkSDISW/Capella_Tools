import sys
from pathlib import Path
from openai import OpenAI
from IPython.display import display, Markdown
from IPython.core.display import HTML
import numpy as np
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup
from ipywidgets import widgets
from IPython.display import display
import time
from IPython import get_ipython
from jupyter_ui_poll import ui_events
import time
from capella_tools.model_configurator import get_api_key, get_base_url, get_model


    

class EmbeddingManager :
    def __init__(self, model=None, base_url=None, api_key=None, config_name=None):
        """Initialize the analyzer with YAML content."""
        config = {}
        if config_name:
            config_path = Path.home() / ".secrets" / "model_configs.json"
            if config_path.exists():
                with config_path.open() as f:
                    configs = json.load(f)
                config = configs.get(config_name, {})
                if not config:
                    raise ValueError(f"No config named '{config_name}' found in model_configs.json.")
        elif model is None and base_url is None and api_key is None:
            config_path = Path.home() / ".secrets" / "model_configs.json"
            if config_path.exists():
                with config_path.open() as f:
                    configs = json.load(f)
                default_name = configs.get("_default")
                if default_name:
                    config = configs.get(default_name, {})
        
        def nonempty(value):
            return value if value and value.strip() else None
        
        self.api_key = nonempty(api_key) or nonempty(config.get("api_key")) or get_api_key()
        self.llm_url = nonempty(base_url) or nonempty(config.get("base_url")) or get_base_url()
        self.model = nonempty(model) or nonempty(config.get("model")) or get_model()
        
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key, base_url=self.llm_url)
        
        print(f"✅ EmbeddingManager initialized")
        print(f"🔐 API Key: {'Provided' if api_key else 'Loaded from secrets'}")
        print(f"🌐 Base URL: {self.llm_url or 'Default'}")
        print(f"🤖 Model: {self.model}")
        self.model = "text-embedding-3-small"
        self.embedding_file =''
        self.model_file = ''
        self.selected_objects_output = []  # Stores selected objects persistently
        self.ranked_objects = []  # Store ranked results from the query    
        self.selection_done = False  # ✅ Flag to signal completion
        
    def save_embeddings(self ):
        """Save embeddings to a file."""
        with open(self.embedding_file, "w") as f:
            json.dump(self.embeddings, f)

    def set_files(self, model_file, embedding_file ) :
        """Set model file and ebedding fie."""
        self.model_file = model_file
        self.embedding_file = embedding_file

    def is_embedding_up_to_date(self):
        """Checks if the embedding file exists and is up to date with the model."""
        aird_file = self.model_file
        base = Path(aird_file).with_suffix("")  # Strip .aird
        capella_file = base.with_suffix(".capella")
        afm_file = base.with_suffix(".afm")    
        # ✅ Ensure embedding file exists before accessing it
        if not os.path.exists(self.embedding_file):
            print("❌ Embedding file not found. A new one will be created.")
            return False
        if not os.path.exists(aird_file):
            print("❌ Model .aird file not found. Check the file path.")
            return False
        if not os.path.exists(afm_file):
            print("❌ Model .afm file not found. Check the file path.")
            return False
        if not os.path.exists(capella_file):
            print("❌ Modle .capella file not found. Check the file path.")
            return False
    
        # ✅ Compare timestamps only if both files exist
        aird_file = self.model_file
        base = Path(aird_file).with_suffix("")  # Strip .aird
        capella_file = base.with_suffix(".capella")
        afm_file = base.with_suffix(".afm")
        embedding_time = os.path.getmtime(self.embedding_file)
        for related_file in (aird_file,capella_file, afm_file):
            related_time = os.path.getmtime(related_file)
            if related_time > embedding_time:
                return False  # One of the files is newer than .aird

        return True  # .aird is at least as recent as .capella and .afm


    
    
    def generate_object_embeddings(self, objects):
        for obj in objects:
            # Combine metadata into a single text string
            metadata_text = f"{obj['name']} {obj['type']} {obj['phase']} {obj['source_component']} {obj['target_component']}"
            metadata_text =  metadata_text.replace("\n", " ")
            obj["embedding"] = self.client.embeddings.create(input = [metadata_text], model=self.model).data[0].embedding
           
        self.embeddings = objects
        print("embeddings generated")
        return objects

    def create_model_embeddings(self, model) :
        def get_project_requirements(model):
            """ Get all requirement not located in a phase and created by TC requirement integration"""
            all_requirements = []
            
            def collect_requirements(module):
                """Recursively collect all requirements from a CapellaModuprintle."""
                #print(module)
                if hasattr(module, "requirements"):
                    for req in module.requirements:
                        all_requirements.append(req)
            
                if hasattr(module, "owned_modules"):
                    for submodule in module.owned_modules:
                        collect_requirements(submodule)
            
                if hasattr(module, "folders"):
                    for folder in module.folders:
                        collect_requirements(folder)
            
            
            # Search through all extensions in the project
            for ext in model.project.model_root.extensions:
                for subext in getattr(ext, "extensions", []):
                    if getattr(subext, "xtype", "") == "CapellaRequirements:CapellaModule":
                        collect_requirements(subext)
            return all_requirements

        def get_req_info(object, phase ) :
            object_info = {
                    "uuid": object.uuid,
                    "name": object.long_name,
                    "type": type(object).__name__,
                    "phase" : phase,
                    "source_component": "",
                    "target_component": "" 
                }
            return object_info
        
        def get_object_info(object, phase ) :
            object_info = {
                    "uuid": object.uuid,
                    "name": object.name,
                    "type": type(object).__name__,
                    "phase" : phase,
                    "source_component": "",
                    "target_component": "" 
                }
            return object_info

        
        def get_physical_component_info(object, phase ) :
            object_info = {
                    "uuid": object.uuid,
                    "name": object.name,
                    "type": f"{type(object).__name__}-{object.nature}",
                    "phase" : phase,
                    "source_component": "",
                    "target_component": "" 
                }
            return object_info
        def get_component_exchange_info(object, phase ) :
            object_info = {
                    "uuid": object.uuid,
                    "name": object.name,
                    "type": type(object).__name__,
                    "phase" : phase,
                    "source_component": obj.source.owner.name if obj.source and obj.source.owner else None,
                    "target_component": obj.target.owner.name if obj.target and obj.target.owner else None 
                }
            return object_info


        def get_diagram_info(object, phase ) :
            object_info = {
                    "uuid": object.uuid,
                    "name": object.name,
                    "type": type(object).__name__,
                    "phase" : phase,
                    "source_component": "",
                    "target_component": ""
                }
            return object_info
            
        def add_unique_object(obj_list, new_obj):
            """
            Adds a new object to the list if its UUID is not already present.
        
            :param obj_list: List of existing objects.
            :param new_obj: Object to potentially add to the list.
            """
            if not any(obj.get('uuid') == new_obj.get('uuid') for obj in obj_list):       
                obj_list.append(new_obj)

        if self.is_embedding_up_to_date() :
            print("Loading embeddings")
            self.load_embeddings()
        else : 
            print("Creating Embeddings")
            object_data = []
            phase = "Project"
            for component in get_project_requirements(model):  
                object_info = get_req_info(component,phase)
                add_unique_object(object_data,object_info)
            #OA 
            phase = "Operational Analysis OA"
            for component in model.oa.all_requirements:  
                object_info = get_req_info(component,phase)
                add_unique_object(object_data,object_info)
            for component in model.oa.all_entities:  
                object_info = get_object_info(component,phase)
                add_unique_object(object_data,object_info)
            for obj in model.oa.all_activities:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.oa.all_capabilities:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.oa.all_entity_exchanges:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.oa.all_processes:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.oa.diagrams:  
                object_info = get_diagram_info(obj,phase)
                add_unique_object(object_data,object_info)
            #SA
            phase = "System Analysis SA"
            for component in model.oa.all_requirements:  
                object_info = get_req_info(component,phase)
                add_unique_object(object_data,object_info)
            for component in model.sa.all_components: 
                object_info = get_object_info(component,phase)
                add_unique_object(object_data,object_info)
            for obj in model.sa.all_capabilities:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.sa.all_function_exchanges:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.sa.all_functions:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.sa.all_missions:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.sa.all_functional_chains:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.sa.diagrams:  
                object_info = get_diagram_info(obj,phase)
                add_unique_object(object_data,object_info)
            #LA
            phase = "Logical Architecture LA"
            for component in model.oa.all_requirements:  
                object_info = get_req_info(component,phase)
                add_unique_object(object_data,object_info) 
            for obj in model.la.all_capabilities:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for component in model.la.all_components:  
                object_info = get_object_info(component,phase)
                add_unique_object(object_data,object_info)
            for obj in model.la.all_functions:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.la.all_function_exchanges:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.la.all_functional_chains:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.la.all_interfaces:  
                object_info =  get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.la.component_exchanges:  
                object_info =  get_component_exchange_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.la.actor_exchanges:  
                object_info =  get_component_exchange_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.la.diagrams:  
                object_info = get_diagram_info(obj,phase)
                add_unique_object(object_data,object_info)
            #PA
            phase = "Physical Architecture PA"
            for component in model.oa.all_requirements:  
                object_info = get_req_info(component,phase)
                add_unique_object(object_data,object_info) 
            for component in model.pa.all_components:  
                object_info = get_physical_component_info(component,phase)
                add_unique_object(object_data,object_info)
            for obj in model.pa.all_functions:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.pa.all_functional_chains:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.pa.all_function_exchanges:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.pa.all_capabilities:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.pa.all_component_exchanges:  
                object_info = get_component_exchange_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.pa.all_physical_exchanges:  
                object_info = get_component_exchange_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.pa.all_physical_links:  
                object_info = get_component_exchange_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.pa.all_physical_paths:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.pa.all_physical_exchanges:  
                object_info = get_component_exchange_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.pa.diagrams:  
                object_info = get_diagram_info(obj,phase)
                add_unique_object(object_data,object_info)
            
            model_embeddings = self.generate_object_embeddings(object_data)
            
            print("Saving embeddings")
            self.save_embeddings()



    
    def load_embeddings(self):
        """Load embeddings from a file."""
        with open(self.embedding_file, "r") as f:
            self.embeddings = json.load(f)
            print("embeddings loaded.")

    # Define a cosine similarity function
    def cosine_similarity(self, vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    # Find similar objects based on the query
    def find_similar_objects(self, query,  top_n=10):
        query_embedding = self.client.embeddings.create(input = [query], model=self.model).data[0].embedding
        similarities = []
        
        for obj in self.embeddings:
            similarity = self.cosine_similarity(query_embedding, obj["embedding"])
            similarities.append((obj, similarity))
        
        # Sort by similarity in descending order
        similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
        return similarities[:top_n]



    def locate_possible_objects(self,prompt):
        """
        Interactive function to query objects, review responses, and select indices for further processing.
        
        :param model_embedding_manager: The manager object to handle embedding and similarity queries.
        :return: List of selected objects based on indices.
        """

        # Step 2: Filter and rank objects
        ranked_objects = self.find_similar_objects(prompt)
        
        # Step 3: Display ranked objects
        print("\nThis is a list of ranked Objects Based on Query:")
        for i, (obj, similarity) in enumerate(ranked_objects):
            print(f"Index: {i}, Name: {obj['name']}, Similarity: {similarity:.2f}, "
                  f"Type: {obj['type']},Phase: {obj['phase']}, Source: {obj.get('source_component', 'N/A')}, "
                  f"Target: {obj.get('target_component', 'N/A')}")
        #print(ranked_objects)
        return ranked_objects



    def interactive_query_and_selection_widgets(self):
        """
        Interactive widget-based function for querying objects and selecting multiple results.
        Uses `jupyter_ui_poll` to ensure non-blocking UI interactions.
        """
        self.selection_done = False  # ✅ Reset flag before starting

        # Create input widget for user query
        query_input = widgets.Text(
            placeholder="Enter query for objects...",
            layout=widgets.Layout(width="80%")
        )
        
        # Create output widget to display ranked results
        output_area = widgets.Output()
        
        # Create a multi-select widget
        multi_select = widgets.SelectMultiple(
            options=[],
            description="Select:",
            layout=widgets.Layout(width="80%", height="200px")
        )
        
        # Create submit and reset buttons
        submit_button = widgets.Button(
            description="Submit Selection",
            button_style="primary",
            icon="check"
        )
        
        reset_button = widgets.Button(
            description="Reset",
            button_style="warning",
            icon="times"
        )

        # Function to handle query submission (stores ranked objects)
        def on_query_submit(change):
            output_area.clear_output()
            query = query_input.value.strip()
            
            if not query:
                with output_area:
                    print("⚠️ Please enter a query.")
                return
            
            # Get ranked objects **only once** and store them
            self.ranked_objects = self.find_similar_objects(query)
            
            # Update multi-select options dynamically
            multi_select.options = [(f"{obj['name']} ({obj['type']})", i) for i, (obj, _) in enumerate(self.ranked_objects)]
            
            with output_area:
                print("\n🔍 Ranked Objects Based on Query:")
                for i, (obj, similarity) in enumerate(self.ranked_objects):
                    print(f"{i}: {obj['name']} | Type: {obj['type']} | Phase: {obj['phase']} | Similarity: {similarity:.2f}")

        # Function to handle submission (uses stored ranked objects)
        def on_submit_clicked(b):
            output_area.clear_output()
            selected_indices = list(multi_select.value)
        
            if not selected_indices:
                with output_area:
                    print("⚠️ No objects selected.")
                return
        
            # Retrieve selected objects from stored ranked results
            self.selected_objects_output = [self.ranked_objects[i][0] for i in selected_indices]
        
            with output_area:
                print("\n✅ Selected Object Details:")
                for obj in self.selected_objects_output:
                    print(f"\n🔹 Name: {obj['name']}")
                    print(f"   Type: {obj['type']}")
                    print(f"   Phase: {obj['phase']}")
                    print(f"   Source Component: {obj.get('source_component', 'N/A')}")
                    print(f"   Target Component: {obj.get('target_component', 'N/A')}")
            
            # ✅ Signal that selection is complete
            self.selection_done = True  

        # Function to reset selection
        def on_reset_clicked(b):
            query_input.value = ""
            multi_select.options = []
            output_area.clear_output()
            self.ranked_objects = []  # Clear stored results
            self.selected_objects_output = []  # Clear selections
            self.selection_done = False  # Reset completion flag

        # Attach handlers to widgets
        query_input.observe(on_query_submit, names="value")
        submit_button.on_click(on_submit_clicked)
        reset_button.on_click(on_reset_clicked)
        
        # Display widgets
        display(widgets.VBox([query_input, multi_select, submit_button, reset_button, output_area]))
        # ✅ Wait using `ui_events()` to keep UI responsive
        print("Waiting for selection...")
        with ui_events() as poll:
            while not self.selection_done:
                poll(10)  # ✅ Process up to 10 UI events (keeps UI interactive)
                time.sleep(1)  # ✅ Non-blocking pause before rechecking


        

    
    def get_selected_objects(self):
        """
        Retrieve the selected objects after the widget interaction is complete.
        """
        return self.selected_objects_output

    def interactive_query_and_selection(self):
        """
        Interactive function to query objects, review responses, and select indices for further processing.
        
        :param model_embedding_manager: The manager object to handle embedding and similarity queries.
        :return: List of selected objects based on indices.
        """
        embeddings = self.embeddings
        while True:
            # Step 1: Prompt for query
            query = input("Enter query for objects or diagrams to be analyzed: ")
    
            # Step 2: Filter and rank objects
            ranked_objects = self.find_similar_objects(query)
    
            # Step 3: Display ranked objects
            print("\nThis is a list of ranked Objects Based on Query:")
            for i, (obj, similarity) in enumerate(ranked_objects):
                print(f"Index: {i}, Name: {obj['name']}, Similarity: {similarity:.2f}, "
                      f"Type: {obj['type']},Phase: {obj['phase']}, Source: {obj.get('source_component', 'N/A')}, "
                      f"Target: {obj.get('target_component', 'N/A')}")
    
            # Step 4: Ask for user action
            user_input = input("\nEnter the indices of the selected objects (comma-separated), or any non-integer input to retry: ")
    
            # Check if the input contains only integers
            if not all(part.strip().isdigit() for part in user_input.split(",")):
                # Retry if any non-integer input is detected
                print("\nNon-integer input detected. Retrying with a new query.")
                continue
    
            try:
                # Parse selected indices
                selected_indices = [int(i.strip()) for i in user_input.split(",")]
                selected_objects = [ranked_objects[i][0] for i in selected_indices]
                #print("\nSelected Objects:")
                #for obj in selected_objects:
                #    print(f"Name: {obj['name']}, Type: {obj['type']}")
                return selected_object
            except (ValueError, IndexError):
                # Handle invalid input
                print("\nInvalid input. Please enter valid indices or retry.")



    def query_and_select_top_objects(self, prompt, top_n=20):
        """
        Query and return top N ranked objects based on similarity.
    
        :param prompt: The query string describing what to look for.
        :param top_n: Number of top ranked objects to return.
        :return: List of top N selected objects.
        """
        # Step 1: Rank objects based on the query
        ranked_objects = self.find_similar_objects(prompt)
    
        # Step 2: Display ranked objects
        print("\nThis is a list of ranked Objects Based on Query:")
        for i, (obj, similarity) in enumerate(ranked_objects[:top_n]):
            print(f"Index: {i}, Name: {obj['name']}, Similarity: {similarity:.2f}, "
                  f"Type: {obj['type']}, Phase: {obj['phase']}, "
                  f"Source: {obj.get('source_component', 'N/A')}, "
                  f"Target: {obj.get('target_component', 'N/A')}")
    
        # Step 3: Return the top N objects
        selected_objects = [obj for obj, _ in ranked_objects[:top_n]]
        return selected_objects

