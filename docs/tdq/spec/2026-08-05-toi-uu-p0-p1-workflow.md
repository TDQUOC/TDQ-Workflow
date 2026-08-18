# SPEC — Triển khai 16 đề xuất P0+P1 tối ưu workflow TDQ & user-level Claude Code

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-05 · Bản: 1.0 · Request: ../requests/2026-08-05-toi-uu-p0-p1-workflow.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: biến 16/19 đề xuất P0+P1 của audit vòng 3
  (`knowledge/2026-08-05-audit-toi-uu-workflow.md` mục 9) thành thay đổi code/doc thật,
  đo được bằng test/grep cụ thể — giảm carry-cost lặp lại mỗi turn/session và vá 2
  mâu thuẫn luật + 1 rủi ro false-positive đã audit nêu.
- Trong phạm vi: 5 P0 (P0-2, P0-3, P0-4, P0-5, P0-6) + 11 P1 (P1-1, P1-2, P1-3, P1-4,
  P1-5, P1-6, P1-7, P1-10, P1-11, P1-12, P1-13).
- NGOÀI phạm vi:
  - P0-1 — đã làm xong ở round trước (nới trần report), không lặp lại.
  - P1-8, P1-9 — audit ghi sai/lỗi thời, đã làm xong ở vòng 2 (§10 `tdq-conventions/SKILL.md`).
  - Toàn bộ P2 (7 đề xuất) — user chốt chỉ làm P0+P1 round này.
  - P1-3 phần code: chỉ ghi chú rủi ro, KHÔNG đổi code `stop_gate.py` (user chọn Q4.A).
  - P1-12 phần đo thật: chỉ thiết kế kịch bản, KHÔNG tự chạy đo before/after round này
    (user chọn Q6.A — cần 2 session sạch, không tự động hoá được trong 1 lần chạy).
  - `tdq-conventions/SKILL.md`: không tách theo lane (user chọn Q2.A, chỉ tách `tdq-intake`).

