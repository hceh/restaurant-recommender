import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2('Homepage'),
            dcc.Graph()
        ])
    ])
])
