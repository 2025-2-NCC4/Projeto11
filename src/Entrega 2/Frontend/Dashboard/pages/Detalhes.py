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
                html.P(f'{get_mes(mes)} / {ano}', style={'font-size': '18px', 'color': 'white'})
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
                html.P(f'{get_mes(mes)} / {ano}', style={'font-size': '18px', 'color': 'white'})
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
                html.P(f'{get_mes(mes)} / {ano}', style={'font-size': '18px', 'color': 'white'})
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
        dfCuponsFix["hora"] = dfCuponsFix["hora"].astype(str)  # Ensure 'hora' is string for grouping

        # Coupons Redeemed Per Hour
        df_hourly = dfCuponsFix.groupby(dfCuponsFix["hora"]).agg({"id_cupom": "count"}).reset_index()
        df_hourly.rename(columns={"id_cupom": "cupons_por_hora"}, inplace=True)

        # Coupons Redeemed Per Day of the Week
        dfCuponsFix["dia_da_semana"] = dfCuponsFix["data"].dt.day_name()
        df_daily = dfCuponsFix.groupby("dia_da_semana").agg({"id_cupom": "count"}).reset_index()
        df_daily["dia_da_semana"] = pd.Categorical(df_daily["dia_da_semana"],
                                                   categories=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                                                               "Saturday", "Sunday"], ordered=True)
        df_daily = df_daily.sort_values("dia_da_semana")

        # Creating Graphs
        fig_hourly = px.line(df_hourly, x="hora", y="cupons_por_hora", title="🕒 Cupons Resgatados por Hora",
                             labels={"hora": "Hora", "cupons_por_hora": "Quantidade de Cupons"},
                             template="plotly_white")
        fig_hourly.update_layout(margin=dict(l=40, r=20, t=60, b=40))

        fig_daily = px.bar(df_daily, x="dia_da_semana", y="id_cupom", title="📅 Cupons Resgatados por Dia da Semana",
                           labels={"dia_da_semana": "Dia da Semana", "id_cupom": "Quantidade de Cupons"},
                           template="plotly_white")
        fig_daily.update_layout(margin=dict(l=40, r=40, t=60, b=40))

        # Continue with the rest of your layout code

        return html.Div([
            html.Div([
                html.H1('📊 Cupons Resgatados', className="titulo"),
                html.P(f'{get_mes(mes)} / {ano}', style={'font-size': '18px', 'color': 'white'})
            ], className="header", style={'margin-bottom': '20px'}),

            # First Row: Displaying KPIs and Graphs
            html.Div([
                html.Div([
                    html.Div([
                        html.H2('Cupons Resgatados por Hora', style={'margin-bottom': '10px', 'color': '#000000'}),
                        dcc.Graph(figure=fig_hourly, style={'height': '300px'}),
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
                        html.H2('Cupons Resgatados por Dia da Semana',
                                style={'margin-bottom': '10px', 'color': '#000000'}),
                        dcc.Graph(figure=fig_daily, style={'height': '300px'}),
                    ], style={
                        'padding': '30px',
                        'border': '1px solid #ddd',
                        'border-radius': '12px',
                        'background-color': '#fff',
                        'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                        'text-align': 'center'
                    }),
                ], style={'flex': '1'}),
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
                html.P(f'{get_mes(mes)} / {ano}', style={'font-size': '18px', 'color': 'white'})
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
    elif kpi == "valorMedioTicket":
        # Filtrar o DataFrame de cupons para o período desejado
        dfCuponsFix = get_df_for_period(dfCupons, ano, mes)
        dfBasePedestreFix = get_df_for_period(dfBasePedestre, ano, mes)
        if dfCuponsFix is None or dfCuponsFix.empty:
            return html.Div("⚠️ Nenhum dado disponível para o período selecionado.",
                            style={"text-align": "center", "color": "red"})
        # Combinar com a base de dados do Pedestre para agregar o valor por celular
        dfCombined = pd.merge(dfCuponsFix, dfBasePedestreFix, on="celular", how="inner")
        # Calcular o valor médio por ticket (média de valor_cupom por celular)
        valor_medio_ticket = dfCombined.groupby("celular")["valor_cupom"].mean().reset_index()
        # Calcular a média geral de valor por ticket
        valor_medio_geral = valor_medio_ticket["valor_cupom"].mean()
        # Gerar uma distribuição de valor médio por faixa etária (opcional, mas ajuda na análise)
        dfCombined['faixa_idade'] = pd.cut(dfCombined['idade'], bins=[0, 18, 30, 40, 50, 60, 100],
                                           labels=['0-18', '19-30', '31-40', '41-50', '51-60', '61+'])
        idade_distribuicao = dfCombined.groupby('faixa_idade')['valor_cupom'].mean().reset_index()
        idade_distribuicao.columns = ['Faixa Etária', 'Valor Médio por Ticket']
        # Gerar gráficos
        fig_valor_medio = px.bar(idade_distribuicao, x='Faixa Etária', y='Valor Médio por Ticket',
                                 title="💰 Valor Médio por Ticket por Faixa Etária", color='Faixa Etária')
        fig_valor_medio.update_layout(legend=dict(font=dict(size=10), title=""), showlegend=True)
        return html.Div([
            html.Div([
                html.H1('💰 Dados sobre Valor Médio por Ticket', className="titulo"),
                html.P(f'{get_mes(mes)} / {ano}', style={'font-size': '18px', 'color': 'white'})
            ], className="header", style={'margin-bottom': '10px'}),
            html.Div([
                html.Div([
                    html.Div([
                        html.H2(f'Valor Médio Geral por Ticket: R${valor_medio_geral:.2f}',
                                style={'margin-bottom': '5px', 'color': '#000000'}),
                        html.P('Distribuição do valor médio por faixa etária:', style={'font-size': '16px'}),
                        dcc.Graph(figure=fig_valor_medio, style={'height': '350px', 'width': '100%'})
                    ], style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '12px',
                              'background-color': '#fff', 'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                              'text-align': 'center', 'margin-bottom': '15px'}),
                ], style={'flex': '1', 'margin-right': '15px'}),
            ], style={
                'display': 'flex',
                'flex-direction': 'row',
                'justify-content': 'space-between',
                'align-items': 'stretch',
                'padding': '5px 15px'
            })
        ])
    elif kpi == "margemOperacional":
        # Filtrar o DataFrame de cupons para o período desejado
        dfCuponsFix = get_df_for_period(dfCupons, ano, mes)
        dfBasePedestreFix = get_df_for_period(dfBasePedestre, ano, mes)
        if dfCuponsFix is None or dfCuponsFix.empty:
            return html.Div("⚠️ Nenhum dado disponível para o período selecionado.",
                            style={"text-align": "center", "color": "red"})
        # Calcular o lucro operacional
        dfCuponsFix['lucro_operacional'] = dfCuponsFix['repasse_picmoney']
        # Calcular a receita total
        receita_total = dfCuponsFix['valor_cupom'].sum()
        # Calcular o lucro operacional total
        lucro_operacional_total = dfCuponsFix['lucro_operacional'].sum()
        # Calcular a margem operacional
        if receita_total > 0:
            margem_operacional = (lucro_operacional_total / receita_total) * 100
        else:
            margem_operacional = 0  # Caso a receita total seja 0, a margem operacional será 0%
        # Gerar uma distribuição de margem operacional por faixa etária
        dfCombined = pd.merge(dfCuponsFix, dfBasePedestreFix, on="celular", how="inner")
        dfCombined['faixa_idade'] = pd.cut(dfCombined['idade'], bins=[0, 18, 30, 40, 50, 60, 100],
                                           labels=['0-18', '19-30', '31-40', '41-50', '51-60', '61+'])
        margem_por_idade = dfCombined.groupby('faixa_idade').apply(
            lambda x: (x['lucro_operacional'].sum() / x['valor_cupom'].sum()) * 100).reset_index()
        margem_por_idade.columns = ['Faixa Etária', 'Margem Operacional (%)']
        # Adicionar um gráfico de Margem Operacional por Categoria de Estabelecimento
        margem_por_categoria = dfCuponsFix.groupby('categoria_estabelecimento').apply(
            lambda x: (x['lucro_operacional'].sum() / x['valor_cupom'].sum()) * 100).reset_index()
        margem_por_categoria.columns = ['Categoria de Estabelecimento', 'Margem Operacional (%)']
        # Gerar gráficos
        fig_margem_operacional = px.bar(margem_por_idade, x='Faixa Etária', y='Margem Operacional (%)',
                                        title="📊 Margem Operacional por Faixa Etária", color='Faixa Etária')
        fig_margem_operacional_por_categoria = px.bar(margem_por_categoria, x='Categoria de Estabelecimento',
                                                      y='Margem Operacional (%)',
                                                      title="📊 Margem Operacional por Categoria de Estabelecimento",
                                                      color='Categoria de Estabelecimento')
        # Ajuste dos gráficos
        fig_margem_operacional.update_layout(legend=dict(font=dict(size=10), title=""), showlegend=True)
        fig_margem_operacional_por_categoria.update_layout(legend=dict(font=dict(size=10), title=""), showlegend=True)
        return html.Div([
            html.Div([
                html.H1('📊 Dados sobre Margem Operacional', className="titulo"),
                html.P(f'{get_mes(mes)} / {ano}', style={'font-size': '18px', 'color': 'white'})
            ], className="header", style={'margin-bottom': '10px'}),
            html.Div([
                html.Div([
                    html.Div([
                        html.H2(f'Margem Operacional Geral: {margem_operacional:.2f}%',
                                style={'margin-bottom': '5px', 'color': '#000000'}),
                        html.P('Distribuição da margem operacional por faixa etária:', style={'font-size': '16px'}),
                        dcc.Graph(figure=fig_margem_operacional, style={'height': '350px', 'width': '100%'})
                    ], style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '12px',
                              'background-color': '#fff', 'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                              'text-align': 'center', 'margin-bottom': '15px'}),
                ], style={'flex': '1', 'margin-right': '15px'}),
                # Novo gráfico: Margem Operacional por Categoria de Estabelecimento
                html.Div([
                    html.Div([
                        html.H2('Margem Operacional por Categoria de Estabelecimento',
                                style={'margin-bottom': '5px', 'color': '#000000'}),
                        dcc.Graph(figure=fig_margem_operacional_por_categoria,
                                  style={'height': '550px', 'width': '100%'})
                    ], style={'padding': '20px', 'border': '1px solid #ddd', 'border-radius': '12px',
                              'background-color': '#fff', 'box-shadow': '0 2px 8px rgba(0,0,0,0.05)',
                              'text-align': 'center', 'margin-bottom': '15px'}),
                ], style={'flex': '2'}),
            ], style={
                'display': 'flex',
                'flex-direction': 'row',
                'justify-content': 'space-between',
                'align-items': 'stretch',
                'padding': '5px 15px'
            })
        ])

    elif kpi == "usuariosdiarios":
        # Recuperando os dados filtrados para o ano e mês
        dfCuponsFix = get_df_for_period(dfCupons, ano, mes)
        dfBasePedestreFix = get_df_for_period(dfBasePedestre, ano, mes)
        if dfCuponsFix is None or dfBasePedestreFix is None or dfCuponsFix.empty or dfBasePedestreFix.empty:
            return html.Div("⚠️ Nenhum dado disponível para o período selecionado.",
                            style={"text-align": "center", "color": "red"})
        # Concatenando os dados de cupons e base de pedestres
        dfConcat = pd.concat([dfCuponsFix, dfBasePedestreFix], axis=0, ignore_index=True)
        # Convertendo a coluna de data para datetime
        dfConcat['data'] = pd.to_datetime(dfConcat['data'], format='%d/%m/%Y')
        # Filtrando os dados para excluir os registros do dia 22
        dfConcat = dfConcat[dfConcat['data'].dt.day != 22]
        # Agrupando por data e contando os usuários únicos
        agrupado_por_dia = dfConcat.groupby(dfConcat['data'].dt.date).agg({
            'celular': 'nunique',  # Contar usuários únicos por dia
        }).reset_index()
        # Calculando a média diária de usuários
        mediaUserDaily = 166829 / 30  # Substitua o valor 166829 pelo total de usuários no mês se necessário
        print("Média diária de usuários:", mediaUserDaily)
        # Gráfico de linha para evolução de usuários diários
        fig_line = px.line(
            agrupado_por_dia,
            x='data',
            y='celular',
            title="📅 Evolução de Usuários Diários",
            labels={'celular': 'Número de Usuários'},
            template="plotly_white"
        )
        fig_line.update_layout(margin=dict(l=40, r=20, t=60, b=40))
        # Gráfico de barras para a distribuição de usuários diários
        fig_bar = px.bar(
            agrupado_por_dia,
            x='data',
            y='celular',
            title="📊 Distribuição de Usuários por Dia",
            labels={'celular': 'Número de Usuários'},
            template="plotly_white"
        )
        fig_bar.update_layout(margin=dict(l=40, r=20, t=60, b=40))
        # Retornando o layout do dashboard com os gráficos
        return html.Div([
            html.Div([
                html.H1('📊 Usuários Diários', className="titulo"),
                html.P(f'{get_mes(mes)} / {ano}', style={'font-size': '18px', 'color': 'white'})
            ], className="header", style={'margin-bottom': '20px'}),
            html.Div([
                html.Div([
                    html.Div([
                        html.H2('Média Diária de Usuários', style={'margin-bottom': '10px', 'color': '#000000'}),
                        html.P(f'{mediaUserDaily:.0f} usuários',
                               style={'font-size': '28px',
                                      'font-weight': 'bold',
                                      'color': '#FF7F0E',
                                      'margin': '0'}),
                        html.P('Média diária de usuários durante o mês',
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
                        html.H3('📈 Indicadores de Usuários',
                                style={'margin-bottom': '15px', 'color': '#333', 'font-weight': '600'}),
                        html.Div([
                            dcc.Graph(figure=fig_line, style={'height': '300px'}),
                            dcc.Graph(figure=fig_bar, style={'height': '300px'})
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
    elif kpi == "taxaRetencao":
        dfCuponsFix = get_df_for_period(dfCupons, ano, mes)
        dfBasePedestreFix = get_df_for_period(dfBasePedestre, ano, mes)
        if dfCuponsFix is None or dfBasePedestreFix is None or dfCuponsFix.empty or dfBasePedestreFix.empty:
            return html.Div("⚠️ Nenhum dado disponível para o período selecionado.",
                            style={"text-align": "center", "color": "red"})
        # Concatenando os dados de cupons e base de pedestres
        dfConcat = pd.concat([dfCuponsFix, dfBasePedestreFix], axis=0, ignore_index=True)
        # Convertendo a coluna de data para datetime
        dfConcat['data'] = pd.to_datetime(dfConcat['data'], format='%d/%m/%Y')
        # Definindo as datas das semanas
        datas_primeira_semana = pd.to_datetime(
            ['2025-07-01', '2025-07-02', '2025-07-03', '2025-07-04', '2025-07-05', '2025-07-06',
             '2025-07-07'])  # Semana 1
        datas_ultima_semana = pd.to_datetime(
            ['2025-07-23', '2025-07-24', '2025-07-26', '2025-07-27', '2025-07-28', '2025-07-29',
             '2025-07-30'])  # Semana final
        # Filtrando os dados para a primeira e última semana
        celulares_primeira_semana = dfConcat[dfConcat['data'].isin(datas_primeira_semana)]
        celulares_ultima_semana = dfConcat[dfConcat['data'].isin(datas_ultima_semana)]
        # Excluindo o dia 22 de ambas as semanas
        celulares_primeira_semana = celulares_primeira_semana[celulares_primeira_semana['data'].dt.day != 22]
        celulares_ultima_semana = celulares_ultima_semana[celulares_ultima_semana['data'].dt.day != 22]
        # Encontrando os celulares que apareceram nas duas semanas
        celulares_que_apareceram_nas_duas = celulares_ultima_semana[
            celulares_ultima_semana['celular'].isin(celulares_primeira_semana['celular'])]
        # Calculando os números de usuários únicos nas duas semanas
        tamanho_primeira_semana = celulares_primeira_semana['celular'].nunique()
        tamanho_ultima_semana = celulares_ultima_semana['celular'].nunique()
        tamanho_duas_semanas = celulares_que_apareceram_nas_duas['celular'].nunique()
        # Taxa de Retenção
        taxa_retentao = (tamanho_duas_semanas / tamanho_primeira_semana) * 100
        # Gráfico de área empilhada para evolução de usuários entre as semanas
        usuarios_primeira_semana = celulares_primeira_semana.groupby(celulares_primeira_semana['data'].dt.date).agg(
            {'celular': 'nunique'}).reset_index()
        usuarios_ultima_semana = celulares_ultima_semana.groupby(celulares_ultima_semana['data'].dt.date).agg(
            {'celular': 'nunique'}).reset_index()
        df_area = pd.concat(
            [usuarios_primeira_semana.assign(Semana='Primeira'), usuarios_ultima_semana.assign(Semana='Última')])
        fig_area = px.area(
            df_area,
            x='data',
            y='celular',
            color='Semana',
            title="📅 Evolução de Usuários nas Semanas",
            labels={'celular': 'Número de Usuários'},
            template="plotly_white",
            color_discrete_map={"Primeira": "#1f77b4", "Última": "#ff7f0e"}
        )
        fig_area.update_layout(margin=dict(l=40, r=20, t=60, b=40))
        # Gráfico de donut para mostrar a divisão entre os que retornaram e os que não retornaram
        fig_donut = px.pie(
            names=["Retornaram", "Não Retornaram"],
            values=[tamanho_duas_semanas, tamanho_primeira_semana - tamanho_duas_semanas],
            hole=0.4,
            title="🏷️ Retorno de Usuários",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_donut.update_traces(textinfo="percent+label", textposition="outside", pull=[0.05, 0.05])
        fig_donut.update_layout(margin=dict(l=40, r=40, t=60, b=40))
        # Gráfico de dispersão para mostrar a densidade de usuários por dia
        fig_scatter = px.scatter(
            pd.concat(
                [celulares_primeira_semana.assign(Semana="Primeira"), celulares_ultima_semana.assign(Semana="Última")]),
            x='data',
            y='celular',
            color='Semana',
            title="📍 Densidade de Usuários por Dia",
            labels={'celular': 'Número de Usuários'},
            template="plotly_white",
            color_discrete_map={"Primeira": "#1f77b4", "Última": "#ff7f0e"}
        )
        fig_scatter.update_layout(margin=dict(l=40, r=20, t=60, b=40))
        # Layout com os gráficos e a taxa de retenção
        return html.Div([
            html.Div([
                html.H1('📊 Taxa de Retenção de Usuários', className="titulo"),
                html.P(f'{get_mes(mes)} / {ano}', style={'font-size': '18px', 'color': 'white'})
            ], className="header", style={'margin-bottom': '20px'}),
            html.Div([
                # Seção com a taxa de retenção
                html.Div([
                    html.Div([
                        html.H2('Taxa de Retenção', style={'margin-bottom': '10px', 'color': '#000000'}),
                        html.P(f'{taxa_retentao:.2f}%',
                               style={'font-size': '28px', 'font-weight': 'bold', 'color': '#FF7F0E', 'margin': '0'}),
                        html.P('Percentual de usuários que retornaram na última semana',
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
                # Seção com os gráficos de retenção
                html.Div([
                    html.Div([
                        html.H3('📈 Indicadores de Retenção de Usuários',
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
    elif kpi == 'tempomedio':
        dfCuponsFix = get_df_for_period(dfCupons, ano, mes)
        dfBasePedestreFix = get_df_for_period(dfBasePedestre, ano, mes)
        if dfCuponsFix is None or dfBasePedestreFix is None or dfCuponsFix.empty or dfBasePedestreFix.empty:
            return html.Div("⚠️ Nenhum dado disponível para o período selecionado.",
                            style={"text-align": "center", "color": "red"})
        # Concatenando os dados de cupons e base de pedestres
        dfConcat = pd.concat([dfCuponsFix, dfBasePedestreFix], axis=0, ignore_index=True)
        # Convertendo a coluna de data para datetime
        dfConcat['data'] = pd.to_datetime(dfConcat['data'], format='%d/%m/%Y')
        dfConcat['horario'] = pd.to_datetime(dfConcat['horario'], format='%H:%M:%S')
        # Ordenando o DataFrame por usuário ('celular') e por 'horario'
        dfConcat = dfConcat.sort_values(by=['celular', 'horario'])
        # Calculando a diferença entre transações consecutivas do mesmo usuário
        dfConcat['diff'] = dfConcat.groupby('celular')['horario'].diff().dt.total_seconds() / 3600  # diferença em horas
        # Identificando o início de novas sessões
        dfConcat['nova_sessao'] = dfConcat['diff'] > 4
        # Criando um identificador único para cada sessão por usuário
        dfConcat['sessao_id'] = dfConcat.groupby('celular')['nova_sessao'].cumsum()
        # Calculando a duração de cada sessão (diferença entre a primeira e última transação)
        duracao_sessao = dfConcat.groupby(['celular', 'sessao_id'])['horario'].agg(['min', 'max'])
        # Calculando a duração total de cada sessão em minutos
        duracao_sessao['duracao'] = (duracao_sessao['max'] - duracao_sessao[
            'min']).dt.total_seconds() / 60  # em minutos
        # Categorizar as sessões conforme a duração
        def categorizar_duracao(duracao):
            if duracao <= 15:
                return '0-15 minutos'
            elif duracao <= 30:
                return '15-30 minutos'
            elif duracao <= 60:
                return '30-60 minutos'
            elif duracao <= 120:
                return '1-2 horas'
            elif duracao <= 240:
                return '2-4 horas'
            else:
                return 'Mais de 4 horas'
        # Aplicando a função para categorizar
        duracao_sessao['categoria'] = duracao_sessao['duracao'].apply(categorizar_duracao)
        # Contabilizando as sessões por categoria
        contagem_categorias = duracao_sessao['categoria'].value_counts()
        # Calculando a porcentagem de sessões em cada categoria
        porcentagem_categorias = (contagem_categorias / contagem_categorias.sum()) * 100
        # Calculando o tempo médio de sessão
        tempo_medio_sessao = duracao_sessao['duracao'].mean()
        # Exibindo os resultados no console
        print("Tempo médio de sessão: {:.2f} minutos".format(tempo_medio_sessao))
        print("Contagem de sessões por categoria:")
        print(contagem_categorias)
        print("\nPorcentagem de sessões por categoria:")
        print(porcentagem_categorias)
        # Criando o gráfico de Donut para as categorias de duração
        fig_donut = px.pie(
            names=porcentagem_categorias.index,
            values=porcentagem_categorias,
            hole=0.4,
            title="⏱️ Distribuição do Tempo das Sessões",
            labels={'celular': 'Categoria de Sessão'},
            template="plotly_white",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_donut.update_traces(textinfo="percent+label", textposition="outside",
                                pull=[0.05] * len(porcentagem_categorias))
        fig_donut.update_layout(margin=dict(l=40, r=40, t=60, b=40))
        # Criando o gráfico de Barras para a contagem de sessões por categoria
        fig_bar = px.bar(
            contagem_categorias,
            x=contagem_categorias.index,
            y=contagem_categorias,
            title="📊 Contagem de Sessões por Categoria de Duração",
            labels={'x': 'Categoria de Sessão', 'y': 'Número de Sessões'},
            template="plotly_white",
            color=contagem_categorias.index,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_bar.update_layout(margin=dict(l=40, r=20, t=60, b=40))
        # Layout completo para o Dash
        return html.Div([
            html.Div([
                html.H1('⏳ Tempo Médio de Sessão', className="titulo"),
                html.P(f'{get_mes(mes)} / {ano}', style={'font-size': '18px', 'color': 'white'})
            ], className="header", style={'margin-bottom': '20px'}),
            html.Div([
                # Seção com o tempo médio de sessão
                html.Div([
                    html.Div([
                        html.H2('Tempo Médio de Sessão', style={'margin-bottom': '10px', 'color': '#000000'}),
                        html.P(f'{tempo_medio_sessao:.2f} minutos',
                               style={'font-size': '28px', 'font-weight': 'bold', 'color': '#FF7F0E', 'margin': '0'}),
                        html.P('Tempo médio de uso por sessão dos usuários',
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
                # Seção com os gráficos de categoria de sessão
                html.Div([
                    html.Div([
                        html.H3('📊 Indicadores de Sessões por Duração',
                                style={'margin-bottom': '15px', 'color': '#333', 'font-weight': '600'}),
                        html.Div([
                            dcc.Graph(figure=fig_donut, style={'height': '300px'}),
                            dcc.Graph(figure=fig_bar, style={'height': '300px'})
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
    else:
        return html.H3("KPI não reconhecido.")