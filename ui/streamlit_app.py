import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from config import DATABASE_PATH, LOGO_DIR

st.set_page_config(page_title="Construction Archive Agent v4.2", layout="wide")

st.markdown("""
<style>
button,a,[role="button"],.stButton button,div[data-testid="stExpander"] summary,div[data-baseweb="select"],label{cursor:pointer!important}
a{color:#5db2ff!important;text-decoration:none;font-weight:700}
a:hover{text-decoration:underline}
.company-card{border:1px solid rgba(255,255,255,.12);border-radius:24px;padding:28px;margin:12px 0 22px 0;background:linear-gradient(135deg,rgba(58,123,255,.14),rgba(255,255,255,.03))}
.link-pill{display:inline-block;padding:9px 14px;border-radius:999px;border:1px solid rgba(93,178,255,.55);margin-right:8px;margin-bottom:8px}
.profile-box{border:1px solid rgba(255,255,255,.10);border-radius:18px;padding:18px;margin:14px 0;background:rgba(255,255,255,.025)}
.report-box{border:1px solid rgba(93,178,255,.22);border-radius:20px;padding:24px;background:rgba(93,178,255,.045);margin-top:18px}
</style>
""", unsafe_allow_html=True)

st.title("Construction Archive Agent v4.2")
st.caption("오늘 뉴스 · 중복 제거 이슈 아카이브 · 회사 리포트 · 공식 채용공고")

