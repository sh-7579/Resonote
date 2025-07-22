import streamlit as st
from .components import render_progress_bar, get_progress_status

def render_sidebar_content(app):
    """サイドバーのコンテンツ全体を描画する"""
    
    st.header("📊 対話状況")
    user_exchanges = app.chat_manager.get_user_exchange_count(st.session_state.messages)
    max_exchanges = app.chat_manager.max_exchanges
    
    conversation_ended = st.session_state.get("conversation_ended", False)
    
    progress_html = render_progress_bar(
        current=user_exchanges,
        maximum=max_exchanges,
        ended=conversation_ended  # 終了状態を渡す
    )
    st.markdown(progress_html, unsafe_allow_html=True)
    
    # 終了状態に応じてメッセージを表示
    if conversation_ended:
        st.info("✅ 対話完了。Notionに保存しましょう。")
    else:
        status_info = get_progress_status(user_exchanges, max_exchanges)
        if status_info["progress"] >= 0.7:
            st.warning(f"{status_info['icon']} {status_info['status']}: あと{max_exchanges - user_exchanges}回で終了です")

    st.divider()
    st.header("🛠️ 操作")

    if not st.session_state.get("conversation_ended", False):
        # 対話が終了していない場合、「🔚 対話を終了」ボタンを表示
        if st.button("🔚 対話を終了", use_container_width=True):
            st.session_state.conversation_ended = True
            app.add_message("assistant", "対話を終了しました。サイドバーからNotionへの保存が可能です。")
            st.rerun()
    else:
        # 対話が終了している場合、「Notionに保存」ボタンを表示
        st.markdown("""
        <style>
            .sidebar-save-container{padding:1rem;background-color:#f8f9fa;border-radius:8px;border:1px solid #e9ecef;margin:1rem 0}
            .save-ready-text{color:#28a745;font-weight:500;margin-bottom:0.5rem;font-size:.9rem;text-align:center}
            .stButton > button{background-color:#28a745!important;color:#fff!important;border:none!important;border-radius:6px!important;font-weight:500!important;width:100%!important}
            .stButton > button:hover{background-color:#218838!important}
        </style>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown('<div class="save-ready-text">✨ 学習記録の準備ができました</div>', unsafe_allow_html=True)
            if st.button("📝 Notionに保存", key="save_to_notion", use_container_width=True):
                if len(st.session_state.messages) > 1:
                    with st.spinner("要約中..."):
                        structured_data = app.summarize_conversation(st.session_state.messages)
                    if structured_data:
                        with st.spinner("Notionに保存中..."):
                            response = app.save_to_notion(structured_data, st.session_state.paper_info)
                        if response:
                            st.session_state.save_completed = True
                            st.session_state.saved_notion_url = response.get('url', '')
                            st.success("✅ 保存が完了しました！")
                            st.rerun()
                        else:
                            st.error("❌ 保存に失敗しました。")
                    else:
                        st.warning("⚠️ 要約データが生成されませんでした。")
                else:
                    st.warning("⚠️ 対話がありません。")

    st.divider()
    st.header("💡 使用方法")
    st.markdown("""
    1. **学習内容を入力**し、AIと対話
    2. 好きなタイミングで「**対話を終了**」
    3. 「**Notionに保存**」で記録完了
    """)
    st.info("AIが文脈を判断し、必要に応じて 関連論文を自動で検索します。")