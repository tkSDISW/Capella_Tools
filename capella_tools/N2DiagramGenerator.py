
# Copyright Siemens AG
# Licensed under the Apache License, Version 2.0 (see full text in LICENSES/Apache-2.0.txt)

# Dot-files are licensed under CC0-1.0 (see full text in LICENSES/CC0-1.0.txt)

# To provide the same look and feel across platforms, this library is bundled
# with the OpenSans font (capellambse/OpenSans-Regular.ttf).
# The OpenSans font is Copyright 2020 The Open Sans Project Authors,
# licensed under OFL-1.1 (see full text in LICENSES/OFL-1.1.txt)

# Re-import necessary modules after code execution state reset
import pandas as pd
import matplotlib.pyplot as plt
import yaml
from IPython.display import HTML, display
from pathlib import Path
class N2DiagramGenerator:
    def __init__(self, yaml_content: str, diagram_name: str = None, mode: str = "functional"):
        """
        :param yaml_content: Raw YAML string
        :param diagram_name: Optional name for the N² matrix
        :param mode: "functional" or "component"
        """
        def uuid_constructor(loader, node): return loader.construct_scalar(node)
        yaml.add_constructor("!uuid", uuid_constructor, Loader=yaml.SafeLoader)

        self.diagram_name = diagram_name or f"{mode.capitalize()} Exchange Matrix"
        self.yaml_data = yaml.safe_load(yaml_content)
        self.mode = mode.lower()
        self.matrix = None
        self.labels = []

    def extract_entity_map(self, entity_type, entity_keys):
        """Generic method to extract a UUID → name mapping for given entity type."""
        objects = self.yaml_data.get("model", {}).get("objects", [])
        entity_map = {}
        for obj in objects:
            if obj.get("type") in entity_type:
                uuid = obj.get("primary_uuid")
                name = obj.get("name")
                if uuid and name:
                    entity_map[uuid] = name
        return entity_map

    def extract_exchanges(self):
        objects = self.yaml_data.get("model", {}).get("objects", [])
        elements = set()
        exchanges = []

        if self.mode == "functional":
            port_to_function = self.extract_port_to_function_map()
            for obj in objects:
                if obj.get("type") == "FunctionalExchange":
                    src_ports = obj.get("source function or activity port", [])
                    tgt_ports = obj.get("target function or activity port", [])
                    src_uuid = src_ports[0].get("ref_uuid") if src_ports else None
                    tgt_uuid = tgt_ports[0].get("ref_uuid") if tgt_ports else None
                    src = port_to_function.get(src_uuid)
                    tgt = port_to_function.get(tgt_uuid)
                    if src and tgt:
                        elements.update([src, tgt])
                        exchanges.append((src, tgt))

        elif self.mode == "component":
            comp_map = self.extract_entity_map(["Component", "LogicalComponent", "PhysicalComponent"], ["primary_uuid", "name"])
            for obj in objects:
                src_list = obj.get("source component", [])
                tgt_list = obj.get("target component", [])
                if obj.get("type") == "ComponentExchange":
                    src = comp_map.get(src_list[0].get("ref_uuid")) if src_list else None
                    tgt = comp_map.get(tgt_list[0].get("ref_uuid")) if tgt_list else None
                    if src and tgt:
                        elements.update([src, tgt])
                        exchanges.append((src, tgt))

        self.labels = sorted(elements)
        index = {name: i for i, name in enumerate(self.labels)}
        size = len(self.labels)
        matrix = [["" for _ in range(size)] for _ in range(size)]
        for src, tgt in exchanges:
            matrix[index[src]][index[tgt]] = "✔"

        self.matrix = pd.DataFrame(matrix, index=self.labels, columns=self.labels)

    def extract_port_to_function_map(self):
        objects = self.yaml_data.get("model", {}).get("objects", [])
        port_to_function = {}
        for obj in objects:
            if obj.get("type") in ["FunctionInputPort", "FunctionOutputPort"]:
                port_uuid = obj.get("primary_uuid")
                owner = obj.get("owner", {})
                if isinstance(owner, dict):
                    function_name = owner.get("name")
                    if port_uuid and function_name:
                        port_to_function[port_uuid] = function_name
        return port_to_function

    def display_n2_diagram(self):
        if self.matrix.empty:
            print(f"⚠️ No {self.mode} exchanges found to display.")
            return
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.imshow([[1 if cell == "✔" else 0 for cell in row] for row in self.matrix.values], cmap="Greens" if self.mode == "component" else "Blues")
        ax.set_xticks(range(len(self.labels)))
        ax.set_yticks(range(len(self.labels)))
        ax.set_xticklabels(self.labels, rotation=90)
        ax.set_yticklabels(self.labels)
        ax.set_title(f"N² Diagram: {self.diagram_name}")
        plt.show()

    def save_to_excel(self, output_path=None):
        if output_path is None:
            output_path = f"{self.diagram_name.replace(' ', '_')}_n2.xlsx"
        self.matrix.to_excel(output_path)
        print(f"Excel file saved to {output_path}")

    def save_to_html(self, output_path=None):
        html = self.matrix.to_html(border=1)
        output_path = output_path or f"{self.diagram_name.replace(' ', '_')}_n2.html"
        with open(output_path, "w") as f:
            f.write(html)
        display(HTML(html))
        print(f"HTML file saved to {output_path}")

    def run_all(self):
        self.extract_exchanges()
        if self.matrix.empty:
            print(f"⚠️ No {self.mode} exchanges found in model.")
        else:
            self.display_n2_diagram()
        self.save_to_excel()
        self.save_to_html()


