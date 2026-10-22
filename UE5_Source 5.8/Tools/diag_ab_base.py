"""Diagnose why AB_HectorBase's state machine is not contributing to the pose."""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\diag_ab_base.txt"
ABP = "/Game/Characters/HectorBase/AB_HectorBase"
lines = []


def say(m):
    lines.append(str(m))


try:
    abp = unreal.EditorAssetLibrary.load_asset(ABP)
    say("abp = %s" % abp)
    say("root connected  = %s" % unreal.NobleAnimGraphAuthoring.is_root_connected(abp))
    say("machine in pose = %s" % unreal.NobleAnimGraphAuthoring.is_state_machine_connected(abp))

    for name in ("Locomotion", "Default", "AnimGraphNode_StateMachine_0"):
        sm = unreal.NobleAnimGraphAuthoring.get_or_create_state_machine(abp, name)
        say("machine '%s' -> %s states=%s" % (
            name, sm,
            unreal.NobleAnimGraphAuthoring.get_state_names(sm) if sm else None))

    say("--- dump ---")
    unreal.NobleAnimGraphAuthoring.dump_anim_graph(abp)

    sm = unreal.NobleAnimGraphAuthoring.get_or_create_state_machine(abp, "Locomotion")
    say("retry slot  = %s" % unreal.NobleAnimGraphAuthoring.connect_state_machine_to_slot(abp, sm))
    say("retry root  = %s" % unreal.NobleAnimGraphAuthoring.connect_root_to_state_machine(abp, sm))
    say("root now    = %s" % unreal.NobleAnimGraphAuthoring.is_root_connected(abp))
    say("in pose now = %s" % unreal.NobleAnimGraphAuthoring.is_state_machine_connected(abp))
    say("compiled    = %s" % unreal.NobleAnimGraphAuthoring.compile_anim_blueprint(abp))
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-DIAGAB] wrote %d lines" % len(lines))
