import re
import sqlite3
from ast import literal_eval
from urllib.parse import parse_qs

import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output

from config import app
from src.data_collector import BusinessDataSet, project_root

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


def create_citymapper_link(row):
    return f'https://citymapper.com/directions?endcoord={row.latitude}%2C{row.longitude}&' \
           f"endname={row['name'].replace(' ', '%20')}&" \
           f"endaddress={row.address.replace(' ', '%20').replace(',', '%2C')}%2C%20{row.city}%2C%20{row.postal_code}"


def create_hours_table(hours: dict):
    header_values = ['Day:', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    table_header = [html.Thead(html.Tr([html.Th(_) for _ in header_values]))]

    row = [html.Td('Hours:')]
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        if day in hours:
            row.append(html.Td(hours[day].replace(':0', ':00')))
        else:
            row.append(html.Td('Closed'))
    row = html.Tr(row)

    table = dbc.Table(
        table_header + [html.Tbody(row)],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
    )
    return table


def create_location_map(df):
    hover_template = '<b>{}</b><br>{}<br>{}<br>{}<br>Rating: {:.1f}<extra></extra>'

    df['hover'] = hover_template.format(df['name'], df.address, df.city, df.postal_code, df.stars)

    fig = go.Figure(go.Scattermapbox(
        lat=[df.latitude],
        lon=[df.longitude],
        mode='markers',
        hovertemplate=[df.hover],
        marker=go.scattermapbox.Marker(size=14, color='#9c1919', opacity=0.7),
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

    df = pd.read_sql(query, conn, parse_dates={'DATE': '%Y-%m-%d %H:%M:%S'})
    return df


def get_location_attributes(loc: pd.Series):
    pattern = re.compile(r'(?<=[a-z])(?=[A-Z])')

    def convert_attr_to_text(text: str):
        s = pattern.sub(' ', text)
        s = "".join(filter(lambda x: not x.isdigit(), s))
        return s

    def convert_true_to_tick(s):
        try:  # if 'True' or '1' or dict etc
            s = literal_eval(s)
        except ValueError:  # if just a regular string
            pass

        if s is True:
            return '\u2705'  # True to tick
        elif isinstance(s, int):
            return '$' * s  # convert price value to number of $'s
        else:
            try:
                return s.title().replace('_', ' ')
            except AttributeError:  # for False
                return s

    d_dicts = [_ for _ in loc.attributes.keys() if '{' in loc.attributes[_]]
    d_strs = [
        _ for _ in loc.attributes.keys() if
        ('{' not in loc.attributes[_] and loc.attributes[_].lower() not in ['False', u'none'])
    ]

    d_dicts = {convert_attr_to_text(_): literal_eval(loc.attributes[_]) for _ in d_dicts}
    d_strs = {convert_attr_to_text(_): convert_true_to_tick(loc.attributes[_]) for _ in d_strs}

    d_strs = {_: d_strs[_] for _ in d_strs if d_strs[_] not in [False, 'None', '']}

    return d_dicts, d_strs


def create_attributes_detail(s: dict, d: dict):
    body = list()
    for att in s:
        body.append(html.P(f'{att} - {s[att]}'))
    f_s = list()
    for item in d:
        f = d[item]
        trues = [_.title() for _ in f if f[_]]
        f_s.append({item: trues})
        body.append(html.P(f'{item.title()} - {", ".join(trues)}'))
    return body[:10]


layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H2(id='deep-dive-header')
        ])
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='deep-dive-map', config=config)
        ], width=6),
        dbc.Col([
            html.H4('About'),
            dbc.Row([
                dbc.Col(id='deep-dive-attributes-table', width=6),
                dbc.Col(id='deep-dive-attributes-table-2', width=6),
            ])
        ], width=6),
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Button(
                    'Open in Citymapper',
                    id='citymapper-link',
                    color='success',
                    className='mr-1',
                    block=True,
                ),
                dbc.Button(
                    'Return to Home',
                    id='deep-dive-home-link',
                    color='primary',
                    className='mr-1',
                    block=True,
                    href='/',
                ),
            ])
        ], width=3),
        dbc.Col(id='deep-dive-hours', width=9),
    ]),
    html.Br(),
    html.Br(),
    # dbc.Row([])
])


@app.callback(
    [
        Output('deep-dive-header', 'children'),
        Output('citymapper-link', 'href'),
        Output('deep-dive-map', 'figure'),
        Output('deep-dive-hours', 'children'),
        Output('deep-dive-attributes-table', 'children'),
        Output('deep-dive-attributes-table-2', 'children'),
    ],
    [
        Input('url', 'search')
    ]
)
def update(url):
    if '?' not in url:
        selected = base_data.data.nlargest(1, 'rank_value').iloc[0]
    else:
        params = parse_qs(url)
        selected = base_data.data.loc[params.get('?id')].iloc[0]

    # todo:
    #  top reviews
    #  description
    #  similar restaurants

    dicts, strs = get_location_attributes(selected)

    attributes = create_attributes_detail(strs, dicts)
    a1 = attributes[:10]
    a2 = attributes[10:]

    return selected['name'], create_citymapper_link(selected), create_location_map(selected), \
           create_hours_table(selected.hours), a1, a2
