#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
documented_effort.py  —  PM-First Rebuild, Step 4: mine DOCUMENTED effort from W3F text
========================================================================================
The git signal (any flavour) is internally coherent but does not converge with planned/cost
(Experiment 1). To anchor a defensible PM we need effort that humans actually WROTE DOWN.
This miner harvests every documented effort/resource signal from the W3F grant *applications*
and *milestone-delivery* files - authentic, public, and independent of git:

  per project (the same census grouping as harvest_deliveries):
    - planned_fte, planned_duration_months, planned_cost_usd, planned_pm   (top-level budget)
    - team_size                  : number of named team members (a real documented headcount)
    - sum_milestone_duration_months : summed per-milestone "Estimated Duration" (weeks->months)
    - n_milestone_fte_mentions   : count of per-milestone FTE statements
    - documented_pm_explicit     : effort stated IN WORDS (person-months/weeks/days/hours),
                                   normalised to person-months and summed (the closest thing to
                                   a self-reported actual that exists in the public record)
    - effort_phrases_raw         : the raw matched phrases, for human audit (never trust blindly)

These become (a) additional indicators for the latent true-effort model (Step 3) and (b) a
documentary anchor to validate absolute PM, reducing reliance on a developer survey.

Reuses harvest_deliveries (clone, app index, primary-repo pick, planned regexes). stdlib only.
Output: data/calibration/documented_effort.csv
"""
import argparse, csv, glob, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harvest_deliveries as H

# ── documented-effort extractors (independent of git) ───────────────────────────────────
# explicit effort stated in words. Normalise each unit to person-months.
PM_PER = {"month": 1.0, "week": 1.0/4.345, "day": 1.0/19.0, "hour": 1.0/152.0}
EFFORT_PHRASE = re.compile(
    r"(\d+(?:\.\d+)?)\s*"
    r"(person[\s-]?month|person[\s-]?week|person[\s-]?day|person[\s-]?hour|"
    r"man[\s-]?month|man[\s-]?week|man[\s-]?day|man[\s-]?hour|"
    r"engineer[\s-]?month|developer[\s-]?month|staff[\s-]?month|"
    r"month|week|day|hour)s?\b", re.I)
# we only trust an explicit phrase as EFFORT when it carries a person/man/engineer/... qualifier;
# bare "month/week/day/hour" matches are kept in the raw column but NOT summed (too ambiguous).
EFFORT_QUALIFIED = re.compile(r"(person|man|engineer|developer|staff)[\s-]?(month|week|day|hour)", re.I)

MS_DUR = re.compile(r"Estimated Duration:\*\*\s*([\d.]+)\s*(week|month)", re.I)
MS_FTE = re.compile(r"\bFTE:?\*\*?\s*([\d.]+)", re.I)
TEAM_HDR = re.compile(r"(?im)^#+\s*team\s*members?\b|team\s*members?\s*:?\*\*")

def team_size(txt):
    m = TEAM_HDR.search(txt)
    if not m:
        return ""
    tail = txt[m.end():m.end()+2000]
    tail = re.split(r"(?m)^#+\s", tail)[0]                  # stop at next heading
    bullets = re.findall(r"(?m)^\s*(?:[-*]|\d+\.)\s+\S+", tail)
    if bullets:
        return len(bullets)
    # comma-separated names on the heading line / next line
    nxt = tail.strip().splitlines()[0] if tail.strip() else ""
    names = [x for x in re.split(r",| and ", nxt) if len(x.strip()) > 1]
    return len(names) if 1 < len(names) <= 30 else ""

def documented_pm_explicit(txt):
    total, raw = 0.0, []
    for val, unit in EFFORT_PHRASE.findall(txt):
        u = unit.lower()
        raw.append(f"{val} {unit}")
        if EFFORT_QUALIFIED.search(unit) or "person" in u or "man" in u or "engineer" in u \
           or "developer" in u or "staff" in u:
            base = next((k for k in PM_PER if k in u), None)
            if base:
                try: total += float(val) * PM_PER[base]
                except ValueError: pass
    return (round(total, 3) if total > 0 else ""), "; ".join(raw[:12])

def milestone_signals(txt):
    months = 0.0; n = 0
    for val, unit in MS_DUR.findall(txt):
        try:
            v = float(val); months += v * (1.0/4.345 if unit.lower().startswith("week") else 1.0); n += 1
        except ValueError:
            pass
    return (round(months, 2) if n else ""), n, len(MS_FTE.findall(txt))

def find_application_text(app_index, key, primary):
    """Return (text, url) of the matched application, mirroring harvest_deliveries matching."""
    target = primary.lower().replace("https://github.com/", "") if primary else ""
    if target:
        for (apf, stem, txt, url) in app_index:
            if target in txt.lower():
                return txt, url
    for exact in (True, False):
        for (apf, stem, txt, url) in app_index:
            s = H.slug(stem)
            hit = (s == key) if exact else (s and (s.startswith(key) or key.startswith(s)
                   or (len(key) >= 6 and key in s) or (len(s) >= 6 and s in key)))
            if hit:
                return txt, url
    return "", ""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="resolve_cache")
    ap.add_argument("--out", default="data/calibration/documented_effort.csv")
    a = ap.parse_args()

    deliv = os.path.join(a.cache, "deliv"); grants = os.path.join(a.cache, "grants")
    general = os.path.join(a.cache, "general")
    os.makedirs(a.cache, exist_ok=True)
    if not H.clone(H.DELIV_URL, deliv, shallow=False):
        sys.exit("[FATAL] could not clone delivery repo.")
    have_g = H.clone(H.GRANTS_URL, grants, shallow=True)
    have_gg = H.clone(H.GENERAL_GRANTS_URL, general, shallow=True)
    app_index = H.build_app_index(grants if have_g else "", general if have_gg else "")
    print(f"[info] application index: {len(app_index)} files")

    files = [f for f in glob.glob(os.path.join(deliv, "deliveries", "*.md"))
             if not os.path.basename(f).startswith(".")
             and "template" not in os.path.basename(f).lower()]
    groups, display = {}, {}
    for f in files:
        stem = H.project_key(os.path.basename(f)); gkey = H.slug(stem)
        if not gkey: continue
        groups.setdefault(gkey, []).append(f)
        display.setdefault(gkey, {}).setdefault(stem, 0); display[gkey][stem] += 1

    FIELDS = ["project_id", "repo_url", "application_url", "n_delivery_files",
              "planned_fte", "planned_duration_months", "planned_cost_usd", "planned_pm",
              "team_size", "sum_milestone_duration_months", "n_milestone_fte_mentions",
              "documented_pm_explicit", "effort_phrases_raw", "status", "note"]
    out = []
    n_explicit = n_team = 0
    for key in sorted(groups):
        gfiles = sorted(groups[key])
        pid = max(display[key], key=lambda s: display[key][s])
        all_repos = []
        deliv_txt = ""
        for f in gfiles:
            t = open(f, encoding="utf-8", errors="ignore").read(); deliv_txt += "\n" + t
            for x in H.repos_in_text(t):
                if x not in all_repos: all_repos.append(x)
        primary, own, shared = H.pick_primary(all_repos, key)
        if not primary:
            out.append({**{k: "" for k in FIELDS}, "project_id": pid,
                        "n_delivery_files": len(gfiles), "status": "NO_REPO"}); continue
        repo_url = "https://github.com/" + primary
        app_txt, app_url = find_application_text(app_index, key, repo_url)
        corpus = (app_txt or "") + "\n" + deliv_txt          # scan application AND delivery text

        fte = dur = cost = ""
        p = H._parse_planned(app_txt, app_url) if app_txt else None
        if p: fte, dur, cost, _ = p
        planned_pm = ""
        try:
            if fte and dur: planned_pm = f"{float(fte)*float(dur):.2f}"
        except ValueError: pass

        ts = team_size(app_txt) if app_txt else ""
        ms_dur, ms_n, ms_fte_n = milestone_signals(corpus)
        dpm, raw = documented_pm_explicit(corpus)
        if dpm != "": n_explicit += 1
        if ts != "": n_team += 1

        out.append(dict(project_id=pid, repo_url=repo_url, application_url=app_url,
                        n_delivery_files=len(gfiles), planned_fte=fte,
                        planned_duration_months=dur, planned_cost_usd=cost, planned_pm=planned_pm,
                        team_size=ts, sum_milestone_duration_months=ms_dur,
                        n_milestone_fte_mentions=ms_fte_n, documented_pm_explicit=dpm,
                        effort_phrases_raw=raw, status="OK", note=""))

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS); w.writeheader(); w.writerows(out)
    ok = sum(1 for r in out if r["status"] == "OK")
    print(f"Projects: {len(out)} | OK {ok} | with team_size {n_team} | with explicit documented PM {n_explicit}")
    print(f"Wrote {a.out}")

if __name__ == "__main__":
    main()
