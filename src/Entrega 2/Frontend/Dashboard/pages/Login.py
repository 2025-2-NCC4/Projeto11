import dash
from dash import html, dcc

dash.register_page(__name__, path='/')

layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H2("Login", className="login-title", style={'color':'#000000'}),  # Titulo
                html.Div(
                    children=[
                        # Input Email
                        html.Div(
                            children=[
                                html.Label("Email", htmlFor="email"),
                                dcc.Input(
                                    id="email",
                                    type="email",
                                    placeholder="Digite o seu E-mail",
                                    className="input-field"
                                ),
                            ], className="input-container"
                        ),
                        # Input Senha
                        html.Div(
                            children=[
                                html.Label("Senha", htmlFor="password"),
                                dcc.Input(
                                    id="password",
                                    type="password",
                                    placeholder="Digite a sua senha",
                                    className="input-field"
                                ),
                            ], className="input-container"
                        ),
                        # Botão login
                        html.Button("Login", id="login-button", className="login-btn"),
                        # Esqueci a senha e registrar-se
                        html.Div(
                            children=[
                                dcc.Link("Esqueceu a senha?", href="/esqueci-senha", className="link"),
                                html.Br(),
                                dcc.Link("Registrar-se", href="/Cadastro", className="link"),
                                html.Br(),
                                dcc.Link("Entrar como convidado", href="/Home", className="link"),
                            ], className="links-container"
                        ),
                        html.Div(id="login-status", className="status-message"),
                        dcc.Location(id="urlLogin", refresh=True),
                        dcc.Location(id="urlLoginLogado", refresh=True),
                        dcc.Location(id="urlAtualLogin", refresh=True),
                    ], className="form-container"
                ),
            ], className="login-card"
        ),
    ], className="page-container"
)