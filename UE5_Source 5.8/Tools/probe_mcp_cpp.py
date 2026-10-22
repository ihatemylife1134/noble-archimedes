#!/usr/bin/env python3
"""Confirm that our own C++ helpers cannot be reached over the MCP channel.

The plugin exposes 123 named commands and no generic "call this function" or
"run this code" entry point, so a helper like
UNobleAnimGraphAuthoring::SetStateSequence has no route in. This sends that name
anyway and reports the raw response, with a known-working command alongside as a
control so a channel failure cannot be mistaken for a command failure.
"""
import json
import os
import traceback

import mcp_call

OUT = os.path.join(os.environ["TEMP"], "mcp_cpp_probe.txt")
lines = []


def say(m):
    lines.append(str(m))


def probe(command, params, label):
    try:
        response = mcp_call.call(command, params)
        say("%-26s %s" % (label, json.dumps(response)[:300]))
    except Exception as exc:  # noqa: BLE001
        say("%-26s EXCEPTION: %s" % (label, exc))


try:
    # Control: a real plugin command, to prove the channel itself works.
    probe("does_asset_exist",
          {"asset_path": "/Game/Characters/HectorBase/ActorCore/AC_Idle"},
          "control (plugin cmd)")

    # Our C++ helper, under several plausible names.
    probe("set_state_sequence",
          {"anim_blueprint_path": "/Game/Characters/HectorBase/AB_HectorBaseV2",
           "state_name": "Idle"}, "our helper: snake_case")
    probe("SetStateSequence",
          {"anim_blueprint_path": "/Game/Characters/HectorBase/AB_HectorBaseV2",
           "state_name": "Idle"}, "our helper: PascalCase")
    probe("noble_set_state_sequence",
          {"anim_blueprint_path": "/Game/Characters/HectorBase/AB_HectorBaseV2",
           "state_name": "Idle"}, "our helper: prefixed")

    # A generic escape hatch, if one existed.
    probe("execute_python", {"code": "print('hello')"}, "execute_python")
    probe("run_python", {"code": "print('hello')"}, "run_python")
    probe("execute_console_command", {"command": "stat fps"}, "console command")
except Exception:
    say("FAILED:")
    say(traceback.format_exc())

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("wrote %s" % OUT)
