# Tiger MCP Server

Tiger MCP Server 

## Quickstart

### Install 
```shell
mkdir demo
cd demo

# Create virtual environment and activate it
python -m venv .venv
source .venv/bin/activate
# or windows
# .venv\Scripts\activate

pip install tigermcp
```

### Configure TigerOpen API credentials environment variables

Method 1: Specify the configuration file
```bash
export TIGEROPEN_PROPS_PATH="path/to/your/tiger_openapi_config.properties"
```

Method 2: Specify tiger_id/private_key/account directly
```bash
export TIGEROPEN_TIGER_ID="your Tiger ID"
export TIGEROPEN_PRIVATE_KEY="your private key"
export TIGEROPEN_ACCOUNT="your trading account"
```

Set `TIGERMCP_READONLY` to true if you want to run the server in read-only mode (no trading actions allowed).



### Run
```shell
tigermcp 
```

### Run with Cursor/Claude/Trae


```json
{
  "mcpServers": {
    "tigermcp": {
      "command": "/path/to/tigermcp",
      "env": {
        "TIGEROPEN_PROPS_PATH": "/path/to/your/tiger_openapi_config.properties"
      }
    }
  }
}
```


