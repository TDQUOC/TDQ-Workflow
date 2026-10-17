#!/usr/bin/env python3
"""
TDQ Continuous Learning & Harvest Tool (tdq_harvest.py)
Captures lessons learned, bug-fix insights, and patterns from working logs and tests into
a quarantined staging area (docs/tdq/knowledge/candidates/) for explicit human CLI approval,
preventing autonomous memory poisoning.
"""

import argparse
import datetime
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional

CANDIDATES_DIR = Path("docs/tdq/knowledge/candidates")
APPROVED_DIR = Path("docs/tdq/knowledge/approved")


def log(msg: str, verbose: bool = False, level: str = "INFO") -> None:
    """Standard timestamped logger adhering to TDQ Service Logging doctrine."""
    if not verbose and os.environ.get("TDQ_LOG") == "0":
        return
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = f"[{now_str}] [TDQ-HARVEST] [{level}]"
    print(f"{prefix} {msg}")


def ensure_dirs(project_root: Path = Path(".")) -> None:
    """Ensure quarantined knowledge directories exist."""
    (project_root / CANDIDATES_DIR).mkdir(parents=True, exist_ok=True)
    (project_root / APPROVED_DIR).mkdir(parents=True, exist_ok=True)


def generate_candidate_id(prefix: str = "k") -> str:
    """Generate a clean timestamp-based identifier for knowledge candidate."""
    now = datetime.datetime.now()
    return f"{prefix}_{now.strftime('%Y%m%d_%H%M%S')}"


def extract_insights_from_text(content: str, source_path: str) -> List[Dict[str, str]]:
    """Scan markdown text for bug fix notes, lessons learned, or troubleshooting resolutions."""
    insights = []
    # Patterns matching error & fix narratives common in working logs
    pattern = re.compile(
        r"(?:(?:Lỗi|Bug|Problem|Issue|Fail):\s*(.+?)\n+(?:Khắc phục|Fix|Resolution|Pass|Solution):\s*(.+?)(?=\n\n|\Z))",
        re.IGNORECASE | re.DOTALL,
    )

    matches = pattern.findall(content)
    for idx, (issue, resolution) in enumerate(matches, 1):
        clean_issue = " ".join(issue.strip().splitlines())
        clean_res = " ".join(resolution.strip().splitlines())
        cand_id = f"{generate_candidate_id()}_{idx}"
        summary = clean_issue[:100] + ("..." if len(clean_issue) > 100 else "")
        insights.append({
            "id": cand_id,
            "source": source_path,
            "summary": summary,
            "issue": clean_issue,
            "resolution": clean_res,
        })
    return insights


def cmd_scan(args: argparse.Namespace, project_root: Path = Path(".")) -> int:
    """Scan latest working logs for troubleshoot patterns and deposit into candidate staging."""
    ensure_dirs(project_root)
    verbose = getattr(args, "verbose", False)
    log("Starting knowledge scan across recent logs...", verbose=verbose)

    log_dir = project_root / "docs" / "workinglog"
    if not log_dir.exists():
        log(f"Working log directory not found at {log_dir}", verbose=verbose, level="WARN")
        return 0

    log_files = sorted(log_dir.glob("*.md"), reverse=True)
    if not log_files:
        log("No working log files available for scan.", verbose=verbose)
        return 0

    target_files = log_files[:3]
    total_found = 0

    for file_path in target_files:
        try:
            text = file_path.read_text(encoding="utf-8")
            rel_source = file_path.relative_to(project_root).as_posix()
            items = extract_insights_from_text(text, rel_source)
            for item in items:
                cand_file = project_root / CANDIDATES_DIR / f"{item['id']}.md"
                if not cand_file.exists():
                    body = (
                        f"---\n"
                        f"id: {item['id']}\n"
                        f"date: {datetime.date.today().isoformat()}\n"
                        f"source: {item['source']}\n"
                        f"status: candidate\n"
                        f"summary: \"{item['summary']}\"\n"
                        f"---\n\n"
                        f"### Issue\n{item['issue']}\n\n"
                        f"### Resolution\n{item['resolution']}\n"
                    )
                    cand_file.write_text(body, encoding="utf-8")
                    total_found += 1
                    log(f"Discovered candidate: {item['id']} ({item['summary']})", verbose=verbose)
        except Exception as exc:
            log(f"Error reading {file_path}: {exc}", verbose=verbose, level="ERROR")

    print(f"Scan complete. {total_found} new candidate(s) staged in {CANDIDATES_DIR.as_posix()}.")
    return 0


