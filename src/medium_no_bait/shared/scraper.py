import requests
from datetime import datetime
from typing import List
import xml.etree.ElementTree as ET
from .models import Article

class MediumScraper:
    AUTHOR_RSS_TEMPLATE = "https://medium.com/feed/@{author}"
    PUBLICATION_RSS_TEMPLATE = "https://medium.com/feed/{pub}"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        })

    def fetch_articles_from_author(self, author: str, limit: int = 10) -> List[Article]:
        author = author.lstrip("@")
        url = self.AUTHOR_RSS_TEMPLATE.format(author=author)
        return self._fetch_from_rss(url, limit)

    def fetch_articles_from_publication(self, pub: str, limit: int = 10) -> List[Article]:
        url = self.PUBLICATION_RSS_TEMPLATE.format(pub=pub)
        return self._fetch_from_rss(url, limit)

    def _fetch_from_rss(self, url: str, limit: int = 10) -> List[Article]:
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return []
            
            root = ET.fromstring(response.content)
            articles = []
            for item in root.findall(".//item")[:limit]:
                title_elem = item.find("title")
                link_elem = item.find("link")
                if title_elem is None or link_elem is None: continue
                
                # Namespaces for Medium-specific metadata
                ns = {'content': 'http://purl.org/rss/1.0/modules/content/', 'dc': 'http://purl.org/dc/elements/1.1/'}
                
                title = title_elem.text
                link = link_elem.text
                
                author_elem = item.find("dc:creator", ns)
                author_name = author_elem.text if author_elem is not None else "Unknown"
                
                # 1. Tags (Author-defined categories)
                tags = [cat.text for cat in item.findall("category")]
                
                # 2. Premium Detection (Missing <content:encoded> in Premium RSS items)
                content_elem = item.find("content:encoded", ns)
                is_premium = content_elem is None
                
                pub_date_str = item.find("pubDate").text
                try:
                    pub_date = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S %Z")
                except ValueError:
                    pub_date = datetime.now()

                articles.append(Article(
                    title=title,
                    link=link,
                    author=author_name,
                    pub_date=pub_date,
                    tags=tags,
                    is_premium=is_premium
                ))
            return articles
        except Exception:
            return []
