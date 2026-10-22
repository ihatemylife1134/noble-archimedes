#!/usr/bin/env python3
"""Create combat montages on the new character's skeleton.

The old AM_Hector_* montages are bound to SK_Hector_Skeleton (the stub), so they
cannot drive SK_HectorBase -- that is why attacks looked wrong. These are built
from clips already retargeted onto the new skeleton.

Calls are strictly sequential: each MCP command spawns its own FTSTicker callback
and overlapping callbacks can crash the engine (CLAUDE.md rules 9 and 30).
"""
import json
import os
import traceback

import mcp_call

OUT = os.path.join(os.environ["TEMP"], "attack_montages.txt")
DEST = "/Game/Characters/HectorBase/Montages"
CLIP_DIR = "/Game/Characters/HectorBase/Retargeted"
# The anim graph slot node is named DefaultSlot, matching the old AB_Hector's
# montages. The tool's default is the "DefaultGroup.DefaultSlot" path form.
SLOT = "DefaultSlot"

MONTAGES = [
    ("RTG_anim_Counter_Attack_01", "AM_HectorBase_Light1"),
    ("RTG_anim_Counter_Attack_08", "AM_HectorBase_Light2"),
    ("RTG_anim_Finisher_Attack_05", "AM_HectorBase_Light3"),
    ("RTG_AS_Spear_Attack_01", "AM_HectorBase_Heavy"),
    ("RTG_AN_Hector_Guard", "AM_HectorBase_Guard"),
    ("RTG_AN_Hector_QuickStep", "AM_HectorBase_QuickStep"),
    ("RTG_AN_Hector_HitReaction", "AM_HectorBase_HitReaction"),
    ("RTG_AN_Hector_Death", "AM_HectorBase_Death"),
    ("RTG_AN_Hector_Jump", "AM_HectorBase_Jump"),
]
lines = []


def say(m):
    lines.append(str(m))


try:
    for clip, montage in MONTAGES:
        try:
            response = mcp_call.call("create_anim_montage", {
                "animation_path": "%s/%s" % (CLIP_DIR, clip),
                "montage_name": montage,
                "destination_path": DEST,
                "slot_name": SLOT,
            })
            say("%-26s -> %s" % (montage, json.dumps(response)[:220]))
        except Exception as exc:  # noqa: BLE001
            say("%-26s FAILED: %s" % (montage, exc))

    say("")
    say("--- verify ---")
    response = mcp_call.call("list_assets", {"path": DEST, "recursive": False})
    result = response.get("result", response)
    say("count = %s" % result.get("count"))
    for asset in result.get("assets", []):
        say("  %-28s %s" % (asset.get("name"), asset.get("class")))
except Exception:
    say("FAILED:")
    say(traceback.format_exc())

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("wrote %s" % OUT)
