"""
Noble Archimedes content pipeline (UE 5.8).

Run with:
    UnrealEditor-Cmd.exe <project>.uproject -run=PythonScript -script=<this file> -unattended -nosplash

Creates/updates:
  /Game/DataTables/DT_*          - all 11 CSV data tables
  /Game/Blueprints/...           - core Blueprints from the C++ classes
  /Game/Input/Actions/IA_*       - Enhanced Input actions
  /Game/Input/IMC_Default        - default mapping context
  /Game/Maps/Chap_01..10_*       - all ten chapter blockouts

The script is idempotent for Blueprints and input assets. Data tables are
recreated so struct changes are picked up; nothing references them yet.
"""

import csv
import json
import math
import os
import re
import traceback

import unreal

LOG_PREFIX = "[NA-CONTENT] "

CONTENT_DIR = unreal.SystemLibrary.get_project_content_directory()
DATA_TABLE_DIR = os.path.join(CONTENT_DIR, "DataTables")
MANIFEST_PATH = os.path.join(DATA_TABLE_DIR, "ImportManifest.json")

ASSET_TOOLS = unreal.AssetToolsHelpers.get_asset_tools()
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

STATS = {"created": 0, "updated": 0, "skipped": 0, "errors": 0}
ERRORS = []
BP_OBJECTS = {}


def log(message):
    unreal.log(LOG_PREFIX + str(message))


def warn(message):
    unreal.log_warning(LOG_PREFIX + str(message))


def error(message):
    STATS["errors"] += 1
    ERRORS.append(str(message))
    unreal.log_error(LOG_PREFIX + str(message))


def snake(name):
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def set_prop(obj, name, value, required=False):
    """Set an editor property, accepting PascalCase or snake_case names."""
    for candidate in (snake(name), name):
        try:
            obj.set_editor_property(candidate, value)
            return True
        except Exception:
            continue
    if required:
        error("Could not set property '%s' on %r" % (name, obj))
    return False


def rgb_color(r, g, b, a=255):
    # Unreal Python's Color constructor is (B, G, R, A).
    return unreal.Color(
        max(0, min(255, int(b))),
        max(0, min(255, int(g))),
        max(0, min(255, int(r))),
        max(0, min(255, int(a))))


def get_prop(obj, name, default=None):
    for candidate in (snake(name), name):
        try:
            return obj.get_editor_property(candidate)
        except Exception:
            continue
    return default


def asset_path(folder, name):
    return "%s/%s" % (folder, name)


def load_asset(path):
    return unreal.EditorAssetLibrary.load_asset(path)


def save_asset(path):
    if not unreal.EditorAssetLibrary.save_asset(path, only_if_is_dirty=False):
        warn("Failed to save asset: %s" % path)


def compile_blueprint(bp):
    try:
        unreal.KismetEditorUtilities.compile_blueprint(bp)
        return True
    except Exception:
        try:
            unreal.BlueprintEditorLibrary.compile_blueprint(bp)
            return True
        except Exception as exc:
            warn("Could not compile %r: %r" % (bp, exc))
            return False


def ensure_blueprint(name, folder, parent_path):
    """Create a Blueprint if it does not exist. Returns the Blueprint asset."""
    path = asset_path(folder, name)
    if name in BP_OBJECTS:
        STATS["skipped"] += 1
        return BP_OBJECTS[name]

    existing = load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
    if existing:
        BP_OBJECTS[name] = existing
        compile_blueprint(existing)
        STATS["skipped"] += 1
        return existing

    parent = unreal.load_class(None, parent_path)
    if not parent and not parent_path.endswith("_C"):
        parent = unreal.load_class(None, "%s.%s_C" % (parent_path, parent_path.rsplit("/", 1)[-1]))
    if not parent:
        error("Missing parent class for %s: %s" % (name, parent_path))
        return None

    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent)
    bp = ASSET_TOOLS.create_asset(name, folder, unreal.Blueprint, factory)
    if not bp:
        error("Failed to create Blueprint %s" % path)
        return None

    BP_OBJECTS[name] = bp
    compile_blueprint(bp)
    save_asset(path)
    STATS["created"] += 1
    log("Created Blueprint %s" % path)
    return bp


def bp_class(path, name):
    bp = BP_OBJECTS.get(name)
    if bp:
        try:
            cls = bp.generated_class()
            if cls:
                return cls
        except Exception:
            pass

    full = "%s.%s_C" % (path, name)
    cls = unreal.load_class(None, full)
    if not cls:
        cls = unreal.load_object(None, full)
    if not cls:
        try:
            cls = unreal.EditorAssetLibrary.load_blueprint_class(asset_path(path, name))
        except Exception:
            cls = None
    return cls


INPUT_CACHE = {}


def create_input_action(name, value_type):
    path = asset_path("/Game/Input/Actions", name)
    existing = INPUT_CACHE.get(name)
    if not existing and unreal.EditorAssetLibrary.does_asset_exist(path):
        existing = load_asset(path)
    if existing:
        ia = existing
        STATS["updated"] += 1
    else:
        factory = unreal.InputAction_Factory()
        ia = ASSET_TOOLS.create_asset(name, "/Game/Input/Actions", unreal.InputAction, factory)
        STATS["created"] += 1

    if not ia:
        error("Failed to create Input Action %s" % name)
        return None

    INPUT_CACHE[name] = ia
    ia.set_editor_property("value_type", value_type)
    save_asset(path)
    return ia


IMC_CACHE = {}


def create_mapping_context(name):
    path = asset_path("/Game/Input", name)
    existing = IMC_CACHE.get(name)
    if not existing and unreal.EditorAssetLibrary.does_asset_exist(path):
        existing = load_asset(path)
    if existing:
        imc = existing
        STATS["updated"] += 1
    else:
        factory = unreal.InputMappingContext_Factory()
        imc = ASSET_TOOLS.create_asset(name, "/Game/Input", unreal.InputMappingContext, factory)
        STATS["created"] += 1

    if not imc:
        error("Failed to create Input Mapping Context %s" % name)
    IMC_CACHE[name] = imc
    return imc


# ---------------------------------------------------------------------------
# Animation pipeline (FBX -> AnimSequence -> AnimMontage -> AnimBlueprint)
# ---------------------------------------------------------------------------

PROJECT_DIR = os.path.dirname(CONTENT_DIR.rstrip("/\\"))
HECTOR_FBX_DIR = os.path.join(PROJECT_DIR, "ArtSource", "Hector", "Export")
HECTOR_DIR = "/Game/Characters/Hector"
HECTOR_ANIM_DIR = HECTOR_DIR + "/Animations"
HECTOR_MONTAGE_DIR = HECTOR_DIR + "/Montages"
HECTOR_MESH_NAME = "SK_Hector"
HECTOR_ANIMBP_NAME = "AB_Hector"

# Animations authored by ArtSource/Hector/hector_anims.py (30 fps keyframes).
HECTOR_ANIMATIONS = (
    "Idle", "Walk", "Run", "Jump",
    "Light1", "Light2", "Light3", "Heavy",
    "Guard", "QuickStep", "HitReaction", "Death",
)

# Sequences that loop while the state is active.
HECTOR_LOOPING = {"Idle", "Walk", "Run", "Jump", "Guard"}

# Weapon type -> (combo stage animations, finisher animations).
# The combat component indexes ComboAnimations[Stage-1] for light attacks and
# FinalAttackAnimations[Stage-1] for the heavy finisher, so both arrays are
# authored to three stages.
WEAPON_ANIM_SETS = {
    "Sword": (["Light1", "Light2", "Light3"], ["Heavy"]),
    "Axe": (["Light1", "Light2", "Light3"], ["Heavy"]),
    "Spear": (["Light1", "Light2", "Light3"], ["Heavy"]),
    "Knuckles": (["Light1", "Light2", "Light3"], ["Heavy"]),
    "Special": (["Light1", "Light2"], ["Heavy"]),
}

COMBO_STAGES = 3
ANIM_MONTAGES = {}


def hector_sequence_name(anim):
    return "AN_Hector_%s" % anim


def hector_montage_name(anim):
    return "AM_Hector_%s" % anim


def hector_sequence_path(anim):
    return asset_path(HECTOR_ANIM_DIR, hector_sequence_name(anim))


def hector_montage_path(anim):
    return asset_path(HECTOR_MONTAGE_DIR, hector_montage_name(anim))


def import_fbx(source_file, folder, asset_name, configure):
    """Import one FBX as ``folder/asset_name`` and return the created asset.

    ``configure`` receives the FbxImportUI so each caller can pick the import
    type. Automated type detection must stay off: when it is on, UE re-detects
    the type from the file and imports a static mesh even though animation-only
    import was requested.
    """
    if not os.path.exists(source_file):
        error("Missing FBX: %s" % source_file)
        return None

    task = unreal.AssetImportTask()
    task.set_editor_property("filename", source_file)
    task.set_editor_property("destination_path", folder)
    task.set_editor_property("destination_name", asset_name)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("save", True)

    options = unreal.FbxImportUI()
    options.set_editor_property("automated_import_should_detect_type", False)
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    configure(options)
    task.set_editor_property("options", options)

    try:
        ASSET_TOOLS.import_asset_tasks([task])
    except Exception as exc:
        error("FBX import failed for %s: %r" % (source_file, exc))
        return None

    return load_asset(asset_path(folder, asset_name))

def import_hector_mesh():
    """Import SK_Hector.fbx and return (mesh, skeleton)."""
    def configure(options):
        options.set_editor_property("import_mesh", True)
        options.set_editor_property("import_as_skeletal", True)
        options.set_editor_property("import_animations", False)
        options.set_editor_property("mesh_type_to_import",
                                    unreal.FBXImportType.FBXIT_SKELETAL_MESH)

    mesh = import_fbx(os.path.join(HECTOR_FBX_DIR, "SK_Hector.fbx"),
                      HECTOR_DIR, HECTOR_MESH_NAME, configure)
    if not mesh:
        error("Failed to import the Hector skeletal mesh")
        return None, None

    skeleton = get_prop(mesh, "skeleton")
    if not skeleton:
        error("Imported Hector mesh has no skeleton")
        return mesh, None

    STATS["created"] += 1
    log("Imported %s (skeleton %s)" % (mesh.get_path_name(),
                                       skeleton.get_path_name()))
    return mesh, skeleton


