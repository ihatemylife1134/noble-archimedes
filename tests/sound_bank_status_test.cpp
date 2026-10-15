#include "ps2_runtime_macros.h"
#include "../src/recomp/guest_entry_compat.hpp"
#include "resource_entry_aliases.hpp"
#include "ps2_runtime.h"
#include "../src/recomp/sound_bank_callbacks.hpp"
#include <cstdint>
#include <iostream>
#include <vector>

void sub_0042FD28_0x42fd28(uint8_t*, R5900Context*, PS2Runtime*);
void sub_00431128_0x431128(uint8_t*, R5900Context*, PS2Runtime*);
void sub_0042F790_0x42f790(uint8_t*, R5900Context*, PS2Runtime*);
void sub_0042FCE8_0x42fce8(uint8_t*, R5900Context*, PS2Runtime*);
void sub_0042FCB0_0x42fcb0(uint8_t*, R5900Context*, PS2Runtime*);
void sub_0042FA50_0x42fa50(uint8_t*, R5900Context*, PS2Runtime*);
void sub_007A7750_0x7a7750(uint8_t*, R5900Context*, PS2Runtime*) {
    throw std::runtime_error("resource alias entered the preceding function");
}
void sub_007A77D8_0x7a77d8(uint8_t*, R5900Context*, PS2Runtime*) {
    throw std::runtime_error("record release alias entered the preceding function");
}
void sub_0045C228_0x45c228(uint8_t*, R5900Context*, PS2Runtime*) {
    throw std::runtime_error("scene prologue test entered a later scene operation");
}
void sub_0042F9F8_0x42f9f8(uint8_t*, R5900Context*, PS2Runtime*)
{
    throw std::runtime_error("unexpected queue-finalization state");
}

extern const uint32_t g_ps2RecompiledFunctionTableBase = 0x42FA50u;
extern const uint32_t g_ps2RecompiledFunctionTableEnd = 0x92482Cu;
extern const uint32_t g_ps2RecompiledFunctionTableSlotCount = (0x92482Cu - 0x42FA50u) / 4u;
PS2Runtime::RecompiledFunction g_ps2RecompiledFunctionTable[g_ps2RecompiledFunctionTableSlotCount] = {};
void replyCallback(uint8_t* ram, R5900Context* ctx, PS2Runtime*)
{
    std::memcpy(ram + 0xADCBE0u, ram + 0x93A4A0u, 4u);
    std::memcpy(ram + 0xAD82B0u, ram + 0xADCBE0u, 4u);
    ctx->pc = GPR_U32(ctx, 31);
}

