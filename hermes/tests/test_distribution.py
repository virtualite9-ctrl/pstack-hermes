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
            self.assertLess(len(body.splitlines()), 30)
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
