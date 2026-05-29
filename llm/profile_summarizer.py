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
                return json.loads(text[s:e + 1])
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
                    "너는 한국 건설사 기업정보를 정리하는 리서치 애널리스트다. "
                    "반드시 JSON만 출력한다. 공식 텍스트에 근거한 내용만 요약한다."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )
    return res.choices[0].message.content


def _ollama_complete(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1},
    }
    res = requests.post(OLLAMA_URL, json=payload, timeout=240)
    res.raise_for_status()
    return res.json().get("response", "")


def _complete(prompt):
    if LLM_PROVIDER == "openai":
        return _openai_complete(prompt)
    return _ollama_complete(prompt)


def summarize_company_profile(company, raw_text):
    if not USE_LLM:
        return {
            "vision": "",
            "talent": "",
            "business_areas": "",
            "notes": "LLM 비활성화 상태. 공식 자료 확인 후 직접 입력 필요.",
        }

    raw_text = (raw_text or "").strip()
    if not raw_text:
        return {
            "vision": "",
            "talent": "",
            "business_areas": "",
            "notes": "공식 페이지 텍스트를 충분히 수집하지 못함.",
        }

    raw_text = raw_text[:8000]
    prompt = f'''
아래는 {company}의 공식 홈페이지/채용페이지/사업소개 페이지에서 수집한 텍스트다.
메뉴명, 푸터, 반복 문구, '자세히보기', 'more', 파일명, 개인정보, 쿠키 안내 등은 제거하고
회사 소개 아카이브에 들어갈 내용만 정리해라.

중요:
- 모르는 내용은 추정하지 말고 빈 문자열로 둔다.
- 원문을 길게 붙여넣지 말고 핵심만 3~5개 항목으로 압축한다.
- 문장은 한국어로 자연스럽게 작성한다.
- 반드시 JSON만 출력한다.

회사명: {company}

수집 텍스트:
{raw_text}

JSON 스키마:
{{
  "vision": "비전/경영이념/핵심가치 요약. 없으면 빈 문자열",
  "talent": "인재상/채용 관련 핵심가치 요약. 없으면 빈 문자열",
  "business_areas": "주요 사업영역 요약. 없으면 빈 문자열",
  "notes": "출처 텍스트가 부족하거나 확인 필요한 점"
}}
'''

    try:
        parsed = _safe_json(_complete(prompt))
        if not parsed:
            raise RuntimeError("LLM did not return valid JSON.")
        return {
            "vision": (parsed.get("vision") or "").strip(),
            "talent": (parsed.get("talent") or "").strip(),
            "business_areas": (parsed.get("business_areas") or "").strip(),
            "notes": (parsed.get("notes") or "").strip(),
        }
    except Exception as e:
        print(f"Profile LLM fallback for {company}: {e}")
        return {
            "vision": "",
            "talent": "",
            "business_areas": "",
            "notes": f"LLM 정리 실패: {e}",
        }
