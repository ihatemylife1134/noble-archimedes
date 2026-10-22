#!/usr/bin/env python3
"""Import ActorCore motions directly onto the character's skeleton.

These FBXs carry a CC3+ rig that Reallusion's converter has already normalised
for UE (every UE-mannequin bone name is present, plus an explicit UE5 reference
pose action). Importing straight onto survival_character_Skeleton therefore
sidesteps the IK retargeter, which is producing static clips.

Per CLAUDE.md rules 37 and 41: the skeleton must resolve before the call, and
animation imports are heavy so calls are sequential with a pause between.
"""
import json
import os
import time
import traceback

import mcp_call

OUT = os.path.join(os.environ["TEMP"], "actorcore_import.txt")
SKELETON = "/Game/Characters/HectorBase/survival_character_Skeleton"
DEST = "/Game/Characters/HectorBase/ActorCore"
DOWNLOADS = os.path.join(os.environ["USERPROFILE"], "Downloads")
FILES = [
    (r"Actorcore-Unreal-1022-260107\Motion\male-idle_279398.fbx", "AC_Idle"),
    (r"Actorcore-Unreal-1022-261969\Motion\walk-relaxed-625493\walk-relaxed-1start-379003.fbx", "AC_Walk_Start"),
    (r"Actorcore-Unreal-1022-261969\Motion\walk-relaxed-625493\walk-relaxed-2loop-378986.fbx", "AC_Walk_Loop"),
    (r"Actorcore-Unreal-1022-261969\Motion\walk-relaxed-625493\walk-relaxed-3end-378968.fbx", "AC_Walk_End"),
]
lines = []


def say(m):
    lines.append(str(m))


def call(command, params):
    response = mcp_call.call(command, params)
    return response.get("result", response)


try:
    say("skeleton exists = %s" % json.dumps(call(
        "does_asset_exist", {"asset_path": SKELETON})))

    for relative, name in FILES:
        full = os.path.join(DOWNLOADS, relative)
        if not os.path.exists(full):
            say("%-14s MISSING on disk: %s" % (name, full))
            continue
        try:
            result = call("import_animation", {
                "source_path": full,
                "skeleton_path": SKELETON,
                "animation_name": name,
                "destination_path": DEST,
            })
            say("%-14s %s" % (name, json.dumps(result)[:300]))
        except Exception as exc:  # noqa: BLE001
            say("%-14s FAILED: %s" % (name, exc))
        time.sleep(4)  # heavy operation: let the engine settle

    say("")
    say("--- imported assets ---")
    say(json.dumps(call("list_assets", {"path": DEST, "recursive": False}))[:1200])
except Exception:
    say("FAILED:")
    say(traceback.format_exc())

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("wrote %s" % OUT)
