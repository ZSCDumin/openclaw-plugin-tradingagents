# Publishing

This plugin is package-ready for OpenClaw installs from npm or GitHub.

## Validate locally

```bash
npm install
npm test
npm run plugin:build
npm run plugin:validate
npm pack --dry-run
```

## Publish to npm

1. Confirm the package name in `package.json`.
2. Log in with an npm account that can publish the package.
3. Publish:

```bash
npm publish
```

Users can then install with:

```bash
openclaw plugins install openclaw-plugin-tradingagents
openclaw plugins enable tradingagents
openclaw daemon restart
```

## Publish to GitHub

Push this directory to a public GitHub repository. Users can then install with:

```bash
openclaw plugins install github:<owner>/openclaw-plugin-tradingagents
openclaw plugins enable tradingagents
openclaw daemon restart
```

## Notes

- The OpenClaw plugin itself does not execute shell commands or read environment variables.
- The TradingAgents runtime is a local HTTP service on `127.0.0.1:8765`.
- Keep `dist/`, `python/`, `openclaw.plugin.json`, `README.md`, and `LICENSE` in the npm package.
