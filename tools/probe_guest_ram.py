"""Read explicit guest RAM words from a running PID or a saved minidump.

Live mode opens the supplied process for query/read access only and locates
the game's 32 MiB RDRAM allocation by a known four-word table. Dump mode uses
an explicit validated base. Both check a phase-index word and print only the
requested guest addresses.
"""

import argparse
import ctypes
from pathlib import Path
import struct
import sys


PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
MEM_PRIVATE = 0x20000
PAGE_GUARD = 0x100
PAGE_NOACCESS = 0x01
READABLE_PROTECTIONS = {0x02, 0x04, 0x08, 0x20, 0x40, 0x80}
RDRAM_SIZE = 32 * 1024 * 1024
SCAN_MIN_REGION = 16 * 1024 * 1024
SCAN_MAX_REGION = 64 * 1024 * 1024
SCAN_BUDGET = 256 * 1024 * 1024
ANCHOR_ADDRESS = 0x009C7050
ANCHOR_WORDS = (0x0043B990, 0x0043B9B0, 0x0043B9C0, 0x0043B9E0)
PHASE_INDEX_ADDRESS = 0x00AC23A0
PHASE_TABLE_ADDRESS = 0x00AC23A4
PHASE_FRAME_TABLE_ADDRESS = 0x00AC23E4
# The generated guest code's `lui 0xB2; addiu -0x7500` resolves to B18B00.
TARGET_WORDS = tuple(range(0x00B18B00, 0x00B18B44, 4))


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", ctypes.c_ulong),
        ("PartitionId", ctypes.c_ushort),
        ("RegionSize", ctypes.c_size_t),
        ("State", ctypes.c_ulong),
        ("Protect", ctypes.c_ulong),
        ("Type", ctypes.c_ulong),
    ]


def fail(message):
    print(f"read_guest_ram: {message}", file=sys.stderr)
    raise SystemExit(2)


def parse_guest_address(token):
    """Resolve a numeric guest address or MIPS HI:LO[:OFFSET] address token."""
    parts = token.split(":")
    try:
        if len(parts) == 1:
            return int(token, 0)
        if len(parts) not in (2, 3):
            raise ValueError
        hi = int(parts[0], 0)
        lo = int(parts[1], 0)
        if not -0x8000 <= hi <= 0xFFFF or not -0x8000 <= lo <= 0xFFFF:
            raise ValueError
        # LUI places the 16-bit immediate in the high half; ADDIU sign-extends
        # its low immediate before adding it to that value.
        address = ((hi & 0xFFFF) << 16) + (lo if lo < 0x8000 else lo - 0x10000)
        if len(parts) == 3:
            address += int(parts[2], 0)
        return address
    except ValueError:
        raise ValueError(
            f"invalid address {token!r}; use an integer or HI:LO[:OFFSET] "
            "with HI/LO in signed-or-unsigned 16-bit range"
        ) from None


def parse_targets(tokens):
    targets = []
    for token in tokens:
        try:
            targets.append((token, parse_guest_address(token)))
        except ValueError as error:
            fail(str(error))
    return targets


def validate_guest_base(read, guest_base, allow_invalid_phase=False):
    """A runtime pointer is only a hint; validate the game data in this PID."""
    if guest_base <= 0 or guest_base + RDRAM_SIZE > 0x00007FFFFFFFFFFF:
        return None
    anchor = struct.pack("<4I", *ANCHOR_WORDS)
    phase_bytes = read(guest_base + PHASE_INDEX_ADDRESS, 4)
    if read(guest_base + ANCHOR_ADDRESS, len(anchor)) != anchor or phase_bytes is None:
        return None
    phase_index = struct.unpack("<I", phase_bytes)[0]
    if phase_index >= 16:
        if allow_invalid_phase and read(guest_base + PHASE_TABLE_ADDRESS, 128) is not None:
            # An explicit runtime allocation hint plus the current game's
            # anchor identifies RAM even when its phase stack is unhealthy.
            # Never use an invalid index to read outside the fixed phase block.
            return guest_base, phase_index, None, None
        return None
    phase_bytes = read(guest_base + PHASE_TABLE_ADDRESS + phase_index * 4, 4)
    frame_bytes = read(guest_base + PHASE_FRAME_TABLE_ADDRESS + phase_index * 4, 4)
    if phase_bytes is None or frame_bytes is None:
        return None
    return guest_base, phase_index, struct.unpack("<I", phase_bytes)[0], struct.unpack("<I", frame_bytes)[0]


