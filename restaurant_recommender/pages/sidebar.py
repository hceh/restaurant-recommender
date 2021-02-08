import dash
import dash_trich_components as dtc
from dash.dependencies import Input, Output, State

from app import app

layout = dtc.SideBar([
    dtc.SideBarItem(id='btn_homepage', label="Homepage", icon="fas fa-home"),
    dtc.SideBarItem(id='btn_2', label="Single", icon="fas fa-chart-line"),
    dtc.SideBarItem(id='btn_3', label="Page 3", icon="far fa-list-alt"),
    dtc.SideBarItem(id='btn_4', label="Page 4", icon="fas fa-info-circle"),
    dtc.SideBarItem(id='btn_settings', label="Settings", icon="fas fa-cog"),
])


@app.callback(
    Output('url', 'pathname'),
    [Input('btn_homepage', 'n_clicks_timestamp'),
     Input('btn_2', 'n_clicks_timestamp'),
     Input('btn_3', 'n_clicks_timestamp'),
     Input('btn_4', 'n_clicks_timestamp'),
     Input('btn_settings', 'n_clicks_timestamp')],
    [State('url', 'pathname')]
)
def toggle_collapse(input1, input2, input3, input4, input5, url_curr): # todo: can I replace with *args or something?
    d_buttons = {
        'btn_homepage': '/#',
        'btn_2': '/deep-dive',
        'btn_3': '/#',
        'btn_4': '/#',
        'btn_settings': '/settings',
    }

    ctx = dash.callback_context

    if not ctx.triggered:
        return url_curr
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return d_buttons.get(button_id, '/#')
