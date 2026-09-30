#include "iso_vfs.hpp"
#include <iostream>
#include <algorithm>
#include <cstring>

namespace NobleArchimedes
{

IsoVfs::IsoVfs() = default;

IsoVfs::~IsoVfs()
{
    if (m_isoStream.is_open())
    {
        m_isoStream.close();
    }
}

std::string IsoVfs::normalizePath(const std::string& path) const
{
    std::string norm = path;
    std::replace(norm.begin(), norm.end(), '\\', '/');
    while (!norm.empty() && norm.front() == '/')
    {
        norm.erase(norm.begin());
    }
    // Remove ";1" version postfix if present
    auto semicolon = norm.find(';');
    if (semicolon != std::string::npos)
    {
        norm = norm.substr(0, semicolon);
    }
    std::transform(norm.begin(), norm.end(), norm.begin(), ::toupper);
    return norm;
}

bool IsoVfs::mountIso(const std::filesystem::path& isoPath)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_isoPath = isoPath;
    if (m_isoStream.is_open())
    {
        m_isoStream.close();
    }

    m_isoStream.open(m_isoPath, std::ios::binary);
    if (!m_isoStream.is_open())
    {
        std::cerr << "[IsoVfs] Failed to open ISO image at: " << m_isoPath << std::endl;
        return false;
    }

    m_isoMounted = parseIsoHeader();
    return m_isoMounted;
}

bool IsoVfs::mountExtractedDir(const std::filesystem::path& extractedDir)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    m_extractedDir = extractedDir;
    m_extractedMounted = std::filesystem::exists(m_extractedDir) && std::filesystem::is_directory(m_extractedDir);
    return m_extractedMounted;
}

bool IsoVfs::parseIsoHeader()
{
    // Sector 16 is Primary Volume Descriptor
    m_isoStream.seekg(16 * kIsoSectorSize, std::ios::beg);
    uint8_t pvd[kIsoSectorSize];
    m_isoStream.read(reinterpret_cast<char*>(pvd), sizeof(pvd));
    if (m_isoStream.gcount() != sizeof(pvd))
    {
        return false;
    }

    // Verify "CD001" signature
    if (std::memcmp(&pvd[1], "CD001", 5) != 0)
    {
        std::cerr << "[IsoVfs] Invalid ISO9660 signature in " << m_isoPath << std::endl;
        return false;
    }

    // Root directory record is at byte offset 156 (0x9C) in PVD
    const uint8_t* rootRecord = &pvd[156];
    uint32_t rootExtent = *reinterpret_cast<const uint32_t*>(&rootRecord[2]);
    uint32_t rootSize = *reinterpret_cast<const uint32_t*>(&rootRecord[10]);

    m_entries.clear();
    parseDirectory(rootExtent, rootSize, "");
    std::cout << "[IsoVfs] Successfully indexed " << m_entries.size() << " files and directories from ISO." << std::endl;
    return true;
}

void IsoVfs::parseDirectory(uint32_t extentSector, uint32_t dirSize, const std::string& currentPath)
{
    std::vector<uint8_t> buffer(dirSize);
    m_isoStream.seekg(static_cast<uint64_t>(extentSector) * kIsoSectorSize, std::ios::beg);
    m_isoStream.read(reinterpret_cast<char*>(buffer.data()), dirSize);

    size_t offset = 0;
    while (offset < dirSize)
    {
        uint8_t len = buffer[offset];
        if (len == 0)
        {
            // Advance to next sector boundary
            offset = ((offset / kIsoSectorSize) + 1) * kIsoSectorSize;
            continue;
        }

        if (offset + len > dirSize)
            break;

        const uint8_t* record = &buffer[offset];
        uint32_t fileExtent = *reinterpret_cast<const uint32_t*>(&record[2]);
        uint32_t fileSize = *reinterpret_cast<const uint32_t*>(&record[10]);
        uint8_t flags = record[25];
        uint8_t nameLen = record[32];

        std::string rawName(reinterpret_cast<const char*>(&record[33]), nameLen);
        offset += len;

        // Skip '.' (0x00) and '..' (0x01)
        if (rawName.empty() || rawName[0] == 0x00 || rawName[0] == 0x01)
            continue;

        auto semi = rawName.find(';');
        if (semi != std::string::npos)
            rawName = rawName.substr(0, semi);

        std::string fullPath = currentPath.empty() ? rawName : (currentPath + "/" + rawName);
        std::string normPath = normalizePath(fullPath);
        bool isDir = (flags & 2) != 0;

        IsoFileEntry entry;
        entry.path = normPath;
        entry.startSector = fileExtent;
        entry.sizeBytes = fileSize;
        entry.isDirectory = isDir;
        m_entries[normPath] = entry;

        if (isDir)
        {
            parseDirectory(fileExtent, fileSize, fullPath);
        }
    }
}

