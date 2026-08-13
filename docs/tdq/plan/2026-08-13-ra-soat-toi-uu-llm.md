# PLAN — Rà soát mức tối ưu cho LLM của tdq-workflow

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-ra-soat-toi-uu-llm.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — mọi task đổ về cùng một báo cáo và cùng một script đo, tách worktree chỉ tốn công merge. (user chốt "main" lúc 2026-08-13)
Trạng thái plan: HOÀN THÀNH

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. **Cấm sửa file sản phẩm.** Request này chỉ ĐO và VIẾT BÁO CÁO. File được phép tạo/sửa:
   `scripts/context_surface.py`, `tests/test_context_surface.py`, và tài liệu TDQ của
   chính request này. Mọi khuyến nghị nằm trong báo cáo dưới dạng khối trích.

## P1 — Công cụ đo bề mặt

- [x] **T1.1** (n5 e12m) `tests/test_context_surface.py`: script liệt kê đủ 3 tầng nạp
  (description · thân SKILL.md · references/agent/hook), mỗi dòng có ký tự và tầng, và
  có cờ tắt log — Test: `python3 -m pytest tests/test_context_surface.py -q` đỏ đúng lý do thiếu file
- [x] **T1.2** (n8 e25m) `scripts/context_surface.py`: quét `skills/`, `agents/`,
  `hooks/scripts/`, `portable/`, in bảng `file | tầng nạp | ký tự | token ước tính |
  tần suất vào context`; log timestamp ra stderr, tắt bằng `--quiet` — Test: `python3 -m pytest tests/test_context_surface.py -q` xanh và `python3 scripts/context_surface.py` exit 0
- [x] **T1.3** (n5 e12m) Thêm chế độ `--hooks` đo thời gian chạy từng hook: chạy mỗi hook
  5 lần với payload mẫu ở `tests/fixtures/`, in trung vị theo mili-giây — Test: `python3 scripts/context_surface.py --hooks` in đủ 6 dòng có đơn vị `ms`

**Xong P1 khi**: một lệnh dựng lại được cả bảng bề mặt lẫn bảng tốc độ hook, test xanh.

## P2 — Thu số đo

- [x] **T2.1** (n3 e10m) Chạy `context_surface.py`, chốt bảng bề mặt ≥ 35 file, lưu tạm
  vào mục `## Đo bề mặt` của báo cáo — Test: `grep -c "^| " ` mục đó ≥ 35
- [x] **T2.2** (n3 e8m) Chạy `context_surface.py --hooks`, ghi mục `## Tốc độ hook` kèm
  điều kiện đo — Test: `grep -c "ms" ` mục đó ≥ 6

**Xong P2 khi**: hai bảng số đo đã nằm trong báo cáo, mọi con số tái lập được bằng một lệnh.

## P3 — Phân tích

- [x] **T3.1** (n5 e15m) Dò trùng lặp chéo: `skills/` với `portable/workflow/`, và luật
  bị chép ở nhiều file (tick, mode, khuôn duyệt, luật `(mcp)`). Ghi mục `## Trùng lặp`,
  mỗi mục ≥ 2 đường dẫn kèm số dòng — Test: mỗi dòng trong mục có ≥ 2 dấu `:` chỉ vị trí
  - Dùng: `graphify`
  - Để: hỏi quan hệ file trong `graphify-out/` để không bỏ sót cặp trùng, nạp trước bước đỏ.
  - Ra: mục `## Trùng lặp` trong `docs/tdq/reports/2026-08-13-ra-soat-toi-uu-llm.md`
  - Kiểm: `grep -c ":" ` mục đó ≥ 1 dòng cho mỗi cặp trùng tìm được
  - Không dùng cho: xếp hạng cơ hội (T3.3) — việc đó do người đọc luật quyết, không do đồ thị
