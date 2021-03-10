import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from config import app
from src.pages import homepage, sidebar, info, deep_dive

app.layout = html.Div([
    sidebar.layout,
    html.Br(),
    html.Div(id='page_content'),
    dcc.Location(id='url', refresh=False),
], style={'position': 'relative'})

d_pages = {
    '/': homepage.layout,
    '/deep-dive': deep_dive.layout,
    '/info': info.layout,
}


# moving between pages 
@app.callback(Output('page_content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    return d_pages.get(pathname, homepage.layout)


if __name__ == '__main__':
    app.run_server(port=8000)
