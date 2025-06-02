from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import TextSendMessage
import requests
import json
import os

# === 環境変数（Render側で設定する） ===
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "ここにチャネルアクセストークンを直書きしてもOK")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "ここにシークレットを直書きしてもOK")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    try:
        event = json.loads(body)["events"][0]
        user_id = event["source"]["userId"]
        message = event["message"]["text"]
        reply_token = event["replyToken"]
        user_name = "れんげつ様"
        is_premium = False

        # GASに送信して応答をもらう
        gas_response = send_to_gas(user_id, user_name, message, is_premium)
        print("GAS Response:", gas_response)

        # LINEに返信
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=gas_response)
        )

    except Exception as e:
        print("Error:", e)
        abort(400)

    return 'OK'

def send_to_gas(user_id, user_name, message, is_premium):
    url = "https://script.google.com/macros/s/AKfycbxHRdbQRJxfLD4NVzsfO9fOjeg68ujCfVczU9zTo-zfq2FXclDA_yMgR1tRLZTPXFHt/exec"
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
