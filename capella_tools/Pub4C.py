import os
from xml.etree import ElementTree as ET

class Traceability_Store:
    """
    A class to load and process artifacts, links, and link types from a traceability XML file.
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self._artifacts = []
        self._link_types = []
        self._load_data()

    # Existing methods remain unchanged...

    def get_artifacts_for_model_element(self, model_element_uuid):
        """
        Returns a list of artifacts linked to the given model element UUID.
        
        :param model_element_uuid: UUID of the model element to search for.
        :return: List of Traceability_Artifact objects linked to the model element.
        """
        linked_artifacts = [
            artifact for artifact in self._artifacts
            if any(link.model_element_uuid == model_element_uuid for link in artifact.artifact_links)
        ]
        return linked_artifacts

    
    

    def _load_data(self):
        """Loads and processes the XML file."""
        if not os.path.exists(self.file_path):
            print(f"Warning: File '{self.file_path}' does not exist.")
            return
    
        try:
            tree = ET.parse(self.file_path)
            root = tree.getroot()
    
            # Process Link Types
            for link_type in root.findall(".//ownedLinkTypes"):
                name = link_type.get("name")
                uuid = link_type.get("id")
                self._link_types.append(Traceability_LinkType(name=name, uuid=uuid))
    
            # Process Artifacts
            store = root.find(".//store")
            if store is not None:
                for artifact in store.findall("ownedArtifacts"):
                    name = artifact.get("title")
                    artifact_id = artifact.get("identifier")
                    url = artifact.get("url")
                    uuid = artifact.get("id")
                    identifier=  artifact.get("identifier")
    
                    new_artifact = Traceability_Artifact(name=name, artifact_id=artifact_id, url=url)
                    new_artifact.uuid = uuid
                    new_artifact.identifier = identifier
    
                    # Process Artifact Links
                    for link in artifact.findall("ownedLinks"):
                        link_type_id = link.get("type")
                        artifact_uuid = link.get("artifact")
                        model_element_uuid = (
                            link.find("modelObject").get("href").split("#")[-1]
                            if link.find("modelObject") is not None
                            else None
                        )
    
                        # Find the Traceability_LinkType object matching the link_type_id
                        link_type_obj = next(
                            (lt for lt in self._link_types if lt.uuid == link_type_id), None
                        )
    
                        # Add the link to the artifact
                        new_artifact.add_link(link_type_obj, artifact_uuid, model_element_uuid)
    
                    self._artifacts.append(new_artifact)
    
        except ET.ParseError as e:
            print(f"Error parsing the XML file: {e}")
        except Exception as ex:
            print(f"An unexpected error occurred: {ex}")

    @property
    def all_artifacts(self):
        """Returns the list of loaded artifacts."""
        return self._artifacts

    @property
    def all_link_types(self):
        """Returns the list of loaded link types."""
        return self._link_types

    def __repr__(self):
        return (f"Traceability_TStore(file_path={self.file_path}, "
                f"artifacts={len(self._artifacts)}, link_types={len(self._link_types)})")

class Traceability_ArtifactLink:
    def __init__(self, link_type, artifact_uuid, model_element_uuid):
        self.link_type = link_type
        self.artifact_uuid = artifact_uuid
        self.model_element_uuid = model_element_uuid

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __repr__(self):
        return (f"Traceability_ArtifactLink(link_type={self.link_type}, "
                f"artifact_uuid={self.artifact_uuid}, model_element_uuid={self.model_element_uuid})")




class Traceability_Artifact:
    def __init__(self, name, artifact_id, url):
        self.name = name
        self.artifact_id = artifact_id
        self.url = url
        self.uuid = None
        self.identifier = ""
        self.artifact_links = []
        self.property_values = []

    def add_link(self, link_type, artifact_uuid, model_element_uuid):
        link = Traceability_ArtifactLink(link_type, artifact_uuid, model_element_uuid)
        self.artifact_links.append(link)

    def add_property_value(self, requirement_title, name_value_pairs):
        """
        Adds a new property value entry.
        
        :param requirement_title: The title of the requirement.
        :param name_value_pairs: List of dictionaries containing name-value pairs.
        """
        #print(name_value_pairs)
        property_value = PropertyValue(requirement_title)
        property_value.add_pair("value", name_value_pairs[0]['value'].strip())
        property_value.add_pair("unit",  name_value_pairs[0]['unit'])
        self.property_values.append(property_value)
        
    def add_property_value(self, requirement_title, name_value_pairs):
        """
        Adds a new property value entry formatted for Jinja.
        
        :param requirement_title: The title of the requirement.
        :param name_value_pairs: List of dictionaries containing name-value pairs.
        """
        print("name_value_pairs:",name_value_pairs)
        self.property_values.append({ "name": "value",   "value": name_value_pairs[0]['value'].strip()})
        self.property_values.append({ "name": "unit",   "value": name_value_pairs[0]['unit']})
    
    def get_property_values(self):
        """
        Returns the list of property values.
        """
        return self.property_values
        
    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __repr__(self):
        return (f"Traceability_Artifact(name={self.name}, artifact_id={self.artifact_id}, url={self.url}, "
                f"uuid={self.uuid}, artifact_links={self.artifact_links}, property_values={self.property_values})")


class Traceability_LinkType:
    def __init__(self, name, uuid):
        self.name = name
        self.uuid = uuid

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __repr__(self):
        return f"Traceability_LinkType(name={self.name}, uuid={self.uuid})"
