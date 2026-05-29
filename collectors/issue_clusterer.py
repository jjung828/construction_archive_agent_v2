from rapidfuzz import fuzz
from config import ISSUE_SIMILARITY_THRESHOLD

def normalize_title(title):
    if not title: return ""
    text = title
    for word in ["단독", "종합", "속보", "포토", "영상", "[", "]"]:
        text = text.replace(word, "")
    return text.strip()

def cluster_articles(articles, threshold=ISSUE_SIMILARITY_THRESHOLD):
    clusters = []
    for article in articles:
        title = normalize_title(article.get("title", ""))
        placed = False
        for cluster in clusters:
            rep = normalize_title(cluster[0].get("title", ""))
            if fuzz.token_set_ratio(title, rep) >= threshold:
                cluster.append(article); placed = True; break
        if not placed: clusters.append([article])
    return clusters
