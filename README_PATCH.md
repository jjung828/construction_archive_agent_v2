# v3.1 Profile Clean Patch

기존 `construction_archive_agent_v3` 폴더에 덮어쓰기/추가하세요.

## 해결하는 문제
- 회사정보에 공식 홈페이지 원문이 길게 그대로 들어가는 문제 해결
- LLM으로 비전/인재상/사업영역을 3~5줄 요약 정리
- LLM 실패 시 원문을 그대로 저장하지 않고 빈 값/확인 필요로 처리
- UI에서 회사정보를 카드 형태로 정리
- `data/company_profiles.csv`에도 정리된 결과를 다시 저장

## 실행 순서

1. Ollama 켜기
```bash
ollama run qwen2.5:7b
```

2. `.env` 확인
```env
USE_LLM=true
LLM_PROVIDER=ollama
OLLAMA_MODEL=qwen2.5:7b
```

3. 패키지 설치
```bash
pip install -r requirements.txt
```

4. 회사정보 LLM 정리 실행
```bash
python update_company_profiles.py
```

5. DB 다시 반영
```bash
python seed_company_profiles.py
```

6. 화면 실행
```bash
streamlit run ui/streamlit_app.py
```
