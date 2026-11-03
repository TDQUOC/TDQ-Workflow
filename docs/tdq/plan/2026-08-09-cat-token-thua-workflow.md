# PLAN — Cắt token thừa trong TDQ workflow

Ngày: 2026-08-09 · Spec: ../spec/2026-08-09-cat-token-thua-workflow.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — 6 hạng mục đụng chồng lên 4 file dùng chung (`spec-template.md`, `plan-template.md`, `doc_lint.py`, `tdq_state.py`), chạy song song sẽ xung đột merge (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT ("duyệt plan mode main") — HOÀN THÀNH 2026-08-09

## Năng lực → task

| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| graphify | T5.2 | `graphify-out/graph.json` có mtime mới hơn lúc bắt đầu turn |
| mem0-memory | T5.3 | một memory chứa cụm `TDQ workflow cắt token thừa`, tìm lại được bằng search |

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: chạy check trước (đỏ) → sửa → chạy lại đến xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy test của module vừa đụng. Full suite chạy đúng một lần ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục `## QC vòng N — fix` của file này, không cần duyệt lại.
6. Không commit/push cho đến khi user yêu cầu.
7. Khối hợp đồng dưới đây vẫn ghi đủ 6 trường vì T2.1 mới là chỗ bỏ `Nạp`. Sau T2.1
   trường thừa không gây lỗi lint, nên không phải sửa lại plan.

## P1 — Cắt bản chép và step thừa (C1, C2, C3), thuần markdown

- [x] **T1.1** `skill-inventory.md`: đổi luật ghi bảng — chỉ ghi dòng `DÙNG` và `NỀN`, cộng đúng một dòng tổng `Đã xét N skill khác — khác lĩnh vực`; bỏ mục "Bảng quá dài" vì luật mới đã bao — Test: `grep -c "Đã xét" skills/tdq-intake/references/skill-inventory.md` ≥ 1 và `grep -c "Bảng quá dài" …` = 0
- [x] **T1.2** `spec-template.md` §3b: sửa mô tả bảng theo luật mới, giữ nguyên 3 phán quyết và 4 lý do đóng để `doc_lint` R8 không đổi — Test: `python3 scripts/doc_lint.py skills/tdq-spec/references/spec-template.md` exit 0
- [x] **T1.3** `spec-template.md` §4: đổi dòng log service thành có điều kiện — bắt buộc khi plan có ít nhất một task tạo/sửa file mã nguồn chạy được; không có runtime thì ghi một dòng lý do bỏ — Test: `grep -c "có runtime" skills/tdq-spec/references/spec-template.md` ≥ 1
- [x] **T1.4** `plan-template.md`: xoá hẳn mục `## Năng lực → task` và dòng chú thích của nó — Test: `grep -c "Năng lực → task" skills/tdq-plan/references/plan-template.md` = 0
- [x] **T1.5** `plan-template.md`: phase `Px — Log & test bắt buộc` đổi thành có điều kiện, kèm khuôn một dòng lý do bỏ khi không có runtime — Test: `grep -c "có runtime" skills/tdq-plan/references/plan-template.md` ≥ 1

**Xong P1 khi**: 5 lệnh grep/lint ở trên đều trả đúng giá trị mong đợi.

## P2 — Hợp đồng skill còn 5 trường

- [x] **T2.1** `doc_lint.py`: bỏ `"Nạp"` khỏi hằng `CONTRACT_FIELDS` — Test: `cd scripts && python3 -c "import doc_lint; print('Nạp' in doc_lint.CONTRACT_FIELDS)"` in `False`
- [x] **T2.2** `plan-template.md`: khuôn khối hợp đồng còn 5 trường; câu "Agent ngoài không có skill system: đọc `<đường dẫn>/SKILL.md`" dời vào trường `Để` để không mất chỉ dẫn cho sub-agent — Test: khối khuôn không còn dòng `- Nạp:` (`grep -c "^  - Nạp:" …` = 0) và vẫn còn chuỗi `SKILL.md` (`grep -c "SKILL.md" …` ≥ 1)
- [x] **T2.3** `tests/test_doc_lint.py`: thêm test khẳng định `CONTRACT_FIELDS` đúng 5 trường và không chứa `Nạp`; sửa fixture/test cũ nào còn đòi `Nạp` — Test: `cd tests && python3 -m unittest test_doc_lint` 0 fail

**Xong P2 khi**: `cd tests && python3 -m unittest test_doc_lint` xanh và `--pair` vẫn bắt được plan thiếu trường `Kiểm`.

## P3 — Cắt lặp trong phases.md và interview (C4, C5)

- [x] **T3.1** `tdq_state.py`: `phases-doc` thôi sinh mục chi tiết từng phase; giữ bảng 8 cột và khối "lệnh nguyên văn" — Test: `python3 scripts/tdq_state.py phases-doc | grep -c "^## analyze"` = 0
- [x] **T3.2** `tdq_state.py`: bước interview của phase `quick` trong `PHASE_TABLE` đổi thành có điều kiện — chỉ hỏi câu chốt vòng khi vòng đó có ít nhất một câu hỏi — Test (đã sửa: T3.1 bỏ checklist khỏi `phases-doc` nên phải soi thẳng hằng nguồn): `cd scripts && python3 -c "import tdq_state; print(sum('có ít nhất một câu hỏi' in c for c in tdq_state.PHASE_TABLE['quick']['checklist']))"` ≥ 1
- [x] **T3.3** Sinh lại `phases.md` bằng `phases-doc --plugin-root`, không sửa tay — Test: `cd tests && python3 -m unittest test_phase_table` 0 fail
- [x] **T3.4** `interview.md`: ghi luật câu chốt vòng có điều kiện, khớp nguyên văn với `PHASE_TABLE` — Test: `grep -c "có ít nhất một câu hỏi" skills/tdq-intake/references/interview.md` ≥ 1

**Xong P3 khi**: `phases.md` khớp hằng nguồn và ngắn hơn bản cũ ít nhất 40 dòng.

## P4 — Một nguồn sự thật cho CLAUDE.md (C6)

- [x] **T4.1** `docs/claude-md-mau.md`: cắt phần chi tiết đã có ở file đích trong bảng `MOVED` của `tests/test_claude_md_core.py` (failover tavily, chi tiết working log, checklist spec, chi tiết mode thực thi, định tuyến plugin), thay bằng một dòng trỏ về `skills/tdq-conventions/`; giữ nguyên 12 luật bất biến — Test: `cd tests && python3 -m unittest test_claude_md_core` 0 fail và `wc -c docs/claude-md-mau.md` < 3.463
- [x] **T4.2** Đồng bộ bản mẫu ra `~/.claude/CLAUDE.md` — Test: `diff docs/claude-md-mau.md ~/.claude/CLAUDE.md` không in gì, exit 0

**Xong P4 khi**: hai file giống hệt nhau và `test_claude_md_core.py` xanh.

## P5 — Đóng sổ

- [x] **T5.1** Chạy toàn bộ test suite, sửa mọi test đỏ do 4 phase trên gây ra — Test: `cd tests && python3 -m unittest discover -p 'test_*.py'` 0 fail
- [x] **T5.2** Sinh lại graph sau khi đổi code — Test: `ls -l graphify-out/graph.json` có mtime trong turn này
  - Dùng: `graphify`
  - Nạp: gọi skill `graphify` trước bước kiểm của task này. Agent ngoài không có skill
    system: đọc `skills/graphify/SKILL.md` rồi làm theo.
  - Để: chạy `graphify extract . --code-only` sau khi `doc_lint.py` và `tdq_state.py` đã đổi
  - Ra: `graphify-out/graph.json` cập nhật
  - Kiểm: `python3 -c "import json,os;print(os.path.getmtime('graphify-out/graph.json'))"` lớn hơn mtime đầu turn
  - Không dùng cho: trả lời câu hỏi kiến trúc trong report — report viết tay từ kết quả QC
- [x] **T5.3** Ghi một fact dài hạn về hình dạng workflow sau khi cắt — Test: search mem0 trả về ≥ 1 kết quả chứa `TDQ workflow cắt token thừa`
  - Dùng: `mem0-memory` (mcp)
  - Nạp: gọi skill `mem0-memory` trước bước kiểm của task này. Agent ngoài không có skill
    system: đọc `skills/mem0-memory/SKILL.md` rồi làm theo.
  - Để: lưu một fact ngắn — 6 điểm nghẽn đã cắt và ranh giới không đụng gate duyệt
  - Ra: một memory trong project `TDQWorkflow`
  - Kiểm: `mcp__mem0__search_memories` với truy vấn `TDQ workflow cắt token thừa` trả ≥ 1 kết quả
  - Không dùng cho: lưu nội dung spec/plan/report — những thứ đó đã nằm trong repo

**Xong P5 khi**: full suite xanh, graph đã sinh lại, fact đã lưu.

## Definition of Done

Trỏ về §6 của spec. 11 hạng mục, mỗi hạng mục một lệnh:

- D1 `grep -c "Đã xét" skills/tdq-intake/references/skill-inventory.md` ≥ 1
- D2 `grep -c "có runtime" skills/tdq-spec/references/spec-template.md` ≥ 1
- D3 `grep -c "Năng lực → task" skills/tdq-plan/references/plan-template.md` = 0
- D4 `cd scripts && python3 -c "import doc_lint; print('Nạp' in doc_lint.CONTRACT_FIELDS)"` in `False`
- D5 `python3 scripts/tdq_state.py phases-doc | grep -c "^## analyze"` = 0
- D6 `cd tests && python3 -m unittest test_phase_table` 0 fail
- D7 `grep -c "có ít nhất một câu hỏi" skills/tdq-intake/references/interview.md` ≥ 1
- D8 `diff docs/claude-md-mau.md ~/.claude/CLAUDE.md` exit 0, không in gì
- D9 `cd tests && python3 -m unittest test_claude_md_core` 0 fail
- D10 `python3 scripts/doc_lint.py <mọi file trong skills/ vừa sửa>` exit 0
- D11 `cd tests && python3 -m unittest discover -p 'test_*.py'` 0 fail
