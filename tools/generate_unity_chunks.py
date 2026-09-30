"""
Noble Archimedes - Fast Direct Unity Chunk Generator
Inlines recompiled function implementations directly into chunk files,
completely eliminating 500+ redundant file-opens and header reparses per chunk.
Reduces compilation time by over 90%.
"""

from pathlib import Path
import re


_DISPATCH_TRANSFER_HELPERS = {
    "sub_00420450_0x420450.cpp",
    "sub_0041FFF0_0x41fff0.cpp",
}
_DISPATCH_TRANSFER_SWITCH = "    switch (ctx->pc) {"
_DISPATCH_TRANSFER_GUARD_PATTERN = re.compile(
    r"if\s*\(\s*runtime->guestDispatchDepth\(\)\s*!=\s*0u?\s*&&\s*"
    r"runtime->eeScheduler\(\)\.currentContext\(\)\s*==\s*ctx\s*\)\s*"
    r"\{\s*throw\s+EeDispatcherTransfer\s*\{\s*\}\s*;\s*\}",
    re.MULTILINE,
)
_DISPATCH_TRANSFER_GUARD = (
    "    if (runtime->guestDispatchDepth() != 0 && "
    "runtime->eeScheduler().currentContext() == ctx) {\n"
    "        throw EeDispatcherTransfer{};\n"
    "    }\n\n"
)


def _apply_dispatch_transfer_fix(function_file: Path, content: str) -> tuple[str, bool]:
    """Keep nested EE dispatcher transfer guards on the targeted helpers after regeneration."""
    if function_file.name not in _DISPATCH_TRANSFER_HELPERS:
        return content, False

    if _DISPATCH_TRANSFER_GUARD_PATTERN.search(content):
        return content, True

    if content.count(_DISPATCH_TRANSFER_SWITCH) != 1:
        raise ValueError(
            f"Expected one resume switch in generated {function_file.name}"
        )
    return content.replace(
        _DISPATCH_TRANSFER_SWITCH,
        _DISPATCH_TRANSFER_GUARD + _DISPATCH_TRANSFER_SWITCH,
        1,
    ), True


def generate_chunks(generated_dir: str, chunks_dir: str, num_chunks: int = 32):
    gen_path = Path(generated_dir)
    chunk_path = Path(chunks_dir)
    chunk_path.mkdir(parents=True, exist_ok=True)

    func_files = sorted(list(gen_path.glob("sub_*.cpp")))
    print(f"Discovered {len(func_files)} recompiled function files.")

    if not func_files:
        print("No function files found to batch!")
        return

    chunks = [[] for _ in range(num_chunks)]
    for idx, f in enumerate(func_files):
        chunks[idx % num_chunks].append(f)

    changed_chunks = []
    for i, file_list in enumerate(chunks):
        chunk_file = chunk_path / f"recomp_chunk_{i:02d}.cpp"
        contains_dispatch_transfer_helper = any(f.name in _DISPATCH_TRANSFER_HELPERS for f in file_list)
        parts = [
            "// Auto-generated Noble Archimedes fast unity chunk\n",
            "#include <stdexcept>\n",
            '#include "ps2_runtime_macros.h"\n',
            '#include "ps2_runtime.h"\n',
            "#include <ps2_recompiled_functions.h>\n",
            "#include <ps2_recompiled_stubs.h>\n",
            '#include "ps2_syscalls.h"\n',
            '#include "ps2_stubs.h"\n\n',
        ]
        if contains_dispatch_transfer_helper:
            parts.insert(-1, '#include "runtime/ee_scheduler.h"\n')

        for function_file in file_list:
            content = function_file.read_text(encoding="utf-8", errors="replace")
            # Find start of function definition (void sub_...).
            idx = content.find("void sub_")
            function_content = content[idx:] if idx != -1 else content
            function_content, _ = _apply_dispatch_transfer_fix(function_file, function_content)
            parts.extend((function_content, "\n\n"))

        content = "".join(parts)
        if not chunk_file.exists() or chunk_file.read_text(encoding="utf-8") != content:
            chunk_file.write_text(content, encoding="utf-8")
            changed_chunks.append(chunk_file)

    print(f"Generated {num_chunks} inlined unity chunks in {chunks_dir}; updated {len(changed_chunks)}.")
    return changed_chunks

if __name__ == "__main__":
    generate_chunks("src/recomp/generated", "src/recomp/chunks", num_chunks=32)
