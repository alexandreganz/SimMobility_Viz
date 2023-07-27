import numpy as np
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
import geopandas as gpd
from keplergl import KeplerGl


#first Visualization
def trips_day():
    columns_read = ['label', 'time_range_2','count']
    trip_group = pd.read_csv('data/processed_dataframes/vc_runs.csv',usecols=columns_read, sep=',')
    
    # Step 2: Group the DataFrame by 'label' and 'time_range_2', and sum the 'count' column
    trip_group = trip_group.groupby(['label', 'time_range_2'])['count'].sum().reset_index()

    # Step 3: Calculate the total population count for each 'label'
    category_total = trip_group.groupby('label')['count'].transform('sum')

    # Step 4: Add a 'percentage' column to the DataFrame
    trip_group['percentage'] = ((trip_group['count'] / category_total) * 100).round(2)

    # Step 5: Create a bar plot using Plotly
    fig = px.bar(trip_group, 
                x='time_range_2', 
                y='percentage',
                labels={'percentage': 'Percentage (%)', 'time_range_2': 'Time of Day (30 min time intervals)', 'label': 'Scenario', 'count': 'Count of Trips'},
                color='label',
                barmode='group',
                title='Trips by Time of Day',
                color_discrete_sequence=px.colors.qualitative.Alphabet,
                hover_data=['count', 'percentage'])

    # Step 6: Update the layout of the plot
    fig.update_layout(
        title=dict(
            text='Trips by Time of Day',
            x=0.5,
            font=dict(size=20)),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1))

    # Step 7: Update the y-axis tick suffix to display percentage symbol
    fig.update_layout(yaxis_ticksuffix="%")
    
    return fig






# Second Visualization
def tour_person():
    columns_read = ['person_id', 'label','count']
    df = pd.read_csv('data/processed_dataframes/vc_runs.csv', usecols=columns_read, sep=',')
    
    # Step 1: Group by 'person_id' and 'label', and sum the 'count' column
    number_tours = df.groupby(['person_id', 'label'])['count'].sum().reset_index()

    # Step 2: Group by 'count' and 'label', and count the occurrences
    number_tours = number_tours.groupby(['count', 'label']).size().reset_index(name='Population_Count')

    # Step 3: Replace values greater than 4 with '+4 trips' in a new column 'trip_count'
    number_tours['trip_count'] = pd.cut(number_tours['count'], bins=[1, 2, 3, 4, 5, float('inf')],
                                    labels=['1', '2', '3', '4', '+4 trips'], right=False)

    # Step 4: Group by 'label' and 'trip_count', and sum the 'Population_Count' column
    number_tours = number_tours.groupby(['label', 'trip_count'])['Population_Count'].sum().reset_index()

    # Step 5: Define the order of the 'trip_count' categories
    category_order = ['1', '2', '3', '4', '+4 trips']

    # Step 6: Convert 'trip_count' to categorical with the defined order
    number_tours['trip_count'] = pd.Categorical(number_tours['trip_count'], category_order)

    # Step 7: Sort the DataFrame based on the categorical order
    number_tours = number_tours.sort_values('trip_count')

    # Step 8: Calculate the total population count for each 'label'
    total_population = number_tours.groupby('label')['Population_Count'].transform('sum')

    # Step 9: Add a 'Percentage' column to the DataFrame
    number_tours['Percentage'] = ((number_tours['Population_Count'] / total_population) * 100).round(2)

    # Step 10: Create a bar plot using Plotly
    fig = px.bar(number_tours, x='trip_count',
                y='Percentage', 
                color='label',
                labels={'trip_count': 'Number of Tours', 'Percentage': 'Percentage (%)', 'label':'Scenario', 'Population_Count':'Count'},
                barmode='group',
                color_discrete_sequence=px.colors.qualitative.Alphabet,
                template='plotly',
                hover_data=['Population_Count', 'Percentage'])

    # Step 11: Update the layout of the plot
    fig.update_layout(
        title=dict(
            text='Number of Tours',
            x=0.5,
            font=dict(size=20)),
        yaxis_ticksuffix="%", # Display percentage symbol on the y-axis ticks
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1),
        showlegend=False) # Hide the legend
    
    return fig


