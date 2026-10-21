import unreal


def say(msg):
    unreal.log_warning("[NA-LAYOUT] " + str(msg))


les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les.load_level("/Game/Maps/Chap_01_AbandonedCastle")
for a in eas.get_all_level_actors():
    cn = a.get_class().get_name()
    if cn in ("PlayerStart", "Room", "ChapterPortal", "BP_ChapterPortal_C", "TargetPoint"):
        loc = a.get_actor_location()
        rot = a.get_actor_rotation()
        say("%s %s loc=(%.1f,%.1f,%.1f) yaw=%.1f" % (
            cn, a.get_actor_label(), loc.x, loc.y, loc.z, rot.yaw))
say("DONE")
