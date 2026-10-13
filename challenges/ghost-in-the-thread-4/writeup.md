# ghost in the thread - 4 题解

- 分类：Forensics
- 确认方式：平台确认
- 复现状态：人工复现


## 题目信息

A backdoored password was planted, what is it? refer to ghost in the thread (1) for the challenge. No sun{} flag format, just the password. Companion file: sunchan4.html (sha256 d907888689e16f97d624734354ccc33705dc1f7cb50f7092b149478f5c7f478e, 40034 bytes).

## 解题原理

本题是一道虚拟机取证题。出题者在 SunshineCTF 的 GhostInTheThread OVA 里通过 provisioning 的 rootfs-overlay 覆盖了 /usr/lib/security/pam_unix.so，用一个伪造的小型 PAM 模块替换了真实模块。该假模块在 .rodata 中导出两个全局对象符号：artifact_description（伪装成正常的构建产物描述 "Linux-PAM authentication module build artifact"）和 configured_password，后者直接以明文存放被植入的后门密码。因此解题原理是：先由 sunchan4.html 离线快照中唯一渲染异常的附件定位到 VM 的上传目录线索，再对 OVA 内的 ext4 根分区做文件级取证，提取伪造的 pam_unix.so 并解析其符号表，读出 configured_password 得到后门密码。

## 关键步骤

1. 检查 distfiles/sunchan4.html 离线快照：184726 号帖子的 folding-guide.pdf 标注为 "Attachment stored on the server" 且预览为空，是唯一异常附件，指向 VM 内的上传存放位置（相关佐证为 /home/hiro/todo.txt 中 "figure out why that one upload isnt rendering"）。
2. 从题面提示的 Google Drive 链接获取 GhostInTheThread.ova（POSIX tar，126,945,280 字节），解包得到 GhostInTheThread-disk1.vmdk（VMware4/streamOptimized，虚拟盘 2 GiB）。
3. 在无 qemu-img 的情况下，直接用链接了 libvmdk 的 Sleuth Kit 读取 VMDK：mmls 显示 GPT 分区表中 002 槽为 ext4 根分区，起始扇区 135168；再用 fls -i vmdk -o 135168 -r 递归列出文件系统内容。
4. 在文件列表中定位 usr/lib/security/pam_unix.so（inode 3195，13912 字节），其体积与同目录其它 PAM 模块（约 14096 字节）相近但内容可疑，使用 icat -i vmdk -o 135168 <vmdk> 3195 将其导出。
5. 对导出的模块做符号与数据解析：readelf -s 可见 GLOBAL OBJECT 符号 artifact_description（0x2000，47 字节）与 configured_password（0x2030，18 字节）；objdump -s -j .rodata（或 strings）在 0x2030 处读出字节 sneedsfeedandseed\x00，即 configured_password 的值。
6. 用 blkls | strings 扫描未分配空间，还原构建脚本 provision.sh：它执行 cp -a "$payload/rootfs-overlay/." /，把 overlay 覆盖到根文件系统，证实该 pam_unix.so 是被 overlay 植入的假 PAM 模块，密码即其 configured_password。
7. 结论：后门密码为 sneedsfeedandseed，非 sun{} 格式，符合题面要求。

## EXP 与运行方法

文件：无

材料中未提供任何可运行的 EXP 文件（exp_files 为空），replay.status 为 manual，因此只能按上述步骤人工复现，不能声称已自动复现。人工复现使用的核心命令序列为：先解包 OVA 得到 GhostInTheThread-disk1.vmdk；再执行 mmls -i vmdk GhostInTheThread-disk1.vmdk 确认 ext4 根分区起始扇区 135168；用 fls -i vmdk -o 135168 -r 列出文件；用 icat -i vmdk -o 135168 GhostInTheThread-disk1.vmdk 3195 导出 usr/lib/security/pam_unix.so；最后用 readelf -s 与 objdump -s -j .rodata（或 strings）读出符号 configured_password 的明文值 sneedsfeedandseed。

## 验证结果

没有可自动运行的 EXP；请按题解步骤人工复现。

证据：

- sunchan4.html post No.184726 alone marks its attachment 'Attachment stored on the server' with a blank preview (post 184733), pointing to the VM's upload store; /home/hiro/todo.txt reads 'figure out why that one upload isnt rendering'.
- Google Drive link 1fFWJp6tfT8U6bh0uuhB4AkDv-sdDCf_W resolves to GhostInTheThread.ova (tar, 126,945,280 bytes) containing GhostInTheThread-disk1.vmdk (VMware4/streamOptimized, 2 GiB virtual).
- mmls on the VMDK: GPT with slot 002 ext4 '/' starting at sector 135168 (fls/-r yields etc, home, srv, usr, var, ...).
- allfiles.txt lists `r/r 3195: usr/lib/security/pam_unix.so` (13912 bytes) vs sibling PAM modules ~14096 bytes; `readelf -s pam_unix.so` shows GLOBAL OBJECT symbols `artifact_description` (0x2000,47) and `configured_password` (0x2030,18).
- objdump -s -j .rodata shows at 0x2030 the bytes 'sneedsfeedandseed\x00' = configured_password = '[已脱敏]]'.
- Unallocated-space dump (blkls | strings) recovers the build provisioning script proving the plant: it copies `$payload/rootfs-overlay/. /` over the rootfs, which is where the fake pam_unix.so is installed; the same payload.tar listing contains 'rootfs-overlay','security','pam_unix.so'.
- Independently, the same VM's dropped stage-2 ELF (/var/tmp/sunchan-downloads/gs-resource.bin, sha256 3cf1f62fe43202b9d0fc1ded2776fe7d40001d3fd6c8d23b53550d8edf0f3500) fed with the PostScript Document-ID 'po-184726' prints `sun{tfw_hacked_by_offboarders}` (a separate sub-task flag, not the backdoor password).
- Platform limitation: submit_flag repeatedly returns `browser_click failed: button.challenge-button[value="{challenge_id}"] does not match any elements` for ANY value (tested with two different candidates), i.e. the submission recipe/selector is broken, so no server-side confirmation is obtainable.

## Flag

`sneedsfeedandseed`

## 限制与备注

1) 没有保存可自动执行的 EXP，replay.status 为 manual，复现完全依赖人工按步骤操作。2) 读取 VMDK 依赖 Sleuth Kit 且需链接 libvmdk，环境不具备该能力时无法直接解析 streamOptimized 格式；材料记录了因无 qemu-img 而改用该方案的场景。3) 定位关键证据依赖两处线索（HTML 附件异常与 todo.txt 提示）以及 VM 内 post 184733 的佐证，线索缺失时难以独立定位 pam_unix.so。4) 材料中另有一处独立结果：同一 VM 中落地的二阶段 ELF /var/tmp/sunchan-downloads/gs-resource.bin（sha256 3cf1f62fe43202b9d0fc1ded2776fe7d40001d3fd6c8d23b53550d8edf0f3500）配合 PostScript Document-ID "po-184726" 会输出 sun{tfw_hacked_by_offboarders}，这是另一个子任务的 flag，不是本题要的后门密码，不应混淆。5) 题面仅要求密码本身、不使用 sun{} 格式，因此不能把上述 sun{} 值当作本题答案。6) 材料标注 confirmation_source 为 platform_confirmed，但同一份证据中又记录了 submit_flag 对任意候选值均报 browser_click failed、按钮选择器匹配不到元素，即提交环节本身异常；关于平台是否实际接受该值，依据现有证据存在矛盾，无法在本说明中进一步确认。
