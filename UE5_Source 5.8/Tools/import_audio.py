#!/usr/bin/env python3
"""Import the free sword SFX pack into /Game/Audio/SFX/Sword/<Category>.

Source is the extracted pack in the user's Downloads. Idempotent: re-running
re-imports in place, so renames in the pack are picked up.
"""
import os
import unreal

SRC_ROOT = os.path.join(os.environ["USERPROFILE"], "Downloads",
                        "free_realistic_sword_sound_effects_pack",
                        "Free Realistic Sword Sound Effects Pack")
DEST_ROOT = "/Game/Audio/SFX/Sword"

OUT = r"C:\Users\Madi\AppData\Local\Temp\import_audio.txt"
lines = []


def say(msg):
    lines.append(str(msg))


def flush():
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


try:
    tasks = []
    for category in sorted(os.listdir(SRC_ROOT)):
        folder = os.path.join(SRC_ROOT, category)
        if not os.path.isdir(folder):
            continue
        dest = "%s/%s" % (DEST_ROOT, category.replace(" ", ""))
        for entry in sorted(os.listdir(folder)):
            if not entry.lower().endswith(".wav"):
                continue
            task = unreal.AssetImportTask()
            task.filename = os.path.join(folder, entry)
            task.destination_path = dest
            task.destination_name = os.path.splitext(entry)[0].replace(" ", "_")
            task.automated = True
            task.replace_existing = True
            task.save = True
            task.factory = unreal.SoundFactory()
            tasks.append(task)

    say("queued %d wav files" % len(tasks))
    if tasks:
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
        imported = 0
        for task in tasks:
            paths = task.imported_object_paths
            if paths:
                imported += len(paths)
                say("  %s -> %s" % (os.path.basename(task.filename), paths[0]))
            else:
                say("  FAILED %s" % os.path.basename(task.filename))
        say("imported %d assets" % imported)
        for cat in sorted(os.listdir(SRC_ROOT)):
            folder = os.path.join(SRC_ROOT, cat)
            if os.path.isdir(folder):
                dest = "%s/%s" % (DEST_ROOT, cat.replace(" ", ""))
                assets = unreal.EditorAssetLibrary.list_assets(dest, recursive=False)
                say("  %-22s %d assets in %s" % (cat, len(assets), dest))
except Exception as exc:
    say("IMPORT FAILED: %s" % exc)

flush()
unreal.log("[NA-AUDIO] wrote %d lines" % len(lines))
