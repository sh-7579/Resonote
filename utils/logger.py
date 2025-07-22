import streamlit as st
import traceback

def log_error(e: Exception):
    """エラーをログに記録し、詳細を表示"""
    st.error(f"エラーが発生しました: {e}")
    st.write(traceback.format_exc())