"""Resolve E7's single canonical retained capture paths."""
import gzip
import json
from pathlib import Path

EVIDENCE=Path(__file__).resolve().parent


def resolve(path):
    path=Path(path)
    if path.exists(): return path
    for manifest in EVIDENCE.glob('e7*-retained.json'):
        for row in json.loads(manifest.read_text())['files']:
            if row['original']==str(path): return EVIDENCE/row['canonical']
    raise FileNotFoundError(path)


def read_capture(path):
    path=resolve(path)
    if path.suffix=='.gz':
        with gzip.open(path,'rb') as f:return f.read()
    return path.read_bytes()
