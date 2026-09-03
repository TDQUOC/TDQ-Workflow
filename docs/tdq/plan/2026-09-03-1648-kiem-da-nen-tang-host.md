# PLAN — Kiểm bộ workflow chạy được ở máy khác và trên Linux/Windows
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐÃ DUYỆT · Spec: ../spec/2026-09-03-1648-kiem-da-nen-tang-host.md · Lane: full

Mode thực thi: main — `tdq_bench.py simulate` ra `Winner: đội (gap 11.2 phút)`, nhưng con số đó
dựng trên giả định các task chạy song song được. Ở plan này giả định đó SAI: T2.1/T2.2/T2.3 cùng
ghi một file báo cáo, T1.1/T1.2 cùng ghi một script — đúng định nghĩa file nóng, mà luật file
nóng cấm hai worktree cùng lưu một file. Chia đội ở đây chỉ đổi 11 phút lý thuyết lấy conflict
thật. Chuỗi phụ thuộc cũng gần như thẳng: đo trước → viết phát hiện → viết lệnh kiểm → test
đóng số. Vì vậy đề xuất `main`.

## Phase 1 — Đo lại bằng máy, không tin trí nhớ

- [x] **T1.1** (e12m) Viết script đếm bằng `ast`: số `subprocess` có `text=True` thiếu
  `encoding=`, số `open()` chế độ text thiếu `encoding=`, số import stdlib chỉ có trên POSIX
  (`fcntl`, `pwd`, `termios`, `grp`), số lời gọi `os.chmod`. Quét `scripts/` + `hooks/`.
  In ra JSON để test đọc lại được. — Test: `python3 tools_kiem/dem_da_nen_tang.py --json` in đủ
  4 khoá, mã thoát 0
  Chạm: `tools_kiem/dem_da_nen_tang.py`

- [x] **T1.2** (e10m) Đếm số hook gọi thẳng tên lệnh `python3` trong cả 3 nguồn:
  `hooks/hooks.json`, `portable_codex/.codex/hooks.json`, `antigravity_portable/hooks.json`.
  Thêm khoá vào JSON của T1.1. — Test: JSON có khoá `hook_goi_python3` với 3 nguồn, mỗi nguồn
  một số nguyên
  Chạm: `tools_kiem/dem_da_nen_tang.py`

- [x] **T1.3** (e10m) Giả lập trên macOS: chạy một hook với PATH đã bỏ `python3` và bắt đúng
  triệu chứng; chạy lại với `PYTHONIOENCODING=cp1252` trên chuỗi tiếng Việt. Ghi output thật
  vào file bằng chứng. — Test: `docs/tdq/report/2026-09-03-1648-kiem-da-nen-tang-host-bang-chung.md`
  chứa output nguyên văn của cả 2 lần giả lập
  Chạm: `docs/tdq/report/2026-09-03-1648-kiem-da-nen-tang-host-bang-chung.md`

## Phase 2 — Viết báo cáo tương thích (Đ1, Đ3, Đ4)

- [x] **T2.1** (e20m) Viết 4 khối phát hiện P1–P4, mỗi khối đủ 5 trường (triệu chứng · vị trí
  `file:dòng` · hệ điều hành dính · mức nguy · cách sửa đề xuất) và một nhãn lớp bằng chứng
  (`đọc mã` / `giả lập` / `tài liệu`). — Test: script kiểm đếm được 4 khối, mỗi khối đủ 5 trường
  và có nhãn
  Chạm: `docs/tdq/report/2026-09-03-1648-kiem-da-nen-tang-host-tuong-thich.md`

- [x] **T2.2** (e8m) Viết mục "điểm mạnh": ≥3 mục, mỗi mục kèm con số lấy thẳng từ JSON của
  T1.1 và lệnh tái lập nó. — Test: mọi con số trong mục điểm mạnh khớp JSON, kiểm bằng script
  Chạm: `docs/tdq/report/2026-09-03-1648-kiem-da-nen-tang-host-tuong-thich.md`

- [x] **T2.3** (e10m) Viết mục "chưa chốt được": console encoding trên Windows, đường dẫn plugin
  agy, hook Codex Windows native. Mỗi mục nêu rõ vì sao chưa chốt và trỏ tới một lệnh của Đ2.
  — Test: ≥3 mục, mỗi mục chứa ít nhất một mã lệnh `L#` có thật trong file lệnh kiểm
  Chạm: `docs/tdq/report/2026-09-03-1648-kiem-da-nen-tang-host-tuong-thich.md`

## Phase 3 — Danh sách lệnh user tự chạy (Đ2)

- [x] **T3.1** (e15m) Viết ≥6 lệnh, chia 2 nhóm Linux / Windows, mỗi lệnh mang mã `L#` và 2
  dòng "đạt là thấy gì / hỏng là thấy gì". Nhóm Windows viết bằng PowerShell thuần.
  — Test: script kiểm đếm ≥6 mã `L#`, đủ 2 nhóm, mỗi lệnh đủ 2 dòng kết quả
  Chạm: `docs/tdq/report/2026-09-03-1648-kiem-da-nen-tang-host-lenh-kiem.md`

- [x] **T3.2** (e6m) Rà nhóm Windows không nhắc `bash`, `sh -c`, `wsl`, `/dev/null`, và cả hai
  file báo cáo không chỗ nào khẳng định "đã chạy được trên Linux/Windows".
  — Test: `grep -nE "bash|sh -c|wsl" <nhóm Windows>` không ra dòng nào
  Chạm: `docs/tdq/report/2026-09-03-1648-kiem-da-nen-tang-host-lenh-kiem.md`

