import unreal

def say(msg):
    unreal.log_warning("[NA-INSPECT] " + str(msg))

MAP = "/Game/Maps/Chap_01_AbandonedCastle"
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if not les.load_level(MAP):
    raise RuntimeError("failed to load %s" % MAP)

actors = eas.get_all_level_actors()
say("TOTAL_ACTORS=%d" % len(actors))
art = [a for a in actors if a.actor_has_tag("NA_ArtPass")]
say("ART_ACTORS=%d" % len(art))

classes = {}
for a in art:
    name = a.get_class().get_name()
    classes[name] = classes.get(name, 0) + 1
say("ART_CLASSES=%r" % sorted(classes.items()))

missing_mesh = []
no_material = []
static_count = 0
for a in art:
    if isinstance(a, unreal.StaticMeshActor):
        static_count += 1
        comps = a.get_components_by_class(unreal.StaticMeshComponent)
        if not comps:
            missing_mesh.append((a.get_actor_label(), "no component"))
            continue
        comp = comps[0]
        mesh = comp.get_editor_property("static_mesh")
        mats = comp.get_editor_property("override_materials")
        if not mesh:
            missing_mesh.append((a.get_actor_label(), "no mesh"))
        if not mats:
            no_material.append(a.get_actor_label())
say("STATIC_MESH_ACTORS=%d MISSING_MESH=%d NO_MATERIAL=%d" % (
    static_count, len(missing_mesh), len(no_material)))
say("MISSING_MESH_SAMPLE=%r" % missing_mesh[:10])
say("NO_MATERIAL_SAMPLE=%r" % no_material[:10])
for a in art[:6]:
    if isinstance(a, unreal.StaticMeshActor):
        comp = a.get_components_by_class(unreal.StaticMeshComponent)[0]
        say("MAT_SAMPLE %s -> %r" % (a.get_actor_label(),
                                     comp.get_editor_property("override_materials")))

for a in art:
    if isinstance(a, unreal.PointLight):
        comp = a.get_component_by_class(unreal.PointLightComponent)
        if comp:
            say("LIGHT %s intensity=%s radius=%s color=%s" % (
                a.get_actor_label(),
                comp.get_editor_property("intensity"),
                comp.get_editor_property("attenuation_radius"),
                comp.get_editor_property("light_color")))
            break

for a in art:
    if isinstance(a, unreal.ExponentialHeightFog):
        comp = a.get_component_by_class(unreal.ExponentialHeightFogComponent)
        if comp:
            for p in ("fog_density", "fog_height_falloff", "fog_inscattering_color",
                      "volumetric_fog_enabled", "volumetric_fog"):
                try:
                    say("FOG_PROP %s=%r" % (p, comp.get_editor_property(p)))
                except Exception as exc:
                    say("FOG_PROP %s MISSING (%s)" % (p, exc))
            break

for a in art:
    if isinstance(a, unreal.SkyLight):
        comp = a.get_component_by_class(unreal.SkyLightComponent)
        if comp:
            for p in ("intensity", "light_color", "real_time_capture"):
                try:
                    say("SKY_PROP %s=%r" % (p, comp.get_editor_property(p)))
                except Exception as exc:
                    say("SKY_PROP %s MISSING (%s)" % (p, exc))
            break

for a in art:
    if isinstance(a, unreal.PostProcessVolume):
        say("PP unbound=%r" % a.get_editor_property("unbound"))
        try:
            settings = a.get_editor_property("settings")
            say("PP settings_type=%s" % type(settings))
        except Exception as exc:
            say("PP settings error %s" % exc)
        break

# Blueprint CDO check.
bp = unreal.EditorAssetLibrary.load_asset("/Game/Blueprints/Characters/BP_HectorCharacter")
if bp:
    cls = bp.generated_class()
    cdo = unreal.get_default_object(cls)
    comp = cdo.get_editor_property("mesh")
    if isinstance(comp, unreal.SkeletalMeshComponent):
        say("HECTOR_SKEL_MESH=%s OVERRIDES=%s" % (
            comp.get_editor_property("skeletal_mesh_asset") if comp else None,
            comp.get_editor_property("override_materials") if comp else None))
    else:
        say("HECTOR_MESH_TYPE=%s" % type(comp))

say("INSPECT_DONE")
