# CTF Agent 中文使用说明

CTF Agent 是一个多模型并行的 CTF 自动解题框架。Coordinator 负责发现和调度题目，多个 Solver Agent 负责分析同一道题，Solver 运行在独立 Docker 工具容器中。

支持：

- Playwright MCP 浏览器平台模式
- 标准 CTFd API 模式
- 本地题目模式
- 附件题、远程环境题和混合题
- Claude 或 Codex Coordinator
- Claude、Codex、DeepSeek 等 Solver 模型
- 按题型给 Coordinator 提供目标偏好，例如优先判断 PWN

## 工作流程

```text
平台或本地题目
        |
        v
题目发现与环境准备
        |
        v
Coordinator
        |
        v
Challenge Swarm
        |
        v
Docker Solver Sandbox
        |
        v
Flag 发现与可选提交
```

Playwright MCP 模式下，Agent 可以通过浏览器完成登录、发现题目、下载附件、启动远程环境和读取连接地址。默认不会提交 Flag。

项目固定使用 `@playwright/mcp@0.0.82`，启动时会动态读取 MCP 工具列表。Coordinator 可以使用导航、快照、点击、键盘、下拉框、弹窗、网络、文件上传和 `browser_run_code_unsafe` 等工具；附件下载仍由平台层负责校验和归档。

## 环境要求

- Python 3.14+
- `uv`
- Docker Desktop 或 Docker Engine
- Node.js/npm，用于启动 Playwright MCP
- 至少一个模型提供商的 API Key，或已配置的 Claude/Codex CLI

## 安装

PowerShell：

```powershell
uv sync
Copy-Item .env.example .env
python tools/build_sandbox.py
```

编辑 `.env`，填写正在使用的模型 API Key：

```env
DEEPSEEK_API_KEY=your_deepseek_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

也可以使用 Anthropic、OpenAI 或 Google 模型。配置文件中的敏感信息不要提交到 Git。

## 最常用命令

### 浏览器平台模式

`auto` 模式使用 Playwright MCP 访问未知或非 CTFd 平台，例如 CTF²：

```powershell
uv run ctf-solve `
  --platform auto `
  --platform-url https://platform.example.com `
  --login `
  --coordinator claude `
  --models deepseek/deepseek-flash `
  --challenges-dir challenges `
  --max-challenges 1 `
  --no-submit `
  -v
```

第一次使用 `--login` 时，程序会打开有界面浏览器。手动完成比赛平台登录后，回到终端按 Enter，Agent 会继续执行。该选项不会登录 Claude Code。

auto 模式会先登记题目，再由程序级准备队列自动处理附件候选。附件下载完成、文件哈希校验通过后，Solver 才会启动；页面快照和日志不会被当作题目附件。

当前实现会把所有已登记的未解题自动加入后台准备队列，不再依赖 Coordinator 逐题调用下载工具。`--max-preparations` 控制附件/环境准备并发，默认 4；`--max-challenges` 只控制同时运行的 Solver swarm。题目必须先完成题型识别和资源准备，只有进入 `ready` 后才会启动 Solver。附件先通过可见页面按钮下载；按钮定位失败时，在已登录浏览器上下文内执行同源 fetch，HttpOnly Cookie 不会导出到 Coordinator 或宿主 HTTP 客户端。附件大小或 SHA-256 不匹配时不会进入 `ready`。

如果任务中断，可以使用状态库中的运行 ID 恢复：

```powershell
uv run ctf-solve `
  --platform auto `
  --platform-url https://platform.example.com `
  --resume-run <run_id> `
  --no-submit
```

题包状态保存在 `.runtime/challenge_state.sqlite3`。环境题在环境尚未启动或连接信息尚未登记时处于 `waiting_for_environment`；附件缺失、下载失败或平台需要人工操作时才进入 `needs_input`，不会启动空沙箱。

浏览器 profile 默认保存在：

```text
.runtime/playwright-profile/
```

