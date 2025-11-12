"""
05_build_ai_agent_with_tools.py
ReActパターンを使ったAIエージェントの実装

このスクリプトでは以下を学びます：
1. ReAct（Reasoning + Acting）パターンの実装
2. AIにツールを与える方法
3. Thought → Action → Observation のループ
4. 自律的に問題を解決するAIエージェント

参考: https://til.simonwillison.net/llms/python-react-pattern
"""

import os
import re
from openai import OpenAI

# OpenRouterクライアントの初期化
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)


class Agent:
    """ReActパターンで動作するAIエージェント"""
    
    def __init__(self, system_prompt):
        self.system_prompt = system_prompt
        self.messages = [{"role": "system", "content": system_prompt}]
    
    def __call__(self, message):
        """メッセージを送信して返答を取得"""
        self.messages.append({"role": "user", "content": message})
        
        completion = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=self.messages
        )
        
        result = completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": result})
        
        return result


# ReActパターンのプロンプト
REACT_PROMPT = """
あなたは以下のループで動作します：
Thought（思考）、Action（行動）、PAUSE、Observation（観察）

ループの最後にAnswer（回答）を出力します。

Thought: 質問について考えたことを記述
Action: 利用可能なアクションを実行し、PAUSEを返す
Observation: アクションの実行結果

利用可能なアクション：

calculate:
例: calculate: 4 * 7 / 3
計算を実行して結果を返します（Pythonの構文を使用）

【例】

質問: 15 × 23 は？
Thought: 計算が必要です
Action: calculate: 15 * 23
PAUSE

その後、以下が返されます：

Observation: 345

そして出力：

Answer: 15 × 23 = 345 です
""".strip()


# アクションを抽出する正規表現
action_re = re.compile(r'^Action: (\w+): (.*)$', re.MULTILINE)


def calculate(expression):
    """計算ツール"""
    try:
        return eval(expression)
    except Exception as e:
        return f"計算エラー: {e}"


# 利用可能なツール
known_actions = {
    "calculate": calculate,
}


def query(question, max_turns=5):
    """ReActパターンでクエリを実行"""
    agent = Agent(REACT_PROMPT)
    next_prompt = question
    
    print(f"質問: {question}\n")
    
    for i in range(max_turns):
        result = agent(next_prompt)
        print(result)
        
        # Actionがあるかチェック
        actions = action_re.findall(result)
        
        if actions:
            # アクションを実行
            action, action_input = actions[0]
            
            if action not in known_actions:
                print(f"エラー: 不明なアクション {action}")
                return None
            
            print(f"\n🔧 実行: {action}({action_input})")
            observation = known_actions[action](action_input)
            print(f"📊 結果: {observation}\n")
            
            next_prompt = f"Observation: {observation}"
        else:
            # Actionがない場合は終了
            return result
    
    return None


if __name__ == "__main__":
    print("\n🤖 ReActパターン AIエージェント")
    print("=" * 60)
    print("AIが自分で考えてツールを使い、問題を解決します！\n")
    
    # ユーザーから質問を受け取る
    question = input("質問: ")
    
    # AIエージェントで処理
    query(question)
    
    print("\n" + "=" * 60)
    print("✅ 完了！")
    print("\n💡 ポイント: AIは質問を理解し、必要なツール（calculate）を")
    print("   自分で選んで使いました。これがReActパターンです。")
    print("\n💡 次のステップ: 新しいツールを追加してみましょう！")
    print("   例: weather（天気）、translate（翻訳）など")
    print("=" * 60)
