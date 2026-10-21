import unreal


def say(m):
    unreal.log_warning("[NA-RUNNER] " + str(m))


les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
les.load_level("/Game/Maps/Chap_01_AbandonedCastle")
for a in eas.get_all_level_actors():
    label = a.get_actor_label()
    if label.startswith("Art_Runner") or label.startswith("Floor_"):
        loc = a.get_actor_location()
        scale = a.get_actor_scale3d()
        say("%s loc=(%.1f,%.1f,%.1f) scale=(%.2f,%.2f,%.2f)" % (
            label, loc.x, loc.y, loc.z, scale.x, scale.y, scale.z))
        comp = a.get_component_by_class(unreal.StaticMeshComponent)
        if comp:
            mesh = comp.get_editor_property("static_mesh")
            say("  mesh=%r" % (mesh,))
            for i in range(comp.get_num_materials()):
                mat = comp.get_material(i)
                say("  mat[%d]=%r" % (i, mat))
                if mat:
                    for prop in ("tint", "base_color", "roughness", "metallic",
                                 "tiling", "emissive_color"):
                        try:
                            say("    %s=%r" % (prop, mat.get_editor_property(prop)))
                        except Exception:
                            pass
say("DONE")
