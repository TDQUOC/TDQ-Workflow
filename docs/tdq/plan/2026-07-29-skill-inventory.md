# PLAN — Kiểm kê & tận dụng skill phụ trợ (0.3.3)

Spec: `../spec/2026-07-29-skill-inventory.md` (bản 1.1, duyệt 2026-07-29) · Trạng thái plan: **HOÀN THÀNH** (QC PASS 14/14)

Mode thực thi: **main** — user chốt "duyệt plan mode main" 2026-07-29. Lý do: các file móc
nhau dạng chuỗi (template → fixture R8 → test → `--pair` → QC dogfood), chia worktree sẽ đổ
công merge vô ích.

Nguyên tắc: mỗi task một test, đi **red → green**; pass là tick `[x]` ngay.
Thứ tự: P1 (script) → P2 (intake) → P3 (khuôn spec/plan) → P4 (lint) → P5 (build) →
P6 (phase table) → P7 (portable) → P8 (đóng gói) → P9 (QC + report).

## Năng lực → task

| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| `security-review` | T9.2 | Mục Q9 trong `docs/tdq/qc/2026-07-29-skill-inventory.md` dán kết quả rà + số phát hiện |

## P1 — `scripts/skill_inventory.py` + test

- [x] **T1.1** Khung CLI + `main()`: nhận `--project <dir>` (mặc định cwd), in bảng
  `name | mô tả ≤60 ký tự | nguồn`, exit 0 khi dữ liệu trục trặc, exit 2 khi sai cú pháp.
  Dùng lại `_warn`/`_info` của `tdq_state.py`. — Test `tests/test_skill_inventory.py::
  test_cli_exit_codes` (không HOME giả → vẫn exit 0; cờ lạ → exit 2).
- [x] **T1.2** Quét `~/.claude/skills/*/SKILL.md` + `<project>/.claude/skills/*/SKILL.md`,
  đọc `name:`/`description:` từ frontmatter. — Test `test_scans_user_and_project_dirs`
  (HOME giả trong tmpdir có 2 skill, project có 1 → ra đúng 3, nguồn đúng).
- [x] **T1.3** Gộp `enabledPlugins` từ 3 tầng: `~/.claude/settings.json` →
  `<project>/.claude/settings.json` → `<project>/.claude/settings.local.json`, tầng sau đè
  tầng trước. — Test `test_settings_three_layers` (user bật, project tắt → không liệt kê).
- [x] **T1.4** Đọc `installed_plugins.json`: chỉ lấy entry có trong `enabledPlugins`;
  **bỏ** entry `scope: "project"` có `projectPath` khác project đang chạy. — Test
  `test_project_scope_filtered` (plugin của project khác không xuất hiện).
- [x] **T1.5** Chỉ đọc thư mục `installPath` của bản đang cài — cấm quét cache. — Test
  `test_reads_installpath_only` (cache giả có 2 version, chỉ version trong
  `installed_plugins.json` được liệt kê, không trùng lặp).
- [x] **T1.6** Cuối bảng luôn in đúng 2 dòng cố định:
  `— Bảng trên chỉ gồm skill trên đĩa.` /
  `— CHÉP THÊM các skill built-in đang thấy trong context vào bảng kiểm kê rồi phán quyết từng dòng.`
  — Test `test_builtin_reminder_lines` (so khớp nguyên văn).
- [x] **T1.7** Log service: `settings.json`/`installed_plugins.json` thiếu hoặc hỏng JSON →
  1 dòng ⚠️ kèm timestamp ra stderr, bảng vẫn in phần còn lại, exit 0; `TDQ_LOG=0` → stderr
  rỗng. — Test `test_warn_on_broken_json` + `test_tdq_log_0_silences`.

## P2 — Bước B0 trong `tdq-intake`

- [x] **T2.1** Viết `skills/tdq-intake/references/skill-inventory.md` (≤200 dòng): khuôn bảng
  kiểm kê 4 cột copy-paste · 4 lý do loại đóng (`khác lĩnh vực` / `spec §3 đã chọn cách khác
  tốt hơn` / `thiếu quyền/công cụ skill đó cần` / `user đã cấm`) · luật "phân vân → DÙNG" ·
  luật >20 skill (gom `KHÔNG` cùng lý do vào 1 dòng) · lệnh chạy script. — Test:
  `test_token_budget::test_reference_files_bounded` + `doc_lint.py skills` exit 0.
