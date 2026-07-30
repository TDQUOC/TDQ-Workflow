# SPEC — TDQ 0.3.0: tuân thủ kiểm được, state đọc được, workflow đủ rõ cho mọi model
<!-- doc-lint: allow R8 -->  <!-- spec viết trước 0.3.3, chưa có mục 3b -->

Phiên bản: 1.2 · Ngày: 2026-07-28 · Lane: full · Trạng thái: **CHỜ DUYỆT**
Nguồn: [request](../requests/2026-07-28-instruction-hardening-7b.md) · [questions](../questions/2026-07-28-instruction-hardening-7b.md) · [research](../research/2026-07-28-instruction-hardening-7b.md) · [knowledge](../knowledge/2026-07-28-instruction-hardening-7b.md)

**Lịch sử sửa**
- v1.0 — bản đầu.
- v1.1 — thêm §2.3 thiết kế state file (theo góp ý user).
- v1.2 — rà kỹ toàn bộ: **sửa lỗi thiết kế ở §2.1** (bỏ việc soát transcript, chuyển sang kiểm bằng hiệu ứng), thêm §2.7 ngân sách token, §2.8 giao thức một turn, §2.9 định nghĩa chính xác; siết lại 3 rule lint quá gắt; QC lên Q1–Q15. Chi tiết 7 phát hiện ở §8.

---

## 1. Mục tiêu & phạm vi

### 1.1 Mục tiêu

0.2.0 bỏ gate cứng nhưng thay bằng **chữ**: hook nhắc, skill dặn, CLAUDE.md dặn — không có gì kiểm được agent có làm theo hay không. 0.3.0 làm ba việc:

1. **Tuân thủ trở nên kiểm được**: mỗi lời nhắc có **mã**; hook ghi lại mã đã phát và **hành động thật đã quan sát được**; cuối turn đối chiếu hai bên.
2. **"Suy ra bước kế tiếp" → "chạy một lệnh"**: `tdq_state.py next` in phase hiện tại, việc kế tiếp, lệnh copy-paste, checklist tick được; `docs/tdq/STATE.md` cho agent đọc thẳng.
3. **Instruction + skills viết lại theo chuẩn model yếu cũng làm đúng**: 9 skill → 5, thân dạng checklist đánh số, chi tiết đẩy sang `references/`, thêm bản **portable** chạy ngoài Claude Code — tất cả trong ngân sách token khai báo trước (§2.7).

### 1.2 In-scope

- §2.1 Giao thức tuân thủ (mã nhắc, sổ turn, kiểm bằng hiệu ứng ở `stop_gate`).
- §2.2 CLI: lệnh mới `next`, `get <key>`; hook dùng lại chính hàm của CLI.
- §2.3 Thiết kế state file: mirror `STATE.md`, ghi nguyên tử, tự phục hồi, bảng quyết định phase.
- §2.4 Skills 9 → 5 (+ `tdq-conventions`), thân gọn + `references/`; xoá hẳn `tdq-approve`.
- §2.5 Bản portable `portable/`.
- §2.6 Lint chất lượng doc + test.
- §2.7 Ngân sách token (có test đo).
- §2.8 Giao thức một turn · §2.9 Định nghĩa chính xác (slug, dấu hiệu duyệt, "repo đổi", exit code).
- §2.10 Dọn dẹp T2–T4, C1–C5, D1–D2 · §2.11 Cập nhật `~/.claude/CLAUDE.md` §10.
- Bump 0.2.0 → **0.3.0**, cập nhật marketplace + bản cài user-level.

### 1.3 Out-of-scope

- **Không** quay lại `permissionDecision: "deny"`.
- **Không** đọc/parse transcript trong bất kỳ hook nào (xem §8, phát hiện P1).
- **Không** tải/chạy model 7B thật để nghiệm thu — thay bằng lint doc. Muốn kiểm thật thì mở request riêng.
- **Không** đổi schema state (giữ `schema_version: 3`); `STATE.md` là bản dẫn xuất, không thêm/bớt khoá.
- **Không** làm khoá đa phiên: xung đột 2 session chỉ **cảnh báo**, không tự giải quyết.
- **Không** thêm hook mới: 5 hook hiện có là đủ (§2.1 chứng minh).
- **Không** đụng repo khác, trừ đúng một file `~/.claude/CLAUDE.md` §10 (bạn đã cho phép, và tôi trình nội dung trước khi ghi).

---

## 2. Đầu ra cụ thể

### 2.1 Giao thức tuân thủ: nhắc có mã → quan sát hiệu ứng → đối chiếu cuối turn

**Nguyên tắc**: bằng chứng tuân thủ là **hiệu ứng quan sát được**, không phải lời tự khai của model. Model yếu rất dễ in "đã làm xong" mà không làm; hook không được tin điều đó.

**5 mã nhắc** (danh sách đóng — thêm mã mới phải sửa spec):

