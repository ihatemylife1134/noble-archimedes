"""Probe Enhanced Input mapping behaviour in UE 5.8 Python."""

import unreal

LOG = "[NA-INPUTTEST] "


def log(msg):
    unreal.log(LOG + str(msg))


asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

# Create a scratch input action + mapping context.
ia_factory = unreal.InputAction_Factory()
ia = asset_tools.create_asset("IA_Test", "/Game/__Scratch", unreal.InputAction, ia_factory)
ia.set_editor_property("value_type", unreal.InputActionValueType.AXIS2D)
log("IA created: %r value_type=%r" % (ia, ia.get_editor_property("value_type")))

imc_factory = unreal.InputMappingContext_Factory()
imc = asset_tools.create_asset("IMC_Test", "/Game/__Scratch", unreal.InputMappingContext, imc_factory)
log("IMC created: %r" % imc)

try:
    key = unreal.Key(key_name="W")
    log("Key constructed: %r %r" % (key, key.to_dict()))
except Exception as exc:
    log("Key construction failed: %r" % exc)
    key = None

if key is not None:
    try:
        mapping = imc.map_key(ia, key)
        log("map_key returned %r" % mapping)
        log("mapping dir: %s" % ", ".join(m for m in dir(mapping) if not m.startswith("_")))
        for prop in ("action", "key", "modifiers", "triggers"):
            try:
                log("mapping.%s = %r" % (prop, mapping.get_editor_property(prop)))
            except Exception as exc:
                log("mapping.%s missing: %r" % (prop, exc))
    except Exception as exc:
        log("map_key failed: %r" % exc)

log("mappings after map_key: %r" % imc.get_editor_property("mappings"))
log("mapping count: %r" % imc.get_editor_property("mappings").__len__())

# Try adding a modifier through the mappings array.
try:
    mappings = imc.get_editor_property("mappings")
    mod = unreal.InputModifierNegate()
    mod.set_editor_property("x", True)
    mod.set_editor_property("y", True)
    mod.set_editor_property("z", False)
    mappings[0].set_editor_property("modifiers", [mod])
    imc.set_editor_property("mappings", mappings)
    log("mappings after modifier set: %r" % imc.get_editor_property("mappings"))
except Exception as exc:
    log("modifier set failed: %r" % exc)

# Widget tree probe
try:
    wf = unreal.WidgetBlueprintFactory()
    wbp = asset_tools.create_asset("WBP_Test", "/Game/__Scratch", unreal.WidgetBlueprint, wf)
    log("WBP created: %r" % wbp)
    tree = wbp.get_editor_property("widget_tree")
    log("widget_tree: %r" % tree)
    log("root: %r" % tree.get_editor_property("root_widget"))
except Exception as exc:
    log("widget test failed: %r" % exc)