- [x] **T2.2** Thêm bước **B0** vào `skills/tdq-intake/SKILL.md` (trước bước "Đọc code", ≤6
  dòng): chạy `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/skill_inventory.py"`, chép thêm skill
  built-in từ context, điền bảng theo khuôn, lưu vào `docs/tdq/knowledge/<slug>.md` mục
  `## Năng lực dùng được`. Lane quick (Phần C): 1 dòng bắt buộc trong mini-plan
  `Năng lực: <danh sách DÙNG hoặc "không có">`. — Test: `doc_lint` R6 (≤120 dòng) +
  `test_skill_shape` xanh.

## P3 — Khuôn spec §3b + hợp đồng 6 trường ở plan

- [x] **T3.1** `skills/tdq-spec/references/spec-template.md`: thêm khối `## 3b. Năng lực &
  công cụ` (bảng 4 cột `Skill|Nguồn|Phán quyết|Dùng ở đâu / Lý do loại` + chú thích "Phân
  vân → DÙNG. Không được xoá mục này kể cả khi mọi dòng là KHÔNG."). — Test:
  `grep "## 3b" spec-template.md` + reference ≤200 dòng.
- [x] **T3.2** `skills/tdq-plan/references/plan-template.md`: thêm bảng `## Năng lực → task`
  + khối hợp đồng 6 trường mẫu (`Dùng/Nạp/Để/Ra/Kiểm/Không dùng cho`, mỗi trường 1 dòng,
  ≤7 dòng/khối) ngay trong khuôn task. `skills/tdq-plan/SKILL.md` thêm 1 luật: mọi `DÙNG`
  ở spec §3b phải nở thành ≥1 khối đủ 6 trường. — Test: `grep` các trường trong template +
  `doc_lint` R6 tdq-plan ≤100 dòng.

## P4 — `doc_lint.py`: R8 + `--pair`

- [x] **T4.1** **R8**: file nằm dưới thư mục `spec/` phải có heading `## 3b` và bảng ≥1 dòng
  dữ liệu; ô phán quyết chỉ nhận `DÙNG`/`KHÔNG`; `KHÔNG` phải kèm 1 trong 4 lý do đóng
  (khớp tiền tố). Không áp cho `skills/`, `portable/`. — Test `test_doc_lint`: fixture spec
  thiếu §3b → R8 lỗi; ô lý do tự chế → lỗi; fixture đủ → im.
- [x] **T4.2** **`--pair <spec> <plan>`**: đọc các dòng `DÙNG` ở §3b của spec; với mỗi skill,
  tìm trong plan khối có `Dùng:` trùng tên; kiểm đủ 6 trường `Dùng/Nạp/Để/Ra/Kiểm/Không dùng
  cho`. Thiếu khối hoặc thiếu trường → in `plan:<dòng>: [R8] skill <tên> thiếu <trường>`,
  exit 1. — Test: cặp đủ → exit 0; cặp thiếu `Kiểm` → exit 1 nêu đúng chữ `Kiểm`; `DÙNG`
  không có khối → exit 1.
- [x] **T4.3** Thêm `<!-- doc-lint: allow R8 -->` vào 4 spec cũ (`2026-07-28-*.md ×3,
  2026-07-29-turn-effect-blindspot.md`). — Test: `python3 scripts/doc_lint.py skills portable
  docs/tdq/spec` exit 0 (spec mới của request này đã có §3b thật).

## P5 — `tdq-build` thi hành hợp đồng

- [x] **T5.1** `skills/tdq-build/SKILL.md` Phần A: chèn vào vòng lặp task bước "Task có khối
  `Dùng:` → nạp skill đó TRƯỚC bước đỏ, làm đúng trường `Để`, cấm lan sang `Không dùng cho`".
  `references/qc.md`: thêm hạng mục "chạy trường **Kiểm** của từng khối; không ra artifact ở
  trường **Ra** → sửa spec §3b thành `KHÔNG — <lý do>` rồi chạy lại `--pair`". — Test:
  `doc_lint` R6 tdq-build ≤150 dòng + `grep "Kiểm"` trong qc.md.

## P6 — `PHASE_TABLE` + `phases.md`

- [x] **T6.1** Thêm đúng 1 mục checklist vào phase `analyze`: chạy `skill_inventory.py`, điền
  bảng vào `knowledge/<slug>.md`; và 1 mục vào `no_state` (lane quick): dòng `Năng lực:` trong
  mini-plan. Sinh lại `phases.md` (skills + portable) bằng lệnh phases-doc. — Test:
  `test_phase_table` xanh + `test_token_budget::test_next_output` (`next` ≤20 dòng mọi phase).

## P7 — Portable

- [x] **T7.1** `portable/workflow/01-intake.md`: bước kiểm kê chạy script + tự liệt kê năng lực
  sẵn có của agent (không có skill system thì ghi công cụ tương đương). `02-spec.md`: §3b có
  cột "tương đương nếu không có skill". Đồng bộ `references/` nếu đổi. — Test:
  `test_portable_sync` + `test_docs_consistency` xanh.

## P8 — Đóng gói 0.3.3

- [x] **T8.1** `CHANGELOG.md` mục `## 0.3.3` · `plugin.json` → `0.3.3` ·
  `claude plugin validate . --strict` PASS · gỡ + cài lại plugin user-level (xoá cache cũ).
  — Test: `test_docs_consistency` (version ↔ changelog) + output validate.

## P9 — QC & report

- [x] **T9.1** Q1–Q8, Q11–Q12 của spec §6: full suite (≥215 test) · script trên máy thật ra
  7 skill · lint · trần token · phase table · portable · validate · không hồi quy hook.
- [x] **T9.2** Q9 — rà bảo mật `skill_inventory.py` (hợp đồng bên dưới).
  - Dùng: `security-review`
  - Nạp: gọi skill `security-review` SAU khi P1 xanh, TRƯỚC khi đóng QC.
  - Để: rà `skill_inventory.py` — script đọc `settings.json`/`installed_plugins.json` và ghép
    đường dẫn từ dữ liệu ngoài (path traversal, symlink, JSON độc).
  - Ra: mục Q9 trong `docs/tdq/qc/2026-07-29-skill-inventory.md` dán kết quả + số phát hiện.
  - Kiểm: `grep -n "Q9" docs/tdq/qc/2026-07-29-skill-inventory.md` có PASS/FAIL kèm bằng chứng.
  - Không dùng cho: các file doc/template/test.
- [x] **T9.3** Q10 — lượt đọc "chỉ làm theo chữ" trên `references/skill-inventory.md` + khuôn
  §3b: điền bảng mẫu mà không suy luận ngoài văn bản; chỗ phải đoán → sửa chữ ngay tại đó.
- [x] **T9.4** Q13 — `doc_lint.py --pair docs/tdq/spec/2026-07-29-skill-inventory.md
  docs/tdq/plan/2026-07-29-skill-inventory.md` → exit 0 (dogfood trên chính cặp file này).
- [x] **T9.5** Q14 — chạy trường **Kiểm** của T9.2; không ra artifact → sửa §3b theo luật.
- [x] **T9.6** Viết `docs/tdq/qc/<slug>.md` (Q1–Q14 + bằng chứng) · report ≤50 dòng ·
  append working log · `graphify extract . --code-only` · hỏi user về commit.

## QC vòng 1 — fix

- [x] **QC1.1** (từ Q9) `skill_inventory.py` in nguyên ký tự điều khiển (ANSI escape, BEL)
  từ `name:`/`description:` của SKILL.md ra terminal → một SKILL.md xấu có thể xoá/ghi đè
  màn hình user. Lọc mọi ký tự < 0x20 (giữ khoảng trắng thường) khỏi name/desc trước khi in.
  — Test `test_skill_inventory.py::test_control_chars_stripped` (desc chứa `\x1b[2J`+`\x07`
  → stdout không còn byte điều khiển, exit 0).

## Definition of Done

Đúng DoD spec §6: đủ 13 đầu ra · Q1–Q14 PASS có bằng chứng · plan tick 100% · report ≤50
dòng · plugin 0.3.3 cài lại được. QC fail → thêm task `QCn.x` vào plan này (không cần duyệt
lại) và loop đến khi pass.

## Việc chờ user (ngoài DoD)

- State vẫn trỏ `2026-07-28-instruction-hardening-7b` — `init 2026-07-29-skill-inventory full`
  sẽ xoá state đó; chỉ chạy khi user đồng ý.
- Commit 0.3.0 → 0.3.3 vẫn chưa có — hỏi lại ở cuối P9.
