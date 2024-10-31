import json
import os

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd

from omegaconf import OmegaConf
import hydra
from align_system.utils.hydrate_state import hydrate_scenario_state
from align_system.prompt_engineering.outlines_prompts import scenario_state_description_1

from action_filtering import filter_actions

# Function to list YAML files in configs directory.
def list_config_files(dir_path):
    return [file for file in os.listdir(dir_path) if file.endswith('.yaml') or file.endswith('.yml')]

def list_json_files(dir_path='oracle-json-files'):
    return [file for file in os.listdir(dir_path) if file.endswith('.json')]

# Initialize an algorithm with an empty config as a placeholder
adm = None

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE, dbc.icons.BOOTSTRAP])

# Define the attributes and initial values
attributes = ['ingroup_bias', 'moral_judgement', 'value_of_life', 'quality_of_life']
num_attributes = len(attributes)
initial_values = [5] * num_attributes

app.layout = dbc.Container(fluid=True, style={'width': '60%'}, children=[
    html.H1('Align-Demo', className='mb-4'),

    dcc.Store(id='attributes-store', data={
        'target_kdma_values': {
            attribute: value
            for attribute, value in zip(attributes, initial_values)
        }
    }),  # Store component to keep track of attribute values

    dcc.Store(id='dataset-store'),
    dcc.Store(id='scenario-id-store'),
    dcc.Store(id='alignment-target-store'),
    dcc.Store(id="action-store"),
    dcc.Store(id="action-gt-store"),
    dcc.Store(id="justification-store"),
    dcc.Store(id='log-store'),

    dbc.Row([
        dbc.Col([
            html.Label('Input Dataset:', className='mb-2', style={'font-size': 25}),
            dcc.Dropdown(
                id='dataset-dropdown',
                options=[{'label': i, 'value': i} for i in list_json_files()],
                style={"height": '40px',
                       'font-size': 22}
            )
        ]),

        dbc.Col([
            html.Label('Scenario ID:', className='mb-2', style={'font-size': 25}),
            dcc.Dropdown(
                id='scenario-id-dropdown',
                options=[],
                placeholder='Select a Scenario ID...',
                className='mr-3',
                style={"height": '40px',
                       'font-size': 22}
            ),
        ]),
        dbc.Col([
            html.Label('Probe ID:', className='mb-2', style={'font-size': 25}),
            dcc.Dropdown(
                id='probe-id-dropdown',
                options=[],
                placeholder='Select a probe ID...',
                className='mr-3',
                style={"height": '40px',
                       'font-size': 22}

            )
        ])
    ]),

    html.Div([
        dbc.Accordion([
            dbc.AccordionItem(
                [
                    html.Label('Scenario:', className='mb-2', style={'font-size': 25}),
                    dbc.Textarea(
                        id='scenario-input',
                        className='mb-3',
                        readOnly=True,
                        placeholder='Enter scenario...',
                        style={'height': '250px', 'font-size': 22},
                    ),

                    html.Label('Probe:', className='mb-2', style={'font-size': 25}),
                    dbc.Textarea(
                        id='probe-input',
                        readOnly=True,
                        className='mb-3',
                        placeholder='Enter probe...',
                        style={'height': '80px', 'font-size': 22},
                    ),

                    html.Label('Action Choices:', className='mb-2', style={'font-size': 25}),
                    dbc.Textarea(
                        id='responses-input',
                        readOnly=True,
                        className='mb-3',
                        placeholder='Enter responses...',
                        style={'height': '150px', 'font-size': 22},
                    )
                ], title=html.Label('Scenario-State Prompt', style={'font-size': 25})
            ),
        ]), html.Div(id="scenario-accordion", className="mt-4")
    ]),

    html.Label('Configuration Files:', className='mb-2', style={'font-size': 25}),
    dcc.Dropdown(
        id='alignment-target-dropdown',
        options=[
            {'label': filename, 'value': os.path.join('configs/hydra/alignment_target', filename)}
            for filename in list_config_files('configs/hydra/alignment_target')
        ],
        placeholder='Select a configuration file...',
        className='mb-3',
        style={'font-size': 22}
    ),

    html.Label('ADM Configuration (YAML):', className='mb-2', style={'font-size': 25}),
    dcc.Dropdown(
        id='adm-config-input',
        options=[
            {'label': filename, 'value': os.path.join('configs/hydra/adm', filename)}
            for filename in list_config_files('configs/hydra/adm')
        ],
        className='mb-3',
        placeholder='Select ADM configuration..',
        style={'font-size': 22}
    ),

    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-indicator-load",
                children=[
                    dbc.Button('LOAD MODEL', id='load-model-button', color='primary', className='mb-3'),
                ],
                type="default"
            ),
        ]),
        dbc.Col([
            dcc.Loading(
                id="loading-indicator-run",
                children=[
                    dbc.Button('RUN MODEL', id='run-button', color='primary', className='mb-3'),
                ],
                type="default"
            ),
        ]),
        dbc.Col([
            dbc.Button('DISPLAY RESULTS', id='results-button', color='primary', className='mb-3'),
        ]),
    ]),

    dcc.Loading(
        html.Div([
            html.Label('Chosen Response:', className='mb-2', style={'font-size': 25}),
            dbc.Row([
                dbc.Col([
                    dbc.Textarea(
                        id='action-output',
                        readOnly=True,
                        className='mb-3',
                        style={'height': '50px'}
                    ),
                ]),
                dbc.Col([
                    dbc.Textarea(
                        id='kdma-output',
                        readOnly=True,
                        className='mb-3',
                        style={'height': '50px'}
                    ),
                ]),
            ]),

            html.Label('Justification:', className='mb-2', style={'font-size': 25}),
            dbc.Textarea(
                id='justification-output',
                readOnly=True,
                placeholder='Justification for the chosen response will appear here...',
                style={'height': '150px'}
            ),


            html.Label('GT vs Predicted KDMA:', className='mb-2'),
            dcc.Graph(id="kdma-bar-chart")
        ], id='results', style={'display': 'none'})
    )
])

