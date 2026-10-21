import unreal

names = [n for n in dir(unreal.MaterialSamplerType) if n.startswith("SAMPLERTYPE")]
unreal.log_warning("[NA-SAMPLER] " + repr(names))
