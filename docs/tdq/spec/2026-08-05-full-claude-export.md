# SPEC — Full claude export (multi-repo local dependency)

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-05 · Bản: 1.0 · Request: ../requests/2026-08-05-full-claude-export.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: `claude_export.py build` sinh 1 bundle export đầy đủ tại
  `~/Documents/claude-code-export` (đè bản cũ đang lệch 6 mục) mang theo **full clone
  Git** của MỌI repo local dependency (không chỉ TDQWorkflow) + toàn bộ instruction/
  setting/config/rule cấp user của `~/.claude`, để dựng lại được trên máy khác.
- Trong phạm vi:
  - Thêm `claude-export/local-repos.json` (danh sách tường minh tên bundle → path repo
    nguồn), mặc định 2 dòng: `tdqworkflow-repo` (repo hiện tại) + `mem0-repo`
    (`~/Documents/mem0R&D` — repo nguồn của MCP server local `mem0`).
  - Sửa `claude_export.py`: loop clone N repo từ `local-repos.json` thay vì 1 repo
    hard-code; `copy_repo_memory` áp cho từng repo có `.remember/`.
  - Tổng quát hoá `CONFIG_DIRS` mục `skills/`: copy MỌI thư mục con cấp 1 của
    `~/.claude/skills/` (hiện có `graphify` + `mem0-memory`, bỏ sót `mem0-memory` do
    hard-code tên) thay vì liệt kê tên cụ thể.
  - Copy `~/Library/LaunchAgents/com.mem0.gateway.plist` (và mọi `.plist` khác khớp
    tên repo trong `local-repos.json`, hiện chỉ có 1) vào `config/launch-agents/` —
    CHỈ để tham khảo, không tự load/restore trên máy đích.
  - `write_manifest`/`write_readme` liệt kê N repo (tên, path nguồn, commit SHA) thay
    vì giả định 1 repo.
  - `cmd_check` so drift cho từng repo trong `local-repos.json` (không chỉ 1).
  - Build bundle thật (`--zip`), chạy `check` xác nhận 0 mục lệch, append
    `claude-export/EXPORT_LOG.md`, ghi working log.
- NGOÀI phạm vi:
  - KHÔNG tự cài/khởi động lại mem0 (Ollama, Qdrant, venv) trên máy đích — máy đích tự
    chạy `install-user.sh` của repo `mem0-repo` đã clone, theo README riêng của repo đó.
  - KHÔNG copy nguyên `~/.claude.json` (chỉ tách `mcpServers` như hiện tại) — chứa
    `oauthAccount`/`machineID`/`userID`, không phải instruction/setting/rule.
  - KHÔNG auto-detect repo local dependency mới trong tương lai — danh sách
    `local-repos.json` là tường minh, cập nhật tay khi có thêm dependency.
  - KHÔNG động tới `specs/`, `plans/`, cache files (`plugin-catalog-cache.json`,
    `mcp-needs-auth-cache.json`...) ở `~/.claude` — không phải instruction/rule.

## 1b. Lộ trình
| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Thuần nội bộ (Python stdlib, git, JSON, filesystem) — không thư viện/API ngoài nào chưa rõ. |
| Interview | CÓ (đã xong ở phase analyze) | 3 câu hỏi + 1 bổ sung đã làm đổi phạm vi (thêm repo mem0, generalize skills/). |
| QC độc lập (agent) | CÓ | Có thao tác đè bundle thật + secret-scan — cần agent QC độc lập chạy lại `check`, giải nén, xác minh cấu trúc trước khi coi là xong. |
| Chia nhiều subagent song song | BỎ | Khối lượng vừa (1 file chính ~550 dòng + test), sửa liền mạch nhanh hơn điều phối song song. |
| Review sâu (tdq-reviewer) | BỎ | Thay đổi có kiểm soát trên script đã có 46 test làm khung an toàn, không phải thiết kế mới rủi ro cao. |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Config danh sách repo local | `claude-export/local-repos.json` | File tồn tại, JSON hợp lệ, có đúng 2 key `tdqworkflow-repo`/`mem0-repo` với path tuyệt đối còn tồn tại trên máy |
| 2 | `claude_export.py` hỗ trợ N repo | `scripts/claude_export.py` (hàm clone/manifest/readme/check) | Test mới PASS: build ra 2 thư mục repo trong bundle, cả 2 có `.git` |
| 3 | `skills/` copy tổng quát | `scripts/claude_export.py` (`CONFIG_DIRS`) | Test mới PASS: bundle có cả `config/skills-graphify/` và `config/skills-mem0-memory/` |
| 4 | LaunchAgent tham khảo | `scripts/claude_export.py` + bundle `config/launch-agents/com.mem0.gateway.plist` | Test mới PASS: file có mặt trong bundle, nội dung khớp sha256 nguồn |
| 5 | Bundle export mới thay bản cũ | `~/Documents/claude-code-export` + `.zip` | `claude_export.py check --dest ...` exit 0 (0 mục lệch) ngay sau build |
| 6 | Log thủ công | `claude-export/EXPORT_LOG.md`, `docs/workinglog/2026-08-05.md` | Có dòng mới ghi EXPORT_DEST + tóm tắt kết quả build |

