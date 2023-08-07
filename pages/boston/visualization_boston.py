import pandas as pd
import polars as pl
import geopandas as gpd
import plotly.express as px
from datetime import datetime
import plotly.graph_objects as go
import numpy as np
from keplergl import KeplerGl

def trips_day():
    selected_columns = ['scenario_label', 'time_range']
    df = pl.read_csv('data/processed_dataframes/boston/boston_runs.csv', columns = selected_columns, infer_schema_length=10000,ignore_errors=True, null_values=['Green-C1/Green-D-Reservoir17/Green-E1/'])
    
    # Group the dataframe 'df' by 'scenario_label' and 'time_range', and count the occurrences in each group.
    trip_group =  df.groupby(['scenario_label','time_range']).agg(pl.count())
    
    # Sort the grouped dataframe by the 'time_range' column.
    sorted_df = trip_group.sort('time_range')
    
    # Convert the sorted dataframe back to a pandas DataFrame.
    sorted_df = sorted_df.to_pandas()

    # Group the sorted DataFrame by 'scenario_label', calculate the total count for each group, and broadcast it back to each row.
    category_total = sorted_df.groupby('scenario_label')['count'].transform('sum')

    # Calculate the percentage of each count relative to the total count for its corresponding 'scenario_label'.
    sorted_df['percentage'] = (sorted_df['count'] / category_total * 100).round(2)
    
    sorted_df['time_range'] = sorted_df['time_range'].astype('str')
    sorted_df['time_range'] = sorted_df['time_range'].str[11:16]
    sorted_df['time_range'] = pd.to_datetime(sorted_df['time_range'], format='%H:%M')
    sorted_df = sorted_df.sort_values(by='time_range')
    sorted_df['time_range'] = sorted_df['time_range'].dt.strftime('%H:%M')
    

    fig = px.histogram(sorted_df, 
                x='time_range', 
                y='percentage', 
                color='scenario_label',
                barmode='overlay',
                hover_data={'count'},
                labels = {'time_range': 'Time of Day (30 min time intervals)', 
                        'percentage': 'Percentage (%)', 
                        'scenario_label' : 'Scenario'},
                color_discrete_sequence=px.colors.qualitative.Alphabet)

    fig.update_layout(
            title_text='Trips by Time of Day',
            title_x=0.5,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1))
    fig.update_layout(yaxis_ticksuffix = "%")
    
    return fig


# Second Visualization
def tour_person():
    
    selected_columns = ['person_id', 'scenario_label']
    df = pl.read_csv('data/processed_dataframes/boston/boston_runs.csv', columns = selected_columns, infer_schema_length=10000,ignore_errors=True, null_values=['Green-C1/Green-D-Reservoir17/Green-E1/'])
    number_tours =  df.groupby(['person_id','scenario_label']).agg(pl.count())
    number_tours = number_tours.to_pandas()
    # Replace values greater than 4 with '+4 trips' in a new column 'trip_count'
    number_tours['trip_count'] = pd.cut(number_tours['count'], bins=[1, 2, 3, 4, 5,6,7,8,float('inf')],
                                    labels=['1', '2', '3', '4', '5','6','7','+8 trips'], right=False)
    number_tours = number_tours.groupby(['scenario_label', 'trip_count'])['count'].sum().reset_index()

    # Define the order of the 'trip_count' categories
    category_order = ['1', '2', '3', '4', '5','6','7', '+8 trips']

    # Convert 'trip_count' to categorical with the defined order
    number_tours['trip_count'] = pd.Categorical(number_tours['trip_count'], category_order)

    # Sort the DataFrame based on the categorical order
    number_tours = number_tours.sort_values('trip_count')

    # Calculate the total population count
    total_tours = number_tours.groupby('scenario_label')['count'].transform('sum')


    # Calculate the total population count
    number_tours['percentage'] = ((number_tours['count'] / total_tours) * 100).round(2)


    fig = px.bar(number_tours, 
                x='trip_count', 
                y='percentage', 
                color='scenario_label',
                barmode='group',
                hover_data={'count'},
                labels = { 'percentage': 'Percentage (%)', 
                        'scenario_label' : 'Scenario',
                        'trip_count': 'Number of Tours'},
                color_discrete_sequence=px.colors.qualitative.Alphabet)

    fig.update_layout(
            title_text='Number of Tours per Person',
            title_x=0.5,
            showlegend=False)
    fig.update_layout(yaxis_ticksuffix = "%")

    return fig


