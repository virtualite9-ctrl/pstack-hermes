from support import *

class ActualCLI(Fixture):
    def test_project_create_maintain(self):
        for mode in ('create', 'maintain'):
            result = self.cli(A, self.aroot, mode=mode)
            self.assertEqual(result.returncode, 0, result.stderr)
        actual = subprocess.run([sys.executable, str(self.aroot / 'app.py'), 'deposit', '2'], text=True, capture_output=True)
        self.assertEqual(actual.returncode, 0)
        self.assertIn(actual.stdout.strip(), (self.aroot / 'drive.txt').read_text())

    def test_formal_real_exhaustive_mutation_restore(self):
        target = self.broot / 'implementation/ledger.py'
        before = sha(target)
        run = subprocess.run([sys.executable, str(self.broot / 'run_checks.py'), '--output', str(self.broot)], text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(before, sha(target))
        self.receipt = load(self.broot / 'receipt.json')
        self.assertEqual(load(self.broot / 'result.json')['sequences'], sum(4 ** i for i in range(5)))
        result = self.cli(B, self.broot)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.maintain()
        self.receipt['maintenance']['changes'][0]['classification'] = 'model-harness-drift'
        result = self.cli(B, self.broot, mode='maintain', action='advance-sync')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(load(self.broot / 'receipt-input.json')['sync_commit'], 'a' * 40)
        # Updated harness must still detect the mutation and leave the source unchanged.
        rerun = subprocess.run([sys.executable, str(self.broot / 'run_checks.py'), '--output', str(self.broot)], text=True, capture_output=True)
        self.assertEqual(rerun.returncode, 0, rerun.stderr)
        self.assertTrue(load(self.broot / 'result.json')['mutation']['detected'])
        self.assertEqual(before, sha(target))

    def test_optimized_happy(self):
        for skill, root in ((A, self.aroot), (B, self.broot)):
            result = self.cli(skill, root, optimize=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_checked_in_negative_cli_examples(self):
        for path in sorted((A / 'examples').glob('fail-*.json')):
            self.ev = load(path)
            result = self.cli(A, self.aroot, mode='maintain')
            self.assertEqual(result.returncode, 1, (path.name, result.stdout, result.stderr))
