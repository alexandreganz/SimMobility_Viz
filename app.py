"""
This app creates an animated sidebar using the dbc.Nav component and some local
CSS. Each menu item has an icon, when the sidebar is collapsed the labels
disappear and only the icons remain. Visit www.fontawesome.com to find
alternative icons to suit your needs!

dcc.Location is used to track the current location, a callback uses the current
location to render the appropriate page content. The active prop of each
NavLink is set automatically according to the current pathname. To use this
feature you must install dash-bootstrap-components >= 0.11.0.

For more details on building multi-page Dash applications, check out the Dash
documentation: https://dash.plot.ly/urls
"""
import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import sys
import dash_uploader as du
sys.path.insert(0, 'pages/virtual_city')
sys.path.insert(0, 'pages/boston')


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, use_pages= True,external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, external_stylesheets])

du.configure_upload(app,  r"data/raw_dataframes", use_upload_id=False)

PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
sidebar = html.Div(
    [
        html.Div(
            [
                # width: 3rem ensures the logo is the exact width of the
                # collapsed sidebar (accounting for padding)
                html.Img(src=PLOTLY_LOGO, style={"width": "3rem"}),
                html.H2("Sidebar"),
            ],
            className="sidebar-header",
        ),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink(
                    [html.I(className="fas fa-home me-2"), html.Span("Home")],
                    href="/",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fa fa-car me-2"),
                        html.Span("Virtual City"),
                    ],
                    href="/virtualcity",
                    active="exact",
                ),
                dbc.NavLink(
                    [
                        html.I(className="fa fa-taxi me-2"),
                        html.Span("Boston"),
                    ],
                    href="/boston",
                    active="exact",
                ),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    className="sidebar",
)

app.layout = html.Div([dcc.Location(id="url"), 
                       sidebar, 
                       dash.page_container])


if __name__ == "__main__":
    app.run_server(debug=True, port=8051)