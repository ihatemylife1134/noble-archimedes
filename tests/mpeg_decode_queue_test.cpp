#include <algorithm>
#include <array>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <deque>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <mutex>
#include <sstream>
#include <string>
#include <vector>
extern "C" {
#include <libavcodec/avcodec.h>
#include <libavutil/error.h>
#include <libavutil/log.h>
#include <libswscale/swscale.h>
}
#define PS2X_HAS_FFMPEG 1
#define AGRESSIVE_LOGS 0
#include "DECODER_SOURCE"

static std::string fingerprint(const MpegDecodedFrame &frame)
{
    uint64_t hash = 1469598103934665603ull;
    for (const auto byte : frame.rgba) { hash ^= byte; hash *= 1099511628211ull; }
    std::ostringstream out;
    out << frame.width << ' ' << frame.height << ' ' << frame.repeatPict << ' '
        << frame.pts90k << ' ' << hash;
    return out.str();
}

static std::vector<std::string> run(const std::vector<uint8_t> &input, size_t &peak, bool multiTimestamp = false)
{
    MpegFfmpegDecoder decoder;
    std::deque<MpegDecodedFrame> frames;
    const size_t chunks[] = {1, 7, 31, 255, 4096, 16384};
    size_t offset = 0, iteration = 0;
    while (offset < input.size())
    {
        const size_t count = std::min(chunks[iteration++ % std::size(chunks)], input.size() - offset);
        std::vector<uint8_t> temporary(count + AV_INPUT_BUFFER_PADDING_SIZE, 0);
        std::copy_n(input.data() + offset, count, temporary.data());
        const bool timestamped = offset == 0 || (multiTimestamp && count == 16384u);
        const int64_t pts = timestamped ? 90000 + static_cast<int64_t>(offset) * 3 : -1;
        const int64_t dts = timestamped ? pts - 9000 : -1;
        if (!decoder.feed(temporary.data(), count, frames, pts, dts))
            throw std::runtime_error("feed failed");
        // Queued compressed packets must own their input after feed returns.
        std::fill(temporary.begin(), temporary.end(), 0xDD);
        peak = std::max(peak, frames.size());
        offset += count;
    }
    if (!decoder.flush(frames)) throw std::runtime_error("flush failed");
    peak = std::max(peak, frames.size());
#if !MPEG_BASELINE
    if (peak > 5u) throw std::runtime_error("decoded frame lead is unbounded");
    if (!decoder.hasPendingInput()) throw std::runtime_error("EOF discarded queued compressed input");
#endif
    std::vector<std::string> result;
    for (unsigned guard = 0; guard < 1000; ++guard)
    {
#if !MPEG_BASELINE
        if (!decoder.pump(frames)) throw std::runtime_error("pump failed");
        peak = std::max(peak, frames.size());
#endif
        if (frames.empty()) break;
        result.push_back(fingerprint(frames.front()));
        frames.pop_front();
    }
#if !MPEG_BASELINE
    if (decoder.hasPendingInput() || !frames.empty()) throw std::runtime_error("decoder did not drain EOF");
#endif
    decoder.reset();
    std::vector<uint8_t> padded(input);
    padded.resize(input.size() + AV_INPUT_BUFFER_PADDING_SIZE, 0);
    if (!decoder.feed(padded.data(), input.size(), frames) || !decoder.flush(frames))
        throw std::runtime_error("decoder reuse failed");
    // Destruction must release any compressed packets still queued after reset.
    decoder.reset();
    return result;
}

int main(int argc, char **argv)
{
    try {
        if (argc != 4) return 2;
        std::ifstream input(argv[1], std::ios::binary);
        const std::vector<uint8_t> data((std::istreambuf_iterator<char>(input)), {});
        if (data.empty()) throw std::runtime_error("missing synthetic input");
        size_t peak = 0;
        auto frames = run(data, peak);
        if (frames.size() != std::stoul(argv[3])) throw std::runtime_error("wrong frame count: " + std::to_string(frames.size()));
        const auto timestamped = run(data, peak, true);
        if (timestamped.size() != frames.size()) throw std::runtime_error("timestamped stream lost frames");
        frames.insert(frames.end(), timestamped.begin(), timestamped.end());
#if MPEG_BASELINE
        std::ofstream output(argv[2]);
        for (const auto &line : frames) output << line << '\n';
        std::fprintf(stderr, "EAGER negative control: %zu frames, peak=%zu; bounded assertion would fail\n", frames.size(), peak);
        if (peak <= 5u) throw std::runtime_error("negative control did not expose unbounded decoding");
#else
        std::ifstream reference(argv[2]);
        std::vector<std::string> expected;
        std::string line;
        while (std::getline(reference, line)) expected.push_back(line);
        if (frames != expected) throw std::runtime_error("pixel/order/timestamp/metadata differ from eager decoder");
        std::fprintf(stderr, "PASS: %zu identical frames, peak=%zu; fragment lifetime, EOF and reset checks pass\n", frames.size(), peak);
#endif
    } catch (const std::exception &error) {
        std::fprintf(stderr, "FAIL: %s\n", error.what());
        return 1;
    }
}
