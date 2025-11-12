"""
05_simple_agent_one_tool.py
シンプルなReActエージェント（1つのツールのみ）

このスクリプトでは以下を学びます：
1. ReAct（Reasoning + Acting）パターンの基本
2. AIが自分で考えてツールを使う仕組み
3. Thought → Action → Observation のループ

まずは1つのツールで仕組みを理解しましょう！

⚠️ 注意: shell_commandツールは危険なコマンドを実行しないでください
"""

import os
import re
import subprocess
from openai import OpenAI

# OpenRouterクライアントの初期化
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
)


class Agent:
    """ReActパターンで動作するシンプルなAIエージェント"""
    
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

shell_command:
例: shell_command: ls -la
シェルコマンドを実行して結果を返します
⚠️ 警告: 危険なコマンド（rm, sudo等）は実行しないでください

【例】

質問: 現在のディレクトリにあるファイルを見せて
Thought: ファイル一覧を取得するにはlsコマンドが必要です
Action: shell_command: ls -la
PAUSE

（システムから返される）
Observation: total 48
drwxr-xr-x  8 user  staff   256 Nov 12 10:30 .
drwxr-xr-x  5 user  staff   160 Nov 12 09:00 ..
-rw-r--r--  1 user  staff  1234 Nov 12 10:30 README.md

Thought: ファイル一覧が得られました
Answer: 現在のディレクトリには以下のファイルがあります：
- README.md（1234バイト）

重要：必ず日本語で考えて、日本語で答えてください。
""".strip()


# アクションを抽出する正規表現
action_re = re.compile(r'^Action: (\w+): (.*)$', re.MULTILINE)


def shell_command(command):
    """
    シェルコマンドを実行（危険なコマンドに注意！）
    
    ⚠️ セキュリティ警告:
    - rm, sudo, dd などの危険なコマンドは実行しないでください
    - 本番環境では絶対に使用しないでください
    - 教育目的のみの使用に限定してください
    """
    # 危険なコマンドのブラックリスト
    dangerous_commands = ['rm', 'sudo', 'dd', 'mkfs', 'format', ':(){', 'wget', 'curl -O']
    
    # 危険なコマンドチェック
    for dangerous in dangerous_commands:
        if dangerous in command.lower():
            return f"⚠️ 危険なコマンド '{dangerous}' が検出されました。実行を拒否します。"
    
    try:
        # コマンドを実行（タイムアウト5秒）
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        output = result.stdout.strip()
        if result.stderr:
            output += f"\nエラー: {result.stderr.strip()}"
        
        return output if output else "コマンドは正常に実行されました（出力なし）"
    except subprocess.TimeoutExpired:
        return "コマンドがタイムアウトしました（5秒制限）"
    except Exception as e:
        return f"コマンド実行エラー: {e}"


# 利用可能なツール
known_actions = {
    "shell_command": shell_command,
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
    print("\n🤖 シンプルなReActエージェント（1ツール）")
    print("=" * 60)
    print("AIが自分で考えてシェルコマンドを使います！")
    print("\n利用可能なツール:")
    print("  💻 shell_command - シェルコマンドを実行（⚠️ 危険なコマンドは禁止）")
    print("\n試してみよう:")
    print("  「現在のディレクトリのファイル一覧を見せて」")
    print("  「今日の日付は？」")
    print("  「現在のPythonバージョンは？」")
    print("\n⚠️ 注意: rm, sudo などの危険なコマンドは実行しないでください")
    print("=" * 60)
    
    # ユーザーから質問を受け取る
    question = input("\n質問: ")
    
    # AIエージェントで処理
    query(question)
    
    print("\n" + "=" * 60)
    print("💡 ポイント:")
    print("   1. AIが「Thought」で何をすべきか考えた")
    print("   2. 「Action」でシェルコマンドを使った")
    print("   3. 「Observation」で結果を確認した")
    print("   4. 「Answer」で最終的な答えを出した")
    print("\n   これがReActパターンの基本です！")
    print("\n💡 次のステップ:")
    print("   06_advanced_agent_multiple_tools.py で複数のツールを使えるエージェントを試しましょう！")
    print("   AIが状況に応じて適切なツールを選ぶ様子を観察できます！")
    print("=" * 60)

