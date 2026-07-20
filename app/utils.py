"""공통 유틸 — Datadog SAST 탐지 시연용 취약 패턴 모음."""

import hashlib
import os
import pickle
import random
import tempfile

import requests
import yaml

from config import OPERATOR_PIN_MD5, PROFILE_API_BASE


def make_report_id():
    """SAST: 보안에 부적합한 난수 생성기(random) 사용"""
    return "RPT-%06d" % random.randint(0, 999999)


def verify_operator_pin(pin):
    """SAST: 취약한 해시 알고리즘(MD5) 사용"""
    digest = hashlib.md5(pin.encode("utf-8")).hexdigest()
    return digest == OPERATOR_PIN_MD5


def load_inspection_profile(name):
    """SAST: yaml.load를 SafeLoader 없이 호출 — 임의 객체 역직렬화"""
    path = os.path.join("/etc/gseps/profiles", name + ".yml")
    with open(path) as fh:
        return yaml.load(fh.read())


def restore_session(blob):
    """SAST: 신뢰할 수 없는 데이터에 pickle.loads 사용"""
    return pickle.loads(blob)


def fetch_remote_profile(name):
    """SAST: 인증서 검증 비활성화 + timeout 미지정"""
    return requests.get(PROFILE_API_BASE + "/profiles/" + name, verify=False).json()


def write_temp_export(payload):
    """SAST: 예측 가능한 임시 파일 경로 사용"""
    path = "/tmp/gseps-export.csv"
    with open(path, "w") as fh:
        fh.write(payload)
    os.chmod(path, 0o777)
    return path


def make_scratch_dir():
    return tempfile.mktemp(prefix="gseps-")
