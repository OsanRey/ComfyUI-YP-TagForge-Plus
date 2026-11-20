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
        self._corpus_signature = None
        self._corpus_size = 0

    def signature(self):
        return json.dumps([(name, (self.data_dir / name).stat().st_size,
                            (self.data_dir / name).stat().st_mtime_ns) for name in
                           ("danbooru_tags.csv", "danbooru_tags_cooccurrence.csv")])

    def _minimum_corpus_size(self, connection, signature):
        if self._corpus_signature != signature:
            # The CSVs do not include a post total. The union of any two tags
            # gives a lower bound. Use the most common tag and its neighbors
            # so the estimate needs only an indexed lookup of those pairs.
            row = connection.execute("""
                WITH common AS (SELECT tag,count FROM tags ORDER BY count DESC,tag LIMIT 1),
                neighbors AS (
                    SELECT b AS tag,n FROM edges JOIN common ON a=common.tag
                    UNION ALL SELECT a AS tag,n FROM edges JOIN common ON b=common.tag
                )
                SELECT MAX(common.count,COALESCE((
                    SELECT MAX(common.count+t.count-e.n)
                    FROM neighbors e JOIN tags t ON t.tag=e.tag
                    WHERE t.tag<>common.tag AND e.n BETWEEN 1 AND MIN(common.count,t.count)
                ),0)) FROM common
            """).fetchone()
            self._corpus_size = row[0] if row else 0
            self._corpus_signature = signature
        return self._corpus_size

    def ensure(self):
        with self.lock:
            signature = self.signature()
            if self.database.exists():
                try:
                    with closing(sqlite3.connect(self.database)) as connection:
                        if connection.execute("SELECT signature FROM metadata").fetchone() == (signature,):
                            return self._minimum_corpus_size(connection, signature)
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
                with closing(sqlite3.connect(self.database)) as connection:
                    return self._minimum_corpus_size(connection, signature)
            finally:
                temporary.unlink(missing_ok=True)

    def search(self, tag, limit=20):
        return self.search_with_sources(tag, limit)[1]

    def search_with_sources(self, tag, limit=20, alias_groups=()):
        corpus_size = self.ensure()
        if not corpus_size:
            return [], []
        with closing(sqlite3.connect(self.database)) as connection:
            for aliases in ((tag,), *alias_groups):
                sources = [
                    row for alias in sorted(aliases)
                    if (row := connection.execute(
                        "SELECT tag,category FROM tags WHERE tag=? AND count>0", (alias,),
                    ).fetchone())
                ]
                if sources:
                    break
            if not sources:
                return [], []
            names = [name for name, _ in sources]
            parameters = {f"tag{i}": name for i, name in enumerate(names)}
            placeholders = ",".join(f":{key}" for key in parameters)
            general = all(category == "0" for _, category in sources)
            # Rank by overlap above the independence baseline, retaining the
            # Jaccard value and source of the strongest match for each result.
            query = f"""
                WITH sources AS (SELECT tag,category,count FROM tags WHERE tag IN ({placeholders})),
                pairs AS (
                    SELECT s.tag AS source,e.b AS tag,e.n FROM sources s JOIN edges e ON e.a=s.tag
                    UNION ALL
                    SELECT s.tag AS source,e.a AS tag,e.n FROM sources s JOIN edges e ON e.b=s.tag
                ),
                scored AS (
                    SELECT t.tag,t.category,t.count,s.tag AS source,
                        MAX(e.n)/(s.count+t.count-MAX(e.n)) AS similarity,
                        (MAX(e.n)-s.count*t.count/:corpus_size)/(s.count+t.count-MAX(e.n)) AS score
                    FROM pairs e JOIN sources s ON s.tag=e.source JOIN tags t ON t.tag=e.tag
                    WHERE t.tag NOT IN (SELECT tag FROM sources)
                        AND e.n BETWEEN 1 AND MIN(s.count,t.count)
                        AND (:category IS NULL OR t.category=:category)
                        AND (s.category<>'0' OR t.category='0' OR (:characters AND t.category='4'))
                    GROUP BY t.tag,s.tag
                    HAVING score>0
                ),
                ranked AS (
                    SELECT *, ROW_NUMBER() OVER (
                        PARTITION BY tag ORDER BY score DESC,similarity DESC,source
                    ) AS rank FROM scored
                )
                SELECT tag,category,count,similarity,source FROM ranked
                WHERE rank=1
                ORDER BY score DESC,similarity DESC,tag
                LIMIT :limit
            """
            filters = {**parameters, "corpus_size": corpus_size}
            rows = connection.execute(query, {
                **filters, "category": "0" if general else None, "characters": False,
                "limit": max(1, min(100, int(limit))),
            }).fetchall()
            if general:
                rows.extend(connection.execute(query, {
                    **filters, "category": "4", "characters": True, "limit": 5,
                }))
        categories = {"0": "General", "1": "Artist", "3": "Copyright", "4": "Character", "5": "Meta"}
        return names, [{"term": name, "text": name, "value": name, "category": category,
                        "categoryName": categories.get(category, "General"), "postCount": str(int(count)),
                        "site": "danbooru", "translate": "", "similarity": similarity, "sourceTag": source}
                       for name, category, count, similarity, source in rows]