## 3. Cách tiếp cận & lý do
- Chọn: danh sách repo tường minh (`local-repos.json`) thay vì auto-detect.
- Vì: đã kiểm chứng trực tiếp — LaunchAgent `com.mem0.gateway.plist` chạy từ venv ĐÃ
  CÀI (`~/Library/Application Support/Mem0`), không có trường nào trỏ ngược lại repo
  nguồn `mem0R&D`; auto-detect từ MCP server config (`~/.claude.json`) cũng bất khả thi
  vì entry chỉ là URL `http://127.0.0.1:8765/mcp`, không mang thông tin path. Danh
  sách tường minh là cách DUY NHẤT chính xác 100%, đổi lại phải cập nhật tay khi có
  dependency mới — chấp nhận được vì tần suất thêm dependency thấp.
- Đã loại: heuristic quét `known_marketplaces.json` + toàn bộ `LaunchAgents/*.plist` để
  đoán repo — vì không có back-reference đáng tin, rủi ro false negative (bỏ sót) cao
  hơn lợi ích tự động hoá.
- Đã loại: giữ nguyên chỉ 1 repo, để user tự clone `mem0R&D` tay — vì trái đúng yêu cầu
  gốc "để có thể setup đầy đủ ở máy khác" (thiếu mem0 = thiếu 1 MCP server đang dùng
  hàng ngày, không phải setup đầy đủ).

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `graphify` | user | DÙNG | Chạy `graphify extract . --code-only` cuối turn có đổi code (bắt buộc). |
| `mem0-memory` | user | KHÔNG | khác lĩnh vực — việc kỹ thuật nội bộ 1 request, không phải quyết định kiến trúc/sở thích cross-project cần nhớ dài hạn |
| `tdq-workflow:tdq-spec` | plugin:tdq-workflow | NỀN | Skill khung đang chạy — viết spec này. |
| `tdq-workflow:tdq-plan` | plugin:tdq-workflow | NỀN | Skill khung — viết plan ngay sau duyệt spec (đúng quy ước các spec trước, vd `2026-08-04-toi-uu-token-workflow.md`). |
| `tdq-workflow:tdq-build` | plugin:tdq-workflow | NỀN | Skill khung — thực thi plan sau khi duyệt (đúng quy ước hiện hành, không phải công cụ dùng TRONG một task cụ thể). |
| `claude-md-improver` | plugin:claude-md-management | KHÔNG | khác lĩnh vực — không đổi `CLAUDE.md` |
| `frontend-design` | plugin:frontend-design | KHÔNG | khác lĩnh vực — không có UI |
| `plugin-dev:*` (agent/command/hook/mcp/settings/plugin/skill-development) | plugin:plugin-dev | KHÔNG | khác lĩnh vực — không tạo plugin mới, chỉ sửa 1 script Python nội bộ |
| `mcp-server-dev:*` | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực — không xây MCP server mới, chỉ export config MCP đã có |
| `tavily-*` | plugin:tavily | KHÔNG | khác lĩnh vực — việc thuần nội bộ, không có ẩn số ngoài cần search (đã xác nhận ở §1b) |
| `skill-creator` | plugin:skill-creator | KHÔNG | khác lĩnh vực — không tạo skill mới |
| `playground`, `remember`, `hookify:*` | plugin tương ứng | KHÔNG | khác lĩnh vực |
| `dataviz`, `artifact-design`, `artifact-diagramming`, `artifact-capabilities` | built-in | KHÔNG | khác lĩnh vực — không tạo artifact/chart |
| `claude-api` | built-in | KHÔNG | khác lĩnh vực — không gọi Claude API trực tiếp trong code sửa |
| `update-config`, `keybindings-help` | built-in | KHÔNG | khác lĩnh vực — không đổi `settings.json`/keybindings của CHÍNH máy khi làm việc (chỉ export bản sao) |
| `run` | built-in | KHÔNG | khác lĩnh vực — không có app để chạy/screenshot |
| `simplify` | built-in | KHÔNG | spec §3 đã chọn cách khác tốt hơn — thay đổi đã có kế hoạch rõ ràng theo test, không cần pass dọn dẹp chung |
| `security-review`, `review`, `init` | built-in | KHÔNG | khác lĩnh vực — không phải yêu cầu review bảo mật/tổng quan repo hay khởi tạo project mới |
| `code-review:code-review` | plugin:code-review | KHÔNG | spec §3 đã chọn cách khác tốt hơn — đã có QC riêng bằng agent `tdq-qc-tester` (đã quyết ở §1b) |
| `agent-sdk-dev:*` | plugin:agent-sdk-dev | KHÔNG | khác lĩnh vực — không xây Agent SDK app |

