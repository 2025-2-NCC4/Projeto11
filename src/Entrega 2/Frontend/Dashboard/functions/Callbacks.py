import base64
import io
from urllib.parse import urlparse, parse_qs

import dash
import pandas as pd
import requests
from dash import Output, Input, State, html, dcc
from flask import Flask, redirect, request, make_response
from functions import PadronizacaoCSV

#Endpoints backend
backendURL = "http://localhost:5000"
backendURL_cadastro = backendURL + "/cadastro"
backendURL_login = backendURL +"/login"

def registrarcallbacks(app):
    #Registrar os cookies
    @app.server.route('/set_user_cookie')
    def set_user_cookie():
        nome = request.args.get('nome')
        email = request.args.get('email')
        cargo = request.args.get('cargo')

        response = make_response(redirect('/Home'))

        response.set_cookie('user_nome', nome)
        response.set_cookie('user_email', email)
        response.set_cookie('user_cargo', cargo)

        return response

    # Callback Cadastro
    @app.callback(
        Output("signup-status", "children"),
        Output("urlCadastro", "href"),
        Input("signup-button", "n_clicks"),
        State("nome", "value"),
        State("email", "value"),
        State("password", "value"),
        State("position", "value"),
        State("other-position", "value"),
        prevent_initial_call=True
    )
    def cadastro_handler(n_clicks, nome, email, password, position, other_position):
        if position == 'Outro' and other_position:
            position = other_position

        if n_clicks:
            payload = {"nome": nome, "email": email, "senha": password, "cargo": position}
            try:
                resp = requests.post(backendURL_cadastro, json=payload)
            except Exception as e:
                return f"Erro de conexão: {e}", dash.no_update

            if resp.status_code == 201:
                redirect_url = f"/set_user_cookie?nome={nome}&email={email}&cargo={position}"
                return "Cadastro realizado com sucesso!", redirect_url
            elif resp.status_code == 400:
                return f"Dados inválidos: {resp.text}", dash.no_update
            else:
                return f"Erro {resp.status_code}: {resp.text}", dash.no_update

        return dash.no_update, dash.no_update

    #Callback Login
    @app.callback(
        Output("login-status", "children"),
        Output("urlLogin", "href"),
        Input("login-button", "n_clicks"),
        State("email", "value"),
        State("password", "value"),
        prevent_initial_call=True
    )
    def login_handler(n_clicks, email, password):
        trigger = dash.ctx.triggered_id
        if trigger == "login-button":
            payload = {"email": email, "senha": password}
            try:
                resp = requests.post(backendURL_login, json=payload)
            except Exception as e:
                return f"Erro de conexão: {e}", dash.no_update

            if resp.status_code == 201:
                json_data = resp.json()
                redirect_url = f"/set_user_cookie?nome={json_data["nome"]}&email={email}&cargo={json_data["cargo"]}"
                return "Login realizado com sucesso!", redirect_url
            elif resp.status_code == 400:
                return f"Dados inválidos: {resp.text}", dash.no_update
            elif resp.status_code == 404:
                return "Usuário não encontrado.", dash.no_update
            else:
                return f"Erro {resp.status_code}: {resp.text}", dash.no_update

        return dash.no_update, dash.no_update

    #Callback para a visibilidade da caixa de opção outras
    @app.callback(
        Output('other-position', 'style'),
        Output('other-position-container', 'style'),
        Input('position', 'value')
    )
    def show_other_position_input(selected_position):
        if selected_position == 'Outro':
            return {'display': 'block'}, {'display': 'block'}
        return {'display': 'none'}, {'display': 'none'}

    #Callback para buscar informações para a página Home
    @app.callback(
        Output("user-info", "children"),
        Output("CargoCard", "children"),
        Output("CargoCard", "href"),
        Input("url", "pathname")
    )
    def display_user_info(pathname):
        nome = request.cookies.get("user_nome")
        cargo = request.cookies.get("user_cargo")
        link = ""

        if cargo == "CEO":
            link = "/CEO"
        elif cargo == "CFO":
            link = "/CFO"
        elif cargo == "CTO":
            link = "/CTO"
        else:
            return "Usuário não logado.", dash.no_update, "Cargo invalido"

        if nome and cargo:
            return f"Olá, {nome}!", f"{cargo}", link
        return "Usuário não logado.", dash.no_update, dash.no_update
    #Redireciona a paǵina Cadastro para a página Home, caso o usuário esteja logado
    @app.callback(
        Output("urlCadastroLogado","href"),
        Input("urlAtualCadastro", "href")
    )
    def redirecionar_cadastro(urlAtualCadastro):
        nome = request.cookies.get("user_nome")
        if nome:
            return "/Home"
        return dash.no_update

    @app.callback(
        Output("urlLoginLogado", "href"),
        Input("urlAtualLogin", "href")
    )
    def redirecionar_cadastro(urlAtualLogin):
        nome = request.cookies.get("user_nome")
        if nome:
            return "/Home"
        return dash.no_update

    # Callback para upload do arquivo e mudança do layout
    @app.callback(
        [Output('drag-and-drop-container', 'style', allow_duplicate=True),
         Output('uploaded-layout', 'style', allow_duplicate=True),
         Output('output-data-upload', 'children')],
        Input('upload-data', 'contents'),
        Input('upload-data', 'filename'),
        prevent_initial_call=True
    )
    def upload_file(contents, filename):
        if contents is None:
            return {'display': 'block'}, {'display': 'none'}, None

        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)

        try:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep=";")

            return {'display': 'none'}, {'display': 'block'}, html.Div([
    html.Div([
        html.H4(f"📂 Arquivo Carregado: {filename}",
                style={'margin-bottom': '5px', 'color': '#333', 'font-weight': '600'}),
        html.Hr(style={'border': '1px solid #ddd', 'margin': '10px 0'}),

        html.P("Prévia dos primeiros registros do arquivo:",
               style={'font-size': '14px', 'color': '#666', 'margin-bottom': '10px'}),

        html.Div([
            html.Table(
                [html.Tr([html.Th(col, style={'padding': '6px 10px', 'background-color': '#2C3E50',
                                              'color': 'white', 'border': '1px solid #ddd', 'font-weight': '500'})
                          for col in df.columns])] +
                [html.Tr([
                    html.Td(df.iloc[i][col],
                            style={'padding': '5px 8px', 'text-align': 'center', 'border': '1px solid #ddd'})
                    for col in df.columns
                ]) for i in range(min(len(df), 5))],
                style={
                    'width': '100%',
                    'font-size': '12px',
                    'border-collapse': 'collapse',
                    'border-radius': '6px',
                    'overflow': 'hidden',
                    'background-color': '#fafafa',
                }
            )
        ], style={
            'max-height': '250px',
            'overflowY': 'auto',
            'margin-top': '10px',
            'border': '1px solid #eee',
            'border-radius': '8px',
            'box-shadow': '0 2px 6px rgba(0,0,0,0.05)',
            'padding': '5px',
        }),
    ], style={
        'background-color': '#fff',
        'border-radius': '10px',
        'padding': '20px',
        'box-shadow': '0 2px 8px rgba(0,0,0,0.1)',
        'margin-bottom': '25px'
    }),

    html.Div([
        html.H4("⚙️ Configurações de Upload", style={'color': '#333', 'margin-bottom': '15px'}),

        html.Div([
            html.Label("Escolha a base:", style={'font-weight': '500'}),
            dcc.RadioItems(
                id='base-choice',
                options=[
                    {'label': 'Base Cadastral', 'value': 'base_cadastral'},
                    {'label': 'Base de Teste', 'value': 'base_teste'},
                    {'label': 'Base de Pedestre', 'value': 'base_pedestre'},
                    {'label': 'Base de Transação', 'value': 'base_transicao'}
                ],
                value='base_cadastral',
                labelStyle={'display': 'block', 'margin': '8px 0'},
                inputStyle={'margin-right': '6px'}
            ),
        ], style={'margin-bottom': '20px'}),

        html.Div([
            html.Div([
                html.Label("Ano:", style={'font-weight': '500'}),
                dcc.Input(
                    id='input-ano',
                    type='number',
                    placeholder='Ex: 2025',
                    min=2000, max=2100, step=1,
                    style={'width': '100%', 'padding': '5px'}
                ),
            ], style={'flex': 1, 'margin-right': '10px'}),

            html.Div([
                html.Label("Mês:", style={'font-weight': '500'}),
                dcc.Dropdown(
                    id='input-mes',
                    options=[{'label': mes, 'value': i+1} for i, mes in enumerate([
                        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
                    ])],
                    placeholder="Selecione o mês",
                    style={'width': '100%'}
                ),
            ], style={'flex': 1})
        ], style={'display': 'flex', 'gap': '10px', 'margin-bottom': '20px'}),

        html.Button(
            '⬆️ Enviar para o Backend',
            id='upload-button-csv',
            n_clicks=0,
            style={
                'background-color': '#0078D7',
                'color': 'white',
                'padding': '10px 20px',
                'border': 'none',
                'border-radius': '6px',
                'cursor': 'pointer',
                'font-weight': '500'
            }
        ),

        html.Div(id="uploadCSV", style={'margin-top': '20px', 'font-size': '14px', 'color': '#333'})
    ], className='Pagina', style={
        'background-color': '#fff',
        'border-radius': '10px',
        'padding': '25px',
        'box-shadow': '0 2px 8px rgba(0,0,0,0.1)',
        'margin-bottom': '30px'
    })
], style={'padding': '20px 40px', 'background-color': '#f4f6f8', 'width': '80%'})


        except Exception as e:
            return {'display': 'block'}, {'display': 'none'}, html.Div([
                f"There was an error processing this file: {str(e)}"
            ])

    @app.callback(
        Output('uploadCSV', 'children'),
        Input('upload-button-csv', 'n_clicks'),
        State('upload-data', 'contents'),
        State('upload-data', 'filename'),
        State('base-choice', 'value'),
        State('input-ano', 'value'),
        State('input-mes', 'value'),
        prevent_initial_call=True
    )
    def enviarCSV(n_clicks, contents, filename, base_choice, ano, mes):
        if n_clicks is None or contents is None:
            return "Nenhum arquivo selecionado ou botão não clicado."

        try:
            if ano is None or mes is None:
                return "Por favor, informe o ano e o mês antes de enviar o arquivo."

            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep=";")

            if base_choice == "base_cadastral":
                df = PadronizacaoCSV.PadronizarBaseCadastral(df)
            elif base_choice == "base_teste":
                df = PadronizacaoCSV.PadronizarMassaTeste(df)
            elif base_choice == "base_pedestre":
                df = PadronizacaoCSV.PadronizarBasePedestre(df)
            elif base_choice == "base_transicao":
                df = PadronizacaoCSV.PadronizarCupons(df)

            nome = request.cookies.get("user_nome")

            if not nome:
                return "Usuário não autenticado."

            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False, sep=";")
            csv_content = csv_buffer.getvalue()

            files = {
                'file': (filename, csv_content, 'text/csv')
            }
            data = {
                'nome': nome,
                'base': base_choice,
                'ano': ano,
                'mes': mes
            }

            backend_upload_url = f"{backendURL}/upload_csv"
            response = requests.post(backend_upload_url, files=files, data=data)

            if response.status_code == 200:
                return f"✅ Arquivo enviado com sucesso! ({base_choice} - {mes}/{ano})"
            else:
                return f"❌ Erro ao enviar arquivo: {response.status_code} - {response.text}"

        except Exception as e:
            return f"⚠️ Erro ao processar o arquivo: {str(e)}"

    # Callback para o btn voltar
    @app.callback(
        [Output('drag-and-drop-container', 'style', allow_duplicate=True),
            Output('uploaded-layout', 'style', allow_duplicate=True)],
        Input('go-back-button', 'n_clicks'),
        prevent_initial_call=True
    )
    def go_back(n_clicks):
        if n_clicks > 0:
            return {'display': 'block'}, {'display': 'none'}
        return {'display': 'none'}, {'display': 'block'}