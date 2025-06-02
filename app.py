from flask import Flask, request, abort
import requests
import json

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    try:
        event = json.loads(body)["events"][0]
        user_id = event["source"]["userId"]
        message = event["message"]["text"]
        user_name = "れんげつ様"  # 仮の固定名
        is_premium = False  # 初期はfalse（GASで管理）

        # GASに送信
        gas_response = send_to_gas(user_id, user_name, message, is_premium)
        print("GAS Response:", gas_response)

    except Exception as e:
        print("Error:", e)
        abort(400)

    return 'OK'

def send_to_gas(user_id, user_name, message, is_premium):
    url = "https://script.google.com/macros/s/AKfycbw8ZEOnqZHVcqfinlhxu4eMAs_Pdbwsapym6RFcAhGRod0_VcZVgspUzf70BgS0xAXg/exec"  # ← 差し替え必要
    headers = {
        "Content-Type": "application/json"  # ← これが超重要
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
    app.run(port=8000)
