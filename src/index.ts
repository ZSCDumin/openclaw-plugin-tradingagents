import { Type } from "typebox";
import { defineToolPlugin } from "openclaw/plugin-sdk/tool-plugin";

type RunnerPayload = Record<string, unknown>;

const endpoint = "http://127.0.0.1:8765";

async function runTradingAgents(payload: RunnerPayload, timeoutSeconds: number) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutSeconds * 1000);
  try {
    const response = await fetch(`${endpoint.replace(/\/$/, "")}/run`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    const text = await response.text();
    let parsed: unknown;
    try {
      parsed = JSON.parse(text);
    } catch {
      throw new Error(`TradingAgents service returned non-JSON output: ${text.slice(0, 2000)}`);
    }
    if (!response.ok) {
      const message = typeof parsed === "object" && parsed !== null && "error" in parsed ? String(parsed.error) : response.statusText;
      throw new Error(`TradingAgents service error: ${message}`);
    }
    return parsed;
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw new Error(`TradingAgents service timed out after ${timeoutSeconds}s at ${endpoint}.`);
    }
    if (error instanceof Error) {
      throw new Error(`TradingAgents service is unavailable at ${endpoint}: ${error.message}`);
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

export default defineToolPlugin({
  id: "tradingagents",
  name: "TradingAgents",
  description: "Run TradingAgents multi-agent market analysis from OpenClaw conversations.",
  tools: (tool) => [
    tool({
      name: "tradingagents_setup_status",
      description: "Check whether the TradingAgents Python runtime can be started.",
      parameters: Type.Object({
        timeoutSeconds: Type.Optional(Type.Number({ description: "Maximum seconds to wait for the check.", minimum: 5, maximum: 300 })),
      }),
      execute: async ({ timeoutSeconds = 120 }) =>
        runTradingAgents(
          {
            action: "health",
          },
          timeoutSeconds,
        ),
    }),
    tool({
      name: "tradingagents_analyze",
      description:
        "Run TradingAgents analysis for a market ticker and return a concise decision report. Use for stock, ETF, index-proxy, Hong Kong, China A-share, India, crypto, and other Yahoo Finance tickers.",
      parameters: Type.Object(
        {
          ticker: Type.String({
            description: "Yahoo Finance ticker, for example AAPL, NVDA, SPY, 0700.HK, 600519.SS, BTC-USD.",
          }),
          analysisDate: Type.Optional(Type.String({ description: "Analysis date in YYYY-MM-DD format. Defaults to today." })),
          llmProvider: Type.Optional(Type.String({ description: "TradingAgents LLM provider, for example openai, anthropic, google, deepseek, qwen, ollama, openai_compatible." })),
          deepThinkLlm: Type.Optional(Type.String({ description: "Model for complex reasoning, for example gpt-5.5." })),
          quickThinkLlm: Type.Optional(Type.String({ description: "Model for quick analyst steps, for example gpt-5.4-mini." })),
          backendUrl: Type.Optional(Type.String({ description: "Optional OpenAI-compatible backend URL, for example http://localhost:1234/v1." })),
          outputLanguage: Type.Optional(Type.String({ description: "Final report language. Examples: English, Chinese." })),
          maxDebateRounds: Type.Optional(Type.Number({ description: "Research debate rounds.", minimum: 0, maximum: 5 })),
          maxRiskRounds: Type.Optional(Type.Number({ description: "Risk discussion rounds.", minimum: 0, maximum: 5 })),
          checkpoint: Type.Optional(Type.Boolean({ description: "Enable LangGraph checkpoint resume for long analyses." })),
          timeoutSeconds: Type.Optional(Type.Number({ description: "Maximum seconds to wait for analysis.", minimum: 60, maximum: 7200 })),
        },
        { additionalProperties: false },
      ),
      execute: async ({
        ticker,
        analysisDate,
        llmProvider,
        deepThinkLlm,
        quickThinkLlm,
        backendUrl,
        outputLanguage,
        maxDebateRounds,
        maxRiskRounds,
        checkpoint,
        timeoutSeconds = 1800,
      }) =>
        runTradingAgents(
          {
            action: "analyze",
            ticker,
            analysisDate,
            llmProvider,
            deepThinkLlm,
            quickThinkLlm,
            backendUrl,
            outputLanguage,
            maxDebateRounds,
            maxRiskRounds,
            checkpoint,
          },
          timeoutSeconds,
        ),
    }),
  ],
});
