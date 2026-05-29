import pandas as pd
import feedparser
import urllib.parse
from bs4 import BeautifulSoup
from config import COMPANIES_CSV, NEWS_LIMIT_PER_COMPANY, NEWS_PERIOD, KEYWORDS
from web_utils import extract_relevant_text, clean_text, resolve_google_news_url

def load_companies(csv_path=COMPANIES_CSV):
    return pd.read_csv(csv_path).fillna("")

def clean_html(text):
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)

def build_query(company_name, aliases=None, extra_keywords=None):
    names = [company_name]
    if aliases and isinstance(aliases, str):
        names.extend([x.strip() for x in aliases.split("|") if x.strip()])
    name_query = " OR ".join([f'"{name}"' for name in names])
    keywords = extra_keywords if extra_keywords else KEYWORDS
    keyword_query = " OR ".join(keywords)
    return f"({name_query}) ({keyword_query}) when:{NEWS_PERIOD}"

def google_news_rss_url(query):
    return f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=ko&gl=KR&ceid=KR:ko"

def collect_google_news(company_name, aliases=None, extra_keywords=None, limit=NEWS_LIMIT_PER_COMPANY, fetch_body=True):
    feed = feedparser.parse(google_news_rss_url(build_query(company_name, aliases, extra_keywords)))
    articles = []
    for entry in feed.entries[:limit]:
        title = clean_html(entry.get("title", ""))
        rss_summary = clean_html(entry.get("summary", ""))
        link = resolve_google_news_url(entry.get("link", ""))
        source = entry.source.get("title", "") if hasattr(entry, "source") else ""
        body = ""
        if fetch_body:
            body = extract_relevant_text(link, keywords=[company_name] + list(extra_keywords or KEYWORDS), max_chars=1200)
        content = clean_text(body) if body else clean_text(rss_summary)
        articles.append({
            "title": title,
            "content": content,
            "rss_summary": rss_summary,
            "source": source or "Google News",
            "url": link,
            "published_at": entry.get("published", "")
        })
    return articles

def collect_news(company_name, aliases=None):
    return collect_google_news(company_name, aliases, fetch_body=True)