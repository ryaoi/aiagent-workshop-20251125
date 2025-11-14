# OpenAI APIの使い方

## OpenAI APIとは？

OpenAI APIは、GPT-4などの強力なAIモデルをプログラムから使えるサービスです。自分のプログラムに、AIを組み込むことができます。

## OpenRouterを使います

このワークショップでは**OpenRouter**というサービスを使います。OpenRouterは、OpenAI、Anthropic、Googleなど、複数のAIモデルに統一されたAPIでアクセスできるサービスです。OpenAI APIと互換性があるため、コードの書き方はほぼ同じです。

違いは接続先のURLだけです：

```python
# OpenAI 直接
client = OpenAI(api_key="sk-...")

# OpenRouter（今回使用）
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="sk-..."
)
```

`base_url`を指定するだけで、OpenRouterを通してAIにアクセスできます。

## 基本的なAPIの構造

APIを使うには、大きく3つのステップがあります。

まず、クライアントを初期化します：

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="your-api-key"
)
```

次に、AIにメッセージを送ります：

```python
completion = client.chat.completions.create(
    model="anthropic/claude-sonnet-4.5",  # 使用するモデル
    messages=[                              # メッセージのリスト
        {
            "role": "user",                 # 誰が話すか
            "content": "こんにちは"         # メッセージの内容
        }
    ]
)
```

そして、AIからの返答を取得します：

```python
response = completion.choices[0].message.content
print(response)  # AIの返答が出力される
```

これだけで、AIとの会話ができます。

## ロール（Role）の種類

メッセージには「役割」を示す`role`というフィールドがあります。これは、そのメッセージが誰から発せられたものかを示すもので、3種類あります。

**`system`（システム）**は、AIの振る舞いや性格を設定するためのロールです：

```python
{
    "role": "system",
    "content": "あなたは親切なプログラミング講師です。"
}
```

**`user`（ユーザー）**は、ユーザーからの質問やメッセージを表します：

```python
{
    "role": "user",
    "content": "Pythonのfor文について教えて"
}
```

**`assistant`（アシスタント）**は、AIの過去の返答を表します。これは会話履歴を保持するために使います：

```python
{
    "role": "assistant",
    "content": "for文は繰り返し処理を行うための構文です。"
}
```

## 会話履歴の管理

ここで重要なポイントがあります。AIは自動的に会話を覚えているわけではありません。メッセージを送るたびに、過去の会話も一緒に含める必要があるのです。

例えば、こんな風に：

```python
messages = [
    {"role": "system", "content": "あなたは数学の先生です。"},
    {"role": "user", "content": "2 + 2 は？"},
    {"role": "assistant", "content": "4です。"},
    {"role": "user", "content": "それに5を足すと？"}  # 前の会話を含めている
]

completion = client.chat.completions.create(
    model="anthropic/claude-sonnet-4.5",
    messages=messages
)
```

このように、過去のユーザーメッセージとAIの返答を全て含めることで、AIは文脈を理解できるようになります。

## 返答の構造

APIからの返答には様々な情報が含まれていますが、実際に使うのは主に次の部分です：

```python
response = completion.choices[0].message.content
```

返答データ全体はこのような構造になっています：

```python
{
    "id": "chatcmpl-...",
    "object": "chat.completion",
    "created": 1234567890,
    "model": "anthropic/claude-sonnet-4.5",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "こんにちは！どのようなお手伝いができますか？"
            },
            "finish_reason": "stop"
        }
    ],
    "usage": {
        "prompt_tokens": 10,
        "completion_tokens": 20,
        "total_tokens": 30
    }
}
```

ほとんどの場合、`choices[0].message.content`だけを取り出せば十分です。

より詳しいAPIのレスポンスデータ構造については、OpenAIの公式ドキュメントを参照してください：

https://platform.openai.com/docs/api-reference/chat/create

**今後のAPI利用について：Responses APIへの移行**

このワークショップでは従来の**Chat Completions API**（`client.chat.completions.create()`）を使用していますが、OpenAIは新しい**Responses API**（`client.responses.create()`）への移行を推奨しています。

Responses APIの主な利点：
- **より簡潔な構文**: `messages`の代わりに`input`で直接文字列を渡せる
- **エージェント機能がビルトイン**: web検索、ファイル検索、コード実行などが標準搭載
- **パフォーマンス向上**: 推論モデル使用時に約3%の精度向上
- **コスト削減**: キャッシュ最適化により40-80%のコスト削減
- **ステートフル対応**: ターン間で文脈を自動保持

```python
# 従来のChat Completions API（このワークショップで使用）
completion = client.chat.completions.create(
    model="gpt-5",
    messages=[
        {"role": "user", "content": "こんにちは"}
    ]
)
print(completion.choices[0].message.content)

# 新しいResponses API（今後推奨）
response = client.responses.create(
    model="gpt-5",
    input="こんにちは"
)
print(response.output_text)
```

Chat Completions APIは引き続きサポートされますが、新規プロジェクトではResponses APIの使用が推奨されています。

詳しくは以下の移行ガイドを参照してください：

https://platform.openai.com/docs/guides/migrate-to-responses?update-item-definitions=responses&update-multiturn=responses

## システムプロンプトの例

システムプロンプトを工夫することで、AIの振る舞いを様々に変えられます。いくつか例を見てみましょう。

プログラミング講師として振る舞わせたい場合：

```python
{
    "role": "system",
    "content": "あなたは親切なプログラミング講師です。初心者にもわかりやすく説明してください。"
}
```

関西弁で話すAIを作りたい場合：

```python
{
    "role": "system",
    "content": "あなたは関西弁で話すAIです。親しみやすく、明るい口調で話してください。"
}
```

JSON形式で回答を返してほしい場合：

```python
{
    "role": "system",
    "content": "回答は必ずJSON形式で返してください。"
}
```

システムプロンプト次第で、AIの性格や出力形式を自由にコントロールできます。

## 環境変数の使い方

セキュリティ上、APIキーは直接コードに書かないのが基本です。環境変数で管理しましょう。

ターミナルで環境変数をセットします：

```bash
export OPENROUTER_API_KEY="your-api-key"
```

これで、Pythonから環境変数を読み込めるようになります：

```python
import os

api_key = os.environ.get("OPENROUTER_API_KEY")
```

このワークショップでは、講師が提供するAPIキーを使います。以下のコマンドを実行してください：

```bash
export OPENROUTER_API_KEY="講師から提供されたキー"
```

## 使用料金について

OpenRouterやOpenAIは、使用量に応じて課金されます。料金は**トークン数**（おおよそ単語数に相当）と**モデルの性能**で決まります。高性能なモデルほど料金も高くなります。

今回のワークショップでは講師が用意したAPIキーを使うので、料金を気にする必要はありません。

## 注意すべきこと

いくつか覚えておくべき重要なポイントがあります。

**APIキーは秘密情報です。** GitHubにpushしたり、人に見せたりしないようにしましょう。

**送れる会話の量には制限があります。** モデルによって、一度に処理できる会話の長さが決まっています。この長さは「トークン」という単位で測られます（おおよそ単語や文字の数）。例えば、Claude Sonnet 4.5は約1,000,000トークンまで処理できます。この制限を超えるとエラーになります。また、制限内でも会話が長くなりすぎると、古い情報が薄れて文脈がうまく伝わらない可能性があります。

---

では、実際にコードを書いて試してみましょう！

次は [02_get_response_from_ai.py](02_get_response_from_ai.py) を実行して、基本的なAPI呼び出しを体験してください。

