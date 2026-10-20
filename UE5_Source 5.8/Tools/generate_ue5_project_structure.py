#!/usr/bin/env python3
"""
Generate a complete UE5 project structure for the Noble Archimedes fan recreation.
This script creates the directory structure needed for the UE5 Editor.

Usage:
    python generate_ue5_project_structure.py
"""

import os
from pathlib import Path

PROJECT_ROOT = Path("UE5_Source")

DIRECTORIES = [
    # Content directories
    "Content/Blueprints/Characters",
    "Content/Blueprints/Combat",
    "Content/Blueprints/Companions",
    "Content/Blueprints/Enemies",
    "Content/Blueprints/Enemies/Bosses",
    "Content/Blueprints/Items",
    "Content/Blueprints/Items/Materials",
    "Content/Blueprints/Level",
    "Content/Blueprints/UI",
    "Content/Maps/Chap_01_AbandonedCastle",
    "Content/Maps/Chap_02_BaljhetMountains",
    "Content/Maps/Chap_03_GaribaldiTemple",
    "Content/Maps/Chap_04_MortviaAqueduct",
    "Content/Maps/Chap_05_ForestOfJigramunt",
    "Content/Maps/Chap_06_CordovaTown",
    "Content/Maps/Chap_07_EneomaosMachineTower",
    "Content/Maps/Chap_08_AiolonRuins",
    "Content/Maps/Chap_09_InfiniteCorridor",
    "Content/Maps/Chap_10_DraculasCastle",
    "Content/Models/Characters",
    "Content/Models/Enemies",
    "Content/Models/Companions",
    "Content/Models/Weapons",
    "Content/Models/Items",
    "Content/Models/Environment",
    "Content/Textures/Characters",
    "Content/Textures/Enemies",
    "Content/Textures/Companions",
    "Content/Textures/Weapons",
    "Content/Textures/Items",
    "Content/Textures/Environment",
    "Content/Textures/UI",
    "Content/Materials/Characters",
    "Content/Materials/Enemies",
    "Content/Materials/Companions",
    "Content/Materials/Weapons",
    "Content/Materials/Items",
    "Content/Materials/Environment",
    "Content/Materials/UI",
    "Content/Animations/Characters",
    "Content/Animations/Enemies",
    "Content/Animations/Companions",
    "Content/Animations/Weapons",
    "Content/Audio/SFX",
    "Content/Audio/Music",
    "Content/Audio/Ambient",
    "Content/Audio/UI",
    "Content/VFX/Combat",
    "Content/VFX/Companion",
    "Content/VFX/Environment",
    "Content/VFX/Item",
    "Content/DataTables",
    "Content/Localization",
    "Content/Movies",
    # Source directories
    "Source/NobleArchimedes/Public",
    "Source/NobleArchimedes/Private",
    # Config directories
    "Config",
    # Build scripts
    "BuildScripts",
    # Tools
    "Tools",
    # Shaders
    "Shaders",
]

def create_structure():
    print("Creating UE5 project structure...")
    print(f"Root: {PROJECT_ROOT.absolute()}")
    print()

    for dir_path in DIRECTORIES:
        full_path = PROJECT_ROOT / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        # Create .gitkeep in empty directories
        gitkeep = full_path / ".gitkeep"
        if not any(full_path.iterdir()):
            gitkeep.touch()

    print(f"\nCreated {len(DIRECTORIES)} directories.")
    print(f"\nProject structure ready at: {PROJECT_ROOT.absolute()}")
    print("\nNext steps:")
    print("  1. Copy C++ source files to Source/NobleArchimedes/")
    print("  2. Copy Config files to Config/")
    print("  3. Copy Data Tables to Content/DataTables/")
    print("  4. Create Blueprints and assets in UE5 Editor")
    print("  5. Build and package!")

if __name__ == "__main__":
    create_structure()