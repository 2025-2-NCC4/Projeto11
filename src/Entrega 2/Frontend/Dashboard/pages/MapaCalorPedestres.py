import dash
from dash import html, dcc, Output, Input
import plotly.express as px
from flask import request

from functions.CallbackMetricas import dfBasePedestre, get_df_for_period

# Registrar a página no Dash
dash.register_page(__name__, path='/mapacalorpedestres')

# Criar o mapa de calor
def create_heatmap(df):
    fig = px.density_mapbox(df,
                            lat='latitude',
                            lon='longitude',
                            z='ultimo_valor_capturado',
                            radius=10,
                            center={'lat': -23.55052, 'lon': -46.633308},  # Centro de São Paulo
                            zoom=12,
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
        html.Button("Massa de teste", className="login-btn", id='btnMassaTeste', style={ 'width':'200px', 'margin-right':'20px'}),
        html.Button("Base Pedestre", className="login-btn", id='btnBasePedestre', style={'background-color': '#969696','width':'200px'}),
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
                id="celular-seletor",
                options=[
                    {"label": "iPhone", "value": "iPhone"},
                    {"label": "Android", "value": "Android"},
                    {"label": "Celular", "value": "tudo"}
                ],
                value="Android",
                clearable=False,
                style={"width": "200px", "margin-right": "20px", "height": '40px'}
            ),
                dcc.Dropdown(
                id="modelo-seletor",
                options=[
                    {"label": "Modelo", "value": "tudo"}
                ],
                value="Realme C35",
                clearable=False,
                style={"width": "200px", "margin-right": "20px", "height": '40px'}
            ),
            dcc.Dropdown(
                id="tipo-seletor",
                options=[
                {"label": "Cashback", "value": "Cashback"},
                {"label": "Desconto", "value": "Desconto"},
                {"label": "Produto", "value": "Produto"},
                {"label": "Cupom", "value": "tudo"}
                ],
                value="Cashback",
                clearable=False,
                style={"width": "200px", "margin-right": "20px", "height": '40px'}
            ),
            dcc.Dropdown(
                id="lojaPedestre-seletor",
                options=[
                {"label": "Restaurantes", "value": "Restaurantes e Gastronomia"},
                {"label": "Supermercados", "value": "Supermercados e Mercados Express"},
                {"label": "Farmácias", "value": "Farmácias e Drogarias"},
                {"label": "Clubes", "value": "Clubes e Centros de Convivência"},
                {"label": "Lojas de Móveis", "value": "Lojas de Móveis e Decoração"},
                {"label": "Lojas de Roupas", "value": "Lojas de Roupas e Calçados"},
                {"label": "Eletrodomésticos", "value": "Lojas de Eletrodomésticos e Utilidades Domésticas"},
                {"label": "Loja", "value": "tudo"}
                ],
                value="Restaurantes e Gastronomia",
                clearable=False,
                style={"width": "200px", "margin-right": "20px", "height": '40px'}
            ),
                dcc.Dropdown(
                id="sexo-seletor",
                options=[
                {"label": "Masculino", "value": "Masculino"},
                {"label": "Feminino", "value": "Feminino"},
                {"label": "Outro", "value": "Outro"},
                {"label": "Sexo", "value": "tudo"}
                ],
                value="Masculino",
                clearable=False,
                style={"width": "200px", "margin-right": "20px", "height": '40px'}
            ),
    ],style={"display": "flex", "align-items": "center", "justify-content": "center", "margin-bottom": "30px"}),
            html.Div(id="mapa-container-Pedestre", className="content", style={
            'height': '100vh',
            'width': '100%'
        }),
    dcc.Location(id="redirectMapaPedestre", refresh=True),
    dcc.Location(id="mudarMapaPedestre", refresh=True)
], style={
    'fontFamily': 'Arial, sans-serif',
    'backgroundColor': '#f4f4f4',
    'padding': '20px',
    'height': '100vh',
    'display': 'flex',
    'flexDirection': 'column',
    'alignItems': 'center',
    'width':'200vh'
})

