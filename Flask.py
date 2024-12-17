from flask import Flask, render_template, jsonify, request, make_response
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from sqlalchemy import create_engine
import json
from datetime import datetime
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Retrieve credentials from environment variables
dbname = os.getenv("DB_NAME")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")

db_url = f"postgresql+psycopg2://{user}:{password}@{host}/{dbname}"
engine = create_engine(db_url)
 
# Load data
query = "SELECT * FROM merged_data;"
merged_data_df = pd.read_sql_query(query, engine)
 
# Remove timezone information
for col in merged_data_df.select_dtypes(include=['datetime64[ns]', 'datetime64[ns, UTC]']).columns:
    if merged_data_df[col].dt.tz is not None:
        merged_data_df[col] = merged_data_df[col].dt.tz_convert(None)
    merged_data_df[col] = merged_data_df[col].dt.tz_localize(None)
 
app = Flask(__name__, template_folder="C:/Users/RamadhanZome/Desktop/AMAZON/ANALYSIS CODE AND DATA/templates")
 
# Helper functions
def map_lifecycle_state(data):
    status_mapping = {
        'End of Life': 'End of Life',
        'Active': 'Active',
        'Ordered': 'Active',
        'Unavailable': 'Active',
        'Unknown State': 'Unknown State'
    }
    data['Lifecycle state'] = data['Lifecycle state'].map(status_mapping).fillna('Unknown State')
    return data
 
def plot_lp_status_weekly(lp_status_weekly, weeks):
    filtered_data = lp_status_weekly[lp_status_weekly['WEEK'].isin(weeks)]
    filtered_data_melted = pd.melt(filtered_data, id_vars=['WEEK'], value_vars=['Active', 'End of Life', 'Unknown State'], var_name='Lifecycle state', value_name='Number of LPs')
 
    fig = px.bar(filtered_data_melted, x='WEEK', y='Number of LPs', color='Lifecycle state', barmode='group',
                 title='Weekly LP Lifecycle Status',
                 labels={'Number of LPs': 'Number of LPs', 'WEEK': 'Week', 'Lifecycle state': 'Lifecycle State'},
                 color_discrete_map={'Active': '#2ca02c', 'End of Life': '#1f77b4', 'Unknown State': '#9467bd'})
   
    fig.update_traces(hovertemplate='%{y}<extra></extra>', base=None)
    fig.update_layout(xaxis=dict(tickmode='array', tickvals=weeks, ticktext=[str(week) for week in weeks], range=[min(weeks), None]),
                      paper_bgcolor='rgba(255, 255, 255, 0.8)')
   
    return fig
 
def plot_toll_transactions(toll_transactions_weekly, weeks):
    filtered_data = toll_transactions_weekly[(toll_transactions_weekly['WEEK'].isin(weeks)) & (toll_transactions_weekly['TRANSACTION TYPE'].isin(['Transponder Toll', 'Plate Toll']))]
    fig = px.bar(filtered_data, x='WEEK', y='Count', color='TRANSACTION TYPE', barmode='group',
                 title=f'Weekly Count of Toll Transactions for Active Assets (Power Units Only)',
                 labels={'Count': 'Number of Transactions', 'WEEK': 'Week', 'TRANSACTION TYPE': 'Transaction Type'},
                 color_discrete_map={'Transponder Toll': '#2ca02c', 'Plate Toll': '#1f77b4'})
 
    fig.update_traces(hovertemplate='%{y}<extra></extra>', base=None)
    fig.update_layout(xaxis=dict(tickmode='array', tickvals=weeks, ticktext=[str(week) for week in weeks]),
                paper_bgcolor='rgba(255, 255, 255, 0.8)'  
    )
 
    return fig
 
def plot_active_lp_sources(active_lp_weekly, weeks):
    filtered_data = active_lp_weekly[(active_lp_weekly['WEEK'].isin(weeks)) & (active_lp_weekly['SOURCE'] != 'CITATION')]
    colors = ['#2ca02c', '#1f77b4', '#9467bd']
    fig = px.bar(filtered_data, x='WEEK', y='Count', color='SOURCE', barmode='group',
                 title=f'Active Status for SRTs VS Electronic Tolls',
                 labels={'Count': 'Number of Active LPs', 'WEEK': 'Week', 'SOURCE': 'Source'},
                 color_discrete_map={source: color for source, color in zip(filtered_data['SOURCE'].unique(), colors)})
 
    fig.update_traces(hovertemplate='%{y}<extra></extra>', base=None)
    fig.update_layout(xaxis=dict(tickmode='array', tickvals=weeks, ticktext=[str(week) for week in weeks]),
                    paper_bgcolor='rgba(255, 255, 255, 0.8)'
   
    )
 
    return fig
 
