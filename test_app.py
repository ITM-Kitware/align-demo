# Import necessary libraries
from dash import Dash, html, dcc
import dash
from typing import Dict
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from dynamic_components import predicted_kdma_widget, predicted_kdma_choices_widget

import json



# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# TODO add a multi-select dropdown that allows the user to select multiple attributes that populate the interactive radar chart

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

# Define the layout of the app
app.layout = html.Div([
    dcc.Store(id='attributes-store', data={
        'target_kdma_values': {
            attribute: value
            for attribute, value in zip(attributes, initial_values)
        }
    }),  # Store component to keep track of attribute values
    
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
])

@app.callback(
    Output('attributes-store', 'data'),
    [Input('interactive-radar-chart', 'clickData')],
    [State('attributes-store', 'data')]
)
def update_store(clickData, data):
    if clickData is not None:
        clicked_theta = clickData['points'][0]['theta']
        clicked_r = clickData['points'][0]['r']
        data['target_kdma_values'][clicked_theta] = clicked_r
    return data


# Callback to update the radar chart based on click
@app.callback(
    Output('interactive-radar-chart', 'figure'),
    [Input('interactive-radar-chart', 'clickData')],
    [State('interactive-radar-chart', 'figure')]
)
def update_chart(clickData, figure):
    if clickData is not None:
        # Extract clicked theta and r
        clicked_theta = clickData['points'][0]['theta']
        clicked_r = clickData['points'][0]['r']
        
        # Update the corresponding value in the visible data
        for i, attribute in enumerate(attributes):
            if attribute == clicked_theta:
                if i < len(figure['data'][0]['r']):
                    figure['data'][0]['r'][i] = clicked_r
                    # No need to update hover text since it's disabled
                break

    # Update and return the figure
    return figure


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


# Run the app server (use debug=True if you want to enable the Dash debug mode)
if __name__ == '__main__':
    app.run_server(debug=True)