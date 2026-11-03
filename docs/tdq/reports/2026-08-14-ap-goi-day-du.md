# REPORT — Áp Gói đầy đủ Đ1–Đ7 (`2026-08-14-ap-goi-day-du` · lane full · mode main · 17/17 task tick đủ)

Đã làm — **P1 văn bản (Đ2–Đ7)**: dời nhánh quick khỏi thân `tdq-intake/SKILL.md` sang `quick-lane.md` (3 → 12 bước đánh số), hạ Phần B/C của `tdq-build/SKILL.md` xuống `qc.md` + `report-template.md` và để lại dòng trỏ có chữ "BẮT BUỘC mở file đó", gom phần nền của 3 file conventions vào `## Phụ lục` mà giữ nguyên 100% câu chữ, khử 2 từ mơ hồ ở `scope-round.md`, dán chú "nhắc lại có chủ ý" ở đúng 8 chỗ chép lại luật, thêm khối "Return format — copy this shape exactly" cho 3 file agent.

Đã làm — **P3 mã (Đ1)**: thêm cờ `--loc <từ khoá>` và `--tat-ca` cho `scripts/skill_inventory.py` (bản lọc CẤM ẩn nguồn `project` và `plugin:tdq-workflow`, luôn in dòng báo đã ẩn bao nhiêu + lệnh xem đủ), 2 lớp test mới, cập nhật 2 dòng lệnh B0 trong `skills/tdq-intake/references/`.

Kết quả: tầng `nạp khi gọi skill` **8.473 → 7.579 token** (−894, −10,6%) · thân `tdq-build/SKILL.md` 1.936 → 1.536 (−21%) · thân `tdq-intake/SKILL.md` 1.844 → 1.288 (−30%) · output kiểm kê skill mỗi lần chạy B0 **39.722 → 1.845 byte** khi lọc (−95,4%, ≈ −9.300 token), bản không cờ giữ nguyên từng byte · phần bị dời nằm ở tầng `đọc khi cần` 43.981 → 46.188 — đổi tầng chứ không xoá.

Số luật (đếm mệnh lệnh theo 10 cụm file): **0/10 dòng giảm** — 7 dòng tăng, 3 dòng giữ nguyên. Không đề xuất nào làm mất một luật nào.

Kiểm: `python3 -m pytest tests/ -q` → **569 passed, 241 subtests passed, 0 failed** (mốc trước 563) · `doc_lint.py --pair <spec> <plan>` exit 0 · `git status --porcelain -- hooks portable` rỗng · QC 15 hạng mục, **Q1–Q14 PASS** kèm lệnh + output thật, Q15 (model hạng thấp chạy thử) kết luận "không bỏ bước nào" · QC độc lập bằng agent `tdq-qc-tester` cũng ra PASS Q1–Q14 · 0 vòng fix.

Đầu ra: `docs/tdq/qc/2026-08-14-ap-goi-day-du.md` (bảng đối chiếu luật · 15 hạng mục · `## Ảnh hưởng Đ1` · chạy thử model hạng thấp · `## QC độc lập`) · `docs/tdq/plan/2026-08-14-ap-goi-day-du.md` · 20 file đã sửa trong `skills/`, `agents/`, `scripts/`, `tests/`.

Giới hạn: hai tiêu chí SỐ trong spec §6 không đạt theo nghĩa đen, ghi rõ trong file QC thay vì nới âm thầm — Q2 dừng ở 1.536 token thay vì mốc < 1.400 (muốn thấp hơn phải cắt tiếp Luật cứng + Phần A của `tdq-build/SKILL.md`, ngoài phạm vi Đ3); Q3 "số từ bằng nhau" không thể đúng khi Đ4 buộc thêm nhãn `## Phụ lục`, nên đọc theo Quyết định 4A là **0 từ bị mất**, chứng minh bằng diff từng từ. Cả hai vẫn PASS theo Quyết định 1A: đích token là đích MỀM, điều kiện thật là token giảm + số luật không giảm.

Giới hạn khác: nhánh "không bao giờ ẩn nguồn `project`" của `--loc` mới chỉ được phủ bằng unit test — máy thật hiện có 0 skill nguồn `project` nên chưa có bằng chứng ngoài đời. `hooks/` và `portable/` không đụng tới, nên bản portable của workflow chưa nhận các thay đổi này.

Git: **chưa commit, chưa push**, không có commit gỡ chặn nào giữa build.