## 1b. Lộ trình
Chép từ `knowledge/2026-08-05-toi-uu-p0-p1-workflow.md` mục "Lộ trình".

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Phân tích | CÓ (đã xong) | Đọc code qua Explore agent + interview 6 câu — hết chỗ mơ hồ |
| Research web (tavily) | BỎ | Việc kỹ thuật nội bộ, không có ẩn số bên ngoài; research external đã đủ ở audit vòng 3 |
| Interview | CÓ (đã xong) | 6 câu ảnh hưởng effort/rủi ro thật, tất cả đã trả lời |
| Spec | CÓ | Bắt buộc theo khung TDQ |
| Plan | CÓ | 16 đề xuất chạm nhiều file độc lập theo cụm — chia phase rõ, mode do user chốt lúc duyệt |
| QC độc lập bằng agent (`tdq-qc-tester`) | CÓ | Chạm hook lõi (`bash_gate.py`, `_common.py`) — cần 1 lượt kiểm độc lập ngoài self-check |
| Review sâu bằng agent (`tdq-reviewer`) | BỎ (mặc định) | Chỉ gọi nếu user yêu cầu thêm lúc duyệt plan |
| Implement → report | CÓ | Khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | `turn_snapshot()` chạy `git status --porcelain` đúng 1 lần thay vì 2 | `scripts/tdq_state.py` | Test mới đếm số lần gọi `_git(..., "status", ...)` trong 1 lần `turn_snapshot()` = 1 |
| 2 | `bash_gate.py` đọc `turn_rows()` đúng 1 lần/invoke, truyền xuống các hàm dùng lại | `hooks/scripts/bash_gate.py`, `hooks/scripts/_common.py` | Test mới đếm số lần đọc file `.tdq-turn.jsonl` trong 1 lần `main()` = 1 |
| 3 | Hết mâu thuẫn hard/soft-block task `(mcp)` khi external — chốt hard-block | `skills/tdq-intake/references/quick-lane.md` | `grep -n "làm theo user"` trên file trả rỗng; `doc_lint.py --pair` với `tdq-build/SKILL.md` exit 0 |
| 4 | §6 `tdq-conventions/SKILL.md` trỏ link tới `reminder-codes.md` thay vì diễn giải lại định nghĩa "đã đổi repo" | `skills/tdq-conventions/SKILL.md` | `grep -n "reminder-codes.md" skills/tdq-conventions/SKILL.md` trả ≥1 |
| 5 | 3 lệnh git rời rạc lúc đóng worktree external gộp bằng `&&` | `skills/tdq-build/SKILL.md` (mục Đóng worktree) | Đọc lại bằng mắt: đúng 1 dòng lệnh gộp thay vì 3 dòng rời |
| 6 | `tdq-intake/SKILL.md` Phần B tách ra reference riêng, quick lane không nạp | `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/analyze-full.md` (file mới) | `wc -l skills/tdq-intake/SKILL.md` giảm so với 117 dòng gốc; Phần C (quick lane) không còn chứa nội dung Phần B |
| 7 | `lane-decision.md` dùng đúng khuôn `interview.md` thay vì tự định nghĩa khuôn riêng | `skills/tdq-intake/references/lane-decision.md` | Đọc lại bằng mắt: khuôn câu hỏi khớp `interview.md`; `doc_lint.py` exit 0 |
| 8 | Test mới canh khớp ngưỡng digest 1.500 ký tự giữa 8 file agent + skill nguồn | `tests/test_agent_digest_sync.py` (file mới) | `python3 -m unittest test_agent_digest_sync -v` PASS; sửa số ở 1 file mà không sửa 7 file kia → test FAIL (kiểm tay 1 lần khi build) |
| 9 | Ghi chú rủi ro false-positive `stop_gate.py` khi 2 phiên cùng chạy 1 worktree chính | `skills/tdq-conventions/references/reminder-codes.md` | `grep -n "2 phiên"` (hoặc từ khoá tương đương) trên file trả ≥1 |
| 10 | Thêm 3 ví dụ cụ thể (đổi schema DB, xoá data, đổi API contract công khai) vào nhóm "cần dừng hỏi" | `skills/tdq-build/SKILL.md` (Luật cứng) | Đọc lại bằng mắt: đủ 3 ví dụ xuất hiện trong đoạn Luật cứng |
| 11 | `skill_dump()` chỉ chép khối hợp đồng (Dùng/Nạp/Để/Ra/Kiểm) + lệnh CLI, bỏ phần diễn giải dài | `scripts/external_task.py` | Test mới: dump skill `tdq-build` → output ngắn hơn bản hiện tại (so byte, có ngưỡng cụ thể trong test) |
| 12 | `prompt_context.py` dedupe: turn sau in gọn nếu state + nội dung NEXT/APPROVE không đổi so với turn trước | `hooks/scripts/prompt_context.py` | Test mới: gọi hook 2 lần liên tiếp cùng state → output lần 2 ngắn hơn/khác lần 1 theo đúng quy tắc dedupe |
| 13 | Khuyến nghị `/clear` sau khi đóng 1 request/session dài | `portable/AGENTS.md` (mục Working log hoặc mục mới) | `grep -n "/clear"` trên file trả ≥1 |
| 14 | Mục "Nhánh external" (62 dòng) tách ra reference riêng, chỉ nạp khi `implement_mode=external` | `skills/tdq-build/SKILL.md`, `skills/tdq-build/references/external-build.md` (file mới) | `wc -l skills/tdq-build/SKILL.md` giảm so với 150 dòng gốc; Phần A bước 1 có câu trỏ nạp file mới khi mode external |
| 15 | Kịch bản đo carry-cost before/after chuẩn hoá (tài liệu quy trình, chưa phải số đo) | `skills/tdq-conventions/references/measure-scenario.md` (file mới) | File tồn tại, có danh sách thao tác cố định + lệnh `token_audit.py --transcript-dir` mẫu cho 2 session |
| 16 | Hướng dẫn chạy test suite ở chế độ tóm tắt (không dán log dài vào chat) | `skills/tdq-build/references/qc.md` | `grep -n "\-q\|dot reporter\|redirect"` (hoặc từ khoá tương đương) trên file trả ≥1 |

## 3. Cách tiếp cận & lý do

- Chọn: sửa trực tiếp từng điểm đã xác định rõ vị trí qua rà soát code (Explore agent),
  thay đổi tối thiểu đủ đạt đầu ra §2, không refactor rộng hơn phạm vi 16 mục.
