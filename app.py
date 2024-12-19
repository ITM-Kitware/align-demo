import json
import os

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import hydra
from omegaconf import OmegaConf
import torch

from align_system.utils.hydrate_state import hydrate_scenario_state
# from transformers import pipeline


from action_filtering import filter_actions
from app_layout import model_1_layout, model_2_layout, load_dataset_components

# Initialize an algorithm with an empty config as a placeholder
adm = None
adm_2 = None
# Torch determinism for reproducibility
os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
torch.use_deterministic_algorithms(True)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE, dbc.icons.BOOTSTRAP])

app.layout = dbc.Container(fluid=True, style={'width': '100%'}, children=[
    html.H1('Align-Demo', className='mb-4'),

    # Store component to keep track of attribute values
    dcc.Store(id='dataset-store'),
    dcc.Store(id='scenario-id-store'),
    dcc.Store(id='alignment-target-store'),
    dcc.Store(id='alignment-target-store-2'),

    dbc.Stack(children=load_dataset_components, direction='horizontal', gap=3),
    html.Hr(),
    dbc.Row([
        dbc.Col(children=model_1_layout),
        dbc.Col(children=model_2_layout),
    ])
])


### -------------------- Load Dataset to Store -------------------------- ###
@app.callback(
    [Output('dataset-store', 'data'),
     Output('scenario-id-store', 'data')],
    [Input('dataset-dropdown', 'value')],
    prevent_initial_call=True,
)
def load_dataset_store(selected_dataset):
    with open(f'oracle-json-files/{selected_dataset}', 'r') as f:
        dataset = json.load(f)
        scenario_ids = []
        scenarios = {}
        for record in dataset:
            scenario_id = record['input']['scenario_id']

            if scenario_id not in scenarios:
                scenario_ids.append(scenario_id)
                scenarios[scenario_id] = []

            scenarios[scenario_id].append(
                record['input']
            )
        return scenarios, scenario_ids

### -------------------- Updated Scenario ID Dropdowns for both models --------------------- ###
@app.callback(
    Output('scenario-id-dropdown', 'options'),
    [Input('scenario-id-store', 'data')],
    prevent_initial_call=True,
)
def update_scenario_id_dropdown(scenario_ids):
    if scenario_ids:
        scenarios = [{'label': str(scenario_id), 'value': str(scenario_id)} for scenario_id in scenario_ids]
        return scenarios
    else:
        return [], []


# ### -------------------- Updated Probe ID Dropdowns --------------------- ###
@app.callback(
    Output('probe-id-dropdown', 'options'),
    State('dataset-store', 'data'),
    Input('scenario-id-dropdown', 'value'),
    prevent_initial_call=True,
)
def update_probe_id_dropdown(scenarios, scenario_id):
    if scenarios:
        probe_ids = []
        for scenario in scenarios[scenario_id]:
            state, actions = hydrate_scenario_state(scenario)
            state_dict = state.to_dict()
            if state.elapsed_time != 0:
                probe_id = state_dict["meta_info"]["probe_response"]["probe_id"]
            else:
                probe_id = 'N/A'
            probe_ids.append(probe_id)
        return [{'label': p_id, 'value': p_id} for p_id in probe_ids]
    else:
        return []

### -------------------- LLM loading and ADM instantiation -------------------------- ###
@app.callback(
    Output('load-model-button', 'disabled'),
    [Input('load-model-button', 'n_clicks')],
    [State('llm-dropdown', 'value'),
     State('adm-config-input', 'value'),
     State('system-prompt-checklist', 'value')],
    prevent_initial_call=True
)
def load_llm(n_clicks, llm_backbone, adm_type, aligned):
    if n_clicks > 0:
        adm_config_path = os.path.join('configs/hydra/adm', f"{adm_type}_baseline.yaml")
        if aligned is not None:
            adm_config_path = os.path.join('configs/hydra/adm', f"{adm_type}_aligned.yaml")
        adm_config = OmegaConf.load(adm_config_path)
        adm_config["model_name"] = llm_backbone
        global adm
        adm = hydra.utils.instantiate(adm_config, recursive=True)
        return False

