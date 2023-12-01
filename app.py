import dash
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from dash import dcc, html
import json
import io

from align_system.algorithms.llama_index import LlamaIndex

# domain_docs_dir: /data/shared/MVPData/DomainDocumentsPDF/
#   device: cuda
#   model_name: falcon
#   retrieval_enabled: true

algorithm = LlamaIndex(
    domain_docs_dir='/data/shared/MVPData/DomainDocumentsPDF/',
    device='cuda',
    model_name='falcon',
    retrieval_enabled=True
)
algorithm.load_model()

# Define your Bootstrap theme
BOOTSTRAP_THEME = dbc.themes.BOOTSTRAP

# Initialize the Dash app with Bootstap theme
app = dash.Dash(__name__, external_stylesheets=[BOOTSTRAP_THEME])

# Define the layout of the app with Bootstrap components
app.layout = dbc.Container(fluid=False, style={'width': '70%'}, children=[
    html.H1('Align-demo', className='mb-4'),

    html.Label('Scenario:', className='mb-2'),
    dbc.Textarea(
        id='scenario-input',
        className='mb-3',
        placeholder='Enter scenario...',
        style={'height': '200px'},
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
    dbc.Button('RUN', id='run-button', color='primary', className='mb-3'),
    html.Br(),  # Add a line break to create spacing
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
])

# Callbacks to update the chosen and justification outputs when RUN button is clicked
@app.callback(
    [
        Output('chosen-response-output', 'children'),
        Output('justification-output', 'value')
    ],
    [Input('run-button', 'n_clicks')],
    [State('scenario-input', 'value'),
     State('probe-input', 'value'),
     State('responses-input', 'value')]
)
def run_model(n_clicks, scenario, probe, responses):
    # if any of the inputs are None, return empty strings
    if None in [scenario, probe, responses]:
        return '', ''
    
    # if any are just whitespace, return empty strings
    if scenario.isspace() or probe.isspace() or responses.isspace():
        return '', ''
    
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
        # add log output to justification
        justification += '\n\nLOG:' + log_file.getvalue()
        return chosen_response, justification
    else:
        return '', ''

# Run the app
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)