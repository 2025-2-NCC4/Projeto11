import dash
from dash import html
import pandas as pd

dash.register_page(__name__, path='/')

df = pd.read_csv("https://raw.githubusercontent.com/2025-2-NCC4/Projeto11/refs/heads/main/documentos/Entrega%201/Projeto%20Interdisciplinar%20-%20Ci%C3%AAncia%20de%20dados/PicMoney-Base_Cadastral_de_Players-10_000%20linhas%20(1).csv",sep=";")

layout = html.Div([
    html.H1('Página principal'),
    dash.dash_table.DataTable(data=df.to_dict('records'), page_size=10)
])