- Vì: audit + rà soát code đã xác định chính xác file/dòng cho từng mục — không còn ẩn
  số kỹ thuật, làm tối thiểu giảm rủi ro phá vỡ hook/skill đang chạy ổn.
- Đã loại:
  - Đại tu kiến trúc gộp ngưỡng 1.500 ký tự thành 1 module Python import chung cho cả
    8 file agent — vì file agent là prompt text (`.md`), không "import" hằng số Python
    được; chọn test-lock thay vì đổi cơ chế nạp (đúng quyết định Q3.A).
  - Sửa sâu `stop_gate.py` theo dõi file-theo-turn (Q4.B) — vì effort cao, rủi ro phá
    hook lõi đang chạy ổn, trong khi rủi ro thật chỉ xảy ra ở kịch bản hẹp (2 phiên cùng
    1 worktree chính).
  - Tách `tdq-conventions/SKILL.md` theo lane (Q2.B) — vì không có ranh giới quick/full
    rõ ràng trong file này để tách an toàn.
  - Tự chạy đo carry-cost before/after thật (Q6.B ngược lại) — vì cần 2 session sạch
    thao tác y hệt nhau, không thực hiện được gọn trong 1 lượt build.

## 3b. Năng lực & công cụ
Chép từ `knowledge/2026-08-05-toi-uu-p0-p1-workflow.md` mục "Năng lực dùng được".

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-conventions` | plugin:tdq-workflow | NỀN | Khung quy ước đang chạy cho chính request này |
| `tdq-intake` | plugin:tdq-workflow | NỀN | Đã dùng ở phase analyze |
| `tdq-spec` | plugin:tdq-workflow | NỀN | Đang dùng để viết spec này |
| `tdq-plan` | plugin:tdq-workflow | DÙNG | Viết plan ngay sau khi spec được duyệt |
| `tdq-build` | plugin:tdq-workflow | DÙNG | Thực thi 16 đầu ra ở §2 |
| `graphify` | user | DÙNG | Rebuild graph cuối turn có đổi code |
| `claude-md-improver` | plugin:claude-md-management | KHÔNG | khác lĩnh vực — không đầu ra nào ở §2 chạm `portable/claude-md/CLAUDE.md` |
| Explore agent | built-in | DÙNG | Đã dùng ở phase analyze để rà soát code 19 đề xuất |
| `tavily-*` (mọi biến thể) | plugin:tavily | KHÔNG | khác lĩnh vực — việc kỹ thuật nội bộ, không có ẩn số bên ngoài cần tra cứu |
| `hookify` | plugin:hookify | KHÔNG | spec §3 đã chọn cách khác tốt hơn — sửa hook có sẵn bằng Edit trực tiếp thay vì tạo hook mới |
| `remember` | plugin:remember | KHÔNG | khác lĩnh vực — không dùng `.remember/` cho việc này |
| `skill-creator`, `plugin-dev:*` | plugin | KHÔNG | khác lĩnh vực — không tạo skill/plugin mới |
| `frontend-design`, `playground`, `mcp-server-dev:*` | plugin | KHÔNG | khác lĩnh vực — không liên quan (không UI/MCP server mới) |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: các script/hook đã đổi (`tdq_state.py`, `bash_gate.py`,
  `_common.py`, `prompt_context.py`, `external_task.py`) giữ nguyên cơ chế log hiện có
  (không tắt/giảm mức log khi tối ưu số lần gọi).
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật — đặc biệt
  đầu ra #15 (kịch bản đo) phải là quy trình thật chạy được, không phải mô tả suông.
- Mỗi đầu ra ở §2 có ít nhất 1 test/lệnh kiểm đo được riêng (cột "Đo xong bằng"), chạy
  bằng 1 lệnh.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Sửa `bash_gate.py`/`_common.py`/`stop_gate.py`-liên-quan (hook lõi PreToolUse/Stop) sai có thể chặn nhầm hoặc bỏ sót cảnh báo mọi turn sau | Cao | Test mới cho từng thay đổi (đầu ra #1, #2) + chạy full suite 1 lần ở QC + gọi `tdq-qc-tester` kiểm độc lập |
| Tách `tdq-intake/SKILL.md` và `tdq-build/SKILL.md` thành nhiều file có thể làm quick lane/mode external thiếu nội dung nếu quên thêm câu "Nạp" | Trung bình | Đầu ra #6, #14 đều yêu cầu đọc lại bằng mắt câu trỏ nạp; kiểm tay chạy thử 1 lần lane quick sau khi sửa |
| Đổi `quick-lane.md` sang hard-block (đầu ra #3) có thể khác kỳ vọng nếu có external run cũ đang dở dang | Thấp | Chỉ ảnh hưởng request MỚI mở sau khi merge; không có external run nào đang chạy tại thời điểm spec này |
| `external_task.py skill_dump()` nén nội dung (đầu ra #11) có thể làm engine ngoài thiếu ngữ cảnh nếu nén quá tay | Trung bình | Giữ nguyên khối hợp đồng máy-đọc (Dùng/Nạp/Để/Ra/Kiểm) + lệnh CLI — đây là phần engine cần để chạy đúng, chỉ bỏ phần diễn giải lý do |
| Test mới `test_agent_digest_sync.py` (đầu ra #8) có thể false-positive nếu 1 trong 8 file agent có định dạng số khác nhau (chữ số vs chữ) | Thấp | Viết task với bước red→green: cố ý gõ sai 1 số lúc viết test để xác nhận test bắt được lệch trước khi tick pass |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Đầu ra #1, #2 (dedupe git status/turn_rows) có test riêng và pass | `cd tests && python3 -m unittest discover -v` | 0 fail, gồm 2 test mới |
| Q2 | Đầu ra #3, #4, #5, #7, #9, #10, #13, #16 (sửa nội dung skill/doc) đúng nội dung | `grep`/đọc lại theo cột "Đo xong bằng" của từng dòng §2 tương ứng | Mọi grep trả đúng kỳ vọng, đọc tay xác nhận đủ nội dung |
| Q3 | Đầu ra #6, #14 (tách file) không phá luồng quick lane / mode external | Chạy tay 1 lượt `tdq_state.py init <slug-test> quick` rồi `next`, đối chiếu nội dung Phần A/C `tdq-intake/SKILL.md` vẫn đủ | Không thiếu bước nào so với trước khi tách |
| Q4 | Đầu ra #8 (test lock ngưỡng 1.500) tự bắt được lệch số | `python3 -m unittest test_agent_digest_sync -v` sau khi cố ý sửa sai 1 file rồi sửa lại đúng | FAIL khi lệch, PASS khi khớp |
| Q5 | Đầu ra #11 (nén skill_dump) giảm dung lượng, không mất khối hợp đồng | Test mới so sánh output có đủ 5 trường Dùng/Nạp/Để/Ra/Kiểm + giảm byte so với bản gốc | PASS + có số byte trước/sau trong log test |
| Q6 | Đầu ra #12 (dedupe prompt_context) hoạt động đúng 2 lượt gọi liên tiếp | Test mới gọi hook 2 lần cùng state | Lượt 2 ngắn gọn hơn/khác lượt 1 đúng quy tắc |
| Q7 | Đầu ra #15 (kịch bản đo) là quy trình chạy được thật | Đọc lại + thử áp dụng 1 bước mẫu trong file (không cần chạy hết kịch bản) | Không có bước mơ hồ/thiếu lệnh cụ thể |
| Q8 | Toàn bộ file đã sửa/tạo qua lint | `python3 scripts/doc_lint.py <toàn bộ file .md đã đổi>` | exit 0 |
| Q9 | Không phá hook đang chạy — QC độc lập | Agent `tdq-qc-tester` chạy lại full suite + probe hook `bash_gate.py`/`prompt_context.py` bằng input mẫu | PASS, không phát hiện lệch so với báo cáo tự kiểm |
| Q10 | `graphify` rebuild sau khi đổi code | `graphify extract . --code-only` | exit 0, mtime mới hơn lúc bắt đầu implement |

DoD: 16/16 đầu ra ở §2 đạt điều kiện đo tương ứng · full test suite 0 fail · `doc_lint.py`
exit 0 trên mọi file `.md` đã đổi · `tdq-qc-tester` xác nhận PASS độc lập · `graphify`
exit 0.

## 7. Câu hỏi còn mở

(rỗng — 6 câu hỏi ở phase analyze đã có đủ trả lời, xem `questions/2026-08-05-toi-uu-p0-p1-workflow.md`)
