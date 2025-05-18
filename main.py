import os
import openai
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
GPT_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = GPT_API_KEY

def reply_to_line(reply_token, message):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    body = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post(url, headers=headers, json=body)

def generate_fortune(user_text):
    prompt = f"""
あなたは霊視占い師「恋月れんげつ」です。
以下の相談者の言葉をもとに、恋愛に関する未来をやさしく2〜3文で占ってください。
少し神秘的な口調で、的確なアドバイスをお願いします。

【相談内容】
{user_text}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150
    )
    return response["choices"][0]["message"]["content"]

# 恋愛占いっぽい内容かを判定する関数
def is_fortune_related(text):
    keywords = ["恋", "未来", "運命", "相手", "復縁", "縁", "出会い", "別れ", "相性", "付き合", "好き", "気になる", "結婚"]
    return any(kw in text for kw in keywords)

@app.route("/webhook", methods=["POST"])
def webhook():
    body = request.json
    for event in body["events"]:
        if event["type"] == "message" and event["message"]["type"] == "text":
            user_text = event["message"]["text"]
            reply_token = event["replyToken"]

            if is_fortune_related(user_text):
                result = generate_fortune(user_text)
            else:
                result = "ふふ…れんげつに占ってほしいことがあれば、恋の話をしてみてくださいね♡"

            reply_to_line(reply_token, result)
    return "OK"

# Render用ポートバインド対応
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
