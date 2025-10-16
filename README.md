
# Capella Tools

Capella Tools is a collection of utilities designed to enhance the capabilities of Capella users in performing requirement development, report generation, and verification tasks directly from Capella models.

## Purpose
This repository provides tools that enable:
- Requirement development from Capella models
- Report generation based on model content
- Verification-related tasks using Capella models

## Audience
This toolkit is intended for the general Capella user community.

## Included Tools
- **Report Generators**: Generate structured reports from Capella models.
- **Digital System Engineering (SE) Fabric Generator**: Create digital SE fabric from systems engineering models.
- **Embedding-Based Model Search and Retrieval Tools**: Efficiently search and retrieve model components using embeddings.
- **Prompt driven analysis and report based on RAG (Retrieval Augmented Generation)**: Prompt driven analysis and reports from Capella models and attached files to support RAG workflows.

Enbedding-Based Model Search and Prompt driven analysis requires Open AI API access to be configured.

## Open AI us prerequisites
To confiure use with Open AI API you will need to know a few things. 
- **model**: The specifc name of model your going to use
- **base url**: The specifc url of the api. Example: https://api.openai.com/v1  
- **api key**: The key that you created specific for your use.

Set configuation notebook allow you to create multple configurations. Therefore you can name the configuration. Exampel "4o" could be a name of a configuration. You can also set a configuration as the default to be used, when you code does not choose a specific configuration. 

## Installation
To install the tools, use the following command:
```bash
pip install --upgrade git+https://github.com/tkSDISW/Capella_Tools
```

## Uninstall
To install the tools, use the following command:
```bash
pip uninstall capella_tools

```


## Examples

The repository includes three example folders that demonstrate how to use Capella Tools:

- **Auto Example**  
- **Ventilator Example**  
- **Trail_Power**

Each folder contains:
- A Capella model that can be loaded into the Capella modeling environment.
- A `Notebook` folder with Jupyter notebooks showcasing Python code that utilizes Capella Tools for various tasks.
- "Set" notebooks are available in each example to set various properties required by tools. 

These examples provide practical insights into how the tools can be applied to real-world systems engineering scenarios.


## License
This repository is licensed under the following licenses:
- Apache License 2.0
- Creative Commons CC0 1.0 Universal
- SIL Open Font License 1.1

## Contact
For questions or support, please contact:
**Tony Komar** - tony.komar@siemens.com