@app.callback(
    [Output('dataset-store', 'data'),
     Output('scenario-id-store', 'data')],
    Input('dataset-dropdown', 'value'),
    prevent_initial_call=True
)
def update_dataset_store(selected_dataset):
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

@app.callback(
    Output('scenario-id-dropdown', 'options'),
    Input('scenario-id-store', 'data'),
    prevent_initial_call=True
)
def update_scenario_id_dropdown(scenario_ids):
    if scenario_ids:
        return [{'label': scenario_id, 'value': scenario_id} for scenario_id in scenario_ids]
    else:
        return []

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

# Callback to update scenario, probe, and responses when a probe ID is selected
@app.callback(
    [Output('scenario-input', 'value'),
     Output('probe-input', 'value'),
     Output('responses-input', 'value')],
    [State('dataset-store', 'data'),
     State('scenario-id-dropdown', 'value')],
    Input('probe-id-dropdown', 'value'),
    prevent_initial_call=True,
)
def update_spr_inputs(scenarios, scenario_id, probe_id):
    for scenario in scenarios[scenario_id]:
        state, actions = hydrate_scenario_state(scenario)
        actions_filtered = filter_actions(state, actions)
        state_dict = state.to_dict()
        if state_dict["meta_info"]["probe_response"] is not None:
            if probe_id != state_dict["meta_info"]["probe_response"]["probe_id"]:
                continue
            probe_id = state_dict["meta_info"]["probe_response"]["probe_id"]
    if probe_id:
        action_ids = []
        for action in actions_filtered:
            action_id_split = action.action_id.split('_')
            action_ids.append(action_id_split[0].capitalize() + ' ' + ' '.join(act.capitalize() for act in action_id_split[1:]))
        return (
            scenario_state_description_1(state),
            'Who would you treat?',
            '\n'.join(action for action in sorted(action_ids))
        )
    else:
        return '', '', ''

