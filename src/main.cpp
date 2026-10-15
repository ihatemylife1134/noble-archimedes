/**
 * Noble Archimedes - Castlevania: Curse of Darkness Native Windows Recompilation
 * 
 * Main host application entry point:
 * - Initializes the high-performance native PS2 runtime
 * - Configures windowing, modern controls, and render backend
 * - Mounts VFS and ISO streaming for instant asset loading
 * - Hooks modern 2026 camera (Action Orbit & Resident Evil 2 Remake OTS)
 * - Executes native x86_64 game logic loop
 */

#include <iostream>
#include <string>
#include <filesystem>
#include <exception>
#include <cstdlib>

#include "ps2_runtime.h"
#include "runtime/ee_scheduler.h"
#include "runtime/ps2_async_stdio.h"
#include "camera/camera_controller.hpp"
#include "input/input_manager.hpp"
#include "ui/modern_overlay.hpp"
#include "vfs/iso_vfs.hpp"
#include "recomp/runtime_stub_registry.hpp"
#include "render/renderer_settings.hpp"
#include "platform/host_timer_resolution.hpp"
#include "Stubs/CD.h"
#include "raylib.h"

// Forward declaration from Pad stub in runtime
namespace ps2_stubs
{
    void setPadOverrideState(uint16_t buttons, uint8_t lx, uint8_t ly, uint8_t rx, uint8_t ry);
    void clearPadOverrideState();
}

// Defined in generated register_functions.o
extern void registerRecompiledFunctions(PS2Runtime *runtime);

struct NobleAppContext
{
    NobleArchimedes::CameraController camera;
    NobleArchimedes::InputManager input;
    NobleArchimedes::ModernOverlay overlay;
    NobleArchimedes::IsoVfs vfs;
};

#ifdef _WIN32
extern "C" {
__declspec(dllimport) unsigned long __stdcall GetModuleFileNameA(void* hModule, char* lpFilename, unsigned long nSize);
__declspec(dllimport) unsigned int __stdcall timeBeginPeriod(unsigned int uPeriod);
__declspec(dllimport) unsigned int __stdcall timeEndPeriod(unsigned int uPeriod);
}

struct ScopedTimerResolution
{
    ScopedTimerResolution()
    {
        timeBeginPeriod(1);
        NobleArchimedes::honorHostTimerResolution();
    }
    ~ScopedTimerResolution() { timeEndPeriod(1); }
};
#endif

static void configureDefaultMemoryCardMode()
{
    const char *mode = std::getenv("PS2_MC_MODE");
    if (mode && *mode)
    {
        return;
    }

#ifdef _WIN32
    _putenv_s("PS2_MC_MODE", "none");
#else
    setenv("PS2_MC_MODE", "none", 0);
#endif
}

static void configureDefaultRendererWorkers()
{
    const char *workers = std::getenv("PS2_GS_THREADS");
    if (workers && *workers)
        return;
    // This game's many small menu draws spend more time coordinating eight
    // workers than rasterizing. Two workers measured faster on the menu and
    // retain parallel drawing; keep explicit user settings authoritative.
#ifdef _WIN32
    _putenv_s("PS2_GS_THREADS", "2");
#else
    setenv("PS2_GS_THREADS", "2", 0);
#endif
}

static bool configureRendererSettings()
{
    std::string error;
    const auto settings = NobleArchimedes::loadRendererSettings(
        NobleArchimedes::rendererSettingsPath(), &error);
    if (!error.empty())
        std::cerr << "[Renderer] " << error << "; using the native default." << std::endl;

    const char *overrideBackend = std::getenv("PS2_GS_BACKEND");
    const std::string backend = NobleArchimedes::resolveRendererBackend(settings, overrideBackend);
    if (!overrideBackend || !*overrideBackend)
    {
#ifdef _WIN32
        if (_putenv_s("PS2_GS_BACKEND", backend.c_str()) != 0)
#else
        if (setenv("PS2_GS_BACKEND", backend.c_str(), 1) != 0)
#endif
        {
            std::cerr << "[Renderer] Could not apply the selected backend." << std::endl;
            return false;
        }
    }
    std::cout << "[Renderer] Selected backend: " << backend << std::endl;
#if !defined(NOBLE_HAVE_PCSX2_GS) || !NOBLE_HAVE_PCSX2_GS
    if (backend == "pcsx2")
    {
        std::cerr << "[Renderer] PCSX2 GS adapter is unavailable in this build. "
                     "Select Native or use a build containing the GS adapter." << std::endl;
        return false;
    }
#endif
    return true;
}

