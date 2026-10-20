#!/usr/bin/env python3
"""
Check if all necessary components are in place for the UE5 rebuild.
This helps track progress and identify missing pieces.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROJECT_ROOT = ROOT / "UE5_Source"

CATEGORIES = {
    "C++ Source Files": {
        "files": [
            "NobleArchimedes/Public/NobleArchimedesTypes.h",
            "NobleArchimedes/Public/HectorCharacter.h",
            "NobleArchimedes/Public/NobleArchimedesCombatComponent.h",
            "NobleArchimedes/Public/NobleArchimedesCameraComponent.h",
            "NobleArchimedes/Public/NobleArchimedesInnocentDevilComponent.h",
            "NobleArchimedes/Public/NobleArchimedesAudioComponent.h",
            "NobleArchimedes/Public/NobleArchimedesVFXComponent.h",
            "NobleArchimedes/Public/NobleArchimedesSaveGame.h",
            "NobleArchimedes/Public/NobleArchimedesGameInstance.h",
            "NobleArchimedes/Public/NobleArchimedesLevelStreaming.h",
            "NobleArchimedes/Public/NobleArchimedesWeaponForge.h",
            "NobleArchimedes/Public/NobleArchimedesItemSystem.h",
            "NobleArchimedes/Private/HectorCharacter.cpp",
            "NobleArchimedes/Private/NobleArchimedesCombatComponent.cpp",
            "NobleArchimedes/Private/NobleArchimedesCameraComponent.cpp",
            "NobleArchimedes/Private/NobleArchimedesInnocentDevilComponent.cpp",
            "NobleArchimedes/Private/NobleArchimedesAudioComponent.cpp",
            "NobleArchimedes/Private/NobleArchimedesVFXComponent.cpp",
            "NobleArchimedes/Private/NobleArchimedesGameInstance.cpp",
            "NobleArchimedes/Private/NobleArchimedesLevelStreaming.cpp",
            "NobleArchimedes/Private/NobleArchimedesWeaponForge.cpp",
            "NobleArchimedes/Private/NobleArchimedesItemSystem.cpp",
            "NobleArchimedes/NobleArchimedes.Build.cs",
        ]
    },
    "Data Tables (CSV)": {
        "files": [
            "Content/DataTables/WeaponDataTable.csv",
            "Content/DataTables/MaterialDataTable.csv",
            "Content/DataTables/WeaponRecipeTable.csv",
            "Content/DataTables/WeaponRecipeTable_Complete.csv",
            "Content/DataTables/WeaponMaterialRequirements.csv",
            "Content/DataTables/InnocentDevilDataTable.csv",
            "Content/DataTables/InnocentDevilEvolutionTable.csv",
            "Content/DataTables/EnemyDataTable.csv",
            "Content/DataTables/EnemyEncounterTable.csv",
            "Content/DataTables/ItemDropTable.csv",
            "Content/DataTables/ChapterProgressionTable.csv",
        ]
    },
    "Configuration": {
        "files": [
            "NobleArchimedes.uproject",
            "Config/DefaultInput.ini",
            "Config/DefaultEngine.ini",
        ]
    },
    "Documentation": {
        "files": [
            "TRANSFER_GUIDE.md",
            "SESSION_HANDOFF.md",
            "RESEARCH_FINDINGS.md",
            "COMPARISON_ORIGINAL_VS_REBUILD.md",
            "Content/Blueprints/AnimationSpec.md",
            "Content/Blueprints/AnimationFrameData.md",
            "Content/Blueprints/AssetNamingSpec.md",
            "Content/Blueprints/AudioSpec.md",
            "Content/Blueprints/ParticleSpec.md",
            "Content/Blueprints/UI_WidgetSpec.md",
            "Content/Blueprints/EnemyEncounterSpec.md",
            "Content/Blueprints/WeaponSpec.md",
            "Content/Blueprints/MaterialSpec.md",
            "Content/Blueprints/LevelSpec.md",
            "Content/Blueprints/LevelDesignSpec_Extended.md",
            "Content/Blueprints/BehaviorTreeSpec.md",
            "Content/Blueprints/AnimationBlueprintSpec.md",
            "Content/Blueprints/UIWireframeSpec.md",
            "Content/DataTables/README_DataTables.md",
            "Content/DataTables/SaveGameSchema.md",
        ]
    },
    "Build & Tools": {
        "files": [
            "BuildScripts/build_playtest.bat",
            "BuildScripts/build_dev.bat",
            "BuildScripts/setup_project.ps1",
            "Tools/validate_rebuild_fidelity.py",
            "Tools/convert_csv_to_datatable.py",
            "Tools/generate_ue5_import_manifest.py",
            "Tools/check_disc_structure.py",
            ".github/workflows/windows-build.yml",
        ]
    },
    "Localization": {
        "files": [
            "Content/Localization/En.json",
        ]
    },
}

def check_category(name, files):
    missing = []
    present = 0
    for f in files["files"]:
        full_path = PROJECT_ROOT / f
        if not full_path.exists():
            # A few handoff documents live at the repository root.
            full_path = ROOT / f
        if full_path.exists():
            present += 1
        else:
            missing.append(f)
    total = len(files["files"])
    print(f"\n{name}: {present}/{total} files present")
    if missing:
        print("  Missing:")
        for f in missing:
            print(f"    - {f}")
    return len(missing) == 0

def main():
    print("UE5 Rebuild Completeness Check")
    print("=" * 50)
    
    all_complete = True
    for category, files in CATEGORIES.items():
        if not check_category(category, files):
            all_complete = False
    
    print("\n" + "=" * 50)
    if all_complete:
        print("ALL COMPONENTS PRESENT - Ready for UE5 build!")
    else:
        print("SOME COMPONENTS MISSING - Check the list above")
    
    return 0 if all_complete else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())