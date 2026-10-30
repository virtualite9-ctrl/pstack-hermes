# Verification draft template
대상: <target>
Launch / Doctor / Drive / Evidence / Cleanup: <repo-grounded steps>
이 템플릿은 실행 완료 증거가 아니다.

예제: `python3 <skill_dir>/examples/bounded_ledger/run_checks.py`
검사: `python3 <skill_dir>/scripts/formal_verification.py check --mode create --receipt receipt.json --root .`
유지: `python3 <skill_dir>/scripts/formal_verification.py check --mode maintain --receipt receipt.json --root .`
갱신: `python3 <skill_dir>/scripts/formal_verification.py advance-sync --mode maintain --receipt receipt.json --root .`
