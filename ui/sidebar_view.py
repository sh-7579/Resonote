import streamlit as st
from .components import render_progress_bar, get_progress_status

def render_sidebar_content(app):
    conversation_ended = st.session_state.get("conversation_ended", False)
    user_exchanges = app.chat_manager.get_user_exchange_count(st.session_state.messages)
    max_exchanges = app.chat_manager.max_exchanges

    # ---- 対話状況カード ----
    st.markdown('<div class="sidebar-card"><div class="sidebar-card-title">📊 対話状況</div>', unsafe_allow_html=True)
    progress_html = render_progress_bar(current=user_exchanges, maximum=max_exchanges, ended=conversation_ended)
    st.markdown(progress_html, unsafe_allow_html=True)

    if conversation_ended:
        st.success("✅ 対話完了。Notionに保存しましょう。")
    else:
        status_info = get_progress_status(user_exchanges, max_exchanges)
        if status_info["progress"] >= 0.7:
            st.warning(f"{status_info['icon']} {status_info['status']}: あと{max_exchanges - user_exchanges}回で終了です")
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- 操作カード ----
    st.markdown('<div class="sidebar-card"><div class="sidebar-card-title">🛠️ 操作</div>', unsafe_allow_html=True)
    if not conversation_ended:
        if st.button("🔚 対話を終了", use_container_width=True):
            st.session_state.conversation_ended = True
            app.add_message("assistant", "対話を終了しました。サイドバーからNotionへの保存が可能です。")
            st.rerun()
    else:
        st.markdown('<p style="color:#28a745;font-size:0.9rem;text-align:center;margin-bottom:0.5rem;">✨ 学習記録の準備ができました</p>', unsafe_allow_html=True)
        if st.button("📝 Notionに保存", key="save_to_notion", use_container_width=True, type="primary"):
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
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- 使い方カード ----
    st.markdown("""
    <div class="sidebar-card">
        <div class="sidebar-card-title">💡 使い方</div>
        <ol style="margin:0;padding-left:1.2rem;font-size:0.88rem;line-height:1.8;">
            <li>学習内容を入力してAIと対話</li>
            <li>好きなタイミングで「対話を終了」</li>
            <li>「Notionに保存」で記録完了</li>
        </ol>
        <p style="font-size:0.82rem;color:#64748b;margin-top:0.6rem;margin-bottom:0;">
            💬 AIが必要に応じて関連論文を自動検索します
        </p>
    </div>
    """, unsafe_allow_html=True)
