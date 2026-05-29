from news_collector import load_companies
from database import init_db, upsert_company_profile
from profile_collector import collect_company_profile_texts

def main():
    init_db()
    companies = load_companies()
    for _, row in companies.iterrows():
        company = row["company"]
        print(f"Collecting company profile: {company}")
        collected = collect_company_profile_texts(
            company=company,
            homepage=row.get("homepage", ""),
            careers_url=row.get("careers_url", ""),
            news_url=row.get("news_url", "")
        )
        data = {
            "rank": int(row["rank"]),
            "company": company,
            "aliases": row.get("aliases", ""),
            "homepage": row.get("homepage", ""),
            "news_url": row.get("news_url", ""),
            "careers_url": row.get("careers_url", ""),
            "vision": collected.get("vision", ""),
            "talent": collected.get("talent", ""),
            "business_areas": collected.get("business_areas", ""),
        }
        upsert_company_profile(data)
        print(f"Profile saved: {company}")
    print("Company profile seed done.")

if __name__ == "__main__":
    main()