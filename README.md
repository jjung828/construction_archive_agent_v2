# Construction Archive Agent v3

국내 건설사 뉴스·이슈·공식 채용공고·회사정보 아카이브 시스템입니다.

## 핵심 변경

- 회사정보 자동 크롤링 제거
- 검증된 `data/company_profiles.csv` 기반 표시
- 실제 로고 파일 지원: `data/logos/회사명.png`
- 로고 파일이 없으면 가짜 로고를 만들지 않음
- 채용공고 구조화
  - 회사명
  - 공고명
  - 채용구분
  - 접수시작일
  - 접수마감일
  - 상태
  - 공식 URL
- 공식 채용 페이지 중심 감시
- 뉴스 수집/이슈 클러스터/LLM 요약 유지

## 실행 순서

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

python reset_database.py
python seed_company_profiles.py
python main.py
streamlit run ui/streamlit_app.py
```

## 회사정보 입력

`data/company_profiles.csv`에 공식 홈페이지에서 확인한 문구를 직접 넣으세요.

```csv
company,vision,talent,business_areas
현대건설,...,...,...
```

## 로고 넣는 법

`data/logos/` 폴더에 정확한 회사명으로 파일을 넣으면 표시됩니다.

```text
data/logos/삼성물산.png
data/logos/현대건설.png
data/logos/대우건설.png
```

## 로컬 LLM 사용

Ollama 실행 후 `.env` 파일 생성:

```env
USE_LLM=true
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b
```

## OpenAI API 사용

```env
USE_LLM=true
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4.1-mini
```