| Mã | Hook phát | Điều kiện phát | Việc agent phải làm | **Hiệu ứng dùng để kiểm** |
|---|---|---|---|---|
| `TDQ:NEXT` | `session_start`, `prompt_context` | Có request đang mở | Chạy `tdq_state.py next`, đi theo output | Sổ turn có sự kiện `next_run` |
| `TDQ:APPROVE` | `prompt_context` | Đang chờ duyệt **và** prompt khớp dấu hiệu duyệt (§2.9.2) | Chạy `approve <target> --by "…"`, hoặc HỎI nếu mơ hồ | `<target>_approved` chuyển `true`, **hoặc** turn có câu hỏi lại (không kiểm được → chỉ nhắc 1 lần) |
| `TDQ:LOG` | `edit_gate` | Sửa file ngoài `docs/workinglog/` mà log hôm nay chưa cập nhật | Append entry cuối `docs/workinglog/<hôm nay>.md` | Sổ turn có `log_written`, **hoặc** mtime file log ≥ mtime file repo mới nhất bị sửa |
| `TDQ:STATE` | `edit_gate`, `bash_gate` | Định Edit/Write `state.json`/`STATE.md`, hoặc lệnh shell ghi thẳng vào chúng | Dùng CLI thay vì sửa file | Sổ turn có `state_cli` |
| `TDQ:GIT` | `bash_gate` | Tên branch/worktree phạm quy, commit message có dấu vết AI, commit/push khi user chưa yêu cầu | Sửa lệnh cho đúng quy ước | Không kiểm được sau khi chạy → chỉ nhắc, tối đa 1 lần/turn/mã |

**Sổ turn** `docs/tdq/.tdq-turn.jsonl` (ẩn, gitignore) — mỗi dòng một JSON:
```json
{"ts":"2026-07-28T23:50:01+07:00","session":"<session_id>","kind":"remind","code":"TDQ:LOG"}
{"ts":"2026-07-28T23:50:07+07:00","session":"<session_id>","kind":"observe","event":"log_written","path":"docs/workinglog/2026-07-28.md"}
```
- Sự kiện `observe` do chính 2 hook PreToolUse ghi (không cần hook mới): `edit_gate` ghi `edit:<path>` và `log_written`; `bash_gate` ghi `state_cli`, `next_run` khi lệnh chứa `tdq_state.py …`.
- `prompt_context` (đầu turn) **xoá mọi dòng của session hiện tại** → phạm vi kiểm gói gọn trong 1 turn.
- Ghi lỗi (đĩa đầy, không quyền) → bỏ qua im lặng, không bao giờ làm hỏng tool call.

**Đối chiếu ở `stop_gate`** (KHÔNG đọc transcript):

| Tình huống | Hành động |
|---|---|
| Có `edit:` ngoài `docs/workinglog/` **và** không có `log_written` **và** log hôm nay cũ hơn file vừa sửa | **`decision: "block"`** — điểm chặn duy nhất, y như 0.2.0 |
| Đã phát `TDQ:NEXT` nhưng không có `next_run` | `additionalContext` nhắc lại, không chặn |
| Đã phát `TDQ:STATE` nhưng không có `state_cli` | `additionalContext` nhắc lại, không chặn |
| Đã phát `TDQ:APPROVE` mà state vẫn chưa duyệt | `additionalContext` nhắc lại, không chặn |
| Đã phát `TDQ:GIT` | `additionalContext` nhắc lại một lần, không chặn |
| `stop_hook_active = true` | Im lặng tuyệt đối (chống lặp vô hạn) |

**Echo `✓ [TDQ:<CODE>]`** vẫn được yêu cầu trong skills — nhưng **chỉ như chỉ dẫn hành vi** (buộc model dừng lại và xác nhận đã làm), **không phải bằng chứng**: không hook nào đọc nó. Vì vậy một model yếu "khai gian" cũng không qua được `stop_gate`. Chi phí: đúng 1 dòng cho mỗi mã thật sự được phát.

**Định dạng lời nhắc** (nội dung `additionalContext`, đúng 3 dòng, tiếng Việt, ≤ 200 ký tự — §2.7):
```
[TDQ:LOG] Append entry vào docs/workinglog/2026-07-28.md trước khi kết thúc turn.
Cách làm: mở file, thêm mục "## HH:MM — <việc>" ở CUỐI file.
Xong thì in: ✓ [TDQ:LOG] đã append docs/workinglog/2026-07-28.md
```

### 2.2 CLI: `next` và `get <key>`

