#!/usr/bin/env python3
"""Diagnose Chapter 1 spawn geometry: player start vs room triggers vs barriers."""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\diag_ch1.txt"
lines = []


def say(msg):
    lines.append(str(msg))


def get_prop(obj, name, default=None):
    import re
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    for candidate in (snake, name):
        try:
            return obj.get_editor_property(candidate)
        except Exception:
            continue
    return default


LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

if not LES.load_level("/Game/Maps/Chap_01_AbandonedCastle"):
    say("FAILED to load map")
else:
    for actor in EAS.get_all_level_actors():
        cls = actor.get_class().get_name()
        label = str(actor.get_actor_label())
        loc = actor.get_actor_location()

        if cls.startswith("PlayerStart"):
            say("PlayerStart  %s loc=(%.0f, %.0f, %.0f)" % (label, loc.x, loc.y, loc.z))

        if cls.startswith("BP_Room"):
            box = get_prop(actor, "RoomTriggerBox")
            extent = None
            if box:
                extent = box.get_unscaled_box_extent() if hasattr(box, "get_unscaled_box_extent") else None
                try:
                    extent = box.get_editor_property("box_extent")
                except Exception:
                    pass
            say("Room %-14s loc=(%.0f, %.0f, %.0f) trigger_extent=%s locked=%s save=%s"
                % (get_prop(actor, "RoomName"), loc.x, loc.y, loc.z, extent,
                   get_prop(actor, "bIsLocked"), get_prop(actor, "bIsSaveRoom")))

            # Lock barrier placement tells us whether the seal matches the room.
            try:
                for comp in actor.get_components_by_class(unreal.StaticMeshComponent):
                    if str(comp.get_name()).startswith("LockBarrier"):
                        rloc = comp.get_relative_location()
                        scale = comp.get_relative_scale3d()
                        say("    %s rel=(%.0f, %.0f, %.0f) scale=(%.2f, %.2f, %.2f) vis=%s hidden=%s"
                            % (comp.get_name(), rloc.x, rloc.y, rloc.z,
                               scale.x, scale.y, scale.z,
                               comp.is_visible(), comp.get_editor_property("hidden_in_game")))
            except Exception as exc:
                say("    barrier read ERR %s" % exc)

        if "NavMeshBoundsVolume" in cls:
            scale = actor.get_actor_scale3d()
            say("NavMeshBounds loc=(%.0f, %.0f, %.0f) scale=(%.1f, %.1f, %.1f)"
                % (loc.x, loc.y, loc.z, scale.x, scale.y, scale.z))

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log_warning("[DIAGCH1] written %d lines" % len(lines))
