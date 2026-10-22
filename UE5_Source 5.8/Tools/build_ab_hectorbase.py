"""Build AB_HectorBase on the new character and point BP_HectorCharacter at it.

The new mesh uses a different Skeleton asset from the old stub, so AB_Hector
cannot drive it. This creates a fresh AnimBlueprint on survival_character_Skeleton
with the same variable contract the C++ bridge already writes (bIsMoving,
bIsRunning, bIsIdle), plays the retargeted clips, and swaps the mesh over.
"""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\build_ab_hectorbase.txt"
MESH = "/Game/Characters/HectorBase/SK_HectorBase"
DIR = "/Game/Characters/HectorBase"
ABP_NAME = "AB_HectorBase"
CLIP_CANDIDATES = {
    "Idle": ["/Game/Characters/HectorBase/Retargeted/RTG_anim_Idle",
             "/Game/Characters/HectorBase/Retargeted/RTG_AN_Hector_Idle"],
    "Walk": ["/Game/Characters/HectorBase/Retargeted/RTG_anim_Walk_Fwd_Loop_L",
             "/Game/Characters/HectorBase/Retargeted/RTG_AN_Hector_Walk"],
    "Run": ["/Game/Characters/HectorBase/Retargeted/RTG_anim_Jog_Loop_Fwd",
            "/Game/Characters/HectorBase/Retargeted/RTG_AN_Hector_Run"],
}
CHAR_BP = "/Game/Blueprints/Characters/BP_HectorCharacter"
lines = []


def say(m):
    lines.append(str(m))


def load(path):
    return unreal.EditorAssetLibrary.load_asset(path) if \
        unreal.EditorAssetLibrary.does_asset_exist(path) else None


def pkg(asset):
    return asset.get_path_name().split(".")[0]


try:
    mesh = load(MESH)
    if not mesh:
        raise RuntimeError("SK_HectorBase missing")
    skeleton = mesh.get_editor_property("skeleton")
    say("skeleton = %s" % (skeleton.get_name() if skeleton else None))
    if not skeleton:
        raise RuntimeError("mesh has no skeleton")

    abp = load("%s/%s" % (DIR, ABP_NAME))
    if not abp:
        factory = unreal.AnimBlueprintFactory()
        factory.set_editor_property("target_skeleton", skeleton)
        factory.set_editor_property("parent_class", unreal.AnimInstance)
        abp = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            ABP_NAME, DIR, unreal.AnimBlueprint, factory)
    say("abp = %s" % (pkg(abp) if abp else None))
    if not abp:
        raise RuntimeError("could not create AnimBlueprint")

    sm = unreal.NobleAnimGraphAuthoring.get_or_create_state_machine(abp, "Locomotion")
    say("state machine = %s" % (sm.get_name() if sm else None))
    if not sm:
        raise RuntimeError("no state machine")

    states = {}
    for name, candidates in CLIP_CANDIDATES.items():
        clip = None
        for path in candidates:
            clip = load(path)
            if clip:
                say("clip %-5s = %s" % (name, path))
                break
        if not clip:
            say("MISSING clip %s (tried %s)" % (name, candidates))
            continue
        state = unreal.NobleAnimGraphAuthoring.add_state(sm, name, clip, True)
        unreal.NobleAnimGraphAuthoring.ensure_state_output_connected(sm, name)
        states[name] = state
        say("state %-5s -> %s  (%s)" % (name, bool(state), clip.get_name()))

    for var, default in (("bIsMoving", False), ("bIsRunning", False),
                         ("bIsIdle", True)):
        say("var %-11s added=%s" % (
            var, unreal.NobleAnimGraphAuthoring.add_bool_variable(abp, var, default)))

    say("entry connected = %s" % unreal.NobleAnimGraphAuthoring.set_entry_state_by_name(
        sm, "Idle"))

    # AnimationBlueprintSpec.md: Idle -> Walk/Run blend 0.1s, Walk/Run -> Idle
    # 0.1s. A run->walk transition needs a "not running" rule, which the
    # bool-variable rule helper cannot express, so Run also exits on bIsIdle.
    rules = [
        ("Idle", "Walk", "bIsMoving", 0.1),
        ("Walk", "Run", "bIsRunning", 0.1),
        ("Walk", "Idle", "bIsIdle", 0.1),
        ("Run", "Idle", "bIsIdle", 0.1),
    ]
    for src, dst, var, blend in rules:
        if src not in states or dst not in states:
            say("skip transition %s->%s (missing state)" % (src, dst))
            continue
        trans = unreal.NobleAnimGraphAuthoring.add_transition(
            sm, states[src], states[dst], blend, False)
        ok = unreal.NobleAnimGraphAuthoring.set_transition_rule_variable(trans, var)
        say("transition %s->%s rule=%-10s ok=%s" % (src, dst, var, ok))

    say("states = %s" % unreal.NobleAnimGraphAuthoring.get_state_names(sm))
    say("transitions = %d" % unreal.NobleAnimGraphAuthoring.get_transition_count(sm))
    say("root connected = %s" % unreal.NobleAnimGraphAuthoring.is_root_connected(abp))
    say("slot connected = %s" % unreal.NobleAnimGraphAuthoring.connect_state_machine_to_slot(
        abp, sm))
    say("machine in pose = %s" % unreal.NobleAnimGraphAuthoring.is_state_machine_connected(abp))
    say("compiled = %s" % unreal.NobleAnimGraphAuthoring.compile_anim_blueprint(abp))
    unreal.EditorAssetLibrary.save_asset(pkg(abp), only_if_is_dirty=False)
    say("saved %s" % pkg(abp))

    # Point the player Blueprint at the new mesh and its AnimBlueprint. The
    # component archetype is the Blueprint's own template, so editing it here is
    # the same as changing the defaults in the editor.
    char_bp = load(CHAR_BP)
    if not char_bp:
        say("character BP not found at %s" % CHAR_BP)
    else:
        cdo = unreal.get_default_object(char_bp.generated_class())
        comp = None
        for prop in ("mesh", "Mesh"):
            try:
                comp = cdo.get_editor_property(prop)
                break
            except Exception:  # noqa: BLE001
                continue
        say("mesh component = %s" % (comp.get_name() if comp else None))
        if comp:
            try:
                say("mesh before = %s" % comp.get_editor_property("skeletal_mesh_asset"))
            except Exception as exc:  # noqa: BLE001
                say("mesh read failed: %s" % exc)
            comp.set_editor_property("skeletal_mesh_asset", mesh)
            try:
                comp.set_anim_instance_class(abp.generated_class())
                say("anim class set")
            except Exception as exc:  # noqa: BLE001
                say("anim class set failed: %s" % exc)
            say("mesh after  = %s" % comp.get_editor_property("skeletal_mesh_asset"))
            say("anim class  = %s" % comp.get_editor_property("anim_class"))
            unreal.EditorAssetLibrary.save_asset(pkg(char_bp), only_if_is_dirty=False)
            say("saved %s" % pkg(char_bp))
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-ABHECTORBASE] wrote %d lines" % len(lines))
