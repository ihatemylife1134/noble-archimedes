import time

import unreal

START = time.time()
STATE = {"n": 0, "handle": None}


def say(msg):
    unreal.log_warning("[NA-CAPTEST] " + str(msg))


def tick(delta):
    STATE["n"] += 1
    elapsed = time.time() - START
    if STATE["n"] <= 5 or STATE["n"] % 60 == 0:
        say("tick n=%d elapsed=%.2f" % (STATE["n"], elapsed))
    if elapsed >= 10.0:
        say("test quit at %.2f" % elapsed)
        if STATE["handle"] is not None:
            unreal.unregister_slate_post_tick_callback(STATE["handle"])
        unreal.SystemLibrary.quit_editor()


STATE["handle"] = unreal.register_slate_post_tick_callback(tick)
say("test scheduled")
