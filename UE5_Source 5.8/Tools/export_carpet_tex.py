import unreal


def say(m):
    unreal.log_warning("[NA-EXPORT] " + str(m))


tex = unreal.EditorAssetLibrary.load_asset(
    "/Game/Art/Generated/carpet/T_carpet_A")
say("tex=%r" % tex)
say("doc=%r" % getattr(tex.export_to_disk, "__doc__", None))
for prop in ("source_file", "source_color_settings", "never_stream",
             "srgb", "compression_settings", "lod_group"):
    try:
        say("%s=%r" % (prop, tex.get_editor_property(prop)))
    except Exception as exc:
        say("%s error %r" % (prop, exc))
try:
    say("source_id=%r" % tex.blueprint_get_texture_source_id_string())
except Exception as exc:
    say("source_id error %r" % exc)
say("DONE")
