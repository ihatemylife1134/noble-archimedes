#!/usr/bin/env python3
"""Spike: author a two-state animation state machine through the editor module.

Proves the C++ authoring bridge (Tools cannot reach the state machine graph from
Python alone) end to end: create the machine, add states with sequence players,
wire the entry state and a transition, compile, and read the result back.

Output: C:\\Users\\Madi\\AppData\\Local\\Temp\\spike_sm.txt
"""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\spike_sm.txt"
ABP_PATH = "/Game/Characters/Hector/AB_Hector"
ANIM_DIR = "/Game/Characters/Hector/Animations"
lines = []


def say(msg):
    lines.append(str(msg))


def report(label, fn):
    try:
        result = fn()
        say("  %s -> OK %r" % (label, result))
        return result
    except Exception as exc:
        say("  %s -> FAIL %r" % (label, exc))
        return None


lib = getattr(unreal, "NobleAnimGraphAuthoring", None)
say("NobleAnimGraphAuthoring = %s" % lib)
say("members = %s" % ([m for m in dir(lib) if not m.startswith("_")] if lib else []))

abp = unreal.load_asset(ABP_PATH)
say("ABP = %s" % abp)

if lib and abp:
    idle = unreal.load_asset(ANIM_DIR + "/AN_Hector_Idle")
    walk = unreal.load_asset(ANIM_DIR + "/AN_Hector_Walk")
    say("idle=%s walk=%s" % (idle, walk))

    machine = report("get_or_create_state_machine",
                     lambda: lib.get_or_create_state_machine(abp, "LocomotionSpike"))
    say("machine = %s" % machine)

    if machine:
        idle_state = report("add_state Idle",
                            lambda: lib.add_state(machine, "SpikeIdle", idle, True))
        walk_state = report("add_state Walk",
                            lambda: lib.add_state(machine, "SpikeWalk", walk, True))
        say("states: idle=%s walk=%s" % (idle_state, walk_state))

        if idle_state:
            report("set_entry_state", lambda: lib.set_entry_state(machine, idle_state))

        if idle_state and walk_state:
            report("add_transition Idle->Walk",
                   lambda: lib.add_transition(machine, idle_state, walk_state, 0.1, False))
            report("add_transition Walk->Idle",
                   lambda: lib.add_transition(machine, walk_state, idle_state, 0.1, False))

        report("compile", lambda: lib.compile_anim_blueprint(abp))
        say("state names = %r" % (lib.get_state_names(machine),))
        say("transition count = %r" % (lib.get_transition_count(machine),))

unreal.EditorAssetLibrary.save_loaded_asset(abp) if abp else None

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log_warning("[SPIKE-SM] written %d lines" % len(lines))