**`tdq_state.py next`** — không tham số, in khối tiếng Việt 5 phần, ≤ 20 dòng:
```
[TDQ:NEXT] <slug> · lane <quick|full> · phase <phase> · Project: <đường dẫn tuyệt đối>
Việc tiếp theo: <đúng 1 việc>
Lệnh:
  <lệnh copy-paste, hoặc "(không có lệnh)">
Checklist (copy vào câu trả lời, tick dần):
- [ ] <bước 1>
- [ ] <bước 2>
Xong khi: <điều kiện đo được để sang phase sau>
```
- `next --brief` → đúng 1 dòng đầu (dùng cho `prompt_context`, §2.7).
- Không có state / không `active_request` → in hướng dẫn `init <slug> <lane>` + công thức slug (§2.9.1), exit 0.
- Nội dung lấy từ **hằng `PHASE_TABLE`** trong `tdq_state.py` (§2.3.4) — mọi phase trong `VALID_PHASES` phải có entry, test khoá cứng.
- `session_start.py` và `prompt_context.py` **import và gọi lại chính hàm này**, không viết lại chữ ở nơi thứ hai.

**`tdq_state.py get <key>`** — in đúng giá trị một khoá (không JSON, không nhãn) để script/agent dùng trực tiếp; khoá không tồn tại → in rỗng + cảnh báo stderr, exit 0. `get` không tham số giữ nguyên hành vi cũ (in JSON đầy đủ).

### 2.3 Thiết kế state file

Nguyên tắc: **state là nguồn sự thật duy nhất về "đang ở đâu"**; agent đọc được mà không cần suy luận, và không có cách nào làm hỏng mà hệ thống không tự gỡ.

#### 2.3.1 Hai file, một nguồn sự thật

| File | Vai trò | Ai ghi | Ai đọc |
|---|---|---|---|
| `docs/tdq/state.json` | Nguồn sự thật, máy đọc, schema 3 | **Chỉ** `tdq_state.py` | script, hook |
| `docs/tdq/STATE.md` | **Mirror người/model đọc** — sinh lại sau MỖI lần ghi | **Chỉ** `tdq_state.py` (tự động, trong cùng hàm `save()`) | agent (Read thẳng), user |

`STATE.md` ≤ 30 dòng, cấu trúc cố định:
```markdown
# TDQ STATE (tự sinh — không sửa tay)
Cập nhật: <ISO> · Project: <đường dẫn> · schema 3

| Trường | Giá trị |
|---|---|
| Request | <slug> |
| Lane | full |
| Phase | spec |
| Spec | docs/tdq/spec/….md — ⏳ chờ duyệt |
| Plan | (chưa có) |
| Mode thực thi | (chưa chốt) |

## Đang ở đâu
<1–2 câu>

## Việc tiếp theo
<y hệt output `next`>
```
Lý do có mirror: harness không chạy được lệnh (hoặc model yếu) chỉ cần `Read docs/tdq/STATE.md` là đủ — không parse JSON, không phải nhớ ý nghĩa 20 khoá.

#### 2.3.2 Quy tắc đọc/ghi cho agent (nhúng vào `tdq-conventions` + `AGENTS.md`)

1. **Đọc**: đọc thẳng `docs/tdq/STATE.md` (ưu tiên) hoặc `state.json`. Không cần lệnh, không cần xin phép.
2. **Ghi**: **chỉ** qua `python3 scripts/tdq_state.py <init|set|approve|reset>`. Cấm Edit/Write vào `state.json` và `STATE.md`.
3. **Không chắc đang ở đâu** → chạy `tdq_state.py next`. Cấm đoán.
4. **Chạy thử/smoke** → bắt buộc `TDQ_PROJECT_DIR=<thư mục tạm>` ở **từng lệnh**; cấm `||` fallback. (Sự cố 2026-07-28: một lệnh smoke thiếu biến này đã ghi đè state thật.)

#### 2.3.3 Yêu cầu kỹ thuật xử lý file

| # | Yêu cầu | Cách làm | Kiểm bằng |
|---|---|---|---|
| S1 | Ghi nguyên tử | ghi `state.json.tmp` cùng thư mục → `os.replace()`; `STATE.md` cùng cách | mock `os.replace` lỗi → file cũ còn nguyên |
| S2 | Tự phục hồi khi hỏng | JSON lỗi → đổi tên `state.json.corrupt-<ts>`, dựng lại từ `default_state()`, cảnh báo stderr, exit 0 | ghi file rác → `get`/`next` vẫn chạy, có file `.corrupt-*` |
| S3 | Backfill, giữ khoá lạ | thiếu khoá → bù từ `default_state()`; khoá lạ → giữ nguyên | test cũ + test khoá lạ |
| S4 | Enum sai không làm chết | `lane`/`phase`/`implement_mode` sai → cảnh báo + coi như `None`/`idle`, vẫn chạy | `phase=xyz` → `next` in hướng dẫn khôi phục, exit 0 |
| S5 | Luôn in đường dẫn project | mọi output `next`/`get`/`STATE.md` có dòng `Project: <tuyệt đối>` | `TDQ_PROJECT_DIR` khác cwd → in đúng đường dẫn đó |
| S6 | Cảnh báo state trùng/mồ côi | mở rộng `find_shadow_states()`: cảnh báo cả khi có `STATE.md` mà không có `state.json` | fixture 2 state |
| S7 | Phát hiện xung đột 2 session | `set/approve` thấy `updated_at` trên đĩa mới hơn giá trị đã đọc → cảnh báo rồi **vẫn ghi** | sửa file giữa read và write |
| S8 | Không exit ≠ 0 vì trạng thái | mọi lỗi trạng thái là cảnh báo; chỉ sai **cú pháp lệnh** mới exit 2 + usage tiếng Việt | quét mọi lệnh × trạng thái xấu |

