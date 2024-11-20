# ALIGN System Demo

## Description
This repository contains the source files and configurations for a web application designed demo the algorithms in the [align-system.](https://github.com/ITM-Kitware/align-system) The app is built with Python using the `dash` and `plotly` libraries. Users can interact with the app to select and run different algorithms, visualize the chosen algorithm's decision-making process, and compare outcomes across multiple algorithms. (Note: Currently, the demo includes  the `Outlines Transformers Structured ADM configuration. Configuration for other ADMs will be added soon.)

## Content Overview

### `app.py`
- Main application file containing the logic for a Dash web app.
- Implements a model comparison workflow for a baseline and aligned ADMs.

## `app_layout.py`
- The script that contains the front-end UI

## `action_filtering.py`
- Implements the action filtering logic from the align system without the eval loop structure.

### `configs/`
This directory contains various YAML configuration files:
- `hydra/adm`: Folder containing the Algorithmic Decision Maker (ADM) config files.
- `hydra/alignment_target`: Folder containing the Key Decision Making Attribute (KDMA) config files.
- `prompt_engineering`: Folder containing the KDMA descriptions

### `oracle-json-file/`
Input dataset used to hydrate the scenario and character state for a given scenario ID.

## Usage
To run the web app:

1. Ensure you have Python installed along with the necessary dependencies.
```
pip install -r requirements.txt
```
2. Hardware Requirements:
```
It is recommended to have atleast 32GB RAM and 2 GPUs, each with atleast 32BG VRAM.
````

2. Run the following command
```
python app.py
```
3. Access the web app in your web browser at `http://127.0.0.1:8052/` or the specified port number.
The demo interface can be used to run the default scenarios from the ITM-ALIGN datasets. Furthermore,
the system and scenario prompts can be edited to test "what if" situation changes for a given set
of action choices.
