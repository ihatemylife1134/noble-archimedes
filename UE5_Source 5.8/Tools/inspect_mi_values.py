import unreal


def say(m):
    unreal.log_warning("[NA-MIVAL] " + str(m))


for path in ("/Game/Art/Materials/Generated/MI_ClothRed",
             "/Game/Art/Materials/Generated/MI_StoneDark"):
    mi = unreal.EditorAssetLibrary.load_asset(path)
    say(path)
    for prop in ("scalar_parameter_values", "vector_parameter_values",
                 "texture_parameter_values"):
        try:
            values = mi.get_editor_property(prop)
        except Exception as exc:
            say("  %s error %r" % (prop, exc))
            continue
        for v in values:
            try:
                name = v.get_editor_property("parameter_info").get_editor_property("name")
            except Exception:
                name = "?"
            try:
                val = v.get_editor_property("parameter_value")
            except Exception:
                val = "?"
            say("  %s %s=%r" % (prop, name, val))
say("DONE")
