"""Rebuild AB_HectorBase so its states play the retargeted mocap clips.

add_state returns an existing state rather than replacing its sequence, so the
only way to move the states off the procedural clips is to rebuild the
AnimBlueprint. The mesh and anim class on BP_HectorCharacter keep pointing at
AB_HectorBase_C, which the rebuilt asset regenerates under the same name.
"""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\rebuild_ab.txt"
DIR = "/Game/Characters/HectorBase"
NAME = "AB_HectorBase"
MESH = "/Game/Characters/HectorBase/SK_HectorBase"
# Mocap first; the procedural clips are only a fallback now.
CLIP_CANDIDATES = {
    "Idle": ["/Game/Characters/HectorBase/Retargeted/RTG_anim_Idle",
             "/Game/Characters/HectorBase/Retargeted/RTG_AN_Hector_Idle"],
    "Walk": ["/Game/Characters/HectorBase/Retargeted/RTG_anim_Walk_Fwd_Loop_L",
             "/Game/Characters/HectorBase/Retargeted/RTG_AN_Hector_Walk"],
    "Run": ["/Game/Characters/HectorBase/Retargeted/RTG_anim_Jog_Loop_Fwd",
            "/Game/Characters/HectorBase/Retargeted/RTG_AN_Hector_Run"],
}
RULES = [
    ("Idle", "Walk", "bIsMoving", 0.1),
    ("Walk", "Run", "bIsRunning", 0.1),
    ("Walk", "Idle", "bIsIdle", 0.1),
    ("Run", "Idle", "bIsIdle", 0.1),
]
lines = []


def say(m):
    lines.append(str(m))


def load(path):
    return unreal.EditorAssetLibrary.load_asset(path) if \
        unreal.EditorAssetLibrary.does_asset_exist(path) else None


def pkg(asset):
    return asset.get_path_name().split(".")[0]


try:
    full = "%s/%s" % (DIR, NAME)
    if unreal.EditorAssetLibrary.does_asset_exist(full):
        say("deleting existing %s: %s" % (
            full, unreal.EditorAssetLibrary.delete_asset(full)))

    mesh = load(MESH)
    skeleton = mesh.get_editor_property("skeleton")
    factory = unreal.AnimBlueprintFactory()
    factory.set_editor_property("target_skeleton", skeleton)
    factory.set_editor_property("parent_class", unreal.AnimInstance)
    abp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        NAME, DIR, unreal.AnimBlueprint, factory)
    say("created %s on %s" % (pkg(abp) if abp else None,
                              skeleton.get_name() if skeleton else None))

    sm = unreal.NobleAnimGraphAuthoring.get_or_create_state_machine(abp, "Locomotion")
    states = {}
    for state_name, candidates in CLIP_CANDIDATES.items():
        clip = None
        for path in candidates:
            clip = load(path)
            if clip:
                say("state %-5s clip = %s" % (state_name, path.split("/")[-1]))
                break
        if not clip:
            say("state %s has NO clip (tried %s)" % (state_name, candidates))
            continue
        node = unreal.NobleAnimGraphAuthoring.add_state(sm, state_name, clip, True)
        unreal.NobleAnimGraphAuthoring.ensure_state_output_connected(sm, state_name)
        states[state_name] = node

    for var, default in (("bIsMoving", False), ("bIsRunning", False),
                         ("bIsIdle", True)):
        unreal.NobleAnimGraphAuthoring.add_bool_variable(abp, var, default)

    say("entry = %s" % unreal.NobleAnimGraphAuthoring.set_entry_state_by_name(sm, "Idle"))
    for src, dst, var, blend in RULES:
        if src in states and dst in states:
            trans = unreal.NobleAnimGraphAuthoring.add_transition(
                sm, states[src], states[dst], blend, False)
            say("transition %s->%s rule=%s ok=%s" % (
                src, dst, var,
                unreal.NobleAnimGraphAuthoring.set_transition_rule_variable(trans, var)))

    say("states = %s" % unreal.NobleAnimGraphAuthoring.get_state_names(sm))
    say("transitions = %d" % unreal.NobleAnimGraphAuthoring.get_transition_count(sm))

    # Slot must exist before the machine can feed it, and the slot name has to
    # match the montages' slot (DefaultSlot).
    say("slot pipeline = %s" % unreal.NobleAnimGraphAuthoring.ensure_slot_pipeline(
        abp, sm, unreal.Name("DefaultSlot")))
    say("root connected = %s" % unreal.NobleAnimGraphAuthoring.is_root_connected(abp))
    say("in pose        = %s" % unreal.NobleAnimGraphAuthoring.is_state_machine_connected(abp))
    say("compiled       = %s" % unreal.NobleAnimGraphAuthoring.compile_anim_blueprint(abp))
    say("saved          = %s" % unreal.EditorAssetLibrary.save_asset(
        pkg(abp), only_if_is_dirty=False))
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-REBUILDAB] wrote %d lines" % len(lines))
