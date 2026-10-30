---
name: verify-project-draft
description: "프로젝트 검증 요청 시 사용자 경로를 실행하고 증거를 인계한다."
version: 1.0.0
author: pstack Hermes contributors
license: MIT
metadata:
  verification_kind: project
---
# 프로젝트 검증 인계 초안

이 템플릿은 실행 완료 증거가 아니다. 생성 시 각 항목을 실제 값·명령·결과로 교체한다.

## Repository/source locator+digest
대상 repository: <repository>; revision: <revision>; source locator: <path:function>; SHA256 digest: <digest>.

## Launch
<build·launch·readiness 고정 명령과 실제 결과; 단명 CLI는 각 실행 및 잔존 PID 없음 기록>

## Doctor
<읽기 전용 버전·환경·소유 포트·건강 확인 명령과 실제 결과>

## Drive per feature
<feature ID마다 사용자 경로·실행 명령·관찰 end state·기대값·실제값>

## Evidence
<action/result evidence 생성 명령·stdout/stderr·exit·파일 경로·SHA256; stdout-only 여부 명시 및 실제 stdout 보존·hash>

## Cleanup
<자신이 만든 자원만 정리하는 명령·PID; cleanup 후 evidence 생존 및 hash 재확인 명령·결과>

## Coverage
<source/live coverage를 별도로 기록; blocked/unreachable 사유 및 미검증 범위>

## 완성 기준
frontmatter를 실제 대상에 맞춘다. 미해결 <...>, TODO, {{ 슬롯을 제거한다. 실제 생성 SKILL에는 예제 대신 승인된 대상 명령과 측정한 결과·digest를 넣는다. 다음 에이전트가 처음 읽고 재실행할 수 있어야 하며 구조 PASS를 의미적 증명으로 확대하지 않는다. 산출·등록 경계는 workflow를 따른다.

예제는 복사본에서 실행한다(exit 코드는 줄 끝 주석):

```sh
cp -R <skill_dir>/assets/examples project-copy
cd project-copy
python3 <skill_dir>/scripts/project_verification.py check --mode create --map feature-map.json --evidence evidence.json --root .
python3 <skill_dir>/scripts/project_verification.py check --mode maintain --map feature-map.json --evidence evidence.json --root .
sed 's/"sha256": "[0-9a-f]*"/"sha256": "0000000000000000000000000000000000000000000000000000000000000000"/' evidence.json > fail-stale.json
python3 <skill_dir>/scripts/project_verification.py check --mode maintain --map feature-map.json --evidence fail-stale.json --root .  # exit 1: stale evidence
sed 's/"live_coverage": "pass"/"live_coverage": "unreachable"/' evidence.json > fail-unreachable.json
python3 <skill_dir>/scripts/project_verification.py check --mode maintain --map feature-map.json --evidence fail-unreachable.json --root .  # exit 1: unreachable is not PASS
```

feature-map 템플릿(placeholder는 완료 증거가 아님):

```json
{
  "schema_version": 1,
  "features": [
    {
      "id": "<id>",
      "user_path": "<path>"
    }
  ]
}
```

evidence 템플릿:

```json
{
  "schema_version": 1,
  "entries": "<evidence entries>",
  "cleanup": "<owned PID records>",
  "findings": []
}
```
