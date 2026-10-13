"""Probe challenge_state.sqlite3 schema/states plus run bookkeeping tables."""
import sqlite3
import sys

DB = r"E:\华为杯\AGENT\ctf-agent\.runtime\challenge_state.sqlite3"
c = sqlite3.connect(DB)
c.row_factory = sqlite3.Row
tables = [r[0] for r in c.execute("select name from sqlite_master where type='table'")]
print("TABLES:", tables)
print("challenges cols:", [r[1] for r in c.execute("pragma table_info(challenges)")])
print()
print("states:", dict(c.execute("select state, count(*) from challenges group by state").fetchall()))
print()
for r in c.execute("select name, state, coalesce(reason,'') as reason from challenges order by state, name"):
    print(f"{r['state']:<26} {r['name'][:44]:<46} {r['reason'][:50]}")
for t in tables:
    if t != "challenges":
        try:
            cols = [r[1] for r in c.execute(f"pragma table_info({t})")]
            n = c.execute(f"select count(*) from {t}").fetchone()[0]
            print(f"\n[t] {t} ({n} rows) cols={cols}")
            for row in c.execute(f"select * from {t} limit 8"):
                print("   ", dict(row))
        except Exception as exc:  # noqa: BLE001
            print(t, "ERR", exc)
sys.exit(0)
