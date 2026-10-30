# 범위 형식검증: 생성 / 유지

## 생성→산출→증명→유지 인계

1. 생성: 에이전트가 한 문장 property와 user harm을 실제 코드에서 정한다. repository, 실제 code locator/digest(SHA256), sync revision을 바인딩한다. bounds/assumptions/tool version 및 실제 실행 명령을 고정한다. 사용자 승인된 고정 명령은 에이전트가 직접 실행하되 manifest 안 임의 command 실행은 금지한다. 도구 부재·미승인은 blocked다.
2. 산출: repo/.hermes/verification-skills/verify-&lt;slug&gt;/SKILL.md (slug는 실제 프로젝트 이름으로 치환)는 project-owned 명시 로딩 산출물이며 자동 발견·등록되지 않는다. 등록은 별도 승인 후 의도한 profile의 skill_manage로만 한다. 템플릿의 frontmatter·한국어 H1·필수 섹션을 채우고 미해결 꺾쇠 슬롯·미완료 표시·이중 중괄호 슬롯을 제거한다. 목표는 다음 에이전트가 처음 읽고 재실행하는 것이다.
3. 증명: baseline→faulty mutation 탐지→복원→재실행 순서로 수행하고 각 명령·exit·실제 결과·counterexample·복원 전후 digest를 증거로 보존한다. 승인된 격리 복사본에서 mutation하며 원본을 변경하지 않는다. 예제의 기존 code hash 및 sync revision을 유지하고 source/harness를 고쳐 출처를 맞추지 않는다. baseline이나 mutation 탐지가 실패하면 PASS가 아니다.
4. 유지 인계: 다음 에이전트는 산출물을 명시 로딩하고 편집 전 OLD check, sync 이후 실제 diff와 새 writer, bounds 변경을 검토한다. counterexample/product-bug와 model-harness-drift를 구별하고 근거를 남긴다. 복원 후 재실행 및 증거 hash를 확인한다. 유지 실패·blocked에서 sync 미갱신 원칙을 지키며 통과한 gate 후에만 advance-sync한다. 명시한 유한 bounds를 운영전체·무한증명으로 확대하지 않는다.

create: 실제 코드에서 중요한 promise와 사용자 피해를 고른다. code locator, 파일 SHA256, sync commit, bounds, assumptions, 도구 버전 고정 command를 기록한다. 모델만 대신 검증하지 않는다. 도구가 없으면 blocked로 보고하며 설치나 solver 실행을 암묵적으로 하지 않는다. 실제 코드의 faulty mutation이 property를 깨뜨리는지 확인하고 원복 후 SHA를 비교한다. finding을 숨기기 위해 property를 약화하지 않는다.

maintain: 편집 전 OLD check부터 실행·보존한다. 마지막 sync commit 이후 diff와 commit intent를 읽으며 이동/rename/split된 covered 함수 및 보호 상태의 NEW writer를 찾는다. no-effect / model-harness-drift / intentional-promise-change(출처·이전 및 새 promise 필수) / product-bug로 분류한다. updated와 bug가 동시에 있을 수 있으며 미해결 bug는 finding이다. 원하는 PASS가 아닌 현재 코드에서 모델·harness를 갱신한다. bounds 유지 또는 변경·축소를 명시한다. 갱신 후 실제 faulty mutation을 재실행하고 원복 digest를 확인한다. blocked/failing/미해결일 때 sync marker는 절대로 갱신하지 않는다.

구조 validator는 intent citation이 코드를 충실히 설명하는지 증명하지 못한다. 의미적 분류, NEW writer 탐색의 완전성 및 독립 리뷰는 사람/모델 판단이다. 이 Python AST 스캐너는 명시된 code_root 아래 Python 함수 본문의 Assign/AnnAssign/AugAssign에 나타나는 protected_state 이름/속성 writer만 검출한다. 모듈 수준 대입·alias/setattr·다른 언어·외부 모듈·네이티브 코드·동시성은 보증하지 않는다. 현재 SyntaxError는 traceback+exit 1로 종료한다(구조 오류 exit 2로 정규화되지 않음). 이 범위로 제품 전체를 증명한다고 말하지 않는다.

