"""
F2 - mechanical / timing fidelity gate.

Compares what the game actually ships against the design documents:

  AnimationFrameData.md   combo windows 0.35 / 0.45 / 0.60
  AnimationBlueprintSpec  perfect guard 0.1s, quick step 0.3s, double step 0.5s
  AnimationFrameData.md   attack startup/active/recovery at 60 fps

Runtime values are read from the combat component defaults so the test cannot
drift from the code. Clip timings are measured from the imported sequences.

Tolerance policy:
  * timings  -> hard failure beyond 1 ms (these are gameplay rules)
  * clip len -> reported as DEVIATION beyond 60 ms (art timing drift)

Run as a PythonScript commandlet.
"""
import unreal

LOG = "[NA-FID2] "
ERRORS = []
DEVIATIONS = []

SPEC_COMBO = {1: 0.35, 2: 0.45, 3: 0.60}
SPEC_PERFECT_GUARD = 0.1
SPEC_QUICKSTEP_IFRAMES = 0.3
SPEC_DOUBLE_STEP = 0.5
TIME_TOL = 0.001

# (startup, active, recovery) frames at 60 fps, from AnimationFrameData.md.
SPEC_FRAME_DATA = {
    "Light1": (6, 4, 8),
    "Light2": (5, 4, 7),
    "Light3": (6, 5, 9),
    "Heavy": (8, 6, 10),
}
SPEC_FPS = 60.0
CLIP_TOL = 0.060

ANIM_DIR = "/Game/Characters/Hector/Animations"


def log(msg):
    unreal.log_warning(LOG + str(msg))


def err(msg):
    ERRORS.append(str(msg))
    unreal.log_error(LOG + "ERROR: " + str(msg))


def deviation(msg):
    DEVIATIONS.append(str(msg))
    unreal.log_warning(LOG + "DEVIATION: " + str(msg))


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


def check_timing(label, actual, expected):
    if actual is None:
        err("%s could not be read" % label)
        return
    ok = abs(actual - expected) <= TIME_TOL
    log("%-22s actual=%.3f expected=%.3f %s"
        % (label, actual, expected, "OK" if ok else "MISMATCH"))
    if not ok:
        err("%s is %.3fs but the spec says %.3fs" % (label, actual, expected))

log("=== RUNTIME TIMINGS (combat component defaults) ===")
bp_class = unreal.load_class(
    None, "/Game/Blueprints/Characters/BP_HectorCharacter.BP_HectorCharacter_C")
if not bp_class:
    err("BP_HectorCharacter class not found")
else:
    cdo = unreal.get_default_object(bp_class)
    combat = get_prop(cdo, "CombatComponent")
    if not combat:
        err("BP_HectorCharacter has no CombatComponent")
    else:
        for stage, expected in SPEC_COMBO.items():
            try:
                actual = combat.get_combo_window_seconds(stage)
            except Exception as exc:
                err("GetComboWindowSeconds(%d) failed: %s" % (stage, exc))
                continue
            check_timing("combo window stage %d" % stage, actual, expected)

        check_timing("perfect guard window",
                     get_prop(combat, "PerfectGuardWindow"), SPEC_PERFECT_GUARD)
        check_timing("quick step i-frames",
                     get_prop(combat, "QuickStepIframes"), SPEC_QUICKSTEP_IFRAMES)
        check_timing("double step window",
                     get_prop(combat, "DoubleStepWindow"), SPEC_DOUBLE_STEP)

        hit_delay = get_prop(combat, "AttackHitDelay")
        max_health = get_prop(combat, "MaxHealth")
        log("attack hit delay=%.3fs max health=%.0f" % (hit_delay or 0.0, max_health or 0.0))

log("=== CLIP TIMINGS vs 60 fps frame data ===")
for label, frames in SPEC_FRAME_DATA.items():
    expected = sum(frames) / SPEC_FPS
    seq = unreal.load_asset("%s/AN_Hector_%s" % (ANIM_DIR, label))
    if not seq:
        err("AN_Hector_%s missing" % label)
        continue

    actual = get_prop(seq, "sequence_length") or 0.0
    good = abs(actual - expected) <= CLIP_TOL
    log("%-8s clip=%.2fs spec=%.2fs (%d frames @60) %s"
        % (label, actual, expected, sum(frames), "OK" if good else "DRIFT"))
    if not good:
        deviation("AN_Hector_%s is %.2fs but the frame data implies %.2fs"
                  % (label, actual, expected))

log("=== RESULT ===")
log("RESULT=%s errors=%d deviations=%d"
    % ("FAIL" if ERRORS else "PASS", len(ERRORS), len(DEVIATIONS)))
for message in ERRORS:
    log("FAILED: " + message)
for message in DEVIATIONS:
    log("DRIFT: " + message)
