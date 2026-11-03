# Mini-plan: Cài đặt/cập nhật Agy, Codex, TDQ Plugin và Smoke Test toàn diện trên macOS & Linux

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Mục tiêu
Triển khai bộ ba công cụ cốt lõi (**Agy**, **Codex**, **TDQ Workflow Plugin v0.73.1**) lên 2 môi trường từ xa:
1. **macOS Apple Silicon ARM64** (`tdq@100.105.75.71`, pass: `1772`)
2. **Linux Ubuntu x86_64** (`admin@100.102.92.43` / `tdq`, pass: `1`)

Thực hiện kiểm thử thực tế (real smoke test project) mô phỏng đầy đủ vòng đời phát triển của TDQ Workflow, kiểm tra các tương tác MCP, CLI, Git hooks và bộ tìm kiếm 3 tầng, sau đó thống kê và kết xuất báo cáo đa nền tảng chi tiết.

## Các đầu việc thực hiện (Tasks)

- [ ] **T1**: Viết controller SSH tự động kết nối và khảo sát môi trường hiện tại của cả 2 máy (Node, Python, Git, vị trí cài đặt Agy, Codex CLI, Claude/Codex config).
- [ ] **T2**: Kiểm tra, cập nhật hoặc cài đặt:
  - **Agy**: Cấu hình và kiểm tra binary `agy` / portable skills.
  - **Codex**: Kiểm tra binary `codex`, cấu hình `~/.codex/config.toml` và mcp.
  - **TDQ Workflow Plugin**: Đồng bộ mã nguồn mới nhất (kèm tính năng Spec Fresher-Centric vừa xây dựng) vào thư mục cache plugin `~/.claude/plugins/cache/tdq-local/tdq-workflow/0.73.1/` trên cả 2 máy.
- [ ] **T3**: Chạy `tdq_setup.py` trên cả 2 máy để thiết lập và ghim cấu hình `~/.claude/CLAUDE.md`, kiểm tra 8 bậc setup.
- [ ] **T4**: Tạo smoke test project thực tế `smoke_test_tdq_crossplatform` trên từng máy:
  - Khởi tạo git repo và cấu hình project.
  - Chạy chu trình state: `init` -> `plan` -> `implement` -> `qc` -> `report` -> `idle`.
  - Kiểm tra các lệnh core: `tdq_state.py`, `tdq_harvest.py`, `tdq_test.py`, `tdq_finish.py`.
- [ ] **T5**: Thu thập số liệu thời gian, hiệu năng thực thi, bộ nhớ và lập bảng tổng hợp kết quả chi tiết cho người dùng.

## Definition of Done (QC Kỹ Lưỡng)
- [ ] Q1: Kết nối SSH thành công tới cả 2 máy macOS và Linux.
- [ ] Q2: Kiểm tra trạng thái Agy và Codex trên cả 2 máy, đảm bảo file config hợp lệ.
- [ ] Q3: Plugin TDQ Workflow v0.73.1 được đồng bộ trọn vẹn và `tdq_setup.py` chạy qua kiểm tra các bậc.
- [ ] Q4: Kịch bản smoke test project chạy từ đầu đến cuối không có ngoại lệ (exit 0) trên cả 2 hệ điều hành.
- [ ] Q5: Báo cáo đối sánh hiệu năng đa nền tảng (macOS vs Linux vs Windows) đầy đủ, rõ ràng.
