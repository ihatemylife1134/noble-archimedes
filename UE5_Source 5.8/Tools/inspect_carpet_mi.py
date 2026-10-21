import unreal


def say(m):
    unreal.log_warning("[NA-CARPET] " + str(m))


mi = unreal.EditorAssetLibrary.load_asset(
    "/Game/Art/Materials/Generated/MI_Carpet")
say("mi=%r parent=%r" % (mi, mi.get_editor_property("parent") if mi else None))
for v in mi.get_editor_property("scalar_parameter_values"):
    say("scalar %s=%r" % (
        v.get_editor_property("parameter_info").get_editor_property("name"),
        v.get_editor_property("parameter_value")))
for v in mi.get_editor_property("vector_parameter_values"):
    say("vector %s=%r" % (
        v.get_editor_property("parameter_info").get_editor_property("name"),
        v.get_editor_property("parameter_value")))
for v in mi.get_editor_property("texture_parameter_values"):
    say("texture %s=%r" % (
        v.get_editor_property("parameter_info").get_editor_property("name"),
        v.get_editor_property("parameter_value")))
say("DONE")