def import_hector_animation(anim, skeleton):
    """Import one A_Hector_<anim>.fbx as an AnimSequence."""
    def configure(options):
        options.set_editor_property("import_mesh", False)
        options.set_editor_property("import_as_skeletal", True)
        options.set_editor_property("import_animations", True)
        options.set_editor_property("import_rigid_mesh", False)
        options.set_editor_property("mesh_type_to_import",
                                    unreal.FBXImportType.FBXIT_ANIMATION)
        options.set_editor_property("skeleton", skeleton)
        # Bone tracks live on the animation import data, not on FbxImportUI.
        anim_data = unreal.FbxAnimSequenceImportData()
        anim_data.set_editor_property("import_bone_tracks", True)
        options.set_editor_property("anim_sequence_import_data", anim_data)

    sequence = import_fbx(os.path.join(HECTOR_FBX_DIR, "A_Hector_%s.fbx" % anim),
                          HECTOR_ANIM_DIR, hector_sequence_name(anim), configure)
    if not sequence or sequence.get_class().get_name() != "AnimSequence":
        error("Failed to import animation %s" % anim)
        return None

    # The authored root motion is in place for now; attacks stay in place and
    # locomotion is driven by CharacterMovement.
    if anim in HECTOR_LOOPING:
        set_prop(sequence, "loop", True)
    STATS["created"] += 1
    return sequence


def import_hector_animations(skeleton):
    sequences = {}
    for anim in HECTOR_ANIMATIONS:
        sequence = import_hector_animation(anim, skeleton)
        if sequence:
            sequences[anim] = sequence
    log("Imported %d of %d Hector animations" %
        (len(sequences), len(HECTOR_ANIMATIONS)))
    return sequences


def create_hector_montage(anim, sequence, skeleton):
    """Create (or refresh) the montage for one animation.

    The montage is saved immediately: a data table may only reference it once
    the asset exists on disk, otherwise the reference resolves to None.
    """
    path = hector_montage_path(anim)
    existing = load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
    if existing:
        montage = existing
        set_prop(montage, "sequence_length", get_prop(sequence, "sequence_length"))
        STATS["updated"] += 1
    else:
        factory = unreal.AnimMontageFactory()
        set_prop(factory, "source_animation", sequence)
        set_prop(factory, "target_skeleton", skeleton)
        montage = ASSET_TOOLS.create_asset(hector_montage_name(anim),
                                           HECTOR_MONTAGE_DIR,
                                           unreal.AnimMontage, factory)
        if not montage:
            error("Failed to create montage for %s" % anim)
            return None
        STATS["created"] += 1

    save_asset(path)
    return montage


def create_hector_montages(sequences, skeleton):
    for anim in HECTOR_ANIMATIONS:
        sequence = sequences.get(anim)
        if not sequence:
            continue
        montage = create_hector_montage(anim, sequence, skeleton)
        if montage:
            ANIM_MONTAGES[anim] = montage
    log("Created %d Hector montages" % len(ANIM_MONTAGES))
    return ANIM_MONTAGES


# Spec states (AnimationBlueprintSpec.md §1) mapped to the authored clips.
# States whose dedicated clip is not authored yet reuse the closest clip and are
# reported, so the art gap stays visible instead of looking finished.
HECTOR_STATE_CLIPS = {
    "Idle": "Idle",
    "Walk": "Walk",
    "Run": "Run",
    "JumpStart": "Jump",
    "JumpLoop": "Jump",
    "JumpLand": "Jump",
    "Light1": "Light1",
    "Light2": "Light2",
    "Light3": "Light3",
    "Heavy": "Heavy",
    "GuardStart": "Guard",
    "GuardLoop": "Guard",
    "GuardRelease": "Guard",
    "PerfectGuard": "Guard",
    "QuickStep": "QuickStep",
    "HitReaction": "HitReaction",
    "Death": "Death",
}

# States that must not loop.
HECTOR_ONESHOT_STATES = {
    "JumpStart", "JumpLand", "Light1", "Light2", "Light3", "Heavy",
    "GuardStart", "GuardRelease", "PerfectGuard", "QuickStep",
    "HitReaction", "Death",
}

# One-shot states return to Idle when their clip finishes. Combo chaining and
# input-driven transitions need the AnimBlueprint event graph (see the warning
# logged by build_hector_state_machine).
HECTOR_RETURN_TO_IDLE = (
    "JumpLand", "Light1", "Light2", "Light3", "Heavy", "GuardRelease",
    "PerfectGuard", "QuickStep", "HitReaction",
)

# Locomotion switches are driven by bool variables the event graph sets.
HECTOR_LOCOMOTION_RULES = (
    ("Idle", "Walk", 0.10, "bIsMoving"),
    ("Idle", "Run", 0.10, "bIsRunning"),
    ("Walk", "Run", 0.10, "bIsRunning"),
    ("Run", "Walk", 0.10, "bIsMoving"),
    ("Walk", "Idle", 0.10, "bIsIdle"),
    ("Run", "Idle", 0.10, "bIsIdle"),
)

def _connect(src_node, dst_node):
    """Connect src_node's pose output to the first input dst_node accepts.

    Pin names differ between anim nodes (the montage slot's pose input is
    ``Source`` while the graph root's is ``Result``), so let the graph schema
    validate each candidate instead of matching names.
    """
    if not src_node or not dst_node:
        return False
    for out_pin in src_node.list_output_pins():
        for in_pin in dst_node.list_input_pins():
            try:
                if out_pin.try_create_connection(in_pin):
                    return True
            except Exception:
                continue
    return False


def _find_node(graph, class_name):
    for node in graph.get_graph_nodes_of_class(unreal.AnimGraphNode_Base):
        if node.get_class().get_name() == class_name:
            return node
    return None


def build_hector_state_machine(blueprint, sequences):
    """Author the Hector state machine through the editor authoring bridge.

    UE 5.8 does not let Python add nodes to an AnimationStateMachineGraph (the
    graph's node list and UAnimStateNode::BoundGraph are not script-visible), so
    this delegates to the NobleArchimedesEditor module.
    """
    library = getattr(unreal, "NobleAnimGraphAuthoring", None)
    if not library:
        warn("NobleAnimGraphAuthoring is unavailable; skipping the state machine")
        return False

    machine = library.get_or_create_state_machine(blueprint, "Locomotion")
    if not machine:
        error("Could not create the Hector state machine")
        return False

    states = {}
    aliased = []
    for state_name, clip in HECTOR_STATE_CLIPS.items():
        sequence = sequences.get(clip)
        if not sequence:
            warn("State %s has no clip (%s missing)" % (state_name, clip))
            continue
        state = library.add_state(machine, state_name, sequence,
                                  state_name not in HECTOR_ONESHOT_STATES)
        if state:
            states[state_name] = state
        if clip != state_name:
            aliased.append("%s->%s" % (state_name, clip))

    if not states:
        error("No Hector states were created")
        return False

    library.set_entry_state(machine, states.get("Idle"))

    # One-shots return to Idle automatically once their clip ends.
    for state_name in HECTOR_RETURN_TO_IDLE:
        source, target = states.get(state_name), states.get("Idle")
        if source and target:
            library.add_transition(machine, source, target, 0.10, True)

    # Locomotion switches read bool variables that the event graph will set.
    for from_name, to_name, blend, variable in HECTOR_LOCOMOTION_RULES:
        source, target = states.get(from_name), states.get(to_name)
        if not (source and target):
            continue
        library.add_bool_variable(blueprint, variable, False)
        transition = library.add_transition(machine, source, target, blend, False)
        if transition:
            library.set_transition_rule_variable(transition, variable)

    compiled = library.compile_anim_blueprint(blueprint)
    names = [str(n) for n in library.get_state_names(machine)]
    log("Hector state machine: %d states, %d transitions, compiled=%s"
        % (len(names), library.get_transition_count(machine), compiled))
    if aliased:
        warn("States reusing another clip (art gap): %s" % ", ".join(sorted(aliased)))
    warn("Locomotion rules (bIsMoving/bIsRunning/bIsIdle) still need the "
         "AnimBlueprint event graph; until then the machine rests in Idle.")
    return compiled


def create_hector_anim_blueprint(skeleton, sequences):
    """Create AB_Hector with a Slot node so montages reach the output pose.

    Combat animations are played directly through ``PlayAnimMontage``, so the
    AnimGraph only needs to forward the base pose through the default slot.
    Idle is fed into the slot as the resting pose.
    """
    path = asset_path(HECTOR_DIR, HECTOR_ANIMBP_NAME)
    blueprint = load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
    if blueprint:
        STATS["updated"] += 1
    else:
        factory = unreal.AnimBlueprintFactory()
        set_prop(factory, "target_skeleton", skeleton)
        blueprint = ASSET_TOOLS.create_asset(HECTOR_ANIMBP_NAME, HECTOR_DIR,
                                             unreal.AnimBlueprint, factory)
        if not blueprint:
            error("Failed to create %s" % HECTOR_ANIMBP_NAME)
            return None
        STATS["created"] += 1

    graphs = blueprint.get_animation_graphs()
    anim_graph = graphs[0] if graphs else None
    if not anim_graph:
        error("%s has no animation graph" % HECTOR_ANIMBP_NAME)
        return blueprint

    try:
        editor = unreal.BlueprintGraphEditor.get_graph_editor(anim_graph)
    except Exception as exc:
        warn("Could not open the %s graph editor: %r"
             % (HECTOR_ANIMBP_NAME, exc))
        editor = None

    if not editor:
        return blueprint

    slot = _find_node(anim_graph, "AnimGraphNode_Slot")
    if not slot:
        for action in ("Animation|Montage|Slot'DefaultSlot'",
                       "Animation|Montage|Slot'DefaultGroup.DefaultSlot'"):
            try:
                slot = editor.create_node_from_name(action,
                                                    unreal.Vector2D(360, 0), [])
            except Exception:
                slot = None
            if slot:
                break

    if not slot:
        warn("Montage slot node is unavailable; montages will not render")
        save_asset(path)
        return blueprint

    root = _find_node(anim_graph, "AnimGraphNode_Root")
    if not _connect(slot, root):
        warn("Could not connect the montage slot to the AnimGraph output")

    player = _find_node(anim_graph, "AnimGraphNode_SequencePlayer")
    if not player:
        try:
            player = editor.create_node_from_name(
                "Animation|Sequences|SequencePlayer", unreal.Vector2D(120, 0), [])
        except Exception:
            player = None

    idle = sequences.get("Idle")
    if player and idle:
        node_struct = get_prop(player, "node")
        if node_struct is not None and set_prop(node_struct, "sequence", idle):
            set_prop(player, "node", node_struct)
        if not _connect(player, slot):
            warn("Could not connect the idle player to the slot")

    save_asset(path)
    return blueprint


