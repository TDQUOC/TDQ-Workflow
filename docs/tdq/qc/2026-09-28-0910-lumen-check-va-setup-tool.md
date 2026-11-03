# QC — Bộ tìm kiếm 4 tầng: kiểm bằng hiệu ứng, reindex mỗi turn, và skill `tdq-setup`

Ngày: 2026-09-28 · Spec: ../spec/2026-09-28-0910-lumen-check-va-setup-tool.md ·
Plan: ../plan/2026-09-28-0910-lumen-check-va-setup-tool.md · Mức QC: `full`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Mức `full` chạy: DoD + trọn unit test + hồi quy vùng chạm + ràng buộc kiến trúc + clean code.
KHÔNG chạy smoke test và runtime test ở phase này, KHÔNG gọi agent QC độc lập — đó là mức `ultra`.
Lưu ý để không hiểu lầm: đường smoke test của `tdq_setup.py` là **sản phẩm** của request, và nó đã
được chạy thật một lần trong phase implement; ở đây nó được kiểm bằng unit test, đúng mức `full`.

## 20 hạng mục Definition of Done

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Bậc 5 không phụ thuộc PATH | **PASS** | `unittest ... -k path` → `Ran 2 tests OK`; đo thật trên macOS: `shutil.which("ollama")=None`, socket `True`, bậc 5 không in lệnh cài ollama (`"brew install ollama" in lenh_cai` → `False`) |
| Q2 | Bậc 5 bắt được lumen không trả lời | **PASS** | `-k vong` → `Ran 3 tests OK`; ca lumen trả rỗng cho ra không ĐẠT kèm chữ "vòng đi-về" |
| Q3 | Bậc 5 bắt được index thiếu nội dung mới | **PASS** | `-k noidung` → `Ran 4 tests OK`; đo thật: `bậc 5 → CẢNH BÁO (index chưa có nội dung mới nhất — code mới hơn lần dựng index gần nhất 3 phút)` |
| Q4 | Bậc graphify | **PASS** | `-k graphify` → `Ran 6 tests OK`; đo thật: `CẢNH BÁO (đồ thị cũ hơn mã nguồn 56 phút)` rồi `ĐẠT (đồ thị mới hơn mọi file mã nguồn)` sau khi dựng lại |
| Q5 | Reindex vào kết turn | **PASS** | `test_finish_reindex -k ok` → `Ran 4 tests OK`; chạy thật: `reindex ok (Done. Indexed 13 files, 326 chunks in 4.881s.)` |
| Q6 | Reindex không treo turn | **PASS** | `-k tran` → `Ran 2 tests OK`; quá trần → `fail` + ghi nợ, lệnh vẫn thoát |
| Q7 | Cờ bỏ graphify đã biến mất | **PASS** | `tdq_finish.py --skip-graphify --dry-run` → `exit=2`, `error: unrecognized arguments: --skip-graphify` |
| Q8 | Đổi tên trọn vẹn | **PASS** | `grep -rn "tdq-lsp-setup" scripts skills tests README.md` → **0 dòng** |
| Q9 | `setup` cài, kiểm và smoke test | **PASS** | `-k smoke` → `Ran 5 tests OK`; chạy thật một lệnh in bảng 4 tầng: grep ĐẠT · LSP ĐẠT · graphify ĐẠT · lumen ĐẠT |
| Q10 | File nợ | **PASS** | `-k no` → `Ran 7 tests OK`; chạy hai lần: lần hai `Nợ: 1 món (0 dòng mới)` — không nhân bản |
| Q11 | `setup` vá được hook plugin | **PASS** | `-k hook` → `Ran 4 tests OK` trên fixture thư mục tạm; đã vá thật hook `PreToolUse` của plugin lumen, giữ `SessionStart`, có `hooks.json.truoc-tdq.bak` |
| Q12 | Luật 4 tầng | **PASS** | `test_luat_4_tang` → `Ran 6 tests OK`: có graphify là một tầng, có bảng phụ thuộc runtime, số đo ghi kèm tên repo, câu "no separate reindex step" đã bị xoá |
| Q13 | Năm chỗ trích luật không lệch | **PASS** | `test_tdq_setup_skill` → `Ran 9 tests OK` |
| Q14 | Khối ghim user-level | **PASS** | `test_claude_md_core -k khoi` → `Ran 6 tests OK`; ghi hai lần vẫn một khối, phần user không đổi |
| Q15 | Trần byte bản mẫu | **PASS** | `-k byte` → `Ran 1 test OK`; trần 3800 → **4300** kèm chú giải lý do và ngày |
| Q16 | Đồ thị graphify | **PASS** | đếm trên `graph.json`: **0/1726 node** trỏ vào file không còn tồn tại |
| Q17 | Ba hệ | **PASS** | Windows `Ran 2077 OK` · Linux 3.14.4 `Ran 2054 OK` · macOS pyenv 3.13.15 `Ran 2054 OK` · macOS brew 3.14.7 `Ran 2054 OK`; ca PATH chạy THẬT trên macOS |
| Q18 | Không làm rối môi trường hai máy | **PASS** | thư mục tạm đã xoá sạch trên cả hai; không cài gói nào; không sửa cấu hình nào; mọi lần gọi python trên macOS đều bằng đường dẫn tuyệt đối tới pyenv/brew, **không chạm python của Apple** |
| Q19 | Ràng buộc kiến trúc | **PASS** | `grep -rn "import hooks" scripts` → 0; file code mới nằm trong `scripts/`; skill không chứa dòng mã nào |
| Q20 | Nợ đã khai | **PASS** | `docs/tdq/no-phu-thuoc.md` có dòng `mem0-memory`; §9 bản mẫu KHÔNG bị sửa lặng lẽ |

