#!/usr/bin/env python3
"""store_metadata.py - generate a fastlane metadata tree from the design contract.

Output (under --out):
  fastlane/metadata/<locale>/{name,subtitle,description,keywords,promotional_text,release_notes,
                              privacy_url,support_url}.txt                       (deliver / App Store)
  fastlane/metadata/android/<locale>/{title,short_description,full_description}.txt
  fastlane/metadata/android/<locale>/changelogs/<versionCode>.txt                (supply / Google Play)

Text is drafted from contract.meta (title, logline, genre, pillars, ...). Optional overrides live in
contract["store"] = {"name","subtitle","description","keywords","promotional_text","release_notes",
"short_description","full_description","privacy_url","support_url","version_code"} (a field may also
be a {locale: text} map). Non-default locales get the same English draft and are flagged
needs_translation: translate them before upload. Limits are enforced; drafted fields are shortened
at a word boundary, overridden fields over the limit are reported as errors.

Limits: App Store name/subtitle 30, keywords 100, promotional text 170, description 4000.
        Play title 30, short description 80, full description 4000.
Exit codes: 0 ok, 1 limit violations or placeholder URLs, 2 usage/input error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

LIMITS = {"name": 30, "subtitle": 30, "keywords": 100, "promotional_text": 170, "description": 4000,
          "release_notes": 4000, "title": 30, "short_description": 80, "full_description": 4000}
PLACEHOLDER = "https://example.com/"
STOP = {"a", "an", "the", "and", "or", "of", "to", "in", "for", "with", "your", "you", "is", "it", "on", "game"}


def fit(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit - 1]
    if " " in cut:
        cut = cut.rsplit(" ", 1)[0]
    return cut.rstrip(" ,;:-.") + "…" if limit > 40 else cut.rstrip(" ,;:-.")


def fit_block(text: str, limit: int) -> str:
    return text if len(text) <= limit else fit(text, limit)


def pick(store: dict, key: str, locale: str, default: str):
    """Return (text, overridden)."""
    v = store.get(key)
    if isinstance(v, dict):
        v = v.get(locale) or v.get(locale.split("-")[0])
    return (str(v), True) if v else (default, False)


def keywords(meta: dict, name: str) -> str:
    seen = {w.lower() for w in re.findall(r"[A-Za-z0-9']+", name)}
    words: list[str] = []
    for src in [meta.get("genre", ""), meta.get("subgenre", ""), meta.get("analogy", "")] + list(meta.get("pillars", [])):
        for w in re.findall(r"[A-Za-z0-9]+", str(src).lower()):
            if w not in seen and w not in STOP and len(w) > 2:
                seen.add(w)
                words.append(w)
    out = ""
    for w in words:
        nxt = (out + "," + w) if out else w
        if len(nxt) > LIMITS["keywords"]:
            break
        out = nxt
    return out


def draft(contract: dict, locale: str) -> dict:
    meta, store = contract.get("meta", {}), contract.get("store", {})
    title = meta.get("title") or contract.get("title") or "Untitled"
    logline = meta.get("logline") or meta.get("analogy") or ""
    pillars = [str(p) for p in meta.get("pillars", [])]
    body = "\n\n".join(filter(None, [
        logline,
        ("What you will love:\n" + "\n".join("- " + p for p in pillars)) if pillars else "",
        {"premium": "One purchase, no ads.", "iap": "Free to play with optional in-app purchases.",
         "ads": "Free to play with optional ads.", "hybrid": "Free to play with optional ads and in-app purchases.",
         "subscription": "Optional subscription."}.get(meta.get("monetization_model", ""), "")]))
    base = {
        "name": title, "title": title,
        "subtitle": logline or meta.get("genre", ""),
        "short_description": logline or title,
        "description": body, "full_description": body,
        "promotional_text": logline,
        "release_notes": "Initial release.",
    }
    out: dict = {"_overridden": set()}
    for k, v in base.items():
        text, over = pick(store, k if k != "title" else "name", locale, v)  # the Play title shares the App Store name override
        if k in ("description", "full_description") and k not in store and "description" in store:
            text, over = pick(store, "description", locale, v)
        if over:
            out["_overridden"].add(k)
        out[k] = text if over or k in ("name", "title") else fit_block(text, LIMITS[k]) if k in ("description", "full_description", "release_notes") else fit(text, LIMITS[k])
    kw, over = pick(store, "keywords", locale, keywords(meta, out["name"]))
    out["keywords"] = kw
    if over:
        out["_overridden"].add("keywords")
    out["privacy_url"] = pick(store, "privacy_url", locale, meta.get("privacy_url") or PLACEHOLDER + "privacy")[0]
    out["support_url"] = pick(store, "support_url", locale, meta.get("support_url") or PLACEHOLDER + "support")[0]
    return out


def validate(vals: dict, locale: str) -> list[dict]:
    issues = []
    for field, limit in LIMITS.items():
        if field in vals and len(vals[field]) > limit:
            issues.append({"locale": locale, "field": field, "severity": "error",
                           "message": "%s is %d chars, limit %d" % (field, len(vals[field]), limit)})
    for field in ("name", "title", "subtitle", "short_description", "description", "full_description"):
        if field in vals and not vals[field].strip():
            issues.append({"locale": locale, "field": field, "severity": "error", "message": field + " is empty"})
    for field in ("privacy_url", "support_url"):
        if vals[field].startswith(PLACEHOLDER):
            issues.append({"locale": locale, "field": field, "severity": "warning",
                           "message": "%s is a placeholder; set contract.meta.%s" % (field, field)})
    return issues


def generate(contract: dict, out: Path, locales: list[str]) -> dict:
    version_code = str(contract.get("store", {}).get("version_code") or contract.get("meta", {}).get("version_code") or 1)
    files: list[str] = []
    issues: list[dict] = []
    for i, loc in enumerate(locales):
        vals = draft(contract, loc)
        issues += validate(vals, loc)
        if i > 0 or loc.split("-")[0] != "en":
            issues.append({"locale": loc, "field": "*", "severity": "warning", "message": "text is the English draft; needs_translation"})
        ios = out / "fastlane" / "metadata" / loc
        andr = out / "fastlane" / "metadata" / "android" / loc
        plan = [(ios, "name", "name"), (ios, "subtitle", "subtitle"), (ios, "description", "description"),
                (ios, "keywords", "keywords"), (ios, "promotional_text", "promotional_text"),
                (ios, "release_notes", "release_notes"), (ios, "privacy_url", "privacy_url"), (ios, "support_url", "support_url"),
                (andr, "title", "title"), (andr, "short_description", "short_description"),
                (andr, "full_description", "full_description"),
                (andr / "changelogs", "release_notes", version_code)]
        for d, key, fname in plan:
            d.mkdir(parents=True, exist_ok=True)
            p = d / (fname + ".txt")
            p.write_text(vals[key].rstrip("\n") + "\n", encoding="utf-8")
            files.append(str(p.relative_to(out)))
    errs = [x for x in issues if x["severity"] == "error"]
    warns = [x for x in issues if x["severity"] == "warning" and x["field"] != "*"]
    return {"out": str(out), "locales": locales, "version_code": version_code, "files": files, "issues": issues,
            "verdict": "fail" if (errs or warns) else "pass"}


def selftest() -> int:
    long_title = "Z" * 40
    assert len(fit("word " * 100, 30)) <= 30 and len(fit("short", 30)) == 5
    kw = keywords({"genre": "Puzzle", "pillars": ["Calm sliding tiles", "Tiny handcrafted levels"]}, "Tile Drift")
    assert kw and len(kw) <= 100 and " " not in kw and "tile" not in kw.split(","), kw
    with tempfile.TemporaryDirectory() as td:
        out = Path(td)
        c = {"meta": {"title": "Tile Drift", "logline": "Slide calm tiles into place across hand-built puzzles that never rush you.",
                      "genre": "puzzle", "pillars": ["Calm", "Tactile"], "monetization_model": "premium",
                      "privacy_url": "https://acme.test/p", "support_url": "https://acme.test/s"}, "store": {"version_code": 7}}
        r = generate(c, out, ["en-US", "de-DE"])
        assert r["verdict"] == "pass" or all(i["severity"] == "warning" for i in r["issues"]), r["issues"]
        for rel in ["fastlane/metadata/en-US/name.txt", "fastlane/metadata/android/de-DE/changelogs/7.txt",
                    "fastlane/metadata/android/en-US/short_description.txt"]:
            assert (out / rel).exists(), rel
        assert len((out / "fastlane/metadata/en-US/subtitle.txt").read_text(encoding="utf-8").strip()) <= 30
        assert len((out / "fastlane/metadata/android/en-US/short_description.txt").read_text(encoding="utf-8").strip()) <= 80
        c["store"]["name"] = long_title
        r = generate(c, out, ["en-US"])
        assert r["verdict"] == "fail" and any(i["field"] == "name" and i["severity"] == "error" for i in r["issues"])
        r = generate({"meta": {"title": "X"}}, out, ["en-US"])
        assert any(i["field"] == "privacy_url" for i in r["issues"]) and r["verdict"] == "fail"
    print("selftest ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Generate fastlane store metadata from the design contract.")
    ap.add_argument("--contract", help="path to .gamestudio/contract.json")
    ap.add_argument("--out", help="output directory (fastlane/ tree is created inside)")
    ap.add_argument("--locales", default="en-US", help="comma-separated locales, default en-US")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if a.selftest:
        return selftest()
    if not a.contract or not a.out:
        print("error: --contract and --out are required", file=sys.stderr)
        return 2
    try:
        contract = json.loads(Path(a.contract).read_text(encoding="utf-8"))
        assert isinstance(contract, dict)
    except (OSError, ValueError, AssertionError) as e:
        print("error: cannot read contract: %s" % e, file=sys.stderr)
        return 2
    locales = [x.strip() for x in a.locales.split(",") if x.strip()]
    if not locales or not all(re.match(r"^[a-z]{2,3}(-[A-Za-z0-9]{2,4})?$", x) for x in locales):
        print("error: invalid --locales", file=sys.stderr)
        return 2
    res = generate(contract, Path(a.out), locales)
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        print("Wrote %d files to %s (version code %s)" % (len(res["files"]), res["out"], res["version_code"]))
        for i in res["issues"]:
            print("  [%s] %s %s: %s" % (i["severity"], i["locale"], i["field"], i["message"]))
        print("Verdict: " + res["verdict"].upper())
    return 1 if res["verdict"] == "fail" else 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
