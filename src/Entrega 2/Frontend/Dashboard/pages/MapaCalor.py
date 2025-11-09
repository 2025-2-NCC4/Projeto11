import dash
from dash import html, dcc, Output, Input
import plotly.express as px
from flask import request

from functions.CallbackMetricas import dfMassaTeste, get_df_for_period

# Registrar a página no Dash
dash.register_page(__name__, path='/mapacalor')

# Criar o mapa de calor
def create_heatmap(df):
    fig = px.density_mapbox(df,
                            lat='latitude',
                            lon='longitude',
                            z='valor_compra',
                            radius=10,
                            center={'lat': -23.570847, 'lon': -46.645782},  # Centro de São Paulo
                            zoom=14,
                            mapbox_style="open-street-map")
    return fig

# Layout da página
layout = html.Div([
    html.H1('Mapa de Calor - São Paulo', style={
        'textAlign': 'center',
        'marginTop': '0px',
        'color': '#4A4A4A'
    }),
    html.Div([
        html.Button("Massa de teste", className="login-btn", id='btnMassaTeste', style={'background-color': '#969696', 'width':'200px', 'margin-right':'20px'}),
        # html.Button("Base Pedestre", className="login-btn", id='btnBasePedestre', style={'width':'200px'}),
    ], style={"display": "flex", "align-items": "center", "justify-content": "center", "margin-bottom": "30px"}),


html.Div([
            dcc.Dropdown(
                id="mes-seletor",
                options=[
                    {"label": "Janeiro", "value": 1},
                    {"label": "Fevereiro", "value": 2},
                    {"label": "Março", "value": 3},
                    {"label": "Abril", "value": 4},
                    {"label": "Maio", "value": 5},
                    {"label": "Junho", "value": 6},
                    {"label": "Julho", "value": 7},
                    {"label": "Agosto", "value": 8},
                    {"label": "Setembro", "value": 9},
                    {"label": "Outubro", "value": 10},
                    {"label": "Novembro", "value": 11},
                    {"label": "Dezembro", "value": 12},
                ],
                value=7,
                clearable=False,
                style={"width": "200px", "margin-right": "20px", "height": '40px'}
            ),
            dcc.Input(
                id="ano-seletor",
                type="number",
                value=2025,
                min=2020, max=2100,
                step=1,
                style={"width": "120px", "height": '35px'}
            ),
        ], style={"display": "flex", "align-items": "center", "justify-content": "center", "margin-bottom": "30px"}),
    html.Div([
                dcc.Dropdown(
                id="categoria-seletor",
                options=[
                    {"label": "Vestuário", "value": "vestuário"},
                    {"label": "Eletrodoméstico", "value": "eletrodoméstico"},
                    {"label": "Mercado Express", "value": "mercado express"},
                    {"label": "Móveis", "value": "móveis"},
                    {"label": "Restaurante", "value": "restaurante"},
                    {"label": "Farmácia", "value": "farmácia"},
                    {"label": "Outros", "value": "outros"},
                    {"label": "Categorias", "value": "tudo"}
                ],
                value="tudo",
                clearable=False,
                style={"width": "200px", "margin-right": "20px", "height": '40px'}
            ),
                dcc.Dropdown(
                id="cupom-seletor",
                options=[
                    {"label": "Produto", "value": "Produto"},
                    {"label": "Desconto", "value": "Desconto"},
                    {"label": "Cashback", "value": "Cashback"},
                    {"label": "Cupom", "value": "tudo"},
                ],
                value="tudo",
                clearable=False,
                style={"width": "200px", "margin-right": "20px", "height": '40px'}
            ),
            dcc.Dropdown(
                id="loja-seletor",
                options=[
                {"label": "Loja", "value": "tudo"}
                ],
                value="tudo",
                clearable=False,
                style={"width": "200px", "margin-right": "20px", "height": '40px'}
            ),
    ],style={"display": "flex", "align-items": "center", "justify-content": "center", "margin-bottom": "30px"}),
            html.Div(id="mapa-container", className="content", style={
            'height': '100vh',
            'width': '100%'
        }),
    dcc.Location(id="redirectMapa", refresh=True),
    dcc.Location(id="mudarMapa", refresh=True)
], style={
    'fontFamily': 'Arial, sans-serif',
    'backgroundColor': '#f4f4f4',
    'padding': '20px',
    'display': 'flex',
    'flexDirection': 'column',
    'alignItems': 'center',
    'min-width':'175vh'
})

# @dash.callback(
#     Output("mudarMapa", "href"),
#     Input("btnBasePedestre", "n_clicks")
# )
# def mudarMapa(n_clicks):
#     if n_clicks > 0:
#         return "/mapacalorpedestres"

@dash.callback(
    Output("redirectMapa", "href"),
    Input("redirectMapa", "href")
)
def redirecionar(link):
    nome = request.cookies.get("user_nome")
    if not nome:
        return "/"
    return dash.no_update

