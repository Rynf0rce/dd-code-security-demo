# dd-code-security-demo

**GSEPS × Datadog Code Security 시연용 저장소**

> ⚠️ **경고**
> 이 저장소의 코드는 Datadog Code Security(SAST / SCA / Secret Scanning / IaC)의
> 탐지 동작을 시연하기 위해 **의도적으로 취약하게** 작성되었습니다.
> 포함된 자격증명·토큰·키는 전부 데모용 더미 문자열이며 실제 시스템과 무관합니다.
> 운영 환경에 배포하거나 `terraform apply` 하지 마십시오.

---

## 목적

| 대상 | 확인 |
|---|---|
| Datadog 조직 | `DPN \| GS Neotek` (`1200353729`) |
| Datadog 사이트 | `us3.datadoghq.com` (`DD_SITE=us3.datadoghq.com`) |
| 시연 일자 | 2026-07-22 GSEPS Code Security 강의 |

## 저장소 구성

```
.
├── app/                        # Python (Flask) 백엔드 — SAST 탐지 대상
│   ├── main.py                 #   SQLi / command injection / SSTI / debug=True
│   ├── utils.py                #   MD5 / yaml.load / pickle / verify=False / insecure random
│   └── config.py               #   하드코딩 자격증명 + Secret Scanning 대상 더미 키
├── frontend/                   # Node.js 대시보드 — SAST + SCA 탐지 대상
│   ├── index.js                #   eval / exec / SHA1 / XSS / prototype pollution
│   ├── package.json
│   └── package-lock.json       #   SCA 대상 lockfile (transitive 포함 80개 패키지)
├── infra/terraform/main.tf     # IaC 탐지 대상 — S3 공개, 0.0.0.0/0 SG, RDS 비암호화, IAM *
├── Dockerfile                  # IaC 탐지 대상 — latest 태그, root 실행, ARG 시크릿 (전시용)
├── Dockerfile.runtime          # 런타임(IAST) 시연용 실제 빌드 이미지
├── docker-compose.yml          # Agent + 계측된 앱 (IAST / Runtime SCA)
├── requirements.txt            # SCA 대상 lockfile (CVE 보유 버전 고정)
├── code-security.datadog.yaml  # Repository 레벨 SAST 설정 (현행 스키마)
└── .github/workflows/
    └── datadog-code-security.yml   # CI 스캔 경로 (대안/설명용)
```

> **파일명 주의**: 구 스키마 `static-analysis.datadog.yml` 은 deprecated 입니다.
> 두 파일이 모두 존재하면 `code-security.datadog.yaml` 이 우선합니다.

## 의도적으로 심어둔 취약점

### SAST (first-party code)

| 파일 | 패턴 | 유형 |
|---|---|---|
| `app/main.py` | 문자열 포맷으로 SQL 조립 | SQL Injection |
| `app/main.py` | `os.system()` + 사용자 입력 | Command Injection |
| `app/main.py` | `subprocess(..., shell=True)` | Command Injection |
| `app/main.py` | `render_template_string()` + 사용자 입력 | SSTI |
| `app/main.py` | `app.run(debug=True, host="0.0.0.0")` | 디버그 모드 노출 |
| `app/utils.py` | `hashlib.md5()` | 취약한 해시 |
| `app/utils.py` | `yaml.load()` (SafeLoader 없음) | 안전하지 않은 역직렬화 |
| `app/utils.py` | `pickle.loads()` | 안전하지 않은 역직렬화 |
| `app/utils.py` | `requests.get(..., verify=False)` | 인증서 검증 비활성화 |
| `app/utils.py` | `random.randint()` 를 ID 생성에 사용 | 취약한 난수 |
| `app/utils.py` | `tempfile.mktemp()`, `chmod 0o777` | 안전하지 않은 임시 파일 |
| `frontend/index.js` | `eval()` + 사용자 입력 | Code Injection |
| `frontend/index.js` | `child_process.exec()` + 사용자 입력 | Command Injection |
| `frontend/index.js` | `crypto.createHash('sha1')` | 취약한 해시 |
| `frontend/index.js` | 이스케이프 없는 HTML 반환 | Reflected XSS |
| `frontend/index.js` | `_.merge(defaults, req.body)` | Prototype Pollution |

### Secret Scanning / 하드코딩 자격증명

