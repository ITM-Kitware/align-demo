import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import dcc, html
import json

# Placeholder for the get_model function
def get_model():
    # Note that this should be implemented to return a real model
    def model(scenario, probe, responses):
        # Placeholder logic
        return {'choice': 0, 'reasoning': "Reasoning placeholder..."}
    return model

# Define your Bootstrap theme
BOOTSTRAP_THEME = dbc.themes.BOOTSTRAP

# Initialize the Dash app with Bootstap theme
app = dash.Dash(__name__, external_stylesheets=[BOOTSTRAP_THEME])

# Define the layout of the app with Bootstrap components
app.layout = dbc.Container(fluid=True, children=[
    html.H1("Align-demo", className="mb-4"),
    
    dbc.Textarea(
        id='scenario-input',
        value='',
        className="mb-3",
        placeholder='Enter scenario...',
        style={'height': '200px'},
    ),
    dbc.Textarea(
        id='probe-input',
        value='',
        className="mb-3",
        placeholder='Enter probe...',
        style={'height': '80px'},
    ),
    dbc.Textarea(
        id='responses-input',
        value='',
        className="mb-3",
        placeholder='Enter responses...',
        style={'height': '150px'},
    ),
    dbc.Button('RUN', id='run-button', color="primary", className="mb-3"),
    
    html.Div(
        id='chosen-response-output',
        className="mb-3",
        style={'whiteSpace': 'pre-line'}
    ),
    
    dbc.Textarea(
        id='justification-output',
        value='',
        # bs_size="lg",
        readOnly=True,
        placeholder='Justification for the chosen response will appear here...',
        style={'height': '150px'}
    ),
])

# Callbacks to update the chosen and justification outputs when RUN button is clicked
@app.callback(
    [
        Output('chosen-response-output', 'children'),
        Output('justification-output', 'value')
    ],
    [
        Input('run-button', 'n_clicks')
    ],
    [
        State('scenario-input', 'value'),
        State('probe-input', 'value'),
        State('responses-input', 'value')
    ]
)
def run_model(n_clicks, scenario, probe, responses):
    if n_clicks is not None:
        model = get_model()
        result = model(scenario, probe, responses)
        response_lines = responses.split('\n')
        chosen_response = response_lines[result['choice']]
        justification = result['reasoning']
        return chosen_response, justification
    else:
        return '', ''

# Run the app
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)