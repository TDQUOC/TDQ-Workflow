# Brief — sai khuôn thì lấy test làm chuẩn
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

Người dùng hỏi: "có cách nào để claude đọc output trả ra để hạn chế lỗi kết quả sai khuôn không?"
Tôi đưa 4 phương án (A lấy test làm chuẩn khi sai khuôn · B hỏi lại Codex một lần bằng
`codex exec resume` · C kèm trích đoạn ≤ 1.500 ký tự · D đổi provider tôn trọng schema).
Người dùng trả lời: "a".

**Đọc lần đầu:**
- **Mục tiêu:** một lượt `tdq_codex.py run` bị chấm `fail · ly_do=ket-qua-sai-khuon` không còn
  làm hỏng task đã làm đúng. Leader chạy lại test của task: test xanh + vùng file `dat` → tính
  xong; test đỏ → fail.
- **Phạm vi đoán:** luật `skills/tdq-build/references/codex-mode.md` (bước 4–6 của một task),
  có thể cả `scripts/tdq_codex.py` (JSON phán quyết gợi ý bước kế, hoặc nhận lệnh test để tự
  chạy lại), test, bundle.
- **Chỗ chưa rõ:**
  - Ai chạy lại test: leader tự chạy theo luật, hay `run` nhận `--lenh-test` và tự chạy?
  - Chỉ áp cho `ket-qua-sai-khuon`, hay cả `khong-co-ket-qua` và `model-bao-chua-xong`?
  - Trạng thái in ra khi test cứu được lượt: `xong` hay một trạng thái riêng để còn đếm được?
  - Timeout, deny, exit ≠ 0 có được cứu không (đề xuất: không)?
  - Dòng log và bench đếm lượt "cứu bằng test" thế nào?
- **Kiểm hiệu ứng LSP:** `tdq_lsp.py check` 7/7 bậc ĐẠT. Ký hiệu thử: `claude_export.sha256_of`
  (`tdq_checkportable.py` có hàm trùng tên, đã loại khỏi phép đếm).
  - `find_references`: 10 tham chiếu, gồm 5 ở `scripts` và 5 ở `tests`.
  - grep: `claude_export.py` 3 + `build_portable.py` 2 + `test_claude_export.py` 5 = 10, tức 3 file.
  - Kết luận: LSP phủ đủ 3/3 file và nhìn thấy tham chiếu chéo file → PASS.

**Uỷ quyền trước (nguyên văn):** "1a và merge vào main và pump version và commit". Tới bước
report: commit trên nhánh, tăng version, merge `--no-ff` vào `main` mà không hỏi lại. KHÔNG push.

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-09-14: 10 skill trên đĩa (`--loc` giữ 8, ẩn 2), cộng skill
built-in trong context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | phase analyze đang chạy |
| tdq-spec | plugin:tdq-workflow | NỀN | phase spec |
| tdq-plan | plugin:tdq-workflow | NỀN | phase plan |
| tdq-build | plugin:tdq-workflow | NỀN | implement/QC/report; chính là file luật `codex-mode.md` bị sửa |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật chung, state, duyệt |
| tdq-lsp-setup | plugin:tdq-workflow | NỀN | thứ tự tìm ký hiệu code |
| Đã xét 4 skill khác (tdq-status, tdq-check-status, graphify, built-in) | plugin/user/built-in | KHÔNG | khác lĩnh vực |

### Điều đọc được từ code

- `scripts/tdq_codex.py` `_cli_run` in ra 1 dòng JSON `{"trang_thai", "giay", "vung_file"}`, **không
  có `ly_do`**. Mã lý do chỉ nằm ở cuối dòng log gửi ra stderr (`in_log_luot`, tắt được bằng
  `TDQ_LOG=0`). Leader đọc JSON (bước 4 luật) nên chỉ thấy `fail` và không phân biệt được "Codex
  làm hỏng" với "Codex làm xong nhưng trả lời sai khuôn".
- Không script nào đọc JSON của `run` (grep `trang_thai`: `tdq_eval.py` có trường cùng tên nhưng
  của bộ đo khác). Người đọc duy nhất là leader, nên thêm khoá vào JSON không làm vỡ ai.
- `run` trả exit 1 với mọi trạng thái khác `xong`; vùng file vẫn được hậu kiểm (`hau_kiem`) ở mọi
  trạng thái, kể cả `fail`.