@st.cache_data(ttl=60)
def read_table(name):
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        df = pd.read_sql(f"SELECT * FROM {name}", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

def safe(v):
    if pd.isna(v):
        return ""
    return str(v)

def link(url, label="열기", pill=False):
    if not isinstance(url, str) or not url.strip():
        return ""
    cls = ' class="link-pill"' if pill else ""
    return f'<a{cls} href="{url}" target="_blank">{label}</a>'

def page_df(df, size, page):
    return df.iloc[(page - 1) * size:(page - 1) * size + size]

def logo_file(company):
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        p = LOGO_DIR / f"{company}{ext}"
        if p.exists():
            return str(p)
    return ""

def render_news(df):
    for _, r in df.iterrows():
        with st.container(border=True):
            st.markdown(f"### {safe(r.get('title',''))}")
            c = st.columns(4)
            c[0].markdown(f"**회사**: {safe(r.get('company',''))}")
            c[1].markdown(f"**분류**: {safe(r.get('category',''))}")
            c[2].markdown(f"**감성**: {safe(r.get('sentiment',''))}")
            c[3].markdown(f"**중요도**: {safe(r.get('importance',''))}/5")
            st.markdown(f"**수집일**: {safe(r.get('collected_at',''))}")
            st.markdown(f"**출처**: {safe(r.get('source',''))} / **게시일**: {safe(r.get('published_at',''))}")
            st.markdown(f"**요약**: {safe(r.get('summary',''))}")
            with st.expander("본문 일부 보기"):
                st.write(safe(r.get("body_excerpt","")))
            st.markdown(link(r.get("url",""), "기사 바로가기", True), unsafe_allow_html=True)

def render_issues(df):
    for _, r in df.iterrows():
        with st.container(border=True):
            st.markdown(f"### {safe(r.get('representative_title',''))}")
            c = st.columns(5)
            c[0].markdown(f"**회사**: {safe(r.get('company',''))}")
            c[1].markdown(f"**분류**: {safe(r.get('category',''))}")
            c[2].markdown(f"**감성**: {safe(r.get('sentiment',''))}")
            c[3].markdown(f"**관련 기사**: {safe(r.get('article_count',''))}건")
            c[4].markdown(f"**중요도**: {safe(r.get('importance',''))}/5")
            st.markdown(f"**생성/갱신**: {safe(r.get('created_at',''))} / {safe(r.get('updated_at',''))}")
            st.markdown(f"**이슈 요약**: {safe(r.get('issue_summary',''))}")
            urls = safe(r.get("urls","")).splitlines()
            if urls:
                with st.expander("관련 기사 링크 보기"):
                    for i, u in enumerate(urls, 1):
                        st.markdown(link(u, f"관련 기사 {i}", True), unsafe_allow_html=True)

def render_company(row, report_row=None):
    company = safe(row.get("company",""))
    logo = logo_file(company)
    st.markdown('<div class="company-card">', unsafe_allow_html=True)
    if logo:
        st.image(logo, width=220)
    st.markdown(f"## {safe(row.get('rank',''))}위. {company}")
    st.markdown(
        link(row.get("homepage",""), "공식 홈페이지", True)
        + link(row.get("news_url",""), "보도자료/뉴스룸", True)
        + link(row.get("careers_url",""), "채용 페이지", True),
        unsafe_allow_html=True
    )
    if not logo:
        st.caption("로고 파일 없음: data/logos/회사명.png 를 넣으면 표시됩니다.")
    st.markdown("</div>", unsafe_allow_html=True)

    if report_row is not None and safe(report_row.get("report_md", "")):
        st.markdown('<div class="report-box">', unsafe_allow_html=True)
        st.markdown(safe(report_row.get("report_md", "")))
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("리포트 출처 보기"):
            for line in safe(report_row.get("source_urls", "")).splitlines():
                if ":" in line:
                    label, url = line.split(":", 1)
                    st.markdown(link(url.strip(), label.strip(), True), unsafe_allow_html=True)
                else:
                    st.write(line)
    else:
        st.warning("회사 리포트가 없습니다. `python update_company_reports.py` 후 `python seed_company_reports.py`를 실행하세요.")
        for title, col in [("비전 / 경영이념", "vision"), ("인재상", "talent"), ("사업영역", "business_areas"), ("메모", "notes")]:
            text = safe(row.get(col, ""))
            if title == "메모" and not text:
                continue
            st.markdown('<div class="profile-box">', unsafe_allow_html=True)
            st.markdown(f"### {title}")
            st.write(text or "company_profiles.csv에 공식 문구를 입력하거나 회사 리포트를 생성하세요.")
            st.markdown("</div>", unsafe_allow_html=True)

def render_jobs(df):
    for _, r in df.iterrows():
        with st.container(border=True):
            st.markdown(f"### {safe(r.get('company',''))} - {safe(r.get('title',''))}")
            c = st.columns(4)
            c[0].markdown(f"**구분**: {safe(r.get('job_type',''))}")
            c[1].markdown(f"**시작**: {safe(r.get('start_date','')) or '미확인'}")
            c[2].markdown(f"**마감**: {safe(r.get('end_date','')) or '미확인'}")
            c[3].markdown(f"**상태**: {safe(r.get('status',''))}")
            st.markdown(f"**수집일**: {safe(r.get('collected_at',''))}")
            st.markdown(f"**출처**: {safe(r.get('source',''))}")
            st.write(safe(r.get("detail","")))
            st.markdown(link(r.get("official_url",""), "공식 공고 바로가기", True), unsafe_allow_html=True)

tab_today, tab_archive, tab_raw, tab_company, tab_job, tab_log = st.tabs(
    ["오늘 뉴스", "이슈 아카이브", "원문 기사 전체", "회사정보", "공식 채용공고", "수집 로그"]
)

with tab_today:
    st.subheader("오늘 뉴스")
    df = read_table("news_articles")
    if df.empty:
        st.info("아직 저장된 기사가 없습니다.")
    else:
        df = df.sort_values("collected_at", ascending=False)
        df["collected_date"] = pd.to_datetime(df["collected_at"], errors="coerce").dt.date.astype(str)
        today_str = str(date.today())
        f = df[df["collected_date"] == today_str].copy()

        with st.form("today_form"):
            c1, c2, c3 = st.columns(3)
            comp = c1.selectbox("회사 선택", ["전체"] + sorted(f["company"].dropna().unique().tolist()), key="today_comp")
            cat = c2.selectbox("분류 선택", ["전체"] + sorted(f["category"].dropna().unique().tolist()), key="today_cat")
            size = c3.selectbox("표시 개수", [10, 20, 50, 100], index=0, key="today_size")
            st.form_submit_button("적용")

        if comp != "전체":
            f = f[f["company"] == comp]
        if cat != "전체":
            f = f[f["category"] == cat]

        max_page = max(1, (len(f) + size - 1) // size)
        page = st.number_input("페이지", 1, max_page, 1, key="today_page")
        st.metric("오늘 수집 기사 수", len(f))
        render_news(page_df(f, size, page))

with tab_archive:
    st.subheader("이슈 아카이브")
    df = read_table("issue_clusters")
    if df.empty:
        st.info("아직 저장된 이슈가 없습니다.")
    else:
        df = df.sort_values("updated_at", ascending=False)
        df["updated_date"] = pd.to_datetime(df["updated_at"], errors="coerce").dt.date.astype(str)

        with st.form("archive_form"):
            c1, c2, c3, c4 = st.columns(4)
            comp = c1.selectbox("회사 선택", ["전체"] + sorted(df["company"].dropna().unique().tolist()), key="archive_comp")
            cat = c2.selectbox("분류 선택", ["전체"] + sorted(df["category"].dropna().unique().tolist()), key="archive_cat")
            day = c3.selectbox("갱신일", ["전체"] + sorted(df["updated_date"].dropna().unique().tolist(), reverse=True), key="archive_day")
            size = c4.selectbox("표시 개수", [10, 20, 50, 100], index=0, key="archive_size")
            st.form_submit_button("적용")

        f = df.copy()
        if comp != "전체":
            f = f[f["company"] == comp]
        if cat != "전체":
            f = f[f["category"] == cat]
        if day != "전체":
            f = f[f["updated_date"] == day]

        max_page = max(1, (len(f) + size - 1) // size)
        page = st.number_input("페이지", 1, max_page, 1, key="archive_page")
        st.metric("누적 이슈 수", len(f))
        render_issues(page_df(f, size, page))

with tab_raw:
    st.subheader("원문 기사 전체")
    df = read_table("news_articles")
    if df.empty:
        st.info("아직 저장된 기사가 없습니다.")
    else:
        df = df.sort_values("collected_at", ascending=False)
        df["collected_date"] = pd.to_datetime(df["collected_at"], errors="coerce").dt.date.astype(str)

        with st.form("raw_form"):
            c1, c2, c3, c4, c5 = st.columns(5)
            comp = c1.selectbox("회사 선택", ["전체"] + sorted(df["company"].dropna().unique().tolist()), key="raw_comp")
            cat = c2.selectbox("분류 선택", ["전체"] + sorted(df["category"].dropna().unique().tolist()), key="raw_cat")
            day = c3.selectbox("수집일", ["전체"] + sorted(df["collected_date"].dropna().unique().tolist(), reverse=True), key="raw_day")
            mode = c4.radio("보기", ["카드", "표"], horizontal=True, key="raw_mode")
            size = c5.selectbox("표시 개수", [10, 20, 50, 100], index=0, key="raw_size")
            st.form_submit_button("적용")

        f = df.copy()
        if comp != "전체":
            f = f[f["company"] == comp]
        if cat != "전체":
            f = f[f["category"] == cat]
        if day != "전체":
            f = f[f["collected_date"] == day]

        max_page = max(1, (len(f) + size - 1) // size)
        page = st.number_input("페이지", 1, max_page, 1, key="raw_page")
        st.metric("누적 원문 기사 수", len(f))
        shown = page_df(f, size, page)
        render_news(shown) if mode == "카드" else st.dataframe(shown, use_container_width=True)

with tab_company:
    st.subheader("회사정보")
    profiles = read_table("company_profiles")
    reports = read_table("company_reports")

    if profiles.empty:
        st.info("회사정보가 없습니다. python seed_company_profiles.py 실행.")
    else:
        profiles = profiles.sort_values("rank")
        t1, t2, t3 = st.tabs(["1~10위", "11~20위", "21~30위"])
        for tab, lo, hi, key in [(t1, 1, 10, "a"), (t2, 11, 20, "b"), (t3, 21, 30, "c")]:
            with tab:
                part = profiles[(profiles["rank"] >= lo) & (profiles["rank"] <= hi)]
                names = part["company"].tolist()
                if names:
                    selected = st.selectbox("회사 선택", names, key=f"profile_{key}")
                    row = part[part["company"] == selected].iloc[0]

                    report_row = None
                    if not reports.empty and selected in reports["company"].values:
                        report_row = reports[reports["company"] == selected].iloc[0]

                    render_company(row, report_row)

with tab_job:
    st.subheader("공식 채용공고")
    df = read_table("job_postings")
    if df.empty:
        st.info("아직 저장된 공식 채용공고가 없습니다. 수집 로그에서 공고 없음/실패 여부를 확인하세요.")
    else:
        df = df.sort_values("collected_at", ascending=False)
        with st.form("job_form"):
            c1, c2, c3 = st.columns(3)
            comp = c1.selectbox("회사 선택", ["전체"] + sorted(df["company"].dropna().unique().tolist()), key="job_comp")
            status = c2.selectbox("상태 선택", ["전체"] + sorted(df["status"].dropna().unique().tolist()), key="job_status")
            size = c3.selectbox("표시 개수", [10, 20, 50], index=0, key="job_size")
            st.form_submit_button("적용")
        f = df.copy()
        if comp != "전체":
            f = f[f["company"] == comp]
        if status != "전체":
            f = f[f["status"] == status]
        max_page = max(1, (len(f) + size - 1) // size)
        page = st.number_input("페이지", 1, max_page, 1, key="job_page")
        st.metric("선택 결과 공고 수", len(f))
        render_jobs(page_df(f, size, page))

with tab_log:
    st.subheader("채용공고 수집 로그")
    df = read_table("job_collection_logs")
    if df.empty:
        st.info("아직 채용공고 수집 로그가 없습니다.")
    else:
        df = df.sort_values("checked_at", ascending=False)
        st.dataframe(df, use_container_width=True)