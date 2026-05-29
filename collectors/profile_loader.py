import pandas as pd
from config import COMPANIES_CSV, COMPANY_PROFILES_CSV, LOGO_DIR
from database import init_db, upsert_company_profile

def find_logo(company):
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        path = LOGO_DIR / f"{company}{ext}"
        if path.exists(): return str(path)
    return ""

def seed_company_profiles():
    init_db()
    companies = pd.read_csv(COMPANIES_CSV).fillna("")
    profiles = pd.read_csv(COMPANY_PROFILES_CSV).fillna("")
    merged = companies.merge(profiles[["company", "vision", "talent", "business_areas", "notes"]], on="company", how="left").fillna("")
    for _, row in merged.iterrows():
        data = {"rank": int(row["rank"]), "company": row["company"], "aliases": row.get("aliases", ""), "homepage": row.get("homepage", ""), "news_url": row.get("news_url", ""), "careers_url": row.get("careers_url", ""), "logo_path": find_logo(row["company"]), "vision": row.get("vision", ""), "talent": row.get("talent", ""), "business_areas": row.get("business_areas", ""), "notes": row.get("notes", "")}
        upsert_company_profile(data)
        print(f"Profile saved: {row['company']}")
