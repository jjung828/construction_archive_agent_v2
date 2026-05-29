import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ConstructionArchiveAgent/2.4)"}

def resolve_google_news_url(url):
    if not url:
        return url
    try:
        parsed = urlparse(url)
        if "news.google.com" not in parsed.netloc:
            return url
        qs = parse_qs(parsed.query)
        for key in ["url", "q"]:
            if key in qs and qs[key]:
                return unquote(qs[key][0])
    except Exception:
        return url
    return url

def fetch_html(url, timeout=12):
    if not url:
        return ""
    url = resolve_google_news_url(url)
    try:
        res = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        res.raise_for_status()
        if not res.encoding or res.encoding.lower() == "iso-8859-1":
            res.encoding = res.apparent_encoding
        return res.text
    except Exception as e:
        print(f"fetch_html error: {url} / {e}")
        return ""

def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    return text.replace("\xa0", " ").strip()

def soup_text_from_url(url):
    html = fetch_html(url)
    if not html:
        return ""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()
    candidates = []
    for selector in ["article", "main", ".article", ".news", ".view", ".content", ".contents", ".container"]:
        for elem in soup.select(selector):
            txt = clean_text(elem.get_text(" ", strip=True))
            if len(txt) > 200:
                candidates.append(txt)
    if not candidates:
        ps = [clean_text(p.get_text(" ", strip=True)) for p in soup.find_all("p")]
        ps = [p for p in ps if len(p) > 30]
        if ps:
            candidates.append(" ".join(ps))
    if not candidates:
        body = soup.body.get_text(" ", strip=True) if soup.body else soup.get_text(" ", strip=True)
        candidates.append(clean_text(body))
    candidates = sorted(candidates, key=len, reverse=True)
    return candidates[0][:4000] if candidates else ""

def extract_relevant_text(url, keywords=None, max_chars=1200):
    text = soup_text_from_url(url)
    if not text:
        return ""
    if not keywords:
        return text[:max_chars]
    sentences = re.split(r"(?<=[.!?。])\s+|(?<=다\.)\s+", text)
    picked = [s for s in sentences if any(k.lower() in s.lower() for k in keywords)]
    if not picked:
        return text[:max_chars]
    return clean_text(" ".join(picked))[:max_chars]