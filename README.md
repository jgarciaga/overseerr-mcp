# MCP server for Overseerr

MCP server to interact with Overseerr API for movie and TV show requests management.

<!-- Badge will be added once published -->

## Components

### Tools

The server implements multiple tools to interact with Overseerr:

- overseerr_status: Get the status of the Overseerr server
- overseerr_movie_requests: Get the list of all movie requests that satisfies the filter arguments
- overseerr_tv_requests: Get the list of all TV show requests that satisfies the filter arguments

### Example prompts

It's good to first instruct Claude to use Overseerr. Then it will always call the tool when appropriate.

Try prompts like these:
- Get the status of our Overseerr server
- Show me all the movie requests that are currently pending
- List all TV show requests from the last month that are now available
- What movies have been requested but are not available yet?
- What TV shows have recently become available in our library?

## Configuration

### Overseerr API Key & URL

There are two ways to configure the environment with the Overseerr API credentials:

1. Add to server config (preferred)

```json
{
  "overseerr-mcp": {
    "command": "uvx",
    "args": [
      "overseerr-mcp"
    ],
    "env": {
      "OVERSEERR_API_KEY": "<your_api_key_here>",
      "OVERSEERR_URL": "<your_overseerr_url>"
    }
  }
}
```

2. Create a `.env` file in the working directory with the following required variables:

```
OVERSEERR_API_KEY=your_api_key_here
OVERSEERR_URL=your_overseerr_url_here
```

Note: You can find the API key in the Overseerr settings under "API Keys".

## Quickstart

### Install

#### Overseerr API Key

You need an Overseerr instance running and an API key:
1. Navigate to your Overseerr installation
2. Go to Settings → General
3. Find the "API Key" section
4. Generate a new API key if you don't already have one

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`

On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  
```json
{
  "mcpServers": {
    "overseerr-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "<dir_to>/overseerr-mcp",
        "run",
        "overseerr-mcp"
      ],
      "env": {
        "OVERSEERR_API_KEY": "<your_api_key_here>",
        "OVERSEERR_URL": "<your_overseerr_url>"
      }
    }
  }
}
```
</details>

**Note: This MCP server is not yet published. Currently, only the development configuration is available.**

## Development

### Building

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).

You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory /path/to/overseerr-mcp run overseerr-mcp
```

Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.

You can also watch the server logs with this command:

```bash
tail -n 20 -f ~/Library/Logs/Claude/mcp-server-overseerr-mcp.log