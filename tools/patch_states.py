"""Quick state patch: mark specific native_ids as needs_input (solved/no-respawn)."""
import sqlite3

DB = r"E:\华为杯\AGENT\ctf-agent\.runtime\challenge_state.sqlite3"
TARGETS = {
    "01a0b970-d6cf-7d1f-b267-611af8804a35": "solved 系统后门用户分析",
    "01a0bef9-c271-7b0f-b696-410b2a17ea81": "solved day3-aes",
}
c = sqlite3.connect(DB)
for native_id, reason in TARGETS.items():
    cur = c.execute(
        "update challenges set state='needs_input', reason=? where native_id=?",
        (f"coordinator: {reason}", native_id),
    )
    print(native_id, "rows:", cur.rowcount)
c.commit()
print("states:", dict(c.execute("select state, count(*) from challenges group by state").fetchall()))
