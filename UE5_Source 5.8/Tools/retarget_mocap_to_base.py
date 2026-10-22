"""Replace the procedural locomotion clips with mannequin mocap, 29->29.

The procedural clips came from the old stub rig through only 13 shared bone
names, which is why locomotion shows almost no motion and attack poses are
mangled. The Free Animation Library clips are on the UE mannequin, which maps
1:1 onto the new character's chains.

The retargeted outputs deliberately reuse the existing clip names
(RTG_AN_Hector_Idle/Walk/Run) so the state machine picks them up with no graph
edits: the authoring helper returns an existing state rather than replacing its
sequence, so the asset has to change instead of the graph.
"""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\retarget_mocap.txt"
SRC_DIR = "/Game/FreeAnimationLibrary"
OUT_DIR = "/Game/Characters/HectorBase/Retargeted"
SRC_MESH = "/Game/FreeAnimationLibrary/Demo/Characters/Mannequins/Meshes/SKM_Manny_Simple"
DST_MESH = "/Game/Characters/HectorBase/SK_HectorBase"
RIG = "/Game/Characters/HectorBase/Retarget/RTG_HectorBase"

# source clip name -> output clip name
MAP = {
    "anim_Idle": "RTG_AN_Hector_Idle",
    "anim_Walk_Fwd_Loop_L": "RTG_AN_Hector_Walk",
    "anim_Jog_Loop_Fwd": "RTG_AN_Hector_Run",
    # kept for the attack montages that still need building
    "anim_Counter_Attack_01": "RTG_anim_Attack_1",
    "anim_Counter_Attack_08": "RTG_anim_Attack_2",
    "anim_Finisher_Attack_05": "RTG_anim_Attack_3",
    "AS_Spear_Attack_01": "RTG_anim_Attack_Heavy",
}
lines = []


def say(m):
    lines.append(str(m))


def load(path):
    return unreal.EditorAssetLibrary.load_asset(path) if \
        unreal.EditorAssetLibrary.does_asset_exist(path) else None


def pkg(asset):
    return asset.get_path_name().split(".")[0]


try:
    src_mesh = load(SRC_MESH)
    dst_mesh = load(DST_MESH)
    rig = load(RIG)
    say("src mesh=%s dst mesh=%s retargeter=%s" % (
        bool(src_mesh), bool(dst_mesh), bool(rig)))
    if not all((src_mesh, dst_mesh, rig)):
        raise RuntimeError("missing inputs")

    # Locate the source clips by name.
    found = {}
    for path in unreal.EditorAssetLibrary.list_assets(SRC_DIR, recursive=True):
        name = path.split("/")[-1].split(".")[0]
        if name in MAP and name not in found:
            found[name] = path
    say("located %d/%d source clips" % (len(found), len(MAP)))
    for name in MAP:
        say("  %-24s %s" % (name, found.get(name, "MISSING")))

    assets = []
    for name in MAP:
        if name in found:
            assets.append(unreal.EditorAssetLibrary.find_asset_data(found[name]))
    say("retargeting %d clips" % len(assets))
    if assets:
        created = unreal.IKRetargetBatchOperation.duplicate_and_retarget(
            assets, src_mesh, dst_mesh, rig,
            target_path=OUT_DIR, prefix="RTG_", overwrite_existing_files=True)
        say("batch returned %d" % (len(created) if created else 0))
        for asset in (created or []):
            say("  %s" % asset.package_name)
        say("save_directory = %s" % unreal.EditorAssetLibrary.save_directory(
            OUT_DIR, only_if_is_dirty=False, recursive=True))

    # The batch names outputs after the sources; rename the three locomotion
    # ones onto the names the state machine already plays.
    renames = [
        ("RTG_anim_Idle", "RTG_AN_Hector_Idle"),
        ("RTG_anim_Walk_Fwd_Loop_L", "RTG_AN_Hector_Walk"),
        ("RTG_anim_Jog_Loop_Fwd", "RTG_AN_Hector_Run"),
    ]
    for old, new in renames:
        old_path = "%s/%s" % (OUT_DIR, old)
        if unreal.EditorAssetLibrary.does_asset_exist(old_path):
            say("rename %s -> %s : %s" % (
                old, new,
                unreal.EditorAssetLibrary.rename_asset(
                    old_path, "%s/%s" % (OUT_DIR, new))))
        else:
            say("rename skipped, %s absent" % old_path)

    say("save_directory again = %s" % unreal.EditorAssetLibrary.save_directory(
        OUT_DIR, only_if_is_dirty=False, recursive=True))
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-RETARGETMOCAP] wrote %d lines" % len(lines))
