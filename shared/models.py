from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Article:
    title: str
    link: str
    author: str
    pub_date: datetime
    claps: int = 0
    reading_time: float = 0.0
    content: str = ""
    summary: str = ""

    def __str__(self):
        return f"{self.title} by {self.author} ({self.claps} claps, {self.reading_time:.1f} min read)"
