import dash
import dash_trich_components as dtc
from dash.dependencies import Input, Output, State

from config import app

layout = dtc.SideBar([
    dtc.SideBarItem(id='btn_homepage', label="Homepage", icon="fas fa-home"),
    dtc.SideBarItem(id='btn_detail', label="Detail", icon="fas fa-list-alt"),
    dtc.SideBarItem(id='btn_info', label="Info", icon="fas fa-info-circle"),
], bg_color='#9c1919', text_color='#ffffff')


@app.callback(
    Output('url', 'pathname'),
    [Input('btn_homepage', 'n_clicks_timestamp'),
     Input('btn_detail', 'n_clicks_timestamp'),
     Input('btn_info', 'n_clicks_timestamp')],
    [State('url', 'pathname')]
)
def toggle_collapse(input1, input2, input3, url_curr):  # todo: can I replace with *args or something?
    d_buttons = {
        'btn_homepage': '/#',
        'btn_detail': '/deep-dive',
        'btn_info': '/info',
    }

    ctx = dash.callback_context

    if not ctx.triggered:
        return url_curr
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return d_buttons.get(button_id, '/#')