## Bốn hạng mục cố định

**QC-F1 — trọn bộ test.** `python -m unittest discover -s tests -q` →
`Ran 2077 tests in 338.594s` · `OK (skipped=9)`. Không fail, không error.

**QC-F2 — hồi quy vùng chạm.** Chạy riêng từng module trên các dòng `Chạm:` của plan:

| Module test | Kết quả |
|---|---|
| `test_tdq_lsp` · `test_bac_lumen_hieu_ung` · `test_setup_status` · `test_team_chong_conflict` | 49 · 15 · 45 · 25 ca, OK |
| `test_finish_reindex` · `test_timing` · `test_tdq_eval` | 7 · 30 · 109 ca, OK |
| `test_tdq_setup` · `test_tdq_setup_skill` · `test_luat_4_tang` | 26 · 9 · 6 ca, OK |
| `test_claude_md_core` · `test_doc_lint` · `test_token_budget` · `test_tuong_thich_host` · `test_docs_consistency` | 11 · 65 · 8 · 5 · 8 ca, OK |

Không node nào thiếu test. `scripts/tdq_no.py` là file mới và được phủ từ hai phía —
`test_tdq_setup` (lớp `GhiNo`) và `test_finish_reindex` (ca ghi nợ khi quá trần).

**QC-F3 — ràng buộc kiến trúc.** Bốn dòng khai ở spec §5:

| Ràng buộc | Kết quả |
|---|---|
| `skills/` chỉ nhắc tên lệnh, cấm chép nội dung script | PASS — `skills/tdq-setup/SKILL.md` không có dòng mã nào |
| File code MỚI phải nằm trong `scripts/` hoặc `hooks/` | PASS — `scripts/tdq_setup.py`, `scripts/tdq_no.py` |
| `scripts/` không được import `hooks/` | PASS — `grep -rn "import hooks" scripts` → 0 |
| Chỉ `tdq_state.py` ghi `state.json` | PASS — file nợ là file riêng, không phải state |

**Một lệch tôi tự khai, không nằm trong bốn dòng trên.** Quyết định ngôn ngữ 3 tầng (2026-08-22)
nói chú thích/docstring của `scripts/` và chuỗi máy in ra phải viết TIẾNG ANH. `i18n_check.py` đếm
**122 dòng tiếng Việt** trong hai file mới của tôi. Tôi không sửa trong request này vì hai lý do
đo được: không test nào gác i18n trên `scripts/` (bộ test chỉ kiểm chính công cụ đo), và repo đang
lẫn sẵn — `tdq_lsp.py` 161 dòng, `tdq_state.py` 42 dòng. Dọn lẻ một file sẽ làm vùng đó lệch hơn
với hàng xóm của nó. Đã ghi thành nợ trong `docs/tdq/no-phu-thuoc.md`.

