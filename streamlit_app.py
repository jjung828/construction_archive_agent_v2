import streamlit as st
import sqlite3
import pandas as pd
from config import DATABASE_PATH

st.set_page_config(page_title="Construction Archive Agent v2.4", layout="wide")
st.markdown("""
<style>
button,a,[role="button"],.stButton button,div[data-testid="stExpander"] summary,div[data-baseweb="select"],label{cursor:pointer!important}
a{color:#4da3ff!important;text-decoration:none;font-weight:700}
a:hover{text-decoration:underline}
.company-hero{border:1px solid rgba(255,255,255,.12);border-radius:22px;padding:28px;margin-bottom:20px;background:linear-gradient(135deg,rgba(77,163,255,.12),rgba(255,255,255,.03))}
.logo-badge{width:78px;height:78px;border-radius:22px;display:flex;align-items:center;justify-content:center;font-size:30px;font-weight:900;background:linear-gradient(135deg,#2b6cff,#00c2ff);color:white;margin-bottom:14px}
.link-pill{display:inline-block;padding:9px 14px;border-radius:999px;border:1px solid rgba(77,163,255,.5);margin-right:8px;margin-bottom:8px}
</style>
""", unsafe_allow_html=True)

st.title("Construction Archive Agent v2.4")
st.caption("국내 건설사 뉴스·이슈·회사정보·채용공고 아카이브")

