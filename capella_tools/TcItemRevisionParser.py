# SPDX-FileCopyrightText: © Siemens AG
# SPDX-License-Identifier: Apache-2.0
"""
TcItemRevision Parser
~~~~~~~~~~~~~~~~~~~~~

This module defines the `TcItemRevisionParser` class, which extracts and manages
`smw:TcItemRevision` elements from a `.capella` file associated with a given `.aird` file.

This project is compliant with the REUSE Specification Version 3.0.

Copyright Siemens AG, licensed under Apache 2.0 (see full text in LICENSES/Apache-2.0.txt)

Dot-files are licensed under CC0-1.0 (see full text in LICENSES/CC0-1.0.txt)

To provide the same look and feel across platforms, we distribute our library bundled
with the OpenSans font (capellambse/OpenSans-Regular.ttf). The OpenSans font is
Copyright 2020 The Open Sans Project Authors, licensed under OFL-1.1
(see full text in LICENSES/OFL-1.1.txt).

Typical usage example:
    parser = TcItemRevisionParser("/path/to/model.aird", teamcenter_url="https://example.com")
    revision = parser.get_by_id("some-uuid")
    print(revision["itemId"])
    print(revision["url"])

The parser identifies elements by their `xsi:type="smw:TcItemRevision"` attribute and collects
the following fields if present:
- id
- tcuid
- stableTcId
- itemId
- revisionId
- url (if Teamcenter URL is provided)

Author: Anthony Komar
"""

import os
import xml.etree.ElementTree as ET

class TcItemRevisionParser:
    """
    A parser class to extract smw:TcItemRevision entries from a .capella file
    located in the same directory as a given .aird file.

    Attributes:
        aird_file_path (str): Path to the .aird file.
        capella_file_path (str): Path to the associated .capella file.
        items (dict): Dictionary mapping IDs to extracted TcItemRevision metadata.
        teamcenter_url (str): Optional base URL for linking to Teamcenter objects.
    """

    def __init__(self, aird_file_path, teamcenter_url=None):
        """
        Initialize the parser with the path to a .aird file. Automatically locates
        the corresponding .capella file and extracts TcItemRevision entries.

        Args:
            aird_file_path (str): Path to the .aird file.
            teamcenter_url (str, optional): Base URL for constructing Teamcenter links.
        """
        self.aird_file_path = aird_file_path
        self.capella_file_path = self._find_capella_file()
        self.items = {}
        self.teamcenter_url = teamcenter_url.rstrip("/") if teamcenter_url else None

        if self.capella_file_path:
            self._parse_capella_file()

    def _find_capella_file(self):
        """
        Search for a .capella file in the same directory as the .aird file.

        Returns:
            str or None: Path to the .capella file if found, else None.
        """
        base_dir = os.path.dirname(self.aird_file_path)
        for file in os.listdir(base_dir):
            if file.endswith(".capella"):
                return os.path.join(base_dir, file)
        return None

    def _parse_capella_file(self):
        """
        Parse the .capella XML and extract elements with xsi:type="smw:TcItemRevision".
        Store each entry using the ID of the parent Capella model object as the key.
        """
        tree = ET.parse(self.capella_file_path)
        root = tree.getroot()

        for parent in root.iter():
            for elem in parent:
                if elem.tag == "ownedExtensions" and elem.attrib.get("{http://www.w3.org/2001/XMLSchema-instance}type") == "smw:TcItemRevision":
                    tcuid = elem.attrib.get('tcuid')
                    parent_id = parent.attrib.get('id')
                    item = {
                        'id': parent_id,
                        'tcuid': tcuid,
                        'stableTcId': elem.attrib.get('stableTcId'),
                        'itemId': elem.attrib.get('itemId'),
                        'revisionId': elem.attrib.get('revisionId'),
                    }
                    if self.teamcenter_url and tcuid:
                        item['url'] = f"{self.teamcenter_url}/#/com.siemens.splm.clientfx.tcui.xrt.showObject?uid={tcuid}"
                    if parent_id:
                        self.items[parent_id] = item

    def get_by_id(self, item_id):
        """
        Retrieve a specific TcItemRevision entry by its ID.

        Args:
            item_id (str): The 'id' attribute of the TcItemRevision element.

        Returns:
            dict or None: The corresponding TcItemRevision data, or None if not found.
        """
        return self.items.get(item_id)

    def all_items(self):
        """
        Retrieve all parsed TcItemRevision entries.

        Returns:
            list: A list of all TcItemRevision dictionaries.
        """
        return list(self.items.values())

    def find_uuid_by_teamcenter_key(self, item_id, revision_id):
        """
        Look up the Capella UUID based on Teamcenter item ID and revision ID.

        Args:
            item_id (str): The Teamcenter item ID (e.g., '096065').
            revision_id (str): The Teamcenter revision ID (e.g., 'A').

        Returns:
            str or None: The Capella UUID (i.e., Capella object's ID), or None if not found.
        """
        for uuid, data in self.items.items():
            if data.get("itemId") == item_id and data.get("revisionId") == revision_id:
                return uuid
        return None

    def find_uuid_by_teamcenter_string(self, item_revision_str):
        """
        Look up the Capella UUID using a combined Teamcenter string in the form 'ItemID/RevisionID'.

        Args:
            item_revision_str (str): A string in the format '096065/A'.

        Returns:
            str or None: The Capella UUID if found, else None.
        """
        if '/' not in item_revision_str:
            return None
        item_id, revision_id = item_revision_str.split('/', 1)
        return self.find_uuid_by_teamcenter_key(item_id.strip(), revision_id.strip())
