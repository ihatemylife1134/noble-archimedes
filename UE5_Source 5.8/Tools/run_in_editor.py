#!/usr/bin/env python3
"""Run a local Python file inside the LIVE Unreal editor via execute_python.

The executed code is a single `exec(open(...).read())` line, so the real script
lives on disk and can be long, versioned and edited normally instead of being
escaped into a JSON string.

Results are written to a file: PowerShell treats Python's stderr as a fatal error,
and the editor's own print output lands in the editor log rather than in the
command response.

Usage (path is fixed via the SLICE_SCRIPT constant to avoid argv quoting issues):
    python Tools/run_in_editor.py
"""
import json
import os

import mcp_call

SLICE_SCRIPT = r"C:\Projects\NobleArchimedes\Tools\sword_slice_live.py"
OUT = os.path.join(os.environ["TEMP"], "run_in_editor.txt")

code = "exec(open(r'%s').read())" % SLICE_SCRIPT.replace("\\", "/")

lines = []
try:
    response = mcp_call.call("execute_python", {"code": code}, timeout=300)
    lines.append("response: %s" % json.dumps(response))
except Exception as exc:  # noqa: BLE001
    lines.append("EXCEPTION: %s" % exc)

# The script writes its own report; surface it here too.
script_report = os.path.join(os.environ["TEMP"], "sword_slice.txt")
if os.path.exists(script_report):
    lines.append("")
    lines.append("--- script report ---")
    with open(script_report, encoding="utf-8") as fh:
        lines.append(fh.read())

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("wrote %s" % OUT)