# Third Visualization
def indicators():
    # Third Visualization
    columns_read = ['scenario_label', 'travel_time','total_dist']

    # Assuming 'trip_group' is a DataFrame containing the necessary data
    df = pl.read_csv('data/processed_dataframes/boston/boston_runs.csv', columns = columns_read, infer_schema_length=10000,ignore_errors=True, null_values=['Green-C1/Green-D-Reservoir17/Green-E1/'])

    # Create the go.Indicator plot
    fig = go.Figure()

    # Calculate the total number of trips for each scenario
    sum_trips = df.groupby('scenario_label').agg(pl.count()).to_pandas()
    sum_trips = sum_trips.groupby('scenario_label')['count'].mean().round(2)

    # Calculate the average travel time for each scenario
    average_travel_times = df.groupby('scenario_label').agg(travel_time=pl.col('travel_time').mean()).to_pandas()
    average_travel_times['travel_time'] = average_travel_times['travel_time'].round(2)
    average_travel_times = average_travel_times.groupby('scenario_label')['travel_time'].mean().round(2)

    # Calculate the average travel distance for each scenario

    average_travel_distances = df.groupby('scenario_label').agg(total_dist=pl.col('total_dist').mean()).to_pandas()
    average_travel_distances['total_dist'] = average_travel_distances['total_dist'].round(2)
    average_travel_distances = average_travel_distances.groupby('scenario_label')['total_dist'].mean().round(2)

    # Calculate the standard deviation of travel time for each scenario

    std_travel_times = df.groupby('scenario_label').agg(travel_time=pl.col('travel_time').std()).to_pandas()
    std_travel_times['travel_time'] = std_travel_times['travel_time'].round(2)
    std_travel_times = std_travel_times.groupby('scenario_label')['travel_time'].mean().round(2)

    # Create a list of scenario numbers
    scenario_numbers = average_travel_times.index

    # Define the horizontal spacing for the indicators based on the number of scenarios
    x_spacing = 1.0 / len(average_travel_times)

    # Define the vertical spacing for the time indicators
    time_indicator_y = 0.5

    # Loop through each scenario and add a trace dynamically for the travel time with the specified position
    for i, (scenario, trips) in enumerate(sum_trips.items()):
        position = {'x': [i * x_spacing, (i + 1) * x_spacing], 'y': [time_indicator_y, 0.95]}
        fig.add_trace(
            go.Indicator(
                mode='number',
                value=trips,
                title_text=f'<b>{scenario_numbers[i]}</b><br>Number of Trips',  # Title with scenario number and indicator name
                domain=position,
                # Customize the font
                title_font=dict(size=20),
                number_font=dict(size=25)
            )
        )

    # Define the vertical spacing for the distance indicators
    distance_indicator_y = 0.45

    # Loop through each scenario and add a trace dynamically for the travel distance with the specified position
    for i, (scenario, avg_time) in enumerate(average_travel_times.items()):
        position = {'x': [i * x_spacing, (i + 1) * x_spacing], 'y': [distance_indicator_y, 0.5]}
        fig.add_trace(
            go.Indicator(
                mode='number',
                value=avg_time,
                title_text=f'Avg Travel Time',  # Title with scenario number and indicator name
                domain=position,
                # Customize the font
                title_font=dict(size=13),
                number_font=dict(size=15)
            )
        )

    # Define the vertical spacing for the third set of indicators (e.g., average cost)
    cost_indicator_y = 0.3

    # Loop through each scenario and add a trace dynamically for the third indicator with the specified position
    for i, (scenario, avg_std) in enumerate(std_travel_times.items()):
        position = {'x': [i * x_spacing, (i + 1) * x_spacing], 'y': [cost_indicator_y, 0.35]}
        fig.add_trace(
            go.Indicator(
                mode='number',
                value=avg_std,
                title_text=f'Std Travel Time',  # Title with scenario number and indicator name
                domain=position,
                # Customize the font
                title_font=dict(size=13),
                number_font=dict(size=15)
            )
        )

    # Define the vertical spacing for the fourth set of indicators (e.g., standard deviation of travel time)
    std_indicator_y = 0.15

    # Loop through each scenario and add a trace dynamically for the fourth indicator with the specified position
    for i, (scenario, avg_distance) in enumerate(average_travel_distances.items()):
        position = {'x': [i * x_spacing, (i + 1) * x_spacing], 'y': [std_indicator_y, 0.2]}
        fig.add_trace(
            go.Indicator(
                mode='number',
                value=avg_distance,
                title_text=f'Avg Travel Distance',  # Title with indicator name
                domain=position,
                # Customize the font
                title_font=dict(size=13),
                number_font=dict(size=15)
            )
        )

    # Update the layout of the plot
    fig.update_layout(
        title=dict(
            x=0.5,
            y=0.95,
            font=dict(size=20)
        ),
        margin={'l': 0,'t':0, 'r': 0},
        plot_bgcolor='rgba(0,0,0,0)',    # Set the plot background color to transparent
        paper_bgcolor='rgba(0,0,0,0)',    # Set the paper (entire plot) background color to transparent
    )

    return fig



