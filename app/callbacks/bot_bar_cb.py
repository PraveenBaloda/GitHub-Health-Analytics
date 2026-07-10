from dash import Input, Output
import plotly.graph_objects as go
import pandas as pd
from src.data_loader import load_bot_activity
from app.components.filters import get_month_range

def register(app):
    @app.callback(
        Output('bot-bar', 'figure'),
        [Input('repo-filter', 'value'), Input('month-slider', 'value')]
    )
    def update_bot_bar(selected_repos, month_range):
        start_month, end_month = get_month_range(month_range)
        
        df = load_bot_activity(selected_repos)
        if df.empty:
            return go.Figure(layout=dict(title="No activity data found matching filters"))
            
        df = df[(df['year_month'] >= start_month) & (df['year_month'] <= end_month)]
        if df.empty:
            return go.Figure(layout=dict(title="No activity data found in selected month range"))
            
        grouped = df.groupby(['repo', 'is_bot'])['event_count'].sum().reset_index()
        pivot_df = grouped.pivot(index='repo', columns='is_bot', values='event_count').fillna(0)
        
        human_col = bot_col = None
        for col in pivot_df.columns:
            if str(col) in ['0', 'False', '0.0', 'false']: human_col = col
            elif str(col) in ['1', 'True', '1.0', 'true']: bot_col = col
            
        human_events = pivot_df[human_col] if human_col is not None else pd.Series(0, index=pivot_df.index)
        bot_events = pivot_df[bot_col] if bot_col is not None else pd.Series(0, index=pivot_df.index)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=pivot_df.index, y=human_events, name='Human Activity', marker_color='#1f77b4'))
        fig.add_trace(go.Bar(x=pivot_df.index, y=bot_events, name='Bot Activity', marker_color='#d62728'))
        
        fig.update_layout(
            barmode='stack', title='Bot vs. Human Activity Volume',
            xaxis_title='Repository', yaxis_title='Total Event Count',
            template='plotly_white', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig
