from dash import Dash, dcc, html
import plotly.express as px
import sqlite3
import pandas as pd

app = Dash(__name__)

# Load repo list for dropdown
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
conn = sqlite3.connect(os.path.join(BASE_DIR, 'github_analytics.db'))
repos = pd.read_sql("SELECT DISTINCT repo FROM events", conn)['repo'].tolist()
conn.close()

app.layout = html.Div([
    html.H1("GitHub Repository Health Analytics"),
    
    # Global filters
    html.Div([
        dcc.Dropdown(
            id='repo-filter',
            options=[{'label': r, 'value': r} for r in repos],
            multi=True,
            placeholder='Select repositories...'
        ),
        dcc.Dropdown(
            id='ecosystem-filter',
            options=[
                {'label': 'Frontend', 'value': 'Frontend'},
                {'label': 'ML/Data', 'value': 'ML/Data'},
                {'label': 'Backend/DevOps', 'value': 'Backend/DevOps'}
            ],
            placeholder='Select ecosystem...'
        )
    ]),
    
    # Placeholder panels
    html.Div([
        dcc.Graph(id='streamgraph'),
        dcc.Graph(id='pr-sankey'),
        dcc.Graph(id='issue-heatmap'),
        dcc.Graph(id='bot-bar'),
        dcc.Graph(id='health-dashboard'),
    ])
])

if __name__ == '__main__':
    app.run(debug=True)