# Verification draft template
대상: <target>
Launch / Doctor / Drive / Evidence / Cleanup: <repo-grounded steps>
이 템플릿은 실행 완료 증거가 아니다.

예제는 복사본에서 실행한다(exit 코드는 줄 끝 주석):

```sh
cp -R <skill_dir>/assets/examples/bounded_ledger ledger-copy
cd ledger-copy
python3 run_checks.py --output .
python3 <skill_dir>/scripts/formal_verification.py check --mode create --receipt receipt.json --root .
python3 <skill_dir>/scripts/formal_verification.py check --mode maintain --receipt receipt.json --root .  # exit 1: create receipt has no maintenance record
python3 <skill_dir>/scripts/formal_verification.py advance-sync --mode maintain --receipt receipt.json --root .  # exit 1: file is not written
```

자신의 대상(실행 완료 증거가 아님):

```text
python3 <skill_dir>/scripts/formal_verification.py check --mode create --receipt receipt.json --root .
python3 <skill_dir>/scripts/formal_verification.py check --mode maintain --receipt receipt.json --root .
python3 <skill_dir>/scripts/formal_verification.py advance-sync --mode maintain --receipt receipt.json --root .
```
