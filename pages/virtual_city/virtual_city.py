import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import json
import geopandas as gpd

from data_processing import process_files
from visualization import *
import sys
sys.path.append('pages/virtual_city')

dash.register_page(__name__, name ='Home', path='/virtualcity')


dropdown_category_options = [{'label':'Mode of Transport', 'value': 'mode'},
                                    {'label':'Education', 'value': 'education_category'},
                                    {'label':'Gender', 'value': 'gender'},
                                    {'label':'Age', 'value': 'age'},
                                    {'label': 'Income', 'value': 'range_income'},
                                    {'label': 'Employment', 'value': 'job_name'}]

dropdown_category_options_2 = [{'label':'Education', 'value': 'education_category'},
                                    {'label':'Gender', 'value': 'gender'},
                                    {'label':'Age', 'value': 'age'},
                                    {'label': 'Income', 'value': 'range_income'},
                                    {'label': 'Employment', 'value': 'job_name'}
                                    ]

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

layout = html.Div(
    [
        
        html.H2("Drop your Simulation Files Below"),
        html.P("You need to upload at least two files, being one the baseline and another scenario (subtripmetrics.csv)"),
        dbc.Row(
            [
                dbc.Col(
                    children=
                    [
                        dcc.Upload(
                            id='upload-data-single',
                            children=html.Div(['Drag and Drop or ',html.A('Select Files')]),
                            style={
                                'width': '100%',
                                'height': '100px',
                                'lineHeight': '100px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'backgroundColor':'silver',
                                'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'
                            },multiple=False, max_size=-1   
                        ),
                        html.Div(id="file-list-single")
                    ]
                ),
                dbc.Col(
                    children=
                    [
                        dcc.Upload(
                            id='upload-data-multiple',
                            children=html.Div(['Drop here your other Scenarios']),
                            style={
                                'width': '100%',
                                'height': '100px',
                                'lineHeight': '100px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'backgroundColor':'silver',
                                'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'
                                },multiple=True, max_size=-1
                        ),
                        html.Div(id="file-list-multiple")
                    ]
                )
            ]
        ),
        html.Br(),
        html.Div(
            style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center'},
            children=
            [
                dbc.Button("Create Report", color='primary', className="me-1", id="transform-button", n_clicks=0, style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'})
            ]
        ),
        html.Hr(),
        html.Div(html.H2("Simulation Stats", id= 'simulation-title', style={"display": "none",'textAlign': 'left'})),
        html.Br(),
        dbc.Spinner(color="primary",
                    children=
                    [
                        html.Div(id='output-message'),
                        html.Div(id='visualization_1',style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(html.Div(id='visualization_2'),style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}),
                                dbc.Col(html.Div(id='kpis'),style={'backgroundColor':'#f8f9fa','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'})
                            ]
                        )
                    ]),
        
        html.Br(),
        html.Hr(),
        html.Div(html.H2("Demographic Analysis",id= "Dropdopwn-label", style={"display": "none"}),style={'textAlign': 'left'}),
        html.Br(),
        dbc.Spinner(color='secondary',
                    children=
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Div(id='visualization_3'),style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}),
                                dbc.Col(html.Div(id='visualization_4'),style={'backgroundColor':'#f8f9fa','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}),
                            ]
                        ),
                    ]),
        html.Br(),
        dbc.Stack(id='block_filters_1',
                  children=
            [
                dbc.Col(
                    children=
                    [
                        html.Div("Choose your Category:",  style={'font-weight': 'bold'}),
                        dcc.Dropdown(
                            id='category-dropdown',
                            options=dropdown_category_options,
                            value = dropdown_category_options[0]['value'],
                            clearable=False,
                            style={"display": "none",'maxHeight': '200px', 'textAlign': 'center'})
                    ],style={'backgroundColor':'white','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}
                ),
                dbc.Col(
                    children=
                    [
                        html.Div("Select Sub Category Values:",  style={'font-weight': 'bold'}),
                        dcc.Dropdown(
                            id='subcategory-dropdown',
                            options=[],
                            value = [],
                            multi=True,
                            style={"display": "none", 'maxHeight': '300px', 'textAlign': 'center'})  
                    ],style={'backgroundColor':'white','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}
                )
            ],
               gap=3,style={"display": "none"}
        ),
        html.Br(),
        dbc.Spinner(color='success',
                    children=
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Div(id='visualization_5'),style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'})
                            ]
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(html.Div(id='visualization_6'),style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}),
                                dbc.Col(html.Div(id='visualization_7'),style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'})
                            ]
                        )
                    ]        
                    ),
        html.Br(),
        html.Hr(),
        html.Div(html.H2("Choice Analysis",id= "choice-title", style={"display": "none"}),style={'textAlign': 'left'}),
        html.Br(),
        dbc.Stack(id='block_filters_2',
                  children=
            [
                dbc.Col(
                    [
                        html.Div("Choose your Category:",  style={'font-weight': 'bold'}),
                        dcc.Dropdown(
                        id='category-dropdown-2',
                        options=dropdown_category_options_2,
                        value = dropdown_category_options_2[0]['value'],
                        clearable=False,
                        style={"display": "none",'maxHeight': '200px','textAlign': 'center'}
                )],style={'backgroundColor':'white','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}),
                
                dbc.Col(
                    [
                        html.Div("Choose your Scenario:",  style={'font-weight': 'bold'}),
                        html.Div(dcc.RadioItems(
                            id='scenario-options',
                            options=[],
                            value= 'scenario_1'))
                        ],style={'backgroundColor':'white','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'})
            ],direction="horizontal",gap=3,style={"display": "none"},
        ),
        html.Br(),
        dbc.Spinner(color='success',
                    children=
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Div(id='visualization_8'),style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'})
                            ]
                        )
                    ]),
        html.Br(),
        html.Hr(),
        html.Div(html.H2("Map Analysis",id= "map-title", style={"display": "none"}),style={'textAlign': 'center'}),
        html.Br(),
        dbc.Stack(id='block_filters_3',
                  children=
            [
                dbc.Col(
                    [
                        html.Div("Choose your Category:",  style={'font-weight': 'bold'}),
                        dcc.Dropdown(
                            id='category-dropdown-3',
                            options=dropdown_category_options,
                            value = dropdown_category_options[0]['value'],
                            clearable=False,
                            style={"display": "none"}
                            )],style={'backgroundColor':'white','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)',}),
                dbc.Col(
                    [
                        html.Div("Choose your Scenario:",  style={'font-weight': 'bold'}),
                        dcc.Dropdown(
                            id='scenario-options-2',
                            options=[],
                            value= 'baseline',
                            clearable=False,
                            style={"display": "none"}
                            )],style={'backgroundColor':'white','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}),
                dbc.Col(
                    [
                        html.Div("Select Target Zone:",  style={'font-weight': 'bold'}),
                        dcc.RadioItems(
                            id='zone-goal',
                            options= [{'label':'Destination Zone' , 'value': 'destination_taz'},
                                      {'label':'Origin Zone' , 'value': 'origin_taz'}],
                            value = 'destination_taz',
                            style={"display": "none"}
                            )],style={'backgroundColor':'white','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}),
                dbc.Col(
                    [
                        html.Div("Choose Variable:",  style={'font-weight': 'bold'}),
                        dcc.RadioItems(
                            id='variable-target',
                            options= [{'label':'Average Distance' , 'value': 'total_distance'},
                                      {'label':'Average Time' , 'value': 'travel_time'},
                                      {'label':'Count of Trips' , 'value': 'count'}],
                            value = 'travel_time',
                            style={"display": "none"}
                )],style={'backgroundColor':'white','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'})
            ],
        direction="horizontal",gap=3,style={"display": "none"},),
        html.Br(),
        dbc.Row(id='block_filters_4',
                children=
            [
                dbc.Col(
                    [
                        html.Div("Select your Category Values:",  style={'font-weight': 'bold'}),
                        dcc.Dropdown(
                            id='subcategory-dropdown-2',
                            options=[],
                            value = [],
                            multi=True,
                            style={"display": "none"})],style={'backgroundColor':'white','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'})
            ],style={"display": "none"},),
        html.Br(),
        dbc.Row(
                    children=
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Div(id='visualization_9')),
                                dbc.Col(html.Div(id='visualization_10'))
                                ]),
                        ]),
        html.Br(),
        dbc.Row(
            [
                html.H3("Individual Trips Visualization",  id ='kepler-title', style={'font-weight': 'bold', "display": "none"}),
                html.Br(),
                html.Iframe(id='kepler_map_trips', src='',height='800', width='800')
                
            ]
        ),
        ],
    className="content", style={'backgroundColor':'#f8f9fa'})




