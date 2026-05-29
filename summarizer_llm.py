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
from summarizer import summarize_article, summarize_issue_cluster

def _safe_json_loads(text):
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except Exception:
                pass
    return None

def _openai_complete(prompt):
    from openai import OpenAI

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is empty.")

    client = OpenAI(api_key=OPENAI_API_KEY)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "너는 한국 건설산업 뉴스 분석가다. "
                    "반드시 JSON만 출력한다. "
                    "요약은 과장하지 말고, 기사에 있는 내용만 근거로 작성한다."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )

    return response.choices[0].message.content

def _ollama_complete(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1
        }
    }

    res = requests.post(OLLAMA_URL, json=payload, timeout=120)
    res.raise_for_status()

    return res.json().get("response", "")

def _llm_complete(prompt):
    if LLM_PROVIDER == "ollama":
        return _ollama_complete(prompt)
    return _openai_complete(prompt)

def summarize_article_with_llm(company, article):
    fallback = summarize_article(company, article)

    if not USE_LLM:
        return fallback

    title = article.get("title", "")
    content = article.get("content", "")
    source = article.get("source", "")
    url = article.get("url", "")

    prompt = f"""
아래 건설사 관련 기사를 분석해 JSON만 출력해.

회사명: {company}
제목: {title}
출처: {source}
URL: {url}
내용:
{content}

출력 JSON 스키마:
{{
  "summary": "3문장 이하 핵심 요약",
  "category": "수주|분양|재건축·재개발|해외사업|실적·재무|안전사고|소송·제재|연구개발·기술|ESG|인사·조직|채용|기타",
  "sentiment": "긍정|중립|부정",
  "importance": 1
}}

importance는 1~5 정수로 판단해.
"""

    try:
        raw = _llm_complete(prompt)
        parsed = _safe_json_loads(raw)

        if not parsed:
            return fallback

        return {
            "summary": parsed.get("summary", fallback["summary"]),
            "category": parsed.get("category", fallback["category"]),
            "sentiment": parsed.get("sentiment", fallback["sentiment"]),
            "importance": int(parsed.get("importance", fallback["importance"])),
        }

    except Exception as e:
        print(f"LLM article fallback: {e}")
        return fallback

def summarize_issue_cluster_with_llm(company, articles):
    fallback = summarize_issue_cluster(company, articles)

    if not USE_LLM or not articles:
        return fallback

    joined = "\n\n".join(
        [
            f"[{idx}] 제목: {a.get('title','')}\n요약: {a.get('summary','')}\nURL: {a.get('url','')}"
            for idx, a in enumerate(articles, start=1)
        ]
    )

    prompt = f"""
아래는 같은 건설사 관련 유사 기사 묶음이다.
중복 기사를 하나의 이슈로 통합해서 JSON만 출력해.

회사명: {company}

기사 목록:
{joined}

출력 JSON 스키마:
{{
  "representative_title": "이슈를 가장 잘 나타내는 제목",
  "issue_summary": "이슈 단위 3~5문장 요약",
  "category": "수주|분양|재건축·재개발|해외사업|실적·재무|안전사고|소송·제재|연구개발·기술|ESG|인사·조직|채용|기타",
  "sentiment": "긍정|중립|부정",
  "importance": 1
}}

importance는 1~5 정수.
기사에 없는 내용은 추정하지 마.
"""

    try:
        raw = _llm_complete(prompt)
        parsed = _safe_json_loads(raw)

        if not parsed:
            return fallback

        return {
            "representative_title": parsed.get("representative_title", fallback["representative_title"]),
            "issue_summary": parsed.get("issue_summary", fallback["issue_summary"]),
            "category": parsed.get("category", fallback["category"]),
            "sentiment": parsed.get("sentiment", fallback["sentiment"]),
            "importance": int(parsed.get("importance", fallback["importance"])),
            "article_count": len(articles),
            "urls": "\n".join([a.get("url", "") for a in articles]),
        }

    except Exception as e:
        print(f"LLM issue fallback: {e}")
        return fallback