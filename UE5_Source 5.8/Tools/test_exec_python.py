#!/usr/bin/env python3
"""Test the execute_python command added to the vendored UnrealMCP plugin.

Two checks: that arbitrary Python runs in the live editor at all, and that it can
reach a project C++ helper (UNobleAnimGraphAuthoring), which no built-in plugin
command can do. Uses a read-only helper first so a failure cannot change state.
"""
import json
import os
import traceback

import mcp_call

OUT = os.path.join(os.environ["TEMP"], "exec_python_test.txt")
lines = []


def say(m):
    lines.append(str(m))


def run(label, code):
    try:
        response = mcp_call.call("execute_python", {"code": code})
        say("%-34s %s" % (label, json.dumps(response)[:400]))
    except Exception as exc:  # noqa: BLE001
        say("%-34s EXCEPTION: %s" % (label, exc))


try:
    run("trivial python", "print('NA-MCP python is alive')")

    run("read a project asset", (
        "import unreal\n"
        "abp = unreal.EditorAssetLibrary.load_asset("
        "'/Game/Characters/HectorBase/AB_HectorBaseV2')\n"
        "print('NA-MCP abp =', abp)"
    ))

    # The point of the exercise: our own C++ helper, unreachable by any other route.
    run("project C++ helper (read-only)", (
        "import unreal\n"
        "abp = unreal.EditorAssetLibrary.load_asset("
        "'/Game/Characters/HectorBase/AB_HectorBaseV2')\n"
        "sm = unreal.NobleAnimGraphAuthoring.get_or_create_state_machine(abp, 'Locomotion')\n"
        "for state in ('Idle', 'Walk', 'Run'):\n"
        "    print('NA-MCP', state, '->', "
        "unreal.NobleAnimGraphAuthoring.get_state_sequence_name(sm, state))\n"
        "print('NA-MCP root connected =', "
        "unreal.NobleAnimGraphAuthoring.is_root_connected(abp))\n"
    ))
except Exception:
    say("FAILED:")
    say(traceback.format_exc())

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("wrote %s" % OUT)
