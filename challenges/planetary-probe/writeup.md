# Planetary Probe 题解

- 分类：web
- 题目地址：<https://planetary.web.2026.sunshinectf.games/>
- Flag：`sun{bl1nd_psqli_2_rc3_p4Nd0FyZt8k2}`
- 复现状态：EXP 已在题目在线端点完整运行并恢复出 Flag。

## 题目信息

探测器只返回 carrier 或 null 两种状态，不回显查询结果。关键入口是 `/probe` 的 `planet` 参数。

## 解题原理

`planet` 参数存在 PostgreSQL SQL 注入。输入 `MARS' AND 1=1--` 返回 carrier，`MARS' AND 1=2--` 返回 null，因此该接口可以作为一位布尔 oracle。

数据库用户 `probe` 不是 superuser，`pg_read_file('/etc/passwd')` 也不可用；但它属于 PostgreSQL 预定义角色 `pg_execute_server_program`。这项权限允许 SQL 执行 `COPY ... TO PROGRAM`。因此不能只根据 `rolsuper=false` 就断定服务器端程序执行不可用。

注入还允许堆叠语句。`COPY (SELECT 1) TO PROGRAM 'true'` 成功时页面返回 carrier；换成会以非零状态退出的程序时，COPY 报错，页面返回 null。于是可以让服务器端 shell 检查 `/flag.txt` 的指定字节，并把进程退出状态变成布尔 oracle。整个利用只读取文件，不需要创建或修改数据库表。

EXP 对每个偏移使用 `head`/`tail` 取一个字节，通过 shell `printf` 将字节转成数值，再用 `test -gt` 做二分。每个字符确认后继续读下一位，直到取到闭合花括号。用数值比较可以避免不同 locale 下对下划线等字符排序不一致的问题。

## 关键步骤

1. 确认布尔 SQL 注入：

   ```text
   /probe?planet=MARS' AND 1=1--
   /probe?planet=MARS' AND 1=2--
   ```

   前者显示 carrier，后者显示 null。

2. 确认 PostgreSQL 角色权限：

   ```sql
   SELECT current_user;
   SELECT rolsuper FROM pg_roles WHERE rolname = current_user;
   SELECT pg_has_role(current_user, 'pg_execute_server_program', 'member');
   ```

   当前用户为 `probe`，`rolsuper` 为 false，但 `pg_execute_server_program` 成员检查为 true。

3. 验证 `COPY TO PROGRAM` 的退出状态可作为 oracle。概念 payload 如下；实际请求由 EXP 负责 URL 编码和 SQL 字符串转义：

   ```sql
   MARS'; COPY (SELECT 1) TO PROGRAM 'true'; SELECT 1;--
   ```

   成功时 `SELECT 1` 提供一行，页面显示 carrier；若程序非零退出，COPY 失败，页面显示 null。

4. 利用 shell 对 `/flag.txt` 做逐字节数值比较，通过布尔二分恢复文件开头的 Flag。文件内容较大，但恢复在闭合 `}` 处停止。

## EXP 与运行方法

文件：`exp/exp.py`

需要 Python 3 和 `requests`：

```powershell
python -m pip install requests
python challenges\planetary-probe\exp\exp.py
```

可用 `--url` 指定题目地址、`--delay` 调整串行请求间隔，或用 `--max-length` 设置最大 Flag 长度。脚本默认使用题目地址，串行发送请求；不会并发探测，也不会在数据库中留下表或记录。

## 验证结果

EXP 完整运行成功，239 次 oracle 请求恢复出：

```text
sun{bl1nd_psqli_2_rc3_p4Nd0FyZt8k2}
```

此前 trace 中的 `public.zleak` 只有一行，内容是 `select v from zleak`，属于诱饵，不是 Flag。失败尝试把“不是 superuser”错误地当成“没有 COPY PROGRAM 权限”，并把 `zleak` 的长度误判为 Flag 线索。
