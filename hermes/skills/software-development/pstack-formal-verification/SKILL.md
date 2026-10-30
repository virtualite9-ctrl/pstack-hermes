---
name: pstack-formal-verification
description: 코드에 연결된 경계 속성 검증을 만들거나 갱신할 때 쓴다.
version: 1.0.0
author: Lauren Tan (cursor/plugins pstack 원저자), Hermes 포팅
license: MIT
metadata:
  hermes:
    tags: [verification, pstack, formal]
---

# 경계 속성 검증 (생성/유지)

create와 maintain은 하나의 공용 클래스에서 처리한다. 원본은 cursor/plugins pstack 0.15.36 (commit 1ba91fc25c0977741dd0e267849e6234b037ed0a), MIT, Lauren Tan이다.
실제 예제 코드를 한도 내에서 전수 실행하고 mutation 민감도·sync commit 영수증을 검사한다. 먼저 references/workflow.md를 읽는다. 무한 증명이나 운영 시스템 증명이 아니다.
구조 gate는 독립 리뷰·사람 승인·의미적 정확성을 증명하지 못하며 OS sandbox도 아니다. 제품 코드 수정, 공개·push·PR 자동화, 설치는 하지 않고 사람 승인이 필요하다. 기록의 진실성과 intent citation의 충실성은 사람/모델이 판단한다.

실행 명령은 사용자가 실행하며 manifest의 command는 실행하지 않는다. maintain은 같은 명령에 `--mode maintain`을 쓴다.

## 번들 파일
- [assets/examples/bounded_ledger/implementation/ledger.py](assets/examples/bounded_ledger/implementation/ledger.py)
- [assets/examples/bounded_ledger/receipt.json](assets/examples/bounded_ledger/receipt.json)
- [assets/examples/bounded_ledger/result.json](assets/examples/bounded_ledger/result.json)
- [assets/examples/bounded_ledger/run_checks.py](assets/examples/bounded_ledger/run_checks.py)
- [references/upstream-license.md](references/upstream-license.md)
- [references/workflow.md](references/workflow.md)
- [scripts/formal_verification.py](scripts/formal_verification.py)
- [templates/receipt.template.json](templates/receipt.template.json)
- [templates/verification-skill.template.md](templates/verification-skill.template.md)
