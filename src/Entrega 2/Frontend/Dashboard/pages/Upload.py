import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import base64
import io
import pandas as pd
from flask import request

dash.register_page(__name__, path='/Upload')

layout = html.Div([
    html.Div(id="drag-and-drop-container", children=[
        html.H1('Upload CSV File', style={'text-align': 'center'}),
        dcc.Upload(
            id='upload-data',
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select a File')
            ]),
            style={
                'width': '80%',
                'height': '300px',
                'lineHeight': '300px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'margin': '20px auto',
                'backgroundColor': '#f8f8f8',
                'fontSize': '18px'
            },
            accept='.csv'
        ),
        dcc.Location(id="redirectUpload", refresh=True)
    ], className='Pagina', style={'width':'200vh', 'height':'100vh'}),

    html.Div(id="uploaded-layout", style={'display': 'none'}, children=[
        html.Div(id='output-data-upload', style={'color': '#ffffff'}),
        html.Button('Go Back', id='go-back-button', n_clicks=0, style={
                'background-color': '#0078D7',
                'color': 'white',
                'padding': '10px 20px',
                'border': 'none',
                'border-radius': '6px',
                'cursor': 'pointer',
                'font-weight': '500',
                'margin-left':'40px',
                'margin-bottom':'20px'
            })
    ])
])

@dash.callback(
    Output("redirectUpload", "href"),
    Input("redirectUpload", "href")
)
def redirecionar(link):
    nome = request.cookies.get("user_nome")
    if not nome:
        return "/"
    return dash.no_update



