from database import (
    init_db,
    save_article,
    save_issue_cluster,
    update_articles_issue_id,
    save_job_posting,
    save_job_collection_log,
)
from collectors.news_collector import load_companies, collect_news
from collectors.issue_clusterer import cluster_articles
from collectors.official_job_collector import collect_all_official_jobs
from llm.summarizer import summarize_article, summarize_issue
from reports import write_daily_reports, write_job_alert_report

def process_news():
    companies = load_companies()
    total_articles = 0
    total_issues = 0

    for _, row in companies.iterrows():
        company = row["company"]
        aliases = row.get("aliases", "")

        print(f"Collecting news: {company}")
        raw_articles = collect_news(company, aliases)

        saved_articles = []

        for article in raw_articles:
            parsed = summarize_article(company, article)

            data = {
                "company": company,
                "title": article["title"],
                "body_excerpt": article.get("body_excerpt", ""),
                "summary": parsed["summary"],
                "category": parsed["category"],
                "sentiment": parsed["sentiment"],
                "importance": parsed["importance"],
                "source": article["source"],
                "url": article["url"],
                "published_at": article.get("published_at", "")
            }

            if save_article(data):
                saved_articles.append(data)
                total_articles += 1
                print(f"Saved news: {article['title']}")
            else:
                print(f"Duplicate news skipped: {article['title']}")

        clusters = cluster_articles(saved_articles)

        for cluster in clusters:
            issue = summarize_issue(company, cluster)
            issue["company"] = company
            issue_id = save_issue_cluster(issue)
            update_articles_issue_id(company, [a["url"] for a in cluster], issue_id)
            total_issues += 1

    return total_articles, total_issues

def process_jobs():
    jobs, logs = collect_all_official_jobs()

    for log in logs:
        save_job_collection_log(log)

    new_jobs = []
    for job in jobs:
        if save_job_posting(job):
            new_jobs.append(job)
            print(f"Saved official job: {job['company']} - {job['title']}")
        else:
            print(f"Duplicate job skipped: {job['company']} - {job['title']}")

    return new_jobs

def main():
    init_db()
    total_articles, total_issues = process_news()
    new_jobs = process_jobs()

    write_daily_reports()
    write_job_alert_report(new_jobs)

    print(f"Done. New articles: {total_articles}")
    print(f"Done. New issues: {total_issues}")
    print(f"Done. New official jobs: {len(new_jobs)}")

if __name__ == "__main__":
    main()