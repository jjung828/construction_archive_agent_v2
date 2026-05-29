# Cloud Deploy Patch: GitHub Actions + SQLite + Streamlit Cloud

이 패치는 로컬 PC 의존을 줄이고, GitHub에 올려둔 코드가 자동으로 뉴스/이슈를 수집하게 만드는 배포용 패치입니다.

## 목표 구조

```text
GitHub Repository
├─ data/archive.db
├─ main.py
├─ ui/streamlit_app.py
└─ .github/workflows/collect.yml
      └─ 매일 00:00 / 12:00 KST 자동 실행
```

Streamlit Cloud는 GitHub repo를 읽어서 웹앱을 띄우고, GitHub Actions는 정해진 시간에 `main.py`를 실행한 뒤 변경된 DB를 다시 repo에 커밋합니다.

## 무료 운영 원칙

DB에는 아래만 저장합니다.

- 회사명
- 기사 제목
- 요약
- 카테고리
- 중요도
- 원문 URL
- 이슈 묶음
- 채용공고 링크/상태

원문 전문 HTML 전체는 저장하지 않습니다.  
용량이 커지는 것을 막기 위해 `maintenance/compact_archive.py`가 긴 본문 일부를 자동으로 잘라냅니다.

## 1. GitHub repo 만들기

1. GitHub 접속
2. New repository
3. repo 이름 예: `construction-archive-agent`
4. Public 추천

## 2. 파일 업로드

현재 프로젝트 폴더 내용을 GitHub repo에 올립니다.

초기에는 아래 폴더/파일이 꼭 있어야 합니다.

```text
.github/workflows/collect.yml
data/
ui/streamlit_app.py
main.py
requirements.txt
config.py
database.py
```

## 3. GitHub Actions 권한 설정

GitHub repo에서:

```text
Settings → Actions → General → Workflow permissions
```

아래 선택:

```text
Read and write permissions
```

그리고 저장.

## 4. GitHub Secrets 설정

repo에서:

```text
Settings → Secrets and variables → Actions → New repository secret
```

### LLM 없이 완전 무료 운영

아무 secret 안 넣어도 됩니다.  
이 경우 규칙 기반 요약/분류로 돌아갑니다.

### OpenAI 사용 시

```text
OPENAI_API_KEY = sk-...
USE_LLM = true
LLM_PROVIDER = openai
OPENAI_MODEL = gpt-4.1-mini
```

## 5. 자동 수집 실행

자동 실행 시간:

```text
KST 00:00
KST 12:00
```

수동 실행:

```text
GitHub → Actions → Collect construction archive → Run workflow
```

## 6. Streamlit Cloud 배포

1. https://share.streamlit.io 접속
2. GitHub 계정 연결
3. New app
4. Repository 선택
5. Main file path:

```text
ui/streamlit_app.py
```

6. Deploy

## 7. 수정사항 생겼을 때

```text
수정 파일 덮어쓰기
→ GitHub에 commit/push
→ Streamlit Cloud 자동 반영
→ GitHub Actions 자동 수집에도 반영
```

## 8. 주의

- 연구실 PC가 꺼져도 상관없습니다.
- GitHub Actions가 수집을 담당합니다.
- Streamlit 앱은 보기 전용입니다.
- GitHub Actions는 정시에서 몇 분 지연될 수 있습니다.
- 대량 Playwright 크롤링은 무료 러너 시간을 많이 먹을 수 있으므로, 너무 많은 사이트를 한 번에 긁지 않는 게 좋습니다.
