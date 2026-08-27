# BRIEF — Portable TDQ workflow cho Antigravity (user-level, thư mục `antigravity_portable/`)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay bây giờ tôi muốn mở request yêu cầu bạn phân tích và tạo một portable skill workflow
> cho antigravity ở user-level output ở trong folder antigravity_portable và người dùng chỉ
> cần coppy all nội dung trong folder đó vào antigravity là antigravity có thể nhận ngay,
> yêu cầu phair có đầy đủ behavior và đầy đủ instruction để đảm bảo antigravity không skip
> gate hoặc mấy behavior của tdq-workflow

Đọc lần đầu:
- **Mục tiêu:** sinh một bundle portable riêng cho Antigravity (agy), đặt ở
  `antigravity_portable/` tại root repo, output ở mức **user-level** (tức đích copy là
  `~/.gemini/antigravity-cli/skills/` — global, không phải per-workspace `.agents/skills/`)
  — copy nguyên thư mục là dùng được ngay, không cần chỉnh sửa gì thêm.
- **Phạm vi đoán:** tái dùng nội dung nguồn `skills/tdq-*`, `agents/`, `scripts/` giống cách
  `build_portable.py` đã sinh `portable_claude/` và `portable_codex/`, nhưng đóng gói theo
  đúng cách Antigravity nạp cấu hình (không phải Claude Code, không phải Codex CLI).
- **Điểm chưa rõ (cần chốt ở B):**
  1. Antigravity KHÔNG có hook system (không có PreToolUse/Stop gate như Claude Code) —
     "đảm bảo không skip gate" phải đạt bằng cách nào khi thiếu tầng enforce tự động?
  2. `antigravity_portable/` là thư mục build-sinh-ra (giống `portable_claude/`,
     `portable_codex/`) hay build thủ công một lần? Có cần thêm target thứ 3 vào
     `build_portable.py`, hay tận dụng `AGENTS.md` + `workflow/` đã có sẵn trong
     `portable_codex/` (comment trong `build_portable.py` ghi rõ phần đó vốn *đã* thiết kế
     làm fallback cho Antigravity)?
  3. "user-level" — xác nhận đích là thư mục global của agy
     (`~/.gemini/antigravity-cli/skills/`), khác `.agents/skills/` per-workspace.
  4. Có cần mang theo `scripts/` (tdq_state.py, tdq_finish.py, …) để lệnh trong skill chạy
     được, và Antigravity có tự nạp `AGENTS.md`/`GEMINI.md` ở đâu khi dùng skill global?

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-08-27: 9 skill trên đĩa (lọc theo từ khoá), cộng skill
built-in trong context (không skill nào áp dụng — việc này là sinh file/thư mục nội bộ
project, không cần dataviz/artifact/design/…).

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | phase đang chạy |
| tdq-lsp-setup | plugin:tdq-workflow | NỀN | đã chạy bậc 6/6 ở bước 1b |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật nạp chung mọi skill |
| tdq-diagram | plugin:tdq-workflow | NỀN | bắt buộc trước plan ở lane full |
| tdq-spec | plugin:tdq-workflow | NỀN | phase kế tiếp |
| tdq-plan | plugin:tdq-workflow | NỀN | phase sau spec |
| tdq-build | plugin:tdq-workflow | NỀN | phase implement |
| tdq-check-status / tdq-status | plugin:tdq-workflow | NỀN | không dùng trong request này, sẵn có nếu ngắt phiên |
| Đã xét ~223 skill khác (built-in + plugin khác) | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Khảo sát hiện trạng (đọc code + doc trước khi research ngoài)

