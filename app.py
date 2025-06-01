from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import os

app = Flask(__name__)

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
GAS_WEB_APP_URL = "https://script.google.com/macros/s/AKfycbyEXAMPLE/exec"  # ← あなたのGASデプロイURLに置き換えてください

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

def get_user_data(user_id):
    response = requests.get(GAS_WEB_APP_URL, params={"action": "get", "user_id": user_id})
    return response.json() if response.status_code == 200 else {}

def save_user_data(user_id, name, count, is_premium):
    payload = {
        "action": "save",
        "user_id": user_id,
        "name": name,
        "count": count,
        "is_premium": is_premium
    }
    requests.post(GAS_WEB_APP_URL, data=payload)

@app.route("/")
def home():
    return "ok"

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
    msg = event.message.text.strip()

    user_data = get_user_data(user_id)
    name = user_data.get("name", None)
    count = int(user_data.get("count", 0))
    is_premium = user_data.get("is_premium", "false") == "true"

    reply = ""

    if msg.startswith("名前は"):
        name = msg.replace("名前は", "").strip()
        reply = f"{name}さんって呼べばいいの？♡"
    elif msg == "プレミアム登録":
        is_premium = True
        reply = "プレミアム登録が完了しました♡"
    else:
        count += 1
        if not is_premium and count > 20:
            reply = "ごめんね、20通以上はプレミアム登録してね♡"
        else:
            reply = f"{name}さん、お話してくれてうれしいな♡" if name else "名前教えてくれたら、もっと仲良くなれるかも♡"

    save_user_data(user_id, name, count, is_premium)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))
