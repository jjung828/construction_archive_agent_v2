from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOGO_DIR = DATA_DIR / "logos"
REPORT_DIR = BASE_DIR / "reports"
DATABASE_PATH = DATA_DIR / "archive.db"
COMPANIES_CSV = DATA_DIR / "companies.csv"
COMPANY_PROFILES_CSV = DATA_DIR / "company_profiles.csv"
OFFICIAL_JOBS_CSV = DATA_DIR / "official_job_sources.csv"
NEWS_LIMIT_PER_COMPANY = 12
NEWS_PERIOD = "1d"
ISSUE_SIMILARITY_THRESHOLD = 82
USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
KEYWORDS = ["수주", "공사", "건설", "재건축", "재개발", "정비사업", "분양", "해외사업", "플랜트", "안전", "사고", "소송", "제재", "실적", "영업이익", "연구", "기술", "특허", "신기술", "ESG"]
