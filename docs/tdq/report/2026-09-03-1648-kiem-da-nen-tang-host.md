# REPORT — Kiểm bộ workflow ở máy khác và trên Linux/Windows (`2026-09-03-1648-kiem-da-nen-tang-host` · lane full · mode main · 9/9 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** viết script đếm bằng `ast` (không grep) cho 5 mẫu mã quyết định tính đa nền tảng ·
chạy 3 lần giả lập trên macOS tái hiện đúng cơ chế hỏng · viết báo cáo tương thích 4 phát hiện
+ 4 điểm mạnh + 3 điểm chưa chốt · viết 8 lệnh để user tự chạy trên Linux/Windows · viết 13 ca
test giữ mọi con số và vị trí trong báo cáo khỏi mục. Không sửa một dòng mã sản phẩm nào.

**Kết quả — 4 phát hiện:** **P1 (chặn đường)** cả 3 host đều gọi thẳng `python3` trong
`hooks.json` (5/5, 5/5, 2/2 command), tên mà PowerShell thuần không phân giải được ·
**P2 (cao)** cảnh báo "bundle dựng ở máy khác" trong `tdq_checkportable.py:367` là mã chết:
điều kiện `if "~" in noi_dung` quét cả file, mà mô tả trong file có `~/.gemini/...`, nên nhánh
`elif` phát hiện thư mục nhà lạ không bao giờ chạy tới — đúng ca user đang hỏi thì cổng gác
tắt · **P3 (trung bình)** bundle agy nướng cứng `$HOME` máy dựng, có chủ ý và có lý do, nhưng
lời dặn "phải dựng lại" chỉ nằm trong docstring, README bundle không nói gì · **P4 (cao trong
mode sub-agent)** `tdq_team.py:896` chạy `Test:` qua `shell=True`, trên Windows là cmd.exe nên
plan viết `python3 -m pytest` sẽ đỏ sai lý do và `merge` từ chối nhánh lành.

**Ba điểm mạnh:** 0 chỗ `open()` thiếu `encoding=` · 0 import stdlib chỉ có trên POSIX ·
0 đường dẫn tuyệt đối cứng và chỉ 1 chỗ đọc `sys.platform`. Nửa khó nhất của bài toán encoding
đã đúng sẵn.

**Ba điểm CHƯA chốt được vì không có máy thật:** console encoding trên Windows khi stdout là
pipe (18 chỗ `subprocess(text=True)` thiếu `encoding=`, 0 chỗ ép UTF-8 trong toàn repo — giả
lập ném `UnicodeEncodeError` thật, nhưng bản Python trên máy đích mới quyết định) · đường dẫn
plugin agy (tài liệu công khai lệch với đường dẫn repo đang dùng) · hook Codex trên Windows
native. Mỗi điểm nối tới một lệnh cụ thể trong file lệnh kiểm.

**Kiểm:** `pytest -q` 100 failed / 1531 passed — ĐÚNG BẰNG mốc đỏ 100 có sẵn, không sinh ca đỏ
mới · bộ test mới 13 ca xanh, 34 subtest · QC PASS 15/15 hạng mục, không phải mở vòng fix ·
`doc_lint` exit 0 trên cả 4 file `.md` · `git status` xác nhận 0 file mã sản phẩm bị sửa.

**Đầu ra:** `docs/tdq/report/<slug>-tuong-thich.md` (báo cáo chính) ·
`docs/tdq/report/<slug>-lenh-kiem.md` (8 lệnh user tự chạy) ·
`docs/tdq/report/<slug>-bang-chung.md` (output nguyên văn 3 lần giả lập) ·
`tools_kiem/dem_da_nen_tang.py` · `tests/test_bao_cao_da_nen_tang.py` ·
`docs/tdq/qc/<slug>.md`.

**Khác biệt luật↔code phát hiện dọc đường:** `skills/tdq-spec/SKILL.md` bắt buộc chạy phase
`diagram` sau `spec`, nhưng `PHASE_TABLE` trong `tdq_state.py` không có phase đó và skill
`tdq-diagram` không tồn tại trong repo — `set phase=diagram` bị từ chối. Đã báo user ngay lúc
gặp và đi thẳng sang `plan`. Nằm ngoài phạm vi request này.

**Còn treo, không nằm trong request:** hai khoá Tavily lộ trong lịch sử public vẫn chờ user tự
xoay vòng · bảng `## Cấu trúc` của README còn ghi `skills/ (6)` trong khi có 8 skill.
