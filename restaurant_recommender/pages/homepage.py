import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import plotly.graph_objects as go
from dash.dependencies import Output, Input, State
from geopy.distance import distance

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

config = {
    'displaylogo': False,
    'modeBarButtonsToRemove': ['zoom2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d', 'toggleSpikelines']
}


def create_location_map(df):
    hover_template = '<b>{}</b><br>{}<br>{}<br>{}<br>Rating: {:.1f}<extra></extra>'

    df['hover'] = [
        hover_template.format(row['name'], row.address, row.city, row.postal_code, row.stars)
        for ix, row in df.iterrows()
    ]

    fig = go.Figure(go.Scattermapbox(
        lat=df.latitude,
        lon=df.longitude,
        mode='markers',
        hovertemplate=df.hover,
    ))

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            zoom=8.5,
            center=go.layout.mapbox.Center(
                lat=(df.latitude.max() + df.latitude.min()) / 2,
                lon=(df.longitude.max() + df.longitude.min()) / 2,
            ),
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=600,
    )

    fig.update_geos(
        fitbounds='locations'
    )

    return fig


def card_creator(row):
    card = dbc.Card(
        dbc.CardBody(
            [
                html.H5(row['name'], className="card-title"),
                html.P([
                    row.address, html.Br(), row.categories, html.Br(), # row.city, html.Br(), row.postal_code, html.Br(),
                    f'Rating: {row.stars:.1f} / Reviews: {row.review_count:,.0f}'
                ], className='card-text'),
                dbc.Button(
                    "More info",
                    color='primary',
                    className="mt-auto",
                    href=f'/deep-dive?id={row.business_id}',
                    id=f'btn-{row.business_id}'
                ),
            ]
        ), id=f'homepage-card-{row.business_id}'
    )
    return card


layout = dbc.Container([
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H2('Where to eat in Toronto?'),
        ], width=8),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.Br(),
            dbc.FormGroup([
                dbc.Label('City', html_for='homepage-city-selector'),
                dcc.Dropdown(
                    id='homepage-city-selector',
                    options=[{'value': _, 'label': _} for _ in base_data.get_cities()],
                    value=None,
                    multi=True,
                    clearable=True,
                ),
            ]),
            html.Hr(),
            dbc.FormGroup([
                dbc.Label('Category Search', html_for='homepage-cat-search'),
                dbc.Input(id='homepage-cat-search', placeholder='Try Poutine...', type='text')
            ]),
            html.Hr(),
            dbc.FormGroup([
                dbc.Label('Restaurant Search', html_for='homepage-rest-search'),
                dbc.Input(id='homepage-rest-search', placeholder='Subway?', type='text')
            ]),
            html.Hr(),
            dbc.FormGroup([
                dbc.Label('Minimum Rating', html_for='homepage-star-min'),
                dcc.Dropdown(
                    id='homepage-star-minimum',
                    options=[{'label': f'{_:.1f}', 'value': f'{_:.1f}'} for _ in np.arange(0, 5.1, 0.5)[::-1]],
                    value='0.0',
                    multi=False,
                    clearable=False,
                )
            ]),
            html.Hr(),
            dbc.InputGroup([
                dbc.InputGroupAddon(
                    dbc.Select(
                        id='homepage-distance-from',
                        options=[{'label': f'Within {_:.0f}km', 'value': _} for _ in [1, 2, 5, 10]],
                        value=10
                    ), addon_type='prepend'),
                dbc.Input(
                    id='homepage-address-lookup',
                    placeholder='e.g. CN Tower'
                ),
            ]),
            html.Br(),
            dbc.Button('Search', id='homepage-address-lookup-btn', color='danger'),
            html.Hr(),
            html.H3(id='homepage-restaurant-num'),
            html.P('Locations found')
        ], width=4),
        dbc.Col([
            dcc.Loading([
                dcc.Graph(id='homepage-map', config=config)
            ])
        ], width=8)
    ]),
    html.Br(),
    html.Hr(),
    html.H2('Top Suggestions'),
    html.Br(),
    dbc.Row([dbc.Col(dbc.CardDeck(id=f'homepage-deck-0'), width=12)]), html.Br(),
    dbc.Row([dbc.Col(dbc.CardDeck(id=f'homepage-deck-1'), width=12)]), html.Br(),
    dbc.Row([dbc.Col(dbc.CardDeck(id=f'homepage-deck-2'), width=12)]), html.Br(),
    dbc.Row([dbc.Col(dbc.CardDeck(id=f'homepage-deck-3'), width=12)]), html.Br(),
    dbc.Row([dbc.Col(dbc.CardDeck(id=f'homepage-deck-4'), width=12)]), html.Br(),
    html.Br(),
    html.Br(),
])


@app.callback(
    [
        Output('homepage-map', 'figure'),
        Output('homepage-restaurant-num', 'children'),
        Output('homepage-deck-0', 'children'),
        Output('homepage-deck-1', 'children'),
        Output('homepage-deck-2', 'children'),
        Output('homepage-deck-3', 'children'),
        Output('homepage-deck-4', 'children'),
    ],
    [
        Input('homepage-address-lookup-btn', 'n_clicks')
    ],
    [
        State('homepage-city-selector', 'value'),
        State('homepage-cat-search', 'value'),
        State('homepage-rest-search', 'value'),
        State('homepage-star-minimum', 'value'),
        State('homepage-address-lookup', 'value'),
        State('homepage-distance-from', 'value')
    ],
)
def filter_map_by_dropdown(_, cities, search, restaurant, stars, address, distance_km):
    df = base_data.data.copy()

    if cities:
        df = df[df.city.isin(cities)]

    if search:
        for s in search.split(','):
            s = s.lower().strip()
            df = df[df.categories.str.lower().str.contains(s)]

    if restaurant:
        df = df[df['name'].str.lower().str.contains(restaurant.lower())]

    if stars:
        df = df[df['stars'] >= float(stars)]

    if address:
        lat, long = base_data.get_coord_from_address(address)

        def get_distance(row):
            return distance((row.latitude, row.longitude), (lat, long)).kilometers

        df['custom_distance'] = df.apply(get_distance, axis=1)
        df = df[df.custom_distance <= float(distance_km)]

    cards = [card_creator(row) for ix, row in df.nlargest(20, 'rank_value').iterrows()]

    out_list = [create_location_map(df), f'{df.shape[0]:,.0f}']
    out_list.extend([cards[i * 4:(i + 1) * 4] for i in range((len(cards) + 3) // 4)])

    return out_list
