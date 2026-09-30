from pathlib import Path
import toml
import re

with open("cvcod_ps2recomp_config.toml", "r") as f:
    cfg = toml.load(f)

stubs = cfg.get("general", {}).get("stubs", [])

with open("src/recomp/generated/register_functions.cpp", "r") as f:
    text = f.read()

raw_ranges = re.findall(r"\{\s*(\d+)u?,\s*(\d+)u?,\s*([^\}]+)\s*\}", text)
valid = [(int(s), int(e), fn.strip()) for s, e, fn in raw_ranges if int(s) < 1355112]

missing = []
for item in stubs:
    name, addr_str = item.split("@")
    addr = int(addr_str, 16)
    slot = (addr - 0x400000) // 4
    covered = any(s <= slot <= e for s, e, fn in valid)
    if not covered:
        missing.append((name, addr))

kernel_dir = Path("tools/PS2Recomp/ps2xRuntime/src/lib/Kernel")
all_headers = list(kernel_dir.rglob("*.h"))

registry = []

for name, addr in missing:
    clean_name = name.lstrip("_")
    for h in all_headers:
        htext = h.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"\bvoid\s+(" + re.escape(clean_name) + r")\s*\(", htext)
        if m:
            ns = "ps2_syscalls" if "Syscalls" in str(h) else "ps2_stubs"
            registry.append((name, clean_name, addr, ns))
            break

print(f"Writing runtime_stub_registry with {len(registry)} stubs...")

# Generate header
with open("src/recomp/runtime_stub_registry.hpp", "w", encoding="utf-8") as h_out:
    h_out.write("""#pragma once

class PS2Runtime;

namespace NobleArchimedes {
    void registerAllRuntimeStubs(PS2Runtime *runtime);
}
""")

# Generate cpp
with open("src/recomp/runtime_stub_registry.cpp", "w", encoding="utf-8") as c_out:
    c_out.write("""#include "runtime_stub_registry.hpp"
#include "ps2_runtime.h"
#include <iostream>

// Forward declare runtime stubs
namespace ps2_stubs {
""")
    stubs_set = set(r[1] for r in registry if r[3] == "ps2_stubs")
    for s in sorted(stubs_set):
        c_out.write(f"    void {s}(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);\n")
    c_out.write("}\n\n// Forward declare runtime syscalls\nnamespace ps2_syscalls {\n")
    syscalls_set = set(r[1] for r in registry if r[3] == "ps2_syscalls")
    for s in sorted(syscalls_set):
        c_out.write(f"    void {s}(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);\n")
    c_out.write("""}

namespace NobleArchimedes {
void registerAllRuntimeStubs(PS2Runtime *runtime) {
""")
    c_out.write(f'    std::cout << "[Stubs] Registering {len(registry)} Sony SDK runtime stubs into function table..." << std::endl;\n')
    for name, clean, addr, ns in sorted(registry, key=lambda x: x[2]):
        c_out.write(f"    runtime->registerFunction(0x{addr:08X}u, {ns}::{clean});\n")
    c_out.write(f'    std::cout << "[Stubs] Successfully registered {len(registry)} runtime handlers." << std::endl;\n')
    c_out.write("}\n}\n")

print("Generated src/recomp/runtime_stub_registry.hpp and .cpp successfully!")
