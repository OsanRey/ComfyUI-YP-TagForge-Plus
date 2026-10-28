"""Disk index of Autocomplete Plus co-occurrences; no browser-side 100 MB load."""
import csv
import json
import os
import sqlite3
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import Lock
from contextlib import closing


class RelatedIndex:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.database = self.data_dir / "related.sqlite3"
        self.lock = Lock()

    def signature(self):
        return json.dumps([(name, (self.data_dir / name).stat().st_size,
                            (self.data_dir / name).stat().st_mtime_ns) for name in
                           ("danbooru_tags.csv", "danbooru_tags_cooccurrence.csv")])

    def ensure(self):
        with self.lock:
            signature = self.signature()
            if self.database.exists():
                try:
                    with closing(sqlite3.connect(self.database)) as connection:
                        if connection.execute("SELECT signature FROM metadata").fetchone()[0] == signature:
                            return
                except sqlite3.DatabaseError:
                    pass
            with NamedTemporaryFile(dir=self.data_dir, suffix=".tmp", delete=False) as stream:
                temporary = Path(stream.name)
            try:
                connection = sqlite3.connect(temporary)
                try:
                    connection.executescript("""
                        PRAGMA journal_mode=OFF;
                        CREATE TABLE metadata(signature TEXT);
                        CREATE TABLE tags(tag TEXT PRIMARY KEY, category TEXT, count REAL);
                        CREATE TABLE edges(a TEXT, b TEXT, n REAL);
                    """)
                    with (self.data_dir / "danbooru_tags.csv").open(encoding="utf-8-sig", newline="") as stream:
                        reader = csv.DictReader(stream)
                        connection.executemany("INSERT OR REPLACE INTO tags VALUES(?,?,?)",
                            ((row["tag"], row["category"], float(row["count"])) for row in reader))
                    with (self.data_dir / "danbooru_tags_cooccurrence.csv").open(encoding="utf-8-sig", newline="") as stream:
                        reader = csv.DictReader(stream)
                        connection.executemany("INSERT INTO edges VALUES(?,?,?)",
                            ((row["tag_a"], row["tag_b"], float(row["count"])) for row in reader))
                    connection.executescript("CREATE INDEX edge_a ON edges(a); CREATE INDEX edge_b ON edges(b);")
                    connection.execute("INSERT INTO metadata VALUES(?)", (signature,))
                    connection.commit()
                finally:
                    connection.close()
                os.replace(temporary, self.database)
            finally:
                temporary.unlink(missing_ok=True)

    def search(self, tag, limit=20):
        self.ensure()
        with closing(sqlite3.connect(self.database)) as connection:
            count = connection.execute("SELECT count FROM tags WHERE tag=?", (tag,)).fetchone()
            if not count or not count[0]:
                return []
            rows = connection.execute("""
                SELECT t.tag,t.category,t.count,MAX(e.n)/(?+t.count-MAX(e.n)) AS score
                FROM (SELECT b AS tag,n FROM edges WHERE a=?
                      UNION ALL SELECT a AS tag,n FROM edges WHERE b=?) e
                JOIN tags t ON t.tag=e.tag
                WHERE t.tag<>? AND t.count>0
                GROUP BY t.tag HAVING score>0
                ORDER BY score DESC,t.tag LIMIT ?
            """, (count[0], tag, tag, tag, max(1, min(100, int(limit))))).fetchall()
        categories = {"0": "General", "1": "Artist", "3": "Copyright", "4": "Character", "5": "Meta"}
        return [{"term": name, "text": name, "value": name, "category": category,
                 "categoryName": categories.get(category, "General"), "postCount": str(int(count)),
                 "site": "danbooru", "translate": "", "similarity": score}
                for name, category, count, score in rows]