## 4. Yêu cầu bắt buộc
- Log service bật mặc định: `claude_export.py` đã có `log()` timestamp ISO ra stderr,
  tắt bằng `--quiet`, thêm debug bằng `--verbose` — giữ nguyên, áp dụng cho log dòng
  mới (clone N repo, copy plist).
- Không placeholder/TODO/mock: `local-repos.json` chứa path thật, đã xác nhận tồn tại
  trên máy trước khi ghi.
- Mỗi phần đổi có unit test riêng trong `tests/test_claude_export.py`, chạy bằng
  `python3 -m unittest test_claude_export` (từ thư mục `tests/`).

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| `mem0R&D` đang có 2 file uncommitted (`docs/tdq/STATE.md`, `docs/workinglog/2026-08-05.md`) | Clone chỉ lấy bản đã commit, bundle thiếu 2 thay đổi mới nhất của repo đó | Giữ đúng hành vi hiện có với TDQWorkflow (`git clone` + log cảnh báo số file dirty) — nhất quán, không cần xử lý đặc biệt |
| Bundle tăng kích thước (thêm 1 repo ~1.4 MB + `.git` 620 KB) | Build/zip lâu hơn chút, dung lượng tăng | Không đáng kể (<2 MB thêm so với bundle hiện ~17 MB) — không cần tối ưu |
| `local-repos.json` trỏ path không tồn tại trên máy khác chạy `build` | `build` phải báo lỗi rõ, không crash traceback mù mờ | Test case: path không tồn tại → thoát mã lỗi có log rõ tên repo thiếu |
| Path `mem0R&D` chứa ký tự `&` | Có thể vỡ khi ghép chuỗi shell không quote | Dùng toàn bộ qua `os.path`/`subprocess` list-args (không qua shell string) — đã đúng pattern sẵn có trong code |
| Copy `.plist` chứa thông tin máy (username trong path) | Không phải secret nhưng là thông tin cá nhân máy nguồn | Chấp nhận được — chỉ để THAM KHẢO cấu trúc launchd, README ghi rõ máy đích tự sinh plist theo path của máy đó qua `install-user.sh` |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Test suite `claude_export` | `python3 -m unittest test_claude_export -v` (trong `tests/`) | Toàn bộ test cũ (46) + test mới đều PASS |
| Q2 | Build bundle thật | `python3 scripts/claude_export.py build --dest ~/Documents/claude-code-export --zip` | Exit code 0, log không cảnh báo secret sót |
| Q3 | Drift check ngay sau build | `python3 scripts/claude_export.py check --dest ~/Documents/claude-code-export` | Exit 0, in `0 mục lệch` |
| Q4 | Cấu trúc bundle | Agent QC đọc `manifest.json`, liệt kê `ls <dest>` | Có `tdqworkflow-repo/.git`, `mem0-repo/.git`, `config/skills-mem0-memory/`, `config/skills-graphify/`, `config/launch-agents/com.mem0.gateway.plist` |
| Q5 | Zip toàn vẹn | `unzip -t ~/Documents/claude-code-export.zip` | "No errors detected" |
| Q6 | Secret scan sạch | Đọc log build dòng "quét secret: sạch" + agent QC grep thử 1 giá trị TAVILY key thật trong bundle | Không tìm thấy giá trị thật ở bất kỳ file nào |

DoD: 6 hạng mục QC trên đều PASS; `EXPORT_LOG.md` và `docs/workinglog/2026-08-05.md`
đã ghi dòng build mới; bundle cũ (`claude-code-export`, `.zip`) đã bị đè bởi bundle mới
tại đúng vị trí cũ.

## 7. Câu hỏi còn mở
(Không có — 3 câu hỏi vòng 1 + yêu cầu bổ sung đã được trả lời và rà soát đầy đủ ở
`docs/tdq/knowledge/2026-08-05-full-claude-export.md`.)
