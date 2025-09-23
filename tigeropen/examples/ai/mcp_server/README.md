# Tiger MCP Server

Tiger MCP Server 

## Quickstart

### Install [`uv`](https://docs.astral.sh/uv/getting-started/installation/)
uv is a Python package and project manager.

macOS/Linux, open a terminal and run:
```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Windows, open PowerShell as Administrator and run:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
  

### Configure TigerOpen API credentials environment variables
Set `TIGEROPEN_PROPS_PATH` to the path of your `tiger_openapi_config.properties` file, which contains tiger_id/private_key/account information.
```bash
export TIGEROPEN_PROPS_PATH="path/to/your/tiger_openapi_config.properties"
```

Alternatively, you can specify tiger_id/private_key/account directly
```bash
export TIGEROPEN_TIGER_ID="your Tiger ID"
export TIGEROPEN_PRIVATE_KEY="your private key"
export TIGEROPEN_ACCOUNT="your trading account"
```

Set `TIGERMCP_READONLY` to true if you want to run the server in read-only mode (no trading actions allowed).


### Run
```shell
uvx tigermcp 
```

### Run with Cursor/Claude/Trae
```json
{
  "mcpServers": {
    "tigermcp": {
      "command": "uvx",
      "args": ["tigermcp"],
      "env": {
        "TIGEROPEN_PROPS_PATH": "/path/to/your/tiger_openapi_config.properties"
      }
    }
  }
}
```

### FAQ

#### Error: `realpath: command not found`  

If your system is macOS 12 or lower, you may encounter the following error when running the mcp server:
```
/Users/tiger/.cache/uv/archive-v0/5iV7KVbKUQlypQW-eBHBn/bin/tigermcp: line 2: realpath: command not found
/Users/tiger/.cache/uv/archive-v0/5iV7KVbKUQlypQW-eBHBn/bin/tigermcp: line 2: /Users/tiger/python: No such file or directory
/Users/tiger/.cache/uv/archive-v0/5iV7KVbKUQlypQW-eBHBn/bin/tigermcp: line 2: exec: /Users/tiger/python: cannot execute: No such file or directory
```
you need to install `coreutils`:

If you don't have Homebrew installed, install it first by running the following command in your terminal:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Then, install `coreutils` by running:
```bash
brew install coreutils
``` 

### Release Notes
- 0.1.4 (2025-08-29) Fix issues
- 0.1.3 (2025-08-29) Fix issues
- 0.1.2 (2025-08-28) Fix issues
- 0.1.1 (2025-08-25) Initial release