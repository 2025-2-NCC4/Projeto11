import dash
import pandas as pd
from flask import request
from dash import html, dcc, Output, Input
import plotly.express as px

from functions.CallbackMetricas import dfCupons, dfMassaTeste, dfBaseCadastral, dfBasePedestre, get_mes, \
    get_df_for_period

# from app import dfCupons, dfBaseCadastral,dfBasePedestres,dfMassaTeste

dash.register_page(__name__, path='/Home')

ano = 2025
mes = 7

def create_no_data_layout():
    return html.Div([
        html.Div([
            html.H1('📊 Métricas Gerais', className="titulo"),
        ], className="header", style={'margin-bottom': '20px'}),

        html.Div([
            html.Div([
                html.H2('Não há dados para esse período', style={'color': 'red', 'font-size': '24px', 'text-align': 'center'}),
                html.P('Por favor, selecione um período com dados disponíveis.', style={'text-align': 'center'}),
            ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'height': '400px'})
        ], style={'display': 'flex', 'flex-direction': 'column', 'gap': '20px', 'padding': '20px'}),
        dcc.Location(id="novaData", refresh=True)
    ], className="Pagina", style={'padding-top': '0'})

def generate_metrics(dfCupons, dfBasePedestre, dfMassaTeste, dfBaseCadastral, ano, mes):
    # Obtenção dos dados filtrados por período
    dfCuponsFix = get_df_for_period(dfCupons, ano, mes)
    dfBasePedestreFix = get_df_for_period(dfBasePedestre, ano, mes)
    dfMassaTesteFix = get_df_for_period(dfMassaTeste, ano, mes)
    dfBaseCadastralFix = get_df_for_period(dfBaseCadastral, ano, mes)

    if dfCuponsFix is None or dfBaseCadastralFix is None or dfBasePedestreFix is None or dfMassaTesteFix is None:
        return None

    dfCuponsFix["data"] = pd.to_datetime(dfCuponsFix["data"], dayfirst=True, errors="coerce")

    # Cálculos gerais
    receita_total = dfCuponsFix["valor_cupom"].sum()
    lucro_total = dfCuponsFix["repasse_picmoney"].sum()
    margem_total = (lucro_total / receita_total * 100) if receita_total != 0 else 0
    margem_formatada = "{:,.2f}".format(margem_total).replace(",", "_").replace(".", ",").replace("_", ".")

    # Cálculo do valor médio por ticket
    total_cupons = len(dfCuponsFix)
    valor_medio_ticket = receita_total / total_cupons if total_cupons > 0 else 0
    valor_medio_ticket_formatado = "{:,.2f}".format(valor_medio_ticket).replace(",", "_").replace(".",
                                                                                                  ",").replace(
        "_", ".")

    # Métricas Diárias
    df_diaria = dfCuponsFix.groupby("data", as_index=False).agg(
        {"valor_cupom": "sum", "repasse_picmoney": "sum"})
    df_diaria["margem"] = (df_diaria["repasse_picmoney"] / df_diaria["valor_cupom"]) * 100

    # Métricas por Categoria
    df_categoria = dfCuponsFix.groupby("categoria_estabelecimento", as_index=False).agg(
        {"valor_cupom": "sum", "repasse_picmoney": "sum"})
    df_categoria["margem"] = (df_categoria["repasse_picmoney"] / df_categoria["valor_cupom"]) * 100
    df_categoria = df_categoria.sort_values("margem", ascending=False).head(8)

    # Criação de Gráficos
    df_area = df_diaria.melt(id_vars="data", value_vars=["valor_cupom", "repasse_picmoney"],
                             var_name="Tipo", value_name="Valor")
    fig_area = px.area(
        df_area, x="data", y="Valor", color="Tipo",
        title="📅 Evolução de Receita e Lucro Diário",
        color_discrete_map={"valor_cupom": "#1f77b4", "repasse_picmoney": "#2ca02c"},
        template="plotly_white"
    )
    fig_area.update_layout(margin=dict(l=40, r=20, t=60, b=40), legend_title_text='')

    fig_donut = px.pie(
        df_categoria,
        names="categoria_estabelecimento",
        values="margem",
        hole=0.5,
        title="🏷️ Margem Média por Categoria",
        color_discrete_sequence=px.colors.sequential.Oranges_r
    )
    fig_donut.update_traces(textinfo="percent+label", textposition="outside", pull=[0.05] * len(df_categoria))
    fig_donut.update_layout(margin=dict(l=40, r=40, t=60, b=40))

    # Gráfico de barras para a distribuição de lucro por tipo de cupom
    df_cupom_tipo = dfCuponsFix.groupby("tipo_cupom", as_index=False).agg(
        {"valor_cupom": "sum", "repasse_picmoney": "sum"})
    fig_bars = px.bar(
        df_cupom_tipo,
        x="tipo_cupom", y="repasse_picmoney",
        title="📊 Lucro por Tipo de Cupom",
        labels={"repasse_picmoney": "Lucro", "tipo_cupom": "Tipo de Cupom"},
        color="tipo_cupom",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_bars.update_layout(margin=dict(l=40, r=40, t=60, b=40))

    # Gráfico de distribuição por faixa de valor de cupom (novo gráfico)
    bins = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500]  # Defina as faixas
    labels = ['0-50', '51-100', '101-150', '151-200', '201-250', '251-300', '301-350', '351-400', '401-450',
              '451-500']
    dfCuponsFix['faixa_valor'] = pd.cut(dfCuponsFix['valor_cupom'], bins=bins, labels=labels)

    df_faixa_valor = dfCuponsFix.groupby("faixa_valor", as_index=False).agg({"valor_cupom": "count"})
    fig_faixa_valor = px.bar(
        df_faixa_valor,
        x="faixa_valor", y="valor_cupom",
        title="📊 Distribuição de Cupons por Faixa de Valor",
        labels={"valor_cupom": "Número de Cupons", "faixa_valor": "Faixa de Valor do Cupom"},
        color="faixa_valor",
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig_faixa_valor.update_layout(margin=dict(l=40, r=40, t=60, b=40))

    return {
        "margem_total": margem_formatada,
        "fig_area": fig_area,
        "fig_donut": fig_donut,
        "fig_bars": fig_bars,
        "fig_faixa_valor": fig_faixa_valor,  # Novo gráfico
        "receita_total": f"R${receita_total:,.2f}".replace(",", "_").replace(".", ",").replace("_", "."),
        "lucro_total": f"R${lucro_total:,.2f}".replace(",", "_").replace(".", ",").replace("_", "."),
        "valor_medio_ticket": f"R${valor_medio_ticket_formatado}",
        "margemop": f"{lucro_total / receita_total * 100:,.2f}%".replace(",", "_").replace(".", ",").replace(
            "_", ".")
    }


# Layout
def create_layout(metrics):
    return html.Div([
        html.Div([
            dcc.Location(id="homeRedirect", refresh=True),
            html.H1(id="nomeUsuarioHome", className="titulo"),
            html.H1('📊 Métricas Gerais', className="titulo"),
        ], className="header", style={'margin-bottom': '20px'}),

        # html.Div([
        #     dcc.Dropdown(
        #         id="mes-seletor-home",
        #         options=[
        #             {"label": "Janeiro", "value": 1},
        #             {"label": "Fevereiro", "value": 2},
        #             {"label": "Março", "value": 3},
        #             {"label": "Abril", "value": 4},
        #             {"label": "Maio", "value": 5},
        #             {"label": "Junho", "value": 6},
        #             {"label": "Julho", "value": 7},
        #             {"label": "Agosto", "value": 8},
        #             {"label": "Setembro", "value": 9},
        #             {"label": "Outubro", "value": 10},
        #             {"label": "Novembro", "value": 11},
        #             {"label": "Dezembro", "value": 12},
        #         ],
        #         value=8,  # Default: agosto
        #         clearable=False,
        #         style={"width": "200px", "margin-right": "20px", "height": '40px'}
        #     ),
        #     dcc.Input(
        #         id="ano-seletor-home",
        #         type="number",
        #         value=2025,
        #         min=2020, max=2100,
        #         step=1,
        #         style={"width": "120px", "height": '35px'}
        #     ),
        # ], style={"display": "flex", "align-items": "center", "justify-content": "center", "margin-bottom": "30px"}),
        html.Div([
            # Seção de Receita Total, Lucro e Valor Médio por Ticket
            html.Div([
                dcc.Link([
                    html.H2('Receita Total', style={ 'color': '#000', 'text-decoration': 'none', 'font-size': '15px'}),
                    html.P(metrics["receita_total"],
                           style={'font-size': '28px', 'font-weight': 'bold', 'color': '#1f77b4',
                                    'text-decoration': 'none',
                                  'margin': '0'}),
                    html.P('Valor total das receitas no mês', style={'font-size': '14px', 'color': '#888'})
                ], href=f"/Detalhes?kpi=receita&ano={ano}&mes={mes}", style={ 'width': '220px'
                }, className="metricasMainCardHome"),

                dcc.Link([
                    html.H2('Lucro Líquido', style={ 'color': '#000', 'font-size': '15px'}),
                    html.P(metrics["lucro_total"],
                           style={'font-size': '28px', 'font-weight': 'bold', 'color': '#FF7F0E',
                                  'margin': '0'}),
                    html.P('Lucro após deduções', style={'font-size': '14px', 'color': '#888'})
                ], href=f"/Detalhes?kpi=lucro&ano={ano}&mes={mes}", style={
                    'width': '220px'
                }, className="metricasMainCardHome"),

                dcc.Link([
                    html.H2('Valor Médio por Ticket', style={'color': '#000', 'font-size': '15px'}),
                    html.P(metrics["valor_medio_ticket"],
                           style={'font-size': '28px', 'font-weight': 'bold', 'color': '#FF5CFF',
                                  'margin': '0'}),
                    html.P('Valor médio por cupom no período', style={'font-size': '14px', 'color': '#888'})
                ], href=f"/Detalhes?kpi=valorMedioTicket&ano={ano}&mes={mes}", style={
                    'width': '220px'
                }, className="metricasMainCardHome"),

                dcc.Link([
                    html.H2('Margem Operacional', style={'color': '#000', 'font-size': '15px'}),
                    html.P(metrics["margemop"],
                           style={'font-size': '28px', 'font-weight': 'bold', 'color': '#5CFF5C',
                                  'margin': '0'}),
                    html.P('Margem de receita que retorna a PicMoney',
                           style={'font-size': '14px', 'color': '#888'})
                ], href=f"/Detalhes?kpi=margemOperacional&ano={ano}&mes={mes}", style={
                    'width': '220px'
                }, className="metricasMainCardHome"),
            ], style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'space-between',
                      'flex': 1}),

            # Gráficos
            html.Div([
                html.Div([
                    dcc.Graph(figure=metrics["fig_area"], style={'height': '400px', 'width': '100%', 'border-radius': '10px'}),
                    dcc.Graph(figure=metrics["fig_donut"], style={'height': '400px', 'width': '100%', 'border-radius': '10px'})
                ], style={'flex': 1, 'padding': '10px', 'border-radius': '10px'}),

                html.Div([
                    dcc.Graph(figure=metrics["fig_bars"], style={'height': '400px', 'width': '100%', 'border-radius': '10px'}),
                    dcc.Graph(figure=metrics["fig_faixa_valor"], style={'height': '400px', 'width': '100%', 'border-radius': '10px'})
                    # Novo gráfico
                ], style={'flex': 1, 'padding': '10px', 'border-radius': '10px'}),
            ], style={
                'display': 'flex',
                'flex-direction': 'row',
                'justify-content': 'space-between',
                'align-items': 'stretch',
                'gap': '20px',
                'border-radius': '10px',
                'flex': 2
            })
        ], style={'display': 'flex', 'flex-direction': 'column', 'gap': '20px', 'padding': '20px'}),
        dcc.Location(id="verificarNome")
    ], className="Pagina", style={'padding-top': '0',  'width':'100vh'}, id="novaData")


# Geração das métricas e layout
metrics = generate_metrics(dfCupons, dfBasePedestre, dfMassaTeste, dfBaseCadastral, ano, mes)
if metrics is None:
    layout = create_no_data_layout()
else:
    layout = create_layout(metrics)


@dash.callback(
    Output("nomeUsuarioHome", "children"),
    Input("verificarNome", "pathname")
)
def mudarNome(pathname):
    nome = request.cookies.get("user_nome")
    link = ""

    if nome:
        return f"Olá, {nome}"
    return dash.no_update

@dash.callback(
    Output("novaData", "children"),
    Input("mes-seletor-home", "value"),
    Input("ano-seletor-home", "value")
)
def novaData(mesEscolhido, anoEscolhido):
    metrics = generate_metrics(dfCupons, dfBasePedestre, dfMassaTeste, dfBaseCadastral, anoEscolhido, mesEscolhido)

    if metrics is None:
        return create_no_data_layout()

    return create_layout(metrics)

@dash.callback(
    Output("homeRedirect", "href"),
    Input("homeRedirect", "href")
)
def redirecionar(link):
    nome = request.cookies.get("user_nome")
    if not nome:
        return "/"
    return dash.no_update