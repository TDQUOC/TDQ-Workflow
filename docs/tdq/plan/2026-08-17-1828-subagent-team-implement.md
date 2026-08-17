# PLAN — Mode subagent chạy như một đội: leader phân công cả plan, agent chạy song song, merge có kiểm

Ngày: 2026-08-17 · Spec: ../spec/2026-08-17-1828-subagent-team-implement.md (bản 1.3, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — 28 task đều dồn vào một chuỗi phụ thuộc chặt (P2 cần `[>]` của P1, P3 cần bản đồ của P2, P4 mô tả chính hai thứ đó), và 3 file `tdq_state.py`/`edit_gate.py`/`tdq_team.py` bị nhiều task cùng đụng; hơn nữa chính công cụ để chạy mode đội là thứ request này mới tạo ra, chưa tồn tại lúc bắt đầu. (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH (mode main) — 28/28 task tick [x], QC 23/23 PASS

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. **Mọi thử nghiệm git (worktree, nhánh, merge) chạy trên repo tạm dựng bằng
   `tempfile.TemporaryDirectory()`. Cấm tạo nhánh hay worktree trong repo thật.**

## P1 — Nền: trạng thái `[>]` được mọi nơi hiểu

- [x] **T1.1** (n4 e10m) Mở rộng `_TASK_LINE` và `plan_tick_state` trong `scripts/tdq_state.py`: nhận thêm dấu `>`, trả thêm khoá `dispatched_count` và `dispatched_ids` — Test: `pytest tests/test_team_mode.py -k tick_state -q` — plan 4 `[>]` + 1 `[~]` cho `doing_count=1`, `dispatched_count=4`
  - Chạm: `plan_tick_state()` → `edit_gate.main()`, `stop_gate.main()`, `tdq_checkstatus` (nguồn: `graphify affected "plan_tick_state" --depth 2`)
- [x] **T1.2** (n2 e8m) Bảng `PHASE_TABLE` trong `tdq_state.py` mô tả mode đội ở phase implement: nêu `[>]`, bước 0 phân công, và lệnh `tdq_team.py` — Test: `python3 scripts/tdq_state.py next` in đúng dòng mới khi `implement_mode=subagent`
- [x] **T1.3** (n2 e6m) `[>]` không làm sai tỉ lệ tiến độ mà công cụ ngoài đang đếm — Test: plan 10 task (3 `[x]`, 4 `[>]`, 1 `[~]`) → `total=10`, `xong=3`, không đổi cách đếm cũ

**Xong P1 khi**: `plan_tick_state` trả đủ 5 khoá và mọi test cũ vẫn xanh.

## P2 — `scripts/tdq_team.py`: phân công, chia đợt, worktree, merge

- [x] **T2.1** (n5 e25m) Khung CLI + log service: 7 lệnh con `phan-cong · kiem-ke · cum · mo · kiem · hop · don`, log stderr timestamp ISO, tắt bằng `TDQ_LOG=0`, exit 0/1/2 — Test: `python3 scripts/tdq_team.py --help` exit 0; `TDQ_LOG=0` không in gì ra stderr
- [x] **T2.2** (n8 e30m) `phan-cong`: đọc TOÀN BỘ plan, dựng vùng file từ dòng `Chạm:`, suy phụ thuộc, ghi `docs/tdq/team/<slug>.json` gồm `{plan_sha, tasks:{<id>:{quyet_dinh, ly_do, vung_file, dot}}}` — Test: plan mẫu 8 task → json đủ 8 bản ghi, mỗi bản ghi đủ 4 trường, số đợt khớp chuỗi phụ thuộc
- [x] **T2.3** (n7 e18m) Luật quyết định: mặc định `giao`; chỉ `tu_lam` khi thuộc đúng 4 nhóm (phụ thuộc task chưa xong · vùng file đang khoá · nhãn `(mcp)` · sửa file luật/hook leader đang dùng) — Test: plan mẫu 1 task phụ thuộc + 1 task `(mcp)` + 3 task rời → 3 task rời cùng một đợt, 2 task kia `tu_lam` kèm đúng mã lý do
- [x] **T2.4** (n4 e12m) `kiem-ke`: exit khác 0 khi có task `tu_lam` thiếu lý do hoặc lý do ngoài 4 nhóm; thông điệp nêu mã task + câu lệnh sửa — Test: bản đồ hỏng → exit 1, stderr chứa cả `T2.3` lẫn chuỗi `Giữ:`
- [x] **T2.5** (n3 e10m) Khoá theo sha: `phan-cong` ghi `plan_sha`; `cum`/`kiem-ke` từ chối chạy khi plan đã đổi — Test: sửa plan một ký tự → `cum` exit khác 0, nêu lệnh `phan-cong` để sinh lại
- [x] **T2.6** (n6 e15m) `cum`: in đợt kế tiếp gồm các task `giao` không đụng vùng đang khoá; task bị giữ in kèm lý do — Test: có agent đang giữ `scripts/a.py` → task chạm file đó không vào đợt, stdout nêu rõ vùng khoá
- [x] **T2.7** (n6 e20m) `mo <task-id>`: tạo nhánh + worktree từ nhánh tích hợp, tên không bắt đầu bằng `claude|antigravity|gemini|codex` — Test: repo git tạm → `git worktree list` có đúng 1 worktree mới, tên nhánh đúng khuôn
- [x] **T2.8** (n6 e20m) `kiem <nhanh>`: dò xung đột bằng `git merge-tree $(git merge-base A B) A B`, KHÔNG đụng repo — Test: 2 nhánh sửa cùng file → báo XUNG ĐỘT, exit khác 0, `git status` trước/sau giống hệt
- [x] **T2.9** (n7 e20m) `hop <nhanh>`: hợp tuần tự vào nhánh tích hợp, bật `rerere`, chặn merge khi `kiem` chưa pass — Test: 3 nhánh rời nhau → cả 3 vào nhánh tích hợp, `git log --oneline` đủ 3 commit, nhánh gốc của user không đổi
- [x] **T2.10** (n3 e12m) `don`: `git worktree remove` + `prune`, không `rm -rf` — Test: sau khi dọn, `git worktree list` sạch và `.git/worktrees/` không còn thư mục của request

**Xong P2 khi**: 7 lệnh con đều chạy được trên repo git tạm và `pytest tests/test_team_mode.py -q` xanh.

## P3 — Hook & chẩn đoán: nới đúng chỗ, chặn đúng chỗ

- [x] **T3.1** (n5 e15m) `hooks/scripts/edit_gate.py` thôi chặn khi nhiều `[>]`; vẫn chặn 2 `[~]`, vẫn chặn khi không dấu nào — Test: bơm 3 payload → nhiều `[>]` không chặn, hai `[~]` chặn, không dấu chặn
  - Chạm: `edit_gate.main()` → không node nào phụ thuộc (nguồn: `graphify affected "edit_gate" --depth 2`)
- [x] **T3.2** (n7 e20m) Mã mới `[TDQ:TEAM]` trong `edit_gate.py`: `implement_mode=subagent` + file đang sửa nằm trong `vung_file` của task `giao` chưa có nhánh → CHẶN — Test: cùng một file, task `giao` thì chặn, task `tu_lam` thì KHÔNG chặn
- [x] **T3.3** (n4 e10m) Chặn mới: có `[>]` mà nhánh tương ứng không tồn tại → CHẶN (agent chết giữa chừng) — Test: đánh `[>]` không tạo nhánh → hook chặn, nêu lệnh `tdq_team.py mo`
- [x] **T3.4** (n4 e12m) `scripts/tdq_checkstatus.py`: ca D4 thôi báo lỗi khi nhiều `[>]`; thêm ca "đã giao mà chưa merge" kèm hành động tiếp theo — Test: `pytest tests/test_check_status.py -q` xanh + ca mới có test riêng
  - Dùng: `tdq-status`
  - Để: giữ đúng ngôn ngữ chẩn đoán sẵn có khi thêm ca mới, không tự đặt khuôn khác
  - Ra: `scripts/tdq_checkstatus.py` có ca mới và ca D4 đã sửa
  - Kiểm: `python3 -m pytest tests/test_check_status.py -q` xanh
  - Không dùng cho: đổi định dạng output của các ca đã có

**Xong P3 khi**: hook chặn/không chặn đúng 6 tình huống và test cũ của hook vẫn xanh.

## P4 — Luật: viết đủ chi tiết cho mọi model (spec §4a)

- [x] **T4.1** (n8 e35m) `skills/tdq-build/references/team-mode.md`: đủ khuôn ba mục, BẢNG TRA quyết định (4 nhóm giữ + dòng mặc định GIAO, có cột dấu hiệu và cột lệnh kiểm), ≥4 cặp ví dụ ĐÚNG/SAI, khuôn prompt agent 7 trường — Test: `pytest tests/test_team_mode.py -k khuon -q`
  - Dùng: `tdq-build`
  - Để: viết vòng lặp đội đúng ngôn ngữ và cấu trúc của skill build hiện có
  - Ra: `skills/tdq-build/references/team-mode.md`
  - Kiểm: `python3 scripts/doc_lint.py skills/tdq-build/references/team-mode.md` exit 0
  - Không dùng cho: đổi Phần B (QC) và Phần C (report) của skill build
- [x] **T4.2** (n5 e20m) `skills/tdq-build/SKILL.md` Phần A mode `subagent` viết lại: bước 0 phân công cả plan → vòng lặp phát đợt → merge → đợt kế; trỏ sang `team-mode.md` — Test: `doc_lint` exit 0 và không còn câu "giao ĐÚNG 1 task"
- [x] **T4.3** (n6 e25m) `skills/tdq-plan/SKILL.md` + `references/plan-template.md`: mọi task sửa/tạo file mã nguồn phải có dòng `Chạm:`; plan có mục `## Cụm song song` — Test: `doc_lint --pair` trên cặp spec-plan của chính request này exit 0
  - Dùng: `tdq-plan`
  - Để: sửa đúng khuôn plan mà không phá luật `(mcp)` và luật `(eNm)` đang có
  - Ra: `skills/tdq-plan/SKILL.md`, `skills/tdq-plan/references/plan-template.md`
  - Kiểm: `python3 -m pytest tests/ -q -k plan` xanh
  - Không dùng cho: đổi cổng mode và khuôn câu hỏi duyệt plan
- [x] **T4.4** (n3 e15m) `skills/tdq-plan/references/mode-gate.md`: mô tả option B khớp mô hình đội thật (lai, leader tự làm phần tuần tự) — Test: `doc_lint` exit 0; grep không còn mô tả cũ mâu thuẫn
- [x] **T4.5** (n6 e20m) `skills/tdq-conventions/SKILL.md` §1: cho đóng sổ nhiều lần trong một turn; thêm luật "plan chưa hết task thì không kết thúc turn" + đúng 3 ngoại lệ — Test: `pytest tests/test_soul_rules.py tests/test_step_budget.py -q` xanh; grep thấy đủ 3 ngoại lệ
  - Dùng: `tdq-conventions`
  - Để: sửa §1 giao thức một turn đúng chỗ, giữ nguyên các mục còn lại
  - Ra: `skills/tdq-conventions/SKILL.md`
  - Kiểm: `python3 -m pytest tests/test_soul_rules.py -q` xanh
  - Không dùng cho: đổi soul.md — đổi soul phải mở request riêng có user duyệt
- [x] **T4.6** (n4 e15m) `agents/tdq-implementer.md`: thêm trường `CỤM`, `BASE`, `VÙNG FILE`, luật cấm sửa ngoài vùng được giao, bắt kèm đường dẫn spec+plan — Test: file có đủ 7 trường của khuôn prompt và khuôn trả lời khớp `tdq_team.py hop`
  - Dùng: tdq-implementer (agent)
  - Để: cập nhật hợp đồng agent con cho khớp mô hình đội
  - Ra: `agents/tdq-implementer.md`
  - Kiểm: `pytest tests/test_team_mode.py -k implementer -q` xanh
  - Không dùng cho: gọi agent thật để thử — phase implement này chạy mode `main`

**Xong P4 khi**: 6 file luật đều đạt khuôn ba mục và `doc_lint` exit 0 trên từng file.

## P5 — Log & test bắt buộc

- [x] **T5.1** (n3 e10m) Log service của `tdq_team.py` bật mặc định: timestamp ISO, nêu lệnh con và kết quả, tắt bằng `TDQ_LOG=0` — Test: chạy 1 lệnh có/không `TDQ_LOG=0`, so stderr
- [x] **T5.2** (n7 e30m) `tests/test_team_mode.py`: unit test cho từng thành phần P1–P4, gồm nhóm `khuon` kiểm khuôn ba mục/bảng tra/ví dụ/khuôn prompt và nhóm kiểm mọi lệnh nêu trong file luật là lệnh có thật — Test: `python3 -m pytest tests/test_team_mode.py -q` xanh
- [x] **T5.3** (n3 e12m) Sinh lại hai bundle portable và kiểm — Test: `python3 scripts/build_portable.py` rồi `tdq_checkportable.py check` cho cả hai bản, đều báo `SẠCH`
  - Dùng: `tdq-checkportable`
  - Để: kiểm bundle sau khi sinh lại, đọc đúng tiền tố kết quả
  - Ra: `portable_claude/`, `portable_codex/` khớp manifest
  - Kiểm: `python3 portable_codex/scripts/tdq_checkportable.py check` exit 0
  - Không dùng cho: chạy `setup --trust` — request này không đụng `~/.codex`

**Xong P5 khi**: `python3 -m pytest tests/ -q` xanh và cả hai bundle báo `SẠCH`.

## P6 — QC

- [x] **T6.1** (n6 e25m) Chạy đủ Q1–Q22 theo spec §6, ghi output thật vào `docs/tdq/qc/2026-08-17-1828-subagent-team-implement.md` — Test: file qc có kết luận PASS/FAIL kèm output cho từng hạng mục
- [x] **T6.2** (n5 e20m) QC độc lập Q23: giao agent kiểm lại toàn bộ, không tin lời khai của phase implement — Test: file qc có mục kết luận độc lập kèm output thật
  - Dùng: tdq-qc-tester (agent)
  - Để: chạy lại Q1–Q22 độc lập và soi biên mà phase implement có thể đã bỏ qua
  - Ra: mục `## Kết quả QC độc lập` trong file qc
  - Kiểm: mục đó có verdict PASS/FAIL kèm lệnh và output thật cho từng hạng mục
  - Không dùng cho: tự sửa mã khi FAIL — agent chỉ báo, task fix do phase implement làm

**Xong P6 khi**: Q1–Q23 đều PASS.

## Definition of Done

Trỏ về §6 của spec (23 hạng mục). Mỗi dòng kiểm bằng một lệnh:

1. Q1 `python3 -m pytest tests/ -q` — pass, số test ≥ 767
2. Q2 `pytest tests/test_team_mode.py -k tick_state -q` — `doing_count=1`, `dispatched_count=4`
3. Q3 bơm 3 payload vào `edit_gate.py` — nhiều `[>]` không chặn, hai `[~]` chặn, không dấu chặn
4. Q4 `tdq_team.py cum` trên plan mẫu có 2 task chung file — hai task khác đợt, exit 0
5. Q5 `tdq_team.py kiem` trên repo tạm 2 nhánh đụng nhau — báo XUNG ĐỘT, repo không đổi
6. Q6 `tdq_team.py hop` 3 nhánh rời — đủ 3 commit trong nhánh tích hợp
7. Q7 `tdq_team.py don` rồi `git worktree list` — sạch, `.git/worktrees/` không rác
8. Q8 chạy 1 lệnh có/không `TDQ_LOG=0` — có timestamp ISO / im hoàn toàn
9. Q9 `grep` trong `tdq-conventions/SKILL.md` — có luật chống ngưng + đúng 3 ngoại lệ
10. Q10 `doc_lint.py --pair <spec> <plan>` và `doc_lint.py` từng file — exit 0
11. Q11 `build_portable.py` rồi `checkportable check` hai bản — đều `SẠCH`
12. Q12 `git status --short` trước/sau test — không nhánh/worktree lạ
13. Q13 `tdq_team.py cum` trên plan trộn — 3 task rời cùng đợt, 2 task kia giữ kèm lý do
14. Q14 `tdq_team.py cum` khi có vùng đang khoá — task chạm vùng đó không vào đợt
15. Q15 `tdq_team.py phan-cong` plan mẫu 8 task — json đủ 8 bản ghi, mỗi bản ghi 4 trường
16. Q16 `tdq_team.py kiem-ke` bản đồ thiếu lý do — exit khác 0, in đúng mã task
17. Q17 payload sửa file thuộc task `giao` chưa có nhánh — chặn kèm `[TDQ:TEAM]`; task `tu_lam` không chặn
18. Q18 `pytest tests/test_team_mode.py -k khuon -q` — mọi file luật đủ khuôn ba mục
19. Q19 test đọc `team-mode.md` — bảng tra đủ 4 nhóm + dòng GIAO + 2 cột
20. Q20 test đọc `team-mode.md` — ≥4 cặp ĐÚNG/SAI, khuôn prompt đủ 7 trường
21. Q21 test quét lệnh trong file luật — mọi lệnh con tồn tại, `--help` exit 0
22. Q22 `tdq_team.py kiem-ke` trên bản đồ hỏng — stderr có mã task + câu lệnh sửa
23. Q23 agent `tdq-qc-tester` chạy lại Q1–Q22 — kết luận PASS kèm output thật
