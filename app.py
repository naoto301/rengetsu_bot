from flask import Flask, request, abort
import requests
import os
import json
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 環境変数
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
GAS_URL = os.environ["GAS_URL"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text.strip()

    # GASへ送信
    payload = {
        "user_id": user_id,
        "message": user_message
    }

    try:
        res = requests.post(GAS_URL, json=payload)
        res_data = res.json()
    except Exception:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="占い中に予期せぬエラーが起きました。時間を置いてお試しください。")
        )
        return

    reply1 = res_data.get("reply1")
    reply2 = res_data.get("reply2")

    messages = [TextSendMessage(text=reply1)]
    if reply2:
        messages.append(TextSendMessage(text=reply2))

    line_bot_api.reply_message(event.reply_token, messages)


@app.route("/", methods=["GET"])
def health_check():
    return "れんげつBot稼働中"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
