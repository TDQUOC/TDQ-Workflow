# tdq-workflow — Plugin Claude Code

Workflow spec-driven giúp agent làm đúng ngay từ lần implement đầu: phân tích kỹ, interview đến khi rõ, spec/plan tiếng Việt phải được **bạn duyệt** trước khi agent được sửa code, QC lặp đến khi pass, report ≤ 50 dòng.

Từ 0.3.0, bộ instruction được viết lại theo hướng **bước đánh số + mốc "Xong khi:" + con trỏ "Bước kế tiếp:"**, để cả model nhỏ chạy local cũng đi đúng workflow, không phải đoán.

## Pipeline

```
Intake ──► Analysis ──► Spec ──► Plan ──► Implement ──► QC ──► Report
 (lane?)   (interview)  [DUYỆT]  [DUYỆT]  (1 turn,      (loop   (≤50 dòng)
                                           tick ngay)    plan)
Chế độ nhanh (express): Analysis ngắn ──► Plan ≤10 dòng trong chat ──► [DUYỆT] ──► ghi log ──► Implement
```

## Cách hook điều khiển agent

Hook **nhắc, không chặn tool**. Mỗi lời nhắc là một dòng mã đóng:

| Mã | Khi nào xuất hiện |
|---|---|
| `TDQ:NEXT` | đầu session / đầu mỗi turn — phase hiện tại + việc kế tiếp |
| `TDQ:APPROVE` | sửa file ngoài `docs/` khi spec/plan/quick chưa được ghi nhận duyệt |
| `TDQ:LOG` | turn có thay đổi repo mà chưa append `docs/workinglog/<ngày>.md` |
| `TDQ:STATE` | định ghi thẳng `docs/tdq/state.json` thay vì dùng CLI |
| `TDQ:GIT` | lệnh git commit/push/branch — kiểm quy ước tên và message |

Instruction bắt agent: thấy `[TDQ:<MÃ>]` → làm việc trong đó TRƯỚC, xong in `✓ [TDQ:<MÃ>]`.

**Verify-by-effect**: hook không tin lời agent. Mỗi turn ghi một sổ tạm (`docs/tdq/.tdq-turn.jsonl`) gồm dòng `remind` (hook đã nhắc mã nào) và dòng `observe` (hiệu ứng thật: đã sửa file gì, đã ghi log chưa, đã gọi CLI state chưa). Hook `Stop` đối chiếu hai bên — agent in `✓` mà không có hiệu ứng thật thì vẫn bị bắt. Điểm **chặn** duy nhất còn lại là working log.

Từ 0.3.1, hook còn **nhìn thẳng vào đĩa**: đầu turn chụp `sha256` của working log hôm nay cùng vân tay `git status` + `git diff HEAD`, cuối turn so lại. Nhờ vậy cách ghi không còn quan trọng — append log bằng `cat >>`/`tee`/`sed -i` vẫn được công nhận, và sửa repo hoàn toàn bằng shell vẫn bị đòi ghi log. Project không phải git repo thì rơi về đối chiếu bằng sổ turn như cũ.

## Duyệt bằng chat thường

Nhắn "duyệt spec", "ok plan mode main", "duyệt nhanh" — không cần cú pháp lệnh. Agent ghi nhận vào state kèm **nguyên văn** câu bạn nói (`spec_approved_by` / `plan_approved_by` / `quick_approved_by`) để còn đối chiếu. Câu mơ hồ ("ok", "spec ok chưa?") KHÔNG được tính là duyệt — agent phải hỏi lại. Duyệt xong lưu sha256 của spec; spec đổi sau khi duyệt sẽ bị cảnh báo.

## Cài đặt

### Cách 1 — qua marketplace (khuyên dùng)

Repo này tự nó là một marketplace: `.claude-plugin/marketplace.json` khai marketplace tên
`tdq-local`, chứa plugin `tdq-workflow`. Trong Claude Code:

```
/plugin marketplace add TDQUOC/TDQ-Workflow
/plugin install tdq-workflow@tdq-local
```

Ghim theo nhánh hoặc tag thì thêm `#<ref>` vào URL đầy đủ (dấu `#`, không phải `@` — `@` là dấu
ngăn giữa tên plugin và tên marketplace lúc install):

```
/plugin marketplace add https://github.com/TDQUOC/TDQ-Workflow.git#v0.40.0
```

Cài sẵn cho cả project — ai trust folder là marketplace tự được thêm, không hỏi lại:

```json
{
  "extraKnownMarketplaces": {
    "tdq-local": {
      "source": { "source": "github", "repo": "TDQUOC/TDQ-Workflow" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": { "tdq-workflow@tdq-local": true }
}
```

### Cách 2 — chạy thẳng từ thư mục, không cài

```bash
claude --plugin-dir /đường/dẫn/tới/TDQWorkflow
```

**Bật workflow cho MỌI task**: dán block instruction trong `docs/notes/user-level-install.md`
(mục 3) vào `~/.claude/CLAUDE.md` (user-level) hoặc `CLAUDE.md` root project (per-project).

### Cách 3 — agent ngoài Claude Code

