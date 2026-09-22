"""Resolve E26's single canonical retained capture paths."""
import gzip
import os
import json
from pathlib import Path

EVIDENCE=Path(__file__).resolve().parent


def resolve(path):
    path=Path(path)
    if path.exists() and os.environ.get('E26_CANONICAL_ONLY')!='1': return path
    for manifest in EVIDENCE.glob('e26*-retained.json'):
        for row in json.loads(manifest.read_text())['files']:
            if row['original']==str(path): return EVIDENCE/row['canonical']
    raise FileNotFoundError(path)


def read_capture(path):
    path=resolve(path)
    if path.suffix=='.gz':
        with gzip.open(path,'rb') as f:return f.read()
    return path.read_bytes()
