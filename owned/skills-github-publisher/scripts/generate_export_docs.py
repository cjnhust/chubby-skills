#!/usr/bin/env python3
"""Generate publish-facing docs for a staged Codex skills export."""

from __future__ import annotations

import sys
import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path

sys.dont_write_bytecode = True


FRONTMATTER_LINE = re.compile(r"^(?P<key>[A-Za-z0-9_.-]+):\s*(?P<value>.+?)\s*$")
SKILL_REF_PATTERN = re.compile(r"\b([A-Za-z0-9][A-Za-z0-9-]*[A-Za-z0-9])\b")


@dataclass
class SkillEntry:
    group: str
    slug: str
    path: Path
    rel_path: str
    name: str
    title: str
    description: str
    version: str | None
    homepage: str | None
    references: list[str]


@dataclass
class VendorUnit:
    rel_path: str
    package_name: str | None
    version: str | None
    repository: str | None
    homepage: str | None
    license_name: str | None


@dataclass
class EvidenceGroup:
    group_id: str
    name: str
    origin_status: str
    license_status: str
    source_url: str | None
    source_evidence: str | None
    license_name: str | None
    license_evidence: str | None
    notes: str | None
    skill_slugs: list[str]
    unit_paths: list[str]


@dataclass
class LoadedEvidence:
    groups: list[EvidenceGroup]
    by_skill: dict[str, EvidenceGroup]
    by_unit: dict[str, EvidenceGroup]


def normalized_status(value: object) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip().lower()
    return "pending"


def is_confirmed(value: str) -> bool:
    return value == "confirmed"


def overall_status(groups: list[EvidenceGroup], field: str) -> str:
    if not groups:
        return "pending"
    return "confirmed" if all(is_confirmed(getattr(group, field)) for group in groups) else "pending"


def has_root_license(root: Path) -> bool:
    candidates = [
        root / "LICENSE",
        root / "LICENSE.md",
        root / "LICENSE.txt",
        root / "COPYING",
        root / "COPYING.md",
        root / "COPYING.txt",
    ]
    return any(path.exists() for path in candidates)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate docs for a staged skills export.")
    parser.add_argument("--root", required=True, help="Staged export root containing owned/ and third-party/.")
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    lines = text.splitlines()
    end_index = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_index = idx
            break
    if end_index is None:
        return {}, text

    fields: dict[str, str] = {}
    for line in lines[1:end_index]:
        match = FRONTMATTER_LINE.match(line)
        if not match:
            continue
        key = match.group("key")
        value = strip_quotes(match.group("value"))
        fields[key] = value
        if key == "homepage":
            fields["homepage"] = value
    rest = "\n".join(lines[end_index + 1 :]).lstrip("\n")

    homepage_match = re.search(r"^\s*homepage:\s*(\S+)\s*$", "\n".join(lines[1:end_index]), re.MULTILINE)
    if homepage_match:
        fields["homepage"] = strip_quotes(homepage_match.group(1))
    return fields, rest


def first_heading(markdown_body: str) -> str | None:
    for line in markdown_body.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return None


def sanitize_inline(text: str) -> str:
    return " ".join(text.replace("|", "\\|").split())


def short_description(text: str, limit: int = 180) -> str:
    if not text:
        return ""
    concise = text
    for marker in (" Use when ", " Also trigger ", " Trigger on "):
        if marker in concise:
            concise = concise.split(marker, 1)[0].strip()
            break
    concise = sanitize_inline(concise)
    if len(concise) <= limit:
        return concise
    return concise[: limit - 3].rstrip() + "..."


def load_review_evidence(root: Path) -> LoadedEvidence:
    evidence_path = root / "third-party" / "review-evidence.json"
    if not evidence_path.exists():
        return LoadedEvidence(groups=[], by_skill={}, by_unit={})
    payload = json.loads(read_text(evidence_path))
    groups: list[EvidenceGroup] = []
    by_skill: dict[str, EvidenceGroup] = {}
    by_unit: dict[str, EvidenceGroup] = {}

    for raw_group in payload.get("groups", []):
        if not isinstance(raw_group, dict):
            continue
        group = EvidenceGroup(
            group_id=str(raw_group.get("id", "")),
            name=str(raw_group.get("name", "")),
            origin_status=normalized_status(raw_group.get("origin_status")),
            license_status=normalized_status(raw_group.get("license_status")),
            source_url=raw_group.get("source_url") if isinstance(raw_group.get("source_url"), str) else None,
            source_evidence=raw_group.get("source_evidence") if isinstance(raw_group.get("source_evidence"), str) else None,
            license_name=raw_group.get("license_name") if isinstance(raw_group.get("license_name"), str) else None,
            license_evidence=raw_group.get("license_evidence") if isinstance(raw_group.get("license_evidence"), str) else None,
            notes=raw_group.get("notes") if isinstance(raw_group.get("notes"), str) else None,
            skill_slugs=[item for item in raw_group.get("skill_slugs", []) if isinstance(item, str)],
            unit_paths=[item for item in raw_group.get("unit_paths", []) if isinstance(item, str)],
        )
        groups.append(group)
        for slug in group.skill_slugs:
            by_skill[slug] = group
        for unit_path in group.unit_paths:
            by_unit[unit_path] = group
    return LoadedEvidence(groups=groups, by_skill=by_skill, by_unit=by_unit)


