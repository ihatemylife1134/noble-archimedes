#include "runtime_stub_registry.hpp"
#include "ps2_runtime.h"
#include <iostream>

// Forward declare runtime stubs
namespace ps2_stubs {
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

namespace NobleArchimedes {
void registerAllRuntimeStubs(PS2Runtime *runtime) {
    std::cout << "[Stubs] Registering 60 Sony SDK runtime stubs into function table..." << std::endl;
    runtime->registerFunction(0x0074BE30u, ps2_stubs::sceSdTransToIOP);
    runtime->registerFunction(0x0074DFC0u, ps2_stubs::sceCdSeek);
    runtime->registerFunction(0x0074E090u, ps2_stubs::sceCdStandby);
    runtime->registerFunction(0x0074E140u, ps2_stubs::sceCdStop);
    runtime->registerFunction(0x0074F588u, ps2_stubs::sceGsSyncVCallback);
    runtime->registerFunction(0x0074FD10u, ps2_stubs::sceDmaGetEnv);
    runtime->registerFunction(0x0074FE40u, ps2_stubs::sceDmaSendI);
    runtime->registerFunction(0x0074FEB8u, ps2_stubs::sceDmaRecv);
    runtime->registerFunction(0x0074FF00u, ps2_stubs::sceDmaRecvN);
    runtime->registerFunction(0x0074FF80u, ps2_stubs::sceDmaRecvI);
    runtime->registerFunction(0x00750038u, ps2_stubs::sceDmaWatch);
    runtime->registerFunction(0x00750CC8u, ps2_stubs::sceVu0DivVector);
    runtime->registerFunction(0x00750CE8u, ps2_stubs::sceVu0DivVectorXYZ);
    runtime->registerFunction(0x00751148u, ps2_stubs::sceVu0CameraMatrix);
    runtime->registerFunction(0x007511F8u, ps2_stubs::sceVu0NormalLightMatrix);
    runtime->registerFunction(0x007512B8u, ps2_stubs::sceVu0LightColorMatrix);
    runtime->registerFunction(0x00751428u, ps2_stubs::sceVu0DropShadowMatrix);
    runtime->registerFunction(0x007515B8u, ps2_stubs::sceVu0RotTransPersN);
    runtime->registerFunction(0x00751678u, ps2_stubs::sceVu0InterVectorXYZ);
    runtime->registerFunction(0x007516C0u, ps2_stubs::sceVu0ClipScreen);
    runtime->registerFunction(0x00751708u, ps2_stubs::sceVu0ClipScreen3);
    runtime->registerFunction(0x00751768u, ps2_stubs::sceVu0ClipAll);
    runtime->registerFunction(0x007517F8u, ps2_stubs::sceVpu0Reset);
    runtime->registerFunction(0x00752790u, ps2_stubs::sceMcEnd);
    runtime->registerFunction(0x007527F8u, ps2_stubs::sceMcChangeThreadPriority);
    runtime->registerFunction(0x007528B8u, ps2_stubs::sceMcGetSlotMax);
    runtime->registerFunction(0x007534A8u, ps2_stubs::sceMcChdir);
    runtime->registerFunction(0x007537D8u, ps2_stubs::sceMcFlush);
    runtime->registerFunction(0x00753BC0u, ps2_stubs::sceMcUnformat);
    runtime->registerFunction(0x007545F0u, ps2_stubs::scePadGetFrameCount);
    runtime->registerFunction(0x00754738u, ps2_stubs::scePadStateIntToStr);
    runtime->registerFunction(0x007549D0u, ps2_stubs::scePadInfoComb);
    runtime->registerFunction(0x00754E78u, ps2_stubs::scePadGetButtonMask);
    runtime->registerFunction(0x00755108u, ps2_stubs::scePadSetVrefParam);
    runtime->registerFunction(0x007551D8u, ps2_stubs::scePadGetPortMax);
    runtime->registerFunction(0x0075E380u, ps2_syscalls::iRotateThreadReadyQueue);
    runtime->registerFunction(0x00760C88u, ps2_stubs::sceSifGetOtherData);
    runtime->registerFunction(0x00761820u, ps2_stubs::sceSifRpcLoop);
    runtime->registerFunction(0x007630E8u, ps2_stubs::sceIoctl);
    runtime->registerFunction(0x00765520u, ps2_stubs::sceSifAllocIopHeap);
    runtime->registerFunction(0x00765590u, ps2_stubs::sceSifAllocSysMemory);
    runtime->registerFunction(0x007656A8u, ps2_stubs::sceSifLoadIopHeap);
    runtime->registerFunction(0x00766550u, ps2_stubs::sceSifLoadElf);
    runtime->registerFunction(0x00766578u, ps2_stubs::sceSifGetIopAddr);
    runtime->registerFunction(0x00766668u, ps2_stubs::sceSifSetIopAddr);
    runtime->registerFunction(0x007668A0u, ps2_stubs::sceSifIsAliveIop);
    runtime->registerFunction(0x00768CA0u, ps2_stubs::sceDeci2Close);
    runtime->registerFunction(0x00768DE8u, ps2_stubs::sceDeci2ExReqSend);
    runtime->registerFunction(0x00768E18u, ps2_stubs::sceDeci2ExLock);
    runtime->registerFunction(0x00768E40u, ps2_stubs::sceDeci2ExUnLock);
    // Real MPEG and IPU functions are compiled into the game ELF between 0x90E5F0 and 0x92B5A0.
    // Do not override them with dummy stubs.
    runtime->registerFunction(0x00918AA0u, ps2_stubs::sceCdStSeekF);
    runtime->registerFunction(0x00918AD0u, ps2_stubs::sceCdStSeek);
    runtime->registerFunction(0x00918CC0u, ps2_stubs::sceCdStPause);
    runtime->registerFunction(0x00918D10u, ps2_stubs::sceCdStResume);
    runtime->registerFunction(0x00918D68u, ps2_stubs::sceCdStStat);
    std::cout << "[Stubs] Successfully registered runtime handlers." << std::endl;
}
}
