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
9. [Current Status](#9-current-status)
10. [What Comes Next](#10-what-comes-next)

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
GitHub-Health-Analytics-CS661/
├── app/
│   └── app.py                    # Main Dash application
├── features/
│   ├── feature_engineering.py    # Feature computation scripts
│   ├── bus_factor.csv            # Bus factor per repo
│   ├── pr_latency.csv            # PR merge latency
│   ├── issue_response.csv        # Issue response times
│   ├── contributor_network.csv   # Contributor edges
│   └── bot_activity.csv          # Bot vs human monthly
├── preprocessing/
│   └── clean_data.py             # Data cleaning script
├── requirements.txt
├── README.md
└── PROGRESS.md                   # This file





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



