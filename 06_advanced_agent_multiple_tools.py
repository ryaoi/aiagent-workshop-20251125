"""
06_advanced_agent_multiple_tools.py
複数のツールを使える高度なReActエージェント

このスクリプトでは以下を学びます：
1. 複数のツールを持つAIエージェント
2. AIが状況に応じて適切なツールを選択
3. API呼び出し、CSV操作、コマンド実行など
4. より実用的なAIエージェントの構築

⚠️ 注意: shell_commandツールは危険なコマンドを実行しないでください
"""

import os
import re
import csv
import subprocess
from datetime import datetime
import httpx
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

weather:
例: weather: Tokyo
指定された都市の現在の天気を返します

save_memo:
例: save_memo: 明日は会議がある
メモをCSVファイルに保存します（日時付き）

read_memos:
例: read_memos: 
保存されている全てのメモを読み込みます

shell_command:
例: shell_command: ls -la
シェルコマンドを実行します
⚠️ 警告: 危険なコマンド（rm, sudo等）は実行しないでください

【例1: 計算】

質問: 15 × 23 は？
Thought: 掛け算の計算が必要です
Action: calculate: 15 * 23
PAUSE

（システムから返される）
Observation: 345

Thought: 計算結果が得られました
Answer: 15 × 23 = 345 です

【例2: 天気】

質問: 東京の天気は？
Thought: 天気情報を取得する必要があります
Action: weather: Tokyo
PAUSE

（システムから返される）
Observation: 東京の天気: Partly cloudy +15°C

Thought: 天気情報が得られました
Answer: 東京は部分的に曇りで、気温は15度です

【例3: メモの保存】

質問: 明日は13時に会議があることをメモして
Thought: メモを保存する必要があります
Action: save_memo: 明日は13時に会議
PAUSE

（システムから返される）
Observation: メモを保存しました

Thought: メモの保存が完了しました
Answer: メモを保存しました。「明日は13時に会議」と記録しました

【例4: コマンド実行】

質問: 現在のディレクトリにあるファイルを見せて
Thought: ファイル一覧を取得するにはlsコマンドが必要です
Action: shell_command: ls -la
PAUSE

（システムから返される）
Observation: total 48
drwxr-xr-x  8 user  staff   256 Nov 12 10:30 .
drwxr-xr-x  5 user  staff   160 Nov 12 09:00 ..
-rw-r--r--  1 user  staff  1234 Nov 12 10:30 memos.csv

Thought: ファイル一覧が得られました
Answer: 現在のディレクトリには以下のファイルがあります：
- memos.csv（1234バイト）

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


def weather(city):
    """天気情報取得ツール（wttr.in APIを使用）"""
    try:
        # wttr.in APIを使用（無料、認証不要）
        response = httpx.get(
            f"https://wttr.in/{city}?format=%C+%t",
            timeout=5.0,
            follow_redirects=True
        )
        
        if response.status_code == 200:
            return f"{city}の天気: {response.text.strip()}"
        else:
            return f"天気情報を取得できませんでした（ステータス: {response.status_code}）"
    except Exception as e:
        return f"天気情報取得エラー: {e}"


def save_memo(memo):
    """メモをCSVファイルに保存"""
    try:
        filename = "memos.csv"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # ファイルが存在しない場合はヘッダーを書き込む
        file_exists = os.path.exists(filename)
        
        with open(filename, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["日時", "メモ"])
            writer.writerow([timestamp, memo])
        
        return f"メモを保存しました: {memo}"
    except Exception as e:
        return f"メモ保存エラー: {e}"


def read_memos(dummy=""):
    """保存されている全てのメモを読み込む"""
    try:
        filename = "memos.csv"
        
        if not os.path.exists(filename):
            return "まだメモは保存されていません"
        
        with open(filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # ヘッダーをスキップ
            memos = list(reader)
        
        if not memos:
            return "まだメモは保存されていません"
        
        # 最新5件のメモを返す
        recent_memos = memos[-5:]
        result = f"保存されているメモ（最新{len(recent_memos)}件）:\n"
        for timestamp, memo in recent_memos:
            result += f"- [{timestamp}] {memo}\n"
        
        return result.strip()
    except Exception as e:
        return f"メモ読み込みエラー: {e}"


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
    "calculate": calculate,
    "weather": weather,
    "save_memo": save_memo,
    "read_memos": read_memos,
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
    print("\n🤖 高度なReActエージェント（複数ツール対応）")
    print("=" * 60)
    print("AIが状況に応じて適切なツールを選んで問題を解決します！")
    print("\n利用可能なツール:")
    print("  📊 calculate     - 計算を実行")
    print("  🌤️  weather      - 天気情報を取得")
    print("  📝 save_memo     - メモをCSVファイルに保存")
    print("  📖 read_memos    - 保存したメモを読み込む")
    print("  💻 shell_command - シェルコマンドを実行（⚠️ 危険なコマンドは禁止）")
    print("\n試してみよう:")
    print("  計算: 「25 × 34 は？」")
    print("  天気: 「東京の天気は？」")
    print("  メモ: 「明日は会議があるとメモして」「今までのメモを見せて」")
    print("  コマンド: 「現在のディレクトリのファイル一覧を見せて」")
    print("=" * 60)
    
    # ユーザーから質問を受け取る
    question = input("\n質問: ")
    
    # AIエージェントで処理
    query(question)
    
    print("\n" + "=" * 60)
    print("💡 ポイント:")
    print("   1. AIが「Thought」で何をすべきか考えた")
    print("   2. 複数のツールから適切なものを選んだ")
    print("   3. 「Action」でツールを使った")
    print("   4. 「Observation」で結果を確認した")
    print("   5. 「Answer」で最終的な答えを出した")
    print("\n   これがReActパターン（思考→行動→観察のループ）です！")
    print("\n💡 05との違い:")
    print("   05: 1つのツール（shell_command）のみ → ReActの基本を理解")
    print("   06: 複数のツール → AIが状況に応じて選択できる！")
    print("\n💡 次のステップ:")
    print("   新しいツールを追加してエージェントをさらに拡張してみましょう！")
    print("=" * 60)
