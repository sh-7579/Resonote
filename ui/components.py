from streamlit.components.v1 import html as st_html
import streamlit as st
from datetime import datetime

GLOBAL_CSS = """
<style>
    /* ---- レイアウト ---- */
    .main .block-container {
        max-width: 860px;
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }

    /* ---- ヘッダーバナー ---- */
    .app-header {
        background: linear-gradient(135deg, #2c7be5 0%, #1a56c4 100%);
        color: white;
        padding: 1.4rem 2rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 4px 16px rgba(44,123,229,0.25);
    }
    .app-header-left h1 {
        margin: 0;
        font-size: 1.6rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .app-header-left p {
        margin: 0.2rem 0 0;
        font-size: 0.88rem;
        opacity: 0.85;
    }
    .app-header-date {
        font-size: 0.85rem;
        opacity: 0.8;
        text-align: right;
        white-space: nowrap;
    }

    /* ---- チャットバブル ---- */
    [data-testid="stChatMessage"] {
        border-radius: 14px !important;
        padding: 0.6rem 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    [data-testid="stChatMessage"][data-testid*="user"],
    div[class*="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        background: #dbeafe !important;
        margin-left: 4rem !important;
    }
    div[class*="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        background: #ffffff !important;
        border: 1px solid #e2e8f0 !important;
        margin-right: 4rem !important;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }

    /* ---- チャット入力欄 ---- */
    [data-testid="stChatInput"] textarea {
        border-radius: 12px !important;
        border: 1.5px solid #2c7be5 !important;
        font-size: 0.95rem !important;
    }

    /* ---- スケルトンローディング ---- */
    .skeleton-wrap {
        padding: 0.8rem 1rem;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        margin-right: 4rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .skeleton-line {
        height: 12px;
        border-radius: 6px;
        background: linear-gradient(90deg, #e2e8f0 25%, #f1f5f9 50%, #e2e8f0 75%);
        background-size: 200% 100%;
        animation: shimmer 1.4s infinite;
        margin-bottom: 8px;
    }
    @keyframes shimmer {
        0%   { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }

    /* ---- カスタムスピナー ---- */
    .custom-spinner {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        padding: 0.7rem 1.1rem;
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 10px;
        font-size: 0.9rem;
        color: #1d4ed8;
        margin-bottom: 0.8rem;
    }
    .spinner-dot {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #2c7be5;
        animation: bounce 1.2s infinite ease-in-out;
        display: inline-block;
    }
    .spinner-dot:nth-child(2) { animation-delay: 0.2s; }
    .spinner-dot:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
        40%            { transform: scale(1.0); opacity: 1.0; }
    }

    /* ---- プログレスバー ---- */
    .progress-wrap {
        background: #e9ecef;
        border-radius: 8px;
        padding: 0.2rem;
        margin-bottom: 0.6rem;
    }

    /* ---- サイドバーカード ---- */
    .sidebar-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .sidebar-card-title {
        font-size: 0.78rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 0.5rem;
    }
</style>
"""

def inject_global_css():
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

def render_header():
    today = datetime.now().strftime("%Y年%m月%d日 (%a)")
    st.markdown(f"""
    <div class="app-header">
        <div class="app-header-left">
            <h1>📝 Resonote</h1>
            <p>AIとの対話で学習を記録しよう</p>
        </div>
        <div class="app-header-date">{today}</div>
    </div>
    """, unsafe_allow_html=True)

def render_skeleton_loading():
    st.markdown("""
    <div class="skeleton-wrap">
        <div class="skeleton-line" style="width:75%"></div>
        <div class="skeleton-line" style="width:55%"></div>
        <div class="skeleton-line" style="width:65%"></div>
    </div>
    """, unsafe_allow_html=True)

def render_custom_spinner(label: str = "AIが応答を準備中です..."):
    st.markdown(f"""
    <div class="custom-spinner">
        <span class="spinner-dot"></span>
        <span class="spinner-dot"></span>
        <span class="spinner-dot"></span>
        <span>{label}</span>
    </div>
    """, unsafe_allow_html=True)

def scroll_to_bottom():
    js = """
    <script>
        function scrollToBottom() {
            const body = window.parent.document.querySelector('section.main');
            if (body) { body.scrollTop = body.scrollHeight; }
        }
        setTimeout(scrollToBottom, 150);
    </script>
    """
    st_html(js, height=0, width=0)

def render_progress_bar(current: int, maximum: int, ended: bool) -> str:
    if ended:
        progress_value = 1.0
        color = "#2c7be5"
        status_text = f"対話完了 <b>({current}/{maximum})</b>"
        remaining_text = "保存してください"
    else:
        progress_value = min(current / maximum, 1.0) if maximum > 0 else 0
        remaining = max(0, maximum - current)
        status_text = f"対話回数: <b>{current}/{maximum}</b>"
        remaining_text = f"残り: {remaining} 回"
        if progress_value >= 0.9:   color = "#dc3545"
        elif progress_value >= 0.7: color = "#ffc107"
        else:                       color = "#28a745"

    return f"""
    <div class="progress-wrap">
        <div style="width:{progress_value*100}%;background:{color};height:14px;border-radius:6px;transition:width 0.5s ease;"></div>
    </div>
    <div style="display:flex;justify-content:space-between;font-size:0.88rem;margin-bottom:0.4rem;">
        <span style="color:#64748b;">{status_text}</span>
        <span style="color:{color};font-weight:600;">{remaining_text}</span>
    </div>
    """

def get_progress_status(current: int, maximum: int) -> dict:
    progress_value = min(current / maximum, 1.0) if maximum > 0 else 0
    if progress_value >= 0.9:
        return {"status": "終了間近", "color": "#dc3545", "icon": "🔚", "progress": progress_value}
    elif progress_value >= 0.7:
        return {"status": "要注意",   "color": "#ffc107", "icon": "⚠️",  "progress": progress_value}
    elif progress_value >= 0.5:
        return {"status": "順調",     "color": "#17a2b8", "icon": "📈", "progress": progress_value}
    else:
        return {"status": "開始",     "color": "#28a745", "icon": "🚀", "progress": progress_value}
