#pragma once
/* Private consumer API for actual PCSX2 GS. No C++ ABI/allocator crosses DLL. */
#include <stdint.h>
#if defined(_WIN32)
#define NOBLE_GS_CALL __cdecl
#else
#define NOBLE_GS_CALL
#endif
#ifdef __cplusplus
extern "C" {
#endif
#define NOBLE_PCSX2_GS_ABI_VERSION 1u
typedef void* NoblePcsx2GsInstance;
enum NoblePcsx2GsStatus {
 NOBLE_GS_OK=0, NOBLE_GS_INVALID_ARGUMENT=1, NOBLE_GS_ABI_MISMATCH=2,
 NOBLE_GS_UNAVAILABLE=3, NOBLE_GS_ALREADY_OPEN=4, NOBLE_GS_BUFFER_TOO_SMALL=5,
 NOBLE_GS_INTERNAL_ERROR=6, NOBLE_GS_UNSUPPORTED=7
};
enum NoblePcsx2GsRenderer { NOBLE_GS_D3D11_SURFACELESS=1 };
typedef struct NoblePcsx2GsConfig {
 uint32_t size,renderer,width,height;
 const char* resources_utf8;
 uint32_t flags,reserved;
} NoblePcsx2GsConfig;
typedef struct NoblePcsx2GsPrivRegs {
 uint64_t pmode,smode1,smode2,srfsh,synch1,synch2,syncv;
 uint64_t dispfb1,display1,dispfb2,display2,extbuf,extdata,extwrite,bgcolor;
 uint64_t csr,imr,busdir,siglblid;
} NoblePcsx2GsPrivRegs;
typedef struct NoblePcsx2GsFrame {
 uint32_t size,width,height,stride_bytes;
 uint64_t required_bytes;
} NoblePcsx2GsFrame;
typedef struct NoblePcsx2GsApi {
 uint32_t size,version;
 const char* (NOBLE_GS_CALL *identity)(void); /* DLL-owned immutable UTF-8. */
 int32_t (NOBLE_GS_CALL *last_error)(char*,uint32_t);
 int32_t (NOBLE_GS_CALL *open)(const NoblePcsx2GsConfig*,NoblePcsx2GsInstance*);
 int32_t (NOBLE_GS_CALL *close)(NoblePcsx2GsInstance);
 int32_t (NOBLE_GS_CALL *reset)(NoblePcsx2GsInstance);
 /* Runtime path numbering1/2/3. Any byte span copied; preserve fragments. */
 int32_t (NOBLE_GS_CALL *raw_gif)(NoblePcsx2GsInstance,uint32_t,const uint8_t*,uint32_t);
 int32_t (NOBLE_GS_CALL *write_register)(NoblePcsx2GsInstance,uint32_t,uint64_t);
 int32_t (NOBLE_GS_CALL *image)(NoblePcsx2GsInstance,const uint8_t*,uint32_t);
 int32_t (NOBLE_GS_CALL *privileged)(NoblePcsx2GsInstance,const NoblePcsx2GsPrivRegs*);
 int32_t (NOBLE_GS_CALL *flush)(NoblePcsx2GsInstance);
 /* byte count must be a multiple16; caller owns destination. */
 int32_t (NOBLE_GS_CALL *read_fifo)(NoblePcsx2GsInstance,uint8_t*,uint32_t);
 int32_t (NOBLE_GS_CALL *vsync)(NoblePcsx2GsInstance,uint32_t,uint32_t);
 /* RGBA8 packed rows. NULL buffer queries required capacity, no ownership transfer. */
 int32_t (NOBLE_GS_CALL *rgba)(NoblePcsx2GsInstance,uint32_t,uint32_t,uint8_t*,uint64_t,NoblePcsx2GsFrame*);
 int32_t (NOBLE_GS_CALL *read_vram)(NoblePcsx2GsInstance,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t*);
 int32_t (NOBLE_GS_CALL *write_vram)(NoblePcsx2GsInstance,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t);
 int32_t (NOBLE_GS_CALL *snapshot_vram)(NoblePcsx2GsInstance,uint8_t*,uint32_t);
} NoblePcsx2GsApi;
typedef int32_t (NOBLE_GS_CALL *NoblePcsx2GsQueryApi)(uint32_t,uint32_t,NoblePcsx2GsApi*);
/* Exact exported name: noble_pcsx2_gs_query_api. One process-global GS instance.
   Caller supplies clean masked FP environment and restores guest FP state.
   Calls are synchronous; the module retains no caller data/buffer pointers. */
#ifdef __cplusplus
}
#endif
