# 범위 형식검증: 생성 / 유지

create: 실제 코드에서 중요한 promise와 사용자 피해를 고른다. code locator, 파일 SHA256, sync commit, bounds, assumptions, 도구 버전 고정 command를 기록한다. 모델만 대신 검증하지 않는다. 도구가 없으면 blocked로 보고하며 설치나 solver 실행을 암묵적으로 하지 않는다. 실제 코드의 faulty mutation이 property를 깨뜨리는지 확인하고 원복 후 SHA를 비교한다. finding을 숨기기 위해 property를 약화하지 않는다.

maintain: 편집 전 OLD check부터 실행·보존한다. 마지막 sync commit 이후 diff와 commit intent를 읽으며 이동/rename/split된 covered 함수 및 보호 상태의 NEW writer를 찾는다. no-effect / model-harness-drift / intentional-promise-change(출처·이전 및 새 promise 필수) / product-bug로 분류한다. updated와 bug가 동시에 있을 수 있으며 미해결 bug는 finding이다. 원하는 PASS가 아닌 현재 코드에서 모델·harness를 갱신한다. bounds 유지 또는 변경·축소를 명시한다. 갱신 후 실제 faulty mutation을 재실행하고 원복 digest를 확인한다. blocked/failing/미해결일 때 sync marker는 절대로 갱신하지 않는다.

구조 validator는 intent citation이 코드를 충실히 설명하는지 증명하지 못한다. 의미적 분류, NEW writer 탐색의 완전성 및 독립 리뷰는 사람/모델 판단이다. 이 Python AST 스캐너는 명시된 code_root 아래 Python의 Assign/AnnAssign/AugAssign에 나타나는 protected_state 이름/속성 writer만 검출한다. 동적 setattr, 외부 모듈, alias, 네이티브 코드, 동시성은 범위 밖이다. 이 범위로 제품 전체를 증명한다고 말하지 않는다.

Receipt JSON: schema_version 정확한 int 1; status pass/fail/blocked; sync_commit, target_commit 40자 hex; bounds 양의 int 값 object; assumptions 비어 있지 않은 문자열 list; command는 python3==X.Y.Z run_checks.py 형식의 버전고정 기록일 뿐 실행하지 않는다. code_root root 기준 상대 디렉터리, protected_state 문자열 list, targets 비어 있지 않은 list({path, sha256, locators: qualified 함수명 list}); 첫 target은 mutation 대상. result는 {path, sha256} 증거. findings list는 비어야 PASS.
Result JSON: baseline_pass bool, sequences 양의 int, bounds(receipt와 동일), target_sha256, mutation {detected bool, counterexample list, restored bool, before_sha256, after_sha256}. 현재 코드·실행 결과·원복 digest가 모두 일치해야 한다. SHA는 provenance/정확성의 독립 보증이 아니다.
maintain 추가: maintenance {old_check:{ran_before_edit: true,status:pass/fail/blocked,artifact:{path,sha256}}, reviewed_since:기존 sync, moves_and_new_writers_reviewed:true, bounds_change:unchanged 또는 설명, changes:[{classification, resolved:true, citation, intentional인 경우 old_promise/new_promise}]}. old check의 stale PASS는 새 PASS로 간주하지 않는다.

sync 갱신 명령은 [명령 템플릿](../templates/verification-skill.template.md)에 있다.

advance-sync는 공용 gate 전부를 먼저 통과시킨 경우에만 target_commit으로 marker를 쓴다. 구조 오류/blocked 시 파일을 쓰지 않는다. check는 읽기 전용. exit 0=모든 필수 구조 기준 PASS, 1=stale/missing/empty/coverage/mutation/원복/타입/안전 기준 실패, 2=사용·입출력·JSON 파싱 오류. manifest의 command는 실행하지 않는다. bounded 예제는 명시된 유한 입력 시퀀스만 전수 실행하며 무한 수학 증명, 전체 시스템 증명, 운영제품 검증과 다르다.
