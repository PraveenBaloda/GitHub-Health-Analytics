import pandas as pd
import sqlite3

print("Loading CSV... this will take 1-2 minutes")
df = pd.read_csv('gh_archive_data.csv')
print("Loaded. Rows:", len(df))

# Step 1 - Parse dates
df['date'] = pd.to_datetime(df['date'])
df['merged_at'] = pd.to_datetime(df['merged_at'])
df['closed_at'] = pd.to_datetime(df['closed_at'])

# Step 2 - Fix fake 1970 dates
df.loc[df['merged_at'].dt.year == 1970, 'merged_at'] = None
df.loc[df['closed_at'].dt.year == 1970, 'closed_at'] = None
print("Fixed 1970 dates")

# Step 3 - Flag bots
df['is_bot'] = df['actor'].str.contains(
    'bot|Bot|\[bot\]|robot|mirror', regex=True, na=False
)
print("Bots flagged:", df['is_bot'].sum())

# Step 4 - Add ecosystem labels
ecosystem_map = {
    'facebook/react': 'Frontend',
    'facebook/react-native': 'Frontend',
    'vuejs/vue': 'Frontend',
    'sveltejs/svelte': 'Frontend',
    'angular/angular': 'Frontend',
    'vercel/next.js': 'Frontend',
    'tailwindlabs/tailwindcss': 'Frontend',
    'mui/material-ui': 'Frontend',
    'twbs/bootstrap': 'Frontend',
    'pytorch/pytorch': 'ML/Data',
    'tensorflow/tensorflow': 'ML/Data',
    'keras-team/keras': 'ML/Data',
    'huggingface/transformers': 'ML/Data',
    'microsoft/DeepSpeed': 'ML/Data',
    'ray-project/ray': 'ML/Data',
    'scikit-learn/scikit-learn': 'ML/Data',
    'pandas-dev/pandas': 'ML/Data',
    'numpy/numpy': 'ML/Data',
    'microsoft/vscode': 'Backend/DevOps',
    'kubernetes/kubernetes': 'Backend/DevOps',
    'golang/go': 'Backend/DevOps',
    'elastic/elasticsearch': 'Backend/DevOps',
    'apache/spark': 'Backend/DevOps',
    'hashicorp/terraform': 'Backend/DevOps',
    'ansible/ansible': 'Backend/DevOps',
    'tiangolo/fastapi': 'Backend/DevOps',
    'django/django': 'Backend/DevOps',
    'pallets/flask': 'Backend/DevOps',
    'docker/compose': 'Backend/DevOps',
    'flutter/flutter': 'Frontend',
}
df['ecosystem'] = df['repo'].map(ecosystem_map)
print("Ecosystem nulls:", df['ecosystem'].isna().sum())

# Step 5 - Add year_month column
df['year_month'] = df['date'].dt.to_period('M').astype(str)

# Step 6 - Save to SQLite
print("Saving to SQLite... this will take 2-3 minutes")
conn = sqlite3.connect('github_analytics.db')
df.to_sql('events', conn, if_exists='replace', index=False)
conn.close()

print("ALL DONE")
print("Database saved as github_analytics.db")