@dash.callback(
    Output("mapa-container", "children"),
    Output("loja-seletor", "options"),
    Input("mes-seletor", "value"),
    Input("ano-seletor", "value"),
    Input("categoria-seletor", "value"),
    Input("cupom-seletor", "value"),
    Input("loja-seletor", "value")
)
def atualizarMapa(mes, ano, categoria, cupom, loja):
    df_Massa_Teste = get_df_for_period(dfMassaTeste, ano, mes)
    lojas = []

    if categoria == "tudo":
        lojas = [
            {"label": "Havaianas", "value": "Havaianas"},
            {"label": "Riachuelo", "value": "Riachuelo"},
            {"label": "Renner", "value": "Renner"},
            {"label": "Lojas Americanas", "value": "Lojas Americanas"},
            {"label": "Livraria Cultura", "value": "Livraria Cultura"},
            {"label": "Smart Fit", "value": "Smart Fit"},
            {"label": "Pão de Açúcar", "value": "Pão de Açúcar"},
            {"label": "Extra Mercado", "value": "Extra Mercado"},
            {"label": "Drogaria São Paulo", "value": "Drogaria São Paulo"},
            {"label": "Ponto Frio", "value": "Ponto Frio"},
            {"label": "Kalunga", "value": "Kalunga"},
            {"label": "Daiso Japan", "value": "Daiso Japan"},
            {"label": "Fast Shop", "value": "Fast Shop"},
            {"label": "Outback", "value": "Outback"},
            {"label": "Subway", "value": "Subway"},
            {"label": "Loja", "value": "tudo"}
        ]
    elif categoria == "vestuário":
        lojas = [
            {"label": "Havaianas", "value": "Havaianas"},
            {"label": "Riachuelo", "value": "Riachuelo"},
            {"label": "Renner", "value": "Renner"},
            {"label": "Lojas Americanas", "value": "Lojas Americanas"},
            {"label": "Loja", "value": "tudo"}
        ]
    elif categoria == "eletrodoméstico":
        lojas = [
            {"label": "Ponto Frio", "value": "Ponto Frio"},
            {"label": "Kalunga", "value": "Kalunga"},
            {"label": "Loja", "value": "tudo"}
        ]
    elif categoria == "mercado express":
        lojas = [
            {"label": "Pão de Açúcar", "value": "Pão de Açúcar"},
            {"label": "Extra Mercado", "value": "Extra Mercado"},
            {"label": "Loja", "value": "tudo"}
        ]
    elif categoria == "móveis":
        lojas = [
            {"label": "Daiso Japan", "value": "Daiso Japan"},
            {"label": "Fast Shop", "value": "Fast Shop"},
            {"label": "Loja", "value": "tudo"}
        ]
    elif categoria == "restaurante":
        lojas = [
            {"label": "Outback", "value": "Outback"},
            {"label": "Subway", "value": "Subway"},
            {"label": "Loja", "value": "tudo"}
        ]
    elif categoria == "farmácia":
        lojas = [
            {"label": "Drogaria São Paulo", "value": "Drogaria São Paulo"},
            {"label": "Loja", "value": "tudo"}
        ]
    elif categoria == "outros":
        lojas = [
            {"label": "Livraria Cultura", "value": "Livraria Cultura"},
            {"label": "Smart Fit", "value": "Smart Fit"},
            {"label": "Loja", "value": "tudo"}
        ]

    if df_Massa_Teste is None:
        return "Nenhum dado durante esse periodo", lojas

    dfFinal = ""
    if categoria != "tudo" and cupom == "tudo" and loja == "tudo":
        print("Categoria")
        dfFinal = df_Massa_Teste[df_Massa_Teste['tipo_loja'] == categoria]
    elif categoria == "tudo" and cupom != "tudo" and loja == "tudo":
        print("cupom")
        dfFinal = df_Massa_Teste[df_Massa_Teste['tipo_cupom'] == cupom]
    elif categoria == "tudo" and cupom == "tudo" and loja != "tudo":
        print("loja")
        df_por_loja = df_Massa_Teste[df_Massa_Teste['nome_loja'] == loja]
    elif categoria == "tudo" and cupom == "tudo" and loja == "tudo":
        dfFinal = df_Massa_Teste
    else:
        if categoria != "tudo" and cupom != "tudo" and loja == "tudo":
            df_por_cupom = df_Massa_Teste[df_Massa_Teste['tipo_cupom'] == cupom]
            df_por_categoria = df_por_cupom[df_por_cupom['tipo_loja'] == categoria]
            dfFinal = df_por_categoria
        elif categoria != "tudo" and cupom == "tudo" and loja != "tudo":
            df_por_categoria = df_Massa_Teste[df_Massa_Teste['tipo_loja'] == categoria]
            df_por_loja = df_por_categoria[df_por_categoria['nome_loja'] == loja]
            dfFinal = df_por_loja
        elif categoria == "tudo" and cupom != "tudo" and loja != "tudo":
            df_por_cupom = df_Massa_Teste[df_Massa_Teste['tipo_cupom'] == cupom]
            df_por_loja = df_por_cupom[df_por_cupom['nome_loja'] == loja]
            dfFinal = df_por_loja
        else:
            print("tudo")
            df_por_cupom = df_Massa_Teste[df_Massa_Teste['tipo_cupom'] == cupom]
            df_por_categoria = df_por_cupom[df_por_cupom['tipo_loja'] == categoria]
            df_por_loja = df_por_categoria[df_por_categoria['nome_loja'] == loja]
            dfFinal = df_por_loja


    return dcc.Graph(
        id='mapa-calor',
        figure=create_heatmap(dfFinal)
    ), lojas