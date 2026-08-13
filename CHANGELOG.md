# Changelog

Mới nhất trên cùng. Ngày theo múi giờ máy phát hành.

## 0.11.12 — 2026-08-13

Đổi nhãn "Năng lực" thành "Ước tính sẽ dùng skill" trong tóm tắt chế độ nhanh, cho thân
thiện người dùng.

- `skills/tdq-intake/SKILL.md`, `references/quick-lane.md`, `references/skill-inventory.md`:
  đổi nhãn dòng `Năng lực: <...>` → `Ước tính sẽ dùng skill: <...>` ở đúng 3 chỗ user-facing
  của chế độ nhanh. Không đụng heading `### Năng lực dùng được` ở brief/spec chuyên sâu.

## 0.11.11 — 2026-08-13

Bắt buộc dùng `tdq_finish.py` (thay Edit tay) và chạy trước đoạn chat cuối turn — sửa gốc
việc câu hỏi/tóm tắt TDQ bị chế độ focus của Claude Code gập ẩn.

- `skills/tdq-conventions/SKILL.md` §1 bước 4: thêm bắt buộc gọi `tdq_finish.py` (cấm
  Edit/Read rồi tự append tay working log). Lệnh đó phải là hành động cuối cùng của turn,
  chạy TRƯỚC đoạn chat kết thúc turn — không gọi thêm tool sau khi đã in đoạn đó.

## 0.11.10 — 2026-08-13

Gắn nhãn khuôn mẫu khi tóm tắt spec/plan trích lại, tránh nhầm là câu hỏi sống.

- `skills/tdq-spec/SKILL.md` bước 4, `skills/tdq-plan/SKILL.md` bước 5: khi đầu ra chính
  là một khuôn/mẫu văn bản và cần trích nguyên khối đó vào tóm tắt duyệt. Gắn nhãn "(khuôn
  mẫu — áp dụng cho các lần hỏi sau, không phải câu hỏi của turn này)" trước đoạn trích.

## 0.11.9 — 2026-08-13

Gọn UX câu hỏi chọn lane, gọi "pipeline" khi hiện với user.

- `skills/tdq-intake/SKILL.md` bước 2: bỏ yêu cầu in dòng `Cỡ:/Cần:` ra chat (giữ làm căn
  cứ nội bộ), đổi câu hỏi user sang "Bạn muốn chạy pipeline nào?".
- `skills/tdq-intake/references/lane-decision.md`: mục "Dòng tự nhận định" thành đánh giá
  nội bộ; "Khuôn câu hỏi" viết lại — bỏ Cỡ/Cần, dùng "pipeline", thêm khối giải thích
  ngắn nghĩa 2 pipeline. Không đổi `interview.md` hay thuật ngữ `lane` nội bộ.

## 0.11.8 — 2026-08-13

Lưu & nhúng ảnh đính kèm vào working log.

- `skills/tdq-conventions/SKILL.md` §6: thêm quy ước — turn có ảnh user gửi kèm + phải
  ghi working log → copy ảnh từ cache session sang `docs/workinglog/assets/<slug>/<n>.<ext>`
  (track git), chèn markdown `![...]` vào chuỗi `--log`. Không sửa `tdq_finish.py`.

## 0.11.7 — 2026-08-13

Bắt buộc rõ hơn việc in tóm tắt spec/plan trước dòng duyệt.

- `skills/tdq-spec/SKILL.md` bước 4, `skills/tdq-plan/SKILL.md` bước 5: thêm câu
  tự-kiểm ngay trước dòng `➤ Duyệt:` — buộc xác nhận tin nhắn CHỨA tóm tắt thật, không
  được thay bằng câu thông báo suông kiểu "đã ghi log, đang chờ duyệt".

## 0.11.6 — 2026-08-13

Thân thiện hơn với người dùng mới ở câu hỏi khuôn A/B/C và dòng duyệt.

- `skills/tdq-intake/references/interview.md`: khối hint cuối mỗi vòng hỏi đổi từ 1 câu
  chung chung sang 2 phần — nguyên tắc (gõ chữ cái hoặc câu tự nhiên) + 1 ví dụ trung tính.
- 3 dòng `➤ Duyệt:` (`tdq-spec`, `tdq-plan`, `tdq-intake` bước duyệt nhanh) thêm vế ngắn
  nói rõ duyệt xong dẫn tới bước gì tiếp theo (viết plan / build / implement ngay).

## 0.11.5 — 2026-08-13

Bịt 3 lỗ hổng tick checkbox ở chế độ chuyên sâu.

