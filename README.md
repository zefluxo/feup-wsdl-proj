# WSDL Project

## How to Run

### 1. Run Requirements

This project uses Python to run. To install the needed requirements, use the following:

**for Linux**:
    
    bash ./requirements.sh

**for Windows**:
    
    .\requirements.bat

### 2. Run the Web App 

To run the application, type the following **while in the root directory**:

    streamlit run main.py

## How to Use

After running the Web App, the application is accessible locally at ``http://localhost:8501``.

### Entity Recognition Tab

The entity recognition feature receives an input text and a language option. It outputs a list of found entities with all attributes.

### SPARQL Query Tab

The SPARQL query feature allows any SPARQL query to be ran against our database and outputs a JSON data dump of all retrieved results.