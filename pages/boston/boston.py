import dash
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import dash_uploader as du
import json
import geopandas as gpd
import os

from data_processing_boston import concat_csv_to_dataframe
from visualization_boston import *
import sys
sys.path.append('pages/boston')

dash.register_page(__name__, name ='Boston', path='/boston')


dropdown_category_options_boston = [{'label':'Mode of Transport', 'value': 'mode'},
                                    {'label':'Education', 'value': 'education_category'},
                                    {'label':'Gender', 'value': 'gender_category'},
                                    {'label':'Age', 'value': 'age_category'},
                                    {'label': 'Income', 'value': 'income_category'},
                                    {'label': 'Employment Category', 'value': 'employment_category'},]


dropdown_category_options_2_boston = [{'label':'Education', 'value': 'education_category'},
                                    {'label':'Gender', 'value': 'gender_category'},
                                    {'label':'Age', 'value': 'age_category'},
                                    {'label': 'Income', 'value': 'income_category'},
                                    {'label': 'Employment Category', 'value': 'employment_category'}]


styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

# 2) Use the Upload component
layout = html.Div(
    [
        html.H2("Drop your Simulation Files Below"),
        html.P("You need to upload at least two files, being one the baseline and another scenario (subtripmetrics.csv)"),
        du.Upload(text='Drag and Drop Here to upload!',
                  id='dash-uploader',
                  cancel_button=True,
                  pause_button=False,
                  max_file_size=50000,
                  max_files=2
                  ),
        html.Br(),
        dbc.Button("Create Report", color='primary', className="me-1", id="transform-button-boston", n_clicks=0, style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}),
        html.Br(),
        html.Hr(),

        dbc.Spinner(
            color="primary",
            children=
            [
                html.Div(id='output-message-boston'),
                html.Div(id='visualization_1_boston',style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(html.Div(id='visualization_2_boston',style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'})),
                        dbc.Col(html.Div(id='visualization_3_boston',style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}))
                    ]
                ),
                html.Br(),
                html.Hr(),
                html.Div(html.H2("Demographic Analysis",id= "Dropdopwn-label"),style={'textAlign': 'left'}),
                html.Br(),
            ]
        ),
        dbc.Spinner(color='secondary',
                    children=
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Div(id='visualization_4_boston'),style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}),
                                dbc.Col(html.Div(id='visualization_5_boston'),style={'backgroundColor':'#f8f9fa','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}),
                            ]
                        )
                    ]
        ),
        html.Br(),
        dbc.Stack(id='block_filters_1',
                  children=
                  [
                      dbc.Col(
                          children=
                          [
                              html.Div("Choose your Category:",  style={'font-weight': 'bold'}),
                              dcc.Dropdown(
                                  id='category-dropdown-boston',
                                  options=dropdown_category_options_boston,
                                  value = dropdown_category_options_boston[0]['value'],
                                  clearable=False,
                              )
                          ]
                      ),
                      dbc.Col(
                          children=
                          [
                              html.Div("Select Sub Category Values:",  style={'font-weight': 'bold'}),
                              dcc.Dropdown(
                                  id='subcategory-dropdown-boston',
                                options=[],
                                value = [],
                                multi=True,
                                style={'maxHeight': '300px', 'textAlign': 'center'})  
                              ],style={'backgroundColor':'white','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}
                          )
                  ], gap=3),
        html.Br(),
        dbc.Spinner(color='success',
                    children=
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Div(id='visualization_6_boston'),style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'})
                            ]
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Col(html.Div(id='visualization_7_boston'),style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}),
                                dbc.Col(html.Div(id='visualization_8_boston'),style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'})
                            ]
                        )
                    ]),
        html.Br(),
        html.Hr(),
        html.Div(html.H2("Choice Analysis",id= "choice-title"),style={'textAlign': 'left'}),
        html.Br(),
        dbc.Stack(id='block_filters_2',
                  children=
                  [
                      dbc.Col(
                          [
                              html.Div("Choose your Category:",  style={'font-weight': 'bold'}),
                               dcc.Dropdown(
                                   id='category-dropdown-2-boston',
                                   options=dropdown_category_options_2_boston,
                                   value = dropdown_category_options_2_boston[0]['value'],
                                   clearable=False,
                               )
                          ]
                      ),
                      dbc.Col(
                          [
                              html.Div("Choose your Scenario:",  style={'font-weight': 'bold'}),
                              html.Div(dcc.RadioItems(
                                  id='scenario-options-boston',
                                  options=[{'label':'Scenario 1', 'value': 'scenario_1', 'disabled': True},
                                          {'label':'Scenario 2', 'value': 'scenario_2', 'disabled': True}],
                                  value= 'scenario_1'
                              ))
                          ]
                      )
                  ],direction="horizontal",gap=3),
        html.Br(),
        dbc.Spinner(color='success',
                    children=
                    [
                        dbc.Row(
                            [
                                dbc.Col(html.Div(id='visualization_9_boston'),style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'})
                            ]
                        )
                    ]),
        html.Br(),
        html.Hr(),
        html.Div(html.H2("Map Analysis",id= "map-title"),style={'textAlign': 'center'}),
        html.Br(),
        dbc.Stack(id='block_filters_3',
                   children=
                   [
                       dbc.Col(
                           [
                               html.Div("Choose your Category:",  style={'font-weight': 'bold'}),
                               dcc.Dropdown(
                                   id='category-dropdown-3-boston',
                                   options=dropdown_category_options_boston,
                                    value = dropdown_category_options_boston[0]['value'],
                                    clearable=False,
                                    )],style={'backgroundColor':'white','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)',}),
                       
                       dbc.Col(
                           [
                               html.Div("Choose your Scenario:",  style={'font-weight': 'bold'}),
                               dcc.Dropdown(
                                   id='scenario-options-2-boston',
                                   options=[{'label':'Scenario 1', 'value': 'scenario_1' },
                                          {'label':'Scenario 2', 'value': 'scenario_2'}],
                                   value= 'scenario_1',
                                   clearable=False)],style={'backgroundColor':'white','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}),
                       
                       dbc.Col(
                           [
                               html.Div("Select Target Zone:",  style={'font-weight': 'bold'}),
                               dcc.RadioItems(id='zone-goal-boston',
                                              options= [{'label':'Destination Zone' , 'value': 'destination_taz'},
                                                        {'label':'Origin Zone' , 'value': 'origin_taz'}],
                                              value = 'destination_taz')],style={'backgroundColor':'white','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}),
                       dbc.Col(
                           [
                               html.Div("Choose Variable:",  style={'font-weight': 'bold'}),
                               dcc.RadioItems(
                                   id='variable-target-boston',
                                   options= [{'label':'Average Distance (meters)' , 'value': 'total_dist'},
                                             {'label':'Average Time (minutes)' , 'value': 'travel_time'},
                                             {'label':'Count of Trips' , 'value': 'count'}],
                                   value = 'travel_time',
                                   )],style={'backgroundColor':'white','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'})
                   ],direction="horizontal",gap=3
                  ),
        html.Br(),
        dbc.Row(id='block_filters_4',
                children=
                [
                    dbc.Col(
                        [
                            html.Div("Select your Category Values:",  style={'font-weight': 'bold'}),
                            dcc.Dropdown(
                                id='subcategory-dropdown-2-boston',
                                options=[],
                                value = [],
                                multi=True,
                            )
                        ],style={'backgroundColor':'white','box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'},
                    )
                    ]),
        html.Br(),
        dbc.Row(
            children=
            [
                dbc.Row(
                    children=
                    [
                        dbc.Col(dbc.Spinner(html.Div(id='visualization_10_boston'))),
                        dbc.Col(html.Div(id='visualization_11_boston')),
                    ]
                )   
            ]
        ),
        html.Br(),
        dbc.Button("Generate Maps", color='primary', className="me-1", id="kepler-button", n_clicks=0, style ={'box-shadow': '2px 2px 5px rgba(0, 0, 0, 0.3)'}),
        html.Br(),
        dbc.Spinner(children=
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    children=
                                    [
                                        html.H3("Map Delta Travel Distance",  style={'font-weight': 'bold'}),
                                        html.Br(),
                                        html.Iframe(id='kepler_map_trips_boston_time', src='',height='600', width='650')
                                    ]
                                        ),
                                dbc.Col(
                                    [
                                        html.H3("Map Delta Travel Time",  style={'font-weight': 'bold'}),
                                        html.Br(),
                                    html.Iframe(id='kepler_map_trips_boston_distance', src='',height='600', width='650')])
                                
                            ]
                        )
                    ]
        )
                    
        
        
        
        
        
],className="content",)