#Fourth Visualization
def demographic_distribution(category):
    # Assuming 'trip_group' is a DataFrame containing the necessary data
    
    columns_read = ['scenario_label',category]

    # Assuming 'trip_group' is a DataFrame containing the necessary data
    df = pl.read_csv('data/processed_dataframes/boston/boston_runs.csv', columns = columns_read, infer_schema_length=10000,ignore_errors=True, null_values=['Green-C1/Green-D-Reservoir17/Green-E1/'])

    
    

    # Step 1: Calculate the sum of 'count' for each combination of 'label' and 'mode'
    mode_shares = df.groupby(['scenario_label', category]).agg(pl.count().alias('count')).to_pandas()
    
    
    

    # Step 2: Calculate the total population count for each 'label'
    total_mode = mode_shares.groupby('scenario_label')['count'].transform('sum')

    # Step 3: Calculate the percentage of each mode count relative to the total count for the corresponding 'label'
    mode_shares['Percentage'] = ((mode_shares['count'] / total_mode) * 100).round(2)

    # Step 4: Create the plot using plotly express bar chart
    if category == 'range_income':
        # Category order for 'range_income'
        category_order = ['No Income', '$1-$1000', '$1001-$1499', '$1500-$1999', '$2000-$2499', '$2500-$2999',
                          '$3000-$3999', '$4000-$4999', '$5000-$5999', '$6000-$6999', '$7000-$7999', '$8000 and above']
        mode_shares[category] = pd.Categorical(mode_shares[category], categories=category_order, ordered=True)
        mode_shares = mode_shares.sort_values(category)
        
    elif category == 'age':
        # Category order for 'age'
        category_order = ['0-3 yrs old', '4-9yrs old', '10-14 yrs old', '15-19 yrs old', '20-24 yrs old', '25-29 yrs old',
                          '30-34 yrs old', '35-39  yrs old', '40-44 yrs old', '45-49  yrs old', '50-54 yrs old',
                          '55-59  yrs old', '60-64 yrs old', '65-69 yrs old', '70-74  yrs old', '75-79 yrs old',
                          '80-84 yrs old', '85+']
        
        mode_shares[category] = pd.Categorical(mode_shares[category], categories=category_order, ordered=True)
        mode_shares = mode_shares.sort_values(category)
    else:
        # Sort the values by the 'count' column in descending order
        mode_shares = mode_shares.sort_values(by='count', ascending=False)

    fig = px.bar(
        mode_shares,
        x=category,
        y='Percentage',
        color='scenario_label',
        labels={'mode': 'Mode of Transport', 
                'Percentage': 'Percentage (%)',
                'range_income':'Income Level',
                'age': 'Age Level',
                'education_category':'Level of Education',
                'gender':'Gender',
                'scenario_label':'Scenario'},
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Alphabet,
        template='plotly',
        # Set the category order for the plot for 'range_income' and 'age', or None for other cases
    )

    # Get the adjusted title from the labels dictionary
    adjusted_title = f'Distribution Across {fig.layout.xaxis.title.text}'
    # Update the layout with the adjusted title
    fig.update_layout(title_text=adjusted_title, title_font_size=20, title_x=0.5,)

    # Step 7: Display the y-axis ticks with a percentage symbol
    fig.update_layout(yaxis_ticksuffix="%",
                      legend=dict(
                          orientation="h",
                          yanchor="bottom",
                          y=1.02,
                          xanchor="right",
                          x=1),
                      showlegend=False
                      )
    
    
    return fig


