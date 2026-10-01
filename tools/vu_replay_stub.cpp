// Offline replay dependencies only. Never link this file into the runtime.
// Register/data/pipeline execution remains the selected production VU sources;
// the replay compares every call's bits, cycles, and ordered PATH1 packets.
#include "runtime/ps2_memory.h"
#include "runtime/gs/gs_frontend.h"
#include "runtime/gs/ps2_gif_arbiter.h"

#include <cstring>
#include <cstdlib>
#include <stdexcept>

PS2Memory::PS2Memory()
    : m_rdram(nullptr), m_scratchpad(nullptr), iop_ram(nullptr),
      m_seenGifCopy(false), m_gsVRAM(nullptr)
{
}

PS2Memory::~PS2Memory()
{
    delete[] m_vu0Code;
    delete[] m_vu0Data;
    delete[] m_vu1Code;
    delete[] m_vu1Data;
}

bool PS2Memory::initialize(size_t)
{
    if (m_vu1Code)
        throw std::runtime_error("minimal VU memory may initialize only once");
    m_vu0Code = new uint8_t[PS2_VU0_CODE_SIZE]{};
    m_vu0Data = new uint8_t[PS2_VU0_DATA_SIZE]{};
    m_vu1Code = new uint8_t[PS2_VU1_CODE_SIZE]{};
    m_vu1Data = new uint8_t[PS2_VU1_DATA_SIZE]{};
    return true;
}

void PS2Memory::write64(uint32_t address, uint64_t value)
{
    if (address & 7u)
        throw std::runtime_error("unaligned code upload in minimal replay");
    if (address >= PS2_VU1_CODE_BASE &&
        address - PS2_VU1_CODE_BASE <= PS2_VU1_CODE_SIZE - sizeof(value))
    {
        std::memcpy(m_vu1Code + address - PS2_VU1_CODE_BASE, &value, sizeof(value));
        m_vu1CodeGeneration.fetch_add(1u, std::memory_order_relaxed);
        return;
    }
    if (address >= PS2_VU0_CODE_BASE &&
        address - PS2_VU0_CODE_BASE <= PS2_VU0_CODE_SIZE - sizeof(value))
    {
        std::memcpy(m_vu0Code + address - PS2_VU0_CODE_BASE, &value, sizeof(value));
        m_vu0CodeGeneration.fetch_add(1u, std::memory_order_relaxed);
        return;
    }
    throw std::runtime_error("minimal replay memory supports VU code uploads only");
}

void PS2Memory::submitGifPacket(GifPathId path, const uint8_t *data,
                              uint32_t size, bool, bool)
{
    if (path != GifPathId::Path1 || !m_gifPacketCallback)
        throw std::runtime_error("minimal replay requires a PATH1 packet callback");
    m_gifPacketCallback(data, size);
}

GS::GS() = default;
void GS::init(uint8_t *, uint32_t, GSRegisters *) {}
void GS::processGIFPacket(const uint8_t *, uint32_t)
{
    throw std::runtime_error("minimal replay must capture PATH1 through tracked memory");
}

void register_ps2_vu1_tests()
{
    throw std::runtime_error("--tests requires the authoritative full-runtime build; omit --minimal");
}

namespace HostProfile
{
    void startRipSamplerForCurrentThread(const char *environment)
    {
        if (std::getenv(environment))
            throw std::runtime_error("RIP sampling requires the full-runtime replay build");
    }
}
