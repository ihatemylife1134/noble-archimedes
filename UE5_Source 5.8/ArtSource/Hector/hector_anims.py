"""Hector keyframed animations (30 fps). Rotations are bone-local XYZ degrees.
Root motion is authored on the 'root' bone ('root_loc', cm).
Arms rest along +/-X in bind pose, so idle drops them with Y, not Z: with the bone
running along its own X, a Z rotation sweeps the arm horizontally forward, which
is why the shipped clips held both arms out in front of the chest. Y pitches the
arm down to the side."""

ARMS = dict(upperarm_l=(0, -80, 0), upperarm_r=(0, 80, 0), lowerarm_l=(0, -12, 0), lowerarm_r=(0, 18, 0))


def P(base=None, **kw):
    d = dict(base or {})
    d.update(kw)
    return d


IDLE0 = P(ARMS, spine_02=(2, 0, 0))
IDLE = [(0, IDLE0),
        (30, P(ARMS, spine_02=(4, 0, 0), spine_03=(2, 0, 0), upperarm_l=(0, 0, -60), upperarm_r=(0, 0, 60), root_loc=(0, 0, -0.8))),
        (60, IDLE0)]


def _cycle(stride, lift, arm, lean, n, bob):
    h, q = n // 2, n // 4
    base = P(ARMS, spine_01=(lean, 0, 0))
    a = P(base, thigh_l=(-stride, 0, 0), calf_l=(8, 0, 0), thigh_r=(stride, 0, 0), calf_r=(10, 0, 0),
          upperarm_l=(0, -80, arm), upperarm_r=(0, 80, -arm), spine_03=(0, 0, 4))
    b = P(base, calf_l=(lift, 0, 0), calf_r=(6, 0, 0), root_loc=(0, 0, bob))
    c = P(base, thigh_l=(stride, 0, 0), calf_l=(10, 0, 0), thigh_r=(-stride, 0, 0), calf_r=(8, 0, 0),
          upperarm_l=(0, -80, -arm), upperarm_r=(0, 80, arm), spine_03=(0, 0, -4))
    d = P(base, calf_l=(6, 0, 0), calf_r=(lift, 0, 0), root_loc=(0, 0, bob))
    return [(0, a), (q, b), (h, c), (h + q, d), (n, a)]


WALK = _cycle(22, 30, 14, 3, 32, 2.0)
RUN = _cycle(38, 70, 32, 10, 20, 3.5)


def _strike(wind, hit, rec, spine_w, spine_s, arm_up, swing):
    w = P(spine_02=(0, 0, spine_w), spine_03=(0, 0, spine_w), clavicle_r=(0, 0, 8),
          upperarm_r=(0, -arm_up, 30), lowerarm_r=(0, 0, 50), upperarm_l=(0, 0, -50),
          thigh_l=(-14, 0, 0), thigh_r=(10, 0, 0), calf_r=(12, 0, 0))
    s = P(spine_02=(6, 0, spine_s), spine_03=(4, 0, spine_s), clavicle_r=(0, 0, -6),
          upperarm_r=(0, arm_up * 0.6, 95 + swing), lowerarm_r=(0, 0, 8), upperarm_l=(0, 0, -70),
          thigh_l=(-24, 0, 0), calf_l=(14, 0, 0), thigh_r=(16, 0, 0), calf_r=(6, 0, 0), root_loc=(0, -14, -3))
    return [(0, IDLE0), (wind, w), (wind + hit, s), (wind + hit + rec, IDLE0)]


# Combo windows 0.35 / 0.45 / 0.60 s -> each strike resolves inside its window.
LIGHT1 = _strike(4, 3, 8, 30, -30, 40, -20)       # 0.50 s total, hit at 0.23 s
LIGHT2 = _strike(4, 3, 9, -35, 25, -30, 25)
LIGHT3 = _strike(5, 4, 11, 45, -40, 70, -35)
HEAVY = [(0, IDLE0),
         (10, P(spine_01=(-10, 0, 0), spine_02=(-12, 0, 20), upperarm_r=(0, -60, -10), lowerarm_r=(0, 0, 70),
                upperarm_l=(0, -40, 10), lowerarm_l=(0, 0, -70), thigh_l=(-10, 0, 0), thigh_r=(10, 0, 0))),
         (16, P(spine_01=(18, 0, 0), spine_02=(20, 0, -10), upperarm_r=(0, 40, 80), lowerarm_r=(0, 0, 6),
                upperarm_l=(0, 30, -80), lowerarm_l=(0, 0, -6), thigh_l=(-34, 0, 0), calf_l=(24, 0, 0),
                thigh_r=(22, 0, 0), calf_r=(10, 0, 0), root_loc=(0, -26, -10))),
         (34, IDLE0)]