def build_hector_animation():
    """Run the whole Hector animation pipeline.

    Must run before the data tables so the weapon rows can reference the
    generated montages.
    """
    if not os.path.isdir(HECTOR_FBX_DIR):
        warn("Hector FBX sources not found at %s; skipping animation build"
             % HECTOR_FBX_DIR)
        return False

    mesh, skeleton = import_hector_mesh()
    if not skeleton:
        return False

    sequences = import_hector_animations(skeleton)
    create_hector_montages(sequences, skeleton)
    blueprint = create_hector_anim_blueprint(skeleton, sequences)
    if blueprint:
        build_hector_state_machine(blueprint, sequences)
    return True


def weapon_montage_refs(weapon_type):
    """Return (combo paths, finisher paths) for a weapon type's data table row."""
    combo_anims, finisher_anims = WEAPON_ANIM_SETS.get(
        weapon_type, (["Light1", "Light2", "Light3"], ["Heavy"]))

    def to_paths(anims):
        paths = []
        for anim in anims:
            montage = ANIM_MONTAGES.get(anim)
            if montage:
                paths.append(montage.get_path_name())
        return paths

    combo = to_paths(combo_anims)
    if combo and len(combo) < COMBO_STAGES:
        # The combat code always advances to three stages, so repeat the last
        # authored montage rather than leaving a stage with nothing to play.
        while len(combo) < COMBO_STAGES:
            combo.append(combo[-1])
        warn("%s authors %d combo montages; padded to %d stages"
             % (weapon_type, len(combo_anims), COMBO_STAGES))

    # The finisher is indexed by the current combo stage, so repeat the heavy
    # montage across every stage it can be requested from.
    finisher_source = to_paths(finisher_anims)
    finisher = []
    if finisher_source:
        for stage in range(COMBO_STAGES):
            finisher.append(finisher_source[stage % len(finisher_source)])
    return combo, finisher




# ---------------------------------------------------------------------------
# Data tables
# ---------------------------------------------------------------------------

INT_FIELDS = {
    "Chapter", "Count", "Level", "Experience", "Health", "MaxHealth", "Attack",
    "ForgeLevel", "EvoCrystalCount", "Material1Count", "Material2Count",
    "Material3Count", "Material4Count", "ComboAnimCount", "FinalAttackAnimCount",
    "SaveRoomCount", "GreenDoorRoomCount",
}

FLOAT_FIELDS = {
    "AttackRange", "AttackSpeed", "BaseDamage", "Damage", "DetectionRange",
    "RespawnTime", "DropChance", "AttackPower",
}

BOOL_FIELDS = {
    "IsBoss", "Stealable", "CanBeStolen", "bIsUnlocked", "bIsEvolved",
    "IsStealOnly", "IsRare", "bIsRare",
}

ENUM_FIELDS = {
    "WeaponType", "DamageType", "EvoCrystalColor", "DevilType",
    "InnocentDevilAcquired", "EvolutionCrystalColor",
}

# csv column -> struct property when the names differ
RENAMES = {
    "SaveRooms": "SaveRoomCount",
    "GreenDoorRooms": "GreenDoorRoomCount",
}

TABLE_CONFIG = {
    "WeaponDataTable.csv": {"key": ["WeaponName"]},
    "MaterialDataTable.csv": {
        "key": ["MaterialName"],
        "color": {"MaterialColor": ["MaterialColorR", "MaterialColorG", "MaterialColorB", "MaterialColorA"]},
        "skip": ["MaterialColorR", "MaterialColorG", "MaterialColorB", "MaterialColorA"],
        "renames": {"IsRare": "bIsRare"},
    },
    "WeaponRecipeTable.csv": {"key": ["WeaponName"], "array": ["RequiredMaterials"]},
    "WeaponRecipeTable_Complete.csv": {
        "key": ["WeaponName"],
        "array": ["RequiredMaterials"],
        "skip": ["AttackPower", "AttackSpeed", "AttackRange", "EvoCrystalColor"],
    },
    "WeaponMaterialRequirements.csv": {"key": ["WeaponName"]},
    "InnocentDevilDataTable.csv": {"key": ["DevilName"]},
    "EnemyDataTable.csv": {"key": ["EnemyName"]},
    "EnemyEncounterTable.csv": {"key": ["Chapter", "EnemyName"]},
    "ItemDropTable.csv": {"key": ["EnemyName", "ItemName"]},
    "InnocentDevilEvolutionTable.csv": {"key": ["DevilName", "Level"]},
    "ChapterProgressionTable.csv": {"key": ["Chapter"]},
}


def parse_value(field, raw, cfg):
    value = (raw or "").strip()
    if value == "":
        return None

    if field in cfg.get("array", []):
        return [part.strip() for part in value.split(";") if part.strip()]

    if field in BOOL_FIELDS:
        return value.lower() in ("true", "1", "yes")
    if field in INT_FIELDS:
        try:
            return int(float(value))
        except ValueError:
            warn("Bad int '%s' for %s; keeping 0" % (value, field))
            return 0
    if field in FLOAT_FIELDS:
        try:
            return float(value)
        except ValueError:
            warn("Bad float '%s' for %s; keeping 0.0" % (value, field))
            return 0.0
    return value


def read_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_rows(csv_file, rows, cfg):
    key_columns = cfg["key"]
    result = {}
    used = {}

    for index, row in enumerate(rows):
        clean = {}
        for key, value in row.items():
            if key is None:
                continue
            if isinstance(value, list):
                value = value[0] if value else ""
            clean[key.strip()] = (value or "").strip()
        row = clean

        key_parts = [row.get(column, "") for column in key_columns]
        base_key = "_".join(part for part in key_parts if part) or "Row_%03d" % index
        used[base_key] = used.get(base_key, 0) + 1
        row_key = base_key if used[base_key] == 1 else "%s_%d" % (base_key, used[base_key])
        row_key = re.sub(r"[^A-Za-z0-9_\- ]", "_", row_key)

        payload = {}
        skip = set(cfg.get("skip", []))
        color_specs = cfg.get("color", {})
        renames = cfg.get("renames", {})

        for column, raw in row.items():
            if not column or column in skip:
                continue
            field = renames.get(column, RENAMES.get(column, column))
            value = parse_value(field, raw, cfg)
            if value is None:
                continue
            payload[field] = value

        for property_name, components in color_specs.items():
            values = []
            for component in components:
                raw = row.get(component, "").strip()
                try:
                    values.append(float(raw) if raw else 0.0)
                except ValueError:
                    values.append(0.0)
            if any(v != 0.0 for v in values):
                payload[property_name] = {
                    "R": values[0], "G": values[1], "B": values[2],
                    "A": values[3] if len(values) > 3 else 1.0,
                }

        result[row_key] = payload

    return result


def apply_weapon_montages(entry):
    """Attach the generated montage references to one weapon table row.

    FWeaponData.ComboAnimations / FinalAttackAnimations are hard object
    references, so the row carries asset paths that the JSON importer resolves
    through ImportText.
    """
    if not ANIM_MONTAGES:
        return
    weapon_type = entry.get("WeaponType")
    if not weapon_type:
        return

    combo, finisher = weapon_montage_refs(weapon_type)
    if combo:
        entry["ComboAnimations"] = combo
    if finisher:
        entry["FinalAttackAnimations"] = finisher


def import_data_table(csv_file, struct_name, suggested_name):
    csv_path = os.path.join(DATA_TABLE_DIR, csv_file)
    if not os.path.exists(csv_path):
        error("Missing CSV: %s" % csv_path)
        return

    struct_path = "/Script/NobleArchimedes.%s" % (struct_name[1:] if struct_name.startswith("F") else struct_name)
    struct_obj = unreal.load_object(None, struct_path)
    if not struct_obj:
        error("Missing struct %s (%s)" % (struct_name, struct_path))
        return

    cfg = TABLE_CONFIG.get(csv_file, {"key": []})
    rows = read_csv(csv_path)
    payload_rows = build_rows(csv_file, rows, cfg)
    if not payload_rows:
        error("No rows parsed from %s" % csv_file)
        return

    folder = "/Game/DataTables"
    path = asset_path(folder, suggested_name)

    # Refill in place. The asset keeps a stable path so Blueprint references
    # survive re-imports. If a future C++ change alters a row struct's memory
    # layout (not just enum values), delete the asset once and rerun.
    table = None
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        table = load_asset(path)
        if table:
            # The JSON importer replaces matching row names, so stable CSVs
            # can be refilled in place without touching the asset identity.
            STATS["updated"] += 1

    if not table:
        factory = unreal.DataTableFactory()
        factory.set_editor_property("struct", struct_obj)
        table = ASSET_TOOLS.create_asset(suggested_name, folder, unreal.DataTable, factory)
        STATS["created"] += 1
    if not table:
        error("Failed to create DataTable %s" % path)
        return

    # UE's JSON DataTable importer expects a top-level array of row objects and
    # reads the row name from the "Name" field (ImportKeyField defaults to
    # "Name"). The key field is skipped when matching struct properties.
    json_rows = []
    for row_key, payload in payload_rows.items():
        entry = {"Name": row_key}
        entry.update(payload)
        if csv_file == "WeaponDataTable.csv":
            apply_weapon_montages(entry)
        json_rows.append(entry)

    json_text = json.dumps(json_rows, indent=2)
    ok = unreal.DataTableFunctionLibrary.fill_data_table_from_json_string(table, json_text)
    if not ok:
        error("JSON import failed for %s" % suggested_name)
        return

    table.modify()
    actual_rows = table.get_row_names()
    if len(actual_rows) != len(payload_rows):
        error("%s imported %d of %d rows" % (suggested_name, len(actual_rows), len(payload_rows)))
        return

    unreal.EditorAssetLibrary.save_loaded_asset(table, only_if_is_dirty=False)
    log("Imported %s: %d rows -> %s" % (csv_file, len(actual_rows), path))


