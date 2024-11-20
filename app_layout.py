import os

import dash_bootstrap_components as dbc
from dash import dcc, html

# Function to list YAML files in configs directory.
def list_adms():
    return ['outlines_transformers_structured']

def list_json_files(dir_path='oracle-json-files'):
    return [str(file) for file in os.listdir(dir_path) if file.endswith('.json')]

def list_llm_backbones():
    return ['mistralai/Mistral-7B-Instruct-v0.2', 'meta-llama/Meta-Llama-3-8B-Instruct']

# Define the attributes and initial values
attributes = ['moral_deservingness', 'maximization']
num_attributes = len(attributes)
initial_values = [5] * num_attributes


load_dataset_components = (
    dbc.Col([
        html.Label('Input Dataset:', className='mb-2', style={'font-size': 25}),
        dcc.Dropdown(
            id='dataset-dropdown',
            options=[{'label': i, 'value': i} for i in list_json_files()],
            placeholder="Select Dataset...",
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
)

model_1_layout = (
    dbc.Stack([
        dbc.Col([
            html.Label('LLM Chat backbone:', className='mb-1', style={'font-size': 22}),
            dcc.Dropdown(
                id='llm-dropdown',
                options=[{'label': i, 'value': i} for i in list_llm_backbones()],
                className='dropdown-class-1',
                placeholder='Select LLM chat backbone',
                style={'font-size': 22, 'width': '100%'}
            ),
        ]),
        dbc.Col([
            html.Label('Algorithm:', className='mb-2', style={'font-size': 22}),
            dcc.Dropdown(
                id='adm-config-input',
                options=[
                    {'label': filename, 'value': filename}
                    for filename in list_adms()
                ],
                className='dropdown-class-1',
                placeholder='Select Algorithm..',
                style={'font-size': 22, 'width': '100%'}
            ),
        ]),
        dcc.Checklist(
            id='system-prompt-checklist',
            options=[
                {'label': 'Aligned', 'value': 'aligned'},
            ],
            className='mt-4',
            style={'font-size': 22}
        ),
        dcc.Loading(
            id="loading-indicator-model",
            children=[
                dbc.Button('LOAD MODEL', id='load-model-button',
                            color='primary', className='mt-5'),
            ],
            type="default",
        ),
    ], direction='horizontal', gap=3),
    html.Hr(),
    dbc.Stack([
        html.Label('Alignment Attribute Target:', className='mb-2', style={'font-size': 22}),
        dcc.Dropdown(
            id='kdma-dropdown',
            options=[{'label': i, 'value': i} for i in attributes],
            className='dropdown-class-1',
            placeholder='Select Alignment Attribute...',
            style={'font-size': 22, 'width': '100%'}
        ),
    ], id='alignment-target-stack', direction='vertical', gap=3, style={'display': 'none'}),
    html.Div([
        dcc.Slider(0, 1, 0.1,
            value=0.8,
            id='kdma-slider',
        ),
    ], id='slider-div', style={'display': 'none'}),

    html.Div(id='space-div', style={'display': 'block', 'marginBottom': '170px'}),

    html.Hr(),
     dcc.Loading(
        id="loading-indicator-system-prompt",
        children=[
            dbc.Button('LOAD SYSTEM PROMPT', id='load-system-prompt-button', color='primary', className='mb-1'),
        ],
        type="default",
    ),
    dbc.Row([
        dbc.Col([
            html.Label('Prompt:', className='mt-2', style={'font-size': 25}),
            dbc.Textarea(
                id='system-prompt',
                value="",
                readOnly=False,
                className='mb-3',
                style={'height': '600px', 'font-size': 22},
            ),
        ]),
    ]),

    dbc.Row([
        dbc.Col([
            html.Label('Action Choices (READ-ONLY):', className='mt-2', style={'font-size': 25}),
            dbc.Textarea(
                id='action-choices-prompt',
                value="",
                readOnly=True,
                className='mb-3',
                style={'height': '200px', 'font-size': 22},
            ),
        ]),
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-indicator-run",
                children=[
                    dbc.Button('RUN MODEL', id='run-button', color='primary', className='mb-3'),
                ],
                type="default"
            ),
        ]),
    ]),

    dbc.Row([
        dbc.Col([
            html.Label('System Response:', className='mb-2', style={'font-size': 25}),
            dcc.Loading(
                id="loading-indicator-response",
                children=[
                    dbc.Textarea(
                        id='system-response',
                        readOnly=False,
                        className='mb-3',
                        style={'height': '300px', 'font-size': 22}
                    ),
            ], type="default"),
        ]),
    ]),
)