def demo_table(category):
    columns_read = ['scenario_label',category]

    # Assuming 'trip_group' is a DataFrame containing the necessary data
    df = pl.read_csv('data/processed_dataframes/boston/boston_runs.csv', columns = columns_read, infer_schema_length=10000,ignore_errors=True, null_values=['Green-C1/Green-D-Reservoir17/Green-E1/'])

    
    
    # Step 1: Calculate the sum of 'count' for each combination of 'label' and 'mode'
    mode_shares = df.groupby(['scenario_label', category]).agg(pl.count().alias('count')).to_pandas()

    # Step 2: Calculate the total population count for each 'label'
    total_mode = mode_shares.groupby('scenario_label')['count'].transform('sum')

    # Step 3: Calculate the percentage of each mode count relative to the total count for the corresponding 'label'
    mode_shares['Percentage'] = ((mode_shares['count'] / total_mode) * 100).round(2)

    # Pivot the data to create the mode_table using the 'mode' and 'label' columns, summing the 'count' and 'Percentage' values
    mode_table = mode_shares.pivot_table(values=['count', 'Percentage'], index=category, columns='scenario_label', aggfunc='sum', margins=True, margins_name='Total').reset_index()

    # Sort the DataFrame by the custom order based on 'category'
    if category == 'range_income':
        category_order = ['No Income', '$1-$1000', '$1001-$1499', '$1500-$1999', '$2000-$2499', '$2500-$2999',
                          '$3000-$3999', '$4000-$4999', '$5000-$5999', '$6000-$6999', '$7000-$7999', '$8000 and above', 'Total']
        mode_table[category] = pd.Categorical(mode_table[category], categories=category_order, ordered=True)
        mode_table = mode_table.sort_values(category)
    elif category == 'age':
        category_order = ['0-3 yrs old', '4-9yrs old', '10-14 yrs old', '15-19 yrs old', '20-24 yrs old', '25-29 yrs old',
                          '30-34 yrs old', '35-39  yrs old', '40-44 yrs old', '45-49  yrs old', '50-54 yrs old',
                          '55-59  yrs old', '60-64 yrs old', '65-69 yrs old', '70-74  yrs old', '75-79 yrs old',
                          '80-84 yrs old', '85+', 'Total']
        mode_table[category] = pd.Categorical(mode_table[category], categories=category_order, ordered=True)
        mode_table = mode_table.sort_values(category)


    # Drop columns containing 'Total' in their names, as they were added by margins=True in the pivot_table
    columns_to_drop = [col for col in mode_table.columns if 'Total' in col]
    mode_table.drop(columns=columns_to_drop, inplace=True)

    # Rename the columns to add clarity and distinguish between count and percentage values
    mode_table.columns = [f'{col[0]} {col[1]}' for col in mode_table.columns]

    # Create a list of column names for easy access
    column_names = list(mode_table.columns)

    # Create a Plotly table dynamically with all columns as values
    header_values = []
    cell_colors = []  # List to store cell colors

    for col in column_names:
        if 'Percentage' in col:
            header_values.append(f'<b>{col} %</b>')  # Bold header for percentage columns
        elif category in col:
            header_values.append(f'<b>{col}</b>')  # Bold header for the 'mode' column
            cell_colors.append(['paleturquoise'] * len(mode_table))  # Set cell colors for the 'mode' column
        else:
            header_values.append(f'<b>{col}</b>')  # Bold header for other columns
            cell_colors.append(['lavender'] * len(mode_table))  # Set cell colors for other columns

    # Create the Plotly table
    table = go.Table(
        header=dict(values=header_values, fill_color='Purple', align='center', font=dict(color='white', size=12)),  # Set header properties
        cells=dict(values=[mode_table[col] for col in column_names], fill=dict(color=cell_colors), align='center')  # Set cell properties
    )

    # Create a Figure object and add the table to it
    fig = go.Figure(data=[table])

    # Update the layout for the table
    fig.update_layout(
        margin={'l': 0, 't':0, 'r': 0},
        title=None,
        plot_bgcolor='rgba(0,0,0,0)',    # Set the plot background color to transparent
        paper_bgcolor='rgba(0,0,0,0)'
    )

        
    return fig


def options_sub_category_dropdown(category):
    columns_read = [category]
    df = pl.read_csv('data/processed_dataframes/boston/boston_runs.csv', columns = columns_read, infer_schema_length=10000,ignore_errors=True, null_values=['Green-C1/Green-D-Reservoir17/Green-E1/'])
    df = df.select([category]).unique().to_pandas()
    df = df[category].unique()
    
    return df


