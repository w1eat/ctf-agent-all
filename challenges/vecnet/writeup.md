# Vecnet 题解

- 分类：misc
- Flag：**sun{k33p_your_emb3ddings_secur3!}**
- 本地证据：归档已在线重取并用解出的密码成功解密；用户反馈平台已显示解出。
- 平台关联：旧求解轨迹的提交确认被互相冲突的页面提示拦截，无法证明队伍平台上的成功提交对应哪一次本地尝试。

## 题目信息

VecNet 是一个使用向量数据库和文本嵌入的语义邮件防护服务。解题线索分散在站点 Git 历史、MailHog 邮件和暴露的 ChromaDB 中。

## 解题原理

先从公开的 .git 历史找回被撤销的服务配置和 fetch.php 逻辑，进而定位 MailHog 与 ChromaDB。MailHog 中的邮件给出 vec2text 反演参数；ChromaDB 的 VecNetDB 集合则保存了密码规则的嵌入、该密码的 SHA-256，以及固定后缀。对规则嵌入做文本反演，结合邮件中的参数得到密码格式；再用已知 SHA-256 验证候选密码。恢复的密码可解开 specs.7z，归档中的 flag.txt 给出 Flag。

## 关键步骤

1. 检查站点公开的 Git 元数据（例如 /.git/HEAD、/.git/logs/HEAD），还原提交历史及对象。历史记录显示服务配置曾被提交后撤销；另一个提交中的 fetch.php 注释说明了精确的内部归档 URL。不要把历史配置中与解题无关的服务密钥复制到题解。
2. 阅读 fetch.php，确认它只接受特定 URL，并允许取回 /files/specs.7z。通过 fetch.php?url=http://localhost/files/specs.7z 下载加密归档。
3. 从被撤销的配置和邮件线索定位 MailHog（端口 8025）及 ChromaDB（端口 8000）。在 ChromaDB 的 default_tenant/default_database 下列出集合，找到 VecNetDB，读取其 ids、documents 与 embeddings。
4. VecNetDB 中 user_hash_sha256 保存 SHA-256：d8dd241199d2617765d7613fdd1df5358297b55f258647fe463de586bbfe3ebf；magic_string 保存固定后缀 sunshinectf8_；user_password_requirements 只有嵌入，没有明文。MailHog 邮件给出 vec2text 参数 num_steps=4、sequence_beam_width=5。
5. 使用邮件中指定的 jxm/gtr__nq__32 模型反演 user_password_requirements 嵌入。反演句意为“用户名字和姓氏的首字母，后接三个特殊字符，再接 magic string”。账户名 Greg Roberts 给出前缀 GR。
6. 依据这个规则，以 SHA-256 模式验证密码。Hashcat 示例：

~~~sh
hashcat -m 1400 -a 3 hash.txt -1 '?l?u' -2 '?s' '?1?1?2?2?2sunshinectf8_'
~~~

该掩码命中 GR$*#sunshinectf8_，其 SHA-256 与数据库记录一致。
7. 用该密码解开 specs.7z。归档仅含 flag.txt，内容为上方 Flag。

## EXP 与运行方法

文件：exp/recover.py

脚本从题目 fetch.php 下载归档并打印 flag.txt。需要 Python 3.10+ 和 py7zr；把恢复出的归档密码作为参数传入：

~~~powershell
python exp/recover.py --password 'GR$*#sunshinectf8_'
~~~

该脚本复现归档下载和解密；嵌入反演与哈希掩码验证仍需按关键步骤单独完成。在线复核结果：归档为 186 字节，解密得到 flag.txt（34 字节）；明文 SHA-256 为 531de226b28e3662ba5572972e74b62aae23c1e39edc6441b43dc9de114423a6。

## 验证结果

通过题目在线端点重新获取归档，用 py7zr 以恢复出的密码解密，成功读出与 Flag 字符串一致的文件内容。用户报告队伍平台显示此题已解；旧 Agent 轨迹的提交确认因页面同时出现 Incorrect 提示而失败，因此这里不声称这次本地提交就是平台的成功提交。
