#pragma once

#include <cstdint>
#include <string>
#include <vector>
#include <unordered_map>
#include <fstream>
#include <memory>
#include <mutex>
#include <filesystem>

namespace NobleArchimedes
{

constexpr size_t kIsoSectorSize = 2048;

struct IsoFileEntry
{
    std::string path;
    uint32_t startSector = 0;
    uint64_t sizeBytes = 0;
    bool isDirectory = false;
};

class IsoVfs
{
public:
    IsoVfs();
    ~IsoVfs();

    bool mountIso(const std::filesystem::path& isoPath);
    bool mountExtractedDir(const std::filesystem::path& extractedDir);

    bool hasFile(const std::string& path) const;
    uint64_t getFileSize(const std::string& path) const;
    uint32_t getFileSector(const std::string& path) const;

    // Reads bytes from file (either directly from extracted directory or streamed from ISO)
    int64_t readFile(const std::string& path, uint64_t offset, void* buffer, size_t size);

    // Direct sector read
    bool readSectors(uint32_t startSector, uint32_t sectorCount, void* destination);

    const std::unordered_map<std::string, IsoFileEntry>& getEntries() const { return m_entries; }

private:
    std::string normalizePath(const std::string& path) const;
    bool parseIsoHeader();
    void parseDirectory(uint32_t extentSector, uint32_t dirSize, const std::string& currentPath);

    std::filesystem::path m_isoPath;
    std::filesystem::path m_extractedDir;
    mutable std::ifstream m_isoStream;
    mutable std::mutex m_mutex;
    std::unordered_map<std::string, IsoFileEntry> m_entries;
    bool m_isoMounted = false;
    bool m_extractedMounted = false;
};

} // namespace NobleArchimedes
