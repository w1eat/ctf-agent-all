---
title: PostgreSQL 角色成员关系与程序执行权限
source_challenge: Planetary Probe analysis notes
verification_status: pending
---

# PostgreSQL 角色成员关系与程序执行权限

关键词：PostgreSQL、Postgres、pgsql、角色成员、role membership、pg_roles、pg_has_role、pg_execute_server_program、server-side program。

在考虑服务器侧程序功能前，先区分当前数据库角色、成员关系和该功能所需权限。角色名称或错误提示只是线索；应通过可观察的权限检查结果确认是否具备执行能力。把数据库权限与操作系统进程权限分开记录，避免把能够构造 SQL 语句误判为能够运行服务器程序。

适用条件：已确认目标是 PostgreSQL，并且有可靠途径查询角色或权限谓词。权限不足时，后续程序执行 oracle 不适用。

验证状态：待验证。此卡是通用检查顺序，不代表 Planetary Probe 已通过权限验证。
