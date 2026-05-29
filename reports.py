from datetime import datetime
import sqlite3
import pandas as pd
from config import REPORT_DIR, DATABASE_PATH

def read_table(name):
    conn = sqlite3.connect(DATABASE_PATH)
    try: df = pd.read_sql(f"SELECT * FROM {name}", conn)
    except Exception: df = pd.DataFrame()
    conn.close(); return df

def write_daily_reports():
    REPORT_DIR.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    issues = read_table("issue_clusters")
    if issues.empty: return ""
    path = REPORT_DIR / f"{today}_daily_issues.md"
    issues = issues.sort_values("created_at", ascending=False)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Daily Construction Issues - {today}\n\n")
        for _, row in issues.iterrows():
            f.write(f"## {row['company']} - {row['representative_title']}\n")
            f.write(f"- Category: {row['category']}\n- Sentiment: {row['sentiment']}\n- Importance: {row['importance']} / 5\n- Related articles: {row['article_count']}\n")
            f.write(f"- Summary: {row['issue_summary']}\n\n{row['urls']}\n\n")
    return str(path)

def write_job_alert_report(new_jobs):
    REPORT_DIR.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    path = REPORT_DIR / f"{today}_official_job_alerts.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Official Job Alerts - {today}\n\n")
        if not new_jobs:
            f.write("새 공식 채용공고가 없습니다.\n"); return str(path)
        for job in new_jobs:
            f.write(f"## {job['company']} - {job['title']}\n")
            f.write(f"- Type: {job['job_type']}\n- Start: {job['start_date']}\n- End: {job['end_date']}\n- Status: {job['status']}\n- URL: {job['official_url']}\n- Detail: {job['detail']}\n\n")
    return str(path)