def demographic_distribution_time(category, subcategory):
    # Assuming 'trip_group' is a DataFrame containing the necessary data
    
    df = pl.read_csv('data/processed_dataframes/boston/boston_runs.csv', columns = ['scenario_label', 'time_range', category], infer_schema_length=10000,ignore_errors=True, null_values=['Green-C1/Green-D-Reservoir17/Green-E1/'])

    distribution_mode_stacked = df.groupby(['scenario_label', 'time_range', category]).agg(pl.count()).to_pandas()
    
    distribution_mode_stacked = distribution_mode_stacked[distribution_mode_stacked[category].isin(subcategory)]
    

    fig = px.histogram(
        distribution_mode_stacked,
        facet_col='scenario_label',         # Group the plots by 'label' in separate columns
        barnorm='percent',         # Normalize the bars to show percentages
        x='time_range',          # Assign 'time_range_2' to the x-axis
        y='count',                 # Assign 'count' to the y-axis
        color=category,            # Assign 'mode' to the bar colors
        hover_data={'count'},      # Include 'count' in the hover tooltip
        labels={'mode': 'Mode of Transport', 
                'Percentage': 'Percentage (%)',
                'range_income':'Income Level',
                'age': 'Age Level',
                'education_category':'Level of Education',
                'gender':'Gender',
                'scenario_label':'Scenario'},  # Customize axis labels
        color_discrete_sequence=px.colors.qualitative.Dark24
    )

    # Get the adjusted title from the labels dictionary
    adjusted_title = f'Distribution Across 30 min Interval'
    # Update the layout with the adjusted title
    fig.update_layout(title_text=adjusted_title, title_font_size=20, title_x=0.5)

    for axis in fig.layout:
        if type(fig.layout[axis]) == go.layout.XAxis:
            fig.layout[axis].title.text = ''

    # Step 6: Add a new annotation to the plot
    # This annotation will be displayed below the plot and provides additional information.
    fig.update_layout(
        annotations=list(fig.layout.annotations) +  # keep the original annotations and add a new one
        [
            go.layout.Annotation(
                x=0.5,
                y=-0.2,                    # Position the annotation below the plot
                font=dict(size=14),
                showarrow=False,
                text="Time of Day in 30 Min Intervals",  # The text of the annotation
                xref="paper",
                yref="paper"
            )
        ]
    )


    # Step 7: Show the plot.
    return fig


def create_diff_plot_travel_time(category, subcategory):
    
    
    columns_read = ['scenario_label', 'travel_time','total_dist',category]
    df = pl.read_csv('data/processed_dataframes/boston/boston_runs.csv', columns = columns_read, infer_schema_length=10000,ignore_errors=True, null_values=['Green-C1/Green-D-Reservoir17/Green-E1/'])
    
    # Group the DataFrame by 'scenario_label' and 'mode' columns and calculate various aggregations.
    diff_mode = df.groupby(['scenario_label', category]).agg(
        count_label=pl.col('scenario_label').count(),
        mean_travel_time=pl.col('travel_time').mean(),
        mean_total_distance=pl.col('total_dist').mean()).to_pandas()
    
    
    diff_mode = diff_mode[diff_mode[category].isin(subcategory)]
    
    # Pivot the DataFrame to make it suitable for further processing.
    diff_mode = diff_mode.pivot_table(index=category, columns='scenario_label')
    
        # Get the unique scenario labels and exclude the baseline label ('scenario_1').
    scenario_labels = diff_mode.columns.get_level_values('scenario_label').unique()
    scenario_labels = scenario_labels[scenario_labels != 'scenario_1']
    
        # Initialize an empty DataFrame to store the differences from the baseline scenario.
    diff_df = pd.DataFrame()

    # Calculate the differences for each scenario label compared to the baseline scenario ('scenario_1').
    baseline = diff_mode.xs('scenario_1', level='scenario_label', axis=1)
    for scenario_label in scenario_labels:
        scenario_diff = (diff_mode.xs(scenario_label, level='scenario_label', axis=1) / baseline) - 1
        diff_df[f'{scenario_label} Total-Distance_mean'] = scenario_diff.iloc[:, 1]
        diff_df[f'{scenario_label} Travel-Time_mean'] = scenario_diff.iloc[:, 2]
        
        
        # Create the long format DataFrame for easier plotting.
    long_df = pd.DataFrame(diff_df.unstack().reset_index())
    long_df.columns = ['scenario_label', category, 'value']
    long_df['measure'] = long_df['scenario_label'].str.split(' ', expand=True)[1]
    long_df['scenario_label'] = long_df['scenario_label'].str.split(' ').str[0]
    long_df = long_df.pivot_table(index=['scenario_label', category], columns='measure', values='value', aggfunc='sum').reset_index()
    long_df = long_df.sort_values('Total-Distance_mean')

    # Drop rows where any value in 'Travel-Time_mean' or 'Total-Distance_mean' columns is equal to 0.
    columns_to_check = ['Travel-Time_mean', 'Total-Distance_mean']
    for index, row in long_df.iterrows():
        if any(row[column] == 0 for column in columns_to_check):
            long_df.drop(index, inplace=True)

    # Create the bar plot using Plotly Express (px).
    fig = px.bar(long_df, x=category, y="Travel-Time_mean", color="scenario_label", barmode="group",
                labels={'Travel-Time_mean': "Delta Travel Time",
                        'mode': 'Mode of Transport'})
    fig.update_yaxes(tickformat=".2%")
    fig.update_layout(
        title_text='Difference from Base Scenario in (%) - Travel Time',
        title_x=0.5,
        showlegend=False
    )
    
    return fig


