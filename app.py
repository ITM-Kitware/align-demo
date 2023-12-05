import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import json
import io
import yaml
import os

from algorithms import get_algorithm

# Make sure you have your 'dataset.json' in your project directory
with open('data/bbn-data.json', 'r') as f:
    dataset = json.load(f)

# Function to list YAML files in configs directory.
def list_config_files(dir_path='configs'):
    return [file for file in os.listdir(dir_path) if file.endswith('.yaml') or file.endswith('.yml')]

# Initialize an algorithm with an empty config as a placeholder
algorithm = None

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(fluid=False, style={'width': '50%'}, children=[
    html.H1('Align-demo', className='mb-4'),

    html.Label('Probe ID:', className='mb-2'),
    dcc.Dropdown(
        id='probe-id-dropdown',
        options=[{'label': pid, 'value': pid} for pid in dataset.keys()],
        placeholder='Select a probe ID...',
        className='mb-3',
    ),

    html.Label('Scenario:', className='mb-2'),
    dbc.Textarea(
        id='scenario-input',
        className='mb-3',
        placeholder='Enter scenario...',
        style={'height': '150px'},
    ),
    html.Label('Probe:', className='mb-2'),
    dbc.Textarea(
        id='probe-input',
        className='mb-3',
        placeholder='Enter probe...',
        style={'height': '80px'},
    ),
    html.Label('Responses:', className='mb-2'),
    dbc.Textarea(
        id='responses-input',
        className='mb-3',
        placeholder='Enter responses...',
        style={'height': '150px'},
    ),

    html.Label('Configuration Files:', className='mb-2'),
    dcc.Dropdown(
        id='config-files-dropdown',
        options=[
            {'label': filename, 'value': os.path.join('configs', filename)}
            for filename in list_config_files()
        ],
        placeholder='Select a configuration file...',
        className='mb-3',
    ),
    
    html.Label('ADM Configuration (YAML):', className='mb-2'),
    dbc.Textarea(
        id='adm-config-input',
        className='mb-3',
        placeholder='Enter ADM configuration in YAML format...',
        style={'height': '150px'},
    ),

    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-indicator",
                children=[
                    dbc.Button('LOAD MODEL', id='load-model-button', color='primary', className='mb-3'),
                ],
                type="default"
            ),
        ]),
        dbc.Col([
            dbc.Button('RUN', id='run-button', color='primary', className='mb-3'),
        ]),
    ]),

    html.Label('Chosen Response:', className='mb-2'),
    html.Div(
        id='chosen-response-output',
        className='mb-3',
        style={'whiteSpace': 'pre-line'}
    ),

    html.Label('Justification:', className='mb-2'),
    dbc.Textarea(
        id='justification-output',
        readOnly=True,
        placeholder='Justification for the chosen response will appear here...',
        style={'height': '150px'}
    ),

    html.Label('Log:', className='mb-2'),
    dbc.Textarea(
        id='log-output',
        readOnly=True,
        placeholder='Log output will appear here...',
        style={'height': '200px', 'overflow': 'auto'},
    ),
])

# Callback to update scenario, probe, and responses when a probe ID is selected
@app.callback(
    [Output('scenario-input', 'value'),
     Output('probe-input', 'value'),
     Output('responses-input', 'value')],
    [Input('probe-id-dropdown', 'value')]
)
def update_spr_inputs(probe_id):
    if probe_id and probe_id in dataset:
        entry = dataset[probe_id]
        return entry['scenario'], entry['probe'], '\n'.join(entry['choices'])
    else:
        return '', '', ''

# Callback for loading the model when the load model button is clicked and disabling the button
@app.callback(
    [Output('load-model-button', 'disabled'), 
     Output('log-output', 'value'),
     Output('run-button', 'disabled')],
    [Input('load-model-button', 'n_clicks')],
    [State('adm-config-input', 'value')],
    # prevent_initial_call=True
)
def load_model(n_clicks, config_yaml):
    global algorithm
    if n_clicks is not None and n_clicks > 0:
        if config_yaml:
            try:
                config = yaml.safe_load(config_yaml)
                # The actual loading of the algorithm should be wrapped with a loading indicator
                # handled by the frontend
                algorithm = get_algorithm(config)
                if algorithm is None:
                    return True, f'Error loading model with config:\n{json.dumps(config, indent=2)}', True

                return False, f'Algorithm loaded with the following config:\n{json.dumps(config, indent=2)}', False
            except yaml.YAMLError as e:
                return True, f'Error parsing YAML:\n{e}', True
        return True, 'No config provided', True
    return False, '', algorithm is None

# Callback to load YAML file into the ADM Configuration textarea
@app.callback(
    Output('adm-config-input', 'value'),
    [Input('config-files-dropdown', 'value')],
    prevent_initial_call=True
)
def load_yaml(config_file_path):
    if config_file_path is not None:
        if config_file_path:
            try:
                with open(config_file_path, 'r') as f:
                    config_yaml = f.read()
                return config_yaml
            except Exception as e:
                return f'Error loading YAML file: {e}'
        else:
            return 'No configuration file selected.'
    return ''


# Callbacks to update the chosen and justification outputs when RUN button is clicked
@app.callback(
    [Output('chosen-response-output', 'children'),
     Output('justification-output', 'value'),
     Output('log-output', 'value', allow_duplicate=True)
    ],
    [Input('run-button', 'n_clicks')],
    [State('scenario-input', 'value'),
     State('probe-input', 'value'),
     State('responses-input', 'value')],
    prevent_initial_call=True
)
def run_model(n_clicks, scenario, probe, responses):
    # if any of the inputs are None, return empty strings
    if None in [scenario, probe, responses]:
        return '', '', ''

    # if any are just whitespace, return empty strings
    if scenario.isspace() or probe.isspace() or responses.isspace():
        return '', '', ''

    if n_clicks is not None and n_clicks > 0:
        # create a StringIO object to capture the print output
        log_file = io.StringIO()
        result = algorithm(
            {
                'scenario': scenario,
                'probe': probe,
                'state': None,
                'choices': responses.split('\n')
            },
            None,
            log_file=log_file
        )
        response_lines = responses.split('\n')
        chosen_response = response_lines[result['choice']] if response_lines else ''
        justification = json.dumps(result['info'])
        return chosen_response, justification, log_file.getvalue()
    else:
        return '', '', ''

if __name__ == '__main__':
    app.run_server(debug=True)