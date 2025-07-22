import os
import streamlit as st

# --- APIキーと環境変数の設定 ---
# Streamlit Secretsまたは環境変数からキーを安全に読み込む
def get_env_variable(key: str) -> str:
    value = os.getenv(key, st.secrets.get(key))
    if not value or len(value.strip()) < 10:
        st.error(f"エラー: {key} が設定されていません。環境変数またはStreamlit Secretsに設定してください。")
        st.stop()
    return value

NOTION_API_KEY = get_env_variable('NOTION_API_KEY')
NOTION_DATABASE_ID = get_env_variable('NOTION_DATABASE_ID')
GOOGLE_API_KEY = get_env_variable('GOOGLE_API_KEY')

SEMANTIC_SCHOLAR_BASE_URL = "https://api.semanticscholar.org/graph/v1"
MIN_REQUEST_INTERVAL = 1.0  # 最小リクエスト間隔（秒）
CACHE_EXPIRY_HOURS = 24  # キャッシュの有効期限（時間）

# --- 機能の有効化/無効化スイッチ ---
ENABLE_PAPER_SEARCH = False  # Trueにすると有効、Falseにすると無効

# --- 定数設定 ---
API_TIMEOUT = 30  # APIリクエストのタイムアウト（秒）

# --- 対話管理設定 ---
MAX_EXCHANGES = 5  # 最大対話回数
WARNING_THRESHOLD = int(MAX_EXCHANGES * 0.8)  # 警告を開始する閾値
SATISFACTION_KEYWORDS = [
    "以上です", "終わりましょう", "結構です", "ありがとう", "おつかれ", 
    "終了して", "もういい", "やめて", "thank", "finish", "end", "stop", "done"
]
PAPER_TRIGGER_KEYWORDS = [
    "論文", "paper", "研究論文", "学術論文", "文献", "参考文献",
    "先行研究", "関連研究", "最新研究", "研究動向", "technique", 
    "method", "approach", "survey"
]

# --- プロンプト設定 ---
CHAT_SYSTEM_PROMPT = """
あなたは、ユーザーの学習記録をサポートする、洞察力に優れたAIコーチです。
ユーザーから今日の活動報告を受けたら、以下の点を意識して対話を進めてください。

## 基本的な対話の流れ:
1. 報告内容に対して建設的で具体的なコメントを返す
2. 「過去の学習履歴」を参考に、学習の継続性や成長点を指摘
3. ユーザーの学習を深めるために、具体的で思考を促す質問を<strong>必ず1つだけ</strong>投げかける。<strong>応答の最後は、必ずこの質問で締めくくること。</strong>
4. <strong> 【最重要】複数の質問は絶対にしないでください。</strong>
5. 会話は簡潔で実用的に、ユーザーが返信しやすいように心がける
## 過去の学習履歴（参考）:
{past_records}

## 関連論文情報:
{paper_info}
"""

END_OF_CONVERSATION_PROMPT = """
対話履歴全体と、提示された論文情報を分析し、以下の指示に従って最後のまとめのメッセージを生成してください。

### 対話履歴:
{chat_history}

### 関連論文情報:
{paper_info}

### 指示:
1. **追加の質問は一切しないでください。**
2. 今日の学習内容（対話履歴）を2-3文で簡潔に、肯定的に要約してください。
3. もし「関連論文情報」に具体的な内容があり、「まだ検索されていません」という文字列が含まれていない場合、各論文のタイトルと著者名を挙げ、その重要性を一言で説明してください。
4. 今日の学習の成果やプロセスを具体的に評価し、励ましの言葉でユーザーを勇気づけてください。
5. 「本日もお疲れ様でした。」といった自然な挨拶で締めくくってください。
6. 最後に、サイドバーから「Notionに保存」ボタンを押すよう、明確に案内してください。
"""

SUMMARIZATION_PROMPT = """
以下の対話履歴を分析し、Notionデータベースに保存するための構造化データを生成してください。

## 指示
- 対話から最も重要な学習内容を抽出し、各項目を埋めてください
- `title`は学習内容の核心を表現する簡潔で分かりやすいタイトル（例：「Transformer実装でAttention機構を理解」）
- `keywords`は学習内容の主要な技術・概念を**3つ以内**で抽出
- `summary`は対話全体を150字程度で要約（学習内容、気づき、課題を含む）
- `action_items`は次に取り組むべき具体的なアクションを2-3個抽出
- `learning_category`は学習分野を1つ選択（例：プログラミング、統計、研究など）
- **必ず指示されたJSON形式で、JSONデータのみを出力してください**

## 出力形式（JSON）
{{
    "title": "学習記録タイトル",
    "keywords": ["キーワード1", "キーワード2", "キーワード3"],
    "summary": "今日の学習内容、気づき、課題の要約",
    "action_items": ["次にやること1", "次にやること2"],
    "learning_category": "学習分野"
}}

## 対話履歴:
{chat_history}
"""

TRIGGER_CLASSIFIER_PROMPT = """あなたは、ユーザーのリクエストが学術的な論文検索を必要とするかどうかを判断する分類器です。
ユーザーが特定の技術、研究トピック、アルゴリズム、または複雑な学術分野について言及している場合は「Yes」と答えてください。
一般的な会話、感情、または単純な質問の場合は「No」と答えてください。

回答は必ず「Yes」か「No」のどちらか一言だけにしてください。

ユーザーのリクエスト: 「{user_prompt}」
"""

PAPER_COMMENT_PROMPT = """以下のユーザーの学習内容と、提示された論文リストを考慮してください。

### ユーザーの学習内容:
「{user_prompt}」

### 関連論文リスト:
{paper_info}

### 指示:
上記の論文の中から、ユーザーの学習内容に最も関連が深いと思われるものを1つか2つ選び、なぜそれが役立つのかをあなたの言葉で説明してください。
<strong> 論文の具体的な内容（手法や結果など）に関する質問はしないでください。</strong>
代わりに、<strong>「この中で特に気になる論文はありましたか？」や「この方向性で学習を進めてみるのはいかがですか？」のように、ユーザーの興味や次のアクションを尋ねる質問を1つだけ投げかけて、会話を自然に続けてください。</strong>
"""