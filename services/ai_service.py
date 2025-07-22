import google.generativeai as genai
import json
import re
from typing import List, Dict, Any

from utils.logger import log_error
from services.paper_searcher import PaperSearcher 
from models.data_models import SummaryData
import config
import streamlit as st

class AIService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.paper_searcher = PaperSearcher()

    def start_chat_session(self, past_records_text: str, paper_info: str) -> Any:
        """AIとのチャットセッションを開始"""
        prompt = config.CHAT_SYSTEM_PROMPT.format(
            past_records=past_records_text,
            paper_info=paper_info
        )
        return self.model.start_chat(history=[
            {'role': 'user', 'parts': [prompt]},
            {'role': 'model', 'parts': ["こんにちは！今日の学習について教えてください。"]}
        ])
    
    def needs_paper_search(self, user_prompt: str) -> bool:
        """
        AIに、ユーザーのプロンプトが論文検索を必要とする内容か判断させる。
        """
        try:
            # configからプロンプトを読み込んで使用する
            prompt = config.TRIGGER_CLASSIFIER_PROMPT.format(user_prompt=user_prompt)
            
            # 非常に短い、決定的な応答を期待する設定
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,  # 判定を安定させるため、創造性を0に
                    max_output_tokens=5 # 「Yes」か「No」だけなので、出力は最小限に
                )
            )
            
            # AIの応答を小文字にして「yes」が含まれているかチェック
            decision = response.text.strip().lower()
            return "yes" in decision

        except Exception as e:
            log_error(f"AIによる論文検索要否判断中にエラー: {e}")
            # エラーが発生した場合は、安全策として検索しない
            return False
    
    def search_papers(self, user_prompt: str, limit: int = 3) -> str:
        """
        PaperSearcherの機能を順番に呼び出して、整形された論文情報を返す
        """
        try:
            # ステップ1: ユーザーの入力から最適な検索クエリを生成
            with st.spinner("検索キーワードを抽出中..."):
                search_query = self.paper_searcher.extract_search_query(user_prompt)
            
            if not search_query:
                return "適切な検索キーワードが見つかりませんでした。"

            # ステップ2: 生成したクエリで論文を検索
            with st.spinner(f"「{search_query}」で論文を検索中..."):
                papers = self.paper_searcher.search_papers(search_query, limit=limit)
            
            # ステップ3: 検索結果をAI用に整形
            formatted_text = self.paper_searcher.format_papers_for_ai(papers)
            
            return formatted_text
            
        except Exception as e:
            log_error(e)
            return f"論文検索中にエラーが発生しました: {e}"

    def summarize_conversation(self, chat_history: List[Dict[str, str]]) -> SummaryData:
        """対話履歴を要約し、SummaryDataオブジェクトを返す"""
        try:
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
            prompt = config.SUMMARIZATION_PROMPT.format(chat_history=history_text)
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.1)
            )
            
            json_text = re.sub(r'```json\s*|\s*```', '', response.text.strip())
            data = json.loads(json_text)
            
            if not all(k in data for k in ['title', 'summary']):
                 raise ValueError("要約データに必要なキーが不足しています。")

            return SummaryData(**data)

        except (json.JSONDecodeError, ValueError, Exception) as e:
            log_error(e)
            user_messages = [msg['content'] for msg in chat_history if msg['role'] == 'user']
            fallback_summary = user_messages[0][:150] if user_messages else "今日の学習記録"
            return SummaryData(summary=f"要約生成に失敗しました。最初の発言: {fallback_summary}...")
        
    def generate_final_comment(self, chat_history: List[Dict[str, str]], paper_info: str) -> str:
        """対話終了用の特別なまとめコメントを生成する"""
        try:
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
            
            prompt = config.END_OF_CONVERSATION_PROMPT.format(
                chat_history=history_text,
                paper_info=paper_info
            )
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(temperature=0.7)
            )
            return response.text

        except Exception as e:
            log_error(f"終了コメント生成中にエラー: {e}")
            return "本日の対話は以上となります。お疲れ様でした！サイドバーから記録をNotionに保存してください。"
