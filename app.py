from flask import Flask, request
import requests
import os
from google import genai

app = Flask(__name__)

# 🔐 ENV VARIABLES (Render)
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MY_USERNAME = "vsingh_rides"

# 🤖 Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# 🧠 Prevent duplicate replies
processed_comments = set()


# 🔹 Home route
@app.route("/")
def home():
    return "Gemini AI Bot Running 🚀"


# 🔹 Webhook verification
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Verification failed", 403


# 🔹 Get post caption
def get_post_caption(media_id):
    try:
        url = f"https://graph.facebook.com/v19.0/{media_id}"
        params = {
            "fields": "caption",
            "access_token": ACCESS_TOKEN
        }

        res = requests.get(url, params=params)
        data = res.json()

        return data.get("caption", "")

    except Exception as e:
        print("Caption fetch error:", e)
        return ""


# 🔹 Webhook handler
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("📩 Incoming:", data)

    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                if "text" in value:
                    comment_id = value.get("id")
                    text = value.get("text", "")
                    username = value.get("from", {}).get("username")
                    parent_id = value.get("parent_id")
                    media_id = value.get("media", {}).get("id")

                    print(f"💬 Comment: {text} | User: {username}")

                    # 🚫 Skip own comments
                    if username == MY_USERNAME:
                        continue

                    # 🚫 Skip replies
                    if parent_id and parent_id != comment_id:
                        continue

                    # 🚫 Avoid duplicate replies
                    if comment_id in processed_comments:
                        continue

                    processed_comments.add(comment_id)

                    # 🧠 Get post caption
                    caption = get_post_caption(media_id)

                    print("📌 Caption:", caption)

                    # 🤖 Generate AI reply
                    reply = generate_ai_reply(text, caption)

                    # 📤 Send reply
                    reply_to_comment(comment_id, reply)

    except Exception as e:
        print("❌ Error:", e)

    return "ok", 200


# 🤖 Gemini AI reply (context-aware)
def generate_ai_reply(user_text, caption):
    try:
        prompt = f"""
        You are a friendly Instagram creator.

        POST CAPTION:
        {caption}

        USER COMMENT:
        {user_text}

        Write a short, human-like reply (1-2 lines):
        - Understand the post context
        - Use emojis
        - Sound natural (not robotic)
        - Slightly encourage engagement or follow

        Reply:
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text.strip()

    except Exception as e:
        print("AI Error:", e)
        return "Thanks 🙌🔥"


# 📤 Reply to comment
def reply_to_comment(comment_id, message):
    url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"

    payload = {
        "message": message,
        "access_token": ACCESS_TOKEN
    }

    res = requests.post(url, data=payload)
    print("📤 Reply Response:", res.text)


# 🔹 Optional: check models (debug)
@app.route("/models")
def list_models():
    try:
        models = client.models.list()
        return {"models": [m.name for m in models]}
    except Exception as e:
        return {"error": str(e)}


# 🚀 Run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
