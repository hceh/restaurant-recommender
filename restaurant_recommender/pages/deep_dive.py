from urllib.parse import parse_qs

import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from restaurant_recommender.data_collector import BusinessDataSet

base_data = BusinessDataSet(category='restaurant', state='ON')
cities_fix = {
    'East Gwillimburry': 'East Gwillimbury',
    'ETOBICOKE': 'Etobicoke',
    'Etibicoke': 'Etobicoke',
    'Etobiicoke': 'Etobicoke',
    'King': 'King City',
    'Oakridges': 'Oak Ridges',
    'Oakvile': 'Oakville',
    'Richmond Hil': 'Richmond Hill',
    'Scarobrough': 'Scarborough',
    'Thornhil': 'Thornhill',
    'Tornto': 'Toronto',
    'Whiitby': 'Whitby',
    'Whtiby': 'Whitby',
}
base_data.fix_values('city', cities_fix)

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
    if '?' not in url:
        return 'No specific tag specified'
    params = parse_qs(url)
    selected = base_data.data.loc[params.get('?id')].iloc[0]

    return selected['name']
