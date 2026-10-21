import unreal


def say(msg):
    unreal.log_warning("[NA-LAYOUT2] " + str(msg))


les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les.load_level("/Game/Maps/Chap_01_AbandonedCastle")
counts = {}
for a in eas.get_all_level_actors():
    cn = a.get_class().get_name()
    counts[cn] = counts.get(cn, 0) + 1
say("CLASSES=%r" % sorted(counts.items()))
for a in eas.get_all_level_actors():
    cn = a.get_class().get_name()
    label = a.get_actor_label()
    if cn in ("StaticMeshActor", "PointLight", "SpotLight", "SkyLight", "ExponentialHeightFog",
              "PostProcessVolume", "PlayerStart", "BP_ChapterPortal_C") or "Room" in cn or "Enemy" in cn or "Boss" in cn:
        if cn in ("StaticMeshActor",) and label.startswith("Art_"):
            continue
        loc = a.get_actor_location()
        say("%s | %s | (%.0f,%.0f,%.0f)" % (cn, label, loc.x, loc.y, loc.z))
say("DONE")
