import sqlite3
from urllib.parse import parse_qs

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output

from app import app
from restaurant_recommender.data_collector import BusinessDataSet, project_root

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


def create_hours_table(hours: dict):
    table_header = [
        html.Thead(html.Tr([html.Th("Day"), html.Th("Hours")]))
    ]

    table_body = list()
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        if day in hours:
            table_body.append(html.Tr([html.Td(day), html.Td(hours[day].replace(':0', ':00'))]))
        else:
            table_body.append(html.Tr([html.Td(day), html.Td('Closed')]))

    table = dbc.Table(table_header + [html.Tbody(table_body)], bordered=True)
    return table


def create_location_map(df):
    hover_template = '<b>{}</b><br>{}<br>{}<br>{}<br>Rating: {:.1f}<extra></extra>'

    df['hover'] = hover_template.format(df['name'], df.address, df.city, df.postal_code, df.stars)

    fig = go.Figure(go.Scattermapbox(
        lat=[df.latitude],
        lon=[df.longitude],
        mode='markers',
        hovertemplate=[df.hover],
        marker=go.scattermapbox.Marker(size=14, color='rgb(255, 0, 0)', opacity=0.7),
    ))

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            zoom=15,
            center=go.layout.mapbox.Center(
                lat=df.latitude,
                lon=df.longitude,
            ),
        ),
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=400,
    )

    return fig


def get_review_data(business_id: str) -> pd.DataFrame:
    query = f"SELECT * FROM REVIEWS WHERE REVIEWS.BUSINESS_ID = '{business_id}' LIMIT 200"
    conn = None
    try:
        conn = sqlite3.connect(project_root / 'data/reviews.sqlite')
        print("Connection to SQLite DB successful")
    except sqlite3.Error as e:
        print(f"The error '{e}' occurred")

    df = pd.read_sql(query, conn, parse_dates={'DATE':'%Y-%m-%d %H:%M:%S'})
    return df


layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2(id='deep-dive-header')
        ])
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='deep-dive-map')
        ], width=6),
        dbc.Col(id='deep-dive-hours', width={'offset': 3, 'size': 3}),
    ]),
    html.Br(),
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
    ]),
    html.Br(),
])


@app.callback(
    [
        Output('deep-dive-header', 'children'),
        Output('citymapper-link', 'href'),
        Output('deep-dive-map', 'figure'),
        Output('deep-dive-hours', 'children')
    ],
    [
        Input('url', 'search')
    ]
)
def update_header(url):
    if '?' not in url:
        selected = base_data.data.nlargest(1, 'rank_value').iloc[0]
    else:
        params = parse_qs(url)
        selected = base_data.data.loc[params.get('?id')].iloc[0]

    # todo:
    #  opening hours
    #  top reviews
    #  description
    #  similar restaurants
    #  return to home button

    return selected['name'], create_citymapper_link(selected), create_location_map(selected), \
           create_hours_table(selected.hours)
