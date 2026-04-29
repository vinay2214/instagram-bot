from flask import Flask, request
import requests
import os
import random

app = Flask(__name__)

ACCESS_TOKEN = "EAAL7JziZAf9YBRZAbzTz5DWDEgK5JLZBhpKaFD9CnAgx1sYpkNOGRyvZB4vucZBHzZCQfY53mNriMaFi0GjRKtyTN7TWnzJT8E8I0ZC44jOCZCZC9kcPEXrTOZASZBbsut2BANk3m3HJJAGTL9LoYKUSBZAOYjZCU1KMu1uPnTr1gegVqSqeM3M1cXPdZCDu8hsJ9OIoKzrgt4s515zTVzbZAKbxVF5GxcSjbZCTC3oLsYB8pGCg5tWVF2izeR3T67ItQ5pR4FDmrZCdZA4knvkZCrLk9e70S7TOQZDZD"
VERIFY_TOKEN = "vinay2022"
MY_USERNAME = "vsingh_rides"

processed_comments = set()

# 🔥 Smart keyword categories
KEYWORDS = {
    "positive": ["nice", "awesome", "great", "love", "amazing", "🔥", "😍", "❤️"],
    "question": ["how", "what", "price", "details", "where", "when"],
    "negative": ["bad", "worst", "fake", "not good"]
}

# 🔥 Reply variations
REPLIES = {
    "positive": [
        "Thanks 🙌🔥 Really appreciate it!",
        "Glad you liked it 😍 Stay tuned!",
        "Love the support ❤️ Follow for more!"
    ],
    "question": [
        "Great question! DM us 'HI' and we’ll help you 👀",
        "Send us a DM with 'INFO' 📩",
        "We’ll guide you—just DM us 👍"
    ],
    "negative": [
        "We’re sorry to hear that 😔 DM us so we can fix it!",
        "Let’s improve this—message us 🙌"
    ],
    "default": [
        "Thanks for commenting 🙌🔥",
        "Appreciate it ❤️",
        "Stay connected 🚀"
    ]
}


# 🔹 Home route
@app.route("/")
def home():
    return "Bot is live 🚀"


# 🔹 Verify webhook
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Error", 403


# 🔹 Main webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Incoming:", data)

    try:
        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})

                # 🔥 COMMENT HANDLING
                if "text" in value:
                    comment_id = value.get("id")
                    text = value.get("text", "").lower()
                    username = value.get("from", {}).get("username")
                    parent_id = value.get("parent_id")

                    # 🚫 Skip own comments
                    if username == MY_USERNAME:
                        continue

                    # 🚫 Skip replies
                    if parent_id and parent_id != comment_id:
                        continue

                    # 🚫 Skip duplicates
                    if comment_id in processed_comments:
                        continue

                    processed_comments.add(comment_id)

                    # 🎯 Decide reply type
                    reply_type = "default"
                    for key, words in KEYWORDS.items():
                        if any(word in text for word in words):
                            reply_type = key
                            break

                    message = random.choice(REPLIES[reply_type])

                    reply_to_comment(comment_id, message)

                # 🔥 DM HANDLING (only works if user messages you first)
                if "messages" in value:
                    for msg in value["messages"]:
                        sender_id = msg["from"]["id"]
                        text = msg.get("text", "").lower()

                        print("DM received:", text)

                        send_dm(sender_id, auto_reply_dm(text))

    except Exception as e:
        print("Error:", e)

    return "ok", 200


# 🔹 Reply to comment
def reply_to_comment(comment_id, message):
    url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"

    requests.post(url, data={
        "message": message,
        "access_token": ACCESS_TOKEN
    })


# 🔹 DM reply logic
def auto_reply_dm(text):
    if "hi" in text:
        return "Hey 👋 Thanks for reaching out! How can we help?"
    if "info" in text:
        return "Here are the details 🔥👇 (add your offer here)"
    return "Thanks for messaging us 🙌"


# 🔹 Send DM
def send_dm(user_id, message):
    url = "https://graph.facebook.com/v19.0/me/messages"

    payload = {
        "recipient": {"id": user_id},
        "message": {"text": message},
        "access_token": ACCESS_TOKEN
    }

    res = requests.post(url, json=payload)
    print("DM sent:", res.text)


# 🔹 Run app (Render compatible)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
