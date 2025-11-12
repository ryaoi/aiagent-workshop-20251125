"""
02_get_response_from_ai.py
OpenAI APIを使った基本的なチャット応答の例

このスクリプトでは以下を学びます：
1. OpenAIクライアントの初期化
2. AIにメッセージを送る方法
3. AIからの返答を受け取る方法
"""

import os
from openai import OpenAI

# OpenRouterクライアントの初期化
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)


def chat(user_message):
    """AIにメッセージを送って返答を取得"""
    # AIにメッセージを送る
    completion = client.chat.completions.create(
        model="openai/gpt-4o",  # 使用するモデル
        messages=[
            {
                "role": "user",  # 誰が話すか
                "content": user_message  # メッセージの内容
            }
        ]
    )
    
    # AIからの返答を取得
    ai_response = completion.choices[0].message.content
    return ai_response


if __name__ == "__main__":
    print("AIに質問してみましょう！\n")
    
    # ユーザーから質問を受け取る
    question = input("質問: ")
    
    # AIに送信して返答を取得
    response = chat(question)
    
    # 結果を表示
    print(f"AI: {response}")
    print("\n💡 ポイント: 毎回新しい会話として処理されます。AIは前の質問を覚えていません。")

