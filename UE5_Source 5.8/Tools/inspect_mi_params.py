import unreal


def say(m):
    unreal.log_warning("[NA-MIPARAM] " + str(m))


paths = [
    "/Game/Art/Materials/Generated/MI_ClothRed",
    "/Game/Art/Materials/Generated/MI_StoneDark",
    "/Game/Art/Materials/Generated/MI_Stone",
]
for path in paths:
    mi = unreal.EditorAssetLibrary.load_asset(path)
    say("MI %s parent=%r" % (path, mi.get_editor_property("parent") if mi else None))
    if not mi:
        continue
    for name in ("BaseColorTex", "NormalTex", "ORMTex", "EmissiveTex",
                 "BaseTint", "Tiling", "Roughness", "Metallic", "EmissiveStrength"):
        for getter in ("get_texture_parameter_value", "get_vector_parameter_value",
                       "get_scalar_parameter_value"):
            try:
                value = getattr(mi, getter)(name)
                say("  %s.%s=%r" % (name, getter, value))
                break
            except Exception:
                continue
say("DONE")
