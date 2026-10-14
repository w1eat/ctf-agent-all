---
title: COPY TO PROGRAM 退出状态 oracle
source_challenge: Planetary Probe analysis notes
verification_status: pending
---

# COPY TO PROGRAM 退出状态 oracle

关键词：PostgreSQL、pgsql、COPY TO PROGRAM、COPY FROM PROGRAM、server-side program、exit status、退出状态 oracle。

如果环境允许服务器侧程序调用，某些调用失败会使数据库错误包含进程退出状态。将待判断条件映射到不同退出状态，再观察应用是否稳定暴露这一区别，可把错误通道用作布尔 oracle。先以无敏感数据的真假对照验证状态传播，再考虑任何数据恢复。

适用条件：当前角色确有相应权限；注入上下文允许该语句形式；应用保留可区分的错误信息；服务器执行环境与外部输入的引用规则已被验证。`COPY FROM PROGRAM` 与 `COPY TO PROGRAM` 的数据流方向不同，应分别确认语句和权限，不可互换推断。

验证状态：待验证。此卡描述可能的判别路径，不声称原题已执行成功。
