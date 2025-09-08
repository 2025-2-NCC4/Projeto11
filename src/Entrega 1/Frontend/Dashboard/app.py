import dash
from dash import Dash, html, dcc

app = Dash(__name__, use_pages=True)

app.layout = html.Div([

    html.Div([
        html.Img(src='assets/piclogo.png', className="PicLogo"),
        html.H1('Dashboard Interativa PicMoney'),
        *[
        html.Div(
            dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"], className="button-link")
        ) for page in dash.page_registry.values()
        ]
    ], className="MainHeader"),
    dash.page_container
], className="DashboardPag")

if __name__ == '__main__':
    app.run(debug=True)