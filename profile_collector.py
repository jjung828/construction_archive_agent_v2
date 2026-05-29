from web_utils import extract_relevant_text, clean_text

VISION_KEYWORDS = ["비전", "vision", "미션", "mission", "경영이념", "핵심가치", "가치체계", "철학"]
TALENT_KEYWORDS = ["인재상", "인재", "talent", "채용", "recruit", "career", "역량", "도전", "창의", "전문성", "소통"]
BUSINESS_KEYWORDS = ["사업영역", "사업분야", "주요사업", "건축", "토목", "플랜트", "주택", "인프라", "개발", "환경", "에너지"]

def compact(text):
    text = clean_text(text)
    if not text:
        return ""
    return text[:900] + ("..." if len(text) > 900 else "")

def collect_company_profile_texts(company, homepage="", careers_url="", news_url=""):
    vision = extract_relevant_text(homepage, VISION_KEYWORDS, 900) if homepage else ""
    business = extract_relevant_text(homepage, BUSINESS_KEYWORDS, 900) if homepage else ""
    talent = extract_relevant_text(careers_url, TALENT_KEYWORDS, 900) if careers_url else ""
    if not talent and homepage:
        talent = extract_relevant_text(homepage, TALENT_KEYWORDS, 900)
    return {"vision": compact(vision), "talent": compact(talent), "business_areas": compact(business)}