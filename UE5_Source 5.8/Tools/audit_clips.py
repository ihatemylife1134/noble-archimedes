"""Audit what the attack montages and locomotion clips actually are.

Hypothesis: the attack montages are the OLD stub-skeleton assets, carrying root
motion authored for the stub's orientation, which would spin the character back
90 degrees the moment one plays. Locomotion shows nothing for a related reason.
"""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\audit_clips.txt"
ABP = "/Game/Characters/HectorBase/AB_HectorBase"
lines = []


def say(m):
    lines.append(str(m))


def skel_of(asset):
    try:
        return asset.get_editor_property("skeleton").get_name()
    except Exception:  # noqa: BLE001
        return "?"


def prop(asset, name):
    try:
        return asset.get_editor_property(name)
    except Exception:  # noqa: BLE001
        return "n/a"


try:
    # --- attack montages -------------------------------------------------
    say("=== montages under /Game/Characters/Hector ===")
    for path in unreal.EditorAssetLibrary.list_assets(
            "/Game/Characters/Hector", recursive=True):
        name = path.split("/")[-1].split(".")[0]
        if not name.startswith("AM_"):
            continue
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if not asset:
            continue
        say("%-22s skeleton=%-28s slot=%-12s rootMotion=%s" % (
            name, skel_of(asset),
            prop(asset, "slot_anim_tracks") if False else "see below",
            prop(asset, "enable_root_motion")))
        try:
            tracks = asset.get_editor_property("slot_anim_tracks")
            names = []
            for t in tracks:
                names.append(str(t.get_editor_property("slot_name")))
            say("    slots = %s" % names)
        except Exception as exc:  # noqa: BLE001
            say("    slot read failed: %s" % exc)

    # --- the retargeted clips --------------------------------------------
    say("")
    say("=== retargeted clips on the new character ===")
    for path in unreal.EditorAssetLibrary.list_assets(
            "/Game/Characters/HectorBase/Retargeted", recursive=True):
        asset = unreal.EditorAssetLibrary.load_asset(path)
        if not asset:
            continue
        say("%-26s skeleton=%-28s len=%.2f rootMotion=%s" % (
            path.split("/")[-1].split(".")[0], skel_of(asset),
            prop(asset, "sequence_length") if isinstance(
                prop(asset, "sequence_length"), float) else -1.0,
            prop(asset, "enable_root_motion")))

    # --- what the state machine plays -------------------------------------
    say("")
    say("=== AB_HectorBase state -> clip ===")
    abp = unreal.EditorAssetLibrary.load_asset(ABP)
    sm = unreal.NobleAnimGraphAuthoring.get_or_create_state_machine(abp, "Locomotion")
    for state in unreal.NobleAnimGraphAuthoring.get_state_names(sm):
        say("  %-6s -> %s" % (
            state, unreal.NobleAnimGraphAuthoring.get_state_sequence_name(sm, state)))
    say("anim class on BP mesh = %s" % (
        unreal.get_default_object(
            unreal.EditorAssetLibrary.load_asset(
                "/Game/Blueprints/Characters/BP_HectorCharacter")
            .generated_class()).get_editor_property("mesh")
        .get_editor_property("anim_class")))

    # --- candidate clean sources -----------------------------------------
    say("")
    say("=== FreeAnimationLibrary candidates ===")
    hits = 0
    for path in unreal.EditorAssetLibrary.list_assets(
            "/Game/FreeAnimationLibrary", recursive=True):
        name = path.split("/")[-1].split(".")[0]
        low = name.lower()
        if any(k in low for k in ("idle", "walk", "jog", "run", "sword", "attack")):
            asset = unreal.EditorAssetLibrary.load_asset(path)
            if isinstance(asset, unreal.AnimSequence):
                say("%-34s skeleton=%-26s len=%.2f" % (
                    name, skel_of(asset), asset.get_editor_property("sequence_length")))
                hits += 1
                if hits >= 25:
                    break
    if not hits:
        say("  none found")
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-AUDITCLIPS] wrote %d lines" % len(lines))
