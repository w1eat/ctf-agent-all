"""Mark one or more native challenge ids as needs_input so the spawner never re-queues them.

Usage: python mark_needs_input.py <native_id> [<native_id> ...]
"""
import sqlite3
import sys

DB = r"E:\华为杯\AGENT\ctf-agent\.runtime\challenge_state.sqlite3"

ids = sys.argv[1:]
if not ids:
    print("usage: mark_needs_input.py <native_id> ...")
    sys.exit(1)

c = sqlite3.connect(DB)
for native_id in ids:
    cur = c.execute(
        "update challenges set state='needs_input', reason=? where native_id=?",
        ("coordinator: platform-accepted solve; do not respawn", native_id),
    )
    print(native_id, "rows:", cur.rowcount)
c.commit()
print("states:", dict(c.execute("select state, count(*) from challenges group by state").fetchall()))
