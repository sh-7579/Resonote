from streamlit.components.v1 import html

def scroll_to_bottom():
    """
    ページの最下部までスクロールするためのJavaScriptを実行するコンポーネント
    """
    js = """
    <script>
        function scrollToBottom() {
            const body = window.parent.document.querySelector('section.main');
            if (body) {
                body.scrollTop = body.scrollHeight;
            }
        }
        // 遅延させて実行することで、コンテンツの描画後にスクロールする
        setTimeout(scrollToBottom, 150);
    </script>
    """
    html(js, height=0, width=0)

def render_progress_bar(current: int, maximum: int, ended: bool) -> str:
    """対話回数の進捗バーをHTMLで描画（終了状態を追加）"""
    
    # 対話が終了しているかどうで表示を切り替える
    if ended:
        progress_value = 1.0
        color = "#0d6efd"  # 完了を示す青色
        status_text = f"対話完了 <b>({current}/{maximum})</b>"
        remaining_text = "保存してください"
    else:
        progress_value = min(current / maximum, 1.0) if maximum > 0 else 0
        remaining = max(0, maximum - current)
        status_text = f"対話回数: <b>{current}/{maximum}</b>"
        remaining_text = f"残り: {remaining} 回"
        
        if progress_value >= 0.9: color = "#dc3545"  # 赤
        elif progress_value >= 0.7: color = "#ffc107"  # 黄
        else: color = "#28a745"  # 緑

    return f"""
    <div style="background: #e9ecef; border-radius: 8px; padding: 0.2rem; margin-bottom: 1rem;">
        <div style="width: {progress_value * 100}%; background: {color}; height: 16px; border-radius: 6px; transition: width 0.5s ease;"></div>
    </div>
    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem;">
        <span style="color: #6c757d;">{status_text}</span>
        <span style="color: {color}; font-weight: bold;">{remaining_text}</span>
    </div>
    """

def get_progress_status(current: int, maximum: int) -> dict:
    """進捗状況の詳細情報を取得"""
    progress_value = min(current / maximum, 1.0) if maximum > 0 else 0
    
    if progress_value >= 0.9:
        status = "終了間近"
        status_color = "#dc3545"
        status_icon = "🔚"
    elif progress_value >= 0.7:
        status = "要注意"
        status_color = "#ffc107"
        status_icon = "⚠️"
    elif progress_value >= 0.5:
        status = "順調"
        status_color = "#17a2b8"
        status_icon = "📈"
    else:
        status = "開始"
        status_color = "#28a745"
        status_icon = "🚀"
    
    return {
        "status": status,
        "color": status_color,
        "icon": status_icon,
        "progress": progress_value,
    }