## Khối hợp đồng skill

- Dùng: Rà tài liệu sinh ra
- Để: rà 3 file `.md` request này sinh ra bằng `scripts/doc_lint.py`, đúng khuôn tài liệu TDQ.
- Ra: exit 0, 0 violation.
- Kiểm: `python3 scripts/doc_lint.py <3 file>` mã thoát 0.
- Không dùng cho: kiểm nội dung kỹ thuật của báo cáo — việc đó là của bộ test T4.1.

- Dùng: Quét mã theo cú pháp
- Để: đếm chính xác các mẫu mã nguồn bằng `ast` (thiếu `encoding=`, import POSIX, `os.chmod`), làm số liệu gốc cho báo cáo.
- Ra: một JSON 5 khoá, tái lập được bằng một lệnh.
- Kiểm: `python3 tools_kiem/dem_da_nen_tang.py --json` in đủ 5 khoá.
- Không dùng cho: đếm nội dung file JSON/Markdown — chỗ đó đọc thẳng, không parse bằng `ast`.

- Dùng: Tra tài liệu host
- Để: xác nhận hành vi thật của Codex CLI và agy trên Windows bằng WebSearch, mỗi khẳng định kèm link nguồn.
- Ra: mỗi câu nói về host trong báo cáo có đúng một link.
- Kiểm: bộ test T4.1 kiểm mọi đoạn mang nhãn `tài liệu` đều chứa `http`.
- Không dùng cho: kết luận về mã trong repo này — chỗ đó chỉ đọc mã mới tính.

- Dùng: Kiểm bundle khớp manifest
- Để: chạy `scripts/tdq_checkportable.py` trên 3 bundle để lấy triệu chứng thật của P2.
- Ra: output nguyên văn dán vào file bằng chứng.
- Kiểm: file bằng chứng chứa dòng NOTE của lệnh này.
- Không dùng cho: sửa bundle — request này chỉ đọc.

- Dùng: Dựng lại bundle
- Để: chạy `scripts/build_portable.py` để quan sát `command` sinh ra, chứng minh P1 và P3.
- Ra: 3 bundle CLEAN, `hooks.json` dán vào file bằng chứng.
- Kiểm: `tdq_checkportable.py check` CLEAN cả 3 bundle.
- Không dùng cho: đổi cách sinh `command` — đó là việc của request sau.

## Phase 4 — Đóng số và dịch vụ log

- [x] **T4.1** (e18m) Viết bộ test giữ báo cáo khỏi mục: đếm lại bằng `ast` và so với con số đã
  ghi trong báo cáo; kiểm 4 khối phát hiện đủ trường và có nhãn; kiểm mọi `file:dòng` trong báo
  cáo trỏ đúng file có thật và số dòng nằm trong file; kiểm ≥6 mã `L#` đủ 2 nhóm; kiểm không có
  câu khẳng định đã chạy máy thật. — Test: `python3 -m pytest tests/test_bao_cao_da_nen_tang.py -q` xanh
  Chạm: `tests/test_bao_cao_da_nen_tang.py`

- [x] **T4.2** (e5m) Đóng sổ turn bằng dịch vụ log: `tdq_finish.py --files <2 báo cáo> --log
  "<đã làm gì, file nào, kết quả test>" --phase qc`. — Test: lệnh in `✓ tdq_finish` với
  `lint=ok · worklog=ok`
  Chạm: `docs/workinglog/2026-09-03.md`

## Cụm song song

Cụm A (T1.1, T1.2) → Cụm B (T1.3) → Cụm C (T2.1, T2.2, T2.3) → Cụm D (T3.1, T3.2) → Cụm E
(T4.1) → T4.2. Cụm C và D cùng đụng file báo cáo của mình nên chạy tuần tự trong mode `main`.

## Definition of Done

Bám §6 của spec, 11 dòng, mỗi dòng một lệnh kiểm:

- [x] Báo cáo có đủ 4 phát hiện P1–P4, mỗi khối 5 trường + nhãn lớp bằng chứng — `pytest tests/test_bao_cao_da_nen_tang.py -k khoi_phat_hien`
- [x] Mọi `file:dòng` trong báo cáo trỏ đúng file thật, dòng nằm trong file — `pytest ... -k vi_tri_that`
- [x] Danh sách lệnh có ≥6 mã `L#`, chia đúng 2 nhóm — `pytest ... -k du_lenh`
- [x] Nhóm Windows không nhắc `bash`/`sh -c`/`wsl` — `pytest ... -k windows_thuan`
- [x] Mục điểm mạnh có ≥3 mục, số khớp kết quả đếm bằng `ast` — `pytest ... -k diem_manh`
- [x] Mục chưa chốt có ≥3 mục, mỗi mục trỏ tới một mã `L#` có thật — `pytest ... -k chua_chot`
- [x] Không chỗ nào khẳng định "đã chạy được trên Linux/Windows" — `pytest ... -k khong_khang_dinh_qua_tay`
- [x] Script đếm chạy được và in đủ 5 khoá JSON — `python3 tools_kiem/dem_da_nen_tang.py --json`
- [x] `doc_lint.py` exit 0 trên cả 3 file `.md` sinh ra — `python3 scripts/doc_lint.py <3 file>`
- [x] `git diff --name-only` chỉ liệt kê file trong vùng ghi của spec §2b — `git diff --name-only`
- [x] Toàn bộ suite không vượt mốc đỏ 100 — `python3 -m pytest -q`