之后可以复用登录状态。同一个 profile 目录同一时间只能被一个 ctf-solve 使用；如果另一个进程正在占用它，启动时会直接报错退出，而不是等浏览器工具逐个超时。也可以指定 profile 目录：

```powershell
uv run ctf-solve `
  --platform auto `
  --platform-url https://platform.example.com `
  --browser-profile D:\ctf-runtime\platform-profile `
  --models deepseek/deepseek-flash `
  --no-submit
```

### 标准 CTFd 模式（仅发现和下载）

标准 CTFd 使用 API adapter：

```powershell
uv run ctf-solve `
  --platform ctfd `
  --ctfd-url https://ctfd.example.com `
  --ctfd-token ctfd_your_token `
  --coordinator claude `
  --models deepseek/deepseek-flash `
  --challenges-dir challenges `
  --max-challenges 1 `
  --no-submit `
  -v
```

CTFd API 不再用于提交 flag。所有 flag 提交都必须使用 `--platform auto`，由 Playwright MCP 完成浏览器操作并验证成功标记。

`--ctfd-url` 必须是 CTFd 根地址，不要填写前端页面路由。例如：

```text
正确： https://ctfd.example.com
错误： https://ctf2.dasctf.com/explorer
```

### 本地题目模式

已有题目文件时，可以不连接平台：

```powershell
uv run ctf-solve `
  --platform local `
  --challenge challenges\warmup `
  --models deepseek/deepseek-flash `
  --no-submit `
  -v
```

题目目录示例：

```text
challenges/warmup/
  metadata.yml
  distfiles/
```

`metadata.yml` 中的 `connection_info` 表示远程服务，`distfiles/` 表示附件。两者同时存在时，题目会被识别为混合题。

下载的原始附件会保存到 `distfiles/` 并记录 SHA-256，不会自动解压。Solver 负责在沙箱中自行解压和分析。

## 题型偏好与 Agent 判断

使用 `--challenge-type` 告诉 Coordinator 目标题型。它是 Agent 的分类偏好，不是程序根据
category 字段进行的硬过滤：

```powershell
# 只做 PWN
uv run ctf-solve `
  --platform auto `
  --platform-url https://platform.example.com `
  --challenge-type pwn `
  --no-submit

# 同时做 PWN 和 Reverse
uv run ctf-solve `
  --platform auto `
  --platform-url https://platform.example.com `
  --challenge-type pwn,reverse `
  --no-submit
```

支持的常见类型：

```text
pwn, web, crypto, reverse, forensics, stego,
misc, mobile, osint, blockchain
```

类型不区分大小写，也支持常见别名：

- `binary exploitation` 会归一化为 `pwn`，但通用的 `binary` 和 `exploit` 不会自动当成 PWN
- `rev`、`reversing` 会归一化为 `reverse`
- `web3`、`smart contract` 会归一化为 `blockchain`

Coordinator 会综合题目分类、名称、描述、标签、附件和连接信息进行判断，再决定是否调用
`spawn_swarm`。

## Flag 提交

默认不提交 Flag。`--no-submit` 下模型输出首先登记为候选 Flag，至少需要独立验证会话复现相同值后才会被 Swarm 标记为已解。建议先使用：

```text
--no-submit
```

只有显式添加 `--submit` 才允许调用平台提交接口：

提交模式会在 Coordinator 启动后的第一个阶段自动检查提交 recipe。已有有效 recipe 会直接复用；缺失或不完整时，Coordinator 必须先使用已登录的 Playwright 浏览器观察真实题目页面并调用 `save_recipe`，程序确认 recipe 就绪后才允许启动 Solver swarm。recipe 准备失败会 fail-closed，不会先解题再到提交时才报错；可用 `--no-submit` 明确运行仅验证模式。



```powershell
uv run ctf-solve `
  --platform auto `
  --platform-url https://platform.example.com `
  --submit `
  --models deepseek/deepseek-flash
```

