# PLAN — Ưu tiên MCP, Auto Setup & Tự động Cập nhật Plugin

Ngày: 2026-10-20 · Spec: ../spec/2026-10-20-1115-uu-tien-mcp-auto-setup.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — ĐÃ DUYỆT
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — MCP-First Instruction, Anchor & Pre-flight Guide
- P2 — Incremental Auto-Setup khi Đổi Phiên Bản
- P3 — SessionStart Auto Check & Update Plugin
- Dòng `Chạm:` (đặt NGAY DƯỚI mọi task TẠO hoặc SỬA file mã nguồn)
- Luật file nóng (một file, nhiều task chạm)
- Dòng `Cần:` (khai phụ thuộc giữa các task)
- Cụm song song
- P4 — Log & test bắt buộc
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Tuân thủ 6 mã cấm cơ học (ANTI-1 Fake Red, ANTI-2 Blind Assertion, ANTI-3 Dirty State Git, ANTI-4 Late Tick, ANTI-5 Raw Dump, ANTI-6 Broad Area).

## P1 — MCP-First Instruction, Anchor & Pre-flight Guide
- [x] **T1.1** (e15m) Viết cẩm nang `skills/tdq-setup/references/mcp-first-guide.md` chuẩn hóa nguyên tắc MCP-First, kịch bản pre-flight connection check cho Roblox, Unity, Chrome DevTools và câu thông báo hướng dẫn bật khi chưa kết nối — Test: `doc_lint` trên file guide PASS.
  - Chạm: `skills/tdq-setup/references/mcp-first-guide.md` → file mới, chưa node nào phụ thuộc
- [x] **T1.2** (e15m) Cập nhật khối `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` bổ sung mục `## Nguyên tắc Ưu tiên MCP & Bộ kỹ năng MCP (MCP-First)` ghim tự động vào `CLAUDE.md`, đồng bộ mẫu spec/plan (§3b) — Test: `tests/test_tu_khoi_tao.py` và `doc_lint` PASS.
  - Chạm: `scripts/tdq_setup.py`, `skills/tdq-spec/references/spec-template.md`, `skills/tdq-plan/references/plan-template.md` → khối instruction và template
  - Cần: T1.1
- [x] **T1.3** (e12m) Cập nhật khối neo phục hồi `[TDQ:ANCHOR]` trong `hooks/scripts/session_start.py` bổ sung quy tắc nhắc nhở `MCP-First` sau khi nén phiên (compact/resume) — Test: test chuỗi anchor không vượt trần ký tự và chứa `MCP-First`.
  - Chạm: `hooks/scripts/session_start.py` → hook session_start (anchor block)
  - Cần: T1.2

**Xong P1 khi**: Toàn bộ instruction toàn cục, anchor sau nén, cẩm nang pre-flight check và template spec/plan đều chứa nguyên tắc MCP-First.

## P2 — Incremental Auto-Setup khi Đổi Phiên Bản
- [x] **T2.1** (e20m) Mở rộng `tu_dong_cap_nhat_khi_doi_phien_ban` trong `scripts/tdq_setup.py`: so sánh version cũ với version mới, tự động chạy setup bù các phần mới (cài shim, cập nhật allow permissions, kiểm tra LSP, đồng bộ Codex, chạy hook dry-run) và ghi nhận mốc mới — Test: unit test kịch bản phát hiện version cũ và thực thi setup bù PASS.
  - Chạm: `scripts/tdq_setup.py` → hàm tu_dong_cap_nhat_khi_doi_phien_ban
  - Cần: T1.2

**Xong P2 khi**: Hệ thống tự động kích hoạt setup bù đắp đầy đủ cấu hình và dependency khi phát hiện phiên bản cài đặt mới.

## P3 — SessionStart Auto Check & Update Plugin
- [x] **T3.1** (e20m) Xây dựng hàm kiểm tra và tự động nâng cấp plugin scope user trong `hooks/scripts/session_start.py` và `scripts/tdq_setup.py`: tự động phát hiện `v_cai < v_nguon`, gọi lệnh cập nhật `claude plugin update` hoặc đồng bộ cache cục bộ, phát thông báo xác nhận — Test: unit test mock runner kiểm tra auto-update plugin được kích hoạt an toàn.
  - Chạm: `hooks/scripts/session_start.py`, `scripts/tdq_setup.py` → logic auto-update plugin
  - Cần: T2.1

**Xong P3 khi**: Khởi động phiên làm việc tự động phát hiện và đồng bộ nâng cấp plugin scope user khi repo nguồn có phiên bản mới hơn.

## P4 — Log & test bắt buộc
- [x] **T4.1** (e15m) Xây dựng bộ test suite `tests/test_mcp_first_auto_setup.py` kiểm chứng độc lập 4 tính năng: MCP-First instruction, anchor compact, incremental auto-setup và auto-update plugin; kiểm tra log và xử lý ngoại lệ — Test: `py -3 tests/test_mcp_first_auto_setup.py` PASS 100%.
  - Chạm: `tests/test_mcp_first_auto_setup.py` → file test mới
  - Cần: T1.3, T2.1, T3.1

## Cụm song song
- Cụm 1: T1.1 → T1.2 → T1.3 (chuỗi chính sách và instruction MCP-First).
- Cụm 2: T2.1 (incremental auto-setup trong `tdq_setup.py`).
- Cụm 3: T3.1 (hook SessionStart tự động cập nhật plugin).
- Cụm 4: T4.1 (tổng hợp test suite độc lập cho toàn bộ các module).
- Thực thi tuần tự trên nhánh `main` inline theo thứ tự phụ thuộc để đảm bảo tính nhất quán của file setup và hook.

## Luật file nóng (một file, nhiều task chạm)
- `scripts/tdq_setup.py`: T1.2, T2.1 và T3.1 cùng chạm → áp dụng chiến lược **nâng lên đợt sớm**: T1.2 hoàn thành khối instruction trước, sau đó T2.1 hoàn thành logic setup bù, T3.1 hoàn thiện logic đồng bộ plugin.
- `hooks/scripts/session_start.py`: T1.3 và T3.1 cùng chạm → T1.3 sửa khối anchor trước, T3.1 gắn hàm auto-update plugin vào đầu main.

## Definition of Done
- [x] Q1 Instruction & Anchor MCP-First — `KHOI_HUONG_DAN` và `[TDQ:ANCHOR]` chứa nguyên tắc `MCP-First` và pre-flight check.
- [x] Q2 Pre-flight Check Guide & Spec/Plan — `mcp-first-guide.md` hướng dẫn check kết nối Roblox, Unity, DevTools; spec §3b và plan template có tiêu chí MCP.
- [x] Q3 Incremental Auto-Setup khi đổi version — `tu_dong_cap_nhat_khi_doi_phien_ban` chạy setup bù và cập nhật mốc phiên bản thành công khi phát hiện version cũ.
- [x] Q4 SessionStart Auto Update Plugin — Khi phiên bản cài user scope cũ hơn repo, hook tự động gọi cập nhật/đồng bộ plugin.
