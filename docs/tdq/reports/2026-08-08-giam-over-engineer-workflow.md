# REPORT — Giảm over-engineer & over-test cho TDQ workflow

Ngày: 2026-08-08 · Lane full · Mode main · Spec: ../spec/2026-08-08-giam-over-engineer-workflow.md

## Đã làm

Tám phase, 30 task, cộng vòng fix 1 (5 task) — tất cả tick `[x]`.

- **Bỏ hẳn nhánh external và deep search**: xoá 20 file (`external_task.py`,
  `external_models.py`, `search_task.py`, 2 schema, 2 sample e2e, 4 agent runner,
  3 reference, 5 test). `VALID_MODES` còn `main|subagent`.
- **Xoá `portable/`** (18 file) và `tests/test_portable_sync.py`; bản mẫu CLAUDE.md
  chuyển thành `docs/claude-md-mau.md`.
- **QC bám DoD**: số hạng mục QC bằng số dòng Definition of Done, mỗi dòng một phép kiểm
  chạy được bằng lệnh, cộng đúng 1 hạng mục chạy full-suite. Vòng fix chỉ chạy lại hạng
  mục đã FAIL cộng hạng mục bản fix có thể làm hỏng, trần 3 vòng.
- **Tầng `nhỏ`** trước quick/full: đủ 4 điều kiện thì trả lời hoặc sửa luôn, không mở
  request; kèm luật thoát bắt buộc khi giữa chừng vỡ điều kiện.
- **Gộp brief**: `requests/` + `knowledge/` + `questions/` thành một file
  `docs/tdq/brief/<slug>.md` ba mục.
- **Gọn skill**: `tdq-conventions/SKILL.md` 7.345 → 5.912 byte, phần carry-cost tách ra
  `references/context-budget.md`.
- **Cắt test**: xoá `test_skill_docs.py`, `test_agent_digest_sync.py`, viết lại
  `test_docs_consistency.py`, bỏ 3 test trùng trong `test_context_hooks.py`.

## Số đo trước/sau

| Số đo | Trước (`704ac3f`) | Sau |
|---|---|---|
| Byte 13 file skill lõi của một vòng full | 51.070 | 48.278 |
| Byte toàn bộ `skills/` | 102.166 | 81.467 |
| File output mỗi request | 7 | 5 |
| Suite: số test / giây / test đỏ | 600 / 80,0 s / 1 | 410 / 58,2 s / 0 |

Hai số giây đo liền nhau trên cùng máy. `tdq-conventions/SKILL.md` — file nạp ở MỌI
phase — giảm 19,5%.

## Kết quả QC

Vòng 1 tự chạy: Q1-Q10 PASS. Agent `tdq-qc-tester` chạy độc lập: **FAIL**, 9/10, và nó
đúng — tìm ra 5 khiếm khuyết thật, tất cả đã sửa trong vòng fix 1 (dưới trần 3 vòng):

1. Lệnh DoD `python3 -m unittest discover -q` chạy ở gốc repo trả `NO TESTS RAN`, exit 5
   — sai ở 4 chỗ trong spec và 9 chỗ trong plan, đã đổi thành `discover -s tests -t tests -q`.
2. D2 làm thiếu: luật "vòng fix bắt buộc kể cả khi user tắt QC" vẫn còn ở 4 chỗ.
3. Mâu thuẫn trần vòng fix giữa `quick-lane.md` và `qc.md`.
4. `agents/tdq-reviewer.md` còn khuôn `knowledge/requests`.
5. Số đo suite cũ ghi sai (618/55 s), đo lại là 600 test và có 1 test đỏ.

Sau fix: 410 test OK, bản `HOME=/nonexistent` cũng OK, `doc_lint skills` exit 0.

## Lệch plan, phải khai báo

- **Kéo T7.1 lên sớm**: P6 cắt §10 của conventions làm 5 test wording trong
  `test_skill_docs.py` đỏ, mà P7 vốn xoá chính file đó.
- **T7.1 không xoá cả `test_docs_consistency.py`** như plan viết: giữ lại 3 phép kiểm
  toàn vẹn repo thật (marketplace khớp plugin, CHANGELOG có version hiện tại, không có
  `.DS_Store`) và bỏ phần assert văn xuôi.
- **T7.3 chỉ cắt 3 test trùng** đã đối chiếu tay, không cắt thêm cho đủ số — cắt theo
  chỉ tiêu là đúng thứ request này muốn bỏ.
- **Commit `de76221`** đã tự chạy khi build (được phép theo luật gỡ chặn kỹ thuật): xoá
  external + portable. Không push. Ngoài commit đó chưa commit gì thêm.

## Sự cố trong lúc làm

Lúc 22:59 một lệnh test hook của tôi chạy `tdq_state.py init 2026-08-08-hook-check full`
mà **thiếu `TDQ_PROJECT_DIR`**, nên ghi đè state thật: `active_request` đổi, `phase` về
`idle`, mất dấu duyệt spec/plan. Doc, code, test, commit không bị ảnh hưởng. Đã báo user
và chỉ khôi phục sau khi user chọn phương án A, ghi lại đúng nguyên văn hai câu duyệt cũ.

## Còn treo

- Doc cũ trong `docs/tdq/requests|knowledge|questions/` **không** được chuyển sang
  `brief/`; luật mới chỉ áp cho request mở từ đây về sau.
- `grep -ril external` vẫn khớp `tests/test_state.py` — cố ý, test đó khoá luật "mode
  external bị từ chối".
- `~/.claude/CLAUDE.md` của user vẫn nhắc mode `external` và deep search. Tôi không sửa
  file cấu hình cá nhân của user; cần user quyết có bỏ hai mục đó không.
