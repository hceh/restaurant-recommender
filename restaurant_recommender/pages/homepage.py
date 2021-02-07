import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

from restaurant_recommender.data_collector import BusinessDataSet

base_data = BusinessDataSet(category='restaurant', state='ON')


def create_location_map(df):
    fig = px.scatter_mapbox(
        df,
        lat='latitude',
        lon='longitude',
        hover_name='name',
        hover_data=['address', 'postal_code', 'stars'],
        zoom=8.5,
        height=600,
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
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
