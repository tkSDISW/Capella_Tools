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


class EmbeddingManager :
    def __init__(self):
        """Initialize the analyzer with YAML content."""
        try:
            self.api_key = get_api_key()
            print("OpenAI API Key retrieved successfully.")
        except (FileNotFoundError, ValueError) as e:
            print(e)
            sys.exit(1)  # Exit with an error code

       
        self.client = OpenAI(
            api_key=self.api_key,  # This is the default and can be omitted
            )
        self.model = "text-embedding-3-small"
        self.embedding_file =''
        self.model_file = ''
        self.selected_objects_output = []  # Stores selected objects persistently
        self.ranked_objects = []  # Store ranked results from the query    
        
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
        
        # ✅ Ensure embedding file exists before accessing it
        if not os.path.exists(self.embedding_file):
            print("❌ Embedding file not found. A new one will be created.")
            return False
    
        if not os.path.exists(self.model_file):
            print("❌ Model file not found. Check the file path.")
            return False
    
        # ✅ Compare timestamps only if both files exist
        model_time = os.path.getmtime(self.model_file)
        embedding_time = os.path.getmtime(self.embedding_file)
    
        return embedding_time >= model_time
    
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
        def get_component_exchange_info(object, phase ) :
            object_info = {
                    "uuid": object.uuid,
                    "name": object.name,
                    "type": type(object).__name__,
                    "phase" : phase,
                    "source_component": obj.source.owner.name,
                    "target_component": obj.target.owner.name 
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
            #OA  
            phase = "Operational Analysis OA"
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
            for obj in model.la.all_capabilities:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for component in model.la.all_components:  
                object_info = get_object_info(component,phase)
                add_unique_object(object_data,object_info)
            for obj in model.la.all_functions:  
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
            for component in model.pa.all_components:  
                object_info = get_object_info(component,phase)
                add_unique_object(object_data,object_info)
            for obj in model.pa.all_functions:  
                object_info = get_object_info(obj,phase)
                add_unique_object(object_data,object_info)
            for obj in model.pa.all_functional_chains:  
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

    async def interactive_query_and_selection_widgets(self):
        """
        Interactive widget-based function for querying objects and selecting multiple results.
        Stores the selected objects for later retrieval and **allows execution to continue after submission**.
        """
        self.future = asyncio.Future()  # Future to wait for user selection

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
            
            # Update multi-select options
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
            
            # ✅ Resolve the Future to allow execution to continue
            if not self.future.done():
                self.future.set_result(self.selected_objects_output)

        # Function to reset selection
        def on_reset_clicked(b):
            query_input.value = ""
            multi_select.options = []
            output_area.clear_output()
            self.ranked_objects = []  # Clear stored results
            self.selected_objects_output = []  # Clear selections

        # Attach handlers to widgets
        query_input.observe(on_query_submit, names="value")
        submit_button.on_click(on_submit_clicked)
        reset_button.on_click(on_reset_clicked)
        
        # Display widgets
        display(widgets.VBox([query_input, multi_select, submit_button, reset_button, output_area]))

        # ✅ Wait for selection to complete before continuing execution
        return await self.future





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
                return selected_objects
            except (ValueError, IndexError):
                # Handle invalid input
                print("\nInvalid input. Please enter valid indices or retry.")