_G = P(spine_02=(6, 0, 0), upperarm_r=(-40, 0, 60), lowerarm_r=(0, 0, 100), upperarm_l=(-45, 0, -60),
       lowerarm_l=(0, 0, -100), thigh_l=(-12, 0, 0), thigh_r=(12, 0, 0), calf_r=(12, 0, 0), calf_l=(10, 0, 0),
       root_loc=(0, 0, -4))
GUARD = [(0, IDLE0), (3, _G), (30, P(_G, spine_02=(7, 0, 0), root_loc=(0, 0, -4.5)))]
# Quick Step: 0.3 s i-frames -> roll completes by frame 9, recovers by 16.
QUICKSTEP = [(0, IDLE0),
             (3, P(spine_01=(25, 0, 0), thigh_l=(-50, 0, 0), calf_l=(60, 0, 0), thigh_r=(20, 0, 0), calf_r=(40, 0, 0),
                   upperarm_l=(30, 0, -40), upperarm_r=(30, 0, 40), root_loc=(0, -60, -18))),
             (9, P(spine_01=(15, 0, 0), thigh_l=(-20, 0, 0), calf_l=(30, 0, 0), thigh_r=(-10, 0, 0), calf_r=(30, 0, 0),
                   upperarm_l=(10, 0, -50), upperarm_r=(10, 0, 50), root_loc=(0, -150, -8))),
             (16, P(IDLE0, root_loc=(0, -180, 0)))]
HIT = [(0, IDLE0),
       (3, P(spine_01=(-14, 0, 6), spine_02=(-12, 0, 0), neck_01=(-15, 0, 0), upperarm_l=(0, 0, -40),
             upperarm_r=(0, 0, 40), thigh_l=(10, 0, 0), root_loc=(0, 12, -2))),
       (14, IDLE0)]
DEATH = [(0, IDLE0),
         (8, P(spine_01=(-20, 0, 0), spine_02=(-15, 0, 0), neck_01=(-20, 0, 0), thigh_l=(-20, 0, 0), calf_l=(70, 0, 0),
               thigh_r=(-10, 0, 0), calf_r=(80, 0, 0), upperarm_l=(0, 0, -20), upperarm_r=(0, 0, 20), root_loc=(0, 10, -40))),
         (22, P(pelvis=(-80, 0, 0), thigh_l=(70, 0, 0), thigh_r=(80, 0, 0), calf_l=(10, 0, 0),
                upperarm_l=(0, 0, -100), upperarm_r=(0, 0, 100), root_loc=(0, 40, -82))),
         (40, P(pelvis=(-90, 0, 0), thigh_l=(88, 0, 0), thigh_r=(90, 0, 0), upperarm_l=(0, 0, -110),
                upperarm_r=(0, 0, 105), root_loc=(0, 55, -86)))]
_AIR = P(thigh_l=(-50, 0, 0), calf_l=(70, 0, 0), thigh_r=(10, 0, 0), calf_r=(30, 0, 0),
         upperarm_l=(-40, 0, -50), upperarm_r=(-40, 0, 50))
JUMP = [(0, IDLE0),
        (5, P(thigh_l=(-30, 0, 0), calf_l=(50, 0, 0), thigh_r=(-30, 0, 0), calf_r=(50, 0, 0),
              spine_01=(15, 0, 0), root_loc=(0, 0, -16))),
        (10, _AIR), (20, _AIR)]

ANIMS = {"Idle": IDLE, "Walk": WALK, "Run": RUN, "Light1": LIGHT1, "Light2": LIGHT2, "Light3": LIGHT3,
         "Heavy": HEAVY, "Guard": GUARD, "QuickStep": QUICKSTEP, "HitReaction": HIT, "Death": DEATH, "Jump": JUMP}
