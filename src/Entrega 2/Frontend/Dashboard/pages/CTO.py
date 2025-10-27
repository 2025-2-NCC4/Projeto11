import dash
from dash import html, dcc, Input, Output
import pandas as pd
from functions.CallbackMetricas import dfCupons, dfBaseCadastral, dfMassaTeste, dfBasePedestre

dash.register_page(__name__, path='/CTO')


def formatarValores(valor):
    return "{:,.2f}".format(valor).replace(",", "_").replace(".", ",").replace("_", ".")

def get_df_for_period(array, ano, mes):
    for item in array:
        if item["ano"] == ano and item["mes"] == mes:
            return item["data"]
    return None

layout = html.Div([
    html.Div([
        html.H1("Visão Estratégica do CTO"),
        html.P("Monitore a performance tecnológica, confiabilidade e inovação da empresa.", style={'text-align':'center'}),

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
                value=8,
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

    html.Div(id="cto-kpi-container", className="content"),
], className="Pagina", style={'width':'200vh', 'padding-top':'0'})


@dash.callback(
    Output("cto-kpi-container", "children"),
    Input("mes-seletor", "value"),
    Input("ano-seletor", "value")
)
def atualizar_metricas(mes, ano):
    df_cupons = get_df_for_period(dfCupons, ano, mes)
    df_base_cadastral = get_df_for_period(dfBaseCadastral, ano, mes)
    df_base_pedestre = get_df_for_period(dfBasePedestre, ano, mes)
    df_massa_teste = get_df_for_period(dfMassaTeste, ano, mes)

    if df_cupons is None or df_base_cadastral is None or df_base_pedestre is None:
        return html.Div("⚠️ Nenhum dado disponível para o período selecionado.",
                        style={"text-align": "center", "color": "red"})

    # KPI 1: Sistema de Cadastro de Usuários
    num_usuarios = df_base_pedestre['celular'].nunique()
    formatted_num_usuarios = formatarValores(num_usuarios)

    merged_df = df_base_cadastral.merge(df_base_pedestre, on='celular', how='inner')

    # KPI 2: Taxa de Adoção de Aplicativo
    num_com_app = df_base_pedestre[df_base_pedestre['possui_app_picmoney'] == 'Sim']['celular'].nunique()
    taxa_adocao_app = (num_com_app / num_usuarios) * 100 if num_usuarios != 0 else 0
    formatted_taxa_adocao_app = formatarValores(taxa_adocao_app)

    # KPI 3: Valor Médio de Cupom
    valor_medio_cupom = df_cupons['valor_cupom'].mean()
    formatted_valor_medio_cupom = formatarValores(valor_medio_cupom)

    # KPI 4: Performance do Sistema de Pedestres
    num_pedestres = df_base_pedestre['celular'].nunique()
    formatted_num_pedestres = formatarValores(num_pedestres)

    # KPI 5: Adoção Geográfica de Serviços
    geo_adocao = merged_df.groupby('cidade_residencial')['celular'].nunique().sort_values(ascending=False).head(3)
    geo_adocao = geo_adocao.reset_index()
    geo_adocao_str = ", ".join([f"{row['cidade_residencial']} ({formatarValores(row['celular'])} usuários)" for _, row in geo_adocao.iterrows()])

    df_base_pedestre['data_ultima_compra'] = pd.to_datetime(df_base_pedestre['data_ultima_compra'], errors='coerce', dayfirst=True)
    df_massa_teste['data_captura'] = pd.to_datetime(df_massa_teste['data_captura'], errors='coerce')

    # KPI 6: Eficiência do Fluxo de Dados
    df_base_pedestre['latency'] = (df_massa_teste['data_captura'] - df_base_pedestre['data_ultima_compra']).dt.total_seconds()
    df_base_pedestre['latency'] = df_base_pedestre['latency'].fillna(0)
    eficiencia_fluxo = df_base_pedestre['latency'].mean()
    formatted_eficiencia_fluxo = formatarValores(eficiencia_fluxo)

    # KPI layout
    return html.Div([
        html.Div([
            html.Div([
                dcc.Link([
                    html.H3('💻 Sistema de Cadastro de Usuários', className="kpi-title"),
                    html.P('Quantos usuários estão cadastrados na plataforma.', className="kpi-description"),
                    html.P(f'{formatted_num_usuarios} usuários', className="kpi-value"),
                ], className="kpi-box", href=f"/Detalhes?kpi=usuarios&ano={ano}&mes={mes}"),
            ], className="card-metrica"),

            html.Div([
                dcc.Link([
                    html.H3('🔧 Taxa de Adoção de Aplicativo', className="kpi-title"),
                    html.P('Proporção de usuários que possuem o app instalado.', className="kpi-description"),
                    html.P(f'{formatted_taxa_adocao_app}%', className="kpi-value"),
                ], className="kpi-box", href=f"/Detalhes?kpi=margem&ano={ano}&mes={mes}"),
            ], className="card-metrica"),

            html.Div([
                dcc.Link([
                    html.H3('📊 Valor Médio de Cupom', className="kpi-title"),
                    html.P('Média do valor de cada cupom gerado.', className="kpi-description"),
                    html.P(f'R$ {formatted_valor_medio_cupom}', className="kpi-value"),
                ], className="kpi-box", href=f"/Detalhes?kpi=margem&ano={ano}&mes={mes}"),
            ], className="card-metrica"),
        ], className="row-metrica", style={"display": "flex", "gap": "20px", "padding-bottom": "20px"}),

        html.Div([
            html.Div([
                dcc.Link([
                    html.H3('🛠️ Performance do Sistema de Pedestres', className="kpi-title"),
                    html.P('Quantas interações com o sistema ocorreram.', className="kpi-description"),
                    html.P(f'{formatted_num_pedestres} pedestres', className="kpi-value"),
                ], className="kpi-box", href=f"/Detalhes?kpi=margem&ano={ano}&mes={mes}"),
            ], className="card-metrica"),

            html.Div([
                dcc.Link([
                    html.H3('📍 Adoção Geográfica de Serviços', className="kpi-title"),
                    html.P('Distribuição dos usuários por cidade.', className="kpi-description"),
                    html.P(geo_adocao_str, className="kpi-value"),
                ], className="kpi-box", href=f"/Detalhes?kpi=margem&ano={ano}&mes={mes}"),
            ], className="card-metrica"),

            html.Div([
                dcc.Link([
                    html.H3('⚡ Eficiência do Fluxo de Dados', className="kpi-title"),
                    html.P('Tempo médio de captura e processamento de dados.', className="kpi-description"),
                    html.P(f'{formatted_eficiencia_fluxo} segundos', className="kpi-value"),
                ], className="kpi-box", href=f"/Detalhes?kpi=margem&ano={ano}&mes={mes}"),
            ], className="card-metrica"),
        ], className="row-metrica", style={"display": "flex", "gap": "20px"}),
    ], className="content", style={'padding':'20px'})
