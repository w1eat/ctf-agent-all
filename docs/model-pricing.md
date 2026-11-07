# 模型用量与价格口径

核对日期：2026-10-23。金额为 USD，每百万 token；更新本地单价和 DeepSeek 兼容别名，不自动切换模型。

| 模型 | 普通输入 | 缓存命中输入 | 输出 |
| --- | ---: | ---: | ---: |
| deepseek-flash（高峰） | 0.30 | 0.006 | 1.20 |
| deepseek-flash（低峰） | 0.15 | 0.003 | 0.60 |
| deepseek-v4-pro（高峰） | 1.32 | 0.044 | 3.96 |
| deepseek-v4-pro（低峰） | 0.66 | 0.022 | 1.98 |
| gemini-3-flash-preview（文本、图片、视频输入） | 0.50 | 0.05 | 3.00 |
| gpt-5.4-mini | 0.75 | 0.075 | 4.50 |
| gpt-5.4（输入 ≤272K） | 2.50 | 0.25 | 15.00 |
| gpt-5.4（输入 >272K） | 5.00 | 0.50 | 22.50 |
| gpt-5.3-codex | 1.75 | 0.175 | 14.00 |
| claude-opus-4-6（全球） | 5.00 | 0.50 | 25.00 |
| us.anthropic.claude-opus-4-6-v1（Bedrock US 地理区域） | 5.50 | 0.55 | 27.50 |

DeepSeek 按响应时间换算 UTC：周一至周五 01:00–04:00、06:00–10:00 为高峰，其他时段及周末为低峰。边界采用左闭右开。中国法定节假日也享受低峰价；项目未引入节假日日历，因此工作日高峰时段遇到法定节假日会保守高估。没有逐请求时间的汇总用量也采用高峰价。`deepseek-v4-flash`、`deepseek-v4-flash-vision-exp` 按 Flash 的兼容别名处理。[DeepSeek 官方价格](https://api-docs.deepseek.com/quick_start/pricing/)

Gemini 的音频输入单独按 1.00、缓存音频按 0.10 计费；输出含思考 token。未计算缓存存储、搜索等非 token 费用。[Google 官方价格](https://ai.google.dev/gemini-api/docs/pricing)

OpenAI 使用标准 API 价格，不含 Fast、Batch、Flex、地域加价等差异。GPT-5.4 的长上下文判断按单次请求输入长度；仅有 SDK 聚合数据时，采用最近一次请求提供的输入长度，因此仍是估算。Spark 没有核实到公开 API token 单价，已移除原先的猜测值；保留 token，显示价格未知。[GPT-5.4](https://developers.openai.com/api/docs/models/gpt-5.4)、[GPT-5.4 mini](https://developers.openai.com/api/docs/models/gpt-5.4-mini)、[OpenAI API 定价](https://developers.openai.com/api/docs/pricing)

Claude 的 5 分钟缓存写入为 6.25，1 小时缓存写入为 10.00；已写入和读取缓存的 token 从普通输入中扣除。识别到 1 小时缓存写入明细时使用对应价格，否则按默认 5 分钟估算。Bedrock US 地理区域按全球价格加 10%，缓存写入也适用该系数。[Claude 官方价格及地域说明](https://platform.claude.com/docs/en/about-claude/pricing)、[AWS 模型及地理区域说明](https://docs.aws.amazon.com/bedrock/latest/userguide/model-card-anthropic-claude-opus-4-6.html)

## 统计与预算

- Solver、Coordinator、Writeup 共用统计器，按 `solver`、`coordinator`、`writeup` 分类；状态查询返回 `usage_by_category` 和 `cost_incomplete`。
- Pydantic AI 在每次模型响应后记账；校验失败、工具失败、超时、取消都保留已返回用量。失败后的消息历史会留给下一次尝试。
- Claude 按消息 ID 合并用量，最终结果补足本轮 token；同一 SDK 会话的累计成本按差额入账，并替换本轮本地估算。累计费用异常回退或带有 token 的结果回报零增量时保留本地估算。`reported_cost_usd` 表示 SDK 报告的估算，不是账单金额。[Claude SDK 用量口径](https://code.claude.com/docs/en/agent-sdk/cost-tracking)
- Codex 按每个 thread 的累计 token 差额记账；重复或过时通知不会重复计入。订阅额度不能直接换算为 API 美元费用，这里的本地结果仅供预算参考。[Codex 计费说明](https://learn.chatgpt.com/docs/pricing)
- 已核对的价格优先于依赖库的内置快照；其余模型尝试 `genai-prices`，找不到价格时记录未知次数并标记总额不完整。自定义中转站、Azure、协议折扣仍须以实际服务账单核对。
- `SOLVER_MAX_COST_USD` 仍为每个 Solver 的预算。Pydantic AI 在下一次请求前检查已观察成本；Claude 同时使用 SDK 的预算参数；Codex 收到达到预算的用量通知后结束本轮并关闭后端。正在进行的请求可能让费用越过阈值，未知价格也无法保证美元预算。协调器和 Writeup 分开记账，不套用 Solver 预算。

## 日志与活动状态

默认聚合 Claude SDK 的 `thinking_tokens` 进度元数据，每 5 秒或遇到正常事件时输出计数；关闭日志前补写剩余计数。其他模型消息、工具结果和错误继续保留。需要原始进度时设置 `COORDINATOR_TRACE_RAW_PROGRESS=true`。

状态包含 `last_activity`、`current_operation`、`operation_elapsed_seconds` 和 `idle_seconds`。模型响应和工具调用、返回会刷新活跃时间；长时间等待会显示具体操作及耗时，不据此自动终止 Agent。