def import_all_data_tables():
    if not os.path.exists(MANIFEST_PATH):
        error("Missing manifest: %s" % MANIFEST_PATH)
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)

    for entry in manifest.get("tables", []):
        import_data_table(entry["csv_file"], entry["struct_name"], entry["suggested_name"])


# ---------------------------------------------------------------------------
# Blueprints
# ---------------------------------------------------------------------------

BLUEPRINTS = [
    ("BP_HectorCharacter", "/Game/Blueprints/Characters", "/Script/NobleArchimedes.HectorCharacter"),
    ("BP_EnemyBase", "/Game/Blueprints/Characters", "/Script/NobleArchimedes.EnemyBase"),
    ("BP_BossBase", "/Game/Blueprints/Characters", "/Script/NobleArchimedes.BossBase"),
    ("BP_InnocentDevilActor", "/Game/Blueprints/Characters", "/Script/NobleArchimedes.InnocentDevilActor"),
    ("BP_Room", "/Game/Blueprints/World", "/Script/NobleArchimedes.Room"),
    ("BP_SaveRoom", "/Game/Blueprints/World", "/Script/NobleArchimedes.SaveRoom"),
    ("BP_CandleBreakable", "/Game/Blueprints/World", "/Script/NobleArchimedes.CandleBreakable"),
    ("BP_ItemDrop", "/Game/Blueprints/World", "/Script/NobleArchimedes.ItemDrop"),
    ("BP_ChapterPortal", "/Game/Blueprints/World", "/Script/NobleArchimedes.ChapterPortal"),
    ("BP_MapChecker", "/Game/Blueprints/System", "/Script/NobleArchimedes.MapChecker"),
    ("BP_NobleArchimedesHUD", "/Game/Blueprints/UI", "/Script/NobleArchimedes.NobleArchimedesHUD"),
    ("BP_NobleHUDWidget", "/Game/Blueprints/UI", "/Script/NobleArchimedes.NobleHUDWidget"),
    ("BP_NobleArchimedesGameModeBase", "/Game/Blueprints/Core", "/Script/NobleArchimedes.NobleArchimedesGameModeBase"),
    ("BP_NobleArchimedesPlayerController", "/Game/Blueprints/Core", "/Script/NobleArchimedes.NobleArchimedesPlayerController"),
    ("BP_NobleArchimedesGameInstance", "/Game/Blueprints/Core", "/Script/NobleArchimedes.NobleArchimedesGameInstance"),
]

# The CSV row is the source of truth for stats; the Blueprint supplies the
# class and the placeholder mesh. Additional archetypes are generated from
# EnemyDataTable.csv so every chapter can spawn real enemy classes.
ENEMY_ARCHETYPES = {
    "BP_Skeleton": ("BP_EnemyBase", "Skeleton"),
    "BP_Zombie": ("BP_EnemyBase", "Zombie"),
    "BP_Ghoul": ("BP_EnemyBase", "Ghoul"),
    "BP_SentinelKnight": ("BP_BossBase", "Castle Elite"),
}

BOSS_ENEMY_NAMES = set()


def enemy_bp_name(enemy_name):
    if enemy_name in ("Sentinel Knight", "Castle Elite"):
        return "BP_SentinelKnight"
    for bp_name, (_, row_name) in ENEMY_ARCHETYPES.items():
        if row_name == enemy_name:
            return bp_name
    return "BP_EnemyBase"


def expand_enemy_archetypes(enemy_stats):
    encounter_path = os.path.join(DATA_TABLE_DIR, "EnemyEncounterTable.csv")
    if os.path.exists(encounter_path):
        for row in read_csv(encounter_path):
            if str(row.get("IsBoss", "false")).lower() == "true":
                BOSS_ENEMY_NAMES.add(row.get("EnemyName", ""))

    mapped_rows = {row_name for _, row_name in ENEMY_ARCHETYPES.values()}
    for enemy_name in enemy_stats:
        if enemy_name in mapped_rows:
            continue
        bp_name = "BP_" + "".join(
            part.capitalize() for part in re.split(r"[^A-Za-z0-9]+", enemy_name)
            if part)
        parent = "BP_BossBase" if enemy_name in BOSS_ENEMY_NAMES else "BP_EnemyBase"
        ENEMY_ARCHETYPES[bp_name] = (parent, enemy_name)


def load_enemy_stats():
    path = os.path.join(DATA_TABLE_DIR, "EnemyDataTable.csv")
    if not os.path.exists(path):
        error("Missing enemy stats CSV: %s" % path)
        return {}
    return {row["EnemyName"]: row for row in read_csv(path)}


def apply_enemy_stats(cdo, row, drop_class, is_boss=False):
    if not row:
        return False

    set_prop(cdo, "EnemyName", row["EnemyName"])
    set_prop(cdo, "ChapterNumber", int(float(row.get("Chapter", 1))))
    health = float(row.get("Health", 50.0))
    set_prop(cdo, "Health", health)
    set_prop(cdo, "MaxHealth", health)
    set_prop(cdo, "Damage", float(row.get("Damage", 10.0)))
    set_prop(cdo, "AttackRange", float(row.get("AttackRange", 150.0)))
    set_prop(cdo, "DetectionRange", float(row.get("DetectionRange", 600.0)))
    set_prop(cdo, "Weaknesses", row.get("Weaknesses", ""))
    set_prop(cdo, "Tolerances", row.get("Tolerances", ""))
    set_prop(cdo, "ItemDrops", row.get("ItemDrops", ""))
    can_steal = str(row.get("CanBeStolen", "false")).lower() == "true"
    set_prop(cdo, "CanBeStolen", can_steal)
    set_prop(cdo, "bIsBoss", bool(is_boss))

    drops = [part.strip() for part in row.get("ItemDrops", "").split(";")
             if part.strip() and part.strip().lower() != "none"]
    if can_steal and drops:
        set_prop(cdo, "StealItem", drops[0])

    if drop_class:
        set_prop(cdo, "ItemDropClass", drop_class)
    return True


def create_all_blueprints():
    for name, folder, parent in BLUEPRINTS:
        ensure_blueprint(name, folder, parent)

    enemy_stats = load_enemy_stats()
    expand_enemy_archetypes(enemy_stats)
    drop_class = bp_class("/Game/Blueprints/World", "BP_ItemDrop")

    # Base classes keep the drop class so every child can spawn loot.
    for base_name in ("BP_EnemyBase", "BP_BossBase"):
        base_cls = bp_class("/Game/Blueprints/Characters", base_name)
        if base_cls and drop_class:
            set_prop(unreal.get_default_object(base_cls), "ItemDropClass", drop_class)

    for name, (parent_name, row_name) in ENEMY_ARCHETYPES.items():
        parent_folder = "/Game/Blueprints/Characters"
        parent_path = asset_path(parent_folder, parent_name)
        bp = ensure_blueprint(name, parent_folder, parent_path)
        if not bp:
            continue
        cls = bp_class(parent_folder, name)
        if not cls:
            error("Missing generated class for %s" % name)
            continue
        cdo = unreal.get_default_object(cls)
        if not apply_enemy_stats(cdo, enemy_stats.get(row_name), drop_class,
                                 parent_name == "BP_BossBase"):
            warn("No enemy data for %s (%s)" % (name, row_name))
        unreal.EditorAssetLibrary.save_asset(asset_path(parent_folder, name))

    # The reusable boss base gets the final-boss baseline.
    boss_cls = bp_class("/Game/Blueprints/Characters", "BP_BossBase")
    if boss_cls:
        boss_cdo = unreal.get_default_object(boss_cls)
        apply_enemy_stats(boss_cdo, enemy_stats.get("Final Boss"), drop_class, True)
        unreal.EditorAssetLibrary.save_asset(asset_path("/Game/Blueprints/Characters", "BP_BossBase"))

    # Give the Innocent Devil placeholder a visible body.
    devil_cls = bp_class("/Game/Blueprints/Characters", "BP_InnocentDevilActor")
    if devil_cls:
        devil_cdo = unreal.get_default_object(devil_cls)
        skeletal_cube = unreal.load_asset("/Engine/EngineMeshes/SkeletalCube.SkeletalCube")
        mesh = get_prop(devil_cdo, "Mesh")
        if skeletal_cube and mesh:
            set_prop(mesh, "SkeletalMeshAsset", skeletal_cube)
            set_prop(mesh, "RelativeScale3D", unreal.Vector(0.6, 0.6, 1.1))
        unreal.EditorAssetLibrary.save_asset(asset_path("/Game/Blueprints/Characters", "BP_InnocentDevilActor"))

    # Make dropped items visible in the blockout.
    item_cls = bp_class("/Game/Blueprints/World", "BP_ItemDrop")
    if item_cls:
        item_cdo = unreal.get_default_object(item_cls)
        cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
        item_mesh = get_prop(item_cdo, "ItemMesh")
        if cube and item_mesh:
            set_prop(item_mesh, "StaticMesh", cube)
            set_prop(item_mesh, "RelativeScale3D", unreal.Vector(0.25, 0.25, 0.25))
        unreal.EditorAssetLibrary.save_asset(asset_path("/Game/Blueprints/World", "BP_ItemDrop"))

    # Candles are the early source of forge materials.
    candle_cls = bp_class("/Game/Blueprints/World", "BP_CandleBreakable")
    if candle_cls:
        candle_cdo = unreal.get_default_object(candle_cls)
        candle_mesh = get_prop(candle_cdo, "CandleMesh")
        if cube and candle_mesh:
            set_prop(candle_mesh, "StaticMesh", cube)
            set_prop(candle_mesh, "RelativeScale3D", unreal.Vector(0.12, 0.12, 0.5))
        if item_cls:
            set_prop(candle_cdo, "ItemDropClass", item_cls)
        set_prop(candle_cdo, "PossibleDrops", ["Iron Shard", "Potion", "Silver Ingot"])
        set_prop(candle_cdo, "DropChance", 1.0)
        unreal.EditorAssetLibrary.save_asset(asset_path("/Game/Blueprints/World", "BP_CandleBreakable"))

    portal_cls = bp_class("/Game/Blueprints/World", "BP_ChapterPortal")
    if portal_cls:
        portal_cdo = unreal.get_default_object(portal_cls)
        portal_mesh = get_prop(portal_cdo, "PortalMesh")
        if cube and portal_mesh:
            set_prop(portal_mesh, "StaticMesh", cube)
            set_prop(portal_mesh, "RelativeScale3D", unreal.Vector(2.4, 0.15, 3.0))
        set_prop(portal_cdo, "bRequireBossDefeated", True)
        unreal.EditorAssetLibrary.save_asset(asset_path("/Game/Blueprints/World", "BP_ChapterPortal"))