- `plan_tick_state` (`scripts/tdq_state.py`) trả thêm `doing_count`.
- `edit_gate.py` chặn khi có ≥2 task cùng `[~]`, và chặn sau 3 lần sửa mã liên tiếp
  mà chưa tick (đếm streak qua sổ turn, reset khi `plan_sha` đổi).
- Luật giao subagent (`tdq-build`/`tdq-plan` SKILL.md, `agents/tdq-implementer.md`)
  đổi xuống đúng 1 task/lần gọi để tick theo kịp tiến độ thật.

## 0.11.4 — 2026-08-12

Hai lane đổi TÊN GỌI cho người đọc: `chế độ nhanh (express)` và
`chế độ chuyên sâu (deep)`. Định danh máy vẫn là `quick`/`full` — state không đổi lược
đồ, không cần migrate, mọi khoá `quick_*` giữ nguyên.

- `tdq_state.LANE_LABELS` + `lane_label()` là nguồn nhãn duy nhất. Lane lạ trả lại
  nguyên chuỗi thay vì nổ, vì đây là lớp hiển thị.
- `tdq_state.LANE_ALIASES` + `normalize_lane()` là cửa vào duy nhất cho lane do user gõ.
  `init <slug> express` ghi `lane=quick`; `approve nhanh` ghi vào khoá `quick_*`.
- Hook nhận câu duyệt bằng từ mới: `duyệt nhanh`, `duyệt express`. Câu cũ `duyệt quick`
  chạy y như trước. `nhanh` chỉ tính khi đứng ngay sau từ đồng ý, nên "ok làm nhanh nhé"
  KHÔNG bị hiểu là duyệt.
- Văn bản skill, bản portable, README và mô tả plugin gọi lane bằng nhãn mới. Tài liệu
  lịch sử trong `docs/tdq/` giữ nguyên.

493 test xanh.

## 0.11.3 — 2026-08-12

Hàng rào tick ở lane quick chặn thật thay vì chỉ nhắc.

- **`TDQ:TICK` chuyển từ nhắc sang chặn** (`edit_gate.py`): sửa file ngoài `docs/` khi
  phase là `implement`/`qc` mà plan không có task nào mang `[~]` → `permissionDecision:
  "deny"`. Lý do: `stop_gate` chỉ so vân tay plan đầu/cuối turn. Lane quick vốn làm trọn
  gói trong một turn, nên gom tick vào cuối vẫn lọt hàng rào cũ.
- **Miễn trừ `tests/**`**: red→green đòi viết test đỏ trước khi có gì để tick.
- **`block()` trong `_common.py`**: cổng deny duy nhất, KHÔNG dedupe theo mã — điều kiện
  chặn tự tan khi tick, dedupe sẽ cho lần sửa thứ hai lọt qua trong khi plan vẫn đứng yên.
- **Lane quick học đủ ba trạng thái checkbox**: `PHASE_TABLE["quick"]` và
  `skills/tdq-intake/references/quick-lane.md` trước đây chỉ dạy `[x]`, nên hook đòi một
  thứ tài liệu không hề yêu cầu. Nay có mục "Luật tick" và `forbidden` cấm gom tick.
- **Bất biến T2.11 thu hẹp**: `transcript_path` vẫn cấm tuyệt đối trong `hooks/` và
  `scripts/`; chuỗi `"deny"` chỉ được phép trong `_common.py`, để không hook nào tự dựng
  JSON deny riêng.

479 test xanh.

## 0.11.2 — 2026-08-09

Bảng kiểm kê năng lực (B0) giữ được tín hiệu định tuyến cho cả skill mô tả tiếng Việt.

- **`TRIGGER_RE` thêm nhánh tiếng Việt**: `dùng khi|dùng cho|gọi khi|áp dụng khi|khi cần|
  khi user`. Đo trên 274 skill: 0 khớp nhầm vào mô tả tiếng Anh — các cụm này đều có dấu.
- **Mô tả `tdq-build`, `tdq-plan`, `tdq-spec` theo khuôn chung**: câu chốt `Lane full.`
  đổi thành câu `Dùng khi …`, cùng khuôn "câu 1 = nó là gì, câu 2 = dùng khi nào" mà 211
  skill tiếng Anh đang dùng. Cách này giữ regex sạch, không phải nhét từ riêng của TDQ
  (`lane full`) vào một biểu thức dùng chung cho skill của mọi plugin.

Kết quả: 5/6 skill tdq giữ được câu điều kiện, trước đó 0/6. `tdq-conventions` không nằm
trong số này vì nó không có câu "dùng khi nào" — nó được các skill `tdq-*` khác nạp bằng
liên kết trực tiếp, không đi qua bảng B0.

