# v4.3 Company Report Fix

## 해결
- update_company_reports.py가 0행짜리 company_reports.csv를 만드는 문제 방지
- company_profile_sources.csv 인코딩 자동 처리: utf-8-sig / utf-8 / cp949 / euc-kr
- 빈 줄 제거
- enabled 값 TRUE/true/1/yes/y 모두 허용
- sources가 0개면 즉시 에러 메시지 출력
- seed_company_reports.py가 빈 CSV일 때 원인을 알 수 있게 출력

## 덮어쓸 파일
- collectors/company_report_collector.py
- update_company_reports.py
- seed_company_reports.py
- data/company_profile_sources.csv

## 실행
```bash
python update_company_reports.py
python seed_company_reports.py
streamlit run ui/streamlit_app.py
```