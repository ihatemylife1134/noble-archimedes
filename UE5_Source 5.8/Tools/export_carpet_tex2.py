import unreal


def say(m):
    unreal.log_warning("[NA-EXPORT2] " + str(m))


tex = unreal.EditorAssetLibrary.load_asset(
    "/Game/Art/Generated/carpet/T_carpet_A")
out = r"C:\Projects\NobleArchimedes\Saved\Screenshots\WindowsEditor\T_carpet_A_export.png"
try:
    opts = unreal.ImageWriteOptions()
    tex.export_to_disk(out, opts)
    say("exported to %s" % out)
except Exception as exc:
    say("export failed: %r" % exc)
say("DONE")
