import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html
import json

# Placeholder for the get_model function
def get_model():
    def model(scenario, probe, response):
        # Placeholder logic
        return {'choice': 0, 'reasoning': "Reasoning placeholder..."}
    return model

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1("Align-demo"),
    dcc.Textarea(
        id='scenario-input',
        value='',
        style={'width': '100%', 'height': 300},
        placeholder='Enter scenario...'
    ),
    dcc.Textarea(
        id='probe-input',
        value='',
        style={'width': '100%', 'height': 100},
        placeholder='Enter probe...'
    ),
    dcc.Textarea(
        id='responses-input',
        value='',
        style={'width': '100%', 'height': 200},
        placeholder='Enter responses...'
    ),
    html.Button('RUN', id='run-button', n_clicks=0),
    html.Div(id='chosen-response-output', style={'whiteSpace': 'pre-line'}),
    dcc.Textarea(
        id='justification-output',
        value='',
        style={'width': '100%', 'height': 300},
        readOnly=True,
        placeholder='Justification for the chosen response will appear here...'
    ),
])

# Callback for running the model and updating the output components
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
def run_model(n_clicks, scenario, probe, response):
    if n_clicks > 0:
        model = get_model()
        result = model(scenario, probe, response)
        response_lines = response.split('\n')
        chosen_response = response_lines[result['choice']]
        justification = result['reasoning']
        return chosen_response, justification
    else:
        return '', ''

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)