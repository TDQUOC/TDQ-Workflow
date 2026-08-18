# QC — Luôn tổ chức modular, luôn ưu tiên sub-agent chạy song song
Ngày: 2026-08-18 · Plan: ../plan/2026-08-18-1744-uu-tien-subagent-song-song.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Khuôn spec có mục ranh giới module | `grep -c "2b. Ranh giới module" skills/tdq-spec/references/spec-template.md` | 1 | PASS |
| Q2 | Linter chặn spec lane full thiếu mục đó | `pytest tests/test_doc_lint.py -q` | 54 passed | PASS |
| Q3 | Khuôn plan bắt buộc khối cụm | `pytest tests/test_team_mode.py -q -k khai_vung_file` | 2 passed | PASS |
| Q4 | Trường `Cần:` đổi được thứ tự đợt | `pytest tests/test_team_mode.py -q -k phu_thuoc` | 8 passed | PASS |
| Q5 | Số đợt 4 plan thật giảm hoặc bằng | `pytest tests/test_uu_tien_song_song.py -q -k so_dot` | 3 passed, 8 subtests | PASS |
| Q6 | Phát liên tục | `pytest tests/test_team_mode.py -q -k lien_tuc` | 5 passed | PASS |
| Q7 | Ưu tiên đường găng | `pytest tests/test_team_mode.py -q -k duong_gang` | 5 passed | PASS |
| Q8 | Trần trên 4 | `pytest tests/test_team_mode.py -q -k tran` | 4 passed | PASS |
| Q9 | Cổng mode nêu lệnh và hệ số | `grep -c "he-so-agent 1.5" skills/tdq-plan/SKILL.md` | 2 | PASS |
| Q10 | Doctrine hết khoá theo mode | `grep -c "implement_mode = subagent" skills/tdq-build/references/team-mode.md` | 0 | PASS |
| Q11 | Bảng lý do giữ có 5 dòng | `pytest tests/test_uu_tien_song_song.py -q -k ly_do` | 3 passed, 5 subtests | PASS |
| Q12 | Prompt có ranh giới ba tầng | `pytest tests/test_uu_tien_song_song.py -q -k ranh_gioi` | 3 passed, 12 subtests | PASS |
| Q13 | Lane quick có agent con | `grep -c "agent con" skills/tdq-intake/references/quick-lane.md` | 4 | PASS |
| Q14 | Hook không chặn ngoài project dir | `pytest tests/test_edit_gate.py -q -k ngoai_project` | 4 passed (có ca `TDQ:TEAM`) | PASS |
| Q15 | Plan cũ thiếu `Cần:` vẫn chạy | `tdq_bench.py mo-phong --plan …codex-native-layers.md` | exit 0, "Thắng: đội (chênh 8.1 phút)" | PASS |
| Q16 | Portable khớp bản gốc | `build_portable.py` chạy hai lần, so `git status --short` | hai lần giống hệt (32 dòng, bản sinh ổn định) | PASS |
| Q17 | Lint file tài liệu đã sửa | `doc_lint.py <9 file>` | exit 0 | PASS |
| Q18 | Toàn bộ suite | `pytest -q` | 975 passed, 1240 subtests | PASS |
| Q19 | Kiểm độc lập | agent `tdq-qc-tester` chạy lại Q1–Q18 | vòng 1: FAIL, 12 defect · sau vòng fix QC1.1–QC1.10: hết defect mức chặn | PASS (sau fix) |
| QC-F1 | Full suite | `pytest -q` | 975 passed, 0 failed | PASS |
| QC-F2 | Hồi quy vùng chạm | test của mọi module trong dòng `Chạm:` | 231 + 66 passed | PASS |
| QC-F3 | Ràng buộc kiến trúc spec §5 | kiểm từng dòng, xem bằng chứng | 6/6 giữ nguyên | PASS |
| QC-F4 | Clean code 5 câu | checklist `clean-code.md` | 5/5 "có" | PASS |

## Bằng chứng

### Q5 — số đợt trước/sau trên 4 plan thật