def plot_sla_trend_bar(sla_trend_df, weeks):
    filtered_data = sla_trend_df[sla_trend_df['WEEK'].isin(weeks)]
    fig = px.bar(filtered_data, x='WEEK', y='Count', color='SLA MET', barmode='group',
                 title=f'SLA Data Week over Week',
                 labels={'Count': 'Number of Transactions', 'WEEK': 'Week', 'SLA MET': 'SLA Status'},
                 color_discrete_map={'Within SLA': '#2ca02c', 'Outside SLA': '#1f77b4'})
 
    fig.update_traces(hovertemplate='%{y}<extra></extra>', base=None)
    fig.update_layout(xaxis=dict(tickmode='array', tickvals=weeks, ticktext=[str(week) for week in weeks]),
                    paper_bgcolor='rgba(255, 255, 255, 0.8)'                
    )
 
    return fig
 
def plot_lp_count_weekly(filtered_lp_status_weekly):
    fig = px.line(filtered_lp_status_weekly, x='WEEK', y=['Active', 'End of Life', 'Unknown State'],
                  title='LP Count Week Over Week (Active & End of Life)',
                  labels={'value': 'Number of LPs', 'WEEK': 'Week', 'variable': 'Lifecycle State'},
                  color_discrete_map={'Active': '#2ca02c', 'End of Life': '#1f77b4'})
    fig.update_traces(mode='lines+markers')
    fig.update_layout(paper_bgcolor='rgba(255, 255, 255, 0.8)')
    fig.update_traces(hovertemplate='week %{x} <br>%{y}<extra></extra>')
    return fig
 
def toll_transactions_line_plot(filtered_toll_transactions_weekly):
    fig = px.line(filtered_toll_transactions_weekly, x='WEEK', y='Count',
                  title='Count of Active LICENSE PLATEs(Power Units Only) based on Transaction Type',
                  labels={'Count': 'Number of Transactions', 'WEEK': 'Week'},
                  color='TRANSACTION TYPE',
                  color_discrete_map={'Transponder Toll': '#2ca02c', 'Plate Toll': '#1f77b4'})
    fig.update_traces(hovertemplate='week %{x} <br>%{y}<extra></extra>')
    fig.update_layout(paper_bgcolor='rgba(255, 255, 255, 0.8)')
    return fig
 
def plot_active_lp_sources_trend(filtered_active_lp_weekly):
    traces = []
    for source, data in filtered_active_lp_weekly.groupby('SOURCE'):
        trace = go.Scatter(x=data['WEEK'], y=data['Count'], mode='lines', name=f'Trend - {source}')
        traces.append(trace)
    layout = go.Layout(
        title='Trend of Active LICENSE PLATEs by Source',
        xaxis=dict(title='Week'),
        yaxis=dict(title='Number of Active LPs'),
        paper_bgcolor='rgba(255, 255, 255, 0.8)'
    )
    fig = go.Figure(data=traces, layout=layout)
    fig.update_traces(hovertemplate='week %{x} <br> %{y}<extra></extra>')
    return fig
 
def plot_sla_trend_line(filtered_sla_trend_df):
    fig = px.line(filtered_sla_trend_df, x='WEEK', y='Count', color='SLA MET',
                  title='SLA Trend Over Time',
                  labels={'Count': 'Number of Transactions', 'WEEK': 'Week', 'SLA MET': 'SLA Status'},
                  color_discrete_map={'Within SLA': '#2ca02c', 'Outside SLA': '#1f77b4'})
    fig.update_traces(mode='lines+markers')
    fig.update_traces(hovertemplate='week %{x} <br>%{y}<extra></extra>')
    fig.update_layout(paper_bgcolor='rgba(255, 255, 255, 0.8)')
    return fig
 
