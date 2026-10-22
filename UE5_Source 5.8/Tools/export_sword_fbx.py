"""Export the Phase 1 sword source clips to FBX so they can be re-imported.

The ActionRPG clips are .uasset on SK_Mannequin_Skeleton. UE has no Python API to
change an animation's skeleton, so the working route is to export to FBX and
re-import onto the character's skeleton -- the same path proven with ActorCore.

The API is AssetTools.export_assets(assets, export_path, options); there is no
run_asset_export_task.
"""
import os

import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\sword_export.txt"
ANIM_DIR = "/Game/Characters/Animations"
OUT_DIR = r"C:\Projects\NobleArchimedes\ArtSource\ActionRPG\Exported"
# source clip -> the name it will be imported as
CLIPS = [
    ("Anim_Sword_Idle", "Sword_Idle"),
    ("Combat_Blade_Swing_Far", "Sword_Light1"),
    ("Attack03", "Sword_Light2"),
]
lines = []


def say(m):
    lines.append(str(m))


try:
    os.makedirs(OUT_DIR, exist_ok=True)
    tools = unreal.AssetToolsHelpers.get_asset_tools()

    for source_name, target_name in CLIPS:
        path = "%s/%s" % (ANIM_DIR, source_name)
        asset = unreal.EditorAssetLibrary.load_asset(path) if \
            unreal.EditorAssetLibrary.does_asset_exist(path) else None
        if not asset:
            say("%-24s MISSING" % source_name)
            continue

        out_fbx = os.path.join(OUT_DIR, "%s.fbx" % target_name)
        if os.path.exists(out_fbx):
            os.remove(out_fbx)

        # export_assets takes (assets_to_export, export_path) where the array is a
        # list of asset PATH STRINGS, not asset objects -- passing objects raises
        # "Cannot nativize 'AnimSequence' as 'String'".
        result = None
        try:
            result = tools.export_assets([asset.get_path_name()], OUT_DIR)
        except Exception as exc:  # noqa: BLE001
            say("%-24s export_assets failed: %s" % (source_name, exc))

        default_out = os.path.join(OUT_DIR, "%s.fbx" % source_name)
        if os.path.exists(default_out) and default_out != out_fbx:
            if os.path.exists(out_fbx):
                os.remove(out_fbx)
            os.rename(default_out, out_fbx)

        exists = os.path.exists(out_fbx)
        say("%-24s -> %-16s result=%s fbx=%s%s" % (
            source_name, target_name, result, exists,
            " (%.2f MB)" % (os.path.getsize(out_fbx) / 1048576.0) if exists else ""))
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-SWORDEXPORT] wrote %d lines" % len(lines))