- `MA_LY_DO` có 6 mã. Ba mã nằm ở khâu đọc câu trả lời: `khong-co-ket-qua`, `ket-qua-sai-khuon`,
  `model-bao-chua-xong`. Ba mã còn lại xảy ra trước khâu đó: `qua-han` (bị giết giữa chừng),
  `bi-chan` (hàng rào chặn), `exit-khac-0` (CLI lỗi).
- Luật `codex-mode.md` bước 6 ĐÃ lấy test làm chuẩn ("Test xanh + `dat` → tick"). Nhưng luật không
  nói phải làm gì khi phán quyết là `fail`, nên leader dễ bỏ qua bước chạy lại test.
- `tdq_bench.doc_log_codex` chỉ lấy mẫu thời gian từ lượt `xong`. Lượt `fail` không vào mẫu dù Codex
  có thể đã làm đúng.
- `dong_log_nhip` (dòng log nhịp đỏ/xanh) chỉ có ở test, không lệnh nào ghi ra.
- Bản sao luật cần sinh lại qua `build_portable.py`: 4 bản `codex-mode.md` + các bản `tdq_codex.py`.
- `_cli_run` chưa có test đơn vị đầu-cuối (nợ từ request trước).

### Nghiên cứu

B2: BỎ — thay đổi thuần nội bộ workflow (luật đọc phán quyết + 1 khoá JSON), không có thư viện
hay chuẩn ngoài nào để tra. Hành vi của Codex CLI với schema đã đo thật ở request
`2026-09-14-1252-run-cham-fail-sai-schema`.

Vòng scope: BỎ — request chỉ đổi một hành vi (cách xử lý một lượt có mã lý do cụ thể), không
chạm dữ liệu user, tiền hay API công khai, và các mặt còn lại suy ra được từ code.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| research (B2) | BỎ | thuần nội bộ, không có nguồn ngoài |
| vòng scope | BỎ | một hành vi, không dấu hiệu nào của scope-round |
| spec | CÓ | lane full |
| plan | CÓ | lane full |
| implement | CÓ | sửa `tdq_codex.py` + luật + test + bundle |
| qc | CÓ | có test đơn vị + lượt Codex thật |
| report | CÓ | kèm commit, tăng version, merge (đã uỷ quyền trước) |

Luồng tính năng:
1. `run` báo lý do trong JSON và chỉ ra lượt nào đáng chạy lại test.
2. Leader chạy lại test theo luật: xanh + vùng `dat` thì tick, đỏ thì fail.
3. Ghi dấu lượt "cứu bằng test" để QC/report/bench đếm được.

## Hỏi đáp

Vòng chi tiết 1 · 2026-09-14 · người dùng trả lời nguyên văn: "1a 2a 3a 4a"

1. Việc chạy lại test đặt ở đâu?
   - A (đề xuất): `run` thêm `ly_do` + `can_chay_lai_test: true` vào JSON, leader tự chạy lại test theo luật
   - B: `run` nhận `--lenh-test`, tự chạy test, in trạng thái riêng
   - C: chỉ sửa luật, leader đọc dòng log stderr
   - **Chọn: A**
2. Mã lý do nào được cứu bằng test?
   - A (đề xuất): `ket-qua-sai-khuon` + `khong-co-ket-qua`
   - B: chỉ `ket-qua-sai-khuon`
   - C: cả ba mã khâu đọc câu trả lời, gồm `model-bao-chua-xong`
   - `qua-han`/`bi-chan`/`exit-khac-0` không bao giờ được cứu (chung mọi phương án)
   - **Chọn: A**
3. Lượt được test cứu thì ghi và đếm thế nào?
   - A (đề xuất): dòng log `run` giữ `fail · ly_do=…`; leader tick kèm `(cứu bằng test · ly_do=…)`
     trong plan; bench vẫn chỉ lấy mẫu lượt `xong`
   - B: lệnh con ghi dòng `xong-nho-test` để bench đếm
   - **Chọn: A**
4. Bổ sung thêm gì không? — **Chọn: A** (không, làm tiếp)

Kiểm cổng (B6): phạm vi rõ — CÓ · cần cài gì — KHÔNG · phạm vi QC đã xác định — CÓ (test đơn
vị hàm mới + khuôn JSON, luật + bundle khớp, lượt Codex thật in đủ khoá mới). Hết câu hỏi có
thể đổi sản phẩm → sang spec.
