import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_gpt35_response(user_message, name):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"あなたは霊視占い師『恋月れんげつ』です。語尾に『〜ですね』『〜でしょう』『〜かも』をよく使い、優しい口調で話します。名前は{name}さんです。"},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content

def get_gpt4_response(user_id, user_message, name):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": f"あなたは霊視占い師『恋月れんげつ』です。特に深層心理と霊的エネルギーに基づいたアドバイスが得意です。クライアントは{name}さんです。"},
            {"role": "user", "content": user_message}
        ]
    )
    return response.choices[0].message.content