# Third Visualization
def indicators():
    columns_read = ['label', 'travel_time','total_distance']

    # Assuming 'trip_group' is a DataFrame containing the necessary data
    df = pd.read_csv('data/processed_dataframes/vc_runs.csv',usecols=columns_read, sep=',')

    # Create the go.Indicator plot
    fig = go.Figure()

    # Calculate the total number of trips for each scenario
    sum_trips = df.groupby('label')['travel_time'].size().round(2)

    # Calculate the average travel time for each scenario
    average_travel_times = df.groupby('label')['travel_time'].mean().round(2)

    # Calculate the average travel distance for each scenario
    average_travel_distances = df.groupby('label')['total_distance'].mean().round(2)

    # Calculate the standard deviation of travel time for each scenario
    std_travel_times = df.groupby('label')['travel_time'].std().round(2)

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

    # Show the plot
    return fig


#Fourth Visualization
def demographic_distribution(category):
    # Assuming 'trip_group' is a DataFrame containing the necessary data
    df = pd.read_csv('data/processed_dataframes/vc_runs.csv', usecols=['label', category], sep=',')

    # Step 1: Calculate the sum of 'count' for each combination of 'label' and 'mode'
    mode_shares = df.groupby(['label', category]).size().reset_index(name='count')

    # Step 2: Calculate the total population count for each 'label'
    total_mode = mode_shares.groupby('label')['count'].transform('sum')

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
        color='label',
        labels={'mode': 'Mode of Transport', 
                'Percentage': 'Percentage (%)',
                'range_income':'Income Level',
                'age': 'Age Level',
                'education_category':'Level of Education',
                'gender':'Gender',
                'label':'Scenario'},
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
    df = pd.read_csv('data/processed_dataframes/vc_runs.csv', usecols=['label', category], sep=',')

    # Step 1: Calculate the sum of 'count' for each combination of 'label' and 'mode'
    mode_shares = df.groupby(['label', category]).size().reset_index(name='count')

    # Step 2: Calculate the total population count for each 'label'
    total_mode = mode_shares.groupby('label')['count'].transform('sum')

    # Step 3: Calculate the percentage of each mode count relative to the total count for the corresponding 'label'
    mode_shares['Percentage'] = ((mode_shares['count'] / total_mode) * 100).round(2)

    # Pivot the data to create the mode_table using the 'mode' and 'label' columns, summing the 'count' and 'Percentage' values
    mode_table = mode_shares.pivot_table(values=['count', 'Percentage'], index=category, columns='label', aggfunc='sum', margins=True, margins_name='Total').reset_index()

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

        
def demographic_distribution_time(category, subcategory):
    # Assuming 'trip_group' is a DataFrame containing the necessary data
    df = pd.read_csv('data/processed_dataframes/vc_runs.csv', usecols=['label', 'time_range_2', category], sep=',')
    distribution_mode_stacked = df.groupby(['label', 'time_range_2', category]).size().reset_index(name='count')
    
    distribution_mode_stacked = distribution_mode_stacked[distribution_mode_stacked[category].isin(subcategory)]
    

    fig = px.histogram(
        distribution_mode_stacked,
        facet_col='label',         # Group the plots by 'label' in separate columns
        barnorm='percent',         # Normalize the bars to show percentages
        x='time_range_2',          # Assign 'time_range_2' to the x-axis
        y='count',                 # Assign 'count' to the y-axis
        color=category,            # Assign 'mode' to the bar colors
        hover_data={'count'},      # Include 'count' in the hover tooltip
        labels={'mode': 'Mode of Transport', 
                'Percentage': 'Percentage (%)',
                'range_income':'Income Level',
                'age': 'Age Level',
                'education_category':'Level of Education',
                'gender':'Gender',
                'label':'Scenario'},  # Customize axis labels
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


def options_sub_category_dropdown(category):
    df = pd.read_csv('data/processed_dataframes/vc_runs.csv', sep=',')
    df = df[category]
    
    return df


def create_diff_plot_travel_time(category, subcategory):
    # Read the CSV file and filter relevant columns
    df = pd.read_csv('data/processed_dataframes/vc_runs.csv', usecols=['label','travel_time','total_distance', category], sep=',')
    df = df[df[category].isin(subcategory)]
    
    # Calculate mean values for travel_time and total_distance per label and category
    time_distr_df = df.groupby(['label', category]).agg(
        count_label=('label', 'count'),
        mean_travel_time=('travel_time', 'mean'),
        mean_total_distance=('total_distance', 'mean')
    ).reset_index()

    # Pivot the data to have labels as columns and categories as rows
    pivot_df = time_distr_df.pivot_table(index=category, columns='label')

    # Get scenario labels and exclude the baseline label
    scenario_labels = pivot_df.columns.get_level_values('label').unique()
    scenario_labels = scenario_labels[scenario_labels != 'baseline']

    # Calculate differences from the baseline for each scenario
    diff_df = pd.DataFrame()
    baseline = pivot_df.xs('baseline', level='label', axis=1)
    for scenario_label in scenario_labels:
        scenario_diff = (pivot_df.xs(scenario_label, level='label', axis=1) / baseline) - 1
        diff_df[f'{scenario_label} Total-Distance_mean'] = scenario_diff.iloc[:, 1]
        diff_df[f'{scenario_label} Travel-Time_mean'] = scenario_diff.iloc[:, 2]

    # Create the long format dataframe to prepare for plotting
    long_df = pd.DataFrame(diff_df.unstack().reset_index())
    
    
    
    
    
    long_df.columns = ['label', 'category', 'value']
    long_df['measure'] = long_df['label'].str.split(' ', expand=True)[1]
    long_df['label'] = long_df['label'].str.split(' ').str[0]
    long_df = long_df.pivot_table(index=['label','category'], columns='measure', values='value', aggfunc='sum').reset_index()
    long_df = long_df.sort_values('Total-Distance_mean')

    # Drop rows where any of the difference values is 0
    columns_to_check = ['Travel-Time_mean', 'Total-Distance_mean']
    long_df = long_df[~long_df[columns_to_check].eq(0).any(axis=1)]

    # Create the figures for the two bar plots
    fig_diff_time = px.bar(long_df, x="category", y="Travel-Time_mean", color="label", barmode="group",
                           color_discrete_sequence=px.colors.qualitative.Alphabet,
                           labels={'Total-Distance_mean': "Delta Travel Distance",
                                   'category': 'Gender', 
                                  'category': 'Mode of Transport', 
                                  'category': 'Income Level', 
                                  'category': 'Age', 
                                  'category': 'Level of Education',
                                  'label': 'Scenario'})
    fig_diff_time.update_yaxes(tickformat=".2%")
    fig_diff_time.update_layout(
        title_text='Difference from Base Scenario in (%) - Travel Time',
        title_x=0.5,
        legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1),
        margin=dict(t=100),
        showlegend=True
    )

    fig_diff_distance = px.bar(long_df, x="category", y="Total-Distance_mean", color="label", barmode="group",
                               color_discrete_sequence=px.colors.qualitative.Alphabet,
                               labels={'Total-Distance_mean': "Delta Travel Distance",
                                       'category': 'Gender', 
                                      'category': 'Mode of Transport', 
                                      'category': 'Income Level', 
                                      'category': 'Age', 
                                      'category': 'Level of Education',
                                      'label': 'Scenario'})
    fig_diff_distance.update_yaxes(tickformat=".2%")
    fig_diff_distance.update_layout(
        title_text='Difference from Base Scenario in (%) - Travel Distance',
        title_x=0.5,
     legend=dict(
        orientation="h",
        entrywidth=70,
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1),
        margin=dict(t=100),
        showlegend=False
    )

    return fig_diff_time, fig_diff_distance


