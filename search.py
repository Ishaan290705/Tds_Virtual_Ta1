import os
import json
from bs4 import BeautifulSoup

# Load and parse course content from tds-content.xml
def load_course_content(path="tds-content.xml"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "xml")
        docs = []
        for doc in soup.find_all("document"):
            source = doc.find("source").text.strip()
            content = doc.find("document_content").text.strip()
            docs.append((source, content))
        return docs
    except FileNotFoundError:
        print(f"[ERROR] Could not find the file: {path}")
        return []

# Load and parse scraped Discourse posts from JSON files
def load_discourse_posts(folder="discourse"):
    docs = []
    if not os.path.exists(folder):
        print(f"[WARNING] Discourse folder '{folder}' not found.")
        return docs
    for file in os.listdir(folder):
        if file.endswith(".json"):
            path = os.path.join(folder, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    title = data.get("title", "Discourse Post")
                    posts = data.get("post_stream", {}).get("posts", [])
                    content = "\n".join(p.get("cooked", "") for p in posts)
                    url = f"https://discourse.onlinedegree.iitm.ac.in/t/{file.replace('.json', '')}"
                    docs.append((url, f"{title}\n{content}"))
            except Exception as e:
                print(f"[ERROR] Could not load {file}: {e}")
    return docs

# Search for best match from any docs
def search_content(question: str, docs):
    q_words = question.lower().split()
    best_score = 0
    best_match = None

    for source, text in docs:
        text_lower = text.lower()
        match_count = sum(q in text_lower for q in q_words)
        if match_count > best_score:
            best_score = match_count
            best_match = (source, text)

    if best_match:
        source, text = best_match
        for line in text.split("\n"):
            if any(q in line.lower() for q in q_words):
                return line.strip(), [{"url": source, "text": "From course content"}]
        return "Matched, but couldn't extract a relevant line.", [{"url": source, "text": "From course content"}]

    return "Sorry, I couldn't find a match.", []

# Combine both sources
def load_all_content():
    return load_course_content() + load_discourse_posts()
