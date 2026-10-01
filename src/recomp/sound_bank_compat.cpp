#include "sound_bank_compat.hpp"
#include "sound_bank_callbacks.hpp"
#include "ps2_runtime.h"
#include "ps2_runtime_macros.h"

#include <cstdint>
#include <cstring>
#include <initializer_list>
#include <unordered_map>

// The custom IOP sound command service is not implemented yet. Preserve its
// EE-side bank handshake without tying completion to host audio output.
namespace noble_sound
{
namespace
{
struct BankMasks { uint16_t requested, complete; };
std::unordered_map<const uint8_t*, BankMasks> bankMasks;
PS2Runtime::RecompiledFunction guestCallback = nullptr;
}
inline uint16_t readMask(const uint8_t* ram, uint32_t address)
{
    uint16_t value;
    std::memcpy(&value, ram + address, sizeof(value));
    return value;
}

inline void writeMask(uint8_t* ram, uint32_t address, uint16_t value)
{
    std::memcpy(ram + address, &value, sizeof(value));
}

void acceptedCommand(uint8_t* ram, uint32_t command, uint32_t argument)
{
    const bool prepare = command == 0x62030000u;
    const bool begin = prepare || (command & 0xFF000000u) == 0x1C000000u;
    const bool finish = (command & 0xFF000000u) == 0x1D000000u;
    if (!begin && !finish) return;
    const uint32_t channel = prepare ? argument >> 16 : command & 0xFFu;
    if (channel >= 16u) return;
    const uint16_t bit = static_cast<uint16_t>(1u << channel);
    auto [entry, inserted] = bankMasks.try_emplace(ram, BankMasks{
        readMask(ram, 0xAD82B0u), readMask(ram, 0xAD82B2u)});
    auto& masks = entry->second;
    masks.requested |= bit;
    masks.complete = begin ? masks.complete & ~bit : masks.complete | bit;
    for (const uint32_t base : {0xAD82B0u, 0xADCBE0u})
    {
        writeMask(ram, base, masks.requested);
        writeMask(ram, base + 2u, masks.complete);
    }
}

uint32_t bankStatus(const uint8_t* ram, uint32_t pc, uint32_t channel)
{
    const uint32_t shift = channel & 31u;
    const uint32_t requested = (readMask(ram, 0xAD82B0u) >> shift) & 1u;
    const uint32_t complete = (readMask(ram, 0xAD82B2u) >> shift) & 1u;
    if (pc == 0x42FD68u) return requested;
    if (pc == 0x42FD80u) return complete;
    if (pc == 0x42FD98u || pc == 0x42FDB8u)
    {
        const uint32_t address = (0xAD8074u + channel * 12u + (pc == 0x42FDB8u)) & 0x1FFFFFFu;
        return static_cast<uint32_t>(static_cast<int32_t>(static_cast<int8_t>(ram[address])));
    }
    if (pc == 0x42FDD8u || pc == 0x42FDF8u)
    {
        const uint32_t address = (0xAD8070u + channel * 12u + (pc == 0x42FDF8u ? 8u : 0u)) & 0x1FFFFFFu;
        uint32_t value;
        std::memcpy(&value, ram + address, sizeof(value));
        return value;
    }
    return requested && !complete;
}

namespace
{
void soundReplyCallback(uint8_t* ram, R5900Context* ctx, PS2Runtime* runtime)
{
    // The fallback RPC reply contains no bank feedback. Fill just these two
    // status fields before the original guest callback copies its reply.
    if (const auto it = bankMasks.find(ram); it != bankMasks.end())
    {
        writeMask(ram, 0x93A4A0u, it->second.requested);
        writeMask(ram, 0x93A4A2u, it->second.complete);
    }
    guestCallback(ram, ctx, runtime);
}
}

void installCallbacks(PS2Runtime* runtime)
{
    const auto original = runtime->lookupFunction(0x431718u);
    if (original == soundReplyCallback) return;
    guestCallback = original;
    bankMasks.clear();
    runtime->registerFunction(0x431718u, soundReplyCallback);
}
}