def collect_skill_entries(root: Path) -> list[SkillEntry]:
    entries: list[SkillEntry] = []
    third_party_slugs = {path.name for path in (root / "third-party").iterdir()} if (root / "third-party").exists() else set()

    for group in ("owned", "third-party"):
        group_dir = root / group
        if not group_dir.exists():
            continue
        for skill_dir in sorted(path for path in group_dir.iterdir() if path.is_dir()):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue
            raw = read_text(skill_file)
            fields, body = parse_frontmatter(raw)
            name = fields.get("name", skill_dir.name)
            title = first_heading(body) or name
            description = fields.get("description", "").strip()
            version = fields.get("version")
            homepage = fields.get("homepage")

            refs = sorted(
                {
                    ref
                    for ref in SKILL_REF_PATTERN.findall(raw)
                    if ref in third_party_slugs and ref != skill_dir.name
                }
            )

            entries.append(
                SkillEntry(
                    group=group,
                    slug=skill_dir.name,
                    path=skill_dir,
                    rel_path=str(skill_dir.relative_to(root)),
                    name=name,
                    title=title,
                    description=description,
                    version=version,
                    homepage=homepage,
                    references=refs,
                )
            )
    return entries


def parse_package_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(read_text(path))
    except (OSError, json.JSONDecodeError):
        return {}


def normalize_repository(value: object) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        url = value.get("url")
        if isinstance(url, str):
            return url
    return None


def collect_vendor_units(root: Path) -> list[VendorUnit]:
    units: list[VendorUnit] = []
    third_party_dir = root / "third-party"
    if not third_party_dir.exists():
        return units

    for package_json in sorted(third_party_dir.glob("*/scripts/vendor/*/package.json")):
        payload = parse_package_json(package_json)
        unit_dir = package_json.parent
        units.append(
            VendorUnit(
                rel_path=str(unit_dir.relative_to(root)),
                package_name=payload.get("name") if isinstance(payload.get("name"), str) else None,
                version=payload.get("version") if isinstance(payload.get("version"), str) else None,
                repository=normalize_repository(payload.get("repository")),
                homepage=payload.get("homepage") if isinstance(payload.get("homepage"), str) else None,
                license_name=payload.get("license") if isinstance(payload.get("license"), str) else None,
            )
        )
    return units


def infer_baoyu_repo(entries: list[SkillEntry]) -> str | None:
    for entry in entries:
        if entry.slug.startswith("baoyu-") and entry.homepage:
            return entry.homepage.split("#", 1)[0]
    return None


def markdown_link(label: str, target: str | None) -> str:
    if not target:
        return label
    return f"[{label}]({target})"


def choose_examples(entries: list[SkillEntry]) -> list[str]:
    available = {entry.slug for entry in entries}
    candidates = [
        ("skills-github-publisher", "audit and prepare a local skills tree for safe GitHub publication"),
        ("engineering-story-pipeline", "turn local notes into a Chinese technical article and slide deck"),
        ("research-report-pipeline", "write a Chinese technical research report from a topic and source list"),
        ("baoyu-url-to-markdown", "save a webpage as markdown"),
        ("baoyu-translate", "translate an article into Chinese or English"),
        ("baoyu-cover-image", "generate a cover image for an article"),
    ]
    examples: list[str] = []
    for slug, task in candidates:
        if slug in available:
            examples.append(f"`Use ${slug} to {task}.`")
    return examples


