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
            model="anthropic/claude-sonnet-4.5",
            messages=self.messages
        )
        
        result = completion.choices[0].message.content
        self.messages.append({"role": "assistant", "content": result})
        
        return result


# ReActパターンのプロンプト
REACT_PROMPT = """
あなたは日本語で応答するAIエージェントです。
以下のループで動作します：Thought（思考）→ Action（行動）→ PAUSE → Observation（観察）

必ず日本語で応答してください。

ステップ：
1. Thought: 何をすべきか考える（日本語で）
2. Action: ツールを使う場合は「Action: ツール名: パラメータ」の形式で記述
3. PAUSE: ツールの実行を待つ
4. Observation: ツールの結果が返される
5. Answer: 最終的な答えを出す（日本語で）

利用可能なツール：

calculate:
例: calculate: 4 * 7 / 3
計算を実行して結果を返します（Pythonの構文）

【例】

質問: 15 × 23 は？
Thought: 掛け算の計算が必要です
Action: calculate: 15 * 23
PAUSE

（システムから返される）
Observation: 345

Thought: 計算結果が得られました
Answer: 15 × 23 = 345 です

重要：必ず日本語で考えて、日本語で答えてください。
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
    
    print(f"❓ 質問: {question}\n")
    print("=" * 60)
    
    for turn in range(1, max_turns + 1):
        print(f"\n🔄 ターン {turn}")
        print("-" * 60)
        
        result = agent(next_prompt)
        
        # 結果を見やすく表示
        print(f"🤔 AIの応答:\n{result}")
        
        # Actionがあるかチェック
        actions = action_re.findall(result)
        
        if actions:
            # アクションを実行
            action, action_input = actions[0]
            
            if action not in known_actions:
                print(f"\n❌ エラー: 不明なアクション '{action}'")
                return None
            
            print(f"\n⚙️  ツール実行: {action}")
            print(f"   入力: {action_input}")
            observation = known_actions[action](action_input)
            print(f"   結果: {observation}")
            
            next_prompt = f"Observation: {observation}"
        else:
            # Actionがない場合は終了（最終回答）
            print("\n" + "=" * 60)
            print("✅ 最終回答が得られました")
            return result
    
    print("\n⚠️ 最大ターン数に達しました")
    return None


if __name__ == "__main__":
    print("\n🤖 ReActパターン AIエージェント")
    print("=" * 60)
    print("AIが自分で考えてツールを使い、問題を解決します！")
    print("計算が必要な質問をしてみてください。")
    print("例: 「25 × 34 は？」「(15 + 7) × 3 を計算して」")
    print("=" * 60)
    
    # ユーザーから質問を受け取る
    question = input("\n質問: ")
    
    # AIエージェントで処理
    query(question)
    
    print("\n" + "=" * 60)
    print("💡 ポイント:")
    print("   1. AIが「Thought」で何をすべきか考えた")
    print("   2. 「Action」でツールを選んで使った")
    print("   3. 「Observation」で結果を確認した")
    print("   4. 「Answer」で最終的な答えを出した")
    print("\n   これがReActパターン（思考→行動→観察のループ）です！")
    print("\n💡 次のステップ:")
    print("   新しいツールを追加してエージェントを拡張してみましょう！")
    print("=" * 60)
