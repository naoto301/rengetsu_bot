from flask import Flask, request, abort
import requests
import json
import os
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 環境変数から取得
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/", methods=['GET'])
def index():
    return "れんげつBot is running.", 200

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Error in handler:", e)
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    message_text = event.message.text
    user_name = "れんげつ様"  # 初期名
    is_premium = False       # 初期はFalse、GAS側で管理

    # GASへ送信
    gas_response = send_to_gas(user_id, user_name, message_text, is_premium)
    
    # LINEに返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=gas_response)
    )

def send_to_gas(user_id, user_name, message, is_premium):
    url = "https://script.google.com/macros/s/AKfycbya-0mNXSOhv22TfZlpuP0yuhwmo55QRqUcmF7iVtH5rI9zwL9t2UaIlbkHFtHR6aFs/exec"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "userId": user_id,
        "name": user_name,
        "message": message,
        "premium": is_premium
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return response.text

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
