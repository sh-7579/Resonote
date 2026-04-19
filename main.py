import streamlit as st
import config
from services.ai_service import AIService
from services.notion_service import NotionService
from managers.chat_manager import ChatManager
from ui.completion_page import render_completion_page
from ui.components import scroll_to_bottom, inject_global_css, render_header, render_skeleton_loading, render_custom_spinner
from ui.sidebar_view import render_sidebar_content

class ResonoteAppOrchestrator:
    def __init__(self):
        st.set_page_config(page_title="Resonote", layout="centered", page_icon="📝")
        self.ai_service = AIService(api_key=config.GOOGLE_API_KEY)
        self.notion_service = NotionService(api_key=config.NOTION_API_KEY, database_id=config.NOTION_DATABASE_ID)
        self.chat_manager = ChatManager(max_exchanges=config.MAX_EXCHANGES)

    def add_message(self, role, content):
        st.session_state.messages.append({"role": role, "content": content})

    def run(self):
        if 'app' not in st.session_state:
            st.session_state.app = self

        if st.session_state.get("start_new_chat", False):
            keys_to_delete = [key for key in st.session_state.keys()]
            for key in keys_to_delete:
                del st.session_state[key]
            self.initialize_chat()
        
        if "messages" not in st.session_state:
            self.initialize_chat()

        if st.session_state.get("save_completed", False):
            render_completion_page()
        else:
            self.render_main_app()

    def render_main_app(self):
        inject_global_css()

        if st.session_state.get("scroll_to_bottom", False):
            scroll_to_bottom()
            st.session_state.scroll_to_bottom = False

        render_header()

        with st.sidebar:
            render_sidebar_content(self)

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if not st.session_state.get("conversation_ended", False):
            if prompt := st.chat_input("今日の学習内容を報告してください..."):
                self.handle_user_input(prompt)
    
    def initialize_chat(self):
        with st.spinner("過去の学習記録を読み込んでいます..."):
            past_records = self.notion_service.get_past_records(days=14)
            st.session_state.past_records_text = "\n".join([r.to_string() for r in past_records]) if past_records else "過去の記録はありません。"
        
        st.session_state.paper_info = "まだ論文は検索されていません。"
        chat = self.ai_service.start_chat_session(st.session_state.past_records_text, st.session_state.paper_info)
        st.session_state.chat = chat
        st.session_state.messages = [{"role": "assistant", "content": chat.history[1].parts[0].text}]
        
        st.session_state.save_completed = False
        st.session_state.start_new_chat = False
        st.session_state.conversation_ended = False
        st.session_state.paper_search_performed = False
        st.rerun()

    def handle_user_input(self, prompt: str):
        self.add_message("user", prompt)
        spinner_placeholder = st.empty()
        skeleton_placeholder = st.empty()

        with spinner_placeholder:
            render_custom_spinner("AIが応答を準備中です...")
        with skeleton_placeholder:
            render_skeleton_loading()

        user_exchanges = self.chat_manager.get_user_exchange_count(st.session_state.messages)
        if self.chat_manager.should_end_conversation(prompt, user_exchanges):
            spinner_placeholder.empty()
            skeleton_placeholder.empty()
            self._handle_conversation_end()
            return

        if config.ENABLE_PAPER_SEARCH and not st.session_state.paper_search_performed and self.ai_service.needs_paper_search(prompt):
            spinner_placeholder.empty()
            skeleton_placeholder.empty()
            self._handle_paper_search_flow(prompt)
        else:
            spinner_placeholder.empty()
            skeleton_placeholder.empty()
            self._handle_regular_chat(prompt)

    def _handle_paper_search_flow(self, prompt: str):
        st.session_state.paper_search_performed = True

        search_query = self.ai_service.paper_searcher.extract_search_query(prompt)

        if not search_query:
            self.add_message("assistant", "適切な検索キーワードが見つかりませんでした。")
        else:
            papers = self.ai_service.paper_searcher.search_papers(search_query, limit=3)
            st.session_state.paper_info = self.ai_service.paper_searcher.format_papers_for_ai(papers)

            if "関連する論文が見つかりませんでした" not in st.session_state.paper_info:
                ui_message = f"関連しそうな論文をいくつか見つけました。\n\n---\n\n{st.session_state.paper_info}"
                self.add_message("assistant", ui_message)
            else:
                self.add_message("assistant", st.session_state.paper_info)

            comment_prompt = config.PAPER_COMMENT_PROMPT.format(
                user_prompt=prompt,
                paper_info=st.session_state.paper_info
            )
            response = st.session_state.chat.send_message(comment_prompt)
            self.add_message("assistant", response.text)

        user_exchanges = self.chat_manager.get_user_exchange_count(st.session_state.messages)
        if self.chat_manager.should_end_conversation(prompt, user_exchanges):
            st.session_state.conversation_ended = True

        st.session_state.scroll_to_bottom = True
        st.rerun()

    def _handle_regular_chat(self, prompt: str):
        response = st.session_state.chat.send_message(prompt)
        self.add_message("assistant", response.text)

        user_exchanges = self.chat_manager.get_user_exchange_count(st.session_state.messages)
        if self.chat_manager.should_end_conversation(prompt, user_exchanges):
            st.session_state.conversation_ended = True

        st.session_state.scroll_to_bottom = True
        st.rerun()

    def _handle_conversation_end(self):
        final_comment = self.ai_service.generate_final_comment(
            chat_history=st.session_state.messages,
            paper_info=st.session_state.paper_info
        )
        self.add_message("assistant", final_comment)
        st.session_state.conversation_ended = True

        st.session_state.scroll_to_bottom = True
        st.rerun()

    def summarize_conversation(self, messages):
        return self.ai_service.summarize_conversation(messages)

    def save_to_notion(self, data, paper_info):
        return self.notion_service.save_to_notion(data, paper_info)


if __name__ == "__main__":
    ResonoteAppOrchestrator().run()