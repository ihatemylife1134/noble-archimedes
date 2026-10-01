// Offline VU replay and interpreter benchmark. No guest executable is needed.
#include "runtime/ps2_vu1.h"
#include "runtime/ps2_memory.h"
#include "runtime/gs/gs_frontend.h"
#include "MiniTest.h"
#include "ps2_vu1_capture.h"

#include <chrono>
#include <bit>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <thread>
#if defined(__SSE2__)
#include <xmmintrin.h>
#endif

namespace HostProfile { void startRipSamplerForCurrentThread(const char *); }

void register_ps2_vu1_tests();

namespace
{
    uint32_t warmupRepeats = 1u;
    // Diagnostic only: flushing intermediate products can change FMAC output.
    // The replay still rejects any changed state/data/packet/cycle result.
    void configureFloatingDiagnostic()
    {
#if defined(__SSE2__)
        if (std::getenv("PS2_VU_REPLAY_FTZ_DIAGNOSTIC"))
            _mm_setcsr(_mm_getcsr() | 0x8040u);
#endif
    }
    struct Workload
    {
        std::string name;
        vu_replay::InputHeader header;
        VU1State initial{};
        std::vector<uint8_t> code;
        std::vector<uint8_t> data;
        VU1State expected{};
        std::vector<uint8_t> expectedData;
        std::vector<std::vector<uint8_t>> expectedPackets;
        bool hasExpected = false;
        bool resume = false;
    };

    void readBytes(std::ifstream &file, void *data, size_t bytes)
    {
        if (!file.read(static_cast<char *>(data), static_cast<std::streamsize>(bytes)))
            throw std::runtime_error("truncated replay file");
    }

    Workload readWorkload(const std::filesystem::path &input)
    {
        Workload workload;
        workload.name = input.stem().string();
        std::ifstream file(input, std::ios::binary);
        readBytes(file, &workload.header, sizeof(workload.header));
        if (workload.header.magic != vu_replay::kInputMagic || workload.header.version != vu_replay::kVersion ||
            workload.header.stateSize != sizeof(VU1State) || workload.header.codeSize > PS2_VU1_CODE_SIZE ||
            workload.header.dataSize > PS2_VU1_DATA_SIZE || workload.header.codeSize < 8u || workload.header.dataSize < 16u)
            throw std::runtime_error("unsupported replay input header");
        readBytes(file, &workload.initial, sizeof(workload.initial));
        workload.code.resize(workload.header.codeSize);
        workload.data.resize(workload.header.dataSize);
        readBytes(file, workload.code.data(), workload.code.size());
        readBytes(file, workload.data.data(), workload.data.size());
        std::string output = input.string();
        const size_t suffix = output.rfind("_input.bin");
        if (suffix == std::string::npos)
            throw std::runtime_error("replay input must end in _input.bin");
        output.replace(suffix, 10u, "_output.bin");
        std::ifstream oracle(output, std::ios::binary);
        vu_replay::OutputHeader expectedHeader;
        readBytes(oracle, &expectedHeader, sizeof(expectedHeader));
        if (expectedHeader.magic != vu_replay::kOutputMagic || expectedHeader.version != vu_replay::kVersion ||
            expectedHeader.stateSize != sizeof(VU1State) || expectedHeader.dataSize != workload.header.dataSize ||
            expectedHeader.packetCount > 65536u)
            throw std::runtime_error("unsupported replay output header");
        readBytes(oracle, &workload.expected, sizeof(workload.expected));
        workload.expectedData.resize(expectedHeader.dataSize);
        readBytes(oracle, workload.expectedData.data(), workload.expectedData.size());
        for (uint32_t i = 0u; i < expectedHeader.packetCount; ++i)
        {
            uint32_t size = 0u;
            readBytes(oracle, &size, sizeof(size));
            if (size > 0x10000u)
                throw std::runtime_error("invalid replay packet size");
            auto &packet = workload.expectedPackets.emplace_back(size);
            readBytes(oracle, packet.data(), packet.size());
        }
        workload.hasExpected = true;
        return workload;
    }

    uint32_t upper(uint8_t op, uint8_t dest, uint8_t ft, uint8_t fs, uint8_t fd)
    {
        return (uint32_t(dest) << 21) | (uint32_t(ft) << 16) | (uint32_t(fs) << 11) | (uint32_t(fd) << 6) | op;
    }

#if defined(PS2_VU_CHAIN_CAPTURE_SUPPORTED)
    std::vector<Workload> readChain(const std::filesystem::path &input)
    {
        if (std::filesystem::file_size(input) > vu_replay::kMaxChainBytes)
            throw std::runtime_error("replay chain exceeds byte bound");
        std::ifstream file(input, std::ios::binary);
        vu_replay::ChainHeader header;
        readBytes(file, &header, sizeof(header));
        if (header.magic != vu_replay::kChainMagic || header.version != vu_replay::kVersion ||
            header.stateSize != sizeof(VU1State) || header.layout != vu_replay::stateLayout() ||
            header.callCount == 0u || header.callCount > 4096u)
            throw std::runtime_error("unsupported replay chain header/layout");
        std::vector<Workload> calls;
        for (uint32_t index = 0u; index < header.callCount; ++index)
        {
            Workload &call = calls.emplace_back();
            call.name = input.stem().string() + "-" + std::to_string(index);
            vu_replay::ChainCallHeader invocation;
            readBytes(file, &invocation, sizeof(invocation));
            if (invocation.resume != (index == 0u ? 0u : 1u) ||
                invocation.codeSize < 8u || invocation.codeSize > PS2_VU1_CODE_SIZE || (invocation.codeSize & 7u) != 0u ||
                invocation.dataSize < 16u || invocation.dataSize > PS2_VU1_DATA_SIZE)
                throw std::runtime_error("unsupported replay chain invocation");
            call.resume = invocation.resume != 0u;
            call.header.codeSize = invocation.codeSize;
            call.header.dataSize = invocation.dataSize;
            call.header.maxCycles = invocation.maxCycles;
            readBytes(file, &call.initial, sizeof(call.initial));
            call.code.resize(invocation.codeSize);
            call.data.resize(invocation.dataSize);
            readBytes(file, call.code.data(), call.code.size());
            readBytes(file, call.data.data(), call.data.size());
            readBytes(file, &call.expected, sizeof(call.expected));
            call.expectedData.resize(invocation.dataSize);
            readBytes(file, call.expectedData.data(), call.expectedData.size());
            uint32_t packets = 0u;
            readBytes(file, &packets, sizeof(packets));
            if (packets > 65536u)
                throw std::runtime_error("invalid replay chain packet count");
            for (uint32_t packet = 0u; packet < packets; ++packet)
            {
                uint32_t size = 0u;
                readBytes(file, &size, sizeof(size));
                if (size > 0x10000u)
                    throw std::runtime_error("invalid replay chain packet size");
                auto &bytes = call.expectedPackets.emplace_back(size);
                readBytes(file, bytes.data(), bytes.size());
            }
            call.hasExpected = true;
        }
        return calls;
    }
#endif