Tổng description 6 skill: 899 → 892 ký tự, vẫn dưới trần 900 của `test_token_budget`.

## 0.11.1 — 2026-08-09

Sửa bảng kiểm kê năng lực (B0) mất tín hiệu định tuyến. Chỉ đụng
`scripts/skill_inventory.py` và test của nó; không đổi khuôn bảng, gate duyệt hay lint.

- **Đọc được `description` nhiều dòng**: parser cũ coi dấu YAML block scalar (`|`, `|-`,
  `>`, `>-`) là nội dung nên 56/268 skill ra ô vô nghĩa (trọn cụm firecrawl, tavily,
  adobe, base44/datarobot). Nay gom mọi dòng thụt vào tới khoá cấp 0 kế tiếp, trần 80 dòng
  frontmatter. 56 → 0 ô vô nghĩa.
- **Rút gọn có nhận biết cụm trigger**: cắt cụt 60 ký tự làm mất câu "dùng khi nào" ở
  146/211 skill. Nay giữ đầu rồi ghép ` … ` + 50 ký tự kể từ cụm trigger
  (`use when|use this|whenever|when the user|trigger`), dò lùi 15 ký tự để bắt cả ca cụm
  nằm vắt ngưỡng. Giữ được trigger 24,6% → 100%.
- **Ký tự `|` trong description đổi thành `/`**: 18 dòng vỡ số cột → 0.

Chi phí: output kiểm kê 6.199 → 9.264 token mỗi lần chạy (+49,4%); quy về đơn giá là
8,4 → 22,8 skill-có-trigger trên mỗi 1k token (+171%). Ô dài nhất 113 ký tự.

## 0.11.0 — 2026-08-09

Cắt token thừa: bỏ 6 chỗ workflow bắt chép lại thứ đã có, hoặc bắt làm step không sinh giá
trị. Không đụng gate duyệt — quick vẫn 1 cổng, full vẫn 2 cổng (spec + plan).

- **Bảng kiểm kê năng lực thôi chép cả 242 skill**: chỉ ghi một dòng cho mỗi skill `DÙNG`
  hoặc `NỀN`, cộng đúng một dòng tổng `Đã xét <N> skill khác — khác lĩnh vực`. Vẫn phải RÀ
  hết như cũ; chỉ cắt phần ghi ra. Bỏ mục "Bảng quá dài" vì luật mới đã bao.
- **Bỏ mục `## Năng lực → task` trong plan**: đây là bản chép thứ ba của cùng một bảng
  (brief → spec §3b → plan). Ánh xạ năng lực → task vẫn kiểm được bằng khối hợp đồng.
- **Phase log & test thành có điều kiện**: chỉ bắt buộc khi việc có runtime (plan có ít
  nhất một task tạo/sửa file mã nguồn chạy được). Không có runtime → ghi đúng một dòng
  `Log: BỎ — <lý do>` ở spec §4 và plan.
- **Hợp đồng skill còn 5 trường**: bỏ `Nạp`, câu chỉ đường `SKILL.md` cho agent ngoài dời
  vào trường `Để`. `doc_lint.CONTRACT_FIELDS` cập nhật theo.
- **`phases-doc` thôi sinh mục chi tiết từng phase** (nó lặp lại SKILL.md của chính phase
  đó): `phases.md` 89 → 33 dòng. Checklist đầy đủ lấy bằng `tdq_state.py next`.
- **Câu chốt vòng interview thành có điều kiện**: chỉ hỏi "Bạn muốn bổ sung thêm gì không?"
  khi vòng đó thật sự có câu hỏi; không có thì đi thẳng bước sau.
- **`docs/claude-md-mau.md` là nguồn sự thật duy nhất cho `~/.claude/CLAUDE.md`**: đã hợp
  nhất phần chỉ có ở bản live (plugin đã bật sẵn, mem0), cắt chi tiết đã nằm ở file đích,
  rồi đồng bộ. Hai file nay `diff` rỗng — 4.243 → 3.460 byte.

### Phá vỡ tương thích

- Plan cũ còn dòng `- Nạp:` trong khối hợp đồng vẫn lint qua (trường thừa không bị bắt),
  nhưng khuôn mới không sinh ra nó nữa.
- `phases-doc` không còn in mục `## <phase>`; script nào parse output đó phải chuyển sang
  đọc bảng hoặc khối "Lệnh nguyên văn".

## 0.10.0 — 2026-08-09

Cắt over-engineer và over-test khỏi chính bộ workflow. Bản này **xoá tính năng**, đọc kỹ
mục "Phá vỡ tương thích" trước khi nâng.

