import unreal

MAPS = [
    "Chap_01_AbandonedCastle",
    "Chap_02_BaljhetMountains",
    "Chap_03_GaribaldiTemple",
    "Chap_04_MortviaAqueduct",
    "Chap_05_ForestOfJigramunt",
    "Chap_06_CordovaTown",
    "Chap_07_EneomaosMachineTower",
    "Chap_08_AiolonRuins",
    "Chap_09_InfiniteCorridor",
    "Chap_10_DraculasCastle",
]


def say(m):
    unreal.log_warning("[NA-ALLART] " + str(m))


les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

for map_name in MAPS:
    path = "/Game/Maps/%s" % map_name
    if not les.load_level(path):
        say("%s LOAD_FAIL" % map_name)
        continue
    total = 0
    art = 0
    meshes = 0
    missing_mesh = 0
    missing_mat = 0
    lights = 0
    fog = 0
    pp = 0
    player_yaw = None
    for actor in eas.get_all_level_actors():
        total += 1
        label = actor.get_actor_label() or ""
        if actor.actor_has_tag("NA_ArtPass"):
            art += 1
        if isinstance(actor, unreal.StaticMeshActor):
            meshes += 1
            comp = actor.get_component_by_class(unreal.StaticMeshComponent)
            if comp:
                if not comp.get_editor_property("static_mesh"):
                    missing_mesh += 1
                try:
                    mat = comp.get_material(0)
                except Exception:
                    mat = None
                if not mat:
                    missing_mat += 1
        if isinstance(actor, unreal.PointLight):
            lights += 1
        if isinstance(actor, unreal.ExponentialHeightFog):
            fog += 1
        if isinstance(actor, unreal.PostProcessVolume):
            pp += 1
        if isinstance(actor, unreal.PlayerStart):
            player_yaw = actor.get_actor_rotation().yaw
    say("%s actors=%d art=%d meshes=%d missing_mesh=%d missing_mat=%d lights=%d fog=%d pp=%d yaw=%s" % (
        map_name, total, art, meshes, missing_mesh, missing_mat, lights, fog, pp, player_yaw))
say("DONE")
