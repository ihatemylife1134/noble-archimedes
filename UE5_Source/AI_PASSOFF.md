# Noble Archimedes UE5 Audit Passoff

## Purpose

This handoff is for the next AI or developer taking over the Unreal Engine audit. It records the repository state, verified findings, blockers, recommended repair order, and validation commands.

## Scope Audited

- Project root: `UE5_Source/`
- Project descriptor: `UE5_Source/NobleArchimedes.uproject`
- C++ module: `UE5_Source/NobleArchimedes/`
- Configuration: `UE5_Source/Config/`
- Build scripts: `UE5_Source/BuildScripts/`
- CI: `UE5_Source/.github/workflows/windows-build.yml`
- Validation tools: `UE5_Source/Tools/`

The repository contains 87 files under `UE5_Source`, including 14 headers and 12 `.cpp` files. It contains no `.uasset`, `.umap`, `.ubulk`, or `.pak` files.

## Executive Assessment

The project is not ready for a direct Unreal Engine 5.8.3 compile from the checked directory. The design/data validation passes, but project generation and C++ compilation are blocked by module layout, invalid Build.cs syntax, missing target descriptors, a missing SaveGame implementation, and likely Unreal reflection/type issues.

The project appears to be a source/specification handoff rather than a complete playable Unreal project. Content folders contain CSV, JSON, INI, and Markdown files but no imported Unreal assets or maps.

## Verified Findings

### P0: Must fix before compilation

1. **Invalid C# syntax in Build.cs**
   - File: `UE5_Source/NobleArchimedes/NobleArchimedes.Build.cs`
   - Current line:
     ```csharp
     PCHUsage = PCHUsageMode::UseExplicitOrSharedPCHs;
     ```
   - Required C# syntax:
     ```csharp
     PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
     ```

2. **Incorrect source layout in the checked project**
   - Current module location:
     `UE5_Source/NobleArchimedes/`
   - Expected project layout:
     `UE5_Source/Source/NobleArchimedes/`
   - `BuildScripts/setup_project.ps1` attempts to copy the module into another project at `C:\Projects\NobleArchimedes\Source\NobleArchimedes`, so the script is acting as a migration step rather than building this repository in place.
   - Recommendation: choose one model and make it explicit. Prefer making `UE5_Source` a self-contained Unreal project with `Source/NobleArchimedes/Public` and `Source/NobleArchimedes/Private`.

3. **No target rule files**
   - No `*.Target.cs` files were found.
   - Add at minimum:
     - `Source/NobleArchimedes.Target.cs`
     - `Source/NobleArchimedesEditor.Target.cs`
   - Use the standard `TargetRules` definitions for Game and Editor targets, then regenerate project files.

4. **Missing SaveGame implementation**
   - Declared/header file: `NobleArchimedes/Public/NobleArchimedesSaveGame.h`
   - Missing: `NobleArchimedes/Private/NobleArchimedesSaveGame.cpp`
   - The class declares `UNobleArchimedesSaveGame::UNobleArchimedesSaveGame()` and needs a matching definition.
   - Add the constructor source file, include the header, and initialize only what requires explicit initialization.

5. **Animation member type is suspicious and must be corrected**
   - File: `NobleArchimedes/Public/NobleArchimedesTypes.h`
   - Current members:
     ```cpp
     TArray<FAnimMontage> ComboAnimations;
     TArray<FAnimMontage> FinalAttackAnimations;
     ```
   - Recommended form:
     ```cpp
     class UAnimMontage;
     TArray<TObjectPtr<UAnimMontage>> ComboAnimations;
     TArray<TObjectPtr<UAnimMontage>> FinalAttackAnimations;
     ```
   - Add the forward declaration before the struct. Verify this type against the installed UE version during the first UHT compile.

### P1: Must fix before a usable editor project

6. **Engine version is inconsistent with the requested target**
   - `NobleArchimedes.uproject` has `EngineAssociation: "5.5"`.
   - `setup_project.ps1`, `build_dev.bat`, `build_playtest.bat`, and CI reference `UE_5.5`.
   - Update the project and scripts to the installed engine version. Do not claim UE 5.8.3 validation until the build runs with that exact installation.

7. **CI workflow cannot build**
   - File: `.github/workflows/windows-build.yml`
   - The Unreal installation step prints a message and exits with code 1.
   - It also assumes `C:\Program Files\Epic Games\UE_5.5`.
   - Recommendation: use a self-hosted Windows runner with UE installed, or replace this workflow with a documented external build process. Add a preflight step that validates `RunUAT.bat`, the project path, and engine version.

8. **No Unreal assets or maps exist**
   - The repository has 0 `.uasset` and 0 `.umap` files.
   - `DefaultInput.ini` references `/Game/Input/IMC_Default.IMC_Default`, but no corresponding asset exists.
   - `DefaultEngine.ini` references `/Game/Maps/Transition`, but no map exists.
   - Level streaming code names ten chapter levels, but no maps exist.
   - Recommendation: create/import assets after the C++ module compiles. Do not treat CSV files as imported DataTables until the editor import has been performed and verified.

9. **Input configuration is internally mixed**
   - `DefaultInput.ini` contains legacy `ActionMappings` and `AxisMappings`.
   - It also references Enhanced Input assets, but the assets are absent.
   - Recommendation: select Enhanced Input as the canonical system, create the Input Actions and Mapping Context assets, and bind them in C++. Retain legacy mappings only if the code actually consumes them.

