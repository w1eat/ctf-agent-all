---
title: PostgreSQL 布尔注入识别
source_challenge: Planetary Probe analysis notes
verification_status: pending
---

# PostgreSQL 布尔注入识别

关键词：PostgreSQL、Postgres、pgsql、SQL injection、布尔注入、布尔盲注、boolean blind SQL injection、true/false oracle。

当输入会影响数据库谓词，却没有直接显示查询结果时，先观察一个可控条件为真和为假时的响应差异。可比较状态码、结果数量、固定错误文本或页面结构；重复基线和对照试验，避免把网络波动或缓存误认为 oracle。数据库类型必须由报错、语法响应或其他独立线索支持，不应只凭题目描述猜测。

适用条件：输入确实进入 SQL 上下文；真假两类响应可重复区分；比较指标不依赖偶发超时。若条件不可稳定区分，先继续确认注入点和响应路径。

验证状态：待验证。此卡来自保存的 Planetary Probe 分析线索；本地记录没有平台确认或独立成功证据。
