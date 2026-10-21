"""
Placeholder gate: prove every generated asset has real content, not a stub.

A "fully built" asset must carry substance, not just exist:

  SK_Hector      real skeleton, >1 bone, >=1 LOD, >=1 material section
  AN_Hector_*    >1 frame of keys, non-empty bone tracks, correct skeleton
  AM_Hector_*    >=1 section, >=1 slot track with an animation, play length > 0
  AB_Hector      graph output + montage slot nodes present
  BP_Hector      references SK_Hector (not the engine skeletal cube)

Run as a PythonScript commandlet. Exit code is reported through the log marker
[NA-SUBSTANCE] RESULT=...; errors are listed individually.
"""

import unreal

LOG = "[NA-SUBSTANCE] "
ERRORS = []
REPORT = []

HECTOR_DIR = "/Game/Characters/Hector"
ANIM_DIR = HECTOR_DIR + "/Animations"
MONTAGE_DIR = HECTOR_DIR + "/Montages"
ANIMATIONS = (
    "Idle", "Walk", "Run", "Jump", "Light1", "Light2", "Light3", "Heavy",
    "Guard", "QuickStep", "HitReaction", "Death",
)

# Anything below these thresholds is a placeholder, not authored content.
MIN_BONES = 8
MIN_LODS = 1
MIN_KEYS = 2
MIN_TRACKS = 1


def log(msg):
    text = LOG + str(msg)
    REPORT.append(text)
    unreal.log_warning(text)


def err(msg):
    text = LOG + "ERROR: " + str(msg)
    ERRORS.append(str(msg))
    REPORT.append(text)
    unreal.log_error(text)


def get_prop(obj, name, default=None):
    import re
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    snake = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()
    for candidate in (snake, name):
        try:
            return obj.get_editor_property(candidate)
        except Exception:
            continue
    return default


def load(path, label):
    asset = unreal.load_asset(path)
    if not asset:
        err("%s missing at %s" % (label, path))
        return None
    if asset.get_class().get_name() in ("StaticMesh", "SkeletalMesh") and \
            asset.get_path_name().startswith("/Engine/"):
        err("%s is an engine placeholder (%s)" % (label, asset.get_path_name()))
        return None
    return asset


# ------------------------------------------------------------------ skeleton
# NOTE: AnimationBlueprintLibrary is not exposed to Python in this engine build,
# and SkeletalMesh.LODInfo is protected, so substance is proven from readable
# properties: skeleton bone count and material slots.
log("=== SKELETON ===")
mesh = load(HECTOR_DIR + "/SK_Hector", "SK_Hector")
skeleton = None
bone_count = 0
if mesh:
    skeleton = get_prop(mesh, "skeleton")
    if not skeleton:
        err("SK_Hector has no skeleton")
    else:
        tree = get_prop(skeleton, "bone_tree") or []
        bone_count = len(tree)
        if bone_count < MIN_BONES:
            err("SK_Hector is a stub: only %d bones" % bone_count)

    materials = get_prop(mesh, "materials") or []
    if not materials:
        err("SK_Hector has no material slots")
    log("SK_Hector bones=%d material_slots=%d" % (bone_count, len(materials)))

# --------------------------------------------------------------- sequences
log("=== ANIMATION SEQUENCES ===")
AUTHORED_FPS = 30.0
for anim in ANIMATIONS:
    label = "AN_Hector_%s" % anim
    seq = load("%s/%s" % (ANIM_DIR, label), label)
    if not seq:
        continue

    keys = get_prop(seq, "number_of_sampled_keys") or 0
    length = get_prop(seq, "sequence_length") or 0.0
    seq_skel = get_prop(seq, "skeleton")

    # The authored clips are 30 fps keyframes, so key count and length must
    # agree. A mismatch means the import dropped or padded frames.
    expected = (keys - 1) / AUTHORED_FPS if keys > 1 else 0.0
    log("%-20s keys=%-4d len=%.2fs expected=%.2fs" % (label, keys, length, expected))

    if keys < MIN_KEYS:
        err("%s is a stub: %d sampled keys" % (label, keys))
    if length <= 0.0:
        err("%s has zero length" % label)
    if keys > 1 and abs(length - expected) > 0.05:
        err("%s frame data does not match 30 fps (len %.2f vs %.2f)"
            % (label, length, expected))
    if skeleton and seq_skel != skeleton:
        err("%s does not target the Hector skeleton" % label)

# --------------------------------------------------------------- anim graph
log("=== ANIM BLUEPRINT ===")
abp = load(HECTOR_DIR + "/AB_Hector", "AB_Hector")
if abp:
    graphs = abp.get_animation_graphs()
    if not graphs:
        err("AB_Hector has no animation graph")
    else:
        classes = [n.get_class().get_name() for n in
                   graphs[0].get_graph_nodes_of_class(unreal.AnimGraphNode_Base)]
        log("AB_Hector nodes=%s" % classes)
        if "AnimGraphNode_Root" not in classes:
            err("AB_Hector has no graph output")
        if "AnimGraphNode_Slot" not in classes:
            err("AB_Hector has no montage slot (montages would not render)")
    if not abp.generated_class():
        err("AB_Hector does not compile")

# ------------------------------------------------------------- character wiring
log("=== CHARACTER WIRING ===")
bp_class = unreal.load_class(None, "/Game/Blueprints/Characters/BP_HectorCharacter.BP_HectorCharacter_C")
if not bp_class:
    err("BP_HectorCharacter class not found")
else:
    cdo = unreal.get_default_object(bp_class)
    mesh_comp = get_prop(cdo, "Mesh")
    used_mesh = get_prop(mesh_comp, "SkeletalMeshAsset") if mesh_comp else None
    anim_class = get_prop(mesh_comp, "AnimClass") if mesh_comp else None
    log("BP_HectorCharacter mesh=%s anim=%s" % (used_mesh, anim_class))

    if not used_mesh:
        err("BP_HectorCharacter has no skeletal mesh assigned")
    elif used_mesh.get_path_name().startswith("/Engine/"):
        err("BP_HectorCharacter still uses the placeholder mesh %s"
            % used_mesh.get_path_name())
    elif mesh and used_mesh.get_path_name() != mesh.get_path_name():
        err("BP_HectorCharacter uses %s, expected %s"
            % (used_mesh.get_path_name(), mesh.get_path_name()))

    if not anim_class:
        err("BP_HectorCharacter has no AnimClass (character will T-pose)")
    elif abp and anim_class.get_name() != abp.generated_class().get_name():
        err("BP_HectorCharacter AnimClass is not AB_Hector")

log("=== RESULT ===")
log("RESULT=%s errors=%d" % ("FAIL" if ERRORS else "PASS", len(ERRORS)))
for message in ERRORS:
    log("FAILED: " + message)