@callback(
    Output('subcategory-dropdown-boston', 'options'),
    Output('subcategory-dropdown-boston', 'value'),
    Input('category-dropdown-boston', 'value')
)
def category_options(category):
    
    dff = options_sub_category_dropdown(category)
    
    return [{'label': c, 'value': c} for c in sorted(dff)], dff

@callback(
    Output('subcategory-dropdown-2-boston', 'options'),
    Output('subcategory-dropdown-2-boston', 'value'),
    Input('category-dropdown-3-boston', 'value')
)
def category_options(category):
    
    dff = options_sub_category_dropdown(category)
    
    return [{'label': c, 'value': c} for c in sorted(dff)], dff




@callback(Output('visualization_1_boston', 'children'),
          Input('output-message-boston','children'))
def viz_1(output_message):
    if output_message == " ":
        fig = trips_day()
        return dcc.Graph(figure=fig)
    else:
        # Return an empty div if output_message is not " "
        return html.Div()



@callback(Output('visualization_2_boston', 'children'),
          Input('output-message-boston','children'))
def viz_2(output_message):
    if output_message == " ":
        fig = tour_person()
        return dcc.Graph(figure=fig)
    else:
        # Return an empty div if output_message is not " "
        return html.Div()




@callback(Output('visualization_3_boston', 'children'),
          Input('output-message-boston','children'))
