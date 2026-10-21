import time

import unreal

MAP = "/Game/Maps/Chap_01_AbandonedCastle"


def say(msg):
    unreal.log_warning("[NA-LATE] " + str(msg))


les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les.load_level(MAP)
unreal.AutomationLibrary.finish_loading_before_screenshot()

try:
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    for command in ("ShowFlag.ActorIcons 0", "ShowFlag.Gizmos 0",
                    "ShowFlag.Selection 0", "ShowFlag.Billboard 0"):
        unreal.SystemLibrary.execute_console_command(world, command)
except Exception as exc:
    say("show flags failed: %r" % exc)

cam = eas.spawn_actor_from_class(
    unreal.CameraActor, unreal.Vector(0.0, -940.0, 300.0),
    unreal.Rotator(roll=0.0, pitch=-4.0, yaw=90.0))
cam.set_actor_label("NA_Capture_Late")
comp = cam.get_component_by_class(unreal.CameraComponent)
if comp:
    comp.set_editor_property("field_of_view", 90.0)

state = {"start": time.time(), "shot": False, "handle": None}


def tick(delta):
    elapsed = time.time() - state["start"]
    if not state["shot"] and elapsed >= 18.0:
        state["shot"] = True
        say("screenshot at %.1f" % elapsed)
        unreal.AutomationLibrary.take_high_res_screenshot(
            1600, 900, "NA_Chapter1_Late", camera=cam, mask_enabled=False,
            capture_hdr=False, comparison_tolerance=unreal.ComparisonTolerance.LOW,
            comparison_notes="late compile check", delay=0.0, force_game_view=True)
    if elapsed >= 30.0:
        say("quitting at %.1f" % elapsed)
        if state["handle"] is not None:
            unreal.unregister_slate_post_tick_callback(state["handle"])
        unreal.SystemLibrary.quit_editor()


state["handle"] = unreal.register_slate_post_tick_callback(tick)
say("scheduled")