Đo bằng chính `tdq_team`: cột "trước" = `_chia_dot_theo_phase` (luật cũ, phase làm proxy
phụ thuộc), cột "sau" = `chia_dot` (luật mới, đồ thị `Cần:`).

| Plan | Task | Task khai `Cần:` | Đợt trước | Đợt sau |
|---|---|---|---|---|
| 2026-08-17-1828-subagent-team-implement | 28 | 0 | 6 | 6 |
| 2026-08-17-2001-smoke-test-main-vs-doi | 20 | 0 | 13 | 13 |
| 2026-08-17-2121-toi-uu-context-workflow | 21 | 0 | 10 | 10 |
| 2026-08-18-1744-uu-tien-subagent-song-song | 39 | 18 | 18 | 10 |

Đọc thẳng, không tô hồng: **chỉ plan nào khai `Cần:` mới giảm đợt** (18 → 10, tức 44%).
Ba plan cũ không khai nên rơi về luật cũ và giữ nguyên số đợt — đúng thiết kế "không phá
plan cũ", nhưng cũng có nghĩa lợi ích chỉ đến khi khuôn plan mới được dùng thật.

### Q16 — cách kiểm thay thế (đã ghi vào plan, quy tắc 10)
Phép kiểm gốc ("git status không in dòng nào") chỉ đúng khi bản portable đã commit; trong
request này portable đang đổi theo nguồn. Kiểm tương đương: chạy build hai lần, `git status
--short portable_claude portable_codex` lần hai giống hệt lần một — bản sinh ổn định, không trôi.

### QC-F1 — một lần đỏ do nhiễu, đã dựng lại
Lượt chạy full suite ĐẦU tiên đỏ một test: `test_bench.py::ThucDoTest::
test_thuc_do_khong_de_lai_worktree_hay_thu_muc_tam`. Nguyên nhân: agent QC độc lập đang
chạy song song trong cùng repo và có dựng worktree tạm — test này soi worktree còn sót
trên toàn repo. Chạy lại riêng test đó: 2 passed; chạy lại full suite: 962 passed, 0 đỏ.
Ghi ra đây vì "chạy lại thì xanh" không được phép nói suông.

### QC-F2 — hồi quy theo vùng chạm
```
pytest tests/test_team_mode.py tests/test_doc_lint.py tests/test_edit_gate.py \
       tests/test_bench.py tests/test_uu_tien_song_song.py tests/test_luat_skill.py -q
→ 231 passed, 395 subtests passed
pytest tests/test_build_portable.py tests/test_checkportable.py -q  → 66 passed
```
Không có node nào trong vùng chạm thiếu test.

### QC-F3 — ràng buộc kiến trúc
- `hooks/` gọi `scripts/`, không có chiều ngược: `edit_gate.py` chỉ import `_common` và `tdq_state`.
- `skills/` chỉ nêu TÊN LỆNH: `tdq-plan/SKILL.md` gọi `tdq_bench.py mo-phong`; `quick-lane.md`
  chỉ nhắc tên hằng `TRAN_SONG_SONG`, không chép giá trị luật vào skill.
- Không tạo file mã nguồn mới: chỉ sửa 3 file có sẵn trong `scripts/` và `hooks/`; file mới
  duy nhất là `tests/test_uu_tien_song_song.py`.
- `portable_*` sinh bằng `build_portable.py`, không sửa tay.
- Không ghi `state.json` ngoài `tdq_state.py`.
- `tdq_bench.py` vẫn gọi `tdq_team.chia_dot` / `quyet_dinh_task` — chữ ký giữ nguyên, luật
  chia đợt vẫn một nguồn.

### QC-F4 — clean code
- SRP: có. `chia_dot` chỉ còn chọn đường; hai luật xếp đợt tách thành `_chia_dot_theo_phu_thuoc`
  và `_chia_dot_theo_phase`; phần chọn đợt sớm nhất tách thành `_dot_som_nhat`.
- OCP: có. Thêm nhóm lý do giữ task chỉ cần thêm một dòng vào `LY_DO_GIU`; thông báo và số
  nhóm đọc từ `len(LY_DO_GIU)`, không còn số 4 chép tay.
