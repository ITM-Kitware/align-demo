from typing import Dict, Tuple
from dash import dcc, html
import plotly.graph_objs as go
import dash_bootstrap_components as dbc


def predicted_kdma_widget(predicted_kdma_values: Dict[str, int], label_kdma_values: Dict[str, int]=None, target_kdma_values: Dict[str, int]=None):
    print(predicted_kdma_values, label_kdma_values, target_kdma_values)
    categories = list(predicted_kdma_values.keys())

    if target_kdma_values is not None:
        categories = list(set(categories) & set(target_kdma_values.keys()))

    if label_kdma_values is not None:
        categories = list(set(categories) & set(label_kdma_values.keys()))
    
    predicted_values = [predicted_kdma_values[category] for category in categories]

    data = [go.Scatterpolar(
        r=predicted_values,
        theta=categories,
        fill='toself',
        name='Predicted'
    )]

    if label_kdma_values is not None:
        label_values = [label_kdma_values[category] for category in categories]
        data.append(
            go.Scatterpolar(
                r=label_values,
                theta=categories,
                fill='toself',
                name='Actual Label'
            )
        )

    if target_kdma_values is not None:
        target_values = [target_kdma_values[category] for category in categories]
        data.append(
            go.Scatterpolar(
                r=target_values,
                theta=categories,
                fill='toself',
                name='Target'
            )
        )

    layout = go.Layout(
        polar=dict(radialaxis=dict(
            visible=True,
            range=[0, max(max(predicted_values), *(label_values if label_kdma_values else []), *(target_values if target_kdma_values else []))],
        )),
        showlegend=True
    )

    return dcc.Graph(figure=go.Figure(data=data, layout=layout))


def predicted_kdma_choices_widget(choices_with_values: Dict[str, Tuple[Dict[str, int], Dict[str, int], Dict[str, int]]], choice_idx: int=None):
    cards = [
        dbc.Col(
            dbc.Card(
                [
                    dbc.CardHeader(html.H3(choice)),
                    dbc.CardBody(
                        [
                            predicted_kdma_widget(
                                predicted_kdma_values=predicted_kdma_values,
                                label_kdma_values=label_kdma_values,
                                target_kdma_values=target_kdma_values
                            )
                        ]
                    ),
                ],
                style={'width': '100%', 'margin-bottom': '10px', 'background-color': 'lightgreen' if i == choice_idx else 'white'}  # Adjust the card's width, margin, and background color as necessary
            ),
            width=6  # Bootstrap grid system allows up to 12 columns across the page, 'width=4' means 3 cards per row
        )
        for i, (choice, (predicted_kdma_values, label_kdma_values, target_kdma_values)) in enumerate(choices_with_values.items())
    ]

    # Now use dbc.Row to arrange the cards into a grid
    card_grid = dbc.Row(cards, justify='start')  # You can adjust justify to 'center', 'end', 'between', 'around', etc.

    return html.Div(card_grid)


def make_results_widget(choices, model_response, target_kdmas, label_kdmas=None):
    if 'predicted_kdmas' in model_response:
        predicted_kdmas = model_response['predicted_kdmas']
        
        choices_with_values = {
            choice: (
                predicted_kdmas[i],
                label_kdmas[i] if label_kdmas is not None else None,
                target_kdmas
            )
            for i, choice in enumerate(choices)
        }
        
        return predicted_kdma_choices_widget(choices_with_values, choice_idx=model_response['choice'])
    return None
    


# def algo_inputs