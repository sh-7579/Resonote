from notion_client import Client
from datetime import datetime, timedelta
from typing import List, Dict, Any
import streamlit as st # Streamlitのエラー表示用

from utils.logger import log_error
from models.data_models import SummaryData, PastRecord

class NotionService:
    def __init__(self, api_key: str, database_id: str):
        self.client = Client(auth=api_key)
        self.database_id = database_id

    def get_past_records(self, days: int = 14) -> List[PastRecord]:
        """Notionから過去の記録を取得し、PastRecordオブジェクトのリストを返す"""
        try:
            past_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            response = self.client.databases.query(
                database_id=self.database_id,
                filter={"property": "Date", "date": {"on_or_after": past_date}},
                sorts=[{"property": "Date", "direction": "descending"}]
            )
            
            records = []
            for page in response.get('results', []):
                properties = page.get('properties', {})
                title_prop = properties.get('Title', {}).get('title', [])
                title = title_prop[0]['text']['content'] if title_prop else "無題"
                date_prop = properties.get('Date', {}).get('date', {})
                date_val = date_prop.get('start', '日付不明')
                category_prop = properties.get('Category', {}).get('select', {})
                category = category_prop.get('name', '不明')
                
                # 本文（要約）は子ブロックから取得
                summary = "要約なし"
                children_response = self.client.blocks.children.list(block_id=page['id'])
                for child in children_response.get('results', []):
                    if child.get('type') == 'paragraph':
                        text_parts = child.get('paragraph', {}).get('rich_text', [])
                        if text_parts:
                            summary = text_parts[0]['text']['content']
                            break
                
                records.append(PastRecord(date=date_val, title=title, category=category, summary=summary))
            return records
        except Exception as e:
            log_error(e)
            return []

    def save_to_notion(self, data: SummaryData, paper_info: str = "") -> Dict[str, Any]:
        """構造化された学習データをNotionに保存"""
        try:
            children = self._build_notion_page_content(data, paper_info)
            properties = self._build_notion_page_properties(data)

            response = self.client.pages.create(
                parent={"database_id": self.database_id},
                properties=properties,
                children=children
            )
            return response
        except Exception as e:
            # エラーをStreamlitの画面に直接表示させる
            st.error(f"Notionからのデータ読み込み中にエラーが発生しました！")
            st.exception(e) # エラーの詳細を画面に出力
            
            log_error(e) 
            return []

    def _build_notion_page_properties(self, data: SummaryData) -> Dict[str, Any]:
        """Notionページのプロパティを構築"""
        next_actions_text = data.action_items[0][:100] if data.action_items else ""
        return {
            "Title": {"title": [{"text": {"content": data.title}}]},
            "Date": {"date": {"start": datetime.now().strftime('%Y-%m-%d')}},
            "Keywords": {"multi_select": [{"name": tag} for tag in data.keywords]},
            "Next Actions": {"rich_text": [{"text": {"content": next_actions_text}}]},
            "Category": {"select": {"name": data.learning_category}}
        }

    def _build_notion_page_content(self, data: SummaryData, paper_info: str) -> List[Dict[str, Any]]:
        """Notionページの本文コンテンツを構築"""
        content = [
            self._create_heading("📝 学習要約"),
            self._create_paragraph(data.summary),
            self._create_heading("🚀 次のアクション"),
            *self._create_bulleted_list(data.action_items),
        ]
        if paper_info:
            content.extend([
                self._create_heading("📚 関連論文情報"),
                self._create_paragraph(paper_info)
            ])
        return content
    
    # --- Notionブロック作成のヘルパーメソッド ---
    def _create_heading(self, text: str, level: int = 2) -> Dict:
        return {"object": "block", "type": f"heading_{level}", f"heading_{level}": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

    def _create_paragraph(self, text: str) -> Dict:
        return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]}}

    def _create_bulleted_list(self, items: List[str]) -> List[Dict]:
        return [{"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": item}}]}} for item in items]