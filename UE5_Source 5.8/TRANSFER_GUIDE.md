# TRANSFER GUIDE — Moving to Windows GPU Machine

This guide helps you transfer the UE5 fan recreation project to your Windows machine and build it.

## 1. FILES TO TRANSFER

Copy the entire `UE5_Source/` folder to your Windows machine:

```
C:\Projects\NobleArchimedes\
├── .uproject
├── Config/
│   ├── DefaultEngine.ini
│   └── DefaultInput.ini
├── Content/           (Create empty folders - Blueprints, Maps, Audio, etc.)
├── Source/
│   ├── NobleArchimedes/
│   │   ├── Public/
│   │   │   ├── NobleArchimedesTypes.h
│   │   │   ├── NobleArchimedesCombatComponent.h
│   │   │   ├── NobleArchimedesCharacter.h
│   │   │   ├── NobleArchimedesCameraComponent.h
│   │   │   ├── NobleArchimedesInnocent DevilComponent.h
│   │   │   ├── NobleArchimedesSaveGame.h
│   │   │   ├── NobleArchimedesGameInstance.h
│   │   │   ├── NobleArchimedesLevelStreaming.h
│   │   │   ├── NobleArchimedesWeaponForge.h
│   │   │   └── NobleArchimedesItemSystem.h
│   │   └── Private/
│   │       ├── NobleArchimedesCombatComponent.cpp
│   │       ├── NobleArchimedesCharacter.cpp
│   │       ├── NobleArchimedesCameraComponent.cpp
│   │       ├── NobleArchimedesInnocent DevilComponent.cpp
│   │       ├── NobleArchimedesGameInstance.cpp
│   │       ├── NobleArchimedesLevelStreaming.cpp
│   │       ├── NobleArchimedesWeaponForge.cpp
│   │       └── NobleArchimedesItemSystem.cpp
│   └── NobleArchimedes.Build.cs
├── .gitignore
└── TRANSFER_GUIDE.md
```

## 2. WINDOWS SETUP

### Install Prerequisites
- Windows 10/11 (64-bit)
- Visual Studio 2022 (with C++ workload)
- Unreal Engine 5.5+ (Epic Games Launcher)
- ~150 GB free disk space

### Create Project
1. Launch Unreal Editor
2. Games → Third Person → C++
3. Project Name: `NobleArchimedes`
4. Location: `C:\Projects\NobleArchimedes\`
5. Click Create

### Replace Source Files
Copy the `Source/` folder contents into your new project, replacing any default files.

### Generate Visual Studio Files
1. Right-click `NobleArchimedes.uproject`
2. Select "Generate Visual Studio project files"
3. Open `NobleArchimedes.sln` in Visual Studio
2. Build → Build Solution

## 3. CONTENT CREATION CHECKLIST

Create these in the UE5 Editor (Content Browser):

### Blueprints
- [ ] BP_Forgemaster_Character (based on C++ class)
- [ ] BP_Enemy_Base
- [ ] BP_Sword, BP_Axe, BP_Spear, BP_Knuckles, BP_Special
- [ ] BP_Fairy, BP_Griffin, BP_Salamander, BP_Ogre, BP_Skeleton_Devil, BP_Witch_Devil, BP_Pumpkin
- [ ] BP_Potion, BP_HighPotion, BP_Serum, BP_Uncurse
- [ ] BP_Material_Base (for ~40 materials)
- [ ] BP_SaveRoom, BP_GreenDoorRoom, BP_Candle_Breakable
- [ ] WB_HealthBar, WB_ManaBar, WB_ComboCounter, WB_WeaponIndicator, WB_Innocent DevilStatus, WB_MainMenu

### Maps
- [ ] PersistentLevel.umap
- [ ] Chap_01_AbandonedCastle.umap through Chap_10_DraculasCastle.umap

### Input
- [ ] IMC_Default (Input Mapping Context)
- [ ] IA_Move, IA_Look, IA_Jump, IA_AttackLight, IA_AttackHeavy, IA_Dodge, IA_GuardPress, IA_GuardRelease, IA_Special, IA_Interact, IA_Menu, IA_Map, IA_CameraMode

### Data Assets
- [ ] WeaponDataTable (based on FWeaponData)
- [ ] WeaponRecipeTable (based on FWeaponRecipe)
- [ ] MaterialDataTable (based on FMaterialData)
- [ ] Innocent DevilDataTable (based on FInnocent DevilData)
- [ ] EnemyDataTable (enemy stats per chapter)

## 4. BUILD & PACKAGE

### Development Build
```powershell
# From Unreal Editor or command line
UnrealEditor.exe NobleArchimedes -run=Build -target=NobleArchimedes -platform=Win64 -configuration=Development
```

### Shipping Build (for playtesting)
```powershell
RunUAT.bat BuildCookRun -project=C:\Projects\NobleArchimedes\NobleArchimedes.uproject -platform=Win64 -clientconfig=Shipping -serverconfig=Shipping -cook -stage -package -prerequisites -build
```

**Output:** `C:\Projects\NobleArchimedes\Saved\StagedBuilds\Windows\NobleArchimedes\NobleArchimedes.exe`

## 5. GIT (OPTIONAL)

Initialize git on Windows for version control:

```powershell
cd C:\Projects\NobleArchimedes\
git init
git lfs install
git lfs track "*.uasset" "*.umap" "*.psd" "*.tga" "*.png" "*.jpg" "*.wav" "*.fbx" "*.obj"
git add .
git commit -m "Initial UE5 project setup"
```

## 6. TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| Build fails | Run "Generate Visual Studio project files" from .uproject context menu |
| Missing modules | Check .Build.cs has all required dependencies |
| Blueprint errors | Ensure C++ classes are compiled before opening Blueprints |
| Crashes on startup | Verify all required plugins are enabled in .uproject |
| Save/load not working | Check Saved/Saves/ directory exists |

## 7. PRIVATE USE REMINDER

This is a fan recreation for private, educational use only:
- ✅ Personal playtesting
- ✅ Learning UE5 and game development
- ❌ No public distribution
- ❌ No monetization
- ❌ No sharing with others
- ❌ No use of original game assets (ISOs, extracted files, audio, textures)

All assets must be original creations.