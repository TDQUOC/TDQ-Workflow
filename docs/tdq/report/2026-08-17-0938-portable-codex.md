# REPORT — Bộ portable tự sinh cho hai harness

Ngày: 2026-08-17 · Plan: ../plan/2026-08-17-0938-portable-codex.md · Lane: full · Mode: main
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Đã làm

- `scripts/build_portable.py` — sinh HAI bản từ một nguồn: `portable_claude/` (`.claude/skills`,
  `.claude/agents`, 5 hook trong `.claude/settings.json`, `.mcp.json`) và `portable_codex/`
  (`AGENTS.md` + `workflow/01..08-*.md` + `references/`). Bản cũ `portable/` viết tay đã xoá.
- `scripts/tdq_checkportable.py` — `check` đối chiếu sha256 theo `manifest.json`, kiểm Python /
  lệnh ngoài / MCP; `setup` dựng lại hai file cấu hình tái tạo được, luôn sao lưu
  `<file>.tdq-bak-<timestamp>`, phần còn lại báo `CÒN …` và exit khác 0.
- Skill `tdq-checkportable` (nguồn ở `portable_src/`, không tính vào ngân sách context bộ chính)
  + README mỗi bản nêu ba giới hạn cứng: tin cậy thư mục, duyệt MCP, khởi động lại.
- Version 0.23.0 + CHANGELOG; `.graphifyignore` loại ba thư mục portable.

## Hai ràng buộc kiến trúc phát hiện lúc làm

- `hooks/scripts/_common.py` suy thư mục scripts bằng `../../scripts`, nên `hooks/` và `scripts/`
  buộc nằm cạnh nhau → gốc `.claude/tdq/`, và rewrite biến phải kèm đúng tiền tố đó.
- Logic sinh `settings.json`/`.mcp.json` phải sống trong `tdq_checkportable.py` (file duy nhất đi
  theo bundle) để máy đích dựng lại được; `build_portable.py` import ngược, giữ một bản logic.

## Kiểm

- `python3 -m pytest tests/ -q` → **743 passed, 375 subtests**, exit 0.
- QC độc lập bằng agent `tdq-qc-tester`, 3 vòng: vòng 1 FAIL (5 khuyết tật), vòng 2 FAIL (1 sót +
  4 mới), vòng 3 **PASS toàn bộ**, không phát sinh khuyết tật mới. Chứng cứ: `../qc/<slug>.md`.
- Lỗi nặng nhất đã sửa: lệnh "Bước 0" mà chính tài liệu bảo gõ đầu tiên lại exit 1 trên bundle
  sạch (gốc suy sai độ sâu) — nay `tim_goc_bundle()` đi ngược tìm `manifest.json`.

## Lệch so với spec

Spec §5 (quyết định 3B) nói `setup` được "tự cài gói và sửa cấu hình mức người dùng". Mã không có
đường nào chạm pip hay `~`, nên thay vì viết thêm, tôi **thu hẹp lời hứa trong tài liệu** cho khớp
năng lực thật: `setup` chỉ dựng lại hai file cấu hình tái tạo được từ dữ liệu trong bundle. Lý do:
lời hứa sai khiến người dùng tin đã được vá rồi bỏ qua phần phải tự làm. Muốn đúng 3B thì cần một
request bổ sung.

## Chưa làm

Không có. Mọi task trong plan đã tick `[x]`.

## Commit

Chưa commit — chờ user yêu cầu.
