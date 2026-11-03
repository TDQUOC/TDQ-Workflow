# QC — giảm over-engineer workflow TDQ

Ngày: 2026-08-08 · Plan: ../plan/2026-08-08-giam-over-engineer-workflow.md · Vòng: 1

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Tầng `nhỏ` dùng được | đọc `skills/tdq-intake/SKILL.md` + phân loại lại 5 request cũ | 4 điều kiện + luật thoát có mặt; 2/5 request cũ tụt xuống tầng `nhỏ` | PASS |
| Q2 | QC bám DoD | `grep -rn "3 hạng mục" skills/` | không có dòng nào | PASS |
| Q3 | External sạch | `grep -ril external skills hooks agents scripts tests` | chỉ còn `tests/test_state.py` (test chứng minh mode external bị TỪ CHỐI) | PASS |
| Q4 | `portable/` đã xoá | `ls portable` · `ls -l docs/claude-md-mau.md` | `No such file or directory` · 3463 byte | PASS |
| Q5 | Gộp brief chạy được | `TDQ_PROJECT_DIR=<tmp> tdq_state.py init … && … next` | checklist phase `analyze` in ra `docs/tdq/brief/<slug>.md` cả 3 chỗ | PASS |
| Q6 | `doc_lint` đúng phạm vi | `doc_lint.py <tmp>/docs/tdq/brief/2026-08-08-test-brief.md` và `doc_lint.py docs/tdq/requests/<slug>.md` | exit 0 cả hai | PASS |
| Q7 | Cửa thoát `allow R5` | `python3 -m unittest discover -s tests -t tests -p test_doc_lint.py` | 33 test OK | PASS |
| Q8 | Suite xanh và hermetic | `python3 -m unittest discover -s tests -t tests -q` và bản `HOME=/nonexistent` | 410 test OK / 410 test OK | PASS |
| Q9 | 6 rào an toàn còn nguyên | chạy 5 hook với state giả trong thư mục tạm | 4 hook nhắc (`permissionDecision: allow`), `stop_gate` chặn khi thiếu working log | PASS |
| Q10 | Số đo trước/sau | `wc -c`, `git cat-file -s`, `time … unittest` | 4 cặp số ở mục Số đo | PASS |

## Bằng chứng

### Q1 — phân loại lại 5 request cũ theo tầng mới

| Request | Đã chạy | Theo luật mới | Vì sao |
|---|---|---|---|
| 2026-08-07-siet-qc-lane-quick | full | full | đổi luật QC ở nhiều file skill + hook + test, phải interview |
| 2026-08-05-toi-uu-token-vong-2 | full | full | phân tích rộng rồi mới spec/plan |
| 2026-08-05-format-cau-hoi-interview | quick | quick | sửa khuôn câu hỏi ở nhiều file skill, không cần interview |
| 2026-08-05-validate-export | quick | **nhỏ** | chỉ chạy lại `claude_export.py check` + `unzip -t`, không sửa file mã nguồn, xong 1 turn |
| 2026-08-05-rebuild-sync-export | quick | **nhỏ** | chỉ chạy lại lệnh build cho đồng bộ bundle, không sửa code |

2/5 request cũ lẽ ra không phải mở request: mỗi cái tiết kiệm 1 file plan + 1 gate duyệt.

### Q3 — chỗ còn chữ "external"

```
tests/test_state.py
```

Cố ý: `test_mode_external_bi_tu_choi` khoá luật "mode external bị từ chối, không âm thầm nhận".

### Q8 — suite

```
Ran 410 tests in 29.969s
OK
Ran 410 tests in 32.329s   # HOME=/nonexistent
OK
```

### Q9 — 5 hook với state giả (`TDQ_PROJECT_DIR` tạm, phase=implement, spec chưa duyệt)