int main(int argc, char *argv[])
{
#ifdef _WIN32
    ScopedTimerResolution timerResolution;
    char exePathBuf[1024] = {0};
    if (GetModuleFileNameA(nullptr, exePathBuf, sizeof(exePathBuf)) > 0) {
        std::filesystem::path fullExePath(exePathBuf);
        if (fullExePath.has_parent_path()) {
            std::filesystem::current_path(fullExePath.parent_path());
        }
    }
#endif

    setvbuf(stdout, nullptr, _IONBF, 0);
    setvbuf(stderr, nullptr, _IONBF, 0);
    std::cout.setf(std::ios::unitbuf);
    std::cerr.setf(std::ios::unitbuf);
    // Unbuffered writes go to an in-process relay, so a slow or paused
    // console/log file never stalls the emulation thread (PS2_SYNC_STDIO=1 disables).
    ps2_async_stdio::install();
    configureDefaultMemoryCardMode();
    configureDefaultRendererWorkers();
    if (!configureRendererSettings())
        return 1;

    std::cout << "=======================================================\n";
    std::cout << "  Noble Archimedes - Castlevania: Curse of Darkness   \n";
    std::cout << "       Native Windows 64-bit Recompilation (2026)      \n";
    std::cout << "=======================================================\n" << std::endl;

    std::filesystem::path elfPath = "extracted/SLUS_211.68";
    if (argc > 1) {
        elfPath = argv[1];
    }

    if (!std::filesystem::exists(elfPath)) {
        std::cerr << "[Error] Target game binary not found at: " << elfPath << std::endl;
        std::cerr << "Please ensure extracted/SLUS_211.68 is present or provide path as argument." << std::endl;
        return 1;
    }

    const std::string windowTitle = "Noble Archimedes: Castlevania - Curse of Darkness (NTSC-U) [2026 Modern Recomp]";

    try
    {
        NobleAppContext app;

        // 1. Mount virtual file systems
        std::cout << "[VFS] Mounting disk assets from extracted/..." << std::endl;
        app.vfs.mountExtractedDir("extracted");

        const std::filesystem::path isoFile = "Castlevania - Curse of Darkness (USA).iso";
        if (std::filesystem::exists(isoFile))
        {
            std::cout << "[VFS] Mounting disc stream from " << isoFile.string() << "..." << std::endl;
            if (app.vfs.mountIso(isoFile))
            {
                std::vector<ps2_stubs::CdImageFileEntry> cdEntries;
                cdEntries.reserve(app.vfs.getEntries().size());
                for (const auto &[path, entry] : app.vfs.getEntries())
                {
                    if (!entry.isDirectory)
                        cdEntries.push_back({path, entry.startSector, entry.sizeBytes});
                }
                ps2_stubs::configureCdImageIndex(isoFile, cdEntries);
                std::cout << "[VFS] Connected " << cdEntries.size()
                          << " ISO files to the native CD runtime." << std::endl;
            }
        }

        PS2Runtime runtime;

        // 2. Configure 2026 Modern Controls & Overlay Callbacks
        runtime.setDebugUiCallbacks(
            [](PS2Runtime &rt, void *userData) {
                (void)rt;
                auto *ctx = static_cast<NobleAppContext *>(userData);
                ctx->overlay.initialize();
                std::cout << "[Input/Camera] Classic PS2 camera selected by default." << std::endl;
                std::cout << "  -> Action Orbit / Over-The-Shoulder can be selected with the camera controls." << std::endl;
            },
            [](PS2Runtime &rt, void *userData) {
                auto *ctx = static_cast<NobleAppContext *>(userData);
                float dt = GetFrameTime();
                if (dt <= 0.0f || dt > 0.1f) dt = 1.0f / 60.0f;

                // Poll input and update camera
                ctx->input.update(dt, ctx->camera);
                const auto &st = ctx->input.getState();

                // Inject modern control state directly into guest PS2 pad read pipeline.
                // Automated captures can drive the lower-level pad stub through PS2_PAD_SCRIPT.
                static const bool scriptedPadInput = [] {
                    const char *value = std::getenv("PS2_PAD_SCRIPT");
                    return value && *value && std::string(value) != "0";
                }();
                if (!scriptedPadInput)
                {
                    ps2_stubs::setPadOverrideState(
                        st.ps2Buttons,
                        st.ps2LeftStickX,
                        st.ps2LeftStickY,
                        st.ps2RightStickX,
                        st.ps2RightStickY
                    );
                }

                // Check for movie skip when Start / Escape / Enter is pressed
                if ((st.ps2Buttons & NobleArchimedes::PAD_START) == 0) {
                    const uint32_t movieBase = rt.memory().read32(0x009B7B70u);
                    if (movieBase != 0 && (movieBase & 3) == 0 && movieBase < (PS2_RAM_SIZE - 0x69200u)) {
                        rt.memory().write32(movieBase + 0x690B8u + 0x60u, 1);
                        rt.memory().write32(movieBase + 0x69414u, 1);
                    }
                }

                // Render 2026 Enhanced HUD & UI
                ctx->overlay.draw(rt, ctx->camera, ctx->input);

                static int s_frameCount = 0;
                static const bool kernelDiagnostics = [] {
                    const char *value = std::getenv("PS2_KERNEL_DIAGNOSTICS");
                    return value && *value && std::string(value) != "0";
                }();
                ++s_frameCount;
                if (kernelDiagnostics && s_frameCount % 60 == 1) {
                    const auto snapshot = rt.eeScheduler().snapshot();
                    const auto &gs = rt.memory().gs();
                    std::cout << "[Kernel Diag] Frame=" << s_frameCount
                              << " RunningThread=" << snapshot.runningThreadId
                              << " TotalThreads=" << snapshot.threads.size()
                              << " dispfb1=0x" << std::hex << gs.dispfb1
                              << " display1=0x" << gs.display1
                              << " pmode=0x" << gs.pmode
                              << " smode2=0x" << gs.smode2
                              << std::dec
                              << " dmaStart=" << rt.memory().dmaStartCount()
                              << " gifCopy=" << rt.memory().gifCopyCount()
                              << " gsWrite=" << rt.memory().gsWriteCount()
                              << " vifWrite=" << rt.memory().vifWriteCount()
                              << std::endl;
                    for (const auto &th : snapshot.threads) {
                        std::cout << "  Thread id=" << th.id
                                  << " status=" << static_cast<int>(th.status)
                                  << " pc=0x" << std::hex << th.pc
                                  << " ra=0x" << th.ra
                                  << " sp=0x" << th.sp
                                  << std::dec
                                  << " waitReason=" << static_cast<int>(th.waitReason)
                                  << " waitId=" << th.waitId
                                  << std::endl;
                    }
                }

                // PNG readback/encoding is a diagnostic operation; doing it
                // every second stalls input and presentation during normal play.
                static const bool captureFrames = [] {
                    const char *value = std::getenv("NOBLE_FRAME_CAPTURE");
                    return value && *value && std::string(value) != "0";
                }();
                if (captureFrames && (s_frameCount == 30 || s_frameCount % 60 == 0)) {
                    TakeScreenshot("noble_archimedes_preview.png");
                    if (s_frameCount <= 1200 && s_frameCount % 300 == 0) {
                        std::string framePath = "noble_archimedes_frame_" + std::to_string(s_frameCount) + ".png";
                        TakeScreenshot(framePath.c_str());
                    }
                }
            },
            [](PS2Runtime &rt, void *userData) {
                (void)rt;
                auto *ctx = static_cast<NobleAppContext *>(userData);
                ctx->overlay.shutdown();
                ps2_stubs::clearPadOverrideState();
            },
            &app
        );

        // 3. Initialize Runtime Window & Render Subsystems
        std::cout << "[Init] Initializing native PS2 runtime & window subsystem..." << std::endl;
        if (!runtime.initialize(windowTitle.c_str()))
        {
            std::cerr << "[Fatal] Failed to initialize PS2 runtime window/graphics backend." << std::endl;
            return 1;
        }

        // 4. Register Recompiled MIPS Functions & Runtime Stubs
        std::cout << "[Init] Registering recompiled guest functions..." << std::endl;
        registerRecompiledFunctions(&runtime);
        NobleArchimedes::registerAllRuntimeStubs(&runtime);
        runtime.setMissingFunctionPolicy(PS2Runtime::MissingFunctionPolicy::SkipCallDebug);

        // 5. Load ELF binary
        std::cout << "[Init] Loading ELF binary: " << elfPath.string() << std::endl;
        if (!runtime.loadELF(elfPath.string()))
        {
            std::cerr << "[Fatal] Failed to load guest ELF headers into memory." << std::endl;
            return 1;
        }

        // 6. Run Native Game Logic Loop
        std::cout << "[Run] Starting native execution loop..." << std::endl;
        runtime.run();

        std::cout << "[Exit] Shutting down cleanly." << std::endl;
        return 0;
    }
    catch (const std::exception &e)
    {
        std::cerr << "[Fatal Exception] " << e.what() << std::endl;
        return 1;
    }
    catch (...)
    {
        std::cerr << "[Fatal Exception] Unknown unhandled exception occurred." << std::endl;
        return 1;
    }
}