model_2_layout = (
    dbc.Stack([
        dbc.Col([
            html.Label('LLM Chat backbone:', className='mb-1', style={'font-size': 22}),
            dcc.Dropdown(
                id='llm-dropdown-2',
                options=[{'label': i, 'value': i} for i in list_llm_backbones()],
                className='dropdown-class-1',
                placeholder='Select LLM chat backbone',
                style={'font-size': 22, 'width': '100%'}
            ),
        ]),
        dbc.Col([
            html.Label('Algorithm:', className='mb-2', style={'font-size': 22}),
            dcc.Dropdown(
                id='adm-config-input-2',
                options=[
                    {'label': filename, 'value': filename}
                    for filename in list_adms()
                ],
                className='dropdown-class-1',
                placeholder='Select Algorithm..',
                style={'font-size': 22, 'width': '100%'}
            ),
        ]),
        dcc.Checklist(
            id='system-prompt-checklist-2',
            options=[
                {'label': 'Aligned', 'value': 'aligned'},
            ],
            className='mt-4',
            style={'font-size': 22}
        ),
        dcc.Loading(
            id="loading-indicator-model-2",
            children=[
                dbc.Button('LOAD MODEL', id='load-model-button-2',
                            color='primary', className='mt-5'),
            ],
            type="default",
        ),
    ], direction='horizontal', gap=3),
    html.Hr(),
    dbc.Stack([
        html.Label('Alignment Attribute Target:', className='mb-2', style={'font-size': 22}),
        dcc.Dropdown(
            id='kdma-dropdown-2',
            options=[{'label': i, 'value': i} for i in attributes],
            className='dropdown-class-1',
            placeholder='Select Alignment Attribute',
            style={'font-size': 22, 'width': '100%'}
        ),
    ], id='alignment-target-stack-2', direction='vertical', gap=3, style={'display': 'none'}),
    html.Div([
        dcc.Slider(0, 1, 0.1,
            value=0.8,
            id='kdma-slider-2',
        ),
    ], id='slider-div-2', style={'display': 'none'}),

    html.Div(id='space-div-2', style={'display': 'block', 'marginBottom': '170px'}),

    html.Hr(),
    dcc.Loading(
        id="loading-indicator-system-prompt-2",
        children=[
            dbc.Button('LOAD SYSTEM PROMPT', id='load-system-prompt-button-2', color='primary', className='mb-1'),
        ],
        type="default",
    ),
    dbc.Row([
        dbc.Col([
            html.Label('Prompt:', className='mt-2', style={'font-size': 25}),
            dbc.Textarea(
                id='system-prompt-2',
                value="",
                readOnly=False,
                className='mb-3',
                style={'height': '600px', 'font-size': 22}
            ),
        ]),
    ]),

    dbc.Row([
        dbc.Col([
            html.Label('Action Choices (READ-ONLY):', className='mt-2', style={'font-size': 25}),
            dbc.Textarea(
                id='action-choices-prompt-2',
                value="",
                readOnly=True,
                className='mb-3',
                style={'height': '200px', 'font-size': 22},
            ),
        ]),
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-indicator-run-2",
                children=[
                    dbc.Button('RUN MODEL', id='run-button-2', color='primary', className='mb-3'),
                ],
                type="default"
            ),
        ]),
    ]),

    dbc.Row([
        dbc.Col([
            html.Label('System Response:', className='mb-2', style={'font-size': 25}),
            dcc.Loading(
                id="loading-indicator-response-2",
                children=[
                    dbc.Textarea(
                        id='system-response-2',
                        readOnly=False,
                        className='mb-3',
                        style={'height': '300px', 'font-size': 22}
                    ),
            ], type="default"),
        ]),
    ]),
)
