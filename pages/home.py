import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, name ='Home', path='/')

layout = html.Div(
    [
        dbc.Row(dbc.Col(html.H1("Welcome to SimMobility Visualization"))),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.H2("Purpose"),
                            html.Div("The under-construction SimMobility visualization tool developed by DTU Transport Department aims to enhance the analysis and interpretation of simulation data generated by the SimMobility platform. It holds promise for providing valuable insights to researchers and practitioners in the field of urban mobility, contributing to improved transportation planning and optimization in urban environments.")
                        ]
                    )
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.H2("How to Use"),
                            dcc.Markdown(
                                """
                                Below you will see an example of how to use the tool. The main focus is to optimize the data analysis of your simulation. In this case remember to have the csv version of the file called subtrip_metrics. In case you have any doubts, you can check [here](https://github.com/smart-fm/simmobility-prod/wiki/Mid-Term-Output)
                                the output files of the Mid Day process.
                                Currently the tool is configured to only view Mid Day data, specifically submetrics, however we will be working to expand the analysis to other generated files.
                                """)
                        ]
                    )
                )
            ]
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.H2("Available Simulated Locations"),
                            html.Div(
                                [
                                    html.P("SimMobility Visualization is currently available for the following simulated locations:"),
                                    dcc.Markdown(
                                        """
                                        - Virtual City &#x2714
                                        - Boston &#x2714
                                        - Singapore &#x2718
                                        - Copenhagen (under development) &#x2718
                                        """
                                    )
                                ]
                                
                            )
                        ]
                    )
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.H2("Outputs Available to Visualize:"),
                            html.P("SimMobility has several output files generated by each simulation, so far the files that are fully functional are:"),
                            dcc.Markdown(
                                """
                                - subtrip_metrics.csv &#x2714
                                - das_trip.csv &#x2718
                                """
                            )
                        ]
                    )
                )
            ]
        )
        
        
        
        
        
        
        
        
    ], className="content")