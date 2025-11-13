"""
03_conversation_history.py
会話履歴を継続する方法

このスクリプトでは以下を学びます：
1. messagesリストで会話履歴を管理する方法
2. 過去の会話を含めてAIに送る方法
3. AIが文脈を理解して答える仕組み
"""

import os
from openai import OpenAI

# OpenRouterクライアントの初期化
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)


def chat(messages, user_message):
    """会話履歴を保持しながらAIとチャット"""
    # ユーザーメッセージを履歴に追加
    messages.append({"role": "user", "content": user_message})
    
    # AIにメッセージを送信（会話履歴全体を含める）
    completion = client.chat.completions.create(
        model="anthropic/claude-sonnet-4.5",
        messages=messages  # 過去の会話も全て送る
    )
    
    # AIの返答を取得
    ai_response = completion.choices[0].message.content
    
    # AIの返答も履歴に追加
    messages.append({"role": "assistant", "content": ai_response})
    
    return ai_response


if __name__ == "__main__":
    print("AIと会話してみましょう！（終了: quit）\n")
    
    # 会話履歴を保存するリスト
    messages = []
    
    while True:
        # ユーザー入力を取得
        question = input("あなた: ")
        
        # 終了コマンド
        if question.lower() in ["quit", "exit", "終了"]:
            break
        
        # 空の入力はスキップ
        if not question.strip():
            continue
        
        # AIとチャット（会話履歴を渡す）
        response = chat(messages, question)
        print(f"AI: {response}\n")