def calculate_savings(merged_data_df):
    merged_data_df['Savings'] = merged_data_df['HIGH RATES'] - merged_data_df['AMOUNT']
    weekly_savings_summary = merged_data_df.groupby('WEEK')['Savings'].agg(['sum', 'mean']).reset_index()
    weekly_savings_summary.columns = ['Week', 'Total Savings', 'Average Savings']
   
    return weekly_savings_summary
 
def plot_savings_trend(weekly_savings_summary):
    fig = px.line(weekly_savings_summary, x='Week', y=['Total Savings'], title='Savings Trend Over Time',
                  labels={'value': 'Amount ($)', 'Week': 'Week'},
                  color_discrete_map={'Total Savings': '#1f77b4'})
    fig.update_yaxes(tickprefix="$", tickformat=",")
    fig.update_traces(mode='lines+markers', hovertemplate='week %{x} <br> $%{y:,.2f}<extra></extra>')  
    fig.update_layout(paper_bgcolor='rgba(255, 255, 255, 0.8)')
    return fig
 
def calculate_summary_metrics(merged_data_df, selected_weeks):
    filtered_data = merged_data_df[merged_data_df['WEEK'].isin(selected_weeks)]
 
    total_transactions = filtered_data.shape[0]
    total_savings = filtered_data['Savings'].sum()
    active_lp_count = filtered_data[filtered_data['Lifecycle state'] == 'Active']['LICENSE PLATE'].nunique()
 
    return total_transactions, total_savings, active_lp_count
 
def calculate_percentage_within_sla(merged_data_df, selected_weeks):
    filtered_data = merged_data_df[(merged_data_df['WEEK'].isin(selected_weeks)) & (merged_data_df['SLA MET'] == 'Within SLA')]
    total_transactions = merged_data_df[merged_data_df['WEEK'].isin(selected_weeks)].shape[0]
    if total_transactions > 0:
        percentage_within_sla = (filtered_data.shape[0] / total_transactions) * 100
    else:
        percentage_within_sla = 0  
    return percentage_within_sla
 
# Ensure YEAR and WEEK columns are included in the grouped data
 
weekly_savings_summary = calculate_savings(merged_data_df)
lp_status_weekly = merged_data_df.groupby(['YEAR', 'WEEK', 'Lifecycle state'])['LICENSE PLATE'].nunique().unstack(fill_value=0).reset_index()
active_lp_df = merged_data_df[(merged_data_df['Lifecycle state'] == 'Active') & (merged_data_df['REPORT TYPE'] != 'TRAILER')]
toll_transactions_df = active_lp_df[active_lp_df['TRANSACTION TYPE'].isin(['Transponder Toll', 'Plate Toll'])]
toll_transactions_weekly = toll_transactions_df.groupby(['YEAR', 'WEEK', 'TRANSACTION TYPE'])['LICENSE PLATE'].nunique().reset_index(name='Count')
active_lp_weekly = active_lp_df.groupby(['YEAR', 'WEEK', 'SOURCE']).size().reset_index(name='Count')
sla_trend_df = merged_data_df.groupby(['YEAR', 'WEEK', 'SLA MET']).size().reset_index(name='Count')
 
 
unique_weeks = merged_data_df['WEEK'].unique()
unique_weeks.sort()
week_options = [{'label': str(week), 'value': week} for week in unique_weeks]
 
@app.route('/')
def index():
    return render_template('dashboard.html')
 
# @app.after_request
 
# def add_security_headers(response):
#     response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' https://cdn.plot.ly; style-src 'self' https://cdn.jsdelivr.net"
#     return response
 
@app.route('/plot_lp_status_weekly')
def plot_lp_status_weekly_route():
    year = request.args.get('year', type=int)
    weeks = request.args.getlist('weeks', type=int)
    if not weeks and year:
        weeks = merged_data_df[merged_data_df['YEAR'] == year]['WEEK'].unique()
    fig = plot_lp_status_weekly(lp_status_weekly, weeks)
    return jsonify(json.loads(fig.to_json()))
 
@app.route('/plot_toll_transactions')
def plot_toll_transactions_route():
    year = request.args.get('year', type=int)
    weeks = request.args.getlist('weeks', type=int)
    if not weeks and year:
        weeks = merged_data_df[merged_data_df['YEAR'] == year]['WEEK'].unique()
    fig = plot_toll_transactions(toll_transactions_weekly, weeks)
    return jsonify(json.loads(fig.to_json()))
 
