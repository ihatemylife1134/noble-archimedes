import unreal
names = [n for n in dir(unreal.EditorAssetLibrary) if "load" in n.lower() or "delete" in n.lower() or "rename" in n.lower() or "unload" in n.lower()]
for n in names:
    print(n)
print("--- package funcs ---")
print([n for n in dir(unreal) if "unload" in n.lower() or "package" in n.lower()][:60])
