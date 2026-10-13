"""Offline labeled retrieval check for the Des-CTF-Knowledge snapshot."""

from __future__ import annotations

import json
import platform
import statistics
import time
from types import SimpleNamespace

from backend.config import Settings
from backend.external_knowledge import ExternalKnowledge
from backend.knowledge import KnowledgeStore
from backend.knowledge_service import KnowledgeService
from backend.local_knowledge import LocalKnowledge

CASES = [
    ("联合注入 查字段", "SQL.md"),
    ("报错注入 updatexml", "SQL.md"),
    ("堆叠注入 SQL", "SQL.md"),
    ("宽字节 GBK 注入", "SQL.md"),
    ("二次注入 SQL", "SQL.md"),
    ("DNS注入 SQL", "SQL.md"),
    ("无回显 命令执行", "命令执行.md"),
    ("disable_functions 绕过", "命令执行.md"),
    ("反弹shell 命令执行", "命令执行.md"),
    ("无字母 命令执行", "命令执行.md"),
    ("MIME 文件上传 绕过", "文件上传漏洞.md"),
    ("htaccess 文件上传", "文件上传漏洞.md"),
    ("图片马 文件上传", "文件上传漏洞.md"),
    ("php伪协议 文件包含", "文件包含.md"),
    ("日志包含 LFI", "文件包含.md"),
    ("session包含 文件包含", "文件包含.md"),
    ("SSRF gopher redis", "SSRF漏洞.md"),
    ("SSRF fastcgi", "SSRF漏洞.md"),
    ("SSRF DNS-rebinding", "SSRF漏洞.md"),
    ("POP链 PHP反序列化", "PHP反序列化漏洞总结.md"),
    ("__wakeup 反序列化 绕过", "PHP反序列化漏洞总结.md"),
    ("SoapClient PHP反序列化", "PHP反序列化漏洞总结.md"),
    ("Jinja2 subclasses SSTI", "SSTI.md"),
    ("JWT KID 注入", "JWT.md"),
    ("PNG IHDR CRC 图片宽高", "图片隐写.md"),
    ("ZIP 伪加密 压缩包", "压缩包总结.md"),
    ("DTMF 音频隐写", "音频隐写.md"),
    ("PHP 弱类型 strcmp 代码审计", "php代码审计.md"),
    ("XSS payload 速查", "PAYLOAD-CHEATSHEET.md"),
    ("sqlmap 参数 速查", "工具使用/sqlmap-Cheat-Sheet.md"),
]
NEGATIVE = ["完全不存在的随机术语 qxjvzp", "银河花园量子猫 938271", "unrelated-nonsense-token-8493"]
STRESS_CASES = [
    ("宽字节 GBK 注入 " + " ".join(f"zznoise{index:02d}" for index in range(16)), "SQL.md"),
    (" ".join(f"zznoise{index:02d}" for index in range(64)) + " 宽字节 GBK 注入", "SQL.md"),
]
PLANETARY_CASES = [
    ("PostgreSQL boolean injection oracle", "knowledge/local/postgresql-boolean-injection.md"),
    ("pgsql 布尔盲注 真假响应", "knowledge/local/postgresql-boolean-injection.md"),
    ("pg_has_role pg_execute_server_program 角色成员", "knowledge/local/postgresql-role-program-privileges.md"),
    ("COPY TO PROGRAM 退出状态 oracle", "knowledge/local/postgresql-copy-program-oracle.md"),
    ("server-side program exit status", "knowledge/local/postgresql-copy-program-oracle.md"),
    ("布尔 oracle 逐字节恢复 byte by byte", "knowledge/local/boolean-oracle-byte-recovery.md"),
]


def main() -> None:
    source = ExternalKnowledge(Settings().external_knowledge_dir)
    if not source.available:
        raise SystemExit("No local knowledge snapshot; run ctf-knowledge sync first")
    settings = SimpleNamespace(external_knowledge_enabled=True,
                               external_knowledge_dir=str(source.root), challenge_run_id="",
                               external_knowledge_context_items=4, external_knowledge_context_chars=4000)
    service = KnowledgeService(settings, KnowledgeStore(".runtime/evaluation-memory.sqlite3", enabled=False))
    service.external = source
    service.local = LocalKnowledge()
    if not service.local.available:
        raise SystemExit("No curated local snapshot; run ctf-knowledge index-local first")
    misses = []
    unified_misses = []
    times = []
    for query, expected in CASES:
        began = time.perf_counter()
        hits = source.search(query, limit=5)
        times.append((time.perf_counter() - began) * 1000)
        if not any(hit["path"] == expected for hit in hits):
            misses.append({"query": query, "expected": expected, "actual": [hit["path"] for hit in hits]})
        unified = service.search(query, limit=5)
        if not any(hit["path"] == expected for hit in unified):
            unified_misses.append({"query": query, "expected": expected,
                                   "actual": [hit["path"] for hit in unified]})
    negatives = [query for query in NEGATIVE if source.search(query, category="web")]
    unified_negatives = [query for query in NEGATIVE if service.search(query, category="web")]
    stress_misses = []
    unified_stress_misses = []
    for query, expected in STRESS_CASES:
        hits = source.search(query, limit=5)
        if not any(hit["path"] == expected for hit in hits):
            stress_misses.append({"expected": expected, "actual": [hit["path"] for hit in hits]})
        unified = service.search(query, limit=5)
        if not any(hit["path"] == expected for hit in unified):
            unified_stress_misses.append({"expected": expected,
                                          "actual": [hit["path"] for hit in unified]})
    planetary_misses = []
    for query, expected in PLANETARY_CASES:
        hits = service.search(query, limit=5)
        if not any(hit["path"] == expected for hit in hits):
            planetary_misses.append({"query": query, "expected": expected,
                                     "actual": [hit["path"] for hit in hits]})
    # A second pass measures warm-cache latency separately from first-query work.
    warm = []
    for _ in range(4):
        for query, _ in CASES:
            began = time.perf_counter()
            source.search(query, limit=5)
            warm.append((time.perf_counter() - began) * 1000)
    p95 = sorted(warm)[int(len(warm) * 0.95) - 1]
    cold_p95 = sorted(times)[int(len(times) * 0.95) - 1]
    print(json.dumps({"snapshot": source.snapshot_id, "local_snapshot": service.local.snapshot_id,
                      "documents": source.status()["documents"],
                      "machine": platform.platform(), "queries": len(CASES),
                      "hit_at_5": (len(CASES) - len(misses)) / len(CASES),
                      "stress_hit_at_5": (len(STRESS_CASES) - len(stress_misses)) / len(STRESS_CASES),
                      "cold_mean_ms": round(statistics.mean(times), 2),
                      "cold_p95_ms": round(cold_p95, 2), "warm_p95_ms": round(p95, 4),
                      "negative_false_positives": negatives, "misses": misses,
                      "stress_misses": stress_misses,
                      "unified_hit_at_5": (len(CASES) - len(unified_misses)) / len(CASES),
                      "unified_stress_hit_at_5": (len(STRESS_CASES) - len(unified_stress_misses)) / len(STRESS_CASES),
                      "unified_negative_false_positives": unified_negatives,
                      "unified_misses": unified_misses,
                      "unified_stress_misses": unified_stress_misses,
                      "planetary_hit_at_5": (len(PLANETARY_CASES) - len(planetary_misses)) / len(PLANETARY_CASES),
                      "planetary_misses": planetary_misses}, ensure_ascii=True, indent=2))


if __name__ == "__main__":
    main()