@callback(Output('kepler_map_trips', 'srcDoc'),
          Input('output-message','children'))
def kepler_map_creation(output_message):
    if output_message == " ":
        
        map_kepler = create_kepler_map()
        
        return map_kepler
    else:
        return html.Div()
        

@callback(Output('visualization_1', 'children'),
          Input('output-message','children'))
def viz_1(output_message):
    if output_message == " ":
        fig = trips_day()
        return dcc.Graph(figure=fig)
    else:
        # Return an empty div if output_message is not " "
        return html.Div()
        

@callback(Output('visualization_2', 'children'),
          Input('output-message','children'))
def viz_2(output_message):
    if output_message == " ":
        fig_2 = tour_person()
        return dcc.Graph(figure=fig_2)
    else:
        # Return an empty div if visualization_1 is None
        return html.Div()
    
@callback(Output('kpis', 'children'),
          Input('output-message','children'))
def kpi(output_message):
    if output_message == " ":
        fig_3 = indicators()
        return dcc.Graph(figure=fig_3)
    else:
        # Return an empty div if visualization_1 is None
        return html.Div()



#make dropdown and label next to it appear when the button is clicked
@callback(Output('category-dropdown', 'style'),
          Output('Dropdopwn-label', 'style'),
          Output('subcategory-dropdown', 'style'),
          Output('simulation-title', 'style'),
          Output('choice-title', 'style'),
          Output('category-dropdown-2', 'style'),
          Output('map-title', 'style'),
          Output('category-dropdown-3', 'style'),
          Output('subcategory-dropdown-2', 'style'),
          Output('zone-goal', 'style'),
          Output('variable-target', 'style'),
          Output('scenario-options-2','style'),
          Output('block_filters_1','style'),
          Output('block_filters_2','style'),
          Output('block_filters_3','style'),
          Output('block_filters_4','style'),
          Output('kepler-title','style'),
          Input('output-message','children'),
          )