@app.callback(
    Output('load-model-button-2', 'disabled'),
    [Input('load-model-button-2', 'n_clicks')],
    [State('llm-dropdown-2', 'value'),
     State('adm-config-input-2', 'value'),
     State('system-prompt-checklist-2', 'value')],
    prevent_initial_call=True
)
def load_llm_2(n_clicks, llm_backbone, adm_type, aligned):
    if n_clicks > 0:
        adm_config_path = os.path.join('configs/hydra/adm', f"{adm_type}_baseline.yaml")
        if aligned is not None:
            adm_config_path = os.path.join('configs/hydra/adm', f"{adm_type}_aligned.yaml")
        adm_config = OmegaConf.load(adm_config_path)
        adm_config["model_name"] = llm_backbone
        global adm_2
        adm_2 = hydra.utils.instantiate(adm_config, recursive=True)
        return False

### -------------------- Load Alignment Target -------------------------- ###
@app.callback(
    [Output('alignment-target-store', 'data')],
    Input('load-system-prompt-button', 'n_clicks'),
    [State('system-prompt-checklist', 'value'),
     State('kdma-dropdown', 'value'),
     State('kdma-slider', 'value')],
    prevent_initial_call=True,
)
def load_alignment_target(n_clicks, is_aligned, kdma, kdma_value):
    if n_clicks > 0:
        if kdma and 'aligned' in is_aligned:
            kdma_split = kdma.split('_')
            kdma_file = ' '.join(kdma_split).capitalize()
            if kdma_file in ["Moral deservingness", "Maximization"]:
                binary_alignment = "low"
                print(kdma_value)
                if float(kdma_value) >= 0.5:
                    binary_alignment = "high"
                alignment_target = OmegaConf.load(os.path.join("configs/hydra/alignment_target",f"{kdma}_{binary_alignment}.yaml"))

            alignment_target = OmegaConf.to_object(alignment_target)
        else:
            alignment_target = None
        return [alignment_target]

@app.callback(
    [Output('alignment-target-store-2', 'data')],
    Input('load-system-prompt-button-2', 'n_clicks'),
    [State('system-prompt-checklist-2', 'value'),
     State('kdma-dropdown-2', 'value'),
     State('kdma-slider-2', 'value')],
    prevent_initial_call=True,
)
def load_alignment_target_2(n_clicks, is_aligned, kdma, kdma_value):
    if n_clicks > 0:
        if kdma and 'aligned' in is_aligned:
            kdma_split = kdma.split('_')
            kdma_file = ' '.join(kdma_split).capitalize()
            if kdma_file in ["Moral deservingness", "Maximization"]:
                binary_alignment = "low"
                if float(kdma_value) >= 0.5:
                    binary_alignment = "high"
                alignment_target = OmegaConf.load(os.path.join("configs/hydra/alignment_target",f"{kdma}_{binary_alignment}.yaml"))

            alignment_target = OmegaConf.to_object(alignment_target)
        else:
            alignment_target = None
        return [alignment_target]

@app.callback(
    [Output('slider-div', 'style'),
     Output('alignment-target-stack', 'style'),
     Output('space-div', 'style')],
    Input('system-prompt-checklist', 'value'),
    prevent_initial_call=True
)
def show_hide_alignment_target(aligned):
    if 'aligned' in aligned and aligned is not None:
        return {'display': 'block'}, {'display': 'flex'}, {'display': 'none'}
    return {'display': 'none'}, {'display': 'none'}, {'display': 'block', 'marginBottom': '170px'}

@app.callback(
    [Output('slider-div-2', 'style'),
     Output('alignment-target-stack-2', 'style'),
     Output('space-div-2', 'style')],
    Input('system-prompt-checklist-2', 'value'),
    prevent_initial_call=True
)
def show_hide_alignment_target_2(aligned):
    if 'aligned' in aligned and aligned is not None:
        return {'display': 'block'}, {'display': 'flex'}, {'display': 'none'}
    return {'display': 'none'}, {'display': 'none'}, {'display': 'block', 'marginBottom': '170px'}

### ------------------------ Load ADM System Prompt to UI ------------------------ ###