    uint32_t special(uint8_t op, uint8_t dest, uint8_t ft, uint8_t fs)
    {
        return (uint32_t(dest) << 21) | (uint32_t(ft) << 16) | (uint32_t(fs) << 11) |
               (uint32_t(op & 0x7cu) << 4) | (op & 3u) | 0x3cu;
    }

    Workload synthetic(const std::string &name)
    {
        Workload workload;
        workload.name = name;
        workload.header.codeSize = PS2_VU1_CODE_SIZE;
        workload.header.dataSize = PS2_VU1_DATA_SIZE;
        workload.header.maxCycles = name == "short-call" ? 2u : 65536u;
        workload.code.resize(PS2_VU1_CODE_SIZE);
        workload.data.resize(PS2_VU1_DATA_SIZE);
        workload.initial.vf[0][3] = 1.0f;
        workload.initial.q = 1.0f;
        workload.initial.r = 0x3f800000u;
        for (uint32_t reg = 1u; reg < 32u; ++reg)
            for (uint32_t lane = 0u; lane < 4u; ++lane)
                workload.initial.vf[reg][lane] = 0.125f * static_cast<float>(1u + ((reg + lane) & 7u));
        for (uint32_t qw = 0u; qw < workload.data.size() / 16u; ++qw)
            std::memcpy(workload.data.data() + qw * 16u, workload.initial.vf[(qw & 7u) + 1u], 16u);
        constexpr uint32_t nop = 0x000002ffu;
        for (uint32_t pair = 0u; pair < 34u; ++pair)
        {
            uint32_t lo = 0u;
            uint32_t hi = nop;
            if (pair < 32u && name != "short-call")
            {
                lo = (0x08u << 25) | (1u << 16) | (1u << 11) | 1u;
                if (name == "fmac")
                    hi = upper(pair & 1u ? 0x18u : 0x28u, 0xfu, 31u, 30u, (pair & 15u) + 1u);
                else if (name == "matrix")
                    hi = (pair & 3u) == 3u ? upper(0x08u + (pair & 3u), 0xfu, 31u, 30u, (pair & 15u) + 1u)
                                          : special((pair & 3u) == 0u ? 0x18u : 0x08u + (pair & 3u), 0xfu, 31u, 30u);
                else if (name == "load-store")
                {
                    hi = upper(0x28u, 0xfu, 31u, 30u, (pair & 7u) + 1u);
                    lo = pair & 1u ? (0x01u << 25) | (0xfu << 21) | (((pair & 7u) + 8u) << 11) | (pair & 7u)
                                   : (0xfu << 21) | (((pair & 7u) + 8u) << 16) | (pair & 7u);
                }
            }
            if (name == "short-call" && pair == 0u)
                hi |= 0x40000000u;
            else if (pair == 32u)
                lo = (0x20u << 25) | (static_cast<uint32_t>(-33) & 0x7ffu);
            std::memcpy(workload.code.data() + pair * 8u, &lo, 4u);
            std::memcpy(workload.code.data() + pair * 8u + 4u, &hi, 4u);
        }
        return workload;
    }

    uint64_t hashBytes(uint64_t hash, const void *bytes, size_t size)
    {
        const auto *data = static_cast<const uint8_t *>(bytes);
        for (size_t i = 0u; i < size; ++i)
            hash = (hash ^ data[i]) * 1099511628211ull;
        return hash;
    }

