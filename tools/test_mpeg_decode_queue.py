"""Compare bounded MPEG decoding with a frozen eager decoder on a synthetic clip."""
import argparse
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/PS2Recomp/ps2xRuntime/src/lib/Kernel/Stubs/MPEG.cpp"
FFMPEG = ROOT / "tools/PS2Recomp/build/ThirdParty/ffmpeg-prefix/src/ffmpeg_external"
OUT = ROOT / "output/mpeg_decode_queue"


def write_if_changed(path, text):
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")


def decoder_source(source):
    # Compile the production decoder directly, avoiding the unrelated syscall
    # registry and scheduler dependencies of the rest of MPEG.cpp.
    start = source.index("        struct MpegDecodedFrame")
    end = source.index("#else\n        // TODO", start)
    return source[start:end] + "\n#endif\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", action="store_true")
    parser.add_argument("--corpus", type=Path, help="Optional elementary MPEG-video corpus")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PATH"] = str(FFMPEG / "bin") + os.pathsep + env.get("PATH", "")
    corpus = OUT / "synthetic.m2v"
    if not corpus.exists():
        subprocess.run([str(FFMPEG / "bin/ffmpeg.exe"), "-v", "error", "-f", "lavfi",
                        "-i", "testsrc2=size=128x96:rate=30000/1001", "-frames:v", "120",
                        "-c:v", "mpeg2video", "-bf", "2", "-g", "12", "-f", "mpeg2video",
                        str(corpus)], env=env, check=True)
    name = "eager" if args.baseline else "bounded"
    decoder = OUT / f"{name}_decoder.inc"
    if not args.baseline or not decoder.exists():
        code = decoder_source(SOURCE.read_text())
        if args.baseline:
            # On a fresh checkout, use the eager negative-control policy. An
            # existing pre-change snapshot is retained for historical comparison.
            code = code.replace("kDecodedLead = 4u", "kDecodedLead = std::numeric_limits<size_t>::max()")
        write_if_changed(decoder, code)
    test = (ROOT / "tests/mpeg_decode_queue_test.cpp").read_text()
    test = test.replace('"DECODER_SOURCE"', '"' + decoder.as_posix() + '"')
    cpp = OUT / f"{name}.cpp"
    write_if_changed(cpp, test)
    exe = OUT / f"{name}.exe"
    if not exe.exists() or exe.stat().st_mtime_ns < max(cpp.stat().st_mtime_ns, decoder.stat().st_mtime_ns):
        subprocess.run(["g++", "-std=c++20", "-O2", "-DMPEG_BASELINE=" + str(int(args.baseline)),
                        "-I" + str(FFMPEG / "include"), str(cpp), "-o", str(exe),
                        str(FFMPEG / "bin/avcodec.lib"), str(FFMPEG / "bin/avutil.lib"),
                        str(FFMPEG / "bin/swscale.lib")], check=True, env=env)
    corpus = args.corpus.resolve() if args.corpus else corpus
    counted = subprocess.run([str(FFMPEG / "bin/ffprobe.exe"), "-v", "error", "-select_streams", "v:0",
                              "-count_frames", "-show_entries", "stream=nb_read_frames", "-of",
                              "default=nokey=1:noprint_wrappers=1", str(corpus)],
                             check=True, env=env, capture_output=True, text=True)
    count = int(counted.stdout.strip())
    reference = OUT / (corpus.stem + "_reference.txt")
    subprocess.run([str(exe), str(corpus), str(reference), str(count)], check=True, env=env)


if __name__ == "__main__":
    main()
