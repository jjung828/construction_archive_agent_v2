from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DATABASE_PATH

Base = declarative_base()

class NewsArticle(Base):
    __tablename__ = "news_articles"
    id = Column(Integer, primary_key=True)
    collected_at = Column(DateTime, default=datetime.now)
    published_at = Column(String)
    company = Column(String)
    title = Column(String)
    body_excerpt = Column(Text)
    summary = Column(Text)
    category = Column(String)
    sentiment = Column(String)
    importance = Column(Integer)
    source = Column(String)
    url = Column(Text)
    issue_id = Column(Integer, nullable=True)
    __table_args__ = (UniqueConstraint("company", "url", name="uq_company_url"),)

class IssueCluster(Base):
    __tablename__ = "issue_clusters"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    company = Column(String)
    representative_title = Column(String)
    issue_summary = Column(Text)
    category = Column(String)
    sentiment = Column(String)
    importance = Column(Integer)
    article_count = Column(Integer)
    urls = Column(Text)

class CompanyProfile(Base):
    __tablename__ = "company_profiles"
    id = Column(Integer, primary_key=True)
    rank = Column(Integer)
    company = Column(String, unique=True)
    aliases = Column(Text)
    homepage = Column(Text)
    news_url = Column(Text)
    careers_url = Column(Text)
    logo_path = Column(Text)
    vision = Column(Text)
    talent = Column(Text)
    business_areas = Column(Text)
    notes = Column(Text)
    updated_at = Column(DateTime, default=datetime.now)

class CompanyReport(Base):
    __tablename__ = "company_reports"
    id = Column(Integer, primary_key=True)
    company = Column(String, unique=True)
    report_md = Column(Text)
    source_urls = Column(Text)
    updated_at = Column(DateTime, default=datetime.now)

class JobPosting(Base):
    __tablename__ = "job_postings"
    id = Column(Integer, primary_key=True)
    collected_at = Column(DateTime, default=datetime.now)
    company = Column(String)
    title = Column(String)
    job_type = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    status = Column(String)
    source = Column(String)
    official_url = Column(Text)
    detail = Column(Text)
    __table_args__ = (UniqueConstraint("company", "official_url", name="uq_company_official_job_url"),)

class JobCollectionLog(Base):
    __tablename__ = "job_collection_logs"
    id = Column(Integer, primary_key=True)
    checked_at = Column(DateTime, default=datetime.now)
    company = Column(String)
    source = Column(String)
    url = Column(Text)
    status = Column(String)
    message = Column(Text)
    found_count = Column(Integer)

engine = create_engine(f"sqlite:///{DATABASE_PATH}")
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def save_article(data):
    session = Session()
    exists = session.query(NewsArticle).filter_by(company=data["company"], url=data["url"]).first()
    if exists:
        session.close()
        return None
    article = NewsArticle(**data)
    session.add(article)
    session.commit()
    article_id = article.id
    session.close()
    return article_id

def save_issue_cluster(data):
    session = Session()
    cluster = IssueCluster(**data)
    session.add(cluster)
    session.commit()
    issue_id = cluster.id
    session.close()
    return issue_id

def get_issue_clusters(company=None):
    session = Session()
    q = session.query(IssueCluster)
    if company:
        q = q.filter(IssueCluster.company == company)
    rows = q.all()
    session.expunge_all()
    session.close()
    return rows

def merge_issue_cluster(issue_id, new_urls, new_summary=None, new_importance=None):
    session = Session()
    issue = session.query(IssueCluster).filter(IssueCluster.id == issue_id).first()
    if not issue:
        session.close()
        return

    urls = []
    if issue.urls:
        urls = [u.strip() for u in issue.urls.splitlines() if u.strip()]

    for url in new_urls:
        if url and url not in urls:
            urls.append(url)

    issue.urls = "\n".join(urls)
    issue.article_count = len(urls)
    issue.updated_at = datetime.now()

    if new_importance is not None:
        issue.importance = max(issue.importance or 1, int(new_importance))

    if new_summary and (not issue.issue_summary or len(issue.issue_summary) < 50):
        issue.issue_summary = new_summary

    session.commit()
    session.close()

def update_articles_issue_id(company, urls, issue_id):
    session = Session()
    session.query(NewsArticle).filter(
        NewsArticle.company == company,
        NewsArticle.url.in_(urls)
    ).update({"issue_id": issue_id}, synchronize_session=False)
    session.commit()
    session.close()

def upsert_company_profile(data):
    session = Session()
    existing = session.query(CompanyProfile).filter_by(company=data["company"]).first()
    if existing:
        for k, v in data.items():
            setattr(existing, k, v)
        existing.updated_at = datetime.now()
    else:
        session.add(CompanyProfile(**data))
    session.commit()
    session.close()

def upsert_company_report(data):
    session = Session()
    existing = session.query(CompanyReport).filter_by(company=data["company"]).first()
    if existing:
        existing.report_md = data.get("report_md", "")
        existing.source_urls = data.get("source_urls", "")
        existing.updated_at = datetime.now()
    else:
        session.add(CompanyReport(**data))
    session.commit()
    session.close()

def save_job_posting(data):
    session = Session()
    exists = session.query(JobPosting).filter_by(
        company=data["company"], official_url=data["official_url"]
    ).first()
    if exists:
        session.close()
        return False
    session.add(JobPosting(**data))
    session.commit()
    session.close()
    return True

def save_job_collection_log(data):
    session = Session()
    session.add(JobCollectionLog(**data))
    session.commit()
    session.close()