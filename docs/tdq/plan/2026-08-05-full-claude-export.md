# PLAN — Full claude export (multi-repo local dependency)

Ngày: 2026-08-05 · Spec: ../spec/2026-08-05-full-claude-export.md (bản 1.0, ĐÃ DUYỆT) · Lane: full.
Mode thực thi: main — mọi task đụng chung 1 file (`scripts/claude_export.py`) · phụ
thuộc chặt tuần tự (config → clone → skills/plist → manifest/README/check → test →
build thật trên máy host) · bước cuối phải chạy trên đúng máy nguồn, không isolate
được bằng git worktree · làm liền mạch trong hội thoại này nhanh hơn chia agent song song.
Trạng thái plan: HOÀN THÀNH

## Năng lực → task
| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| `graphify` | T6.1 | `graphify-out/graph.json`, `manifest.json` cập nhật, khớp code mới |

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: viết test trước (đỏ) → code → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Config danh sách repo local
- [x] **T1.1** Tạo `claude-export/local-repos.json` — `{"tdqworkflow-repo": "<abs path repo hiện tại>", "mem0-repo": "/Users/truongdinhquoc/Documents/mem0R&D"}` — Test: `python3 -c "import json; d=json.load(open('claude-export/local-repos.json')); assert set(d)=={'tdqworkflow-repo','mem0-repo'}; import os; assert all(os.path.isdir(p) for p in d.values())"`

**Xong P1 khi**: file JSON hợp lệ, cả 2 path tồn tại trên máy.

## P2 — Multi-repo clone trong `claude_export.py`
- [x] **T2.1** Đổi `clone_repo`/`cmd_build`: đọc `local-repos.json`, loop `git clone --quiet` từng repo vào `<dest>/<tên>`, log 1 dòng cảnh báo nếu repo dirty (giữ hành vi hiện có) — Test: test mới `test_two_local_repos_are_cloned` — bundle có cả `tdqworkflow-repo/.git` và `mem0-repo/.git`
- [x] **T2.2** `copy_repo_memory` áp dụng cho từng repo có `.remember/` (không chỉ repo đầu tiên) — Test: `test_remember_copied_for_every_repo_with_it` — `.remember/` của repo có untracked file được copy đúng đích, `tmp/`/`logs/` vẫn bị lọc
- [x] **T2.3** Thêm dòng `log()` cho bước đọc `local-repos.json` (số repo tìm thấy) và mỗi lần clone xong 1 repo — Test: `test_build --verbose` output chứa tên cả 2 repo ở mức debug

**Xong P2 khi**: build thử trong `tempfile` sinh đúng 2 thư mục repo, mỗi cái còn nguyên `.git`.

## P3 — Tổng quát `skills/` + copy LaunchAgent plist
- [x] **T3.1** Đổi `CONFIG_DIRS`: bỏ dòng cứng `("skills/graphify", "config/skills-graphify")`, thay bằng bước quét `os.listdir(claude_home/"skills")`, mỗi thư mục con → `config/skills-<tên>/` — Test: `test_every_skill_subdir_is_copied` — bundle giả có 2 skill (`graphify`, `mem0-memory`) → cả 2 xuất hiện trong `config/`
- [x] **T3.2** Thêm bước copy `~/Library/LaunchAgents/<Label khớp tên repo trong local-repos.json>.plist` vào `<dest>/config/launch-agents/` (biết tên file qua quy ước `com.<tên repo bỏ hậu tố -repo>.gateway.plist`; không có thì bỏ qua, không lỗi) — Test: `test_matching_launch_agent_plist_is_copied` — sha256 file trong bundle khớp file nguồn

**Xong P3 khi**: bundle giả có `config/skills-mem0-memory/SKILL.md` và `config/launch-agents/com.mem0.gateway.plist`.

## P4 — Manifest/README/check hỗ trợ N repo
- [x] **T4.1** `write_manifest`: thay khoá đơn `repo_commit` bằng `repos: {<tên>: {"source": <path>, "commit": <sha>}}` (giữ `repo_commit` = SHA của `tdqworkflow-repo` để không vỡ tương thích ngược với `MANIFEST.template.json` hiện có 8 khoá) — Test: `test_manifest_lists_every_repo` — `manifest["repos"]` có 2 entry, mỗi entry có `source` + `commit` đúng
- [x] **T4.2** `write_readme`: thêm bảng "Repo local dependency" (tên, path nguồn, commit) vào `README.md` sinh ra — Test: `test_readme_lists_every_repo` — README chứa cả `tdqworkflow-repo` và `mem0-repo`
- [x] **T4.3** `cmd_check`: loop `manifest["repos"]` · so `git rev-parse HEAD` của từng path nguồn với `commit` đã ghi · báo lệch riêng từng repo (dùng đúng khuôn `(rel, why)` hiện có) — Test: `test_check_reports_drift_per_repo` — sửa 1 commit ở 1 trong 2 repo giả → `check` chỉ báo lệch đúng tên repo đó