def dropdown_appear(output_message):
    if output_message == " ":
        return {"display": "block"},{"display": "block"},{"display": "table"},{"display": "block"},{"display": "block"},{"display": "block"},{"display": "block"},{"display": "block"},{"display": "table"},{"display": "block"},{"display": "block"},{"display": "block"},{"display": "flex"},{"display": "flex"},{"flex": "flex"},{"display": "flex"},{"display": "block"}
    else:
        # Return an empty div if visualization_1 is None
        return {"display": "none"}, {"display": "none"}, {"display": "none"}, {"display": "none"},{"display": "none"},{"display": "none"},{"display": "none"},{"display": "none"},{"display": "none"},{"display": "none"},{"display": "none"},{"display": "none"},{"display": "none"},{"display": "none"},{"display": "none"},{"display": "none"},{"display": "none"},{"display": "none"}



@callback(Output('visualization_3', 'children'),
          Output('visualization_4', 'children'),
          Input('output-message','children'),
          Input('category-dropdown','value'))
def viz_demographic(output_message, category):
    if output_message == " ":
        fig_4 = demographic_distribution(category)
        fig_5 = demo_table(category)

        return dcc.Graph(figure=fig_4), dcc.Graph(figure=fig_5)
    else:
        # Return an empty div if visualization_1 is None
        return html.Div(), html.Div()


@callback(
    Output('subcategory-dropdown', 'options'),
    Output('subcategory-dropdown', 'value'),
    Input('category-dropdown', 'value')
)
def category_options(category):
    
    dff = options_sub_category_dropdown(category)
    
    return [{'label': c, 'value': c} for c in sorted(dff.unique())], dff.unique()
    
    
    
@callback(
    Output('subcategory-dropdown-2', 'options'),
    Output('subcategory-dropdown-2', 'value'),
    Input('category-dropdown-3', 'value')
)
def category_options(category):
    
    dff = options_sub_category_dropdown(category)
    
    return [{'label': c, 'value': c} for c in sorted(dff.unique())], dff.unique()
    

