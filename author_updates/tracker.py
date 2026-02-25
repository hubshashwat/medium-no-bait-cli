import sys
import os
from datetime import datetime
from typing import List

# Add parent to path to import shared models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.scraper import MediumScraper
from shared.models import Article

class UpdatesTracker:
    def __init__(self, targets: List[str], target_type: str = "authors"):
        self.targets = [t.lstrip("@") for t in targets]
        self.target_type = target_type
        self.scraper = MediumScraper()

    def get_updates_after(self, date_limit: datetime, update_timestamp: bool = False, limit: int = 10, keywords: List[str] = None) -> List[Article]:
        all_updates = []
        from shared.storage import Storage
        storage = Storage()

        for target in self.targets:
            if self.target_type == "authors":
                articles = self.scraper.fetch_articles_from_author(target, limit=limit)
            else:
                articles = self.scraper.fetch_articles_from_publication(target, limit=limit)
            
            updates = [a for a in articles if a.pub_date > date_limit]
            
            # Filter by keywords if provided
            if keywords:
                filtered_updates = []
                for art in updates:
                    content_to_check = (art.title + " " + getattr(art, "summary", "")).lower()
                    if any(kw.lower() in content_to_check for kw in keywords):
                        filtered_updates.append(art)
                updates = filtered_updates

            all_updates.extend(updates)
            
            if update_timestamp and updates:
                storage.update_last_access(target, type=self.target_type, dt=datetime.now())
        
        all_updates.sort(key=lambda x: x.pub_date, reverse=True)
        return all_updates

if __name__ == "__main__":
    # Test
    tracker = AuthorTracker(["@intellizab", "curiosai"])
    limit = datetime(2026, 2, 20)
    print(f"Checking updates after {limit.date()}...")
    updates = tracker.get_updates_after(limit)
    for art in updates:
        print(f"[{art.pub_date.date()}] {art.title} by {art.author}")
