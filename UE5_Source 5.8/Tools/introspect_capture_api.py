import unreal


def say(msg):
    unreal.log_warning("[NA-CAPAPI] " + str(msg))


for cls_name in ("AutomationLibrary", "EditorLevelLibrary", "LevelEditorSubsystem",
                 "EditorScreenshotLibrary", "EditorAssetLibrary", "UnrealEditorSubsystem"):
    cls = getattr(unreal, cls_name, None)
    if not cls:
        say("%s missing" % cls_name)
        continue
    names = [n for n in dir(cls) if any(k in n.lower() for k in
             ("screenshot", "play", "simulate", "viewport", "render", "capture", "quit"))]
    say("%s: %r" % (cls_name, names))