@app.route('/plot_active_lp_sources')
def plot_active_lp_sources_route():
    year = request.args.get('year', type=int)
    weeks = request.args.getlist('weeks', type=int)
    if not weeks and year:
        weeks = merged_data_df[merged_data_df['YEAR'] == year]['WEEK'].unique()
    fig = plot_active_lp_sources(active_lp_weekly, weeks)
    return jsonify(json.loads(fig.to_json()))
 
@app.route('/plot_sla_trend_bar')
def plot_sla_trend_bar_route():
    year = request.args.get('year', type=int)
    weeks = request.args.getlist('weeks', type=int)
    if not weeks and year:
        weeks = merged_data_df[merged_data_df['YEAR'] == year]['WEEK'].unique()
    fig = plot_sla_trend_bar(sla_trend_df, weeks)
    return jsonify(json.loads(fig.to_json()))
 
 
@app.route('/plot_lp_count_weekly')
def plot_lp_count_weekly_route():
    year = request.args.get('year', type=int)
    weeks = request.args.getlist('weeks', type=int)
    filtered_data = lp_status_weekly[lp_status_weekly['YEAR'] == year]
    fig = plot_lp_count_weekly(filtered_data)
    return jsonify(json.loads(fig.to_json()))
 
@app.route('/toll_transactions_line_plot')
def toll_transactions_line_plot_route():
    year = request.args.get('year', type=int)
    weeks = request.args.getlist('weeks', type=int)
    filtered_data = toll_transactions_weekly[toll_transactions_weekly['YEAR'] == year]
    fig = toll_transactions_line_plot(filtered_data)
    return jsonify(json.loads(fig.to_json()))
 
@app.route('/plot_active_lp_sources_trend')
def plot_active_lp_sources_trend_route():
    year = request.args.get('year', type=int)
    weeks = request.args.getlist('weeks', type=int)
    filtered_data = active_lp_weekly[active_lp_weekly['YEAR'] == year]
    fig = plot_active_lp_sources_trend(filtered_data)
    return jsonify(json.loads(fig.to_json()))
 
@app.route('/plot_sla_trend_line')
def plot_sla_trend_line_route():
    year = request.args.get('year', type=int)
    weeks = request.args.getlist('weeks', type=int)
    filtered_data = sla_trend_df[sla_trend_df['YEAR'] == year]
    fig = plot_sla_trend_line(filtered_data)
    return jsonify(json.loads(fig.to_json()))
 
 
@app.route('/plot_savings_trend')
def calculate_savings_route():
    fig = plot_savings_trend(weekly_savings_summary)
    return jsonify(json.loads(fig.to_json()))
 
@app.route('/get_years')
def get_years():
    years = merged_data_df["YEAR"].unique()
    years.sort()
    current_year = pd.Timestamp.now().year
    return jsonify({'years': years.tolist()})
 
@app.route('/get_weeks_for_year')
def get_weeks():
    year = request.args.get('year', type=int)
    if year is None:
        year = datetime.now().year  # Default to current year if none specified
    weeks = merged_data_df[merged_data_df['YEAR'] == year]['WEEK'].unique()
    weeks.sort()
    return jsonify({'weeks': weeks.tolist()})
   
@app.route('/summary_metrics')
def summary_metrics_route():
    weeks = request.args.getlist('weeks', type=int)
    if not weeks:
        weeks = merged_data_df['WEEK'].unique()
 
    total_transactions, total_savings, active_lp_count = calculate_summary_metrics(merged_data_df, weeks)
    return jsonify({
        'total_transactions': total_transactions,
        'total_savings': total_savings,
        'active_lp_count': active_lp_count
    })
 
@app.route('/set_cookie')
def set_cookie():
    resp = make_response("Cookie Set")
    resp.set_cookie('my_cookie', 'cookie_value', max_age=3600)  
    return resp
 
@app.route('/get_cookie')
def get_cookie():
    cookie_value = request.cookies.get('my_cookie')
    return f'Cookie Value: {cookie_value}'
 
if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port = 5000, debug=True)
    except Exception as e:
        print(f"An error occurred: {e}")