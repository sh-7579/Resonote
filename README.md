# 📝 Resonote

AIとの対話を通じて学習内容を記録・振り返るStreamlitアプリケーションです。  
毎日の学習をチャット形式でAIに報告すると、関連論文の自動検索・Notionへの保存まで一気に行えます。

---

## 機能

- **AIコーチとの対話** — Google Geminiが学習内容に対して質問・フィードバックを返します
- **関連論文の自動検索** — Semantic Scholar APIを用いて学習トピックに関連する論文を自動で取得・提示します
- **Notionへの自動保存** — 対話終了後、要約・キーワード・次のアクションを構造化してNotionに保存します
- **過去の学習履歴参照** — 直近14日間の記録をNotionから取得し、AIが継続的な学習をサポートします

---

## 技術スタック

| 役割 | 技術 |
|---|---|
| フロントエンド | Streamlit |
| AI | Google Gemini API (`gemini-2.5-flash`) |
| 論文検索 | Semantic Scholar API |
| データ保存 | Notion API |

---

## セットアップ

### 1. リポジトリのクローン

```bash
git clone https://github.com/sh-7579/Resonote.git
cd Resonote
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

`.env.example` をコピーして `.env` を作成し、各APIキーを入力してください。

```bash
cp .env.example .env
```

```env
GOOGLE_API_KEY=your_google_api_key
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_notion_database_id
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_api_key
```

### 4. Notionデータベースの準備

Notionに以下のプロパティを持つデータベースを作成し、インテグレーションを接続してください。

| プロパティ名 | タイプ |
|---|---|
| Title | タイトル |
| Date | 日付 |
| Keywords | マルチセレクト |
| Category | セレクト |
| Next Actions | テキスト |

### 5. 起動

```bash
streamlit run main.py
```

---

## 使い方

1. アプリを起動し、今日の学習内容をチャットに入力
2. AIのフィードバックや質問に答えながら対話を深める
3. 学習トピックに応じて関連論文が自動で提示される
4. 対話終了後、サイドバーの「Notionに保存」で記録を保存

---

## ディレクトリ構成

```
Resonote/
├── main.py              # エントリーポイント
├── config.py            # 設定・プロンプト定数
├── requirements.txt
├── managers/
│   └── chat_manager.py  # 対話フロー制御
├── models/
│   └── data_models.py   # データクラス
├── services/
│   ├── ai_service.py    # Gemini AI連携
│   ├── notion_service.py# Notion連携
│   └── paper_searcher.py# 論文検索
├── ui/
│   ├── components.py    # 共通UIコンポーネント
│   ├── sidebar_view.py  # サイドバー
│   └── completion_page.py # 保存完了ページ
└── utils/
    └── logger.py        # エラーログ
```

---

## APIキーの取得

- **Google Gemini API** — [Google AI Studio](https://aistudio.google.com/)
- **Notion API** — [Notion Integrations](https://www.notion.so/my-integrations)
- **Semantic Scholar API** — [Semantic Scholar API](https://www.semanticscholar.org/product/api) （任意・なくても動作します）
