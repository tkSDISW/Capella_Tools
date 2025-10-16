# Copyright Siemens AG
# Licensed under the Apache License, Version 2.0 (see full text in LICENSES/Apache-2.0.txt)

# Dot-files are licensed under CC0-1.0 (see full text in LICENSES/CC0-1.0.txt)

# To provide the same look and feel across platforms, this library is bundled
# with the OpenSans font (capellambse/OpenSans-Regular.ttf).
# The OpenSans font is Copyright 2020 The Open Sans Project Authors,
# licensed under OFL-1.1 (see full text in LICENSES/OFL-1.1.txt)

import sys
from pathlib import Path
from openai import OpenAI
from IPython.display import display, Markdown
from IPython.core.display import HTML
import numpy as np
import json
import os
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from ipywidgets import widgets
from IPython.display import display
import time
from IPython import get_ipython
from jupyter_ui_poll import ui_events
import time
from capella_tools.model_configurator import get_api_key, get_base_url, get_model


class EmbeddingManager:
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
            return value if value and str(value).strip() else None

        self.api_key = nonempty(api_key) or nonempty(config.get("api_key")) or get_api_key()
        self.llm_url = nonempty(base_url) or nonempty(config.get("base_url")) or get_base_url()
        self.model = nonempty(model) or nonempty(config.get("model")) or get_model()

        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key, base_url=self.llm_url)

        print(f"✅ EmbeddingManager initialized")
        print(f"🔐 API Key: {'Provided' if api_key else 'Loaded from secrets'}")
        print(f"🌐 Base URL: {self.llm_url or 'Default'}")
        print(f"🤖 Model: {self.model}")
        # Preserve prior behavior: override to embeddings model
        self.model = "text-embedding-3-small"

        self.embedding_file = ''
        self.model_file = ''
        self.selected_objects_output = []  # Stores selected objects persistently
        self.ranked_objects = []          # Store ranked results from the query
        self.selection_done = False       # ✅ Flag to signal completion
        self.embeddings = []              # The list of items currently in memory
        self._last_loaded_meta = None     # Meta from file (if any)

    # ---------- File + meta handling ----------

    def _capella_model_name_from_aird(self) -> str:
        """Return the Capella model name derived from the .aird filename stem."""
        if not self.model_file:
            return ""
        return Path(self.model_file).stem

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")

    def save_embeddings(self):
        """Save embeddings + meta to a JSON file (backward compatible loader)."""
        meta = {
            "created_at": self._now_iso(),
            "llm_model": self.model,
            "capella_model_name": self._capella_model_name_from_aird(),
        }
        payload = {
            "meta": meta,
            "items": self.embeddings,
        }
        with open(self.embedding_file, "w", encoding="utf-8") as f:
            json.dump(payload, f)
        self._last_loaded_meta = meta

    def set_files(self, model_file, embedding_file):
        """Set model (.aird) file and embedding file."""
        self.model_file = model_file
        self.embedding_file = embedding_file

    def _read_embedding_file(self):
        """Internal: read the embedding file JSON and normalize shape."""
        with open(self.embedding_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Backward compatibility: old files were just a list
        if isinstance(data, list):
            meta = None
            items = data
        else:
            meta = data.get("meta")
            items = data.get("items", [])

        return meta, items

    def is_embedding_up_to_date(self):
        """
        Check whether the current embedding file matches the model + metadata
        and is newer than any related Capella files (.aird/.capella/.afm).

        Rules:
        - embedding file exists
        - meta.llm_model == self.model
        - meta.capella_model_name == stem(self.model_file)
        - created_at >= last modified time of any related model files
        """
        aird_file = self.model_file
        if not self.embedding_file or not aird_file:
            print("❌ Model or embedding file path not set.")
            return False

        base = Path(aird_file).with_suffix("")  # Strip .aird
        capella_file = base.with_suffix(".capella")
        afm_file = base.with_suffix(".afm")

        # Ensure all model files exist
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
            print("❌ Model .capella file not found. Check the file path.")
            return False

        try:
            meta, _ = self._read_embedding_file()
        except Exception as e:
            print(f"❌ Failed to read embedding file JSON: {e}")
            return False

        # If the file is an old-format list (no meta), force regeneration
        if not meta:
            print("ℹ️ Embedding file is legacy format (no meta). Regeneration required.")
            return False

        expected_name = self._capella_model_name_from_aird()
        if meta.get("llm_model") != self.model:
            print(f"ℹ️ LLM model changed: file={meta.get('llm_model')} current={self.model}")
            return False
        if meta.get("capella_model_name") != expected_name:
            print(f"ℹ️ Capella model name mismatch: file={meta.get('capella_model_name')} current={expected_name}")
            return False

        # Compare created_at to model files mtimes
        try:
            created = meta.get("created_at")
            created_ts = datetime.fromisoformat(created.replace("Z", "+00:00")).timestamp()
        except Exception:
            print("ℹ️ Invalid or missing created_at in meta; regenerating.")
            return False

        for related in (aird_file, capella_file, afm_file):
            if os.path.getmtime(related) > created_ts:
                print(f"ℹ️ Model file newer than embeddings: {related}")
                return False

        # If we get here, we consider it up to date
        return True

    def get_embedding_file_info(self):
        """
        Return a small dict with the path, meta, and count.
        Useful for logging or simple artifact creation.
        """
        if not os.path.exists(self.embedding_file):
            return {"path": self.embedding_file, "meta": None, "count": 0}

        meta, items = self._read_embedding_file()
        # If legacy, meta will be None; fabricate a minimal meta for convenience
        if meta is None:
            meta = {
                "created_at": None,
                "llm_model": None,
                "capella_model_name": self._capella_model_name_from_aird(),
            }
        return {"path": self.embedding_file, "meta": meta, "count": len(items)}

    def retrieve_embedding_artifact(self):
        """
        Return a tool-friendly artifact describing the embedding file.
        Keeps things generic so agents can pass it around.
        """
        info = self.get_embedding_file_info()
        return {
            "type": "embedding_file",
            "path": info["path"],
            "meta": info["meta"],
            "count": info["count"],
            "display_name": f"Embeddings ({info['count']}) - {info['meta'].get('capella_model_name') if info['meta'] else 'Unknown'}"
        }

    # ---------- Embedding creation / loading ----------

    def generate_object_embeddings(self, objects):
        for obj in objects:
            # Combine metadata into a single text string
            metadata_text = f"{obj['name']} {obj['type']} {obj['phase']} {obj['source_component']} {obj['target_component']}"
            metadata_text = metadata_text.replace("\n", " ")
            obj["embedding"] = self.client.embeddings.create(
                input=[metadata_text],
                model=self.model
            ).data[0].embedding

        self.embeddings = objects
        print("embeddings generated")
        return objects

    def create_model_embeddings(self, model):
        def get_project_requirements(model):
            """Get all requirements not located in a phase and created by TC requirement integration"""
            all_requirements = []

            def collect_requirements(module):
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

        def get_req_info(object, phase):
            return {
                "uuid": object.uuid,
                "name": object.long_name,
                "type": type(object).__name__,
                "phase": phase,
                "source_component": "",
                "target_component": ""
            }

        def get_object_info(object, phase):
            return {
                "uuid": object.uuid,
                "name": object.name,
                "type": type(object).__name__,
                "phase": phase,
                "source_component": "",
                "target_component": ""
            }

        def get_physical_component_info(object, phase):
            return {
                "uuid": object.uuid,
                "name": object.name,
                "type": f"{type(object).__name__}-{object.nature}",
                "phase": phase,
                "source_component": "",
                "target_component": ""
            }

        def get_component_exchange_info(object, phase):
            # bugfix: use 'object' param rather than undefined 'obj'
            return {
                "uuid": object.uuid,
                "name": object.name,
                "type": type(object).__name__,
                "phase": phase,
                "source_component": object.source.owner.name if getattr(object, "source", None) and getattr(object.source, "owner", None) else None,
                "target_component": object.target.owner.name if getattr(object, "target", None) and getattr(object.target, "owner", None) else None
            }

        def get_diagram_info(object, phase):
            return {
                "uuid": object.uuid,
                "name": object.name,
                "type": type(object).__name__,
                "phase": phase,
                "source_component": "",
                "target_component": ""
            }

        def add_unique_object(obj_list, new_obj):
            if not any(obj.get('uuid') == new_obj.get('uuid') for obj in obj_list):
                obj_list.append(new_obj)

        if self.is_embedding_up_to_date():
            print("Loading embeddings")
            self.load_embeddings()
        else:
            print("Creating Embeddings")
            object_data = []

            # Project-level requirements
            phase = "Project"
            for component in get_project_requirements(model):
                add_unique_object(object_data, get_req_info(component, phase))

            # OA
            phase = "Operational Analysis OA"
            for component in model.oa.all_requirements:
                add_unique_object(object_data, get_req_info(component, phase))
            for component in model.oa.all_entities:
                add_unique_object(object_data, get_object_info(component, phase))
            for obj in model.oa.all_activities:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.oa.all_capabilities:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.oa.all_entity_exchanges:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.oa.all_processes:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.oa.diagrams:
                add_unique_object(object_data, get_diagram_info(obj, phase))

            # SA
            phase = "System Analysis SA"
            for component in model.oa.all_requirements:
                add_unique_object(object_data, get_req_info(component, phase))
            for component in model.sa.all_components:
                add_unique_object(object_data, get_object_info(component, phase))
            for obj in model.sa.all_capabilities:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.sa.all_function_exchanges:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.sa.all_functions:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.sa.all_missions:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.sa.all_functional_chains:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.sa.diagrams:
                add_unique_object(object_data, get_diagram_info(obj, phase))

            # LA
            phase = "Logical Architecture LA"
            for component in model.oa.all_requirements:
                add_unique_object(object_data, get_req_info(component, phase))
            for obj in model.la.all_capabilities:
                add_unique_object(object_data, get_object_info(obj, phase))
            for component in model.la.all_components:
                add_unique_object(object_data, get_object_info(component, phase))
            for obj in model.la.all_functions:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.la.all_function_exchanges:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.la.all_functional_chains:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.la.all_interfaces:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.la.component_exchanges:
                add_unique_object(object_data, get_component_exchange_info(obj, phase))
            for obj in model.la.actor_exchanges:
                add_unique_object(object_data, get_component_exchange_info(obj, phase))
            for obj in model.la.diagrams:
                add_unique_object(object_data, get_diagram_info(obj, phase))

            # PA
            phase = "Physical Architecture PA"
            for component in model.oa.all_requirements:
                add_unique_object(object_data, get_req_info(component, phase))
            for component in model.pa.all_components:
                add_unique_object(object_data, get_physical_component_info(component, phase))
            for obj in model.pa.all_functions:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.pa.all_functional_chains:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.pa.all_function_exchanges:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.pa.all_capabilities:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.pa.all_component_exchanges:
                add_unique_object(object_data, get_component_exchange_info(obj, phase))
            for obj in model.pa.all_physical_exchanges:
                add_unique_object(object_data, get_component_exchange_info(obj, phase))
            for obj in model.pa.all_physical_links:
                add_unique_object(object_data, get_component_exchange_info(obj, phase))
            for obj in model.pa.all_physical_paths:
                add_unique_object(object_data, get_object_info(obj, phase))
            for obj in model.pa.all_physical_exchanges:
                add_unique_object(object_data, get_component_exchange_info(obj, phase))
            for obj in model.pa.diagrams:
                add_unique_object(object_data, get_diagram_info(obj, phase))

            # Generate + save
            self.generate_object_embeddings(object_data)
            print("Saving embeddings")
            self.save_embeddings()

    def load_embeddings(self):
        """Load embeddings (list) from a file; tolerate legacy format."""
        with open(self.embedding_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            # Legacy
            self.embeddings = data
            self._last_loaded_meta = None
        else:
            self._last_loaded_meta = data.get("meta")
            self.embeddings = data.get("items", [])
        print("embeddings loaded.")

    # ---------- Similarity search ----------

    @staticmethod
    def cosine_similarity(vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def find_similar_objects(self, query, top_n=10):
        query_embedding = self.client.embeddings.create(input=[query], model=self.model).data[0].embedding
        similarities = []
        for obj in self.embeddings:
            similarity = self.cosine_similarity(query_embedding, obj["embedding"])
            similarities.append((obj, similarity))
        similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
        return similarities[:top_n]

    # ---------- Interactive helpers (unchanged) ----------

    def locate_possible_objects(self, prompt):
        ranked_objects = self.find_similar_objects(prompt)
        print("\nThis is a list of ranked Objects Based on Query:")
        for i, (obj, similarity) in enumerate(ranked_objects):
            print(
                f"Index: {i}, Name: {obj['name']}, Similarity: {similarity:.2f}, "
                f"Type: {obj['type']},Phase: {obj['phase']}, Source: {obj.get('source_component', 'N/A')}, "
                f"Target: {obj.get('target_component', 'N/A')}"
            )
        return ranked_objects

    def interactive_query_and_selection_widgets(self):
        self.selection_done = False
        query_input = widgets.Text(placeholder="Enter query for objects...", layout=widgets.Layout(width="80%"))
        output_area = widgets.Output()
        multi_select = widgets.SelectMultiple(options=[], description="Select:", layout=widgets.Layout(width="80%", height="200px"))
        submit_button = widgets.Button(description="Submit Selection", button_style="primary", icon="check")
        reset_button = widgets.Button(description="Reset", button_style="warning", icon="times")

        def on_query_submit(change):
            output_area.clear_output()
            query = query_input.value.strip()
            if not query:
                with output_area:
                    print("⚠️ Please enter a query.")
                return
            self.ranked_objects = self.find_similar_objects(query)
            multi_select.options = [(f"{obj['name']} ({obj['type']})", i) for i, (obj, _) in enumerate(self.ranked_objects)]
            with output_area:
                print("\n🔍 Ranked Objects Based on Query:")
                for i, (obj, similarity) in enumerate(self.ranked_objects):
                    print(f"{i}: {obj['name']} | Type: {obj['type']} | Phase: {obj['phase']} | Similarity: {similarity:.2f}")

        def on_submit_clicked(b):
            output_area.clear_output()
            selected_indices = list(multi_select.value)
            if not selected_indices:
                with output_area:
                    print("⚠️ No objects selected.")
                return
            self.selected_objects_output = [self.ranked_objects[i][0] for i in selected_indices]
            with output_area:
                print("\n✅ Selected Object Details:")
                for obj in self.selected_objects_output:
                    print(f"\n🔹 Name: {obj['name']}")
                    print(f"   Type: {obj['type']}")
                    print(f"   Phase: {obj['phase']}")
                    print(f"   Source Component: {obj.get('source_component', 'N/A')}")
                    print(f"   Target Component: {obj.get('target_component', 'N/A')}")
            self.selection_done = True

        def on_reset_clicked(b):
            query_input.value = ""
            multi_select.options = []
            output_area.clear_output()
            self.ranked_objects = []
            self.selected_objects_output = []
            self.selection_done = False

        query_input.observe(on_query_submit, names="value")
        submit_button.on_click(on_submit_clicked)
        reset_button.on_click(on_reset_clicked)
        display(widgets.VBox([query_input, multi_select, submit_button, reset_button, output_area]))
        print("Waiting for selection...")
        with ui_events() as poll:
            while not self.selection_done:
                poll(10)
                time.sleep(1)

    def get_selected_objects(self):
        return self.selected_objects_output

    def interactive_query_and_selection(self):
        embeddings = self.embeddings
        while True:
            query = input("Enter query for objects or diagrams to be analyzed: ")
            ranked_objects = self.find_similar_objects(query)
            print("\nThis is a list of ranked Objects Based on Query:")
            for i, (obj, similarity) in enumerate(ranked_objects):
                print(
                    f"Index: {i}, Name: {obj['name']}, Similarity: {similarity:.2f}, "
                    f"Type: {obj['type']},Phase: {obj['phase']}, Source: {obj.get('source_component', 'N/A')}, "
                    f"Target: {obj.get('target_component', 'N/A')}"
                )
            user_input = input("\nEnter the indices of the selected objects (comma-separated), or any non-integer input to retry: ")
            if not all(part.strip().isdigit() for part in user_input.split(",")):
                print("\nNon-integer input detected. Retrying with a new query.")
                continue
            try:
                selected_indices = [int(i.strip()) for i in user_input.split(",")]
                selected_objects = [ranked_objects[i][0] for i in selected_indices]
                return selected_objects
            except (ValueError, IndexError):
                print("\nInvalid input. Please enter valid indices or retry.")

    def query_and_select_top_objects(self, prompt, top_n=20):
        ranked_objects = self.find_similar_objects(prompt)
        print("\nThis is a list of ranked Objects Based on Query:")
        for i, (obj, similarity) in enumerate(ranked_objects[:top_n]):
            print(
                f"Index: {i}, Name: {obj['name']}, Similarity: {similarity:.2f}, "
                f"Type: {obj['type']}, Phase: {obj['phase']}, "
                f"Source: {obj.get('source_component', 'N/A')}, "
                f"Target: {obj.get('target_component', 'N/A')}"
            )
        selected_objects = [obj for obj, _ in ranked_objects[:top_n]]
        return selected_objects


