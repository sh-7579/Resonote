import streamlit as st
import random
from .components import inject_global_css

def render_completion_page():
    inject_global_css()

    st.markdown("""
    <style>
        .fade-in { animation: fadeIn 1.2s ease-in-out; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(16px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        .success-banner {
            background: linear-gradient(135deg, #2c7be5 0%, #1a56c4 100%);
            color: white;
            padding: 2rem;
            border-radius: 14px;
            text-align: center;
            margin-bottom: 1.8rem;
            box-shadow: 0 4px 16px rgba(44,123,229,0.25);
        }
        .success-banner h2 { margin: 0 0 0.4rem; font-size: 1.5rem; }
        .success-banner p  { margin: 0; opacity: 0.88; font-size: 0.95rem; }
        .info-card {
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            border-radius: 12px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 1rem;
        }
        .info-card h4 { color: #1d4ed8; margin: 0 0 0.5rem; font-size: 1rem; }
        .info-card ul { margin: 0; padding-left: 1.2rem; font-size: 0.9rem; line-height: 1.8; }
        .motivational-quote {
            font-style: italic;
            text-align: center;
            color: #64748b;
            margin: 1.5rem 0;
            padding: 1rem 1.4rem;
            border-left: 4px solid #2c7be5;
            background: #f8fafc;
            border-radius: 0 8px 8px 0;
            font-size: 0.95rem;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="fade-in success-banner">
        <h2>🎉 学習記録の保存が完了しました！</h2>
        <p>今日も学習お疲れ様でした。継続的な学習が未来への投資です。</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("saved_notion_url"):
        st.link_button("🔗 Notionページを開く", st.session_state.saved_notion_url, use_container_width=True)

    st.markdown("""
    <div class="info-card">
        <h4>💡 次のステップ</h4>
        <ul>
            <li>Notionで今日の学習内容を見直してみましょう</li>
            <li>明日の学習計画を立ててみませんか？</li>
            <li>学んだ内容を実践に活かすチャンスを探してみましょう</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    motivational_messages = [
        "「学習は一日にして成らず。継続こそが力なり。」",
        "「今日学んだことが、明日のあなたを作る。」",
        "「小さな積み重ねが、大きな変化を生む。」",
        "「知識は誰にも奪われることのない財産です。」",
    ]
    st.markdown(f'<div class="motivational-quote">{random.choice(motivational_messages)}</div>', unsafe_allow_html=True)

    st.markdown("---")
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 新しい記録を開始", type="primary", use_container_width=True):
            st.session_state.start_new_chat = True
            st.rerun()

    st.markdown('<div style="text-align:center;margin-top:2rem;color:#94a3b8;"><small>Resonote | 継続は力なり 💪</small></div>', unsafe_allow_html=True)