    uint64_t benchmark(const Workload &workload, uint32_t repeats, bool quiet = false, FILE *snapshotFile = nullptr)
    {
        PS2Memory memory;
        if (!memory.initialize())
            throw std::runtime_error("PS2Memory initialize failed");
        GS gs;
        gs.init(memory.getGSVRAM(), PS2_GS_VRAM_SIZE, &memory.gs());
        std::vector<std::vector<uint8_t>> packets;
        memory.setGifPacketCallback([&](const uint8_t *bytes, uint32_t size)
        {
            packets.emplace_back(bytes, bytes + size);
        });
        // A tracked pointer exercises the same decoded-cache path as the game.
        for (uint32_t offset = 0u; offset < workload.code.size(); offset += 8u)
        {
            uint64_t pair = 0u;
            std::memcpy(&pair, workload.code.data() + offset, 8u);
            memory.write64(PS2_VU1_CODE_BASE + offset, pair);
        }
        VU1Interpreter interpreter;
        double seconds = 0.0;
        uint64_t cycles = 0u;
        VU1State actual{};
        configureFloatingDiagnostic();
        for (uint32_t repeat = 0u; repeat < warmupRepeats + repeats; ++repeat)
        {
            interpreter.state() = workload.initial;
            packets.clear();
            std::memcpy(memory.getVU1Data(), workload.data.data(), workload.data.size());
            // execute preserves the private absolute clock; measure using its
            // resulting clock difference rather than the restored public copy.
            const auto start = std::chrono::steady_clock::now();
            interpreter.execute(memory.getVU1Code(), workload.header.codeSize,
                                memory.getVU1Data(), workload.header.dataSize, gs, &memory,
                                workload.initial.pc, workload.initial.top, workload.initial.itop,
                                workload.header.maxCycles);
            const auto end = std::chrono::steady_clock::now();
            actual = interpreter.state();
            const uint64_t delta = actual.cycles - cycles;
            cycles = actual.cycles;
            actual.cycles = delta;
            if (workload.hasExpected &&
                (std::memcmp(&actual, &workload.expected, sizeof(actual)) != 0 ||
                 std::memcmp(memory.getVU1Data(), workload.expectedData.data(), workload.expectedData.size()) != 0 ||
                 packets != workload.expectedPackets))
                throw std::runtime_error(workload.name + ": state/data/cycle/PATH1 replay mismatch");
            if (repeat >= warmupRepeats)
                seconds += std::chrono::duration<double>(end - start).count();
        }
        uint64_t hash = hashBytes(1469598103934665603ull, &actual, sizeof(actual));
        hash = hashBytes(hash, memory.getVU1Data(), workload.header.dataSize);
        for (const auto &packet : packets)
            hash = hashBytes(hash, packet.data(), packet.size());
        if (!quiet)
            std::printf("%s repeats=%u cycles=%llu ms=%.3f cycles/s=%.0f hash=%016llx packets=%zu verified=%u\n",
                        workload.name.c_str(), repeats, static_cast<unsigned long long>(actual.cycles), seconds * 1000.0,
                        actual.cycles * repeats / seconds, static_cast<unsigned long long>(hash), packets.size(), workload.hasExpected);
        if (snapshotFile)
        {
            std::fwrite(&actual, sizeof(actual), 1u, snapshotFile);
            std::fwrite(memory.getVU1Data(), 1u, workload.header.dataSize, snapshotFile);
        }
        return hash;
    }

#if defined(PS2_VU_CHAIN_CAPTURE_SUPPORTED)
    // Exercise a signature-guarded kernel with actual captured inputs. The
    // snapshots are compared byte for byte against the unchanged interpreter;
    // this test deliberately includes calls that leave private writes pending.
    void kernelGuardFuzz(const std::filesystem::path &input, const std::filesystem::path &output)
    {
        const auto calls = readChain(input);
        if (calls.size() < 18u)
            throw std::runtime_error("kernel guard corpus needs a hot name chain");
        std::ofstream snapshots(output, std::ios::binary);
        if (!snapshots)
            throw std::runtime_error("cannot write kernel guard snapshots");
        PS2Memory memory;
        if (!memory.initialize()) throw std::runtime_error("PS2Memory initialize failed");
        GS gs;
        gs.init(memory.getGSVRAM(), PS2_GS_VRAM_SIZE, &memory.gs());
        VU1Interpreter interpreter;
        std::vector<std::vector<uint8_t>> packets;
        bool callbackChange = false;
        bool callbackIdentical = false;
        bool callbackSeen = false;
        const uint64_t changedEnd = uint64_t((0x08u << 25) | (9u << 16) | 11u) |
                                    (uint64_t(0x400002ffu) << 32);
        memory.setGifPacketCallback([&](const uint8_t *bytes, uint32_t size) {
            packets.emplace_back(bytes, bytes + size);
            if (!callbackSeen && (callbackChange || callbackIdentical))
            {
                callbackSeen = true;
                uint64_t original = 0;
                std::memcpy(&original, memory.getVU1Code() + 0x130u, sizeof(original));
                memory.write64(PS2_VU1_CODE_BASE + 0x130u, callbackChange ? changedEnd : original);
            }
        });
        uint32_t cases = 0;
        uint32_t invocations = 0;
        const auto save = [&](uint32_t caseIndex, uint32_t callIndex, uint32_t codeSize, uint64_t entryCycle) {
            const uint32_t header[] = {caseIndex, callIndex, codeSize, static_cast<uint32_t>(packets.size())};
            snapshots.write(reinterpret_cast<const char *>(header), sizeof(header));
            VU1State actual = interpreter.state();
            actual.cycles -= entryCycle;
            snapshots.write(reinterpret_cast<const char *>(&actual), sizeof(actual));
            snapshots.write(reinterpret_cast<const char *>(memory.getVU1Code()), PS2_VU1_CODE_SIZE);
            snapshots.write(reinterpret_cast<const char *>(memory.getVU1Data()), PS2_VU1_DATA_SIZE);
            for (const auto &packet : packets)
            {
                const uint32_t size = static_cast<uint32_t>(packet.size());
                snapshots.write(reinterpret_cast<const char *>(&size), sizeof(size));
                snapshots.write(reinterpret_cast<const char *>(packet.data()), size);
            }
            ++invocations;
        };
        for (const uint32_t source : {3u, 5u, 17u})
            for (const uint32_t budget : {0u, 1u, 2u, 7u, 32u, 64u})
                for (uint32_t variant = 0u; variant < 6u; ++variant)
                {
                    if (source != 3u && variant >= 4u) continue;
                    const Workload &call = calls[source];
                    for (uint32_t offset = 0; offset < call.code.size(); offset += 8u)
                    {
                        uint64_t word = 0;
                        std::memcpy(&word, call.code.data() + offset, sizeof(word));
                        memory.write64(PS2_VU1_CODE_BASE + offset, word);
                    }
                    interpreter.reset();
                    interpreter.state() = call.initial;
                    interpreter.state().cycles = 0u;
                    std::memcpy(memory.getVU1Data(), call.data.data(), call.data.size());
                    callbackChange = callbackIdentical = callbackSeen = false;
                    // Warm the code/signature cache before rewriting a word,
                    // shrinking the code bounds, or mutating code in PATH1.
                    interpreter.execute(memory.getVU1Code(), call.header.codeSize,
                                        memory.getVU1Data(), call.header.dataSize, gs, &memory,
                                        call.initial.pc, call.initial.top, call.initial.itop, 2048u);
                    const uint64_t warmedCycle = interpreter.state().cycles;
                    if (variant == 1u || variant == 2u)
                    {
                        uint64_t original = 0;
                        std::memcpy(&original, memory.getVU1Code() + 0x130u, sizeof(original));
                        memory.write64(PS2_VU1_CODE_BASE + 0x130u, variant == 1u ? original : changedEnd);
                    }
                    interpreter.state() = call.initial;
                    interpreter.state().cycles = warmedCycle;
                    std::memcpy(memory.getVU1Data(), call.data.data(), call.data.size());
                    if (variant >= 4u)
                    {
                        // The 16-byte EOP tag completes on XGKICK's issue
                        // cycle, so the callback changes the next pair before
                        // the interpreter fetches its E-bit instruction.
                        const uint64_t tag[] = {0x8000u, 0u};
                        std::memcpy(interpreter.state().vf[13], tag, sizeof(tag));
                        // Suppress the record-copy path, which otherwise
                        // supplies another tag before this short EOP tag.
                        const uint32_t zero = 0u;
                        const uint32_t record = (call.initial.top & 0x3ffu) * 16u;
                        std::memcpy(memory.getVU1Data() + record + 4u, &zero, sizeof(zero));
                        std::memcpy(memory.getVU1Data() + record + 8u, &zero, sizeof(zero));
                        interpreter.state().vi[12] = 0;
                        callbackChange = variant == 4u;
                        callbackIdentical = variant == 5u;
                    }
                    const uint32_t codeSize = variant == 3u ? 0x1b0u : call.header.codeSize;
                    uint64_t entryCycle = interpreter.state().cycles;
                    packets.clear();
                    interpreter.execute(memory.getVU1Code(), codeSize, memory.getVU1Data(), call.header.dataSize,
                                        gs, &memory, call.initial.pc, call.initial.top, call.initial.itop, budget);
                    save(cases, 0u, codeSize, entryCycle);
                    uint32_t callIndex = 1u;
                    for (const uint32_t resumeBudget : {1u, 2u, 5u, 7u, 128u})
                    {
                        entryCycle = interpreter.state().cycles;
                        packets.clear();
                        interpreter.resume(memory.getVU1Code(), codeSize, memory.getVU1Data(), call.header.dataSize,
                                           gs, &memory, call.initial.top, call.initial.itop, resumeBudget);
                        save(cases, callIndex++, codeSize, entryCycle);
                    }
                    if (variant >= 4u && !callbackSeen)
                        throw std::runtime_error("kernel callback guard corpus did not reach PATH1");
                    if (variant == 4u && interpreter.state().vi[9] != 11)
                        throw std::runtime_error("kernel ignored callback microcode replacement in case " + std::to_string(cases));
                    ++cases;
                }
        if (!snapshots)
            throw std::runtime_error("kernel guard snapshot write failed");
        std::printf("kernel guard cases=%u invocations=%u snapshots=%s verified=1\n", cases, invocations,
                    output.string().c_str());
    }