def create_diff_plot_travel_distance(category, subcategory):
    columns_read = ['scenario_label', 'travel_time','total_dist',category]
    df = pl.read_csv('data/processed_dataframes/boston/boston_runs.csv', columns = columns_read, infer_schema_length=10000,ignore_errors=True, null_values=['Green-C1/Green-D-Reservoir17/Green-E1/'])
    
    # Group the DataFrame by 'scenario_label' and 'mode' columns and calculate various aggregations.
    diff_mode = df.groupby(['scenario_label', category]).agg(
        count_label=pl.col('scenario_label').count(),
        mean_travel_time=pl.col('travel_time').mean(),
        mean_total_distance=pl.col('total_dist').mean()
    )

    # Convert the result to a pandas DataFrame for better manipulations.
    diff_mode = diff_mode.to_pandas()

    # Pivot the DataFrame to make it suitable for further processing.
    diff_mode = diff_mode.pivot_table(index=category, columns='scenario_label')

    # Get the unique scenario labels and exclude the baseline label ('scenario_1').
    scenario_labels = diff_mode.columns.get_level_values('scenario_label').unique()
    scenario_labels = scenario_labels[scenario_labels != 'scenario_1']

    # Initialize an empty DataFrame to store the differences from the baseline scenario.
    diff_df = pd.DataFrame()

    # Calculate the differences for each scenario label compared to the baseline scenario ('scenario_1').
    baseline = diff_mode.xs('scenario_1', level='scenario_label', axis=1)
    for scenario_label in scenario_labels:
        scenario_diff = (diff_mode.xs(scenario_label, level='scenario_label', axis=1) / baseline) - 1
        diff_df[f'{scenario_label} Total-Distance_mean'] = scenario_diff.iloc[:, 1]
        diff_df[f'{scenario_label} Travel-Time_mean'] = scenario_diff.iloc[:, 2]

    # Create the long format DataFrame for easier plotting.
    long_df = pd.DataFrame(diff_df.unstack().reset_index())
    long_df.columns = ['scenario_label', category, 'value']
    long_df['measure'] = long_df['scenario_label'].str.split(' ', expand=True)[1]
    long_df['scenario_label'] = long_df['scenario_label'].str.split(' ').str[0]
    long_df = long_df.pivot_table(index=['scenario_label', category], columns='measure', values='value', aggfunc='sum').reset_index()
    long_df = long_df.sort_values('Total-Distance_mean')

    # Drop rows where any value in 'Travel-Time_mean' or 'Total-Distance_mean' columns is equal to 0.
    columns_to_check = ['Travel-Time_mean', 'Total-Distance_mean']
    for index, row in long_df.iterrows():
        if any(row[column] == 0 for column in columns_to_check):
            long_df.drop(index, inplace=True)

    # Create the bar plot using Plotly Express (px).
    fig = px.bar(long_df, x=category, y="Total-Distance_mean", color="scenario_label", barmode="group",
                labels={'Total-Distance_mean': "Delta Travel Distance",
                        'mode': 'Mode of Transport'})
    fig.update_yaxes(tickformat=".2%")
    fig.update_layout(
        title_text='Difference from Base Scenario in (%) - Travel Distance',
        title_x=0.5,
        showlegend=False
    )
    
    return fig


