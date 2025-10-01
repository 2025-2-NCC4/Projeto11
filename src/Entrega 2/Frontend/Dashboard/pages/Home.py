import dash
from dash import html, dcc
import plotly.express as px

from app import dfCupons, dfBaseCadastral,dfBasePedestres,dfMassaTeste

dash.register_page(__name__, path='/Home')

totalTransacoes = len(dfCupons)

receitaTotal = dfCupons['valor_cupom'].sum()
formatted_receitaTotal = f"R${receitaTotal:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

tipoCupons = dfCupons["tipo_cupom"].value_counts()

fig = px.pie(
    names=tipoCupons.index,
    values=tipoCupons.values,
    title="Distribuição por Cupons",
    labels={"value": "Count", "names": "Tipo de Cupom"},
    hole=0.3
)

fig.update_layout(
    paper_bgcolor='#ADD8E6',
    plot_bgcolor='#F5DEB3'
)

layout = html.Div([
    html.Div([
        html.Div("CEO", className="CEOCard"),
        html.Div("CFO", className="CFOCard"),
        html.Div("CTO", className="CTOCard")
    ], className="Cards"),

    html.Div([
        html.Div([
            dcc.Graph(
                id="pie-chart",
                figure=fig,
                style={}
            ),
        ], style={'height':'300px', 'width':'400px', 'margin-right':'20px', 'margin-left': '-10px'}),

        html.Div([
            dcc.Link(
                "Mapa de Calor",
                href='/mapacalor', style={'text-decoration': 'none', 'color':'#ffffff', 'height': '100%', 'width':'100%'}
            ),
        ],className="CEOCard"),

        html.Div(f"Receita Total\n{formatted_receitaTotal}", className="CTOCard")
    ], className="Cards")
], className="Pagina")