```
session_start   → [TDQ] Luật … + [TDQ:NEXT] … phase implement
prompt_context  → [TDQ:NEXT] …
edit_gate       → permissionDecision "allow" + [TDQ:APPROVE] sửa file ngoài docs/ khi spec chưa duyệt
bash_gate       → permissionDecision "allow" + [TDQ:GIT] tên branch phạm quy ước
stop_gate       → {"decision": "block", "reason": "[TDQ:LOG] Turn này đổi repo (src/a.py) …"}
```

## Số đo (Q10) — trước/sau

| Số đo | Trước | Sau | Cách đo |
|---|---|---|---|
| Byte skill 13 file lõi của một vòng full | 51.070 | 48.278 | `wc -c` trên cùng danh sách file, bản trước lấy bằng `git cat-file -s` tại `704ac3f` |
| Byte toàn bộ `skills/` | 102.166 | 81.467 | tổng `git cat-file -s` tại `704ac3f` so với `wc -c` cây hiện tại |
| File output mỗi request | 7 (requests, questions, knowledge, research, spec, plan, qc/report) | 5 (brief, spec, plan, qc, report; research khi cần) | đếm file `docs/tdq/*/<slug>.md` |
| Số test / giây chạy suite | 600 / 80,0 giây, 1 đỏ | 410 / 58,2 giây, 0 đỏ | `python3 -m unittest discover -s tests -t tests -q`, đo LIỀN NHAU lúc 00:2x |

`tdq-conventions/SKILL.md` — file nạp ở MỌI phase — giảm 7.345 → 5.912 byte (−19,5%).

Ghi chú giây: máy tải khác nhau thì số giây khác nhau — lượt đo lúc 22:5x cho 49,8 giây so với 30,0 giây. Cặp số trong bảng đo liền nhau nên so được với nhau.

Ghi chú: số 48.091 byte ghi ở phase analyze không tái lập được bằng lệnh đã lưu, nên
bảng này đo lại cả hai đầu bằng CÙNG một cách; cột "trước" lấy tại commit `704ac3f`.

## Kết luận

PASS toàn bộ 10 hạng mục. Không có vòng fix.

## Vòng 2 — agent `tdq-qc-tester` chạy độc lập (T8.3)

Kết luận của agent: **FAIL** — 9/10 PASS, Q10 FAIL. Agent chạy 59 lệnh, không sửa file
nào trong repo. Bằng chứng đầy đủ của agent nằm ngoài repo, ở thư mục scratchpad phiên
này (`qc-doc-lap-2026-08-08-giam-over-engineer-workflow.md`).

| # | Agent | Ghi chú |
|---|---|---|
| Q1 | PASS | đọc `SKILL.md` L11-25: đủ 4 điều kiện + luật thoát |
| Q2 | PASS | `grep -rn "3 hạng mục" skills/` rỗng |
| Q3 | PASS | thêm phép kiểm động: `--mode external` trả "Mode không hợp lệ", rc=2 |
| Q4 | PASS | — |
| Q5 | PASS | — |
| Q6 | PASS | thêm chứng cứ ngược: cùng file đặt ngoài `docs/tdq` thì R5 bắt lỗi, exit 1 |
| Q7 | PASS | thêm chứng cứ đỏ-trước: bản `704ac3f` chạy trên cùng file trả `[R5] câu 65 từ` |
| Q8 | PASS | 410 test OK, bản `HOME=/nonexistent` cũng OK |
| Q9 | PASS | 4 hook `allow`, `stop_gate` `block` đúng |
| Q10 | **FAIL** | chưa có `docs/tdq/reports/<slug>.md` |

### Khiếm khuyết agent tìm ra — đã đối chiếu lại, đều đúng

1. **Q10 FAIL — report chưa viết.** Đúng theo mặt chữ, nhưng là do thứ tự phase: report
   là việc của phase `report`, chạy sau QC. Không mở vòng fix cho mục này.
