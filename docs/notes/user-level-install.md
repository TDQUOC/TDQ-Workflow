# Hướng dẫn tự cài tdq-workflow ở user-level (thủ công)

Plugin này mặc định chỉ chạy trong repo (`claude --plugin-dir …`) và **không bao giờ tự cài user-level**. Nếu bạn muốn mọi project đều có, tự làm các bước sau.

## 1. Cài qua local marketplace

```bash
# thêm repo này làm marketplace (chạy 1 lần)
claude plugin marketplace add /Users/truongdinhquoc/Documents/TDQWorkflow
# cài plugin ở scope user
claude plugin install tdq-workflow --scope user
```
Kiểm tra: mở session mới bất kỳ → gõ `/tdq-workflow:tdq-status` → phải trả "Chưa có request TDQ nào đang chạy…".

Lưu ý: repo chưa có file `.claude-plugin/marketplace.json` thì lệnh add sẽ báo thiếu — tạo tối thiểu:
```json
{
  "name": "tdq-local",
  "owner": { "name": "TDQ" },
  "plugins": [{ "name": "tdq-workflow", "source": "./" }]
}
```

## 2. Đồng bộ rule working log ở `~/.claude/CLAUDE.md`

Rule user-level hiện ghi log vào `docs/superpowers/workinglog/YYYY-MM-DD.md`, còn plugin dùng `docs/workinglog/YYYY-MM-DD.md`. Nếu giữ nguyên sẽ có 2 chỗ log lệch nhau. Sửa mục 7 trong `~/.claude/CLAUDE.md`:

- Đổi mọi `docs/superpowers/workinglog/` → `docs/workinglog/`.

(Hook `stop_gate`/`edit_gate` của plugin chỉ nhìn `docs/workinglog/`.)

## 3. Thêm instruction TDQ cho MỌI task vào `~/.claude/CLAUDE.md`

Plugin enforce bằng hook, nhưng để Claude chủ động đi đúng workflow (theo `idea.md`) hãy dán block sau vào `~/.claude/CLAUDE.md` (dùng user-level) hoặc `CLAUDE.md` ở root project (dùng per-project với `--plugin-dir`):

```markdown
# TDQ Workflow — quy tắc cho mọi task

## Workflow bắt buộc
- Mọi yêu cầu mới → vào TDQ workflow (skill tdq-start): tóm tắt, đề xuất lane kèm lý do và hỏi người dùng chọn **quick** (việc nhỏ, rõ) hay **full** (Analysis → Spec → Plan → Implement → QC → Report).
- Đóng vai chuyên gia đúng lĩnh vực của yêu cầu; phân tích kỹ code hiện có + research đa hướng trước khi làm; điều gì chưa rõ thì interview người dùng (mỗi câu hỏi kèm option + summary siêu ngắn + đề xuất) đến khi hết mơ hồ — cấm tự đoán, cấm placeholder/mock coi như thật.
- Spec/plan/report viết tiếng Việt. Spec và plan không lập trong cùng 1 turn. Report cuối ≤ 50 dòng.

## Gate duyệt (cứng)
- Chỉ NGƯỜI DÙNG duyệt, bằng cách tự gõ `/tdq-workflow:tdq-approve spec|plan|quick`. Claude không được tự gọi/mô phỏng lệnh này và không được đụng `docs/tdq/state.json` dưới mọi hình thức.
- Chưa duyệt → không sửa file ngoài `docs/` (hook chặn); khi bị chặn thì tiếp tục hoàn thiện spec/plan trong `docs/` và luôn in đúng dòng: `➤ Để duyệt: gõ /tdq-workflow:tdq-approve <spec|plan|quick> · Góp ý: nhắn trực tiếp`.
- Lane quick: trình plan ≤ 10 dòng trong chat → chờ duyệt → append summary plan vào working log TRƯỚC → rồi mới implement.

## Implement
- Sau khi plan được duyệt: implement end-to-end trong 1 turn, không dừng giữa chừng; nếu chờ sub-agent thì phải chờ hoặc đặt trigger tự tiếp tục, không ngắt turn.
- Tick `[x]` vào plan NGAY khi từng task pass test/validate của nó — không gom chờ cuối turn.
- Mỗi task có unit test, đi theo red → green. QC fail → bổ sung task fix vào plan (không cần duyệt lại) và loop đến khi pass toàn bộ.
- Sản phẩm build ra luôn có log service bật mặc định (timestamp, ghi đủ chi tiết sự kiện/data để debug, tắt được qua config).

## Doc & working log
- Doc hệ thống của workflow nằm trong project: `docs/tdq/{requests,questions,research,knowledge,spec,plan,qc,reports}/` — là layer thông tin tin cậy, luôn cập nhật khi có thông tin mới.
- Turn nào có thay đổi repo → append working log `docs/workinglog/YYYY-MM-DD.md` (append CUỐI file; quên sẽ bị hook chặn end turn).

## Git & Graphify
- Tên branch/commit/worktree không bắt đầu bằng `claude|antigravity|gemini|codex`; commit message không chứa "generated with …"/"được tạo cùng/với …"/Co-Authored-By AI; chỉ commit/push khi người dùng yêu cầu.
- Check graphify ready (`graphify --version`); chưa có thì đề xuất người dùng setup theo https://github.com/Graphify-Labs/graphify. Cuối turn có thay đổi code → chạy `graphify extract . --code-only` để graph luôn mới (commit thì hook post-commit tự rebuild).
```

Lưu ý tương thích:
- Block trên viết khớp với hook của plugin (đường log `docs/workinglog/`, lệnh duyệt, state.json) — đừng sửa các đường dẫn/lệnh trong đó.
- Nếu `~/.claude/CLAUDE.md` của bạn đã có các mục trùng (Tavily/research, phong cách ngắn gọn, git naming, working log) thì giữ 1 bản, tránh dán lặp; riêng đường log phải là `docs/workinglog/` (xem mục 2).
- Giới hạn summary trong chat: spec ≤ 10 dòng, plan ≤ 10 dòng (chặt hơn mức trần 50/100 dòng của idea.md — vẫn hợp lệ).

## 4. Gỡ

```bash
claude plugin uninstall tdq-workflow --scope user
claude plugin marketplace remove tdq-local
```

## Lưu ý an toàn
- Hook chặn ghi trực tiếp `docs/tdq/state.json` áp dụng ở mọi project đã bật plugin — duyệt gate chỉ bằng `/tdq-workflow:tdq-approve …`.
- Cập nhật plugin: sửa trong repo này rồi `claude plugin marketplace update tdq-local` (hoặc gỡ/cài lại).
