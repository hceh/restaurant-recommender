import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

from restaurant_recommender.data_collector import BusinessDataSet

base_data = BusinessDataSet(category='restaurant', state='ON')


def create_location_map(df):
    fig = go.Figure(go.Scattermapbox(
        lat=df.latitude,
        lon=df.longitude,
        mode='markers',
        text=df.name + '<br>' + df.address + '<br>' + df.postal_code + '<br>Stars: ' + df.stars.astype(str),
    ))

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            zoom=8.5,
            center=go.layout.mapbox.Center(
                lat=df.latitude.mean(),
                lon=df.longitude.mean()
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
    dbc.Row([
        dbc.Col([
            html.H2('Homepage'),
        ], width=8),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Markdown('Filters, top ranked restaurants going here')
        ], width=4),
        dbc.Col([
            dcc.Graph(id='homepage-map', figure=create_location_map(base_data.data))  # todo: add custom config
        ], width=8)
    ])
])
