import pandas as pd
from collectors.company_report_collector import collect_company_raw_reports, REPORTS_CSV
from llm.company_report_summarizer import build_company_report

def main():
    grouped = collect_company_raw_reports()

    if not grouped:
        raise RuntimeError("보고서 생성 대상 회사가 0개입니다.")

    rows = []

    for company, data in grouped.items():
        raw_text = "\n\n".join(data["raw_text"])
        source_urls = "\n".join(data["sources"])

        print(f"Building company report: {company}")
        report_md = build_company_report(company, raw_text, source_urls)

        rows.append({
            "company": company,
            "report_md": report_md,
            "source_urls": source_urls
        })

    df = pd.DataFrame(rows)

    if df.empty:
        raise RuntimeError("company_reports.csv로 저장할 데이터가 0행입니다.")

    df.to_csv(REPORTS_CSV, index=False, encoding="utf-8-sig")
    print(f"Saved: {REPORTS_CSV}")
    print(f"Report rows: {len(df)}")

if __name__ == "__main__":
    main()