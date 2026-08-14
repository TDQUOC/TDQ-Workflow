# Changelog

Mới nhất trên cùng. Ngày theo múi giờ máy phát hành.

## 0.16.0 — 2026-08-14

Cắt chi phí context của chính workflow mà không bỏ một luật nào: đếm mệnh lệnh theo 10
cụm file cho **7 cụm tăng · 3 cụm giữ nguyên · 0 cụm giảm**. Nguyên tắc áp dụng xuyên
suốt: dời văn bản xuống tầng `đọc khi cần` và để lại dòng trỏ có chữ BẮT BUỘC, tuyệt đối
không xoá luật.

- `scripts/skill_inventory.py`: thêm `--loc <từ khoá>` và `--tat-ca`. Bản lọc CẤM ẩn skill
  nguồn `project` và `plugin:tdq-workflow` (hai nguồn quyết định phán quyết DÙNG ở bước
  B0), và luôn in dòng cuối báo đã ẩn bao nhiêu kèm lệnh xem đủ. Chạy không cờ giữ nguyên
  từng byte. Bước B0 dùng `--loc`: **39.722 → 1.845 byte** mỗi lần chạy (≈ −9.300 token).
- `skills/tdq-intake/SKILL.md`: nhánh chế độ nhanh dời sang
  `references/quick-lane.md`, đánh số lại thành 12 bước. Thân 1.844 → 1.288 token.
- `skills/tdq-build/SKILL.md`: Phần B (QC) và Phần C (Report) dời xuống `references/qc.md`
  và `references/report-template.md`. Thân 1.936 → 1.536 token.
- `skills/tdq-conventions/`: phần nền/giải thích của 3 file gom vào mục `## Phụ lục`,
  **giữ nguyên 100% câu chữ** (diff theo từ: 0 từ bị mất).
- `skills/tdq-intake/references/scope-round.md`: khử 2 từ mơ hồ thành điều kiện đo được.
- 8 chỗ cố ý chép lại luật giữa các file nay có nhãn "nhắc lại có chủ ý" — chống việc
  lần sau bị nhầm là trùng lặp rồi xoá đi.
- `agents/tdq-implementer.md`, `tdq-qc-tester.md`, `tdq-reviewer.md`: thêm khối
  "Return format — copy this shape exactly".
- Tổng tầng `nạp khi gọi skill` **8.473 → 7.579 token** (−10,6%). Test 563 → 569 passed,
  0 failed. QC 15 hạng mục, Q1–Q14 PASS; một lượt QC độc lập bằng agent `tdq-qc-tester`
  chạy lại từ đầu cho cùng phán quyết. Model hạng thấp chạy thử: không bỏ bước nào.
- Chưa đụng `hooks/` và `portable/` — bản portable chưa nhận các thay đổi này.

## 0.15.1 — 2026-08-14

Bản tài liệu: đề xuất cơ chế chống quick-fix phá kiến trúc. Chưa đụng file thực thi nào
trong `skills/`, `scripts/`, `hooks/` — việc áp cơ chế vào workflow là request riêng.

- `docs/tdq/knowledge/2026-08-14-chong-no-ky-thuat.md` (mới): 4 khoảng trống đo được của
  workflow hiện tại, kèm bằng chứng `file:line`. Cộng 6 cơ chế M1–M6; mỗi cơ chế có
  nguyên văn dòng luật copy dán được, chỗ chèn `file:mục`, mức chi phí A/B, một lệnh kiểm.
