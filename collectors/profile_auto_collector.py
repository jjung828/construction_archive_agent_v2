import pandas as pd
from bs4 import BeautifulSoup

from config import COMPANIES_CSV
from utils.web import fetch_html, clean_text
from llm.profile_summarizer import summarize_company_profile

IMPORTANT_KEYWORDS = [
    "비전", "미션", "경영이념", "핵심가치", "가치체계", "인재상", "인재",
    "사업영역", "사업분야", "주요사업", "건축", "토목", "플랜트", "주택",
    "인프라", "개발", "환경", "에너지", "채용", "recruit", "career",
    "vision", "mission", "value", "business"
]

NOISE_KEYWORDS = [
    "개인정보처리방침", "이메일무단수집거부", "쿠키", "copyright", "family site",
    "로그인", "회원가입", "사이트맵", "language", "검색"
]


def _extract_clean_page_text(url):
    html = fetch_html(url)
    if not html:
        return ""

    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    parts = []
    for elem in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "dt", "dd", "strong", "span"]):
        txt = clean_text(elem.get_text(" ", strip=True))
        if len(txt) < 8:
            continue
        low = txt.lower()
        if any(n.lower() in low for n in NOISE_KEYWORDS):
            continue
        if any(k.lower() in low for k in IMPORTANT_KEYWORDS) or len(txt) >= 40:
            parts.append(txt)

    unique = []
    seen = set()
    for p in parts:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    return " ".join(unique)[:12000]


def collect_profile_raw_text(row):
    urls = [row.get("homepage", ""), row.get("careers_url", ""), row.get("news_url", "")]
    chunks = []
    for url in urls:
        if not isinstance(url, str) or not url.strip():
            continue
        print(f"  fetching: {url}")
        txt = _extract_clean_page_text(url)
        if txt:
            chunks.append(f"[SOURCE: {url}]\n{txt}")
    return "\n\n".join(chunks)


def build_clean_profiles():
    companies = pd.read_csv(COMPANIES_CSV).fillna("")
    rows = []
    for _, row in companies.iterrows():
        company = row["company"]
        print(f"Cleaning company profile with LLM: {company}")
        raw_text = collect_profile_raw_text(row)
        cleaned = summarize_company_profile(company, raw_text)
        rows.append({
            "rank": row["rank"],
            "company": company,
            "vision": cleaned.get("vision", ""),
            "talent": cleaned.get("talent", ""),
            "business_areas": cleaned.get("business_areas", ""),
            "notes": cleaned.get("notes", ""),
        })
    return pd.DataFrame(rows)
