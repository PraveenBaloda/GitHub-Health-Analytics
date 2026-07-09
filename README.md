# GitHub Repository Health Analytics
### CS661: Big Data Visual Analytics

An interactive web-based visual analytics system that analyzes the health 
and collaboration patterns of open-source GitHub repositories. The system 
helps developers, engineering managers, and open-source maintainers 
understand project health by visualizing contributor activity, code review 
efficiency, issue responsiveness, and technology adoption trends.

---

## Project Structure
GitHub-Health-Analytics-CS661/
├── app/
│   └── app.py                  # Main Dash web application
├── features/
│   └── feature_engineering.py  # PR latency, bus factor, bot detection
├── preprocessing/
│   └── clean_data.py           # Data cleaning and SQLite database creation
├── requirements.txt
└── README.md

---

## Dataset

- **Source:** GH Archive (https://gharchive.org) via Google BigQuery
- **Size:** 485MB, 3.4 million rows
- **Period:** January 2023 – December 2024
- **Repositories:** 30 repos across 3 ecosystems
  - Frontend: React, Vue, Svelte, Angular, Next.js, Tailwind, Material-UI, Bootstrap, React Native
  - ML/Data: PyTorch, TensorFlow, Keras, HuggingFace, DeepSpeed, Ray, scikit-learn, pandas, NumPy
  - Backend/DevOps: VSCode, Kubernetes, Go, Elasticsearch, Spark, Terraform, Ansible, FastAPI, Django, Flask, Docker Compose

> The dataset file (`gh_archive_data.csv`) and database (`github_analytics.db`) 
> are not included in this repository due to size limits.  
> Download from: [Google Drive Link Here]

---

## Setup and Installation

### 1. Clone the repository
git clone https://github.com/virendrakala/GitHub-Health-Analytics-CS661-.git
cd GitHub-Health-Analytics-CS661

### 2. Install dependencies
pip3 install -r requirements.txt

### 3. Download the data
Download `gh_archive_data.csv` from the Google Drive link above and place 
it in the root project folder.

### 4. Run data cleaning
This will create the cleaned `github_analytics.db` SQLite database.
python3 preprocessing/clean_data.py
Expected output:
Loading CSV... this will take 1-2 minutes
Loaded. Rows: 3448426
Fixed 1970 dates
Bots flagged: 848909
Ecosystem nulls: 0
Saving to SQLite... this will take 2-3 minutes
ALL DONE
Database saved as github_analytics.db

### 5. Run feature engineering
python3 features/feature_engineering.py

### 6. Run the app
python3 app/app.py
Open your browser and go to: `http://127.0.0.1:8050`

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Data Extraction | Google BigQuery |
| Data Processing | Python, Pandas, NumPy, NetworkX |
| Database | SQLite |
| Visualization | Plotly, Dash, Dash-Cytoscape |

---

## Visualizations

1. **Technology Adoption Streamgraph** — Monthly activity trends across ecosystems
2. **Contributor Collaboration Network** — Force-directed graph with bus-factor scoring
3. **PR Lifecycle Sankey + Box Plots** — Code review stages and merge latency
4. **Issue Responsiveness Heatmap** — Calendar heatmap of daily issue activity
5. **Bot vs Human Activity** — Stacked bar chart with global bot toggle
6. **Repository Health Dashboard** — KPI summary cards with cross-filtering

---
## Course Details

- **Course:** CS661 Big Data Visual Analytics
- **Instructor:** Prof. Soumya Dutta
- **Institute:** IIT Kanpur
- **Semester:** 2025-26