@app.callback(
    [Output('system-prompt', 'value'),
     Output('action-choices-prompt', 'value')],
    [Input('load-system-prompt-button', 'n_clicks'),
     Input('alignment-target-store', 'data')],
    [State('dataset-store', 'data'),
     State('scenario-id-dropdown', 'value'),
     State('probe-id-dropdown', 'value')],
    prevent_initial_call=True
)
def load_system_prompt(n_clicks, alignment_target, scenarios, scenario_id, probe_id):
    if n_clicks > 0:
        for scenario in scenarios[scenario_id]:
            state, actions = hydrate_scenario_state(scenario)
            actions_filtered = filter_actions(state, actions)
            state_dict = state.to_dict()
            if state_dict["meta_info"]["probe_response"] is not None:
                if probe_id != state_dict["meta_info"]["probe_response"]["probe_id"]:
                    continue
                probe_id = state_dict["meta_info"]["probe_response"]["probe_id"]
        kwargs = {
            'demo_kwargs': {
                'max_generator_tokens': 8092,
                'generator_seed': 2,
                'shuffle_choices': False
            }
        }
        if alignment_target is not None:
            alignment_target = OmegaConf.create(alignment_target)

        prompts, _ = adm.instance.get_dialog_texts(
            scenario_state=state,
            available_actions=actions_filtered,
            alignment_target=alignment_target,
            kdma_descriptions_map="configs/prompt_engineering/kdma_descriptions.yml",
            demo_kwargs=kwargs["demo_kwargs"]
        )

        prompt_sections = prompts[0].split('\n\n')

        prompt = '\n\n'.join(prompt_sections[:-1])
        action_choices = prompt_sections[-1]

        return [prompt], [action_choices]

@app.callback(
    [Output('system-prompt-2', 'value'),
     Output('action-choices-prompt-2', 'value')],
    [Input('load-system-prompt-button-2', 'n_clicks'),
     Input('alignment-target-store-2', 'data')],
    [State('dataset-store', 'data'),
     State('scenario-id-dropdown', 'value'),
     State('probe-id-dropdown', 'value')],
    prevent_initial_call=True
)
def load_system_prompt_2(n_clicks, alignment_target, scenarios, scenario_id, probe_id):
    if n_clicks > 0:
        for scenario in scenarios[scenario_id]:
            state, actions = hydrate_scenario_state(scenario)
            actions_filtered = filter_actions(state, actions)
            state_dict = state.to_dict()
            if state_dict["meta_info"]["probe_response"] is not None:
                if probe_id != state_dict["meta_info"]["probe_response"]["probe_id"]:
                    continue
                probe_id = state_dict["meta_info"]["probe_response"]["probe_id"]

        kwargs = {
            'demo_kwargs': {
                'max_generator_tokens': 8092,
                'generator_seed': 2,
                'shuffle_choices': False
            }
        }
        if alignment_target is not None:
            alignment_target = OmegaConf.create(alignment_target)
        prompts, positive_dialogs = adm_2.instance.get_dialog_texts(
            scenario_state=state,
            available_actions=actions_filtered,
            alignment_target=alignment_target,
            kdma_descriptions_map="configs/prompt_engineering/kdma_descriptions.yml",
            demo_kwargs=kwargs["demo_kwargs"]
        )

        prompt_sections = prompts[0].split('\n\n')

        prompt = '\n\n'.join(prompt_sections[:-1])
        action_choices = prompt_sections[-1]

        return [prompt], [action_choices]

