import unreal

for args in ((255, 0, 0, 255), (0, 0, 255, 255), (51, 140, 255, 255)):
    c = unreal.Color(*args)
    unreal.log_warning("[NA-COLOR] args=%r -> r=%d g=%d b=%d a=%d" % (
        args, c.r, c.g, c.b, c.a))
