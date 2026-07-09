# Project Progress Log
## GitHub Repository Health Analytics | CS661 | Group __

This document tracks everything we have done so far, 
every decision we made, and why we made it. 
Anyone reading this should be able to understand 
the full project without asking anyone.

---

## Table of Contents
1. [Project Idea and Motivation](#1-project-idea-and-motivation)
2. [Data Source Decision](#2-data-source-decision)
3. [Data Extraction](#3-data-extraction)
4. [Data Overview](#4-data-overview)
5. [Data Cleaning](#5-data-cleaning)
6. [Project Structure](#6-project-structure)
7. [Feature Engineering](#7-feature-engineering)
8. [Tech Stack Decisions](#8-tech-stack-decisions)
9. [File Guide — What to Do in Each File](#9-file-guide--what-to-do-in-each-file)
10. [Current Status](#10-current-status)
11. [What Comes Next](#11-what-comes-next)

---

## 1. Project Idea and Motivation

### What problem are we solving?
Every developer at some point has to decide whether to 
use an open-source library in their project. To make 
that decision, they visit the GitHub page and try to 
judge the project health manually:
- Is it still being maintained?
- How fast do they fix bugs?
- Is only one person doing everything?
- Is the project growing or dying?

Right now this requires checking each repository one 
by one with no structured way to compare across projects.

### What we are building
An interactive web-based visual analytics system that 
lets users explore the health of open-source GitHub 
repositories across multiple dimensions — contributor 
activity, code review efficiency, issue responsiveness, 
technology adoption trends — all in one place with 
cross-filtering between panels.

### Who is it for?
- Open-source maintainers
- Engineering managers evaluating libraries
- Developers deciding which tools to adopt

### Why this topic?
- We are CS students — we already understand every 
  concept in this domain (PRs, issues, contributors). 
  No domain learning curve.
- The data is free and publicly available.
- The questions we are answering are real questions 
  that real engineering teams ask every day.
- Every visualization choice is naturally justified 
  by the question it answers.

---

## 2. Data Source Decision

### What we chose
**GH Archive** (https://gharchive.org)

GH Archive records every public GitHub event since 
2011 in structured JSON format with hourly granularity. 
Google hosts this entire dataset as a public BigQuery 
dataset (`githubarchive.*`), which allows SQL queries 
at no cost (up to 1TB/month free).

### Why not other sources?
- Kaggle datasets are static and often outdated
- GitHub REST API has rate limits (5000 requests/hour) 
  which makes large scale analysis impractical
- GH Archive gives us the complete event stream with 
  no rate limits

### How we verified it works
Before finalizing the data source, we ran a test query 
on Google BigQuery:

```sql
SELECT
  repo.name,
  type,
  COUNT(*) as event_count
FROM `githubarchive.day.20240101`
WHERE repo.name IN (
  'facebook/react',
  'vuejs/vue',
  'tensorflow/tensorflow'
)
GROUP BY repo.name, type
ORDER BY event_count DESC
```

This returned real GitHub data immediately, confirming 
the dataset is accessible and well-structured.

---

## 3. Data Extraction

### What we extracted
We queried the BigQuery public dataset filtering to:
- 30 specific repositories across 3 ecosystems
- 2 year window: January 2023 to December 2024
- 6 event types only

### Event types we kept and why

| Event Type | Why We Need It |
|------------|---------------|
| PullRequestEvent | PR lifecycle, review latency |
| IssuesEvent | Issue responsiveness analysis |
| IssueCommentEvent | Response time, contributor network |
| PushEvent | Commit activity, bus factor |
| WatchEvent | Technology adoption trends |
| ReleaseEvent | Release patterns |

### Repositories selected

**Frontend Ecosystem (9 repos)**
- facebook/react
- facebook/react-native
- vuejs/vue
- sveltejs/svelte
- angular/angular
- vercel/next.js
- tailwindlabs/tailwindcss
- mui/material-ui
- twbs/bootstrap

**ML/Data Ecosystem (9 repos)**
- pytorch/pytorch
- tensorflow/tensorflow
- keras-team/keras
- huggingface/transformers
- microsoft/DeepSpeed
- ray-project/ray
- scikit-learn/scikit-learn
- pandas-dev/pandas
- numpy/numpy

**Backend/DevOps Ecosystem (11 repos)**
- microsoft/vscode
- kubernetes/kubernetes
- golang/go
- elastic/elasticsearch
- apache/spark
- hashicorp/terraform
- ansible/ansible
- tiangolo/fastapi
- django/django
- pallets/flask
- docker/compose
- flutter/flutter

### Output
Raw data saved as `gh_archive_data.csv`

---

## 4. Data Overview

### Basic Statistics

| Property | Value |
|----------|-------|
| Total rows | 3,448,426 |
| Total columns | 10 |
| File size | 485.3 MB |
| Date range | Jan 1 2023 to Dec 31 2024 |
| Unique actors | 520,041 |
| Unique human actors | 519,233 |
| Unique bot actors | 808 |

### Column Descriptions

| Column | Type | Description |
|--------|------|-------------|
| repo | string | Full repo name e.g. facebook/react |
| date | datetime | When the event occurred (UTC) |
| event_type | string | Type of GitHub event |
| actor | string | GitHub username who triggered event |
| action | string | Specific action within event type |
| pr_or_issue_number | integer | PR or issue number |
| closed_at | datetime | When PR/issue was closed |
| merged_at | datetime | When PR was merged |
| state | string | open, closed, or none |
| author_association | string | Actor's relationship to the repo |

### Event Distribution

| Event Type | Count | Percentage |
|------------|-------|------------|
| IssueCommentEvent | 1,555,472 | 45.1% |
| PushEvent | 582,564 | 16.9% |
| WatchEvent | 573,744 | 16.6% |
| PullRequestEvent | 411,496 | 11.9% |
| IssuesEvent | 323,307 | 9.4% |
| ReleaseEvent | 1,843 | 0.1% |

### Events per Ecosystem

| Ecosystem | Repos | Events |
|-----------|-------|--------|
| ML/Data | 9 | 1,345,003 |
| Backend/DevOps | 11 | 1,160,021 |
| Frontend | 9 | 651,205 |

### Top 5 Repos by Activity

| Repository | Events |
|------------|--------|
| pytorch/pytorch | 686,671 |
| microsoft/vscode | 321,380 |
| kubernetes/kubernetes | 300,200 |
| flutter/flutter | 292,197 |
| tensorflow/tensorflow | 177,584 |

### Bot Activity

| Property | Value |
|----------|-------|
| Bot events | 848,909 |
| Human events | 2,599,517 |
| Bot percentage | 24.62% |

Top bots: k8s-ci-robot (148,901), pytorchmergebot 
(126,308), github-actions[bot] (105,592)

### PR Statistics

| Property | Value |
|----------|-------|
| Total PR events | 411,496 |
| Unique PRs | 140,024 |
| Matched open-to-merge pairs | 98,518 |
| Median merge time | 11.5 hours |
| Mean merge time | 149.8 hours |

### Issue Statistics

| Property | Value |
|----------|-------|
| Total issue events | 323,307 |
| Issues opened | 157,887 |
| Issues closed | 152,908 |
| Issues with response data | 134,101 |
| Median response time | 3.9 hours |
| Mean response time | 235.5 hours |

---

## 5. Data Cleaning

### Why cleaning was needed
1. `merged_at` and `closed_at` use `1970-01-01` as a 
   placeholder when the value is null. This breaks any 
   time-based calculation.
2. 24.62% of events are from bot accounts which inflate 
   all activity metrics unfairly.
3. Each row only knows its repo name, not which 
   ecosystem it belongs to. This needs to be added.
4. Date columns are stored as strings in CSV format 
   and need to be parsed as datetime objects.

### What we did

**Step 1 — Parse all date columns**
```python
df['date'] = pd.to_datetime(df['date'])
df['merged_at'] = pd.to_datetime(df['merged_at'])
df['closed_at'] = pd.to_datetime(df['closed_at'])
```

**Step 2 — Fix 1970 placeholder dates**
```python
df.loc[df['merged_at'].dt.year == 1970, 'merged_at'] = None
df.loc[df['closed_at'].dt.year == 1970, 'closed_at'] = None
```

**Step 3 — Flag bot accounts**
```python
df['is_bot'] = df['actor'].str.contains(
    'bot|Bot|\[bot\]|robot|mirror', regex=True, na=False
)
```

**Step 4 — Add ecosystem labels**
Each repo mapped to Frontend, ML/Data, or 
Backend/DevOps ecosystem.

**Step 5 — Add year_month column**
```python
df['year_month'] = df['date'].dt.to_period('M').astype(str)
```

**Step 6 — Save to SQLite database**
```python
conn = sqlite3.connect('github_analytics.db')
df.to_sql('events', conn, if_exists='replace', index=False)
```

### Output
`github_analytics.db` — 500MB SQLite database with 
clean data ready to query.

### Script
See `preprocessing/clean_data.py`

---

## 6. Project Structure
---

## 7. Feature Engineering

### Why we need feature engineering
The raw events table does not directly contain what 
we want to visualize. We need to derive higher level 
metrics from it.

### Features being computed

**PR Latency** (`pr_latency.csv`)
- Match PullRequestEvent with action=opened to 
  PullRequestEvent with action=closed and merged_at set
- Compute difference in hours
- Filter out negative or zero values

**Issue Response Time** (`issue_response.csv`)
- Match IssuesEvent action=opened with earliest 
  IssueCommentEvent on same issue number
- Compute difference in hours

**Bot vs Human Activity** (`bot_activity.csv`)
- Group by repo and year_month
- Separate bot rows from human rows
- Count each separately

**Contributor Network** (`contributor_network.csv`)
- Find all actors who commented on the same PR
- Connect them with an edge
- Weight = number of times they co-collaborated

**Bus Factor** (`bus_factor.csv`)
- Count total push and PR activity per actor per repo
- Sort contributors by activity descending
- Bus factor = minimum people whose removal costs 
  the project 50% of its activity

---

## 7a. Bus Factor — Explained

### What is "bus factor"?
It's a way to measure how risky a project is in terms of 
people. It answers: "If the top contributors got hit by a 
bus tomorrow, how much trouble would this project be in?"

A **low bus factor** (like 1 or 2) means the project depends 
heavily on a tiny number of people. If they left, the project 
would struggle to keep going.

A **high bus factor** means contribution is spread across many 
people, so the project is more resilient — losing a few people 
doesn't hurt much.

### How we calculated it

**Step 1 — Decide what counts as "activity"**
We used two event types as a proxy for real contribution work:
- `PushEvent` (someone pushed code)
- `PullRequestEvent` (someone opened/worked on a PR)

We did NOT include comments, issues, or watches here — those 
measure discussion/interest, not code contribution.

**Step 2 — Remove bots**
Every repo has automated accounts (CI bots, merge bots, release 
bots) that generate huge amounts of fake "activity." We already 
had an `is_bot` column from data cleaning, so we filtered these 
out. Without this step, bots would completely hide the real 
human bus factor.

**Step 3 — Count activity per person, per repo**
For each repo, we counted how many push/PR events each human 
contributor made.

**Step 4 — Sort and find the tipping point**
We sorted contributors from most active to least active, then 
added them up one by one until we crossed 50% of the repo's 
total activity. The number of people it took to cross that 
line is the bus factor.

Example: if a repo's top 3 contributors together made 50%+ of 
all push/PR activity, the bus factor is 3.

### The code

```python
import pandas as pd
import sqlite3

conn = sqlite3.connect('github_analytics.db')

query = """
SELECT repo, actor
FROM events
WHERE event_type IN ('PushEvent', 'PullRequestEvent')
  AND is_bot = 0
"""
df = pd.read_sql(query, conn)
conn.close()

activity = (
    df.groupby(['repo', 'actor'])
      .size()
      .reset_index(name='activity_count')
)

def compute_bus_factor(group):
    sorted_group = group.sort_values(
        'activity_count', ascending=False
    ).reset_index(drop=True)
    total = sorted_group['activity_count'].sum()
    threshold = total * 0.5
    cumulative = 0
    for i, row in sorted_group.iterrows():
        cumulative += row['activity_count']
        if cumulative >= threshold:
            return i + 1
    return len(sorted_group)

bus_factor_results = []
for repo, group in activity.groupby('repo'):
    bf = compute_bus_factor(group)
    bus_factor_results.append({
        'repo': repo,
        'bus_factor': bf,
        'total_contributors': group['actor'].nunique(),
        'total_activity': group['activity_count'].sum()
    })

bus_factor_df = pd.DataFrame(
    bus_factor_results
).sort_values('bus_factor')
bus_factor_df.to_csv('bus_factor.csv', index=False)
```

### Output
`features/bus_factor.csv` — one row per repo, with:

| Column | Meaning |
|--------|---------|
| repo | repo name |
| bus_factor | min people whose removal costs 50%+ activity |
| total_contributors | unique human contributors |
| total_activity | total push/PR events (bots excluded) |

### Interesting findings
- `tiangolo/fastapi`, `keras-team/keras`, `pallets/flask`: 
  bus_factor 1 — one maintainer holds everything together
- `pytorch/pytorch`: bus_factor 29 out of 2266 contributors
- `kubernetes/kubernetes`: bus_factor 56 — very well distributed

### Scripts
See `features/feature_engineering.py`

---

## 8. Tech Stack Decisions

### Why Plotly Dash and not React + D3
- Entire app in Python — no JavaScript needed
- Everyone on the team knows Python
- Dash has built-in cross-filtering support
- Plotly charts are interactive by default
- Dash-Cytoscape handles network graphs in Python

### Why SQLite and not PostgreSQL
- No server setup needed
- Single file database
- Fast enough for 3.4 million rows
- Works on every laptop without configuration

### Why BigQuery for extraction
- GH Archive is already hosted there as a public dataset
- Free up to 1TB/month
- SQL interface — easy to filter exactly what we need
- No scraping, no API limits

### Full stack

| Component | Technology | Reason |
|-----------|------------|--------|
| Data extraction | Google BigQuery | Free, fast, SQL |
| Data processing | Python, Pandas, NumPy | Everyone knows it |
| Graph metrics | NetworkX | Best Python graph library |
| Database | SQLite | Simple, no setup |
| App and charts | Plotly Dash | Python only, interactive |
| Network graph | Dash-Cytoscape | Force directed in Python |

---

## 9. File Guide — What to Do in Each File

This section tells every team member exactly what 
needs to be written in each file.

---

### `app/globals.py`


This file runs once when the app starts. It sets up 
the shared database connection and loads constants 
that every other file needs.

What to put here:
- Path to `github_analytics.db`
- A `get_connection()` function that returns a SQLite connection
- `REPOS` list — all 30 repo names loaded from the database
- `ECOSYSTEMS` list — ['Frontend', 'ML/Data', 'Backend/DevOps']
- `MONTHS` list — all year_month values from the database

Every other file imports from here. Do not duplicate 
these values anywhere else.

---

### `src/data_loader.py`


This file contains all the functions that query the 
database. No other file should write raw SQL — they 
all call functions from here.

Functions to write:
- `load_events(repos, ecosystem, start_month, end_month, include_bots)`
  → returns filtered rows from the events table
- `load_pr_latency(repos)` 
  → returns rows from pr_latency table
- `load_issue_response(repos)` 
  → returns rows from issue_response table
- `load_bot_activity(repos)` 
  → returns rows from bot_activity table
- `load_bus_factor(repos)` 
  → returns rows from bus_factor table
- `load_contributor_network(repo)` 
  → returns edges from contributor_network table

---

### `src/analytics.py`


This file contains helper functions that compute 
derived metrics from raw DataFrames. These functions 
are called by the callbacks before plotting.

Functions to write:
- `compute_monthly_activity(df)` 
  → group events by repo and month, return counts
- `compute_ecosystem_monthly(df)` 
  → group events by ecosystem and month, return counts
- `compute_health_summary(repos, pr_df, issue_df, bot_df, bf_df)` 
  → compute one-row-per-repo summary table for dashboard
- `get_pr_stage_counts(df)` 
  → count PRs at each stage (opened, merged, closed) for Sankey

---

### `app/components/layout.py`


This file defines the visual structure of the entire 
page. Think of it as the HTML skeleton.

What to write:
- `create_filters()` function
  → Returns the top filter bar with repo dropdown, 
    ecosystem dropdown, date range slider, bot toggle
- `create_panels()` function  
  → Returns the six chart panels arranged in a 3-row 
    2-column grid. Each panel has a title and a 
    `dcc.Graph` with an id that callbacks will target.

Chart IDs that must match callbacks exactly:
- `streamgraph`
- `network-graph`
- `pr-sankey`
- `issue-heatmap`
- `bot-bar`
- `health-dashboard`

---

### `app/components/filters.py`


Small helper functions for processing filter values.

What to write:
- `get_month_range(slider_values)` 
  → converts slider [0, 23] to ('2023-01', '2024-12')

---

### `app/callbacks/streamgraph_cb.py`


Visualization: Technology Adoption Trends  
Chart type: Stacked area chart (streamgraph)  
Why this chart: Shows how relative activity proportions 
shift across ecosystems over time — a line chart cannot 
show this clearly when multiple series are stacked.

What to write:
- One `@app.callback` that reads from repo-filter, 
  ecosystem-filter, month-slider, bot-toggle
- Calls `load_events()` then `compute_ecosystem_monthly()`
- Builds a `go.Scatter` with `stackgroup='one'` for each 
  ecosystem — one trace per ecosystem
- Returns the figure to the `streamgraph` output

---

### `app/callbacks/network_cb.py`


Visualization: Contributor Collaboration Network  
Chart type: Force-directed network graph  
Why this chart: Reveals contributor clusters and central 
nodes organically — no table or bar chart can show network 
structure.

What to write:
- One `@app.callback` that reads from repo-filter
- Calls `load_contributor_network(repo)` for the first 
  selected repo
- Uses NetworkX to compute node positions 
  (`nx.spring_layout`)
- Builds a plotly figure with edges as `go.Scatter` lines 
  and nodes as `go.Scatter` markers
- Node size = how many edges (degree centrality)
- Node color = red if bus_factor risk, green otherwise
- Returns figure to `network-graph` output

---

### `app/callbacks/sankey_cb.py`


Visualization: PR Lifecycle and Review Latency  
Chart type: Sankey diagram + box plots  
Why this chart: Sankey shows where PRs drop off or stall 
at each stage — something a histogram alone cannot show.

What to write:
- One `@app.callback` reading repo-filter, month-slider, 
  bot-toggle
- Calls `load_events()` then `get_pr_stage_counts()`
- Builds `go.Sankey` with three nodes:
  - Opened → Merged
  - Opened → Closed Without Merge
- Also add a box plot of merge latency from 
  `load_pr_latency()` as a second subplot
- Returns figure to `pr-sankey` output

---

### `app/callbacks/heatmap_cb.py`


Visualization: Issue Responsiveness Calendar Heatmap  
Chart type: Calendar heatmap  
Why this chart: Gaps in daily activity immediately signal 
maintainer inactivity — a line chart would hide these gaps.

What to write:
- One `@app.callback` reading repo-filter, month-slider
- Calls `load_events()`, filters to IssuesEvent and 
  IssueCommentEvent only
- Groups by date to get daily counts
- Builds a `go.Heatmap` where:
  - x = week of year
  - y = day of week (Mon-Sun)
  - z = number of issue events that day
- Returns figure to `issue-heatmap` output

---

### `app/callbacks/bot_bar_cb.py`


Visualization: Bot vs Human Activity  
Chart type: Stacked bar chart  
Why this chart: Shows the exact split of automated vs 
real human activity per repo — critical for understanding 
whether activity metrics are honest.

What to write:
- One `@app.callback` reading repo-filter, month-slider
- Calls `load_bot_activity(repos)`
- Aggregates bot_events and human_events per repo
- Builds `go.Bar` with two traces — one for human 
  (blue), one for bot (red) — with `barmode='stack'`
- Returns figure to `bot-bar` output

---

### `app/callbacks/dashboard_cb.py`


Visualization: Repository Health Summary Dashboard  
Chart type: KPI table or indicator cards  
Why this chart: Synthesizes all metrics into one 
comparable view so users can evaluate repos side by 
side in seconds.

Build this LAST — it depends on all other features 
being ready in the database.

What to write:
- One `@app.callback` reading repo-filter
- Calls `load_pr_latency()`, `load_issue_response()`, 
  `load_bot_activity()`, `load_bus_factor()`
- Calls `compute_health_summary()` from analytics.py
- Builds a `go.Table` showing one row per repo with:
  - Median merge time
  - Median issue response time  
  - Bus factor score
  - Bot activity percentage
- Returns figure to `health-dashboard` output

---

### `app/app.py`


This is the entry point. It should be short and clean.

What to write:
- Initialize the Dash app
- Import layout functions from components/layout.py
- Set `app.layout` using `create_filters()` and 
  `create_panels()`
- Import and call `register(app)` from every callback file
- `if __name__ == '__main__': app.run(debug=True)`

---

### `visualizations/`
**Owner: Everyone**

Put EDA plots and screenshots here as the project progresses.

What goes here:
- EDA plots (event distribution, monthly trends, bot 
  percentages) as PNG files
- Screenshots of the working app panels once built
- These will be used in the final report

---



## 11. What Comes Next

### Build order for visualizations
Build in this order — easiest to hardest:

1. `bot_bar_cb.py` — just counts, simplest chart
2. `streamgraph_cb.py` — monthly aggregation, stacked area
3. `heatmap_cb.py` — daily grouping, calendar layout
4. `sankey_cb.py` — needs pr_latency table ready
5. `network_cb.py` — needs contributor_network table + NetworkX
6. `dashboard_cb.py` — built last, depends on everything else

### How to combine everyone's work
- Each person writes their callback file independently
- Person 6 or 7 imports all callbacks in `app.py`
- Feature CSV files are pushed to GitHub by each person
- Person 1 or 2 loads all CSVs into the database and 
  shares the updated database on Google Drive

### Final deliverables
- Working web application
- Project report in LaTeX
- GitHub repository with all code
- Live demo during final exam week

---

*Last updated: July 2026*  
*Update the status table whenever a task is completed*