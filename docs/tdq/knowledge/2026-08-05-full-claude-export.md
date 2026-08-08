# Knowledge — 2026-08-05-full-claude-export

## Năng lực dùng được

| Năng lực | Có sẵn | Dùng? | Vì sao |
|---|---|---|---|
| `graphify` | Có | Có | Bắt buộc cuối turn có đổi code (§quy tắc chung). |
| `mem0-memory` | Có | Không | Việc thuần kỹ thuật nội bộ 1 repo, không phải quyết định kiến trúc cross-project cần nhớ dài hạn. |
| Skill built-in khác (dataviz, artifact-*, tavily-*, plugin-dev...) | Có | Không | Không tạo artifact/chart/MCP mới; không có ẩn số ngoài cần research (đã xác nhận ở B3). |
| `tdq-workflow:*` (spec/plan/build/qc) | Có | Có | Khung bắt buộc của toàn bộ request. |

## Đã đọc

- `scripts/claude_export.py` (523 dòng) — full source, hiểu rõ `CONFIG_FILES`,
  `CONFIG_DIRS`, `clone_repo`, `copy_repo_memory`, `rewrite_marketplace_path`,
  `write_manifest`, `write_readme`, secret-scan/redact, `check`.
- `claude-export/INSTRUCTIONS.md`, `EXPORT_LOG.md`, `MANIFEST.template.json`,
  `README.template.md` — quy ước ghi log thủ công sau mỗi lần build thật.
- `tests/test_claude_export.py` — 46 test, chạy PASS (baseline trước khi sửa).
- `~/.claude/plugins/known_marketplaces.json`, `installed_plugins.json` — xác nhận
  `tdq-local → TDQWorkflow` là marketplace local-directory DUY NHẤT; các plugin khác
  100% nguồn GitHub (không cần clone thêm).
- `~/.claude.json` khối `mcpServers` — 3 server: `tavily-primary`, `tavily-backup`
  (HTTP remote), `mem0` (`http://127.0.0.1:8765` — LOCAL).
- `~/Library/LaunchAgents/com.mem0.gateway.plist` — xác nhận mem0 chạy từ venv đã cài
  ở `~/Library/Application Support/Mem0`, KHÔNG trỏ ngược lại repo nguồn.
- `~/Documents/mem0R&D` — repo nguồn của mem0 gateway: 1 commit, không remote, có
  `.remember/`, có `install-user.sh` + `mem0.manifest.yaml` tự đủ hướng dẫn cài trên
  máy đích; không chứa secret thật (chỉ code phát hiện secret + `cloud_api_keys_required: false`).
- `~/.claude/` (toàn bộ 42 mục top-level + `plugins/`, `skills/`) — đối chiếu với
  `CONFIG_FILES`/`CONFIG_DIRS` hiện tại, tìm gap theo yêu cầu bổ sung của user.
- Bundle export cũ tại `~/Documents/claude-code-export` — chạy `check` thấy lệch 6 mục
  (xác nhận cần build lại, không chỉ đọc).

## Quyết định đã chốt

1. **2 repo local dependency**, không phải 1: `TDQWorkflow` (đã có) +
   `mem0R&D` (mới) — clone full `.git` (chỉ commit đã có, giống hành vi hiện tại),
   copy riêng `.remember/` như đã làm với TDQWorkflow.
2. **Danh sách repo tường minh**, không auto-detect: thêm file
   `claude-export/local-repos.json` dạng `{"tên trong bundle": "path tuyệt đối trên máy nguồn"}`,
   mặc định 2 dòng (`tdqworkflow-repo` → repo chính, `mem0-repo` → `~/Documents/mem0R&D`).
   Script đọc file này, loop clone thay vì hard-code 1 lệnh `clone_repo`. Lý do chọn A
   ở Q2: đã kiểm chứng auto-detect không khả thi (plist không back-reference).
3. **LaunchAgent tham khảo**: copy `~/Library/LaunchAgents/com.mem0.gateway.plist` (và
   mọi `.plist` khác có tên chứa các tên repo local — chỉ 1 cái hiện có) vào
   `config/launch-agents/`. KHÔNG tự restore/load plist trên máy đích — đúng nguyên
   tắc "không cài gì lên máy đích" đã ghi trong `INSTRUCTIONS.md`.
