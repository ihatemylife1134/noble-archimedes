#!/usr/bin/env python3
"""Import the trimmed ActorCore motions, replacing the 900-frame versions.

The trimmed FBXs contain only the motion (171 frames idle, 156 walk loop) with
the 900-frame reference-pose action removed. They are imported with the same
asset names as before, so the AnimBlueprint states that already point at those
clips pick up the trimmed data without any re-wiring.

Per CLAUDE.md rules 37 and 41: the skeleton must resolve first, and animation
imports are heavy, so calls are sequential with a pause between.
"""
import json
import os
import time
import traceback

import mcp_call

OUT = os.path.join(os.environ["TEMP"], "import_trimmed.txt")
SKELETON = "/Game/Characters/HectorBase/survival_character_Skeleton"
DEST = "/Game/Characters/HectorBase/ActorCore"
TRIMMED = r"C:\Projects\NobleArchimedes\ArtSource\ActorCore\Trimmed"
FILES = [
    ("AC_Idle.fbx", "AC_Idle"),
    ("AC_Walk_Loop.fbx", "AC_Walk_Loop"),
]
lines = []


def say(m):
    lines.append(str(m))


def call(command, params):
    response = mcp_call.call(command, params)
    return response.get("result", response)


try:
    say("skeleton = %s" % json.dumps(call(
        "does_asset_exist", {"asset_path": SKELETON})))

    for filename, name in FILES:
        full = os.path.join(TRIMMED, filename)
        if not os.path.exists(full):
            say("%-16s MISSING: %s" % (name, full))
            continue
        try:
            result = call("import_animation", {
                "source_path": full,
                "skeleton_path": SKELETON,
                "animation_name": name,
                "destination_path": DEST,
            })
            say("%-16s %s" % (name, json.dumps(result)[:320]))
        except Exception as exc:  # noqa: BLE001
            say("%-16s FAILED: %s" % (name, exc))
        time.sleep(4)

    say("")
    say("--- clips now in %s ---" % DEST)
    say(json.dumps(call("list_assets", {"path": DEST, "recursive": False}))[:1500])
except Exception:
    say("FAILED:")
    say(traceback.format_exc())

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("wrote %s" % OUT)
