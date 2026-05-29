# v4.2 Company Report Patch

기존 construction_archive_agent_v3/v4 폴더에 덮어쓰기하세요.

## 핵심 변경
- 회사정보를 vision/talent/business_areas로 억지 분류하지 않고,
  회사별 자유형 리서치 보고서 형태로 정리합니다.
- data/company_profile_sources.csv에 회사별 공식 페이지 URL을 넣으면,
  해당 페이지들을 수집해서 LLM으로 회사 리포트를 생성합니다.
- Streamlit 회사정보 탭에서 기존 칸형 정보보다 회사 리포트를 우선 표시합니다.

## 실행 순서

1. 패치 덮어쓰기
2. Ollama 실행 상태 확인
```bash
ollama run qwen2.5:7b
```

3. .env 확인
```env
USE_LLM=true
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b
```

4. 리포트 생성
```bash
python update_company_reports.py
```

5. DB 반영
```bash
python seed_company_reports.py
```

6. 실행
```bash
streamlit run ui/streamlit_app.py
```

## 회사별 수집 페이지 추가 방법

`data/company_profile_sources.csv`에 행 추가:

```csv
company,label,url,enabled
현대건설,인재상,https://www.hdec.kr/kr/career/talent01.aspx,true
```

회사별로 비전/인재상/사업영역/ESG/기술혁신/채용 페이지 등을 여러 개 넣을 수 있습니다.