# QC — Kiểm bộ workflow chạy được ở máy khác và trên Linux/Windows
Ngày: 2026-09-03 · Plan: ../plan/2026-09-03-1648-kiem-da-nen-tang-host.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

11 dòng DoD → Q1–Q11, cộng 4 hạng mục cố định QC-F1→F4.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | 4 phát hiện, mỗi khối 5 trường + nhãn | `pytest ... -k khoi_phat_hien` | 1 passed, 4 subtests | PASS |
| Q2 | Mọi `file:dòng` trỏ đúng file thật | `pytest ... -k vi_tri_that` | 1 passed, 9 subtests | PASS |
| Q3 | ≥6 mã `L#`, đủ 2 nhóm | `pytest ... -k du_lenh` | 8 mã, 2 nhóm | PASS |
| Q4 | Nhóm Windows không `bash`/`sh -c`/`wsl` | `pytest ... -k windows_thuan` | 4 subtests sạch | PASS |
| Q5 | Điểm mạnh ≥3 mục, số khớp `ast` | `pytest ... -k diem_manh -k khop` | 0/0/18 khớp | PASS |
| Q6 | Chưa chốt ≥3 mục, trỏ `L#` có thật | `pytest ... -k chua_chot` | C1→L4,L5 · C2→L7 · C3→L6 | PASS |
| Q7 | Không khẳng định "đã chạy được trên Linux/Windows" | `pytest ... -k khong_khang_dinh_qua_tay` | 2 file sạch | PASS |
| Q8 | Script đếm in đủ 5 khoá JSON | `python3 tools_kiem/dem_da_nen_tang.py --json` | 5 khoá, exit 0 | PASS |
| Q9 | `doc_lint` exit 0 trên 3 file `.md` | `python3 scripts/doc_lint.py <3 file>` | 0 violation | PASS |
| Q10 | Chỉ ghi trong vùng spec §2b | `git status --porcelain` | 0 file mã sản phẩm bị sửa | PASS |
| Q11 | Suite không vượt mốc đỏ 100 | `python3 -m pytest -q` | 100 failed / 1531 passed | PASS |
| QC-F1 | Toàn bộ test suite | `python3 -m pytest -q` | 100 failed / 1531 passed / 1466 subtests, 216 s | PASS |
| QC-F2 | Bộ test mới của request | `pytest tests/test_bao_cao_da_nen_tang.py -q` | 13 passed, 34 subtests | PASS |
| QC-F3 | Ràng buộc kiến trúc spec §5 | xem `## Bằng chứng` | 3/3 giữ nguyên | PASS |
| QC-F4 | Clean code — 5 câu tự kiểm | xem `## Bằng chứng` | 5/5 yes | PASS |

## Bằng chứng

**Q10 — vùng ghi.** `git status --porcelain` liệt kê: 3 file báo cáo, brief, spec, plan,
`tests/test_bao_cao_da_nen_tang.py`, `tools_kiem/` — đúng vùng "Đầu ra request" của spec §2b.
Ngoài ra có `docs/tdq/STATE.md`, `docs/tdq/timing.jsonl`, `docs/tdq/stop_streak.json`,
`docs/workinglog/2026-09-03.md`, `graphify-out/*` — tất cả do hook tự sinh, không do task nào
ghi. **Không một file nào trong `scripts/`, `hooks/` hay 3 bundle bị sửa** — đúng ràng buộc R1
(user chọn 4b: chỉ báo cáo).

**Q11 — mốc đỏ.** 100 đỏ, đúng bằng mốc nền HEAD sạch đã đo ở request trước, từ 4 ca có sẵn
(`test_bench.py`, `test_luat_skill.py`, `test_rules_library.py`, `test_skill_router.py`).
Request này không sinh ca đỏ mới. Số passed tăng 1518 → 1531 vì 13 ca mới đều xanh.

**QC-F3 — ràng buộc kiến trúc spec §5.**
- R1 (không sửa mã sản phẩm): giữ — xem Q10.
- R2 (Windows là PowerShell thuần): giữ — 4 từ cấm `bash`/`sh -c`/`wsl`/`/dev/null` không xuất
  hiện trong nhóm Windows, có test canh.
- R3 (không có máy thật): giữ — có test cấm câu "đã chạy được trên Linux/Windows", và mỗi phát
  hiện mang nhãn lớp bằng chứng để người đọc biết nó đứng ở mức nào.

**QC-F4 — 5 câu tự kiểm.**
1. Hàm nào >60 dòng? Không — dài nhất là `dem_ma_nguon` (37 dòng).
2. Logic lặp copy-paste? Không — `_ten_ham`/`_co_tham_so`/`_gia_tri_that` tách riêng, dùng chung.
3. Tên biến mơ hồ? Không — theo lối đặt tên tiếng Việt đang có của repo.
4. Magic number? Không — ngưỡng (≥4 phát hiện, ≥6 lệnh, ≥3 mục) đều lấy thẳng từ DoD của spec.
5. Nhánh nào không test? Không — cả 5 khoá của script đếm đều có ca đối chiếu.

**Điều phải nói thẳng.** Lộ trình trong brief ghi có phase `diagram`, nhưng repo này KHÔNG có
phase đó trong `PHASE_TABLE` của `tdq_state.py` và cũng không có skill `tdq-diagram`;
`set phase=diagram` bị từ chối. Tôi đi thẳng `spec → plan` và đã báo user ngay lúc đó. Đây là
chỗ luật trong `skills/tdq-spec/SKILL.md` mô tả một phase không tồn tại trong máy — một khác
biệt luật↔code, nằm ngoài phạm vi request này.