2. **`state.json` bị đè.** Lúc 22:59 một lệnh test hook của phiên chính chạy
   `tdq_state.py init 2026-08-08-hook-check full` mà **thiếu `TDQ_PROJECT_DIR`**, ghi
   vào state thật: `active_request` thành `2026-08-08-hook-check`, `phase` về `idle`,
   mất dấu duyệt spec/plan. Doc, code, test, commit không bị ảnh hưởng. Chờ user quyết
   cách khôi phục.
3. **Lệnh DoD sai — LỖI THẬT.** `python3 -m unittest discover -q` chạy ở gốc repo trả
   `NO TESTS RAN`, **exit 5**. Lệnh này nằm trong spec (D8, mục Q8) và plan (T2.x, T3,
   T6.1, T7.x, Tx.2). Lệnh đúng: `python3 -m unittest discover -s tests -t tests -q`.
4. **D2 làm thiếu — LỖI THẬT.** Spec D2 yêu cầu bỏ luật "vòng fix bắt buộc kể cả khi
   user tắt QC". Luật vẫn còn ở `quick-lane.md`, `tdq-intake/SKILL.md` và `PHASE_TABLE`.
5. **Mâu thuẫn trần vòng fix.** `quick-lane.md` dòng 15 ghi lane full "trần không giới
   hạn", trong khi `qc.md` dòng 58 ghi "Trần 3 vòng".
6. **`agents/tdq-reviewer.md` còn khuôn cũ** `knowledge/requests` — sót của D5.
7. **Số đo sai.** Bảng trên ghi "618 / 55 giây"; đo lại tại `704ac3f`: **600 test,
   49,8 giây, 1 đỏ**. Đã sửa trong bảng Số đo.

Mục 3, 4, 5, 6, 7 mở vòng fix 1 trong plan.

## Vòng fix 1 — kết quả

| Fix | Đã làm | Lệnh kiểm | Kết quả |
|---|---|---|---|
| F1 | lệnh DoD sửa ở spec (4 chỗ) và plan (9 chỗ) | `python3 -m unittest discover -s tests -t tests -q` | Ran 410 tests OK |
| F2 | bỏ luật "vòng fix kể cả khi user bỏ QC" ở `quick-lane.md`, `tdq-intake/SKILL.md`, `PHASE_TABLE`, dòng `_info` của `approve quick --no-qc`; sinh lại `phases.md` | `grep -rn "kể cả khi user\|kể cả lúc user" skills/ scripts/` · `test_quick_qc.py` | rỗng · Ran 15 tests OK |
| F3 | `quick-lane.md` dòng 15: lane full đổi "trần không giới hạn" thành "trần 3 vòng" | `grep -rn "không giới hạn" skills/ scripts/` | chỉ còn "không giới hạn cứng" của độ dài report |
| F4 | `agents/tdq-reviewer.md`: `knowledge/context files` và `knowledge/requests` thành `brief` | `grep -n "knowledge\|requests" agents/tdq-reviewer.md` | rỗng |
| F5 | chạy lại hạng mục FAIL cộng hạng mục bản fix có thể làm hỏng | Q2, Q5, Q7, Q8 và `doc_lint skills` | tất cả PASS |

Chi tiết F5:

```
Q2  grep -rn "3 hạng mục" skills/            → rỗng
Q5  TDQ_PROJECT_DIR=<tmp> … next             → 3 dòng nhắc docs/tdq/brief/<slug>.md
Q7  discover -p test_doc_lint.py             → nằm trong 410 test, OK
Q8  discover -s tests -t tests -q            → Ran 410 tests OK
    HOME=/nonexistent  (bản hermetic)        → Ran 410 tests OK
    doc_lint skills · doc_lint spec+plan     → exit 0 · exit 0
```

Còn treo sang phase `report`: Q10 của agent (file `reports/<slug>.md`) — viết ở phase sau.

## Kết luận vòng 1

Q1-Q9 PASS. 5 khiếm khuyết agent tìm ra đã sửa hết trong 1 vòng, dưới trần 3 vòng.
Q10 đóng khi report viết xong.
