---
name: verify-formal-draft
description: "형식 검증 요청 시 한정된 속성을 검사하고 유지 근거를 인계한다."
version: 1.0.0
author: pstack Hermes contributors
license: MIT
metadata:
  verification_kind: formal
---
# 범위 형식검증 인계 초안

이 템플릿은 실행 완료 증거가 아니다. 생성 시 각 항목을 실제 값·명령·결과로 교체한다.

## Repository/source locator+digest
대상 repository: <repository>; source locator: <path:function>; SHA256 digest: <digest>.

## Property
<실제 코드가 지켜야 하는 한 문장 property>

## Harm
<위반 시 구체적인 user harm>

## Code binding+sync
<실제 code locator/digest 및 sync revision·target revision; 출처 대조 명령·결과>

## Bounds
<유한 bounds·assumptions·tool version 및 버전 조회 명령·실제 결과>

## Commands
<승인된 baseline 및 재실행 고정 명령·exit·증거 경로·hash; manifest command는 실행하지 않음>

## Mutation
<baseline→faulty mutation 탐지→복원→재실행 명령과 결과·counterexample·복원 전후 digest>

## Interpretation
<counterexample/product-bug vs model-harness-drift 분류·근거; 운영전체·무한증명 아님>

## Maintenance
<편집 전 OLD check·sync 이후 diff와 NEW writer 검토·bounds 변경·mutation 재검출; 실패·blocked에서 sync 미갱신>

## 완성 기준
frontmatter를 실제 대상에 맞춘다. 미해결 <...>, TODO, {{ 슬롯을 제거한다. 실제 생성 SKILL에는 예제 대신 승인된 대상 명령과 측정한 결과·digest를 넣는다. 다음 에이전트가 처음 읽고 재실행할 수 있어야 한다. AST 탐색·SyntaxError 한계와 산출·등록 경계는 workflow를 따른다.

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
