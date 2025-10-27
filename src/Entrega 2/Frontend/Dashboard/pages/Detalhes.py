import dash
from dash import html, dcc, Input, Output
from urllib.parse import parse_qs, urlparse
from functions.CallbackMetricas import dfCupons, get_mes, dfBasePedestre, dfMassaTeste, dfBaseCadastral
import plotly.express as px
import pandas as pd

dash.register_page(__name__, path='/Detalhes')

layout = html.Div([
    dcc.Location(id='url-detalhes', refresh=False),  # Captura a URL
    html.Div(id='conteudo-detalhes', className="Pagina", style={'width':'200vh'})  # Conteúdo que será atualizado
])

def get_df_for_period(array, ano, mes):
    for item in array:
        if item["ano"] == ano and item["mes"] == mes:
            return item["data"]
    return None



@dash.callback(
    Output('conteudo-detalhes', 'children'),
    Input('url-detalhes', 'search')  # Pega a parte da URL após o "?"
)
def atualizar_detalhes(search):
    if not search:
        return html.H3("Selecione uma métrica na página do CEO.")

    # Extrai os parâmetros da URL
    query = parse_qs(urlparse(search).query)
    kpi = query.get('kpi', [None])[0]
    ano = query.get('ano', [None])[0]
    mes = query.get('mes', [None])[0]

    if not (kpi and ano and mes):
        return html.H3("Parâmetros inválidos na URL.")

    ano = int(ano)
    mes = int(mes)

    if kpi == "receita":
        dfCuponsFix = get_df_for_period(dfCupons, ano, mes)

        if dfCuponsFix is None or dfCuponsFix.empty:
            return html.Div("⚠️ Nenhum dado disponível para o período selecionado.",
                            style={"text-align": "center", "color": "red"})

        receitaTotal = dfCuponsFix['valor_cupom'].sum()
        receita = "{:,.2f}".format(receitaTotal).replace(",", "_").replace(".", ",").replace("_", ".")

        dfCuponsFix["data"] = pd.to_datetime(dfCuponsFix["data"], dayfirst=True, errors="coerce")

        df_diaria = dfCuponsFix.groupby("data", as_index=False)["valor_cupom"].sum()
        fig_diaria = px.line(
            df_diaria, x="data", y="valor_cupom",
            title="📅 Receita Diária no Mês",
            labels={"data": "Data", "valor_cupom": "Receita (R$)"},
            template="plotly_white"
        )
        fig_diaria.update_traces(line_color="#0083B8", line_width=3)
        fig_diaria.update_layout(margin=dict(l=40, r=20, t=60, b=40))

        df_categoria = (
            dfCuponsFix.groupby("categoria_estabelecimento", as_index=False)["valor_cupom"].sum()
            .sort_values("valor_cupom", ascending=False)
            .head(10)
        )
        fig_categoria = px.bar(
            df_categoria, x="valor_cupom", y="categoria_estabelecimento",
            orientation="h",
            title="🏷️ Top 10 Categorias por Receita",
            labels={"valor_cupom": "Receita (R$)", "categoria_estabelecimento": "Categoria"},
            template="plotly_white",
            color="valor_cupom",
            color_continuous_scale="Blues"
        )
        fig_categoria.update_layout(yaxis={'categoryorder': 'total ascending'}, margin=dict(l=80, r=20, t=60, b=40))

        # --- Layout HTML ---
        return html.Div([
            # Header
            html.Div([
                html.H1('📊 Receita Total', className="titulo"),
                html.P(f'{get_mes(mes)} / {ano}', style={'font-size': '18px', 'color': '#666'})
            ], className="header", style={'margin-bottom': '20px'}),

            html.Div([
                html.Div([
                    html.Div([
                        html.H2('Receita Total do Mês', style={'margin-bottom': '10px', 'color': '#000000'}),
                        html.P(f'R$ {receita}',
                               style={'font-size': '28px',
                                      'font-weight': 'bold',
                                      'color': '#0083B8',
                                      'margin': '0'}),
                        html.P('Comparada ao mesmo período anterior',
                               style={'font-size': '14px', 'color': '#888'})
                    ], style={
                        'padding': '20px',
                        'border': '1px solid #ddd',
                        'border-radius': '12px',
                        'background-color': '#fff',
                        'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                        'text-align': 'center'
                    }),
                ], style={'flex': '1', 'margin-right': '20px'}),

                html.Div([
                    html.Div([
                        html.Div([
                            html.H3('📈 Indicadores de Receita',
                                    style={'margin-bottom': '15px', 'color': '#333', 'font-weight': '600'}),
                            dcc.Graph(figure=fig_diaria, style={'height': '300px'}),
                            dcc.Graph(figure=fig_categoria, style={'height': '300px'})
                        ], style={
                            'padding': '20px',
                            'border': '1px solid #ddd',
                            'border-radius': '12px',
                            'background-color': '#fff',
                            'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                        })
                    ])
                ], style={'flex': '2'}),
            ], style={
                'display': 'flex',
                'flex-direction': 'row',
                'justify-content': 'space-between',
                'align-items': 'stretch',
                'padding': '10px 20px'
            })
        ])



    elif kpi == "lucro":
        dfCuponsFix = get_df_for_period(dfCupons, ano, mes)

        if dfCuponsFix is None or dfCuponsFix.empty:
            return html.Div("⚠️ Nenhum dado disponível para o período selecionado.",
                            style={"text-align": "center", "color": "red"})

        lucro_total = dfCuponsFix["repasse_picmoney"].sum()
        lucro_formatado = "{:,.2f}".format(lucro_total).replace(",", "_").replace(".", ",").replace("_", ".")

        dfCuponsFix["data"] = pd.to_datetime(dfCuponsFix["data"], dayfirst=True, errors="coerce")

        df_diaria = dfCuponsFix.groupby("data", as_index=False)["repasse_picmoney"].sum()
        fig_diaria_lucro = px.line(
            df_diaria, x="data", y="repasse_picmoney",
            title="📅 Lucro Líquido Diário no Mês",
            labels={"data": "Data", "repasse_picmoney": "Lucro Líquido (R$)"},
            template="plotly_white"
        )
        fig_diaria_lucro.update_traces(line_color="#2E8B57", line_width=3)
        fig_diaria_lucro.update_layout(margin=dict(l=40, r=20, t=60, b=40))

        df_categoria = (
            dfCuponsFix.groupby("categoria_estabelecimento", as_index=False)["repasse_picmoney"].sum()
            .sort_values("repasse_picmoney", ascending=False)
            .head(10)
        )
        fig_categoria_lucro = px.bar(
            df_categoria, x="repasse_picmoney", y="categoria_estabelecimento",
            orientation="h",
            title="🏷️ Top 10 Categorias por Lucro Líquido",
            labels={"repasse_picmoney": "Lucro Líquido (R$)", "categoria_estabelecimento": "Categoria"},
            template="plotly_white",
            color="repasse_picmoney",
            color_continuous_scale="Greens"
        )
        fig_categoria_lucro.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(l=80, r=20, t=60, b=40)
        )

        return html.Div([
            html.Div([
                html.H1('💰 Lucro Líquido', className="titulo"),
                html.P(f'{get_mes(mes)} / {ano}', style={'font-size': '18px', 'color': '#666'})
            ], className="header", style={'margin-bottom': '20px'}),

            html.Div([
                html.Div([
                    html.Div([
                        html.H2('Lucro Líquido do Mês', style={'margin-bottom': '10px', 'color':'#000000'}),
                        html.P(f'R$ {lucro_formatado}',
                               style={'font-size': '28px',
                                      'font-weight': 'bold',
                                      'color': '#2E8B57',
                                      'margin': '0'}),
                        html.P('Resultado líquido do período selecionado',
                               style={'font-size': '14px', 'color': '#888'})
                    ], style={
                        'padding': '30px',
                        'border': '1px solid #ddd',
                        'border-radius': '12px',
                        'background-color': '#fff',
                        'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                        'text-align': 'center'
                    }),
                ], style={'flex': '1', 'margin-right': '20px'}),

                html.Div([
                    html.Div([
                        html.Div([
                            html.H3('📊 Indicadores de Lucro',
                                    style={'margin-bottom': '15px', 'color': '#333', 'font-weight': '600'}),
                            dcc.Graph(figure=fig_diaria_lucro, style={'height': '300px'}),
                            dcc.Graph(figure=fig_categoria_lucro, style={'height': '300px'})
                        ], style={
                            'padding': '20px',
                            'border': '1px solid #ddd',
                            'border-radius': '12px',
                            'background-color': '#fff',
                            'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                        })
                    ])
                ], style={'flex': '2'}),
            ], style={
                'display': 'flex',
                'flex-direction': 'row',
                'justify-content': 'space-between',
                'align-items': 'stretch',
                'padding': '10px 20px'
            })
        ])

    elif kpi == "margem":

        dfCuponsFix = get_df_for_period(dfCupons, ano, mes)
        if dfCuponsFix is None or dfCuponsFix.empty:
            return html.Div("⚠️ Nenhum dado disponível para o período selecionado.",style={"text-align": "center", "color": "red"})

        dfCuponsFix["data"] = pd.to_datetime(dfCuponsFix["data"], dayfirst=True, errors="coerce")


        receita_total = dfCuponsFix["valor_cupom"].sum()
        lucro_total = dfCuponsFix["repasse_picmoney"].sum()
        margem_total = (lucro_total / receita_total * 100) if receita_total != 0 else 0
        margem_formatada = "{:,.2f}".format(margem_total).replace(",", "_").replace(".", ",").replace("_", ".")


        df_diaria = (
            dfCuponsFix.groupby("data", as_index=False).agg({"valor_cupom": "sum", "repasse_picmoney": "sum"})
        )

        df_diaria["margem"] = (df_diaria["repasse_picmoney"] / df_diaria["valor_cupom"]) * 100

        df_categoria = (
            dfCuponsFix.groupby("categoria_estabelecimento", as_index=False)
            .agg({"valor_cupom": "sum", "repasse_picmoney": "sum"})
        )
        df_categoria["margem"] = (df_categoria["repasse_picmoney"] / df_categoria["valor_cupom"]) * 100
        df_categoria = df_categoria.sort_values("margem", ascending=False).head(8)

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
        return html.Div([
            html.Div([
                html.H1('📊 Margem de Lucro', className="titulo"),
                html.P(f'{get_mes(mes)} / {ano}', style={'font-size': '18px', 'color': '#666'})
            ], className="header", style={'margin-bottom': '20px'}),
            html.Div([
                html.Div([
                    html.Div([
                        html.H2('Margem Média do Mês', style={'margin-bottom': '10px', 'color':'#000000'}),
                        html.P(f'{margem_formatada}%',
                               style={'font-size': '28px',
                                      'font-weight': 'bold',
                                      'color': '#FF7F0E',
                                      'margin': '0'}),
                        html.P('Percentual médio de lucro sobre a receita',
                               style={'font-size': '14px', 'color': '#888'})
                    ], style={
                        'padding': '30px',
                        'border': '1px solid #ddd',
                        'border-radius': '12px',
                        'background-color': '#fff',
                        'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                        'text-align': 'center'
                    }),
                ], style={'flex': '1', 'margin-right': '20px'}),
                html.Div([
                    html.Div([
                        html.H3('📈 Indicadores de Margem',
                                style={'margin-bottom': '15px', 'color': '#333', 'font-weight': '600'}),
                        html.Div([
                            dcc.Graph(figure=fig_area, style={'height': '300px'}),
                            dcc.Graph(figure=fig_donut, style={'height': '300px'})
                        ], style={'display': 'flex', 'flex-direction': 'column', 'gap': '20px'})
                    ], style={
                        'padding': '20px',
                        'border': '1px solid #ddd',
                        'border-radius': '12px',
                        'background-color': '#fff',
                        'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                    })
                ], style={'flex': '2'})
            ], style={
                'display': 'flex',
                'flex-direction': 'row',
                'justify-content': 'space-between',
                'align-items': 'stretch',
                'padding': '10px 20px'
            })
        ])

    elif kpi == "crescimento":
        dfCuponsFix = get_df_for_period(dfCupons, ano, mes)
        if dfCuponsFix is None or dfCuponsFix.empty:
            return html.Div("⚠️ Nenhum dado disponível para o período selecionado.",
                            style={"text-align": "center", "color": "red"})
        dfCuponsFix["data"] = pd.to_datetime(dfCuponsFix["data"], dayfirst=True, errors="coerce")

        df_mensal = dfCuponsFix.groupby(dfCuponsFix["data"].dt.to_period("M")).agg({"valor_cupom": "sum"})
        df_mensal["crescimento"] = df_mensal["valor_cupom"].pct_change() * 100  # Crescimento percentual mês a mês

        crescimento_medio = df_mensal["crescimento"].mean()
        crescimento_formatado = "{:,.2f}".format(crescimento_medio).replace(",", "_").replace(".", ",").replace("_",".")
        fig_crescimento = px.line(
            df_mensal, x=df_mensal.index.astype(str), y="crescimento",
            title="📈 Crescimento de Receita Mensal",
            labels={"data": "Mês", "crescimento": "Crescimento (%)"},
            template="plotly_white"
        )
        fig_crescimento.update_layout(margin=dict(l=40, r=20, t=60, b=40))
        df_categoria = (
            dfCuponsFix.groupby("categoria_estabelecimento", as_index=False)
            .agg({"valor_cupom": "sum"})
        )
        df_categoria["crescimento"] = (df_categoria["valor_cupom"] / df_categoria["valor_cupom"].sum()) * 100
        fig_categoria = px.bar(
            df_categoria, x="categoria_estabelecimento", y="crescimento",
            title="🏷️ Crescimento por Categoria",
            labels={"categoria_estabelecimento": "Categoria", "crescimento": "Crescimento (%)"},
            template="plotly_white"
        )
        fig_categoria.update_layout(margin=dict(l=40, r=40, t=60, b=40))

        return html.Div([
            html.Div([
                html.H1('📊 Crescimento de Receita', className="titulo"),
                html.P(f'{get_mes(mes)} / {ano}', style={'font-size': '18px', 'color': '#666'})
            ], className="header", style={'margin-bottom': '20px'}),
            html.Div([
                html.Div([
                    html.Div([
                        html.H2('Crescimento Médio do Mês', style={'margin-bottom': '10px', 'color': '#000000'}),
                        html.P(f'{crescimento_formatado}%',
                               style={'font-size': '28px',
                                      'font-weight': 'bold',
                                      'color': '#FF7F0E',
                                      'margin': '0'}),
                        html.P('Percentual médio de crescimento sobre o mês anterior',
                               style={'font-size': '14px', 'color': '#888'})
                    ], style={
                        'padding': '30px',
                        'border': '1px solid #ddd',
                        'border-radius': '12px',
                        'background-color': '#fff',
                        'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                        'text-align': 'center'
                    }),
                ], style={'flex': '1', 'margin-right': '20px'}),
                html.Div([
                    html.Div([
                        html.H3('📈 Indicadores de Crescimento',
                                style={'margin-bottom': '15px', 'color': '#333', 'font-weight': '600'}),
                        html.Div([
                            dcc.Graph(figure=fig_crescimento, style={'height': '300px'}),
                            dcc.Graph(figure=fig_categoria, style={'height': '300px'})
                        ], style={'display': 'flex', 'flex-direction': 'column', 'gap': '20px'})
                    ], style={
                        'padding': '20px',
                        'border': '1px solid #ddd',
                        'border-radius': '12px',
                        'background-color': '#fff',
                        'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                    })
                ], style={'flex': '2'})
            ], style={
                'display': 'flex',
                'flex-direction': 'row',
                'justify-content': 'space-between',
                'align-items': 'stretch',
                'padding': '10px 20px'
            })
        ])


    elif kpi == "categorias":
        def formatarValores(valor):
            return "{:,.2f}".format(valor).replace(",", "_").replace(".", ",").replace("_", ".")

        dfCuponsFix = get_df_for_period(dfCupons, ano, mes)
        df_categoria_sum = dfCuponsFix.groupby('categoria_estabelecimento')['valor_cupom'].sum()
        df_categoria_sum_sorted = df_categoria_sum.sort_values(ascending=False).head(10)
        top_10_categories = df_categoria_sum_sorted.index
        top_10_values = df_categoria_sum_sorted.values
        fig = px.bar(df_categoria_sum_sorted, x=top_10_categories, y=top_10_values,
                     labels={'x': 'Categoria', 'y': 'Total de Valor (R$)'},
                     title="Top 10 Categorias com Maior Receita",
                     template="plotly_dark")
        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=top_10_categories,
                ticktext=top_10_categories,
                tickangle=45,
                tickfont=dict(size=8)
            ),
            yaxis=dict(
                tickformat=",.2f"
            )
        )

        receitaTotal = dfCuponsFix['valor_cupom'].sum()
        formatted_receita = "{:,.2f}".format(receitaTotal).replace(",", "_").replace(".", ",").replace("_", ".")
        return html.Div([
            html.Div([
                html.H1('Categorias mais lucrativas', className="titulo"),
                html.P(f'{get_mes(mes)}/{ano}', style={'text-align':'center'})
            ], className="header"),

            html.Div([
                html.Div([
                    html.H3('Top 10 Categorias Mais Lucrativas', className="card-title", style={'color': '#FFFFFF'}),
                    html.Ul([
                        html.Li(f'{categoria}: R$ {formatarValores(valor)}', className="card-list-item",
                                style={'color': '#FFFFFF'})
                        for categoria, valor in zip(top_10_categories, top_10_values)
                    ])
                ], className="card-metrica", style={'margin': '10px', 'flex': 1}),

                html.Div([
                    dcc.Graph(
                        id='top-10-categorias-graph',
                        figure=fig
                    )
                ], className="card-metrica", style={'margin': '10px', 'flex': 1})
            ], className="Metricas-Card", style={'display': 'flex', 'flex-direction': 'row'})
        ])



    elif kpi == "usuarios":


        dfBasePedestreFix = get_df_for_period(dfBaseCadastral, ano, mes)

        if dfBasePedestreFix is None or dfBasePedestreFix.empty:
            return html.Div("⚠️ Nenhum dado disponível para o período selecionado.",
                            style={"text-align": "center", "color": "red"})


        dfBasePedestreFix["data_nascimento"] = pd.to_datetime(dfBasePedestreFix["data_nascimento"], dayfirst=True,
                                                              errors="coerce")

        sexo_distribuicao = dfBasePedestreFix['sexo'].value_counts(normalize=True).reset_index()

        sexo_distribuicao.columns = ['Sexo', 'Percentual']

        dfBasePedestreFix['faixa_idade'] = pd.cut(dfBasePedestreFix['idade'], bins=[0, 18, 30, 40, 50, 60, 100],
                                                  labels=['0-18', '19-30', '31-40', '41-50', '51-60', '61+'])

        idade_distribuicao = dfBasePedestreFix['faixa_idade'].value_counts(normalize=True).reset_index()

        idade_distribuicao.columns = ['Faixa Etária', 'Percentual']

        categoria_distribuicao = dfBasePedestreFix['categoria_frequentada'].value_counts(normalize=True).reset_index()

        categoria_distribuicao.columns = ['Categoria', 'Percentual']

        bairro_residencial_distribuicao = dfBasePedestreFix['bairro_residencial'].value_counts(
            normalize=True).reset_index()

        bairro_residencial_distribuicao.columns = ['Bairro Residencial', 'Percentual']

        bairro_trabalho_distribuicao = dfBasePedestreFix['bairro_trabalho'].value_counts(normalize=True).reset_index()

        bairro_trabalho_distribuicao.columns = ['Bairro Trabalho', 'Percentual']

        fig_sexo = px.pie(sexo_distribuicao, names="Sexo", values="Percentual", title="🔘 Distribuição por Sexo")

        fig_idade = px.bar(idade_distribuicao, x='Faixa Etária', y='Percentual',
                           title="📊 Distribuição por Faixa Etária", color='Faixa Etária')

        fig_categoria = px.pie(categoria_distribuicao, names="Categoria", values="Percentual",
                               title="🏷️ Categorias Frequentadas")

        fig_bairro_residencial = px.bar(bairro_residencial_distribuicao, x='Bairro Residencial', y='Percentual',
                                        title="🏠 Distribuição por Bairro Residencial", color='Bairro Residencial')

        fig_bairro_trabalho = px.bar(bairro_trabalho_distribuicao, x='Bairro Trabalho', y='Percentual',
                                     title="🏢 Distribuição por Bairro de Trabalho", color='Bairro Trabalho')

        fig_sexo.update_layout(legend=dict(font=dict(size=10), title=""), showlegend=True)

        fig_idade.update_layout(legend=dict(font=dict(size=10), title=""), showlegend=True)

        fig_categoria.update_layout(legend=dict(font=dict(size=10), title=""), showlegend=True)

        fig_bairro_residencial.update_layout(legend=dict(font=dict(size=10), title=""), showlegend=True)

        fig_bairro_trabalho.update_layout(legend=dict(font=dict(size=10), title=""), showlegend=True)


        return html.Div([

            html.Div([

                html.H1('📊 Dados sobre Clientes', className="titulo"),

                html.P(f'{get_mes(mes)} / {ano}', style={'font-size': '18px', 'color': '#666'})

            ], className="header", style={'margin-bottom': '10px'}),

            html.Div([

                html.Div([

                    html.Div([

                        html.H2('Distribuição por Sexo', style={'margin-bottom': '5px', 'color': '#000000'}),
                        dcc.Graph(figure=fig_sexo, style={'height': '350px', 'width': '100%'})

                    ], style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '12px',
                              'background-color': '#fff', 'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                              'text-align': 'center', 'margin-bottom': '15px'}),

                    html.Div([

                        html.H2('Distribuição por Faixa Etária', style={'margin-bottom': '5px', 'color': '#000000'}),

                        dcc.Graph(figure=fig_idade, style={'height': '350px', 'width': '100%'})

                    ], style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '12px',
                              'background-color': '#fff', 'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                              'text-align': 'center', 'margin-bottom': '15px'}),

                ], style={'flex': '1', 'margin-right': '15px'}),

                html.Div([

                    html.Div([

                        html.H3('Distribuição de Categorias Frequentadas',
                                style={'margin-bottom': '10px', 'color': '#333', 'font-weight': '600'}),

                        dcc.Graph(figure=fig_categoria, style={'height': '350px', 'width': '100%'})

                    ], style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '12px',
                              'background-color': '#fff', 'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                              'margin-bottom': '15px'}),

                    html.Div([

                        html.H3('Distribuição por Bairro',
                                style={'margin-bottom': '10px', 'color': '#333', 'font-weight': '600'}),

                        dcc.Graph(figure=fig_bairro_residencial, style={'height': '350px', 'width': '100%'}),

                        dcc.Graph(figure=fig_bairro_trabalho, style={'height': '350px', 'width': '100%'})

                    ], style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '12px',
                              'background-color': '#fff', 'box-shadow': '0 2px 8px rgba(0,0,0,0.05)'}),

                ], style={'flex': '2'})

            ], style={

                'display': 'flex',

                'flex-direction': 'row',

                'justify-content': 'space-between',

                'align-items': 'stretch',

                'padding': '5px 15px'

            })

        ])

    else:
        return html.H3("KPI não reconhecido.")