# Callback to load alignment target
@app.callback(
    [Output('alignment-target-store', 'data')],
    [Input('alignment-target-dropdown', 'value')],
    prevent_initial_call=True,
)
def load_alignment_target(config):
    if config:
        alignment_target = OmegaConf.load(config)
        alignment_target = OmegaConf.to_object(alignment_target)
    else:
        alignment_target = None
    return [alignment_target]


# Callback for loading the model when the load model button is clicked and disabling the button
@app.callback(
    Output('load-model-button', 'disabled'),
    [Input('load-model-button', 'n_clicks')],
    [State('adm-config-input', 'value')],
    prevent_initial_call=True
)
def load_model(n_clicks, config_yaml_path):
    adm_config = OmegaConf.load(config_yaml_path)
    global adm
    adm = hydra.utils.instantiate(adm_config, recursive=True)
    if n_clicks > 0:
        return True

@app.callback(
    [Output('run-button', 'disabled'),
     Output('action-gt-store', 'data', allow_duplicate=True),
     Output('action-store', 'data', allow_duplicate=True),
     Output('justification-store', 'data', allow_duplicate=True)],
    [Input('run-button', 'n_clicks')],
    [State('alignment-target-store', 'data'),
     State('dataset-store', 'data'),
     State('scenario-id-dropdown', 'value'),
     State('probe-id-dropdown', 'value')],
    prevent_initial_call=True
)
def run_model(n_clicks, alignment_target, scenarios, scenario_id, probe_id):
    for i, scenario in enumerate(scenarios[scenario_id]):
        state, actions = hydrate_scenario_state(scenario)
        actions_filtered = filter_actions(state, actions)
        state_dict = state.to_dict()
        if state_dict["meta_info"]["probe_response"] is not None:
            if probe_id != state_dict["meta_info"]["probe_response"]["probe_id"]:
                continue
            probe_id = state_dict["meta_info"]["probe_response"]["probe_id"]

    if alignment_target is not None:
        alignment_target = OmegaConf.create(alignment_target)

    action_taken = adm.instance.choose_action(
        scenario_state=state,
        available_actions=actions_filtered,
        alignment_target=alignment_target,
        kdma_descriptions_map='/data/users/barry.ravichandran/ITM/align-system/align_system/prompt_engineering/kdma_descriptions.yml',
        **adm.get('inference_kwargs', {}))

    actions_filtered_dicts = [action.to_dict() for action in actions_filtered]
    action_taken_dict = action_taken[0].to_dict()
    for action_gt in actions_filtered_dicts:
        if action_gt['action_id'] == action_taken_dict['action_id']:
            chosen_action_gt = action_gt
            break

    return (
        None,
        [chosen_action_gt],
        [action_taken_dict],
        [str(action_taken[0].justification.rstrip())]
    )

# Callbacks to update the chosen and justification outputs when RUN button is clicked
@app.callback(
    [Output('action-output', 'value'),
     Output('kdma-output', 'value'),
     Output('justification-output', 'value'),
     Output('kdma-bar-chart', 'figure'),
     Output('results', 'style')],
    [Input('results-button', 'n_clicks')],
    [State('action-gt-store', 'data'),
     State('action-store', 'data'),
     State('justification-store', 'data')],
    prevent_initial_call=True
)
def display_results(n_clicks, gt, chosen_response, justification):

    if n_clicks is not None and n_clicks > 0:
        gt_action = gt[0]["kdma_association"]
        action_id_chosen = chosen_response[0]["action_id"]
        action_chosen = "Action: " + action_id_chosen
        kdma_chosen = "KDMA: " + str(chosen_response[0]["kdma_association"])
        gt_value = list(gt_action.values())[0] if gt_action is not None else 0
        kdma_value = list(chosen_response[0]["kdma_association"].values())[0]
        df_kdma = pd.DataFrame({"x_data":["GT_KDMA", "Chosen KDMA"], "y_data": [gt_value, kdma_value]})
        fig = px.bar(df_kdma, x="x_data", y="y_data", title="KDMA", width=800, height=400)
        return action_chosen, kdma_chosen, justification, fig, {'display': 'block'}
    else:
        return '', '', '', None, {'display': 'none'}


if __name__ == '__main__':
    app.run_server(debug=True)
