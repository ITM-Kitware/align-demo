import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import json
import io
import yaml
import os

from algorithms import get_algorithm
from dynamic_components import make_results_widget


with open('data/bbn-data.json', 'r') as f:
    dataset = json.load(f)

# Function to list YAML files in configs directory.
def list_config_files(dir_path='configs'):
    return [file for file in os.listdir(dir_path) if file.endswith('.yaml') or file.endswith('.yml')]

# Initialize an algorithm with an empty config as a placeholder
algorithm = None

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the attributes and initial values
attributes = ['basic_knowledge', 'time_pressure', 'risk_aversion', 'fairness', 'protocol_focus', 'utilitarianism']
num_attributes = len(attributes)
initial_values = [5] * num_attributes

# Generate a set of invisible points for the clickable area
invisible_points = []
for i in range(num_attributes):
    for r in range(11):  # From 0 to 10
        invisible_points.append(dict(
            type='scatterpolar',
            r=[r],
            theta=[attributes[i]],
            mode='markers',
            marker=dict(color='rgba(0,0,0,0)'),  # Make the points invisible
            text=[f"{attributes[i]} = {r}"],  # Initialize text for tooltips
            hoverinfo='text'
        ))

app.layout = dbc.Container(fluid=False, style={'width': '50%'}, children=[
    html.H1('Align-demo', className='mb-4'),
    
    dcc.Store(id='attributes-store', data={
        'target_kdma_values': {
            attribute: value
            for attribute, value in zip(attributes, initial_values)
        }
    }),  # Store component to keep track of attribute values
    
    html.Label('Target KDMA Values:', className='mb-2'),
    
    dcc.Dropdown(
        id='attribute-dropdown',
        options=[{'label': attr, 'value': attr} for attr in attributes],
        value=initial_values,  # Initialize with all attributes selected
        multi=True  # Enable multi-selection
    ),
    
    dcc.Graph(
        id='interactive-radar-chart',
        figure={
            'data': [
                go.Scatterpolar(
                    r=initial_values,
                    theta=attributes,
                    fill='toself',
                    name='Visible Data',
                    hoverinfo='skip'
                )

            ] + invisible_points,
            'layout': go.Layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 10]
                    )
                ),
                showlegend=False
            )
        },
        style={'height': '60vh'}
    ),

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

    dcc.Loading(
        html.Div([
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
            
            html.Div(id='result-holder', className='mb-3'),

            html.Label('Log:', className='mb-2'),
            dbc.Textarea(
                id='log-output',
                readOnly=True,
                placeholder='Log output will appear here...',
                style={'height': '200px', 'overflow': 'auto'},
            ),
        ], id='results', style={'display': 'none'})
    )
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
     Output('run-button', 'disabled'),
     Output('attributes-store', 'data', allow_duplicate=True)],
    [Input('load-model-button', 'n_clicks')],
    [State('adm-config-input', 'value'),
     State('attributes-store', 'data')],
    prevent_initial_call=True
)
def load_model(n_clicks, config_yaml, config):
    global algorithm
    if n_clicks is not None and n_clicks > 0:
        if config_yaml:
            try:
                algo_config = yaml.safe_load(config_yaml)
                # The actual loading of the algorithm should be wrapped with a loading indicator
                # handled by the frontend
                algorithm, config['algorithm'] = get_algorithm(algo_config)
                if algorithm is None:
                    return False, True, config

                return False, False, config
            except yaml.YAMLError as e:
                return False, True, config
        return False, True, config
    return False, algorithm is None, config


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
     Output('log-output', 'value', allow_duplicate=True),
     Output('result-holder', 'children'),
     Output('results', 'style')],
    [Input('run-button', 'n_clicks')],
    [State('scenario-input', 'value'),
     State('probe-input', 'value'),
     State('responses-input', 'value'),
     State('attributes-store', 'data')],
    prevent_initial_call=True
)
def run_model(n_clicks, scenario, probe, responses, config):
    # if any of the inputs are None, return empty strings
    if None in [scenario, probe, responses]:
        return '', '', '', dash.no_update, {'display': 'none'}

    # if any are just whitespace, return empty strings
    if scenario.isspace() or probe.isspace() or responses.isspace():
        return '', '', '', dash.no_update, {'display': 'none'}

    if n_clicks is not None and n_clicks > 0:
        # create a StringIO object to capture the print output
        log_file = io.StringIO()
        
        choices = responses.split('\n')
        
        result = algorithm(
            {
                'scenario': scenario,
                'probe': probe,
                'state': None,
                'choices': choices
            },
            target_kdma_values=config['target_kdma_values'],
            log_file=log_file,
            labels=[
                {
                    'basic_knowledge': 0
                }
                for _ in choices
            ],
            **config['algorithm']
        )
        response_lines = responses.split('\n')
        chosen_response = response_lines[result['choice']] if response_lines else ''
        justification = json.dumps(result['info'], indent=4) if 'info' in result else ''
        return chosen_response, justification, log_file.getvalue(), make_results_widget(response_lines, result, config['target_kdma_values']), {'display': 'block'}
    else:
        return '', '', '', dash.no_update, {'display': 'none'}