    void benchmarkChain(const std::filesystem::path &input, uint32_t repeats)
    {
        const auto calls = readChain(input);
        PS2Memory memory;
        if (!memory.initialize())
            throw std::runtime_error("PS2Memory initialize failed");
        GS gs;
        gs.init(memory.getGSVRAM(), PS2_GS_VRAM_SIZE, &memory.gs());
        std::vector<std::vector<uint8_t>> packets;
        memory.setGifPacketCallback([&](const uint8_t *bytes, uint32_t size) { packets.emplace_back(bytes, bytes + size); });
        VU1Interpreter interpreter;
        double seconds = 0.0;
        uint64_t totalCycles = 0u;
        uint64_t totalPackets = 0u;
        uint64_t hash = 1469598103934665603ull;
        configureFloatingDiagnostic();
        for (uint32_t repeat = 0u; repeat < warmupRepeats + repeats; ++repeat)
        {
            interpreter.reset();
            for (const Workload &call : calls)
            {
                for (uint32_t offset = 0u; offset < call.code.size(); offset += 8u)
                {
                    uint64_t pair = 0u;
                    std::memcpy(&pair, call.code.data() + offset, 8u);
                    if (std::memcmp(memory.getVU1Code() + offset, &pair, 8u) != 0)
                        memory.write64(PS2_VU1_CODE_BASE + offset, pair);
                }
                std::memcpy(memory.getVU1Data(), call.data.data(), call.data.size());
                const uint64_t entryCycle = interpreter.state().cycles;
                interpreter.state() = call.initial;
                interpreter.state().cycles = entryCycle;
                packets.clear();
                const auto start = std::chrono::steady_clock::now();
                if (call.resume)
                    interpreter.resume(memory.getVU1Code(), call.header.codeSize,
                                       memory.getVU1Data(), call.header.dataSize, gs, &memory,
                                       call.initial.top, call.initial.itop, call.header.maxCycles);
                else
                    interpreter.execute(memory.getVU1Code(), call.header.codeSize,
                                        memory.getVU1Data(), call.header.dataSize, gs, &memory,
                                        call.initial.pc, call.initial.top, call.initial.itop, call.header.maxCycles);
                const auto end = std::chrono::steady_clock::now();
                VU1State actual = interpreter.state();
                actual.cycles -= entryCycle;
                if (std::memcmp(&actual, &call.expected, sizeof(actual)) != 0 ||
                    std::memcmp(memory.getVU1Data(), call.expectedData.data(), call.expectedData.size()) != 0 ||
                    packets != call.expectedPackets)
                    throw std::runtime_error(call.name + ": chained state/data/cycle/PATH1 mismatch");
                if (repeat >= warmupRepeats)
                {
                    seconds += std::chrono::duration<double>(end - start).count();
                    totalCycles += actual.cycles;
                    totalPackets += packets.size();
                }
                if (repeat == warmupRepeats + repeats - 1u)
                {
                    hash = hashBytes(hash, &actual, sizeof(actual));
                    hash = hashBytes(hash, memory.getVU1Data(), call.header.dataSize);
                    for (const auto &packet : packets)
                        hash = hashBytes(hash, packet.data(), packet.size());
                }
            }
        }
        std::printf("%s chain calls=%zu repeats=%u cycles=%llu ms=%.3f cycles/s=%.0f hash=%016llx packets=%llu verified=1\n",
                    input.stem().string().c_str(), calls.size(), repeats, static_cast<unsigned long long>(totalCycles),
                    seconds * 1000.0, totalCycles / seconds, static_cast<unsigned long long>(hash),
                    static_cast<unsigned long long>(totalPackets));
    }

