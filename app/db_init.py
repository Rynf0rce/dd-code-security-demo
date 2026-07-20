"""
런타임 데모용 SQLite 초기화 스크립트.

IAST 는 taint tracking 방식이라 **사용자 입력이 실제로 취약한 sink 에 도달**해야
탐지합니다. 즉 /api/equipment 의 SQL 쿼리가 실제로 실행되어야 하므로,
컨테이너 기동 전에 DB 와 테이블이 준비되어 있어야 합니다.

main.py 와 분리한 이유: main.py 는 SAST 실측 결과(line 28/39/47/56/64/81)의
기준 파일이라 한 줄이라도 바뀌면 매핑표가 어긋납니다. 그래서 건드리지 않습니다.
"""

import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DB_PATH

SEED = [
    ("GT-1호기", "정상"),
    ("GT-2호기", "점검중"),
    ("ST-1호기", "정상"),
    ("HRSG-1", "경고"),
    ("BOP-펌프A", "정상"),
]


def init_db(path=DB_PATH):
    parent = os.path.dirname(path)
    try:
        os.makedirs(parent, exist_ok=True)
    except OSError:
        path = "/tmp/equipment.db"
        print(f"[db_init] {parent} 생성 실패 → {path} 로 대체", flush=True)

    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS equipment ("
        " id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " name TEXT NOT NULL,"
        " status TEXT NOT NULL,"
        " plant TEXT NOT NULL)"
    )
    cur.execute("SELECT COUNT(*) FROM equipment")
    if cur.fetchone()[0] == 0:
        for i, (name, status) in enumerate(SEED):
            cur.execute(
                "INSERT INTO equipment (name, status, plant) VALUES (?, ?, ?)",
                (name, status, "A1" if i % 2 == 0 else "B2"),
            )
    conn.commit()
    conn.close()
    print(f"[db_init] 준비 완료: {path}", flush=True)
    return path


if __name__ == "__main__":
    init_db()
