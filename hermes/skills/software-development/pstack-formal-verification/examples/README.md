# 合성 bounded ledger

운영제품 검증/무한 증명이 아니다. 실제 implementation/ledger.py의 상태 writer에 대해 alphabet -2,-1,1,2, 길이 0..4의 모든 시퀀스를 전수 실행한다. 한도 0..3과 거절 동작을 확인한다. 한도 검사를 제거한 임시 복사본에서 반례를 얻고 원본 SHA의 불변을 확인한다. 네트워크·solver·추가 설치 없음.

실행 명령은 [명령 템플릿](../templates/verification-skill.template.md)에 있다. 예제 생성 후 구조 검사를 실행한다.

두 번째 명령은 bounded_ledger에서 실행한다. run_checks 재실행은 현재 interpreter 버전과 fresh receipt를 기록한다. 테스트는 OLD stale PASS, 이동 함수 및 NEW writer, 의도된 promise 변경(출처와 old/new)과 product bug, blocked sync 갱신 거부, 갱신 후 mutation 재검출·원복을 별도 temporary copy로 시연한다. 원본 bundle은 테스트 중 수정하지 않는다.