@callback(Output('visualization_5', 'children'),
          Output('visualization_6', 'children'),
          Output('visualization_7', 'children'),
          Input('output-message','children'),
          Input('category-dropdown','value'),
          Input('subcategory-dropdown','value'))
def viz_demographic_time(output_message, category, subcategory):
    if output_message == " ":
        fig_6 = demographic_distribution_time(category, subcategory)
        fig_7, fig_8 = create_diff_plot_travel_time(category, subcategory)

        return dcc.Graph(figure=fig_6), dcc.Graph(figure=fig_7), dcc.Graph(figure=fig_8)
    else:
        # Return an empty div if visualization_1 is None
        return html.Div(),html.Div(),html.Div(),
    
    
    
    


@callback(
    Output('scenario-options', 'options'),
    Output('scenario-options', 'value'),
    Input('output-message','children')   
)
def get_scenario_options(output_message):
    if output_message == " ":
        dff_radio = scenario_options_radio()
        
        return [{'label': c, 'value': c} for c in sorted(dff_radio)], dff_radio[0]


@callback(
    Output('scenario-options-2', 'options'),
    Output('scenario-options-2', 'value'),
    Input('output-message','children')   
)
def get_scenario_options(output_message):
    if output_message == " ":
        dff_radio = scenario_options_radio_2()
        
        return [{'label': c, 'value': c} for c in sorted(dff_radio)], dff_radio[0]



@callback(
    Output('visualization_8', 'children'),
    Input('output-message','children'),
    Input('category-dropdown-2','value'),
    Input('scenario-options','value'))
def create_sankey_chart(output_message, category, scenario):
    if output_message == " ":
        fig_9 = create_sankey(category, scenario)
        
        return dcc.Graph(figure=fig_9)
    else:
        return html.Div()




@callback(
    Output('visualization_9', 'children'),
    Input('output-message','children'),
    Input('category-dropdown-3','value'),
    Input('subcategory-dropdown-2','value'),
    Input('scenario-options-2','value'),
    Input('zone-goal','value'),
    Input('variable-target','value'))
def create_map_zones(output_message, category, subcategory, scenario, zone, variable):
    if output_message == " ":
        fig_10 = create_maps_time(category,subcategory, scenario, zone, variable)
        
        return dcc.Graph(id= 'map_viz',figure=fig_10, clickData={'points': [{'id': 1}]})
    else:
        return html.Div()






@callback(
    Output('visualization_10', 'children'),
    Input('output-message','children'),
    Input('category-dropdown-3','value'),
    Input('subcategory-dropdown-2','value'),
    Input('scenario-options-2','value'),
    Input('zone-goal','value'),
    Input('map_viz', 'clickData')
    )
def create_map_zones(output_message, category, subcategory, scenario, zone, zone_id):
    if output_message == " ":
        zone_id_filter = [zone_id['points'][0]['id']]
        fig_11 = create_line_chart_hover(category,subcategory,scenario,zone,zone_id_filter)
        
        return dcc.Graph(figure=fig_11)
    else:
        return html.Div()

































@callback(Output('output-message', 'children'),
          Input('transform-button', 'n_clicks'),
          [State('upload-data-multiple', 'contents'),
          State('upload-data-single', 'contents')]
)
def creating_dataframe(n_clicks, contents, single_contents):
    if n_clicks > 0:
        if contents and single_contents is not None:
            
            df = process_files(contents, single_contents)
            
            return " "
        else:
            return "Please upload a CSV file first."
    raise PreventUpdate

@callback([Output("file-list-single", "children"),Output("file-list-multiple", "children")],
          
          [Input("upload-data-single", "filename"), Input("upload-data-multiple", "filename")],
    prevent_initial_call=True,
)
def update_file_list(filename_single, filenames_multi):
    if filenames_multi:
        file_list_multi = html.Ul([html.Li(filename) for filename in filenames_multi])
    else:
        file_list_multi = html.Div("No files selected.")

    if filename_single:
        file_list_single = html.Ul([html.Li(filename_single)])
    else:
        file_list_single = html.Div("No file selected.")

    return file_list_single, file_list_multi