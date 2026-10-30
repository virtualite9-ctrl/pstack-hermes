from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

class GateError(ValueError):
    pass

def need(condition, message):
    if not condition:
        raise GateError(message)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def safe(root, value):
    need(type(value) is str and bool(value), 'path must be nonempty string')
    p = PurePosixPath(value)
    need(not p.is_absolute() and '..' not in p.parts and '\\' not in value, 'unsafe path')
    current = root
    need(not root.is_symlink(), 'symlink root')
    for part in p.parts:
        current = current / part
        need(not current.is_symlink(), 'symlink forbidden')
    need(current.resolve().is_relative_to(root.resolve()), 'path escape')
    return current

def load(path):
    with open(path, encoding='utf-8') as stream:
        return json.load(stream)

def schema(obj):
    need(type(obj) is dict, 'object required')
    need(type(obj.get('schema_version')) is int and obj['schema_version'] == 1, 'schema_version must be integer 1')

def artifact(root, record):
    need(type(record) is dict, 'artifact record required')
    path = safe(root, record.get('path'))
    need(path.is_file() and path.stat().st_size > 0, 'missing/empty evidence')
    need(type(record.get('sha256')) is str and digest(path) == record['sha256'], 'stale evidence')
    return path

def main_error(function):
    try:
        function()
        print('PASS: structural gate only')
        return 0
    except (GateError, KeyError, TypeError, AttributeError) as error:
        print('FAIL: ' + str(error), file=sys.stderr)
        return 1
    except (OSError, json.JSONDecodeError, UnicodeError) as error:
        print('ERROR: ' + str(error), file=sys.stderr)
        return 2

class ProjectVerification:
    """One non-executing structural gate for create and maintain."""
    def check(self, mode, feature_map, evidence, root):
        schema(feature_map)
        schema(evidence)
        features = feature_map['features']
        need(type(features) is list and bool(features), 'feature map empty')
        ids = []
        for feature in features:
            need(type(feature) is dict, 'feature object')
            identity = feature['id']
            need(type(identity) is str and bool(identity) and identity not in ids, 'feature id')
            ids.append(identity)
            need(type(feature.get('user_path')) is str and bool(feature['user_path']), 'real user path required')
        entries = evidence['entries']
        need(type(entries) is list and bool(entries), 'evidence entries empty')
        seen = set()
        for entry in entries:
            identity = entry['feature_id']
            need(identity in ids and identity not in seen, 'unknown/duplicate feature')
            seen.add(identity)
            need(entry['source_coverage'] == 'pass', 'source coverage missing')
            need(entry['live_coverage'] == 'pass', 'live coverage not pass')
            need(entry.get('attempted_status', 'pass') == 'pass', 'unreachable cannot become PASS')
            need(entry.get('doctor_before') is True, 'doctor required')
            need(entry.get('real_user_path') is True, 'real user drive required')
            files = entry['artifacts']
            need(type(files) is list and bool(files), 'missing evidence files')
            for record in files:
                artifact(root, record)
        if mode == 'maintain':
            need(seen == set(ids), 'uncovered feature')
        cleanup = evidence['cleanup']
        started, stopped = cleanup['started_pids'], cleanup['cleaned_pids']
        need(type(started) is list and type(stopped) is list, 'pid lists')
        need(all(type(pid) is int and pid > 0 for pid in started + stopped), 'pid must be integer')
        need(len(set(started)) == len(started) and len(set(stopped)) == len(stopped), 'duplicate pid')
        need(set(started) == set(stopped), 'cleanup only all owned PIDs')
        need(cleanup['evidence_preserved'] is True, 'evidence must survive cleanup')
        findings = evidence['findings']
        need(type(findings) is list and not findings, 'unresolved findings')
        # Recheck files after cleanup metadata: cleanup must not remove proof.
        for entry in entries:
            for record in entry['artifacts']:
                artifact(root, record)

def cli():
    parser = argparse.ArgumentParser(description='Validate records; never execute manifest commands')
    parser.add_argument('action', choices=['check'])
    parser.add_argument('--mode', choices=['create', 'maintain'], required=True)
    parser.add_argument('--map', required=True)
    parser.add_argument('--evidence', required=True)
    parser.add_argument('--root', default='.')
    args = parser.parse_args()
    return main_error(lambda: ProjectVerification().check(args.mode, load(args.map), load(args.evidence), Path(args.root)))

if __name__ == '__main__':
    sys.exit(cli())