bool IsoVfs::hasFile(const std::string& path) const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    std::string norm = normalizePath(path);

    if (m_extractedMounted)
    {
        std::filesystem::path local = m_extractedDir / norm;
        if (std::filesystem::exists(local))
            return true;
    }

    return m_entries.find(norm) != m_entries.end();
}

uint64_t IsoVfs::getFileSize(const std::string& path) const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    std::string norm = normalizePath(path);

    if (m_extractedMounted)
    {
        std::filesystem::path local = m_extractedDir / norm;
        if (std::filesystem::exists(local))
        {
            return std::filesystem::file_size(local);
        }
    }

    auto it = m_entries.find(norm);
    if (it != m_entries.end())
    {
        return it->second.sizeBytes;
    }
    return 0;
}

uint32_t IsoVfs::getFileSector(const std::string& path) const
{
    std::lock_guard<std::mutex> lock(m_mutex);
    std::string norm = normalizePath(path);
    auto it = m_entries.find(norm);
    if (it != m_entries.end())
    {
        return it->second.startSector;
    }
    return 0;
}

int64_t IsoVfs::readFile(const std::string& path, uint64_t offset, void* buffer, size_t size)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    std::string norm = normalizePath(path);

    // Fast path: try extracted directory on disk first
    if (m_extractedMounted)
    {
        std::filesystem::path local = m_extractedDir / norm;
        if (std::filesystem::exists(local))
        {
            std::ifstream file(local, std::ios::binary);
            if (file.is_open())
            {
                file.seekg(static_cast<std::streamoff>(offset), std::ios::beg);
                file.read(reinterpret_cast<char*>(buffer), size);
                return file.gcount();
            }
        }
    }

    // Direct ISO stream fallback
    if (!m_isoMounted || !m_isoStream.is_open())
    {
        return -1;
    }

    auto it = m_entries.find(norm);
    if (it == m_entries.end() || it->second.isDirectory)
    {
        return -1;
    }

    const auto& entry = it->second;
    if (offset >= entry.sizeBytes)
    {
        return 0;
    }

    size_t toRead = static_cast<size_t>(std::min<uint64_t>(size, entry.sizeBytes - offset));
    uint64_t bytePos = static_cast<uint64_t>(entry.startSector) * kIsoSectorSize + offset;
    m_isoStream.seekg(static_cast<std::streamoff>(bytePos), std::ios::beg);
    m_isoStream.read(reinterpret_cast<char*>(buffer), toRead);
    return m_isoStream.gcount();
}

bool IsoVfs::readSectors(uint32_t startSector, uint32_t sectorCount, void* destination)
{
    std::lock_guard<std::mutex> lock(m_mutex);
    if (!m_isoMounted || !m_isoStream.is_open())
    {
        return false;
    }

    uint64_t bytePos = static_cast<uint64_t>(startSector) * kIsoSectorSize;
    size_t totalBytes = static_cast<size_t>(sectorCount) * kIsoSectorSize;
    m_isoStream.seekg(static_cast<std::streamoff>(bytePos), std::ios::beg);
    m_isoStream.read(reinterpret_cast<char*>(destination), totalBytes);
    return m_isoStream.gcount() == static_cast<std::streamsize>(totalBytes);
}

} // namespace NobleArchimedes