- Đã có **2 bundle portable sinh máy** từ 1 nguồn (`skills/`, `hooks/`, `agents/`, `scripts/`)
  qua `scripts/build_portable.py`: `portable_claude/` (Claude Code, dùng hook thật) và
  `portable_codex/` (Codex CLI native layer `.agents/skills/` + `.codex/hooks.json`, CỘNG
  `AGENTS.md` + `workflow/NN-*.md` làm **fallback thuần markdown cho harness khác, trong đó
  comment trong code gọi đích danh "Antigravity…"** — tức Antigravity hiện đang bị gộp chung
  vào diện "không có hook", KHÔNG có bundle riêng.
- `portable_codex/` đặt mọi path **tương đối** (`scripts/`, `hooks/`) vì giả định bundle nằm
  NGAY TRONG project (cùng cấp `.agents/skills/`) — mô hình này ăn khớp target
  "per-workspace" nhưng KHÔNG ăn khớp "user-level" (global) mà request này đòi hỏi: một thư
  mục global (`~/.gemini/...`) không nằm cạnh `scripts/`/`hooks/` của TỪNG project, nên mọi
  lệnh trong SKILL.md phải trỏ bằng đường dẫn tuyệt đối cố định dưới `$HOME`, không phải
  đường dẫn tương đối như 2 bundle cũ.
- `docs/tdq/research/2026-08-03-skill-vao-goi-external.md` (nghiên cứu cũ, trước khi có
  research mới ở dưới): agy tự parse `AGENTS.md`/`GEMINI.md` ở workspace root; có skill
  native `.agents/skills/` (project) và `~/.gemini/antigravity-cli/skills/` (global) — nhưng
  bài đó viết TRƯỚC khi agy có hook, nên phần "agy không có hook" trong đó đã lỗi thời (xem
  research mới).

### Research mới (sub-agent, `docs/tdq/research/2026-08-27-1112-antigravity-portable-skill.md`)

Phát hiện quan trọng nhất, LÀM THAY ĐỔI kiến trúc so với giả định ban đầu trong `## Nguyên
văn`: **agy hiện ĐÃ có hook system thật** (`PreToolUse`/`PostToolUse`/`PreInvocation`/
`PostInvocation`/`Stop`), `PreToolUse` trả `decision: deny` chặn cứng tool call, `Stop` trả
`decision: continue` ép loop không dừng sớm — đúng cơ chế "cổng chặn kết lượt" TDQ đang dùng
cho Claude Code, port được sang agy. Cộng thêm Permissions Engine riêng
(`settings.json`, allow/deny/ask theo `action(target)`) làm lớp phòng thủ thứ 2.

Rủi ro lớn đi kèm: **đường dẫn cấu hình global của agy KHÔNG ổn định** giữa các bản/tài liệu
2026 — skill global có ít nhất 3-4 path ứng viên khác nhau tuỳ nguồn
(`~/.gemini/antigravity-cli/skills/`, `~/.gemini/antigravity/skills/`, `~/.gemini/skills/`,
`~/.gemini/config/skills/<plugin>/`), hook/MCP cũng vậy (2 path MCP song song, 1 path hook
mới `~/.gemini/config/` khác hẳn path skill). Workflow (`/workflow-name`) CHỈ là prompt
injection tuần tự, không ép buộc kỹ thuật, có bug xác nhận model tự bỏ qua — không dùng làm
gate chính.

### Đọc code hook hiện có (trước khi thiết kế hook cho agy)

Đọc `hooks/hooks.json` + `hooks/scripts/*.py` (Claude Code, 5 hook): quan trọng nhất —
**bash_gate.py và edit_gate.py KHÔNG BAO GIỜ chặn cứng**, chỉ "observe + remind"
(`additionalContext`, không có `decision: deny`) — đúng như `docs/notes/user-level-install.md`
đã ghi "Hook không chặn tool, chỉ nhắc". Điểm chặn CỨNG duy nhất là **stop_gate.py** (event
`Stop`), và nó chặn dựa trên **hiệu ứng thật trên đĩa** (so sánh snapshot đầu turn với cuối
turn qua `docs/tdq/.tdq-turn.jsonl` + git status), KHÔNG tin dòng echo model tự in. 3 block
point: `TDQ:LOG` (đổi repo mà chưa ghi working log), `TDQ:TICK` (sửa code mà checkbox plan
không nhúc nhích), `TDQ:UNFINISHED` (còn task mở mà phase vẫn `implement`) — có ceiling
`MAX_STREAK=3` để không kẹt cứng session khi thật sự bế tắc.

→ Hệ quả thiết kế cho agy: có 2 lựa chọn không tương đương nhau, cần user chốt (xem vòng hỏi
tiếp theo) — (a) giữ triết lý "remind-only + block cứng chỉ ở Stop" y hệt bản Claude Code cho
nhất quán hành vi giữa 2 harness, hay (b) tận dụng luôn khả năng `PreToolUse` → `deny` thật
của agy để chặn cứng NGAY LÚC gõ lệnh (git naming cấm, ghi state.json qua shell) thay vì chỉ
nhắc — mạnh hơn nhưng có rủi ro false-positive chặn nhầm lệnh hợp lệ (regex trong
`bash_gate.py` vốn được viết cho triết lý "chỉ nhắc", chưa chắc đủ chính xác để dùng làm điều
kiện `deny`).

### Phạm vi đã chốt (vòng scope, turn user trả lời `1abc 2a 3b 4a`)

- Mặt CHỌN: A (gate cứng port hook `PreToolUse`/`Stop` thật + permissions engine lớp 2),
  B (cài trùng lặp mọi path ứng viên + bước tự-kiểm `/skills`/`/mcp`/`/permissions`),
  C (thêm target thứ 3 vào `build_portable.py`, tự sinh từ nguồn `skills/`, không build tay).
- Mặt LOẠI: D (bản tối giản "chỉ cần chạy được") — không chọn, vì user muốn cả gate cứng lẫn
  độ phủ path lẫn tự sinh, không chấp nhận rủi ro bỏ sót.
- Bối cảnh: (2a) chưa biết version agy cụ thể → bundle phải tự-kiểm lúc chạy, không hard-code
  1 path duy nhất; (3b) bundle sẽ dùng chung nhiều máy/đồng nghiệp → README phải rõ, né mọi
  giả định path máy-cụ-thể.
- Mức đầu tư suy ra: **đầy đủ** — vì dùng chung nhiều máy/team, đòi hỏi gate cứng thật (không
  chỉ nhắc), tự sinh để không lệch nguồn, và né path không ổn định của một sản phẩm đang đổi
  nhanh → QC phải có test mô phỏng JSON schema hook thật của agy (không chỉ đọc bằng mắt),
  không chỉ dựa lời hứa "chắc là đúng".

## Hỏi đáp

- Q (vòng scope, 2026-08-27 11:31): 4 câu — mặt bao quanh / version agy / phạm vi dùng /
  bổ sung. → A: `1abc 2a 3b 4a` (xem "Phạm vi đã chốt" ở trên).
- Q (vòng chi tiết, 2026-08-27 11:39): 5 câu — mức chặn PreToolUse / vị trí scripts-hooks cố
  định / phạm vi test / dọn portable_codex / bổ sung. → A: `1b 2a 3a 4a 5a`:
  1. **1b** — dùng `deny` thật của agy ngay ở `PreToolUse` cho 2 case rõ (tên branch cấm, ghi
     thẳng `state.json`), viết regex chặt hơn bản Claude Code (tránh false-positive) vì giờ
     có hậu quả thật (chặn hẳn, không chỉ nhắc).
  2. **2a** — scripts/hooks dùng chung đặt cố định tại `~/.gemini/antigravity-cli/tdq/`
     (scripts/ + hooks/); mọi bản cấu hình cài ở bất kỳ path ứng viên nào đều trỏ absolute
     path về đây.
  3. **3a** — unit test mô phỏng JSON schema stdin/stdout thật của agy (PreToolUse/Stop) cho
     từng hook script, cộng checklist smoke-test thủ công trong README.
  4. **4a** — sửa luôn `build_portable.py` (comment), `portable_codex/README.md`, `AGENTS.md`:
     bỏ Antigravity khỏi nhóm "harness fallback markdown thuần", vì giờ có bundle riêng.
  5. **5a** — không bổ sung, viết spec.

### Kiểm cổng

- Phạm vi cuối rõ chưa? RÕ — build `antigravity_portable/` (nội dung sẽ cài vào
  `~/.gemini/antigravity-cli/`), sinh bằng target thứ 3 của `build_portable.py`, gồm: skill
  (cài trùng lặp nhiều path ứng viên), hook thật (`PreToolUse` deny 2 case + `Stop` block y
  hệt logic `stop_gate.py`), permissions engine `settings.json` làm lớp 2, MCP config trùng
  2 path, scripts/hooks lõi cố định tại `~/.gemini/antigravity-cli/tdq/`, README hướng dẫn
  cài + tự-kiểm (`/skills`, `/mcp`, `/permissions`) + checklist smoke-test thủ công. Đồng
  thời dọn 3 file cũ (`build_portable.py` comment, `portable_codex/README.md`, `AGENTS.md`)
  bỏ Antigravity khỏi nhóm fallback cũ.
- Cần cài/tải/model gì thêm không? KHÔNG — user tự có sẵn agy; bundle chỉ dùng Python
  stdlib (nhất quán quy ước hiện tại, không thêm dependency).
- Phạm vi QC/test đã rõ chưa? RÕ — unit test mô phỏng schema agy cho từng hook script
  (PreToolUse/Stop) + test cấu trúc target mới của `build_portable.py` (giống test đã có cho
  2 target kia) + checklist smoke-test thủ công trong README (không tự động hoá được vì cần
  agy thật).

### Lộ trình

| Bước/phase | CÓ/BỎ | Vì sao |
|---|---|---|
| Phân tích (đã xong) | CÓ | brief này |
| Spec | CÓ | chốt kiến trúc: cấu trúc `antigravity_portable/`, danh sách path cài trùng lặp, schema hook agy, nội dung README |
| Sơ đồ giải thuật (diagram) | CÓ | bắt buộc lane full, sau spec trước plan — 1 sơ đồ luồng cho toàn bộ "cài đặt + hook enforcement + tự-kiểm path" của bundle agy |
| Plan | CÓ | tách task theo: build_portable.py target mới, hook script mới (deny 2 case + Stop y hệt logic), skill content (copy nguồn `skills/tdq-*`), README + checklist, dọn 3 file cũ, test |
| Implement | CÓ | build_portable.py sinh `antigravity_portable/`, viết hook script, README |
| QC | CÓ | test mô phỏng schema agy + test cấu trúc bundle + review checklist smoke-test |
| Report | CÓ | báo cáo kết quả + giới hạn còn lại (rủi ro path không ổn định agy, cần user tự smoke-test) |

Không bỏ bước nào — mọi bước đều cần thiết cho một bundle sinh máy có gate thật.
