# Verification draft template
대상: <target>
Launch / Doctor / Drive / Evidence / Cleanup: <repo-grounded steps>
이 템플릿은 실행 완료 증거가 아니다.

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