def configure_character_blueprint(input_assets, imc):
    folder = "/Game/Blueprints/Characters"
    cls = bp_class(folder, "BP_HectorCharacter")
    if not cls:
        error("BP_HectorCharacter class not found")
        return

    cdo = unreal.get_default_object(cls)
    set_prop(cdo, "DefaultMappingContext", imc, required=True)
    for prop, asset_name in (
        ("MoveAction", "IA_Move"),
        ("LookAction", "IA_Look"),
        ("JumpAction", "IA_Jump"),
        ("LightAttackAction", "IA_LightAttack"),
        ("HeavyAttackAction", "IA_HeavyAttack"),
        ("GuardAction", "IA_Guard"),
        ("DodgeAction", "IA_Dodge"),
        ("InteractAction", "IA_Interact"),
        ("SummonDevilAction", "IA_SummonDevil"),
        ("CameraModeAction", "IA_CameraMode"),
        ("LockOnAction", "IA_LockOn"),
        ("MapAction", "IA_Map"),
        ("PauseAction", "IA_Pause"),
        ("UseItemAction", "IA_UseItem"),
        ("ForgeAction", "IA_Forge"),
        ("QuickSaveAction", "IA_QuickSave"),
        ("QuickLoadAction", "IA_QuickLoad"),
    ):
        ia = input_assets.get(asset_name)
        if ia:
            set_prop(cdo, prop, ia, required=True)

    # Data-driven combat: point the component at the imported weapon table.
    combat = get_prop(cdo, "CombatComponent")
    weapon_table = unreal.load_asset("/Game/DataTables/DT_WeaponDataTable")
    if combat and weapon_table:
        set_prop(combat, "WeaponDataTableAsset", weapon_table, required=True)
        set_prop(combat, "DefaultWeaponName", "Short Sword")
    elif not combat:
        warn("BP_HectorCharacter has no CombatComponent default subobject")

    # Spawn the visible Innocent Devil actor when one is summoned.
    devil_component = get_prop(cdo, "InnocentDevilComponent")
    devil_class = bp_class("/Game/Blueprints/Characters", "BP_InnocentDevilActor")
    if devil_component and devil_class:
        set_prop(devil_component, "DevilActorClass", devil_class, required=True)
    elif not devil_component:
        warn("BP_HectorCharacter has no InnocentDevilComponent default subobject")

    # Use the generated Hector mesh once it exists; otherwise keep a visible
    # placeholder so the blockout stays readable.
    mesh = get_prop(cdo, "Mesh")
    hector_mesh = load_asset("/Game/Characters/Hector/SK_Hector")
    hector_anim = load_asset("/Game/Characters/Hector/AB_Hector")
    if mesh and hector_mesh:
        set_prop(mesh, "SkeletalMeshAsset", hector_mesh)
        set_prop(mesh, "RelativeScale3D", unreal.Vector(1.0, 1.0, 1.0))
        if hector_anim:
            anim_class = hector_anim.generated_class()
            if anim_class:
                set_prop(mesh, "AnimClass", anim_class)
    elif mesh:
        skeletal_cube = load_asset("/Engine/EngineMeshes/SkeletalCube.SkeletalCube")
        if skeletal_cube:
            set_prop(mesh, "SkeletalMeshAsset", skeletal_cube)
            set_prop(mesh, "RelativeScale3D", unreal.Vector(0.9, 0.9, 1.8))

    unreal.EditorAssetLibrary.save_asset(asset_path(folder, "BP_HectorCharacter"))


def configure_game_mode_blueprint():
    core = "/Game/Blueprints/Core"
    gm_cls = bp_class(core, "BP_NobleArchimedesGameModeBase")
    hector_cls = bp_class("/Game/Blueprints/Characters", "BP_HectorCharacter")
    hud_cls = bp_class("/Game/Blueprints/UI", "BP_NobleArchimedesHUD")
    pc_cls = bp_class(core, "BP_NobleArchimedesPlayerController")

    if not (gm_cls and hector_cls and hud_cls and pc_cls):
        error("Cannot configure GameMode: missing generated classes")
        return

    cdo = unreal.get_default_object(gm_cls)
    set_prop(cdo, "DefaultPawnClass", hector_cls, required=True)
    set_prop(cdo, "PlayerControllerClass", pc_cls, required=True)
    set_prop(cdo, "HUDClass", hud_cls, required=True)

    chapter_table = unreal.load_asset("/Game/DataTables/DT_ChapterProgressionTable")
    if chapter_table:
        set_prop(cdo, "ChapterProgressionTable", chapter_table, required=True)
    else:
        warn("DT_ChapterProgressionTable unavailable; chapter unlocks will use defaults")

    # Give the HUD its default widget (the C++ layout for now).
    hud_widget_cls = bp_class("/Game/Blueprints/UI", "BP_NobleHUDWidget")
    if hud_widget_cls:
        hud_cdo = unreal.get_default_object(hud_cls)
        set_prop(hud_cdo, "HUDWidgetClass", hud_widget_cls, required=True)
        unreal.EditorAssetLibrary.save_asset(asset_path("/Game/Blueprints/UI", "BP_NobleArchimedesHUD"))
    else:
        warn("BP_NobleHUDWidget class unavailable; HUD will start empty")

    unreal.EditorAssetLibrary.save_asset(asset_path(core, "BP_NobleArchimedesGameModeBase"))


# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------

INPUT_ACTIONS = [
    ("IA_Move", unreal.InputActionValueType.AXIS2D),
    ("IA_Look", unreal.InputActionValueType.AXIS2D),
    ("IA_Jump", unreal.InputActionValueType.BOOLEAN),
    ("IA_LightAttack", unreal.InputActionValueType.BOOLEAN),
    ("IA_HeavyAttack", unreal.InputActionValueType.BOOLEAN),
    ("IA_Guard", unreal.InputActionValueType.BOOLEAN),
    ("IA_Dodge", unreal.InputActionValueType.BOOLEAN),
    ("IA_Interact", unreal.InputActionValueType.BOOLEAN),
    ("IA_SummonDevil", unreal.InputActionValueType.BOOLEAN),
    ("IA_CameraMode", unreal.InputActionValueType.BOOLEAN),
    ("IA_LockOn", unreal.InputActionValueType.BOOLEAN),
    ("IA_Map", unreal.InputActionValueType.BOOLEAN),
    ("IA_Pause", unreal.InputActionValueType.BOOLEAN),
    ("IA_UseItem", unreal.InputActionValueType.BOOLEAN),
    ("IA_Forge", unreal.InputActionValueType.BOOLEAN),
    ("IA_QuickSave", unreal.InputActionValueType.BOOLEAN),
    ("IA_QuickLoad", unreal.InputActionValueType.BOOLEAN),
]

# (action, key, negate X, negate Y, swizzle YXZ)
INPUT_MAPPINGS = [
    ("IA_Move", "W", False, False, True),
    ("IA_Move", "S", False, True, True),
    ("IA_Move", "D", False, False, False),
    ("IA_Move", "A", True, False, False),
    ("IA_Move", "Gamepad_Left2D", False, False, False),
    ("IA_Look", "Mouse2D", False, True, False),
    ("IA_Look", "Gamepad_Right2D", False, False, False),
    ("IA_Jump", "SpaceBar", False, False, False),
    ("IA_Jump", "Gamepad_FaceButton_Bottom", False, False, False),
    ("IA_LightAttack", "LeftMouseButton", False, False, False),
    ("IA_LightAttack", "Gamepad_FaceButton_Left", False, False, False),
    ("IA_HeavyAttack", "RightMouseButton", False, False, False),
    ("IA_HeavyAttack", "Gamepad_FaceButton_Top", False, False, False),
    ("IA_Guard", "LeftControl", False, False, False),
    ("IA_Guard", "Gamepad_LeftShoulder", False, False, False),
    ("IA_Dodge", "LeftShift", False, False, False),
    ("IA_Dodge", "Gamepad_FaceButton_Right", False, False, False),
    ("IA_Interact", "E", False, False, False),
    ("IA_Interact", "Gamepad_RightShoulder", False, False, False),
    ("IA_SummonDevil", "Q", False, False, False),
    ("IA_SummonDevil", "Gamepad_DPad_Up", False, False, False),
    ("IA_CameraMode", "C", False, False, False),
    ("IA_CameraMode", "Gamepad_DPad_Down", False, False, False),
    ("IA_LockOn", "MiddleMouseButton", False, False, False),
    ("IA_Map", "Tab", False, False, False),
    ("IA_Map", "Gamepad_Special_Left", False, False, False),
    ("IA_Pause", "Escape", False, False, False),
    ("IA_Pause", "Gamepad_Special_Right", False, False, False),
    ("IA_UseItem", "R", False, False, False),
    ("IA_UseItem", "Gamepad_DPad_Left", False, False, False),
    ("IA_Forge", "F", False, False, False),
    ("IA_Forge", "Gamepad_DPad_Right", False, False, False),
    ("IA_QuickSave", "F5", False, False, False),
    ("IA_QuickLoad", "F9", False, False, False),
]


