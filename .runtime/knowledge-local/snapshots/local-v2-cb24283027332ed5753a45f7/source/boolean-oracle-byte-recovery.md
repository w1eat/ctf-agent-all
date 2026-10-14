---
title: 布尔 oracle 的逐字节恢复
source_challenge: Planetary Probe analysis notes
verification_status: pending
---

# 布尔 oracle 的逐字节恢复

关键词：布尔盲注、boolean oracle、逐字节恢复、byte by byte、ASCII、substring、二分查找、PostgreSQL、pgsql。

在真假 oracle 稳定后，先确定目标长度，再对每个位置测试字符区间。对有序的字节或字符编码范围，可用二分条件减少请求次数；对 Unicode 文本应先明确编码和位置函数的语义。每次恢复要重复关键比较并记录置信度，避免一个误判使后续字符全部偏移。

适用条件：有稳定、可重复的布尔响应；目标表达式可按位置访问；请求成本与长度可接受。恢复前先用已知的无敏感文本验证位置从何处开始、空值如何表现以及大小写和编码的处理。

验证状态：待验证。此卡记录通用恢复思路，不包含原题数据或结果。
