---
name: pstack-project-verification
description: 프로젝트 검증의 생성과 유지 및 증거 구조 검사를 수행한다.
version: 1.0.0
metadata:
  hermes:
    tags: [verification, pstack, project]
---

# 생성 / 유지 검증

create와 maintain은 하나의 공용 클래스에서 처리한다. [절차와 스키마](references/workflow.md)를 먼저 읽고 [라이선스·출처](references/upstream-license.md)를 보존한다.
구조 gate는 독립 리뷰·사람 승인·의미적 정확성을 증명하지 못한다. 기록의 진실성과 intent citation이 코드를 충실히 설명하는지는 사람/모델의 의미판단이다.

[검사기](scripts/project_verification.py), [예제](examples/README.md), [생성 템플릿](templates/verification-skill.template.md), [입력 템플릿](templates/feature-map.template.json)을 사용한다.

실행 명령은 [portable 명령 템플릿](templates/verification-skill.template.md)에 있다.
maintain은 동일 명령의 `--mode maintain`으로 실행한다. 명령은 사용자가 실행하며 manifest의 command는 실행하지 않는다.
