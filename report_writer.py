from datetime import datetime
from config import REPORT_DIR

def write_company_report(company, articles, issue_clusters):

    REPORT_DIR.mkdir(exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    path = REPORT_DIR / f"{today}_{company}.md"

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# {company} Daily Report\n\n")
        f.write(f"- Date: {today}\n")
        f.write(f"- Article count: {len(articles)}\n")
        f.write(f"- Issue count: {len(issue_clusters)}\n\n")

        f.write("## Issue Summary\n\n")
        if not issue_clusters:
            f.write("수집된 신규 이슈가 없습니다.\n\n")
        else:
            for idx, issue in enumerate(issue_clusters, start=1):
                f.write(f"### {idx}. {issue['representative_title']}\n")
                f.write(f"- Category: {issue['category']}\n")
                f.write(f"- Sentiment: {issue['sentiment']}\n")
                f.write(f"- Importance: {issue['importance']} / 5\n")
                f.write(f"- Related articles: {issue['article_count']}\n")
                f.write(f"- Summary: {issue['issue_summary']}\n\n")

        f.write("## Raw Articles\n\n")
        if not articles:
            f.write("오늘 수집된 신규 기사가 없습니다.\n")
        else:
            for idx, article in enumerate(articles, start=1):
                f.write(f"### {idx}. {article['title']}\n")
                f.write(f"- Category: {article['category']}\n")
                f.write(f"- Sentiment: {article['sentiment']}\n")
                f.write(f"- Importance: {article['importance']} / 5\n")
                f.write(f"- Published: {article.get('published_at', '')}\n")
                f.write(f"- Source: {article['source']}\n")
                f.write(f"- URL: {article['url']}\n")
                f.write(f"- Summary:\n{article['summary']}\n\n")

    return str(path)