# KNOWLEDGE — Brainstorm + spec triển khai P0+P1 tối ưu workflow & user-level Claude Code

Nguồn: `docs/tdq/knowledge/2026-08-05-audit-toi-uu-workflow.md` mục 9 (19 đề xuất P0+P1
đã chốt triển khai, P2 KHÔNG làm round này).

## Năng lực dùng được

| Skill/công cụ | Phán quyết | Lý do |
|---|---|---|
| `tdq-conventions`/`tdq-intake`/`tdq-spec`/`tdq-plan`/`tdq-build` | DÙNG | Khung vận hành bắt buộc của chính request này |
| `graphify` | DÙNG | Rebuild graph cuối turn có đổi code (luật CLAUDE.md) |
| `claude-md-improver` | PHÂN VÂN → DÙNG | Có thể chạm `portable/claude-md/CLAUDE.md` nếu P1 nào cần sửa thêm dòng khác ngoài dòng 41 đã sửa vòng trước |
| Explore agent (built-in) | DÙNG | Đã dùng ở bước đọc code — P1-9 tự đề xuất chuẩn hoá đúng việc này |
| `tavily-*` (mọi biến thể) | KHÔNG DÙNG round này | 19 đề xuất là kỹ thuật nội bộ (đọc code, sửa script/skill), không có ẩn số bên ngoài cần tra cứu web — nghiên cứu external caching/hook/context đã có đủ ở audit vòng 3 (research/2026-08-05-audit-toi-uu-workflow.md, 12 finding, 4 truy vấn) |
| `hookify` (conversation-analyzer, tạo hook mới) | KHÔNG DÙNG | Round này SỬA script hook có sẵn (`bash_gate.py`, `stop_gate.py`, `prompt_context.py`) trực tiếp bằng Edit, không tạo hook mới qua `/hookify` |
| `remember` | KHÔNG DÙNG | Quản lý qua `docs/workinglog/` + TDQ state, không dùng `.remember/` cho việc này |
| `skill-creator`, `plugin-dev:*` | KHÔNG DÙNG | Không tạo skill/plugin mới, chỉ sửa nội dung skill hiện có bằng Edit thường |
| `frontend-design`, `playground`, `mcp-server-dev:*` | KHÔNG DÙNG | Không liên quan (không có UI/MCP server mới) |

## Rà soát code chi tiết (19 đề xuất, qua Explore agent)

### P0 — vị trí + cách sửa đã xác định rõ, không còn mơ hồ

- **P0-2** `scripts/tdq_state.py:367 turn_snapshot()` — gọi `repo_status_digest()` (dòng
  313→324) và `repo_status_paths()` (dòng 348→354) chạy trùng `git status --porcelain`.
  Sửa: 2 hàm nhận tham số `status=None`, `turn_snapshot()` chạy `_git status` 1 lần rồi
  truyền xuống.
- **P0-3** `hooks/scripts/bash_gate.py` (`_latest_signal`) + `hooks/scripts/_common.py:79-86`
  (`turn_rows()`) — bị gọi lại nhiều lần trong 1 lần `main()` qua `_check_signal_mismatch`
  (2 lần) và `already_reminded()` (3 lần). Sửa: đọc `turn_rows()` đúng 1 lần đầu `main()`,
  truyền xuống qua tham số `rows=None`.
- **P0-4** mâu thuẫn thật: `quick-lane.md:46-48` cho user "đòi" override external dù có
  task `(mcp)` (soft); `tdq-build/SKILL.md:60` giả định đã bị chặn cứng từ lúc duyệt
  (hard). Khuyến nghị: chốt **hard-block** — engine ngoài vốn không gọi được MCP tool,
  cho phép "đòi" chỉ tạo ảo giác lựa chọn mà không chạy nổi.
- **P0-5** không mâu thuẫn nội dung nhưng có 2 bản: định nghĩa đầy đủ ở
  `reminder-codes.md:29-45`, bản rút gọn không link ở `tdq-conventions/SKILL.md:69-73`.
  Sửa: thêm link từ §6 trỏ về reminder-codes.md thay vì diễn giải lại.
- **P0-6** `tdq-build/SKILL.md:105-113` "Đóng worktree" — 3 lệnh git độc lập (dọn
  AGENTS.md, kiểm commit lạ, diff-check) gộp `&&` được, khớp luật gộp Bash đã có ở
  `tdq-conventions/SKILL.md:104-105`.

### P1 — đã xác định rõ (không cần hỏi thêm)

