import urllib.parse
import pandas as pd
import feedparser
from bs4 import BeautifulSoup
from config import COMPANIES_CSV, NEWS_LIMIT_PER_COMPANY, NEWS_PERIOD, KEYWORDS
from utils.web import clean_text, extract_main_text, resolve_google_news_url

def load_companies(csv_path=COMPANIES_CSV):
    return pd.read_csv(csv_path).fillna("")

def clean_html(text):
    if not text: return ""
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
    encoded = urllib.parse.quote(query)
    return f"https://news.google.com/rss/search?q={encoded}&hl=ko&gl=KR&ceid=KR:ko"

def collect_news(company_name, aliases=None):
    query = build_query(company_name, aliases)
    feed = feedparser.parse(google_news_rss_url(query))
    articles = []
    for entry in feed.entries[:NEWS_LIMIT_PER_COMPANY]:
        title = clean_html(entry.get("title", ""))
        rss_summary = clean_html(entry.get("summary", ""))
        url = resolve_google_news_url(entry.get("link", ""))
        source = entry.source.get("title", "") if hasattr(entry, "source") else "Google News"
        body_excerpt = extract_main_text(url, max_chars=1800)
        content = clean_text(body_excerpt if body_excerpt else rss_summary)
        articles.append({"title": title, "body_excerpt": content, "source": source, "url": url, "published_at": entry.get("published", "")})
    return articles
