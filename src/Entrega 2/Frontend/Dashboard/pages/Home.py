import dash
from flask import request
from dash import html, dcc, Output, Input
import plotly.express as px
# from app import dfCupons, dfBaseCadastral,dfBasePedestres,dfMassaTeste

dash.register_page(__name__, path='/Home')

# totalTransacoes = len(dfCupons)
#
# receitaTotal = dfCupons['valor_cupom'].sum()
# formatted_receitaTotal = f"R${receitaTotal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
#
# tipoCupons = dfCupons["tipo_cupom"].value_counts()

# fig = px.pie(
#     names=tipoCupons.index,
#     values=tipoCupons.values,
#     title="Distribuição por Cupons",
#     labels={"value": "Count", "names": "Tipo de Cupom"},
#     hole=0.3
# )

# fig.update_layout(
#     paper_bgcolor='#ADD8E6',
#     plot_bgcolor='#F5DEB3'
# )

layout = html.Div([
    dcc.Location(id="url"),
    html.Div(id="user-info", className='UserTitulo'),
    html.Div([
        html.Div([
            dcc.Link(
                "",
                href='',
                style={'text-decoration': 'none', 'color': '#ffffff', 'height': '100%', 'width': '100%'}
                , id="CargoCard"
            ),
        ], className="CEOCard"),
        html.Div("", className="CFOCard"),
        html.Div("", className="CTOCard")
    ], className="Cards"),

    html.Div([
        # html.Div([
        #     dcc.Graph(
        #         id="pie-chart",
        #         figure=fig,
        #         style={}
        #     ),
        # ], style={'height':'300px', 'width':'400px', 'margin-right':'20px', 'margin-left': '-10px'}),

        html.Div([
            dcc.Link(
                "Mapa de Calor",
                href='/mapacalor', style={'text-decoration': 'none', 'color':'#ffffff', 'height': '100%', 'width':'100%'}
            ),
        ],className="CEOCard"),

        #html.Div(f"Receita Total\n{formatted_receitaTotal}", className="CTOCard")
    ], className="Cards"),
    dcc.Location(id="homeRedirect", refresh=True)
], className="Pagina", style={'width':'200vh', 'height':'100vh', 'padding-top':'0'})

@dash.callback(
    Output("homeRedirect", "href"),
    Input("homeRedirect", "href")
)
def redirecionar(link):
    nome = request.cookies.get("user_nome")
    if not nome:
        return "/"
    return dash.no_update