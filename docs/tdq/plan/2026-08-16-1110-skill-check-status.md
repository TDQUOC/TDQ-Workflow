# PLAN — Skill `tdq-check-status`: dò request đang dở và tiếp tục không mất dữ liệu

Ngày: 2026-08-16 · Spec: ../spec/2026-08-16-1110-skill-check-status.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — 19 task nối nhau trên đúng ba nhóm file (`scripts/tdq_checkstatus.py`, `skills/tdq-check-status/`, `tests/test_check_status.py`); P2–P3 đều sửa cùng một file script nên tách worktree chỉ đẻ xung đột merge (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT (user duyệt 2026-08-16 11:35, mode main)

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Bộ gom bằng chứng

- [x] **T1.1** (n5 e15m) `scripts/tdq_checkstatus.py` khung CLI: lệnh `report`, cờ
  `--json --project --now`, log service ra stderr, không có `active_request` thì in
  "Chưa có request TDQ nào đang chạy" và thoát 0 (ca D1) — Test:
  `pytest tests/test_check_status.py -k "khung_cli or ca_lech_d1"`
- [x] **T1.2** (n5 e15m) `gom_bang_chung()`: đọc state qua `tdq_state.load()`, kiểm tra tồn
  tại + sha256 của `brief/spec/plan/qc/reports/<slug>.md`, đếm tick qua
  `tdq_state.plan_tick_state()` — Test: `pytest tests/test_check_status.py -k gom_bang_chung`
  - Dùng: `graphify`
  - Để: tra node sẵn có (`plan_tick_state`, `sha256_file`, `repo_status_digest`) trước khi
    viết hàm mới, theo luật "tìm rồi mới tạo". Agent ngoài không có skill system: đọc
    `skills/graphify/SKILL.md` rồi làm theo.
  - Ra: một dòng ghi trong task này liệt kê node tái dùng, hoặc lý do tạo mới
  - Kiểm: `graphify query "plan_tick_state"` trả về node của `scripts/tdq_state.py`
  - Không dùng cho: sửa đồ thị, chạy lại `graphify extract` giữa task
  - Node tái dùng (kết quả `graphify query`): `tdq_state.load` · `sha256_file` ·
    `plan_tick_state` · `find_shadow_states` · `_git`. Tạo mới `_dem_tick()` thay vì dùng
    thẳng `plan_tick_state` vì hàm cũ cố tình không trả MÃ task, mà mã task chính là
    thứ trả lời "đang dừng ở đâu" (ca D4) — `_dem_tick` vẫn gọi lại hàm cũ cho path/sha.
- [x] **T1.3** (n5 e12m) Nhánh git của bộ gom: `git log -20 --format=...` và
  `git status --short`, bọc try/except; repo không phải git thì in `—` kèm lý do và KHÔNG
  làm hỏng phần còn lại (ca D7) — Test:
  `pytest tests/test_check_status.py -k "ca_lech_d7 or khong_git"`
- [x] **T1.4** (n3 e8m) Đọc `docs/workinglog/<hôm nay>.md`: mốc entry cuối và entry đó có
  nhắc slug đang mở không (ca D8) — Test: `pytest tests/test_check_status.py -k ca_lech_d8`

**Xong P1 khi**: `python3 scripts/tdq_checkstatus.py report --json` chạy được trên repo
thật, in đủ khối bằng chứng, thoát 0.

## P2 — Chấm 11 ca lệch

- [x] **T2.1** (n8 e25m) Hằng `CA_LECH` trong script: 11 mã D1–D11, mỗi mã đủ 4 trường
  (dấu hiệu, mức `ok|canh-bao|chan`, câu chẩn đoán, mẫu lệnh vá) — Test:
  `pytest tests/test_check_status.py -k ca_lech_bang` (đủ 11 mã, đủ 4 trường, mức nằm trong 3 giá trị)
- [x] **T2.2** (n8 e20m) D2 — phase trong state lệch bằng chứng đĩa: `phase=spec` mà chưa có
  file spec, `phase=implement` mà plan 0 tick, mọi task `[x]` mà vẫn ở `implement` — Test:
  `pytest tests/test_check_status.py -k ca_lech_d2`
- [x] **T2.3** (n3 e10m) D3 — sha256 spec/plan lệch với lúc duyệt → mức `chan`, chẩn đoán
  "cần duyệt lại" — Test: `pytest tests/test_check_status.py -k ca_lech_d3`
- [x] **T2.4** (n3 e10m) D4 — task `[~]` là chỗ dừng: in đúng mã task; nhiều `[~]` thì hạ
  xuống `canh-bao` và liệt kê đủ — Test: `pytest tests/test_check_status.py -k ca_lech_d4`
- [x] **T2.5** (n3 e8m) D5 — file đã đăng ký trong state nhưng mất trên đĩa → mức `chan` —
  Test: `pytest tests/test_check_status.py -k ca_lech_d5`
- [x] **T2.6** (n3 e8m) D6 — cờ duyệt bật nhưng thiếu `*_approved_by` hoặc `*_approved_at` —
  Test: `pytest tests/test_check_status.py -k ca_lech_d6`
- [x] **T2.7** (n5 e15m) D9 `schema_version` cũ hơn bản hiện tại · D10 thiếu `started_at`
  hoặc `phase_history` rỗng · D11 `state.json` lạc chỗ (`find_shadow_states`) — Test:
  `pytest tests/test_check_status.py -k "ca_lech_d9 or ca_lech_d10 or ca_lech_d11"`
- [x] **T2.8** (n5 e12m) Ba mức kết luận: `TIẾP TỤC ĐƯỢC` (không ca nào quá `ok`) ·
  `VÁ RỒI TIẾP TỤC` (có `canh-bao`, mọi ca đều có lệnh vá) · `CẦN USER QUYẾT` (có `chan`
  hoặc có ca không lệnh vá nào chữa được) — Test:
  `pytest tests/test_check_status.py -k ba_muc_ket_luan`

**Xong P2 khi**: 11 ca có test riêng và cùng xanh trong một lệnh
`pytest tests/test_check_status.py -k ca_lech`.

## P3 — Báo cáo và lệnh vá

- [x] **T3.1** (n5 e15m) `bao_cao_markdown()` in đúng 6 mục cố định, đúng thứ tự: Request ·
  Bằng chứng trên đĩa · Ca lệch phát hiện · Kết luận · Lệnh vá đề xuất · Việc kế tiếp —
  Test: `pytest tests/test_check_status.py -k khuon_bao_cao`
- [x] **T3.2** (n5 e12m) Khối lệnh vá: chỉ sinh lệnh thuộc hai họ `tdq_state.py set …` và
  `tdq_state.py approve …`; hàm chặn nội bộ raise khi mẫu lệnh chứa `init`, `reset`, `rm`,
  `>` hay `mv` — Test: `pytest tests/test_check_status.py -k lenh_va`
- [x] **T3.3** (n3 e8m) `--json` in cùng dữ liệu ở dạng máy đọc (khoá: `slug`, `phase`,
  `ket_luan`, `ca_lech[]`, `lenh_va[]`) — Test:
  `pytest tests/test_check_status.py -k bao_cao_json`

**Xong P3 khi**: `python3 scripts/tdq_checkstatus.py report` trên repo thật in đủ 6 mục và
`report --json` parse được bằng `json.loads`.

## P4 — Skill và tài liệu chỉ dẫn

- [x] **T4.1** (n5 e20m) `skills/tdq-check-status/SKILL.md`: frontmatter đúng tên, bước đánh
  số liên tục từ 1, có `Xong khi:` và `Bước kế tiếp:`, dưới trần dòng; nêu rõ luật một cổng
  gật và luật cấm `init`/`reset` — Test:
  `pytest tests/test_skill_shape.py -k check_status`
  - Dùng: `skill-creator`
  - Để: dựng đúng cấu trúc thư mục skill + frontmatter chuẩn Claude Code cho skill mới.
    Agent ngoài không có skill system: đọc `skills/skill-creator/SKILL.md` rồi làm theo.
  - Ra: `skills/tdq-check-status/SKILL.md` tồn tại, có frontmatter `name` + `description`
  - Kiểm: `python3 scripts/doc_lint.py skills/tdq-check-status/SKILL.md` exit 0
  - Không dùng cho: sinh thêm skill khác, sửa 6 skill `tdq-*` đang có
  - Dùng: `plugin-dev:skill-development`
  - Để: viết dòng `description` đủ tín hiệu trigger (session mới, đổi máy, agent khác làm
    hộ) và chia nội dung theo progressive disclosure. Agent ngoài: đọc
    `skills/plugin-dev/skill-development/SKILL.md` rồi làm theo.
  - Ra: dòng `description` trong frontmatter nêu đủ 3 use case của user
  - Kiểm: `grep -c "description:" skills/tdq-check-status/SKILL.md` ra 1
  - Không dùng cho: đổi `description` của 6 skill `tdq-*` đang có
- [x] **T4.2** (n3 e12m) `skills/tdq-check-status/references/report-template.md`: khuôn báo
  cáo 6 mục, có ví dụ điền sẵn cho một ca thật — Test:
  `pytest tests/test_check_status.py -k khuon_bao_cao_file`
- [x] **T4.3** (n5 e15m) `skills/tdq-check-status/references/bang-lech.md`: bảng 11 ca D1–D11
  khớp từng chữ với hằng `CA_LECH` trong script — Test:
  `pytest tests/test_check_status.py -k bang_lech` (so mã và mức giữa hai nơi)
  - Dùng: `tdq-conventions`
  - Để: bảng ca lệch chỉ TRỎ về luật state/duyệt của conventions, không chép lại luật.
    Agent ngoài: đọc `portable/AGENTS.md` mục State và Ghi nhận duyệt rồi làm theo.
  - Ra: `references/bang-lech.md` có ít nhất một liên kết tới `tdq-conventions`
  - Kiểm: `grep -c "tdq-conventions" skills/tdq-check-status/references/bang-lech.md` ≥ 1
  - Không dùng cho: sửa nội dung `skills/tdq-conventions/SKILL.md`
- [x] **T4.4** (n2 e6m) `skills/tdq-status/SKILL.md` thêm đúng một dòng: phát hiện lệch thì
  trỏ sang `tdq-check-status` — Test:
  `pytest tests/test_check_status.py -k status_tro_sang`
  - Chạm: `skills/tdq-status/SKILL.md` → không node mã nguồn nào phụ thuộc (file tài liệu)
  - Dùng: `tdq-status`
  - Để: giữ ranh giới hai skill — `tdq-status` vẫn báo nhanh, chỉ thêm con trỏ. Agent
    ngoài: đọc `skills/tdq-status/SKILL.md` rồi làm theo.
  - Ra: một dòng mới trong `skills/tdq-status/SKILL.md` nhắc tên skill mới
  - Kiểm: `grep -c "tdq-check-status" skills/tdq-status/SKILL.md` ra 1
  - Không dùng cho: chuyển logic khôi phục sang `tdq-status`

**Xong P4 khi**: `pytest tests/test_skill_shape.py -q` xanh và ba file skill mới đều lint sạch.

## P5 — Bản portable và đăng ký ngưỡng

- [x] **T5.1** (n3 e12m) `portable/workflow/05-check-status.md` cùng số bước và cùng bảng ca
  lệch với bản `skills/`; thêm một dòng vào bảng phase của `portable/AGENTS.md` — Test:
  `pytest tests/test_check_status.py -k portable`
  - Chạm: `portable/AGENTS.md` → không node mã nguồn nào phụ thuộc (file tài liệu)
- [x] **T5.2** (n2 e6m) Đăng ký trần dòng skill mới vào `doc_lint.SKILL_LINE_LIMITS` và danh
  sách skill của `tests/test_skill_shape.py` — Test:
  `python3 scripts/doc_lint.py skills/tdq-check-status/SKILL.md` exit 0 và
  `pytest tests/test_doc_lint.py -q` xanh
  - Chạm: `scripts/doc_lint.py` `SKILL_LINE_LIMITS` → `tests/test_skill_shape.py`,
    `tests/test_doc_lint.py` (nguồn: hai test đọc chung hằng này)

**Xong P5 khi**: bản portable và bản skills khớp bước, hai test lint/shape xanh.

## P6 — Log & test bắt buộc

- [x] **T6.1** (n3 e8m) Log service của `tdq_checkstatus.py`: timestamp ra stderr, bật mặc
  định, tắt bằng `TDQ_LOG=0` — Test:
  `TDQ_LOG=0 python3 scripts/tdq_checkstatus.py report 2>err >/dev/null; wc -l < err` ra 0
- [x] **T6.2** (n8 e25m) `tests/test_check_status.py` phủ đủ 21 hạng mục Q1–Q21 của spec §6 —
  Test: `pytest tests/test_check_status.py -q` xanh và `python3 -m pytest -q` không hồi quy
- [x] **T6.3** (n3 e8m) Ngưỡng thời gian: `report` trên repo thật dưới 2,0 giây (giới hạn
  `git log` 20 commit) — Test: `time python3 scripts/tdq_checkstatus.py report` dưới 2,0 giây

**Xong P6 khi**: `python3 -m pytest -q` xanh với số test ≥ 639 + số test mới.

## P7 — Phát hành và đóng request

- [x] **T7.1** (n3 e8m) CHANGELOG mục 0.21.0 + `.claude-plugin/plugin.json` lên 0.21.0 —
  Test: `grep -c "0.21.0" CHANGELOG.md .claude-plugin/plugin.json` cả hai ≥ 1
- [x] **T7.2** (n5 e15m) QC: chạy 21 hạng mục + QC-F1/F2/F3 + `code_rule_scan.py` (clean code
  BẬT), ghi `docs/tdq/qc/<slug>.md`, cộng một lượt kiểm độc lập bằng agent `tdq-qc-tester`
  theo lộ trình spec §1b — Test: `python3 scripts/doc_lint.py docs/tdq/qc/<slug>.md` exit 0
  - Dùng: `tdq-build`
  - Để: chạy đúng ba bước QC và bốn bước report của skill, không làm theo trí nhớ. Agent
    ngoài: đọc `portable/workflow/04-build.md` rồi làm theo.
  - Ra: `docs/tdq/qc/2026-08-16-1110-skill-check-status.md` và `docs/tdq/reports/<slug>.md`
  - Kiểm: `python3 scripts/doc_lint.py docs/tdq/qc/<slug>.md docs/tdq/reports/<slug>.md` exit 0
  - Không dùng cho: tự commit thành quả cuối khi user chưa yêu cầu
- [x] **T7.3** (n3 e10m) Report `docs/tdq/reports/<slug>.md` có bảng thời gian thật của
  request này (`tdq_timing.py show`) — Test:
  `python3 scripts/doc_lint.py docs/tdq/reports/<slug>.md` exit 0 và report có mục `## Thời gian`
  - Dùng: `tdq-plan`
  - Để: nếu QC FAIL thì thêm task fix vào mục `## QC vòng N — fix` của chính file plan này
    theo đúng khuôn task, không cần duyệt lại. Agent ngoài: đọc
    `portable/workflow/03-plan.md` rồi làm theo.
  - Ra: mục `## QC vòng N — fix` trong plan này (chỉ khi có FAIL)
  - Kiểm: `python3 scripts/doc_lint.py --pair docs/tdq/spec/<slug>.md docs/tdq/plan/<slug>.md` exit 0
  - Không dùng cho: viết lại plan hay đổi phạm vi spec đã duyệt
- [x] **T7.4** (n2 e5m) Ghi một fact ngắn về cơ chế khôi phục vào bộ nhớ dài hạn — Test:
  `mcp__mem0__search_memories` với từ khoá "tdq-check-status" trả về fact vừa ghi
  - Dùng: `mem0-memory` (mcp)
  - Để: lưu đúng một fact ngắn "đĩa là bằng chứng, state là lời khai; lệnh vá chỉ set/approve".
    Agent ngoài: bỏ task này nếu harness không có MCP mem0, ghi một dòng lý do vào report.
  - Ra: một memory trong project `TDQWorkflow`
  - Kiểm: `mcp__mem0__search_memories` query "tdq-check-status" trả ≥ 1 kết quả
  - Không dùng cho: lưu nội dung spec/plan, lưu log hội thoại

**Xong P7 khi**: mọi task tick `[x]`, QC PASS, report đã ghi và user đã được hỏi về commit.

## Definition of Done

Trỏ về §6 của spec (Q1–Q21). Liệt kê lại lệnh kiểm:

| # | Lệnh kiểm |
|---|---|
| Q1 | `pytest tests/test_skill_shape.py -k check_status` |
| Q2 | `pytest tests/test_check_status.py -k ca_lech_d1` |
| Q3 | `pytest tests/test_check_status.py -k ca_lech_d2` |
| Q4 | `pytest tests/test_check_status.py -k ca_lech_d3` |
| Q5 | `pytest tests/test_check_status.py -k ca_lech_d4` |
| Q6 | `pytest tests/test_check_status.py -k ca_lech_d5` |
| Q7 | `pytest tests/test_check_status.py -k ca_lech_d6` |
| Q8 | `pytest tests/test_check_status.py -k ca_lech_d7` |
| Q9 | `pytest tests/test_check_status.py -k ca_lech_d8` |
| Q10 | `pytest tests/test_check_status.py -k ca_lech_d9` |
| Q11 | `pytest tests/test_check_status.py -k ca_lech_d10` |
| Q12 | `pytest tests/test_check_status.py -k ca_lech_d11` |
| Q13 | `pytest tests/test_check_status.py -k khuon_bao_cao` |
| Q14 | `pytest tests/test_check_status.py -k lenh_va` |
| Q15 | `pytest tests/test_check_status.py -k portable` |
| Q16 | `pytest tests/test_check_status.py -k khong_git` |
| Q17 | `TDQ_LOG=0 python3 scripts/tdq_checkstatus.py report 2>err >/dev/null; wc -l < err` ra 0 |
| Q18 | `time python3 scripts/tdq_checkstatus.py report` dưới 2,0 giây |
| Q19 | `python3 -m pytest -q` không đỏ, số test ≥ 639 |
| Q20 | `python3 scripts/doc_lint.py <các file tài liệu đã sửa>` exit 0 |
| Q21 | `grep -c "0.21.0" CHANGELOG.md .claude-plugin/plugin.json` cả hai ≥ 1 |
| QC-F1 | `python3 -m pytest -q` toàn suite |
| QC-F2 | Hồi quy mọi vùng `Chạm:`: `pytest tests/test_doc_lint.py tests/test_skill_shape.py tests/test_rules_library.py -q` |
| QC-F3 | Bốn ràng buộc kiến trúc spec §5: `tdq_checkstatus.py` không ghi `state.json`; file mới nằm trong `scripts/`; skill chỉ nhắc tên lệnh; `portable/` khớp bước với `skills/` |
| QC-F4 | Clean code BẬT: `python3 scripts/code_rule_scan.py <file đã đổi>` không còn LỖI |
| QC-F5 | Một lượt kiểm độc lập bằng agent `tdq-qc-tester` (lộ trình spec §1b) |

## QC vòng 1 — fix

Nguồn: lượt kiểm độc lập của agent `tdq-qc-tester` (QC-F5). Q1–Q21 và QC-F1..F4 đều PASS,
nhưng 5 lỗ hổng nằm NGOÀI phạm vi test hiện có, hai trong đó phá thẳng luật "không mất dữ liệu".

- [x] **QC1.1** (n8) `state.json` hỏng cú pháp mà spec/plan còn trên đĩa: bộ dò đang báo
  `TIẾP TỤC ĐƯỢC` + "mở request mới" → agent yếu sẽ chạy lệnh khởi tạo lại và mất cả
  request. Phải phân biệt "không có state" với "có state nhưng đọc không được", ca sau là
  mức `chan` — Test: `pytest tests/test_check_status.py -k state_hong`
- [x] **QC1.2** (n5) `schema_version` là chuỗi → `TypeError`, exit 1, mất luôn báo cáo;
  thiếu hẳn trường thì D9 im. Ép kiểu an toàn, không đọc được coi như schema 0 — Test:
  `pytest tests/test_check_status.py -k schema_la`
- [x] **QC1.3** (n5) `kiem_lenh_va()` lọt `>docs/x.md` (không space), `;mv …`,
  `git checkout --`, `truncate`. Đổi từ danh sách đen sang danh sách trắng khớp NGUYÊN
  chuỗi, chặn mọi ký tự shell — Test: `pytest tests/test_check_status.py -k lenh_va`
- [x] **QC1.4** (n3) D7 một mình đẩy kết luận sang `CẦN USER QUYẾT` rồi in "Trình các ca
  mức `chan`" trong khi không có ca `chan` nào. Sửa câu việc kế tiếp cho đúng thứ đang có
  — Test: `pytest tests/test_check_status.py -k viec_ke_tiep`
- [x] **QC1.5** (n3) Ba chỗ nhỏ: chỉ rỗng `phase_history` thì `set started_at` không chữa
  được (hạ xuống `ok`); D8 phải soi entry CUỐI của working log đúng như T1.4 và in nó ra
  báo cáo; `bang-lech.md` nói rõ giá trị schema lấy từ `SCHEMA_HIEN_TAI` — Test:
  `pytest tests/test_check_status.py -k "ca_lech_d10 or ca_lech_d8"`
