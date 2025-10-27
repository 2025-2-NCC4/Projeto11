import dash
import requests
from dash import html, dcc, Input, Output, State
from flask import request, make_response, redirect
from functions.CallbackMetricas import backendURL

dash.register_page(__name__, path='/Perfil')

layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H2("Perfil", className="profile-title", style={'color': '#000000'}),
                html.P("Você pode realizar alterações no seu perfil aqui.", style={'color': '#000000'}),


                html.Div(
                    children=[
                        # Input Name
                        html.Div(
                            children=[
                                html.Label("Nome", htmlFor="name", style={'padding-left': '23px'}),
                                dcc.Input(
                                    id="name-input",
                                    type="text",
                                    placeholder="Digite o seu nome",
                                    className="input-field",
                                    value=""
                                ),
                            ], className="input-container"
                        ),

                        # Input Email
                        html.Div(
                            children=[
                                html.Label("Email", htmlFor="email", style={'padding-left': '23px'}),
                                dcc.Input(
                                    id="email-input",
                                    type="email",
                                    placeholder="Digite o seu E-mail",
                                    className="input-field",
                                    value=""
                                ),
                            ], className="input-container"
                        ),

                        html.Div(
                            children=[
                                html.Label("Senha atual", htmlFor="password", style={'padding-left': '23px'}),
                                dcc.Input(
                                    id="passwordAntiga-input",
                                    type="password",
                                    placeholder="Digite a sua senha atual",
                                    className="input-field",
                                    value=""
                                ),
                            ], className="input-container"
                        ),

                        html.P("Se desejar, você pode alterar a sua senha.", style={"color": "#000000"}),

                        html.Div(
                            children=[
                                html.Label("Nova Senha", htmlFor="password", style={'padding-left': '23px'}),
                                dcc.Input(
                                    id="passwordNova-input",
                                    type="password",
                                    placeholder="Digite a sua nova senha",
                                    className="input-field",
                                    value=""
                                ),
                            ], className="input-container"
                        ),

                        html.Button("Salvar Alterações", id="save-button", className="login-btn"),

                        html.Button("Sair do perfil", id="sair-button", className="login-btn", style={"background-color": "#FF0000"}),

                        html.Div(id="save-status", className="status-message"),

                        html.Div(
                            children=[
                                dcc.Link("Voltar", href="/", className="link"),
                            ], className="links-container"
                        ),
                    ], className="form-container",
                ),
            ], className="login-card"
        ),
        dcc.Location(id="urlPerfil"),
        dcc.Location(id="urlPefilMudar", refresh=True),
        dcc.Location(id="urlLogout", refresh=True),
        dcc.Location(id="redirectPerfil", refresh=True)
    ], className="page-container"
)


@dash.callback(
    Output("name-input", "value"),
    Output("email-input", "value"),
    Input("urlPerfil", "pathname")
)
def mudar_info(pathname):
    nome = request.cookies.get("user_nome")
    email = request.cookies.get("user_email")
    return nome, email


@dash.callback(
    Output("save-status", "children"),
    Output("urlPefilMudar", "href"),
    Input("save-button", "n_clicks"),
    State("name-input", "value"),
    State("email-input", "value"),
    State("passwordAntiga-input", "value"),
    State("passwordNova-input", "value")
)
def save_profile(n_clicks, name, email, senhaAntiga, senhaNova):
    cargo = request.cookies.get("user_cargo")
    nomeAnterior = request.cookies.get("user_nome")

    if n_clicks:
        backendURLMudarPerfil = backendURL + "/mudar_informacoes"
        payload = {"nome": name, "email": email, "nomeanterior": nomeAnterior, "senhaantiga": senhaAntiga, "senhanova": senhaNova}

        try:
            resp = requests.post(backendURLMudarPerfil, json=payload)
        except Exception as e:
            return "Erro de conexão: " + str(e), dash.no_update

        if resp.status_code == 200:
            redirect_url = f"/set_user_cookie?nome={name}&email={email}&cargo={cargo}"
            return "Sucesso", redirect_url
        elif resp.status_code == 400:
            return f"Dados inválidos: {resp.text}", dash.no_update
        elif resp.status_code == 404:
            return "Usuário não encontrado.", dash.no_update
        else:
            return f"Erro {resp.status_code}: {resp.text}", dash.no_update

    return "", dash.no_update


@dash.callback(
    Output("redirectPerfil", "href"),
    Input("redirectPerfil", "href")
)
def redirecionar(link):
    nome = request.cookies.get("user_nome")
    if not nome:
        return "/"
    return dash.no_update

@dash.callback(
    Output("urlLogout", "href"),
    Input("sair-button", "n_clicks")
)
def sairPerfil(n_clicks):
    if n_clicks>0:
        redirect_url = f"/set_user_cookie?nome={''}&email={''}&cargo={''}"
        return redirect_url
    return ''