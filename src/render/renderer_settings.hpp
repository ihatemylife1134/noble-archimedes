#pragma once

#include <filesystem>
#include <string>

namespace NobleArchimedes {

enum class RendererMode { Native, Pcsx2Gs };
struct RendererSettings { RendererMode mode = RendererMode::Native; };

// A saved change takes effect at the next application start.
std::filesystem::path rendererSettingsPath();
RendererSettings loadRendererSettings(const std::filesystem::path& path, std::string* error = nullptr);
bool saveRendererSettings(const std::filesystem::path& path, RendererSettings settings, std::string* error = nullptr);
const char* rendererBackendName(RendererMode mode);
// An explicit nonempty backend is preserved, including existing "cpu" overrides.
const char* resolveRendererBackend(RendererSettings settings, const char* explicitOverride);

} // namespace NobleArchimedes
