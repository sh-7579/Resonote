import streamlit as st
import random

def render_completion_page():
    """保存完了ページ全体を描画する関数"""
    
    # ページ専用のスタイル
    st.markdown("""
    <style>
        /* (ご提示いただいたCSSスタイルをここにそのまま貼り付け) */
        .fade-in {
            animation: fadeIn 2s ease-in-out;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .section {
            margin-bottom: 1.5rem;
            padding: 1.5rem;
            background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%);
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(44, 123, 229, 0.1);
            border: 1px solid rgba(44, 123, 229, 0.1);
        }
        .section h3 {
            color: #2c7be5;
            margin-bottom: 0.8rem;
            font-size: 1.2rem;
        }
        .section p {
            margin: 0;
            line-height: 1.6;
        }
        .success-banner {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 12px rgba(40, 167, 69, 0.2);
        }
        .next-steps {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 1.5rem;
            margin: 1.5rem 0;
        }
        .motivational-quote {
            font-style: italic;
            text-align: center;
            color: #6c757d;
            margin: 2rem 0;
            padding: 1rem;
            border-left: 4px solid #2c7be5;
            background: #f8f9fa;
        }
    </style>
    """, unsafe_allow_html=True)

    # 成功バナー
    st.markdown("""
    <div class="fade-in success-banner">
        <h2>🎉 学習記録の保存が完了しました！</h2>
        <p>今日も学習お疲れ様でした。継続的な学習が未来への投資です。</p>
    </div>
    """, unsafe_allow_html=True)

    # Notionリンクセクション
    if st.session_state.get("saved_notion_url"):
        st.markdown('<div class="section"><h3>📝 Notionで記録を確認</h3><p>保存された学習記録をNotionで詳細に確認できます。</p></div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align: center; margin: 1.5rem 0;">
            <a href="{st.session_state.saved_notion_url}" target="_blank" style="text-decoration: none;">
                <button style="background: linear-gradient(135deg, #2c7be5 0%, #1e88e5 100%); color: white; padding: 0.8rem 2rem; border: none; border-radius: 8px; font-size: 1.1rem; cursor: pointer; box-shadow: 0 4px 12px rgba(44, 123, 229, 0.3); transition: all 0.3s ease;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                    🔗 Notionページを開く
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)

    # 次のステップ提案
    st.markdown("""
    <div class="next-steps">
        <h4>💡 次のステップ</h4>
        <ul>
            <li>Notionで今日の学習内容を見直してみましょう</li>
            <li>明日の学習計画を立ててみませんか？</li>
            <li>学んだ内容を実践に活かすチャンスを探してみましょう</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

    # モチベーショナルメッセージ
    motivational_messages = [
        "「学習は一日にして成らず。継続こそが力なり。」", "「今日学んだことが、明日のあなたを作る。」",
        "「小さな積み重ねが、大きな変化を生む。」", "「知識は誰にも奪われることのない財産です。」"
    ]
    st.markdown(f'<div class="motivational-quote">{random.choice(motivational_messages)}</div>', unsafe_allow_html=True)

    # アクションボタンエリア（リセット機能はapp.py側で制御）
    st.markdown("---")
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 新しい記録を開始", type="primary", use_container_width=True):
            # このボタンが押されたことをapp.pyに知らせるため、状態をセットして再実行
            st.session_state.start_new_chat = True
            st.rerun()

    # フッター
    st.markdown('<div style="text-align: center; margin-top: 2rem; color: #6c757d;"><small>学習記録アプリ | 継続は力なり 💪</small></div>', unsafe_allow_html=True)