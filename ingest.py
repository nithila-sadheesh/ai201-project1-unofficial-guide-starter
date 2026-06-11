import requests
from bs4 import BeautifulSoup
import json
import os
import re
import time

DOCUMENTS_DIR = "documents"

# Reddit's JSON API requires a real User-Agent or it returns 429/403
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

SOURCES = [
    {"id": 1, "type": "article", "name": "hercampus",
     "url": "https://www.hercampus.com/school/uc-berkeley/uc-berkeley-college-survival-guide/"},
    {"id": 2, "type": "article", "name": "dailycal_survival",
     "url": "https://www.dailycal.org/archives/uc-berkeley-survival-guide-for-newer-students/article_5664df0b-aa7e-5076-8a5a-17be645aa5a9.html"},
    {"id": 3, "type": "article", "name": "plexuss",
     "url": "https://plexuss.com/n/uc-berkeley-college-survival-guide"},
    {"id": 4, "type": "article", "name": "dailycal_motivated",
     "url": "https://www.dailycal.org/archives/stay-motivated-a-uc-berkeley-survival-guide/article_f2a640cd-ea05-5e97-859d-e470df9401ae.html"},
    {"id": 5, "type": "reddit", "name": "reddit_new_student",
     "url": "https://www.reddit.com/r/berkeley/comments/1dqccmk/what_should_every_new_cal_student_know_about/"},
    {"id": 6, "type": "reddit", "name": "reddit_mental_health",
     "url": "https://www.reddit.com/r/berkeley/comments/16hgeb0/mental_health_resource_guide_and_a/"},
    {"id": 7, "type": "reddit", "name": "reddit_safety",
     "url": "https://www.reddit.com/r/berkeley/comments/15njiw6/what_is_essential_to_haveknow_when_living_in/"},
    {"id": 8, "type": "reddit", "name": "reddit_eecs",
     "url": "https://www.reddit.com/r/berkeley/comments/25kp1d/how_to_survive_berkeley_eecs/"},
    {"id": 9, "type": "reddit", "name": "reddit_finals",
     "url": "https://www.reddit.com/r/berkeley/comments/13c6atg/guide_to_maximizing_your_score_on_your_finals_if/"},
    {"id": 10, "type": "reddit", "name": "reddit_succeed",
     "url": "https://www.reddit.com/r/berkeley/comments/pfa2j3/how_to_succeed_at_berkeley/"},
]


def clean_text(text):
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&[a-z]+;', '', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def fetch_article(source):
    print(f"  Fetching article: {source['name']} ...")

    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ERROR fetching {source['name']}: {e}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # Strip obvious clutter
    for tag in soup([
        "script", "style", "nav", "header", "footer",
        "aside", "form", "button", "noscript", "iframe"
    ]):
        tag.decompose()

    # Find main content
    content = (
        soup.find("article")
        or soup.find("main")
        or soup.find(
            class_=re.compile(
                r"article[_-]?body|post[_-]?body|entry[_-]?content|story[_-]?body",
                re.I,
            )
        )
        or soup.find(id=re.compile(r"article|content|main|story", re.I))
        or soup.body
    )

    if content is None:
        print(
            f"  WARNING: could not isolate content for {source['name']}, using full page"
        )
        content = soup

    # Remove Daily Cal / TownNews social-share widgets
    for tag in content.select(
        ".share-container, "
        ".social-share-links, "
        ".social-share-link, "
        "#share-left-affix"
    ):
        tag.decompose()

    text = content.get_text(separator="\n")
    text = clean_text(text)

    return {
        "id": source["id"],
        "type": "article",
        "name": source["name"],
        "url": source["url"],
        "content": text,
    }


def extract_comments(node, depth=0, max_depth=1):
    """Recursively extract top-level comments and their direct replies."""
    comments = []
    children = node.get("data", {}).get("children", [])
    for child in children:
        if child.get("kind") != "t1":
            continue
        data = child.get("data", {})
        body = data.get("body", "").strip()

        # Skip deleted, removed, or very short comments
        if body in ("[deleted]", "[removed]", "") or len(body) < 30:
            continue

        comments.append(body)

        # Include direct replies at depth 0 only
        if depth < max_depth and isinstance(data.get("replies"), dict):
            comments.extend(extract_comments(data["replies"], depth + 1, max_depth))

    return comments


def fetch_reddit(source):
    # Check for a manually saved raw JSON first (in case Reddit blocks automated requests)
    local_path = os.path.join(DOCUMENTS_DIR, "raw", f"{source['name']}.json")
    if os.path.exists(local_path):
        print(f"  Loading Reddit from local file: {local_path}")
        with open(local_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        print(f"  Fetching Reddit thread: {source['name']} ...")
        json_url = source["url"].rstrip("/") + ".json"
        try:
            resp = requests.get(json_url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  ERROR fetching {source['name']}: {e}")
            print(f"  → Visit {source['url']}.json in your browser, save it to documents/raw/{source['name']}.json, then re-run.")
            return None

    post_data = data[0]["data"]["children"][0]["data"]
    title = post_data.get("title", "").strip()

    # Include the post body if it has substantive text (not just a question prompt)
    selftext = post_data.get("selftext", "").strip()
    comments = []
    if selftext and selftext not in ("[deleted]", "[removed]") and len(selftext) > 50:
        comments.append(selftext)

    comments.extend(extract_comments(data[1]))

    print(f"  Found {len(comments)} comments")

    return {
        "id": source["id"],
        "type": "reddit",
        "name": source["name"],
        "url": source["url"],
        "title": title,
        "comments": comments,
    }


def save_document(doc):
    filename = f"{doc['name']}.json"
    path = os.path.join(DOCUMENTS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=2)
    print(f"  Saved → {path}")


def main():
    os.makedirs(DOCUMENTS_DIR, exist_ok=True)

    for source in SOURCES:
        print(f"\n[{source['id']}/10] {source['name']}")
        if source["type"] == "article":
            doc = fetch_article(source)
        else:
            doc = fetch_reddit(source)
            time.sleep(2)  # be polite to Reddit's API

        if doc:
            save_document(doc)
        else:
            print(f"  SKIPPED — fetch failed. Save the page manually as documents/{source['name']}.json")

    print("\nDone. Review one article output before running chunk.py:")
    print("  python -c \"import json; d=json.load(open('documents/hercampus.json')); print(d['content'][:2000])\"")


if __name__ == "__main__":
    main()
