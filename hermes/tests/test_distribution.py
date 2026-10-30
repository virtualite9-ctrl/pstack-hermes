from support import *

class Distribution(unittest.TestCase):
    def test_full_license_and_sources(self):
        license_bytes = (ROOT / 'pstack/LICENSE').read_bytes()
        self.assertEqual(hashlib.sha256(license_bytes).hexdigest(), 'bc957ca6bee02792566a1a028d105e02e247c6e77cf057061674273da77b200e')
        commit = '1ba91fc25c0977741dd0e267849e6234b037ed0a'
        sources = ['create-verification-skill', 'maintain-verification-skill', 'create-formal-verification-skill', 'maintain-formal-verification-skill']
        for bundle in (A, B):
            text = (bundle / 'references/upstream-license.md').read_bytes()
            self.assertIn(license_bytes, text)
            self.assertIn(b'Lauren Tan', text)
            self.assertIn(b'| Source', text)
            for source in sources:
                path = 'pstack/skills/' + source + '/SKILL.md'
                self.assertIn(('https://github.com/cursor/plugins/blob/' + commit + '/' + path).encode(), text)
                self.assertIn(sha(ROOT / path).encode(), text)
                blob = subprocess.check_output(['git', 'rev-parse', commit + ':' + path], cwd=ROOT).strip()
                self.assertIn(blob, text)

    def test_bundle_links_and_thin_skill(self):
        for bundle in (A, B):
            links(bundle)
            body = (bundle / 'SKILL.md').read_text()
            self.assertIn('metadata:\n  hermes:\n    tags:', body)
            self.assertLess(len(body.splitlines()), 45)
            for link in re.findall(r'\]\(([^)]+)\)', body):
                self.assertNotIn('://', link)

    def test_no_personal_paths_and_placeholders(self):
        for bundle in (A, B):
            for path in bundle.rglob('*'):
                if not path.is_file() or '__pycache__' in path.parts: continue
                text = path.read_text()
                self.assertNotIn('/Users/', text, str(path))
                self.assertNotIn('~/', text, str(path))
                self.assertNotIn('dev-codex@', text, str(path))
                if '.template.' not in path.name:
                    self.assertNotIn('TODO', text, str(path))
                    self.assertFalse(re.search(r'<[A-Za-z_][^>\n]*>', text), str(path))

    def test_manifest(self):
        tool = module(ROOT / 'hermes/tools/make_manifest.py', 'manifest')
        actual = load(ROOT / 'hermes/MANIFEST.json')
        self.assertEqual(actual, tool.build(ROOT / 'hermes'))
        self.assertEqual(len(actual['bundles']), 2)


class NativePackaging(unittest.TestCase):
    def runtime_files(self, bundle):
        return sorted(p.relative_to(bundle).as_posix() for p in bundle.rglob('*')
                      if p.is_file() and p.name != 'SKILL.md' and '__pycache__' not in p.parts and p.suffix != '.pyc')

    def test_native_support_dirs_and_suffixes(self):
        for bundle in (A, B):
            for rel in self.runtime_files(bundle):
                self.assertIn(rel.split('/')[0], ('references', 'templates', 'scripts', 'assets'), rel)
                self.assertIn(Path(rel).suffix, ('.md', '.json', '.py'), rel)

    def test_every_runtime_file_linked_exactly_from_root(self):
        for bundle in (A, B):
            body = (bundle / 'SKILL.md').read_text()
            linked = sorted(re.findall(r'\]\(([^)]+)\)', body))
            self.assertEqual(linked, self.runtime_files(bundle))

    def test_frontmatter_contract(self):
        descriptions = []
        for bundle in (A, B):
            head = (bundle / 'SKILL.md').read_text().split('---')[1]
            fields = dict(line.split(': ', 1) for line in head.splitlines() if ': ' in line and not line.startswith(' '))
            desc = fields['description']
            descriptions.append(desc)
            self.assertLessEqual(len(desc), 60)
            self.assertTrue(desc.endswith('.') and desc.count('.') == 1)
            self.assertEqual(fields['license'], 'MIT')
            self.assertIn('Lauren Tan', fields['author'])
        self.assertNotEqual(*descriptions)

    def test_no_bytecode_and_no_assert_gates(self):
        import ast
        for bundle in (A, B):
            self.assertEqual([p for p in bundle.rglob('*') if p.suffix == '.pyc' or '__pycache__' in p.parts], [])
            for path in bundle.rglob('*.py'):
                self.assertFalse([n for n in ast.walk(ast.parse(path.read_text())) if isinstance(n, ast.Assert)], str(path))
