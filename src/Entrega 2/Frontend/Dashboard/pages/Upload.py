import dash
from dash import html

dash.register_page(__name__, path='/Upload')

layout = html.Div([
    html.H1('CEO')
])