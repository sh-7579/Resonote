import os
import requests
import time
import html
from datetime import datetime, timedelta
from typing import Dict, List, Any
import google.generativeai as genai
import config
import utils

class PaperSearcher:
    def __init__(self):
        self.base_url = config.SEMANTIC_SCHOLAR_BASE_URL
        self.headers = {'User-Agent': 'Resonote/1.0'}
        
        # APIキー検証
        api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        if api_key and len(api_key) > 10:
            self.headers['x-api-key'] = api_key
        
        self.last_request_time = 0
        self.min_request_interval = config.MIN_REQUEST_INTERVAL
        self.search_cache = {}
        self.max_cache_size = 100
        self.cache_expiry = timedelta(hours=config.CACHE_EXPIRY_HOURS)
        
        # Geminiモデル初期化
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def search_papers(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """キャッシュ付きの論文検索"""
        if not query or not query.strip():
            return []

        cache_key = f"{query}_{limit}"
        
        # キャッシュ確認
        if cache_key in self.search_cache:
            cached_data, timestamp = self.search_cache[cache_key]
            if datetime.now() - timestamp < self.cache_expiry:
                return cached_data
            else:
                del self.search_cache[cache_key]

        # 新しいデータを取得
        papers = self._make_search_request(query, limit)
        if papers is not None:
            if len(self.search_cache) >= self.max_cache_size:
                oldest_key = next(iter(self.search_cache))
                del self.search_cache[oldest_key]
            
            self.search_cache[cache_key] = (papers, datetime.now())
        
        return papers

    def _make_search_request(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """実際のAPI呼び出し処理"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        
        search_url = f"{self.base_url}/paper/search"
        params = {
            'query': query,
            'limit': limit,
            'fields': 'title,abstract,authors,year,url,citationCount,venue'
        }
        
        response = requests.get(search_url, params=params, headers=self.headers, timeout=15)
        self.last_request_time = time.time()
        
        if response.status_code == 429:
            raise requests.exceptions.RequestException("429 Rate Limited")
        
        response.raise_for_status()
        data = response.json()
        
        return self._process_paper_data(data.get('data', []))

    def _process_paper_data(self, paper_data: List[Dict]) -> List[Dict[str, Any]]:
        """論文データの安全な処理"""
        papers = []
        for paper in paper_data or []:
            if not isinstance(paper, dict):
                continue
            
            authors = []
            for author in paper.get('authors', []) or []:
                if isinstance(author, dict) and author.get('name'):
                    authors.append(author['name'])
            
            paper_info = {
                'title': paper.get('title') or 'No title',
                'abstract': (paper.get('abstract') or 'No abstract')[:300],
                'authors': authors[:5],
                'year': paper.get('year') or 'Unknown',
                'url': paper.get('url') or '',
                'citation_count': max(0, paper.get('citationCount', 0)),
                'venue': paper.get('venue') or 'Unknown venue'
            }
            papers.append(paper_info)
        
        return papers

    def format_papers_for_ai(self, papers: List[Dict[str, Any]]) -> str:
        """論文情報をAI用にフォーマット"""
        if not papers:
            return "関連する論文が見つかりませんでした。"
        
        formatted_papers = []
        for i, paper in enumerate(papers, 1):
            authors_str = ", ".join(paper['authors'][:3])
            if len(paper['authors']) > 3:
                authors_str += " et al."
            
            paper_text = f"""
論文 {i}:
- タイトル: {paper['title']}
- 著者: {authors_str}
- 年: {paper['year']}
- 会議/雑誌: {paper['venue']}
- 被引用数: {paper['citation_count']}
- 要約: {paper['abstract']}
- URL: {paper['url']}
            """
            formatted_papers.append(paper_text.strip())
            
        return "\n\n".join(formatted_papers)

    def needs_paper_search(self, text: str) -> bool:
        """論文検索が必要かチェック"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in config.PAPER_TRIGGER_KEYWORDS)

    def extract_search_query(self, text: str) -> str:
        """検索クエリ抽出"""
        if not text or len(text.strip()) < 3:
            return ""
        
        text = html.escape(text.strip())
        try:
            # 最近の対話から文脈を取得
            import streamlit as st
            recent_messages = st.session_state.messages[-3:] if len(st.session_state.messages) > 3 else st.session_state.messages
            context = "\n".join([f"{msg['role']}: {msg['content']}" for msg in recent_messages])

            prompt = f"""
以下の文脈から論文検索に最適な英語キーワードを3-4個抽出してください。

文脈: {context}
最新メッセージ: {text}

要件:
1. 技術的・学術的なキーワードを優先
2. 具体的な手法名、アルゴリズム名を含める
3. 一般的すぎる語句は除外
4. 出力形式: keyword1 keyword2 keyword3

例: transformer attention mechanism
            """

            response = self.model.generate_content(prompt, 
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=50
                ),
                request_options={"timeout": 30}
            )
            
            raw_query = response.text.strip()
            keywords = [kw.lower() for kw in raw_query.split() if len(kw) >= 3 and kw.replace('-', '').isalnum()]
            
            stop_words = {"the", "and", "for", "with", "using", "based", "method", "approach", "study", "research", "analysis"}
            keywords = [kw for kw in dict.fromkeys(keywords) if kw not in stop_words]
            
            return " ".join(keywords[:4])
            
        except Exception as e:
            utils.log_error(e)
            # フォールバック処理
            words = text.lower().split()
            tech_words = [w for w in words if len(w) > 4 and any(c.isalpha() for c in w)]
            return " ".join(tech_words[:3])
