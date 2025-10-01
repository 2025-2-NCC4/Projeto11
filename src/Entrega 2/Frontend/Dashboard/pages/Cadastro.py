import dash
from dash import html, dcc


dash.register_page(__name__, path='/Cadastro')

layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H2("Cadastro", className="login-title"),  # Titulo
                html.Div(
                    children=[
                        # Input Nome
                        html.Div(
                            children=[
                                html.Label("Nome", htmlFor="name"),
                                dcc.Input(
                                    id="nome",
                                    type="text",
                                    placeholder="Digite o seu primeiro nome",
                                    className="input-field"
                                ),
                            ], className="input-container"
                        ),
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
                        # Botão cadastrar
                        html.Button("Cadastrar-se", id="signup-button", className="login-btn"),

                        # Mesagem de status
                        html.Div(id="signup-status", className="status-message"),
                        #Voltar
                        html.Div(
                            children=[
                                dcc.Link("Voltar", href="/", className="link"),
                            ], className="links-container"
                        ),
                    ], className="form-container"
                ),
            ], className="login-card"
        ),
    ], className="page-container"
)