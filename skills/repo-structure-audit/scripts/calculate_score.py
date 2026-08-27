#!/usr/bin/env python3
"""Calculate repo-structure audit totals from rubric percentages."""

import argparse
import json
from fractions import Fraction


WEIGHTS = {
    "C1": 15, "C2": 10,
    "C3": 10, "C4": 8, "C5": 7,
    "C6": 10, "C7": 8, "C8": 7,
    "C9": 13, "C10": 12,
}
GROUPS = {
    "Navigability": ("C1", "C2"),
    "Ownership": ("C3", "C4", "C5"),
    "Lifecycle": ("C6", "C7", "C8"),
    "Hygiene": ("C9", "C10"),
}
ALLOWED_PERCENTAGES = {0, 20, 40, 60, 80, 100}


def display_number(value):
    number = round(float(value), 1)
    return int(number) if number.is_integer() else number


def score_band(score):
    if score >= 85:
        return "Maintained"
    if score >= 70:
        return "Solid"
    if score >= 50:
        return "Drifting"
    if score >= 30:
        return "Tangled"
    return "Unstructured"


def parse_assignments(parser, raw_assignments):
    values = {}
    for raw in raw_assignments:
        if "=" not in raw:
            parser.error(f"assignment must look like C1=80, C8=pending, or C10=na: {raw}")
        check, raw_value = raw.split("=", 1)
        check = check.upper()
        value = raw_value.lower()
        if check not in WEIGHTS:
            parser.error(f"unknown check: {check}")
        if check in values:
            parser.error(f"duplicate assignment: {check}")
        if value in {"pending", "na"}:
            values[check] = value
            continue
        try:
            percentage = int(value.rstrip("%"))
        except ValueError:
            parser.error(f"invalid value for {check}: {raw_value}")
        if percentage not in ALLOWED_PERCENTAGES:
            parser.error("allowed earned percentages are 0, 20, 40, 60, 80, and 100")
        values[check] = percentage

    missing = [check for check in WEIGHTS if check not in values]
    if missing:
        parser.error(f"missing assignments: {', '.join(missing)}")
    return values


def calculate(values):
    adjusted_max = {}
    for checks in GROUPS.values():
        applicable = [check for check in checks if values[check] != "na"]
        if not applicable:
            raise ValueError("every group needs at least one applicable check")
        base_total = sum(WEIGHTS[check] for check in applicable)
        for check in applicable:
            adjusted_max[check] = Fraction(25 * WEIGHTS[check], base_total)

    groups = {}
    total_earned = Fraction(0)
    total_available = Fraction(0)
    total_pending = Fraction(0)
    pending_checks = []
    na_checks = []

    for group_name, checks in GROUPS.items():
        earned = available = pending = Fraction(0)
        for check in checks:
            value = values[check]
            if value == "na":
                na_checks.append(check)
                continue
            maximum = adjusted_max[check]
            if value == "pending":
                pending += maximum
                pending_checks.append(check)
            else:
                available += maximum
                earned += maximum * value / 100
        groups[group_name] = {
            "earned": display_number(earned),
            "available": display_number(available),
            "pending": display_number(pending),
        }
        total_earned += earned
        total_available += available
        total_pending += pending

    assessed_percent = (
        display_number(total_earned / total_available * 100) if total_available else 0
    )
    final_score = None if pending_checks else display_number(total_earned)
    return {
        "assessed": {
            "earned": display_number(total_earned),
            "available": display_number(total_available),
            "percent": assessed_percent,
        },
        "full_score_range": {
            "minimum": display_number(total_earned),
            "maximum": display_number(total_earned + total_pending),
        },
        "pending_checks": pending_checks,
        "na_checks": na_checks,
        "groups": groups,
        "final_score": final_score,
        "band": score_band(final_score) if final_score is not None else None,
    }


def render_text(result):
    assessed = result["assessed"]
    lines = [
        f"Assessed: {assessed['earned']}/{assessed['available']} "
        f"({assessed['percent']}%)"
    ]
    if result["pending_checks"]:
        score_range = result["full_score_range"]
        pending = ", ".join(result["pending_checks"])
        lines.append(
            f"Full-score range: {score_range['minimum']}–{score_range['maximum']}/100 "
            f"pending {pending}"
        )
    else:
        lines.append(f"Final: {result['final_score']}/100 — {result['band']}")
    for name, group in result["groups"].items():
        if group["pending"]:
            lines.append(
                f"{name}: {group['earned']}/{group['available']} assessed; "
                f"{group['pending']} pending (25 total)"
            )
        else:
            lines.append(f"{name}: {group['earned']}/{group['available']}")
    if result["na_checks"]:
        lines.append(f"N/A with within-group redistribution: {', '.join(result['na_checks'])}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate P1-P10 audit totals from earned percentages."
    )
    parser.add_argument("assignments", nargs="+", help="C1=80, C8=pending, or C10=na")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = parser.parse_args()
    values = parse_assignments(parser, args.assignments)
    try:
        result = calculate(values)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2) if args.json else render_text(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