    void captureChainTest(const std::filesystem::path &prefix)
    {
        std::filesystem::create_directories(prefix.parent_path());
        _putenv_s("PS2_VU_CAPTURE_PREFIX", prefix.string().c_str());
        _putenv_s("PS2_VU_CAPTURE_CHAIN", "1");
        const char *entryValue = std::getenv("PS2_VU_CHAIN_TEST_ENTRY");
        const std::string testEntry = entryValue && *entryValue ? entryValue : "8";
        _putenv_s("PS2_VU_CAPTURE_RESUME_ENTRY", testEntry.c_str());
        _putenv_s("PS2_VU_CAPTURE_COUNT", "1");
        PS2Memory memory;
        if (!memory.initialize()) throw std::runtime_error("PS2Memory initialize failed");
        GS gs;
        gs.init(memory.getGSVRAM(), PS2_GS_VRAM_SIZE, &memory.gs());
        memory.setGifPacketCallback([](const uint8_t *, uint32_t) {});
        const auto pair = [&](uint32_t pc, uint32_t lo, uint32_t hi) {
            memory.write64(PS2_VU1_CODE_BASE + pc, uint64_t(lo) | (uint64_t(hi) << 32));
        };
        pair(0u, (0x01u << 25) | (0xfu << 21) | (2u << 11), upper(0x2au, 0xfu, 31u, 30u, 1u));
        pair(8u, (0x04u << 25) | (0x8u << 21) | (3u << 16), 0x2ffu);
        pair(16u, (0x08u << 25) | (4u << 16) | 5u, 0x2ffu);
        pair(24u, (0x40u << 25) | (5u << 11) | (0x6cu << 4) | 0x3cu, 0x400002ffu);
        pair(32u, 0u, 0x2ffu);
        VU1Interpreter interpreter;
        interpreter.state().vi[5] = 64;
        for (uint32_t component = 0u; component < 4u; ++component)
        {
            interpreter.state().vf[30][component] = 2.0f;
            interpreter.state().vf[31][component] = 3.0f;
            interpreter.state().vf[2][component] = 4.0f;
        }
        const uint64_t tag = 0x1000000000008000ull;
        std::memcpy(memory.getVU1Data() + 1024u, &tag, sizeof(tag));
        // A prior invocation shifts the private clock and leaves pending
        // writes. The next fresh execute clears those writes and starts a new
        // capture chain without consuming the selected-chain quota.
        interpreter.execute(memory.getVU1Code(), PS2_VU1_CODE_SIZE, memory.getVU1Data(), PS2_VU1_DATA_SIZE,
                            gs, &memory, 0u, 0u, 0u, 3u);
        interpreter.execute(memory.getVU1Code(), PS2_VU1_CODE_SIZE, memory.getVU1Data(), PS2_VU1_DATA_SIZE,
                            gs, &memory, 0u, 0x10u, 0x11u, 1u);
        const uint32_t scalar = 0x1234u;
        std::memcpy(memory.getVU1Data(), &scalar, sizeof(scalar));
        interpreter.state().dBitEnabled = true;
        interpreter.state().tBitEnabled = true;
        interpreter.resume(memory.getVU1Code(), PS2_VU1_CODE_SIZE, memory.getVU1Data(), PS2_VU1_DATA_SIZE,
                           gs, &memory, 0x20u, 0x21u, 1u);
        pair(16u, (0x08u << 25) | (4u << 16) | 5u, upper(0x28u, 0xfu, 31u, 1u, 6u));
        interpreter.state().tBitEnabled = false;
        interpreter.resume(memory.getVU1Code(), PS2_VU1_CODE_SIZE, memory.getVU1Data(), PS2_VU1_DATA_SIZE,
                           gs, &memory, 0x30u, 0x31u, 2u);
        interpreter.state().dBitEnabled = false;
        interpreter.resume(memory.getVU1Code(), PS2_VU1_CODE_SIZE, memory.getVU1Data(), PS2_VU1_DATA_SIZE,
                           gs, &memory, 0x40u, 0x41u, 20u);
        const auto path = std::filesystem::path(prefix.string() + "_chain_0000_0000.bin");
        if (std::strtoul(testEntry.c_str(), nullptr, 16) == 16u && vu_replay::chainLimit() == 2u)
        {
            if (std::filesystem::exists(path))
                throw std::runtime_error("discarded chain unexpectedly wrote a file");
            std::printf("chain discarded before late resume selector: verified=1\n");
            return;
        }
        const auto calls = readChain(path);
        if (calls.size() < 2u || calls.front().expected.cycles != 1u || !calls[1].resume)
            throw std::runtime_error("chain did not preserve execute/resume boundary");
        if (vu_replay::chainLimit() >= 4u && (calls.size() != 4u || calls.back().expectedPackets.size() != 1u))
            throw std::runtime_error("chain did not capture ordered PATH1 completion");
        benchmarkChain(path, 1u);
    }
#if defined(PS2_VU_CHAIN_GATE_SUPPORTED)
    void captureGateTest(const std::filesystem::path &prefix)
    {
        std::filesystem::create_directories(prefix.parent_path());
        const auto gatePath = std::filesystem::path(prefix.string() + ".gate");
        const auto chainPath = std::filesystem::path(prefix.string() + "_chain_0000_0000.bin");
        std::filesystem::remove(gatePath);
        std::filesystem::remove(chainPath);
        _putenv_s("PS2_VU_CAPTURE_PREFIX", prefix.string().c_str());
        _putenv_s("PS2_VU_CAPTURE_CHAIN", "1");
        _putenv_s("PS2_VU_CAPTURE_GATE_FILE", gatePath.string().c_str());
        _putenv_s("PS2_VU_CAPTURE_RESUME_ENTRY", "8");
        _putenv_s("PS2_VU_CAPTURE_COUNT", "1");
        PS2Memory memory;
        if (!memory.initialize()) throw std::runtime_error("PS2Memory initialize failed");
        GS gs;
        gs.init(memory.getGSVRAM(), PS2_GS_VRAM_SIZE, &memory.gs());
        memory.setGifPacketCallback([](const uint8_t *, uint32_t) {});
        memory.write64(PS2_VU1_CODE_BASE, uint64_t(0x2ffu) << 32);
        memory.write64(PS2_VU1_CODE_BASE + 8u, uint64_t(0x400002ffu) << 32);
        memory.write64(PS2_VU1_CODE_BASE + 16u, uint64_t(0x2ffu) << 32);
        VU1Interpreter interpreter;
        interpreter.execute(memory.getVU1Code(), PS2_VU1_CODE_SIZE, memory.getVU1Data(), PS2_VU1_DATA_SIZE,
                            gs, &memory, 0u, 0u, 0u, 1u);
        interpreter.resume(memory.getVU1Code(), PS2_VU1_CODE_SIZE, memory.getVU1Data(), PS2_VU1_DATA_SIZE,
                           gs, &memory, 0u, 0u, 0u);
        if (std::filesystem::exists(chainPath) || !vu_replay::captureChain().pending.empty())
            throw std::runtime_error("closed gate consumed a chain or copied invocation inputs");
        std::ofstream(gatePath).put('1');
        std::this_thread::sleep_for(std::chrono::milliseconds(1050));
        // Poll is rate-limited by both elapsed time and invocation count.
        // Enabling during resumes must wait for a complete fresh prefix.
        for (unsigned call=0; call<256u; ++call)
            interpreter.resume(memory.getVU1Code(), PS2_VU1_CODE_SIZE, memory.getVU1Data(), PS2_VU1_DATA_SIZE,
                               gs, &memory, 0u, 0u, 0u);
        if (!vu_replay::captureGate().enabled || std::filesystem::exists(chainPath))
            throw std::runtime_error("gate must enable without writing a partial resume chain");
        std::filesystem::remove(gatePath); // Once enabled, no further file checks.
        interpreter.execute(memory.getVU1Code(), PS2_VU1_CODE_SIZE, memory.getVU1Data(), PS2_VU1_DATA_SIZE,
                            gs, &memory, 0u, 0u, 0u, 1u);
        interpreter.resume(memory.getVU1Code(), PS2_VU1_CODE_SIZE, memory.getVU1Data(), PS2_VU1_DATA_SIZE,
                           gs, &memory, 0u, 0u, 16u);
        const auto calls=readChain(chainPath);
        if (calls.size()!=2u || calls.front().resume || !calls.back().resume || vu_replay::successfulChains!=1u)
            throw std::runtime_error("gate did not retain one complete fresh-plus-resume chain");
        benchmarkChain(chainPath,1u);
        std::printf("capture gate closed/open/fresh-prefix/quota/sticky-enable verified=1\n");
    }
#endif
#endif

