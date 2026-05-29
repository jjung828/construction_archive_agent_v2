import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from news_collector import collect_google_news
from config import JOB_KEYWORDS
from web_utils import HEADERS, clean_text

STRICT_JOB_KEYWORDS = [
    "채용공고", "공개채용", "신입사원", "경력사원", "신입 채용", "경력 채용", "인턴 채용",
    "모집공고", "채용 모집", "서류접수", "입사지원", "공채", "job opening", "apply"
]
MENU_ONLY_KEYWORDS = ["인재상", "인사제도", "복리후생", "직무소개", "채용절차", "채용문의", "faq", "인재채용", "careers", "recruit"]
EXCLUDE_JOB_NOISE = ["분양", "청약", "입주", "계약자", "부당지원", "무죄", "소송", "검찰", "재판", "수주", "재건축", "재개발", "시공권", "부동산", "아파트", "회장", "대표"]

def looks_like_real_job(text, url=""):
    t = f"{text} {url}".lower()
    if any(k.lower() in t for k in EXCLUDE_JOB_NOISE):
        return False
    if any(k.lower() in t for k in STRICT_JOB_KEYWORDS):
        return True
    if any(k.lower() in t for k in MENU_ONLY_KEYWORDS):
        return any(k in t for k in ["2025", "2026", "상반기", "하반기", "수시", "접수", "모집"])
    return False

def collect_jobs_from_official_page(company_name, careers_url):
    if not careers_url:
        return []
    try:
        res = requests.get(careers_url, headers=HEADERS, timeout=15)
        res.raise_for_status()
        if not res.encoding or res.encoding.lower() == "iso-8859-1":
            res.encoding = res.apparent_encoding
    except Exception as e:
        print(f"Official career page error for {company_name}: {e}")
        return []
    soup = BeautifulSoup(res.text, "lxml")
    jobs, seen = [], set()
    for a in soup.find_all("a"):
        text = clean_text(a.get_text(" ", strip=True))
        href = a.get("href", "")
        full_url = urljoin(careers_url, href)
        if not looks_like_real_job(text, full_url):
            continue
        if full_url in seen:
            continue
        seen.add(full_url)
        jobs.append({
            "title": text if text else f"{company_name} 채용공고",
            "content": f"{company_name} 공식 채용 페이지에서 감지된 실제 채용공고 후보입니다.",
            "source": "Official Career Page",
            "url": full_url,
            "published_at": "",
        })
    page_text = clean_text(soup.get_text(" ", strip=True))
    if not jobs and looks_like_real_job(page_text, careers_url):
        jobs.append({
            "title": f"{company_name} 채용공고",
            "content": page_text[:500],
            "source": "Official Career Page",
            "url": careers_url,
            "published_at": "",
        })
    return jobs[:10]

def is_valid_google_job(article):
    return looks_like_real_job(f"{article.get('title','')} {article.get('content','')}", article.get("url", ""))

def collect_jobs_from_google_news(company_name, aliases=None):
    raw = collect_google_news(company_name, aliases, extra_keywords=JOB_KEYWORDS, limit=10, fetch_body=False)
    return [a for a in raw if is_valid_google_job(a)]

def collect_jobs(company_name, aliases=None, careers_url=None):
    merged, seen = [], set()
    for item in collect_jobs_from_official_page(company_name, careers_url) + collect_jobs_from_google_news(company_name, aliases):
        url = item.get("url", "")
        if url and url not in seen:
            seen.add(url)
            merged.append(item)
    return merged