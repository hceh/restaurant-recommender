import dash
import dash_bootstrap_components as dbc

url_fa = 'https://use.fontawesome.com/releases/v5.8.1/css/all.css'

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, url_fa])
app.title = 'Restaurant Finder'
server = app.server
app.config.suppress_callback_exceptions = True