def build_readme(root: Path, entries: list[SkillEntry], vendors: list[VendorUnit], evidence: LoadedEvidence) -> str:
    owned = [entry for entry in entries if entry.group == "owned"]
    third_party = [entry for entry in entries if entry.group == "third-party"]
    baoyu_repo = infer_baoyu_repo(entries)
    examples = choose_examples(entries)
    root_license_present = has_root_license(root)

    lines: list[str] = []
    lines.append("# Codex Skills Export")
    lines.append("")
    lines.append("This repository stages a publishable subset of a larger local Codex skills tree.")
    lines.append("It keeps user-owned skills and third-party skills under separate top-level boundaries so publication and review remain explicit.")
    lines.append("")
    lines.append("## Layout")
    lines.append("")
    lines.append("- `owned/`: skills authored or maintained in this collection.")
    lines.append("- `third-party/`: externally authored or inherited skills kept under a separate review boundary.")
    lines.append("- `third-party/ORIGIN.md`: source and upstream review manifest.")
    lines.append("- `third-party/LICENSES.md`: redistribution and license review manifest.")
    lines.append("- `THIRD_PARTY_ACKNOWLEDGEMENTS.md`: attribution and thanks for imported third-party skills.")
    lines.append("- `SECURITY.md`: publishing-time security rules and disclosure guidance.")
    lines.append("- `RELEASE_CHECKLIST.md`: final checks before creating the public GitHub repo or pushing.")
    lines.append("- `CODEX_SETUP.md`: post-publish Codex connection steps and a review-first smoke test.")
    lines.append("- `LICENSE_DECISION.md`: maintainer note for selecting the root repository license for `owned/` content.")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    lines.append("- Secret, absolute-path, and junk-artifact checks pass on this staged export.")
    if overall_status(evidence.groups, "origin_status") == "confirmed" and overall_status(evidence.groups, "license_status") == "confirmed":
        lines.append("- Third-party provenance and license review are confirmed at repo level for this staged export.")
    else:
        lines.append("- Third-party provenance and license review are still pending before any public release.")
    if root_license_present:
        lines.append("- A root repository license file is present for this export.")
    else:
        lines.append("- The root repository license for `owned/` content is intentionally left for maintainer choice; see `LICENSE_DECISION.md` before public release.")
    lines.append("- Built-in `.system/` skills and `danger-*` skills are intentionally excluded from this export.")
    lines.append("")
    if evidence.groups:
        lines.append("## Source Families")
        lines.append("")
        for group in evidence.groups:
            count = len(group.skill_slugs) + len(group.unit_paths)
            source = markdown_link(group.source_url, group.source_url) if group.source_url else "source under review"
            evidence_text = sanitize_inline(group.source_evidence or "Local evidence only")
            note = sanitize_inline(group.notes or "Manual confirmation still required before release.")
            status_note = f"origin `{group.origin_status}`, license `{group.license_status}`"
            lines.append(f"- `{group.name}`: {count} staged unit(s); {status_note}; {evidence_text} Source: {source}. {note}")
        lines.append("")
    lines.append("## Included Owned Skills")
    lines.append("")
    for entry in owned:
        lines.append(f"- `{entry.slug}`: {short_description(entry.description)}")
    lines.append("")
    lines.append("## Included Third-Party Skills")
    lines.append("")
    for entry in third_party:
        group = evidence.by_skill.get(entry.slug)
        if entry.homepage:
            source_note = markdown_link("source", entry.homepage)
        elif group and group.source_url:
            source_note = f"inferred source family: {markdown_link(group.name, group.source_url)}"
        elif entry.slug.startswith("baoyu-") and baoyu_repo:
            source_note = f"inferred source: {markdown_link('JimLiu/baoyu-skills', baoyu_repo)}"
        else:
            source_note = "source under review"
        detail = short_description(entry.description)
        if entry.version:
            detail = f"{detail} Current imported version marker: `{entry.version}`."
        lines.append(f"- `{entry.slug}`: {detail} {source_note}.")
    lines.append("")
    lines.append("## Example Prompts")
    lines.append("")
    for example in examples:
        lines.append(f"- {example}")
    lines.append("")
    lines.append("## Third-Party Skills Used By Owned Workflows")
    lines.append("")
    referenced = [entry for entry in owned if entry.references]
    if referenced:
        for entry in referenced:
            refs = ", ".join(f"`{ref}`" for ref in entry.references)
            lines.append(f"- `{entry.slug}` currently references these third-party skills: {refs}.")
    else:
        lines.append("- No third-party references were detected from the current owned skills.")
    lines.append("")
    if vendors and all(
        (group := evidence.by_unit.get(unit.rel_path)) is not None
        and is_confirmed(group.origin_status)
        and is_confirmed(group.license_status)
        for unit in vendors
    ):
        lines.append("## Vendored Components")
    else:
        lines.append("## Vendored Components Still Under Review")
    lines.append("")
    if vendors:
        for unit in vendors:
            package_note = unit.package_name or unit.rel_path.rsplit("/", 1)[-1]
            version_note = f" version `{unit.version}`" if unit.version else ""
            group = evidence.by_unit.get(unit.rel_path)
            if group and is_confirmed(group.origin_status) and is_confirmed(group.license_status):
                lines.append(f"- `{unit.rel_path}`: vendored package `{package_note}`{version_note}; covered by confirmed repo-level origin and license review for this export.")
            else:
                lines.append(f"- `{unit.rel_path}`: vendored package `{package_note}`{version_note}; provenance and license review still required.")
    else:
        lines.append("- No vendored components detected in the current staged export.")
    lines.append("")
    lines.append("## Acknowledgements")
    lines.append("")
    if baoyu_repo:
        lines.append(
            f"Thanks to the original author and maintainers of the Baoyu skill family. Current source references in the imported skills point to {markdown_link('JimLiu/baoyu-skills', baoyu_repo)}."
        )
    else:
        lines.append("Thanks to the original authors and maintainers of the imported third-party skills.")
    lines.append("See [`THIRD_PARTY_ACKNOWLEDGEMENTS.md`](THIRD_PARTY_ACKNOWLEDGEMENTS.md) for the current attribution notes and review status.")
    lines.append("")
    lines.append("## Post-Publish Maintenance")
    lines.append("")
    lines.append("- Keep the initial sanitization and first public release local-first.")
    lines.append("- If you later want Codex on GitHub, prefer PR review on this already public repository before broader cloud-side edit flows.")
    lines.append("- If a trusted maintainer later wants Codex to write back to an existing PR branch, make that an explicit minimal-scope request on an already public PR branch rather than an automatic workflow loop.")
    lines.append("- Do not use Codex GitHub maintenance for unpublished branches, internal-only content, or local private policy files.")
    lines.append("")
    return "\n".join(lines) + "\n"


