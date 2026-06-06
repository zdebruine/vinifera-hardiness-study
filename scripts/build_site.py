#!/usr/bin/env python3
"""Build the static site's data layer from the seed CSVs.

Reads ``data/seed/*.csv``, joins related tables, runs the implemented closed-form math
(ripening normal-CDF + score combination from ``src/vinifera``), and writes JSON into
``site/data/`` for the client-side tools to consume.

Stdlib only -- the GitHub Pages workflow runs this without installing dependencies.

NOTE: seed values are illustrative samples, not sourced measurements (see
``data/seed/README.md``). Uncertainties here are first-order MVP estimates tied to the
stated caveats (ERA5 ~regional temperature bias; GDD variability), not formal posteriors.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "data" / "seed"
OUT = ROOT / "site" / "data"

sys.path.insert(0, str(ROOT / "src"))
from vinifera import ripening, score  # noqa: E402

# MVP uncertainty inputs, tied to documented caveats.
SIGMA_HARDINESS_C = 2.5      # spread of bud LT50 around its point estimate
TMIN_BIAS_C = 2.0           # ERA5 regional-vs-site temperature uncertainty (Stage 1 caveat)
GDD_UNCERTAINTY_F = 150.0   # season-to-season / siting GDD uncertainty


def _norm_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def read_csv(name: str) -> list[dict]:
    with (SEED / name).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def p_survive(tmin_c: float, lt50_c: float) -> tuple[float, float]:
    """P(survive) = P(event minimum warmer than LT50), with a finite-difference sd.

    Closed-form normal CDF of the standardized thermal surplus; sd from perturbing the
    (regionally biased) event minimum by TMIN_BIAS_C.
    """
    surplus = tmin_c - lt50_c
    p = _norm_cdf(surplus / SIGMA_HARDINESS_C)
    p_lo = _norm_cdf((surplus - TMIN_BIAS_C) / SIGMA_HARDINESS_C)
    p_hi = _norm_cdf((surplus + TMIN_BIAS_C) / SIGMA_HARDINESS_C)
    return p, abs(p_hi - p_lo) / 2.0


def main() -> int:
    varieties = read_csv("varieties.csv")
    synonyms = read_csv("synonyms.csv")
    pedigree = read_csv("pedigree.csv")
    sites = read_csv("sites.csv")
    freeze_events = read_csv("freeze_events.csv")
    minima = read_csv("site_freeze_minima.csv")
    lt50_rows = read_csv("lt50.csv")
    ripening_rows = read_csv("ripening_req.csv")
    colocation = read_csv("colocation.csv")
    survival_obs = read_csv("survival_obs.csv")

    name_by_id = {v["variety_id"]: v["prime_name"] for v in varieties}
    syn_by_id: dict[str, list[str]] = {}
    for s in synonyms:
        syn_by_id.setdefault(s["variety_id"], []).append(s["synonym"])
    ped_by_id = {p["variety_id"]: p for p in pedigree}
    lt50_by_id = {r["variety_id"]: float(r["lt50_c"]) for r in lt50_rows}
    req_by_id = {
        r["variety_id"]: ripening.RipeningRequirement(
            variety_id=r["variety_id"], gdd_req_f=float(r["gdd_req_f"]), sigma_f=float(r["sigma_f"])
        )
        for r in ripening_rows
    }

    # Coldest recorded seed minimum per site (the screening event).
    coldest: dict[str, dict] = {}
    for m in minima:
        sid, t = m["site_id"], float(m["tmin_c"])
        if sid not in coldest or t < coldest[sid]["tmin_c"]:
            coldest[sid] = {"tmin_c": t, "event_label": m["event_label"]}

    # Enrich varieties.
    varieties_out = []
    for v in varieties:
        vid = v["variety_id"]
        ped = ped_by_id.get(vid)
        parents = []
        if ped:
            for pid in (ped["parent1_id"], ped["parent2_id"]):
                if pid:
                    parents.append({"id": pid, "name": name_by_id.get(pid, pid)})
        varieties_out.append({
            **v,
            "synonyms": syn_by_id.get(vid, []),
            "parents": parents,
            "pedigree_note": ped["note"] if ped else "",
            "lt50_c": lt50_by_id.get(vid),
            "gdd_req_f": float(req_by_id[vid].gdd_req_f) if vid in req_by_id else None,
            "ripening_sigma_f": float(req_by_id[vid].sigma_f) if vid in req_by_id else None,
        })

    sites_out = []
    for s in sites:
        sid = s["site_id"]
        sites_out.append({
            **s,
            "latitude": float(s["latitude"]),
            "longitude": float(s["longitude"]),
            "gdd_winkler_f": float(s["gdd_winkler_f"]),
            "burial_flag": s["burial_flag"] == "1",
            "coldest_event": coldest.get(sid),
        })

    # Suitability matrix: variety x site, both axes + product with propagated uncertainty.
    suitability = []
    for v in varieties:
        vid = v["variety_id"]
        if vid not in req_by_id or vid not in lt50_by_id:
            continue
        req = req_by_id[vid]
        for s in sites_out:
            p_rip = ripening.p_ripen(s["gdd_winkler_f"], req)
            p_rip_lo = ripening.p_ripen(s["gdd_winkler_f"] - GDD_UNCERTAINTY_F, req)
            p_rip_hi = ripening.p_ripen(s["gdd_winkler_f"] + GDD_UNCERTAINTY_F, req)
            p_rip_sd = abs(p_rip_hi - p_rip_lo) / 2.0
            ce = s["coldest_event"]
            if ce is None:
                continue
            p_sur, p_sur_sd = p_survive(ce["tmin_c"], lt50_by_id[vid])
            sc = score.combine(p_sur, p_sur_sd, p_rip, p_rip_sd, variety_id=vid, site_id=s["site_id"])
            suitability.append({
                "variety_id": vid,
                "variety_name": name_by_id[vid],
                "site_id": s["site_id"],
                "site_name": s["name"],
                "event_label": ce["event_label"],
                "event_tmin_c": ce["tmin_c"],
                "burial_flag": s["burial_flag"],
                "p_survive": round(sc.p_survive, 4),
                "p_survive_sd": round(sc.p_survive_sd, 4),
                "p_ripen": round(sc.p_ripen, 4),
                "p_ripen_sd": round(sc.p_ripen_sd, 4),
                "suitability": round(sc.suitability, 4),
                "suitability_sd": round(sc.suitability_sd, 4),
            })

    OUT.mkdir(parents=True, exist_ok=True)
    bundles = {
        "varieties.json": varieties_out,
        "sites.json": sites_out,
        "freeze_events.json": freeze_events,
        "site_minima.json": minima,
        "lt50.json": lt50_rows,
        "ripening.json": ripening_rows,
        "colocation.json": colocation,
        "survival.json": survival_obs,
        "suitability.json": suitability,
        "meta.json": {
            "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "data_status": "seed/illustrative -- not sourced measurements",
            "params": {
                "sigma_hardiness_c": SIGMA_HARDINESS_C,
                "tmin_bias_c": TMIN_BIAS_C,
                "gdd_uncertainty_f": GDD_UNCERTAINTY_F,
            },
            "counts": {
                "varieties": len(varieties_out),
                "sites": len(sites_out),
                "lt50": len(lt50_rows),
                "suitability_cells": len(suitability),
            },
        },
    }
    for fname, payload in bundles.items():
        with (OUT / fname).open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        print(f"  wrote site/data/{fname}")

    print(f"\nBuilt {len(bundles)} JSON bundles into {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
