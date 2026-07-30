# Hướng dẫn tự cài tdq-workflow ở user-level (thủ công)

Plugin này mặc định chỉ chạy trong repo (`claude --plugin-dir …`) và **không bao giờ tự cài user-level**. Nếu bạn muốn mọi project đều có, tự làm các bước sau.

## 1. Cài qua local marketplace

```bash
# thêm repo này làm marketplace (chạy 1 lần)
claude plugin marketplace add /Users/truongdinhquoc/Documents/TDQWorkflow
# cài plugin ở scope user
claude plugin install tdq-workflow --scope user
```
Kiểm tra: mở session mới bất kỳ → skill `tdq-status` phải trả "Chưa có request TDQ nào đang chạy…".

Lưu ý: repo chưa có file `.claude-plugin/marketplace.json` thì lệnh add sẽ báo thiếu — tạo tối thiểu:
```json
{
  "name": "tdq-local",
  "owner": { "name": "TDQ" },
  "plugins": [{ "name": "tdq-workflow", "source": "./" }]
}
```

## 2. Đồng bộ rule working log ở `~/.claude/CLAUDE.md`

Nếu rule user-level của bạn ghi log vào chỗ khác (ví dụ `docs/superpowers/workinglog/`) thì sẽ có 2 chỗ log lệch nhau. Đổi mọi đường dẫn log về `docs/workinglog/YYYY-MM-DD.md` — hook `stop_gate`/`edit_gate` của plugin chỉ nhìn `docs/workinglog/`.

## 3. Thêm instruction TDQ cho MỌI task vào `~/.claude/CLAUDE.md`

Hook chỉ **nhắc**, không ép. Để agent chủ động đi đúng workflow ngay từ lúc nhận yêu cầu, dán block sau vào `~/.claude/CLAUDE.md` (user-level) hoặc `CLAUDE.md` ở root project (per-project với `--plugin-dir`):

```markdown
# TDQ Workflow — quy tắc cho mọi task

## Giao thức tuân thủ (quan trọng nhất)
- Thấy dòng `[TDQ:<MÃ>]` do hook chèn vào ngữ cảnh → **làm đúng việc trong đó TRƯỚC** mọi việc khác, xong in `✓ [TDQ:<MÃ>] <đã làm gì>`. Hook kiểm bằng hiệu ứng thật, không tin dòng `✓` suông.
- Đầu mỗi turn chạy `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" next` và làm đúng việc nó in ra. Ghi state CHỈ bằng CLI đó — không sửa tay `docs/tdq/state.json`.

## Workflow bắt buộc
- Mọi yêu cầu mới → skill `tdq-intake`: tóm tắt, đề xuất lane kèm lý do và hỏi người dùng chọn **quick** (việc nhỏ, rõ) hay **full** (Analysis → Spec → Plan → Implement → QC → Report). Xem trạng thái: skill `tdq-status`.
- Đóng vai chuyên gia đúng lĩnh vực; phân tích kỹ code hiện có + research đa hướng trước khi làm; điều gì chưa rõ thì interview người dùng (mỗi câu hỏi kèm option + summary siêu ngắn + đề xuất) đến khi hết mơ hồ — cấm tự đoán, cấm placeholder/mock coi như thật.
- Spec/plan/report viết tiếng Việt. Spec và plan không lập trong cùng 1 turn. Report cuối ≤ 50 dòng.

