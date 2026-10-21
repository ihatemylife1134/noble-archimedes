import unreal


def say(m):
    unreal.log_warning("[NA-LIGHT] " + str(m))


les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les.load_level("/Game/Maps/Chap_01_AbandonedCastle")
for a in eas.get_all_level_actors():
    label = a.get_actor_label()
    if isinstance(a, unreal.PointLight):
        comp = a.get_component_by_class(unreal.PointLightComponent)
        if comp and (label.startswith("Light_") or label.startswith("Art_")):
            c = comp.get_editor_property("light_color")
            say("POINT %s intensity=%.1f radius=%.1f color=(%d,%d,%d)" % (
                label, comp.get_editor_property("intensity"),
                comp.get_editor_property("attenuation_radius"), c.r, c.g, c.b))
    elif isinstance(a, unreal.DirectionalLight):
        comp = a.get_component_by_class(unreal.DirectionalLightComponent)
        c = comp.get_editor_property("light_color")
        say("DIR %s intensity=%.2f color=(%d,%d,%d)" % (
            label, comp.get_editor_property("intensity"), c.r, c.g, c.b))
    elif isinstance(a, unreal.SkyLight):
        comp = a.get_component_by_class(unreal.SkyLightComponent)
        c = comp.get_editor_property("light_color")
        say("SKY %s intensity=%.2f color=(%d,%d,%d)" % (
            label, comp.get_editor_property("intensity"), c.r, c.g, c.b))
    elif isinstance(a, unreal.PostProcessVolume):
        s = a.get_editor_property("settings")
        for prop in ("bloom_intensity", "bloom_threshold", "vignette_intensity",
                     "film_grain_intensity", "color_grading_intensity",
                     "auto_exposure_bias", "auto_exposure_min_brightness",
                     "auto_exposure_max_brightness", "exposure_offset"):
            try:
                ov = s.get_editor_property("override_" + prop)
            except Exception:
                ov = "?"
            try:
                val = s.get_editor_property(prop)
            except Exception:
                val = "?"
            say("PP %s override=%r value=%r" % (prop, ov, val))
say("DONE")
