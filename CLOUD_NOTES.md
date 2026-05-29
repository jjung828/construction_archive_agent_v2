# Notes

## Why SQLite in GitHub?

혼자 쓰는 무료 운영에서는 SQLite 파일을 GitHub repo에 저장하는 방식이 가장 단순합니다.

장점:
- 별도 DB 서비스 불필요
- Supabase 500MB 제한 회피
- 코드/DB/리포트를 한 repo에서 관리
- Streamlit Cloud에서 바로 읽기 가능

단점:
- 동시에 여러 작업이 DB를 쓰면 충돌 가능
- 대용량에는 부적합
- 원문 전문 저장에는 부적합

그래서 이 프로젝트는 raw HTML 전체를 저장하지 않고, 요약/링크/이슈 중심으로 저장합니다.
