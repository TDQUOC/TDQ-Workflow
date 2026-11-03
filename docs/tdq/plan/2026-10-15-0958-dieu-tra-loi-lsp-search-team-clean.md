# PLAN — Điều tra và khắc phục lỗi LSP search gate và tdq_team clean

Ngày: 2026-10-15 · Spec: ../spec/2026-10-15-0958-dieu-tra-loi-lsp-search-team-clean.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — tdq_bench.py simulate đo 4 task / 1 đợt: subagent 6.1 phút so với main 8.1 phút (lợi 2.0 phút ở hệ số agent 1.5)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Lệnh `tdq_team.py clean [task]` và tài liệu dọn dẹp worktree sau merge
- P2 — Tự động nhận diện ngôn ngữ dự án trong `search_rules.py` / `search_gate.py` và gợi ý `list_symbols`
- P3 — Cập nhật `KHOI_HUONG_DAN`, `CLAUDE.md`, tài liệu tìm kiếm và ngân sách token
- P4 — Log & test bắt buộc
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Lệnh `tdq_team.py clean [task]` và tài liệu dọn dẹp worktree sau merge

- [x] **T1.1** (e8m) Cập nhật `scripts/tdq_team.py` và bộ unit test `tests/test_team_mode.py` (TDD đỏ → xanh): mở rộng parser để lệnh con `clean` nhận tham số task tùy chọn `clean [task]`, nếu truyền task mà worktree đã được dọn trước đó (bởi `merge`) thì in `Worktree for <task> already cleaned.` và trả về `0`; nếu worktree còn tồn tại thì dọn dẹp; nếu không truyền task thì dọn toàn bộ slug như cũ. Cập nhật dòng 91 trong `skills/tdq-build/SKILL.md` và `skills/tdq-build/references/team-mode.md` làm rõ rằng `merge` đã tự động dọn task worktree và cuối wave gọi `sweep --clean` — Test: `python -m unittest discover -s tests -p "test_team_mode.py" -k "clean"`
  - Chạm: `scripts/tdq_team.py`, `tests/test_team_mode.py`, `skills/tdq-build/SKILL.md`, `skills/tdq-build/references/team-mode.md` → `tdq_team.lenh_don()`, `tdq_team.build_parser()` (nguồn: `mcp__lsp__blast_radius` trên `scripts/tdq_team.py`)

**Xong P1 khi**: `python -m unittest discover -s tests -p "test_team_mode.py" -k "clean"` chạy xanh 100% cho cả 3 trường hợp: `clean T1.1` khi đã merge, `clean T1.1` khi chưa dọn, và `clean` toàn bộ slug.

## P2 — Tự động nhận diện ngôn ngữ dự án trong `search_rules.py` / `search_gate.py` và gợi ý `list_symbols`

- [x] **T2.1** (e10m) Cập nhật `scripts/search_rules.py`, `hooks/scripts/search_gate.py` và unit test `tests/test_search_rules.py` (TDD đỏ → xanh): bổ sung hàm `do_ngon_ngu_du_an(cwd)` phát hiện ngôn ngữ chính của dự án (`typescript`, `javascript`, `python`, `go`, `rust`...) dựa trên file mốc (`package.json`, `tsconfig.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`) hoặc `.tdq-lsp-module.json`; truyền `ngon_ngu` vào `loi_nhac()` để in đúng `language_id` thực tế thay vì gán cứng `e.g. python`; trong `quyet_dinh()` bổ sung gợi ý `mcp__lsp__list_symbols(file_path="...")` khi lệnh grep có chỉ định đường dẫn file cụ thể trong `path` — Test: `python -m unittest discover -s tests -p "test_search_rules.py"`
  - Chạm: `scripts/search_rules.py`, `hooks/scripts/search_gate.py`, `tests/test_search_rules.py`, `tests/test_search_gate.py` → `search_rules.loi_nhac()`, `search_rules.quyet_dinh()`, `search_gate.quyet()` (nguồn: `mcp__lsp__blast_radius` trên `scripts/search_rules.py`)

**Xong P2 khi**: `tests/test_search_rules.py` chạy xanh 100% các bài test sinh câu thông báo chặn chính xác theo ngôn ngữ dự án và gợi ý `list_symbols` khi grep trong file cụ thể.

