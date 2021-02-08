import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from app import app

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2(id='deep-dive-header')
        ])
    ])
])


@app.callback(
    Output('deep-dive-header', 'children'),
    [Input('url', 'search')]
)
def update_header(url):
    if '?' in url:
        return url
    else:
        return 'No specific tag specified'
