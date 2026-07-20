# CI 스캔 경로 예시

`datadog-code-security.yml` 은 GitHub Actions 로 Datadog Code Security 스캔을
실행하는 워크플로우입니다. **"소스코드를 외부로 반출할 수 없다"** 는 요건이 있는
고객을 위한 대안 경로입니다.

## 왜 `.github/workflows/` 가 아니라 여기에 있나

이 저장소의 주 경로는 **Datadog-hosted scanning** 입니다. CI 워크플로우는
데모에서 "온프렘/폐쇄망은 이렇게 갑니다" 를 설명하기 위한 참고 자산이라
기본적으로 비활성 상태로 둡니다.

## 실제로 실행하려면

1. 이 파일을 `.github/workflows/datadog-code-security.yml` 로 이동
   (GitHub 웹 UI 에서 직접 생성하거나, 로컬 PAT 에 `workflow` 스코프 추가 후 푸시)
2. repo Settings > Secrets and variables > Actions 에 등록
   - `DD_API_KEY` — DPN | GS Neotek (US3) org 의 API Key
   - `DD_APP_KEY` — 동일 org 의 Application Key, **`code_analysis_read` 스코프 필수**
3. default branch 에 push

## 주의

- `dd_site` 는 반드시 `us3.datadoghq.com`. 미설정 시 기본값이 US1 이라
  **스캔은 성공하고 결과만 사라집니다.**
- `push` 이벤트만 지원합니다. `pull_request` 트리거를 추가하지 마십시오.
- **IaC Security 는 CI 경로로 실행할 수 없습니다** (Datadog-hosted 전용).
- **AI-Native SAST / Fix with Bits 도 CI 스캔 결과에는 적용되지 않습니다.**
