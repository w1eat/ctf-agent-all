# ghost in the thread - 3 题解

- 分类：Forensics
- 确认方式：平台确认
- 复现状态：人工复现


## 题目信息

a week ago moot went on vacation, someone leaked where, but thankfully our faithful, unpaid janitors cleaned it up. where'd moot go on vacation to? refer to ghost in the thread (1) for the challenge. no sun{} format, just the location name. Companion file: sunchan3.html (sha256 d907888689e16f97d624734354ccc33705dc1f7cb50f7092b149478f5c7f478e, 40034 bytes).

## 解题原理

本题为一道取证（Forensics）题，核心是虚拟机镜像中的 SQLite WAL 残留数据恢复。题目设定 SunChan 论坛（/po/ 版）的管理员（材料中称为 janitor/版主）删除了泄露 moot 度假地点的帖子；虽然主数据库 board.sqlite 中的记录行已被删除，但由于 SQLite 采用预写日志（WAL）模式，被删除的页镜像仍残留在 board.sqlite-wal 中，因此可以通过提取并扫描 WAL 内容恢复被删帖子的正文，得到泄露信息。此外，OVAl 内的 VMDK 是 streamOptimized 稀疏格式（含 grain 标记与 zlib 压缩），需要先解析还原为 raw 镜像才能做文件系统取证。

## 关键步骤

1. 从题目给出的 Google Drive 链接下载 GhostInTheThread.ova（大文件需按平台要求完成 confirm/uuid 二次确认）。
2. 解包 OVA 得到 GhostInTheThread-disk1.vmdk（2 GiB streamOptimized 稀疏盘，magic KDMV、compress=1、含 grain 标记）。由于 7z/qemu-img 不可用，自行编写 vmdk2raw.py：按 GD/GT 定位每个 grain，grain 起始为 12 字节 marker（uint64 LBA + uint32 zlib 压缩长度），随后是 zlib 流；逐个解压共 3596 个非零 grain，还原出 disk.raw（2 GiB）。
3. 用 mmls 解析 GPT，确认根 ext4 分区起始扇区为 135168。
4. 用 fls -o 135168 disk.raw 列出文件，找到 /var/lib/sunchan/board.sqlite（inode 65421）、board.sqlite-wal（inode 65420）以及 /srv/sunchan/uploads/po/184726.pdf（892 B，PostScript）；用 icat 提取这些文件。
5. 检查 board.sqlite 的 moderation_actions 表：记录显示 board 为 'po' 的 16 个帖子在 2026-08-07 被以理由 'off-topic or sensitive information' 删除（post id 183901..183989）。这些行在主库中已不存在，但仍残留在 board.sqlite-wal 的页镜像中。
6. 扫描/枚举 WAL 页镜像恢复被删正文（材料中对应 wal_recover.py），得到唯一泄露帖：2026-08-07T15:42:19Z 'I HAVE PROOF THAT MOOT WENT TO MOOTXICO'，即 moot 的度假地点为 mootxico。
7. 在平台提交全小写 'mootxico'，页面返回 Correct，题目显示 Solved（材料记录 164 solves、已解 24/37，flag 由平台确认）。注意 'Mootxico' 混合大小写与 'Mexico' 均被判定为 Incorrect。

## EXP 与运行方法

文件：无

材料未保存任何 EXP 文件（exp_files 为空），replay.status 为 manual，因此没有可自动运行的脚本。人工复现方式为：下载并解包 OVA，用自写的 vmdk2raw.py 将 streamOptimized VMDK 逐 grain 解压还原成 disk.raw，再用 mmls/fls/icat 从 ext4 分区（起始扇区 135168）提取 board.sqlite 与 board.sqlite-wal，最后扫描 WAL 页镜像恢复被删帖正文得到 'mootxico'，并在平台手动提交该全小写字符串。

## 验证结果

没有可自动运行的 EXP；请按题解步骤人工复现。

证据：

- metadata.yml: native_id 30, name 'ghost in the thread - 3', challenge_url https://2026.sunshinectf.org/challenges#ghost%20in%20the%20thread%20-%203-30
- Google Drive link resolves to GhostInTheThread.ova (tar, 126,945,280 B) containing GhostInTheThread-disk1.vmdk (2 GiB streamOptimized sparse extent, magic KDMV, compress=1, flags=0x30003 / has grain markers)
- Wrote a parser (vmdk2raw.py): each grain at GTE sector starts with a 12-byte marker (uint64 LBA + uint32 zlib length) then a zlib stream; decoded all 3596 non-zero grains into disk.raw (2 GiB)
- GPT disk: root ext4 partition starts at sector 135168 (mmls); fls -o 135168 disk.raw lists /var/lib/sunchan/board.sqlite (inode 65421) + board.sqlite-wal (65420) and /srv/sunchan/uploads/po/184726.pdf (892 B, PostScript)
- board.sqlite moderation_actions shows 16 posts on board 'po' deleted 2026-08-07 with reason 'off-topic or sensitive information' (ids 183901..183989); the deleted rows no longer exist in the main DB but survive in board.sqlite-wal
- wal_recover.py enumerates the WAL page images and prints the deleted bodies; the only leak is 2026-08-07T15:42:19Z 'I HAVE PROOF THAT MOOT WENT TO MOOTXICO'
- Platform: submitting 'mootxico' on challenge #30 returned alert 'Correct'; challenge list then showed 'ghost in the thread - 3 ✦ Solved 467 164 solves' (solved 24/37)
- Note: 'Mootxico' (mixed case) was Incorrect and 'Mexico' was Incorrect; the accepted flag is the all-lowercase 'mootxico'

## Flag

`mootxico`

## 限制与备注

依据现有证据，本题复现依赖以下条件：需要能下载并解包约 127 MB 的 OVA，并具备解析 streamOptimized VMDK grain/zlib 结构的能力（材料中因 7z/qemu-img 不可用而自行实现 parser）；需要 mmls/fls/icat 等 Sleuth Kit 类工具；需要自行编写或使用 WAL 页扫描脚本（材料未提供该脚本文件）。平台确认信息来自材料记录，本次未重新执行任何命令验证。另需注意 flag 大小写敏感：仅全小写 'mootxico' 被平台接受，'Mootxico' 与 'Mexico' 均被判定为错误。
