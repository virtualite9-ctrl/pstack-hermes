---
name: pstack-project-verification
description: 프로젝트의 실행·증거 검증 절차를 만들거나 갱신할 때 쓴다.
version: 1.0.0
author: Lauren Tan (cursor/plugins pstack 원저자), Hermes 포팅
license: MIT
metadata:
  hermes:
    tags: [verification, pstack, project]
---

# 프로젝트 실행·증거 검증 (생성/유지)

create와 maintain은 하나의 공용 클래스에서 처리한다. 원본은 cursor/plugins pstack 0.15.36 (commit 1ba91fc25c0977741dd0e267849e6234b037ed0a), MIT, Lauren Tan이다.
기능 지도, launch/doctor/drive/evidence/cleanup 증거와 소스·라이브 커버리지의 구조를 검사한다. 먼저 references/workflow.md를 읽는다. 전체 시스템 증명이 아니다.
구조 gate는 독립 리뷰·사람 승인·의미적 정확성을 증명하지 못하며 OS sandbox도 아니다. 제품 코드 수정, 공개·push·PR 자동화, 설치는 하지 않고 사람 승인이 필요하다. 기록의 진실성과 intent citation의 충실성은 사람/모델이 판단한다.

실행 명령은 사용자가 실행하며 manifest의 command는 실행하지 않는다. maintain은 같은 명령에 `--mode maintain`을 쓴다.

## 번들 파일
- [assets/examples/app.py](assets/examples/app.py)
- [assets/examples/drive.md](assets/examples/drive.md)
- [assets/examples/evidence.json](assets/examples/evidence.json)
- [assets/examples/feature-map.json](assets/examples/feature-map.json)
- [references/upstream-license.md](references/upstream-license.md)
- [references/workflow.md](references/workflow.md)
- [scripts/project_verification.py](scripts/project_verification.py)
- [templates/verification-skill.template.md](templates/verification-skill.template.md)
