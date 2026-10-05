# Changelog — bản lưu trữ 2

Các bản 0.39.0 đến 0.37.0, tách khỏi `CHANGELOG.md` ngày 2026-10-03 (0.39.0 ngày 2026-10-05) để file chính dưới trần R6
500 dòng (`docs/CHANGELOG-archive.md` đã đầy). Mới nhất trên cùng, chữ nghĩa copy nguyên văn.
Lần tách sau: chuyển các bản cũ nhất còn trong `CHANGELOG.md` vào ĐẦU file này.

## 0.39.0 — 2026-09-03

Thang `tdq_lsp.py kiem` thêm **bậc 7** và luật thứ tự tìm kiếm đổi từ một thứ tự cứng sang chọn
lớp theo LOẠI truy vấn. Lý do: thang cũ báo **6/6 ĐẠT** trong cả trạng thái độ phủ truy vấn quan
hệ 7 % lẫn 100 % — nó kiểm sự tồn tại, không kiểm hiệu quả. Báo cáo:
`docs/tdq/report/2026-09-03-0053-sua-luat-va-kiem-lsp-that.md`.

- **`scripts/tdq_lsp.py`** — bảng `LANG_CONFIG` (file mốc gốc import cho 26 ngôn ngữ, chia nhóm
  A/B) và bậc 7 `bac7_cau_hinh_goc_import`. Nhóm B (Python, TS/JS, Lua, C/C++) thiếu file mốc thì
  **CHẶN, thoát 3** vì chỉ mục liên file chết âm thầm mà test vẫn xanh; nhóm A (`go.mod`,
  `Cargo.toml`…) chỉ cảnh báo vì thiếu là dự án không build được, tự lộ. Script chỉ in nội dung
  cần tạo và xin phép, không bao giờ tự ghi file.
- **`skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`** — luật gốc thay bằng bảng 4 loại truy
  vấn kèm số đo: quan hệ → `mcp__lsp__*` (phủ 15/15, grep chỉ precision 67 %); tên chính xác →
  grep (~0,1 s so với 3–6 s); khái niệm mơ hồ → lumen (LSP xếp đích hạng 13/62); chưa phân loại
  → gọi song song. Câu luật chép lại nguyên văn ở đủ 5 chỗ móc.
- **`skills/tdq-intake/references/kiem-lsp-hieu-ung.md`** (mới) — bước kiểm **bằng hiệu ứng** ở
  intake: so `find_references` với grep theo số file phân biệt, ĐẠT khi LSP ≥ grep. Bậc 7 bắt
  nguyên nhân đã biết, bước này bắt triệu chứng dù nguyên nhân là gì.
- **`pyrightconfig.json`** (mới) — chính file mốc mà repo này đang thiếu, đưa độ phủ truy vấn
  quan hệ từ 1/15 file lên 15/15.

## 0.38.0 — 2026-09-02

Năm luật rời `~/.claude/CLAUDE.md` về plugin, instruction toàn cục cắt 57 → **29 dòng (−49%)**.
Thứ tự bắt buộc: viết luật vào `skills/` trước, kiểm, rồi mới cắt. Phương án gốc:
`docs/tdq/report/2026-09-01-2301-quet-instruction-vao-plugin.md`.

- **`skills/tdq-conventions/`** — `approval.md` nhận luật "không tự vào plan mode" (dưới bảng
  "NOT an approval", cùng họ); `SKILL.md` §7 Git nhận luật init git/worktree và ngoại lệ tự
  commit khi build TDQ bị chặn, đặt sát dòng nó là ngoại lệ; §8 Research nhận luật mem0.
- **`scripts/doc_lint.py`** — trần R6 của `tdq-conventions` 165 → 168, đổi lấy 28 dòng bỏ khỏi
  file nạp mỗi lượt của mọi project.
- **`docs/tdq/audit/luat-hien-co.md`** — 10 neo lệch do phần chèn trên được trỏ lại đúng chỗ.

## 0.37.0 — 2026-09-01

Lane nhanh có bước phân tích HIỆN TÊN, và độ sâu của bước đó có ngưỡng rõ ràng. Trước bản này
`phase_key` nuốt mọi pha của lane nhanh về hàng `quick`, nên phân tích không nhìn thấy được ở
đâu cả. Quan trọng: đây là phương án KHÔNG thêm cổng duyệt — lane nhanh vẫn đúng một cổng.

- **`scripts/tdq_state.py`** — thêm hàng `quick_analyze` vào `PHASE_TABLE` và `PHASE_ORDER`;
  `phase_key` trả hàng đó khi `lane=quick`, `phase=analyze` và chưa duyệt. `CONG_THEO_LANE`
  và `APPROVE_TARGETS` giữ NGUYÊN — có test khoá riêng canh điều này. Thêm khoá `brief_file`
  để đăng ký đường dẫn brief, ngang hàng `spec_file`/`plan_file`.
- **`skills/tdq-intake`** — `quick-lane.md` từ 9 lên 10 bước, chèn bước ghi kết quả phân tích
  vào brief; thêm mục ngưỡng B0/B1/B2: B1 đọc code LUÔN LUÔN (LSP + lumen song song), B0 chỉ
  khi vùng chưa có tiền lệ, B2 chỉ khi có ẩn số ngoài. Bỏ B0 hay B2 phải ghi một dòng lý do
  vào `## Phạm vi` của mini-plan — bỏ im lặng là lỗi QC.
- Ngưỡng lấy từ số đo thật trên 43 request đã đóng sổ. Pha `analyze` trung vị 372 s model,
  một request lane nhanh trọn gói 533 s. Bắt cả ba bước không điều kiện làm lane nhanh chậm
  thêm ~70 %. Chi tiết: `docs/tdq/report/2026-09-01-2122-lane-nhanh-kiem-ke-nang-luc.md`.
