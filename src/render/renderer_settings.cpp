#include "renderer_settings.hpp"

#include <atomic>
#include <cstdlib>
#include <fstream>
#include <system_error>
#ifdef _WIN32
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#else
#include <fcntl.h>
#include <unistd.h>
#include <cerrno>
#endif

namespace NobleArchimedes {
namespace {
void report(std::string* error, const std::string& message) { if (error) *error = message; }
constexpr const char* nativeFile = "version=1\nrenderer=native\n";
constexpr const char* hybridFile = "version=1\nrenderer=pcsx2\n";
std::atomic<unsigned long long> sequence{0};
struct TemporaryFile {
    std::filesystem::path path;
    ~TemporaryFile() { if (!path.empty()) { std::error_code ignored; std::filesystem::remove(path, ignored); } }
};
}

std::filesystem::path rendererSettingsPath() {
#ifdef _WIN32
    if (const wchar_t* appData = _wgetenv(L"LOCALAPPDATA"); appData && *appData)
        return std::filesystem::path(appData) / "NobleArchimedes" / "renderer.cfg";
#endif
    return std::filesystem::current_path() / "noble-renderer.cfg";
}

const char* rendererBackendName(RendererMode mode) {
    return mode == RendererMode::Pcsx2Gs ? "pcsx2" : "pgs";
}
const char* resolveRendererBackend(RendererSettings settings, const char* explicitOverride) {
    return explicitOverride && *explicitOverride ? explicitOverride : rendererBackendName(settings.mode);
}

RendererSettings loadRendererSettings(const std::filesystem::path& path, std::string* error) {
    report(error, "");
    std::error_code ec;
    const auto status = std::filesystem::status(path, ec);
    if (ec == std::errc::no_such_file_or_directory || (!ec && !std::filesystem::exists(status))) return {};
    if (ec || !std::filesystem::is_regular_file(status)) {
        report(error, "Cannot read renderer settings: " + (ec ? ec.message() : "not a regular file"));
        return {};
    }
    std::ifstream stream(path, std::ios::binary);
    if (!stream) { report(error, "Cannot open renderer settings"); return {}; }
    char buffer[129];
    stream.read(buffer, sizeof(buffer));
    const auto count = stream.gcount();
    if (stream.bad() || (!stream.eof() && stream.fail())) {
        report(error, "Cannot read renderer settings"); return {};
    }
    const std::string contents(buffer, static_cast<std::size_t>(count));
    if (contents == nativeFile) return {};
    if (contents == hybridFile) return {RendererMode::Pcsx2Gs};
    report(error, "Invalid or truncated renderer settings; using Native");
    return {};
}

bool saveRendererSettings(const std::filesystem::path& path, RendererSettings settings, std::string* error) {
    report(error, "");
    if (settings.mode != RendererMode::Native && settings.mode != RendererMode::Pcsx2Gs) {
        report(error, "Invalid renderer mode"); return false;
    }
    try {
        std::error_code ec;
        const auto parent = path.parent_path();
        if (!parent.empty()) {
            std::filesystem::create_directories(parent, ec);
            if (ec) { report(error, "Cannot create renderer settings directory: " + ec.message()); return false; }
        }
        const std::string contents = settings.mode == RendererMode::Native ? nativeFile : hybridFile;
        TemporaryFile temporary;
#ifdef _WIN32
        HANDLE file = INVALID_HANDLE_VALUE;
        for (unsigned attempt = 0; attempt < 16; ++attempt) {
            auto candidate = path;
            candidate += L".tmp." + std::to_wstring(GetCurrentProcessId()) + L"." + std::to_wstring(sequence.fetch_add(1));
            file = CreateFileW(candidate.c_str(), GENERIC_WRITE, 0, nullptr, CREATE_NEW, FILE_ATTRIBUTE_NORMAL, nullptr);
            if (file != INVALID_HANDLE_VALUE) { temporary.path = std::move(candidate); break; }
            if (GetLastError() != ERROR_FILE_EXISTS && GetLastError() != ERROR_ALREADY_EXISTS) break;
        }
        if (file == INVALID_HANDLE_VALUE) { report(error, "Cannot create temporary renderer settings file (" + std::to_string(GetLastError()) + ")"); return false; }
        DWORD written = 0;
        const bool writeOk = WriteFile(file, contents.data(), static_cast<DWORD>(contents.size()), &written, nullptr) && written == contents.size();
        const bool flushOk = writeOk && FlushFileBuffers(file);
        const bool closeOk = CloseHandle(file);
        if (!writeOk || !flushOk || !closeOk) { report(error, "Cannot write renderer settings"); return false; }
        if (!MoveFileExW(temporary.path.c_str(), path.c_str(), MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH)) {
            report(error, "Cannot replace renderer settings (" + std::to_string(GetLastError()) + ")"); return false;
        }
#else
        int file = -1;
        for (unsigned attempt = 0; attempt < 16; ++attempt) {
            auto candidate = path;
            candidate += ".tmp." + std::to_string(getpid()) + "." + std::to_string(sequence.fetch_add(1));
            file = ::open(candidate.c_str(), O_WRONLY | O_CREAT | O_EXCL, 0600);
            if (file >= 0) { temporary.path = std::move(candidate); break; }
            if (errno != EEXIST) break;
        }
        if (file < 0) { report(error, "Cannot create temporary renderer settings file"); return false; }
        const bool writeOk = ::write(file, contents.data(), contents.size()) == static_cast<ssize_t>(contents.size());
        const bool flushOk = writeOk && ::fsync(file) == 0;
        const bool closeOk = ::close(file) == 0;
        if (!writeOk || !flushOk || !closeOk) { report(error, "Cannot write renderer settings"); return false; }
        std::filesystem::rename(temporary.path, path, ec);
        if (ec) { report(error, "Cannot replace renderer settings: " + ec.message()); return false; }
#endif
        temporary.path.clear();
        return true;
    } catch (const std::exception& e) {
        report(error, "Cannot save renderer settings: " + std::string(e.what()));
        return false;
    }
}
} // namespace NobleArchimedes
