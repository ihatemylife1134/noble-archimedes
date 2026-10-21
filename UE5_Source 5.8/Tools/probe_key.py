"""Probe FKey and mapping construction."""

import unreal

LOG = "[NA-KEYTEST] "


def log(msg):
    unreal.log(LOG + str(msg))


k = unreal.Key()
log("empty key: %r dict=%r" % (k, k.to_dict()))
for prop in ("key_name", "KeyName"):
    try:
        k.set_editor_property(prop, "W")
        log("set_editor_property(%s) OK -> %r dict=%r" % (prop, k, k.to_dict()))
        break
    except Exception as exc:
        log("set_editor_property(%s) failed: %r" % (prop, exc))

# Try import_text
k2 = unreal.Key()
try:
    k2.import_text("W")
    log("import_text OK -> %r dict=%r" % (k2, k2.to_dict()))
except Exception as exc:
    log("import_text failed: %r" % exc)

# Try direct attribute
k3 = unreal.Key()
try:
    k3.key_name = "W"
    log("attr OK -> %r dict=%r" % (k3, k3.to_dict()))
except Exception as exc:
    log("attr failed: %r" % exc)

# Inspect available symbols for widgets
log("widget-related: " + ", ".join(n for n in dir(unreal) if "Widget" in n and "Library" in n))
log("InputMappingContext props: " + ", ".join(m for m in dir(unreal.InputMappingContext) if not m.startswith("_")))