def cmd_list(args: argparse.Namespace, project_root: Path = Path(".")) -> int:
    """List all pending knowledge candidates in staging area."""
    ensure_dirs(project_root)
    verbose = getattr(args, "verbose", False)
    cand_files = sorted((project_root / CANDIDATES_DIR).glob("*.md"))

    if not cand_files:
        print(f"No pending knowledge candidates in {CANDIDATES_DIR.as_posix()}.")
        return 0

    print(f"\nPending Knowledge Candidates ({len(cand_files)}):")
    print(f"{'ID':<25} | {'Date':<10} | {'Source':<30} | {'Summary'}")
    print("-" * 90)

    for cf in cand_files:
        try:
            content = cf.read_text(encoding="utf-8")
            cand_id = cf.stem
            date_val = "Unknown"
            source_val = "Unknown"
            summary_val = ""

            for line in content.splitlines():
                if line.startswith("id:"):
                    cand_id = line.split(":", 1)[1].strip()
                elif line.startswith("date:"):
                    date_val = line.split(":", 1)[1].strip()
                elif line.startswith("source:"):
                    source_val = line.split(":", 1)[1].strip()
                elif line.startswith("summary:"):
                    summary_val = line.split(":", 1)[1].strip().strip('"')

            print(f"{cand_id:<25} | {date_val:<10} | {source_val[:28]:<30} | {summary_val[:35]}")
        except Exception as exc:
            log(f"Failed to read {cf}: {exc}", verbose=verbose, level="WARN")

    print("-" * 90)
    print("Run 'python scripts/tdq_harvest.py approve <ID>' to promote or 'reject <ID>' to discard.\n")
    return 0


def cmd_approve(args: argparse.Namespace, project_root: Path = Path(".")) -> int:
    """Approve a candidate and promote to approved knowledge base."""
    ensure_dirs(project_root)
    verbose = getattr(args, "verbose", False)
    cand_id = args.candidate_id.strip()

    cand_file = project_root / CANDIDATES_DIR / f"{cand_id}.md"
    if not cand_file.exists():
        matching = list((project_root / CANDIDATES_DIR).glob(f"*{cand_id}*.md"))
        if len(matching) == 1:
            cand_file = matching[0]
        else:
            print(f"Error: Candidate '{cand_id}' not found in {CANDIDATES_DIR.as_posix()}.", file=sys.stderr)
            return 1

    content = cand_file.read_text(encoding="utf-8")
    promoted_content = content.replace("status: candidate", "status: approved")

    dest_file = project_root / APPROVED_DIR / cand_file.name
    dest_file.write_text(promoted_content, encoding="utf-8")
    cand_file.unlink()

    log(f"Approved knowledge candidate '{cand_id}' -> {dest_file.as_posix()}", verbose=verbose)
    print(f"[APPROVED] Knowledge candidate '{cand_id}' successfully promoted to {APPROVED_DIR.as_posix()}.")
    return 0


def cmd_reject(args: argparse.Namespace, project_root: Path = Path(".")) -> int:
    """Reject and permanently discard a knowledge candidate."""
    ensure_dirs(project_root)
    verbose = getattr(args, "verbose", False)
    cand_id = args.candidate_id.strip()

    cand_file = project_root / CANDIDATES_DIR / f"{cand_id}.md"
    if not cand_file.exists():
        matching = list((project_root / CANDIDATES_DIR).glob(f"*{cand_id}*.md"))
        if len(matching) == 1:
            cand_file = matching[0]
        else:
            print(f"Error: Candidate '{cand_id}' not found in {CANDIDATES_DIR.as_posix()}.", file=sys.stderr)
            return 1

    cand_file.unlink()
    log(f"Discarded candidate '{cand_id}'", verbose=verbose)
    print(f"[REJECTED] Knowledge candidate '{cand_id}' discarded.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tdq_harvest.py",
        description="TDQ Governed Continuous Learning CLI: harvest, stage, and curate insights.",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose debug logs with timestamps.")

    subparsers = parser.add_subparsers(dest="command", help="Available sub-commands")

    # scan
    sub_scan = subparsers.add_parser("scan", help="Scan recent logs and extract troubleshooting insights into staging.")
    sub_scan.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    # list
    sub_list = subparsers.add_parser("list", help="List all candidate insights waiting for review.")
    sub_list.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    # approve
    sub_app = subparsers.add_parser("approve", help="Approve and promote a staged candidate.")
    sub_app.add_argument("candidate_id", help="Candidate identifier or filename stem")
    sub_app.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    # reject
    sub_rej = subparsers.add_parser("reject", help="Reject and discard a staged candidate.")
    sub_rej.add_argument("candidate_id", help="Candidate identifier or filename stem")
    sub_rej.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "scan":
        return cmd_scan(args)
    elif args.command == "list":
        return cmd_list(args)
    elif args.command == "approve":
        return cmd_approve(args)
    elif args.command == "reject":
        return cmd_reject(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