def create_input_assets():
    actions = {}
    for name, value_type in INPUT_ACTIONS:
        actions[name] = create_input_action(name, value_type)

    imc = create_mapping_context("IMC_Default")
    if not imc:
        return actions, None

    unreal.NobleInputBuilder.clear_mappings(imc)
    for action_name, key, neg_x, neg_y, swizzle in INPUT_MAPPINGS:
        action = actions.get(action_name)
        if not action:
            error("Missing input action %s for mapping %s" % (action_name, key))
            continue
        unreal.NobleInputBuilder.add_key_mapping(imc, action, key, neg_x, neg_y, swizzle)

    save_asset("/Game/Input/IMC_Default")
    return actions, imc


# ---------------------------------------------------------------------------
# Chapter 1 blockout
# ---------------------------------------------------------------------------

MAP_PATH = "/Game/Maps/Chap_01_AbandonedCastle"
BLOCKOUT_TAG = "NA_Blockout"

CHAPTER_MAP_NAMES = {
    1: "Chap_01_AbandonedCastle",
    2: "Chap_02_BaljhetMountains",
    3: "Chap_03_GaribaldiTemple",
    4: "Chap_04_MortviaAqueduct",
    5: "Chap_05_ForestOfJigramunt",
    6: "Chap_06_CordovaTown",
    7: "Chap_07_EneomaosMachineTower",
    8: "Chap_08_AiolonRuins",
    9: "Chap_09_InfiniteCorridor",
    10: "Chap_10_DraculasCastle",
}

# Room names follow Content/Maps/LevelDesignSpec.md. The generic blockout uses
# the first three names for the entry, mid and boss rooms, plus a save room.
CHAPTER_SPECS = {
    2: {"chapter_name": "Baljhet Mountains", "rooms": ("Mountain Pass", "Cliffside Cave", "Summit"),
        "light": (0.55, 0.68, 1.0)},
    3: {"chapter_name": "Garibaldi Temple", "rooms": ("Nave", "Crypt", "Bell Tower"),
        "light": (1.0, 0.82, 0.48)},
    4: {"chapter_name": "Mortvia Aqueduct", "rooms": ("Water Chamber", "Bridge Crossing", "Deep Conduit"),
        "light": (0.35, 0.75, 0.9)},
    5: {"chapter_name": "Forest of Jigramunt", "rooms": ("Forest Edge", "Deep Forest", "Ancient Grove"),
        "light": (0.45, 0.9, 0.5)},
    6: {"chapter_name": "Cordova Town", "rooms": ("Town Square", "Alley", "Cathedral Steps"),
        "light": (1.0, 0.72, 0.4)},
    7: {"chapter_name": "Eneomaos Machine Tower", "rooms": ("Gear Chamber", "Steam Room", "Clock Core"),
        "light": (0.8, 0.55, 0.3)},
    8: {"chapter_name": "Aiolon Ruins", "rooms": ("Ruin Entrance", "Sunken Courtyard", "Inner Vault"),
        "light": (0.75, 0.6, 0.9)},
    9: {"chapter_name": "Infinite Corridor", "rooms": ("Corridor Loop", "Mirror Chamber", "Endless Hall"),
        "light": (0.7, 0.4, 1.0)},
    10: {"chapter_name": "Dracula's Castle", "rooms": ("Grand Hall", "Chapel of Bones", "Throne Room"),
         "light": (1.0, 0.3, 0.3)},
}


def clear_blockout():
    for actor in EAS.get_all_level_actors():
        if (actor.actor_has_tag(BLOCKOUT_TAG)
                or actor.actor_has_tag("NA_ArtPass")
                or isinstance(actor, unreal.PlayerStart)):
            EAS.destroy_actor(actor)


def load_or_create_map():
    if not unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        error("Startup map missing: %s" % MAP_PATH)
        return False
    les = LES
    loaded = False
    try:
        loaded = les.load_level(MAP_PATH)
    except Exception as exc:
        warn("LevelEditorSubsystem.load_level failed: %r" % exc)
    if not loaded:
        try:
            loaded = unreal.EditorLoadingAndSavingUtils.load_map(MAP_PATH)
        except Exception as exc:
            error("Failed to load map: %r" % exc)
            return False
    return bool(loaded)


def spawn_box(label, center, size, cube, material):
    actor = EAS.spawn_actor_from_class(unreal.StaticMeshActor, center, unreal.Rotator(0, 0, 0))
    if not actor:
        error("Failed to spawn box %s" % label)
        return None
    actor.set_actor_label(label)
    actor.set_editor_property("tags", [BLOCKOUT_TAG])
    actor.set_actor_scale3d(unreal.Vector(size[0] / 100.0, size[1] / 100.0, size[2] / 100.0))
    comp = actor.get_component_by_class(unreal.StaticMeshComponent)
    if comp:
        comp.set_static_mesh(cube)
        if material:
            comp.set_material(0, material)
        comp.set_mobility(unreal.ComponentMobility.STATIC)
    return actor


def spawn_room(name, center, size, flags, enemy_classes, enemy_locations, bp_room, chapter=1):
    actor = EAS.spawn_actor_from_class(bp_room, center, unreal.Rotator(0, 0, 0))
    if not actor:
        error("Failed to spawn room %s" % name)
        return None
    actor.set_actor_label("Room_%s" % name.replace(" ", "_"))
    actor.set_editor_property("tags", [BLOCKOUT_TAG])
    set_prop(actor, "RoomName", name, required=True)
    set_prop(actor, "ChapterNumber", chapter)
    for key, value in flags.items():
        if key == "Exits":
            continue
        set_prop(actor, key, value)
    set_prop(actor, "ExitRoomNames", flags.get("Exits", []))
    if enemy_classes:
        set_prop(actor, "EnemyClassesToSpawn", enemy_classes)
    if enemy_locations:
        set_prop(actor, "EnemySpawnLocations", enemy_locations)
    box = get_prop(actor, "RoomTriggerBox")
    if box:
        box.set_box_extent(unreal.Vector(size[0] * 0.5, size[1] * 0.5, 300.0), True)
    return actor


def build_room_shell(name, center, size, height, cube, material, light_color=None,
                     light_intensity=6000.0):
    cx, cy = center.x, center.y
    sx, sy = size[0], size[1]
    gap = 360.0
    thickness = 30.0

    spawn_box("Floor_%s" % name, unreal.Vector(cx, cy, -thickness * 0.5),
              (sx, sy, thickness), cube, material)

    half_seg = (sx - gap) * 0.25
    for sign in (-1.0, 1.0):
        # North / south walls (run along X)
        for x_sign in (-1.0, 1.0):
            spawn_box("WallNS_%s" % name,
                      unreal.Vector(cx + x_sign * (sx + gap) * 0.25, cy + sign * sy * 0.5, height * 0.5),
                      (half_seg * 2.0, thickness, height), cube, material)
        # East / west walls (run along Y)
        for y_sign in (-1.0, 1.0):
            spawn_box("WallEW_%s" % name,
                      unreal.Vector(cx + sign * sx * 0.5, cy + y_sign * (sy + gap) * 0.25, height * 0.5),
                      (thickness, half_seg * 2.0, height), cube, material)

    light = EAS.spawn_actor_from_class(unreal.PointLight, unreal.Vector(cx, cy, height - 50.0),
                                       unreal.Rotator(0, 0, 0))
    if light:
        light.set_actor_label("Light_%s" % name.replace(" ", "_"))
        light.set_editor_property("tags", [BLOCKOUT_TAG])
        comp = light.get_component_by_class(unreal.PointLightComponent)
        if comp:
            set_prop(comp, "Intensity", light_intensity)
            set_prop(comp, "AttenuationRadius", max(sx, sy) * 1.1)
            if light_color:
                set_prop(comp, "LightColor", rgb_color(
                    int(light_color[0] * 255), int(light_color[1] * 255),
                    int(light_color[2] * 255)))


def build_corridor(name, center, size, cube, material):
    spawn_box("Corridor_%s" % name, unreal.Vector(center[0], center[1], -15.0),
              (size[0], size[1], 30.0), cube, material)
    # center is a plain tuple here, so indexing is intentional.


def dress_chapter_one(cube, material, rooms):
    """Give Chapter 1 its interior: ceilings, columns, an altar and a boss dais.

    The shells are floor-plus-walls only, so without this the chapter renders as
    empty boxes with light leaking out of the open tops.
    """
    if not cube:
        return

    for name, (center, size, height) in rooms.items():
        spawn_box("Ceiling_%s" % name,
                  unreal.Vector(center.x, center.y, height),
                  (size[0], size[1], 30.0), cube, material)

    # Entrance Hall: four columns framing the fight space.
    for sx in (-1, 1):
        for sy in (-1, 1):
            spawn_box("Column_Hall_%d_%d" % (sx, sy),
                      unreal.Vector(sx * 620, sy * 620, 210),
                      (160, 160, 420), cube, material)

    # Chapel: stepped altar at the far end.
    spawn_box("AltarStep_Chapel", unreal.Vector(0, 3400, 20),
              (1200, 500, 40), cube, material)
    spawn_box("Altar_Chapel", unreal.Vector(0, 3400, 60),
              (900, 300, 80), cube, material)

    # Boss arena dais and save-room shrine are built by the art pass
    # (Art_BossDais_* / Art_Save*, see Tools/ue5_art_pass.py) so they are not
    # duplicated here.