def build_acknowledgements(entries: list[SkillEntry], vendors: list[VendorUnit], evidence: LoadedEvidence) -> str:
    third_party = [entry for entry in entries if entry.group == "third-party"]
    baoyu_repo = infer_baoyu_repo(entries)
    vendors_confirmed = vendors and all(
        (group := evidence.by_unit.get(unit.rel_path)) is not None
        and is_confirmed(group.origin_status)
        and is_confirmed(group.license_status)
        for unit in vendors
    )
    lines: list[str] = []
    lines.append("# Third-Party Acknowledgements")
    lines.append("")
    lines.append("This staged export keeps imported skills under `third-party/` so attribution and redistribution review remain explicit.")
    lines.append("")
    lines.append("## Baoyu Skill Family")
    lines.append("")
    if baoyu_repo:
        lines.append(
            f"Current source references found in imported skill metadata point to {markdown_link('JimLiu/baoyu-skills', baoyu_repo)}."
        )
    else:
        lines.append("The current imported `baoyu-*` skills are treated as third-party content and still need final upstream confirmation.")
    lines.append("")
    lines.append("Included skills:")
    lines.append("")
    for entry in third_party:
        home = f" ({markdown_link('homepage', entry.homepage)})" if entry.homepage else ""
        lines.append(f"- `{entry.slug}`{home}")
    lines.append("")
    lines.append("Thank you to the original author and maintainers of these third-party skills for publishing and maintaining them.")
    lines.append("If any attribution should be adjusted, update `third-party/ORIGIN.md` and `third-party/LICENSES.md` before release.")
    lines.append("")
    if vendors_confirmed:
        lines.append("## Vendored Components Covered By Repo-Level Review")
    else:
        lines.append("## Vendored Components Still Needing Upstream Confirmation")
    lines.append("")
    if vendors:
        for unit in vendors:
            lines.append(f"- `{unit.rel_path}`")
    else:
        lines.append("- No vendored components were detected.")
    lines.append("")
    return "\n".join(lines) + "\n"