def print_guest_words(read_guest, addresses, label):
    anchor = struct.pack("<4I", *ANCHOR_WORDS)
    if read_guest(ANCHOR_ADDRESS, len(anchor)) != anchor:
        fail(f"known game table did not validate guest base ({label})")
    phase_bytes = read_guest(PHASE_INDEX_ADDRESS, 4)
    if phase_bytes is None:
        fail(f"phase index is unreadable ({label})")
    phase_index = struct.unpack("<I", phase_bytes)[0]
    if phase_index >= 16:
        fail(f"phase index is outside the known table ({label}): {phase_index}")
    phase = struct.unpack(
        "<I", read_guest(PHASE_TABLE_ADDRESS + phase_index * 4, 4) or b"\0" * 4
    )[0]
    frames = struct.unpack(
        "<I", read_guest(PHASE_FRAME_TABLE_ADDRESS + phase_index * 4, 4) or b"\0" * 4
    )[0]
    print(f"{label} phase_index={phase_index} phase=0x{phase:X} phase_frames={frames}")
    for token, address in addresses:
        data = read_guest(address, 4)
        if data is None:
            print(f"guest[{token}->0x{address:08X}]=<unreadable>")
        else:
            value = struct.unpack("<I", data)[0]
            print(f"guest[{token}->0x{address:08X}]=0x{value:08X} ({value})")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pid", nargs="?", help="PID of the running candidate")
    parser.add_argument("--dump", help="saved Windows minidump path (offline mode)")
    parser.add_argument("--base", type=lambda s: int(s, 0), help="validated guest RDRAM base")
    parser.add_argument("--base-file", type=Path, help="runtime pointer hint, validated in the live PID")
    parser.add_argument("--save-ram", help="save validated live RDRAM for offline inspection")
    parser.add_argument(
        "addresses", nargs="*",
        help="guest word addresses to read (default: B18B00 through B18B40)",
    )
    args = parser.parse_args()
    address_tokens = list(args.addresses)
    if args.dump and args.pid is not None:
        # With optional PID before `addresses nargs=*`, argparse assigns the
        # first positional token to pid. In dump mode that token is an address.
        address_tokens.insert(0, args.pid)
    elif not args.dump and args.pid is not None:
        try:
            args.pid = int(args.pid, 0)
        except ValueError:
            fail("live mode PID must be an integer")
    targets = parse_targets(address_tokens) if address_tokens else [
        (f"0x{address:X}", address) for address in TARGET_WORDS
    ]
    if not targets or any(
        address < 0 or address % 4 or address + 4 > RDRAM_SIZE
        for _, address in targets
    ):
        fail("requested addresses must be aligned within the 32 MiB guest RDRAM")

    if args.dump:
        if args.base is None:
            fail("dump mode requires --base")
        from minidump.minidumpfile import MinidumpFile

        reader = MinidumpFile.parse(args.dump).get_reader()

        def read_guest(address, size):
            try:
                return reader.read(args.base + address, size)
            except Exception:
                return None

        print_guest_words(read_guest, targets, f"dump={args.dump} base=0x{args.base:X}")
        return

    if args.pid is None or (args.base is not None and args.base_file is not None):
        fail("live mode requires a PID and at most one base hint")
    if sys.platform != "win32" or ctypes.sizeof(ctypes.c_void_p) != 8:
        fail("live mode requires 64-bit Python on Windows")

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.argtypes = (ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32)
    kernel32.OpenProcess.restype = ctypes.c_void_p
    kernel32.CloseHandle.argtypes = (ctypes.c_void_p,)
    kernel32.ReadProcessMemory.argtypes = (
        ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p,
        ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t),
    )
    kernel32.ReadProcessMemory.restype = ctypes.c_int
    kernel32.VirtualQueryEx.argtypes = (
        ctypes.c_void_p, ctypes.c_void_p,
        ctypes.POINTER(MEMORY_BASIC_INFORMATION), ctypes.c_size_t,
    )
    kernel32.VirtualQueryEx.restype = ctypes.c_size_t

    process = kernel32.OpenProcess(
        PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, args.pid
    )
    if not process:
        fail(f"OpenProcess failed for PID {args.pid} (winerror={ctypes.get_last_error()})")

    def read(address, size):
        buffer = ctypes.create_string_buffer(size)
        received = ctypes.c_size_t()
        ok = kernel32.ReadProcessMemory(
            process, ctypes.c_void_p(address), buffer, size, ctypes.byref(received)
        )
        if not ok or received.value != size:
            return None
        return buffer.raw

    anchor = struct.pack("<4I", *ANCHOR_WORDS)
    candidates = set()
    scanned = 0
    cursor = 0x10000
    max_address = 0x00007FFFFFFF0000
    try:
        hinted_base = args.base
        if args.base_file is not None:
            try:
                hinted_base = int(args.base_file.read_text().strip(), 0)
            except (OSError, ValueError) as error:
                fail(f"runtime base hint is unavailable: {error}")
        if hinted_base is not None:
            candidates.add(hinted_base)
        while hinted_base is None and cursor < max_address and scanned < SCAN_BUDGET:
            mbi = MEMORY_BASIC_INFORMATION()
            queried = kernel32.VirtualQueryEx(
                process, ctypes.c_void_p(cursor), ctypes.byref(mbi), ctypes.sizeof(mbi)
            )
            if not queried:
                break
            base = int(mbi.BaseAddress or 0)
            size = int(mbi.RegionSize)
            if size <= 0:
                break
            protection = int(mbi.Protect) & 0xFF
            eligible = (
                mbi.State == MEM_COMMIT and mbi.Type == MEM_PRIVATE
                and not (mbi.Protect & PAGE_GUARD)
                and protection in READABLE_PROTECTIONS
                and SCAN_MIN_REGION <= size <= SCAN_MAX_REGION
            )
            if eligible:
                chunk_size = 1024 * 1024
                offset = 0
                carry = b""
                while offset < size and scanned < SCAN_BUDGET:
                    take = min(chunk_size, size - offset, SCAN_BUDGET - scanned)
                    data = read(base + offset, take)
                    scanned += take
                    if data is not None:
                        combined = carry + data
                        search_from = 0
                        while True:
                            found = combined.find(anchor, search_from)
                            if found < 0:
                                break
                            absolute = base + offset - len(carry) + found
                            guest_base = absolute - ANCHOR_ADDRESS
                            if guest_base > 0 and guest_base + RDRAM_SIZE <= base + size:
                                candidates.add(guest_base)
                            search_from = found + 1
                        carry = combined[-(len(anchor) - 1):]
                    else:
                        carry = b""
                    offset += take
            cursor = base + size

        validated = []
        for guest_base in candidates:
            result = validate_guest_base(read, guest_base, allow_invalid_phase=hinted_base is not None)
            if result is not None:
                validated.append(result)

        if len(validated) != 1:
            fail(
                f"could not uniquely validate RDRAM base: anchors={len(candidates)} "
                f"phase-valid={len(validated)} scanned={scanned} bytes"
            )

        guest_base, phase_index, phase, frames = validated[0]
        if args.save_ram:
            snapshot = read(guest_base, RDRAM_SIZE)
            if snapshot is None:
                fail("could not read complete guest RAM")
            Path(args.save_ram).write_bytes(snapshot)
        phase_text = "phase_invalid=1" if phase is None else f"phase=0x{phase:X} phase_frames={frames}"
        print(
            f"pid={args.pid} rdram_base=0x{guest_base:X} size=0x{RDRAM_SIZE:X} "
            f"anchor=0x{ANCHOR_ADDRESS:X} phase_index={phase_index} "
            + phase_text
        )
        for token, address in targets:
            data = read(guest_base + address, 4)
            if data is None:
                print(f"guest[{token}->0x{address:08X}]=<unreadable>")
            else:
                value = struct.unpack("<I", data)[0]
                print(f"guest[{token}->0x{address:08X}]=0x{value:08X} ({value})")
    finally:
        kernel32.CloseHandle(process)


if __name__ == "__main__":
    main()
