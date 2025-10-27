import dash
from dash import html, dcc, Input, Output
import pandas as pd
from functions.CallbackMetricas import dfCupons, dfBaseCadastral, dfMassaTeste, dfBasePedestre

dash.register_page(__name__, path='/CFO')


def formatarValores(valor):
    return "{:,.2f}".format(valor).replace(",", "_").replace(".", ",").replace("_", ".")

def get_df_for_period(array, ano, mes):
    for item in array:
        if item["ano"] == ano and item["mes"] == mes:
            return item["data"]
    return None


layout = html.Div([
    html.Div([
        html.H1("Visão Estratégica do CFO"),
        html.P("Acompanhe a saúde financeira e os principais indicadores econômicos da empresa.", style={'text-align':'center'}),

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
                value=8,  # Default: agosto
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
    ], className="header", style={'margin-left':'25px'}),

    html.Div(id="cfo-kpi-container", className="content"),
], className="Pagina", style={'width':'200vh', 'height':'100vh', 'padding-top':'0'})

@dash.callback(
    Output("cfo-kpi-container", "children"),
    Input("mes-seletor", "value"),
    Input("ano-seletor", "value")
)
def atualizar_metricas(mes, ano):
    df_cupons = get_df_for_period(dfCupons, ano, mes)
    if df_cupons is None:
        return html.Div("⚠️ Nenhum dado disponível para o período selecionado.",
                        style={"text-align": "center", "color": "red"})

    receita_total = df_cupons["valor_cupom"].sum()
    lucro_liquido = df_cupons["repasse_picmoney"].sum()
    margem_lucro = (lucro_liquido / receita_total * 100) if receita_total != 0 else 0

    formatted_receita = formatarValores(receita_total)
    formatted_lucro = formatarValores(lucro_liquido)
    formatted_margem = formatarValores(margem_lucro)

    df_categoria_sum = df_cupons.groupby("categoria_estabelecimento")["valor_cupom"].sum().sort_values(ascending=False)
    if not df_categoria_sum.empty:
        categoria_nome = df_categoria_sum.index[0]
        categoria_valor = formatarValores(df_categoria_sum.iloc[0])
    else:
        categoria_nome, categoria_valor = "-", "0"

    prev_mes = mes - 1
    prev_ano = ano
    if prev_mes == 0:
        prev_mes = 12
        prev_ano -= 1

    df_prev = get_df_for_period(dfCupons, prev_ano, prev_mes)
    if df_prev is not None:
        receita_prev = df_prev["valor_cupom"].sum()
        crescimento_receita = ((receita_total - receita_prev) / receita_prev * 100) if receita_prev != 0 else 0
    else:
        crescimento_receita = 0

    formatted_crescimento = formatarValores(crescimento_receita)

    # KPI layout
    return html.Div([
        html.Div([
            html.Div([
                dcc.Link([
                    html.H3('💵 Receita Total', className="kpi-title"),
                    html.P('Mostra a receita gerada por cupons.', className="kpi-description"),
                    html.P(f'R$ {formatted_receita}', className="kpi-value", id="MainKpiReceitaTotal"),
                ], className="kpi-box", href=f"/Detalhes?kpi=receita&ano={ano}&mes={mes}", id="ReceitaTotal"),
            ], className="card-metrica"),

            html.Div([
                dcc.Link([
                    html.H3('💧 Fluxo de Caixa (Cash Flow)', className="kpi-title"),
                    html.P('Rentabilidade real após repasses.', className="kpi-description"),
                    html.P(f'R$ {formatted_lucro}', className="kpi-value", id="MainKpiLucroLiquido"),
                ], className="kpi-box", href=f"/Detalhes?kpi=fluxo&ano={ano}&mes={mes}")
            ], className="card-metrica"),

            html.Div([
                dcc.Link([
                    html.H3('📉 Margem de Lucro', className="kpi-title"),
                    html.P('Mede a rentabilidade em relação à receita.', className="kpi-description"),
                    html.P(f'{formatted_margem}%', className="kpi-value", id="MainKpiMargemLucro"),
                ], className="kpi-box", href=f"/Detalhes?kpi=margem&ano={ano}&mes={mes}")
            ], className="card-metrica"),
        ], className="row-metrica", style={"display": "flex", "gap": "20px", "padding-bottom": "20px"}),

        html.Div([
            html.Div([
                dcc.Link([
                    html.H3('📈 Crescimento de Receita', className="kpi-title"),
                    html.P('Mede o crescimento percentual em relação ao mês anterior.', className="kpi-description"),
                    html.P(f'{formatted_crescimento}%', className="kpi-value", id="MainKpiCrescimentoReceita"),
                ], className="kpi-box", href=f"/Detalhes?kpi=crescimento&ano={ano}&mes={mes}")
            ], className="card-metrica"),

            html.Div([
                dcc.Link([
                    html.H3('💎 Lifetime Value (LTV)', className="kpi-title"),
                    html.P('Valor total gerado por um cliente ao longo do tempo.', className="kpi-description"),
                    html.P(f'1° {categoria_nome} (R$ {categoria_valor})', className="kpi-value", id="MainKpiLTV"),
                ], className="kpi-box", href=f"/Detalhes?kpi=ltv&ano={ano}&mes={mes}")
            ], className="card-metrica"),

            html.Div([
                dcc.Link([
                    html.H3('⏱️ Ciclo de Conversão de Caixa', className="kpi-title"),
                    html.P('Mede a eficiência das operações financeiras.', className="kpi-description"),
                    html.P(f'R$ {categoria_valor}', className="kpi-value", id="MainKpiCicloConversao"),
                ], className="kpi-box", href=f"/Detalhes?kpi=ciclo&ano={ano}&mes={mes}")
            ], className="card-metrica"),
        ], className="row-metrica", style={"display": "flex", "gap": "20px"})
    ], className="content", style={ 'margin-left':'25px'})

