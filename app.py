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

        return gas_response
    
    except Exception as e:
        print("Error:", e)
        abort(400)

    return 'OK'

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
    import os
    port = int(os.environ.get("PORT", 10000))  # Renderが渡す環境変数PORTに対応
    app.run(host="0.0.0.0", port=port)
