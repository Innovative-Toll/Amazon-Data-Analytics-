
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def plot_lp_status_weekly(lp_status_weekly, weeks):
    filtered_data = lp_status_weekly[lp_status_weekly['WEEK'].isin(weeks)]
    filtered_data_melted = pd.melt(filtered_data, id_vars=['WEEK'], value_vars=['Active', 'End of Life','Unknown State'], var_name='Lifecycle state', value_name='Number of LPs')

    fig = px.bar(filtered_data_melted, x='WEEK', y='Number of LPs', color='Lifecycle state', barmode='group',
                 title=f'LP Lifecycle Status for Selected Weeks',
                 labels={'Number of LPs': 'Number of LPs', 'WEEK': 'Week', 'Lifecycle state': 'Lifecycle State'},
                 color_discrete_map={'Active': '#2ca02c', 'End of Life': '#1f77b4', 'Unknown State': '#9467bd'})

    fig.update_traces(hovertemplate='%{y}<extra></extra>', base=None)
    fig.update_layout(xaxis=dict(tickmode='array', tickvals=weeks, ticktext=[str(week) for week in weeks]))

    return fig

def plot_toll_transactions(toll_transactions_weekly, weeks):
    filtered_data = toll_transactions_weekly[(toll_transactions_weekly['WEEK'].isin(weeks)) & (toll_transactions_weekly['TRANSACTION TYPE'].isin(['Transponder Toll', 'Plate Toll']))]
    fig = px.bar(filtered_data, x='WEEK', y='Count', color='TRANSACTION TYPE', barmode='group',
                 title=f'Toll Transactions for Active LICENSE PLATE IDs for Selected Weeks (Power Units Only)',
                 labels={'Count': 'Number of Transactions', 'WEEK': 'Week', 'TRANSACTION TYPE': 'Transaction Type'},
                 color_discrete_map={'Transponder Toll': '#2ca02c', 'Plate Toll': '#1f77b4'})

    fig.update_traces(hovertemplate='%{y}<extra></extra>', base=None)
    fig.update_layout(xaxis=dict(tickmode='array', tickvals=weeks, ticktext=[str(week) for week in weeks]))

    return fig

def plot_active_lp_sources(active_lp_weekly, weeks):
    filtered_data = active_lp_weekly[(active_lp_weekly['WEEK'].isin(weeks)) & (active_lp_weekly['SOURCE'] != 'CITATION')]
    colors = ['#2ca02c', '#1f77b4', '#9467bd']
    fig = px.bar(filtered_data, x='WEEK', y='Count', color='SOURCE', barmode='group',
                 title=f'Active Status for SRTs VS Electronic Tolls for Selected Weeks',
                 labels={'Count': 'Number of Active LPs', 'WEEK': 'Week', 'SOURCE': 'Source'},
                 color_discrete_map={source: color for source, color in zip(filtered_data['SOURCE'].unique(), colors)})

    fig.update_traces(hovertemplate='%{y}<extra></extra>', base=None)
    fig.update_layout(xaxis=dict(tickmode='array', tickvals=weeks, ticktext=[str(week) for week in weeks]))

    return fig

def plot_sla_trend_bar(sla_trend_df, weeks):
    filtered_data = sla_trend_df[sla_trend_df['WEEK'].isin(weeks)]
    fig = px.bar(filtered_data, x='WEEK', y='Count', color='SLA MET', barmode='group',
                 title=f'SLA Data for Selected Weeks',
                 labels={'Count': 'Number of Transactions', 'WEEK': 'Week', 'SLA MET': 'SLA Status'},
                 color_discrete_map={'Within SLA': '#2ca02c', 'Outside SLA': '#1f77b4'})

    fig.update_traces(hovertemplate='%{y}<extra></extra>', base=None)
    fig.update_layout(xaxis=dict(tickmode='array', tickvals=weeks, ticktext=[str(week) for week in weeks]))

    return fig

def plot_lp_count_weekly(lp_status_weekly):
    fig = px.line(lp_status_weekly, x='WEEK', y=['Active', 'End of Life','Unknown State'],
                  title='LP Count Week Over Week(Active & End of Life)',
                  labels={'value': 'Number of LPs', 'WEEK': 'Week', 'variable': 'Lifecycle State'},
                  color_discrete_map={'Active': '#2ca02c', 'End of Life': '#1f77b4'})  # Change color mapping here
    fig.update_traces(mode='lines+markers')

    fig.update_traces(hovertemplate='week %{x} <br>%{y}<extra></extra>')
    return fig

def toll_transactions_line_plot(toll_transactions_weekly):
    filtered_data = toll_transactions_weekly[toll_transactions_weekly['TRANSACTION TYPE'].isin(['Transponder Toll', 'Plate Toll'])]
    fig = px.line(filtered_data, x='WEEK', y='Count',
                 title='Count of Active LICENSE PLATEs(Power Units Only) based on Transaction Type',
                 labels={'Count': 'Number of Transactions', 'WEEK': 'Week'},
                 color='TRANSACTION TYPE',
                 color_discrete_map={'Transponder Toll': '#2ca02c', 'Plate Toll': '#1f77b4'})  # Change color mapping here

    fig.update_traces(hovertemplate='week %{x} <br>%{y}<extra></extra>')
    return fig

def plot_active_lp_sources_trend(active_lp_weekly):
    traces = []
    for source, data in active_lp_weekly[active_lp_weekly['SOURCE'] != 'CITATION'].groupby('SOURCE'):
        trace = go.Scatter(x=data['WEEK'], y=data['Count'], mode='lines', name=f'Trend - {source}')
        traces.append(trace)

    layout = go.Layout(
        title='Trend of Active LICENSE PLATEs by Source',
        xaxis=dict(title='Week'),
        yaxis=dict(title='Number of Active LPs')
    )

    fig = go.Figure(data=traces, layout=layout)

    fig.update_traces(hovertemplate='week %{x} <br> %{y}<extra></extra>')
    return fig

def plot_sla_trend_line(sla_trend_df):
    fig = px.line(sla_trend_df, x='WEEK', y='Count', color='SLA MET', 
                  title='SLA Trend Over Time',
                  labels={'Count': 'Number of Transactions', 'WEEK': 'Week', 'SLA MET': 'SLA Status'},
                  color_discrete_map={'Within SLA': '#2ca02c', 'Outside SLA': '#1f77b4'})
    fig.update_traces(mode='lines+markers')

    fig.update_traces(hovertemplate='week %{x} <br>%{y}<extra></extra>')
    return fig

def calculate_savings(merged_data_df):
    merged_data_df['Savings'] = merged_data_df['HIGH RATES'] - merged_data_df['AMOUNT']
    weekly_savings_summary = merged_data_df.groupby('WEEK')['Savings'].agg(['sum', 'mean']).reset_index()
    weekly_savings_summary.columns = ['Week', 'Total Savings', 'Average Savings']
    return weekly_savings_summary

def plot_savings_trend(weekly_savings_summary):
    fig = px.line(weekly_savings_summary, x='Week', y=['Total Savings', 'Average Savings'], title='Savings Trend Over Time',
                  labels={'value': 'Amount ($)', 'Week': 'Week'},
                  color_discrete_map={'Total Savings': '#1f77b4', 'Average Savings': 'green'})
    fig.update_yaxes(tickprefix="$", tickformat=",")  # Format y-axis tick labels as dollars
    fig.update_traces(mode='lines+markers', hovertemplate='week %{x} <br> $%{y:,.2f}<extra></extra>')  # Update hover information
    return fig