- **Tầng `nhỏ`** đứng trước lane quick/full: đủ 4 điều kiện (không đổi hành vi sản phẩm
  hoặc chỉ một chỗ hiển nhiên · không thêm/xoá file mã nguồn · không đụng hook, state,
  gate duyệt · xong trong một turn) thì trả lời hoặc sửa luôn, KHÔNG mở request. Kèm luật
  thoát bắt buộc: giữa chừng vỡ điều kiện nào thì DỪNG, nói rõ, rồi mở request bình thường.
- **QC bám Definition of Done**: số hạng mục QC bằng số dòng DoD của chính plan đó, mỗi
  dòng một phép kiểm chạy được bằng lệnh, cộng đúng 1 hạng mục chạy full-suite. Thay cho
  checklist cố định 3 hạng mục (quick) và 7 hạng mục (full).
- **Vòng fix gọn lại**: chỉ chạy lại hạng mục đã FAIL cộng hạng mục mà bản fix có thể làm
  hỏng, không chạy lại toàn bộ. Bỏ luật "vòng fix bắt buộc kể cả khi user tắt QC" — tắt QC
  thì không có FAIL để fix, luật cũ tự mâu thuẫn. Giữ trần 3 vòng.
- **Gộp brief**: `docs/tdq/requests/` + `knowledge/` + `questions/` thành một file
  `docs/tdq/brief/<slug>.md` ba mục (Nguyên văn · Hiểu & kiến thức · Hỏi đáp). Doc mỗi
  request còn 5 file thay vì 7.
- **`doc_lint` đúng phạm vi**: `docs/tdq`, `docs/workinglog`, `graphify-out` là biên bản và
  file máy sinh, chỉ chịu R8; sửa cửa thoát `allow` của R5.
- Skill gọn hơn: `tdq-conventions/SKILL.md` 7.345 → 5.912 byte (nạp ở MỌI phase), phần
  carry-cost tách sang `references/context-budget.md`. Toàn bộ `skills/` 102.166 → 81.467 byte.
- Bộ test: 600 → 410 test, bỏ nhóm chỉ assert câu chữ trong `.md` (chặn đúng việc rút gọn
  skill mà không bắt được lỗi hành vi nào). Suite còn 0 test đỏ.

### Phá vỡ tương thích

- **Xoá mode `external`** và toàn bộ nhánh deep search: `external_task.py`,
  `external_models.py`, `search_task.py`, 2 schema, 4 agent runner (`codex-runner`,
  `agy-runner`, `search-runner`, `search-scout`), 3 reference. `VALID_MODES` còn
  `main|subagent`; `approve plan --mode external` bị từ chối, rc=2.
- **Xoá thư mục `portable/`** (18 file). Bản mẫu CLAUDE.md chuyển thành
  `docs/claude-md-mau.md`; sửa `~/.claude/CLAUDE.md` của bạn cho khớp nếu đang nhắc mode
  `external` hay deep search.

## 0.9.0 — 2026-08-07

Siết QC và vòng fix cho lane quick. Trước bản này lane quick chỉ nói "chạy validate" và
không có luật nào cho tình huống gặp bug — `qc.md` cùng luật `## QC vòng N — fix` chỉ
`tdq-build` (lane full) nạp.

- QC quick = 3 hạng mục, **mặc định BẬT**: test từng task pass · đối chiếu TỪNG dòng
  Definition of Done · biên và đường lỗi cơ bản. Bằng chứng append vào mục `## QC` của
  chính file plan, không tạo file `qc/`. Nhẹ hơn full đúng 4 hạng mục (full-suite toàn
  repo, log service, không-placeholder, hợp đồng skill).
- Vòng fix **BẮT BUỘC**, không opt-out được kể cả khi user bỏ QC · task fix ghi dưới
  `## QC vòng N — fix`, fix xong chạy lại đủ 3 hạng mục · **trần 3 vòng** — vượt trần thì
  DỪNG, báo user, đề xuất chuyển lane full, giữ `phase=implement`.
- Cờ mới `approve quick --no-qc` là đường opt-out DUY NHẤT, chỉ hợp lệ với `quick` và
  bắt buộc kèm `--by "<nguyên văn câu user>"`; ghi field state `quick_qc_skipped` và log
  1 dòng có timestamp qua `_info` (stderr, tắt được bằng `TDQ_LOG=0`).
- Luật đồng bộ trên 5 nguồn sự thật: `tdq-intake/references/quick-lane.md`,
  `tdq-intake/SKILL.md`, `scripts/tdq_state.py` (`PHASE_TABLE["quick"]`),
  `portable/workflow/**`, và 2 bản `phases.md` sinh bằng `phases-doc`.
