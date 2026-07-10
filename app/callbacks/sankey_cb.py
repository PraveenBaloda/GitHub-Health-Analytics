from dash import Input, Output
import plotly.graph_objects as go
from src.data_loader import load_events, load_pr_latency
from src.analytics import get_pr_stage_counts
from app.components.filters import get_month_range

def register(app):
    @app.callback(
        Output('pr-sankey', 'figure'),
        [Input('repo-filter', 'value'), Input('month-slider', 'value'), Input('bot-toggle', 'value')]
    )
    def update_sankey(selected_repos, month_range, include_bots):
        start_month, end_month = get_month_range(month_range)
        include_bots_bool = bool(include_bots)
        
        df_events = load_events(repos=selected_repos, start_month=start_month, end_month=end_month, include_bots=include_bots_bool)
        if df_events.empty:
            return go.Figure(layout=dict(title="No events data found matching filters"))
            
        stage_counts = get_pr_stage_counts(df_events)
        
        df_latency = load_pr_latency(selected_repos)
        if not df_latency.empty:
            df_latency = df_latency[(df_latency['month'] >= start_month) & (df_latency['month'] <= end_month)]
        
        label = ["Opened PRs", "Merged", "Closed Without Merge"]
        color = ["#94a3b8", "#10b981", "#ef4444"]
        source = [0, 0]
        target = [1, 2]
        value = [stage_counts['merged'], stage_counts['closed_without_merge']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Sankey(
            domain=dict(x=[0, 0.48], y=[0, 1]),
            node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=label, color=color),
            link=dict(source=source, target=target, value=value, color=["rgba(16, 185, 129, 0.2)", "rgba(239, 68, 68, 0.2)"])
        ))
        
        if not df_latency.empty:
            fig.add_trace(go.Box(
                y=df_latency['latency_hours'],
                x=df_latency['repo'] if len(selected_repos) > 1 else None,
                name="Merge Latency", marker_color='#1f77b4', boxpoints='outliers', xaxis='x2', yaxis='y2'
            ))
            
        fig.update_layout(
            title_text="PR Lifecycle Flow & Review Latency",
            xaxis2=dict(domain=[0.58, 1.0], title="Repository" if len(selected_repos) > 1 else "", showgrid=True),
            yaxis2=dict(domain=[0, 1], title="Hours to Merge", anchor='x2', showgrid=True),
            template='plotly_white', showlegend=False, height=320
        )
        return fig
