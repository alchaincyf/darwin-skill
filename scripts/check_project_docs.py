#!/usr/bin/env python3
"""Check Darwin Skill project docs against docs/TDD.md and docs/RMD.md."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Finding:
    check_id: str
    message: str


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, check_id: str, message: str, findings: list[Finding]) -> None:
    if not condition:
        findings.append(Finding(check_id, message))


def check_required_files(findings: list[Finding]) -> None:
    required = [
        "SKILL.md",
        "README.md",
        "README_EN.md",
        "test-prompts.json",
        "templates/result-card.html",
        "scripts/screenshot.mjs",
        "docs/URD.md",
        "docs/ADD.md",
        "docs/MDD.md",
        "docs/TDD.md",
        "docs/RMD.md",
        "docs/TRACE.md",
        "docs/CHANGELOG.md",
        "docs/PARKING_LOT.md",
        ".vibe/trace.json",
        ".vibe/coupling_history.json",
        ".vibe/doc_state.json",
        ".vibe/update_log.json",
    ]
    for rel_path in required:
        require((ROOT / rel_path).exists(), "TDD-TEST-046", f"Missing required file: {rel_path}", findings)


def check_json_files(findings: list[Finding]) -> None:
    for rel_path in [
        ".vibe/trace.json",
        ".vibe/coupling_history.json",
        ".vibe/doc_state.json",
        ".vibe/update_log.json",
    ]:
        path = ROOT / rel_path
        try:
            load_json(path)
        except Exception as exc:  # noqa: BLE001 - report parser errors without hiding details.
            findings.append(Finding("TDD-TEST-050", f"{rel_path} is not valid JSON: {exc}"))

    coupling = load_json(ROOT / ".vibe/coupling_history.json")
    if isinstance(coupling, dict):
        require(
            coupling.get("status") == "decoupled_lower_triangular",
            "TDD-TEST-051",
            ".vibe/coupling_history.json status must be decoupled_lower_triangular",
            findings,
        )


def check_trace_links(findings: list[Finding]) -> None:
    trace = read_text(ROOT / "docs/TRACE.md")
    required_sections = [
        "## URD 到 ADD",
        "## ADD 到 MDD",
        "## MDD 到 TDD",
        "## TDD 到 RMD",
    ]
    for section in required_sections:
        require(section in trace, "TDD-TEST-047", f"TRACE missing section: {section}", findings)

    for index in range(1, 50):
        require(f"URD-REQ-{index:03d}" in trace, "TDD-TEST-047", f"TRACE missing URD-REQ-{index:03d}", findings)
    for index in range(1, 15):
        require(f"ADD-DP-{index:03d}" in trace, "TDD-TEST-048", f"TRACE missing ADD-DP-{index:03d}", findings)
    for index in range(1, 15):
        require(f"MDD-API-{index:03d}" in trace, "TDD-TEST-049", f"TRACE missing MDD-API-{index:03d}", findings)
        require(f"TDD-TEST-{index + 31:03d}" in trace, "TDD-TEST-049", f"TRACE missing TDD-TEST-{index + 31:03d}", findings)


def check_add_matrix(findings: list[Finding]) -> None:
    add = read_text(ROOT / "docs/ADD.md")
    lines = add.splitlines()
    in_matrix = False
    rows: list[str] = []
    for line in lines:
        if line == "## 4. 设计矩阵":
            in_matrix = True
            continue
        if in_matrix and line.startswith("该矩阵"):
            break
        if in_matrix and line.startswith("| ADD-FR-"):
            rows.append(line)

    require(rows, "TDD-TEST-055", "ADD matrix rows not found", findings)
    for row in rows:
        cells = row.split("|")
        if len(cells) < 16:
            findings.append(Finding("TDD-TEST-055", f"ADD matrix row has too few cells: {row}"))
            continue
        label = cells[1].strip()
        match = re.search(r"ADD-FR-(\d{3})", label)
        if not match:
            findings.append(Finding("TDD-TEST-055", f"ADD matrix row missing FR id: {row}"))
            continue
        fr_index = int(match.group(1))
        for dp_index in range(fr_index + 1, 15):
            cell_index = dp_index + 1
            if cell_index < len(cells) and cells[cell_index].strip() == "X":
                findings.append(
                    Finding(
                        "TDD-TEST-055",
                        f"ADD matrix has upper-triangle dependency: ADD-FR-{fr_index:03d} uses ADD-DP-{dp_index:03d}",
                    )
                )


def check_prompt_file(findings: list[Finding]) -> None:
    prompts = load_json(ROOT / "test-prompts.json")
    require(isinstance(prompts, list), "TDD-TEST-003", "test-prompts.json must contain a list", findings)
    if not isinstance(prompts, list):
        return
    require(2 <= len(prompts) <= 3, "TDD-TEST-012", "test-prompts.json must contain 2 to 3 prompts", findings)
    for item in prompts:
        require(isinstance(item, dict), "TDD-TEST-003", "Each prompt case must be an object", findings)
        if not isinstance(item, dict):
            continue
        for key in ["id", "scenario", "prompt", "expected"]:
            require(key in item and item[key], "TDD-TEST-003", f"Prompt case missing field: {key}", findings)


def check_skill_contracts(findings: list[Finding]) -> None:
    skill = read_text(ROOT / "SKILL.md")
    required_patterns = {
        "TDD-TEST-001": r"Phase 0\.5|测试Prompt设计",
        "TDD-TEST-002": r"评估 Rubric（9维度，总分100）",
        "TDD-TEST-003": r"full_test|dry_run",
        "TDD-TEST-005": r"每轮 1 个维度|每轮只改一个维度",
        "TDD-TEST-006": r"新总分 > 旧总分|严格高于",
        "TDD-TEST-007": r"timestamp\s+commit\s+skill\s+old_score\s+new_score\s+status\s+dimension\s+note\s+eval_mode",
        "TDD-TEST-020": r"Phase 0\.10: 领域调查研究",
        "TDD-TEST-024": r"domain-rubric-evaluation\.md|domain-rubric-evaluation\.json",
        "TDD-TEST-025": r"RQ1.*RQ9|RQ1-RQ9",
        "TDD-TEST-026": r"overall_score < 65|低于 65",
        "TDD-TEST-027": r"confidence_level.*high|置信度不得为 `high`",
        "TDD-TEST-028": r"Phase 0\.35: 用户确认并冻结领域评分标准",
        "TDD-TEST-030": r"rubric_quality_score|rubric_quality_decision",
        "TDD-TEST-031": r"Domain Research|Domain Rubric Quality",
    }
    for check_id, pattern in required_patterns.items():
        require(re.search(pattern, skill), check_id, f"SKILL.md missing required pattern: {pattern}", findings)


def is_runtime_example_line(line: str) -> bool:
    example_markers = [
        "误判",
        "grep -nE",
        "红灯",
        "替换为",
        "视为 gate",
        "典型表现",
        "绿灯",
        "单一 badge",
    ]
    return any(marker in line for marker in example_markers)


def check_runtime_neutrality(findings: list[Finding]) -> None:
    patterns = [
        re.compile(r"在 Claude Code"),
        re.compile(r"Claude Code skill"),
        re.compile(r"Claude Code 用户"),
        re.compile(r"Cursor only"),
        re.compile(r"Codex 中"),
        re.compile(r"^\[!\[Claude Code"),
        re.compile(r"~/\.claude/skills/[a-z]"),
        re.compile(r"/plugin install\b"),
    ]
    for rel_path in ["SKILL.md", "README.md", "README_EN.md"]:
        path = ROOT / rel_path
        for lineno, line in enumerate(read_text(path).splitlines(), start=1):
            if is_runtime_example_line(line):
                continue
            for pattern in patterns:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            "TDD-TEST-004",
                            f"Runtime red flag in {rel_path}:{lineno}: {pattern.pattern}",
                        )
                    )


def check_docs_language(findings: list[Finding]) -> None:
    bad_patterns = [
        "TODO",
        "TBD",
        "待补",
        "xxx",
        "赋能",
        "闭环",
        "底座",
        "抓手",
        "下钻",
        "落地",
    ]
    for path in (ROOT / "docs").glob("*.md"):
        text = read_text(path)
        for pattern in bad_patterns:
            if pattern in text:
                findings.append(Finding("TDD-TEST-052", f"{path.relative_to(ROOT)} contains forbidden marker: {pattern}"))


def check_no_local_user_paths(findings: list[Finding]) -> None:
    text_suffixes = {
        ".css",
        ".html",
        ".js",
        ".json",
        ".md",
        ".mjs",
        ".py",
        ".svg",
        ".ts",
        ".tsx",
        ".txt",
        ".yaml",
        ".yml",
    }
    excluded_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv"}
    personal_path_patterns = [
        re.compile("/" + "Users" + r"/[^/\\\s\"'`]+"),
        re.compile(r"(?i)\b[A-Z]:\\Users\\[^\\/\s\"'`]+"),
        re.compile("/" + "home" + r"/[^/\\\s\"'`]+"),
    ]

    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in excluded_dirs for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix.lower() not in text_suffixes:
            continue

        try:
            text = read_text(path)
        except UnicodeDecodeError:
            continue

        for lineno, line in enumerate(text.splitlines(), start=1):
            for pattern in personal_path_patterns:
                if pattern.search(line):
                    findings.append(
                        Finding(
                            "TDD-TEST-056",
                            f"Local user path found in {path.relative_to(ROOT)}:{lineno}",
                        )
                    )


def check_no_wiki(findings: list[Finding]) -> None:
    require(not (ROOT / "wiki").exists(), "RMD-CHECK-004", "wiki directory must not exist for this revision", findings)


def main() -> int:
    findings: list[Finding] = []
    check_required_files(findings)
    check_json_files(findings)
    check_trace_links(findings)
    check_add_matrix(findings)
    check_prompt_file(findings)
    check_skill_contracts(findings)
    check_runtime_neutrality(findings)
    check_docs_language(findings)
    check_no_local_user_paths(findings)
    check_no_wiki(findings)

    if findings:
        print("Project document checks failed:")
        for finding in findings:
            print(f"- {finding.check_id}: {finding.message}")
        return 1

    print("Project document checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
