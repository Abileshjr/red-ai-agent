import requests
import feedparser
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

client = InferenceClient(token=HF_API_TOKEN)

SUBREDDITS = [
    "https://www.reddit.com/r/technology/.rss",
    "https://www.reddit.com/r/programming/.rss",
    "https://www.reddit.com/r/artificial/.rss"
]

def fetch_posts():
    posts = []
    for url in SUBREDDITS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            posts.append({
                "title": entry.title,
                "content": entry.summary,
                "url": entry.link
            })
    return posts[:10]

def summarize(text):
    import requests

    API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": text[:300]
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    print("STATUS:", response.status_code)
    print("RAW:", response.text)

    try:
        result = response.json()

        if isinstance(result, list):
            return result[0].get("summary_text", "No summary")

        return str(result)

    except:
        return "Parsing error"

def send_to_discord(post, summary):
    message = f"""
📢 **{post['title']}**

🧠 Summary:
{summary}

🔗 {post['url']}
"""
    requests.post(DISCORD_WEBHOOK, json={"content": message})

def main():
    posts = fetch_posts()
    for post in posts:
        text = post["title"] + " " + post["content"]
        summary = summarize(text)
        send_to_discord(post, summary)

if __name__ == "__main__":
    main()