- LSP: có. Không có kế thừa mới; mọi nhánh `return` của `doc_phu_thuoc`/`b_level`/`chia_dot`
  trả cùng kiểu dict, `quyet_dinh_task` luôn trả cặp (quyết định, lý do).
- ISP: có. Mọi tham số đều dùng thật; `chia_dot` giữ tham số `quyet_dinh` vì `tdq_bench.py`
  đang gọi theo chữ ký đó.
- DIP: có. Cổng đề xuất mode gọi lại `tdq_bench.py mo-phong` thay vì viết lệnh thứ hai;
  `edit_gate` dùng lại hàm `within` và `observe` sẵn có thay vì tự so đường dẫn và tự log.

### Q19 — kiểm độc lập
Agent `tdq-qc-tester` chạy lại Q1–Q18 và soi ba điểm rủi ro (lịch trình trong
`tdq_team.py`, nhánh mới của `edit_gate.py`, mâu thuẫn luật giữa các skill). Kết quả vòng 1:
**FAIL, 12 defect**. Không nhận thẳng: tôi kiểm lại từng cái, 10 đúng → thành QC1.1–QC1.10
và đã vá hết (bảng ở mục dưới), 2 không thành task. Sau vòng fix, các lệnh của 12 defect
chạy lại đều xanh và full suite 975 passed.

## Vòng 1 fix — 10 mục, đã đóng hết

Agent `tdq-qc-tester` chạy độc lập trả FAIL với 12 defect. Tôi kiểm lại từng cái thay vì
nhận thẳng: 10 đúng và thành QC1.1–QC1.10 trong plan, 2 không thành task (một cái trùng
với mục đã có, một cái nằm ngoài phạm vi — xem đoạn dưới).

| Mục | Defect | Cách vá | Kiểm lại |
|---|---|---|---|
| QC1.1–QC1.4 | luật/test lệch nhau sau khi thêm `hop-dong` | sửa bảng luật và test khớp tập đóng | `pytest tests/test_team_mode.py -q` 106 passed |
| QC1.5 | hook còn chặn nhánh `TDQ:TEAM` với file NGOÀI project | dời `trong_project` lên trước khối team, dùng chung một biến | `pytest tests/test_edit_gate.py -q -k ngoai_project` 4 passed |
| QC1.6 | `doc_lint.py` không có log service dù spec §4 đòi | thêm `_log` 1 dòng ISO ra stderr, `TDQ_LOG=0` tắt | `pytest tests/test_doc_lint.py -q -k log` 4 passed |
| QC1.7 | test lấy "4 plan mới nhất" — bom nổ chậm | ghim danh sách theo tên, thiếu file là lỗi thật | `pytest tests/test_uu_tien_song_song.py -q -k so_dot` 3 passed |
| QC1.8 | lane quick còn khai 3 trạng thái tick và nêu tên hằng nội bộ | thêm `[>]`, trỏ trần về lệnh `cum` thay vì tên hằng | `doc_lint.py quick-lane.md` exit 0 · `grep -c TRAN_SONG_SONG` ra 0 |
| QC1.9 | spec §6 ghi sai lệnh kiểm Q3 và Q14 | sửa về `-k khai_vung_file` và `tests/test_edit_gate.py` | cả hai lệnh chạy ra xanh, không còn `no tests ran` |
| QC1.10 | file qc thiếu bảng số đợt trước/sau DoD Q5 đòi | thêm bảng ở mục Bằng chứng, kèm số của cả 3 plan không giảm | bảng ở trên |

Defect KHÔNG thành task, nói thẳng ra đây: 57 spec cũ bị thêm dòng
`<!-- doc-lint: allow R10 ... -->` khi bật rule R10 — nằm ngoài dòng `Chạm:` của mọi task.
Đó là hệ quả bắt buộc của việc thêm rule cho lane full mà không muốn 57 file cũ đỏ; nhưng
nó là thay đổi diện rộng không khai trước, nên ghi vào report chứ không giấu.

## Kết luận
Q1–Q19 và QC-F1→F4 PASS. Vòng fix: 1/3 (còn dư trần). Full suite 975 passed, 0 đỏ.