def viz_2(output_message):
    if output_message == " ":
        fig = indicators()
        return dcc.Graph(figure=fig)
    else:
        # Return an empty div if output_message is not " "
        return html.Div()


@callback(Output('visualization_4_boston', 'children'),
          Output('visualization_5_boston', 'children'),
          Input('output-message-boston','children'),
          Input('category-dropdown-boston','value'))
def viz_demographic(output_message, category):
    if output_message == " ":
        fig_4 = demographic_distribution(category)
        fig_5 = demo_table(category)

        return dcc.Graph(figure=fig_4), dcc.Graph(figure=fig_5)
    else:
        # Return an empty div if visualization_1 is None
        return html.Div(), html.Div()




@callback(Output('visualization_6_boston', 'children'),
          Output('visualization_7_boston', 'children'),
          Output('visualization_8_boston', 'children'),
          Input('output-message-boston','children'),
          Input('category-dropdown-boston','value'),
          Input('subcategory-dropdown-boston','value'))
def viz_demographic_time(output_message, category, subcategory):
    if output_message == " ":
        fig_6 = demographic_distribution_time(category, subcategory)
        fig_7= create_diff_plot_travel_time(category, subcategory)
        fig_8= create_diff_plot_travel_distance(category, subcategory)

        return dcc.Graph(figure=fig_6), dcc.Graph(figure=fig_7), dcc.Graph(figure=fig_8)
    else:
        # Return an empty div if visualization_1 is None
        return html.Div(),html.Div(),html.Div(),



@callback(
    Output('visualization_9_boston', 'children'),
    Input('output-message-boston','children'),
    Input('category-dropdown-2-boston','value'))
def create_sankey_chart(output_message, category):
    if output_message == " ":
        fig_9 = create_sankey_boston(category)
        
        return dcc.Graph(figure=fig_9)
    else:
        return html.Div()
    
    
@callback(
    Output('visualization_10_boston', 'children'),
    Input('output-message-boston','children'),
    Input('category-dropdown-3-boston','value'),
    Input('subcategory-dropdown-2-boston','value'),
    Input('scenario-options-2-boston','value'),
    Input('zone-goal-boston','value'),
    Input('variable-target-boston','value'))
def create_map_zones(output_message, category, subcategory, scenario, zone, variable):
    if output_message == " ":
        scenario = [scenario]
        
        fig_10 = create_maps_time(category,subcategory, scenario, zone, variable)
        
        return dcc.Graph(id= 'map_viz_boston', figure=fig_10, clickData={'points': [{'location': 1}]})
    else:
        return html.Div()
    

    
@callback(
    Output('visualization_11_boston', 'children'),
    Input('output-message-boston','children'),
    Input('category-dropdown-3-boston','value'),
    Input('subcategory-dropdown-2-boston','value'),
    Input('scenario-options-2-boston','value'),
    Input('zone-goal-boston','value'),
    Input('map_viz_boston', 'clickData')
    )