**Xong P4 khi**: `check` chạy trên bundle giả 2 repo báo đúng 0 mục lệch lúc sạch, đúng 1 mục lệch khi 1 repo lệch commit.

## P5 — Log & test bắt buộc
- [x] **T5.1** Rà toàn bộ hàm mới (T2.1–T4.3) đều có `log()` ở bước chính (không chỉ debug) — Test: `grep -c "log(" scripts/claude_export.py` tăng so với bản gốc, chạy `build` (không `--quiet`) in ra tên 2 repo + số plist đã copy
- [x] **T5.2** Chạy toàn bộ suite `tests/test_claude_export.py` (46 test cũ + ≥7 test mới của P2–P4) bằng một lệnh — Test: `cd tests && python3 -m unittest test_claude_export -v` → toàn bộ PASS, 0 lỗi/fail

**Xong P5 khi**: T5.2 xanh hoàn toàn.

## P6 — Build thật + QC trên máy nguồn
- [x] **T6.1** Cập nhật code graph — Test: `graphify extract . --code-only` exit 0, `graphify-out/graph.json` có timestamp mới
  - Dùng: `graphify`
  - Nạp: gọi skill `graphify` trước khi chạy lệnh — dùng đúng cú pháp `extract . --code-only` đã quy ước trong CLAUDE.md §7.
  - Để: đồng bộ code graph với các hàm mới/sửa trong `claude_export.py` (P2–P4).
  - Ra: `graphify-out/graph.json`, `graphify-out/manifest.json`, `graphify-out/GRAPH_REPORT.md` cập nhật.
  - Kiểm: `git diff --stat graphify-out/` cho thấy file đổi; lệnh extract thoát mã 0.
  - Không dùng cho: không phân tích kiến trúc sâu hơn phạm vi file đã sửa.
- [x] **T6.2** Build bundle thật: `python3 scripts/claude_export.py build --dest ~/Documents/claude-code-export --zip` — Test: exit code 0, log có dòng "quét secret: sạch", không có dòng cảnh báo secret sót
- [x] **T6.3** `check` ngay sau build: `python3 scripts/claude_export.py check --dest ~/Documents/claude-code-export` — Test: exit 0, in `0 mục lệch`
- [x] **T6.4** Toàn vẹn zip: `unzip -t ~/Documents/claude-code-export.zip` — Test: output kết thúc bằng "No errors detected"
- [x] **T6.5** QC độc lập bằng agent `tdq-qc-tester`: verify cấu trúc bundle thật (không chỉ test giả lập) · liệt kê `ls ~/Documents/claude-code-export`, đọc `manifest.json` · xác nhận có `tdqworkflow-repo/.git`, `mem0-repo/.git`, `config/skills-graphify/`, `config/skills-mem0-memory/`, `config/launch-agents/com.mem0.gateway.plist` · grep thử 1 giá trị TAVILY key thật (lấy từ `~/.claude/settings.json` cục bộ, KHÔNG in ra chat) không xuất hiện trong bundle — Test: agent trả PASS kèm bằng chứng từng mục
- [x] **T6.6** Ghi log thủ công: 2 dòng vào `claude-export/EXPORT_LOG.md` (EXPORT_DEST + tóm tắt: số file, số repo, commit, cảnh báo) theo đúng mẫu trong `INSTRUCTIONS.md`; append working log `docs/workinglog/2026-08-05.md` — Test: `tail -5 claude-export/EXPORT_LOG.md` có dòng mới đúng ngày hôm nay

**Xong P6 khi**: T6.2–T6.5 đều PASS, T6.6 đã ghi.

## QC bổ sung (nếu T6.5 FAIL)
(Thêm task fix trực tiếp vào đây khi QC phát hiện lỗi, không cần duyệt lại plan.)

## Definition of Done
Trỏ về spec §6 (6 hạng mục Q1–Q6):
- Q1 = T5.2 (test suite PASS)
- Q2 = T6.2 (build exit 0, secret sạch)
- Q3 = T6.3 (check 0 lệch)
- Q4 = T6.5 (cấu trúc bundle đủ qua agent QC)
- Q5 = T6.4 (zip toàn vẹn)
- Q6 = T6.2 + T6.5 (secret scan log + grep thủ công của agent QC)
Cộng: `EXPORT_LOG.md` + `docs/workinglog/2026-08-05.md` đã ghi dòng build mới (T6.6);
bundle cũ tại `~/Documents/claude-code-export` (+ `.zip`) đã bị đè bởi bundle mới.
