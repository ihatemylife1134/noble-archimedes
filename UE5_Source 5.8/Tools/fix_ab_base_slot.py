"""Give AB_HectorBase a slot node so montages (attacks) override the pose.

A factory-created AnimBlueprint has no slot node, so the state machine ended up
wired straight to the Root. Montages override a slot, not the Root, so attacks
would never have appeared. The slot name is taken from the existing AB_Hector so
the montages already built against that name keep working.
"""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\fix_ab_base_slot.txt"
BASE = "/Game/Characters/HectorBase/AB_HectorBase"
ROOTS = ("/Game/Blueprints", "/Game/Characters")
lines = []


def say(m):
    lines.append(str(m))


def find_ab_hector():
    for root in ROOTS:
        for path in unreal.EditorAssetLibrary.list_assets(root, recursive=True):
            if path.split("/")[-1].split(".")[0] == "AB_Hector":
                return path
    return None


try:
    base = unreal.EditorAssetLibrary.load_asset(BASE)
    say("base abp = %s" % base)

    ref_path = find_ab_hector()
    say("reference AB_Hector = %s" % ref_path)

    slot_name = None
    if ref_path:
        ref = unreal.EditorAssetLibrary.load_asset(ref_path)
        name = unreal.NobleAnimGraphAuthoring.get_slot_name(ref)
        say("AB_Hector slot name = %s" % name)
        if name and str(name) != "None":
            slot_name = name
    if not slot_name:
        slot_name = unreal.Name("DefaultSlot")
        say("falling back to slot name = %s" % slot_name)

    sm = unreal.NobleAnimGraphAuthoring.get_or_create_state_machine(base, "Locomotion")
    say("states = %s" % unreal.NobleAnimGraphAuthoring.get_state_names(sm))

    ok = unreal.NobleAnimGraphAuthoring.ensure_slot_pipeline(base, sm, slot_name)
    say("ensure_slot_pipeline = %s" % ok)
    say("slot now      = %s" % unreal.NobleAnimGraphAuthoring.get_slot_name(base))
    say("root connected = %s" % unreal.NobleAnimGraphAuthoring.is_root_connected(base))
    say("in pose        = %s" % unreal.NobleAnimGraphAuthoring.is_state_machine_connected(base))
    say("compiled       = %s" % unreal.NobleAnimGraphAuthoring.compile_anim_blueprint(base))
    unreal.EditorAssetLibrary.save_asset(BASE, only_if_is_dirty=False)
    say("saved")
except Exception as exc:
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-SLOTFIX] wrote %d lines" % len(lines))
