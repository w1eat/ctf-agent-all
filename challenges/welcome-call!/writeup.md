# Welcome Call! 题解

- 分类：Forensics
- Flag：**sun{thankyouforplaying}**
- 本地证据：PCAP 中的 SIP/RTP 通话解码后，按样本时间倒序播放，语音明确读出 Flag 的组成。
- 平台关联：用户反馈平台显示此题已解。旧运行记录中确认器看到互相冲突的提示，无法把平台上的成功提交对应到具体一次尝试。

## 题目信息

题目附件为 welcomecall.pcap。描述提示有人接到“旗帜工厂”的电话。

## 解题原理

PCAP 先用 SIP 建立语音通话，随后以 RTP 传送 G.711 μ-law（PCMU，payload type 0）音频。RTP 包的序号连续，但音频样本以倒序录制。按 RTP 序号拼接 payload、解码 μ-law，再将 PCM 样本倒序，得到正常语序的通话。语音直接说明 Flag 前缀为 sun{、后缀为 }，中间内容是 “Thank you for playing”，并要求全小写、无空格。

## 关键步骤

1. 用 Wireshark 或 tshark 打开附件，检查协议统计及会话，找到 SIP 信令和 UDP 4000 → 4002 的 RTP 流。
2. RTP 共 778 个包，payload type 为 0（PCMU），每包 160 字节；序号从 12000 连续到 12777，表示 8 kHz、每包 20 ms 的单声道语音。
3. 按 RTP 序号拼接 payload。每个 RTP 包跳过 12 字节固定头，并按 CSRC、扩展头和 padding 字段处理可选头部。
4. 将拼接后的 μ-law 字节解码为 16-bit PCM，写成 8 kHz 单声道 WAV。听起来是倒放语音。
5. 将 PCM 样本顺序反转后再播放，听到：“Welcome to B-Sides Orlando. The flag that you are looking for is sun with a left curly bracket. Thank you for playing. Right curly bracket. All lowercase, no spaces.”
6. 按语音给出的大小写和格式组成 Flag：sun{thankyouforplaying}。

## EXP 与运行方法

文件：exp/recover_audio.py

需要 Python 3.10+ 和 Scapy。脚本提取 RTP/PCMU 音频并生成 reversed.wav，用任意音频播放器收听即可核对语音内容：

~~~powershell
python -m pip install scapy
python exp/recover_audio.py
~~~

脚本输出 WAV 到脚本所在的 exp 目录。

## 验证结果

附件 SHA-256 为 7e0effd30dbd6fd072fe565f012c86746f9e27cd54eaa2fa942a9c5af4f2d3e6，与题目元数据记录相同。旧求解轨迹保存了 Whisper 对倒序后 WAV 的完整转录；语音内容直接给出 Flag 文本。用户报告队伍平台显示已解，但旧轨迹里对 thankyouforplaying 的提交没有留下平台成功提示，后续页面又同时包含 Correct、Already solved 和 Incorrect 标记，因此无法单靠该轨迹审计具体成功提交值。