Marketplace là cơ chế riêng của Claude Code; Codex, Antigravity, Gemini CLI không đọc
`.claude-plugin/`. Ba host đó dùng bản portable dựng sẵn trong repo — `portable_claude/`,
`portable_codex/`, `antigravity_portable/` — mỗi bundle có `README.md` riêng ghi đúng thứ tự cài.
Host nào không có bundle thì đọc đường dự phòng `portable_codex/workflow/01..09-*.md` theo thứ tự.

## Cập nhật

**Auto-update mặc định TẮT** với marketplace bên thứ ba, kể cả cái này. Bật bằng `/plugin` → tab
**Marketplaces** → `tdq-local` → **Enable auto-update**, hoặc đặt sẵn `"autoUpdate": true` như
block JSON ở trên. Bật rồi thì mỗi lần mở session Claude Code làm mới marketplace và cập nhật
plugin trong nền, delay ngẫu nhiên tới 10 phút để session đang chạy không bị đổi bản giữa chừng;
xong nó nhắc chạy `/reload-plugins`, hoặc bản mới tự vào ở lần mở kế tiếp.

Cập nhật tay lúc nào cũng được:

```
/plugin marketplace update tdq-local
/plugin update tdq-workflow@tdq-local
```

### Bump version — bắt buộc mỗi lần release

`plugin.json` có khai `version`, nên plugin bị **ghim** vào đúng chuỗi đó. Push commit mới mà
không đổi số thì máy người dùng thấy version y hệt và **giữ nguyên bản cache** — auto-update coi
như vô hiệu. Vậy mỗi lần release:

1. Sửa `version` trong `.claude-plugin/plugin.json`.
2. Ghi mục mới vào `CHANGELOG.md`.
3. Dựng lại 3 bundle portable: `python3 scripts/build_portable.py` (bundle nhúng số version).
4. Commit rồi `git push`, kèm tag nếu muốn người dùng ghim được:
   `git tag v<số> && git push origin v<số>`.

Ai muốn người dùng nhận bản mới theo từng commit thay vì theo release thì **bỏ hẳn** trường
`version` — Claude Code rơi về commit SHA, có commit mới là có cập nhật.

Nguồn: <https://code.claude.com/docs/en/plugin-marketplaces> ·
<https://code.claude.com/docs/en/discover-plugins>


## Dùng hằng ngày

1. Nêu yêu cầu → agent dùng `tdq-intake`: tóm tắt, đề xuất **chế độ nhanh (express)** (việc nhỏ, rõ) hay **chế độ chuyên sâu (deep)** (feature/phức tạp) và hỏi bạn chọn.
2. Chế độ chuyên sâu (deep): interview đến khi hết mơ hồ → spec (VI) → bạn nhắn "duyệt spec" → plan (VI, task nào cũng có test).
   Agent đề xuất mode thực thi, bạn nhắn "duyệt plan mode main" (hoặc `subagent`).
   Rồi implement end-to-end 1 turn, tick `[x]` ngay khi từng task pass → QC loop → report.
3. Chế độ nhanh (express): plan ≤ 10 dòng trong chat → bạn nhắn "duyệt nhanh" → agent ghi log rồi mới implement.
4. Xem trạng thái bất kỳ lúc nào: skill `tdq-status`, hoặc `python3 scripts/tdq_state.py next`.

## Cấu trúc

| Thư mục | Vai trò |
|---|---|
| `skills/` (6) | tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-status, tdq-conventions |
| `agents/` (3) | tdq-reviewer, tdq-implementer, tdq-qc-tester |
| `hooks/` (5) | edit_gate, bash_gate (nhắc), session_start, prompt_context, stop_gate (chặn working log) |
| `scripts/tdq_state.py` | CLI state: `next \| get \| init \| set \| approve \| reset \| phases-doc` |
| `docs/claude-md-mau.md` | bản mẫu để chép sang `~/.claude/CLAUDE.md` |
| `tests/` | `python3 -m unittest discover tests` |

Bảng phase (nguồn duy nhất là hằng `PHASE_TABLE` trong `scripts/tdq_state.py`) được **sinh tự động** ra `skills/tdq-conventions/references/phases.md` bằng `python3 scripts/tdq_state.py phases-doc` — không sửa tay.

Doc sinh ra trong project của bạn: `docs/tdq/{brief,research,spec,plan,qc,reports}/` + `docs/workinglog/`. `brief/` gộp yêu cầu + kiến thức + hỏi đáp vào một file.

## Quy ước cứng
- Spec/plan/report: tiếng Việt. Không placeholder, không bịa — thiếu thông tin thì hỏi.
- Ghi state CHỈ bằng `scripts/tdq_state.py`, không sửa tay `state.json`.
- Sản phẩm build ra luôn bật sẵn logging service (timestamp, đủ debug) + unit test từng phần.
- Tên branch/commit không bắt đầu bằng `claude|antigravity|gemini|codex`; commit message không chứa dấu vết AI; chỉ commit khi bạn yêu cầu.
- Web search: `tavily-primary` trước, backup chỉ khi lỗi, có ghi nguồn.
