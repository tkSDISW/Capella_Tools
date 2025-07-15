from setuptools import setup, find_packages
setup(
    name="capella_tools",
    version="1.0",
    packages=find_packages(),
    install_requires=[
        "capellambse==0.6.20",  # Include other dependencies if needed
        "capellambse_context_diagrams=0.7.12",
        "cairosvg",
        "polarion",
        "openai",
        "ipywidgets",
        "pyvis",
        "jupyter_ui_poll",
        "python-docx",
        "PyPDF2"     
    ],
)