def scenario_options_radio():
    df = pd.read_csv('data/processed_dataframes/vc_runs.csv', usecols=['label'], sep=',')
    df = df['label'].unique()
    df = [x for x in df if x != 'baseline']
    return df

def scenario_options_radio_2():
    df = pd.read_csv('data/processed_dataframes/vc_runs.csv', usecols=['label'], sep=',')
    df = df['label'].unique()
    return df




def create_sankey(category, scenario):
    df = pd.read_csv('data/processed_dataframes/vc_runs.csv', usecols=['label','mode',category], sep=',')
    
    # Step 1: Group and aggregate the first DataFrame (df1)
    baseline_df = df[df['label'] == 'baseline']
    df1 = baseline_df.groupby(['mode', category]).size().reset_index()
    df1.columns = ['source', 'target', 'value']

    # Step 2: Calculate the total sum for df1
    total_sum = df1['value'].sum()

    # Step 3: Calculate the percentage of the total for df1
    df1['percentage'] = ((df1['value'] / total_sum) * 100).round(2)

    # Step 4: Sort df1 by percentage in descending order
    df1 = df1.sort_values('percentage', ascending=False)

    # Step 5: Group and aggregate the second DataFrame (df2)
    trip_1 = df[df['label'] == scenario]
    df2 = trip_1.groupby([category, 'mode']).size().reset_index()
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
    cols = ["Base Case", category , scenario]
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
        title_text='Mode of Transport Chosen (Normalized as percent) vs Base Case',
        title_x=0.5,
        title_font_size=25,
        height=800
    )

    # Step 17: Display the Sankey diagram
    return fig




