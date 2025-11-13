"""
04_system_prompting_with_ai.py
システムプロンプトでAIの振る舞いを制御

このスクリプトでは以下を学びます：
1. システムプロンプトでAIの性格や役割を設定
2. system, user, assistantロールの使い分け
3. 会話履歴と組み合わせた使い方
"""

import os
from openai import OpenAI

# OpenRouterクライアントの初期化
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)


def chat(messages, user_message):
    """システムプロンプト付きでAIとチャット"""
    # ユーザーメッセージを履歴に追加
    messages.append({"role": "user", "content": user_message})
    
    # AIにメッセージを送信
    completion = client.chat.completions.create(
        model="anthropic/claude-sonnet-4.5",
        messages=messages  # systemメッセージも含まれている
    )
    
    # AIの返答を取得
    ai_response = completion.choices[0].message.content
    
    # AIの返答も履歴に追加
    messages.append({"role": "assistant", "content": ai_response})
    
    return ai_response


if __name__ == "__main__":
    # システムプロンプトを設定（AIの役割や性格を定義）
    system_prompt = "あなたは親切なプログラミング講師です。初心者にもわかりやすく、簡潔に説明してください。"
    
    # 会話履歴を初期化（システムプロンプトを最初に追加）
    messages = [{"role": "system", "content": system_prompt}]
    
    print("システムプロンプト:")
    print(f"  → {system_prompt}\n")
    print("会話を始めましょう！（終了: quit）\n")
    
    while True:
        # ユーザー入力を取得
        question = input("あなた: ")
        
        # 終了コマンド
        if question.lower() in ["quit", "exit", "終了"]:
            break
        
        # 空の入力はスキップ
        if not question.strip():
            continue
        
        # AIとチャット
        response = chat(messages, question)
        print(f"AI: {response}\n")
