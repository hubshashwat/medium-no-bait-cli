from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Article:
    title: str
    link: str
    author: str
    pub_date: datetime
    tags: list = None
    is_premium: bool = False
    content: str = ""
    summary: str = ""

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    def __str__(self):
        return f"{self.title} by {self.author} ({self.claps} claps, {self.reading_time:.1f} min read)"
