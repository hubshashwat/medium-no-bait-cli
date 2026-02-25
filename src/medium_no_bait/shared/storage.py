import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class Storage:
    def __init__(self, filename: str = "favorites.json"):
        # Put it in a persistent user directory
        config_dir = os.path.expanduser("~/.medium_no_bait")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        self.filepath = os.path.join(config_dir, filename)
        self.data = self._load()

    def _load(self) -> Dict:
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    data = json.load(f)
                    # Ensure all keys exist for older versions
                    if "authors" not in data: data["authors"] = {}
                    if "publications" not in data: data["publications"] = {}
                    if "keywords" not in data: data["keywords"] = []
                    return data
            except Exception:
                return {"authors": {}, "publications": {}, "keywords": []}
        return {"authors": {}, "publications": {}, "keywords": []}

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.data, f, indent=4)

    # Authors
    def get_authors(self) -> List[str]:
        return list(self.data.get("authors", {}).keys())

    def get_last_access(self, target: str, type: str = "authors") -> Optional[datetime]:
        target = target.lstrip("@")
        ts = self.data.get(type, {}).get(target)
        if ts:
            return datetime.fromisoformat(ts)
        return None

    def add_author(self, author: str):
        author = author.lstrip("@")
        if author not in self.data["authors"]:
            from datetime import timedelta
            self.data["authors"][author] = (datetime.now() - timedelta(days=7)).isoformat()
            self.save()

    def remove_author(self, author: str):
        author = author.lstrip("@")
        if author in self.data["authors"]:
            del self.data["authors"][author]
            self.save()

    # Publications
    def get_publications(self) -> List[str]:
        return list(self.data.get("publications", {}).keys())

    def add_publication(self, pub: str):
        if pub not in self.data["publications"]:
            from datetime import timedelta
            self.data["publications"][pub] = (datetime.now() - timedelta(days=7)).isoformat()
            self.save()

    def remove_publication(self, pub: str):
        if pub in self.data["publications"]:
            del self.data["publications"][pub]
            self.save()

    # Keywords
    def get_keywords(self) -> List[str]:
        return self.data.get("keywords", [])

    def add_keyword(self, word: str):
        if word not in self.data["keywords"]:
            self.data["keywords"].append(word)
            self.save()

    def remove_keyword(self, word: str):
        if word in self.data["keywords"]:
            self.data["keywords"].remove(word)
            self.save()

    def update_last_access(self, target: str, type: str = "authors", dt: Optional[datetime] = None):
        target = target.lstrip("@")
        if target in self.data.get(type, {}):
            dt = dt or datetime.now()
            self.data[type][target] = dt.isoformat()
            self.save()

if __name__ == "__main__":
    s = Storage()
    s.add_author("@shashwatwrites")
    print(f"Authors: {s.get_authors()}")
    print(f"Last access: {s.get_last_access('shashwatwrites')}")