- Thêm `tests/test_quick_qc.py` (15 test) khoá cứng parity 5 nguồn.

## 0.8.0 — 2026-08-05

Audit toàn workflow (skills/scripts/hooks/rules) + 16 đề xuất P0/P1 áp dụng. Dedupe
git status/turn_rows/prompt_context, nén `skill_dump()`. Tách nhánh external khỏi
`tdq-build/SKILL.md`, tách Phần B `tdq-intake` sang reference, siết quick-lane. Chốt
ngưỡng digest 1.500 ký tự cho 8 agent, sửa link cross-reference cũ, ghi rủi ro
2-phiên. `tdq-intake/SKILL.md` 117→84 dòng, `tdq-build/SKILL.md` 150→90 dòng.

Luật đặt tên sub-agent (`<model>-<effort>-<việc-kebab>`, vd `sonnet-low-research`)
nâng từ chỗ chỉ nạp trong TDQ build lên tầng global `~/.claude/CLAUDE.md`, áp cho
mọi lần gọi Agent tool; đồng bộ định dạng ở `tdq-conventions/SKILL.md` §9.

## 0.7.0 — 2026-08-05

Workflow linh hoạt: gộp gate spec → plan → build trong cùng turn, lane quick vẫn đủ
bước tư duy, bỏ vòng review máy giữa spec và plan.

Tối ưu token 2 vòng: `token_audit.py` sửa lỗi đếm theo dòng JSONL (lệch +62%) · CLAUDE.md
lõi rút còn 3,2 KB và đẩy luật chi tiết sang `skills/*/references`. Bookkeeping cuối turn
gộp về `tdq_finish.py`, digest sub-agent có trần, 10 LSP chuyển sang nạp theo yêu cầu.

Report của request rút trần từ 50 xuống 10 dòng.

Bộ export sang máy khác đổi từ 7 bước tay sang `scripts/claude_export.py` với 2 lệnh
`build` và `check`. Bản copy repo lấy bằng `git clone` (giữ `.git`, chỉ file tracked) ·
cấu hình MCP đi kèm để khôi phục bằng `claude mcp add-json`. Manifest ghi phiên bản
plugin + commit SHA + sha256 từng file, còn `check` đo độ lệch giữa bundle và máy nguồn.

`approve spec|plan` nay ghi lại được khi file đã sửa sau lần duyệt trước. sha256 và dấu
duyệt được làm mới thay vì bỏ qua · cảnh báo "đã đổi sau khi duyệt" không còn treo vĩnh
viễn sau khi QC sửa spec. File không đổi thì lệnh vẫn là no-op như cũ.

## 0.6.2 — 2026-08-02

Intake default tuyệt đối (mọi prompt mới → tdq-intake), hint duyệt plan theo mode
động, tự chọn đề xuất khi gặp chặn kỹ thuật giữa build (được tự commit gỡ chặn,
không push).

## 0.6.1 — 2026-07-31

Audit toàn diện 0.6.0: 44 findings (A1–A44), 33 issue S/M fix có test riêng,
harden contract cho model cấp thấp; QC Q1–Q10 PASS, suite 367 test.

### Fix
- `tdq_state.py`: literal `\1` + wrap đôi backtick trong `phases-doc`; terminal
  state cho lane quick (idle không lặp checklist); `phases-doc [--plugin-root]`
  sinh 2 bản phases.md (skills plugin-root ↔ portable relative); `_row_age_ok`
  chịu timestamp số.
- `external_task.py`: persist raw output engine khi validate FAIL; retry feed
  trích stdout attempt trước; timeout wrapper/engine so le (A13); atomic write
  report; dir neo project-dir thay vì cwd (cùng `external_models.py`).
- `search_task.py`: guard load schema; `merge` báo `agents_skipped` thay vì nuốt
  file hỏng; cảnh báo separator route chứa `;`; copy brief atomic; raw persist.
- `doc_lint.py`: path không tồn tại → exit 2 thay vì im lặng pass; lỗi IO ra
  message tử tế. `skill_inventory.py` dùng resolver project-dir chung.
- Hook: truncation không cắt giữa inline-code; `plugin_tiers.py` warn luôn ra
  stderr kể cả khi tắt log.

### Đổi
- 4 agent def runner/scout viết lại theo cơ chế chờ thật (Bash nền → đánh thức),
  bảng exit code 0/1/2/3, nhánh `scout-failed`; `tdq-qc-tester`/`tdq-reviewer`
  khóa `tools:` read-only (cần reload plugin).
