import openai
import os

# OpenAIのAPIキー（安全な運用なら .env に分けて管理すべき）
openai.api_key = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")

def get_gpt35_response(message, name="あなた"):
    prompt = f"{name}さんからのご相談です：{message}\n霊視結果："
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
    )
    return response.choices[0].message['content'].strip()

def get_gpt4_response(user_id, message, name="あなた"):
    # プレミアム用（履歴ありにするならここで対応）
    prompt = f"{name}さんからの深層霊視依頼です：{message}\n霊視結果："
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.85,
    )
    return response.choices[0].message['content'].strip()
