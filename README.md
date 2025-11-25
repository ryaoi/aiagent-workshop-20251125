# AIエージェントワークショップ

OpenAIを使ったReActパターンのAIエージェントを1時間で学ぶワークショップです。

## ワークショップの目標

このワークショップでは、AIエージェントの基礎を実践的に学びます。OpenAI APIの基本的な使い方から始めて、システムプロンプトでAIの振る舞いを制御する方法を理解し、最終的にはReActパターンを使った自律的に動作するAIエージェントを構築します。

ワークショップの終わりには、自分で考えてツールを使い分けるAIエージェントが完成します。そこから先は、自分だけのツールを追加して、さらに機能を拡張することもできるようになります。

## 前提条件

このワークショップに参加するには、Pythonの基礎知識があれば十分です。GitHubアカウントとインターネット接続も必要になります。

## セットアップ手順

### 1. GitHub Codespaces で開く

1. このリポジトリのページで「Code」ボタンをクリック
2. 「Codespaces」タブを選択
3. 「＋（Create codespace on main）」をクリック

数分でブラウザ上にVS Codeが起動します。

### 2. 環境変数の設定

ワークショップ中に講師が提供するOpenRouter APIキーを設定します：

```bash
export OPENROUTER_API_KEY="講師から提供されたキー"
```

これだけで準備完了です。

### 3. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

## ワークショップの流れ

### ステップ1: AIとAIエージェントの理解（10分）

まずは基礎知識から始めましょう。[00_introduction_ai_ai_agent.md](00_introduction_ai_ai_agent.md) でAIとAIエージェントの違いを理解し、[01_how_to_use_ai.md](01_how_to_use_ai.md) でOpenAI APIの使い方を学びます。

### ステップ2: AIとの対話を試す（15分）

理論を学んだら、実際に手を動かしてみましょう。

```bash
python 02_get_response_from_ai.py
```

基本的なOpenAI APIの使い方を学びます。質問を1つ入力すると、AIが答えてくれます。シンプルですが、これがAI APIの基本です。

```bash
python 03_conversation_history.py
```

会話履歴を継続する方法を学びます。`messages`リストに過去の会話を保存することで、AIが文脈を理解できるようになります。対話を続けて、AIが前の会話を覚えていることを確認しましょう。

```bash
python 04_system_prompting_with_ai.py
```

システムプロンプトの威力を体験します。最初に「プログラミング講師」という役割が設定されており、AIの返答がどう変わるかを確認できます。

### ステップ3: AIエージェントを構築（25分）

いよいよメインパートです。まずはシンプルなエージェントから始めて、段階的に複雑にしていきましょう。

#### 3-1: シンプルなReActエージェント（10分）

```bash
python 05_simple_agent_one_tool.py
```

ReActパターンの基本を学びます。1つのツール（シェルコマンド実行）だけを持つシンプルなエージェントです。AIが「思考」→「行動」→「観察」のループを回す様子をじっくり観察しましょう。

利用可能なツール：
- **shell_command**: シェルコマンドを実行（例：「現在のディレクトリのファイル一覧を見せて」「今日の日付は？」）⚠️

#### 3-2: 複数ツールを持つ高度なエージェント（15分）

```bash
python 06_advanced_agent_multiple_tools.py
```

複数のツールを持つエージェントに挑戦します。ここからが本番です！AIが状況に応じて適切なツールを選ぶ様子を観察してください。

利用可能なツール：
- **calculate**: 計算を実行（例：「25 × 34 は？」）
- **weather**: 天気情報を取得（例：「東京の天気は？」）
- **save_memo**: メモをCSVファイルに保存（例：「明日は会議とメモして」）
- **read_memos**: 保存したメモを読み込む（例：「今までのメモを見せて」）
- **shell_command**: シェルコマンドを実行（例：「現在のディレクトリのファイル一覧を見せて」）⚠️

⚠️ **注意**: `shell_command`は教育目的のみです。危険なコマンド（`rm`, `sudo`など）は実行しないでください。

### ステップ4: 質疑応答（10分）

ここまでの内容について、疑問に思ったことや深く知りたいことがあれば、遠慮なく質問してください。AIエージェントの実装、ReActパターンの詳細、ツールの追加方法など、何でもお答えします。

もし時間があれば、自分だけのツールを追加してAIエージェントを拡張してみるのもよいでしょう。

## 🛠️ ファイル構成

```
.
├── README.md                             # このファイル
├── 00_introduction_ai_ai_agent.md        # AIとAIエージェントの説明
├── 01_how_to_use_ai.md                   # OpenAI APIの使い方
├── 02_get_response_from_ai.py            # 基本的なAPI呼び出し
├── 03_conversation_history.py            # 会話履歴の継続
├── 04_system_prompting_with_ai.py        # システムプロンプト
├── 05_simple_agent_one_tool.py           # シンプルなReActエージェント（1ツール）
├── 06_advanced_agent_multiple_tools.py   # 高度なReActエージェント（複数ツール）
├── requirements.txt                      # 必要なパッケージ
└── .devcontainer/                        # GitHub Codespaces設定
    └── devcontainer.json
```

## ヒント

コードを実行する前に、まず内容をしっかり読んで理解することが大切です。エラーが出たら慌てずに、エラーメッセージをよく読んでみてください。多くの場合、そこに解決のヒントが書かれています。

コードは自由に編集して実験してみましょう。失敗を恐れずに、色々試すことで学びが深まります。わからないことがあれば、遠慮なく質問してください。

## 🔗 参考リンク

- [OpenAI API ドキュメント](https://platform.openai.com/docs/api-reference)
- [OpenRouter](https://openrouter.ai/)
- [ReActパターンの論文](https://arxiv.org/abs/2210.03629)
- [Simon Willison's ReAct実装](https://til.simonwillison.net/llms/python-react-pattern)
