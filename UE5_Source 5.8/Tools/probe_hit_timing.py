#!/usr/bin/env python3
"""Verify per-attack hit timing is derived from each montage, not a flat constant."""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\hit_timing.txt"
lines = []


def say(msg):
    lines.append(str(msg))


bp_class = unreal.load_class(
    None, "/Game/Blueprints/Characters/BP_HectorCharacter.BP_HectorCharacter_C")
say("class = %s" % bp_class)
if bp_class:
    cdo = unreal.get_default_object(bp_class)
    combat = None
    for name in ("combat_component", "CombatComponent"):
        try:
            combat = cdo.get_editor_property(name)
            break
        except Exception:
            continue
    say("combat = %s" % combat)

    if combat:
        old = None
        for name in ("attack_hit_delay", "AttackHitDelay"):
            try:
                old = combat.get_editor_property(name)
                break
            except Exception:
                continue
        say("legacy flat AttackHitDelay = %r" % old)

        for stage in (1, 2, 3):
            try:
                delay = combat.get_attack_hit_delay(stage, False)
                say("combo stage %d hit delay = %.3fs" % (stage, delay))
            except Exception as exc:
                say("combo stage %d ERR %s" % (stage, exc))

        try:
            say("heavy stage 1 hit delay = %.3fs"
                % combat.get_attack_hit_delay(1, True))
        except Exception as exc:
            say("heavy ERR %s" % exc)

        say("hit fraction constant = %r" % getattr(combat, "AttackHitFraction", "?"))

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log_warning("[HITTIME] written %d lines" % len(lines))