- **P1-5** `scripts/external_task.py:580-608 skill_dump()` — in nguyên văn SKILL.md +
  TOÀN BỘ `references/*.md` (rộng hơn audit mô tả). Ví dụ `tdq-build` = 392 dòng/21.960
  byte mỗi lần dump, dù Claude đã đọc skill này lúc build. Sửa: chỉ chép khối hợp đồng
  máy-đọc (Dùng/Nạp/Để/Ra/Kiểm) + lệnh CLI, bỏ phần diễn giải dài.
- **P1-6/P1-7** hook thật = `hooks/scripts/prompt_context.py`. Thực tế KHÁC audit: dòng
  82+84-116 KHÔNG dedupe gì cả — không phải "chỉ dedupe trong 1 turn". Cơ chế
  `already_reminded()` của `_common.py` không áp dụng cho hook này, vì hook này chỉ
  chạy 1 lần/turn nên khái niệm "trong 1 turn" không có ý nghĩa ở đây. In lại y hệt mỗi
  turn chờ duyệt. Sửa: lưu digest nội dung đã in (không dùng turn log vì bị xoá đầu mỗi
  turn), so khớp turn sau, rút gọn nếu trùng.
- **P1-8, P1-9** — **ĐÃ LÀM RỒI, audit ghi sai/lỗi thời.** `tdq-conventions/SKILL.md:110-113`
  (§10, thêm ở vòng 2, commit `b41225f`) đã có đủ. Cấm `cat`/`grep -A/-B` khi `-c/-l` đủ
  (P1-8) VÀ bắt buộc giao agent riêng khi đọc ≥4 file (P1-9, đúng ngưỡng audit đề xuất).
  **Loại khỏi phạm vi spec round này** — chỉ cần đính chính trong report.
- **P1-10** xác nhận đúng: chưa có khuyến nghị `/clear` ở đâu — đề xuất mới hoàn toàn.
- **P1-11** `tdq-build/SKILL.md` = 150 dòng; mục "Nhánh external" chiếm 62 dòng (>1/3),
  chỉ dùng khi `implement_mode=external`. Tách ra `references/external-build.md`, nạp
  đúng lúc cần (giống cách `report-template.md` đang được tham chiếu) — giảm ~41% dung
  lượng nạp cứng cho mode main/subagent.
- **P1-13** `tdq-build/references/qc.md:7,37` chỉ hướng dẫn cắt gọn nội dung SẼ GHI vào
  file qc — không hướng dẫn cách CHẠY test để tránh log dài vào chat. Sửa: thêm câu
  dùng cờ tóm tắt (`-q`/dot reporter) hoặc redirect + `tail`/`grep` phần fail.

### P1 — cần user quyết định hướng (ảnh hưởng effort/rủi ro thật, xem mục Câu hỏi)

- **P1-1** Kích thước xác nhận đúng audit: `tdq-conventions/SKILL.md` 120 dòng/7.313
  byte + `tdq-intake/SKILL.md` 117 dòng/7.989 byte ≈ 15,3KB. `tdq-intake/SKILL.md`
  Phần B (dòng 43-90, tự ghi "chỉ lane full") tách được rõ ràng cho quick lane.
  `tdq-conventions/SKILL.md` KHÔNG có ranh giới quick/full rõ để tách an toàn.
- **P1-2** Nguồn thật: khuôn interview ổn (đã quy về 1 nguồn, chỉ `lane-decision.md:27-33`
  tự định nghĩa khuôn riêng dù đáng lẽ phải theo interview.md — đây là BUG thật, không
  chỉ trùng lặp). Cấm prefix AI + "chỉ sửa state qua CLI" đã ổn (1 nguồn + enforce bằng
  code). Ngưỡng digest ≤1.500 ký tự hardcode ở **8 file** riêng biệt (7 agent + 1 skill),
  không phải 1 nguồn — các file agent là system-prompt độc lập, không tự "nạp" file khác.
- **P1-3** `stop_gate.py:76-86 _repo_changed()` dùng `repo_status_digest(cwd)` = toàn bộ
  working tree tại `cwd`, không phân biệt theo turn/process. Rủi ro thật chỉ xảy ra khi
  2 phiên Claude Code CÙNG chạy trên 1 worktree chính (worktree external riêng thì không
  bị ảnh hưởng vì `cwd` khác nhau).
