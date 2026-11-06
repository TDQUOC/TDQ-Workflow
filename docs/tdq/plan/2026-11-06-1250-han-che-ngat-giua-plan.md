# PLAN — Hạn chế ngắt giữa plan trên Claude Code

Ngày: 2026-11-06 · Spec: ../spec/2026-11-06-1250-han-che-ngat-giua-plan.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — mô phỏng 5 task theo chuỗi: main 10,2 phút, đội 10,2 phút, `Winner: main` (chênh 0,0 phút); Stop và SessionStart có test riêng, không tự bật `/goal`.
Trạng thái plan: HOÀN THÀNH.

## Quy tắc thi hành

- Mỗi task: đánh `[~]` trước; test đỏ thật → thay đổi nhỏ nhất → test xanh → `[x]` ngay. Khi plan lệch nhẹ, đối chiếu spec đã duyệt, `lech add` rồi tiếp tục; chỉ commit để gỡ blocker. Bốn loại `pause` và cổng duyệt giữ nguyên.
- Chỉ Claude Code; không sửa `hooks/scripts/agy_stop_gate.py`, CI, config ngoài repo hay chạy model trial. `/goal` chỉ là hướng dẫn tùy chọn để người dùng xác nhận rồi tự bật trong session; TDQ không gọi thay.
- Preview planned đã duyệt: `../spec/2026-11-06-1250-han-che-ngat-giua-plan-preview.html` + manifest; verify trước code; không sửa preview sau duyệt để che lệch thiết kế.
- QC `full`: hồi quy vùng chạm trong từng task, một full fresh khi nguồn ổn định, QC/HTML báo chứng cứ thật.

## Thiết kế Trước vs Sau

| Mặt | Trước | Sau |
|---|---|---|
| Stop | Chặn 3 lượt; lượt 4 chỉ `[TDQ:STUCK]` chung chung | Vẫn 3 lượt; hint nêu task và bước kiểm, không tự retry tool |
| Resume | Anchor `doing`/`dispatched` | Có thêm task đầu chưa làm và bước kiểm sau resume/compact |
| Lệch nhỏ | Có fallback/`lech add`, ưu tiên plan–spec chưa rõ | Plan dẫn đường; spec đã duyệt là chuẩn khi xung đột; ghi lệch, tiếp tục, báo ở report |
| `/goal` | Không có điều kiện TDQ | Hướng dẫn tùy chọn; người dùng xác nhận rồi tự bật, không phải gate mới |

## P1 — Stop nhắc đúng và hạ cấp an toàn

- [x] **T1.1** (e16m) Test đỏ→xanh: Stop lần 1–3 nêu task mở và bước tiếp, lần 4 `[TDQ:STUCK]` nêu task/số còn mở; giữ trần 3, reset khi plan đổi, không block pause/`[>]`/phase khác/plan thiếu — Test: `python -m pytest tests/test_stop_gate.py -q`
  - Chạm: `hooks/scripts/stop_gate.py`, `tests/test_stop_gate.py` → `unfinished_reason`, `_chan_chua_xong`, `_streak_bump`, `main` và fixture Stop; LSP refs 11 cho `unfinished_reason`, 3 cho `_chan_chua_xong`; Graphify `affected plan_tick_state` ra Stop/SessionStart/prompt_context, không sửa Antigravity.
  - Dùng: `LSP, Graphify, Grep` (mcp)
  - Để: tìm caller thật của Stop/plan tick và vùng ảnh hưởng hai bước trước khi sửa hook.
  - Ra: bảng `Chạm:` của T1.1/T2.1 gắn caller và test vùng chạm, không dựa riêng vào tên file.
  - Kiểm: `python scripts/tdq_lsp.py check`
  - Không dùng cho: tự sửa state hoặc cài thêm Language Server.
  - Ra thêm: lời nhắc ≤300 ký tự có task/bước kiểm thật khi plan đọc được; fallback hint chung khi plan hỏng; không thay đổi cổng phê duyệt.
  - Tiến độ: test Stop đỏ thật (5 failed, 15 passed); Stop suite 116 passed nhưng receipt vùng chạm INCOMPLETE do nguồn sửa trong lúc chạy. Test đỏ mới xác nhận hint thiếu `Test: y`; hoàn thiện hint rồi chạy vùng chạm trên nguồn ổn định.

## P2 — Khôi phục session

- [x] **T2.1** (e14m) Test đỏ→xanh: SessionStart `resume`/`compact` nhắc task `[~]` hoặc task đầu `[ ]`, phân biệt `[>]`, kiểm receipt/tool cũ trước retry; plan hỏng/không request vẫn fallback — Test: `python -m pytest tests/test_context_hooks.py tests/test_prompt_context.py -q`
  - Chạm: `hooks/scripts/session_start.py`, `tests/test_context_hooks.py`, `tests/test_prompt_context.py` → `main`, recovery anchor; `plan_tick_state` caller Stop và prompt_context đã khảo sát; nếu test đỏ chứng minh cần, sửa `hooks/scripts/prompt_context.py` với test trong cùng task.
  - Cần: T1.1
  - Ra: anchor ngắn, không tự chạy lại tool và không ghi state.

