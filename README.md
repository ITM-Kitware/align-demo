# align-demo

## Description
This repository contains the source files and configurations for a web application designed demo the algorithms in the align-system. The app is built with Python using the `dash` and `plotly` libraries. Users can interact with the app to select and run different algorithms, visualize the chosen algorithm's decision-making process, and compare outcomes across multiple algorithms.

## Content Overview

### `app.py`
- Main application file containing the logic for a Dash web app.
- Includes an interactive radar chart to visualize KDMA attributes and their values, which users can adjust by clicking on the chart
- Implements callbacks for interactivity and supports loading different algorithms for decision-making simulations.

### `algorithms.py`
- Exposes the different algorithm classes from the align-system repository and contains the logic for handling algorithm configurations and decision-making processes

### `dynamic_components.py`
- Defines functions to create composite dash components

### `test_app.py`
- A script to develop components in before integrating them into the app.py script

### `configs/`
This directory contains various YAML configuration files:
- `single-kdma-adm.yml`: Configuration for an algorithm that handles single KDMA values.
- `multi-kdma-adm.yml`: Configures an algorithm capable of predicting multiple KDMA values.
- `dummy.yml`: A simple configuration for testing purposes with a dummy algorithm.
- `llama_index.yml`: Config specifies settings for an algorithm using index-based methods.

## Usage
To run the web app:

1. Ensure you have Python installed along with the necessary libraries (`dash`, `plotly`, `dash-bootstrap-components`).
```
pip install requirements.txt
```
2. Navigate to the directory containing `app.py` or `test_app.py`.
4. Run the script with the command `python app.py` or `python test_app.py`.
5. Access the web app in your web browser at `http://127.0.0.1:8050/` or the specified port number.
6. Use the user interface to interact with the app by loading configurations, running algorithms, and visualizing KDMA values.

For any changes, modifications, or additional usage of the configs or algorithms, refer to the corresponding Python scripts and YAML files, customizing them as required for the intended experiment or demo.


# Implementation Plan
🟡 = in progress

## Goals/Features
### Data
- [X] Paste in/edit scenario, probe, responses (SPR)
- [X] Select probe_id from dropdown that populates SPR inputs with text from dataset
- [X] Input device for target KDMA values
- [ ] Dataset selection
  - [ ] Which attributes depends on dataset... BBN or ST
  - [ ] Which probes depends on dataset

### Model
- [X] Hard-coded single model
- [X] Select ADM from dropdown that populates config text input from default config for that ADM
- [ ] 🟡 Make compatible with all of the ADM configs
- [ ] Select multiple ADMs and run them all at once to compare their outputs
### Inference
- [X] ‘RUN’ button that shows model choice selection and reasoning
  - [X] Show a full log of everything the model did
  - [X] Show a more user-friendly version of the log
- [ ] Generate an ADM-specific visualization of the system output
- [ ] Generate comparison visualizations of multiple ADMs

### Misc
- [X] Add visual identifier to show chosen response
- [ ] There should be a notion of confidence associated with answers
  - [ ] Percentge (for now based on predicted and target KDMA values)
- [ ] Format JSON output to be more readable
- [ ] Add upload dataset functionality


### Phase 1️⃣
- Scenario multi-line text input (15 lines)
- Probe multi-line text input (3 lines)
- Responses multi-line text input (5 lines)
- Load a model when starting the app
  - call `get_model()` as a placeholder to get a model object
  - Pass scenario, probe, response to model `model(scenario, probe, response)`
  - model returns `{'choice': int_choice, 'reasoning': str_reasoning}`
- Run button
  - Output: chosen response line, justification text area
  - State: scenario, probe, responses
- Chosen response (1 line)
  - Use model's `int_choice` to index into responses
- Justification text area (10 lines)


### Phase 2️⃣
- probe ID dropdown
  - On select, populate scenario, probe, responses
  - Read from `dataset.json` to populate the dropdown which is in this format:
```
{
  "probe_id": {
    "scenario": "scenario text",
    "probe": "probe text",
    "choices": [
      "response 1",
      "response 2",
      "response 3",
      "response 4"
    ]
  }
}
```
- ADM config text input
  - Allows the user to enter yml config for ADM
  - Config is passed to `get_algorithm(config)` as a dict
    - `from lib import get_algorithm`
  - Returns an algorithm object that can be called similar to how the current algorithm is called
- Dedicated log scrollable text area
