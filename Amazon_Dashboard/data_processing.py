# data_processing.py

import pandas as pd

def load_data(file_path):
    data = pd.read_excel(file_path, sheet_name=None)
    merged_data = pd.concat(data.values(), ignore_index=True)
    merged_data.columns = merged_data.columns.str.strip()
    return merged_data

def concatenate_dataframes(data):
    merged_data_df = pd.concat(data.values(), ignore_index=True)
    return merged_data_df

def clean_column_names(data):
    data.columns = data.columns.str.strip()
    return data

def map_lifecycle_state(data):
    status_mapping = {'Ordered': 'Active', 'Unavailable': 'Active'}
    data['Lifecycle state'] = data['Lifecycle state'].map(lambda x: status_mapping.get(x, x))
    return data

def calculate_savings(merged_data_df):
    merged_data_df['Savings'] = merged_data_df['HIGH RATES'] - merged_data_df['AMOUNT']
    weekly_savings_summary = merged_data_df.groupby('WEEK')['Savings'].agg(['sum', 'mean']).reset_index()
    weekly_savings_summary.columns = ['Week', 'Total Savings', 'Average Savings']
    return weekly_savings_summary

def calculate_summary_metrics(merged_data_df, selected_weeks):
    filtered_data = merged_data_df[merged_data_df['WEEK'].isin(selected_weeks)]
    
    total_transactions = filtered_data.shape[0]
    average_savings = filtered_data['Savings'].mean()
    active_lp_count = filtered_data[filtered_data['Lifecycle state'] == 'Active']['LICENSE PLATE'].nunique()
    
    return total_transactions, average_savings, active_lp_count

def group_lp_status_weekly(merged_data_df):
    lp_status_weekly = merged_data_df.groupby(['WEEK', 'Lifecycle state'])['LICENSE PLATE'].nunique().unstack(fill_value=0)
    lp_status_weekly = lp_status_weekly.reset_index()
    return lp_status_weekly

def filter_and_group_toll_transactions(merged_data_df):
    # Step 1: Filter for active LICENSE PLATEs and exclude 'TRAILER' report type
    active_lp_df = merged_data_df[(merged_data_df['Lifecycle state'] == 'Active') &
                                   (merged_data_df['REPORT TYPE'] != 'TRAILER')]

    # Step 2: Filter for 'Transponder Toll' and 'plate toll' transaction types
    toll_transactions_df = active_lp_df[active_lp_df['TRANSACTION TYPE'].isin(['Transponder Toll', 'Plate Toll'])]

    # Step 3: Group by week and transaction type, count unique LICENSE PLATEs
    toll_transactions_weekly = toll_transactions_df.groupby(['WEEK', 'TRANSACTION TYPE'])['LICENSE PLATE'].nunique().reset_index(name='Count')
    return toll_transactions_weekly

def group_active_lp_sources_weekly(merged_data_df):
    active_lp_df1 = merged_data_df[(merged_data_df['Lifecycle state'] == 'Active')]
    active_lp_weekly = active_lp_df1.groupby(['WEEK', 'SOURCE']).size().reset_index(name='Count')
    return active_lp_weekly

def read_sla_trend_data(merged_data_df):
    sla_trend_df = merged_data_df.groupby(['WEEK', 'SLA MET']).size().reset_index(name='Count')
    return sla_trend_df