def create_maps_time(category, subcategory, scenario, zone, variable):
    # Read the relevant columns from the CSV file into a pandas DataFrame
    df = pd.read_csv('data/processed_dataframes/vc_runs.csv', usecols=['label', 'time_range_2', category, zone, variable], sep=',')

    # Filter the DataFrame by the specified category and subcategory
    df = df[df[category].isin(subcategory)]
    
    # Filter the DataFrame by the specified scenario
    df = df[df['label'] == scenario]

    # Read geospatial data from a shapefile into a GeoPandas GeoDataFrame and project it to EPSG:4326
    gdf = gpd.read_file('data/shp_files/virtual_city/sm_zone.shp', ignore_fields=['cbd', 'area']).to_crs(epsg=4326)
    gdf.index += 1

    # Group the DataFrame by 'origin_taz' and 'time_range_2' and calculate the mean of 'total_distance' and 'travel_time'
    df = df.groupby([zone, 'time_range_2']).agg({variable : 'mean'}).round(2).reset_index()

    # Convert the 'time_range_2' column to datetime format
    df['time_range_2'] = pd.to_datetime(df['time_range_2'], format='%H:%M')

    # Sort the DataFrame by the 'time_range_2' column
    df.sort_values(by='time_range_2', inplace=True)

    # Reset the index and convert 'time_range_2' column back to 'HH:MM' format
    df.reset_index(drop=True, inplace=True)
    df['time_range_2'] = df['time_range_2'].dt.strftime('%H:%M')

    # Merge the DataFrame with the GeoDataFrame using 'origin_taz' and 'zone_id'
    df = pd.merge(df, gdf, left_on=zone, right_on='zone_id', how='inner')

    # Create a Plotly Express choropleth map
    fig = px.choropleth(
        df,
        geojson=gdf.geometry.__geo_interface__,
        color=variable,
        color_continuous_scale=px.colors.sequential.YlOrRd,
        locations=df.iloc[:, 0],
        animation_frame='time_range_2',
        animation_group=zone,
        labels={'travel_time': 'Avg minutes','total_distance': 'Avg Distance', 'destination_taz': 'zone','origin_taz': 'zone', 'time_range_2': 'Hour'}
    )

    # Update geos settings
    fig.update_geos(fitbounds="locations", 
                    visible=True,
                    landcolor ="#ececec",
                    bgcolor = "#ececec",
                    showcoastlines = False,
                   )


    # Update layout settings
    fig.update_layout(
        title_text='Click in a Zone to Check Performance',
        title_x=0.5,
        title_font_size=25,
        margin={"r": 10, "t": 40, "l": 10, "b": 0},
        dragmode=False,
        uirevision=True,
    )
    
    fig.update_layout(clickmode='event+select')
    
    
    return fig




