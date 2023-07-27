import base64
import pandas as pd
import io
import geopandas as gpd
from dash import html

def process_files(contents, single_contents, label_prefix='scenario'):
    # Load data and set headers and column types
    headers = ['person_id', 'trip_id', 'subtrip_id', 'origin_type', 'origin_node', 'origin_taz', 'destination_type',
               'destination_node', 'destination_taz', 'mode', 'start_time', 'end_time', 'travel_time', 'total_distance',
               'cbd_entry_node', 'cbd_exit_node', 'cbd_entry_time', 'cbd_exit_time', 'cbd_travel_time',
               'non_cbd_travel_time', 'cbd_distance', 'non_cbd_distance', 'extra']
    column_types = {
        'person_id': str, 'trip_id': str, 'subtrip_id': str, 'origin_type': str, 'origin_node': str, 'origin_taz': str,
        'destination_type': str, 'destination_node': str, 'destination_taz': str, 'mode': str, 'start_time': str,
        'end_time': str, 'travel_time': float, 'total_distance': float, 'cbd_entry_node': str, 'cbd_exit_node': str,
        'cbd_entry_time': str, 'cbd_exit_time': str, 'cbd_travel_time': str, 'non_cbd_travel_time': float,
        'cbd_distance': float, 'non_cbd_distance': float, 'extra': float,
    }

    # Load population details and nodes
    df_population = pd.read_csv('data/population/individual.csv', delimiter=',').rename(columns={"id": "person_id"})
    gender_df = pd.read_csv('data/population/gender.csv', delimiter=',').rename(columns={"id": "gender_id", "name": "gender"})
    education_df = pd.read_csv('data/population/education.csv', delimiter=',').rename(columns={"id": "education_id", "name": "education_category"})
    age_df = pd.read_csv('data/population/age.csv', delimiter=',').rename(columns={"id": "age_category_id", "name": "age"})
    income_df = pd.read_csv('data/population/income.csv', delimiter=',').rename(columns={"id": "income_id", "name": "income_range"})
    job_df = pd.read_csv('data/population/employment_status.csv', delimiter=',').rename(columns={"id": "employment_status_id", "name": "job_name"})
    nodes = gpd.read_file('data/shp_files/virtual_city/node.shp').to_crs(epsg=4326)

    # Process each file and store the DataFrames in a list
    combined_data = []
    for i, content in enumerate(contents):
        decoded_content = base64.b64decode(content.split(',')[1])  # Decode the base64-encoded content
        df = pd.read_csv(io.StringIO(decoded_content.decode('utf-8')))  # Read CSV data into DataFrame

        # Apply headers and column types to the DataFrame
        df.columns = headers
        df = df.astype(column_types)

        # Perform data transformations
        df['person_id'] = df['person_id'].str.split('-', expand=True)[0].astype(int)
        time_columns = ['start_time', 'end_time', 'cbd_exit_time', 'cbd_travel_time']
        df[time_columns] = df[time_columns].apply(pd.to_datetime, format='%H:%M:%S')
        df['time_range'] = df['start_time'].dt.floor('30T')
        df = df.assign(distr='count', label=f'{label_prefix}_{i + 1}')

        # Append the processed DataFrame to the list
        combined_data.append(df)

    # Concatenate the DataFrames in the list
    appended_df = pd.concat(combined_data, ignore_index=True)

    # Read the baseline file and process it
    content_type = single_contents.split(',')
    decoded = base64.b64decode(content_type[1])
    df_single = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    df_single.columns = headers
    df_single = df_single.astype(column_types)
    df_single['person_id'] = df_single['person_id'].str.split('-', expand=True)[0].astype(int)
    df_single[time_columns] = df_single[time_columns].apply(pd.to_datetime, format='%H:%M:%S')
    df_single['time_range'] = df_single['start_time'].dt.floor('30T')
    df_single = df_single.assign(distr='count', label='baseline')

    # Concatenate the DataFrames for an unique dataframe (baseline + scenarios)
    appended_df = pd.concat([appended_df, df_single], ignore_index=True)

    # Merge population details with the appended DataFrame
    appended_df = pd.merge(appended_df, df_population, on='person_id', how='inner')
    appended_df = pd.merge(appended_df, gender_df, on='gender_id', how='inner')
    appended_df = pd.merge(appended_df, education_df, on='education_id', how='inner')
    appended_df = pd.merge(appended_df, age_df, on='age_category_id', how='inner')
    appended_df = pd.merge(appended_df, job_df, on='employment_status_id', how='inner')

    # Merge location details
    appended_df = pd.merge(appended_df, nodes, left_on='origin_node', right_on='id', how='inner').rename(columns={'geometry': 'geometry_origin'})
    appended_df = pd.merge(appended_df, nodes, left_on='destination_node', right_on='id', how='inner').rename(columns={'geometry': 'geometry_destination'})
    appended_df['origin_lat'] = appended_df['geometry_origin'].apply(lambda point: point.y)
    appended_df['origin_long'] = appended_df['geometry_origin'].apply(lambda point: point.x)
    appended_df['destination_lat'] = appended_df['geometry_destination'].apply(lambda point: point.y)
    appended_df['destination_long'] = appended_df['geometry_destination'].apply(lambda point: point.x)

    # Get income ranges and labels as lists, assign label based on income range
    income_ranges = sorted(list(income_df['low_limit']) + [float('inf')])
    income_labels = list(income_df['income_range'])
    appended_df['range_income'] = pd.cut(appended_df['income'], bins=income_ranges, labels=income_labels, right=False, include_lowest=True)
    appended_df['distri'] = 'count'

    # Map boolean columns using a dictionary
    boolean_columns = ['work_at_home', 'car_license', 'motor_license', 'vanbus_license']
    mapping_dict = {'f': False, 't': True}
    appended_df[boolean_columns] = appended_df[boolean_columns].replace(mapping_dict)
    appended_df['count'] = 1
    appended_df['start_time'] = appended_df['start_time'].dt.strftime('%H:%M')  # Format time to hour and minute
    appended_df['time_range_2'] = appended_df['time_range'].dt.strftime('%H:%M')

    # Select and reorder columns
    columns_to_keep = [
        'person_id', 'trip_id', 'mode', 'start_time', 'time_range', 'time_range_2', 'travel_time',
        'total_distance', 'gender', 'education_category', 'age','origin_node','destination_node',
        'range_income', 'label', 'distr', 'count', 'distri', 'job_name', 'origin_lat', 'origin_long', 'destination_lat', 'destination_long','origin_taz','destination_taz'
    ]
    appended_df = appended_df[columns_to_keep]

    # Save the processed DataFrame to CSV and return it
    appended_df.to_csv('data/processed_dataframes/vc_runs.csv', index=False)
    return appended_df
