import unreal

for args in ((0, 90, 0), (0, 0, 90), (-50, -35, 0)):
    r = unreal.Rotator(*args)
    unreal.log_warning("[NA-ROT] args=%r -> roll=%.1f pitch=%.1f yaw=%.1f" % (
        args, r.roll, r.pitch, r.yaw))

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les.load_level("/Game/Maps/Chap_01_AbandonedCastle")
for a in eas.get_all_level_actors():
    if isinstance(a, unreal.PlayerStart):
        r = a.get_actor_rotation()
        unreal.log_warning("[NA-ROT] PlayerStart roll=%.1f pitch=%.1f yaw=%.1f" % (
            r.roll, r.pitch, r.yaw))
