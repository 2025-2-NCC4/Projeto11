import dash
import pandas as pd
from dash import Dash, html, dcc, Output
from functions import Callbacks, CallbackMetricas

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

Callbacks.registrarcallbacks(app)
#CallbackMetricas.registrarCallbackMetricas(app)

app.layout = html.Div([

    html.Div([
        html.Img(src='assets/piclogo.png', className="PicLogo"),
        html.H1('Dashboard Interativa PicMoney', style={'text-size':'10px'}),
        html.Div([
            dcc.Link("Home", href="/Home", className="button-link"),
            dcc.Link("Mapa Calor", href="/mapacalor", className="button-link"),
            dcc.Link("Upload", href="/Upload", className="button-link"),
            dcc.Link("Perfil", href="/Perfil", className="button-link"),
            dcc.Link("", href="/", className="button-link", id="btnCargoHeader"),
            dcc.Location(id="url"),
        ])
    ], className="MainHeader"),
    dash.page_container
], className="DashboardPag")



server = app.server

if __name__ == '__main__':
    app.run(debug=True)
