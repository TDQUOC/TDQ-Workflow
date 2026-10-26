# REPORT — Giảm timeout và thời gian chờ agent-lsp (`2026-10-26-0224-giam-timeout-agent-lsp` · lane full · mode main · 8 task hoàn tất)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:**
- **O1 (Chính sách chọn công cụ 3 tầng & Trung hòa blast_radius):** Cập nhật `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `uu-tien-tim-kiem-chi-tiet.md`, `tdq_setup.py` và `docs/claude-md-mau.md`, phân định rõ: dùng `find_references` cho symbol cụ thể, `graphify affected` cho kiến trúc đa tệp, trung hòa hoàn toàn chỉ thị upstream ép gọi `blast_radius` bừa bãi.
- **O2 (Giới hạn chờ MCP Client 90s):** Bổ sung hàm thiết lập `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT = "90000"` trong khối `env` của `~/.claude/settings.json` trong `scripts/tdq_setup.py`, tạo bản sao lưu `.tdq.bak`, cắt đứt hoàn toàn nguy cơ client bị treo 1.800 giây khi server LSP gặp sự cố.
- **O3 (Cổng kiểm soát blast_radius & Mạch ngắt Circuit Breaker):** Cấu hình `lsp_gate.py` và `hooks.json` chặn lệnh gọi `blast_radius` khi `changed_files` > 3 tệp, `scope != "exported"`, hoặc `include_transitive=true`. Tự động ngắt mạch (chuyển sang trạng thái MỞ) khi lần gọi `blast_radius` gần nhất thất bại hoặc có ≥2 lỗi LSP liên tiếp trong workspace.
- **O4 (Sổ quan sát & Phân loại kết quả LSP):** Đăng ký sự kiện `PostToolUseFailure` trong `hooks.json` và bổ sung đo lường trong `search_observe.py`: tính toán chính xác `duration_ms` bằng cách ghép cặp mốc thời gian, gán nhãn 4 trạng thái `outcome` (`ok`, `empty`, `error`, `timeout`), đồng thời bảo toàn hợp đồng mở khóa `khai_niem` ở `PreToolUse` để không bao giờ chặn nhầm lệnh `Grep`.
- **O5 (Thống kê p50/p95 & Đối chiếu Caller Oracle):** Bổ sung các hàm thuần `thong_ke_lsp` và `doi_chieu_caller_oracle` trong `scripts/search_rules.py`. Mở rộng CLI `scripts/search_replay.py --lsp-telemetry` hỗ trợ ghép cặp sự kiện từ transcript JSONL và xuất báo cáo độ trễ phân vị, tỷ lệ `recall`/`precision` chuẩn hóa.

**Kết quả:**
- **Definition of Done Q1–Q5:** Đạt 5/5 PASS ở mức `ultra` (ghi nhận chi tiết tại `docs/tdq/qc/2026-10-26-0224-giam-timeout-agent-lsp.md`).
- **Hồi quy bài kiểm thử vùng chạm:** 168 passed, 18 subtests passed trên toàn bộ 6 tệp test (`test_claude_md_core.py`, `test_auto_update_setup.py`, `test_lsp_gate.py`, `test_search_observe.py`, `test_search_rules.py`, `test_search_replay.py`).
- **Bảo toàn hợp đồng kiến trúc & Hook:** 11 passed ở `test_subagent_start.py` (khớp 14 hooks trên 7 sự kiện), 9 passed ở `test_docs_consistency.py`, 4 passed ở `test_kien_truc.py`, pyright 0 lỗi.
- **Archify Explainer:** Trạng thái `current`, `valid: true` liên kết chặt chẽ với Spec.
- **Ngân sách Token & Linter:** `doc_lint` 0 lỗi trên toàn bộ tài liệu sửa đổi; `token_budget` khớp 100%.

**Giới hạn:**
- Thiết lập `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT = "90000"` được áp dụng ở phạm vi môi trường người dùng (`~/.claude/settings.json`) khi chạy `tdq_setup.py`. Nếu người dùng chạy trên môi trường sandbox không có quyền ghi vào `~/.claude/settings.json`, cần thiết lập biến môi trường này thông qua shell hệ thống.
- Cổng ngắt mạch Circuit Breaker tính trạng thái dựa trên các bản ghi `lsp_ket_qua` trong sổ phiên `.tdq-search.jsonl` của workspace hiện hành. Khi mở một phiên làm việc mới (fresh session), bộ đếm lỗi được reset lại từ đầu.

**Lệch spec:** 0 mục lệch spec.

**Git:** Sẵn sàng commit trên nhánh `bugfix/giam-timeout-agent-lsp`.
