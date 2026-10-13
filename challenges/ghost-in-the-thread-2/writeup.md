# ghost in the thread - 2 题解

- 分类：Forensics
- 确认方式：平台确认
- 复现状态：人工复现


## 题目信息

ghost in the thread - 2 (Forensics). VM image: https://drive.google.com/file/d/1fFWJp6tfT8U6bh0uuhB4AkDv-sdDCf_W/view?usp=sharing (GhostInTheThread.ova).

## 解题原理

这是一道取证（Forensics）题：题目给出一份 OVA 虚拟机镜像（GhostInTheThread.ova），要求判断该镜像中 sysadmin 使用的键盘布局名称，且题目明确说明无需 sun{} 包装，直接提交布局名。核心思路是：磁盘镜像中以明文形式保存了自定义 XKB 布局文件 /usr/share/X11/xkb/symbols/custom，其中把每个物理按键（AD01、AC01、AB01 等 XKB 键位代码）映射到字母；只要把镜像转换为原始磁盘、定位 ext4 根分区、提取该文件，再按 XKB 键位约定还原出三行键盘布局，就可以与公开的键盘布局进行比对命名。该布局按 QWERTY 键序还原为 'bldcvjyou,' / 'nrtsgphaei' / 'xqmwzkf';.'，与 GalileoBlues 的 Gallium（Colstag 变体）布局逐字节一致，因此答案是 Gallium。

## 关键步骤

1. 从题目描述取得 Google Drive 链接，处理 Google Drive 的病毒扫描确认页（提取 confirm=t 与 uuid）后下载 GhostInTheThread.ova（tar 包，约 126,945,280 字节）。
2. 解包 OVA，得到 GhostInTheThread.ovf 与 GhostInTheThread-disk1.vmdk（2 GiB，qemu-img info 显示为 vmdk、create type streamOptimized、compressed）。
3. 使用 qemu-img convert -O raw 把 streamOptimized VMDK 转换为原始镜像 disk.raw（2 GiB）。
4. 解析 GPT 分区表（或使用 mmls），确认 ext4 根分区 '/' 从扇区 135168 开始。
5. 以偏移 135168 使用 fls 列出文件系统，定位到 /usr/share/X11/xkb/symbols/custom（inode 65300），以及 /srv/sunchan/*、/var/lib/sunchan/board.sqlite 等相关文件。
6. 使用 icat -o 135168 disk.raw 65300 导出 custom 文件：内容为 name[Group1] = 'my layout' 和 31 条按键映射，例如 <AD01>b <AD02>l <AD03>d … <AC01>n <AC02>r … <AB01>x <AB02>q … <AB08>apostrophe <AB09>semicolon <AB10>period。
7. 按 XKB 键位约定（AD01=Q、AD02=W…；AC01=A、AC02=S…；AB01=Z、AB02=X…）把映射还原为 QWERTY 键序的三行布局：bldcvjyou, / nrtsgphaei / xqmwzkf';.。
8. 将该三行布局与公开布局比对，发现与 Gallium（Colstag 变体，作者 GalileoBlues，仓库 github.com/GalileoBlues/Gallium）逐字节完全一致；getreuer.info 的 alt-layouts 指南也推荐 Gallium。
9. 依据题目要求直接提交布局名 'Gallium'（不加 sun{}），提交页显示 Correct，题目状态变为 Forensics ✦ Solved。

## EXP 与运行方法

文件：无

本题在材料中没有保存任何可自动运行的 EXP 脚本（exp_files 为空），replay.status 为 manual，因此只能按题解步骤人工复现：手动下载 OVA、用 qemu-img 转换镜像、用 Sleuth Kit 的 fls/icat 按分区偏移 135168 导出 inode 65300 对应的 /usr/share/X11/xkb/symbols/custom，再按 XKB 键位约定手工还原布局并命名。材料中未提供自动化脚本，也未声称 EXP 已自动复现。

## 验证结果

没有可自动运行的 EXP；请按题解步骤人工复现。

证据：

- Challenge text (from submission page): 'ghost in the thread - 2' — 'What keyboard layout was the sysadmin here using? refer to ghost in the thread (1) for the challenge.' / 'No sun{} flag format, just the layout name.'
- GhostInTheThread.ova (tar, 126,945,280 B) downloaded from https://drive.usercontent.google.com/download?id=1fFWJp6tfT8U6bh0uuhB4AkDv-sdDCf_W ; contains GhostInTheThread.ovf + GhostInTheThread-disk1.vmdk (2 GiB streamOptimized).
- qemu-img info: vmdk, create type streamOptimized, compressed; qemu-img convert -O raw -> 2 GiB disk.raw. GPT shows ext4 '/' partition starting at sector 135168.
- fls/icat (offset 135168) lists /usr/share/X11/xkb/symbols/custom (inode 65300). Content: name[Group1] = 'my layout'; keys: <AD01>b <AD02>l <AD03>d <AD04>c <AD05>v <AD06>j <AD07>y <AD08>o <AD09>u <AD10>',' <AC01>n <AC02>r <AC03>t <AC04>s <AC05>g <AC06>p <AC07>h <AC08>a <AC09>e <AC10>i <AC11>'/' <AB01>x <AB02>q <AB03>m <AB04>w <AB05>z <AB06>k <AB07>f <AB08>apostrophe <AB09>semicolon <AB10>period.
- Layout rows reconstructed in QWERTY key order: 'bldcvjyou,' / 'nrtsgphaei' / 'xqmwzkf';.'. This is a byte-for-byte exact match to the canonical Gallium (Colstag) layout rows fetched from https://cdn.jsdelivr.net/gh/GalileoBlues/Gallium@main/Images/Gallium_Colstag.svg which read 'B L D C V J Y O U , N R T S G P H A E I X Q M W Z K F ' ; .' (Gallium by GalileoBlues, https://github.com/GalileoBlues/Gallium).
- Submitted flag 'Gallium' -> submission page alert strong 'Correct', and the challenge row changed to 'Forensics ✦ Solved ghost in the thread - 2 (137 solves)'.
- Independent extra confirmation: the VM's /usr/lib/security/pam_unix.so (inode 3195) is a planted backdoor exporting symbols artifact_description and configured_password (used by the sibling part 4), showing this OVA is the shared 'ghost in the thread' forensic image.

## Flag

`Gallium`

## 限制与备注

材料中无 EXP 脚本且 replay.status 为 manual，自动复现未经验证，全部流程需人工执行。解题依赖若干外部条件：Google Drive 下载可能受病毒扫描确认页与配额限制影响；需要 qemu-img 与 Sleuth Kit（fls/icat）等工具；分区偏移（扇区 135168）与 inode 号（65300）来自本份镜像的具体取证结果，换镜像不一定一致。与 Gallium 布局的一致性依据是材料中记录的与上游仓库图片逐字节行匹配，而非独立第三方判定；虽然提交 'Gallium' 后页面显示 Correct 并被标记为 Solved（confirmation_source 为 platform_confirmed），但对布局命名的严格学术判定仍以公开仓库内容为准。材料另提到镜像中 /usr/lib/security/pam_unix.so（inode 3195）被植入后门符号 artifact_description 与 configured_password（供同系列第 4 部分使用），这只能说明该 OVA 是 'ghost in the thread' 系列共用镜像，与本题答案无直接因果关系。
