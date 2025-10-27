import dash
from click import style
from dash import html, dcc, Input, Output

dash.register_page(__name__, path='/Cadastro')

layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H2("Cadastro", className="login-title", style={'color':'#000000'}),  # Titulo
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
                        # Seleciona posisção
                        html.Div(
                            children=[
                                html.Label("Posição", htmlFor="position"),
                                dcc.RadioItems(
                                    id="position",
                                    options=[
                                        {'label': 'CEO', 'value': 'CEO'},
                                        {'label': 'CTO', 'value': 'CTO'},
                                        {'label': 'CFO', 'value': 'CFO'},
                                        {'label': 'Outro', 'value': 'Outro'}
                                    ],
                                    value='CEO',
                                    className="radio-items"
                                )
                            ], className="input-container", style={'display':'flex', 'flex-direction': 'column'}
                        ),
                        html.Div(
                            children=[
                                html.Label("Qual é o seu cargo?", htmlFor="other-position"),
                                dcc.Input(
                                    id="other-position",
                                    type="text",
                                    placeholder="Digite o seu cargo",
                                    className="input-field",
                                    style={"display": "none"}
                                ),
                            ], className="input-container", id="other-position-container"
                        ),
                        # Botão cadastrar
                        html.Button("Cadastrar-se", id="signup-button", className="login-btn"),

                        # Mensagem de status
                        html.Div(id="signup-status", className="status-message"),

                        #Redireciona após cadastro
                        dcc.Location(id="urlCadastro", refresh=True),
                        dcc.Location(id="urlCadastroLogado", refresh=True),
                        dcc.Location(id="urlAtualCadastro", refresh=True),
                        # Voltar
                        html.Div(
                            children=[
                                dcc.Link("Voltar", href="/", className="link"),
                            ], className="links-container"
                        ),
                    ], className="form-container",
                ),
            ], className="login-card"
        ),
    ], className="page-container"
)