# Postman MCP Server demo

## MCP server installed
- Package: `@postman/postman-mcp-server` (version installed locally)
- MCP server name in `blackbox_mcp_settings.json`: `github.com/postmanlabs/postman-mcp-server`

## How to start locally (stdio)
Set `POSTMAN_API_KEY` in your environment, then run:

```powershell
$env:POSTMAN_API_KEY="<YOUR_POSTMAN_API_KEY>"
node .\node_modules\@postman\postman-mcp-server\dist\src\index.js --minimal --quiet
```

## Tool invocation
To demonstrate capabilities, connect an MCP host that reads `blackbox_mcp_settings.json` and call a minimal tool such as:
- `getWorkspaces` (or another minimal Postman tool from the server’s tool list)

> Note: In this environment, the server requires `POSTMAN_API_KEY` to be set to a **valid** value.