`--submit` 只能与 `--platform auto` 配合使用；`--platform ctfd`、`--platform local` 和 `--challenge` 模式不会执行提交。

## Solver MCP 工具（IDA / JADX / Kali）

提供 `--solver-mcp-config` 后，所有 Solver（Claude、Codex、DeepSeek 等）都能调用同一组 MCP 工具。配置模板见 `solver-mcp.example.json`：复制为 `solver-mcp.local.json`，按本机路径和 Kali 地址修改，再运行：

```powershell
Copy-Item solver-mcp.example.json solver-mcp.local.json
uv run ctf-solve `
  --platform auto `
  --platform-url https://platform.example.com `
  --models deepseek/deepseek-flash `
  --solver-mcp-config solver-mcp.local.json `
  --no-submit
```

题包准备好后，程序会在 `.runtime/solver-mcp/` 安全展开 ZIP/TAR 附件，识别 APK 和常见本机二进制格式。IDA 使用 `idalib-mcp --stdio` 的无界面会话；JADX 由配置中的 Java 启动命令打开 APK，插件返回匹配 APK 包名的 Manifest 后才开放该文件的工具。JADX GUI 同一时间由一道题持有，Swarm 结束后才轮到下一题；题内的多个 APK 也会串行加载。Kali 客户端启动失败只会使 Kali 工具不可用，Solver 仍可用 Docker 解题。

Solver 提供 `list_analysis_tools`、`call_analysis_tool` 和 `analysis_status`。先列出工具；调用 IDA/JADX 时传返回的 `file_id`，网关会自动绑定本题对应会话。MCP 配置文件包含本机路径，`solver-mcp.local.json` 已加入 Git 忽略列表。

## 自学习知识库

项目会将每次 Solver 的解题摘要提炼为可复用知识，并保存到 SQLite：

```text
.runtime/knowledge.sqlite3
```

下一次启动 Solver 时，系统会根据题目名称、题型和模式检索历史方法；只有平台确认过的 `accepted` 记录会自动注入上下文，模型仍须复核其适用性。知识库保存的是解题方法、关键推理和结果类型，不保存 flag、凭据或原始工具输出。

相关配置：

```env
KNOWLEDGE_DB_PATH=.runtime/knowledge.sqlite3
KNOWLEDGE_ENABLED=true
```

这属于检索增强，不会修改模型权重。`accepted` 表示平台确认过的经验；`unverified_candidate` 只表示模型给出了候选结果，不能当作真实 flag。

### 外部 CTF 知识库

赛前手动同步 [Des-CTF-Knowledge](https://github.com/Dest1ny-Sec/Des-CTF-Knowledge)，需要本机安装 Git：

```powershell
uv run ctf-knowledge sync
uv run ctf-knowledge status
uv run ctf-knowledge search "PHP反序列化 wakeup" --limit 5
uv run ctf-knowledge read <搜索结果中的document_id> --start-line 1 --line-count 120
```

也可用 `sync --ref <分支、标签或完整 commit>` 固定指定版本。上游原文、SQLite 全文索引和同步记录保存在 `.runtime/knowledge/`；同步失败时旧快照仍可用。每个 `ctf-solve` 运行会固定上游知识版本，恢复任务沿用原版本，赛中同步不会改变正在运行的 Solver。无上游快照时仍可使用本地审核语料与历史经验，不会自动联网。

经审核的 Markdown 方法卡保存在 `knowledge/local/`，运行 `uv run ctf-knowledge index-local` 可离线更新 `.runtime/knowledge-local/` 的索引。经确认或独立验证的解题方法先进入 `knowledge/inbox/` 草稿区；人工审核后运行 `uv run ctf-knowledge approve <draft.md>`，命令会移入正式语料并重建索引。`status`、`search` 和 `read` 同时支持上游与本地文档。新运行固定两份快照，旧运行恢复时继续沿用原先的上游快照行为。本地目录使用固定默认路径，无需新增 `.env` 项。

三类 Solver 均可调用 `search_knowledge`、`read_knowledge` 和 `stage_knowledge_script`。显式搜索可看到未验证的本地记忆及其 `outcome`；`memory:` ID 可用 `read_knowledge` 读取完整脱敏推理。外部文档的阅读结果含 `next_start_line`，长行还含 `next_char_offset`，可据此继续读取。选中脚本后，导入工具只复制明确选中的外部文件到 `/challenge/workspace/knowledge/`；依赖文件需要从阅读结果的 `related_files` 中选取 ID，作为 `extra_document_ids` 传入。工具不会安装依赖或执行脚本。导入和执行都发生在现有 Docker 沙箱。

```env
EXTERNAL_KNOWLEDGE_ENABLED=true
EXTERNAL_KNOWLEDGE_DIR=.runtime/knowledge
EXTERNAL_KNOWLEDGE_CONTEXT_ITEMS=4
EXTERNAL_KNOWLEDGE_CONTEXT_CHARS=4000
```

自动上下文分别检索题名、标签、附件名与题目描述，最多注入 4 条参考和 4000 个字符；有已验证本地记忆时，最多包含 1 条记忆与 3 条外部参考。

外部文章与 WP 只作为未验证参考。同步仓库含第三方转载资料，引用或再发布时请检查文档记录的原作者、原文链接和单篇许可。离线检索基线可运行 `uv run python -m tools.evaluate_knowledge`；[评估结果](docs/knowledge-evaluation.md)记录了当前快照上的人工标注查询结果。

## Solver 预算与独立验证

默认深度攻坚预算如下，可通过环境变量覆盖：

```env
SOLVER_ATTEMPT_TIMEOUT_SECONDS=1800
SOLVER_MAX_TOOL_STEPS_PER_ATTEMPT=160
SOLVER_MAX_COST_USD=15
MAX_ATTEMPTS_PER_CHALLENGE=5
FLAG_VERIFICATION_QUORUM=2
COORDINATOR_DECISION_TIMEOUT_SECONDS=180
```

每个 Solver 按题型和附件分配 `recon`、`static_analysis`、`dynamic_exploit`、`alternative_path` 或 `verifier` 角色。单模型配置时，候选 Flag 会使用新的会话和新的沙箱进行独立复核；复核会话不会继承原始聊天历史。

浏览器平台提交时，recipe 必须包含真实的浏览器操作步骤：可点击观察到的提交按钮；若页面明确说明回车提交，则在 `{flag}` 输入步骤中设置 `data.submit=true`。`success_markers` 和 `failure_markers` 是提供给 Agent 的辅助证据，不会单独决定结果。提交后系统记录待确认 Flag；确认时会重新抓取当前页面，并要求确认的 Flag 与待确认值一致。Agent 可以根据完整页面上下文推翻 marker，但必须在理由中明确说明冲突。进程重启后待确认状态不会恢复，需要重新提交。

提交前建议先验证题目发现、附件下载、环境启动和 Solver 输出。

## 中文题解与 EXP

Solver 一得到候选 Flag 就会安排生成本地中文题解，不等待平台提交或独立复核。未确认的题解会明确标注“候选 Flag（未经确认）”；之后若平台接受或独立复核通过，同一 Flag 的题解可升级为对应的确认状态。题解包括 Flag、解题过程、证据和复现状态；这些材料不等于平台已接受。

```text
challenges/<题目目录>/writeup.md
challenges/<题目目录>/exp/
challenges/<题目目录>/solution/manifest.json
```

Solver 应把实际使用的 EXP 写到沙箱的 `/challenge/workspace/` 并在结果中登记路径。程序会在沙箱停止前保存这些文件，随后在新沙箱中尝试复现。无法自动运行的题目会标明人工步骤；复现失败会标为“待检查”，不会冒充验证成功。题解生成失败不会影响 Flag 记录，可在下次启动时重试。

默认使用发现 Flag 的 Solver 模型生成题解，可通过 `--writeup-model provider/model` 或 `WRITEUP_MODEL_SPEC` 覆盖。显式设置的模型也会用于重试待处理或失败的旧题解；已完成题解不会自动重写。Claude 题解会读取用户 Claude Code 设置中的认证信息。单题运行会等待本题题解生成；Coordinator 在后台生成。已有记录可用 `uv run ctf-writeup backfill --run-id <运行ID>` 尝试补写；运行范围内的候选 Flag 也会标注为未经确认并生成题解，缺少明确 Flag 或解题材料的旧题仍会跳过。题目目录仍被 Git 忽略，题解和完整 Flag 仅保存在本地。

## Coordinator

Claude Coordinator：

```powershell
uv run ctf-solve --coordinator claude ...
```

Codex Coordinator：

```powershell
uv run ctf-solve --coordinator codex ...
```

两种 Coordinator 都使用统一的平台接口，模型回合超时可通过 `COORDINATOR_DECISION_TIMEOUT_SECONDS` 配置；设为 `0` 可关闭。Solver 只接收题目附件和目标连接信息，不直接获得平台登录凭据。Coordinator 状态中会显示每个 Solver 的角色、轮次、预算、最后活动时间和候选验证状态。

### Coordinator 全权限模式

默认情况下 Coordinator 使用受限工具集。需要让 Claude/Codex Coordinator 使用原生 Agent 工具、宿主机 Shell、文件操作和网络能力时，显式添加：

```powershell
uv run ctf-solve --coordinator claude --coordinator-full-access ...
uv run ctf-solve --coordinator codex --coordinator-full-access ...
```

不添加该参数时保持受限模式；也可以显式使用 `--no-coordinator-full-access` 关闭。

全权限模式会把 Codex 设置为 `danger-full-access` 且不再请求命令审批；请只在可信的题目平台和隔离环境中使用。

Coordinator 的结构化日志写入 `logs/coordinator-<run_id>-<timestamp>.jsonl`，终端文本写入对应的 `logs/run-<run_id>-<timestamp>.log`。事件包含回合、工具调用、取消来源、重连和退出清理阶段的关联 ID、状态、耗时与异常堆栈。日志保留完整原始输入输出，**可能包含平台凭据、Flag 和网页数据**；仅保存在本机且被 Git 忽略。运行结束时保留最近一次运行，其余运行按 7 天或总计 1 GiB 的限制轮转。

## Solver 模型

模型使用 `provider/model` 格式：

```text
deepseek/deepseek-flash
claude-sdk/claude-opus-4-6/medium
codex/gpt-5.4
google/gemini-3-flash-preview
```

DeepSeek 使用 OpenAI-compatible Chat Completions 接口。项目已针对 DeepSeek Thinking mode 做兼容处理：工具选择使用 `auto`，最终结构化输出使用 prompted JSON，避免 `tool_choice=required` 导致 400 错误。

### 通用 OpenAI-compatible 供应商

对于 SiliconFlow 等兼容 OpenAI Chat Completions 的供应商，可以统一配置：

```env
MODEL_NAME=THUDM/GLM-4-9B-0414
API_KEY=your_provider_key
BASE_URL=https://api.siliconflow.cn/v1
```

当设置了 `MODEL_NAME` 且没有传入 `--models` 时，项目会自动使用该模型。也可以显式指定：

```powershell
uv run ctf-solve --models openai/THUDM/GLM-4-9B-0414 ...
```

模型名中的 `/` 会被保留。原有的 `DEEPSEEK_API_KEY`、`DEEPSEEK_BASE_URL` 等专用变量仍然兼容。

## 题目类型

题目通过以下字段自动归类：

```text
有附件 files
    -> attachment