- Docs đồng bộ: thời điểm chốt engine+model (CLAUDE.md §10 ↔ tdq-plan), run-dir
  định nghĩa trong deep-search.md, portable bổ sung external-task.md + 3 file
  scripts trong README, tdq-spec thêm lệnh doc_lint single-file.

## 0.6.0 — 2026-07-31

Deep search nâng thành flow hybrid 2 phase: phase 1 = agent `search-scout`
(Claude + Tavily) chạy song song `search-runner` (agy) đi rộng nắm hướng;
phase 2 = `search-runner` đào sâu theo ≤3 route Claude chốt; merge chung 1 lần.

### Thêm
- **`agents/search-scout.md`**: slot Claude scout cố định (agent 2, route `scout:`) —
  search rộng qua tavily-primary, ghi `agent-2.json` đúng format file agent
  (url_alive/not_found/queries_used), trả 3–5 route gợi ý cho phase 2.
- **`search_task.py split --start-agent N`** (default 1): phase 2 đánh số agent từ 3
  để chung run-dir với phase 1, merge một lần cuối.

### Đổi
- Default model agy: `gemini-3.6-flash-low` → **`gemini-3.6-flash-medium`**
  (escalation giữ flash-high, ≤2 retry).
- `deep-search.md` viết lại theo flow hybrid: slot cố định phase 1 (ngoại lệ luật
  split), mục `## Hướng từ phase 1` + `brief-phase2.md`, 3 nhánh degrade
  (agent 1 hỏng / scout-failed / cả hai hỏng), luôn chạy đủ 2 phase.
- `tavily.md`, `portable/workflow/06-deep-search.md`, CLAUDE.md §10 đồng bộ flow mới.

## 0.5.0 — 2026-07-31

Deep search mặc định đi qua agent `search-runner` + agy CLI: mọi logic dễ hỏng
(cap, retry/escalation, schema, URL sống, dedup, rank tất định, log) nằm trong
`scripts/search_task.py`; model cấp thấp chỉ nhận từng việc nhỏ đã đóng khung.

### Thêm
- **`scripts/search_task.py`** (`split` / `run` / `merge`): chia route round-robin theo
  cap `TDQ_SEARCH_MAX_AGENTS`; mỗi route 1 lần search + đọc sâu ≤N URL qua agy
  `--json-schema`; retry ≤2 với escalation model + đính lỗi cũ vào prompt; check URL
  sống (HEAD→GET); merge dedup theo URL chuẩn hoá, rank tất định (route xác nhận →
  URL sống → có quote → score); log per-agent ISO timestamp, `TDQ_SEARCH_LOG=0` tắt.
- **`scripts/search_report_schema.json`**: schema report bắt buộc evidence quote +
  `source_url` có path; nguồn duy nhất của luật URL.
- **Agent `search-runner`** (vỏ mỏng chạy script) + tài liệu
  `references/deep-search.md` (luật trigger ≥2 dấu hiệu, brief FULL data,
  fallback Tavily khi `engine-failed` ≥2 lần); tầng search ghi ở `tavily.md`,
  `tdq-intake` B3 và `portable/workflow/06-deep-search.md`.
- **`.claude/settings.json`** (project): env block TDQ_SEARCH_* mặc định.

## 0.3.3 — 2026-07-29

Workflow trước đây không hề rà soát skill phụ trợ đang có (audit: điểm mù, không phải
giới hạn kỹ thuật). Bản này thêm bước kiểm kê năng lực bắt buộc, thiên lệch về phía DÙNG,
viết máy móc đủ cho model nhỏ chạy local.

### Thêm
- **`scripts/skill_inventory.py`**: quét skill trên đĩa từ đúng 3 nguồn (user, project,
  plugin đang bật — gộp `enabledPlugins` 3 tầng settings, chỉ đọc `installPath`, bỏ entry
  `scope: project` của project khác, cấm quét cache). Luôn in 2 dòng nhắc chép thêm skill
  built-in (thứ không tồn tại trên đĩa). Log service qua `TDQ_LOG`.
- **Bước B0 ở `tdq-intake`**: kiểm kê năng lực trước khi đọc code; bảng phán quyết
  (khuôn ở `references/skill-inventory.md`) lưu vào `knowledge/<slug>.md`. Quy tắc máy
  chạy được: xét 100% bắt buộc · loại chỉ bằng 4 lý do đóng · **phân vân → DÙNG**.
  Lane quick: mini-plan bắt buộc có dòng `Năng lực:`.
