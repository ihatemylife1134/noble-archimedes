"""
F4 - presentational asset completeness matrix.

Reports, per asset category, how many of the assets named by the design docs
actually exist. This is the honest "how finished does it look" number: it turns
the checklists into a pass/fail count instead of a feeling.

Categories are validated (missing assets fail the gate) only where the category
is expected to be complete. Presentational categories that are still being
authored are reported as gaps so progress is measurable without blocking the
system gates.
"""
import unreal

LOG = "[NA-FID4] "
ERRORS = []
GAPS = []

# Categories that must be complete for the game to be considered built.
REQUIRED = {
    "Sequences": ["AN_Hector_%s" % a for a in (
        "Idle", "Walk", "Run", "Jump", "Light1", "Light2", "Light3", "Heavy",
        "Guard", "QuickStep", "HitReaction", "Death")],
    "Montages": ["AM_Hector_%s" % a for a in (
        "Idle", "Walk", "Run", "Jump", "Light1", "Light2", "Light3", "Heavy",
        "Guard", "QuickStep", "HitReaction", "Death")],
    "Character": ["SK_Hector", "AB_Hector"],
}

# Presentational categories tracked as gaps until the art pass completes.
TRACKED = {
    "WeaponBlueprints": ["WP_%s" % n for n in (
        "Sword_Short", "Sword_Iron", "Sword_Broad", "Sword_Long", "Sword_Great",
        "Sword_Executioner", "Axe_Battle", "Axe_Great", "Axe_Executioner",
        "Spear_Long", "Spear_Halberd", "Spear_Pike", "Knuckles_PunchRings",
        "Knuckles_Claws", "Knuckles_Brass", "Knuckles_Katar",
        "Special_Shuriken", "Special_Bomb", "Special_Gatling")],
    "Niagara": ["NS_%s" % n for n in (
        "WeaponTrail_Sword", "WeaponTrail_Axe", "WeaponTrail_Spear",
        "WeaponTrail_Knuckles", "WeaponTrail_Special", "HitSpark_Fire",
        "HitSpark_Ice", "HitSpark_Light", "HitSpark_Dark", "HitBlood",
        "QuickStepTrail", "PerfectGuardFlash", "GuardBlockFlash",
        "InnocentDevilSummon", "InnocentDevilEvolve", "InnocentDevilAttack",
        "ItemPickup", "CandleBreak", "SaveRoomHeal")],
    "SoundCues": ["SC_Combat_Swing_Sword", "SC_Combat_WeaponHit",
                  "SC_Combat_PlayerHit", "SC_Combat_QuickStep",
                  "SC_Combat_GuardBlock", "SC_Combat_PerfectGuard",
                  "SC_Combat_Death", "SC_Combat_BossTheme",
                  "SC_InnocentDevilSummon", "SC_Item_Pickup", "S_UI_Click"],
}


def log(msg):
    unreal.log_warning(LOG + str(msg))


def err(msg):
    ERRORS.append(str(msg))
    unreal.log_error(LOG + "ERROR: " + str(msg))


def gap(msg):
    GAPS.append(str(msg))
    unreal.log_warning(LOG + "GAP: " + str(msg))


def asset_index():
    """Map of asset-name -> path for everything under /Game."""
    index = {}
    for path in unreal.EditorAssetLibrary.list_assets("/Game", recursive=True,
                                                      include_folder=False):
        name = path.split("/")[-1].split(".")[0]
        index[name] = path
    return index


def check_category(category, names, index, required):
    present = [n for n in names if n in index]
    missing = [n for n in names if n not in index]
    log("%-18s %d/%d" % (category, len(present), len(names)))
    if missing:
        sample = ", ".join(missing[:5])
        more = "" if len(missing) <= 5 else " (+%d more)" % (len(missing) - 5)
        if required:
            err("%s missing %d: %s%s" % (category, len(missing), sample, more))
        else:
            gap("%s missing %d: %s%s" % (category, len(missing), sample, more))
    return len(present), len(names)

log("=== ASSET INDEX ===")
index = asset_index()
log("assets under /Game = %d" % len(index))

log("=== REQUIRED (blocking) ===")
required_total = required_present = 0
for category, names in REQUIRED.items():
    present, total = check_category(category, names, index, True)
    required_present += present
    required_total += total

log("=== TRACKED (reported gaps) ===")
tracked_total = tracked_present = 0
for category, names in TRACKED.items():
    present, total = check_category(category, names, index, False)
    tracked_present += present
    tracked_total += total

log("=== COVERAGE ===")
required_pct = 100.0 * required_present / required_total if required_total else 0.0
tracked_pct = 100.0 * tracked_present / tracked_total if tracked_total else 0.0
log("required   %d/%d (%.1f%%)" % (required_present, required_total, required_pct))
log("presentation %d/%d (%.1f%%)" % (tracked_present, tracked_total, tracked_pct))
log("overall    %d/%d (%.1f%%)"
    % (required_present + tracked_present, required_total + tracked_total,
       100.0 * (required_present + tracked_present) / max(1, required_total + tracked_total)))

log("=== RESULT ===")
log("RESULT=%s errors=%d gaps=%d" % ("FAIL" if ERRORS else "PASS", len(ERRORS), len(GAPS)))
for message in ERRORS:
    log("FAILED: " + message)