def create_map_zones(output_message, category, subcategory, scenario, zone, zone_id):
    if output_message == " ":
        zone_id_filter = [int(point['location']) for point in zone_id['points']]
        scenario = [scenario]
        fig_11 = create_line_chart_hover(category,subcategory,scenario,zone,zone_id_filter)
        
        return dcc.Graph(figure=fig_11)
    else:
        return html.Div()











@callback(Output('kepler_map_trips_boston_time', 'srcDoc'),
          [Input('kepler-button', 'n_clicks')],
          prevent_initial_call=True)
def button_click_kepler(n_clicks):
    if n_clicks > 0:
        url = 'data/shp_files/boston/zones.json'
        country_gdf = gpd.read_file(url)
        df = pl.read_csv('/Users/alexandremuchinski/Desktop/Thesis-Alex/data/processed_dataframes/boston/boston_runs.csv', infer_schema_length=10000,ignore_errors=True, null_values=['Green-C1/Green-D-Reservoir17/Green-E1/'])
        df = df.groupby(['destination_taz','scenario_label']).agg(mean=pl.col('travel_time').round(2).mean()).to_pandas()
        pivot_df = df.pivot_table(index='destination_taz', columns='scenario_label', values='mean', aggfunc='sum').reset_index()
        pivot_df['diff_distance'] = ((pivot_df['scenario_2'] / pivot_df['scenario_1'])-1)*100
        
        pivot_df = pd.merge(pivot_df, country_gdf, left_on='destination_taz', right_on=country_gdf.index , how='inner')
        pivot_df = gpd.GeoDataFrame(pivot_df, geometry='geometry')
        
        boston_time_map =  KeplerGl()
        boston_time_map.add_data(data=pivot_df, name="Trips")
        boston_time_map.save_to_html(file_name="map_kepler_time_boston.html")
        
        with open('map_kepler_time_boston.html', 'r') as f:
            kepler_html_boston_time = f.read()
        
        return kepler_html_boston_time
    else:
        return html.Div()



@callback(Output('kepler_map_trips_boston_distance', 'srcDoc'),
          [Input('kepler-button', 'n_clicks')],
          prevent_initial_call=True)
def button_click_kepler(n_clicks):
    if n_clicks > 0:
        url = 'data/shp_files/boston/zones.json'
        country_gdf = gpd.read_file(url)
        df = pl.read_csv('/Users/alexandremuchinski/Desktop/Thesis-Alex/data/processed_dataframes/boston/boston_runs.csv', infer_schema_length=10000,ignore_errors=True, null_values=['Green-C1/Green-D-Reservoir17/Green-E1/'])
        df = df.groupby(['destination_taz','scenario_label']).agg(mean=pl.col('total_dist').round(2).mean()).to_pandas()
        pivot_df = df.pivot_table(index='destination_taz', columns='scenario_label', values='mean', aggfunc='sum').reset_index()
        pivot_df['diff_distance'] = ((pivot_df['scenario_2'] / pivot_df['scenario_1'])-1)*100
        
        pivot_df = pd.merge(pivot_df, country_gdf, left_on='destination_taz', right_on=country_gdf.index , how='inner')
        pivot_df = gpd.GeoDataFrame(pivot_df, geometry='geometry')
        
        boston_time_map =  KeplerGl()
        boston_time_map.add_data(data=pivot_df, name="Trips")
        boston_time_map.save_to_html(file_name="map_kepler_distance_boston.html")
        
        with open('map_kepler_distance_boston.html', 'r') as f:
            kepler_html_boston_distance = f.read()
        
        return kepler_html_boston_distance
    else:
        return html.Div()








    
    
folder_path = 'data/raw_dataframes'
# Define the callback function
@callback(
    Output('output-message-boston', 'children'),
    [Input('transform-button-boston', 'n_clicks')],
    prevent_initial_call=True
)
def check_folder_files(n_clicks):
    if n_clicks is None:
        return None
# Get a list of all files in the folder
    folder_path = 'data/raw_dataframes'
    current_directory = os.getcwd()
    files_in_folder = os.listdir(folder_path)
    file_paths = [os.path.relpath(os.path.join(folder_path, file), current_directory) for file in files_in_folder if os.path.isfile(os.path.join(folder_path, file))]
    df = concat_csv_to_dataframe(file_paths)
    if not files_in_folder:
        return "Fail message: No files found in the folder."
    return " "



       
       