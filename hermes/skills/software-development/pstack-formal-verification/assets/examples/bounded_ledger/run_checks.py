"""Exhaustive finite real-code example, not production verification or infinite proof."""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import platform
import re
import tempfile

BOUNDS = {'max_length': 4, 'capacity': 3, 'alphabet_size': 4}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def explore(path):
    namespace = {}
    exec(compile(path.read_text(), str(path), 'exec'), namespace)
    count = 0
    for length in range(BOUNDS['max_length'] + 1):
        for sequence in itertools.product((-2, -1, 1, 2), repeat=length):
            ledger = namespace['Ledger']()
            count += 1
            for amount in sequence:
                before = ledger.balance
                value = ledger.apply(amount)
                expected = before + amount if 0 <= before + amount <= 3 else before
                if value != expected or not 0 <= value <= 3:
                    return False, count, list(sequence)
    return True, count, []

def revisions(output):
    # Covered-code revisions are an explicit input: the receipt already present in --output.
    # They are never read from git HEAD, so reruns cannot drift with later commits.
    try:
        previous = json.loads((output / 'receipt.json').read_text())
        values = [previous['sync_commit'], previous['target_commit']]
    except (OSError, ValueError, KeyError, TypeError):
        raise SystemExit('run_checks needs an existing receipt.json in --output that names the source revision')
    if not all(isinstance(v, str) and re.fullmatch('[0-9a-f]{40}', v) for v in values):
        raise SystemExit('receipt.json revisions must be full 40-hex commits')
    return values

def run(output):
    sync_commit, target_commit = revisions(output)
    source_root = Path(__file__).resolve().parent
    target = source_root / 'implementation/ledger.py'
    output.mkdir(parents=True, exist_ok=True)
    before = sha(target)
    passed, sequences, _ = explore(target)
    # Mutation only touches a temporary copy; original must remain byte-identical.
    with tempfile.TemporaryDirectory(dir=str(output)) as temporary:
        mutant = Path(temporary) / 'ledger.py'
        mutant.write_text(target.read_text().replace('if 0 <= candidate <= 3:', 'if True:'))
        mutant_pass, _, counterexample = explore(mutant)
    after = sha(target)
    result = {'baseline_pass': passed, 'sequences': sequences, 'bounds': BOUNDS,
              'target_sha256': before, 'mutation': {'detected': not mutant_pass,
              'counterexample': counterexample, 'restored': before == after,
              'before_sha256': before, 'after_sha256': after}}
    (output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    receipt = {'schema_version': 1, 'status': 'pass' if passed else 'fail',
        'sync_commit': sync_commit,
        'target_commit': target_commit,
        'bounds': BOUNDS, 'assumptions': ['Sequential operations only; integer inputs in finite alphabet'],
        'command': 'python3==' + platform.python_version() + ' run_checks.py',
        'code_root': 'implementation', 'protected_state': ['balance'],
        'targets': [{'path': 'implementation/ledger.py', 'sha256': before,
                     'locators': ['Ledger.__init__', 'Ledger.apply']},
                    {'path': 'run_checks.py', 'sha256': sha(source_root / 'run_checks.py'), 'locators': []}],
        'result': {'path': 'result.json', 'sha256': sha(output / 'result.json')}, 'findings': []}
    # Output is intended to be this example directory or its complete temporary copy.
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(result, sort_keys=True))
    return 0 if passed and not mutant_pass and before == after else 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    raise SystemExit(run(args.output))
