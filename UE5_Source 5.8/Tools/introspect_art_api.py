import unreal

def say(m): unreal.log_warning("[NA-API] " + str(m))

les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les.load_level("/Game/Maps/Chap_01_AbandonedCastle")
for a in eas.get_all_level_actors():
    if a.actor_has_tag("NA_ArtPass") and isinstance(a, unreal.ExponentialHeightFog):
        comp = a.get_component_by_class(unreal.ExponentialHeightFogComponent)
        props = [p for p in dir(comp) if not p.startswith("_")]
        interesting = [p for p in props if any(k in p.lower() for k in ("fog", "inscatter", "volumetric"))]
        say("FOG_PROPS=%r" % interesting)
    if a.actor_has_tag("NA_ArtPass") and isinstance(a, unreal.SkyLight):
        comp = a.get_component_by_class(unreal.SkyLightComponent)
        props = [p for p in dir(comp) if any(k in p.lower() for k in ("capture", "intensity", "color"))]
        say("SKY_PROPS=%r" % props)
    if a.actor_has_tag("NA_ArtPass") and isinstance(a, unreal.PostProcessVolume):
        settings = a.get_editor_property("settings")
        props = [p for p in dir(settings) if not p.startswith("_")]
        say("PP_PROPS=%r" % [p for p in props if any(k in p.lower() for k in ("bloom", "vignette", "grain", "color", "exposure"))])
    if a.actor_has_tag("NA_ArtPass") and isinstance(a, unreal.StaticMeshActor):
        comp = a.get_components_by_class(unreal.StaticMeshComponent)[0]
        mats = comp.get_editor_property("override_materials")
        paths = [str(m.get_path_name()) if m else None for m in mats]
        if a.get_actor_label() in ("Art_Pillar_01_0_0_0", "Art_Ceiling_01_0", "Art_Banner_01_0_-0.28", "Art_Runner_01_0"):
            say("MAT %s -> %r" % (a.get_actor_label(), paths))
say("DONE")
