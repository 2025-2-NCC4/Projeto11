import dash
import pandas as pd
import requests
from dash import Dash, html, dcc, Output, Input, State

backendURL = "http://localhost:5000"

backendURL_cadastro = backendURL + "/cadastro"

dfCupons = pd.read_csv("https://raw.githubusercontent.com/2025-2-NCC4/Projeto11/refs/heads/main/documentos/Entrega%201/Projeto%20Interdisciplinar%20-%20Ci%C3%AAncia%20de%20dados/Base%20de%20Dados/PicMoney-Base_de_Transa__es_-_Cupons_Capturados-100000%20linhas%20(1).csv", sep=";")
dfBaseCadastral = pd.read_csv("https://raw.githubusercontent.com/2025-2-NCC4/Projeto11/refs/heads/main/documentos/Entrega%201/Projeto%20Interdisciplinar%20-%20Ci%C3%AAncia%20de%20dados/Base%20de%20Dados/PicMoney-Base_Cadastral_de_Players-10_000%20linhas%20(1).csv", sep=";")
dfBasePedestres = pd.read_csv("https://raw.githubusercontent.com/2025-2-NCC4/Projeto11/refs/heads/main/documentos/Entrega%201/Projeto%20Interdisciplinar%20-%20Ci%C3%AAncia%20de%20dados/Base%20de%20Dados/PicMoney-Base_Simulada_-_Pedestres_Av__Paulista-100000%20linhas%20(1).csv", sep=";")
dfMassaTeste = pd.read_csv("https://raw.githubusercontent.com/2025-2-NCC4/Projeto11/refs/heads/main/documentos/Entrega%201/Projeto%20Interdisciplinar%20-%20Ci%C3%AAncia%20de%20dados/Base%20de%20Dados/PicMoney-Massa_de_Teste_com_Lojas_e_Valores-10000%20linhas%20(1).csv", sep=";")

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

#Placement temporario para callbacks
#Callback Cadastro
@app.callback(
    Output("signup-status", "children", allow_duplicate=True),
    Input("signup-button", "n_clicks"),
    State("nome", "value"),
    State("email", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def unified_handler(n_clicks, nome, email, password):
    trigger = dash.ctx.triggered_id
    if trigger == "signup-button":
        payload = {"nome": nome, "email": email, "senha": password}
        try:
            resp = requests.post(backendURL_cadastro, json=payload)
        except Exception as e:
            return f"Erro de conexão: {e}"

        if resp.status_code == 201:
            return "Cadastro realizado com sucesso!"
        elif resp.status_code == 400:
            return f"Dados inválidos: {resp.text}"
        else:
            return f"Erro {resp.status_code}: {resp.text}"

    return dash.no_update

app.layout = html.Div([

    html.Div([
        html.Img(src='assets/piclogo.png', className="PicLogo"),
        html.H1('Dashboard Interativa PicMoney', style={'text-size':'10px'}),
        html.Div([
            dcc.Link("Home", href="/Home", className="button-link"),
            dcc.Link("Mapa Calor", href="/mapacalor", className="button-link"),

        ])
    ], className="MainHeader"),
    dash.page_container
], className="DashboardPag", style={'overflow': 'hidden', 'height': '100vh'})

if __name__ == '__main__':
    app.run(debug=True)
