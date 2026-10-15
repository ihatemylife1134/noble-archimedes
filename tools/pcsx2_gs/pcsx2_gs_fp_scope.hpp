#pragma once

#include <immintrin.h>

// Runtime-side x64 GCC/Clang boundary. The MSVC-built GS consumer does not
// include this helper: the runtime owns one guard around each complete call.
#if !defined(__x86_64__) || !(defined(__GNUC__) || defined(__clang__))
#error NoblePcsx2GsFpScope requires the x64 GCC/Clang runtime toolchain
#endif

class NoblePcsx2GsFpScope final {
public:
    NoblePcsx2GsFpScope() noexcept {
        _fxsave64(m_original);
        // No pending unmasked caller exception is executed. FNINIT is
        // nonwaiting and gives the external renderer an empty masked stack.
        __asm__ volatile("fninit" ::: "memory", "st", "st(1)", "st(2)", "st(3)",
                         "st(4)", "st(5)", "st(6)", "st(7)");
        _mm_setcsr(0x1f80u);
    }

    ~NoblePcsx2GsFpScope() noexcept {
        __asm__ volatile("fxrstor64 %0" :: "m"(m_original)
            : "memory", "xmm0", "xmm1", "xmm2", "xmm3", "xmm4", "xmm5",
              "xmm6", "xmm7", "xmm8", "xmm9", "xmm10", "xmm11", "xmm12",
              "xmm13", "xmm14", "xmm15", "st", "st(1)", "st(2)", "st(3)",
              "st(4)", "st(5)", "st(6)", "st(7)");
    }

    NoblePcsx2GsFpScope(const NoblePcsx2GsFpScope&) = delete;
    NoblePcsx2GsFpScope& operator=(const NoblePcsx2GsFpScope&) = delete;
    NoblePcsx2GsFpScope(NoblePcsx2GsFpScope&&) = delete;
    NoblePcsx2GsFpScope& operator=(NoblePcsx2GsFpScope&&) = delete;

private:
    alignas(16) unsigned char m_original[512];
};

// FXSAVE64 covers x87 and SSE state, not AVX upper halves. C ABI calls here
// return integer/status/pointer or caller-owned buffers; no floating/XMM return
// is intended to survive the restoration. Actual DLL ABI validation is separate.
