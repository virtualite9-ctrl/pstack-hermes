from support import *

class Negative(Fixture):
    def test_project_missing_empty_stale(self):
        original = copy.deepcopy(self.ev)
        for kind in ('missing', 'empty', 'stale'):
            with self.subTest(kind=kind):
                self.ev = copy.deepcopy(original)
                item = self.ev['entries'][0]['artifacts'][0]
                if kind == 'missing':
                    item['path'] = 'absent.txt'
                elif kind == 'empty':
                    (self.aroot / 'empty.txt').touch()
                    item['path'] = 'empty.txt'
                else:
                    item['sha256'] = '0' * 64
                with self.assertRaises(PA.GateError):
                    self.project()
                self.assertEqual(self.cli(A, self.aroot, optimize=True).returncode, 1)

    def test_uncovered_source_live_unreachable(self):
        original = copy.deepcopy(self.ev)
        for field in ('source_coverage', 'live_coverage', 'attempted_status'):
            for value in ('fail', 'blocked', 'unreachable', 'not_run'):
                with self.subTest(field=field, value=value):
                    self.ev = copy.deepcopy(original)
                    self.ev['entries'][0][field] = value
                    with self.assertRaises(PA.GateError):
                        self.project()
        self.ev = original
        self.map['features'].append({'id': 'new', 'user_path': 'CLI new'})
        with self.assertRaises(PA.GateError):
            self.project()

    def test_bool_int_and_cleanup(self):
        original = copy.deepcopy(self.ev)
        for bad in ('version', 'pid', 'foreign', 'preserved', 'findings'):
            self.ev = copy.deepcopy(original)
            if bad == 'version': self.ev['schema_version'] = True
            if bad == 'pid': self.ev['cleanup']['started_pids'] = [True]
            if bad == 'foreign': self.ev['cleanup']['cleaned_pids'] = [123]
            if bad == 'preserved': self.ev['cleanup']['evidence_preserved'] = False
            if bad == 'findings': self.ev['findings'] = ['product bug']
            with self.subTest(bad=bad), self.assertRaises(PA.GateError): self.project()

    def test_path_escape_symlink_both(self):
        for unsafe in ('../outside', '/etc/passwd', 'link'):
            with self.subTest(path=unsafe):
                for root in (self.aroot, self.broot):
                    if unsafe == 'link': (root / 'link').symlink_to(root / ('drive.md' if root == self.aroot else 'result.json'))
                self.ev['entries'][0]['artifacts'][0]['path'] = unsafe
                self.receipt['result']['path'] = unsafe
                with self.assertRaises(PA.GateError): self.project()
                with self.assertRaises(FB.GateError): self.formal()

    def test_formal_missing_empty_stale(self):
        original = copy.deepcopy(self.receipt)
        for bad in ('missing', 'empty', 'stale'):
            self.receipt = copy.deepcopy(original)
            if bad == 'missing': self.receipt['result']['path'] = 'missing.json'
            if bad == 'empty':
                (self.broot / 'empty.json').touch()
                self.receipt['result']['path'] = 'empty.json'
            if bad == 'stale': self.receipt['targets'][0]['sha256'] = '0' * 64
            with self.subTest(bad=bad), self.assertRaises(FB.GateError): self.formal()
            self.assertEqual(self.cli(B, self.broot, optimize=True).returncode, 1)

    def test_formal_bool_and_command(self):
        original = copy.deepcopy(self.receipt)
        for bad in ('version', 'bounds', 'command'):
            self.receipt = copy.deepcopy(original)
            if bad == 'version': self.receipt['schema_version'] = True
            if bad == 'bounds': self.receipt['bounds']['max_length'] = True
            if bad == 'command': self.receipt['command'] = 'python3 run_checks.py; dangerous-command'
            with self.subTest(bad=bad), self.assertRaises(FB.GateError): self.formal()

    def test_old_stale_pass_real_code_change(self):
        path = self.broot / 'implementation/ledger.py'
        path.write_text(path.read_text() + '\n# current code differs from old PASS\n')
        with self.assertRaises(FB.GateError): self.formal()
        self.assertEqual(self.cli(B, self.broot).returncode, 1)

    def test_moved_locator(self):
        path = self.broot / 'implementation/ledger.py'
        path.write_text(path.read_text().replace('def apply(', 'def moved_apply('))
        self.receipt['targets'][0]['sha256'] = sha(path)
        with self.assertRaisesRegex(FB.GateError, 'locator'): self.formal()

    def test_new_state_writer(self):
        (self.broot / 'implementation/new_writer.py').write_text('def overwrite(ledger):\n    ledger.balance = 900\n')
        with self.assertRaisesRegex(FB.GateError, 'writer'): self.formal()

    def test_mutation_not_detected_and_not_restored(self):
        self.update_result(lambda result: result['mutation'].update(detected=False))
        with self.assertRaisesRegex(FB.GateError, 'mutation'): self.formal()
        self.update_result(lambda result: result['mutation'].update(detected=True, restored=False))
        with self.assertRaisesRegex(FB.GateError, 'restored'): self.formal()

    def test_blocked_advance_no_write(self):
        self.maintain()
        self.receipt['status'] = 'blocked'
        before = copy.deepcopy(self.receipt)
        with self.assertRaises(FB.GateError): FB.FormalVerification().advance_sync(self.receipt, self.broot)
        self.assertEqual(before, self.receipt)
        result = self.cli(B, self.broot, mode='maintain', action='advance-sync')
        self.assertEqual(result.returncode, 1)
        self.assertEqual(load(self.broot / 'receipt-input.json'), before)

    def test_intent_vs_bug(self):
        self.maintain()
        change = self.receipt['maintenance']['changes'][0]
        change.update(classification='intentional-promise-change', old_promise='capacity 2', new_promise='capacity 3', citation='implementation/ledger.py:Ledger.apply capacity 3')
        self.formal('maintain')
        change['citation'] = ''
        with self.assertRaises(FB.GateError): self.formal('maintain')
        change.update(classification='product-bug', citation='implementation/ledger.py:Ledger.apply violation')
        with self.assertRaises(FB.GateError): self.formal('maintain')

    def test_old_check_required_and_unresolved(self):
        self.maintain()
        self.receipt['maintenance']['old_check']['ran_before_edit'] = False
        with self.assertRaises(FB.GateError): self.formal('maintain')
        self.receipt['maintenance']['old_check']['ran_before_edit'] = True
        self.receipt['maintenance']['changes'][0]['resolved'] = False
        with self.assertRaises(FB.GateError): self.formal('maintain')

    def test_broken_required_link(self):
        bundle = self.root / 'broken-bundle'
        shutil.copytree(A, bundle)
        (bundle / 'references/workflow.md').unlink()
        with self.assertRaises(ValueError): links(bundle)

    def test_json_and_usage_exit_two(self):
        path = self.broot / 'broken.json'
        path.write_text('{')
        command = [sys.executable, str(B / 'scripts/formal_verification.py'), 'check', '--mode', 'create', '--receipt', str(path), '--root', str(self.broot)]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
        self.assertEqual(subprocess.run(command[:2], capture_output=True).returncode, 2)

    def test_git_binding_negatives(self):
        self.assertTrue(git_bound(self.broot, FORMAL_EXAMPLE, self.receipt))
        for key in ('sync_commit', 'target_commit'):
            bad = copy.deepcopy(self.receipt)
            bad[key] = 'f' * 40
            with self.subTest(unknown=key), self.assertRaises(ValueError): git_bound(self.broot, FORMAL_EXAMPLE, bad)
        old = dict(self.receipt, sync_commit='1ba91fc25c0977741dd0e267849e6234b037ed0a', target_commit='1ba91fc25c0977741dd0e267849e6234b037ed0a')
        with self.assertRaises(ValueError): git_bound(self.broot, FORMAL_EXAMPLE, old)  # original defect: path absent at that commit
        with self.assertRaises(ValueError): git_bound(self.broot, FORMAL_EXAMPLE + '-wrong', self.receipt)
        for name in ('implementation/ledger.py', 'run_checks.py'):
            with self.subTest(mismatch=name):
                path = self.broot / name
                original = path.read_bytes()
                path.write_bytes(original + b'\n# differs\n')
                with self.assertRaises(ValueError): git_bound(self.broot, FORMAL_EXAMPLE, self.receipt)
                path.write_bytes(original)

    def test_structural_validator_does_not_check_git(self):
        self.receipt['sync_commit'] = self.receipt['target_commit'] = 'f' * 40
        self.formal()  # shape-only: nonexistent commit passes the validator
        with self.assertRaises(ValueError): git_bound(self.broot, FORMAL_EXAMPLE, self.receipt)