10. **Readiness scripts disagree about missing files**
    - `check_project_readiness.py` reports missing:
      - `NobleArchimedes/Private/NobleArchimedesSaveGame.cpp`
      - `SESSION_HANDOFF.md`
      - `RESEARCH_FINDINGS.md`
      - `Content/Blueprints/LevelDesignSpec.md`
    - `check_rebuild_completeness.py` reports a likely typo in the expected path:
      - `NobleArchimedes/Private/NobleArchivdesLevelStreaming.cpp`
    - Actual file present:
      - `NobleArchimedes/Private/NobleArchimedesLevelStreaming.cpp`
    - Fix the checker path and add the missing implementation file. Keep documentation checks separate from compile readiness.

### P2: Review during first successful UHT/build pass

11. **Reflection accessibility and ownership review**
    - Several private properties are marked `BlueprintReadOnly` without `meta=(AllowPrivateAccess="true")`.
    - Review all private reflected members in the headers after UHT runs. Add the metadata where Blueprint access is intentional, or move properties to protected/public sections.

12. **Pointer properties should use Unreal reflection-safe types where appropriate**
    - Review raw `AActor*`, component pointers, and object pointers exposed through UPROPERTY.
    - Prefer `TObjectPtr<>` for reflected UObject references in current Unreal code, while preserving forward declarations and correct includes.

13. **Level streaming implementation is only a skeleton**
    - The class contains chapter names and declarations, but runtime behavior must be checked against World Partition or the chosen level streaming approach.
    - Verify map package names, loading APIs, unload behavior, transition handling, and editor asset paths.

14. **Game defaults are not configured**
    - The project descriptor does not define explicit `GameInstanceClass`, `GameModeClass`, `PlayerControllerClass`, or default pawn settings.
    - Add project defaults through config or editor assets after the classes compile.

15. **Data table import is not automated end-to-end**
    - CSV validation passes, but no `.uasset` DataTables exist.
    - Verify struct row compatibility, enum spelling, asset import settings, and references from runtime code.

## Validation Results

### Passed

`python UE5_Source/Tools/validate_rebuild_fidelity.py`

- All 11 CSV files found.
- Required columns pass.
- Weapon, damage type, Innocent Devil, chapter, input, Death Doll, and timing checks pass.

### Failed

`python UE5_Source/Tools/check_project_readiness.py`

- C++ source: 13/14.
- Missing `NobleArchimedes/Private/NobleArchimedesSaveGame.cpp`.
- Documentation checks also report missing handoff/specification files.

`python UE5_Source/Tools/check_rebuild_completeness.py`

- C++ source: 22/23.
- Reports misspelled `NobleArchivdesLevelStreaming.cpp` path.
- Reports the same documentation gaps.

### Not run

- UnrealHeaderTool.
- UnrealBuildTool.
- Visual Studio compilation.
- `RunUAT BuildCookRun`.
- Editor startup.
- Cook/package validation.

No Unreal Engine installation was available through this repository audit, so no real UE 5.8.3 build result can be claimed.

## Recommended Repair Order

1. Convert the repository into a self-contained Unreal layout with `Source/NobleArchimedes`.
2. Fix `PCHUsageMode::` to `PCHUsageMode.`.
3. Add Game and Editor `Target.cs` files.
4. Add `NobleArchimedesSaveGame.cpp`.
5. Correct the animation montage property types and run UHT.
6. Update all engine references from 5.5 to the installed target version.
7. Generate Visual Studio project files.
8. Run a Development Editor compile first.
9. Fix UHT, compiler, and linker errors in order; do not proceed to packaging while any remain.
10. Create required input assets, maps, DataTables, and default game assets.
11. Launch the editor and test a blank map with the module loaded.
12. Add a minimal smoke-test map and package Development before attempting Shipping.
13. Repair CI only after a local Development build succeeds.

## Suggested Commands on a UE 5.8.3 Windows Machine

Replace `$UE_ROOT` and `$PROJECT` with actual paths:

```powershell
$UE_ROOT = "C:\Program Files\Epic Games\UE_5.8"
$PROJECT = (Resolve-Path .\UE5_Source\NobleArchimedes.uproject).Path

& "$UE_ROOT\Engine\Build\BatchFiles\GenerateProjectFiles.bat" -project="$PROJECT" -game

& "$UE_ROOT\Engine\Build\BatchFiles\Build.bat" NobleArchimedesEditor Win64 Development "`"$PROJECT`"" -WaitMutex -FromMsBuild

& "$UE_ROOT\Engine\Binaries\Win64\UnrealEditor-Cmd.exe" "$PROJECT" -run=Cook -TargetPlatform=Win64 -unattended -nop4 -buildmachine
```

Do not run the build commands until the source layout and target files are repaired. The exact engine directory name may differ on the machine.

## Handoff Instruction for the Next AI

Start by inspecting the current tree, then repair only the P0 items. Do not create placeholder maps or claim a successful compile. After each repair, regenerate project files and run the narrowest available Unreal validation. Preserve the CSV/specification content. Treat all claims in older handoff files that say the project is complete or build-ready as historical claims that require fresh verification.

## Completion Criteria

The project can be considered compile-ready only when all of the following are true:

- `NobleArchimedes.uproject` opens against the intended UE version.
- Game and Editor target files are present.
- UHT completes without errors.
- The module compiles and links in Development Editor configuration.
- No required source file is missing.
- Input and default map references either resolve to existing assets or are removed.
- A blank smoke-test map opens in the editor.
- A Development package completes.
- Shipping packaging is attempted only after Development succeeds.

## Audit Date

This passoff was generated from the current working tree after filesystem inspection and script execution. It is an audit snapshot, not a claim that any fixes have been applied.