def create_sankey_boston(category):
    
    columns_read = ['mode','scenario_label',category]
    df = pl.read_csv('data/processed_dataframes/boston/boston_runs.csv', columns = columns_read, infer_schema_length=10000,ignore_errors=True, null_values=['Green-C1/Green-D-Reservoir17/Green-E1/']) 
    
        # Step 1: Group and aggregate the first DataFrame (df1)
    df1 = df.filter(df['scenario_label'] == 'scenario_1')
    df1 = df1.groupby(['mode', category]).agg(pl.count()).to_pandas()
    df1.columns = ['source', 'target', 'value']

    # Step 2: Calculate the total sum for df1
    total_sum = df1['value'].sum()

    # Step 3: Calculate the percentage of the total for df1
    df1['percentage'] = ((df1['value'] / total_sum) * 100).round(2)

    # Step 4: Sort df1 by percentage in descending order
    df1 = df1.sort_values('percentage', ascending=False)

    # Step 5: Group and aggregate the second DataFrame (df2)
    df2 = df.filter(df['scenario_label'] == 'scenario_2')
    df2 = df.groupby([category, 'mode']).agg(pl.count()).to_pandas()
    df2['mode'] = df2['mode'] + ' '
    df2.columns = ['source', 'target', 'value']

    # Step 6: Calculate the total sum for df2
    total_sum_2 = df2['value'].sum()

    # Step 7: Calculate the percentage of the total for df2
    df2['percentage'] = ((df2['value'] / total_sum_2) * 100).round(2)

    # Step 8: Sort df2 by percentage in descending order
    df2 = df2.sort_values('percentage', ascending=False)

    # Step 9: Concatenate the two DataFrames (df1 and df2)
    links = pd.concat([df1, df2], axis=0)

    # Step 10: Get unique source and target values from the concatenated DataFrame
    unique_source_target = list(pd.unique(links[['source', 'target']].values.ravel('k')))

    # Step 11: Create a mapping dictionary for the unique source and target values
    mapping_dict = {k: v for v, k in enumerate(unique_source_target)}

    # Assigning dynamic colors to the center column
    unique_categories_links = df1['target'].unique()
    filtered_dict = {key: value for key, value in mapping_dict.items() if key in unique_categories_links}
    filtered_dict = {k: filtered_dict[k] for k in sorted(filtered_dict)}
    # Keep only the values of the filtered dictionary
    filtered_values = list(filtered_dict.values())
    colors_link = px.colors.qualitative.Alphabet[:len(filtered_values)]
    result_dict = {key: value for key, value in zip(filtered_values, colors_link)}

    # Function to map ID to color, or return 'grey' if not found
    def get_color(id1, id2, opacity=255):
        return result_dict.get(id1, result_dict.get(id2, '#808080'))

    # Custom function to convert hex color to RGBA format
    def hex_to_rgba(hex_color):
        red = int(hex_color[1:3], 16)
        green = int(hex_color[3:5], 16)
        blue = int(hex_color[5:7], 16)
        return f'rgba({red}, {green}, {blue}, 0.4)'  # Assuming alpha (opacity) is set to 1.0

    # Step 12: Map the source and target values in the links DataFrame using the mapping dictionary
    links['source'] = links['source'].map(mapping_dict)
    links['target'] = links['target'].map(mapping_dict)
    links['color'] = links.apply(lambda row: get_color(row['source'], row['target']), axis=1)
    # Applying the conversion function to create a new column with RGBA values
    links['rgba_color'] = links['color'].apply(hex_to_rgba)

    # Step 13: Convert the links DataFrame to a dictionary with 'source', 'target', and 'value' as keys
    links_dict = links.to_dict(orient='list')

    # Assigning dynamic colors to the center column
    unique_categories = df1['target'].unique()
    unique_categories = sorted(unique_categories)
    colors = px.colors.qualitative.Alphabet[:len(unique_categories)]
    category_colors = dict(zip(unique_categories, colors))

    # Step 14: Create the Sankey diagram using Plotly
    fig = go.Figure(data=[go.Sankey(
        arrangement='fixed',
        node=dict(
            pad=1,
            thickness=30,
            line=dict(color='black', width=0.5),
            label=unique_source_target,
            color=[category_colors.get(node_label, 'grey') for node_label in unique_source_target]
        ),
        link=dict(
            source=links_dict['source'],
            target=links_dict['target'],
            value=links_dict['percentage'],
            color=links_dict['rgba_color']
        )
    )])

    # Step 15: Add annotations to the plot for column names
    cols = ["Mode Scenario 1", "Employment Status", "Mode Scenario 2"]
    for x_coordinate, column_name in enumerate(cols):
        fig.add_annotation(
            x=x_coordinate / (len(cols) - 1),
            y=1.05,
            xref="paper",
            yref="paper",
            text=column_name,
            showarrow=False,
            font=dict(size=16),
            align="center",
        )

    # Step 16: Update the layout of the plot.
    fig.update_layout(
        title_text='Mode of Transport Chosen',
        title_x=0.5,
        height=800
    )
    
    return fig

