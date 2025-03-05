import os
from IPython.display import display, HTML

class HTMLPage:
    def __init__(self, title="Untitled Page", output_file=None):
        """
        Initialize an HTMLPage object.

        :param title: Title of the HTML page.
        :param output_file: Path to the output file. If None, the page will be displayed in the notebook.
        """
        self.title = title
        self.content = []  # List to store HTML content
        self.output_file = output_file  # Path to output file

    def set_output_file(self, output_file):
        """
        Set the output file path.

        :param output_file: Path to the output file.
        """
        self.output_file = output_file

    def append(self, html_content):
        """
        Append HTML content to the page.

        :param html_content: String of HTML content to add.
        """
        self.content.append(html_content)

    def display(self):
        """
        Display the page. If an output file is specified, write to the file.
        Otherwise, display in the notebook.
        """
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{self.title}</title>
</head>
<body>
    {''.join(self.content)}
</body>
</html>"""

        if self.output_file:
            # Write the HTML content to the output file
            with open(self.output_file, "w") as f:
                f.write(full_html)
            print(f"Page saved to: {self.output_file}")
        else:
            # Display the HTML content in the notebook
            display(HTML(full_html))


