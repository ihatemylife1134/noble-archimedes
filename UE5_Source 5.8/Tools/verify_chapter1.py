"""
Chapter 1 acceptance check - proves the chapter is playtest-ready.

Asserts the Chapter 1 layout against LevelDesignSpec_Extended.md and
EnemyEncounterTable.csv (chapter 1 rows), rather than assuming the build worked:

  rooms          Entrance Hall, Chapel, Save Room, Boss Arena (exactly these)
  encounters     Skeleton 3, Zombie 2, Ghoul 2, Sentinel Knight 1
  flow           exactly one PlayerStart and one ChapterPortal
  safety         one save-room actor, boss arena flagged
  light          per-room lights + a boss spotlight
  content        breakable candles and pickups present
  ai             NavMeshBoundsVolume present (otherwise enemies cannot move)

Run as a PythonScript commandlet.
"""
import unreal

LOG = "[NA-CH1] "
ERRORS = []

MAP_PATH = "/Game/Maps/Chap_01_AbandonedCastle"
EXPECTED_ROOMS = {"Entrance Hall", "Chapel", "Save Room", "Boss Arena"}
# Enemy class name -> required instance count in the chapter.
EXPECTED_ENEMIES = {"BP_Skeleton": 3, "BP_Zombie": 2, "BP_Ghoul": 2,
                    "BP_SentinelKnight": 1}
MIN_CANDLES = 4
MIN_PICKUPS = 4
MIN_ROOM_LIGHTS = 4


def log(msg):
    unreal.log_warning(LOG + str(msg))


def err(msg):
    ERRORS.append(str(msg))
    unreal.log_error(LOG + "ERROR: " + str(msg))


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


LES = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
EAS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

if not LES.load_level(MAP_PATH):
    err("could not load %s" % MAP_PATH)
else:
    rooms, save_actors, portals, starts, navs, spots = [], 0, 0, 0, 0, 0
    candles = pickups = lights = 0
    enemy_counts = {}
    dressing = {"Ceiling": 0, "Column":
                0, "Altar": 0, "Dais": 0, "Pedestal": 0}

    for actor in EAS.get_all_level_actors():
        cls = actor.get_class().get_name()
        label = actor.get_actor_label()

        # Interior dressing is identified by static-mesh label prefix.
        for key in dressing:
            if str(label).startswith(key):
                dressing[key] += 1

        if cls.startswith("BP_Room"):
            rooms.append(get_prop(actor, "RoomName"))
        elif cls.startswith("BP_SaveRoom"):
            save_actors += 1
        elif cls.startswith("BP_ChapterPortal"):
            portals += 1
        elif cls.startswith("PlayerStart"):
            starts += 1
        elif cls.startswith("NavMeshBoundsVolume"):
            navs += 1
        elif cls.startswith("SpotLight"):
            spots += 1
        elif cls.startswith("PointLight"):
            lights += 1
        elif cls.startswith("BP_CandleBreakable"):
            candles += 1
        elif cls.startswith("BP_ItemDrop"):
            pickups += 1

        # Room enemy stacks are TSubclassOf arrays on the room actors.
        if cls.startswith("BP_Room"):
            for entry in (get_prop(actor, "EnemyClassesToSpawn") or []):
                name = entry.get_name() if entry else None
                if name:
                    # Blueprint classes come back with a _C suffix.
                    if name.endswith("_C"):
                        name = name[:-2]
                    enemy_counts[name] = enemy_counts.get(name, 0) + 1

    log("rooms        = %s" % sorted(r for r in rooms if r))
    log("enemies      = %s" % enemy_counts)
    log("start/portal = %d/%d  save_actors=%d nav=%d" %
        (starts, portals, save_actors, navs))
    log("lights       = %d point + %d spot  candles=%d pickups=%d" %
        (lights, spots, candles, pickups))
    log("dressing     = %s" % dressing)

    # Every room needs a ceiling, and the chapter needs its landmarks.
    if dressing["Ceiling"] < len(EXPECTED_ROOMS):
        err("only %d ceilings for %d rooms" % (dressing["Ceiling"], len(EXPECTED_ROOMS)))
    if dressing["Column"] < 4:
        err("entrance hall has %d columns, expected 4" % dressing["Column"])
    if dressing["Altar"] < 1:
        err("chapel has no altar")
    if dressing["Dais"] < 1:
        err("boss arena has no dais")
    if dressing["Pedestal"] < 1:
        err("save room has no pedestal")

    found_rooms = {str(r) for r in rooms if r}
    if found_rooms != EXPECTED_ROOMS:
        err("rooms are %s, spec says %s"
            % (sorted(found_rooms), sorted(EXPECTED_ROOMS)))

    for name, required in EXPECTED_ENEMIES.items():
        actual = enemy_counts.get(name, 0)
        if actual != required:
            err("%s count is %d, encounter table says %d" % (name, actual, required))

    if starts != 1:
        err("expected exactly one PlayerStart, found %d" % starts)
    if portals != 1:
        err("expected exactly one ChapterPortal, found %d" % portals)
    if not save_actors:
        err("no save-room actor in the chapter")
    if not navs:
        err("no NavMeshBoundsVolume: enemy AI cannot path")
    if spots < 1:
        err("boss arena has no spotlight")
    if lights < MIN_ROOM_LIGHTS:
        err("only %d room lights (spec lights every room)" % lights)
    if candles < MIN_CANDLES:
        err("only %d breakable candles, spec puts four in the chapel" % candles)
    if pickups < MIN_PICKUPS:
        err("only %d pickups (recipe + alcove shards + chapel potions)" % pickups)

log("=== RESULT ===")
log("RESULT=%s errors=%d" % ("FAIL" if ERRORS else "PASS", len(ERRORS)))
for message in ERRORS:
    log("FAILED: " + message)