    void fuzz(const std::filesystem::path &output)
    {
        FILE *snapshots = std::fopen(output.string().c_str(), "wb");
        if (!snapshots)
            throw std::runtime_error("cannot write fuzz snapshots");
        uint32_t seed = 0x0191fa27u;
        const auto random = [&]() {
            seed ^= seed << 13;
            seed ^= seed >> 17;
            seed ^= seed << 5;
            return seed;
        };
        constexpr uint32_t edgeBits[] = {0u, 0x80000000u, 1u, 0x80000001u, 0x007fffffu, 0x807fffffu,
                                        0x00800000u, 0x80800000u, 0x3f800000u, 0xbf800000u,
                                        0x7f7fffffu, 0xff7fffffu, 0x7f800000u, 0xff800000u,
                                        0x7fc01234u, 0xffc01234u};
        constexpr uint8_t arithmetic[] = {0x00u, 0x01u, 0x02u, 0x03u, 0x04u, 0x05u, 0x06u, 0x07u,
                                          0x08u, 0x09u, 0x0au, 0x0bu, 0x0cu, 0x0du, 0x0eu, 0x0fu,
                                          0x18u, 0x19u, 0x1au, 0x1bu, 0x1cu, 0x1eu,
                                          0x20u, 0x21u, 0x22u, 0x23u, 0x24u, 0x25u, 0x26u, 0x27u,
                                          0x28u, 0x29u, 0x2au, 0x2cu, 0x2du, 0x2eu};
        uint64_t combined = 1469598103934665603ull;
        for (uint32_t testcase = 0u; testcase < 128u; ++testcase)
        {
            Workload workload = synthetic("fmac");
            workload.name = "fuzz-" + std::to_string(testcase);
            for (auto &vector : workload.initial.vf)
                for (float &lane : vector)
                {
                    const uint32_t bits = random() & 1u ? random() : edgeBits[random() % std::size(edgeBits)];
                    std::memcpy(&lane, &bits, sizeof(bits));
                }
            for (float &lane : workload.initial.acc)
            {
                const uint32_t bits = random() & 1u ? random() : edgeBits[random() % std::size(edgeBits)];
                std::memcpy(&lane, &bits, sizeof(bits));
            }
            const uint32_t q = edgeBits[random() % std::size(edgeBits)];
            const uint32_t immediate = random();
            std::memcpy(&workload.initial.q, &q, sizeof(q));
            std::memcpy(&workload.initial.i, &immediate, sizeof(immediate));
            for (uint32_t pair = 0u; pair < 32u; ++pair)
            {
                const uint8_t opcode = arithmetic[random() % std::size(arithmetic)];
                const uint8_t mask = static_cast<uint8_t>(1u + random() % 15u);
                uint32_t lo = 0u;
                uint32_t hi = pair & 1u ? special(opcode, mask, 31u, 30u)
                                       : upper(opcode, mask, 31u, 30u, (pair & 7u) + 1u);
                if (pair == 7u)
                {
                    lo = immediate;
                    hi |= 0x80000000u;
                }
                std::memcpy(workload.code.data() + pair * 8u, &lo, 4u);
                std::memcpy(workload.code.data() + pair * 8u + 4u, &hi, 4u);
            }
            const uint32_t lowerNop = 0u;
            const uint32_t upperEnd = 0x400002ffu;
            std::memcpy(workload.code.data() + 32u * 8u, &lowerNop, 4u);
            std::memcpy(workload.code.data() + 32u * 8u + 4u, &upperEnd, 4u);
            const uint64_t hash = benchmark(workload, 1u, true, snapshots);
            combined = hashBytes(combined, &hash, sizeof(hash));
        }
        std::fclose(snapshots);
        std::printf("fuzz cases=128 state/data/cycle snapshots=%s hash=%016llx\n", output.string().c_str(),
                    static_cast<unsigned long long>(combined));
    }

