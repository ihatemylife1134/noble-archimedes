#!/usr/bin/env python3
"""
Check if the UE5 project is ready for building.
Verifies all C++ files, data tables, and documentation are in place.
"""

import os
from pathlib import Path

PROJECT_ROOT = Path("UE5_Source 5.8")
REPO_ROOT = PROJECT_ROOT.parent

REQUIRED_FILES = {
    "C++ Headers": [
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
        "NobleArchimedes/Public/NobleArchimedesGameModeBase.h",
        "NobleArchimedes/Public/NobleArchimedesPlayerController.h",
        "NobleArchimedes/Public/Room.h",
        "NobleArchimedes/Public/SaveRoom.h",
        "NobleArchimedes/Public/CandleBreakable.h",
        "NobleArchimedes/Public/EnemyBase.h",
        "NobleArchimedes/Public/BossBase.h",
        "NobleArchimedes/Public/InnocentDevilActor.h",
        "NobleArchimedes/Public/MapChecker.h",
        "NobleArchimedes/Public/ItemDrop.h",
        "NobleArchimedes/Public/NobleArchimedesHUD.h",
    ],
    "C++ Source": [
        "NobleArchimedes/Private/HectorCharacter.cpp",
        "NobleArchimedes/Private/NobleArchimedesCombatComponent.cpp",
        "NobleArchimedes/Private/NobleArchimedesCameraComponent.cpp",
        "NobleArchimedes/Private/NobleArchimedesInnocentDevilComponent.cpp",
        "NobleArchimedes/Private/NobleArchimedesAudioComponent.cpp",
        "NobleArchimedes/Private/NobleArchimedesVFXComponent.cpp",
        "NobleArchimedes/Private/NobleArchimedesSaveGame.cpp",
        "NobleArchimedes/Private/NobleArchimedesGameInstance.cpp",
        "NobleArchimedes/Private/NobleArchimedesLevelStreaming.cpp",
        "NobleArchimedes/Private/NobleArchimedesWeaponForge.cpp",
        "NobleArchimedes/Private/NobleArchimedesItemSystem.cpp",
        "NobleArchimedes/Private/NobleArchimedesGameModeBase.cpp",
        "NobleArchimedes/Private/NobleArchimedesPlayerController.cpp",
        "NobleArchimedes/Private/Room.cpp",
        "NobleArchimedes/Private/SaveRoom.cpp",
        "NobleArchimedes/Private/CandleBreakable.cpp",
        "NobleArchimedes/Private/EnemyBase.cpp",
        "NobleArchimedes/Private/BossBase.cpp",
        "NobleArchimedes/Private/InnocentDevilActor.cpp",
        "NobleArchimedes/Private/MapChecker.cpp",
        "NobleArchimedes/Private/ItemDrop.cpp",
        "NobleArchimedes/Private/NobleArchimedesHUD.cpp",
        "NobleArchimedes/NobleArchimedes.Build.cs",
    ],
    "Data Tables": [
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
    ],
    "Project Config": [
        "NobleArchimedes.uproject",
        "Config/DefaultInput.ini",
        "Config/DefaultEngine.ini",
    ],
    "Documentation": [
        "TRANSFER_GUIDE.md",
        "COMPARISON_ORIGINAL_VS_REBUILD.md",
        "Content/Blueprints/AnimationBlueprintSpec.md",
        "Content/Blueprints/AnimationFrameData.md",
        "Content/Blueprints/AnimationSpec.md",
        "Content/Blueprints/AssetNamingSpec.md",
        "Content/Blueprints/AudioSpec.md",
        "Content/Blueprints/BehaviorTreeSpec.md",
        "Content/Blueprints/EnemyEncounterSpec.md",
        "Content/Blueprints/LevelDesignSpec_Extended.md",
        "Content/Blueprints/MaterialSpec.md",
        "Content/Blueprints/ParticleSpec.md",
        "Content/Blueprints/UIWireframeSpec.md",
        "Content/Blueprints/UI_WidgetSpec.md",
        "Content/Blueprints/WeaponSpec.md",
        "Content/DataTables/README_DataTables.md",
        "Content/DataTables/SaveGameSchema.md",
        "Content/Maps/LevelDesignSpec.md",
    ],
    "RepoRootDocs": [
        "SESSION_HANDOFF.md",
        "RESEARCH_FINDINGS.md",
    ],
    "Tools": [
        "Tools/validate_rebuild_fidelity.py",
        "Tools/check_rebuild_completeness.py",
        "Tools/check_disc_structure.py",
        "Tools/convert_csv_to_datatable.py",
        "Tools/generate_localization.py",
        "Tools/build_asset_manifest.py",
        "Tools/generate_ue5_project_structure.py",
        "Tools/build_asset_manifest.py",
    ],
    "Build Scripts": [
        "BuildScripts/build_playtest.bat",
        "BuildScripts/build_dev.bat",
        "BuildScripts/setup_project.ps1",
    ],
    "CI/CD": [
        ".github/workflows/windows-build.yml",
    ],
    "Localization": [
        "Content/Localization/En.json",
    ],
}

def check_category(name, files):
    missing = []
    present = 0
    for f in files:
        full_path = PROJECT_ROOT / f
        if full_path.exists():
            present += 1
        else:
            missing.append(f)
    total = len(files)
    pct = (present / total * 100) if total > 0 else 0
    print(f"{name}: {present}/{total} ({pct:.0f}%)")
    if missing:
        for f in missing:
            print(f"  MISSING: {f}")
    return len(missing) == 0

def main():
    print("UE5 Project Readiness Check")
    print("=" * 50)
    
    all_complete = True
    for category, files in REQUIRED_FILES.items():
        if category == "RepoRootDocs":
            # Repo root docs live one level above UE5_Source 5.8/
            missing = []
            present = 0
            for f in files:
                full_path = REPO_ROOT / f
                if full_path.exists():
                    present += 1
                else:
                    missing.append(f)
            total = len(files)
            pct = (present / total * 100) if total > 0 else 0
            print(f"{category}: {present}/{total} ({pct:.0f}%)")
            if missing:
                for f in missing:
                    print(f"  MISSING: {f}")
                all_complete = False
        else:
            if not check_category(category, files):
                all_complete = False
    
    print()
    print("=" * 50)
    if all_complete:
        print("ALL COMPONENTS PRESENT - Ready for UE5 build!")
        return 0
    else:
        print("SOME COMPONENTS MISSING - Check the list above")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())