有远程地址 connection_info、environment，或 Agent 登记的 environment_required
    -> remote

附件和远程环境都有
    -> hybrid

两者都没有
    -> unknown
```

本地 metadata 示例：

```yaml
version: beta2
platform: local
native_id: warmup
name: WarmUp
category: pwn
challenge_mode: attachment
description: Local binary challenge
connection_info: ""
```

## Playwright MCP

项目使用安全的 Playwright MCP 工具集，包括：

- 页面导航
- accessibility snapshot
- 文本查找
- 点击和输入
- 等待页面状态
- 网络请求查看
- 截图
- Tab 管理

交互时先获取 snapshot，再使用页面元素引用。Playwright MCP 实际提供的工具会动态加载；当前版本也可能暴露 `browser_run_code_unsafe`。

确认 Node.js/npm 可用：

```powershell
node --version
npx --version
npx -y @playwright/mcp@latest --help
```

如果提示浏览器运行时不存在，可以安装 Playwright 浏览器，或者在 `.env` 中配置：

```env
PLAYWRIGHT_EXECUTABLE_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
```

## Docker 沙箱

每个 Solver 使用一张 `linux/amd64` 工具镜像中的独立容器。完整构建和离线验收运行 `python tools/build_sandbox.py`；脚本先检查 Docker 引擎及数据目录可用空间，完成后写入 `logs/sandbox-build-report.json`。容器内用 `ctf-tools-check --json` 查看实际可用状态，用 `cat /tools.txt` 查看由同一清单生成的工具说明。必备工具缺失时构建失败。

- Web、OSINT：SQLMap、ffuf、DNS/WHOIS、Playwright 和预装的无界面 Chromium
- PWN、逆向：amd64/i386 运行库、GDB、多架构 GDB、QEMU user mode、radare2、Ghidra 11.4.3 和 PyGhidra
- 密码学：SageMath、fpylll、RsaCtfTool、CADO-NFS、flatter、PyTorch
- 取证、隐写、Misc：tshark、Scapy、Volatility 3、磁盘工具、zsteg、stegseek、7z、John、CPU OpenCL Hashcat、PDF/Office 解析、中文 OCR
- 移动端：JADX CLI、Apktool、Androguard、ADB、Frida 客户端；设备和模拟器需在容器外提供
- 区块链：Foundry 的 forge/cast/anvil、solc-select、Slither、Web3.py

题目自带 Compose 环境由宿主机环境管理器启动。容器内的 ARM/MIPS QEMU 提供命令入口；运行具体跨架构程序时仍需相应运行库。

题目附件挂载到：

```text
/challenge/distfiles/
```

Solver 生成的工作文件写入：

```text
/challenge/workspace/
```

## 常见问题

### CTFd 返回 HTML 或 JSONDecodeError

说明配置地址命中了前端页面，而不是 CTFd API。标准 CTFd 使用：

```powershell
--platform ctfd --ctfd-url https://ctfd.example.com
```

非标准平台使用：

```powershell
--platform auto --platform-url https://platform.example.com
```

### DeepSeek 返回 tool_choice 400

确认使用最新代码。DeepSeek Thinking mode 不支持强制工具选择，项目已经将工具选择设为 `auto`。

### 浏览器无法启动

确认 Node.js/npm 和 Chrome/Edge 可用：

```powershell
node --version
npx --version
```

也可以通过 `PLAYWRIGHT_EXECUTABLE_PATH` 指定浏览器路径。

### 如何停止运行

在运行终端按：

```text
Ctrl+C
```

Coordinator 会停止轮询、取消 Solver、关闭浏览器会话，并清理由项目创建的本地环境。

## 测试

运行测试和静态检查：

```powershell
uv run pytest -q
uv run ruff check backend tests
uv run ty check backend
uv run python -m compileall -q backend tests
```

## 相关文档

- 英文说明：[README.md](README.md)
- 示例环境变量：[.env.example](.env.example)
- 题目沙箱构建文件：[sandbox/Dockerfile.sandbox](sandbox/Dockerfile.sandbox)
