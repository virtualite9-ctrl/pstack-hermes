"""Deterministic per-file and per-bundle SHA256 manifest; no installation."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

def build(root):
    bundles = {}
    for bundle in sorted((root / 'skills/software-development').iterdir()):
        files = []
        for path in sorted(bundle.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts and path.suffix != '.pyc':
                files.append({'path': path.relative_to(bundle).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        canonical = json.dumps(files, sort_keys=True, separators=(',', ':')).encode()
        bundles[bundle.name] = {'files': files, 'sha256': hashlib.sha256(canonical).hexdigest()}
    return {'schema_version': 1, 'bundle_hash_algorithm': 'sha256(canonical JSON files; sorted keys, compact separators)', 'bundles': bundles}

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    (root / 'MANIFEST.json').write_text(json.dumps(build(root), indent=2) + '\n')