## Duyệt
- Người dùng duyệt bằng **chat thường** ("duyệt spec", "ok plan mode main", "duyệt quick"). Câu mơ hồ ("ok", "spec ok chưa?") KHÔNG tính là duyệt → phải hỏi lại.
- Ghi nhận ngay khi được duyệt: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve <spec|plan|quick> [--mode main|subagent] --by "<nguyên văn câu người dùng>"`.
- Trình spec/plan xong thì in đúng dòng: `➤ Duyệt: nhắn "duyệt spec" · Góp ý: nhắn trực tiếp` rồi DỪNG turn.
- Lane quick: trình plan ≤ 10 dòng trong chat → chờ duyệt → append summary plan vào working log TRƯỚC → rồi mới implement.

## Implement
- Sau khi plan được duyệt: implement end-to-end trong 1 turn, không dừng giữa chừng; nếu chờ sub-agent thì phải chờ hoặc đặt trigger tự tiếp tục, không ngắt turn.
- Mode thực thi (`main` hay `subagent`) do NGƯỜI DÙNG chọn lúc duyệt; thiếu mode → hỏi, đừng tự chọn.
- Tick `[x]` vào plan NGAY khi từng task pass test/validate của nó — không gom chờ cuối turn.
- Mỗi task có unit test, đi theo red → green. QC fail → bổ sung task fix vào plan (không cần duyệt lại) và loop đến khi pass toàn bộ.
- Sản phẩm build ra luôn có log service bật mặc định (timestamp, ghi đủ chi tiết sự kiện/data để debug, tắt được qua config).

## Doc & working log
- Doc hệ thống của workflow nằm trong project: `docs/tdq/{requests,questions,research,knowledge,spec,plan,qc,reports}/` — là layer thông tin tin cậy, luôn cập nhật khi có thông tin mới.
- Turn nào có thay đổi repo → append working log `docs/workinglog/YYYY-MM-DD.md` (append CUỐI file). Đây là điểm CHẶN duy nhất: quên thì không kết thúc turn được.

## Git & Graphify
- Tên branch/commit/worktree không bắt đầu bằng `claude|antigravity|gemini|codex`; commit message không chứa "generated with …"/"được tạo cùng/với …"/Co-Authored-By AI; chỉ commit/push khi người dùng yêu cầu.
- Check graphify ready (`graphify --version`); chưa có thì đề xuất người dùng setup theo https://github.com/Graphify-Labs/graphify. Cuối turn có thay đổi code → chạy `graphify extract . --code-only` để graph luôn mới (commit thì hook post-commit tự rebuild).
```

Lưu ý tương thích:
- Block trên viết khớp với hook của plugin (đường log `docs/workinglog/`, lệnh CLI state, 5 mã nhắc) — đừng sửa các đường dẫn/lệnh trong đó.
- Nếu `~/.claude/CLAUDE.md` của bạn đã có các mục trùng (Tavily/research, phong cách ngắn gọn, git naming, working log) thì giữ 1 bản, tránh dán lặp; riêng đường log phải là `docs/workinglog/` (xem mục 2).
- Giới hạn summary trong chat: spec ≤ 50 dòng, plan ≤ 10 dòng.

## 4. Dùng ngoài Claude Code

Harness khác (Codex, Antigravity…) không có hook: copy `portable/AGENTS.md`, `portable/workflow/` và `scripts/tdq_state.py` sang project đích — xem `portable/README.md`.

## 5. Gỡ

```bash
claude plugin uninstall tdq-workflow --scope user
claude plugin marketplace remove tdq-local
```

## Lưu ý an toàn
- Hook **không chặn tool** vì lý do chưa duyệt — chỉ nhắc. Điểm chặn duy nhất là working log chưa ghi.
- Hook không đọc transcript và không bao giờ trả `deny`; nó kiểm bằng hiệu ứng thật ghi trong `docs/tdq/.tdq-turn.jsonl` (file tạm mỗi turn).
- Nên thêm `docs/tdq/.tdq-turn.jsonl` vào `.gitignore` của project: đó là file tạm, không phải tài liệu. Từ 0.3.2 nó không còn ảnh hưởng tới việc hook nhận diện thay đổi (cả `docs/tdq/` đã bị loại trừ khỏi vân tay repo), nhưng để lại thì `git status` lúc nào cũng bẩn.
- Cập nhật plugin: sửa trong repo này rồi `claude plugin marketplace update tdq-local` + `claude plugin update tdq-workflow@tdq-local`.
