import unreal

names = [n for n in dir(unreal.MaterialEditingLibrary)
         if any(k in n.lower() for k in ("compile", "update", "instance", "shader"))]
unreal.log_warning("[NA-MCOMPILE] " + repr(names))
for cls_name in ("Texture2D", "EditorAssetLibrary"):
    cls = getattr(unreal, cls_name, None)
    if cls:
        names = [n for n in dir(cls) if any(k in n.lower() for k in ("export", "source", "platform", "pixel"))]
        unreal.log_warning("[NA-MCOMPILE] %s %r" % (cls_name, names))
