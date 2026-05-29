# v4 Patch

기존 construction_archive_agent_v3 폴더에 덮어쓰기하세요.

## 핵심 변경
- 뉴스는 reset_database.py를 직접 실행하지 않는 한 계속 누적 저장됩니다.
- 같은 회사 + 같은 URL은 중복 저장하지 않습니다.
- 뉴스/이슈 탭에 날짜 필터를 추가했습니다.
- 채용공고 수집 로그 테이블을 추가했습니다.
- 정오/자정 자동 실행 스케줄러를 추가했습니다.

## 추가 설치

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

## 1회 수동 실행

```bash
python seed_company_profiles.py
python main.py
streamlit run ui/streamlit_app.py
```

## 자동 실행

```bash
python scheduler.py
```

PC가 켜져 있고 scheduler.py 터미널이 살아 있어야 정오/자정에 자동으로 추가 수집됩니다.

## 중요
어제 뉴스가 사라지는 경우는 보통 `python reset_database.py`를 실행했기 때문입니다.
운영할 때는 reset_database.py를 실행하지 마세요.