#### 2.3.4 Bảng quyết định phase (`PHASE_TABLE` — hằng trong code, doc trích lại)

| Phase | Điều kiện vào | Việc **duy nhất** được làm | Lệnh chuyển tiếp | Cấm |
|---|---|---|---|---|
| (không state) | — | Hỏi lane, tạo `requests/<slug>.md` | `init <slug> <lane>` | Sửa code |
| `analyze` | có request, lane full | Đọc code, research, interview đến hết mơ hồ | `set phase=spec` | Viết spec |
| `spec` | analyze xong | Viết spec, `set spec_file=…`, trình duyệt, DỪNG | `approve spec --by "…"` | Viết plan cùng turn |
| `plan` | `spec_approved=true` | Hỏi mode, viết plan, `set plan_file=…`, trình duyệt, DỪNG | `approve plan --mode <…> --by "…"` | Sửa code |
| `implement` | `plan_approved=true` **và** `implement_mode` ≠ null | Làm hết plan trong 1 turn, tick `[x]` ngay từng task | `set phase=qc` | Dừng giữa chừng; tự chọn mode |
| `qc` | implement xong | Chạy DoD, ghi `qc/<slug>.md`; FAIL → thêm task fix vào plan rồi làm tiếp | `set phase=report` | Bỏ qua test fail |
| `report` | QC PASS | Report ≤ 50 dòng, hỏi user commit | `set phase=idle` hoặc `init` mới | Tự commit |
| `idle` | đã xong/chưa mở | Chờ yêu cầu mới | `init <slug> <lane>` | — |
| lane `quick` | — | Plan ≤ 10 dòng trong chat → chờ duyệt → **ghi working log trước** → implement | `approve quick --by "…"` | Implement trước khi ghi log |

Chống lệch: doc trích lại từ hằng; test Q12 so từng dòng.

### 2.4 Skills 9 → 5 (+ conventions)

| Skill mới | Gộp từ | Thân SKILL.md | `references/` |
|---|---|---|---|
| `tdq-intake` | tdq-start + tdq-analyze | ≤ 120 dòng | `lane-decision.md`, `interview.md` |
| `tdq-spec` | tdq-spec | ≤ 100 dòng | `spec-template.md` |
| `tdq-plan` | tdq-plan | ≤ 100 dòng | `plan-template.md` |
| `tdq-build` | tdq-implement + tdq-qc + tdq-report | ≤ 150 dòng | `qc.md`, `report-template.md` |
| `tdq-status` | tdq-status | ≤ 60 dòng | — |
| `tdq-conventions` | tdq-conventions | ≤ 120 dòng | `tavily.md` (giữ), `approval.md`, `reminder-codes.md` |

**Xoá**: `skills/{tdq-approve,tdq-start,tdq-analyze,tdq-implement,tdq-qc,tdq-report}/`.
**Giữ**: 3 agent trong `agents/` — chỉ cập nhật tham chiếu tên skill.

**Khuôn bắt buộc cho mọi SKILL.md** (lint chấm, §2.6):
- Bước đánh số liên tục, thể mệnh lệnh, **mỗi bước một việc**.
- Bước có thao tác hệ thống → kèm khối lệnh copy-paste.
- Kết thúc bằng hai dòng `Xong khi:` và `Bước kế tiếp:`.
- Không dùng từ mơ hồ trong mục bắt buộc, trừ khi ngay sau đó là bảng quyết định.

### 2.5 Bản portable (chạy ngoài Claude Code)

- `portable/AGENTS.md` ≤ 200 dòng: toàn bộ luật + pipeline, mỗi phase một mục; đầu file ghi rõ "harness này KHÔNG có hook → tự chạy `python3 scripts/tdq_state.py next` sau mỗi bước".
- `portable/workflow/{01-intake,02-spec,03-plan,04-build}.md`: chi tiết từng phase, mỗi file ≤ 200 dòng, bỏ phần riêng của Claude Code.
- `portable/README.md` ≤ 10 dòng: cách copy vào project đích, yêu cầu Python 3, cách chạy.
- Chống lệch: test so **danh sách bước** (dòng bắt đầu bằng số) giữa skill và file portable tương ứng.

### 2.6 Lint chất lượng doc

`scripts/doc_lint.py <đường dẫn...>` → in `file:line: [RULE] mô tả`, exit 1 nếu có vi phạm. Tắt từng dòng bằng `<!-- doc-lint: allow R4 -->` ngay trên dòng đó.

