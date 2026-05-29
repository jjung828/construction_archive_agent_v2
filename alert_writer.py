from pathlib import Path
from datetime import datetime
from config import REPORT_DIR

def write_job_alerts(new_jobs):
    REPORT_DIR.mkdir(exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    path = REPORT_DIR / f"{today}_job_alerts.md"

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Job Alerts - {today}\n\n")

        if not new_jobs:
            f.write("새 채용공고가 없습니다.\n")
            return str(path)

        for idx, job in enumerate(new_jobs, start=1):
            f.write(f"## {idx}. {job['company']} - {job['title']}\n")
            f.write(f"- Source: {job['source']}\n")
            f.write(f"- Published: {job.get('published_at', '')}\n")
            f.write(f"- URL: {job['url']}\n")
            f.write(f"- Summary: {job['summary']}\n\n")

    return str(path)