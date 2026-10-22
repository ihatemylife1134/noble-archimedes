"""Phase 1 sword slice, run inside the LIVE editor via execute_python.

Exports three ActionRPG sword clips to FBX, imports them onto the character's
skeleton, builds the two attack montages, and repoints the weapon DataTable so the
light-attack combo plays them.

Why FBX rather than direct use: the ActionRPG clips are .uasset bound to
SK_Mannequin_Skeleton, and UE has no Python API to change an animation's
skeleton. Exporting and re-importing is the route already proven with ActorCore.

Run with:
    python Tools/mcp_call.py execute_python
      '{"code": "exec(open(r\'C:/Projects/NobleArchimedes/Tools/sword_slice_live.py\').read())"}'
"""
import os

import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\sword_slice.txt"
ANIM_DIR = "/Game/Characters/Animations"
EXPORT_DIR = r"C:\Projects\NobleArchimedes\ArtSource\ActionRPG\Exported"
DEST = "/Game/Characters/HectorBase/Sword"
SKELETON = "/Game/Characters/HectorBase/survival_character_Skeleton"
TABLE = "/Game/DataTables/DT_WeaponDataTable"
MONTAGE_DIR = "/Game/Characters/HectorBase/Montages"
BONES = ["thigh_l", "upperarm_r", "hand_r"]

# source clip -> (imported asset name, montage name or None for a plain clip)
CLIPS = [
    ("Anim_Sword_Idle", "Sword_Idle", None),
    ("Combat_Blade_Swing_Far", "Sword_Light1", "AM_HectorBase_Sword_Light1"),
    ("Attack03", "Sword_Light2", "AM_HectorBase_Sword_Light2"),
]
lines = []


def say(m):
    lines.append(str(m))
    print("NA-SLICE %s" % m)


def load(path):
    return unreal.EditorAssetLibrary.load_asset(path) if \
        unreal.EditorAssetLibrary.does_asset_exist(path) else None


def moves(clip):
    """Five-point motion check; two points cannot tell static from a cycle phase."""
    frames = unreal.AnimationLibrary.get_num_frames(clip)
    points = [int(frames * i / 4) for i in range(5)]
    fn = unreal.AnimationLibrary.get_bone_pose_for_frame
    for bone in BONES:
        values = set()
        for f in points:
            try:
                pose = fn(clip, bone, f, False)
                values.add((round(pose.rotation.x, 4), round(pose.rotation.y, 4),
                            round(pose.rotation.z, 4), round(pose.rotation.w, 4)))
            except Exception:  # noqa: BLE001
                return False
        if len(values) > 1:
            return True
    return False


try:
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    os.makedirs(EXPORT_DIR, exist_ok=True)

    # --- 1. export source clips to FBX -----------------------------------
    say("=== export ===")
    for source, target, _ in CLIPS:
        src_path = "%s/%s" % (ANIM_DIR, source)
        asset = load(src_path)
        if not asset:
            say("%-24s MISSING" % source)
            continue
        # export_assets wants asset PATH STRINGS; objects raise
        # "Cannot nativize 'AnimSequence' as 'String'".
        try:
            tools.export_assets([asset.get_path_name()], EXPORT_DIR)
        except Exception as exc:  # noqa: BLE001
            say("%-24s export failed: %s" % (source, exc))
        produced = os.path.join(EXPORT_DIR, "%s.fbx" % source)
        want = os.path.join(EXPORT_DIR, "%s.fbx" % target)
        if os.path.exists(produced) and produced != want:
            if os.path.exists(want):
                os.remove(want)
            os.rename(produced, want)
        say("%-24s -> %-18s %s" % (
            source, target,
            "%.2f MB" % (os.path.getsize(want) / 1048576.0) if os.path.exists(want) else "NO FBX"))

    # export_assets treats the path as a BASE DIRECTORY and appends the asset's
    # folder structure, so the file lands at
    # <base>/Game/Characters/Animations/<Name>.FBX rather than in <base>.
    say("")
    say("=== relocating exported files ===")
    for source, target, _ in CLIPS:
        found = None
        for root, _dirs, files in os.walk(EXPORT_DIR):
            for name in files:
                if name.lower() == ("%s.fbx" % source).lower():
                    found = os.path.join(root, name)
                    break
            if found:
                break
        if not found:
            say("%-24s not found anywhere under the export dir" % source)
            continue
        want = os.path.join(EXPORT_DIR, "%s.fbx" % target)
        if os.path.normcase(found) != os.path.normcase(want):
            if os.path.exists(want):
                os.remove(want)
            os.rename(found, want)
        say("%-24s -> %-18s %.2f MB" % (
            source, target, os.path.getsize(want) / 1048576.0))
