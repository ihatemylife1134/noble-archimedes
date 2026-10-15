#if !__has_include("../src/render/renderer_settings.hpp")
#include <cstdio>
int main() { std::puts("EXPECTED-RED renderer settings feature missing"); return 3; }
#else
#include "../src/render/renderer_settings.hpp"
#include <chrono>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <stdexcept>
#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#endif
using namespace NobleArchimedes;
namespace {
unsigned checks = 0;
void check(bool value, const char* message) {
    ++checks;
    if (!value) throw std::runtime_error(message);
}
void write(const std::filesystem::path& p, const std::string& bytes) {
    std::ofstream f(p, std::ios::binary); f << bytes;
    if (!f) throw std::runtime_error("fixture write failed");
}
std::string read(const std::filesystem::path& p) {
    std::ifstream f(p, std::ios::binary);
    return {std::istreambuf_iterator<char>(f), std::istreambuf_iterator<char>()};
}
}
int main() {
    const auto root = std::filesystem::temp_directory_path() /
        ("noble_renderer_settings_" + std::to_string(std::chrono::steady_clock::now().time_since_epoch().count()));
    std::filesystem::create_directory(root);
    try {
        const auto file = root / "renderer.cfg";
        std::string error = "stale";
        check(loadRendererSettings(file, &error).mode == RendererMode::Native, "missing default");
        check(error.empty(), "missing file should not diagnose");
        check(saveRendererSettings(file, {RendererMode::Pcsx2Gs}, &error), "save hybrid");
        check(error.empty(), "save clears old error");
        check(loadRendererSettings(file, &error).mode == RendererMode::Pcsx2Gs, "hybrid roundtrip");
        check(error.empty(), "valid hybrid error");
        check(read(file) == "version=1\nrenderer=pcsx2\n", "stable hybrid identifier");
        check(saveRendererSettings(file, {}, &error), "replace with native");
        check(loadRendererSettings(file, &error).mode == RendererMode::Native, "native roundtrip");
        check(read(file) == "version=1\nrenderer=native\n", "stable native identifier");
        for (const auto& bad : {std::string(), std::string("version=1\nrenderer=pcsx2"),
             std::string("version=1\nrenderer=bogus\n"), std::string("version=2\nrenderer=native\n"),
             std::string("version=1\n"), std::string("version=1\nrenderer=native\nextra\n"),
             std::string(5000, 'x'), std::string("version=1\nrenderer=nat") + '\0' + "ive\n"}) {
            write(file, bad);
            check(loadRendererSettings(file, &error).mode == RendererMode::Native, "invalid native default");
            check(!error.empty(), "invalid/truncated diagnosis");
        }
        check(saveRendererSettings(file, {RendererMode::Pcsx2Gs}, &error), "restore existing config");
        const auto old = read(file);
        check(!saveRendererSettings(file, {static_cast<RendererMode>(99)}, &error), "invalid enum rejected");
        check(!error.empty() && read(file) == old, "invalid enum preserves old");
#ifdef _WIN32
        HANDLE lock = CreateFileW(file.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
        check(lock != INVALID_HANDLE_VALUE, "fixture exclusive replacement lock");
        const bool saved = saveRendererSettings(file, {}, &error);
        CloseHandle(lock);
        check(!saved && !error.empty(), "unwritable replacement diagnosed");
        check(read(file) == old, "failed atomic replacement preserves old bytes");
#endif
        check(saveRendererSettings(root / "created" / "nested" / "renderer.cfg", {}, &error), "parent directories created");
        check(loadRendererSettings(root / "created" / "nested" / "renderer.cfg", &error).mode == RendererMode::Native && error.empty(), "created parent roundtrip");
        check(!saveRendererSettings(file / "child.cfg", {}, &error), "file cannot be parent directory");
        check(!error.empty() && read(file) == old, "invalid parent diagnosis preserves old file");
        check(loadRendererSettings(root, &error).mode == RendererMode::Native && !error.empty(), "directory load diagnosis");
        check(std::string(rendererBackendName(RendererMode::Native)) == "pgs", "native backend");
        check(std::string(rendererBackendName(RendererMode::Pcsx2Gs)) == "pcsx2", "hybrid backend");
        for (const char* backend : {"pgs", "cpu", "pcsx2", "future-backend"})
            check(std::string(resolveRendererBackend({}, backend)) == backend, "explicit override precedence");
        check(std::string(resolveRendererBackend({RendererMode::Pcsx2Gs}, nullptr)) == "pcsx2", "saved hybrid without override");
        check(std::string(resolveRendererBackend({}, "")) == "pgs", "empty override default");
#ifdef _WIN32
        const char* previous = std::getenv("LOCALAPPDATA");
        const bool existed = previous != nullptr;
        const std::string previousValue = previous ? previous : "";
        const auto configuredRoot = root / "user-appdata";
        _putenv_s("LOCALAPPDATA", configuredRoot.string().c_str());
        const auto configuredPath = rendererSettingsPath();
        _putenv_s("LOCALAPPDATA", "");
        const auto fallbackPath = rendererSettingsPath();
        _putenv_s("LOCALAPPDATA", existed ? previousValue.c_str() : "");
        check(configuredPath == configuredRoot / "NobleArchimedes" / "renderer.cfg", "LOCALAPPDATA settings path");
        check(fallbackPath == std::filesystem::current_path() / "noble-renderer.cfg", "empty LOCALAPPDATA fallback path");
        const wchar_t* priorWide = _wgetenv(L"LOCALAPPDATA");
        const std::wstring priorWideValue = priorWide ? priorWide : L"";
        const auto unicodeRoot = root / L"appdata_\u6e2c\u8a66";
        _wputenv_s(L"LOCALAPPDATA", unicodeRoot.c_str());
        const auto unicodeSettings = rendererSettingsPath();
        _wputenv_s(L"LOCALAPPDATA", priorWideValue.c_str());
        check(unicodeSettings == unicodeRoot / "NobleArchimedes" / "renderer.cfg", "Unicode LOCALAPPDATA path");
#endif
        check(saveRendererSettings(root / L"config_\u00e9.cfg", {}, nullptr), "unicode path save");
        check(loadRendererSettings(root / L"config_\u00e9.cfg", nullptr).mode == RendererMode::Native, "unicode path load");
        unsigned files = 0;
        for (const auto& entry : std::filesystem::directory_iterator(root)) {
            if (entry.is_directory()) continue;
            ++files;
            check(entry.path().extension() == ".cfg", "temporary files cleaned after failed replacement");
        }
        check(files == 2, "only persisted configuration files remain");
        std::filesystem::remove_all(root);
        std::cout << "GREEN renderer settings real-filesystem checks=" << checks << '\n';
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "FAIL " << e.what() << '\n';
        std::filesystem::remove_all(root);
        return 2;
    }
}
#endif
