#!/usr/bin/env python3
"""compliance_preflight.py - store-compliance preflight for a Godot or Unity mobile project.

Inspects project.godot + export_presets.cfg (Godot) or ProjectSettings/ProjectSettings.asset
(Unity), plus generic checks driven by .gamestudio/config.json and contract.json.
Each check has: id, severity (blocker|warning|info), message, fix, source URL.

Generic checks read an optional "compliance" object from .gamestudio/config.json (falling back to
contract.json): privacy_policy_url, accounts (bool), account_deletion (bool|url),
att_usage_description (string), odds_disclosure (bool|url), coppa {child_directed, ...}.

Exit codes: 0 no blockers, 1 at least one blocker, 2 usage/input error.
Requirements are volatile: verify against the linked sources before release.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

APPLE_REQ = "https://developer.apple.com/news/upcoming-requirements/"
PLAY_TARGET = "https://developer.android.com/google/play/requirements/target-sdk"
PLAY_BILLING = "https://developer.android.com/google/play/billing/deprecation-faq"
PAGE16 = "https://developer.android.com/guide/practices/page-sizes"
GODOT16 = "https://forum.godotengine.org/t/godot-and-google-play-policy-warning-about-16-kb-memory-page-size/120934"
ATT_SRC = "https://developer.apple.com/documentation/apptrackingtransparency"
PRIVACY_MANIFEST = "https://developer.apple.com/documentation/bundleresources/privacy-manifest-files"
PLAY_DELETE = "https://support.google.com/googleplay/android-developer/answer/13327111"
APPLE_GUIDE = "https://developer.apple.com/app-store/review/guidelines/"
PLAY_POLICY = "https://support.google.com/googleplay/android-developer/topic/9858052"
KIDS = "https://developer.apple.com/app-store/kids-apps/"

REQUIREMENTS = [  # (platform, requirement, since/deadline, source)
    ("iOS", "Build with Xcode 26 / iOS 26 SDK or later", "since Apr 28, 2026", APPLE_REQ),
    ("iOS", "Minimum deployment target iOS 13 or later", "since Sep 9, 2026", APPLE_REQ),
    ("iOS", "Privacy manifest (PrivacyInfo.xcprivacy) + required-reason APIs", "since May 1, 2024", PRIVACY_MANIFEST),
    ("Android", "Target API 36 (Android 16)", "Aug 31, 2026 (extension to Nov 1, 2026)", PLAY_TARGET),
    ("Android", "Play Billing Library 8 or later", "Aug 31, 2026 (extension to Nov 1, 2026)", PLAY_BILLING),
    ("Android", "16 KB page-size support, 64-bit (Godot >= 4.5; NDK r28+ / AGP 8.5.1+)", "enforced since Nov 1, 2025", PAGE16),
]
MIN_GODOT = (4, 5)
DANGEROUS_PERMS = {"record_audio", "access_fine_location", "access_coarse_location", "camera",
                   "read_contacts", "read_external_storage", "write_external_storage",
                   "read_phone_state", "read_sms", "send_sms"}
SKIP_DIRS = {".git", ".godot", "node_modules", "Library", "Temp", "Builds", ".import"}


class Report:
    def __init__(self, platform: str) -> None:
        self.platform = platform
        self.checks: list[dict] = []

    def add(self, cid: str, sev: str, msg: str, fix: str = "", src: str = "", plat: str = "all") -> None:
        if self.platform != "all" and plat not in ("all", self.platform):
            return
        self.checks.append({"id": cid, "severity": sev, "platform": plat, "message": msg, "fix": fix, "source": src})

    def ok(self, cid: str, msg: str, plat: str = "all") -> None:
        self.add(cid, "info", "OK: " + msg, "", "", plat)


def parse_ini(text: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    sec = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(";"):
            continue
        m = re.match(r"^\[(.+)\]$", line)
        if m:
            sec = m.group(1)
            out.setdefault(sec, {})
        elif "=" in line:
            k, v = line.split("=", 1)
            out.setdefault(sec, {})[k.strip()] = v.strip().strip('"')
    return out


def ver_tuple(s: str) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", s)[:3]) or (0,)


def load_json(p: Path) -> dict:
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def find_files(root: Path, name: str, limit: int = 3, depth: int = 6) -> list[Path]:
    found: list[Path] = []

    def walk(d: Path, lvl: int) -> None:
        if lvl > depth or len(found) >= limit:
            return
        try:
            for c in sorted(d.iterdir()):
                if c.is_dir() and c.name not in SKIP_DIRS:
                    walk(c, lvl + 1)
                elif c.is_file() and c.name == name:
                    found.append(c)
        except OSError:
            pass
    walk(root, 0)
    return found


# ----------------------------------------------------------------------------- engines
def check_godot(root: Path, cfg: dict, rep: Report) -> dict:
    info = {"engine": "godot", "ios_manifest_in_preset": False, "att_in_preset": False}
    proj = parse_ini((root / "project.godot").read_text(encoding="utf-8", errors="replace"))
    feats = proj.get("application", {}).get("config/features", "")
    m = re.search(r'"(\d+\.\d+)"', feats)
    gv = m.group(1) if m else str(cfg.get("engine_version", "") or "")
    if not gv:
        rep.add("godot.version", "warning", "Godot version not found in project.godot features or config.engine_version.",
                "Set engine_version in .gamestudio/config.json.", GODOT16, "android")
    elif ver_tuple(gv)[:2] < MIN_GODOT:
        rep.add("godot.16kb", "blocker", "Godot %s predates the 16 KB page-size fix (needs >= 4.5)." % gv,
                "Upgrade to Godot 4.5+ and re-export.", GODOT16, "android")
    else:
        rep.ok("godot.16kb", "Godot %s >= 4.5 (16 KB pages)." % gv, "android")
    presets_path = root / "export_presets.cfg"
    if not presets_path.exists():
        rep.add("godot.presets", "blocker", "export_presets.cfg missing.", "Create Android/iOS export presets in the editor.", "", "all")
        return info
    ini = parse_ini(presets_path.read_text(encoding="utf-8", errors="replace"))
    for sec, kv in ini.items():
        if not re.match(r"^preset\.\d+$", sec):
            continue
        opts = ini.get(sec + ".options", {})
        plat = kv.get("platform", "")
        if plat == "Android":
            godot_android(kv, opts, rep)
        elif plat == "iOS":
            godot_ios(opts, rep, info)
    return info


def godot_android(kv: dict, opts: dict, rep: Report) -> None:
    if opts.get("gradle_build/use_gradle_build") != "true":
        rep.add("android.gradle", "blocker", "Gradle build disabled; Play Billing and AAB need a custom Gradle build.",
                "Enable Project > Install Android Build Template and use_gradle_build.", PLAY_BILLING, "android")
    if opts.get("gradle_build/export_format") not in ("1",):
        rep.add("android.aab", "blocker", "Export format is not AAB; Play requires Android App Bundles for new apps.",
                "Set gradle_build/export_format to Export AAB.", PLAY_TARGET, "android")
    if opts.get("architectures/arm64-v8a") != "true":
        rep.add("android.arm64", "blocker", "arm64-v8a disabled; Play requires 64-bit.", "Enable architectures/arm64-v8a.", PAGE16, "android")
    tsdk = opts.get("gradle_build/target_sdk", "")
    if not tsdk:
        rep.add("android.target_sdk", "warning", "target_sdk empty; the engine default applies and may be below 36.",
                "Set gradle_build/target_sdk to 36.", PLAY_TARGET, "android")
    elif ver_tuple(tsdk)[0] < 36:
        rep.add("android.target_sdk", "blocker", "target_sdk %s < 36." % tsdk, "Set gradle_build/target_sdk to 36.", PLAY_TARGET, "android")
    else:
        rep.ok("android.target_sdk", "target_sdk %s." % tsdk, "android")
    package_checks(opts.get("package/unique_name", ""), rep, "android")
    vc = opts.get("version/code", "")
    if not vc.isdigit() or int(vc) < 1:
        rep.add("android.version_code", "blocker", "version/code missing or < 1.", "Set a positive integer; raise it every upload.", PLAY_TARGET, "android")
    perms = sorted(k.split("/", 1)[1] for k, v in opts.items() if k.startswith("permissions/") and v == "true")
    risky = [p for p in perms if p in DANGEROUS_PERMS]
    if risky:
        rep.add("android.permissions", "warning", "Sensitive permissions requested: %s." % ", ".join(risky),
                "Remove unless the game needs them; declare in the Data safety form.", PLAY_POLICY, "android")
    else:
        rep.add("android.permissions", "info", "Permissions requested: %s." % (", ".join(perms) or "none"), "", "", "android")


def godot_ios(opts: dict, rep: Report, info: dict) -> None:
    mn = opts.get("application/min_ios_version", "")
    if not mn:
        rep.add("ios.min_version", "warning", "min_ios_version not set.", "Set application/min_ios_version to 13.0 or later.", APPLE_REQ, "ios")
    elif ver_tuple(mn) < (13,):
        rep.add("ios.min_version", "blocker", "min iOS version %s < 13." % mn, "Raise application/min_ios_version to 13.0+.", APPLE_REQ, "ios")
    else:
        rep.ok("ios.min_version", "min iOS %s." % mn, "ios")
    package_checks(opts.get("application/bundle_identifier", ""), rep, "ios")
    info["ios_manifest_in_preset"] = any(k.startswith("privacy/") for k in opts)
    info["att_in_preset"] = any("tracking" in k.lower() and v for k, v in opts.items() if "domains" not in k)


def package_checks(pkg: str, rep: Report, plat: str) -> None:
    cid = "%s.package" % plat
    if not pkg:
        rep.add(cid, "blocker", "Package / bundle id not set.", "Set a reverse-DNS id, e.g. com.yourstudio.game.", "", plat)
    elif pkg.startswith("com.example") or "$genname" in pkg:
        rep.add(cid, "warning", "Package id '%s' looks like a placeholder." % pkg, "Use your final reverse-DNS id; it cannot change after release.", "", plat)
    elif not re.match(r"^[A-Za-z][A-Za-z0-9_-]*(\.[A-Za-z][A-Za-z0-9_-]*)+$", pkg):
        rep.add(cid, "blocker", "Package id '%s' is not valid reverse-DNS." % pkg, "Use letters/digits/underscores in 2+ dot segments.", "", plat)
    else:
        rep.ok(cid, "package id %s." % pkg, plat)


def check_unity(root: Path, rep: Report) -> dict:
    info = {"engine": "unity", "ios_manifest_in_preset": False, "att_in_preset": False}
    text = (root / "ProjectSettings" / "ProjectSettings.asset").read_text(encoding="utf-8", errors="replace")

    def val(key: str) -> str:
        m = re.search(r"^\s*%s:\s*(.+)$" % re.escape(key), text, re.M)
        return m.group(1).strip() if m else ""

    def nested(key: str, sub: str) -> str:
        m = re.search(r"^\s*%s:\s*\n((?:\s{4,}.+\n)+)" % re.escape(key), text, re.M)
        if m:
            s = re.search(r"^\s*%s:\s*(.+)$" % re.escape(sub), m.group(1), re.M)
            return s.group(1).strip() if s else ""
        return ""
    t = val("AndroidTargetSdkVersion")
    if t in ("", "0"):
        rep.add("android.target_sdk", "warning", "Target API is 'Automatic (highest installed)'; result depends on the build machine.",
                "Pin Target API Level to 36 in Player Settings.", PLAY_TARGET, "android")
    elif int(t) < 36 if t.isdigit() else False:
        rep.add("android.target_sdk", "blocker", "Target API %s < 36." % t, "Set Target API Level to 36.", PLAY_TARGET, "android")
    else:
        rep.ok("android.target_sdk", "target API %s." % t, "android")
    if nested("scriptingBackend", "Android") != "1":
        rep.add("android.il2cpp", "blocker", "Android scripting backend is not IL2CPP; ARM64 requires IL2CPP.", "Player Settings > Scripting Backend = IL2CPP.", PAGE16, "android")
    arch = val("AndroidTargetArchitectures")
    if not arch.isdigit() or not int(arch) & 2:
        rep.add("android.arm64", "blocker", "ARM64 not enabled in target architectures.", "Enable ARM64 under Target Architectures.", PAGE16, "android")
    package_checks(nested("applicationIdentifier", "Android"), rep, "android")
    vc = val("AndroidBundleVersionCode")
    if not vc.isdigit() or int(vc) < 1:
        rep.add("android.version_code", "blocker", "Bundle Version Code missing or < 1.", "Set a positive integer; raise each upload.", PLAY_TARGET, "android")
    rep.add("android.billing", "info", "Verify the IAP package bundles Play Billing Library 8+ and 16 KB-aligned native libs (Unity 6 LTS).",
            "Check Unity IAP / RevenueCat versions in Packages/manifest.json.", PLAY_BILLING, "android")
    mn = val("iOSTargetOSVersionString")
    if not mn:
        rep.add("ios.min_version", "warning", "iOS target OS version not found.", "Set Target minimum iOS Version to 13.0+.", APPLE_REQ, "ios")
    elif ver_tuple(mn) < (13,):
        rep.add("ios.min_version", "blocker", "iOS target %s < 13." % mn, "Raise Target minimum iOS Version to 13.0+.", APPLE_REQ, "ios")
    else:
        rep.ok("ios.min_version", "min iOS %s." % mn, "ios")
    package_checks(nested("applicationIdentifier", "iPhone"), rep, "ios")
    return info


# ----------------------------------------------------------------------------- generic
def has_gacha(doc: dict) -> bool:
    return bool(re.search(r"gacha|loot ?box|random (reward|drop)|pity", json.dumps(doc).lower()))


def check_generic(root: Path, engine: dict, cfg: dict, contract: dict, rep: Report) -> None:
    comp = cfg.get("compliance") or contract.get("compliance") or {}
    meta = contract.get("meta", {})
    tech = contract.get("technical", {})
    mono = meta.get("monetization_model", "")
    # icons
    icons = [p for p in (root.rglob("*icon*.png") if root.exists() else []) if not (set(p.parts) & SKIP_DIRS)][:1]
    if engine["engine"] == "godot":
        icon = parse_ini((root / "project.godot").read_text(encoding="utf-8", errors="replace")).get("application", {}).get("config/icon", "")
        if icon.startswith("res://") and (root / icon[6:]).exists():
            icons = [root / icon[6:]]
    if icons:
        rep.ok("generic.icon", "app icon found (%s)." % icons[0].name)
    else:
        rep.add("generic.icon", "blocker", "No app icon found.", "Add a 1024x1024 icon (no alpha for iOS) and set it in project settings.", APPLE_GUIDE)
    # privacy policy
    url = comp.get("privacy_policy_url") or meta.get("privacy_url") or ""
    if re.match(r"^https://", str(url)):
        rep.ok("generic.privacy_policy", "privacy policy URL set.")
    else:
        rep.add("generic.privacy_policy", "blocker", "No https privacy policy URL in .gamestudio config/contract.",
                "Set compliance.privacy_policy_url in .gamestudio/config.json.", APPLE_GUIDE)
    # accounts
    accounts = comp.get("accounts") if "accounts" in comp else tech.get("backend", "none") not in ("none", "") and tech.get("multiplayer", "none") != "none"
    if accounts and not comp.get("account_deletion"):
        rep.add("generic.account_deletion", "blocker", "Accounts exist but no account-deletion flow is declared (in-app and web).",
                "Implement in-app deletion + a web deletion URL; set compliance.account_deletion.", PLAY_DELETE)
    # ATT
    ads_idfa = mono in ("ads", "hybrid") or bool(contract.get("monetization", {}).get("ads", {}).get("rewarded"))
    if ads_idfa:
        att = comp.get("att_usage_description") or engine.get("att_in_preset")
        if not att:
            for p in find_files(root, "Info.plist"):
                att = att or "NSUserTrackingUsageDescription" in p.read_text(errors="replace", encoding="utf-8")
        if att:
            rep.ok("ios.att", "ATT usage description present.", "ios")
        else:
            rep.add("ios.att", "blocker", "Ads detected but no NSUserTrackingUsageDescription / ATT string.",
                    "Add compliance.att_usage_description and the plist key; request ATT before IDFA use.", ATT_SRC, "ios")
    # privacy manifest
    if find_files(root, "PrivacyInfo.xcprivacy", 1) or engine.get("ios_manifest_in_preset"):
        rep.ok("ios.privacy_manifest", "privacy manifest present.", "ios")
    else:
        rep.add("ios.privacy_manifest", "warning", "No PrivacyInfo.xcprivacy found in the project.",
                "Add one declaring required-reason APIs; confirm SDK manifests (Firebase, ad SDKs).", PRIVACY_MANIFEST, "ios")
    # odds
    if has_gacha(contract) and not comp.get("odds_disclosure"):
        rep.add("generic.odds", "blocker", "Random-reward monetization detected but odds disclosure not declared.",
                "Show drop rates before purchase; set compliance.odds_disclosure.", APPLE_GUIDE)
    # COPPA
    age = meta.get("target_audience", {}).get("age_min")
    if isinstance(age, (int, float)) and age < 13:
        c = comp.get("coppa") or {}
        if not c.get("child_directed"):
            rep.add("generic.coppa", "blocker", "age_min %s < 13 but COPPA / child-directed flags not set." % age,
                    "Set compliance.coppa.child_directed; use child-directed ad settings; no behavioral ads or IDFA.", KIDS)
        elif ads_idfa:
            rep.add("generic.coppa_ads", "warning", "Child-directed app with ads: use certified family-safe ad networks only.",
                    "Disable personalised ads and IDFA/ATT.", PLAY_POLICY)


# ----------------------------------------------------------------------------- main
def run(project: Path, platform: str) -> dict:
    rep = Report(platform)
    cfg = load_json(project / ".gamestudio" / "config.json")
    contract = load_json(project / ".gamestudio" / "contract.json")
    if (project / "project.godot").exists():
        eng = check_godot(project, cfg, rep)
    elif (project / "ProjectSettings" / "ProjectSettings.asset").exists():
        eng = check_unity(project, rep)
    else:
        eng = {"engine": "unknown", "ios_manifest_in_preset": False, "att_in_preset": False}
        rep.add("engine.detect", "warning", "Neither project.godot nor ProjectSettings.asset found; engine checks skipped.",
                "Pass the project root.", "")
    check_generic(project, eng, cfg, contract, rep)
    plats = {"ios": "iOS", "android": "Android"}
    reqs = [r for r in REQUIREMENTS if platform == "all" or r[0] == plats[platform]]
    counts = {s: sum(1 for c in rep.checks if c["severity"] == s) for s in ("blocker", "warning", "info")}
    return {"as_of": "Oct 2026", "engine": eng["engine"], "platform": platform,
            "requirements": [dict(zip(("platform", "requirement", "deadline", "source"), r)) for r in reqs],
            "checks": rep.checks, "counts": counts, "verdict": "fail" if counts["blocker"] else "pass"}


def render(res: dict) -> str:
    out = ["Store requirements (as of Oct 2026 - verify before relying)", ""]
    out.append("| Platform | Requirement | Deadline | Source |")
    out.append("|---|---|---|---|")
    out += ["| %s | %s | %s | %s |" % (r["platform"], r["requirement"], r["deadline"], r["source"]) for r in res["requirements"]]
    out += ["", "Engine: %s   Platform: %s" % (res["engine"], res["platform"]), ""]
    order = {"blocker": 0, "warning": 1, "info": 2}
    for c in sorted(res["checks"], key=lambda c: order[c["severity"]]):
        out.append("[%s] %s: %s" % (c["severity"].upper(), c["id"], c["message"]))
        if c["severity"] != "info" and c["fix"]:
            out.append("    fix: %s" % c["fix"])
        if c["severity"] != "info" and c["source"]:
            out.append("    src: %s" % c["source"])
    n = res["counts"]
    out += ["", "Verdict: %s (%d blockers, %d warnings)" % (res["verdict"].upper(), n["blocker"], n["warning"])]
    return "\n".join(out)


def selftest() -> int:
    def w(p: Path, s: str) -> None:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(s, encoding="utf-8")
    ok_opts = ('gradle_build/use_gradle_build=true\ngradle_build/export_format=1\narchitectures/arm64-v8a=true\n'
               'gradle_build/target_sdk="36"\npackage/unique_name="com.acme.tiles"\nversion/code=3\npermissions/internet=true\n')
    with tempfile.TemporaryDirectory() as td:
        good, bad, uni = Path(td) / "good", Path(td) / "bad", Path(td) / "unity"
        w(good / "project.godot", '[application]\nconfig/features=PackedStringArray("4.5", "Mobile")\nconfig/icon="res://icon.png"\n')
        w(good / "icon.png", "x")
        w(good / "PrivacyInfo.xcprivacy", "<plist/>")
        w(good / "export_presets.cfg", '[preset.0]\nplatform="Android"\n[preset.0.options]\n' + ok_opts +
          '[preset.1]\nplatform="iOS"\n[preset.1.options]\napplication/min_ios_version="14.0"\napplication/bundle_identifier="com.acme.tiles"\n')
        w(good / ".gamestudio" / "config.json", json.dumps({"compliance": {"privacy_policy_url": "https://acme.test/privacy"}}))
        w(good / ".gamestudio" / "contract.json", json.dumps({"meta": {"monetization_model": "premium", "target_audience": {"age_min": 13}}}))
        r = run(good, "all")
        assert r["verdict"] == "pass", [c for c in r["checks"] if c["severity"] == "blocker"]
        w(bad / "project.godot", '[application]\nconfig/features=PackedStringArray("4.3")\n')
        w(bad / "export_presets.cfg", '[preset.0]\nplatform="Android"\n[preset.0.options]\ngradle_build/target_sdk="34"\n'
          'package/unique_name="com.example.x"\n[preset.1]\nplatform="iOS"\n[preset.1.options]\napplication/min_ios_version="12.0"\n')
        w(bad / ".gamestudio" / "contract.json", json.dumps({"meta": {"monetization_model": "hybrid", "target_audience": {"age_min": 8}},
                                                              "economy": {"note": "gacha pity"}, "technical": {"backend": "firebase", "multiplayer": "async"}}))
        r = run(bad, "all")
        ids = {c["id"] for c in r["checks"] if c["severity"] == "blocker"}
        want = {"godot.16kb", "android.gradle", "android.aab", "android.arm64", "android.target_sdk", "android.version_code",
                "ios.min_version", "generic.icon", "generic.privacy_policy", "generic.account_deletion", "ios.att", "generic.odds", "generic.coppa"}
        assert want <= ids, want - ids
        assert all(c["platform"] in ("all", "ios") for c in run(bad, "ios")["checks"])
        w(uni / "ProjectSettings" / "ProjectSettings.asset",
          "PlayerSettings:\n  AndroidTargetSdkVersion: 34\n  AndroidTargetArchitectures: 1\n  AndroidBundleVersionCode: 1\n"
          "  iOSTargetOSVersionString: 12.0\n  applicationIdentifier:\n    Android: com.acme.u\n    iPhone: com.acme.u\n"
          "  scriptingBackend:\n    Android: 0\n")
        r = run(uni, "all")
        ids = {c["id"] for c in r["checks"] if c["severity"] == "blocker"}
        assert {"android.target_sdk", "android.il2cpp", "android.arm64", "ios.min_version"} <= ids, ids
        assert "as of Oct 2026" in render(r)
    print("selftest ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Store-compliance preflight for Godot/Unity mobile projects.")
    ap.add_argument("--project", help="project root directory")
    ap.add_argument("--platform", choices=["ios", "android", "all"], default="all")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if a.selftest:
        return selftest()
    if not a.project or not Path(a.project).is_dir():
        print("error: --project must be an existing directory", file=sys.stderr)
        return 2
    res = run(Path(a.project), a.platform)
    print(json.dumps(res, indent=2) if a.json else render(res))
    return 1 if res["verdict"] == "fail" else 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