- M1 hồ sơ kiến trúc mỗi project · M2 ô "Ràng buộc kiến trúc phải giữ" trong spec §5 ·
  M3 luật "tìm rồi mới tạo" thay dòng implement cũ · M4 khai `Chạm:` bằng
  `graphify affected` trong plan · M5 ba hạng mục QC cố định chống hồi quy (nới luật "số
  hạng mục QC = số dòng DoD") · M6 cổng trùng lặp `jscpd` (mức B, tuỳ chọn).
- Ba gói cộng dồn theo chi phí, khuyến nghị **Gói vừa** (M1–M5, toàn mức A, không script,
  không cổng duyệt mới). Kèm bản rút gọn cho pipeline express và phần tách rõ chỗ nào
  độc lập ngôn ngữ khi áp cho project khác (Unity, game).
- Số liệu lấy từ chạy thật: `grep` trên 1.844 dòng skill, `graphify god-nodes`,
  `graphify affected "payload_cwd"`, `jscpd` 5.0.15 (72 cặp trùng, 1.82% token, exit 0).

## 0.15.0 — 2026-08-14

Interview đi hai tầng: hỏi phạm vi tổng quát trước, rồi mới hỏi chi tiết trong đúng
những mặt user chọn — để spec không bao thiếu cũng không bao dư.

- `skills/tdq-intake/references/scope-round.md` (mới, 5 mục): khi nào chạy · câu 1 chọn
  mặt · câu 2 bối cảnh bằng số · suy mức đầu tư · ghi lại. Vòng scope chạy **có điều
  kiện** theo danh sách đóng 4 dấu hiệu kích hoạt; bỏ thì buộc ghi một dòng
  `Vòng scope: BỎ — <lý do>` vào brief. Áp cho cả lane express lẫn deep.
- Câu 1 chỉ trình 3–5 mặt hợp lĩnh vực của request, soát nội bộ theo khung 9 mặt
  ISO/IEC 25010; luôn có option "chỉ cần chạy được".
- Câu 2 hỏi bối cảnh bằng số (môi trường + bản target, CCU/RPS/số bản ghi, R&D hay
  product, vòng đời & người bảo trì, ràng buộc nền tảng), trần 4 câu. **CẤM** hỏi mức độ
  trừu tượng kiểu "gọn nhất hay đầy đủ chuyên nghiệp" — mức đầu tư do agent suy ra rồi
  nói lại bằng dòng `Tôi hiểu là: <mức> vì <bối cảnh>`, không phải cổng duyệt mới.
- Nối vào 4 chỗ gọi interview: `interview.md` (thêm mục "Hai tầng câu hỏi", tầng 2 chỉ
  hỏi trong các mặt user đã chọn), `analyze-full.md` bước 4, `quick-lane.md`,
  `tdq-intake/SKILL.md`.
- Neo kết quả: `spec-template.md` §1 buộc chép các mặt bị loại vào `NGOÀI phạm vi` (thêm
  một dòng Checklist scope); `tdq_state.py` `PHASE_GUIDE["analyze"]` thêm dòng nhắc vòng
  scope, đặt trước dòng hỏi chi tiết.
- Test: `tests/test_scope_round.py` (nội dung file luật + kiểm cả 4 chỗ gọi đã nối dây),
  `tests/test_next.py::test_next_analyze_asks_for_the_scope_round`.

## 0.14.0 — 2026-08-14

Cổng chọn cách chạy nói bằng tên nghề nghiệp, và phải giải thích vì sao đề xuất mode đó.

- `scripts/tdq_state.py`: thêm `MODE_LABELS`/`MODE_ALIASES` + `mode_label()`/
  `normalize_mode()` — mode tách hai lớp y như lane. Nhãn hiển thị: `main` → "làm trực
  tiếp (inline implement)", `subagent` → "giao trợ lý (sub-agent implement)". Định danh
  máy giữ nguyên `main|subagent` nên state cũ, plan cũ, `--mode` cũ không phải migrate.
  `--mode` và dạng gõ tắt `approve plan <mode>` đều đi qua `normalize_mode`.
- Checklist phase `mode` buộc trình đoạn **"Vì sao đề xuất"** dài 1–3 dòng. Đoạn đó phải
  nêu đủ 4 căn cứ đọc từ chính plan: số task, chuỗi phụ thuộc, số file bị nhiều task cùng
  đụng, có nhãn `(mcp)` không. Kết bằng một câu vì sao không chọn phương án còn lại.
- `skills/tdq-plan/references/mode-gate.md` (mới): khuôn hỏi nguyên văn + luật viết đoạn
  lý do. SKILL.md có trần 100 dòng nên chỉ giữ tóm tắt và link.
- `plan-template.md`, `skills/tdq-build/SKILL.md`: ghi kèm nhãn hiển thị bên cạnh định
  danh máy.
- Hook: `_common.py` in nhãn thay vì định danh máy; `prompt_context.py` nhận `inline`,
  `sub-agent`, biến thể có `implement`, và **chữ cái A/B** đúng như khuôn mời gõ
  (`mode_from_answer`: A = mode plan đề xuất, B = mode còn lại); `edit_gate.py` gợi ý cả
  hai tên.

## 0.13.0 — 2026-08-14

Chốt vai trò graphify thành hai luật rõ: đồ thị CHỈ chứa mã nguồn sản phẩm, và chỉ tra
đồ thị khi cần liên kết hoặc bản đồ tổng thể.

- `.graphifyignore`: liệt kê đủ 8 thư mục (`tests/ docs/ portable/ skills/ agents/
  ClaudeExport/ claude-export/ graphify-out/`), có hiệu lực cả khi chạy `graphify extract`
  không cờ `--code-only`. Node trong đồ thị: 1.421 → 412.
- 6 file `hooks/scripts/` đổi sang `from tdq_state import <tên>` rồi gọi thẳng. Lý do:
  graphify (0.9.28 và 0.9.42) chỉ sinh cạnh `calls` cross-file cho dạng from-import; dạng
  `import M` + `M.f()` không sinh cạnh nào. Cạnh `hooks/* → scripts/tdq_state.py`: 1 → 38,
  `graphify affected "turn_snapshot()"` từ chỗ không ra gì nay ra `prompt_context.py`.
- `skills/tdq-intake/references/analyze-full.md`, `quick-lane.md`: thêm luật ĐỌC — mở đồ
  thị cho câu hỏi liên kết / bản đồ tổng thể, grep cho tìm chuỗi và đọc file cụ thể.
- `scripts/tdq_state.py`: thêm `"graphify-out"` vào `BOOKKEEPING_PATHS`; thư mục do chính
  workflow ghi lại mỗi turn không còn tính vào vân tay repo. Kèm test mới
  `test_digest_ignores_graphify_out`.
- `tests/test_bash_gate.py`: patch `turn_log_read` vào module `_common` (nơi giữ tên đã
  bind) thay vì vào `tdq_state`.

## 0.12.0 — 2026-08-13

Khuôn trình bày thân thiện dùng chung cho mọi chỗ nói với user, và tách bước chọn cách
chạy thành phase `mode` riêng — user chỉ cần nhắn "duyệt plan".

- `skills/tdq-conventions/references/user-facing-block.md` (mới) + bản portable: 5 thành
  phần bắt buộc, cấm emoji, xưng "bạn", luôn có đường dẫn file đầy đủ. Áp cho đủ 7 chỗ
  giao tiếp: hỏi pipeline, interview, duyệt spec, duyệt plan, chọn cách chạy, duyệt chế
  độ nhanh, hỏi commit cuối request.
- `scripts/tdq_state.py`: thêm phase `mode` vào `VALID_PHASES`, `PHASE_ORDER`,
  `PHASE_TABLE`. `approve plan` không kèm `--mode` nay dừng ở phase `mode`; kèm `--mode`
  thì vào thẳng `implement`.
- `hooks/scripts/_common.py`, `prompt_context.py`: khoá `plan` trong `APPROVE_HINTS` bỏ
  phần mode, thêm khoá `mode` giải thích nghĩa `main` và `subagent` ngay tại chỗ.
- Đồng bộ tài liệu: `phases.md` (hai bản), `portable/workflow/03-plan.md`,
  `plan-template.md` (hai bản), `docs/claude-md-mau.md` §6.
- `tests/test_mode_phase.py` (mới) và cập nhật `test_gate_merge`, `test_phase_table`,
  `test_state`, `test_context_hooks`.

## 0.11.13 — 2026-08-13

Bắt chặn của `stop_gate.py` phải ra lệnh in LẠI NGUYÊN VĂN khối chat cuối — lớp vá thứ hai
cho việc focus mode gập ẩn câu hỏi khi turn còn chạy tiếp sau lúc đã in khối user-facing.

- `hooks/scripts/stop_gate.py`: `reason` của cả `[TDQ:LOG]` và `[TDQ:TICK]` nay yêu cầu in
  lại nguyên văn khối chat cuối. `[TDQ:LOG]` bỏ câu bảo tự thêm mục `## HH:MM`, thay bằng
  lệnh `tdq_finish.py`. Sửa kèm lỗi `culprit` lấy từ sổ turn không cắt theo `MAX_PATH_CHARS`
  nên path dài đẩy lời chặn vượt trần 300 ký tự.
- `skills/tdq-conventions/SKILL.md` §1 bước 5: luật in lại nguyên văn 100% khối user-facing,
  đặt ngay sau dòng `✓ [TDQ:<MÃ>]`, áp cho mọi nguyên nhân (hook chặn, sót việc, lỗi tool).
- `skills/tdq-conventions/references/worklog-images.md`: tách phần xử lý ảnh working log ra
  file riêng để `SKILL.md` giữ trong trần 120 dòng của `doc_lint` R6.
- `tests/test_stop_gate.py`: lớp `TestStopGateReprint` — 4 test giữ cụm bắt buộc và trần 300
  ký tự của lời chặn.

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

## 0.3.3 trở về trước

Xem [docs/archive/CHANGELOG-0.1-0.3.md](docs/archive/CHANGELOG-0.1-0.3.md).
