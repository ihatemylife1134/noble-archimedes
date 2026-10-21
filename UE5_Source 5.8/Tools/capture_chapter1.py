import time

import unreal

MAP = "/Game/Maps/Chap_01_AbandonedCastle"
OUT = "NA_Chapter1"


def say(msg):
    unreal.log_warning("[NA-CAPTURE] " + str(msg))


les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not les.load_level(MAP):
    raise RuntimeError("could not load " + MAP)

unreal.AutomationLibrary.finish_loading_before_screenshot()

# Hide editor-only actor billboards, gizmos and selection outlines so the
# screenshots read as game views rather than editor views.
try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for command in ("ShowFlag.ActorIcons 0", "ShowFlag.Gizmos 0",
                    "ShowFlag.Selection 0", "ShowFlag.Billboard 0"):
        unreal.SystemLibrary.execute_console_command(world, command)
except Exception as exc:
    say("show flag setup failed: %r" % exc)

views = [
    ("EntranceHall", unreal.Vector(0.0, -940.0, 300.0), -4.0, 90.0),
    ("Chapel", unreal.Vector(0.0, 2200.0, 300.0), -4.0, 90.0),
    ("BossArena", unreal.Vector(0.0, 4320.0, 360.0), -5.0, 90.0),
]

cams = []
for name, loc, pitch, yaw in views:
    cam = eas.spawn_actor_from_class(
        unreal.CameraActor, loc, unreal.Rotator(roll=0.0, pitch=pitch, yaw=yaw))
    cam.set_actor_label("NA_Capture_" + name)
    comp = cam.get_component_by_class(unreal.CameraComponent)
    if comp:
        comp.set_editor_property("field_of_view", 90.0)
    cams.append((name, cam))
    say("camera %s at %s" % (name, loc))

state = {"start": time.time(), "handle": None, "next": 0}
shot_times = (4.0, 9.0, 14.0)
quit_time = 22.0


def tick(delta):
    elapsed = time.time() - state["start"]
    if state["next"] < len(shot_times) and elapsed >= shot_times[state["next"]]:
        name, cam = cams[state["next"]]
        state["next"] += 1
        full = "%s_%s" % (OUT, name)
        say("screenshot %s at %.1fs" % (full, elapsed))
        unreal.AutomationLibrary.take_high_res_screenshot(
            1600, 900, full, camera=cam, mask_enabled=False, capture_hdr=False,
            comparison_tolerance=unreal.ComparisonTolerance.LOW,
            comparison_notes="Chapter 1 art pass", delay=0.0,
            force_game_view=True)
    if elapsed >= quit_time:
        say("quitting at %.1fs" % elapsed)
        if state["handle"] is not None:
            unreal.unregister_slate_post_tick_callback(state["handle"])
        unreal.SystemLibrary.quit_editor()


state["handle"] = unreal.register_slate_post_tick_callback(tick)
say("capture scheduled")
