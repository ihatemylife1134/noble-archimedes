"""Dump Game Animation Sample 5.8 camera rig values for comparison with ours.

GASP's camera is data-driven: CameraRig_* assets under Blueprints/Cameras/Rigs,
driven by a CameraAsset + CameraDirector and selected by a ChooserTable
(CHT_CameraRig). The framing numbers therefore have to be read out of the assets.
"""
import unreal

OUT = r"C:\Users\Madi\AppData\Local\Temp\gasp_camera2.txt"
CAM_DIR = "/Game/Blueprints/Cameras"
lines = []


def say(m):
    lines.append(str(m))


def render(value):
    if isinstance(value, (int, float, bool, str)):
        return repr(value)
    if isinstance(value, (unreal.Vector, unreal.Vector2D, unreal.Rotator,
                          unreal.Transform, unreal.Color, unreal.LinearColor)):
        return str(value)
    if isinstance(value, (unreal.EnumBase, unreal.Name)):
        return str(value)
    return None


def fields(obj, limit=40):
    try:
        names = [n for n in dir(obj) if not n.startswith("_")]
    except Exception:  # noqa: BLE001
        return []
    out = []
    for name in sorted(names):
        try:
            value = obj.get_editor_property(name)
        except Exception:  # noqa: BLE001
            continue
        out.append((name, value))
        if len(out) >= limit:
            break
    return out


def dump(obj, label, depth=0):
    pad = "    " * (depth + 1)
    say("%s--- %s (%s)" % (pad, label, obj.get_class().get_name()))
    for name, value in fields(obj):
        text = render(value)
        if text is not None:
            say("%s  %s = %s" % (pad, name, text))
        elif isinstance(value, unreal.StructBase):
            say("%s  %s:" % (pad, name))
            dump(value, name, depth + 2)
        elif isinstance(value, (list, unreal.Array)):
            say("%s  %s[%d]:" % (pad, name, len(value)))
            for i, item in enumerate(value[:4]):
                if isinstance(item, unreal.StructBase):
                    dump(item, "%s[%d]" % (name, i), depth + 2)
                else:
                    item_text = render(item)
                    if item_text:
                        say("%s    [%d] %s" % (pad, i, item_text))


try:
    paths = unreal.EditorAssetLibrary.list_assets(CAM_DIR, recursive=True)
    say("camera assets found: %d" % len(paths))
    for path in sorted(paths):
        name = path.split("/")[-1].split(".")[0]
        say("")
        say("=" * 70)
        try:
            asset = unreal.EditorAssetLibrary.load_asset(path)
            if asset is None:
                say("%s  LOAD FAILED" % name)
                continue
            say("%s   path=%s" % (name, path))
            dump(asset, name)
            for prop in ("display_name_map", "enumerators"):
                try:
                    value = asset.get_editor_property(prop)
                except Exception:  # noqa: BLE001
                    continue
                say("    %s = %s" % (prop, value))
        except Exception as exc:  # noqa: BLE001
            say("%s  ERROR: %s" % (name, exc))
except Exception as exc:  # noqa: BLE001
    say("FAILED: %s" % exc)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
unreal.log("[NA-GASPCAM2] wrote %d lines" % len(lines))