def build_chapter_one():
    if not load_or_create_map():
        return

    clear_blockout()

    cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    material = unreal.load_asset("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial")
    bp_room = bp_class("/Game/Blueprints/World", "BP_Room")
    bp_enemy = bp_class("/Game/Blueprints/Characters", "BP_EnemyBase")
    bp_skeleton = bp_class("/Game/Blueprints/Characters", "BP_Skeleton")
    bp_zombie = bp_class("/Game/Blueprints/Characters", "BP_Zombie")
    bp_ghoul = bp_class("/Game/Blueprints/Characters", "BP_Ghoul")
    bp_boss = bp_class("/Game/Blueprints/Characters", "BP_SentinelKnight")
    bp_portal = bp_class("/Game/Blueprints/World", "BP_ChapterPortal")

    if not (cube and bp_room and bp_enemy):
        error("Blockout prerequisites missing (cube=%r room=%r enemy=%r)" % (cube, bp_room, bp_enemy))
        return

    rooms = {
        "Entrance Hall": (unreal.Vector(0, 0, 0), (2200, 2200), 420),
        "Chapel": (unreal.Vector(0, 2800, 0), (1800, 1800), 520),
        "Save Room": (unreal.Vector(-2800, 0, 0), (900, 900), 320),
        "Boss Arena": (unreal.Vector(0, 5600, 0), (2800, 2800), 620),
    }

    # Lighting follows LevelDesignSpec_Extended.md: dim torches in the hall,
    # flickering candlelight in the chapel, a warm glow in the save room and a
    # dark boss arena lit by a single spotlight.
    lighting = {
        "Entrance Hall": ((1.0, 0.72, 0.42), 3200.0),   # torches, dim
        "Chapel": ((1.0, 0.62, 0.30), 2400.0),          # candles, warm
        "Save Room": ((1.0, 0.85, 0.62), 4200.0),       # warm glow
        "Boss Arena": ((0.28, 0.30, 0.40), 900.0),      # dark, cold
    }

    for name, (center, size, height) in rooms.items():
        color, intensity = lighting.get(name, (None, 6000.0))
        build_room_shell(name, center, size, height, cube, material, color, intensity)

    build_corridor("HallToChapel", (0, 1450), (620, 700), cube, material)
    build_corridor("HallToSave", (-1550, 0), (1700, 500), cube, material)
    build_corridor("ChapelToBoss", (0, 3750), (700, 500), cube, material)

    # Interior dressing: ceilings, columns, altar, dais, pedestal.
    dress_chapter_one(cube, material, rooms)

    # Player start in the south of the Entrance Hall.
    start = EAS.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(0, -700, 120), unreal.Rotator(roll=0.0, pitch=0.0, yaw=90.0))
    if start:
        start.set_actor_label("PlayerStart_Chap01")
        start.set_editor_property("tags", [BLOCKOUT_TAG])

    # Four Chapter 1 rooms with their enemy populations.
    spawn_room("Entrance Hall", rooms["Entrance Hall"][0], rooms["Entrance Hall"][1],
               {"bIsLocked": True, "bIsSaveRoom": False, "bIsBossArena": False,
                "Exits": ["Chapel", "Save Room"]},
               [bp_skeleton, bp_skeleton, bp_skeleton, bp_zombie, bp_zombie],
               [unreal.Vector(-600, 300, 100), unreal.Vector(-200, 500, 100),
                unreal.Vector(200, 500, 100), unreal.Vector(600, 300, 100),
                unreal.Vector(0, 700, 100)],
               bp_room)

    spawn_room("Chapel", rooms["Chapel"][0], rooms["Chapel"][1],
               {"bIsLocked": True, "bIsSaveRoom": False, "bIsBossArena": False,
                "Exits": ["Entrance Hall", "Boss Arena"]},
               [bp_ghoul, bp_ghoul],
               [unreal.Vector(-500, 2800, 100), unreal.Vector(500, 2800, 100)],
               bp_room)

    spawn_room("Save Room", rooms["Save Room"][0], rooms["Save Room"][1],
               {"bIsLocked": False, "bIsSaveRoom": True, "bIsBossArena": False,
                "Exits": ["Entrance Hall"]},
               [], [], bp_room)

    spawn_room("Boss Arena", rooms["Boss Arena"][0], rooms["Boss Arena"][1],
               {"bIsLocked": True, "bIsSaveRoom": False, "bIsBossArena": True,
                "Exits": ["Chapel"]},
               [bp_boss] if bp_boss else [bp_enemy],
               [unreal.Vector(0, 5900, 100)],
               bp_room)

    # Save room flame and a few pickups.
    bp_save = bp_class("/Game/Blueprints/World", "BP_SaveRoom")
    if bp_save:
        save_actor = EAS.spawn_actor_from_class(bp_save, unreal.Vector(-2800, 0, 60), unreal.Rotator(0, 0, 0))
        if save_actor:
            save_actor.set_actor_label("SaveRoom_Chap01")
            save_actor.set_editor_property("tags", [BLOCKOUT_TAG])
            set_prop(save_actor, "RoomName", "Save Room")
            set_prop(save_actor, "bIsSaveRoom", True)
            set_prop(save_actor, "bIsLocked", False)

    # Loot per LevelDesignSpec_Extended.md chapter 1:
    #   Entrance Hall -> Short Sword recipe + hidden alcove of Iron Shards
    #   Chapel        -> Potion x2, with breakable candles that also drop
    bp_item = bp_class("/Game/Blueprints/World", "BP_ItemDrop")
    if bp_item:
        hall_loot = (("Short Sword", 0, -900),      # recipe reward
                     ("Iron Shard", -900, -900), ("Iron Shard", -780, -900),
                     ("Iron Shard", -660, -900))    # hidden alcove, west corner
        for index, (item, x, y) in enumerate(hall_loot):
            drop = EAS.spawn_actor_from_class(bp_item, unreal.Vector(x, y, 80),
                                              unreal.Rotator(0, 0, 0))
            if drop:
                drop.set_actor_label("Item_Chap01_%s_%d" % (item.replace(" ", ""), index))
                drop.set_editor_property("tags", [BLOCKOUT_TAG])
                set_prop(drop, "ItemName", item)

        # Two potions in the chapel, as the spec's item list calls for.
        for index, x in enumerate((-450, 450)):
            drop = EAS.spawn_actor_from_class(bp_item, unreal.Vector(x, 2800, 80),
                                              unreal.Rotator(0, 0, 0))
            if drop:
                drop.set_actor_label("Item_Chap01_Potion_%d" % index)
                drop.set_editor_property("tags", [BLOCKOUT_TAG])
                set_prop(drop, "ItemName", "Potion")

    # Breakable candles: the spec puts them in the Chapel; two more light the hall.
    bp_candle = bp_class("/Game/Blueprints/World", "BP_CandleBreakable")
    if bp_candle:
        candles = [(-1400, 2200, "Chapel"), (-600, 2400, "Chapel"),
                   (600, 2400, "Chapel"), (1400, 2200, "Chapel"),
                   (-900, 900, "Hall"), (900, 900, "Hall")]
        for index, (x, y, where) in enumerate(candles):
            candle = EAS.spawn_actor_from_class(bp_candle, unreal.Vector(x, y, 50),
                                                unreal.Rotator(0, 0, 0))
            if candle:
                candle.set_actor_label("Candle_%s_%d" % (where, index))
                candle.set_editor_property("tags", [BLOCKOUT_TAG])
                if where == "Chapel":
                    # Chapel candles drop potions per the secrets list.
                    set_prop(candle, "PossibleDrops", ["Potion", "Potion"])
                else:
                    set_prop(candle, "PossibleDrops", ["Iron Shard", "Potion", "Silver Ingot"])
                set_prop(candle, "DropChance", 1.0)
                if bp_item:
                    set_prop(candle, "ItemDropClass", bp_item)

    # Directional light for global readability.
    sun = EAS.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 1500),
                                     unreal.Rotator(roll=0.0, pitch=-50.0, yaw=-35.0))
    if sun:
        sun.set_actor_label("Sun_Chap01")
        sun.set_editor_property("tags", [BLOCKOUT_TAG])
        comp = sun.get_component_by_class(unreal.DirectionalLightComponent)
        if comp:
            set_prop(comp, "Intensity", 4.0)

    # Boss Arena: dark room with a single spotlight on the Sentinel Knight.
    spot = EAS.spawn_actor_from_class(unreal.SpotLight, unreal.Vector(0, 5900, 560),
                                      unreal.Rotator(roll=0.0, pitch=-90.0, yaw=0.0))
    if spot:
        spot.set_actor_label("Spot_BossArena")
        spot.set_editor_property("tags", [BLOCKOUT_TAG])
        comp = spot.get_component_by_class(unreal.SpotLightComponent)
        if comp:
            set_prop(comp, "Intensity", 26000.0)
            set_prop(comp, "AttenuationRadius", 1800.0)
            set_prop(comp, "InnerConeAngle", 16.0)
            set_prop(comp, "OuterConeAngle", 30.0)

    # Navigation bounds so enemy AI can path through the chapter. Without this
    # the enemies spawn but never move, which makes the chapter untestable.
    nav = EAS.spawn_actor_from_class(unreal.NavMeshBoundsVolume,
                                     unreal.Vector(0, 2900, 300),
                                     unreal.Rotator(0, 0, 0))
    if nav:
        nav.set_actor_label("NavBounds_Chap01")
        nav.set_editor_property("tags", [BLOCKOUT_TAG])
        nav.set_actor_scale3d(unreal.Vector(30.0, 42.0, 6.0))
    else:
        warn("Could not spawn NavMeshBoundsVolume; enemy AI will not path")

    # Exit to Chapter 2. The portal unlocks once the Sentinel Knight dies.
    spawn_chapter_portal(1, unreal.Vector(0, 6650, 120), bp_portal)

    try:
        if not LES.save_current_level():
            warn("save_current_level returned false")
    except Exception as exc:
        warn("save_current_level failed: %r" % exc)
        try:
            unreal.EditorLoadingAndSavingUtils.save_current_map()
        except Exception as exc2:
            error("Failed to save map: %r / %r" % (exc, exc2))

    log("Chapter 1 blockout rebuilt")


def prepare_chapter_map(map_path):
    if unreal.EditorAssetLibrary.does_asset_exist(map_path):
        try:
            if LES.load_level(map_path):
                return True
        except Exception as exc:
            warn("load_level(%s) failed: %r" % (map_path, exc))
        try:
            return bool(unreal.EditorLoadingAndSavingUtils.load_map(map_path))
        except Exception as exc:
            error("Failed to load %s: %r" % (map_path, exc))
            return False

    try:
        return bool(LES.new_level(map_path))
    except Exception as exc:
        error("Failed to create %s: %r" % (map_path, exc))
        return False


def enemy_spawn_locations(center, count, radius=520.0):
    if count <= 0:
        return []
    if count == 1:
        return [center + unreal.Vector(0, 0, 100)]
    return [
        center + unreal.Vector(
            math.cos((2.0 * math.pi * index) / count) * radius,
            math.sin((2.0 * math.pi * index) / count) * radius,
            100)
        for index in range(count)
    ]