**QC-F4 — clean code, 5 câu.**

| Câu | Trả lời | Ghi chú |
|---|---|---|
| SRP — mỗi hàm một lý do để đổi? | **CÓ**, sau khi sửa | Ban đầu KHÔNG: `_do_moi_index` vừa đo vừa dựng lại index. Đã tách: `_index_cu_hon_code` chỉ đọc, `step_reindex` là nơi duy nhất ghi |
| OCP — thêm một ca bằng một dòng dữ liệu? | **CÓ** | Thêm một bậc = thêm một hàm `bacN_*` và một mục trong `chay_kiem`; thêm một lệnh cài được phép = thêm một tiền tố vào `TIEN_TO_CAI_DUOC` |
| LSP — mọi nhánh `return` cùng kiểu, cùng hợp đồng lỗi? | **CÓ**, sau khi sửa | Ban đầu KHÔNG: `_do_moi_index` trả bộ ba chuỗi trong khi hàm anh em cạnh nó trả `(bool, str)`. Nay cả hai cùng `(bool, str)` |
| ISP — mọi tham số truyền vào đều được dùng? | **CÓ**, sau khi sửa | Ban đầu KHÔNG: `smoke_lsp`/`smoke_graphify` nhận `project` rồi bỏ quên; `bac5_lumen` bỏ qua `project` của thang bậc và tự suy ra thư mục khác. Đã vá cả hai |
| DIP — đi qua cửa chung sẵn có thay vì tự dựng lại? | **CÓ**, sau khi sửa | Ban đầu KHÔNG: ba bản wrapper `subprocess`, hai bộ log, hai bản `_binary_lumen`, `ghi_no` trú nhờ trong script cài đặt. Nay một `tdq_lsp._run(cmd, cwd=)`, một biến `TDQ_LOG`, một `_binary_lumen` có cache, và `scripts/tdq_no.py` là hạ tầng chung |

## Vòng soát trước khi kết luận

Không có vòng fix QC nào, vì hai vòng soát đã chạy TRONG phase implement (task T8.1, T8.2) và mọi
phát hiện được vá ngay tại đó:

- `code-review` mức `high`: **8 phát hiện**, vá cả 8. Nặng nhất: `step_reindex` thiếu cổng ollama
  nên mỗi lượt vừa dùng lumen sẽ `fail` và đẻ một dòng nợ; danh sách cho phép cài chỉ soi tiền tố
  đầu chuỗi trong khi bậc 3 nối lệnh bằng ` ; ` và `_chay_lenh` chạy qua shell.
- Bốn agent `simplify` song song (reuse · simplification · efficiency · altitude): **21 phát hiện**,
  vá 14, gộp 5 trùng nhau, bỏ 2 (xem dưới). Nặng nhất là thứ cả bốn cùng chỉ ra: bậc 5 GHI trong
  lúc chẩn đoán, khiến index bị dựng **hai lần mỗi lượt** và một hàm-chỉ-để-đọc lại đi sửa máy
  user. Sau khi vá, thang 8 bậc chạy **1,47 s** thay vì 2–10 s.

Hai phát hiện bị bỏ, có lý do:

| Phát hiện | Vì sao bỏ |
|---|---|
| "Xử hook xung đột ở tầng `settings.json` thay vì sửa file plugin" | Research đã chứng minh Claude Code KHÔNG có cách tắt một hook riêng lẻ; công tắc duy nhất là `disableAllHooks`, thứ sẽ tắt luôn hook của chính workflow này. Phương án thay thế tệ hơn phương án đang có |
| "Nâng `lenh_cai` thành argv có cấu trúc ngay trong `Bac`" | Đúng hướng nhưng lan ra mọi bậc của thang, ngoài phạm vi spec. Đã đóng phần nguy hiểm bằng cách rẻ hơn: `shell=False` + `shlex`, và từ chối thẳng mọi chuỗi có ký tự shell |

## Kết luận

20/20 DoD PASS · QC-F1→F4 PASS · không vòng fix nào · hai món nợ đã khai bằng văn bản.
