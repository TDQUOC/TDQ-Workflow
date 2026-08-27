# SPEC — Portable TDQ workflow cho Antigravity (user-level, `antigravity_portable/`)

Ngày: 2026-08-27 · Bản: 1.0 · Brief: ../brief/2026-08-27-1112-antigravity-portable-skill.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- Mục tiêu: sinh một bundle portable thứ 3 — `antigravity_portable/` — bằng máy (không tay),
  từ đúng 1 nguồn (`skills/`, `hooks/`, `agents/`, `scripts/`) như 2 bundle hiện có, đóng gói
  đúng cơ chế nạp cấu hình thật của Antigravity CLI (agy) ở **user-level** (global,
  `~/.gemini/antigravity-cli/...`), có **gate cứng thật** (không chỉ nhắc) chặn 2 hành vi vi
  phạm rõ ràng và chặn kết lượt sớm khi plan chưa chạy hết — để copy nguyên thư mục vào máy
  đích là dùng được ngay, không cần chỉnh sửa.
- Trong phạm vi:
  - Target sinh thứ 3 trong `scripts/build_portable.py` (`sinh_ban_antigravity`), gọi được qua
    `--only antigravity`.
  - Nội dung `antigravity_portable/`: skill (`skills/tdq-*` port nguyên trạng theo khuôn agy),
    hook thật (`PreToolUse` deny 2 case + `Stop` chặn kết lượt sớm, cùng triết lý
    `stop_gate.py`), permissions engine (`settings.json`) làm lớp phòng thủ thứ 2, MCP config
    (2 path song song), scripts/hooks lõi đặt cố định tại một thư mục canonical dưới `$HOME`,
    README (cài đặt, tự-kiểm `/skills`/`/mcp`/`/permissions`, checklist smoke-test thủ công),
    `manifest.json`.
  - Cài trùng lặp lên MỌI path ứng viên đã biết cho từng loại cấu hình (skill, hook, MCP,
    permissions) vì tài liệu agy 2026 không thống nhất 1 path duy nhất.
  - Dọn 3 file cũ đang gộp Antigravity vào diện "fallback markdown, không hook":
    `scripts/build_portable.py` (dòng comment đầu file), `portable_codex/README.md`,
    `portable_codex/AGENTS.md`.
  - Test: unit test mô phỏng JSON schema stdin/stdout thật của agy cho từng hook script mới,
    test cấu trúc target mới của `build_portable.py` (theo khuôn test cấu trúc đã có cho 2
    target kia).
