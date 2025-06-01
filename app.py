from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import os

app = Flask(__name__)

# 環境変数（Renderに設定しておく）
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
GAS_URL = os.environ["GAS_URL"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except Exception as e:
        print(f"エラー: {e}")
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_msg = event.message.text.strip()

    # GASへデータ送信
    payload = {
        "user_id": user_id,
        "message": user_msg
    }
    try:
        res = requests.post(GAS_URL, json=payload)
        data = res.json()
    except Exception as e:
        print(f"GASエラー: {e}")
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text="占い中に予期せぬエラーが起きました。時間を置いてお試しください。"))
        return

    # GASからの返却値
    name = data.get("name", "")
    count = data.get("count", 0)
    premium = data.get("premium", False)

    # プレミアム登録処理
    if user_msg.startswith("プレミアムID:"):
        premium_code = user_msg.replace("プレミアムID:", "").strip()
        if premium_code == os.environ["PREMIUM_CODE"]:
            requests.post(GAS_URL, json={
                "user_id": user_id,
                "premium_update": True
            })
            reply = "プレミアム登録を確認しました。引き続き、どうぞよろしくお願いします。"
        else:
            reply = "申し訳ありません。プレミアムIDが確認できませんでした。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # 名前登録
    if not name:
        reply = "はじめまして。お名前を教えていただけますか？"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # 10通制限
    if not premium and count > 10:
        reply = "無料でのご相談は10通までとさせていただいております。\nご継続をご希望の場合はプレミアム登録をお願いいたします。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
        return

    # GPT応答生成（ここは簡易化例）
    prompt = f"{name}さんからのご相談：「{user_msg}」\nこの内容を霊視占い師として冷静に助言してください。"
    try:
        openai_key = os.environ["OPENAI_API_KEY"]
        headers = {
            "Authorization": f"Bearer {openai_key}",
            "Content-Type": "application/json"
        }
        json_data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "あなたは厳かで落ち着いた霊視占い師です。口調は冷静かつ敬意を持ち、距離を保ちながらも真摯に答えます。"},
                {"role": "user", "content": prompt}
            ]
        }
        res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=json_data)
        gpt_reply = res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"GPTエラー: {e}")
        gpt_reply = "申し訳ありません。現在、霊視が不安定なようです。少し時間を置いてから再度お試しください。"

    # 最終返信
    final_reply = f"{name}さん、{gpt_reply}"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=final_reply))

# Renderで必須：ポートバインド
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
