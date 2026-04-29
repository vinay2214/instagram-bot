from flask import Flask, request
import requests
import os
import google.generativeai as genai

app = Flask(__name__)

ACCESS_TOKEN = "EAAL7JziZAf9YBRZAbzTz5DWDEgK5JLZBhpKaFD9CnAgx1sYpkNOGRyvZB4vucZBHzZCQfY53mNriMaFi0GjRKtyTN7TWnzJT8E8I0ZC44jOCZCZC9kcPEXrTOZASZBbsut2BANk3m3HJJAGTL9LoYKUSBZAOYjZCU1KMu1uPnTr1gegVqSqeM3M1cXPdZCDu8hsJ9OIoKzrgt4s515zTVzbZAKbxVF5GxcSjbZCTC3oLsYB8pGCg5tWVF2izeR3T67ItQ5pR4FDmrZCdZA4knvkZCrLk9e70S7TOQZDZD"
VERIFY_TOKEN = "vinay2022"
MY_USERNAME = "vsingh_rides"

# 🔐 Gemini setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

processed_comments = set()


# 🔹 Home
@app.route("/")
def home():
    return "Gemini Bot Running 🚀"


# 🔹 Verify webhook
@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return "Error", 403


# 🔹 Webhook
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

                    print(f"💬 {text} | {username}")

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

                    # 🤖 Gemini reply
                    reply = generate_ai_reply(text)

                    reply_to_comment(comment_id, reply)

    except Exception as e:
        print("❌ Error:", e)

    return "ok", 200


# 🤖 Gemini AI reply
def generate_ai_reply(user_text):
    try:
        prompt = f"""
        You are a friendly Instagram creator.
        Reply to this comment in a short, engaging, human-like way.
        Use emojis and keep it under 1-2 lines.
        Encourage engagement naturally.

        Comment: {user_text}
        """

        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception as e:
        print("AI Error:", e)
        return "Thanks 🙌🔥"


# 🔹 Reply to comment
def reply_to_comment(comment_id, message):
    url = f"https://graph.facebook.com/v19.0/{comment_id}/replies"

    res = requests.post(url, data={
        "message": message,
        "access_token": ACCESS_TOKEN
    })

    print("📤 Reply:", res.text)


# 🔹 Run (Render compatible)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
