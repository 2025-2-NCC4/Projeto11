import dash
from dash import html

dash.register_page(__name__, path='/CEO')

layout = html.Div([
    html.H1('CEO')
])