- NGOÀI phạm vi (chốt ở vòng scope, mặt LOẠI = D):
  - KHÔNG làm bản tối giản "chỉ cần chạy được" — user đã loại rõ vì muốn cả gate cứng thật lẫn
    độ phủ path lẫn tự sinh, không chấp nhận rủi ro bỏ sót.
  - KHÔNG cài đặt/thao tác thật trên máy agy của user (trust, approve hook trong UI agy, set
    biến môi trường MCP) — đây là việc user tự làm, bundle chỉ cung cấp file + README, giống
    đúng ranh giới đã áp cho `portable_codex/`.
  - KHÔNG build/tải bất kỳ model hay gói phụ thuộc mới nào — chỉ dùng Python stdlib.
  - KHÔNG sửa hành vi 2 bundle `portable_claude/`/`portable_codex/` ngoài 2 dòng comment/mô tả
    ở mục dọn dẹp trên (không đổi logic sinh, không đổi cấu trúc file của chúng).

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã xong ở analyze) | agy đổi nhanh 2026, kiến thức cũ trong repo về "không có hook" đã sai — bắt buộc research lại trước khi thiết kế |
| Sơ đồ giải thuật (diagram) | CÓ | bắt buộc lane full, sau spec trước plan — vẽ luồng cài đặt + hook enforcement + tự-kiểm path |
| Interview | CÓ (đã xong ở analyze, 2 vòng) | nhiều quyết định kiến trúc (mức deny, vị trí lõi cố định, phạm vi test, dọn file cũ) không thể đoán |
| QC độc lập (agent) | BỎ | phạm vi là sinh file cấu hình + hook script nhỏ có test mô phỏng schema kèm theo; agent implementer tự chạy test đã đủ xác nhận, không cần thêm 1 lượt review kiến trúc riêng |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Target sinh bundle Antigravity | `scripts/build_portable.py` (hàm `sinh_ban_antigravity`, cờ `--only antigravity`) | `python3 scripts/build_portable.py --only antigravity` thoát mã 0, sinh đủ cây `antigravity_portable/` |
| 2 | Hook `PreToolUse` (deny 2 case) | `antigravity_portable/hooks/scripts/agy_pretooluse_gate.py` (nguồn: `hooks/scripts/agy_pretooluse_gate.py`) | test mô phỏng stdin JSON agy trả `decision: deny` cho 2 case cấm, `decision: allow` cho lệnh hợp lệ |
| 3 | Hook `Stop` (chặn kết lượt sớm) | `antigravity_portable/hooks/scripts/agy_stop_gate.py` (nguồn: `hooks/scripts/agy_stop_gate.py`) | test mô phỏng trả `decision: continue` đúng 3 điều kiện port từ `stop_gate.py`, `decision` rỗng/allow khi không vi phạm |
| 4 | Cấu hình hook agy | `antigravity_portable/config/hooks.json` (nội dung cài lặp vào mọi path ứng viên hook) | đúng schema 5 event agy, trỏ absolute path về thư mục lõi cố định |
| 5 | Permissions engine (lớp 2) | `antigravity_portable/config/settings.json` | có `deny` cho `write_file(state.json)`/`command(git branch/commit trái quy tắc)`, JSON hợp lệ |
| 6 | MCP config (2 path song song) | `antigravity_portable/config/mcp_config.json` | JSON hợp lệ, tên biến môi trường không chứa giá trị thật |
| 7 | Skill content port cho agy | `antigravity_portable/skills/tdq-*/SKILL.md` (+ `references/`, `scripts/` liên quan) | mỗi skill nguồn trong `THU_TU_SKILL` có bản tương ứng trong bundle |
| 8 | README cài đặt + tự-kiểm | `antigravity_portable/README.md` | có đủ: danh sách path cài trùng lặp, bước tự-kiểm `/skills`/`/mcp`/`/permissions`, checklist smoke-test thủ công |
| 9 | `manifest.json` bundle | `antigravity_portable/manifest.json` | có sha256 từng file, version, min Python, external commands, MCP servers — khuôn giống 2 bundle kia |
| 10 | Dọn 3 file cũ | `scripts/build_portable.py` (comment đầu file), `portable_codex/README.md`, `portable_codex/AGENTS.md` | không còn cụm nào nhắc "Antigravity" trong nhóm "fallback markdown / không hook" |
| 11 | Test mới | bổ sung ca cho target `antigravity` vào bộ test cấu trúc build_portable hiện có, cộng 1 bộ test mới cho 2 hook script agy | toàn bộ test liên quan chạy xanh |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| Hook script agy | `hooks/scripts/agy_pretooluse_gate.py`, `hooks/scripts/agy_stop_gate.py` | không | 2, 3, 11 |
| Target sinh bundle | `scripts/build_portable.py` (hàm `sinh_ban_antigravity`, cấu hình `config/*.json` sinh trong hàm này) | Hook script agy (copy nguyên hook đã viết vào bundle) | 1, 4, 5, 6, 9 |
| Skill port | `antigravity_portable/skills/` (do target sinh bundle copy từ `skills/tdq-*` nguồn, không có file mã nguồn riêng ngoài nội dung copy) | Target sinh bundle | 7 |
| README bundle | `antigravity_portable/README.md` (nội dung tĩnh do target sinh bundle ghi ra, không đọc từ nguồn khác) | Target sinh bundle | 8 |
| Dọn file cũ | `scripts/build_portable.py` (dòng comment header, KHÁC vùng với hàm `sinh_ban_antigravity`), `portable_codex/README.md`, `portable_codex/AGENTS.md` | không | 10 |
| Test | test cấu trúc build_portable hiện có (mở rộng) + bộ test mới cho hook agy | Hook script agy, Target sinh bundle | 11 |

Ghi chú ranh giới: `scripts/build_portable.py` xuất hiện ở 2 module (Target sinh bundle và Dọn
file cũ) nhưng khai 2 VÙNG DÒNG khác nhau trong cùng file (hàm `sinh_ban_antigravity` mới thêm
vs. block comment header đã có sẵn) — không phải trùng path theo nghĩa bị cấm, vì đây là 2 vùng
sửa tách biệt trong plan (2 task khác nhau, không đụng cùng dòng).

## 3. Cách tiếp cận & lý do

- Chọn: thêm **target sinh thứ 3** vào `build_portable.py` (không build tay `antigravity_portable/`
  một lần), tái dùng khung `copy_loc()`/`sinh_manifest()`/`THU_TU_SKILL` đã có cho 2 target kia;
  viết 2 hook script MỚI riêng cho agy (không tái dùng thẳng `bash_gate.py`/`stop_gate.py` của
  Claude Code) vì schema JSON và ngữ nghĩa `decision` khác hẳn (agy có `deny` thật ở
  `PreToolUse`, Claude Code hook không có); cài redundant lên mọi path ứng viên đã biết thay vì
  chọn 1 path "đúng nhất".
