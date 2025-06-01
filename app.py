from flask import Flask, request, abort
import json
import utils
import gpt

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import os

app = Flask(__name__)

# 環境変数（Renderに設定済み）
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_LINE_TOKEN_HERE")
LINE_CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET", "YOUR_LINE_SECRET_HERE")

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

    # キーワード変換（占いモード）
    if user_message == '金運':
        user_message = '私の金運について霊視してください。'
    elif user_message == '恋愛運':
        user_message = '私の恋愛運について霊視してください。'
    elif user_message == '仕事運':
        user_message = '私の仕事運について霊視してください。'

    # 名前登録チェック
    name_response = utils.detect_and_register_name(user_id, user_message)
    if name_response:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=name_response))
        return

    # プレミアム登録処理（2通送信＋強制GPT-4モード）
    if user_message.startswith("コード："):
        code = user_message.replace("コード：", "").strip()
        utils.register_premium(user_id, code)

        user_data = utils.get_user_data(user_id)
        name = user_data.get("name", "あなた")

        intro_msg = f"✅ プレミアム登録が完了しました{name + 'さん' if name else ''}。深層の霊視を開始します。"
        reply = gpt.get_gpt4_response(user_id, "私の運勢を霊視してください。", name)

        line_bot_api.reply_message(event.reply_token, [
            TextSendMessage(text=intro_msg),
            TextSendMessage(text=reply)
        ])
        return

    # 通常応答処理（無料 or プレミアム判定）
    user_data = utils.get_user_data(user_id)
    is_premium = utils.is_premium_user(user_id)

    if not is_premium and user_data['count'] >= 10:
        line_bot_api.reply_message(event.reply_token,
            TextSendMessage(text="🔒 無料霊視は10通までです。続きはこちら👇\nhttps://note.com/loyal_cosmos1726/m/magazine_id")
        )
        return

    if not is_premium:
        utils.increment_user_count(user_id)

    name = user_data.get("name", "あなた")
    if is_premium:
        reply = gpt.get_gpt4_response(user_id, user_message, name)
    else:
        reply = gpt.get_gpt35_response(user_message, name)

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))

@app.route("/", methods=["GET"])
def health():
    return "れんげつBot起動中"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
