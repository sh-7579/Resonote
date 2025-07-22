import re
from typing import List, Dict

import config

class ChatManager:
    def __init__(self, max_exchanges: int):
        self.max_exchanges = max_exchanges

    def get_user_exchange_count(self, messages: List[Dict[str, str]]) -> int:
        """ユーザーの発言回数をカウント"""
        return sum(1 for msg in messages if msg["role"] == "user")

    def should_end_conversation(self, user_message: str, exchange_count: int) -> bool:
        """対話の終了を判定する"""
        if exchange_count >= self.max_exchanges:
            return True
        
        # 終了キーワードが含まれているかチェック
        if any(keyword in user_message.lower() for keyword in config.SATISFACTION_KEYWORDS):
            return True
        
        # 短い返信が数回続いた場合なども考慮できる
        if len(user_message.strip()) < 10 and exchange_count > 2:
            return True
            
        return False