| 파일 | 값 |
|---|---|
| `app/config.py` | `DB_PASSWORD`, `LEGACY_SCADA_TOKEN` |
| `app/config.py` | AWS Access Key 패턴 (`AKIAIOSFODNN7EXAMPLE` — AWS 공식 문서 예제값) |
| `app/config.py` | Slack Webhook URL 패턴 |
| `frontend/index.js` | `DASHBOARD_API_KEY` |
| `Dockerfile` | `ARG DB_PASSWORD` 빌드 인자 |
| `infra/terraform/main.tf` | `aws_db_instance.password` 평문 |

### SCA — 알려진 CVE 보유 의존성

전 버전 [OSV](https://osv.dev) 기준 2026-07-20 검증 완료.

| 생태계 | 패키지 | 고정 버전 | 대표 CVE |
|---|---|---|---|
| PyPI | PyYAML | 5.1 | **CVE-2020-14343** (CRITICAL, 임의 코드 실행) |
| PyPI | Pillow | 8.1.0 | **CVE-2021-25287/25288** (CRITICAL) |
| PyPI | Flask | 0.12.2 | CVE-2018-1000656 |
| PyPI | Jinja2 | 2.10 | CVE-2019-10906 (sandbox escape) |
| PyPI | Werkzeug | 0.15.2 | CVE-2024-34069 (HIGH) |
| PyPI | requests | 2.19.1 | CVE-2018-18074 |
| PyPI | urllib3 | 1.24.1 | CVE-2019-11236 |
| PyPI | cryptography | 2.3 | CVE-2023-0286 |
| PyPI | paramiko | 2.4.1 | CVE-2018-1000805 (인증 우회) |
| npm | lodash | 4.17.11 | **CVE-2019-10744** (CRITICAL, prototype pollution) |
| npm | minimist | 1.2.0 | **CVE-2021-44906** (CRITICAL) |
| npm | handlebars | 4.0.11 | **CVE-2019-20922** (CRITICAL, RCE) |
| npm | axios | 0.21.0 | CVE-2020-28168 (SSRF) |
| npm | node-fetch | 2.6.0 | CVE-2022-0235 |
| npm | express | 4.16.0 | CVE-2024-43796 |

### IaC (Terraform / Docker)

> ⚠️ **IaC Security 는 Datadog-hosted 스캔 전용입니다.** GitHub Actions(CI) 경로로는
> 아래 항목이 탐지되지 않습니다. 또한 SAST ruleset 에는 `terraform-*` / `docker-*` 가
> 존재하지 않습니다 (구 `docker-best-practices` ruleset 은 제거됨).
> IaC 룰 ID 형식은 `<platform>-<provider>-<rule>` 입니다.

| 파일 | 패턴 |
|---|---|
| `infra/terraform/main.tf` | S3 `public-read` ACL, public access block 전체 해제 |
| `infra/terraform/main.tf` | S3 서버측 암호화·버저닝 미설정 |
| `infra/terraform/main.tf` | Security Group `0.0.0.0/0` → 22, 4840 |
| `infra/terraform/main.tf` | RDS `publicly_accessible=true`, `storage_encrypted=false` |
| `infra/terraform/main.tf` | IAM 정책 `Action: "*", Resource: "*"` |
| `Dockerfile` | `FROM python:latest` (태그 미고정) |
| `Dockerfile` | `USER` 미지정 → root 실행 |
| `Dockerfile` | 원격 URL `ADD` |

## 오탐(False Positive) 처리 시연

억제 주석은 **바로 다음 한 줄에만** 적용됩니다.

```python
# no-dd-sa
foo = 1
bar = 2      # 이 줄은 억제되지 않음
```

특정 룰만 억제할 때는 `<ruleset>/<rule>` 완전 수식명을 씁니다.

```javascript
// no-dd-sa:javascript-code-style/assignment-name
my_foo = 1
```

> 실제 rule ID 는 로컬에서 한 번 실행해 확인하십시오 — 문서 요약에서 추정한 ID 는
> 신뢰할 수 없습니다:
> `datadog-static-analyzer -i . -g -o sarif.json -f sarif`

**억제는 은폐가 아니라 감사 가능한 상태입니다.**
Datadog 문서: *"Violations suppressed with `no-dd-sa` are shown as suppressed,
rather than omitted entirely, so you can search and audit them."*

- Repositories 페이지 → `is_suppressed: true`
- Vulnerabilities 탐색기 → `status: muted`, `workflow.mute.reason: muted_in_code`

저장소 전체 범위 설정은 `code-security.datadog.yaml`,
조직 전체 설정은 Datadog UI(**Security > Settings > Code Security**)에서 관리합니다.
