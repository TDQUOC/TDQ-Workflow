#!/usr/bin/env python3
"""tdq_knowledge.py — Curation and verification for TDQ Knowledge entries (O12 / T3.5).

Enforces:
1. Lifecycle states: candidate, reviewed, rejected, superseded.
2. Candidate / legacy unverified cannot auto-promote to active system policy (auto_policy=false).
3. Reviewed requires human reviewer, review date, and evidence pointer.
4. Superseded requires replacement pointer.
5. Secret screening: detects and rejects synthetic secrets, masks output to prevent leaks.
"""
import glob
import os
import re
import sys

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.join(GOC, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(GOC, "scripts"))

import tdq_state

TRANG_THAI_HOP_LE = ("candidate", "reviewed", "rejected", "superseded")

# Các mẫu nhận diện khóa bí mật / token thông dụng
SECRET_PATTERNS = [
    (re.compile(r"sk-ant-api[a-zA-Z0-9_\-]{10,}", re.IGNORECASE), "Anthropic API Key"),
    (re.compile(r"sk-[a-zA-Z0-9_\-]{20,}", re.IGNORECASE), "OpenAI API Key"),
    (re.compile(r"gh[pousr]_[a-zA-Z0-9]{20,}", re.IGNORECASE), "GitHub Token"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.IGNORECASE), "Private Key"),
    (re.compile(r"Bearer\s+[a-zA-Z0-9_\-\.]{20,}", re.IGNORECASE), "Bearer Token"),
    (re.compile(r"(?:api[_-]?key|secret|password|passwd|token)\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{16,})", re.IGNORECASE), "Generic Secret"),
]


def _log(msg):
    if tdq_state.log_enabled():
        print(f"[{tdq_state.now_iso()}] tdq_knowledge: {msg}", file=sys.stderr)


def _quet_secret(noi_dung):
    """Quét nội dung tìm secret. Trả về (co_secret, loai_secret_masked).

    Tuyệt đối không trả về raw secret để tránh rò rỉ vào log hoặc thông báo lỗi.
    """
    for regex, loai in SECRET_PATTERNS:
        khop = regex.search(noi_dung)
        if khop:
            return True, f"Detected potential secret ({loai})"
    return False, ""


def _tach_frontmatter(noi_dung):
    """Tách frontmatter YAML đơn giản không dùng thư viện ngoài."""
    lines = noi_dung.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, noi_dung

    fm_lines = []
    body_idx = len(lines)
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            body_idx = i + 1
            break
        fm_lines.append(line)

    metadata = {}
    dict_key = None

    for line in fm_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("  ") and dict_key and isinstance(metadata.get(dict_key), dict):
            sub_line = line.strip()
            if ":" in sub_line:
                k, v = sub_line.split(":", 1)
                metadata[dict_key][k.strip()] = _parse_val(v.strip())
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            if not v:
                dict_key = k
                metadata[dict_key] = {}
            else:
                dict_key = None
                metadata[k] = _parse_val(v)

    body = "\n".join(lines[body_idx:])
    return metadata, body


def _parse_val(val_str):
    if val_str.lower() == "true":
        return True
    if val_str.lower() == "false":
        return False
    if val_str.isdigit():
        return int(val_str)
    return val_str.strip('"\'')


def xac_thuc_bai_hoc(duong_dan_hoac_noi_dung):
    """Xác thực một bài học tri thức theo hợp đồng O12.

    Trả về (hop_le, ly_do, metadata).
    """
    if os.path.exists(duong_dan_hoac_noi_dung):
        with open(duong_dan_hoac_noi_dung, "r", encoding="utf-8", errors="replace") as f:
            noi_dung = f.read()
    else:
        noi_dung = duong_dan_hoac_noi_dung

    # 1. Quét phát hiện secret trước tiên
    co_secret, loai_secret = _quet_secret(noi_dung)
    if co_secret:
        return False, f"Rejection: {loai_secret} found in content", {}

    # 2. Tách frontmatter
    metadata, _ = _tach_frontmatter(noi_dung)
    if metadata is None:
        # Tài liệu cũ không có frontmatter
        return True, "Legacy unverified knowledge", {"trang_thai": "legacy_unverified", "auto_policy": False}

    trang_thai = metadata.get("trang_thai")
    if not trang_thai or trang_thai not in TRANG_THAI_HOP_LE:
        return False, f"Invalid or missing trang_thai: {trang_thai!r} (must be one of {TRANG_THAI_HOP_LE})", metadata

    # 3. Kiểm tra candidate: tuyệt đối không được auto_policy = True
    if trang_thai == "candidate":
        if metadata.get("auto_policy") is True:
            return False, "Candidate knowledge cannot set auto_policy=true (manual review required)", metadata

    # 4. Kiểm tra reviewed: bắt buộc người duyệt, ngày duyệt, evidence
    elif trang_thai == "reviewed":
        nguoi_duyet = metadata.get("nguoi_duyet")
        if not nguoi_duyet:
            return False, "Reviewed knowledge must specify 'nguoi_duyet'", metadata
        ngay_duyet = metadata.get("ngay_duyet")
        if not ngay_duyet:
            return False, "Reviewed knowledge must specify 'ngay_duyet'", metadata
        nguon = metadata.get("nguon") or {}
        evidence = nguon.get("evidence") if isinstance(nguon, dict) else None
        if not evidence and not metadata.get("evidence"):
            return False, "Reviewed knowledge must specify 'evidence' in nguon", metadata

    # 5. Kiểm tra superseded: bắt buộc có thay_the
    elif trang_thai == "superseded":
        thay_the = metadata.get("thay_the")
        if not thay_the:
            return False, "Superseded knowledge must specify 'thay_the' pointer", metadata

    return True, "Valid knowledge entry", metadata


def kiem_tra_file(duong_dan):
    """Kiểm tra và log kết quả của 1 file."""
    hop_le, ly_do, _ = xac_thuc_bai_hoc(duong_dan)
    if not hop_le:
        _log(f"FAIL {os.path.basename(duong_dan)}: {ly_do}")
        return False, ly_do
    _log(f"PASS {os.path.basename(duong_dan)}: {ly_do}")
    return True, ly_do


def main(argv=None):
    args = list(argv or sys.argv[1:])
    if not args:
        print("Usage: tdq_knowledge.py check <file_or_dir>", file=sys.stderr)
        return 2

    cmd = args.pop(0)
    if cmd == "check":
        if not args:
            print("Missing target path for check", file=sys.stderr)
            return 2
        target = args[0]
        if os.path.isdir(target):
            files = sorted(glob.glob(os.path.join(target, "*.md")))
        else:
            files = [target]

        tong_loi = 0
        for f in files:
            hop_le, _ = kiem_tra_file(f)
            if not hop_le:
                tong_loi += 1
        return 1 if tong_loi > 0 else 0
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