## P3 — Luật lệch nhẹ và hướng dẫn goal

- [x] **T3.1** (e10m) Red→green: làm rõ plan trước, spec đã duyệt khi mâu thuẫn; lệch nhỏ `lech add` + làm tiếp, commit chỉ gỡ blocker, gom báo cáo cuối; không tự mở cổng duyệt hoặc bỏ test an toàn — Test: `python -m pytest tests/test_luat_skill.py tests/test_runtime_contracts.py -q`
  - Chạm: `skills/tdq-build/SKILL.md`, test contract liên quan nếu cần; không chép thuật toán Python vào skill.
  - Cần: T2.1
  - Ra: luật một chỗ, các file chỉ mục/ngân sách khớp (`doc_index.py`, `token_budget.py` nếu file luật đổi).
- [x] **T3.2** (e8m) Thêm hướng dẫn `/goal` có điều kiện đo task/DoD/QC, nêu giới hạn host/chi phí, yêu cầu người dùng xác nhận trước khi họ bật, không tự gọi goal — Test: `python -m pytest tests/test_luat_skill.py tests/test_runtime_contracts.py -q`
  - Chạm: cùng vùng luật T3.1 (`skills/tdq-build/SKILL.md`) nếu cần; một chủ ghi, làm sau T3.1.
  - Cần: T3.1
  - Dùng: `/goal`
  - Để: hướng dẫn người dùng tùy chọn bật điều kiện plan/DoD/QC trong chính session sau xác nhận riêng; không gọi lệnh thay họ.
  - Ra: một điều kiện goal tham khảo gắn slug/plan, không khẳng định goal luôn kết thúc hoặc âm thầm dùng model đánh giá.
  - Kiểm: `python -m pytest tests/test_luat_skill.py tests/test_runtime_contracts.py -q`
  - Không dùng cho: chạy goal trong QC, tạo session phụ hoặc thay Stop hook.

## P4 — QC và report

- [x] **T4.1** (e12m) QC `full`: DoD Q1–Q6, hồi quy vùng chạm, một full fresh, kiểm giới hạn Stop, kiến trúc, clean code; viết QC Markdown + báo cáo Markdown/Archify HTML bốn phần — Test: `python scripts/tdq_test.py tron-bo --workers 1 --fresh --reuse off`
  - Dùng: `tdq-lean`
  - Để: rà diff tránh scheduler/state/config dư thừa.
  - Ra: danh sách đề xuất `delete/shrink` hoặc `Lean already. Ship.`; QC + report có bằng chứng.
  - Kiểm: `python scripts/doc_lint.py --pair docs/tdq/spec/2026-11-06-1250-han-che-ngat-giua-plan.md docs/tdq/plan/2026-11-06-1250-han-che-ngat-giua-plan.md`
  - Không dùng cho: sửa mã hoặc tự bật `/goal`.
  - Cần: T3.2

## Cụm song song & file nóng

- Chuỗi T1.1 → T2.1 → T3.1 → T3.2 → T4.1 để giữ task/test hợp lệ. File `skills/tdq-build/SKILL.md` chạm hai task: cùng một chủ ghi theo thứ tự, không giao đồng thời. Stop/SessionStart độc lập vùng file nhưng T2.1 đọc kết quả T1.1; không chạy suite cùng lúc.

## Px — Log & test bắt buộc

- Hook giữ log timestamp và `TDQ_LOG=0`; test T1.1/T2.1 khóa trước full. Không thêm service hoặc file log mới; không chạy trial model.

## Definition of Done

- [x] Q1 Stop ba lần có task/bước tiếp, plan xong/pause/`[>]`/phase khác không block — `python -m pytest tests/test_stop_gate.py -q`
- [x] Q2 Lần bốn không block, STUCK nêu đúng task/số còn mở, tick tiến triển reset — `python -m pytest tests/test_stop_gate.py -q`
- [x] Q3 Resume/compact có task `[~]` hoặc đầu `[ ]`, không replay tool, plan hỏng fallback — `python -m pytest tests/test_context_hooks.py tests/test_prompt_context.py -q`
- [x] Q4 Luật plan/spec/lech/commit giữ bốn pause và cổng duyệt — `python -m pytest tests/test_luat_skill.py tests/test_runtime_contracts.py -q`
- [x] Q5 `/goal` chỉ hướng dẫn điều kiện đo được khi có xác nhận, không tự bật hoặc gọi model trial — `python -m pytest tests/test_luat_skill.py tests/test_runtime_contracts.py -q`
- [x] Q6 Full fresh PASS, Antigravity và CI không đổi, Archify report verify — `python scripts/tdq_test.py tron-bo --workers 1 --fresh --reuse off`

Các dòng Q1/Q2 và Q4/Q5 dùng lại cùng output khi nguồn không đổi; không chạy lặp chỉ để tick. Full fresh chỉ ở QC-F1, lỗi thật thì fix và chạy lại sau nguồn ổn định.

Tổng ước tính 60 phút tác vụ, không gồm chờ duyệt và thời gian full suite.
