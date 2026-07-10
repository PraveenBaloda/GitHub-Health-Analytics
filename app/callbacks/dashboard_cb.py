from dash import Input, Output
import plotly.graph_objects as go
import pandas as pd
from src.data_loader import load_pr_latency, load_issue_response, load_bot_activity, load_bus_factor
from src.analytics import compute_health_summary

def _fmt(val, suffix=''):
    return 'N/A' if pd.isna(val) else f"{val}{suffix}"

def register(app):
    @app.callback(
        Output('health-dashboard', 'figure'),
        Input('repo-filter', 'value')
    )
    def update_health_dashboard(selected_repos):
        if not selected_repos:
            return go.Figure(layout=dict(title="Select at least one repository to view its health summary"))

        pr_df = load_pr_latency(selected_repos)
        issue_df = load_issue_response(selected_repos)
        bot_df = load_bot_activity(selected_repos)
        bf_df = load_bus_factor(selected_repos)

        summary = compute_health_summary(selected_repos, pr_df, issue_df, bot_df, bf_df)
        
        if summary.empty:
            return go.Figure(layout=dict(title="No data found for the selected repositories"))

        col_values = [
            list(summary['repo']),
            [_fmt(v) for v in summary['median_merge_hours']],
            [_fmt(v) for v in summary['median_response_hours']],
            [_fmt(v) for v in summary['bus_factor']],
            [_fmt(v, '%') for v in summary['bot_percentage']],
        ]

        n_rows = len(summary)
        row_colors = ['#f9fafb' if i % 2 == 0 else '#ffffff' for i in range(n_rows)]

        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['Repository', 'Median Merge Time (hrs)', 'Median Issue Response (hrs)', 'Bus Factor', 'Bot Activity %'],
                fill_color='#1f2937', font=dict(color='white', size=12), align='left'
            ),
            cells=dict(values=col_values, fill_color=[row_colors] * len(col_values), align='left')
        )])
        fig.update_layout(title='Repository Health Summary', template='plotly_white', margin=dict(t=50, b=20, l=20, r=20))
        return fig