def create_maps_time(category, subcategory, scenario, zone, variable):
    # Step 1: Read data from CSV file using only the necessary columns
    columns_read = ['scenario_label', category, zone, variable]
    df = pl.read_csv('data/processed_dataframes/boston/boston_runs.csv', columns=columns_read, infer_schema_length=10000, ignore_errors=True, null_values=['Green-C1/Green-D-Reservoir17/Green-E1/'])
    
    # Step 2: Filter the DataFrame based on category, subcategory, and scenario
    df = df.filter(pl.col(category).is_in(subcategory))
    df = df.filter(pl.col('scenario_label').is_in(scenario))
    
    # Step 3: Group the DataFrame based on zone and scenario_label and calculate aggregation based on the variable
    if variable == 'count':
        df = df.groupby([zone, 'scenario_label']).agg(count=pl.col('count').count()).to_pandas()
    elif variable == 'travel_time':
        df = df.groupby([zone, 'scenario_label']).agg(mean=pl.col('travel_time').mean()).to_pandas()
    elif variable == 'total_dist':
        df = df.groupby([zone, 'scenario_label']).agg(mean=pl.col('total_dist').mean()).to_pandas()

    # Step 4: Read the GeoJSON file containing zone boundaries
    url = 'data/shp_files/boston/zones.json'
    zones = gpd.read_file(url)
    
    # Step 5: Merge the DataFrame with zone geometries based on the zone column
    df = pd.merge(df, zones, left_on=zone, right_on=zones.index, how='inner')
    df.iloc[:, 2] = df.iloc[:, 2].astype('int')  # Step 6: Convert a specific column to 'int' data type
    df = gpd.GeoDataFrame(df, geometry='geometry') 

    
    # Step 8: Create the choropleth map using Plotly Express and Plotly Mapbox
    fig = px.choropleth_mapbox(df,
                               geojson=df.geometry,
                               color_continuous_scale=px.colors.sequential.RdBu_r,
                               locations=df.iloc[:, 3],
                               color=df.iloc[:, 2],
                               center={"lat": 42.361145, "lon": -71.057083},
                               mapbox_style="carto-positron",
                               zoom=7.3)
    
    return fig


def create_line_chart_hover(category, subcategory, scenario, zone, hover):
    # Read data from the CSV file, selecting relevant columns
    df = pl.read_csv('data/processed_dataframes/boston/boston_runs.csv', columns=['scenario_label', category, zone, 'time_range', 'travel_time', 'total_dist'], infer_schema_length=10000, ignore_errors=True, null_values=['Green-C1/Green-D-Reservoir17/Green-E1/'])

    # Step 2: Filter the DataFrame based on category, subcategory, and scenario
    df = df.filter(pl.col(category).is_in(subcategory))
    df = df.filter(pl.col('scenario_label').is_in(scenario))

    df = df.filter(pl.col(zone).is_in(hover))
    # Filter the DataFrame to include only rows where the 'zone' column matches any value in 'hover' list

    # Group by 'time_range_2' and calculate the mean of 'travel_time' and 'total_distance' columns
    
    df = df.groupby(['time_range']).agg(mean_time=pl.col('travel_time').round(1).mean(), mean_distance =pl.col('total_dist').round(1).mean()).to_pandas()
    
    df['time_range'] = df['time_range'].str[11:16]
    df['time_range'] = pd.to_datetime(df['time_range'], format='%H:%M')
    df = df.sort_values(by='time_range')
    df['time_range'] = df['time_range'].dt.strftime('%H:%M')

    # Create the bar chart trace
    bar_trace = go.Bar(
        x=df['time_range'],
        y=df['mean_distance'],
        marker=dict(color='#AB63FA'),
        name='Distance'
    )
    
        # Create the line chart trace
    line_trace = go.Scatter(
        x=df['time_range'],
        y=df['mean_time'],
        mode='lines',
        name='Time',
        line=dict(color='#19D3F3', width=4),
        yaxis='y2'
    )
    
    


    # Create the figure with both traces
    fig = go.Figure(data=[bar_trace, line_trace])

    # Set up the secondary y-axis to synchronize the scales
    fig.update_layout(
        title='Zone Average Performance',
        title_x=0.5,
        title_font_size=25,
        yaxis=dict(title='Average Travel Distance (in meters)'),
        yaxis2=dict(title='Average Travel Time (in minutes)', overlaying='y', side='right', type='linear'),
    )
    
    

    # Update legend to show both traces side by side (horizontal layout)
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))


    return  fig