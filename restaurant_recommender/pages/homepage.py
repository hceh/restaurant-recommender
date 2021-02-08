import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Output, Input

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
    hover_template = '<b>{}</b><br>{}<br>{}<br>{}<br>Stars: {:.1f}<extra></extra>'

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


layout = dbc.Container([
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H2('Homepage'),
        ], width=8),
    ]),
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
        ], width=4),
        dbc.Col([
            dcc.Loading([
                dcc.Graph(id='homepage-map', config=config)
            ])
        ], width=8)
    ])
])


@app.callback(
    Output('homepage-map', 'figure'),
    [Input('homepage-city-selector', 'value')]
)
def filter_map_by_dropdown(cities):
    df = base_data.data.copy()
    if cities:
        df = df[df.city.isin(cities)]
    return create_location_map(df)
