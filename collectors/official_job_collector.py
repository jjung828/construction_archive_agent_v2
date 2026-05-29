import re
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date
from urllib.parse import urljoin

from config import OFFICIAL_JOBS_CSV
from utils.web import clean_text, fetch_html

REAL_JOB_KEYWORDS = [
    "채용공고", "공개채용", "신입사원", "경력사원", "신입", "경력",
    "인턴", "모집공고", "모집", "서류접수", "입사지원", "공채",
    "수시채용", "상시채용", "채용중", "지원하기", "apply", "job"
]

NON_JOB_MENU = [
    "인재상", "인사제도", "복리후생", "직무소개", "채용절차",
    "채용문의", "FAQ", "자주하는", "지원가이드", "개인정보"
]

NOISE = [
    "분양", "청약", "입주", "수주", "재건축", "재개발", "소송",
    "검찰", "무죄", "아파트", "부동산", "회장", "대표"
]

DATE_PATTERNS = [
    r"(20\\d{2})[.\\-/년 ]+(\\d{1,2})[.\\-/월 ]+(\\d{1,2})",
    r"(\\d{4})[.\\-/](\\d{1,2})[.\\-/](\\d{1,2})",
]

def load_job_sources():
    try:
        df = pd.read_csv(OFFICIAL_JOBS_CSV).fillna("")
        df = df[df["enabled"].astype(str).str.lower().isin(["true", "1", "yes"])]
        return df
    except Exception as e:
        print(f"official_job_sources.csv load failed: {e}")
        return pd.DataFrame()

def looks_like_job(title, url=""):
    text = f"{title} {url}".lower()

    if any(n.lower() in text for n in NOISE):
        return False

    if not any(k.lower() in text for k in REAL_JOB_KEYWORDS):
        return False

    if any(m.lower() in text for m in NON_JOB_MENU):
        strong = any(k in text for k in ["2025", "2026", "상반기", "하반기", "수시", "공개채용", "모집", "접수", "지원하기"])
        if not strong:
            return False

    return True

def extract_dates(text):
    found = []
    for pattern in DATE_PATTERNS:
        for m in re.finditer(pattern, text):
            y, mo, d = m.groups()
            try:
                found.append(date(int(y), int(mo), int(d)).isoformat())
            except Exception:
                pass

    unique = list(dict.fromkeys(found))
    if len(unique) >= 2:
        return unique[0], unique[-1]
    if len(unique) == 1:
        return "", unique[0]
    return "", ""

def infer_job_type(title):
    if "인턴" in title:
        return "인턴"
    if "신입" in title and "경력" in title:
        return "신입/경력"
    if "신입" in title:
        return "신입"
    if "경력" in title:
        return "경력"
    if "공채" in title or "공개채용" in title:
        return "공채"
    if "수시" in title:
        return "수시"
    return "기타"

def calc_status(start_date, end_date):
    today = date.today()
    try:
        if start_date:
            s = date.fromisoformat(start_date)
            if today < s:
                return "예정"
        if end_date:
            e = date.fromisoformat(end_date)
            if today > e:
                return "마감"
            if (e - today).days <= 3:
                return "마감임박"
        return "진행중"
    except Exception:
        return "확인필요"

def parse_jobs_from_html(company, official_url, source_name, html):
    soup = BeautifulSoup(html, "lxml")
    jobs = []
    seen = set()

    candidates = []

    for a in soup.find_all("a"):
        title = clean_text(a.get_text(" ", strip=True))
        href = a.get("href", "")
        url = urljoin(official_url, href)
        if title:
            candidates.append((title, url, "공식 채용 링크"))

    selectors = [
        "li", "tr", ".item", ".list", ".card", ".job", ".recruit",
        "[class*=job]", "[class*=recruit]", "[class*=notice]"
    ]

    for selector in selectors:
        for elem in soup.select(selector):
            text = clean_text(elem.get_text(" ", strip=True))
            if len(text) < 10:
                continue
            a = elem.find("a")
            url = urljoin(official_url, a.get("href", "")) if a else official_url
            candidates.append((text, url, text[:800]))

    for title, url, detail in candidates:
        if not looks_like_job(title, url):
            continue
        key = (title[:100], url)
        if key in seen:
            continue
        seen.add(key)

        start, end = extract_dates(title + " " + detail)

        jobs.append({
            "company": company,
            "title": title[:250],
            "job_type": infer_job_type(title),
            "start_date": start,
            "end_date": end,
            "status": calc_status(start, end),
            "source": source_name,
            "official_url": url,
            "detail": detail[:800],
        })

    uniq = []
    urls = set()
    for job in jobs:
        if job["official_url"] in urls:
            continue
        urls.add(job["official_url"])
        uniq.append(job)

    return uniq[:30]

def fetch_rendered_html(url):
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=45000)
            page.wait_for_timeout(2500)
            html = page.content()
            browser.close()
            return html, "playwright"
    except Exception as e:
        print(f"Playwright failed: {url} / {e}")
        html = fetch_html(url)
        return html, "requests_fallback"

def collect_jobs_from_official_source(company, official_url, source_name="공식 채용"):
    html, method = fetch_rendered_html(official_url)

    if not html:
        return [], {
            "company": company,
            "source": source_name,
            "url": official_url,
            "status": "수집실패",
            "message": f"페이지 HTML을 가져오지 못함. method={method}",
            "found_count": 0,
        }

    jobs = parse_jobs_from_html(company, official_url, source_name, html)

    if jobs:
        status = "공고감지"
        message = f"{len(jobs)}개 공고 후보 감지. method={method}"
    else:
        status = "공고없음"
        message = f"페이지는 읽었지만 실제 공고 후보 없음. method={method}"

    return jobs, {
        "company": company,
        "source": source_name,
        "url": official_url,
        "status": status,
        "message": message,
        "found_count": len(jobs),
    }

def collect_all_official_jobs():
    sources = load_job_sources()
    all_jobs = []
    logs = []

    for _, row in sources.iterrows():
        company = row["company"]
        source_name = row.get("source_name", "공식 채용")
        official_url = row["official_url"]

        print(f"Checking official jobs: {company}")
        jobs, log = collect_jobs_from_official_source(company, official_url, source_name)
        all_jobs.extend(jobs)
        logs.append(log)

    return all_jobs, logs