"""MCP Stdio Server for Distributed ID Snowflake Generator.
100% Python Standard Library.
"""
import sys
import json
from client import SnowflakeIDGenerator

generator = SnowflakeIDGenerator()

def handle_rpc(line):
    try:
        req = json.loads(line)
    except Exception:
        return
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        res = {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "genpark-distributed-id-snowflake-generator-skill", "version": "1.0.1"},
            "capabilities": {"tools": {}}
        }
        send_response(req_id, res)
    elif method == "tools/list":
        tools = [
            {
                "name": "generate_id",
                "description": "Generate next unique 64-bit monotonically increasing Snowflake ID",
                "inputSchema": {"type": "object"}
            },
            {
                "name": "generate_batch",
                "description": "Generate batch of sequential unique 64-bit Snowflake IDs",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "default": 10}
                    }
                }
            },
            {
                "name": "parse_id",
                "description": "Decompose Snowflake ID into timestamp, worker ID, and sequence number",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "snowflake_id": {"type": "integer"}
                    },
                    "required": ["snowflake_id"]
                }
            }
        ]
        send_response(req_id, {"tools": tools})
    elif method == "tools/call":
        name = params.get("name")
        args = params.get("arguments", {})
        if name == "generate_id":
            out = {"snowflake_id": generator.generate_id()}
        elif name == "generate_batch":
            out = {"snowflake_ids": generator.generate_batch(int(args.get("count", 10)))}
        elif name == "parse_id":
            out = generator.parse_id(int(args.get("snowflake_id", 0)))
        else:
            send_error(req_id, -32601, f"Unknown tool: {name}")
            return
        send_response(req_id, {"content": [{"type": "text", "text": json.dumps(out, indent=2)}]})

def send_response(req_id, result):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}) + "\n")
    sys.stdout.flush()

def send_error(req_id, code, message):
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        if line.strip():
            handle_rpc(line.strip())

if __name__ == "__main__":
    main()