Receipt JSON: schema_version 정확한 int 1; status pass/fail/blocked; sync_commit, target_commit 40자 hex(형식만 검사하며 git은 조회하지 않음); bounds 양의 int 값 object; assumptions 비어 있지 않은 문자열 list; command는 python3==X.Y.Z run_checks.py 형식의 버전고정 기록일 뿐 실행하지 않는다. code_root root 기준 상대 디렉터리, protected_state 문자열 list, targets 비어 있지 않은 list({path, sha256, locators: qualified 함수명 list}); 첫 target은 mutation 대상. result는 {path, sha256} 증거. findings list는 비어야 PASS.
Result JSON: baseline_pass bool, sequences 양의 int, bounds(receipt와 동일), target_sha256, mutation {detected bool, counterexample list, restored bool, before_sha256, after_sha256}. 현재 코드·실행 결과·원복 digest가 모두 일치해야 한다. SHA는 provenance/정확성의 독립 보증이 아니다.
maintain 추가: maintenance {old_check:{ran_before_edit: true,status:pass/fail/blocked,artifact:{path,sha256}}, reviewed_since:기존 sync, moves_and_new_writers_reviewed:true, bounds_change:unchanged 또는 설명, changes:[{classification, resolved:true, citation, intentional인 경우 old_promise/new_promise}]}. old check의 stale PASS는 새 PASS로 간주하지 않는다.

sync 갱신 명령은 [명령 템플릿](../templates/verification-skill.template.md)에 있다.

advance-sync는 공용 gate 전부를 먼저 통과시킨 경우에만 target_commit으로 marker를 쓴다. 구조 오류/blocked 시 파일을 쓰지 않는다. check는 읽기 전용. exit 0=모든 필수 구조 기준 PASS, 1=stale/missing/empty/coverage/mutation/원복/타입/안전 기준 실패, 2=사용·입출력·JSON 파싱 오류. manifest의 command는 실행하지 않는다. bounded 예제는 명시된 유한 입력 시퀀스만 전수 실행하며 무한 수학 증명, 전체 시스템 증명, 운영제품 검증과 다르다.


# 합성 bounded ledger

운영제품 검증/무한 증명이 아니다. 실제 implementation/ledger.py의 상태 writer에 대해 alphabet -2,-1,1,2, 길이 0..4의 모든 시퀀스를 전수 실행한다. 한도 0..3과 거절 동작을 확인한다. 한도 검사를 제거한 임시 복사본에서 반례를 얻고 원본 SHA의 불변을 확인한다. 네트워크·solver·추가 설치 없음.

실행 명령은 templates/verification-skill.template.md의 코드 블록에 있다. 예제는 항상 복사본에서 실행해 설치된 번들의 receipt/result를 덮어쓰지 않는다. run_checks.py는 --output의 기존 receipt.json에서 코드 revision(sync_commit, target_commit)을 읽어 그대로 다시 기록하며 git HEAD를 따라가지 않는다. receipt가 없거나 revision이 40자 hex가 아니면 아무것도 쓰지 않고 실패한다. command에는 실제로 실행한 interpreter 버전이 기록되므로 번들 receipt와 다른 interpreter의 재실행은 버전 문자열이 다를 수 있다.

Provenance 한계: formal_verification.py는 commit의 형식만 확인하고 git history를 조회하지 않는다. 설치된 예제는 파일 내용과 digest만 검증하며 git 출처는 검증하지 않는다(git check PASS가 아니다). 예제 receipt의 commit은 covered code(ledger.py, run_checks.py)가 실제로 들어 있는 snapshot commit이며, 프로젝트 저장소에서는 tests/support.py의 git_bound가 해당 commit의 git show bytes와 실제 covered 파일 bytes를 대조한다. 없는 commit/path나 bytes 불일치는 실패한다.

테스트는 OLD stale PASS, 이동 함수 및 NEW writer, 의도된 promise 변경(출처와 old/new)과 product bug, blocked sync 갱신 거부, 갱신 후 mutation 재검출·원복을 별도 temporary copy로 시연한다. 원본 bundle은 테스트 중 수정하지 않는다.
