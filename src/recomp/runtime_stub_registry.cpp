#include "runtime_stub_registry.hpp"
#include "ps2_runtime.h"
#include "sound_bank_callbacks.hpp"
#include "guest_entry_compat.hpp"
#include "resource_entry_aliases.hpp"
#include <iostream>

// Forward declare runtime stubs
namespace ps2_stubs {
    void sceCdSearchFile(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceCdSeek(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceCdStPause(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceCdStResume(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceCdStSeek(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceCdStSeekF(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceCdStStat(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceCdStandby(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceCdStop(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceDeci2Close(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceDeci2ExLock(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceDeci2ExReqSend(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceDeci2ExUnLock(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceDmaGetEnv(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceDmaRecv(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceDmaRecvI(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceDmaRecvN(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceDmaSendI(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceDmaWatch(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceGsSyncVCallback(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceIoctl(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceIpuSync(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceMcChangeThreadPriority(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceMcChdir(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceMcEnd(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceMcFlush(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceMcGetSlotMax(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceMcUnformat(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceMpegAddBs(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceMpegGetDecodeMode(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceMpegGetPictureRAW8(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceMpegGetPictureRAW8xy(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void scePadGetButtonMask(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void scePadGetFrameCount(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void scePadGetPortMax(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void scePadInfoComb(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void scePadSetVrefParam(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void scePadStateIntToStr(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceSdTransToIOP(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceSifAllocIopHeap(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceSifAllocSysMemory(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceSifGetIopAddr(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceSifGetOtherData(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceSifIsAliveIop(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceSifLoadElf(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceSifLoadIopHeap(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceSifRpcLoop(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceSifSetIopAddr(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceVpu0Reset(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceVu0CameraMatrix(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceVu0ClipAll(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceVu0ClipScreen(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceVu0ClipScreen3(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceVu0DivVector(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceVu0DivVectorXYZ(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceVu0DropShadowMatrix(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceVu0InterVectorXYZ(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceVu0LightColorMatrix(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceVu0NormalLightMatrix(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
    void sceVu0RotTransPersN(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
}

// Forward declare runtime syscalls
namespace ps2_syscalls {
    void iRotateThreadReadyQueue(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime);
}

namespace {
void runtime_stub_0074BE30_sceSdTransToIOP(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceSdTransToIOP(rdram, ctx, runtime);
}

void runtime_stub_0074CF08_sceCdSearchFile(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceCdSearchFile(rdram, ctx, runtime);
}

void runtime_stub_0074DFC0_sceCdSeek(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceCdSeek(rdram, ctx, runtime);
}

void runtime_stub_0074E090_sceCdStandby(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceCdStandby(rdram, ctx, runtime);
}

void runtime_stub_0074E140_sceCdStop(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceCdStop(rdram, ctx, runtime);
}

void runtime_stub_0074F588_sceGsSyncVCallback(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceGsSyncVCallback(rdram, ctx, runtime);
}

void runtime_stub_0074FD10_sceDmaGetEnv(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceDmaGetEnv(rdram, ctx, runtime);
}

void runtime_stub_0074FE40_sceDmaSendI(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceDmaSendI(rdram, ctx, runtime);
}

void runtime_stub_0074FEB8_sceDmaRecv(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceDmaRecv(rdram, ctx, runtime);
}

void runtime_stub_0074FF00_sceDmaRecvN(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceDmaRecvN(rdram, ctx, runtime);
}

void runtime_stub_0074FF80_sceDmaRecvI(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceDmaRecvI(rdram, ctx, runtime);
}

void runtime_stub_00750038_sceDmaWatch(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceDmaWatch(rdram, ctx, runtime);
}

void runtime_stub_00750CC8_sceVu0DivVector(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceVu0DivVector(rdram, ctx, runtime);
}

void runtime_stub_00750CE8_sceVu0DivVectorXYZ(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceVu0DivVectorXYZ(rdram, ctx, runtime);
}

void runtime_stub_00751148_sceVu0CameraMatrix(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceVu0CameraMatrix(rdram, ctx, runtime);
}

void runtime_stub_007511F8_sceVu0NormalLightMatrix(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceVu0NormalLightMatrix(rdram, ctx, runtime);
}

void runtime_stub_007512B8_sceVu0LightColorMatrix(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceVu0LightColorMatrix(rdram, ctx, runtime);
}

void runtime_stub_00751428_sceVu0DropShadowMatrix(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceVu0DropShadowMatrix(rdram, ctx, runtime);
}

void runtime_stub_007515B8_sceVu0RotTransPersN(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceVu0RotTransPersN(rdram, ctx, runtime);
}

void runtime_stub_00751678_sceVu0InterVectorXYZ(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceVu0InterVectorXYZ(rdram, ctx, runtime);
}

void runtime_stub_007516C0_sceVu0ClipScreen(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceVu0ClipScreen(rdram, ctx, runtime);
}

void runtime_stub_00751708_sceVu0ClipScreen3(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceVu0ClipScreen3(rdram, ctx, runtime);
}

void runtime_stub_00751768_sceVu0ClipAll(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceVu0ClipAll(rdram, ctx, runtime);
}

void runtime_stub_007517F8_sceVpu0Reset(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceVpu0Reset(rdram, ctx, runtime);
}

void runtime_stub_00752790_sceMcEnd(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceMcEnd(rdram, ctx, runtime);
}

void runtime_stub_007527F8_sceMcChangeThreadPriority(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceMcChangeThreadPriority(rdram, ctx, runtime);
}

void runtime_stub_007528B8_sceMcGetSlotMax(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceMcGetSlotMax(rdram, ctx, runtime);
}

void runtime_stub_007534A8_sceMcChdir(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceMcChdir(rdram, ctx, runtime);
}

void runtime_stub_007537D8_sceMcFlush(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceMcFlush(rdram, ctx, runtime);
}

void runtime_stub_00753BC0_sceMcUnformat(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceMcUnformat(rdram, ctx, runtime);
}

void runtime_stub_007545F0_scePadGetFrameCount(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::scePadGetFrameCount(rdram, ctx, runtime);
}

void runtime_stub_00754738_scePadStateIntToStr(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::scePadStateIntToStr(rdram, ctx, runtime);
}

void runtime_stub_007549D0_scePadInfoComb(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::scePadInfoComb(rdram, ctx, runtime);
}

void runtime_stub_00754E78_scePadGetButtonMask(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::scePadGetButtonMask(rdram, ctx, runtime);
}

void runtime_stub_00755108_scePadSetVrefParam(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::scePadSetVrefParam(rdram, ctx, runtime);
}

void runtime_stub_007551D8_scePadGetPortMax(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::scePadGetPortMax(rdram, ctx, runtime);
}

void runtime_stub_0075E380_iRotateThreadReadyQueue(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_syscalls::iRotateThreadReadyQueue(rdram, ctx, runtime);
}

void runtime_stub_00760C88_sceSifGetOtherData(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceSifGetOtherData(rdram, ctx, runtime);
}

void runtime_stub_00761820_sceSifRpcLoop(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceSifRpcLoop(rdram, ctx, runtime);
}

void runtime_stub_007630E8_sceIoctl(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceIoctl(rdram, ctx, runtime);
}

void runtime_stub_00765520_sceSifAllocIopHeap(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceSifAllocIopHeap(rdram, ctx, runtime);
}

void runtime_stub_00765590_sceSifAllocSysMemory(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceSifAllocSysMemory(rdram, ctx, runtime);
}

void runtime_stub_007656A8_sceSifLoadIopHeap(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceSifLoadIopHeap(rdram, ctx, runtime);
}

void runtime_stub_00766550_sceSifLoadElf(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceSifLoadElf(rdram, ctx, runtime);
}

void runtime_stub_00766578_sceSifGetIopAddr(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceSifGetIopAddr(rdram, ctx, runtime);
}

void runtime_stub_00766668_sceSifSetIopAddr(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceSifSetIopAddr(rdram, ctx, runtime);
}

void runtime_stub_007668A0_sceSifIsAliveIop(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceSifIsAliveIop(rdram, ctx, runtime);
}

void runtime_stub_00768CA0_sceDeci2Close(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceDeci2Close(rdram, ctx, runtime);
}

void runtime_stub_00768DE8_sceDeci2ExReqSend(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceDeci2ExReqSend(rdram, ctx, runtime);
}

void runtime_stub_00768E18_sceDeci2ExLock(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceDeci2ExLock(rdram, ctx, runtime);
}

void runtime_stub_00768E40_sceDeci2ExUnLock(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceDeci2ExUnLock(rdram, ctx, runtime);
}

void runtime_stub_0090F250_sceMpegAddBs(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceMpegAddBs(rdram, ctx, runtime);
}

void runtime_stub_0090F2D8_sceMpegGetPictureRAW8(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceMpegGetPictureRAW8(rdram, ctx, runtime);
}

void runtime_stub_0090F3E8_sceMpegGetDecodeMode(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceMpegGetDecodeMode(rdram, ctx, runtime);
}

void runtime_stub_0090F618_sceMpegGetPictureRAW8xy(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceMpegGetPictureRAW8xy(rdram, ctx, runtime);
}

void runtime_stub_00918AA0_sceCdStSeekF(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceCdStSeekF(rdram, ctx, runtime);
}

void runtime_stub_00918AD0_sceCdStSeek(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceCdStSeek(rdram, ctx, runtime);
}

void runtime_stub_00918CC0_sceCdStPause(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceCdStPause(rdram, ctx, runtime);
}

void runtime_stub_00918D10_sceCdStResume(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceCdStResume(rdram, ctx, runtime);
}

void runtime_stub_00918D68_sceCdStStat(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceCdStStat(rdram, ctx, runtime);
}

void runtime_stub_0092AA08_sceIpuSync(uint8_t *rdram, R5900Context *ctx, PS2Runtime *runtime)
{
    ctx->pc = getRegU32(ctx, 31);
    ps2_stubs::sceIpuSync(rdram, ctx, runtime);
}

}

namespace NobleArchimedes {
void registerAllRuntimeStubs(PS2Runtime *runtime) {
    noble_sound::installCallbacks(runtime);
    noble_entries::install(runtime);
    for (uint32_t address : {0x7A7098u, 0x7A7328u, 0x7A7358u})
        runtime->registerFunction(address, noble_resource_entries);
    runtime->registerFunction(0x79C930u, noble_resource_texture_entries);
    runtime->registerFunction(0x79C960u, noble_resource_mesh_entries);
    runtime->registerFunction(0x79C9F8u, noble_resource_material_entries);
    runtime->registerFunction(0x79CB28u, noble_resource_record_release_entries);
    runtime->registerFunction(0x924828u, noble_resource_animation_entries);
    runtime->registerFunction(0x794EA0u, noble_resource_animation_update_entries);
    runtime->registerFunction(0x487B68u, noble_resource_resolve_entries);
    runtime->registerFunction(0x471DB8u, noble_scene_object_entries);
    std::cout << "[Stubs] Registering 61 Sony SDK runtime stubs into function table..." << std::endl;
    runtime->registerFunction(0x0074BE30u, runtime_stub_0074BE30_sceSdTransToIOP);
    runtime->registerFunction(0x0074CF08u, runtime_stub_0074CF08_sceCdSearchFile);
    runtime->registerFunction(0x0074DFC0u, runtime_stub_0074DFC0_sceCdSeek);
    runtime->registerFunction(0x0074E090u, runtime_stub_0074E090_sceCdStandby);
    runtime->registerFunction(0x0074E140u, runtime_stub_0074E140_sceCdStop);
    runtime->registerFunction(0x0074F588u, runtime_stub_0074F588_sceGsSyncVCallback);
    runtime->registerFunction(0x0074FD10u, runtime_stub_0074FD10_sceDmaGetEnv);
    runtime->registerFunction(0x0074FE40u, runtime_stub_0074FE40_sceDmaSendI);
    runtime->registerFunction(0x0074FEB8u, runtime_stub_0074FEB8_sceDmaRecv);
    runtime->registerFunction(0x0074FF00u, runtime_stub_0074FF00_sceDmaRecvN);
    runtime->registerFunction(0x0074FF80u, runtime_stub_0074FF80_sceDmaRecvI);
    runtime->registerFunction(0x00750038u, runtime_stub_00750038_sceDmaWatch);
    runtime->registerFunction(0x00750CC8u, runtime_stub_00750CC8_sceVu0DivVector);
    runtime->registerFunction(0x00750CE8u, runtime_stub_00750CE8_sceVu0DivVectorXYZ);
    runtime->registerFunction(0x00751148u, runtime_stub_00751148_sceVu0CameraMatrix);
    runtime->registerFunction(0x007511F8u, runtime_stub_007511F8_sceVu0NormalLightMatrix);
    runtime->registerFunction(0x007512B8u, runtime_stub_007512B8_sceVu0LightColorMatrix);
    runtime->registerFunction(0x00751428u, runtime_stub_00751428_sceVu0DropShadowMatrix);
    runtime->registerFunction(0x007515B8u, runtime_stub_007515B8_sceVu0RotTransPersN);
    runtime->registerFunction(0x00751678u, runtime_stub_00751678_sceVu0InterVectorXYZ);
    runtime->registerFunction(0x007516C0u, runtime_stub_007516C0_sceVu0ClipScreen);
    runtime->registerFunction(0x00751708u, runtime_stub_00751708_sceVu0ClipScreen3);
    runtime->registerFunction(0x00751768u, runtime_stub_00751768_sceVu0ClipAll);
    runtime->registerFunction(0x007517F8u, runtime_stub_007517F8_sceVpu0Reset);
    runtime->registerFunction(0x00752790u, runtime_stub_00752790_sceMcEnd);
    runtime->registerFunction(0x007527F8u, runtime_stub_007527F8_sceMcChangeThreadPriority);
    runtime->registerFunction(0x007528B8u, runtime_stub_007528B8_sceMcGetSlotMax);
    runtime->registerFunction(0x007534A8u, runtime_stub_007534A8_sceMcChdir);
    runtime->registerFunction(0x007537D8u, runtime_stub_007537D8_sceMcFlush);
    runtime->registerFunction(0x00753BC0u, runtime_stub_00753BC0_sceMcUnformat);
    runtime->registerFunction(0x007545F0u, runtime_stub_007545F0_scePadGetFrameCount);
    runtime->registerFunction(0x00754738u, runtime_stub_00754738_scePadStateIntToStr);
    runtime->registerFunction(0x007549D0u, runtime_stub_007549D0_scePadInfoComb);
    runtime->registerFunction(0x00754E78u, runtime_stub_00754E78_scePadGetButtonMask);
    runtime->registerFunction(0x00755108u, runtime_stub_00755108_scePadSetVrefParam);
    runtime->registerFunction(0x007551D8u, runtime_stub_007551D8_scePadGetPortMax);
    runtime->registerFunction(0x0075E380u, runtime_stub_0075E380_iRotateThreadReadyQueue);
    runtime->registerFunction(0x00760C88u, runtime_stub_00760C88_sceSifGetOtherData);
    runtime->registerFunction(0x00761820u, runtime_stub_00761820_sceSifRpcLoop);
    runtime->registerFunction(0x007630E8u, runtime_stub_007630E8_sceIoctl);
    runtime->registerFunction(0x00765520u, runtime_stub_00765520_sceSifAllocIopHeap);
    runtime->registerFunction(0x00765590u, runtime_stub_00765590_sceSifAllocSysMemory);
    runtime->registerFunction(0x007656A8u, runtime_stub_007656A8_sceSifLoadIopHeap);
    runtime->registerFunction(0x00766550u, runtime_stub_00766550_sceSifLoadElf);
    runtime->registerFunction(0x00766578u, runtime_stub_00766578_sceSifGetIopAddr);
    runtime->registerFunction(0x00766668u, runtime_stub_00766668_sceSifSetIopAddr);
    runtime->registerFunction(0x007668A0u, runtime_stub_007668A0_sceSifIsAliveIop);
    runtime->registerFunction(0x00768CA0u, runtime_stub_00768CA0_sceDeci2Close);
    runtime->registerFunction(0x00768DE8u, runtime_stub_00768DE8_sceDeci2ExReqSend);
    runtime->registerFunction(0x00768E18u, runtime_stub_00768E18_sceDeci2ExLock);
    runtime->registerFunction(0x00768E40u, runtime_stub_00768E40_sceDeci2ExUnLock);
    runtime->registerFunction(0x0090F250u, runtime_stub_0090F250_sceMpegAddBs);
    runtime->registerFunction(0x0090F2D8u, runtime_stub_0090F2D8_sceMpegGetPictureRAW8);
    runtime->registerFunction(0x0090F3E8u, runtime_stub_0090F3E8_sceMpegGetDecodeMode);
    runtime->registerFunction(0x0090F618u, runtime_stub_0090F618_sceMpegGetPictureRAW8xy);
    runtime->registerFunction(0x00918AA0u, runtime_stub_00918AA0_sceCdStSeekF);
    runtime->registerFunction(0x00918AD0u, runtime_stub_00918AD0_sceCdStSeek);
    runtime->registerFunction(0x00918CC0u, runtime_stub_00918CC0_sceCdStPause);
    runtime->registerFunction(0x00918D10u, runtime_stub_00918D10_sceCdStResume);
    runtime->registerFunction(0x00918D68u, runtime_stub_00918D68_sceCdStStat);
    runtime->registerFunction(0x0092AA08u, runtime_stub_0092AA08_sceIpuSync);
    std::cout << "[Stubs] Successfully registered 61 runtime handlers." << std::endl;
}
}
