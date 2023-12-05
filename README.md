# align-demo

Do fist - 1️⃣, 2️⃣, 3️⃣, 4️⃣ - Do last

## Goals/Features
### Data
- [X] 1️⃣ Paste in/edit scenario, probe, responses (SPR)
- [X] 2️⃣ Select probe_id from dropdown that populates SPR inputs with text from dataset
### Model
- [X] 1️⃣ Hard-coded single model
- [X] 2️⃣ Select ADM from dropdown that populates config text input from default config for that ADM
  - [ ] 3️⃣ Dynamically generate input widgets for the different fields specific to that ADM
    - [ ] 4️⃣ Display editable templates that can be referenced in the config
### Inference
- [X] 1️⃣ ‘RUN’ button that shows model choice selection and reasoning
  - [X] 1️⃣ Show a full log of everything the model did
  - [X] 2️⃣ Show a more user-friendly version of the log


### Components 1️⃣
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


### Components 2️⃣
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