- [x] **T3.2** (n8 e25m) Phân loại nội dung 6 `SKILL.md` theo 5 nhóm của SkillReducer
  (luật lõi · nền tảng · ví dụ · khuôn mẫu · phần thừa), quy ra ký tự từng nhóm — Test: bảng có đủ 6 skill × 5 nhóm, tổng ký tự mỗi skill khớp `wc -c` sai số ≤ 2%
- [x] **T3.3** (n5 e15m) Xếp hạng cơ hội theo `mức tiết kiệm ước tính × tần suất`, mỗi
  dòng có cột `luật bị đụng` và `cách chứng minh giữ nguyên` — Test: không dòng nào để trống hai cột đó
  - Dùng: `tavily-primary` (mcp)
  - Để: kiểm lại số liệu trích từ SkillReducer trước khi lấy làm căn cứ xếp hạng, nạp trước bước đỏ.
  - Ra: dòng nguồn kèm URL trong mục `## Xếp hạng` của báo cáo
  - Kiểm: `grep -c "https://" ` mục đó ≥ 1
  - Không dùng cho: đo số liệu nội bộ (P2) — số đó lấy từ `context_surface.py`, không lấy từ web
- [x] **T3.4** (n5 e20m) Viết 2–3 bản vá mẫu cho cơ hội đứng đầu, dạng khối trích
  trước/sau trong báo cáo, KHÔNG áp vào file thật — Test: `git status --short` không có file sản phẩm nào bị sửa

**Xong P3 khi**: có bảng xếp hạng và bản vá mẫu, chưa file sản phẩm nào bị đụng.

## P4 — Báo cáo

- [x] **T4.1** (n5 e15m) Hoàn thiện `docs/tdq/reports/2026-08-13-ra-soat-toi-uu-llm.md`:
  đủ 5 mục (`Đo bề mặt`, `Tốc độ hook`, `Trùng lặp`, `Xếp hạng`, `Bản vá mẫu`) + kết luận
  ngắn — Test: `python3 scripts/doc_lint.py <file>` exit 0 và `wc -l` ≤ 120
  - Dùng: `mem0-memory` (mcp)
  - Để: ghi đúng một fact ngắn về kết luận kiến trúc của lần rà soát này, sau khi báo cáo chốt.
  - Ra: một memory trong mem0 với `project` = `TDQWorkflow`
  - Kiểm: `search_memories` với từ khoá "context surface" trả về fact vừa ghi
  - Không dùng cho: lưu số đo chi tiết — số đo nằm ở báo cáo, không nhét vào bộ nhớ dài hạn

**Xong P4 khi**: báo cáo sạch lint, trong trần 120 dòng, mọi mục có số đo thật.

## P5 — Log & test bắt buộc

- [x] **T5.1** (n3 e10m) Log service của `context_surface.py`: timestamp, ra stderr, tắt
  bằng `--quiet`, có test riêng — Test: `python3 scripts/context_surface.py --quiet 2>&1 >/dev/null` không in dòng nào
- [x] **T5.2** (n3 e8m) Chạy full suite một lần — Test: `python3 -m pytest tests/ -q` exit 0

**Xong P5 khi**: toàn bộ suite xanh và log tắt được.

## Definition of Done

Trỏ về §6 của spec — 9 hạng mục:

1. Q1 `python3 scripts/doc_lint.py docs/tdq/reports/2026-08-13-ra-soat-toi-uu-llm.md` → exit 0.
2. Q2 `wc -l` báo cáo → ≤ 120 dòng.
3. Q3 mục `## Đo bề mặt` → ≥ 35 dòng dữ liệu.
4. Q4 `python3 scripts/context_surface.py` → exit 0, in bảng.
5. Q5 `python3 -m pytest tests/test_context_surface.py -q` → exit 0.
6. Q6 mục `## Tốc độ hook` → ≥ 6 dòng có `ms`.
7. Q7 mọi dòng xếp hạng có cột `luật bị đụng` không trống.
8. Q8 `git status --short` → chỉ file ở §2 của spec và tài liệu TDQ của request này.
9. Q9 `python3 -m pytest tests/ -q` → exit 0.
