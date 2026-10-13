"""List active/completed runs from the coordinator state DB."""
import sqlite3

DB = r"E:\华为杯\AGENT\ctf-agent\.runtime\challenge_state.sqlite3"
c = sqlite3.connect(DB)
cols = [r[1] for r in c.execute("PRAGMA table_info(runs)").fetchall()]
print("runs columns:", cols)
rows = c.execute("select * from runs order by rowid desc limit 40").fetchall()
for r in rows:
    print(dict(zip(cols, r)))
