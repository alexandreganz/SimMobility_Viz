import pandas as pd
import polars as pl
import geopandas as gpd
import plotly.express as px
from datetime import datetime
import os
import re


def concat_csv_to_dataframe(csv_paths):
    # Create an empty list to store individual DataFrames
    dataframes = []

    # Read each CSV file into a Polars DataFrame and append it to the list
    for i, path in enumerate(csv_paths):
        selected_columns = ['person_id','origin_taz','destination_taz','mode','start_time','end_time','travel_time','total_dist']
        
        column_types = {
            'person_id': pl.Utf8,
            'origin_taz': pl.Int32,
            'destination_taz': pl.Int32,
            'mode': pl.Utf8,
            'start_time': pl.Utf8,
            'end_time': pl.Utf8,
            'travel_time': pl.Float64,
            'total_dist': pl.Float64}
        
        # Read the CSV file with specified column types and other options
        df = pl.read_csv(path,columns = selected_columns, dtypes=column_types, infer_schema_length=10000, ignore_errors=True, null_values=['Green-C1/Green-D-Reservoir17/Green-E1/'])
        
        # Create a label for the scenario based on the index (i)
        scenario_label = f"scenario_{i + 1}"
        df = df.with_columns(pl.lit(scenario_label).alias("scenario_label"))
        
        # Append the DataFrame to the list
        dataframes.append(df)
        
    # Concatenate all DataFrames into a single DataFrame
    df = pl.concat(dataframes)
    
    # Transform the 'person_id' column by removing trailing characters and leading zeros
    df = df.with_columns(df['person_id'].str.slice(0, 9).alias('person_id'))
    pattern = r'(\d{3})(\d{2})00(\d{2})'
    
    def transform_numbers(s):
        return re.sub(pattern, r'\1\2\3', s)
    
    df = df.with_columns(df['person_id'].apply(transform_numbers).alias('person_id'))
    
    # Extract only the numeric part before '-' in 'person_id' column
    df = df.with_columns(df['person_id'].str.split('-').apply(lambda split_list: int(split_list[0])))
    df = df.with_columns(pl.col(['start_time','end_time']).str.to_datetime("%H:%M:%S"))
    df = df.with_columns(pl.col("start_time").dt.truncate("30m").alias('time_range'))

    
    # Read population DataFrame from another CSV file
    population_columns = ['id','person_type_id','gender_id','education_type_id','age_category_id','income']
    income_columns = ['id','name']
    df_population = pl.read_csv('data/population/individual_by_id_for_preday_new.csv', columns = population_columns ,infer_schema_length=10000, separator=',')
    
    #loading the categorical dataframes
    df_gender = pl.read_csv('data/population/gender.csv').rename({"name": "gender_category"})
    df_education = pl.read_csv('data/population/education.csv').rename({"name": "education_category"})
    df_age = pl.read_csv('data/population/age.csv').rename({"name": "age_category"})
    df_income = pl.read_csv('data/population/income.csv',columns= income_columns).rename({"name": "income_category"})
    df_employment = pl.read_csv('data/population/employment_status.csv',columns= income_columns).rename({"name": "employment_category"})
    
    
    

    # Join the main DataFrame with the population DataFrame on 'person_id'
    df = df.join(df_population, left_on='person_id', right_on='id')
    df = df.join(df_gender, left_on='gender_id', right_on='id')
    df = df.join(df_education, left_on='education_type_id', right_on='id')
    df = df.join(df_age, left_on='age_category_id', right_on='id')
    df = df.join(df_income, left_on='income', right_on='id')
    df = df.join(df_employment, left_on='person_type_id', right_on='id')
    
    
    df = df.drop(['person_type_id','gender_id','education_type_id','age_category_id','income'])
    df = df.with_columns(pl.lit(1).alias('count'))
    
    # Save the DataFrame as a CSV file with custom options
    csv_file_path = 'data/processed_dataframes/boston/boston_runs.csv'
    df.write_csv(csv_file_path, has_header=True)

    
    return df