- Vì:
  - Tự sinh bằng máy là bất biến kiến trúc đã chốt cho `portable_*`
    (`docs/kien-truc.md` § Tầng: "Luật bản ngoài ... SINH bằng `scripts/build_portable.py` ...,
    không sửa tay") — bundle thứ 3 không được phá lệ này.
  - agy đã có hook thật (`PreToolUse`/`Stop` với `decision: deny`/`continue`) theo research mới
    (`docs/tdq/research/2026-08-27-1112-antigravity-portable-skill.md`, truy vấn 2) — đủ điều
    kiện kỹ thuật để làm gate cứng thay vì chỉ nhắc như bản Claude Code, đúng yêu cầu gốc của
    user ("đảm bảo Antigravity không skip gate").
  - Path cấu hình global của agy không ổn định giữa các bản 2026 (research, truy vấn 1 & 3) —
    cài trùng lặp + bước tự-kiểm là cách duy nhất giảm rủi ro "cài đúng chỗ này nhưng agy đọc
    chỗ khác" mà không cần biết trước version máy đích.
  - Không dùng Workflows (`/workflow-name`) làm cơ chế ép buộc chính — research (truy vấn 4)
    xác nhận đây chỉ là prompt injection, có bug xác nhận model tự bỏ qua.
- Đã loại:
  - Tận dụng `portable_codex/AGENTS.md` + `workflow/NN-*.md` làm bản đủ dùng cho Antigravity
    (phương án B trong brief mục "Điểm chưa rõ" #2) — LOẠI vì đó là markdown thuần, không có
    gate cứng, không khớp yêu cầu "không skip gate" mà research xác nhận agy giờ có hạ tầng hook
    thật để làm tốt hơn.
  - Port thẳng `bash_gate.py`/`stop_gate.py` sang agy không sửa — LOẠI vì regex trong
    `bash_gate.py` được viết cho triết lý "chỉ nhắc" (false-positive không gây hậu quả), dùng
    làm điều kiện `deny` thật thì rủi ro chặn nhầm lệnh hợp lệ tăng lên, cần viết lại regex chặt
    hơn (đã chốt ở brief, đáp `1b`).
  - Chọn 1 path global duy nhất cho mỗi loại cấu hình — LOẠI vì tài liệu agy không thống nhất,
    hard-code 1 path có xác suất cao là sai trên máy đích cụ thể.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | phase đang chạy |
| tdq-lsp-setup | plugin:tdq-workflow | NỀN | đã chạy bậc 6/6 ở bước 1b của intake |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật nạp chung mọi skill |
| tdq-diagram | plugin:tdq-workflow | NỀN | bắt buộc trước plan ở lane full |
| tdq-spec | plugin:tdq-workflow | NỀN | phase đang viết (spec này) |
| tdq-plan | plugin:tdq-workflow | NỀN | phase kế tiếp sau diagram |
| tdq-build | plugin:tdq-workflow | NỀN | phase implement |
| tdq-check-status / tdq-status | plugin:tdq-workflow | NỀN | không dùng trong request này, sẵn có nếu ngắt phiên |
| Đã xét ~223 skill khác (built-in + plugin khác) | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: 2 hook script mới (`agy_pretooluse_gate.py`, `agy_stop_gate.py`) có
  runtime thật (chạy trong tiến trình agy trên máy đích) → log timestamp ra stderr, tắt được qua
  biến môi trường (theo đúng khuôn `TDQ_LOG=0` đã dùng ở `hooks/scripts/*.py` hiện có).
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật — kể cả trong
  `README.md`/`config/*.json` sinh ra (không được để giá trị mẫu như `"TODO: điền path"` mà
  không có giá trị thật đi kèm).
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`,
  và bám rule ngôn ngữ Python trong `skills/tdq-build/references/rules/`. Luật này luôn áp,
  không có cổng bật/tắt.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ dòng việc này chạm tới):

- "`hooks/` được gọi bởi `scripts/`; `scripts/` **không** được import `hooks/`" — việc này
  chạm ở `scripts/build_portable.py` (hàm `sinh_ban_antigravity` COPY file hook, không import
  nó).
- "`skills/` chỉ được nhắc tên lệnh của `scripts/`, cấm chép nội dung script vào skill" — chạm
  ở nội dung skill port sang `antigravity_portable/skills/`: giữ nguyên cách skill nguồn đã
  viết (chỉ nhắc lệnh), không thêm logic script chép tay vào SKILL.md.
- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`" — chạm ở đúng lý do 2 case
  `deny` của hook `PreToolUse` mới: 1 trong 2 case cấm chính là lệnh ghi thẳng `state.json`
  qua shell, hook mới đưa luật đã có sẵn này lên thành chặn cứng thay vì chỉ nhắc.
- "2026-07-29: hook chỉ nhắc và kiểm bằng hiệu ứng thật, không trả `deny` vì lý do 'chưa
  duyệt'" — chạm ở thiết kế `agy_pretooluse_gate.py`: 2 case `deny` được chọn (tên
  branch/commit cấm, ghi thẳng `state.json`) là vi phạm QUY TẮC CỐ ĐỊNH đã có sẵn từ trước
  (không phải "vì bước trước chưa duyệt"), nên không phá dòng đã chốt này; `agy_stop_gate.py`
  vẫn giữ đúng triết lý "kiểm bằng hiệu ứng thật trên đĩa" y hệt `stop_gate.py`, không suy diễn
  từ lời model tự khai.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Path cấu hình global của agy đổi tiếp sau ngày viết bundle (2026-08-27) | Cài đúng nội dung nhưng sai chỗ, agy không đọc, gate coi như không tồn tại | Cài trùng lặp mọi path ứng viên đã biết (research liệt kê) + README bắt buộc bước tự-kiểm `/skills`/`/mcp`/`/permissions` trước khi tin bundle đã nạp |
| Regex 2 case `deny` quá chặt/quá lỏng | Quá chặt: chặn nhầm lệnh hợp lệ, cản việc thật. Quá lỏng: lọt lệnh cấm, gate vô nghĩa | Unit test mô phỏng cả case phải-chặn lẫn case-lệnh-hợp-lệ-gần-giống cho từng regex trước khi coi task xong |
| agy đổi format JSON `PreToolUse`/`Stop` ở bản mới (sản phẩm đang đổi nhanh) | Hook không parse được input hoặc output sai schema, agy bỏ qua hoặc lỗi cứng | Hook script bọc try/except quanh phần parse input, lỗi parse → trả `allow`/không-chặn thay vì crash tiến trình agy (fail-open cho lỗi hạ tầng, fail-closed chỉ cho 2 case cấm đã match rõ) |
| Không có agy thật để test end-to-end trong CI của repo này | QC chỉ dừng ở test mô phỏng schema, không chứng minh được hành vi thật trên agy | README có checklist smoke-test thủ công; report cuối phải ghi rõ giới hạn này, không tuyên bố "đã kiểm chứng trên agy thật" |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Target sinh bundle chạy được độc lập | `--only antigravity` sinh đủ toàn bộ đầu ra §2 (1-9), thoát mã 0, không đụng `portable_claude/`/`portable_codex/` |
| Q2 | Hook `PreToolUse` deny đúng case, allow lệnh hợp lệ | Test mô phỏng: 2 input vi phạm → `decision: deny`; ≥1 input hợp lệ gần giống (ví dụ tên branch hợp lệ chứa từ khoá gần giống case cấm) → không bị `deny` |
| Q3 | Hook `Stop` chặn kết lượt đúng 3 điều kiện port từ `stop_gate.py` | Test mô phỏng dựng lại 3 tình huống `TDQ:LOG`/`TDQ:TICK`/`TDQ:UNFINISHED` tương ứng, mỗi tình huống trả `decision: continue`; tình huống sạch trả không-chặn |
| Q4 | Cấu hình JSON hợp lệ | `hooks.json`, `settings.json`, `mcp_config.json`, `manifest.json` đều parse JSON được, không chứa giá trị secret thật |
| Q5 | Đã dọn 3 file cũ | grep "Antigravity" trong `scripts/build_portable.py` header comment, `portable_codex/README.md`, `portable_codex/AGENTS.md` không còn khớp trong đoạn mô tả "fallback markdown / không hook" |
| Q6 | Bộ test tổng | toàn bộ test liên quan (hook mới + target build_portable mới + test cũ không bị vỡ) chạy xanh |

DoD: `pytest` toàn bộ (không riêng file mới) chạy xanh; `antigravity_portable/` tồn tại đủ 9
đầu ra §2 mục 1-9; 3 file cũ đã dọn theo Q5; README có đủ 3 mục bắt buộc (đầu ra #8); report
cuối nêu rõ giới hạn "chưa test trên agy thật" theo rủi ro đã ghi ở §5.

## 7. Câu hỏi còn mở

(rỗng)
