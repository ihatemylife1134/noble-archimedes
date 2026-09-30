from pathlib import Path

gen_path = Path("src/recomp/generated")
entry_files = sorted(list(gen_path.glob("entry_*.cpp")))
print(f"Inlining {len(entry_files)} entry files into recomp_chunk_entries.cpp")

header = """// Inlined entry functions for Noble Archimedes
#include <stdexcept>
#include "ps2_runtime_macros.h"
#include "ps2_runtime.h"
#include <ps2_recompiled_functions.h>
#include <ps2_recompiled_stubs.h>
#include "ps2_syscalls.h"
#include "ps2_stubs.h"

// Define registerRecompiledFunctions so caller can link cleanly
void registerRecompiledFunctions(PS2Runtime *runtime) {
    (void)runtime;
    // g_ps2RecompiledFunctionTable is initialized at load time
}

"""

with open("src/recomp/chunks/recomp_chunk_entries.cpp", "w", encoding="utf-8") as out:
    out.write(header)
    for f in entry_files:
        content = f.read_text(encoding="utf-8", errors="replace")
        idx = content.find("void entry_")
        if idx != -1:
            out.write(content[idx:])
            out.write("\n\n")
        else:
            out.write(content)
            out.write("\n\n")

print("Generated src/recomp/chunks/recomp_chunk_entries.cpp successfully!")
