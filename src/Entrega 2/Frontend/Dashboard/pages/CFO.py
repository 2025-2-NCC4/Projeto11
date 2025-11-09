import io
from datetime import datetime

import dash
from dash import html, dcc, Input, Output, State
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Image, Spacer, Paragraph, Table, TableStyle, PageBreak
import plotly.express as px
import plotly.io as pio


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
                value=7,  # Default: agosto
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
            html.Div([
                html.Button("📄 Exportar para PDF", id="btn-exportar-pdf-cfo", n_clicks=0, className="exportar-btn",
                style={
                    "background-color": "#2c4c3b",
                    "color": "white",
                    "border": "none",
                    "border-radius": "8px",
                    "padding": "10px 20px",
                    "font-size": "16px",
                    "cursor": "pointer",
                    "margin": "20px auto",
                    "margin-left":"10px",
                    "display": "block",
                    "box-shadow": "0 2px 6px rgba(0,0,0,0.2)"
                }),
            dcc.Download(id="download-pdf-cfo")
            ])

        ], style={"display": "flex", "align-items": "center", "justify-content": "center", "margin-bottom": "30px"}),
    ], className="header", style={'margin-left':'25px'}),

    html.Div(id="cfo-kpi-container", className="content"),
], className="Pagina", style={'width':'182vh', 'padding-top':'0'})

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
                    html.H3('💵 Receita Total', className="kpi-title", style={'color':'#2c4c3b'}),
                    html.P('Mostra a receita gerada por cupons.', className="kpi-description", style={'color':'black'}),
                    html.P(f'R$ {formatted_receita}', className="kpi-value", id="MainKpiReceitaTotal", style={'color':'black'}),
                ], className="kpi-box", href=f"/Detalhes?kpi=receita&ano={ano}&mes={mes}", id="ReceitaTotal", style={'color':'black'}),
            ], className="metricasMainCard"),

            html.Div([
                dcc.Link([
                    html.H3('💰 Lucro Líquido (Net Profit)', className="kpi-title", style={'color': '#ff7f0e'}),
                    html.P('Mede a rentabilidade real.', className="kpi-description", style={'color': 'black'}),
                    html.P(f'R$ {formatted_lucro}', className="kpi-value", id="MainKpiCeoLucroLiquido",
                           style={'color': 'black'}),
                ], className="kpi-box", href=f"/Detalhes?kpi=lucro&ano={ano}&mes={mes}")
            ], className="metricasMainCard"),

            html.Div([
                dcc.Link([
                    html.H3('📊 Margem de Lucro (Profit Margin)', className="kpi-title", style={'color': '#2ca02c'}),
                    html.P('Indica eficiência operacional.', className="kpi-description", style={'color': 'black'}),
                ], className="kpi-box", href=f"/Detalhes?kpi=margem&ano={ano}&mes={mes}")
            ], className="metricasMainCard"),
        ], className="row-metrica", style={"display": "flex", "gap": "20px", "padding-bottom": "20px"}),

        html.Div([

            html.Div([
                dcc.Link([
                    html.H3('💰 Categorias mais lucrativas', className="kpi-title",
                            style={'color': '#9467bd'}),
                    html.P('Avalia eficácia estratégica.', className="kpi-description", style={'color': 'black'})
                ], className="kpi-box", href=f"/Detalhes?kpi=categorias&ano={ano}&mes={mes}")
            ], className="metricasMainCard"),

            html.Div([
                dcc.Link([
                    html.H3('📅 Cupons resgatados por dia e hora', className="kpi-title", style={'color': '#d62728'}),
                    html.P('Avalia tendências e performance.', className="kpi-description", style={'color': 'black'}),
                    html.P('', className="kpi-value", id="MainKpiCeoCrescimentoReceita", style={'color': 'black'}),
                ], className="kpi-box", href=f"/Detalhes?kpi=crescimento&ano={ano}&mes={mes}")
            ], className="metricasMainCard"),
        ], className="row-metrica", style={"display": "flex", "gap": "20px"})
    ], className="content", style={ 'margin-left':'25px'})