int main()
{
    std::vector<uint8_t> ram(PS2_RAM_SIZE);
    PS2Runtime runtime;
    g_ps2RecompiledFunctionTable[(0x431718u - g_ps2RecompiledFunctionTableBase) / 4u] = replyCallback;
    noble_sound::installCallbacks(&runtime);
    auto query = [&](uint32_t pc, uint32_t channel) {
        R5900Context ctx{};
        ctx.pc = pc;
        SET_GPR_U32(&ctx, 4, channel);
        SET_GPR_U32(&ctx, 31, 0x400000u);
        sub_0042FD28_0x42fd28(ram.data(), &ctx, &runtime);
        if (ctx.pc != 0x400000u) throw std::runtime_error("incorrect return PC");
        return GPR_U32((&ctx), 2);
    };
    for (uint16_t requested : {0u, 1u, 3u, 4u})
    for (uint16_t completed : {0u, 1u, 3u, 4u})
    for (uint32_t channel = 0; channel < 3; ++channel)
    {
        *reinterpret_cast<uint16_t*>(ram.data() + 0xAD82B0u) = requested;
        *reinterpret_cast<uint16_t*>(ram.data() + 0xAD82B2u) = completed;
        const uint32_t expected = ((requested >> channel) & 1u) && !((completed >> channel) & 1u);
        const uint32_t actual = query(0x42FD28u, channel);
        if (actual != expected ||
            *reinterpret_cast<uint16_t*>(ram.data() + 0xAD82B0u) != requested ||
            *reinterpret_cast<uint16_t*>(ram.data() + 0xAD82B2u) != completed)
        {
            std::cerr << "sound status: requested=" << requested << " completed=" << completed
                      << " channel=" << channel << " expected=" << expected << " actual=" << actual << '\n';
            return 1;
        }
    }
    auto command = [&](uint32_t op, uint32_t argument) {
        R5900Context ctx{};
        ctx.pc = 0x431128u;
        SET_GPR_U32(&ctx, 4, op);
        SET_GPR_U32(&ctx, 5, argument);
        SET_GPR_U32(&ctx, 31, 0x400000u);
        sub_00431128_0x431128(ram.data(), &ctx, &runtime);
        return GPR_U32((&ctx), 2);
    };
    // Both channels in the first level's queue must complete, including
    // channel 2, which was absent from the legacy hard-coded 0x0003 masks.
    for (uint32_t channel : {2u, 3u})
    {
        if (command(0x62030000u, channel << 16) != 0u || query(0x42FD28u, channel) != 1u)
            return 3;
        if (query(0x42FD68u, channel) != 1u || query(0x42FD80u, channel) != 0u)
            return 4;
        if (command(0x1D000000u | channel, 0u) != 0u || query(0x42FD28u, channel) != 0u)
            return 5;
        if (query(0x42FD80u, channel) != 1u) return 6;
        // Simulate an empty fallback RPC response and the guest feedback copy.
        std::memset(ram.data() + 0x93A4A0u, 0, 4u);
        R5900Context callback{};
        callback.pc = 0x431718u;
        SET_GPR_U32(&callback, 31, 0x400000u);
        runtime.lookupFunction(0x431718u)(ram.data(), &callback, &runtime);
        if (query(0x42FD28u, channel) != 0u || query(0x42FD80u, channel) != 1u)
            return 10;
    }
    if (command(0x1C000100u, 0u) != 0u || query(0x42FD28u, 0u) != 1u)
        return 9;
    *reinterpret_cast<uint32_t*>(ram.data() + 0xADC748u) = 63u;
    if (command(0x62030000u, 2u << 16) != 0xFFFFFFFFu || query(0x42FD28u, 2u) != 0u)
        return 7;
    // Execute the actual loader's two waiting states. It first waits for the
    // bank to become pending, sends the finish command, then waits for idle.
    g_ps2RecompiledFunctionTable[(0x42FD28u - g_ps2RecompiledFunctionTableBase) / 4u] = sub_0042FD28_0x42fd28;
    g_ps2RecompiledFunctionTable[(0x42FCE8u - g_ps2RecompiledFunctionTableBase) / 4u] = sub_0042FCE8_0x42fce8;
    g_ps2RecompiledFunctionTable[(0x431128u - g_ps2RecompiledFunctionTableBase) / 4u] = sub_00431128_0x431128;
    g_ps2RecompiledFunctionTable[(0x42FCB0u - g_ps2RecompiledFunctionTableBase) / 4u] = sub_0042FCB0_0x42fcb0;
    g_ps2RecompiledFunctionTable[(0x42FA50u - g_ps2RecompiledFunctionTableBase) / 4u] = sub_0042FA50_0x42fa50;
    *reinterpret_cast<uint32_t*>(ram.data() + 0xADC748u) = 0u;
    command(0x62030000u, 2u << 16);
    *reinterpret_cast<uint32_t*>(ram.data() + 0xAD8000u) = 3u;
    *reinterpret_cast<uint32_t*>(ram.data() + 0xAD8008u) = 0u;
    *reinterpret_cast<uint32_t*>(ram.data() + 0xAD8010u) = 2u;
    *reinterpret_cast<uint32_t*>(ram.data() + 0x9C6F7Cu) = 0x42F840u;
    *reinterpret_cast<uint32_t*>(ram.data() + 0x9C6F80u) = 0x42F8A8u;
    *reinterpret_cast<uint32_t*>(ram.data() + 0x9C6F88u) = 0x42F988u;
    for (uint32_t expected : {4u, 6u, 1u})
    {
        R5900Context ctx{};
        ctx.pc = 0x42F790u;
        SET_GPR_U32(&ctx, 29, 0x1FFF000u);
        SET_GPR_U32(&ctx, 31, 0x400000u);
        sub_0042F790_0x42f790(ram.data(), &ctx, &runtime);
        if (ctx.pc != 0x400000u || *reinterpret_cast<uint32_t*>(ram.data() + 0xAD8000u) != expected) {
            std::cerr << "loader state: expected=" << expected << " actual="
                      << *reinterpret_cast<uint32_t*>(ram.data() + 0xAD8000u)
                      << " pc=0x" << std::hex << ctx.pc << std::dec << '\n';
            return 8;
        }
        std::memset(ram.data() + 0x93A4A0u, 0, 4u);
        R5900Context callback{};
        callback.pc = 0x431718u;
        SET_GPR_U32(&callback, 31, 0x400000u);
        runtime.lookupFunction(0x431718u)(ram.data(), &callback, &runtime);
        if (query(0x42FD28u, 2u) != (expected == 4u ? 0u : 1u))
            return 11;
    }
    noble_entries::install(&runtime);
    runtime.registerFunction(0x471DB8u, noble_scene_object_entries);
    struct SceneEntryReached {};
    static bool sceneReached = false;
    constexpr uint32_t sceneObject = 0x31000u;
    constexpr uint32_t sceneSp = 0x1FFE000u;
    *reinterpret_cast<uint32_t*>(ram.data() + sceneObject + 0x24u) = 0x12345678u;
    runtime.registerFunction(0x4578C0u, [](uint8_t* sceneRam, R5900Context* ctx, PS2Runtime*) {
        if (GPR_U32(ctx, 4) != 0x12345678u || GPR_U32(ctx, 29) != sceneSp - 0x30u ||
            GPR_U32(ctx, 31) != 0x471DE8u || GPR_U32(ctx, 17) != 0u ||
            GPR_U32(ctx, 18) != sceneObject || GPR_U32(ctx, 20) != 0x940000u)
            throw std::runtime_error("scene alias skipped its original prologue");
        for (uint32_t saved = 0; saved < 5u; ++saved)
            if (*reinterpret_cast<uint64_t*>(sceneRam + sceneSp - 0x30u + saved * 8u) != 0x111u * (saved + 1u))
                throw std::runtime_error("scene alias changed saved registers");
        if (*reinterpret_cast<uint64_t*>(sceneRam + sceneSp - 8u) != 0x471D08u)
            throw std::runtime_error("scene alias changed saved return address");
        sceneReached = true;
        throw SceneEntryReached{};
    });
    R5900Context scene{};
    scene.pc = 0x471DB8u;
    SET_GPR_U32(&scene, 4, sceneObject);
    SET_GPR_U32(&scene, 29, sceneSp);
    SET_GPR_U32(&scene, 31, 0x471D08u);
    for (uint32_t reg = 0; reg < 5u; ++reg)
        SET_GPR_U64(&scene, 16u + reg, 0x111u * (reg + 1u));
    try { runtime.lookupFunction(scene.pc)(ram.data(), &scene, &runtime); }
    catch (const SceneEntryReached&) {}
    if (!sceneReached) return 25;
    runtime.registerFunction(0x7A7358u, noble_resource_entries);
    runtime.registerFunction(0x79C930u, noble_resource_texture_entries);
    runtime.registerFunction(0x79C960u, noble_resource_mesh_entries);
    runtime.registerFunction(0x79C9F8u, noble_resource_material_entries);
    runtime.registerFunction(0x79CB28u, noble_resource_record_release_entries);
    runtime.registerFunction(0x924828u, noble_resource_animation_entries);
    runtime.registerFunction(0x487B68u, noble_resource_resolve_entries);
    runtime.registerFunction(0x7A77D8u, sub_007A77D8_0x7a77d8);
    // The release callback is a separate leaf after a preceding routine's JR.
    // Exercise every branch and the actual caller's type-9 record layout.
    constexpr uint32_t releaseObject = 0x61000u;
    constexpr uint32_t releaseRecord = releaseObject + 0x50u;
    constexpr uint32_t releaseChild = 0x62000u;
    constexpr uint32_t releaseSp = 0x1FFFE60u;
    for (uint32_t descriptorFlags : {0u, 1u, 0x7FFFFFFFu, 0x80000000u, 0x80000002u, 0xFFFFFFFFu})
    for (uint32_t pointer : {0u, releaseChild})
    for (uint32_t childFlags : {0u, 0x123u, 0x7FFFFFFFu, 0x80000000u, 0x80000005u, 0xFFFFFFFFu})
    {
        std::memset(ram.data() + releaseObject, 0xA5, 64u);
        *reinterpret_cast<uint32_t*>(ram.data() + releaseObject + 0x24u) = 0x12345678u;
        *reinterpret_cast<uint32_t*>(ram.data() + releaseRecord) = 9u;
        *reinterpret_cast<uint32_t*>(ram.data() + releaseRecord + 4u) = descriptorFlags;
        *reinterpret_cast<uint32_t*>(ram.data() + releaseRecord + 8u) = 0xFCu;
        *reinterpret_cast<uint32_t*>(ram.data() + releaseRecord + 12u) = pointer;
        std::memset(ram.data() + releaseChild, 0x5A, 64u);
        *reinterpret_cast<uint32_t*>(ram.data() + releaseChild + 4u) = childFlags;
        std::memset(ram.data() + releaseSp - 64u, 0xCC, 128u);
        uint8_t expectedObject[64], expectedChild[64], expectedRecord[16], expectedStack[128];
        std::memcpy(expectedObject, ram.data() + releaseObject, sizeof(expectedObject));
        std::memset(expectedObject + 0x1Cu, 0, 4u);
        std::memcpy(expectedChild, ram.data() + releaseChild, sizeof(expectedChild));
        const bool childRead = (descriptorFlags & 0x80000000u) && pointer;
        if (childRead && (childFlags & 0x80000000u)) {
            const uint32_t clearedFlags = childFlags & 0x7FFFFFFFu;
            std::memcpy(expectedChild + 4u, &clearedFlags, sizeof(clearedFlags));
        }
        std::memcpy(expectedRecord, ram.data() + releaseRecord, sizeof(expectedRecord));
        std::memcpy(expectedStack, ram.data() + releaseSp - 64u, sizeof(expectedStack));
        R5900Context release{};
        release.pc = 0x79CB28u;
        for (uint32_t reg = 1; reg < 32u; ++reg)
            release.r[reg] = _mm_set_epi64x(0x123456789ABC0000ull + reg, 0x23456789ABCDE000ull + reg);
        SET_GPR_U32(&release, 4, releaseObject);
        SET_GPR_U32(&release, 5, releaseRecord);
        SET_GPR_U32(&release, 29, releaseSp);
        SET_GPR_U32(&release, 31, 0x79D098u);
        const R5900Context before = release;
        runtime.lookupFunction(release.pc)(ram.data(), &release, &runtime);
        const uint64_t expectedV0 = childRead ? ((childFlags & 0x80000000u)
            ? childFlags & 0x7FFFFFFFu : 0x7FFF0000u)
            : static_cast<uint64_t>(static_cast<int64_t>(static_cast<int32_t>(descriptorFlags)));
        const uint64_t expectedV1 = childRead
            ? static_cast<uint64_t>(static_cast<int64_t>(static_cast<int32_t>(childFlags)))
            : GPR_U64((&before), 3);
        if (release.pc != 0x79D098u || release.in_delay_slot ||
            GPR_U64((&release), 2) != expectedV0 || GPR_U64((&release), 3) != expectedV1 ||
            GPR_U64((&release), 5) != releaseRecord + 4u ||
            GPR_U64((&release), 6) != (childRead ? pointer : 0u) ||
            std::memcmp(ram.data() + releaseObject, expectedObject, sizeof(expectedObject)) ||
            std::memcmp(ram.data() + releaseChild, expectedChild, sizeof(expectedChild)) ||
            std::memcmp(ram.data() + releaseRecord, expectedRecord, sizeof(expectedRecord)) ||
            std::memcmp(ram.data() + releaseSp - 64u, expectedStack, sizeof(expectedStack)))
            throw std::runtime_error("record release alias changed original leaf behavior");
        for (uint32_t reg = 0; reg < 32u; ++reg) {
            const bool changed = reg == 2u || reg == 3u || reg == 5u || reg == 6u;
            const auto* actual = reinterpret_cast<const uint8_t*>(&release.r[reg]);
            const auto* original = reinterpret_cast<const uint8_t*>(&before.r[reg]);
            if (std::memcmp(actual + (changed ? 8u : 0u), original + (changed ? 8u : 0u), changed ? 8u : 16u))
                throw std::runtime_error("record release alias changed an untouched register lane");
        }
    }
    for (uint32_t index : {0u, 1u, 2u}) {
        *reinterpret_cast<uint32_t*>(ram.data() + 0x40010u) = 0x50000u;
        *reinterpret_cast<uint32_t*>(ram.data() + 0x40014u) = 2u;
        R5900Context ctx{};
        ctx.pc = 0x924828u;
        SET_GPR_U32(&ctx, 4, 0x40000u);
        SET_GPR_U32(&ctx, 5, index);
        SET_GPR_U32(&ctx, 31, 0x924A5Cu);
        runtime.lookupFunction(ctx.pc)(ram.data(), &ctx, &runtime);
        if (GPR_U32((&ctx), 2) != (index < 2 ? 0x50000u + 128*index : 0u) || ctx.pc != 0x924A5Cu)
            return 20;
    }
    for (uint32_t existing : {0u, 0x1234u})
    for (uint32_t flag : {0u, 0x80000003u}) {
        *reinterpret_cast<uint32_t*>(ram.data() + 0x20010u) = existing;
        *reinterpret_cast<uint32_t*>(ram.data() + 0x30004u) = flag;
        *reinterpret_cast<uint32_t*>(ram.data() + 0x3000Cu) = 0x12C8B80u;
        R5900Context ctx{};
        ctx.pc = 0x79C930u;
        SET_GPR_U32(&ctx, 4, 0x20000u);
        SET_GPR_U32(&ctx, 5, 0x30000u);
        SET_GPR_U32(&ctx, 31, 0x79CF48u);
        runtime.lookupFunction(0x79C930u)(ram.data(), &ctx, &runtime);
        const uint32_t expected = existing ? existing : (flag ? 0x12C8B80u : 0u);
        if (*reinterpret_cast<uint32_t*>(ram.data() + 0x20010u) != expected || ctx.pc != 0x79CF48u)
            return 17;
    }
    *reinterpret_cast<uint32_t*>(ram.data() + 0x20014u) = 0;
    *reinterpret_cast<uint32_t*>(ram.data() + 0x30004u) = 0x80000003u;
    R5900Context mesh{};
    mesh.pc = 0x79C960u;
    SET_GPR_U32(&mesh, 4, 0x20000u);
    SET_GPR_U32(&mesh, 5, 0x30000u);
    SET_GPR_U32(&mesh, 31, 0x79CF48u);
    runtime.lookupFunction(mesh.pc)(ram.data(), &mesh, &runtime);
    if (*reinterpret_cast<uint32_t*>(ram.data() + 0x20014u) != 0x12C8B80u || mesh.pc != 0x79CF48u)
        return 18;
    *reinterpret_cast<uint32_t*>(ram.data() + 0x2001Cu) = 0;
    *reinterpret_cast<uint32_t*>(ram.data() + 0x3000Cu) = 0x32000u;
    *reinterpret_cast<uint32_t*>(ram.data() + 0x32004u) = 5;
    R5900Context material{};
    material.pc = 0x79C9F8u;
    SET_GPR_U32(&material, 4, 0x20000u);
    SET_GPR_U32(&material, 5, 0x30000u);
    SET_GPR_U32(&material, 31, 0x79CF48u);
    runtime.lookupFunction(material.pc)(ram.data(), &material, &runtime);
    if (*reinterpret_cast<uint32_t*>(ram.data() + 0x2001Cu) != 0x32000u ||
        *reinterpret_cast<uint32_t*>(ram.data() + 0x32004u) != 0x80000005u || material.pc != 0x79CF48u)
        return 19;
    std::memset(ram.data() + 0x932750u, 0x5A, 16);
    std::memset(ram.data() + 0x10000u, 0xCC, 96);
    R5900Context defaults{};
    defaults.pc = 0x7A7358u;
    SET_GPR_U32(&defaults, 4, 0x10000u);
    SET_GPR_U32(&defaults, 31, 0x7A761Cu);
    runtime.lookupFunction(0x7A7358u)(ram.data(), &defaults, &runtime);
    for (uint32_t offset : {48u, 64u, 80u})
        if (std::memcmp(ram.data() + 0x10000u + offset, ram.data() + 0x932750u, 16))
            return 15;
    if (defaults.pc != 0x7A761Cu || GPR_U32((&defaults), 4) != 0x10050u ||
        *reinterpret_cast<uint64_t*>(ram.data() + 0x10028u) != 0)
        return 16;
    for (uint32_t pointer : {0u, 0x11CFE00u}) {
        R5900Context ctx{};
        SET_GPR_U32(&ctx, 4, pointer);
        SET_GPR_U32(&ctx, 31, 0x4125F4u);
        runtime.lookupFunction(0x454B40u)(ram.data(), &ctx, &runtime);
        if (*reinterpret_cast<uint32_t*>(ram.data() + 0xAED0F0u) != pointer ||
            GPR_S32((&ctx), 2) != (pointer ? 0 : -1) || ctx.pc != 0x4125F4u)
            return 12;
    }
    runtime.registerFunction(0x439260u, [](uint8_t*, R5900Context* ctx, PS2Runtime*) {
        if (GPR_U32(ctx, 4) != 0x123456u || GPR_U32(ctx, 5) != 0 ||
            GPR_U32(ctx, 29) != 0x1FFF030u || GPR_U32(ctx, 17) != 0x222u)
            throw std::runtime_error("incorrect split epilogue arguments");
        ctx->pc = GPR_U32(ctx, 31);
    });
    R5900Context continuation{};
    SET_GPR_U32(&continuation, 29, 0x1FFF000u);
    SET_GPR_U32(&continuation, 17, 0x123456u);
    for (uint32_t i = 0; i < 5; ++i)
        *reinterpret_cast<uint64_t*>(ram.data() + 0x1FFF000u + 8*i) =
            i == 4 ? 0x43C830u : 0x111u * (i+1);
    continuation.f[13] = 7.0f;
    runtime.lookupFunction(0x500004u)(ram.data(), &continuation, &runtime);
    if (continuation.pc != 0x439260u) return 14;
    // A tail jump transfers to the scheduler rather than nesting a host call.
    runtime.lookupFunction(continuation.pc)(ram.data(), &continuation, &runtime);
    if (continuation.pc != 0x43C830u || continuation.f[13] != 7.0f)
        return 13;
    for (uint32_t flags : {0x10u, 0x20u}) {
        const uint32_t object = 0x10000u;
        *reinterpret_cast<uint32_t*>(ram.data() + object) = 0x87E0B8u;
        *reinterpret_cast<uint32_t*>(ram.data() + object + 4u) = flags;
        *reinterpret_cast<uint32_t*>(ram.data() + object + 0x130u) = 0x10u;
        *reinterpret_cast<uint32_t*>(ram.data() + object + 0x54u) = 0xDEADBEEFu;
        R5900Context resolve{};
        resolve.pc = 0x487B68u;
        SET_GPR_U32(&resolve, 4, object);
        SET_GPR_U32(&resolve, 31, 0x797148u);
        runtime.lookupFunction(0x487B68u)(ram.data(), &resolve, &runtime);
        const uint32_t expected = flags == 0x20u ? 0x487BD0u : 0x87E0B8u;
        if (*reinterpret_cast<uint32_t*>(ram.data() + object + 0x54u) != expected ||
            GPR_U32((&resolve), 2) != expected || resolve.pc != 0x797148u)
            return 20;
    }
    std::cout << "Sound bank and level-entry checks passed\n";
}
