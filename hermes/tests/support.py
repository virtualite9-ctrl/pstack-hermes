from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True  # keep installable bundles free of generated .pyc
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'hermes/skills/software-development'
A = BASE / 'pstack-project-verification'
B = BASE / 'pstack-formal-verification'

def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError('Cannot load module: ' + str(path))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

PA = module(A / 'scripts/project_verification.py', 'project')
FB = module(B / 'scripts/formal_verification.py', 'formal')

FORMAL_EXAMPLE = 'hermes/skills/software-development/pstack-formal-verification/assets/examples/bounded_ledger'

def git_bound(root, prefix, receipt, repo=ROOT):
    """Repo provenance only: git show bytes at each receipt commit must equal the covered file bytes."""
    for key in ('sync_commit', 'target_commit'):
        commit = receipt[key]
        known = subprocess.run(['git', 'rev-parse', '--verify', '--quiet', commit + '^{commit}'], cwd=repo, capture_output=True)
        if known.returncode != 0:
            raise ValueError('unknown commit ' + str(commit))
        for target in receipt['targets']:
            name = prefix + '/' + target['path']
            blob = subprocess.run(['git', 'show', commit + ':' + name], cwd=repo, capture_output=True)
            if blob.returncode != 0:
                raise ValueError('git cannot show ' + name + ' at ' + commit)
            if blob.stdout != (root / target['path']).read_bytes():
                raise ValueError('git bytes differ from covered file: ' + name)
    return True

def load(path):
    return json.loads(path.read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def links(bundle):
    for path in bundle.rglob('*.md'):
        for value in re.findall(r'\]\(([^)]+)\)', path.read_text()):
            if value.startswith('https://'):
                continue
            target = (path.parent / value).resolve()
            if not target.is_relative_to(bundle.resolve()) or not target.exists():
                raise ValueError('broken or escaping link: ' + value)

class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.aroot = self.root / 'project'
        self.broot = self.root / 'formal'
        shutil.copytree(A / 'assets/examples', self.aroot)
        shutil.copytree(B / 'assets/examples/bounded_ledger', self.broot)
        self.map = load(self.aroot / 'feature-map.json')
        self.ev = load(self.aroot / 'evidence.json')
        self.receipt = load(self.broot / 'receipt.json')

    def project(self, mode='maintain'):
        return PA.ProjectVerification().check(mode, self.map, self.ev, self.aroot)

    def formal(self, mode='create'):
        return FB.FormalVerification().check(mode, self.receipt, self.broot)

    def maintain(self):
        self.receipt['maintenance'] = {
            'old_check': {'ran_before_edit': True, 'status': 'pass', 'artifact': copy.deepcopy(self.receipt['result'])},
            'reviewed_since': self.receipt['sync_commit'],
            'moves_and_new_writers_reviewed': True, 'bounds_change': 'unchanged',
            'changes': [{'classification': 'no-effect', 'resolved': True, 'citation': 'implementation/ledger.py:Ledger.apply'}]}
        self.receipt['target_commit'] = 'a' * 40

    def update_result(self, change):
        result = load(self.broot / 'result.json')
        change(result)
        (self.broot / 'result.json').write_text(json.dumps(result))
        self.receipt['result']['sha256'] = sha(self.broot / 'result.json')

    def cli(self, skill, root, receipt=None, mode='create', optimize=False, action='check'):
        command = [sys.executable] + (['-O'] if optimize else [])
        command += [str(skill / 'scripts' / ('project_verification.py' if skill == A else 'formal_verification.py')), action, '--mode', mode, '--root', str(root)]
        if skill == A:
            (root / 'map-input.json').write_text(json.dumps(self.map))
            (root / 'ev-input.json').write_text(json.dumps(self.ev))
            command += ['--map', str(root / 'map-input.json'), '--evidence', str(root / 'ev-input.json')]
        else:
            (root / 'receipt-input.json').write_text(json.dumps(self.receipt if receipt is None else receipt))
            command += ['--receipt', str(root / 'receipt-input.json')]
        return subprocess.run(command, text=True, capture_output=True)