@st.cache_data(ttl=60)
def read_table(table):
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        df = pd.read_sql(f"SELECT * FROM {table}", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df

def safe(v):
    if pd.isna(v): return ""
    return str(v)

def link(url, label="열기", pill=False):
    if not isinstance(url, str) or not url.strip(): return ""
    cls = ' class="link-pill"' if pill else ""
    return f'<a{cls} href="{url}" target="_blank">{label}</a>'

def initials(company):
    company = safe(company)
    if any("가" <= ch <= "힣" for ch in company): return company[:2]
    return "".join([w[0].upper() for w in company.split()[:2]]) or "C"

def page_df(df, size, num):
    return df.iloc[(num-1)*size:(num-1)*size+size]

def render_articles(df):
    for _, r in df.iterrows():
        with st.container(border=True):
            st.markdown(f"### {safe(r.get('title',''))}")
            c = st.columns(4)
            c[0].markdown(f"**회사**: {safe(r.get('company',''))}")
            c[1].markdown(f"**분류**: {safe(r.get('category',''))}")
            c[2].markdown(f"**감성**: {safe(r.get('sentiment',''))}")
            c[3].markdown(f"**중요도**: {safe(r.get('importance',''))}/5")
            st.markdown(f"**출처**: {safe(r.get('source',''))} / **게시일**: {safe(r.get('published_at',''))}")
            st.markdown(f"**요약/본문 일부**: {safe(r.get('summary',''))}")
            st.markdown(link(r.get("url",""), "기사 바로가기", True), unsafe_allow_html=True)

def render_issues(df):
    for _, r in df.iterrows():
        with st.container(border=True):
            st.markdown(f"### {safe(r.get('representative_title',''))}")
            c = st.columns(4)
            c[0].markdown(f"**회사**: {safe(r.get('company',''))}")
            c[1].markdown(f"**분류**: {safe(r.get('category',''))}")
            c[2].markdown(f"**감성**: {safe(r.get('sentiment',''))}")
            c[3].markdown(f"**관련 기사 수**: {safe(r.get('article_count',''))}")
            st.markdown(f"**요약**: {safe(r.get('issue_summary',''))}")
            urls = safe(r.get("urls","")).splitlines()
            if urls:
                with st.expander("관련 링크"):
                    for i,u in enumerate(urls,1):
                        st.markdown(link(u, f"기사 {i}", True), unsafe_allow_html=True)

def render_company(r):
    hero = f"""
    <div class="company-hero">
      <div class="logo-badge">{initials(r.get("company",""))}</div>
      <h1>{safe(r.get("rank",""))}위. {safe(r.get("company",""))}</h1>
      {link(r.get("homepage",""),"공식 홈페이지",True)}
      {link(r.get("news_url",""),"보도자료/뉴스룸",True)}
      {link(r.get("careers_url",""),"채용 페이지",True)}
    </div>
    """
    st.markdown(hero, unsafe_allow_html=True)
    st.markdown("### 별칭"); st.write(safe(r.get("aliases","")) or "없음")
    st.markdown("### 비전 / 경영이념"); st.write(safe(r.get("vision","")) or "아직 수집되지 않음")
    st.markdown("### 인재상 / 채용 관련 정보"); st.write(safe(r.get("talent","")) or "아직 수집되지 않음")
    st.markdown("### 사업영역"); st.write(safe(r.get("business_areas","")) or "아직 수집되지 않음")

def render_jobs(df):
    for _, r in df.iterrows():
        with st.container(border=True):
            st.markdown(f"### {safe(r.get('company',''))} - {safe(r.get('title',''))}")
            st.markdown(f"**출처**: {safe(r.get('source',''))} / **게시일**: {safe(r.get('published_at',''))}")
            st.markdown(f"**상태**: {safe(r.get('status',''))}")
            st.markdown(f"**요약**: {safe(r.get('summary',''))}")
            st.markdown(link(r.get("url",""), "공고 바로가기", True), unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["뉴스 기사","이슈 클러스터","회사정보","채용공고"])

with tab1:
    st.subheader("뉴스 기사")
    df = read_table("news_articles")
    if df.empty: st.info("아직 저장된 기사가 없습니다.")
    else:
        df = df.sort_values("collected_at", ascending=False)
        with st.form("news_form"):
            c1,c2,c3,c4=st.columns(4)
            comp=c1.selectbox("회사 선택", ["전체"]+sorted(df["company"].dropna().unique().tolist()))
            cat=c2.selectbox("분류 선택", ["전체"]+sorted(df["category"].dropna().unique().tolist()))
            mode=c3.radio("보기 방식", ["카드","표"], horizontal=True)
            size=c4.selectbox("표시 개수", [10,20,50,100], index=0)
            st.form_submit_button("적용")
        f=df.copy()
        if comp!="전체": f=f[f["company"]==comp]
        if cat!="전체": f=f[f["category"]==cat]
        maxp=max(1,(len(f)+size-1)//size)
        p=st.number_input("페이지",1,maxp,1,key="news_page")
        st.metric("선택 결과 기사 수", len(f))
        shown=page_df(f,size,p)
        render_articles(shown) if mode=="카드" else st.dataframe(shown, use_container_width=True)

with tab2:
    st.subheader("이슈 클러스터")
    st.info("같은 내용의 기사 여러 개를 하나의 이슈로 묶은 것입니다.")
    df = read_table("issue_clusters")
    if df.empty: st.info("아직 저장된 이슈가 없습니다.")
    else:
        df=df.sort_values("created_at", ascending=False)
        with st.form("issue_form"):
            c1,c2,c3=st.columns(3)
            comp=c1.selectbox("회사 선택", ["전체"]+sorted(df["company"].dropna().unique().tolist()), key="issue_comp")
            cat=c2.selectbox("분류 선택", ["전체"]+sorted(df["category"].dropna().unique().tolist()), key="issue_cat")
            size=c3.selectbox("표시 개수", [10,20,50], index=0, key="issue_size")
            st.form_submit_button("적용")
        f=df.copy()
        if comp!="전체": f=f[f["company"]==comp]
        if cat!="전체": f=f[f["category"]==cat]
        maxp=max(1,(len(f)+size-1)//size)
        p=st.number_input("페이지",1,maxp,1,key="issue_page")
        st.metric("선택 결과 이슈 수", len(f))
        render_issues(page_df(f,size,p))

with tab3:
    st.subheader("회사정보")
    df=read_table("company_profiles")
    if df.empty: st.info("회사정보가 없습니다. python company_profile_seed.py 실행.")
    else:
        df=df.sort_values("rank")
        t1,t2,t3=st.tabs(["1~10위","11~20위","21~30위"])
        for tab,lo,hi,key in [(t1,1,10,"a"),(t2,11,20,"b"),(t3,21,30,"c")]:
            with tab:
                part=df[(df["rank"]>=lo)&(df["rank"]<=hi)]
                names=part["company"].tolist()
                if names:
                    sel=st.selectbox("회사 선택", names, key=f"profile_{key}")
                    render_company(part[part["company"]==sel].iloc[0])

with tab4:
    st.subheader("채용공고")
    st.info("v2.4부터 단순 메뉴 링크는 제외합니다. 동적 페이지는 감지 제한 가능.")
    df=read_table("job_postings")
    if df.empty: st.info("아직 저장된 채용공고가 없습니다.")
    else:
        df=df.sort_values("collected_at", ascending=False)
        with st.form("job_form"):
            c1,c2=st.columns(2)
            comp=c1.selectbox("회사 선택", ["전체"]+sorted(df["company"].dropna().unique().tolist()), key="job_comp")
            size=c2.selectbox("표시 개수", [10,20,50], index=0, key="job_size")
            st.form_submit_button("적용")
        f=df.copy()
        if comp!="전체": f=f[f["company"]==comp]
        maxp=max(1,(len(f)+size-1)//size)
        p=st.number_input("페이지",1,maxp,1,key="job_page")
        st.metric("선택 결과 채용공고 수", len(f))
        render_jobs(page_df(f,size,p))