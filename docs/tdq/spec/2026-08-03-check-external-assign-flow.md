# SPEC — Đổi thiết kế mode external: giao cả plan 1 lần + fix loop

Ngày: 2026-08-03 · Bản: 1.2 · Request: ../requests/2026-08-03-check-external-assign-flow.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: lane full mode external giao TOÀN BỘ plan cho engine ngoài trong MỘT lần gọi (qua subagent runner); plan lớn ước vượt trần timeout → CHIA THEO PHASE, mỗi phase một lần gọi trong một turn. Engine TỰ VERIFY vòng 1 sau mỗi task (chạy lệnh test của task, ghi kết quả vào report). Xong mỗi phase Claude verify phase; xong hết Claude verify tổng; sai → mini-plan fix giao lại external, tối đa 2 vòng; vẫn sai → Claude tự làm phần còn lại.
- Trong phạm vi:
  - `scripts/external_task.py`: chế độ `run-plan` (gói plan, timeout = 540s × số task, trần 3600s, vẫn override qua `TDQ_EXTERNAL_TIMEOUT`), schema report tổng (per-task bên trong), giữ retry 3 attempt/lần gọi.
  - `skills/tdq-build/SKILL.md` "Nhánh external": viết lại flow giao-1-lần + verify tổng + fix loop ≤2 + fallback Claude.
  - `skills/tdq-plan/SKILL.md` "Chốt engine + model": lane full chỉ chốt 1 model (mức `khó`); dòng máy-đọc giữ tương thích cũ.
  - Agents `codex-runner`, `agy-runner`: contract nhận gói plan/gói fix, vẫn là subagent chạy lệnh trigger (main không tự chạy).
  - Khuôn gói: `skills/tdq-build/references/external-task.md` → thêm khuôn gói plan + gói mini-plan fix.
  - Unit test cho mọi phần đổi + cập nhật test cũ bị ảnh hưởng.
- NGOÀI phạm vi: quick lane external (giữ nguyên 1 gói 1 lần gọi); các bước an toàn đóng worktree (cấm engine commit, diff-check + status --porcelain, chạy toàn suite trước merge) giữ nguyên; không đổi engine list, không đổi cơ chế log run.log, không đụng mode main/subagent.

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Lệnh `run-plan` giao cả plan 1 lần | scripts/external_task.py | unit test parse args, timeout scale, report tổng hợp lệ |
| 2 | Schema report plan: MỞ RỘNG `external_report_schema.json` hiện có với discriminator `kind: task\|plan` (kind vắng = task, giữ hồi quy quick lane); plan-report chứa mảng per-task report + status tổng | scripts/external_report_schema.json | validate_report test pass cả report task (cũ, không kind) lẫn report plan |
| 3 | Flow mới trong skill build: luật chia phase (>6 task → chia gói ≤6, mỗi phase 1 turn, phase sau chờ phase trước pass) + verify 3 tầng (engine tự verify vòng 1 · Claude verify phase · Claude verify tổng: toàn suite + diff-check `files_changed` + `status --porcelain`); task fail test hoặc file lệch → vào mini-plan fix | skills/tdq-build/SKILL.md | doc liệt kê đủ luật chia phase + 3 tầng verify + tiêu chí chọn task vào fix; doc_lint exit 0 |
| 4 | Khuôn gói plan/phase + gói fix; mọi gói BẮT BUỘC mục "tự verify: chạy lệnh test từng task, ghi test_result thật"; gói fix thêm "task đã PASS — không làm lại" và "file cấm sửa" | skills/tdq-build/references/external-task.md | có 2 khuôn, trường bắt buộc liệt kê đủ (tự verify + 2 mục bảo vệ) |
| 5 | tdq-plan lane full chỉ chốt 1 model: bỏ hướng dẫn map TB/dễ ở lane full (parse-plan đã nhận dòng chỉ `khó=` — giữ hồi quy) | skills/tdq-plan/SKILL.md | doc chỉ còn 1 model lane full; test parse dòng 1 model + 3 model đều pass |
| 6 | Runner agents nhận gói plan/gói fix | agents/codex-runner.md, agents/agy-runner.md | mô tả agent khớp lệnh run-plan; grep không còn ràng buộc "MỘT task" ở lane full |
| 7 | Test suite xanh | tests/ | toàn bộ test pass 1 lệnh |
| 8 | Cơ chế đếm vòng fix: file `docs/tdq/external/<slug>/fix-rounds.json` (`{"rounds": [{"n":1,"tasks":[…],"result":…}]}`), skill quy định đọc/ghi trước mỗi vòng | skills/tdq-build/SKILL.md + khuôn ở references | doc mô tả format + luật dừng ở 2 vòng; QC Q6 |
| 9 | Đồng bộ doc hệ thống: CLAUDE.md mục 9 (user-level) + câu mô tả external ở tdq-intake/tdq-status nếu còn ghi "giao TỪNG task" | ~/.claude/CLAUDE.md, skills/tdq-intake, skills/tdq-status | `grep -r "TỪNG task"` trong repo + CLAUDE.md không còn mô tả trái flow mới |

