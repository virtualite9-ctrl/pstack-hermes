# 프로젝트 절차 및 JSON 계약

## 생성→산출→증명→유지 인계

1. 생성: 에이전트가 실제 repository와 source locator·SHA256 digest·revision을 조사하고 템플릿을 대상에 맞게 완성한다. 목표는 다음 에이전트가 처음 읽고 재실행하는 것이다. 사용자 승인된 고정 명령은 에이전트가 직접 실행한다. manifest 안 임의 command 실행은 금지한다. 승인되지 않은 설치·운영 변경은 blocked로 인계한다.
2. 산출: repo/.hermes/verification-skills/verify-&lt;slug&gt;/SKILL.md (slug는 실제 프로젝트 이름으로 치환)에 작성한다. 이는 project-owned 명시 로딩 산출물이며 자동 발견·등록되지 않는다. 등록은 별도 승인 후 의도한 profile의 skill_manage로만 한다. 유효한 frontmatter와 한국어 H1, 아래 필수 섹션을 채우고 미해결 꺾쇠 슬롯·미완료 표시·이중 중괄호 슬롯을 제거한다. 템플릿 자체와 완료 산출물을 혼동하지 않는다.
3. 증명: Launch에는 조사한 build·launch·readiness 명령을 기록한다. 단명 CLI면 build 및 각 실행을 기록하고 장기 프로세스가 없음을 명시한다. Doctor는 읽기 전용(read-only)이며 첫 실행·새 세션·이상 후 수행한다. Drive per feature에는 feature별 사용자 경로·실행 명령·관찰 end state·기대값과 실제값을 기록한다. Evidence에는 action/result evidence 생성 명령, stdout/stderr·exit·경로·hash를 기록한다. stdout-only 앱이면 명시하고 실제 stdout을 파일로 보존·hash한다. 예: 승인한 앱 명령의 stdout을 drive.stdout에 리다이렉트한 후 python3 -c 'import hashlib,pathlib; p=pathlib.Path("drive.stdout"); print(hashlib.sha256(p.read_bytes()).hexdigest())'로 hash를 기록한다. 검사기 PASS만으로 live 실행을 대신하지 않는다.
4. 유지 인계: Cleanup은 자신이 만든 자원만 대상으로 PID·파일 목록과 정리 명령을 기록한다. evidence를 정리 대상 밖에 두고 cleanup 후 evidence 생존·hash를 실제 재확인한다. Coverage는 source/live coverage를 분리하고 blocked/unreachable을 PASS로 세지 않는다. 다음 에이전트는 생성 SKILL을 명시 로딩하고 Doctor부터 모든 feature를 재실행하며 신규 surface·변경된 source를 조사한다. 실패 증거를 유지하고 제품 코드·기대값을 약화하지 않는다.

create: 저장소에서 surface/run/drive/observe/isolate를 조사한다. 기존 문서·harness를 우선한다. launch는 격리된 데이터와 readiness까지 도달해야 한다. doctor는 버전·소유 포트·인증·건강을 읽기 전용으로 확인한다. 실제 사용자 경로 한 개 이상을 drive하고 action/result/side effect 증거를 남긴 뒤 cleanup한다. stand-in과 실제 환경 차이는 미검증으로 보고한다.

maintain: index와 feature map 전체를 읽고 source entry point를 확인한다. 누락된 새 사용자 surface를 찾는다. source coverage와 live coverage를 분리한다. 모든 mapped feature를 실제로 drive한다. 첫 drive 및 새 세션마다 doctor, 실패/이상 동작 후 doctor 재확인 및 필요 시 알려진 상태로 reset/relaunch한다. unreachable은 시도 경로와 구체적 prerequisite을 기록하고 PASS로 세지 않는다. harness 수정 후 반드시 live 재검증한다. 제품 버그는 finding으로 보존하며 기대값을 고쳐 숨기지 않는다.

cleanup: 성공/실패 모두 자신이 시작해 PID를 기록한 프로세스만 정리한다. 이름으로 kill하지 않는다. 공유 인스턴스는 건드리지 않는다. 실패 반복의 residue도 정리하되 evidence는 보존하고 실제 파일 존재·해시를 재확인한다. 이 검사기는 프로세스를 시작하거나 kill하지 않는다. 운영 PID의 진실성은 별도 리뷰 대상이다.

Map: JSON object, schema_version는 정확한 int 1, features는 비어 있지 않은 list. 각 feature: id(고유 문자열), user_path(실제 사용자 관점 경로 문자열).
Evidence: schema_version int 1, entries list. 각 entry: feature_id, source_coverage(pass/fail/blocked/unreachable/not_run), live_coverage(같은 상태), attempted_status(선택, 원래 시도 상태; pass만 gate 통과), doctor_before bool, real_user_path bool, artifacts list({path: root 기준 상대경로, sha256: 파일 digest}). create는 1개 이상, maintain은 모든 feature를 요구한다. source/live는 둘 다 pass여야 PASS다.
cleanup: started_pids와 cleaned_pids는 중복 없는 양의 int list이며 동일 집합이어야 한다. bool은 int가 아니다. evidence_preserved bool true 필수. findings list는 미해결 제품 버그를 포함하며 비어 있지 않으면 실패한다.

모든 파일 경로는 root 내부이며 절대경로, 부모 탈출, symlink를 거부한다. 임의 command 필드는 실행하지 않는다. CLI exit 0=모든 필수 구조 기준 PASS, 1=missing/empty/stale evidence, coverage/cleanup/타입/안전 gate 실패, 2=사용 오류·입출력·JSON 파싱 오류. 구조 검사는 실제 사용자 실행, doctor의 진실성, 독립 리뷰 또는 의미적 정확성을 증명하지 못한다.


# 합성 CLI 예제

운영제품 검증이 아니다. app.py의 deposit 2를 실제 실행한 출력이 drive.md다. source는 app.py 분기와 연결된다. 단명 CLI이므로 소유 중인 잔존 PID가 없다.

실행 명령은 templates/verification-skill.template.md의 코드 블록에 있다. 예제는 복사본에서 실행한다. create와 maintain은 모두 exit 0이다. 같은 블록의 파생 negative는 복사본의 evidence.json을 sed로 바꿔 만든다: sha256을 0으로 바꾼 stale, live_coverage를 unreachable로 바꾼 경우이며 둘 다 exit 1이다. 더 많은 negative(missing, uncovered, unreachable attempted_status 등)는 프로젝트 저장소 테스트에서 evidence.json을 파생해 재현한다. 템플릿은 완료 증거가 아니다.
