#!/usr/bin/env python3
"""Minimal client for the UnrealMCP plugin's TCP channel.

The plugin (Plugins/UnrealMCP, https://github.com/endlessblink/it-is-unreal)
listens on 127.0.0.1:55557 and speaks raw UTF-8 JSON: a request is
{"type": <command>, "params": {...}} with no length prefix, and the reply is read
until the accumulated bytes parse as JSON.

This bypasses the MCP layer entirely, so the editor can be driven straight from a
shell. Per the plugin's own safety rules (CLAUDE.md), calls must be strictly
sequential -- each command spawns an FTSTicker callback and overlapping callbacks
can crash the engine.

Usage:
    python mcp_call.py <command> ['{"json": "params"}']
    python mcp_call.py --list
"""
from __future__ import annotations

import json
import socket
import sys

HOST = "127.0.0.1"
PORT = 55557
BUFFER = 65536


def call(command: str, params: dict | None = None, timeout: float = 120.0) -> dict:
    """Send one command and return the parsed response."""
    with socket.create_connection((HOST, PORT), timeout=10.0) as sock:
        sock.settimeout(timeout)
        payload = json.dumps({"type": command, "params": params or {}})
        sock.sendall(payload.encode("utf-8"))

        chunks: list[bytes] = []
        while True:
            try:
                chunk = sock.recv(BUFFER)
            except socket.timeout:
                break
            if not chunk:
                break
            chunks.append(chunk)
            try:
                return json.loads(b"".join(chunks).decode("utf-8"))
            except json.JSONDecodeError:
                continue

        raw = b"".join(chunks)
        if not raw:
            raise RuntimeError("no response from the editor (is it running with the plugin loaded?)")
        return json.loads(raw.decode("utf-8"))


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    if sys.argv[1] == "--list":
        # Lightweight probe: confirms the channel is live.
        print(json.dumps(call("list_assets", {"path": "/Game/Characters/HectorBase"}),
                         indent=2)[:2000])
        return 0

    command = sys.argv[1]
    params = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    try:
        response = call(command, params)
    except Exception as exc:  # noqa: BLE001
        print("CALL FAILED: %s" % exc)
        return 1
    print(json.dumps(response, indent=2)[:6000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