def create_line_chart_hover(category, subcategory, scenario, zone, hover):
    # Read data from the CSV file, selecting relevant columns
    df = pd.read_csv('data/processed_dataframes/vc_runs.csv', usecols=['label', category, zone, 'time_range_2', 'travel_time', 'total_distance'], sep=',')

    # Filter the DataFrame by the given 'scenario'
    df = df[df['label'] == scenario]

    # Filter the DataFrame to include only rows where the 'category' column matches any value in 'subcategory' list
    df = df[df[category].isin(subcategory)]

    # Filter the DataFrame to include only rows where the 'zone' column matches any value in 'hover' list
    df = df[df[zone].isin(hover)]

    # Group by 'time_range_2' and calculate the mean of 'travel_time' and 'total_distance' columns
    df = df.groupby(['time_range_2']).agg({'travel_time': 'mean', 'total_distance': 'mean'}).round(2).reset_index()

    # Create the bar chart trace
    bar_trace = go.Bar(
        x=df['time_range_2'],
        y=df['total_distance'],
        marker=dict(color='#AB63FA'),
        name='Distance'
    )

    # Create the line chart trace
    line_trace = go.Scatter(
        x=df['time_range_2'],
        y=df['travel_time'],
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

    return fig




# Define a function to create a Kepler map
def create_kepler_map():
    # Read the data from the CSV file 'vc_runs.csv' and select specific columns using 'usecols'
    trip_group = pd.read_csv('data/processed_dataframes/vc_runs.csv', usecols=['person_id', 'mode', 'start_time', 'time_range', 'travel_time', 'total_distance', 'gender', 'education_category', 'range_income', 'label', 'job_name', 'origin_node', 'destination_node'], sep=',')

    # Read shapefile data for zones and convert to EPSG 4326 coordinate reference system
    gdf_zones = gpd.read_file('data/shp_files/virtual_city/sm_zone.shp', ignore_fields=['area'])
    gdf_zones.to_crs(epsg=4326)
    # Read shapefile data for nodes and convert to EPSG 4326 coordinate reference system
    gdf_nodes = gpd.read_file('data/shp_files/virtual_city/node.shp', ignore_fields=['z', 'traffic_li', 'tags', 'node_type', 'trafficL', 'source', 'sink', 'expressway', 'intersect', 'busnode'])
    gdf_nodes.to_crs(epsg=4326)
    
    gdf_nodes_2 = gpd.read_file('data/shp_files/virtual_city/node.shp', ignore_fields=['z', 'traffic_li', 'tags', 'node_type', 'trafficL', 'source', 'sink', 'expressway', 'intersect', 'busnode']).to_crs(epsg=4326)
    
    
    # Extract latitude and longitude from the 'geometry' column in gdf_nodes and create new columns for them
    gdf_nodes_2['latitude'] = gdf_nodes_2['geometry'].apply(lambda point: point.y)
    gdf_nodes_2['longitude'] = gdf_nodes_2['geometry'].apply(lambda point: point.x)
    
    # Convert the 'id' column in gdf_nodes to integer data type
    gdf_nodes_2['id'] = gdf_nodes_2['id'].astype(int)
    
    # Read shapefile data for roads and convert to EPSG 4326 coordinate reference system
    gdf_roads = gpd.read_file('data/shp_files/virtual_city/segment.shp', ignore_fields=['link_id', 'sequence_n', 'num_lanes', 'capacity', 'max_speed', 'tags', 'category', 'segwidth', 'segwdthrad', 'length', 'desc', 'linkcatspd', 'capperlane'])
    gdf_roads.to_crs(epsg=4326)
    
    # Merge trip_group dataframe with gdf_nodes dataframe on 'origin_node' column to add origin node information
    trip_group = pd.merge(trip_group, gdf_nodes_2, left_on='origin_node', right_on='id', how='inner')
    
    # Rename columns in trip_group to distinguish origin node information
    trip_group.rename(columns={
        'id': 'origin_id',
        'latitude': 'origin_lat',
        'longitude': 'origin_long'
    }, inplace=True)
    
    # Merge trip_group dataframe with gdf_nodes dataframe on 'destination_node' column to add destination node information
    trip_group = pd.merge(trip_group, gdf_nodes_2, left_on='destination_node', right_on='id', how='inner')
    
    # Rename columns in trip_group to distinguish destination node information
    trip_group.rename(columns={
        'id': 'destination_id',
        'latitude': 'destination_latitude',
        'longitude': 'destination_longitude'
    }, inplace=True)
    
    # Drop the unnecessary 'geometry_x' and 'geometry_y' columns from trip_group
    trip_group.drop(columns=['geometry_x', 'geometry_y'], inplace=True)
    
    config = {}
    exec(open("data/kepler_config_files/kepler_map_config.py").read(), config)
    config = config["config"]
    map_kepler = KeplerGl(height=800,data={'zones': gdf_zones, 'nodes':gdf_nodes, 'roads': gdf_roads,'trips':trip_group},config=config)
    map_kepler.save_to_html(file_name="map_kepler.html")
    
            
    with open('map_kepler.html', 'r') as f:
        kepler_html = f.read()

    # Return the processed trip_group dataframe with origin and destination node information
    return kepler_html