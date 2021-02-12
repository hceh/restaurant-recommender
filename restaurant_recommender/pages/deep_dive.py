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

def create_citymapper_link(row):
    return f'https://citymapper.com/directions?endcoord={row.latitude}%2C{row.longitude}&' \
           f"endname={row['name'].replace(' ', '%20')}&" \
           f"endaddress={row.address.replace(' ', '%20').replace(',', '%2C')}%2C%20{row.city}%2C%20{row.postal_code}"


layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2(id='deep-dive-header')
        ])
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Button(
                'Open in Citymapper',
                id='citymapper-link',
                color='success',
                className='mr-1',
                block=True,
            )
        ], width=3)
    ])
])


@app.callback(
    [Output('deep-dive-header', 'children'),
     Output('citymapper-link', 'href')],
    [Input('url', 'search')]
)
def update_header(url):
    if '?' not in url:
        selected = base_data.data.nlargest(1, 'rank_value').iloc[0]
    else:
        params = parse_qs(url)
        selected = base_data.data.loc[params.get('?id')].iloc[0]

    # todo:
    #  mini map zoomed for location
    #  opening hours
    #  top reviews
    #  description
    #  similar restaurants
    #  return to home button
    #  citymapper link using https://citymapper.com/tools/1053/launch-citymapper-for-directions

    return selected['name'], create_citymapper_link(selected)