    void boundedFuzz(const std::filesystem::path &output)
    {
        FILE *snapshots = std::fopen(output.string().c_str(), "wb");
        if (!snapshots)
            throw std::runtime_error("cannot write bounded fuzz snapshots");
        uint32_t seed = 0x9e3779b9u;
        const auto random = [&]() {
            seed ^= seed << 13;
            seed ^= seed >> 17;
            seed ^= seed << 5;
            return seed;
        };
        const auto finite = [&](uint32_t low, uint32_t high) {
            const uint32_t signMantissa = random() & 0x807fffffu;
            const uint32_t exponent = low + random() % (high - low + 1u);
            const uint32_t bits = signMantissa | (exponent << 23);
            return std::bit_cast<float>(bits);
        };
        constexpr uint8_t arithmetic[] = {0x00u, 0x01u, 0x02u, 0x03u, 0x04u, 0x05u, 0x06u, 0x07u,
                                          0x08u, 0x09u, 0x0au, 0x0bu, 0x0cu, 0x0du, 0x0eu, 0x0fu,
                                          0x18u, 0x19u, 0x1au, 0x1bu, 0x1cu, 0x1eu,
                                          0x20u, 0x21u, 0x22u, 0x23u, 0x24u, 0x25u, 0x26u, 0x27u,
                                          0x28u, 0x29u, 0x2au, 0x2cu, 0x2du, 0x2eu};
        constexpr uint32_t edges[] = {0u, 0x80000000u, 0x32000000u, 0xb2000000u, 0x327fffffu,
                                     0x4d000000u, 0xcd000000u, 0x4d7fffffu};
        constexpr uint32_t exceptional[] = {1u, 0x80000001u, 0x00800000u, 0x80800000u,
                                           0x7f7fffffu, 0xff7fffffu, 0x7fc01234u, 0xffc01234u};
        uint64_t combined = 1469598103934665603ull;
        constexpr uint32_t caseCount = 2304u;
        for (uint32_t testcase = 0u; testcase < caseCount; ++testcase)
        {
            Workload workload = synthetic("fmac");
            workload.name = "bounded-fuzz-" + std::to_string(testcase);
            workload.header.maxCycles = 64u;
            for (auto &vector : workload.initial.vf)
                for (float &lane : vector)
                    lane = finite(100u, 154u);
            for (float &lane : workload.initial.acc)
                lane = finite(100u, 154u);
            workload.initial.q = finite(100u, 154u);
            workload.initial.i = finite(100u, 154u);
            const uint32_t scenario = (testcase / 72u) % 16u;
            for (uint32_t lane = 0u; lane < 4u; ++lane)
            {
                float &left = workload.initial.vf[30][lane];
                float &right = workload.initial.vf[31][lane];
                float &acc = workload.initial.acc[lane];
                if (scenario == 4u || scenario == 5u)
                {
                    left = std::bit_cast<float>(edges[(testcase + lane) % std::size(edges)]);
                    right = std::bit_cast<float>(scenario == 5u ? ((lane & 1u) << 31) : edges[(testcase + lane + 3u) % std::size(edges)]);
                    acc = std::bit_cast<float>(edges[(testcase + lane + 5u) % std::size(edges)]);
                }
                else if (scenario == 6u)
                {
                    left = finite(100u, 154u);
                    right = lane & 1u ? left : -left;
                    acc = left;
                }
                else if ((scenario >= 7u && scenario <= 10u) || scenario == 14u)
                {
                    left = finite(123u, 131u);
                    right = finite(123u, 131u);
                    // Products are computed in double then rounded to float
                    // before entry. The interpreter rounds toward zero, so
                    // these include exact nonzero sums rounded to zero.
                    acc = static_cast<float>(static_cast<double>(left) * static_cast<double>(right));
                    if (scenario == 9u)
                        acc = std::nextafter(acc, 0.0f);
                    else if (scenario == 10u)
                        acc = std::nextafter(acc, std::copysign(INFINITY, acc));
                    if (scenario == 7u || (scenario == 14u && (lane & 1u)))
                        acc = -acc;
                }
                else if (scenario == 11u)
                {
                    left = finite(99u, 100u);
                    right = finite(154u, 155u);
                }
                else if (scenario == 12u || scenario == 13u)
                {
                    left = std::bit_cast<float>(exceptional[(testcase + lane) % std::size(exceptional)]);
                    right = std::bit_cast<float>(exceptional[(testcase + lane + 3u) % std::size(exceptional)]);
                }
                else if (scenario == 15u)
                {
                    left = finite(100u, 100u);
                    right = finite(100u, 100u);
                    acc = lane & 1u ? -left : left;
                }
            }
            if (scenario >= 4u)
            {
                workload.initial.q = workload.initial.vf[31][testcase & 3u];
                workload.initial.i = workload.initial.vf[31][(testcase + 1u) & 3u];
            }
            const uint8_t opcode = arithmetic[(testcase / 2u) % std::size(arithmetic)];
            const uint8_t mask = static_cast<uint8_t>((testcase / 72u + testcase / 1152u) & 15u);
            const uint32_t lo = 0u;
            const uint32_t hi = 0x40000000u | (testcase & 1u ? special(opcode, mask, 31u, 30u)
                                                          : upper(opcode, mask, 31u, 30u, 1u));
            const uint32_t nop = 0x000002ffu;
            std::memcpy(workload.code.data(), &lo, 4u);
            std::memcpy(workload.code.data() + 4u, &hi, 4u);
            std::memcpy(workload.code.data() + 8u, &lo, 4u);
            std::memcpy(workload.code.data() + 12u, &nop, 4u);
            const uint64_t hash = benchmark(workload, 1u, true, snapshots);
            combined = hashBytes(combined, &hash, sizeof(hash));
        }
        std::fclose(snapshots);
        std::printf("bounded-fuzz cases=%u state/data/cycle snapshots=%s hash=%016llx\n", caseCount,
                    output.string().c_str(), static_cast<unsigned long long>(combined));
    }
}

