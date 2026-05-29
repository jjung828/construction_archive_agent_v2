import pandas as pd
from bs4 import BeautifulSoup

from config import DATA_DIR
from utils.web import fetch_html, clean_text

PROFILE_SOURCES_CSV = DATA_DIR / "company_profile_sources.csv"
REPORTS_CSV = DATA_DIR / "company_reports.csv"

NOISE_WORDS = [
    "개인정보처리방침", "이메일무단수집거부", "법적고지", "사이트맵",
    "SNS", "Facebook", "Twitter", "Linkedin", "Print", "Share",
    "주소복사", "맨위로 이동", "COPYRIGHT", "Family Site"
]

def read_csv_safely(path):
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]
    last_error = None

    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc).fillna("")
            print(f"Loaded {path} with encoding={enc}, rows={len(df)}")
            return df
        except Exception as e:
            last_error = e

    raise RuntimeError(f"CSV 읽기 실패: {path} / last_error={last_error}")

def load_profile_sources():
    if not PROFILE_SOURCES_CSV.exists():
        raise FileNotFoundError(f"Not found: {PROFILE_SOURCES_CSV}")

    df = read_csv_safely(PROFILE_SOURCES_CSV)

    required = {"company", "label", "url", "enabled"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"company_profile_sources.csv 컬럼 누락: {missing}")

    # 빈 줄 제거
    df["company"] = df["company"].astype(str).str.strip()
    df["url"] = df["url"].astype(str).str.strip()
    df["enabled"] = df["enabled"].astype(str).str.strip().str.lower()

    df = df[(df["company"] != "") & (df["url"] != "")]
    df = df[df["enabled"].isin(["true", "1", "yes", "y", "t"])]

    print(f"Enabled profile source rows: {len(df)}")
    print(f"Companies in sources: {df['company'].nunique()}")

    if df.empty:
        raise RuntimeError(
            "company_profile_sources.csv에서 활성화된 수집 대상이 0개입니다. "
            "enabled 값이 true인지, 파일 위치가 data/company_profile_sources.csv인지 확인하세요."
        )

    return df

def extract_page_text(url):
    html = fetch_html(url)
    if not html:
        return ""

    soup = BeautifulSoup(html, "lxml")

    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "aside"]):
        tag.decompose()

    parts = []
    for elem in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "dt", "dd", "strong"]):
        txt = clean_text(elem.get_text(" ", strip=True))
        if len(txt) < 8:
            continue
        if any(n.lower() in txt.lower() for n in NOISE_WORDS):
            continue
        parts.append(txt)

    unique = []
    seen = set()
    for p in parts:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    return "\n".join(unique)[:10000]

def collect_company_raw_reports():
    sources = load_profile_sources()
    grouped = {}

    for _, row in sources.iterrows():
        company = row["company"]
        label = row.get("label", "")
        url = row["url"]

        print(f"Collecting profile page: {company} / {label} / {url}")
        text = extract_page_text(url)

        if company not in grouped:
            grouped[company] = {"sources": [], "raw_text": []}

        grouped[company]["sources"].append(f"{label}: {url}")

        if text:
            grouped[company]["raw_text"].append(f"[{label}]\n{text}")
        else:
            grouped[company]["raw_text"].append(f"[{label}]\n페이지 텍스트 수집 실패 또는 내용 없음.")

    print(f"Grouped companies for reports: {len(grouped)}")
    return grouped