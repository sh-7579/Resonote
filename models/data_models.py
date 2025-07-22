from dataclasses import dataclass, field
from typing import List

@dataclass
class SummaryData:
    """対話の要約結果を保持するデータクラス"""
    title: str = "学習記録"
    keywords: List[str] = field(default_factory=list)
    summary: str = "要約が生成されませんでした。"
    action_items: List[str] = field(default_factory=list)
    learning_category: str = "その他"

@dataclass
class PastRecord:
    """過去のNotionレコードを保持するデータクラス"""
    date: str
    title: str
    category: str
    summary: str

    def to_string(self) -> str:
        """テキスト形式でレコードを表現"""
        return f"- {self.date}: {self.title} ({self.category})\n  - 要約: {self.summary}"