@dash.callback(
    Output("download-pdf-cfo", "data"),
    Input("btn-exportar-pdf-cfo", "n_clicks"),
    State("mes-seletor", "value"),
    State("ano-seletor", "value"),
    prevent_initial_call=True
)
def exportar_pdf_cfo(n_clicks, mes, ano):
    from functions.CallbackMetricas import dfCupons, get_mes

    def get_df_for_period(array, ano, mes):
        for item in array:
            if item["ano"] == ano and item["mes"] == mes:
                return item["data"]
        return None

    df_cupons = get_df_for_period(dfCupons, ano, mes)
    if df_cupons is None or df_cupons.empty:
        return dcc.send_string("⚠️ Nenhum dado disponível para o período selecionado.")

    # === Cálculos Financeiros ===
    receita_total = df_cupons["valor_cupom"].sum()
    lucro_total = df_cupons["repasse_picmoney"].sum()
    margem_total = (lucro_total / receita_total * 100) if receita_total != 0 else 0

    prev_mes = mes - 1 if mes > 1 else 12
    prev_ano = ano if mes > 1 else ano - 1
    df_prev = get_df_for_period(dfCupons, prev_ano, prev_mes)
    if df_prev is not None and not df_prev.empty:
        receita_prev = df_prev["valor_cupom"].sum()
        crescimento_receita = ((receita_total - receita_prev) / receita_prev * 100) if receita_prev != 0 else 0
    else:
        crescimento_receita = 0

    # === Criar PDF ===
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    estilos = {
        "titulo": ParagraphStyle("titulo", parent=styles["Title"], fontSize=20, textColor="#2c4c3b", alignment=1),
        "subtitulo": ParagraphStyle("subtitulo", parent=styles["Heading2"], textColor="#333333"),
        "texto": ParagraphStyle("texto", parent=styles["Normal"], fontSize=11, leading=15),
        "resumo": ParagraphStyle("resumo", parent=styles["Normal"], fontSize=12, leading=16, textColor="#2c4c3b"),
    }

    elementos = []

    # === CAPA ===
    try:
        elementos.append(Image("assets/piclogo.png", width=2.5*inch, height=2.5*inch))
    except Exception:
        pass
    elementos.append(Spacer(1, 30))
    elementos.append(Paragraph("💵 Relatório Financeiro do CFO", estilos["titulo"]))
    elementos.append(Paragraph(f"{get_mes(mes)} / {ano}", estilos["texto"]))
    elementos.append(Spacer(1, 20))
    elementos.append(Paragraph(
        "Análise consolidada da saúde financeira e eficiência operacional da empresa.", estilos["texto"]))
    elementos.append(Spacer(1, 30))

    # === TABELA DE KPIs ===
    resumo_dados = [
        ["Indicador", "Valor"],
        ["Receita Total", f"R$ {receita_total:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")],
        ["Lucro Líquido", f"R$ {lucro_total:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")],
        ["Margem de Lucro", f"{margem_total:.2f}%"],
        ["Crescimento Mensal", f"{crescimento_receita:.2f}%"]
    ]
    tabela = Table(resumo_dados, hAlign="LEFT", colWidths=[250, 150])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c4c3b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("FONTSIZE", (0, 0), (-1, -1), 11)
    ]))
    elementos.append(tabela)
    elementos.append(Spacer(1, 25))

    # === Gráfico Receita Diária ===
    df_cupons["data"] = pd.to_datetime(df_cupons["data"], errors="coerce")
    fig_receita = px.line(
        df_cupons.groupby("data", as_index=False)["valor_cupom"].sum(),
        x="data", y="valor_cupom", title="📅 Receita Diária", template="plotly_white"
    )
    img_receita = io.BytesIO(pio.to_image(fig_receita, format="png", width=700, height=400))
    elementos.append(Paragraph("💰 Receita Total", estilos["subtitulo"]))
    elementos.append(Image(img_receita, width=6*inch, height=3*inch))
    elementos.append(Spacer(1, 20))

    # === Lucro por Categoria ===
    df_categoria_lucro = (
        df_cupons.groupby("categoria_estabelecimento", as_index=False)["repasse_picmoney"].sum()
        .sort_values("repasse_picmoney", ascending=False).head(10)
    )
    fig_lucro = px.bar(df_categoria_lucro, x="repasse_picmoney", y="categoria_estabelecimento",
                       orientation="h", title="🏷️ Top Categorias por Lucro", template="plotly_white",
                       color="repasse_picmoney", color_continuous_scale="Greens")
    img_lucro = io.BytesIO(pio.to_image(fig_lucro, format="png", width=700, height=400))
    elementos.append(Paragraph("📈 Lucro Líquido por Categoria", estilos["subtitulo"]))
    elementos.append(Image(img_lucro, width=6*inch, height=3*inch))
    elementos.append(PageBreak())

    # === SEGUNDA PÁGINA — Eficiência Operacional ===
    elementos.append(Paragraph("⚙️ Análise de Eficiência Operacional", estilos["titulo"]))
    elementos.append(Spacer(1, 15))

    df_categoria = (
        df_cupons.groupby("categoria_estabelecimento", as_index=False)
        .agg({"valor_cupom": "sum", "repasse_picmoney": "sum"})
    )
    df_categoria["margem_operacional"] = (df_categoria["repasse_picmoney"] / df_categoria["valor_cupom"]) * 100
    df_categoria = df_categoria.sort_values("margem_operacional", ascending=False).head(10)

    # Gráfico 1 — Margem Operacional por Categoria
    fig_margem_op = px.bar(df_categoria, x="margem_operacional", y="categoria_estabelecimento",
                           orientation="h", title="📊 Margem Operacional por Categoria",
                           template="plotly_white", color="margem_operacional",
                           color_continuous_scale="Blues")
    img_margem = io.BytesIO(pio.to_image(fig_margem_op, format="png", width=700, height=400))
    elementos.append(Image(img_margem, width=6*inch, height=3*inch))
    elementos.append(Spacer(1, 25))

    # Gráfico 2 — Comparativo Receita vs Repasses
    fig_comp = px.bar(df_categoria.melt(id_vars="categoria_estabelecimento",
                                        value_vars=["valor_cupom", "repasse_picmoney"],
                                        var_name="Tipo", value_name="Valor"),
                      x="Valor", y="categoria_estabelecimento", color="Tipo",
                      barmode="group", title="💹 Receita x Repasse por Categoria",
                      template="plotly_white")
    img_comp = io.BytesIO(pio.to_image(fig_comp, format="png", width=700, height=400))
    elementos.append(Image(img_comp, width=6*inch, height=3*inch))
    elementos.append(Spacer(1, 30))

    elementos.append(Paragraph(
        "Esta análise mostra a eficiência operacional e a proporção de lucro em relação à receita por categoria.",
        estilos["texto"]
    ))

    # === Rodapé ===
    elementos.append(Spacer(1, 40))
    data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")
    elementos.append(Paragraph(f"Relatório gerado automaticamente em {data_geracao}.", estilos["texto"]))
    elementos.append(Paragraph("PicMoney CFO Dashboard © 2025", estilos["resumo"]))

    # === Gerar PDF ===
    doc.build(elementos)
    buffer.seek(0)
    return dcc.send_bytes(buffer.getvalue(), f"Relatorio_CFO_{ano}_{mes}.pdf")