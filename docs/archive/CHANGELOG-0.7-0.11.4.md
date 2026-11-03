# Changelog 0.7.0 → 0.11.4

Tách khỏi `CHANGELOG.md` ngày 2026-08-15 để file chính ở dưới trần 500 dòng.
Mới nhất trên cùng.

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
