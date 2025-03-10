import re
from bs4 import BeautifulSoup

class RequirementExtractor:
    """
    A class to extract numerical values and SI units from a Polarion requirement object,
    while handling HTML formatting in the description.
    """

    def __init__(self, polarion_obj):
        """
        Initializes the RequirementExtractor with a Polarion object.

        :param polarion_obj: Polarion requirement object with `title` and `description.content`
        """
        self.title = polarion_obj.title  # Store requirement title
        self.description = self._strip_html(polarion_obj.description.content)  # Clean HTML content
        self.extracted_data = self._extract_value_units()  # Extract values & units

    def _strip_html(self, html_content):
        """
        Strips HTML tags from the given content and normalizes whitespace.
        
        :param html_content: str, raw HTML content
        :return: str, cleaned plain text content
        """
        soup = BeautifulSoup(html_content, "html.parser")
        clean_text = soup.get_text(separator=" ").strip()
        return re.sub(r'\s+', ' ', clean_text)  # Normalize spaces

    def _extract_value_units(self):
        """
        Extracts numerical values and their corresponding SI units from the requirement description.

        :return: list of dictionaries with extracted values and units
        """
        # Define SI unit patterns without word boundary limitations
        #unit_patterns = r'(m|kg|s|A|K|mol|cd|Hz|N|Pa|J|W|V|C|F|Ω|S|Wb|T|H|°C|°F|kWh|ms|km/h|kN|MPa|kW)(?=\s|$|,|\.|;)'
        unit_patterns = r"(?:m|kg|s|A|K|mol|cd|Hz|N|Nm|%|Pa|J|W|V|C|F|Ω|S|Wb|T|H|°C|°F|kWh|ms|km/h|kN|MPa|kW|rpm|€)"



        
        # Number format: supports thousands separator (comma), decimals, and tolerances
        #value_unit_pattern = fr'(\d{{1,3}}(?:,\d{{3}})*\.?\d*\s*(?:±\s*\d+\.?\d*)?)\s*{unit_patterns}'
        #value_unit_pattern = fr'(\d{{1,3}}(?:,\d{{3}})*\.?\d*\s*(?:±\s*\d+\.?\d*)?)\s*({unit_patterns})(?=\s|$|,|\.|;)'
        value_unit_pattern = fr"(\d{{1,3}}(?:,\d{{3}})*\.?\d*\s*(?:±\s*\d+\.?\d*)?)\s*({unit_patterns})(?=\s|$|,|\.|;)"


        # Debug: Print cleaned text and regex pattern
        #print(f"Cleaned Description: {self.description}")
        #print(f"Using unit Pattern: { unit_patterns}")
       # print(f"Using Regex Pattern: {value_unit_pattern}")

        matches = re.findall(value_unit_pattern, self.description)

        # Debug: Print matches found
        #print(f"Regex Matches Found: {matches}")

        # Fix grouping for correct output structure
        return [{"value": match[0].replace(",", ""), "unit": match[1]} for match in matches]

    def get_title(self):
        """ Returns the title of the requirement. """
        return self.title

    def get_description(self):
        """ Returns the cleaned description of the requirement. """
        return self.description

    def get_extracted_values(self):
        """ Returns the extracted numerical values and units. """
        return self.extracted_data

