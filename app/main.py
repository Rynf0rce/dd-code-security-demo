"""
GSEPS 설비 점검 API (Datadog Code Security 데모용)

주의: 이 파일은 의도적으로 취약하게 작성되었습니다.
      Datadog SAST 탐지 시연 외의 목적으로 사용하지 마십시오.
"""

import os
import sqlite3
import subprocess

from flask import Flask, request, jsonify, render_template_string

from config import DB_PATH, LEGACY_SCADA_TOKEN
from utils import make_report_id, load_inspection_profile, verify_operator_pin

app = Flask(__name__)


@app.route("/api/equipment")
def get_equipment():
    """설비 조회 — SAST: SQL injection (문자열 포맷으로 쿼리 조립)"""
    plant = request.args.get("plant", "")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = "SELECT id, name, status FROM equipment WHERE plant = '%s'" % plant
    cursor.execute(query)

    rows = cursor.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "status": r[2]} for r in rows])


@app.route("/api/logs/archive", methods=["POST"])
def archive_logs():
    """운전 로그 아카이브 — SAST: command injection (os.system + 사용자 입력)"""
    log_date = request.form.get("date", "")
    os.system("tar czf /backup/logs-" + log_date + ".tar.gz /var/log/scada/" + log_date)
    return jsonify({"archived": log_date})


@app.route("/api/diagnostics")
def run_diagnostics():
    """진단 실행 — SAST: subprocess with shell=True"""
    target = request.args.get("host", "localhost")
    output = subprocess.check_output(
        "ping -c 2 " + target, shell=True, universal_newlines=True
    )
    return jsonify({"output": output})


@app.route("/api/profile/<profile_name>")
def get_profile(profile_name):
    """점검 프로파일 로드 — utils.load_inspection_profile 내부에서 yaml.load 사용"""
    return jsonify(load_inspection_profile(profile_name))


@app.route("/api/report")
def report():
    """리포트 렌더 — SAST: server side template injection"""
    title = request.args.get("title", "일일 점검 리포트")
    template = "<h1>" + title + "</h1><p>report id: " + make_report_id() + "</p>"
    return render_template_string(template)


@app.route("/api/scada/handshake")
def scada_handshake():
    """레거시 SCADA 연동 — SAST: 하드코딩된 자격증명 사용"""
    return jsonify({"token": LEGACY_SCADA_TOKEN, "endpoint": "10.30.1.44:4840"})


@app.route("/api/operator/auth", methods=["POST"])
def operator_auth():
    pin = request.form.get("pin", "")
    return jsonify({"ok": verify_operator_pin(pin)})


if __name__ == "__main__":
    # SAST: Flask debug 모드 활성화 + 모든 인터페이스 바인딩
    app.run(host="0.0.0.0", port=8080, debug=True)
