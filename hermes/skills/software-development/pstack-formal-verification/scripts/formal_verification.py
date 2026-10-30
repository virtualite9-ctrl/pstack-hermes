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

import ast

class FormalVerification:
    """Receipt validation, not a proof engine or arbitrary command runner."""
    def writers(self, root, code_root, states):
        directory = safe(root, code_root)
        need(directory.is_dir(), 'code root missing')
        found = set()
        for path in directory.rglob('*'):
            need(not path.is_symlink(), 'symlink forbidden')
            if path.suffix != '.py' or not path.is_file():
                continue
            tree = ast.parse(path.read_text())
            relative = path.relative_to(root).as_posix()
            def visit(node, prefix):
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                        name = prefix + child.name
                        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            for item in ast.walk(child):
                                if isinstance(item, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                                    targets = item.targets if isinstance(item, ast.Assign) else [item.target]
                                    for target in targets:
                                        for part in ast.walk(target):
                                            key = part.attr if isinstance(part, ast.Attribute) else part.id if isinstance(part, ast.Name) else None
                                            if key in states:
                                                found.add((relative, name))
                        visit(child, name + '.')
                    else:
                        visit(child, prefix)
            visit(tree, '')
        return found

    def check(self, mode, receipt, root):
        schema(receipt)
        need(receipt['status'] == 'pass', 'blocked/failing check')
        for key in ('sync_commit', 'target_commit'):
            need(type(receipt[key]) is str and re.fullmatch('[0-9a-f]{40}', receipt[key]) is not None, 'commit must be full SHA')
        need(type(receipt['bounds']) is dict and bool(receipt['bounds']), 'bounds required')
        for value in receipt['bounds'].values():
            need(type(value) is int and value > 0, 'integer bounds required')
        need(type(receipt['assumptions']) is list and bool(receipt['assumptions']) and all(type(x) is str and x for x in receipt['assumptions']), 'assumptions required')
        need(type(receipt['command']) is str and re.fullmatch(r'python3==[0-9]+\.[0-9]+\.[0-9]+ run_checks\.py', receipt['command']) is not None, 'version pinned command required')
        targets = receipt['targets']
        need(type(targets) is list and bool(targets), 'targets required')
        covered = set()
        for target in targets:
            path = artifact(root, target)
            tree = ast.parse(path.read_text())
            available = set()
            def names(node, prefix=''):
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                        available.add(prefix + child.name)
                        names(child, prefix + child.name + '.')
                    else:
                        names(child, prefix)
            names(tree)
            need(type(target['locators']) is list, 'locators required')
            for locator in target['locators']:
                need(locator in available, 'moved/missing code locator')
                covered.add((target['path'], locator))
        states = receipt['protected_state']
        need(type(states) is list and bool(states) and all(type(x) is str and x for x in states), 'protected state required')
        discovered = self.writers(root, receipt['code_root'], states)
        need(bool(discovered) and discovered.issubset(covered), 'uncovered state writer')
        result = load(artifact(root, receipt['result']))
        need(result['baseline_pass'] is True, 'baseline failed')
        need(type(result['sequences']) is int and result['sequences'] > 0, 'no bounded execution')
        need(result['bounds'] == receipt['bounds'], 'bounds mismatch')
        mutation = result['mutation']
        need(mutation['detected'] is True and type(mutation['counterexample']) is list and bool(mutation['counterexample']), 'mutation not detected')
        need(mutation['restored'] is True, 'not restored')
        target = targets[0]
        need(mutation['before_sha256'] == mutation['after_sha256'] == target['sha256'], 'restoration digest mismatch')
        need(result['target_sha256'] == target['sha256'], 'stale result')
        need(type(receipt['findings']) is list and not receipt['findings'], 'unresolved findings')
        if mode == 'maintain':
            maintenance = receipt['maintenance']
            need(maintenance['old_check']['ran_before_edit'] is True, 'old check must run before edit')
            need(maintenance['old_check']['status'] in ('pass', 'fail', 'blocked'), 'old result required')
            artifact(root, maintenance['old_check']['artifact'])
            need(maintenance['reviewed_since'] == receipt['sync_commit'], 'review sync mismatch')
            need(maintenance['moves_and_new_writers_reviewed'] is True, 'review moved/new writers')
            need(maintenance['bounds_change'] == 'unchanged' or bool(maintenance['bounds_change']), 'bounds disclosure')
            changes = maintenance['changes']
            need(type(changes) is list and bool(changes), 'classification required')
            for change in changes:
                need(change['classification'] in ('no-effect', 'model-harness-drift', 'intentional-promise-change', 'product-bug'), 'unknown classification')
                need(change['resolved'] is True, 'unresolved change')
                need(type(change['citation']) is str and bool(change['citation']), 'source citation required')
                if change['classification'] == 'intentional-promise-change':
                    need(bool(change['old_promise']) and bool(change['new_promise']), 'promise diff required')
                need(change['classification'] != 'product-bug', 'product bug remains finding')

    def advance_sync(self, receipt, root):
        self.check('maintain', receipt, root)
        receipt['sync_commit'] = receipt['target_commit']
        receipt['maintenance']['reviewed_since'] = receipt['target_commit']
        return receipt

def cli():
    parser = argparse.ArgumentParser(description='Structural receipt gate; commands are never executed')
    parser.add_argument('action', choices=['check', 'advance-sync'])
    parser.add_argument('--mode', choices=['create', 'maintain'], required=True)
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--root', required=True)
    args = parser.parse_args()
    def run():
        receipt = load(args.receipt)
        validator = FormalVerification()
        if args.action == 'advance-sync':
            need(args.mode == 'maintain', 'advance requires maintain')
            updated = validator.advance_sync(receipt, Path(args.root))
            Path(args.receipt).write_text(json.dumps(updated, indent=2) + '\n')
        else:
            validator.check(args.mode, receipt, Path(args.root))
    return main_error(run)

if __name__ == '__main__':
    sys.exit(cli())
