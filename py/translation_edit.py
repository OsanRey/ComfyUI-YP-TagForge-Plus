"""Edit the active translation CSV atomically, preserving other columns and rows."""
import csv
import os
import tempfile
import threading
from pathlib import Path

_lock = threading.Lock()


def save_translation(path, tag, translation):
    path = Path(path)
    with _lock:
        raw = path.read_bytes()
        encoding = "utf-8-sig" if raw.startswith(b"\xef\xbb\xbf") else "utf-8"
        with path.open(encoding=encoding, newline="") as stream:
            rows = list(csv.reader(stream))
        found = False
        for row in rows:
            if row and row[0].strip() == tag:
                if len(row) == 1:
                    row.append(translation)
                else:
                    row[-1] = translation
                found = True
        if not found:
            rows.append([tag, translation])
        newline = "\r\n" if b"\r\n" in raw else "\n"
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding=encoding, newline="", dir=path.parent,
                                             prefix=".translation-", suffix=".tmp", delete=False) as stream:
                temporary = stream.name
                csv.writer(stream, lineterminator=newline).writerows(rows)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
