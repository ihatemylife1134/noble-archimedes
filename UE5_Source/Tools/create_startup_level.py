"""Create a clean, plugin-free startup level for Noble Archimedes.

Run headless:
  UnrealEditor-Cmd.exe <project>.uproject -run=PythonScript -script=<this file> -unattended -nosplash
"""

import unreal

MAP_PACKAGE = "/Game/Maps/Chap_01_AbandonedCastle"


def log(message):
    unreal.log("[NobleArchimedes] " + str(message))


def main():
    level_sub = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    editor_sub = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    actor_sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    if not level_sub:
        log("LevelEditorSubsystem unavailable")
        return False

    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PACKAGE):
        log("Removing existing asset: " + MAP_PACKAGE)
        unreal.EditorAssetLibrary.delete_asset(MAP_PACKAGE)

    created = level_sub.new_level(MAP_PACKAGE)
    log("new_level -> " + str(created))
    if not created:
        return False

    world = editor_sub.get_editor_world()
    if not world:
        log("No editor world after creating level")
        return False

    if actor_sub:
        actor_sub.spawn_actor_from_class(
            unreal.PlayerStart,
            unreal.Vector(0.0, 0.0, 120.0),
            unreal.Rotator(0.0, 0.0, 0.0),
        )
        log("Spawned PlayerStart")

    saved = level_sub.save_current_level()
    log("save_current_level -> " + str(saved))
    return bool(saved)


if __name__ == "__main__":
    log("RESULT: " + ("SUCCESS" if main() else "FAILURE"))