## 3. Cách tiếp cận & lý do
- Chọn: thêm subcommand `run-plan` bên cạnh `run` (giữ `run` cho quick lane), report tổng chứa per-task để verify từng lệnh test; fix loop điều phối ở tầng skill (Claude soạn mini-plan fix `docs/tdq/external/<slug>/fix-round-<n>.task.md` rồi gọi lại runner), đếm vòng bằng `fix-rounds.json` (đầu ra #8).
- Timeout: `run-plan` tính theo SỐ TASK TRONG GÓI ĐƯỢC GIAO (gói fix tính theo số task của gói fix, không theo plan gốc); 540s × n, trần 3600s, override qua `TDQ_EXTERNAL_TIMEOUT`.
- Chia phase khi plan lớn: nếu 540s × (số task toàn plan) > 3600s (tức > 6 task) → Claude chia plan theo phase (nhóm task theo phase sẵn có của plan, hoặc cắt tuần tự ≤ 6 task/gói), mỗi phase = 1 gói `run-plan` = 1 lần gọi runner trong 1 turn; phase sau chỉ giao khi phase trước qua verify phase.
- Verify 3 tầng: (1) engine TỰ verify vòng 1 — gói task bắt buộc engine chạy lệnh test từng task và ghi `test_result` thật vào per-task report; (2) Claude verify PHASE ngay sau mỗi gói — chạy lại lệnh test các task trong phase + diff-check; (3) Claude verify TỔNG sau phase cuối — toàn suite + diff-check + status --porcelain. Fail ở tầng 2/3 → mini-plan fix.
- Attempt cho `run-plan`: giảm còn **2 attempt** (thay vì 3 của `run`) — trần thời gian 1 lần gọi runner ≤ 2 × 3600s; runner vẫn chạy Bash nền + poll, skill ghi rõ trần này để subagent không treo vô hạn.
- Vì: giữ tương thích quick lane, script vẫn ôm phần dễ sai (CLI flag, timeout, parse, retry); user thấy tiến trình qua subagent runner như yêu cầu.
- Đã loại: giao từng task (thiết kế cũ) — user chốt đổi; loại luôn phương án bỏ subcommand `run` — quick lane còn dùng.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-build / tdq-plan / tdq-conventions | plugin:tdq-workflow | NỀN | skill khung của chính workflow đang sửa |
| graphify | user | DÙNG | cập nhật code graph cuối build (quy ước CLAUDE.md) |
| tavily / research | plugin:tavily | KHÔNG | khác lĩnh vực — việc thuần nội bộ, không có ẩn số ngoài |

## 4. Yêu cầu bắt buộc
- Log service bật mặc định: mọi lần gọi engine (plan, fix round) ghi run.log timestamp như hiện tại, tắt qua `TDQ_EXTERNAL_LOG=0`.
- Không placeholder, không TODO stub.
- Mỗi thành phần đổi có unit test riêng, chạy được bằng một lệnh.
- Lệnh trigger engine luôn do subagent runner chạy — main conversation không tự chạy `external_task.py run-plan`.

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Plan lớn vượt trần 3600s | engine bị kill giữa chừng | chia phase ≤6 task/gói (mỗi phase 1 turn); trần 3600s + override env; verify phase/tổng bắt task thiếu → fix loop |
| Engine khai test_result "pass" khống | verify vòng 1 vô nghĩa | Claude verify phase/tổng luôn tự chạy lại lệnh test — không tin report suông (giữ luật hiện có) |
| Engine làm sai nhiều task cùng lúc | 2 vòng fix không đủ | fallback Claude tự làm phần còn lại (đã chốt) |
| Report tổng lớn, model thấp trả JSON hỏng | retry tốn thời gian | run-plan 2 attempt + feedback lỗi + raw dump; run (quick) giữ 3 attempt |
| Runner chờ phiên dài (tới 2×3600s) | subagent treo lâu, khó quan sát | poll + log run.log từng attempt; trần tổng ghi rõ trong contract runner |
| Engine round fix phá task đã xong | mất tiến độ vòng trước | khuôn gói fix bắt buộc mục "task đã PASS — không làm lại" + "file cấm sửa"; verify tổng chạy lại toàn bộ lệnh test mỗi vòng |
| Đổi schema làm hỏng quick lane | quick external gãy | `run` + schema task cũ giữ nguyên, test hồi quy |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Unit test toàn suite | lệnh test chuẩn của repo (pytest/run_tests) | exit 0, không test nào skip vì lỗi |
| Q2 | `run-plan` E2E giả lập engine (mock binary) | test E2E có sẵn pattern trong tests/ | report tổng ghi đúng, timeout scale đúng, exit code đúng |
| Q3 | `parse-plan` tương thích: dòng cũ 3 model + dòng mới 1 model | unit test parse | cả hai dạng pass |
| Q4 | Doc lint spec/plan/skill | `python3 scripts/doc_lint.py <file>` | exit 0 |
| Q5 | Quick lane không gãy | chạy lại test quick-ext hiện có | pass nguyên trạng |
| Q6 | Fix loop: mô phỏng 2 vòng fail → fallback | unit/E2E test đọc-ghi fix-rounds.json + luật dừng | sau vòng 2 fail, cơ chế báo fallback Claude; không có vòng 3 |
| Q7 | Timeout scale theo gói (plan n task, fix m task) | unit test tính timeout | 540×n trần 3600; gói fix dùng m, không dùng n |
| Q8 | Luật chia phase: plan 7+ task | unit test hàm chia gói / kiểm doc + E2E mock 2 phase | gói ≤6 task, đúng thứ tự, phase sau chỉ chạy khi phase trước pass |
| Q9 | Engine tự verify vòng 1 | E2E mock: report thiếu test_result thật → validate fail | report per-task có test_result; thiếu → attempt retry |

DoD: 9 đầu ra ở §2 đạt điều kiện đo; Q1–Q9 PASS có bằng chứng trong `docs/tdq/qc/<slug>.md`.

## 7. Câu hỏi còn mở
(RỖNG)