| Mã | Rule | Chi tiết / ngưỡng |
|---|---|---|
| R1 | Bước phải đánh số liên tục | Trong mục có tiêu đề chứa "Các bước"/"Steps" |
| R2 | Lệnh phải copy-paste được | Dòng chứa `python3`/`tdq_state.py` phải nằm trong khối ``` **hoặc** trong inline-code/bảng markdown |
| R3 | Có điều kiện ra | Mỗi SKILL.md phải có `Xong khi:` và `Bước kế tiếp:` |
| R4 | Cấm từ mơ hồ | "nếu cần", "tùy ý", "nên cân nhắc", "linh hoạt", "tự quyết" — **chỉ soát trong mục bước/bắt buộc**, bỏ qua nếu trong 3 dòng sau có bảng hoặc `→` |
| R5 | Câu ngắn | Câu > 40 từ |
| R6 | Độ dài | SKILL.md ≤ ngưỡng §2.4; mọi file ≤ 500 dòng |
| R7 | Có mẫu output | `tdq-spec`, `tdq-plan`, `tdq-build` phải link tới ≥ 1 file `references/*template*.md` |

`tests/test_doc_lint.py`: fixture vi phạm/sạch cho **từng** rule + chạy lint trên `skills/**` và `portable/**` → 0 vi phạm.

### 2.7 Ngân sách token (có test đo, không phải khuyến nghị)

| Nơi | Trần | Vì sao |
|---|---|---|
| `SessionStart.additionalContext` | ≤ 12 dòng / 600 ký tự | 1 lần/session, được phép đắt nhất |
| `UserPromptSubmit.additionalContext` | ≤ 3 dòng / 240 ký tự | **Mỗi prompt** — dùng `next --brief`; im lặng khi không có việc |
| `PreToolUse.additionalContext` | ≤ 3 dòng / 200 ký tự, **1 lần/mã/turn** | Có thể bắn hàng chục lần mỗi turn |
| `Stop.additionalContext` | ≤ 4 dòng / 300 ký tự | 1 lần/turn |
| `STATE.md` | ≤ 30 dòng | Agent đọc trọn file |
| `next` | ≤ 20 dòng; `--brief` = 1 dòng | — |
| Tổng `description` của 6 skill | ≤ 900 ký tự | Luôn nằm trong context mọi session |
| Mỗi `references/*.md` | ≤ 200 dòng | Chỉ nạp khi cần |

`tests/test_token_budget.py` đo thật từng mục; vượt trần → FAIL.

### 2.8 Giao thức một turn (dán nguyên vào `tdq-conventions` và `AGENTS.md`)

```
1. Đọc dòng [TDQ:…] nếu có → làm đúng việc trong đó TRƯỚC.
2. Không chắc đang ở đâu → chạy: python3 scripts/tdq_state.py next
3. Làm đúng MỘT việc mà next chỉ ra. Không làm việc của phase sau.
4. Đổi trạng thái chỉ bằng CLI (set/approve/init/reset). Không sửa tay state.
5. Turn có thay đổi repo → append docs/workinglog/<hôm nay>.md ở CUỐI file.
6. In ✓ [TDQ:<CODE>] cho từng mã đã xử lý, rồi kết thúc turn.
```

### 2.9 Định nghĩa chính xác (chống mỗi model hiểu một kiểu)

**2.9.1 Slug** — `YYYY-MM-DD-<kebab, ≤ 5 từ, không dấu tiếng Việt, chỉ a-z0-9->`. Ví dụ: yêu cầu "làm hook nhắc thay vì chặn" ngày 28/07/2026 → `2026-07-28-hook-nhac-thay-chan`. Một slug dùng chung cho mọi thư mục của request đó.

**2.9.2 Dấu hiệu duyệt** — prompt được coi là duyệt khi có **cả hai**: (a) một từ trong {duyệt, ok, đồng ý, chốt, approve, "làm đi", "tiến hành"}; (b) một đối tượng trong {spec, plan, quick, mini-plan} hoặc đại từ trỏ rõ đối tượng đang chờ ("cái này" ngay sau khi trình đúng một thứ). Kèm mode khi có {main, subagent}.
Phản ví dụ **không** phải duyệt: "ok tôi hiểu rồi"; "spec này ổn không?"; "duyệt chưa?"; "ok" trả lời một câu hỏi khác. Mơ hồ → **HỎI**, cấm suy diễn.

**2.9.3 "Repo đổi"** — trong sổ turn có ≥ 1 sự kiện `edit:<path>` với `<path>` **không** thuộc `docs/workinglog/`. Chỉ dùng định nghĩa này; không dùng `git status` (thư mục có thể không phải git repo).

**2.9.4 Exit code** — `0`: mọi trường hợp, kể cả trạng thái xấu (chỉ cảnh báo stderr). `2`: sai cú pháp lệnh, kèm usage tiếng Việt. Không có mã nào khác.

**2.9.5 "Một turn"** — từ lúc nhận prompt của user đến lúc kết thúc lượt trả lời. Quy tắc "implement end-to-end trong 1 turn" nghĩa là không được dừng giữa plan để hỏi "có tiếp không".

### 2.10 Dọn dẹp gộp vào

| Mã | Việc |
|---|---|
| T2 | `docs/notes/user-level-install.md`: viết lại §3 + "Lưu ý an toàn" theo 0.3.0 |
| T3 | Bỏ `docs/tdq/state.json` và `docs/tdq/STATE.md` khỏi `.gitignore` (dấu vết duyệt cần bền); thêm `docs/tdq/.tdq-turn.jsonl` vào gitignore |
| T4 | Tạo `CHANGELOG.md` (0.1.x → 0.2.0 → 0.3.0, mới nhất trên cùng, có bảng ánh xạ tên skill cũ→mới) |
| C1–C2 | Xoá "the hook confirms" / "the hooks enforce it" (nằm trong skill bị viết lại) |
| C3 | `marketplace.json`: bỏ "gate duyệt cứng" |
| C4 | `README.md` viết lại theo 0.3.0 (5 skill, giao thức tuân thủ, `next`, portable) |
| C5 | `tdq-status` hiện thêm `implement_mode` và `*_approved_by` |
| D1 | `idea.md` + `docs/{spec,plan,qc,reports}/` (7 file v0.1) → `docs/archive/v0.1/` + README 3 dòng "lưu trữ, không còn đúng" |
| D2 | Xoá `docs/.DS_Store` |

### 2.11 Cập nhật `~/.claude/CLAUDE.md` §10

Viết lại §10 khớp 0.3.0: hook chỉ nhắc; **luật "thấy `[TDQ:<CODE>]` → làm ngay rồi in `✓ [TDQ:<CODE>]`"**; duyệt bằng chat tự nhiên; agent ghi state qua CLI `approve … --by`; tên skill mới; lệnh `next`; giao thức một turn (§2.8). Mục tiêu ≤ 20 dòng (hiện 8 dòng dài). **Tôi trình nguyên văn trong chat và chờ bạn đồng ý trước khi ghi đè.**

---

## 3. Kiến trúc & lý do chọn

| Quyết định | Lý do (có nguồn) |
|---|---|
| Giữ `allow` + `additionalContext`, không `deny` | Doc chính thức xác nhận PreToolUse nhận `additionalContext` (code.claude.com/docs/en/hooks, mục *Add context for Claude*); issue GitHub #15664 nói ngược là **đã lạc hậu**. Bạn đã chọn hướng "nhắc, không chặn" ở 0.2.0. |
| Kiểm bằng **hiệu ứng**, không đọc transcript | Instruction văn xuôi không bảo đảm được (issue anthropics/claude-code#7777; khảo sát "200 dòng rule bị bỏ qua"; doc Anthropic: CLAUDE.md "shapes behavior, does not guarantee it"). Model yếu còn dễ **khai gian**. Hơn nữa 0.1.8 từng đọc transcript và bị chặn nhầm do transcript trễ — không lặp lại (§8 P1). |
| Vẫn giữ echo `✓ [TDQ:…]` như chỉ dẫn | Doc Anthropic *Skill authoring*: "provide a checklist that Claude can copy into its response and check off"; issue #7777 chỉ ra cần "process gating" — buộc model tự xác nhận từng bước. Rẻ (1 dòng) và giúp model mạnh lẫn yếu bám bước. |
| `next` + `STATE.md` | "Just use scripts": bundle script, bảo model chạy rồi đọc kết quả, thay cho hàng chục dòng guardrail bằng chữ. Markdown là format model nhỏ bám tốt nhất (r/LocalLLaMA). |
| Gộp 9 → 5, thân gọn + `references/` | Progressive disclosure là kiến trúc chính thức của skill; doc khuyến nghị thân < 500 dòng. Ít điểm chuyển tiếp = ít chỗ model yếu lạc. |
| Khuôn "một bước một việc, có lệnh, có điều kiện ra" | Nguồn về model nhỏ: "one prompt, one job", "7B love rigid scaffolding", "only do one task at a time", dùng markdown/delimiter phân tách. |
| Ngân sách token có test | Chi tiết hơn mà không kiểm soát sẽ ăn context mỗi turn; trần + test là cách duy nhất giữ lời hứa "tiết kiệm token". |

**Luồng một turn:**
```
UserPromptSubmit → xoá sổ turn của session → next --brief (≤1 dòng) [+ TDQ:APPROVE nếu khớp]
   ↓
PreToolUse Edit/Write → ghi observe(edit:…, log_written) → nhắc TDQ:LOG/TDQ:STATE nếu cần, LUÔN allow
PreToolUse Bash      → ghi observe(state_cli, next_run)  → nhắc TDQ:STATE/TDQ:GIT nếu cần, LUÔN allow
   ↓
agent làm việc, in ✓ [TDQ:…] (chỉ để tự soát)
   ↓
Stop → đối chiếu remind vs observe trong sổ turn (KHÔNG đọc transcript)
        repo đổi mà chưa ghi log → block
        các mã khác thiếu hiệu ứng → nhắc lại, không chặn
```

---

## 4. Yêu cầu bắt buộc

1. **Log service bật mặc định**: hook ghi sổ turn có timestamp; CLI cảnh báo ra stderr có timestamp. Tắt bằng `TDQ_LOG=0`; mặc định BẬT. Không log nội dung file, không log secret.
2. **Không placeholder**: mọi ví dụ trong skill/portable là lệnh chạy được thật.
3. **Unit test cho từng phần**: giao thức tuân thủ, `next`, `get <key>`, state file, lint, portable-sync, ngân sách token; test cũ vẫn xanh.
4. **Không `"deny"`** trong `hooks/` và `scripts/`; **không đọc transcript** ở bất kỳ hook nào (grep `transcript_path` sạch).
5. **Tương thích ngược**: state 0.2.0 (schema 3) chạy thẳng; lần chạy CLI đầu sinh thêm `STATE.md`.
6. **State không bao giờ là lý do dừng việc** (S1–S8).
7. **Hook không bao giờ làm hỏng tool call**: mọi lỗi nội bộ của hook → thoát 0, im lặng.
8. **Tiếng Việt** cho mọi output tới người dùng.

---

## 5. Ràng buộc & rủi ro

| # | Rủi ro | Xử lý |
|---|---|---|
| RR1 | Đổi tên skill → slash command cũ mất | Bảng ánh xạ cũ→mới trong `CHANGELOG.md` + README; cập nhật `~/.claude/CLAUDE.md` cùng lượt |
| RR2 | Echo làm câu trả lời dài thêm | 1 dòng/mã, tối đa 5 mã, chỉ khi mã thật sự được phát |
| RR3 | Sổ turn ghi sai session (nhiều session cùng project) | Mỗi dòng có `session_id`; chỉ đọc/xoá dòng của session hiện tại |
| RR4 | `next` thành nguồn sự thật thứ hai | `PHASE_TABLE` là hằng duy nhất; skill trỏ về `next` thay vì chép lại; test Q12 |
| RR5 | Lint quá gắt | Tắt được từng dòng; R4 chỉ soát mục bước; R5 ngưỡng rộng 40 từ |
| RR6 | Commit `state.json` + `STATE.md` lộ tiến độ nội bộ | Chỉ có slug/phase/timestamp/câu duyệt của chính bạn, không có secret. Không muốn thì bỏ T3, nói một câu |
| RR7 | Lint không chứng minh model 7B chạy đúng thật | Ghi rõ trong report; muốn kiểm thật thì mở request riêng |
| RR8 | `STATE.md` lệch `state.json` | Cùng một hàm `save()` ghi cả hai; `next` phát hiện lệch → sinh lại + cảnh báo |
| RR9 | `STATE.md` làm nhiễu diff | Chấp nhận (đó là dấu vết bạn muốn); không thích thì gitignore riêng nó |
| RR10 | Bảng phase ở 3 nơi → lệch | Hằng trong code là gốc; test Q12 so từng dòng |
| RR11 | Phục hồi state hỏng = mất dữ liệu | Không xoá: giữ `state.json.corrupt-<ts>`, in đường dẫn để khôi phục tay |
| RR12 | Sổ turn không bị xoá (session chết giữa chừng) → nhắc nhầm ở turn sau | `prompt_context` xoá theo session **và** bỏ qua dòng cũ hơn 6 giờ |
| RR13 | Phạm vi 0.3.0 lớn (≈ 30 file) → dễ vỡ giữa chừng | Plan chia phase theo thứ tự phụ thuộc: CLI → hook → skills → portable → lint → dọn dẹp → đóng gói; mỗi task có test riêng, tick ngay |

---

## 6. Phạm vi QC / test / validate (điều kiện pass đo được)

| # | Hạng mục | Cách kiểm | Pass khi |
|---|---|---|---|
| Q1 | Toàn bộ suite | `cd tests && python3 -m unittest discover .` | 0 fail; ≥ 65 test cũ + test mới |
| Q2 | Giao thức tuân thủ | `tests/test_compliance_protocol.py` | remind ghi đúng sổ; observe ghi đúng sổ; repo đổi + chưa log → `block`; thiếu `next_run`/`state_cli` → `additionalContext`, **không** block; `stop_hook_active` → im lặng; đầu turn xoá sạch dòng cũ |
| Q3 | `next` / `--brief` / `get <key>` | `tests/test_next.py` | Mọi phase trong `VALID_PHASES` có output đủ 5 phần; `--brief` đúng 1 dòng; không state → hướng dẫn `init`; `get <key>` in đúng giá trị; exit 0 mọi trường hợp |
| Q4 | Lint | `tests/test_doc_lint.py` | Mỗi rule R1–R7 có fixture vi phạm + fixture sạch; chạy trên `skills/**`, `portable/**` → 0 vi phạm |
| Q5 | Portable đồng bộ | `tests/test_portable_sync.py` | Danh sách bước skill ↔ file portable khớp |
| Q6 | Không deny, không transcript | `grep -rn '"deny"\|transcript_path' hooks/ scripts/` | Không kết quả |
| Q7 | Cấu hình plugin | `claude plugin validate . --strict` | PASS; `plugin.json` = 0.3.0 |
| Q8 | Bản cài thật | `marketplace update` + `plugin update`, rồi `ls` cache | Hiện 0.3.0; có `skills/tdq-intake`, `skills/tdq-build`, `portable/`; **không** có `skills/tdq-approve` |
| Q9 | Smoke bản cài (mọi lệnh đặt `TDQ_PROJECT_DIR`) | Thủ công, dán output vào QC doc | (a) `next` in đúng phase; (b) edit khi chưa duyệt → `allow` + có `[TDQ:`; (c) repo đổi mà chưa ghi log → Stop `block`; (d) `approve quick` 2 lần → rc 0 |
| Q10 | Dọn dẹp | `ls` / `grep` | `docs/archive/v0.1/` đủ 7 file; hết `docs/.DS_Store`; có `CHANGELOG.md`; `grep -rn "gate duyệt cứng\|hooks enforce\|the hook confirms"` (trừ `docs/archive`, `docs/tdq`, `docs/workinglog`) sạch |
| Q11 | State file | `tests/test_state_file.py` — S1–S8 mỗi mục 1 test | 8/8 PASS |
| Q12 | Bảng phase không lệch | `tests/test_phase_table.py` | Bảng trong `tdq-conventions`, `portable/AGENTS.md`, output `next` khớp 100% `PHASE_TABLE` |
| Q13 | Ngân sách token | `tests/test_token_budget.py` | Mọi mục §2.7 trong trần |
| Q14 | Hook không bao giờ làm hỏng tool call | `tests/test_hook_resilience.py` | State hỏng / thư mục chỉ đọc / payload thiếu khoá → hook exit 0, không stack trace |
| Q15 | Skill mới đủ dùng độc lập | Đọc thủ công + lint | Mỗi SKILL.md tự đứng được: có điều kiện vào, các bước, `Xong khi:`, `Bước kế tiếp:`; không yêu cầu kiến thức ngoài `tdq-conventions` |

**Definition of Done**: Q1–Q15 PASS · `~/.claude/CLAUDE.md` §10 cập nhật sau khi bạn đồng ý nội dung · report ≤ 50 dòng ghi rõ giới hạn RR7 + bảng ánh xạ tên skill.

---

## 7. Câu hỏi còn mở

**Không còn.** Hai điểm bạn có thể muốn bác (nói một câu là tôi sửa):
- **T3** — commit `state.json` + `STATE.md` thay vì gitignore.
- **Echo** — nếu thấy thừa, bỏ hẳn phần in `✓ [TDQ:…]`; việc kiểm tuân thủ không phụ thuộc nó (§2.1).

---

## 8. Ghi chú review (rà v1.2)

Bảy phát hiện khi tự rà bản 1.1, đã sửa hết trong bản này:

| # | Phát hiện | Xử lý |
|---|---|---|
| P1 | **Lỗi thiết kế**: v1.1 bắt `stop_gate` **đọc transcript** tìm dòng echo — đúng cơ chế đã bị xoá ở 0.2.0 vì transcript trễ gây chặn nhầm. Model yếu còn có thể in echo giả. | Đổi sang **kiểm bằng hiệu ứng** qua sổ turn; cấm đọc transcript (§1.3, §4.4, Q6) |
| P2 | Không có ngân sách token — "chi tiết hơn" dễ thành "ăn context mỗi turn" | Thêm §2.7 + test Q13 |
| P3 | Thiếu định nghĩa chính xác: slug, dấu hiệu duyệt, "repo đổi", exit code, "một turn" → mỗi model hiểu một kiểu | Thêm §2.9 (có phản ví dụ) |
| P4 | Thiếu "giao thức một turn" — model yếu cần đúng một trình tự để bám | Thêm §2.8, 6 dòng, nhúng vào conventions + AGENTS.md |
| P5 | 3 rule lint quá gắt/mơ hồ: R2 cấm cả lệnh trong bảng, R4 cấm "có thể" (từ rất thường gặp), R7 phát biểu chung chung | Siết lại: R2 chấp nhận inline-code/bảng; R4 bỏ "có thể", chỉ soát mục bước; R7 nêu đích danh 3 skill |
| P6 | `get <key>` có trong in-scope nhưng không được đặc tả; chưa có `next --brief` cho hook rẻ | Đặc tả cả hai ở §2.2 |
| P7 | Thiếu rủi ro vận hành: sổ turn mồ côi khi session chết; hook lỗi làm hỏng tool call; phạm vi 0.3.0 quá lớn | RR12, RR13, yêu cầu §4.7, test Q14 |

**Chưa spawn `tdq-reviewer`**: session này có chỉ thị không gọi subagent trừ khi bạn yêu cầu. Muốn chạy reviewer trước khi duyệt thì nói một câu.
