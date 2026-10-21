"""One-off introspection of UE 5.8 Python APIs used by the content pipeline."""

import unreal


def log(msg):
    unreal.log("[NA-API] " + str(msg))


def dump(name):
    obj = getattr(unreal, name, None)
    log("=== %s: %r ===" % (name, obj))
    if obj is not None:
        members = [m for m in dir(obj) if not m.startswith("_")]
        log(", ".join(members))


for n in sorted(dir(unreal)):
    if any(k in n for k in (
        "InputAction", "InputMapping", "DataTable", "BlueprintFactory",
        "WidgetBlueprint", "MaterialFactory", "NiagaraSystemFactory",
        "StaticMeshActor", "EditorActorSubsystem", "LevelEditorSubsystem",
        "UnrealEditorSubsystem", "AssetTools",
    )):
        log("symbol: " + n)

for n in ("DataTableFactory", "BlueprintFactory", "WidgetBlueprintFactory",
          "InputAction", "InputMappingContext", "DataTableFunctionLibrary",
          "EditorAssetLibrary", "AssetTools", "LevelEditorSubsystem",
          "EditorActorSubsystem", "UnrealEditorSubsystem"):
    dump(n)

log("create_asset doc: " + str(unreal.AssetToolsHelpers.get_asset_tools().create_asset.__doc__))
