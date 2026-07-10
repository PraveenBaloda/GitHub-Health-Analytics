import sqlite3
import pandas as pd
import os

# Base paths

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'github_analytics.db')
FEATURES_DIR = os.path.join(BASE_DIR, 'features')


# Database connection

def get_connection():
    """Returns a SQLite connection to the main events database."""
    return sqlite3.connect(DB_PATH)


# Load constants once at startup

conn = get_connection()

REPOS = pd.read_sql(
    "SELECT DISTINCT repo FROM events ORDER BY repo", conn
)['repo'].tolist()

ECOSYSTEMS = ['Frontend', 'ML/Data', 'Backend/DevOps']

MONTHS = pd.read_sql(
    "SELECT DISTINCT year_month FROM events ORDER BY year_month", conn
)['year_month'].tolist()

conn.close()

print(f"Globals loaded successfully")
print(f"Repos: {len(REPOS)}, Months: {len(MONTHS)}")