"""Recover AB_HectorBase after a failed delete-and-recreate, and wire its states.

create_asset returned None straight after delete_asset, most likely because the
deletion had not been flushed. This deletes, flushes with save_directory, then
recreates; if creation at the original path still refuses, it falls back to a new
asset name and repoints BP_HectorCharacter at whichever succeeded.
"""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\recover_ab.txt"
DIR = "/Game/Characters/HectorBase"
NAME = "AB_HectorBase"
FALLBACK = "AB_HectorBaseV2"
MESH = "/Game/Characters/HectorBase/SK_HectorBase"
CHAR_BP = "/Game/Blueprints/Characters/BP_HectorCharacter"
CLIP_CANDIDATES = {
    "Idle": ["/Game/Characters/HectorBase/Retargeted/RTG_anim_Idle",
             "/Game/Characters/HectorBase/Retargeted/RTG_AN_Hector_Idle"],
    "Walk": ["/Game/Characters/HectorBase/Retargeted/RTG_anim_Walk_Fwd_Loop_L",
             "/Game/Characters/HectorBase/Retargeted/RTG_AN_Hector_Walk"],
    "Run": ["/Game/Characters/HectorBase/Retargeted/RTG_anim_Jog_Loop_Fwd",
            "/Game/Characters/HectorBase/Retargeted/RTG_AN_Hector_Run"],
}
RULES = [("Idle", "Walk", "bIsMoving", 0.1), ("Walk", "Run", "bIsRunning", 0.1),
         ("Walk", "Idle", "bIsIdle", 0.1), ("Run", "Idle", "bIsIdle", 0.1)]
lines = []


def say(m):
    lines.append(str(m))


def load(path):
    return unreal.EditorAssetLibrary.load_asset(path) if \
        unreal.EditorAssetLibrary.does_asset_exist(path) else None


def pkg(a):
    return a.get_path_name().split(".")[0]


def create(name, skeleton):
    factory = unreal.AnimBlueprintFactory()
    factory.set_editor_property("target_skeleton", skeleton)
    factory.set_editor_property("parent_class", unreal.AnimInstance)
    return unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        name, DIR, unreal.AnimBlueprint, factory)


def build(abp, skeleton):
    sm = unreal.NobleAnimGraphAuthoring.get_or_create_state_machine(abp, "Locomotion")
    states = {}
    for state_name, candidates in CLIP_CANDIDATES.items():
        clip = None
        for path in candidates:
            clip = load(path)
            if clip:
                say("  %-5s clip = %s" % (state_name, path.split("/")[-1]))
                break
        if not clip:
            say("  %s has NO clip" % state_name)
            continue
        states[state_name] = unreal.NobleAnimGraphAuthoring.add_state(
            sm, state_name, clip, True)
        unreal.NobleAnimGraphAuthoring.ensure_state_output_connected(sm, state_name)
    for var, default in (("bIsMoving", False), ("bIsRunning", False), ("bIsIdle", True)):
        unreal.NobleAnimGraphAuthoring.add_bool_variable(abp, var, default)
    say("  entry = %s" % unreal.NobleAnimGraphAuthoring.set_entry_state_by_name(sm, "Idle"))
    for src, dst, var, blend in RULES:
        if src in states and dst in states:
            tr = unreal.NobleAnimGraphAuthoring.add_transition(
                sm, states[src], states[dst], blend, False)
            say("  %s->%s %s = %s" % (src, dst, var,
                unreal.NobleAnimGraphAuthoring.set_transition_rule_variable(tr, var)))
    say("  states = %s" % unreal.NobleAnimGraphAuthoring.get_state_names(sm))
    say("  slot pipeline = %s" % unreal.NobleAnimGraphAuthoring.ensure_slot_pipeline(
        abp, sm, unreal.Name("DefaultSlot")))
    say("  root = %s pose = %s compiled = %s" % (
        unreal.NobleAnimGraphAuthoring.is_root_connected(abp),
        unreal.NobleAnimGraphAuthoring.is_state_machine_connected(abp),
        unreal.NobleAnimGraphAuthoring.compile_anim_blueprint(abp)))
    unreal.EditorAssetLibrary.save_asset(pkg(abp), only_if_is_dirty=False)
    return sm


try:
    full = "%s/%s" % (DIR, NAME)
    say("exists before = %s" % unreal.EditorAssetLibrary.does_asset_exist(full))

    mesh = load(MESH)
    skeleton = mesh.get_editor_property("skeleton")

    # Recreate only if something is actually there to clear.
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        say("deleting: %s" % unreal.EditorAssetLibrary.delete_asset(full))
        unreal.EditorAssetLibrary.save_directory(DIR, only_if_is_dirty=False,
                                                 recursive=True)
        say("exists after delete = %s" % unreal.EditorAssetLibrary.does_asset_exist(full))

    abp = None
    for candidate in (NAME, FALLBACK, "AB_HectorBaseV3"):
        abp = create(candidate, skeleton)
        say("create '%s' -> %s" % (candidate, bool(abp)))
        if abp:
            break

    if not abp:
        raise RuntimeError("could not create an AnimBlueprint at all")

    build(abp, skeleton)

    # Make sure the Blueprint points at whatever actually exists.
    bp = load(CHAR_BP)
    cdo = unreal.get_default_object(bp.generated_class())
    comp = cdo.get_editor_property("mesh")
    comp.set_anim_instance_class(abp.generated_class())
    say("BP anim class = %s" % comp.get_editor_property("anim_class"))
    unreal.EditorAssetLibrary.save_asset(CHAR_BP.split(".")[0], only_if_is_dirty=False)
    say("saved BP")
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-RECOVERAB] wrote %d lines" % len(lines))
