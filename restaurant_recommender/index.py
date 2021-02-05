import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from restaurant_recommender.app import app
from restaurant_recommender.pages import homepage, sidebar, settings

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar.layout,
    html.Br(),
    html.Div(id='page-content'),
], style={'position': 'relative'})

d_pages = {
    '/': homepage.layout,
    '/settings': settings.layout,
}


# moving between pages 
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    return d_pages.get(pathname, homepage.layout)


if __name__ == '__main__':
    app.run_server(port=8000)
