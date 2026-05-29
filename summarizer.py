def classify_category(text):
    text = text or ""

    if any(k in text for k in ["채용", "공채", "신입", "경력", "인턴", "모집"]):
        return "채용"
    if any(k in text for k in ["수주", "계약", "낙찰", "시공권", "우선협상"]):
        return "수주"
    if any(k in text for k in ["분양", "청약", "입주", "견본주택"]):
        return "분양"
    if any(k in text for k in ["재건축", "재개발", "정비사업"]):
        return "재건축·재개발"
    if any(k in text for k in ["해외", "사우디", "미국", "베트남", "중동", "플랜트"]):
        return "해외사업"
    if any(k in text for k in ["실적", "매출", "영업이익", "순이익", "적자", "흑자"]):
        return "실적·재무"
    if any(k in text for k in ["사고", "안전", "붕괴", "사망", "중대재해"]):
        return "안전사고"
    if any(k in text for k in ["소송", "제재", "과징금", "처분", "수사", "검찰"]):
        return "소송·제재"
    if any(k in text for k in ["연구", "기술", "특허", "신기술", "R&D", "스마트건설"]):
        return "연구개발·기술"
    if any(k in text for k in ["ESG", "친환경", "탄소", "사회공헌", "지속가능"]):
        return "ESG"
    if any(k in text for k in ["인사", "대표", "임원", "조직개편"]):
        return "인사·조직"

    return "기타"

def classify_sentiment(text):
    text = text or ""

    negative = ["사고", "붕괴", "사망", "중대재해", "소송", "제재", "과징금", "적자", "부실"]
    positive = ["수주", "계약", "흑자", "성장", "개발", "신기술", "ESG", "친환경", "채용"]

    if any(k in text for k in negative):
        return "부정"
    if any(k in text for k in positive):
        return "긍정"

    return "중립"

def estimate_importance(text):
    text = text or ""

    high = ["조", "대형", "해외", "중대재해", "붕괴", "검찰", "국토부", "시공권", "영업이익", "공채"]
    middle = ["수주", "분양", "재건축", "재개발", "ESG", "기술", "특허", "채용"]

    score = 1

    if any(k in text for k in middle):
        score = 3

    if any(k in text for k in high):
        score = 5

    return score

def summarize_article(company, article):
    title = article.get("title", "")
    content = article.get("content", "")
    text = f"{title} {content}"

    summary = content if content else title

    return {
        "summary": summary[:500],
        "category": classify_category(text),
        "sentiment": classify_sentiment(text),
        "importance": estimate_importance(text)
    }

def summarize_issue_cluster(company, articles):
    if not articles:
        return {}

    rep = articles[0]
    combined = " ".join([f"{a.get('title','')} {a.get('summary','')}" for a in articles])
    category = classify_category(combined)
    sentiment = classify_sentiment(combined)
    importance = max([a.get("importance", 1) for a in articles])

    summary = f"{company} 관련 동일/유사 이슈로 판단되는 기사 {len(articles)}건이 수집됨. 대표 기사: {rep.get('title', '')}"

    return {
        "representative_title": rep.get("title", ""),
        "issue_summary": summary,
        "category": category,
        "sentiment": sentiment,
        "importance": importance,
        "article_count": len(articles),
        "urls": "\n".join([a.get("url", "") for a in articles])
    }