@dash.callback(
    Output("mudarMapaPedestre", "href"),
    Input("btnMassaTeste", "n_clicks")
)
def mudarMapa(n_clicks):
    if n_clicks > 0:
        return "/mapacalor"

@dash.callback(
    Output("redirectMapaPedestre", "href"),
    Input("redirectMapaPedestre", "href")
)
def redirecionar(link):
    nome = request.cookies.get("user_nome")
    if not nome:
        return "/"
    return dash.no_update

@dash.callback(
    Output("mapa-container-Pedestre", "children"),
    Output("modelo-seletor", "options"),
    Input("mes-seletor", "value"),
    Input("ano-seletor", "value"),
    Input("celular-seletor", "value"),
    Input("modelo-seletor", "value"),
    Input("tipo-seletor", "value"),
    Input("lojaPedestre-seletor", "value"),
    Input("sexo-seletor", "values")
)
def atualizarMapa(mes, ano, celular, modelo, tipo, loja, sexo):
    df_Base_Pedestre = get_df_for_period(dfBasePedestre, ano, mes)
    modeloCelulares = []

    if celular == "tudo":
        modeloCelulares = [
            {"label": "Realme C35", "value": "Realme C35"},
            {"label": "Motorola G60", "value": "Motorola G60"},
            {"label": "Xiaomi Redmi Note 11", "value": "Xiaomi Redmi Note 11"},
            {"label": "Samsung S21", "value": "Samsung S21"},
            {"label": "Samsung Galaxy A52", "value": "Samsung Galaxy A52"},
            {"label": "iPhone 11", "value": "iPhone 11"},
            {"label": "iPhone 12", "value": "iPhone 12"},
            {"label": "iPhone 14 Pro", "value": "iPhone 14 Pro"},
            {"label": "iPhone 13", "value": "iPhone 13"},
            {"label": "iPhone SE", "value": "iPhone SE"},
        ]
    elif celular == "Android":
        modeloCelulares = [
            {"label": "Realme C35", "value": "Realme C35"},
            {"label": "Motorola G60", "value": "Motorola G60"},
            {"label": "Xiaomi Redmi Note 11", "value": "Xiaomi Redmi Note 11"},
            {"label": "Samsung S21", "value": "Samsung S21"},
            {"label": "Samsung Galaxy A52", "value": "Samsung Galaxy A52"},
        ]
    elif celular == "iPhone":
        modeloCelulares = [
            {"label": "iPhone 11", "value": "iPhone 11"},
            {"label": "iPhone 12", "value": "iPhone 12"},
            {"label": "iPhone 14 Pro", "value": "iPhone 14 Pro"},
            {"label": "iPhone 13", "value": "iPhone 13"},
            {"label": "iPhone SE", "value": "iPhone SE"}
        ]

    if df_Base_Pedestre is None:
        return "Nenhum dado durante esse periodo", modeloCelulares

    dfFinal = ""
    if celular != "tudo" and modelo == "tudo" and tipo == "tudo" and loja == "tudo" and sexo == "tudo":
        dfFinal = df_Base_Pedestre[df_Base_Pedestre['tipo_celular'] == celular]
    elif celular == "tudo" and modelo != "tudo" and tipo == "tudo" and loja == "tudo" and sexo == "tudo":
        dfFinal = df_Base_Pedestre[df_Base_Pedestre['modelo_celular'] == modelo]
    elif celular == "tudo" and modelo == "tudo" and tipo != "tudo" and loja == "tudo" and sexo == "tudo":
        dfFinal = df_Base_Pedestre[df_Base_Pedestre['ultimo_tipo_cupom'] == tipo]
    elif celular == "tudo" and modelo == "tudo" and tipo == "tudo" and loja != "tudo" and sexo == "tudo":
        dfFinal = df_Base_Pedestre[df_Base_Pedestre['ultimo_tipo_loja'] == loja]
    elif celular == "tudo" and modelo == "tudo" and tipo == "tudo" and loja == "tudo" and sexo != "tudo":
        dfFinal = df_Base_Pedestre[df_Base_Pedestre['sexo'] == sexo]
    elif celular == "tudo" and modelo == "tudo" and tipo == "tudo" and loja == "tudo" and sexo == "tudo":
        dfFinal = df_Base_Pedestre
    else:
        if celular != "tudo" and modelo != "tudo" and tipo == "tudo" and loja == "tudo" and sexo == "tudo":
            dfCelular = df_Base_Pedestre[df_Base_Pedestre['tipo_celular'] == celular]
            dfFinal = dfCelular[dfCelular['modelo_celular'] == modelo]
        elif celular != "tudo" and modelo != "tudo" and tipo != "tudo" and loja == "tudo" and sexo == "tudo":
            dfCelular = df_Base_Pedestre[df_Base_Pedestre['tipo_celular'] == celular]
            dfModelo = dfCelular[dfCelular['modelo_celular'] == modelo]
            dfFinal = dfModelo[dfModelo['ultimo_tipo_cupom'] == tipo]
        elif celular != "tudo" and modelo != "tudo" and tipo != "tudo" and loja != "tudo" and sexo == "tudo":
            dfCelular = df_Base_Pedestre[df_Base_Pedestre['tipo_celular'] == celular]
            dfModelo = dfCelular[dfCelular['modelo_celular'] == modelo]
            dfUltimoCupom = dfModelo[dfModelo['ultimo_tipo_cupom'] == tipo]
            dfFinal = dfUltimoCupom[dfUltimoCupom['ultimo_tipo_loja'] == loja]
        elif celular != "tudo" and modelo == "tudo" and tipo != "tudo" and loja == "tudo" and sexo == "tudo":
            dfCelular = df_Base_Pedestre[df_Base_Pedestre['tipo_celular'] == celular]
            dfFinal = dfCelular[dfCelular['ultimo_tipo_cupom'] == tipo]
        elif celular != "tudo" and modelo == "tudo" and tipo == "tudo" and loja != "tudo" and sexo == "tudo":
            dfCelular = df_Base_Pedestre[df_Base_Pedestre['tipo_celular'] == celular]
            dfFinal = dfCelular[dfCelular['ultimo_tipo_loja'] == loja]
        elif celular != "tudo" and modelo == "tudo" and tipo == "tudo" and loja == "tudo" and sexo != "tudo":
            dfCelular = df_Base_Pedestre[df_Base_Pedestre['tipo_celular'] == celular]
            dfFinal = dfCelular[dfCelular['sexo'] == sexo]
        elif celular == "tudo" and modelo != "tudo" and tipo != "tudo" and loja == "tudo" and sexo == "tudo":
            dfModelo = df_Base_Pedestre[df_Base_Pedestre['modelo_celular'] == modelo]
            dfFinal = dfModelo[dfModelo['ultimo_tipo_cupom'] == tipo]
        elif celular == "tudo" and modelo != "tudo" and tipo == "tudo" and loja != "tudo" and sexo == "tudo":
            dfModelo = df_Base_Pedestre[df_Base_Pedestre['modelo_celular'] == modelo]
            dfFinal = dfModelo[dfModelo['ultimo_tipo_loja'] == loja]
        elif celular == "tudo" and modelo != "tudo" and tipo == "tudo" and loja == "tudo" and sexo != "tudo":
            dfModelo = df_Base_Pedestre[df_Base_Pedestre['modelo_celular'] == modelo]
            dfFinal = dfModelo[dfModelo['sexo'] == sexo]
        elif celular != "tudo" and modelo == "tudo" and tipo != "tudo" and loja != "tudo" and sexo == "tudo":
            dfUltimoCupom = df_Base_Pedestre[df_Base_Pedestre['ultimo_tipo_cupom'] == tipo]
            dfFinal = dfUltimoCupom[dfUltimoCupom['ultimo_tipo_loja'] == loja]
        elif celular != "tudo" and modelo != "tudo" and tipo != "tudo" and loja == "tudo" and sexo != "tudo":
            dfUltimoCupom = df_Base_Pedestre[df_Base_Pedestre['ultimo_tipo_cupom'] == tipo]
            dfFinal = dfUltimoCupom[dfUltimoCupom['sexo'] == sexo]
        elif celular == "tudo" and modelo == "tudo" and tipo == "tudo" and loja != "tudo" and sexo != "tudo":
            dfLoja = df_Base_Pedestre[df_Base_Pedestre['ultimo_tipo_loja'] == loja]
            dfFinal = dfLoja[dfLoja['sexo'] == sexo]
        elif celular == "tudo" and modelo != "tudo" and tipo != "tudo" and loja != "tudo" and sexo != "tudo":
            dfModelo = df_Base_Pedestre[df_Base_Pedestre['modelo_celular'] == modelo]
            dfUltimoCupom = dfModelo[dfModelo['ultimo_tipo_cupom'] == tipo]
            dfLoja = dfUltimoCupom[dfUltimoCupom['ultimo_tipo_loja'] == loja]
            dfFinal = dfLoja[dfLoja['sexo'] == sexo]
        elif celular != "tudo" and modelo == "tudo" and tipo != "tudo" and loja != "tudo" and sexo != "tudo":
            dfCelular = df_Base_Pedestre[df_Base_Pedestre['tipo_celular'] == celular]
            dfUltimoCupom = dfCelular[dfCelular['ultimo_tipo_cupom'] == tipo]
            dfLoja = dfUltimoCupom[dfUltimoCupom['ultimo_tipo_loja'] == loja]
            dfFinal = dfLoja[dfLoja['sexo'] == sexo]
        elif celular != "tudo" and modelo != "tudo" and tipo == "tudo" and loja != "tudo" and sexo != "tudo":
            dfCelular = df_Base_Pedestre[df_Base_Pedestre['tipo_celular'] == celular]
            dfModelo = dfCelular[dfCelular['modelo_celular'] == modelo]
            dfLoja = dfModelo[dfModelo['ultimo_tipo_loja'] == loja]
            dfFinal = dfLoja[dfLoja['sexo'] == sexo]
        elif celular != "tudo" and modelo != "tudo" and tipo != "tudo" and loja == "tudo" and sexo != "tudo":
            dfCelular = df_Base_Pedestre[df_Base_Pedestre['tipo_celular'] == celular]
            dfModelo = dfCelular[dfCelular['modelo_celular'] == modelo]
            dfUltimoCupom = dfModelo[dfModelo['ultimo_tipo_cupom'] == tipo]
            dfFinal = dfUltimoCupom[dfUltimoCupom['sexo'] == sexo]
        elif celular != "tudo" and modelo != "tudo" and tipo != "tudo" and loja != "tudo" and sexo == "tudo":
            dfCelular = df_Base_Pedestre[df_Base_Pedestre['tipo_celular'] == celular]
            dfModelo = dfCelular[dfCelular['modelo_celular'] == modelo]
            dfUltimoCupom = dfModelo[dfModelo['ultimo_tipo_cupom'] == tipo]
            dfFinal = dfUltimoCupom[dfUltimoCupom['ultimo_tipo_loja'] == loja]
        else:
            dfCelular = df_Base_Pedestre[df_Base_Pedestre['tipo_celular'] == celular]
            dfModelo = dfCelular[dfCelular['modelo_celular'] == modelo]
            dfUltimoCupom = dfModelo[dfModelo['ultimo_tipo_cupom'] == tipo]
            dfLoja = dfUltimoCupom[dfUltimoCupom['ultimo_tipo_loja'] == loja]
            dfFinal = dfLoja[dfLoja['ultimo_tipo_loja'] == loja]

    return dcc.Graph(
        id='mapa-calor',
        figure=create_heatmap(dfFinal)
    ), modeloCelulares