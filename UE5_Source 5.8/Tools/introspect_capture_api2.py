import unreal


def say(msg):
    unreal.log_warning("[NA-CAPAPI2] " + str(msg))


for name in ("take_high_res_screenshot", "take_automation_screenshot",
             "take_automation_screenshot_at_camera", "finish_loading_before_screenshot"):
    fn = getattr(unreal.AutomationLibrary, name, None)
    if fn:
        say("%s doc=%r" % (name, getattr(fn, "__doc__", None)))

for cls_name in ("SystemLibrary", "KismetSystemLibrary"):
    cls = getattr(unreal, cls_name, None)
    if cls:
        names = [n for n in dir(cls) if any(k in n.lower() for k in ("quit", "exit", "console", "execute"))]
        say("%s quit/exec: %r" % (cls_name, names))

say("slate_register=%r" % hasattr(unreal, "register_slate_post_tick_callback"))
say("slate_unregister=%r" % hasattr(unreal, "unregister_slate_post_tick_callback"))
