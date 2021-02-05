import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

from restaurant_recommender.functions import BusinessDataSet

base_data = BusinessDataSet(category='restaurant', state='ON')


def get_categories(base):
    categories = [_.split(', ') for _ in set(base.data.categories) if _ is not None]
    categories = [item for sublist in categories for item in sublist]

    # import pandas as pd
    # from collections import Counter
    # df_cat_counts = (pd.DataFrame
    #                  .from_dict(dict(Counter(categories)), orient='index', columns=['count'])
    #                  .sort_values('count', ascending=False))

    return [{'value': _, 'id': _} for _ in categories]


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
        # title=f'Restaurants found in {state}',
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
        # dbc.Col([
        #     dcc.Dropdown(
        #         id='homepage-category-picker',
        #         options=[{'label': _, 'value': _} for _ in get_categories(base_data)],
        #         value='AZ'
        #     )
        # ], width=4)
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