def spawn_chapter_loot(chapter, entry_center, bp_item, bp_candle):
    if bp_item:
        items = ["Potion", "Potion", "Potion", "Iron Shard", "Iron Shard", "Silver Ingot"]
        if chapter >= 3:
            items.append("High Potion")
        if chapter >= 7:
            items.extend(["Iron Shard", "Silver Ingot"])
        for index, item in enumerate(items):
            drop = EAS.spawn_actor_from_class(
                bp_item,
                entry_center + unreal.Vector(-300 + index * 150, -500, 80),
                unreal.Rotator(0, 0, 0))
            if drop:
                drop.set_actor_label("Item_%s_%d" % (item.replace(" ", ""), index))
                drop.set_editor_property("tags", [BLOCKOUT_TAG])
                set_prop(drop, "ItemName", item)

    if bp_candle:
        for index, offset in enumerate(((-900, 900), (900, 900), (-900, -900), (900, -900))):
            candle = EAS.spawn_actor_from_class(
                bp_candle, entry_center + unreal.Vector(offset[0], offset[1], 50),
                unreal.Rotator(0, 0, 0))
            if candle:
                candle.set_actor_label("Candle_%d" % index)
                candle.set_editor_property("tags", [BLOCKOUT_TAG])
                set_prop(candle, "PossibleDrops", ["Iron Shard", "Potion", "Silver Ingot"])
                set_prop(candle, "DropChance", 1.0)
                if bp_item:
                    set_prop(candle, "ItemDropClass", bp_item)


def spawn_chapter_portal(chapter, location, bp_portal):
    if not bp_portal or chapter >= 10:
        return
    portal = EAS.spawn_actor_from_class(bp_portal, location, unreal.Rotator(0, 0, 0))
    if not portal:
        error("Failed to spawn chapter %d portal" % chapter)
        return
    portal.set_actor_label("Portal_To_Chapter_%d" % (chapter + 1))
    portal.set_editor_property("tags", [BLOCKOUT_TAG])
    set_prop(portal, "TargetChapter", chapter + 1)
    set_prop(portal, "TargetLevelName", CHAPTER_MAP_NAMES[chapter + 1])
    set_prop(portal, "bRequireBossDefeated", True)
    set_prop(portal, "bCompleteCurrentChapter", True)


def build_generic_chapter(chapter):
    spec = CHAPTER_SPECS[chapter]
    map_name = CHAPTER_MAP_NAMES[chapter]
    map_path = "/Game/Maps/%s" % map_name
    if not prepare_chapter_map(map_path):
        return

    clear_blockout()

    cube = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    material = unreal.load_asset("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial")
    bp_room = bp_class("/Game/Blueprints/World", "BP_Room")
    bp_enemy = bp_class("/Game/Blueprints/Characters", "BP_EnemyBase")
    bp_save = bp_class("/Game/Blueprints/World", "BP_SaveRoom")
    bp_item = bp_class("/Game/Blueprints/World", "BP_ItemDrop")
    bp_candle = bp_class("/Game/Blueprints/World", "BP_CandleBreakable")
    bp_portal = bp_class("/Game/Blueprints/World", "BP_ChapterPortal")

    if not (cube and bp_room and bp_enemy):
        error("Chapter %d prerequisites missing (cube=%r room=%r enemy=%r)" %
              (chapter, cube, bp_room, bp_enemy))
        return

    room_names = spec["rooms"]
    light_color = spec.get("light")
    rooms = {
        room_names[0]: (unreal.Vector(0, 0, 0), (2200, 2200), 420),
        room_names[1]: (unreal.Vector(0, 2800, 0), (1800, 1800), 520),
        "Save Room": (unreal.Vector(-2800, 0, 0), (900, 900), 320),
        room_names[2]: (unreal.Vector(0, 5600, 0), (2800, 2800), 620),
    }

    for name, (center, size, height) in rooms.items():
        build_room_shell(name, center, size, height, cube, material, light_color)

    build_corridor("EntryToMid_%d" % chapter, (0, 1450), (620, 700), cube, material)
    build_corridor("EntryToSave_%d" % chapter, (-1550, 0), (1700, 500), cube, material)
    build_corridor("MidToBoss_%d" % chapter, (0, 3750), (700, 500), cube, material)

    start = EAS.spawn_actor_from_class(
        unreal.PlayerStart, unreal.Vector(0, -700, 120),
        unreal.Rotator(roll=0.0, pitch=0.0, yaw=90.0))
    if start:
        start.set_actor_label("PlayerStart_Chap%02d" % chapter)
        start.set_editor_property("tags", [BLOCKOUT_TAG])

    # Split the chapter's encounters between the entry and mid rooms. Bosses
    # are placed in the third room so the portal stays locked until they die.
    encounter_path = os.path.join(DATA_TABLE_DIR, "EnemyEncounterTable.csv")
    encounters = []
    if os.path.exists(encounter_path):
        encounters = [row for row in read_csv(encounter_path)
                      if int(float(row.get("Chapter", 0))) == chapter]
    non_boss = [row for row in encounters
                if str(row.get("IsBoss", "false")).lower() != "true"]
    boss_rows = [row for row in encounters
                 if str(row.get("IsBoss", "false")).lower() == "true"]

    entry_classes, entry_locations = [], []
    mid_classes, mid_locations = [], []
    for index, row in enumerate(non_boss):
        enemy_name = row.get("EnemyName", "")
        cls = bp_class("/Game/Blueprints/Characters", enemy_bp_name(enemy_name)) or bp_enemy
        count = max(1, int(float(row.get("Count", 1))))
        center = rooms[room_names[0]][0] if index % 2 == 0 else rooms[room_names[1]][0]
        locations = enemy_spawn_locations(center, count)
        if index % 2 == 0:
            entry_classes.extend([cls] * len(locations))
            entry_locations.extend(locations)
        else:
            mid_classes.extend([cls] * len(locations))
            mid_locations.extend(locations)

    boss_classes, boss_locations = [], []
    if boss_rows:
        boss_name = boss_rows[0].get("EnemyName", "")
        boss_cls = bp_class("/Game/Blueprints/Characters", enemy_bp_name(boss_name)) or bp_enemy
        boss_classes = [boss_cls]
        boss_locations = [rooms[room_names[2]][0] + unreal.Vector(0, 300, 100)]

    spawn_room(room_names[0], rooms[room_names[0]][0], rooms[room_names[0]][1],
               {"bIsLocked": True, "bIsSaveRoom": False, "bIsBossArena": False,
                "Exits": [room_names[1], "Save Room"]},
               entry_classes, entry_locations, bp_room, chapter)

    spawn_room(room_names[1], rooms[room_names[1]][0], rooms[room_names[1]][1],
               {"bIsLocked": True, "bIsSaveRoom": False, "bIsBossArena": False,
                "Exits": [room_names[0], room_names[2]]},
               mid_classes, mid_locations, bp_room, chapter)

    spawn_room("Save Room", rooms["Save Room"][0], rooms["Save Room"][1],
               {"bIsLocked": False, "bIsSaveRoom": True, "bIsBossArena": False,
                "Exits": [room_names[0]]},
               [], [], bp_room, chapter)

    spawn_room(room_names[2], rooms[room_names[2]][0], rooms[room_names[2]][1],
               {"bIsLocked": True, "bIsSaveRoom": False, "bIsBossArena": True,
                "Exits": [room_names[1]]},
               boss_classes, boss_locations, bp_room, chapter)

    if bp_save:
        save_actor = EAS.spawn_actor_from_class(
            bp_save, rooms["Save Room"][0] + unreal.Vector(0, 0, 60), unreal.Rotator(0, 0, 0))
        if save_actor:
            save_actor.set_actor_label("SaveRoom_Chap%02d" % chapter)
            save_actor.set_editor_property("tags", [BLOCKOUT_TAG])
            set_prop(save_actor, "RoomName", "Save Room")
            set_prop(save_actor, "bIsSaveRoom", True)
            set_prop(save_actor, "bIsLocked", False)

    spawn_chapter_loot(chapter, rooms[room_names[0]][0], bp_item, bp_candle)
    spawn_chapter_portal(chapter, rooms[room_names[2]][0] + unreal.Vector(0, 1050, 120),
                         bp_portal)

    sun = EAS.spawn_actor_from_class(unreal.DirectionalLight, unreal.Vector(0, 0, 1500),
                                     unreal.Rotator(roll=0.0, pitch=-50.0, yaw=-35.0))
    if sun:
        sun.set_actor_label("Sun_Chap%02d" % chapter)
        sun.set_editor_property("tags", [BLOCKOUT_TAG])
        comp = sun.get_component_by_class(unreal.DirectionalLightComponent)
        if comp:
            set_prop(comp, "Intensity", 4.0)
            if light_color:
                set_prop(comp, "LightColor", rgb_color(
                    int(light_color[0] * 255), int(light_color[1] * 255),
                    int(light_color[2] * 255)))

    try:
        if not LES.save_current_level():
            warn("save_current_level returned false for chapter %d" % chapter)
    except Exception as exc:
        error("Failed to save chapter %d: %r" % (chapter, exc))

    log("Chapter %d blockout rebuilt (%s)" % (chapter, map_name))


def build_all_chapters():
    build_chapter_one()
    for chapter in range(2, 11):
        build_generic_chapter(chapter)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    log("Starting content build. Content dir: %s" % CONTENT_DIR)
    if not EAS or not LES:
        error("Editor subsystems unavailable; run this as a PythonScript commandlet with the editor modules loaded.")
        return

    # Animations must exist before the weapon table so its rows can reference
    # the generated montages.
    build_hector_animation()

    import_all_data_tables()

    create_all_blueprints()

    actions, imc = create_input_assets()
    if imc:
        configure_character_blueprint(actions, imc)

    configure_game_mode_blueprint()
    build_all_chapters()

    unreal.EditorAssetLibrary.save_directory("/Game", only_if_is_dirty=False, recursive=True)

    log("SUMMARY created=%d updated=%d skipped=%d errors=%d" %
        (STATS["created"], STATS["updated"], STATS["skipped"], STATS["errors"]))
    for message in ERRORS:
        log("ERROR: " + message)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        error("Unhandled exception:\n" + traceback.format_exc())
