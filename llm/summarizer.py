import json
import requests
from config import USE_LLM, LLM_PROVIDER, OPENAI_API_KEY, OPENAI_MODEL, OLLAMA_URL, OLLAMA_MODEL

def classify_category(text):
    text = text or ""
    rules = [("수주", ["수주", "계약", "낙찰", "시공권", "우선협상"]), ("분양", ["분양", "청약", "입주", "견본주택"]), ("재건축·재개발", ["재건축", "재개발", "정비사업"]), ("해외사업", ["해외", "사우디", "미국", "베트남", "중동", "플랜트"]), ("실적·재무", ["실적", "매출", "영업이익", "순이익", "적자", "흑자"]), ("안전사고", ["사고", "안전", "붕괴", "사망", "중대재해"]), ("소송·제재", ["소송", "제재", "과징금", "처분", "수사", "검찰"]), ("연구개발·기술", ["연구", "기술", "특허", "신기술", "R&D", "스마트건설"]), ("ESG", ["ESG", "친환경", "탄소", "사회공헌", "지속가능"]), ("인사·조직", ["인사", "대표", "임원", "조직개편"])]
    for cat, keys in rules:
        if any(k in text for k in keys): return cat
    return "기타"

def classify_sentiment(text):
    if any(k in text for k in ["사고", "붕괴", "사망", "중대재해", "소송", "제재", "과징금", "적자", "부실"]): return "부정"
    if any(k in text for k in ["수주", "계약", "흑자", "성장", "개발", "신기술", "ESG", "친환경"]): return "긍정"
    return "중립"

def estimate_importance(text):
    if any(k in text for k in ["조", "대형", "해외", "중대재해", "붕괴", "검찰", "국토부", "시공권", "영업이익"]): return 5
    if any(k in text for k in ["수주", "분양", "재건축", "재개발", "ESG", "기술", "특허"]): return 3
    return 1

def fallback_article(company, article):
    text = f"{article.get('title','')} {article.get('body_excerpt','')}"
    return {"summary": (article.get("body_excerpt") or article.get("title", ""))[:600], "category": classify_category(text), "sentiment": classify_sentiment(text), "importance": estimate_importance(text)}

def safe_json(text):
    try: return json.loads(text)
    except Exception:
        s, e = text.find("{"), text.rfind("}")
        if s != -1 and e != -1 and e > s:
            try: return json.loads(text[s:e+1])
            except Exception: return None
    return None

def complete(prompt):
    if LLM_PROVIDER == "openai":
        from openai import OpenAI
        if not OPENAI_API_KEY: raise RuntimeError("OPENAI_API_KEY is empty.")
        client = OpenAI(api_key=OPENAI_API_KEY)
        res = client.chat.completions.create(model=OPENAI_MODEL, messages=[{"role":"system","content":"너는 한국 건설산업 뉴스 분석가다. 반드시 JSON만 출력한다."},{"role":"user","content":prompt}], temperature=0.1)
        return res.choices[0].message.content
    payload = {"model": OLLAMA_MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.1}}
    res = requests.post(OLLAMA_URL, json=payload, timeout=180); res.raise_for_status(); return res.json().get("response", "")

def summarize_article(company, article):
    fallback = fallback_article(company, article)
    if not USE_LLM: return fallback
    prompt = f'''아래 건설사 관련 기사를 분석해 JSON만 출력해.\n회사명: {company}\n제목: {article.get('title','')}\n내용:\n{article.get('body_excerpt','')}\nJSON: {{"summary":"3문장 이하 핵심 요약","category":"수주|분양|재건축·재개발|해외사업|실적·재무|안전사고|소송·제재|연구개발·기술|ESG|인사·조직|기타","sentiment":"긍정|중립|부정","importance":1}}'''
    try:
        p = safe_json(complete(prompt))
        if not p: return fallback
        return {"summary": p.get("summary", fallback["summary"]), "category": p.get("category", fallback["category"]), "sentiment": p.get("sentiment", fallback["sentiment"]), "importance": int(p.get("importance", fallback["importance"]))}
    except Exception as e:
        print(f"LLM article fallback: {e}"); return fallback

def summarize_issue(company, articles):
    if not articles: return {}
    rep = articles[0]
    fallback = {"representative_title": rep.get("title", ""), "issue_summary": f"{company} 관련 유사 기사 {len(articles)}건이 수집됨. 대표 기사: {rep.get('title','')}", "category": classify_category(" ".join(a.get("title","") for a in articles)), "sentiment": classify_sentiment(" ".join(a.get("title","") for a in articles)), "importance": max([a.get("importance", 1) for a in articles]), "article_count": len(articles), "urls": "\n".join([a.get("url","") for a in articles])}
    if not USE_LLM: return fallback
    joined = "\n\n".join([f"[{i}] 제목: {a.get('title','')}\n요약: {a.get('summary','')}\nURL: {a.get('url','')}" for i, a in enumerate(articles, start=1)])
    prompt = f'''아래 유사 기사 묶음을 하나의 이슈로 통합해 JSON만 출력해.\n회사명: {company}\n기사:\n{joined}\nJSON: {{"representative_title":"대표 이슈 제목","issue_summary":"3~5문장 이슈 요약","category":"수주|분양|재건축·재개발|해외사업|실적·재무|안전사고|소송·제재|연구개발·기술|ESG|인사·조직|기타","sentiment":"긍정|중립|부정","importance":1}}'''
    try:
        p = safe_json(complete(prompt))
        if not p: return fallback
        return {"representative_title": p.get("representative_title", fallback["representative_title"]), "issue_summary": p.get("issue_summary", fallback["issue_summary"]), "category": p.get("category", fallback["category"]), "sentiment": p.get("sentiment", fallback["sentiment"]), "importance": int(p.get("importance", fallback["importance"])), "article_count": len(articles), "urls": fallback["urls"]}
    except Exception as e:
        print(f"LLM issue fallback: {e}"); return fallback
