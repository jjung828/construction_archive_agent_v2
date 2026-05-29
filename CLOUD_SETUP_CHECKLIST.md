# Cloud Setup Checklist

## GitHub
- [ ] repo 생성
- [ ] 프로젝트 파일 업로드
- [ ] Settings → Actions → General → Workflow permissions → Read and write permissions
- [ ] Actions 탭에서 `Collect construction archive` 수동 실행 확인

## Streamlit Cloud
- [ ] New app
- [ ] GitHub repo 선택
- [ ] Main file path: `ui/streamlit_app.py`
- [ ] Deploy

## 자동 수집 확인
- [ ] GitHub Actions 수동 실행 성공
- [ ] `data/archive.db`가 commit 되었는지 확인
- [ ] Streamlit 앱에서 오늘 뉴스/이슈 아카이브 표시 확인

## 운영 규칙
- [ ] reset_database.py는 클라우드 운영 중 실행하지 않기
- [ ] 원문 전문 저장 금지
- [ ] `maintenance/check_db_size.py`로 가끔 용량 확인
