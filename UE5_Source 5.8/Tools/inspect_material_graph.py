import unreal


def say(m):
    unreal.log_warning("[NA-MGRAPH] " + str(m))


mat = unreal.EditorAssetLibrary.load_asset(
    "/Game/Art/Materials/Generated/M_NA_Surface_Master")
mate = unreal.MaterialEditingLibrary
exprs = mate.get_material_expressions(mat)
say("expressions=%d" % len(exprs))
for e in exprs:
    cls = e.get_class().get_name()
    name = ""
    try:
        name = e.get_editor_property("parameter_name")
    except Exception:
        pass
    say("%s name=%r" % (cls, name))
    for out in getattr(e, "outputs", []):
        say("  out %r -> %r" % (out.get_editor_property("output_name"), out))
say("DONE")
