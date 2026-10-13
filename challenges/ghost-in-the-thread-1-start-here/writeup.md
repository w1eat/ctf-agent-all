# ghost in the thread - 1 - start here 题解

- 分类：Forensics
- 确认方式：平台确认
- 复现状态：自动复现通过


## 题目信息

>be moot >never update >get pwned >mfw https://drive.google.com/file/d/1fFWJp6tfT8U6bh0uuhB4AkDv-sdDCf_W/view?usp=sharing (use virtual machine / sandbox). Part 1 of 4 - start here. Attached: sunchan.html. External imagepack on Google Drive.

## 解题原理

本题是取证类多阶段（Part 1/4）题目链的第一环，核心原理是：镜像中一个被伪装成 PDF 的上传文件实为 PostScript 文件，其 %% 注释携带第二阶段投递元数据，而投递下来的静态 ELF 会依据 Document-ID 通过 FNV-1a 校验后异或生成 Flag。具体地，论坛快照 sunchan.html 中的 /po/ 板块，帖子 No.184726 的附件 folding-guide.pdf 是唯一标注“存储于服务器”且预览为空的附件（帖子 184733 描述预览为空），/home/hiro/todo.txt 也提示某个上传无法渲染，这构成异常入口。磁盘镜像 /srv/sunchan/uploads/po/184726.pdf 经 file 判定为 'PostScript document text conforming DSC level 3.0'，其中 %%Document-ID: po-184726、%%Stage2-URL-Base64（解出 http://assets.sunchan.invalid/resources/gs-resource.bin）、%%Stage2-Destination: /var/tmp/sunchan-downloads/gs-resource.bin、%%Stage2-SHA256: 3cf1f62fe43202b9d0fc1ded2776fe7d40001d3fd6c8d23b53550d8edf0f3500 给出完整的第二阶段投递参数。落地文件 gs-resource.bin 的 SHA-256 与元数据一致，是静态 stripped ELF（自称 'SunHash proof-of-work benchmark simulator (offline)'）。其反汇编逻辑为读入 9 字符 Document-ID，计算 FNV-1a（init 0x811c9dc5，prime 0x1000193）并要求 eax==0xdac3d58d，随后输出 30 字节 = input[i%9] ^ key[i] ^ 0x5a（key 为给定的 30 字节序列）。只有 po-184726 满足该哈希条件，故解码得到 Flag。

## 关键步骤

1. 下载 Google Drive 镜像包 GhostInTheThread.ova（tar 包，126,930,944 字节），解出 GhostInTheThread-disk1.vmdk（虚拟 2 GiB，GPT：EFI、BIOS、ext4 '/'）。
2. 用 qemu-img convert 将 VMDK 转为 raw 镜像；由于容器环境无法 loop mount，使用 e2fsprogs 的 debugfs 读取文件系统并 rdump 出内容。
3. 对照附件 sunchan.html：帖子 No.184726 的 'folding-guide.pdf' 是唯一『Attachment stored on the server』且预览为空（帖子 184733 描述为 blank）的附件，/home/hiro/todo.txt 也提示需查明某个上传为何不渲染。
4. 在镜像路径 /srv/sunchan/uploads/po/184726.pdf 发现该文件实为 PostScript（DSC level 3.0），其 %% 注释给出第二阶段元数据：%%Document-ID: po-184726、%%Stage2-URL-Base64（base64 解出 http://assets.sunchan.invalid/resources/gs-resource.bin）、%%Stage2-Destination: /var/tmp/sunchan-downloads/gs-resource.bin、%%Stage2-SHA256: 3cf1f62fe43202b9d0fc1ded2776fe7d40001d3fd6c8d23b53550d8edf0f3500。
5. 校验落地文件 /var/tmp/sunchan-downloads/gs-resource.bin 的 SHA-256 与元数据一致，确认它是静态 stripped ELF；反汇编可知其读入 9 字符 Document-ID，校验 FNV-1a（init 0x811c9dc5、prime 0x1000193）等于 0xdac3d58d，然后输出 30 字节 = input[i%9] ^ key[i] ^ 0x5a。
6. 以 %%Document-ID: po-184726 作为输入即可通过哈希校验；按上述公式计算（等价于运行 printf 'po-184726\n' | ./gs-resource.bin）得到 sun{tfw_hacked_by_offboarders}。
7. 提交该 Flag，平台返回 'Correct'（confirm_submission 报告 CORRECT），确认通过。
8. 已保存 EXP 为 exp/scripts/solve.py，可在沙箱内以 python3 scripts/solve.py 离线复算输出 30 字节的 Flag。