## P3 — Cập nhật `KHOI_HUONG_DAN`, `CLAUDE.md`, tài liệu tìm kiếm và ngân sách token

- [x] **T3.1** (e6m) Cập nhật `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` (và ghim lại vào `~/.claude/CLAUDE.md`) hướng dẫn quy trình cơ học 3 bước gọi LSP (`start_lsp` đầu phiên, `open_document` cho TS/JS, và tra cứu chính xác) giữ độ dài ≤ 25 dòng; cập nhật `skills/tdq-setup/references/uu-tien-tim-kiem.md`, chạy `scripts/doc_index.py --tat-ca` và `scripts/token_budget.py` đồng bộ `docs/tdq/token-budget.json` — Test: `python scripts/doc_lint.py skills/tdq-setup/references/uu-tien-tim-kiem.md && python scripts/token_budget.py --kiem`
  - Chạm: `scripts/tdq_setup.py`, `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `docs/tdq/token-budget.json`
  - Cần: T1.1, T2.1

**Xong P3 khi**: `doc_lint.py` và `token_budget.py --kiem` đạt 0 vi phạm, khối ghim `KHOI_HUONG_DAN` ≤ 25 dòng.

## P4 — Log & test bắt buộc

- [x] **T4.1** (e4m) Kiểm chứng Log service bật mặc định của các module chạm (ISO timestamp trên stderr, tắt qua `TDQ_LOG=0`), và kiểm tra `i18n_check.py` trên toàn bộ file chạm — Test: `python -m unittest discover -s tests -p "test_team_mode.py" -k "clean" && python scripts/i18n_check.py scripts/tdq_team.py scripts/search_rules.py hooks/scripts/search_gate.py scripts/tdq_setup.py skills/tdq-setup/references/uu-tien-tim-kiem.md`
  - Chạm: `tests/test_team_mode.py`, `tests/test_search_rules.py`
  - Cần: T3.1

**Xong P4 khi**: Log service test xanh và `i18n_check.py` đạt 0 vi phạm.

## Cụm song song

- **Đợt 1 (Song song được)**: `T1.1` (chạm `scripts/tdq_team.py`, `tests/test_team_mode.py`, `skills/tdq-build/SKILL.md`, `skills/tdq-build/references/team-mode.md`) và `T2.1` (chạm `scripts/search_rules.py`, `hooks/scripts/search_gate.py`, `tests/test_search_rules.py`) — không giao vùng file.
- **Đợt 2 (Tuần tự sau Đợt 1)**: `T3.1` (cập nhật `KHOI_HUONG_DAN`, `uu-tien-tim-kiem.md` và khóa `token-budget.json`).
- **Đợt 3 (Tuần tự sau Đợt 2)**: `T4.1` (kiểm chứng log service và `i18n_check.py`).

## Definition of Done

- [x] Q1 Lệnh `tdq_team.py clean` hỗ trợ tham số task tùy chọn và xử lý an toàn khi đã dọn (trả về 0 thay vì exit 2) — `python -m unittest discover -s tests -p "test_team_mode.py" -k "clean"`
- [x] Q2 Hook `search_gate.py` và `search_rules.py` tự động phát hiện ngôn ngữ dự án và gợi ý `list_symbols` khi grep trong file cụ thể — `python -m unittest discover -s tests -p "test_search_rules.py" -k "ngon_ngu or list_symbols"`
- [x] Q3 Khối ghim `KHOI_HUONG_DAN`, `CLAUDE.md` và tài liệu hướng dẫn 3 bước gọi LSP đạt chuẩn độ dài ≤ 25 dòng — `python -m unittest discover -s tests -p "test_tdq_setup.py" -k "khoi_huong_dan"`
- [x] Q4 Hợp đồng tài liệu, chuẩn ngôn ngữ 3 tầng và khóa ngân sách token đạt 0 vi phạm — `python scripts/doc_lint.py skills/tdq-setup/references/uu-tien-tim-kiem.md && python scripts/token_budget.py --kiem && python scripts/i18n_check.py scripts/tdq_team.py scripts/search_rules.py hooks/scripts/search_gate.py scripts/tdq_setup.py skills/tdq-setup/references/uu-tien-tim-kiem.md`
