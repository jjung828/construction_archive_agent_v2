import json
import requests

from config import (
    USE_LLM,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    OLLAMA_URL,
    OLLAMA_MODEL,
)

def _safe_json(text):
    try:
        return json.loads(text)
    except Exception:
        s = text.find("{")
        e = text.rfind("}")
        if s != -1 and e != -1 and e > s:
            try:
                return json.loads(text[s:e+1])
            except Exception:
                return None
    return None

def _openai_complete(prompt):
    from openai import OpenAI
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is empty.")
    client = OpenAI(api_key=OPENAI_API_KEY)
    res = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "너는 한국 건설사 리서치 보고서를 작성하는 애널리스트다. "
                    "공식 홈페이지 텍스트에 근거해 간결하고 읽기 좋은 Markdown 보고서를 작성한다."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.15,
    )
    return res.choices[0].message.content

def _ollama_complete(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.15}
    }
    res = requests.post(OLLAMA_URL, json=payload, timeout=240)
    res.raise_for_status()
    return res.json().get("response", "")

def _complete(prompt):
    if LLM_PROVIDER == "openai":
        return _openai_complete(prompt)
    return _ollama_complete(prompt)

def build_company_report(company, raw_text, source_urls):
    raw_text = (raw_text or "").strip()
    if not raw_text:
        return f"""# {company} 회사 리포트

공식 페이지에서 충분한 텍스트를 수집하지 못했습니다.

## 확인 필요
- 회사 공식 홈페이지
- 채용/인재상 페이지
- 사업소개 페이지
"""

    if not USE_LLM:
        return f"""# {company} 회사 리포트

LLM이 비활성화되어 자동 보고서를 생성하지 않았습니다.

## 수집 원문 일부
{raw_text[:1500]}
"""

    prompt = f"""
아래는 {company}의 공식 페이지들에서 수집한 텍스트다.
기존처럼 vision/talent/business 같은 칸에 억지로 맞추지 말고,
회사별 리서치 보고서 형태의 Markdown을 작성해라.

요구사항:
- 공식 텍스트에 근거한 내용만 작성
- 메뉴, 푸터, 공유 버튼, 법적고지, 반복 문구 제거
- 너무 세부 페이지명이 아니라 회사 이해에 도움되는 내용 중심
- 섹션은 상황에 맞게 자유롭게 구성
- 단, 아래 큰 흐름은 가능하면 포함:
  1) 기업 개요
  2) 사업/기술/시장 포지션
  3) 인재상/조직문화
  4) 채용 관점에서 볼 포인트
  5) 확인 필요/자료 부족
- 각 섹션은 너무 길지 않게 bullet 중심
- Markdown만 출력

회사명: {company}

출처 목록:
{source_urls}

수집 텍스트:
{raw_text[:12000]}
"""

    try:
        result = _complete(prompt)
        result = result.strip()
        if not result:
            raise RuntimeError("empty LLM result")
        return result
    except Exception as e:
        return f"""# {company} 회사 리포트

LLM 보고서 생성 실패: {e}

## 수집 원문 일부
{raw_text[:1500]}
"""