- **Spec §3b "Năng lực & công cụ"** (bảng phán quyết `DÙNG/KHÔNG/NỀN`) trong khuôn spec.
- **Hợp đồng skill 6 trường trong plan** (`Dùng/Nạp/Để/Ra/Kiểm/Không dùng cho`): mỗi dòng
  `DÙNG` ở spec phải nở thành khối hợp đồng ở mức task — không còn "ghi tên rồi implement mù".
  `tdq-build` nạp skill theo trường `Nạp` TRƯỚC bước đỏ; QC chạy trường `Kiểm` thật.
- **`doc_lint.py` rule R8** (spec phải có §3b hợp lệ; file trong `spec/` chỉ chịu R8) và
  **`doc_lint.py --pair <spec> <plan>`** (đối chiếu hợp đồng, thiếu trường nào nêu tên
  trường đó). 4 spec cũ miễn trừ bằng `<!-- doc-lint: allow R8 -->`.
- `PHASE_TABLE`: checklist `analyze` + `quick` nhắc bước kiểm kê; `phases.md` sinh lại.
- Portable đồng bộ: agent ngoài không có skill system → xét công cụ tương đương như skill,
  dòng `DÙNG` ghi thêm `tương đương: <cách làm>`.

## 0.3.2 — 2026-07-29

Audit 0.3.1 phát hiện chính vân tay repo lại đẻ ra một kiểu chặn oan mới, nặng hơn
lỗi mà 0.3.1 vá. Bản này sửa hết.

### Sửa
- **Turn read-only không còn bị chặn.** 0.3.1 so vân tay TOÀN repo nhưng chỉ loại
  trừ `docs/tdq/` lúc đặt tên file. Vì vậy chính việc hook append sổ turn sau khi chụp
  ảnh đầu turn cũng làm vân tay đổi. Hệ quả: mọi file bẩn có sẵn bị lôi ra làm vật tế
  thần, kể cả trong turn chỉ đọc hoặc chỉ ghi state. Nay `docs/tdq/` và
  `docs/workinglog/` bị loại trừ ngay từ **pathspec của git**, dùng chung cho cả
  quyết định lẫn đặt tên.
- **`touch` file untracked không còn bị chặn**: file untracked ≤256 KB được lấy dấu
  bằng **nội dung** thay vì `size:mtime` (ngân sách đọc 4 MB mỗi lần lấy vân tay).
- **Windows**: tiền tố vùng loại trừ viết bằng `/` cứng — dùng `os.path.join` thì
  thành `docs\tdq` và bộ lọc im lặng ngừng hoạt động.
- `stop_gate` lấy dòng `turn_start` **mới nhất** thay vì dòng đầu tiên: sổ turn còn
  sót dòng của turn trước thì mốc so sánh có thể cũ tới 6 giờ.
- Trần số file untracked lấy dấu đếm đúng **số file** (trước đây cắt theo số dòng
  `git status`); danh sách path đầu turn nâng trần 100 → 400.
- Path file untracked được stat theo **gốc repo**, không theo cwd (porcelain in path
  theo gốc) — chạy workflow từ thư mục con không còn bỏ lọt.

### Thêm
- Log service cho hook (§6): `git` timeout / không chạy được → ghi cảnh báo kèm
  timestamp ra stderr; mỗi quyết định chặn ghi rõ nguồn bằng chứng và path. Tắt bằng
  `TDQ_LOG=0`.

## 0.3.1 — 2026-07-29

Vá điểm mù của verify-by-effect: sổ turn chỉ thấy hành động đi qua tool Edit/Write,
nên mọi thay đổi qua shell đều vô hình với nó.

### Sửa
- **Hết chặn oan `[TDQ:LOG]`**: append working log bằng `cat >>`, `tee`, `sed -i`,
  heredoc… giờ được công nhận. Trước đây chỉ tool Edit/Write mới ghi được `log_written`,
  nên turn hợp lệ vẫn bị Stop chặn.
- **Hết bỏ lọt chiều ngược lại**: sửa repo hoàn toàn bằng shell (không qua Edit) trước
  đây không sinh `observe edit` nên Stop im lặng dù chưa ghi log; nay vẫn bị đòi.

### Thêm
- `tdq_state.py`: `today_log_rel()`, `repo_status_digest()`, `repo_status_paths()`,
  `turn_snapshot()` — vân tay gồm cả `git status --porcelain -uall` lẫn `git diff HEAD`
  (porcelain không đổi khi sửa tiếp một file vốn đã `M`).
- `prompt_context` ghi một dòng `turn_start` vào sổ turn (không in ra context, không
  tốn token của model); `stop_gate` so lại lúc kết turn.

### Ghi chú
- Không có dòng `turn_start`, project không phải git repo, hoặc `git` lỗi/timeout 2 s →
  rơi về đúng hành vi 0.3.0.