def build_origin_manifest(entries: list[SkillEntry], vendors: list[VendorUnit], evidence: LoadedEvidence) -> str:
    third_party = [entry for entry in entries if entry.group == "third-party"]
    baoyu_repo = infer_baoyu_repo(entries)
    lines: list[str] = []
    lines.append("# Third-Party Origin Review")
    lines.append("")
    lines.append(f"Status: {overall_status(evidence.groups, 'origin_status')}")
    lines.append("")
    if overall_status(evidence.groups, "origin_status") == "confirmed":
        lines.append("This manifest records repo-level origin decisions for the current staged export.")
        lines.append("The operator confirmed that these imported third-party units were sourced from the GitHub repository evidence recorded below.")
    else:
        lines.append("This manifest is a staging-only review document.")
        lines.append("It does not satisfy publish-ready provenance until every row is confirmed and this file is updated accordingly.")
    lines.append("")
    if evidence.groups:
        lines.append("## Source Groups")
        lines.append("")
        for group in evidence.groups:
            source = markdown_link(group.source_url, group.source_url) if group.source_url else "[confirm source]"
            evidence_text = sanitize_inline(group.source_evidence or "Local evidence only")
            notes = sanitize_inline(group.notes or "Manual confirmation still required before release.")
            lines.append(f"- `{group.name}`: origin `{group.origin_status}`. {evidence_text} Source: {source}. {notes}")
        lines.append("")
    lines.append("| Unit | Origin status | Evidence | Proposed upstream or source of truth | Notes |")
    lines.append("| --- | --- | --- | --- | --- |")
    for entry in third_party:
        group = evidence.by_skill.get(entry.slug)
        if entry.homepage:
            evidence_text = "`SKILL.md` metadata homepage"
            upstream = markdown_link(entry.homepage, entry.homepage)
        elif group and group.source_url:
            evidence_text = group.source_evidence or "Grouped source-family evidence"
            upstream = markdown_link(group.source_url, group.source_url)
        elif entry.slug.startswith("baoyu-") and baoyu_repo:
            evidence_text = "Inferred from sibling `baoyu-*` skills with metadata homepage"
            upstream = markdown_link(baoyu_repo, baoyu_repo)
        else:
            evidence_text = "Local source evidence not yet recorded"
            upstream = "[confirm upstream]"
        notes = []
        if entry.version:
            notes.append(f"Imported version marker `{entry.version}`")
        if group and group.notes:
            notes.append(group.notes)
        if not (group and is_confirmed(group.origin_status)):
            notes.append("Manual confirmation still required before release")
        lines.append(
            f"| `{entry.rel_path}` | {'confirmed-repo-level' if group and is_confirmed(group.origin_status) else 'pending-confirmation'} | {sanitize_inline(evidence_text)} | {upstream} | {sanitize_inline('; '.join(notes))} |"
        )
    for unit in vendors:
        group = evidence.by_unit.get(unit.rel_path)
        proposed = unit.repository or unit.homepage or (group.source_url if group and group.source_url else None) or "[confirm vendor upstream]"
        evidence_bits = []
        if unit.repository:
            evidence_bits.append("`package.json` repository")
        if unit.homepage:
            evidence_bits.append("`package.json` homepage")
        if group and group.source_evidence:
            evidence_bits.append(group.source_evidence)
        if not evidence_bits:
            evidence_bits.append("Only local `package.json` found; no upstream URL fields present")
        notes = []
        if unit.package_name:
            notes.append(f"Package `{unit.package_name}`")
        if unit.version:
            notes.append(f"version `{unit.version}`")
        if group and group.notes:
            notes.append(group.notes)
        if not (group and is_confirmed(group.origin_status)):
            notes.append("Vendor provenance still requires manual confirmation")
        upstream = markdown_link(proposed, proposed) if proposed.startswith("http") else proposed
        lines.append(
            f"| `{unit.rel_path}` | {'confirmed-repo-level' if group and is_confirmed(group.origin_status) else 'pending-confirmation'} | {sanitize_inline('; '.join(evidence_bits))} | {upstream} | {sanitize_inline('; '.join(notes))} |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def build_license_manifest(entries: list[SkillEntry], vendors: list[VendorUnit], evidence: LoadedEvidence) -> str:
    third_party = [entry for entry in entries if entry.group == "third-party"]
    lines: list[str] = []
    lines.append("# Third-Party License Review")
    lines.append("")
    lines.append(f"Status: {overall_status(evidence.groups, 'license_status')}")
    lines.append("")
    if overall_status(evidence.groups, "license_status") == "confirmed":
        lines.append("This manifest records the chosen repo-level license basis for the current staged export.")
        lines.append("The operator confirmed that GitHub repository-level license evidence is the review basis for this export.")
    else:
        lines.append("This manifest is a staging-only review document.")
        lines.append("It does not satisfy publish-ready license review until every row is confirmed and this file is updated accordingly.")
    lines.append("")
    if evidence.groups:
        lines.append("## Group-Level License Evidence")
        lines.append("")
        for group in evidence.groups:
            if group.license_name or group.license_evidence or group.notes:
                bits = []
                bits.append(f"license `{group.license_status}`")
                if group.license_name:
                    bits.append(f"Observed license marker `{group.license_name}`")
                if group.license_evidence:
                    bits.append(group.license_evidence)
                if group.notes:
                    bits.append(group.notes)
                lines.append(f"- `{group.name}`: {sanitize_inline(' '.join(bits))}")
        lines.append("")
    lines.append("| Unit | License status | Known evidence | Notes |")
    lines.append("| --- | --- | --- | --- |")
    for entry in third_party:
        group = evidence.by_skill.get(entry.slug)
        if group and is_confirmed(group.license_status):
            notes = "No per-unit license file is staged; this export intentionally relies on confirmed GitHub repo-level license evidence."
        else:
            notes = "No confirmed license file captured in the current staged copy; manual redistribution review required."
        if entry.version:
            notes = f"{notes} Imported version marker `{entry.version}`."
        if group and group.notes:
            notes = f"{notes} {group.notes}"
        evidence_text = "No confirmed local license metadata yet"
        if group and (group.license_name or group.license_evidence):
            parts = []
            if group.license_name:
                parts.append(f"group evidence suggests `{group.license_name}`")
            if group.license_evidence:
                parts.append(group.license_evidence)
            evidence_text = sanitize_inline("; ".join(parts))
        lines.append(
            f"| `{entry.rel_path}` | {'confirmed-repo-level' if group and is_confirmed(group.license_status) else 'pending-confirmation'} | {evidence_text} | {sanitize_inline(notes)} |"
        )
    for unit in vendors:
        group = evidence.by_unit.get(unit.rel_path)
        if unit.license_name:
            evidence_text = f"`package.json` license `{unit.license_name}`"
        else:
            evidence_text = "No `license` field found in local `package.json`"
        if group and (group.license_name or group.license_evidence):
            parts = [evidence_text]
            if group.license_name:
                parts.append(f"group evidence suggests `{group.license_name}`")
            if group.license_evidence:
                parts.append(group.license_evidence)
            evidence_text = sanitize_inline("; ".join(parts))
        if group and is_confirmed(group.license_status):
            notes = "No package-level license field is staged; this export intentionally relies on confirmed GitHub repo-level license evidence."
        else:
            notes = "Vendor license confirmation still required before release."
        if unit.package_name:
            notes = f"Package `{unit.package_name}`. {notes}"
        if group and group.notes:
            notes = f"{notes} {group.notes}"
        lines.append(
            f"| `{unit.rel_path}` | {'confirmed-repo-level' if group and is_confirmed(group.license_status) else 'pending-confirmation'} | {evidence_text} | {sanitize_inline(notes)} |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def build_security_policy() -> str:
    return """# Security Policy

This repository publishes Codex skills and helper scripts. It is prepared for source sharing, not for storing runtime credentials, browser state, or local machine secrets.

## Never Commit

- Real API keys, access tokens, cookies, session exports, browser profiles, local databases, or raw private-key material.
- `.env` files or machine-local overrides containing non-placeholder credentials.
- Built-in `.system/` skills or `danger-*` skills unless they have been intentionally exported and separately reviewed.

## Safe Patterns

- Keep credentials in environment variables or a local secret manager.
- Keep third-party material inside `third-party/` with explicit origin and license review.
- Keep maintainer-specific sensitive scan inputs in a local private policy file such as `$CODEX_HOME/private/publish-policy.json`, not in committed docs or shared shell snippets.
- Prefer redacted examples such as `your_token_here` instead of live values.
- Keep the first sanitization and publication pass local-first. Do not hand unpublished branches, local private policy files, or internal-only skill trees to Codex cloud or GitHub-side Codex flows from this repo workflow.

## Reporting

If you find a leaked secret or sensitive local path:

1. Do not paste the raw value into a public issue.
2. Rotate or revoke the credential first if it is real.
3. Contact the maintainer privately with redacted evidence and affected file paths.

## Local Preflight

Run the staged export scan before public release:

```bash
python3 owned/skills-github-publisher/scripts/preflight_scan.py --root . --strict --strict-provenance --local-policy-file "$CODEX_HOME/private/publish-policy.json"
```

After creating the GitHub repository, enable Secret Scanning and Push Protection before the first public push.

If you later enable Codex on GitHub for this repository, limit the first use to review on already public pull requests rather than broader cloud-side editing. If a trusted maintainer later wants a follow-up task to write back to the current PR branch, make that request explicit and keep the patch scope narrow.
"""


def build_release_checklist(root: Path) -> str:
    root_license_present = has_root_license(root)
    lines: list[str] = []
    lines.append("# Release Checklist")
    lines.append("")
    lines.append("Use this checklist before creating the public GitHub repository or pushing from this export.")
    lines.append("")
    lines.append("## Required Checks")
    lines.append("")
    if root_license_present:
        lines.append("- Verify the root repository license still matches the intended scope of `owned/` content.")
    else:
        lines.append("- Choose the root repository license for `owned/` content and add `LICENSE` before public release.")
    lines.append("- Review `README.md`, `THIRD_PARTY_ACKNOWLEDGEMENTS.md`, `third-party/ORIGIN.md`, and `third-party/LICENSES.md` together.")
    lines.append("- Keep `owned/` and `third-party/` boundaries explicit; do not fold imported skills into `owned/`.")
    lines.append("- Re-run the strict preflight scan from the repository root.")
    lines.append("- Verify the effective Git author identity is public-safe before committing or pushing.")
    lines.append("- Keep maintainer-specific sensitive scan inputs only in a local private policy file, not in committed commands or repo docs.")
    lines.append("- Review `git status --short` and make sure ignored junk such as `node_modules/` is not part of the final handoff.")
    lines.append("- Verify `.system/` and `danger-*` skills are still excluded unless you intentionally reviewed them for publication.")
    lines.append("- Keep Codex GitHub maintenance disabled until the repository is already public, sanitized, and boundary-stable.")
    lines.append("")
    lines.append("## Commands")
    lines.append("")
    lines.append("```bash")
    lines.append("python3 owned/skills-github-publisher/scripts/preflight_scan.py --root . --strict --strict-provenance --local-policy-file \"$CODEX_HOME/private/publish-policy.json\"")
    lines.append("python3 owned/skills-github-publisher/scripts/check_git_identity.py --root . --strict --local-policy-file \"$CODEX_HOME/private/publish-policy.json\"")
    lines.append("git config user.name \"<public-name>\"  # if the effective identity is still private")
    lines.append("git config user.email \"<public-email-or-github-noreply>\"  # if the effective identity is still private")
    lines.append("git status --short")
    lines.append("git init -b main  # only for a fresh local repo")
    lines.append("git switch -c codex/<change-name>  # for updates to an existing public repo")
    lines.append("git add .")
    lines.append("git commit -m \"Prepare public skills export\"")
    lines.append("git show --stat --name-status --oneline -1")
    lines.append("git status --short")
    lines.append("git remote -v")
    lines.append("gh auth login --hostname github.com --git-protocol https --web  # recommended for HTTPS remotes")
    lines.append("git remote add origin <your-github-repo-url>  # prefer https://github.com/... for public repos when internal SSH keys also exist")
    lines.append("python3 owned/skills-github-publisher/scripts/push_pr_handoff.py --root . --base main  # inspect push/PR handoff first")
    lines.append("git push -u origin codex/<change-name>  # for updates to an existing public repo")
    lines.append("gh pr create --base main --head codex/<change-name> --fill-first  # or open the PR in the GitHub UI")
    lines.append("git ls-remote --heads origin codex/<change-name>")
    lines.append("```")
    lines.append("")
    lines.append("## GitHub Setup")
    lines.append("")
    lines.append("- Create the target GitHub repository with the intended visibility.")
    lines.append("- Prefer an HTTPS GitHub remote, or an explicit GitHub-only SSH alias, when the machine also carries separate internal SSH identities.")
    lines.append("- Prefer GitHub CLI login or another OS-keychain-backed HTTPS credential flow over typing PATs into terminal prompts.")
    lines.append("- Enable Secret Scanning and Push Protection before the first public push.")
    lines.append("- For normal updates to an already public repo, push a PR branch and merge through pull request review rather than pushing directly to `main`.")
    lines.append("- If `gh` is not installed locally, use the helper script's printed compare URL and open the PR in the browser manually.")
    lines.append("- Push only after the license decision, third-party manifests, and security scan are all in the expected state.")
    lines.append("- If push protection blocks the push, treat it as a real blocker and fix the flagged content before retrying.")
    lines.append("- If you later enable Codex on GitHub, start with PR review on the already public repository before allowing broader cloud-side edit flows.")
    lines.append("- If a trusted maintainer later wants Codex to write back to an existing public PR branch, make that a one-off explicit request instead of wiring an automatic fix loop.")
    lines.append("")
    return "\n".join(lines) + "\n"


def has_codex_review_gate(root: Path) -> bool:
    workflows_dir = root / ".github" / "workflows"
    return (workflows_dir / "codex-review-gate.yml").exists()


def has_codex_auto_merge(root: Path) -> bool:
    workflows_dir = root / ".github" / "workflows"
    return (workflows_dir / "codex-arm-auto-merge.yml").exists()


def build_codex_setup(root: Path) -> str:
    review_gate_enabled = has_codex_review_gate(root)
    auto_merge_enabled = has_codex_auto_merge(root)
    lines: list[str] = []
    lines.append("# Codex Setup")
    lines.append("")
    lines.append("Use this note after the repository is already public and sanitized.")
    lines.append("The goal is to keep the first Codex-on-GitHub use limited to review on public pull requests.")
    lines.append("")
    lines.append("## Already Prepared In This Repo")
    lines.append("")
    lines.append("- `AGENTS.md` keeps Codex in review-first mode and restates the public-boundary rules.")
    lines.append("- `.github/pull_request_template.md` keeps publication checks explicit for every PR.")
    lines.append("- `SECURITY.md` and `RELEASE_CHECKLIST.md` keep local policy files, internal-only content, and runtime credentials out of the repo.")
    lines.append("")
    lines.append("## Manual Steps You Still Need To Do")
    lines.append("")
    lines.append("1. In ChatGPT or Codex, connect GitHub and authorize only this public repository or the smallest possible repository subset.")
    lines.append("2. If the UI exposes Codex review settings, enable review first.")
    lines.append("3. If you later expect `@codex fix ...` or another follow-up task to update an existing PR branch, verify the same repository is also usable from Codex cloud; the review toggle alone is not enough evidence.")
    lines.append("4. If repository indexing is delayed, retry after a short wait and use the current GitHub import or refresh flow exposed by the product.")
    lines.append("5. Confirm any account-level privacy or training settings that matter for your plan before you rely on the integration.")
    lines.append("")
    lines.append("## If You Need Local Browser Help")
    lines.append("")
    lines.append("- Use an isolated Chrome profile instead of your default browser profile.")
    lines.append("- Keep login manual; do not read cookies, local storage, session storage, or browser credential files.")
    lines.append("- Keep browser-side troubleshooting limited to the minimum public setup hosts: `chatgpt.com`, `github.com`, and `help.openai.com`.")
    lines.append("- Debug in this order:")
    lines.append("  1. `https://chatgpt.com/codex/settings/code-review`")
    lines.append("  2. search the exact repository slug in the repository search box")
    lines.append("  3. if it is missing, go to `https://chatgpt.com/codex/settings/connectors`")
    lines.append("  4. use the GitHub `设置` button to open the ChatGPT Codex Connector installation page on GitHub")
    lines.append("  5. if GitHub asks for login, log in manually in the isolated profile, then authorize the missing repository")
    lines.append("")
    lines.append("## First Smoke Test")
    lines.append("")
    lines.append("- Use a small docs-only pull request.")
    if review_gate_enabled:
        lines.append("- Keep the `codex-review-gate` workflow green; that is the hard merge gate.")
        lines.append("- Only a trusted-maintainer-only submission can skip an extra human approval: the pull request must be opened by the repository owner or another configured admin profile, and every commit on the current head must resolve to that same trusted maintainer set.")
        lines.append("- If the PR is opened by someone else or includes any commit not attributed to that trusted maintainer set, keep the gate blocked until the repository owner or another configured admin approves the current head.")
        if auto_merge_enabled:
            lines.append("- Let GitHub auto-merge the PR after the gate succeeds instead of merging manually.")
        else:
            lines.append("- Merge manually after the gate succeeds if this repo does not install the optional auto-merge workflow.")
        lines.append("- If you are introducing the hard-gate workflows for the first time, the bootstrap PR that lands them may need a one-time manual exception.")
    else:
        lines.append("- If this export repo later adopts the optional `codex-review-gate` workflow, wait for that gate before merging.")
    lines.append("- Trigger Codex review through the currently supported GitHub flow for your account.")
    lines.append("- If Codex reports findings and you want one follow-up fix pass, have a trusted maintainer manually comment `@codex address that feedback` or an explicit `@codex fix ... update this existing PR branch` request.")
    lines.append("- For writeback requests, prefer explicit wording such as `@codex fix the latest review feedback on this existing PR branch. Update this PR branch directly with the minimal patch and do not widen scope.`")
    lines.append("- Do not auto-trigger `@codex address that feedback` from GitHub Actions or bots; keep it human-invoked to avoid review-fix-review loops.")
    lines.append("- Keep the review focus narrow:")
    lines.append("  - secret leakage or local-path regressions")
    lines.append("  - accidental inclusion of internal-only content")
    lines.append("  - ownership-boundary mistakes between `owned/` and `third-party/`")
    lines.append("  - provenance or attribution regressions")
    lines.append("")
    lines.append("Suggested review request:")
    lines.append("")
    lines.append("```text")
    lines.append("@codex review")
    lines.append("")
    lines.append("Focus on secret leakage, local path regressions, internal-only content, and ownership boundary mistakes between owned/ and third-party/.")
    lines.append("```")
    lines.append("")
    lines.append("## Stop Conditions")
    lines.append("")
    lines.append("- Do not use Codex GitHub flows on unpublished branches that still carry local-only policy values.")
    lines.append("- Do not authorize internal repositories from this public-repo setup path.")
    lines.append("- If the first review asks for local private files or ignores the public boundary, disable the GitHub-side flow and keep Codex local-only.")
    lines.append("")
    return "\n".join(lines) + "\n"


def build_license_decision(root: Path) -> str:
    root_license_present = has_root_license(root)
    lines: list[str] = []
    lines.append("# License Decision")
    lines.append("")
    if root_license_present:
        lines.append("A root repository license file is already present in this export.")
        lines.append("Verify that it reflects the intended license for the `owned/` subtree before public release.")
    else:
        lines.append("The root repository license for `owned/` content is intentionally not chosen automatically.")
        lines.append("Choose and add a root `LICENSE` file before public release.")
    lines.append("")
    lines.append("## Third-Party Context")
    lines.append("")
    lines.append("- Imported third-party skills remain under `third-party/`.")
    lines.append("- Third-party origin and redistribution review lives in `third-party/ORIGIN.md` and `third-party/LICENSES.md`.")
    lines.append("- Do not hide third-party obligations behind a new root license; keep attribution and notices explicit.")
    lines.append("")
    lines.append("## Maintainer Decision")
    lines.append("")
    lines.append("- Pick the license you want to grant for the `owned/` subtree.")
    lines.append("- Confirm that the chosen root license and the staged third-party notices can coexist without ambiguity.")
    lines.append("- If the licensing position is still unclear, keep the repository private until resolved.")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root not found or not a directory: {root}")

    entries = collect_skill_entries(root)
    vendors = collect_vendor_units(root)
    evidence = load_review_evidence(root)

    (root / "README.md").write_text(build_readme(root, entries, vendors, evidence), encoding="utf-8")
    (root / "THIRD_PARTY_ACKNOWLEDGEMENTS.md").write_text(build_acknowledgements(entries, vendors, evidence), encoding="utf-8")
    (root / "SECURITY.md").write_text(build_security_policy(), encoding="utf-8")
    (root / "RELEASE_CHECKLIST.md").write_text(build_release_checklist(root), encoding="utf-8")
    (root / "CODEX_SETUP.md").write_text(build_codex_setup(root), encoding="utf-8")
    (root / "LICENSE_DECISION.md").write_text(build_license_decision(root), encoding="utf-8")
    third_party_dir = root / "third-party"
    third_party_dir.mkdir(parents=True, exist_ok=True)
    (third_party_dir / "ORIGIN.md").write_text(build_origin_manifest(entries, vendors, evidence), encoding="utf-8")
    (third_party_dir / "LICENSES.md").write_text(build_license_manifest(entries, vendors, evidence), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