- **P1-4** `tdq-build/SKILL.md:16-21` đã có ví dụ cụ thể (worktree thiếu nền, dependency,
  conflict) nhưng ranh giới "khó đảo ngược"/"phá huỷ" vẫn trừu tượng với case ngoài build
  thường (đổi schema DB, xoá data, đổi API contract công khai).
- **P1-12** `scripts/token_audit.py` không có cơ chế kịch bản chuẩn hoá — chỉ đọc
  transcript thật đã có sẵn (`--transcript-dir`), không tự tạo kịch bản. Đo chuẩn hoá
  cần 2 session sạch thực hiện đúng cùng thao tác trước/sau — không tự động hoá được
  trong 1 lần chạy script.

## Đối chiếu Q3 (mọi mục audit đã có mặt)
19/19 đề xuất P0+P1 đã rà soát code thật ở trên; 2 mục (P1-8, P1-9) phát hiện đã làm
xong ở vòng 2 — sẽ loại khỏi task list spec, ghi rõ lý do trong report để không mất dấu.

## Quyết định (sau interview, `docs/tdq/questions/2026-08-05-toi-uu-p0-p1-workflow.md`)

Phạm vi cuối = 5 P0 (P0-1 đã làm xong vòng trước, loại khỏi spec) + 11 P1 (loại P1-8,
P1-9 đã làm xong) = **16 đề xuất** đưa vào spec/plan round này.

- **P0-4**: chốt hard-block — sửa `quick-lane.md` bỏ câu cho user override, khớp giả
  định hard-block đã có ở `tdq-build/SKILL.md:60`.
- **P1-1**: chỉ tách `tdq-intake/SKILL.md` (Phần B "chỉ lane full", dòng 43-90) ra
  reference riêng, quick lane không nạp. `tdq-conventions/SKILL.md` giữ nguyên.
- **P1-2**: sửa bug `lane-decision.md:27-33` — dùng đúng khuôn `interview.md` thay vì
  tự định nghĩa riêng. Thêm 1 test mới canh khớp số ngưỡng 1.500 ký tự giữa 8 file
  agent và skill nguồn (kiểu `test_portable_sync.py`), KHÔNG đổi cơ chế nạp của agent.
- **P1-3**: chỉ thêm ghi chú rủi ro (2 phiên cùng chạy 1 worktree chính có thể tính oan
  "đã đổi repo") vào `reminder-codes.md`, không đổi code `stop_gate.py`.
- **P1-4**: thêm 3 ví dụ cụ thể (đổi schema DB, xoá data, đổi API contract công khai)
  vào nhóm "cần dừng hỏi" ở Luật cứng `tdq-build/SKILL.md`.
- **P1-12**: chỉ thiết kế kịch bản đo — danh sách thao tác cố định + hướng dẫn trỏ
  `token_audit.py --transcript-dir` vào 2 session before/after. KHÔNG tự chạy đo thật
  round này; ghi rõ trong spec đây là tài liệu/quy trình, chưa phải số đo.
- Các mục còn lại (P0-2, P0-3, P0-5, P0-6, P1-5, P1-6/P1-7, P1-10, P1-11, P1-13) giữ
  đúng hướng sửa đã xác định ở mục "Rà soát code chi tiết" — không có phương án rẽ
  nhánh cần hỏi.

## Lộ trình

| Bước/phase | CÓ/BỎ | Vì sao |
|---|---|---|
| Phân tích (đã xong) | CÓ | Đã đọc code qua Explore agent + interview 6 câu — hết chỗ mơ hồ |
| Research web (tavily) | BỎ | Việc kỹ thuật nội bộ, không có ẩn số bên ngoài; research external đã đủ ở audit vòng 3 |
| Spec | CÓ | Bắt buộc theo khung TDQ, phạm vi 16 đề xuất cần đầu ra đo đếm rõ |
| Plan | CÓ | 16 đề xuất chạm nhiều file độc lập theo cụm (script/hook, skill, test) — hợp chia subagent theo phase, nhưng để user chốt mode lúc duyệt plan |
| QC độc lập bằng agent (`tdq-qc-tester`) | PHÂN VÂN → CÓ | Chạm cả hook lõi (`bash_gate.py`, `stop_gate.py`) — nên có 1 lượt kiểm độc lập ngoài self-check |
| Review sâu bằng agent (`tdq-reviewer`) | BỎ (mặc định) | Chỉ gọi nếu user yêu cầu — đúng luật tdq-spec/tdq-plan |
| Implement → report | CÓ | Khung bất biến |