@app.callback(
    [Output('interactive-radar-chart', 'figure'),
     Output('attributes-store', 'data')],
    [Input('interactive-radar-chart', 'clickData')],
    [State('interactive-radar-chart', 'figure'),
     State('attributes-store', 'data'),
     State('attribute-dropdown', 'value')]
)
def update_chart_and_store(clickData, figure, data, selected_attributes):
    if clickData is not None:
        # Extract clicked theta and r
        clicked_theta = clickData['points'][0]['theta']
        clicked_r = clickData['points'][0]['r']
        
        # Update the corresponding value in the visible data
        for i, attribute in enumerate(figure['data'][0]['theta']):
            if attribute == clicked_theta:
                if i < len(figure['data'][0]['r']):
                    figure['data'][0]['r'][i] = clicked_r
                # No need to update hover text since it's disabled
                break
        
        # Update the target_kdma_values in the data store
        data['target_kdma_values'] = {
            attribute: value
            for attribute, value in zip(figure['data'][0]['theta'], figure['data'][0]['r']) if attribute in selected_attributes
        }
    
    print(data)
    
    return figure, data

@app.callback(
    Output('interactive-radar-chart', 'figure', allow_duplicate=True),
    [Input('attribute-dropdown', 'value'),
     Input('attributes-store', 'data')],
    [State('interactive-radar-chart', 'figure')],
    prevent_initial_call=True
)
def update_radar_chart(selected_attributes, store_data, figure):
    # If no attributes are selected, don't update the chart
    if not selected_attributes:
        raise dash.exceptions.PreventUpdate

    # Filter invisible points to include only selected attributes
    filtered_invisible_points = [
        dict(
            type='scatterpolar',
            r=[r],
            theta=[attribute],
            mode='markers',
            marker=dict(color='rgba(0,0,0,0)'),  # Make the points invisible
            text=[f"{attribute} = {r}"],  # Initialize text for tooltips
            hoverinfo='text'
        )
        for attribute in selected_attributes
        for r in range(11)  # From 0 to 10
    ]

    # Update the visible data based on selected attributes
    new_r_values = [store_data['target_kdma_values'].get(attr, 0) for attr in selected_attributes]
    new_figure_data = [
        go.Scatterpolar(
            r=new_r_values,
            theta=selected_attributes,
            fill='toself',
            name='Visible Data',
            hoverinfo='skip'
        )
    ] + filtered_invisible_points  # Use the filtered invisible points

    # Update the figure with new data and layout
    figure['data'] = new_figure_data

    # Update the layout to only show the selected attributes
    figure['layout'].update({
        'polar': {
            'radialaxis': {
                'visible': True,
                'range': [0, 10]
            },
            'angularaxis': {
                'visible': True,
                'theta': selected_attributes
            }
        }
    })

    return figure


if __name__ == '__main__':
    app.run_server(debug=True)