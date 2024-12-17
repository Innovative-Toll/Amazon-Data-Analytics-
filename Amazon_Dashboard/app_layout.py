import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from config import AppConfig
from data_processing import (
    load_data, clean_column_names, map_lifecycle_state,
    calculate_savings, calculate_summary_metrics, group_lp_status_weekly,
    filter_and_group_toll_transactions, group_active_lp_sources_weekly,
    read_sla_trend_data
)
from visualization import (
    plot_lp_status_weekly, plot_toll_transactions, plot_active_lp_sources, plot_sla_trend_bar,
    plot_lp_count_weekly, toll_transactions_line_plot, plot_active_lp_sources_trend,
    plot_sla_trend_line, plot_savings_trend
)

# Load and process data
data = load_data(AppConfig.DATA_FILE_PATH)
merged_data = clean_column_names(data)
merged_data = map_lifecycle_state(merged_data)

# Calculate metrics
weekly_savings_summary = calculate_savings(merged_data)
lp_status_weekly = group_lp_status_weekly(merged_data)
toll_transactions_weekly = filter_and_group_toll_transactions(merged_data)
active_lp_weekly = group_active_lp_sources_weekly(merged_data)
sla_trend_df = read_sla_trend_data(merged_data)
unique_weeks = sorted(merged_data['WEEK'].unique())

# Create dropdown options for weeks
week_options = [{'label': str(week), 'value': week} for week in unique_weeks]

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, 'style.css'])

# App layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        dbc.Row(
            dbc.Col(
                dbc.Card(
                    dbc.CardBody(
                        html.Div(
                            className='summary-row',
                            children=[
                                html.Div(
                                    className='summary-metric',
                                    children=[
                                        html.Img(src="savings_icon.png", className='icon'),
                                        html.P(id='total-transactions', className='summary-stat')
                                    ]
                                ),
                                html.Div(
                                    className='summary-metric',
                                    children=[
                                        html.Img(src="average_icon.png", className='icon'),
                                        html.P(id='average-savings', className='summary-stat')
                                    ]
                                ),
                                html.Div(
                                    className='summary-metric',
                                    children=[
                                        html.Img(src="license_plate_icon.png", className='icon'),
                                        html.P(id='active-lp-count', className='summary-stat')
                                    ]
                                )
                            ]
                        )
                    ),
                    style={'background-color': 'rgba(0, 51, 102, 0.5)', 'margin-bottom': '20px'}
                ),
                width=12
            )
        ),
        dbc.Row(
            dbc.Col(
                html.H1(
                    "Amazon Weekly Report - Data Analysis Dashboard",
                    style={'text-align': 'center', 'font-family': 'Arial, sans-serif'}
                ),
                style={'margin-bottom': '20px'}
            )
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    dbc.Card(
                        style={'background-color': 'rgba(0, 51, 102, 0.5)', 'margin-bottom': '20px'},
                        children=[
                            dbc.CardHeader(html.H4("Filters", style={'color': '#FFFFFF'})),
                            dbc.CardBody(
                                children=[
                                    html.Label('Week:', style={'color': '#FFFFFF'}),
                                    dcc.Dropdown(
                                        id='week-dropdown',
                                        options=week_options,
                                        value=unique_weeks[:1],
                                        multi=True,
                                        style={'margin-bottom': '10px', 'color': 'black'}
                                    ),
                                    html.Label('Lifecycle State:', style={'color': '#FFFFFF'}),
                                    dcc.Dropdown(
                                        id='lifecycle-state-dropdown',
                                        options=[{'label': state, 'value': state} for state in merged_data['Lifecycle state'].unique()],
                                        multi=True,
                                        style={'margin-bottom': '10px', 'color': 'black'}
                                    ),
                                    html.Label('Source:', style={'color': '#FFFFFF'}),
                                    dcc.Dropdown(
                                        id='source-dropdown',
                                        options=[{'label': source, 'value': source} for source in merged_data['SOURCE'].unique()],
                                        multi=True,
                                        style={'margin-bottom': '10px', 'color': 'black'}
                                    ),
                                    html.Label('Transaction Type:', style={'color': '#FFFFFF'}),
                                    dcc.Dropdown(
                                        id='transaction-type-dropdown',
                                        options=[{'label': transaction, 'value': transaction} for transaction in merged_data['TRANSACTION TYPE'].unique()],
                                        multi=True,
                                        style={'margin-bottom': '10px', 'color': 'black'}
                                    )
                                ]
                            )
                        ]
                    ),
                    width=3
                ),
                dbc.Col(
                    children=[
                        dbc.Card(
                            style={'background-color': 'rgba(0, 51, 102, 0.5)', 'margin-bottom': '20px'},
                            children=[
                                html.Div(id='visualization-output', style={'height': '80vh', 'overflow': 'auto'}),
                                dbc.Button('Show Live Trend', id='plot-toggle-button', n_clicks=0, color='success', className='mt-3'),
                                dbc.Button('Clear Filters', id='clear-filters-button', n_clicks=0, color='danger', className='mt-3')
                            ]
                        )
                    ],
                    width=9
                )
            ]
        )
    ]
)

# Update visualization callback
@app.callback(
    Output('visualization-output', 'children'),
    Input('plot-toggle-button', 'n_clicks'),
    Input('clear-filters-button', 'n_clicks'),
    Input('week-dropdown', 'value'),
    State('plot-toggle-button', 'n_clicks')
)
def update_visualization(button_clicks, clear_clicks, selected_weeks, prev_button_clicks):
    ctx = dash.callback_context
    option_triggered = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    if option_triggered == 'clear-filters-button':
        selected_weeks = unique_weeks[:1]

    if option_triggered == 'clear-filters-button' or button_clicks % 2 == 0:
        return html.Div(
            children=[
                html.Div(
                    children=[
                        dcc.Graph(figure=plot_lp_status_weekly(lp_status_weekly, selected_weeks)),
                        dcc.Graph(figure=plot_toll_transactions(toll_transactions_weekly, selected_weeks))
                    ],
                    style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center'}
                ),
                html.Div(
                    children=[
                        dcc.Graph(figure=plot_active_lp_sources(active_lp_weekly, selected_weeks)),
                        dcc.Graph(figure=plot_sla_trend_bar(sla_trend_df, selected_weeks))
                    ],
                    style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center'}
                )
            ]
        )
    else:
        return html.Div(
            children=[
                html.Div(
                    children=[
                        dcc.Graph(figure=plot_lp_count_weekly(lp_status_weekly)),
                        dcc.Graph(figure=toll_transactions_line_plot(toll_transactions_weekly))
                    ],
                    style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center'}
                ),
                html.Div(
                    children=[
                        dcc.Graph(figure=plot_active_lp_sources_trend(active_lp_weekly)),
                        dcc.Graph(figure=plot_savings_trend(weekly_savings_summary))
                    ],
                    style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center'}
                ),
                html.Div(
                    children=[
                        dcc.Graph(figure=plot_sla_trend_line(sla_trend_df))
                    ],
                    style={'display': 'flex', 'flex-direction': 'row', 'justify-content': 'center'}
                )
            ]
        )

# Update button text callback
@app.callback(
    Output('plot-toggle-button', 'children'),
    Input('plot-toggle-button', 'n_clicks')
)
def update_button_text(n_clicks):
    return 'Show Line Plot' if n_clicks % 2 == 0 else 'View Bar Plot'

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, port=5087)
