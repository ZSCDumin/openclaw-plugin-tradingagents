# TradingAgents

OpenClaw tool plugin for running [TradingAgents](https://github.com/TauricResearch/TradingAgents)
from chat channels such as Feishu/Lark.

The plugin exposes two tools:

- `tradingagents_setup_status`: checks the Python runtime and TradingAgents package.
- `tradingagents_analyze`: runs a multi-agent market analysis for a ticker and returns a concise report.

## Feishu usage

After installing and enabling this plugin in OpenClaw, ask your Feishu bot naturally, for example:

```text
用 TradingAgents 分析 AAPL，输出中文结论
```

```text
分析 0700.HK，日期 2026-07-06，用 deepseek 模型
```

The agent can call `tradingagents_analyze` when it needs structured market research.

## Runtime

TradingAgents is a Python package and requires Python >= 3.10. The OpenClaw plugin
does not spawn Python directly. Instead, run the local TradingAgents HTTP service
explicitly, then let OpenClaw call it.

Start the service with `uv`:

```bash
uv run --with tradingagents --python 3.12 python python/tradingagents_server.py
```

Or use your own virtualenv:

```bash
/path/to/venv/bin/python python/tradingagents_server.py
```

TradingAgents also needs model/data credentials depending on your selected provider and tools,
for example `OPENAI_API_KEY`, `FINNHUB_API_KEY`, or provider-specific keys.

The plugin calls `http://127.0.0.1:8765`. This is fixed in the plugin source so
OpenClaw's install scanner can verify that the plugin is not sending environment
variables to arbitrary network endpoints.

First service start can take several minutes because `uv` may download Python and
TradingAgents dependencies. Keep this service running while using the Feishu bot.

## Install

Once this package is published to npm:

```bash
openclaw plugins install openclaw-plugin-tradingagents
openclaw plugins enable tradingagents
openclaw daemon restart
```

Once this package is pushed to GitHub:

```bash
openclaw plugins install github:<owner>/openclaw-plugin-tradingagents
openclaw plugins enable tradingagents
openclaw daemon restart
```

Then verify:

```bash
openclaw plugins inspect tradingagents
```

## Local development

```bash
npm install
npm run plugin:build
openclaw plugins install . --link
openclaw plugins enable tradingagents
openclaw daemon restart
```

## Build

```bash
npm install
npm run plugin:build
npm run plugin:validate
npm test
```
