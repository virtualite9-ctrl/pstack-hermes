"""Document handoff contracts, not semantic proof or a rendering engine."""
import re
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / 'skills/software-development'
FIELDS = ('name', 'description', 'version', 'author', 'license', 'metadata')
SECTIONS = {
    'project': ('Launch', 'Doctor', 'Drive per feature', 'Evidence', 'Cleanup', 'Coverage'),
    'formal': ('Property', 'Harm', 'Code binding+sync', 'Bounds', 'Commands',
               'Mutation', 'Interpretation', 'Maintenance'),
}
COMMON = ('Repository/source locator+digest',)


def frontmatter(text):
    """Inspect the documented simple YAML mapping subset without dependencies."""
    match = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
    if not match:
        raise ValueError('missing frontmatter')
    header = match.group(1)
    values = {}
    for field in FIELDS:
        found = re.findall(r'^' + field + r':[^\S\n]*(.*)$', header, re.M)
        if len(found) != 1:
            raise ValueError('missing/duplicate field: ' + field)
        value = found[0].strip().strip('\"\'')
        if field != 'metadata' and not value:
            raise ValueError('empty field: ' + field)
        values[field] = value
    if not re.search(r'^metadata:\n  verification_kind: (project|formal)$', header, re.M):
        raise ValueError('missing metadata verification_kind')
    description = values['description']
    if len(description) > 60 or not description.endswith('.') or '요청 시' not in description:
        raise ValueError('description must be trigger-first, <=60 chars, final period')
    kind_match = re.search(r'^  verification_kind: (project|formal)$', header, re.M)
    if kind_match is None:
        raise ValueError('missing verification kind')
    return values, kind_match.group(1), text[match.end():]


def check_generated(text):
    """Pure structural acceptance check; raises ValueError, never executes commands."""
    values, kind, body = frontmatter(text)
    if not re.search(r'^# [^\n]*[가-힣][^\n]*$', body, re.M):
        raise ValueError('missing Korean H1')
    for section in COMMON + SECTIONS[kind]:
        if not re.search(r'^## ' + re.escape(section) + r'\n\S', body, re.M):
            raise ValueError('missing/empty section: ' + section)
    if re.search(r'<[^>\n]+>|TODO|\{\{', text):
        raise ValueError('unresolved placeholder')
    return True


def completed_fixture(kind):
    # Deliberately explicit structural fixture, not a claimed live generated skill.
    header = ('---\nname: verify-fixture\n'
              'description: "검증 요청 시 합성 구조를 검사한다."\n'
              'version: 1.0.0\nauthor: test\nlicense: MIT\nmetadata:\n'
              '  verification_kind: ' + kind + '\n---\n# 검증 구조 시험\n')
    return header + ''.join('\n## ' + section + '\n합성 구조 시험값.\n'
                            for section in COMMON + SECTIONS[kind])


class HandoffContract(unittest.TestCase):
    def test_templates_frontmatter_and_sections(self):
        for kind, sections in SECTIONS.items():
            with self.subTest(kind=kind):
                text = (BASE / ('pstack-' + kind + '-verification') /
                        'templates/verification-skill.template.md').read_text()
                values, actual, body = frontmatter(text)
                self.assertEqual(actual, kind)
                self.assertLessEqual(len(values['description']), 60)
                self.assertRegex(body, r'(?m)^# .*?[가-힣]')
                for section in COMMON + sections + ('완성 기준',):
                    self.assertIn('## ' + section + '\n', body)
                for phrase in ('TODO', '<...>', '{{', '다음 에이전트', '실행 완료 증거가 아니다'):
                    self.assertIn(phrase, body)
                with self.assertRaises(ValueError):
                    check_generated(text)

    def test_workflow_handoff_contract(self):
        common = ('생성→산출→증명→유지 인계', '다음 에이전트가 처음 읽고 재실행',
                  '사용자 승인된 고정 명령', '에이전트가 직접 실행', 'manifest 안 임의 command 실행은 금지',
                  'repo/.hermes/verification-skills/verify-&lt;slug&gt;/SKILL.md',
                  'project-owned 명시 로딩 산출물', '자동 발견·등록되지',
                  '별도 승인 후 의도한 profile의 skill_manage')
        phrases = {
            'project': ('단명 CLI', 'read-only', 'feature별 사용자 경로', '관찰 end state',
                        'action/result evidence 생성 명령', '자신이 만든 자원만',
                        'cleanup 후 evidence 생존', 'source/live coverage', 'stdout-only', 'hash'),
            'formal': ('한 문장 property', 'user harm', 'code locator/digest', 'sync revision',
                       'bounds/assumptions/tool version', 'baseline→faulty mutation 탐지→복원→재실행',
                       'counterexample/product-bug', 'model-harness-drift', 'blocked에서 sync 미갱신',
                       '운영전체·무한증명', '함수 본문의 Assign/AnnAssign/AugAssign',
                       '모듈 수준 대입', 'alias/setattr', '다른 언어', '동시성', 'traceback+exit 1'),
        }
        for kind in SECTIONS:
            text = (BASE / ('pstack-' + kind + '-verification') / 'references/workflow.md').read_text()
            for phrase in common + phrases[kind]:
                with self.subTest(kind=kind, phrase=phrase):
                    self.assertIn(phrase, text)

    def test_generated_positive(self):
        for kind in SECTIONS:
            self.assertTrue(check_generated(completed_fixture(kind)))

    def test_generated_missing_frontmatter(self):
        for kind in SECTIONS:
            with self.assertRaises(ValueError):
                check_generated(completed_fixture(kind).split('---\n', 2)[-1])

    def test_generated_missing_fields(self):
        for field in FIELDS:
            text = re.sub(r'^' + field + r':.*\n', '', completed_fixture('project'), flags=re.M)
            with self.subTest(field=field), self.assertRaises(ValueError):
                check_generated(text)

    def test_generated_placeholder(self):
        for kind in SECTIONS:
            for slot in ('<slot>', 'TODO', '{{ value }}'):
                with self.subTest(kind=kind, slot=slot), self.assertRaises(ValueError):
                    check_generated(completed_fixture(kind) + slot)

    def test_generated_missing_sections(self):
        for kind, sections in SECTIONS.items():
            for section in COMMON + sections:
                text = completed_fixture(kind).replace('## ' + section + '\n', '## removed\n')
                with self.subTest(kind=kind, section=section), self.assertRaises(ValueError):
                    check_generated(text)

    def test_generated_description_and_h1(self):
        base = completed_fixture('formal')
        for bad in ('x' * 61 + '.', '검증 요청 시 검사', '설명만 있다.'):
            text = base.replace('검증 요청 시 합성 구조를 검사한다.', bad)
            with self.assertRaises(ValueError):
                check_generated(text)
        with self.assertRaises(ValueError):
            check_generated(base.replace('# 검증 구조 시험', '# English only'))


if __name__ == '__main__':
    unittest.main()
