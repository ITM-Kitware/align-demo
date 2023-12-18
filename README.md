# align-demo

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
