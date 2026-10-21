#!/usr/bin/env python3
"""audio_post.py - ffmpeg/ffprobe wrapper for game-audio post-processing.

  normalize --in A --out B [--lufs -16] [--tp -1]     two-pass loudnorm (linear), EBU R128
  trim      --in A --out B [--start S] [--end E] [--fade F]   seconds; --fade adds in/out fades
  loop      --in A --out B [--bpm N --bars N] [--beats-per-bar 4] [--xfade 0.5]
                                                      seamless loop; length = bars*beats*60/bpm
                                                      (else source length minus crossfade).
                                                      Needs source >= loop length + crossfade.
  convert   --in A [--out B] --format ogg|m4a|wav     ogg: libvorbis, else native vorbis (upmixed to stereo), else opus
  qc        --in A [--lufs -16] [--tp -1]             LUFS (+-1.5 LU), true peak, clipping,
                                                      DC offset, duration, sample rate

Exit codes: 0 ok, 1 a QC check failed or ffmpeg failed, 2 usage/input error (incl. ffmpeg missing).
Requires ffmpeg + ffprobe on PATH (macOS: brew install ffmpeg).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

LUFS_TOL = 1.5
DC_MAX = 0.01
CODECS = {".wav": ["-c:a", "pcm_s16le"], ".m4a": ["-c:a", "aac", "-b:a", "128k"], ".flac": ["-c:a", "flac"]}


class AudioError(Exception):
    pass


def run(cmd: list[str]) -> str:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    if p.returncode != 0:
        raise AudioError("%s failed: %s" % (cmd[0], p.stderr.strip().splitlines()[-1] if p.stderr.strip() else p.returncode))
    return p.stderr + p.stdout


def ff(*args: str) -> list[str]:
    return ["ffmpeg", "-hide_banner", "-nostdin", "-y"] + list(args)


def probe(path: Path) -> dict:
    out = run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries",
               "stream=codec_name,sample_rate,channels:format=duration", "-of", "json", str(path)])
    d = json.loads(out)
    if not d.get("streams"):
        raise AudioError("no audio stream in %s" % path)
    s = d["streams"][0]
    return {"codec": s.get("codec_name"), "sample_rate": int(s.get("sample_rate", 0)), "channels": s.get("channels"),
            "duration": float(d.get("format", {}).get("duration", 0))}


def parse_loudnorm(stderr: str) -> dict:
    m = re.findall(r"\{[^{}]*\"input_i\"[^{}]*\}", stderr, re.S)
    if not m:
        raise AudioError("could not parse loudnorm output")
    d = json.loads(m[-1])
    return {k: float(v) for k, v in d.items() if k.startswith(("input_", "target_", "output_", "normalization"))
            and re.match(r"^-?[\d.]+$|^-?inf$", str(v))}


def measure(path: Path, lufs: float, tp: float) -> dict:
    err = run(ff("-i", str(path), "-af", "loudnorm=I=%s:TP=%s:LRA=11:print_format=json" % (lufs, tp), "-f", "null", "-"))
    return parse_loudnorm(err)


def astats(path: Path) -> dict:
    err = run(ff("-i", str(path), "-af", "astats=metadata=0:reset=0", "-f", "null", "-"))
    overall = err.split("Overall", 1)[-1]

    def g(key: str):
        m = re.search(r"%s:\s*(-?[\d.]+|-inf|inf)" % re.escape(key), overall)
        return float(m.group(1)) if m else None
    return {"peak_db": g("Peak level dB"), "dc_offset": g("DC offset"), "peak_count": g("Peak count")}


def codec_args(out: Path) -> list[str]:
    ext = out.suffix.lower()
    if ext == ".ogg":
        enc = run(["ffmpeg", "-hide_banner", "-encoders"])
        if "libvorbis" in enc:
            return ["-c:a", "libvorbis", "-q:a", "5"]
        if re.search(r"\svorbis\s", enc):
            return ["-c:a", "vorbis", "-strict", "-2", "-ac", "2", "-b:a", "128k"]  # native encoder is stereo-only
        return ["-c:a", "libopus", "-b:a", "128k"]
    return CODECS.get(ext, [])


def encode(src: Path, out: Path, af: str = "", extra: list[str] | None = None) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = ff("-i", str(src))
    if af:
        cmd += ["-af", af]
    run(cmd + (extra or []) + codec_args(out) + [str(out)])


def cmd_normalize(a: argparse.Namespace) -> dict:
    src, out = Path(a.input), Path(a.out)
    m = measure(src, a.lufs, a.tp)
    af = ("loudnorm=I=%s:TP=%s:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:offset=%s:linear=true"
          % (a.lufs, a.tp, m["input_i"], m["input_tp"], m["input_lra"], m["input_thresh"], m["target_offset"]))
    encode(src, out, af, ["-ar", str(probe(src)["sample_rate"])])
    after = measure(out, a.lufs, a.tp)
    return {"in": str(src), "out": str(out), "before_lufs": m["input_i"], "after_lufs": after["input_i"],
            "after_true_peak": after["input_tp"], "target_lufs": a.lufs, "target_tp": a.tp, "ok": True}


def cmd_trim(a: argparse.Namespace) -> dict:
    src, out = Path(a.input), Path(a.out)
    dur = probe(src)["duration"]
    start, end = a.start or 0.0, a.end if a.end is not None else dur
    if not (0 <= start < end <= dur + 0.01):
        raise AudioError("invalid range %.3f-%.3f for %.3fs source" % (start, end, dur))
    length = end - start
    af = "atrim=start=%s:end=%s,asetpts=PTS-STARTPTS" % (start, end)
    if a.fade:
        f = min(a.fade, length / 2)
        af += ",afade=t=in:d=%s,afade=t=out:st=%s:d=%s" % (f, length - f, f)
    encode(src, out, af)
    return {"in": str(src), "out": str(out), "start": start, "end": end, "duration": probe(out)["duration"], "ok": True}


def loop_length(source_dur: float, xfade: float, bpm=None, bars=None, beats=4) -> float:
    if bpm and bars:
        length = bars * beats * 60.0 / bpm
    elif bpm or bars:
        raise AudioError("--bpm and --bars must be given together")
    else:
        length = source_dur - xfade
    if length <= 2 * xfade:
        raise AudioError("loop length %.3fs too short for crossfade %.3fs" % (length, xfade))
    if source_dur + 0.01 < length + xfade:
        raise AudioError("source is %.3fs; need >= %.3fs (loop length + crossfade)" % (source_dur, length + xfade))
    return length


def cmd_loop(a: argparse.Namespace) -> dict:
    src, out = Path(a.input), Path(a.out)
    dur = probe(src)["duration"]
    length = loop_length(dur, a.xfade, a.bpm, a.bars, a.beats_per_bar)
    x = a.xfade
    # head fades in while the overshoot tail fades out over it, so the end flows back into the start
    fc = ("[0:a]atrim=0:%(t)s,asetpts=PTS-STARTPTS,asplit=3[h][b][tl];"
          "[h]atrim=0:%(x)s,asetpts=PTS-STARTPTS,afade=t=in:d=%(x)s[hi];"
          "[tl]atrim=%(l)s:%(t)s,asetpts=PTS-STARTPTS,afade=t=out:d=%(x)s[to];"
          "[hi][to]amix=inputs=2:duration=longest:normalize=0[mix];"
          "[b]atrim=%(x)s:%(l)s,asetpts=PTS-STARTPTS[body];"
          "[mix][body]concat=n=2:v=0:a=1[o]") % {"t": length + x, "x": x, "l": length}
    out.parent.mkdir(parents=True, exist_ok=True)
    run(ff("-i", str(src), "-filter_complex", fc, "-map", "[o]") + codec_args(out) + [str(out)])
    return {"in": str(src), "out": str(out), "loop_seconds": round(length, 3), "crossfade": x,
            "duration": probe(out)["duration"], "ok": True}


def cmd_convert(a: argparse.Namespace) -> dict:
    src = Path(a.input)
    if not a.format and not a.out:
        raise ValueError("convert needs --format or --out")
    out = Path(a.out) if a.out else src.with_suffix("." + a.format)
    if a.format and out.suffix.lower() != "." + a.format:
        out = out.with_suffix("." + a.format)
    encode(src, out)
    p = probe(out)
    return {"in": str(src), "out": str(out), "codec": p["codec"], "sample_rate": p["sample_rate"],
            "duration": p["duration"], "ok": True}


def qc_checks(p: dict, loud: dict, st: dict, lufs: float, tp: float) -> list[dict]:
    res = []

    def chk(name: str, ok: bool, msg: str) -> None:
        res.append({"check": name, "ok": ok, "message": msg})
    chk("loudness", abs(loud["input_i"] - lufs) <= LUFS_TOL, "integrated %.1f LUFS (target %s +-%s)" % (loud["input_i"], lufs, LUFS_TOL))
    chk("true_peak", loud["input_tp"] <= tp, "true peak %.1f dBTP (max %s)" % (loud["input_tp"], tp))
    pk = st["peak_db"]
    clipped = pk is not None and pk >= -0.01 and (st["peak_count"] is None or st["peak_count"] >= 3)
    chk("clipping", not clipped, "sample peak %s dBFS, %s samples at peak" % (pk, st["peak_count"]))
    dc = st["dc_offset"]
    chk("dc_offset", dc is None or abs(dc) < DC_MAX, "DC offset %s (max %s)" % (dc, DC_MAX))
    chk("duration", p["duration"] > 0.05, "duration %.3fs" % p["duration"])
    chk("sample_rate", p["sample_rate"] in (44100, 48000), "sample rate %d Hz (expected 44100 or 48000)" % p["sample_rate"])
    return res


def cmd_qc(a: argparse.Namespace) -> dict:
    src = Path(a.input)
    p, loud, st = probe(src), measure(src, a.lufs, a.tp), astats(src)
    checks = qc_checks(p, loud, st, a.lufs, a.tp)
    return {"in": str(src), "format": p, "lufs": loud["input_i"], "true_peak": loud["input_tp"], "lra": loud["input_lra"],
            "peak_db": st["peak_db"], "dc_offset": st["dc_offset"], "checks": checks, "ok": all(c["ok"] for c in checks)}


def selftest() -> int:
    d = loop_length(10.0, 0.5, 120, 2)  # 2 bars of 4/4 at 120 bpm = 4s
    assert abs(d - 4.0) < 1e-9 and abs(loop_length(10.0, 0.5) - 9.5) < 1e-9
    for bad in [(3.0, 0.5, 120, 2), (10, 0.5, 120, None)]:
        try:
            loop_length(*bad)
            raise SystemExit("expected AudioError")
        except AudioError:
            pass
    sample = 'x\n{\n\t"input_i" : "-20.50",\n\t"input_tp" : "-3.1",\n\t"input_lra" : "0.1",\n\t"input_thresh" : "-30.5",\n\t"target_offset" : "0.2"\n}\n'
    assert parse_loudnorm(sample)["input_i"] == -20.5
    ok = qc_checks({"duration": 1, "sample_rate": 48000}, {"input_i": -16.2, "input_tp": -2.0}, {"peak_db": -3, "dc_offset": 0.0, "peak_count": 1}, -16, -1)
    assert all(c["ok"] for c in ok)
    bad_qc = qc_checks({"duration": 1, "sample_rate": 22050}, {"input_i": -10, "input_tp": 0.5}, {"peak_db": 0.0, "dc_offset": 0.05, "peak_count": 9}, -16, -1)
    assert [c["check"] for c in bad_qc if c["ok"]] == ["duration"]
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        print("selftest ok (ffmpeg missing: ffmpeg-backed checks skipped)")
        return 0
    ns = lambda **k: argparse.Namespace(**{"lufs": -16.0, "tp": -1.0, "start": None, "end": None, "fade": None, "bpm": None, "bars": None,
                                           "beats_per_bar": 4, "xfade": 0.5, "format": None, "out": None, **k})
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        tone, hot = t / "tone.wav", t / "hot.wav"
        run(ff("-f", "lavfi", "-i", "sine=frequency=220:duration=10:sample_rate=48000", "-af", "volume=0.05", str(tone)))
        run(ff("-f", "lavfi", "-i", "sine=frequency=220:duration=2:sample_rate=48000", "-af", "volume=8", str(hot)))
        r = cmd_normalize(ns(input=str(tone), out=str(t / "n.wav")))
        assert abs(r["after_lufs"] + 16) <= 1.0, r
        assert cmd_qc(ns(input=str(t / "n.wav")))["ok"]
        assert abs(cmd_trim(ns(input=str(tone), out=str(t / "t.wav"), start=1.0, end=3.5, fade=0.1))["duration"] - 2.5) < 0.05
        r = cmd_loop(ns(input=str(tone), out=str(t / "l.wav"), bpm=120, bars=2))
        assert abs(r["duration"] - 4.0) < 0.05, r
        for fmt, codec in (("ogg", None), ("m4a", "aac"), ("wav", "pcm_s16le")):
            r = cmd_convert(ns(input=str(tone), out=str(t / ("c." + fmt)), format=fmt))
            assert (t / ("c." + fmt)).exists() and (codec is None or r["codec"] == codec), r
        q = cmd_qc(ns(input=str(hot)))
        assert not q["ok"] and not next(c for c in q["checks"] if c["check"] == "clipping")["ok"], q
    print("selftest ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="ffmpeg wrapper: normalize, trim, loop, convert, qc.")
    ap.add_argument("command", nargs="?", choices=["normalize", "trim", "loop", "convert", "qc"])
    ap.add_argument("--in", dest="input")
    ap.add_argument("--out")
    ap.add_argument("--lufs", type=float, default=-16.0)
    ap.add_argument("--tp", type=float, default=-1.0)
    ap.add_argument("--format", choices=["ogg", "m4a", "wav"])
    ap.add_argument("--start", type=float)
    ap.add_argument("--end", type=float)
    ap.add_argument("--fade", type=float)
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--bars", type=int)
    ap.add_argument("--beats-per-bar", type=int, default=4)
    ap.add_argument("--xfade", type=float, default=0.5)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if a.selftest:
        return selftest()
    if not a.command or not a.input or (a.command in ("normalize", "trim", "loop") and not a.out):
        print("error: command, --in (and --out for normalize/trim/loop) are required", file=sys.stderr)
        return 2
    if not Path(a.input).is_file():
        print("error: input not found: %s" % a.input, file=sys.stderr)
        return 2
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")):
        print("error: ffmpeg/ffprobe not found on PATH (brew install ffmpeg)", file=sys.stderr)
        return 2
    try:
        res = {"normalize": cmd_normalize, "trim": cmd_trim, "loop": cmd_loop, "convert": cmd_convert, "qc": cmd_qc}[a.command](a)
    except ValueError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    except (AudioError, KeyError) as e:
        res = {"ok": False, "error": str(e)}
    if a.json:
        print(json.dumps(res, indent=2))
    elif res.get("checks"):
        print("QC %s: %s" % (res["in"], "PASS" if res["ok"] else "FAIL"))
        print("\n".join("  [%s] %s: %s" % ("ok" if c["ok"] else "FAIL", c["check"], c["message"]) for c in res["checks"]))
    else:
        print(res.get("error") and "error: " + res["error"] or json.dumps({k: v for k, v in res.items() if k != "ok"}))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
