# Changelog — bản lưu trữ

Các bản phát hành cũ, cắt ra khỏi `CHANGELOG.md` để file chính không vượt trần 500
dòng của `doc_lint` rule R6. Mới nhất trên cùng, y như file chính.

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

## 0.11.4 trở về 0.7.0

Xem [docs/archive/CHANGELOG-0.7-0.11.4.md](docs/archive/CHANGELOG-0.7-0.11.4.md).

## 0.6.2 trở về trước

Xem [docs/archive/CHANGELOG-0.5-0.6.md](docs/archive/CHANGELOG-0.5-0.6.md)
và [docs/archive/CHANGELOG-0.1-0.3.md](docs/archive/CHANGELOG-0.1-0.3.md).