except Exception as exc:
    say("FAILED in export: %s" % exc)
# --- 2. import onto the character's skeleton --------------------------
say("")
say("=== import ===")
skeleton = load(SKELETON)
imported = {}
for source, target, _ in CLIPS:
    fbx = os.path.join(EXPORT_DIR, "%s.fbx" % target)
    if not os.path.exists(fbx):
        say("%-24s no FBX to import" % target)
        continue
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", fbx)
    task.set_editor_property("destination_path", DEST)
    task.set_editor_property("destination_name", target)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", True)
    options = unreal.FbxImportUI()
    options.set_editor_property("import_mesh", False)
    options.set_editor_property("import_animations", True)
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    options.set_editor_property("skeleton", skeleton)
    options.set_editor_property("mesh_type_to_import",
                                unreal.FBXImportType.FBXIT_ANIMATION)
    task.set_editor_property("options", options)
    try:
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    except Exception as exc:  # noqa: BLE001
        say("%-24s import failed: %s" % (target, exc))
    clip = load("%s/%s" % (DEST, target))
    if clip:
        frames = unreal.AnimationLibrary.get_num_frames(clip)
        animating = moves(clip)
        imported[target] = clip
        say("%-24s %d frames, animates = %s" % (target, frames, animating))
    else:
        say("%-24s import produced no asset" % target)

# --- 3. build the attack montages -------------------------------------
say("")
say("=== montages ===")
tools = unreal.AssetToolsHelpers.get_asset_tools()
montages = {}
for source, target, montage_name in CLIPS:
    if not montage_name:
        continue
    clip = imported.get(target)
    if not clip:
        say("%-34s skipped, clip missing" % montage_name)
        continue
    existing = "%s/%s" % (MONTAGE_DIR, montage_name)
    if unreal.EditorAssetLibrary.does_asset_exist(existing):
        say("%-34s already exists, left alone" % montage_name)
        montages[target] = load(existing)
        continue
    factory = unreal.AnimMontageFactory()
    factory.set_editor_property("source_animation", clip)
    factory.set_editor_property("target_skeleton", skeleton)
    created = tools.create_asset(montage_name, MONTAGE_DIR, unreal.AnimMontage, factory)
# --- 4. repoint the weapon table so the combo plays them --------------
say("")
say("=== data table ===")
try:
    table = load(TABLE)
    light1 = montages.get("Sword_Light1")
    light2 = montages.get("Sword_Light2")
    if not table or not light1 or not light2:
        say("cannot repoint: table=%s light1=%s light2=%s" % (
            bool(table), bool(light1), bool(light2)))
    else:
        combo = [light1.get_path_name(), light2.get_path_name(), light2.get_path_name()]
        # The heavy finisher still points at a montage built from a static clip;
        # reusing Light2 keeps heavy attacks visible until Phase 1 items 5-7 land.
        final = [light2.get_path_name()] * 3
        rows = unreal.NobleDataTableAuthoring.get_row_names(table)
        problems = 0
        for row in rows:
            error = unreal.NobleDataTableAuthoring.set_weapon_row_montages(
                table, row, combo, final)
            if error:
                problems += 1
                say("  %-22s %s" % (row, error))
        say("rows = %d, problems = %d" % (len(rows), problems))
        say("sample: %s" % unreal.NobleDataTableAuthoring.describe_weapon_row_montages(
            table, rows[0]))
        say("saved = %s" % unreal.EditorAssetLibrary.save_loaded_asset(
            table, only_if_is_dirty=False))
except Exception as exc:  # noqa: BLE001
    say("data table step failed: %s" % exc)

say("")
say("=== summary ===")
for source, target, montage_name in CLIPS:
    say("%-14s clip=%s montage=%s" % (
        target,
        "yes" if target in imported else "NO",
        montage_name or "(state clip only)"))

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))

    if created:
        slots = []
        try:
            for t in created.get_editor_property("slot_anim_tracks"):
                slots.append(str(t.get_editor_property("slot_name")))
        except Exception:  # noqa: BLE001
            pass
        montages[target] = created
        say("%-34s created, slots=%s" % (montage_name, slots))
    else:
        say("%-34s FAILED to create" % montage_name)

unreal.EditorAssetLibrary.save_directory(MONTAGE_DIR, only_if_is_dirty=False, recursive=True)
unreal.EditorAssetLibrary.save_directory(DEST, only_if_is_dirty=False, recursive=True)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))


with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