4. **Tổng quát hoá `CONFIG_DIRS` cho `skills/`**: thay vì hard-code
   `("skills/graphify", "config/skills-graphify")`, đổi sang tự liệt kê MỌI thư mục
   con cấp 1 của `~/.claude/skills/` (mỗi skill → `config/skills-<tên>/`). Đây là
   fix duy nhất từ yêu cầu bổ sung "đầy đủ ... all of claude user level" — đã rà toàn
   bộ `~/.claude/`, không còn instruction/setting/rule nào khác bị bỏ sót (xem
   `questions/2026-08-05-full-claude-export.md` mục rà soát).
5. **`~/.claude.json` vẫn KHÔNG copy nguyên file** (giữ hành vi cũ) — chứa
   `oauthAccount`/`machineID`/`userID`, không phải "instruction/rule", là danh tính
   máy/tài khoản. Không nằm trong yêu cầu bổ sung của user (user nói instruction/
   setting/config/rule, không nói identity/credential).
6. **README/manifest cần liệt kê N repo** thay vì giả định đúng 1 repo — sửa
   `write_manifest`/`write_readme` khỏi hard-code `REPO_DIR_NAME` đơn lẻ.
7. **`check` command cũng cần đo drift cho N repo** (hiện chỉ so 1 `repo_commit`) —
   mở rộng để so từng repo trong `local-repos.json`.
8. Bundle đích không đổi: vẫn `~/Documents/claude-code-export` (+ `.zip`), đè bản cũ
   (đã xác nhận lệch 6 mục ở bước phân tích quick trước đó).

## Phương án đã loại

- Auto-detect repo local từ MCP server config/LaunchAgent — loại vì không có
  back-reference đáng tin (đã kiểm chứng bằng cách đọc thật plist).
- Tự động chạy lại `install-user.sh` của `mem0R&D` trên máy đích từ trong script export
  — loại, ngoài phạm v" (export tool chỉ tạo bundle, không cài đặt máy đích, README
  hướng dẫn người dùng tự chạy).
- Copy nguyên `~/.claude.json` — loại vì lộ định danh máy/tài khoản, không cần thiết
  cho "instruction/setting/rule".

## Nguồn

- Đọc trực tiếp source code + config trên máy (không có ẩn số thư viện/API ngoài nào
  cần tra cứu — việc thuần nội bộ filesystem/git/JSON, bỏ qua bước research theo đúng
  ngoại lệ ở `analyze-full.md` bước 3).

## Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Phân tích (đã xong) | CÓ | Bắt buộc, đã tìm ra 2 gap thật (mem0R&D, skills/ hard-code) không đoán được nếu bỏ qua. |
| Spec | CÓ | Khung bất biến — chốt phạm vi 8 quyết định trên thành spec chính thức. |
| Plan | CÓ | Khung bất biến — chia task theo 4 nhóm sửa code + test tương ứng. |
| Research thêm | BỎ | Đã xác nhận thuần nội bộ, không thư viện/API ngoài chưa rõ. |
| Chia nhiều subagent song song | BỎ | Khối lượng vừa (~1 file chính + test), 1 luồng làm liền mạch nhanh hơn overhead điều phối. |
| QC độc lập bằng agent riêng | CÓ | Có bước bảo mật (secret scan) + đè bundle thật trên máy — cần agent QC độc lập chạy lại `check` + xác minh bundle mới mở được trên "máy giả lập" (giải nén, đọc README) trước khi coi là xong. |
| Review sâu code (tdq-reviewer) | BỎ | Thay đổi có kiểm soát trên 1 script đã có 46 test làm khung, không phải thiết kế mới rủi ro cao. |
| Implement | CÓ | Khung bất biến. |
| Report | CÓ | Khung bất biến. |

## Kiểm cổng

- **Phạm vi cuối rõ chưa?** Rõ: sửa `claude_export.py` (config-driven multi-repo clone
  + tổng quát hoá `skills/` + copy LaunchAgent plist tham khảo + manifest/README/check
  hỗ trợ N repo), thêm `claude-export/local-repos.json`, build lại bundle thật tại
  `~/Documents/claude-code-export` (đè bản cũ) + `.zip`.
- **Cần model/download/cài đặt gì không?** Không — thuần Python stdlib + git đã có sẵn
  trên máy, không cần cài thêm gì để CHẠY script export (việc cài mem0 trên máy ĐÍCH
  là việc của người dùng máy đó, ngoài phạm vi).
- **Phạm vi QC/test/validate đã có chưa?** Có: 46 test hiện tại làm baseline + test mới
  cho multi-repo/skills-generalize/plist-copy; QC cuối chạy `check` trên bundle thật +
  giải nén xác minh cấu trúc.
