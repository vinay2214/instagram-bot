from flask import Flask, request
import requests
import os

app = Flask(__name__)

# 🔑 Replace with your EAAG Page Access Token
ACCESS_TOKEN = "EAAL7JziZAf9YBRZAbzTz5DWDEgK5JLZBhpKaFD9CnAgx1sYpkNOGRyvZB4vucZBHzZCQfY53mNriMaFi0GjRKtyTN7TWnzJT8E8I0ZC44jOCZCZC9kcPEXrTOZASZBbsut2BANk3m3HJJAGTL9LoYKUSBZAOYjZCU1KMu1uPnTr1gegVqSqeM3M1cXPdZCDu8hsJ9OIoKzrgt4s515zTVzbZAKbxVF5GxcSjbZCTC3oLsYB8pGCg5tWVF2izeR3T67ItQ5pR4FDmrZCdZA4knvkZCrLk9e70S7TOQZDZD"

# 🔐 Verify token (same as Meta webhook)
VERIFY_TOKEN = "vinay2022"

# 👤 Your Instagram username
MY_USERNAME = "vsingh_rides"

# 💬 Positive keywords
POSITIVE_WORDS = [
    "nice", "awesome", "great", "🔥", "love", "good", "amazing",
    "wow", "cool", "best", "fantastic", "perfect",
    "😍", "❤️", "💯", "👏", "super"
]

# 🧠 Store processed comment IDs (avoid duplicates)
processed_comments = set()


# 🔹 Root route (important for Render health check)
@app.route("/", methods=["GET"])
def home():
    return "🚀 Instagram Bot is Running"


# 🔹 Webhook verification
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verified")
        return challenge
    return "❌ Verification failed", 403


# 🔹 Webhook event handler
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
                    comment_text = value.get("text", "").lower()
                    username = value.get("from", {}).get("username")
                    parent_id = value.get("parent_id")

                    print(f"💬 Comment: {comment_text} | User: {username}")

                    # 🚫 1. Skip your own comments (prevents infinite loop)
                    if username == MY_USERNAME:
                        print("🚫 Ignored own comment")
                        continue

                    # 🚫 2. Skip replies (only respond to main comments)
                    if parent_id and parent_id != comment_id:
                        print("🚫 Ignored reply comment")
                        continue

                    # 🚫 3. Skip duplicate webhook events
                    if comment_id in processed_comments:
                        print("⚠️ Duplicate skipped")
                        continue

                    processed_comments.add(comment_id)

                    # ✅ 4. Check for positive words
                    if any(word in comment_text for word in POSITIVE_WORDS):
                        reply_to_comment(comment_id)

    except Exception as e:
        print("❌ Error:", e)

    return "ok", 200


# 🔹 Reply to comment
def reply_to_comment(comment_id):
    url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"

    message = "Thanks for your support 🙌🔥 Follow us for more 🚀"

    payload = {
        "message": message,
        "access_token": ACCESS_TOKEN
    }

    response = requests.post(url, data=payload)
    print("📤 Reply Response:", response.text)


# 🔹 Run server (Render compatible)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)