# UE5 Python Script: Create Blueprints from C++ Classes
# Run this in the UE5 Editor Python console:
#   exec(open(r"C:\Users\Madi\OneDrive\Documents\Default Project\noble-archimedes\UE5_Source\Tools\ue5_create_blueprints.py").read())

import unreal

# Blueprint creation mappings: (C++ class name, Blueprint name, Blueprint folder)
blueprint_mappings = [
    ("HectorCharacter", "BP_HectorCharacter", "/Game/Blueprints/Characters"),
    ("Room", "BP_Room", "/Game/Blueprints/Levels"),
    ("SaveRoom", "BP_SaveRoom", "/Game/Blueprints/Levels"),
    ("CandleBreakable", "BP_CandleBreakable", "/Game/Blueprints/Levels"),
    ("EnemyBase", "BP_EnemyBase", "/Game/Blueprints/Enemies"),
    ("BossBase", "BP_BossBase", "/Game/Blueprints/Enemies"),
    ("InnocentDevilActor", "BP_InnocentDevilActor", "/Game/Blueprints/InnocentDevils"),
    ("ItemDrop", "BP_ItemDrop", "/Game/Blueprints/Items"),
    ("MapChecker", "BP_MapChecker", "/Game/Blueprints/Levels"),
    ("NobleArchimedesHUD", "BP_NobleArchimedesHUD", "/Game/Blueprints/UI"),
    ("NobleArchimedesGameModeBase", "BP_NobleArchimedesGameModeBase", "/Game/Blueprints/Core"),
]

# Create folders
for _, _, folder in blueprint_mappings:
    unreal.EditorAssetLibrary.make_directory(folder)

# Create Blueprint classes
created = []
for cpp_class_name, bp_name, folder in blueprint_mappings:
    asset_path = f"{folder}/{bp_name}"
    
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        print(f"[SKIP] {asset_path} already exists")
        continue
    
    # Find the C++ class
    cpp_class = unreal.load_class(None, f"/Script/NobleArchimedes.{cpp_class_name}")
    if not cpp_class:
        print(f"[ERROR] Could not find C++ class: {cpp_class_name}")
        continue
    
    # Create Blueprint
    bp_factory = unreal.BlueprintFactory()
    bp_factory.set_editor_property("ParentClass", cpp_class)
    
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    new_bp = asset_tools.create_asset(bp_name, folder, unreal.Blueprint, bp_factory)
    
    if new_bp:
        unreal.EditorAssetLibrary.save_loaded_asset(new_bp)
        created.append(bp_name)
        print(f"[OK] Created {asset_path}")
    else:
        print(f"[ERROR] Failed to create {asset_path}")

print(f"\nCreated {len(created)} Blueprint classes: {created}")

# Configure GameMode
game_mode_bp = unreal.load_asset("/Game/Blueprints/Core/BP_NobleArchimedesGameModeBase")
if game_mode_bp:
    # Set default pawn class to BP_HectorCharacter
    hector_bp = unreal.load_asset("/Game/Blueprints/Characters/BP_HectorCharacter")
    if hector_bp:
        game_mode_bp.set_editor_property("DefaultPawnClass", hector_bp.generated_class())
        print("[OK] Set DefaultPawnClass to BP_HectorCharacter")
    
    # Set HUD class
    hud_bp = unreal.load_asset("/Game/Blueprints/UI/BP_NobleArchimedesHUD")
    if hud_bp:
        game_mode_bp.set_editor_property("HUDClass", hud_bp.generated_class())
        print("[OK] Set HUDClass to BP_NobleArchimedesHUD")
    
    unreal.EditorAssetLibrary.save_loaded_asset(game_mode_bp)
    print("[OK] Saved BP_NobleArchimedesGameModeBase")

# Configure project settings
settings = unreal.get_default_object(unreal.GameMapsSettings)
settings.set_editor_property("GameDefaultMap", unreal.load_asset("/Game/Maps/Chap_01_AbandonedCastle"))
settings.set_editor_property("EditorStartupMap", unreal.load_asset("/Game/Maps/Chap_01_AbandonedCastle"))
settings.set_editor_property("GlobalDefaultGameMode", game_mode_bp.generated_class())
print("[OK] Configured project settings")

print("\n=== Blueprint creation complete ===")