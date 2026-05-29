import pandas as pd
from config import DATA_DIR
from database import init_db, upsert_company_report

REPORTS_CSV = DATA_DIR / "company_reports.csv"

def read_reports_csv():
    encodings = ["utf-8-sig", "utf-8", "cp949", "euc-kr"]
    last_error = None

    if not REPORTS_CSV.exists():
        raise FileNotFoundError(f"Not found: {REPORTS_CSV}. Run python update_company_reports.py first.")

    if REPORTS_CSV.stat().st_size == 0:
        raise RuntimeError(f"{REPORTS_CSV} 파일이 0KB입니다. 삭제 후 python update_company_reports.py를 다시 실행하세요.")

    for enc in encodings:
        try:
            df = pd.read_csv(REPORTS_CSV, encoding=enc).fillna("")
            print(f"Loaded reports with encoding={enc}, rows={len(df)}")
            return df
        except Exception as e:
            last_error = e

    raise RuntimeError(f"company_reports.csv 읽기 실패: {last_error}")

def main():
    init_db()
    df = read_reports_csv()

    required = {"company", "report_md", "source_urls"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"company_reports.csv 컬럼 누락: {missing}")

    if df.empty:
        raise RuntimeError("company_reports.csv가 비어 있습니다. update_company_reports.py가 정상적으로 회사별 report rows를 만들었는지 확인하세요.")

    count = 0
    for _, row in df.iterrows():
        company = str(row["company"]).strip()
        if not company:
            continue

        upsert_company_report({
            "company": company,
            "report_md": row.get("report_md", ""),
            "source_urls": row.get("source_urls", ""),
        })
        count += 1
        print(f"Report seeded: {company}")

    print(f"Company reports seed done. rows={count}")

if __name__ == "__main__":
    main()