- Thay đổi trong `docs/tdq/` (state, sổ turn) không tính là "đổi repo".
- `bash_gate.py` **không** đổi: cố đoán lệnh shell bằng regex vừa không đủ vừa dễ cấp
  bằng chứng giả.

## 0.3.0 — 2026-07-29

Mục tiêu: bộ instruction đủ chi tiết để **model nhỏ chạy local** cũng đi đúng workflow,
và hook chuyển hẳn sang vai "nhắc + kiểm bằng hiệu ứng thật".

### Thêm
- **Ledger mỗi turn** `docs/tdq/.tdq-turn.jsonl`: hook ghi dòng `remind` (đã nhắc mã nào)
  và `observe` (hiệu ứng thật: sửa file, ghi log, gọi CLI state). `stop_gate` đối chiếu
  hai bên — agent in `✓` mà không có hiệu ứng thật thì không qua được.
- **5 mã nhắc đóng**: `TDQ:NEXT`, `TDQ:APPROVE`, `TDQ:LOG`, `TDQ:STATE`, `TDQ:GIT`
  (1 lần/mã/turn).
- `tdq_state.py next [--brief]` — trả lời "giờ làm gì" theo phase, kèm checklist.
- `tdq_state.py phases-doc` — **sinh** `references/phases.md` từ hằng `PHASE_TABLE`;
  doc phase không còn viết tay, có test khoá đồng bộ.
- `scripts/doc_lint.py` (R1–R7): bước đánh số liên tục, lệnh copy-paste được, có
  `Xong khi:`/`Bước kế tiếp:`, cấm từ mơ hồ, câu ≤ 40 từ, trần độ dài, bắt buộc link
  mẫu output.
- **Bản portable** `portable/AGENTS.md` + `portable/workflow/` cho agent ngoài Claude Code,
  có test chống lệch bước so với skills.
- Test mới: `test_doc_lint`, `test_token_budget`, `test_portable_sync`,
  `test_skill_shape`, `test_hook_resilience`, `test_docs_consistency`.

### Đổi
- **Skill 10 → 6.** Bảng ánh xạ:

  | Cũ | Mới |
  |---|---|
  | `tdq-start`, `tdq-analyze` | `tdq-intake` |
  | `tdq-implement`, `tdq-qc`, `tdq-report` | `tdq-build` |
  | `tdq-approve` | bỏ hẳn — duyệt bằng chat thường |
  | `tdq-spec`, `tdq-plan`, `tdq-status`, `tdq-conventions` | giữ tên, viết lại theo dạng bước đánh số |

- Thân skill gọn lại, chi tiết đẩy sang `references/` (chỉ nạp khi cần).
- State schema v3: thêm `implement_mode`, `*_approved_by`, `previous_request`;
  mirror `docs/tdq/STATE.md` tự sinh để đọc.
- Ngân sách token có test đo thật (SessionStart ≤ 12 dòng/600 ký tự, UserPromptSubmit
  ≤ 3/240, PreToolUse ≤ 3/200, Stop ≤ 4/300, STATE.md ≤ 30 dòng, `next` ≤ 20 dòng).
- Exit code của CLI: mọi trục trặc state là cảnh báo (exit 0); exit 2 chỉ khi sai cú pháp.
- `docs/tdq/state.json` không còn bị `.gitignore`; thay bằng `docs/tdq/.tdq-turn.jsonl`.
- Doc v0.1 chuyển vào `docs/archive/v0.1/`.

### Bỏ
- Skill `tdq-approve` và mọi gate chặn tool vì lý do "chưa duyệt".
- Hook không còn đọc transcript và không còn trả `deny`.

## 0.2.0 — 2026-07-28

- Chuyển gate duyệt từ **chặn** sang **nhắc**: chưa duyệt mà sửa file ngoài `docs/` thì
  hook đính lời nhắc vào ngữ cảnh thay vì từ chối tool.
- Duyệt bằng chat thường; state lưu nguyên văn câu user duyệt.
- Điểm chặn duy nhất còn lại: chưa append working log thì không kết thúc turn được.
- Lưu sha256 của spec lúc duyệt để phát hiện spec trôi sau khi duyệt.

## 0.1.6 — 2026-07-28

- `implement_mode` do **user** quyết; nới nhận diện dòng mode lúc duyệt.

## 0.1.4 — 2026-07-28

- Siết gate duyệt: chỉ user được gõ lệnh approve, agent không được đụng `state.json`.

## 0.1.0 — 2026-07-27

- Bản đầu: 10 skill, 6 hook, 3 agent, 49 test.
