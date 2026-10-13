# CTF Agent

中文使用说明：[README.zh-CN.md](README.zh-CN.md)

Autonomous CTF (Capture The Flag) solver that races multiple AI models against challenges in parallel. Built in a weekend, we used it to solve all 52/52 challenges and win **1st place at BSidesSF 2026 CTF**.

Built by [Veria Labs](https://verialabs.com), founded by members of [.;,;.](https://ctftime.org/team/222911) (smiley), the [#1 US CTF team on CTFTime in 2024 and 2025](https://ctftime.org/stats/2024/US). We build AI agents that find and exploit real security vulnerabilities for large enterprises.

## Results

| Competition | Challenges Solved | Result |
|-------------|:-:|--------|
| **BSidesSF 2026** | 52/52 (100%) | **1st place ($1,500)** |

The agent solves challenges across all categories — pwn, rev, crypto, forensics, web, and misc.

## How It Works

A **coordinator** LLM manages the competition while **solver swarms** attack individual challenges. Each swarm runs multiple models simultaneously — the first to find the flag wins.

```
                        +-----------------+
                        |  CTFd Platform  |
                        +--------+--------+
                                 |
                        +--------v--------+
                        |  Poller (5s)    |
                        +--------+--------+
                                 |
                        +--------v--------+
                        | Coordinator LLM |
                        | (Claude/Codex)  |
                        +--------+--------+
                                 |
              +------------------+------------------+
              |                  |                  |
     +--------v--------+ +------v---------+ +------v---------+
     | Swarm:          | | Swarm:         | | Swarm:         |
     | challenge-1     | | challenge-2    | | challenge-N    |
     |                 | |                | |                |
     |  Opus (med)     | |  Opus (med)    | |                |
     |  Opus (max)     | |  Opus (max)    | |     ...        |
     |  GPT-5.4        | |  GPT-5.4       | |                |
     |  GPT-5.4-mini   | |  GPT-5.4-mini  | |                |
     |  GPT-5.3-codex  | |  GPT-5.3-codex | |                |
     +--------+--------+ +--------+-------+ +----------------+
              |                    |
     +--------v--------+  +-------v--------+
     | Docker Sandbox  |  | Docker Sandbox |
     | (isolated)      |  | (isolated)     |
     |                 |  |                |
     | pwntools, r2,   |  | pwntools, r2,  |
     | gdb, python...  |  | gdb, python... |
     +-----------------+  +----------------+
```

Each solver runs in a dedicated, high-privilege Docker tooling container with CTF tools pre-installed. It is not a trusted security boundary. Solvers retry different approaches up to the configured per-model attempt limit.

## Quick Start

```bash
# Install
uv sync

# Build sandbox image
python tools/build_sandbox.py

# Configure credentials
cp .env.example .env
# Edit .env with your API keys and CTFd token

# Run against a CTFd instance
  uv run ctf-solve \
  --platform ctfd \
  --ctfd-url https://ctf.example.com \
  --ctfd-token ctfd_your_token \
  --challenges-dir challenges \
  --max-challenges 10 \
  -v
```

## 使用指南

### 1. 安装与准备

要求：

- Python 3.14+
- `uv`
- Docker Desktop 或 Docker Engine
- 至少一个模型提供商的 API Key，或已登录的 Claude/Codex CLI
- Node.js/npm，用于启动 Playwright MCP

PowerShell：

```powershell
uv sync
Copy-Item .env.example .env
python tools/build_sandbox.py
```

编辑 `.env`，至少配置所使用模型的 API Key。首次使用浏览器平台时，不需要把密码写入 `.env`，使用 `--login` 手动登录即可。

### 2. 浏览器平台模式

`auto` 模式通过 Playwright MCP 操作平台页面，适合 CTF² 或未知 CTF 平台：

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

首次运行 `--login` 时会打开有界面浏览器。手动完成登录后，回到终端按 Enter，程序会继续发现题目。浏览器会话默认保存在：

```text
.runtime/playwright-profile/
```

后续运行可以复用该登录态，不需要重复登录。同一个 profile 目录同一时间只能被一个 ctf-solve 使用；若另一个进程正在占用它，启动时会直接报错退出，而不是等到浏览器工具超时。也可以指定 profile：

```powershell
uv run ctf-solve --platform auto `
  --platform-url https://platform.example.com `
  --browser-profile D:\ctf-runtime\platform-profile `
  --models deepseek/deepseek-flash `
  --no-submit
```

### 3. CTFd API 模式（仅发现和下载）

标准 CTFd 使用 legacy API adapter。必须提供 CTFd 根地址和 API Token，不要把 `/explorer` 之类的前端路由当作 CTFd API 地址：

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

### 4. 只做指定题型

使用 `--challenge-type` 限制 Coordinator 的发现、轮询和 Solver 派发范围：

```powershell
# 只做 PWN
uv run ctf-solve --platform auto --platform-url https://platform.example.com `
  --challenge-type pwn --no-submit

# 同时做 PWN 和 Reverse
uv run ctf-solve --platform auto --platform-url https://platform.example.com `
  --challenge-type pwn,reverse --no-submit
```

支持的常见类型包括：`pwn`、`web`、`crypto`、`reverse`、`forensics`、`stego`、`misc`、`mobile`、`osint` 和 `blockchain`。参数不区分大小写，`binary`、`binary exploitation` 等也会归一化为 `pwn`。

### 5. 本地题目模式

已经有本地题目目录时，可以完全脱离平台运行：

```powershell
uv run ctf-solve `
  --platform local `
  --challenge challenges\warmup `
  --models deepseek/deepseek-flash `
  --no-submit `
  -v
```

题目目录至少应包含：

```text
challenges/warmup/
  metadata.yml
  distfiles/        # 可选，附件题文件
```

`metadata.yml` 中的 `connection_info` 表示远程服务；`distfiles/` 表示附件题。两者同时存在时，题目会按混合题处理。

### 6. Flag 提交策略

默认不提交 Flag。`--no-submit` 下模型输出会先进入候选登记，只有独立验证会话复现相同 Flag 后才会标记为已解；只有加入 `--submit` 才允许调用平台提交接口：

```powershell
uv run ctf-solve `
  --platform auto `
  --platform-url https://platform.example.com `
  --submit `
  --models deepseek/deepseek-flash
```

建议先使用 `--no-submit` 验证题目发现、环境启动和解题流程，再单独启用提交。

`--submit` 只能与 `--platform auto` 配合使用；`ctfd`、`local` 和 `--challenge` 模式不会执行提交。

### 7. Coordinator 选择

```powershell
# Claude Coordinator
uv run ctf-solve --coordinator claude ...

# Codex Coordinator
uv run ctf-solve --coordinator codex ...
```

两种 Coordinator 都可以使用平台适配器和 Playwright MCP；Solver 只获得题目附件和目标连接信息，不直接持有平台登录凭据。

默认 Solver 预算为每轮 30 分钟、160 个工具步骤、每个 Solver 15 美元、最多 5 轮。可通过 `SOLVER_ATTEMPT_TIMEOUT_SECONDS`、`SOLVER_MAX_TOOL_STEPS_PER_ATTEMPT`、`SOLVER_MAX_COST_USD`、`MAX_ATTEMPTS_PER_CHALLENGE` 和 `FLAG_VERIFICATION_QUORUM` 覆盖。

### 8. 常见问题

**浏览器无法启动**

确认 Node.js/npm 可用：

```powershell
node --version
npx --version
npx -y @playwright/mcp@latest --help
```

如果 MCP 提示浏览器运行时不存在，可以安装 Playwright 浏览器，或在 `.env` 中设置 `PLAYWRIGHT_EXECUTABLE_PATH` 指向本机 Chrome/Edge。

**CTFd 返回 HTML 或 JSONDecodeError**

通常是 `CTFD_URL` 指向了前端页面路由，而不是 CTFd 根地址。检查：

```text
正确： https://ctfd.example.com
错误： https://ctf2.dasctf.com/explorer
```

非标准平台请使用 `--platform auto --platform-url <平台地址>`。

**DeepSeek 返回 `Thinking mode does not support this tool_choice`**

确认使用的是最新代码。项目已针对 DeepSeek 将工具选择设为 `auto`，并使用 prompted JSON 输出，避免 Thinking mode 下发送 `tool_choice=required`。

## Coordinator Backends

```bash
# Claude SDK coordinator (default)
uv run ctf-solve --coordinator claude ...

# Codex coordinator (GPT-5.4 via JSON-RPC)
uv run ctf-solve --coordinator codex ...
```

## Solver Models

Default model lineup (configurable in `backend/models.py`):

| Model | Provider | Notes |
|-------|----------|-------|
| Claude Opus 4.6 (medium) | Claude SDK | Balanced speed/quality |
| Claude Opus 4.6 (max) | Claude SDK | Deep reasoning |
| GPT-5.4 | Codex | Best overall solver |
| GPT-5.4-mini | Codex | Fast, good for easy challenges |
| GPT-5.3-codex | Codex | Reasoning model (xhigh effort) |
| DeepSeek Flash | DeepSeek API | Optional API-backed solver with vision |

DeepSeek uses the OpenAI-compatible API. Configure `DEEPSEEK_API_KEY` and select it
explicitly when starting a solver:

```bash
uv run ctf-solve \
  --models deepseek/deepseek-flash \
  --ctfd-url https://ctf.example.com \
  --ctfd-token ctfd_your_token
```

## Platform Modes

The coordinator defaults to browser-first platform discovery through Playwright MCP:

```bash
uv run ctf-solve \
  --platform auto \
  --platform-url https://platform.example.com \
  --challenge-type pwn \
  --login \
  --models deepseek/deepseek-flash \
  --no-submit
```

The first `--login` run opens a headed Playwright browser and waits for a manual login to the challenge platform; it does not log in to Claude Code.
The browser profile is persisted under `.runtime/playwright-profile` by default. Discovered
challenge metadata and credential-free browser recipes are stored in the configured runtime
directories. `--submit` is required to enable flag submission; otherwise the run is dry-run.

Writeups now start when a solver reports a flag candidate, without waiting for platform submission or independent verification. Candidate writeups are explicitly labeled unverified and can be upgraded when confirmation arrives. By default, the writeup uses the solver model that found the flag. Set `WRITEUP_MODEL_SPEC` or pass `--writeup-model provider/model` to override it, including retries of pending or failed writeups; completed writeups are not regenerated automatically. Claude writeups read the user's Claude Code settings for authentication. Historical run-scoped candidates can be processed with `ctf-writeup backfill --run-id <run_id>`.

In submit mode, the Coordinator performs a mandatory submission-setup phase before any solver swarm can start. It reuses a valid saved recipe or uses its authenticated Playwright tools to inspect a real challenge form and save a credential-free recipe. Recipes support either an observed submit-button click or Enter submission through the `browser_type` `submit` option. The program fails closed if the recipe is still missing or invalid, instead of allowing solvers to run and discovering the problem only after a flag is found.


Use `--platform ctfd` to keep the legacy CTFd API integration, or `--platform local --challenge`
to solve a previously downloaded challenge without a platform connection.

Browser-auto mode prepares all registered unsolved challenge packages in a background queue.
`--max-preparations` controls attachment/environment preparation concurrency independently from
`--max-challenges`, which controls active solver swarms. Attachment downloads first use the visible
page control, then fall back to a same-origin fetch inside the authenticated browser context; browser
cookies are never exported to the coordinator or host HTTP client. A solver swarm is started only
after the challenge package reaches `ready`; remote challenges wait for the Agent to start the
environment and register its URL, host, or port, and hybrid challenges require both the environment
and every attachment to be ready.

Use `--challenge-type pwn` as a Coordinator classification preference. The Agent inspects the
category, name, description, tags, files, and connection information before deciding whether to
spawn a Solver. It does not equate generic labels such as `binary` or `exploit` with PWN. The
option is case-insensitive and accepts multiple values such as `--challenge-type pwn,reverse`.

`deepseek-flash` supports both thinking and non-thinking modes. The endpoint can be
overridden with `DEEPSEEK_BASE_URL` for a compatible gateway or proxy.

For any OpenAI-compatible provider such as SiliconFlow, configure one generic endpoint:

```env
MODEL_NAME=THUDM/GLM-4-9B-0414
API_KEY=your_provider_key
BASE_URL=https://api.siliconflow.cn/v1
```

When `MODEL_NAME` is set and `--models` is omitted, the project automatically uses that model.
You can also select it explicitly with `--models openai/THUDM/GLM-4-9B-0414`. Model IDs containing
slashes are preserved. The older provider-specific variables such as `DEEPSEEK_API_KEY` and
`DEEPSEEK_BASE_URL` remain supported for compatibility.

## Sandbox Tooling

Each solver gets a dedicated `linux/amd64` CTF tooling container. Build and validate it with `python tools/build_sandbox.py`. This checks Docker disk space, runs offline category smoke tests, and writes `logs/sandbox-build-report.json`. Inside the image, `ctf-tools-check --json` reports actual availability and `/tools.txt` is generated from the same manifest:

| Category | Tools |
|----------|-------|
| **Web and OSINT** | SQLMap, ffuf, DNS/WHOIS, Playwright and headless Chromium |
| **Pwn and reverse** | amd64/i386 runtime, GDB, QEMU user mode, radare2, Ghidra 11.4.3 and PyGhidra |
| **Crypto** | SageMath, fpylll, RsaCtfTool, CADO-NFS, flatter, PyTorch |
| **Forensics, stego, misc** | tshark, Scapy, Volatility 3, zsteg, 7z, John, CPU OpenCL Hashcat, PDF/Office parsing, Chinese OCR |
| **Mobile** | JADX CLI, Apktool, Androguard, ADB and Frida clients |
| **Blockchain** | forge, cast, anvil, solc-select, Slither, Web3.py |

Challenge Compose environments are started by the host environment manager. Android runtime analysis requires an external device or emulator. ARM/MIPS QEMU is installed, but a specific binary may need target architecture libraries.

## Features

- **Multi-model racing** — multiple AI models attack each challenge simultaneously
- **Auto-spawn** — new challenges detected and attacked automatically
- **Coordinator LLM** — reads solver traces, crafts targeted technical guidance
- **Cross-solver insights** — findings shared between models via message bus
- **Docker sandboxes** — isolated containers with full CTF tooling
- **Operator messaging** — send hints to running solvers mid-competition

## Configuration

### Offline CTF knowledge

Sync [Des-CTF-Knowledge](https://github.com/Dest1ny-Sec/Des-CTF-Knowledge) manually before a competition (Git required):

```bash
uv run ctf-knowledge sync
uv run ctf-knowledge status
uv run ctf-knowledge search "PHP deserialization wakeup" --limit 5
uv run ctf-knowledge read <document_id> --start-line 1 --line-count 120
```

Use `sync --ref <branch|tag|full-commit>` to select a revision. Upstream snapshots and the SQLite index live under `.runtime/knowledge/`. Each run pins its upstream snapshot, including after `--resume-run`; syncing during a run does not change its references. With no upstream snapshot, Solvers can still use curated local documents and solving memory. Claude, Codex, and API Solvers can search upstream documents, curated local documents, and solving memory, read full redacted `memory:` records, and copy selected upstream scripts plus explicit dependencies into their Docker workspace. Explicit search includes memory of every outcome; automatic context includes only `accepted` memory. Script staging never executes code or installs packages. Configure `EXTERNAL_KNOWLEDGE_ENABLED`, `EXTERNAL_KNOWLEDGE_DIR`, `EXTERNAL_KNOWLEDGE_CONTEXT_ITEMS`, and `EXTERNAL_KNOWLEDGE_CONTEXT_CHARS` in `.env`; the latter two cap automatic context at four references and 4000 characters by default. Run `uv run python -m tools.evaluate_knowledge` for the [labeled retrieval benchmark](docs/knowledge-evaluation.md). Preserve individual authorship and licensing when reusing third-party material from the source repository.

Curated Markdown methods live in `knowledge/local/`; only that directory is indexed by `uv run ctf-knowledge index-local` into `.runtime/knowledge-local/`. Verified solver methods are drafted in `knowledge/inbox/`; review a draft and run `uv run ctf-knowledge approve <draft.md>` to move it into the curated corpus and reindex. `status`, `search`, and `read` cover both document sources. New runs pin both snapshots; resumed runs created before this feature retain their original upstream-only behavior. Local paths are fixed defaults and require no `.env` entries.

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

```env
CTFD_URL=https://ctf.example.com
CTFD_TOKEN=ctfd_your_token
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...
DEEPSEEK_API_KEY=...
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

All settings can also be passed as environment variables or CLI flags.

Coordinator runs write full JSONL diagnostics to `logs/coordinator-<run_id>-<timestamp>.jsonl` and terminal output to `logs/run-<run_id>-<timestamp>.log`. These files contain unredacted tool input/output and may include credentials or flags. They stay local and are ignored by Git. Older runs are pruned after 7 days or when retained logs exceed 1 GiB; the newest run is kept.

## Requirements

- Python 3.14+
- Docker
- API keys for at least one provider (Anthropic, OpenAI, Google, or DeepSeek)
- `codex` CLI (for Codex solver/coordinator)
- `claude` CLI (bundled with claude-agent-sdk)

## Acknowledgements

- [es3n1n/Eruditus](https://github.com/es3n1n/Eruditus) — CTFd interaction and HTML helpers in `pull_challenges.py`