int main(int argc, char **argv)
{
    try
    {
        HostProfile::startRipSamplerForCurrentThread("PS2_VU_REPLAY_RIP");
        uint32_t repeats = 16u;
        std::vector<std::filesystem::path> inputs;
        for (int i = 1; i < argc; ++i)
        {
            const std::string arg = argv[i];
            if (arg == "--tests")
            {
                register_ps2_vu1_tests();
                return MiniTest::Run();
            }
            if (arg == "--capture-chain-test" && i + 1 < argc)
            {
#if defined(PS2_VU_CHAIN_CAPTURE_SUPPORTED)
                captureChainTest(argv[++i]);
                return 0;
#else
                throw std::runtime_error("selected source snapshot does not support chain capture");
#endif
            }
            if (arg == "--capture-gate-test" && i + 1 < argc)
            {
#if defined(PS2_VU_CHAIN_GATE_SUPPORTED)
                captureGateTest(argv[++i]);
                return 0;
#else
                throw std::runtime_error("selected source snapshot does not support capture gate");
#endif
            }
            if (arg == "--fuzz" && i + 1 < argc)
            {
                fuzz(argv[++i]);
                return 0;
            }
            if (arg == "--bounded-fuzz" && i + 1 < argc)
            {
                boundedFuzz(argv[++i]);
                return 0;
            }
            if (arg == "--kernel-guard-fuzz" && i + 2 < argc)
            {
#if defined(PS2_VU_CHAIN_CAPTURE_SUPPORTED)
                const std::filesystem::path input = argv[++i];
                kernelGuardFuzz(input, argv[++i]);
                return 0;
#else
                throw std::runtime_error("selected source snapshot does not support kernel guard corpus");
#endif
            }
            if (arg == "--repeat" && i + 1 < argc)
                repeats = static_cast<uint32_t>(std::stoul(argv[++i]));
            else if (arg == "--warmup" && i + 1 < argc)
                warmupRepeats = static_cast<uint32_t>(std::stoul(argv[++i]));
            else
                inputs.emplace_back(arg);
        }
        if (repeats == 0u)
            throw std::runtime_error("repeat count must be positive");
        if (warmupRepeats == 0u || warmupRepeats > 1024u || repeats > UINT32_MAX - warmupRepeats)
            throw std::runtime_error("warmup must be 1..1024 and iteration count must not overflow");
        if (inputs.empty())
            for (const std::string name : {"integer", "fmac", "matrix", "load-store", "short-call"})
                benchmark(synthetic(name), name == "short-call" ? repeats * 1000u : repeats);
        else
            for (const auto &input : inputs)
                if (input.filename().string().find("_chain_") != std::string::npos)
#if defined(PS2_VU_CHAIN_CAPTURE_SUPPORTED)
                    benchmarkChain(input, repeats);
#else
                    throw std::runtime_error("selected source snapshot does not support chain replay");
#endif
                else
                    benchmark(readWorkload(input), repeats);
        return 0;
    }
    catch (const std::exception &error)
    {
        std::fprintf(stderr, "VU benchmark failed: %s\n", error.what());
        return 1;
    }
}