## EXP 与运行方法

文件：`exp/scripts/solve.py`

已保存 EXP 为 exp/scripts/solve.py。它不依赖镜像，而是离线复现 ELF 的生成逻辑：内置 30 字节 key 序列与输入 b'po-184726'，用 assert 校验 FNV-1a 结果等于 0xdac3d58d，再按 input[i%9] ^ key[i] ^ 0x5a 计算并打印 30 字节 Flag。运行方式为在沙箱中 cd /challenge/workspace && python3 scripts/solve.py，replay.status 为 verified，退出码 0，stdout 为 sun{tfw_hacked_by_offboarders}。若需在真实二进制上验证，等价命令为 printf 'po-184726\n' | ./gs-resource.bin（错误输入会打印 'source binding rejected'）。

## 验证结果

全新沙箱运行成功，输出与记录的 Flag 一致。

运行命令：`cd /challenge/workspace && python3 scripts/solve.py`

证据：

- sunchan.html post No.184726 attaches 'folding-guide.pdf' which alone is marked 'Attachment stored on the server' and whose preview is described as 'blank' (post 184733), while /home/hiro/todo.txt says 'figure out why that one upload isnt rendering'.
- Google Drive link resolves to GhostInTheThread.ova (tar, 126,930,944 bytes) containing GhostInTheThread-disk1.vmdk (2 GiB virtual, GPT: EFI, BIOS, ext4 '/'); qemu-img convert + e2fsprogs debugfs used to read it (loop mount unavailable).
- The on-disk upload /srv/sunchan/uploads/po/184726.pdf is actually a PostScript file (file: 'PostScript document text conforming DSC level 3.0') carrying stage-2 metadata: %%Document-ID: po-184726, %%Stage2-URL-Base64: aHR0cDovL2Fzc2V0cy5zdW5jaGFuLmludmFsaWQvcmVzb3VyY2VzL2dzLXJlc291cmNlLmJpbg== (http://assets.sunchan.invalid/resources/gs-resource.bin), %%Stage2-Destination: /var/tmp/sunchan-downloads/gs-resource.bin, %%Stage2-SHA256: 3cf1f62fe43202b9d0fc1ded2776fe7d40001d3fd6c8d23b53550d8edf0f3500.
- The dropped payload /var/tmp/sunchan-downloads/gs-resource.bin matches that SHA-256 and is a static stripped ELF ('SunHash proof-of-work benchmark simulator (offline)'). Its disassembly: reads a 9-char Document-ID, checks FNV-1a (init 0x811c9dc5, prime 0x1000193) so that eax==0xdac3d58d, then emits 30 bytes = input[i%9] ^ key[i] ^ 0x5a with key = 59 40 19 10 16 08 1a 37 04 4b 56 1c 0e 06 31 0f 11 33 45 53 11 09 0d 0f 1f 0c 09 58 46 0a.
- Only input 'po-184726' (the %%Document-ID) satisfies the FNV check. Executing the binary: `printf 'po-184726\n' | ./gs-resource.bin` prints 'Document-ID: sun{tfw_hacked_by_offboarders}', while a wrong input prints 'source binding rejected'.
- Platform submission of sun{tfw_hacked_by_offboarders} returned the page alert 'Correct' and confirm_submission reported CORRECT.

## Flag

`sun{tfw_hacked_by_offboarders}`

## 限制与备注

证据充分（confirmation_source 为 platform_confirmed，replay.status 为 verified，EXP 已在沙箱自动复现成功），但仍有若干边界需说明：一是镜像读取依赖特定环境，容器内无法 loop mount，必须改用 qemu-img convert + e2fsprogs debugfs，换环境可能需要调整；Google Drive 链接与外部 imagepack 的可获取性不由本地证据保证。二是原始题目描述中只有 sunchan.html 附件，GhostInTheThread.ova 需自行从外链下载，本材料未包含镜像本体。三是本材料只覆盖 Part 1/4 的链条（HTML 线索→上传文件→PostScript 元数据→ELF→Flag），其余 3 部分的解题依据不在本材料范围内。四是 EXP 是离线复算脚本，并不实际执行被分析的 ELF，因此它验证的是算法与输入的正确性而非二进制行为本身；如需验证二进制行为须自行在隔离虚拟机/沙箱中运行。五是被分析的 ELF 为静态 stripped 二进制，其逻辑结论来自材料给出的反汇编结果，本材料未包含完整反汇编原文。
