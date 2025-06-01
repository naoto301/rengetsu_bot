from flask import Flask, request, abort
import json
import utils
import gpt

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

import os

app = Flask(__name__)

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

    # キーワード変換
    keyword_map = {
        "金運": "私の金運について霊視してください。",
        "恋愛運": "私の恋愛運について霊視してください。",
        "仕事運": "私の仕事運について霊視してください。"
    }
    if user_message in keyword_map:
        user_message = keyword_map[user_message]

    # 名前登録チェック
    name_response = utils.detect_and_register_name(user_id, user_message)
    if name_response:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=name_response))
        return

    # プレミアム登録時
    if user_message.startswith("コード："):
        code = user_message.replace("コード：", "").strip()
        utils.register_premium(user_id, code)

        # 再取得（プレミアム登録直後なのでここで正確なデータを取る）
        user_data = utils.get_user_data(user_id)
        name = user_data.get("name")
        name_text = f"{name}さん" if name else ""

        intro_msg = f"✅ プレミアム登録が完了しました。{name_text} 深層の霊視を開始します。"
        reply = gpt.get_gpt4_response(user_id, "プレミアム登録", name)

        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text=intro_msg),
                TextSendMessage(text=reply)
            ]
        )
        return

    # 無料ユーザーの上限チェック
    user_data = utils.get_user_data(user_id)
    is_premium = utils.is_premium_user(user_id)
    if not is_premium and user_data["count"] >= 10:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="🔒 無料霊視は10通までです。続きはこちら👇\nhttps://note.com/loyal_cosmos1726/m/magazine_id")
        )
        return

    # カウント加算（無料のみ）
    if not is_premium:
        utils.increment_user_count(user_id)

    # 名前再取得
    name = user_data.get("name")

    # GPT応答
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
