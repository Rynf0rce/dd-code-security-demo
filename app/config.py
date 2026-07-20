"""
설정 값 — Datadog Secret Scanning / SAST(hardcoded credential) 탐지 시연용.

주의: 아래 값은 전부 데모용 더미 문자열이며 실제 시스템과 무관합니다.
"""

import os

DB_PATH = "/var/lib/gseps/equipment.db"

PROFILE_API_BASE = "http://profile-api.gseps.internal"

# SAST: 소스코드에 하드코딩된 자격증명
DB_USER = "gseps_app"
DB_PASSWORD = "Gs3ps!Prod#2024"

LEGACY_SCADA_TOKEN = "scada-legacy-9f2b41c8d7e64a15b93c0e7a5d81f206"

OPERATOR_PIN_MD5 = "e10adc3949ba59abbe56e057f20f883e"

# Secret Scanning: AWS 액세스 키 패턴 (데모용 더미 — 실제 계정 아님)
# 이 값은 AWS 공식 문서의 예제 키이므로 실제 자격증명이 아닙니다.
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# 참고: Slack Incoming Webhook 더미 값도 원래 여기에 있었으나,
#       GitHub push protection 이 푸시 자체를 차단해 제거했습니다.
#       (차단 사유: "Slack Incoming Webhook URL")
#       → 데모에서 언급할 만한 대비 포인트입니다:
#         GitHub push protection 은 "들어오는 것"을 막고,
#         Datadog Secret Scanning 은 "이미 들어와 있는 것"을 전 이력에서 찾아냅니다.
SLACK_ALERT_WEBHOOK = os.environ.get("SLACK_ALERT_WEBHOOK", "")
