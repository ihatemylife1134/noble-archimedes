"""Introspect Enhanced Input and Widget APIs."""

import unreal


def log(msg):
    unreal.log("[NA-API2] " + str(msg))


for n in ("Key", "InputActionValueType", "InputMappingContextMappingData",
          "InputModifierNegate", "InputModifierSwizzleAxis", "InputModifierDeadZone",
          "WidgetTree", "CanvasPanel", "TextBlock", "WidgetBlueprint",
          "MaterialEditingLibrary", "MaterialFactoryNew", "StaticMeshActor",
          "StaticMesh", "GameMapsSettings", "GameInstanceSettings"):
    obj = getattr(unreal, n, None)
    log("=== %s: %r ===" % (n, obj))
    if obj is not None:
        log(", ".join(m for m in dir(obj) if not m.startswith("_")))

log("Key doc: " + str(getattr(unreal, "Key", None).__doc__))
log("InputActionValueType values: " + str([v for v in dir(unreal.InputActionValueType) if not v.startswith("_")]))
log("map_key doc: " + str(unreal.InputMappingContext.map_key.__doc__))
log("construct_widget doc: " + str(getattr(unreal.WidgetTree, "construct_widget", None).__doc__))