### ------------------------ Run ADM inference to generate response ------------------------ ###
@app.callback(
    [Output('system-response', 'value')],
    [Input('run-button', 'n_clicks')],
    [State('alignment-target-store', 'data'),
     State('dataset-store', 'data'),
     State('system-prompt','value'),
     State('scenario-id-dropdown', 'value'),
     State('probe-id-dropdown', 'value')],
    prevent_initial_call=True
)
def run_model(n_clicks, alignment_target, scenarios, system_prompt, scenario_id, probe_id):

    if n_clicks > 0:
        for scenario in scenarios[scenario_id]:
            state, actions = hydrate_scenario_state(scenario)
            actions_filtered = filter_actions(state, actions)
            state_dict = state.to_dict()
            if state_dict["meta_info"]["probe_response"] is not None:
                if probe_id != state_dict["meta_info"]["probe_response"]["probe_id"]:
                    continue
                probe_id = state_dict["meta_info"]["probe_response"]["probe_id"]
        if alignment_target is not None:
            alignment_target = OmegaConf.create(alignment_target)

        if isinstance(system_prompt, list):
            system_prompt = system_prompt[0]

        top_level_system_prompt = system_prompt.split('\n\n')[0].split('[INST]')[1]
        state.unstructured = system_prompt.split('\n\n')[2].split('\n')[1]
        character_unstructured = system_prompt.split('\n\n')[1].split('\n')[1:]
        print(character_unstructured)
        for i, j in zip(range(len(state.characters)), range(0, len(state.characters) * 2, 2)):
            state.characters[i].unstructured = character_unstructured[j].split(':')[1]
            state.characters[i].intent = character_unstructured[j+1].split(':')[1]

        adm.instance.system_ui_prompt = top_level_system_prompt

        kwargs = {
            'demo_kwargs': {
                'max_generator_tokens': 8092,
                'generator_seed': 2,
                'shuffle_choices': False
            }
        }
        action_taken, _ = adm.instance.top_level_choose_action(
            scenario_state=state,
            available_actions=actions_filtered,
            alignment_target=alignment_target,
            kdma_descriptions_map='configs/prompt_engineering/kdma_descriptions.yml',
            tokenizer_kwargs={'truncation': False},
            demo_kwargs=kwargs["demo_kwargs"])

        actions_filtered_dicts = [action.to_dict() for action in actions_filtered]
        action_taken_dict = action_taken.to_dict()
        for action_gt in actions_filtered_dicts:
            if action_gt['action_id'] == action_taken_dict['action_id']:
                chosen_action_gt = action_gt
                break

        chosen_action_gt = chosen_action_gt["unstructured"]
        return [
            f"ACTION CHOICE:\n"
            f"{chosen_action_gt}"
            f"\n\nJUSTIFICATION:\n"
            f"{action_taken.justification}"
        ]

@app.callback(
    [Output('system-response-2', 'value')],
    [Input('run-button-2', 'n_clicks')],
    [State('alignment-target-store-2', 'data'),
     State('dataset-store', 'data'),
     State('system-prompt-2','value'),
     State('scenario-id-dropdown', 'value'),
     State('probe-id-dropdown', 'value')],
    prevent_initial_call=True
)
def run_model_2(n_clicks, alignment_target, scenarios, system_prompt, scenario_id, probe_id):

    if n_clicks > 0:
        for scenario in scenarios[scenario_id]:
            state, actions = hydrate_scenario_state(scenario)
            actions_filtered = filter_actions(state, actions)
            state_dict = state.to_dict()
            if state_dict["meta_info"]["probe_response"] is not None:
                if probe_id != state_dict["meta_info"]["probe_response"]["probe_id"]:
                    continue
                probe_id = state_dict["meta_info"]["probe_response"]["probe_id"]
        if alignment_target is not None:
            alignment_target = OmegaConf.create(alignment_target)

        if isinstance(system_prompt, list):
            system_prompt = system_prompt[0]

        top_level_system_prompt = system_prompt.split('\n\n')[0].split('[INST]')[1]
        state.unstructured = system_prompt.split('\n\n')[2].split('\n')[1]
        character_unstructured = system_prompt.split('\n\n')[1].split('\n')[1:]
        print(character_unstructured)
        for i, j in zip(range(len(state.characters)), range(0, len(state.characters) * 2, 2)):
            state.characters[i].unstructured = character_unstructured[j].split(':')[1]
            state.characters[i].intent = character_unstructured[j+1].split(':')[1]

        adm_2.instance.system_ui_prompt = top_level_system_prompt

        kwargs = {
            'demo_kwargs': {
                'max_generator_tokens': 8092,
                'generator_seed': 2,
                'shuffle_choices': False
            }
        }
        action_taken, _ = adm_2.instance.top_level_choose_action(
            scenario_state=state,
            available_actions=actions_filtered,
            alignment_target=alignment_target,
            kdma_descriptions_map='configs/prompt_engineering/kdma_descriptions.yml',
            tokenizer_kwargs={'truncation': False},
            demo_kwargs=kwargs["demo_kwargs"]
        )

        actions_filtered_dicts = [action.to_dict() for action in actions_filtered]
        action_taken_dict = action_taken.to_dict()
        for action_gt in actions_filtered_dicts:
            if action_gt['action_id'] == action_taken_dict['action_id']:
                chosen_action_gt = action_gt
                break

        chosen_action_gt = chosen_action_gt["unstructured"]
        return [
            f"ACTION CHOICE:\n"
            f"{chosen_action_gt}"
            f"\n\nJUSTIFICATION:\n"
            f"{action_taken.justification}"
        ]

if __name__ == '__main__':
    app.run_server(debug=True, port=8052)
