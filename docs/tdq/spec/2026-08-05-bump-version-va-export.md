# SPEC — Bump 0.7.0 + bộ export Claude Code đầy đủ, chạy được bằng một lệnh

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-05 · Bản: 1.0 · Request: ../requests/2026-08-05-bump-version-va-export.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: phát hành `0.7.0`, và thay bộ export thủ công 7 bước bằng
  `scripts/claude_export.py` có 2 lệnh `build`/`check`, vá đủ 8 lỗ hổng đã đo, rồi
  sinh lại bundle `~/Documents/claude-code-export` + file zip.
- Trong phạm vi:
  - Bump `.claude-plugin/plugin.json` `0.6.2` → `0.7.0` + entry `CHANGELOG.md`.
  - `scripts/claude_export.py`: `build` (sinh bundle) và `check` (đo drift), có log timestamp.
  - Bundle mang thêm MCP server, `.git`, `manifest.json` có version + commit SHA.
  - Viết lại `claude-export/INSTRUCTIONS.md`, `README.template.md`, `MANIFEST.template.json`.
  - Unit test cho `claude_export.py`; sinh bundle thật + zip; QC độc lập.
- NGOÀI phạm vi:
  - Không dựng thử máy đích thật (không có máy thứ hai) — chỉ verify bundle tại chỗ.
  - Không đổi nội dung `~/.claude/settings.json`, `CLAUDE.md`, plugin đang bật của máy nguồn.
  - Không đưa key thật vào bundle; không copy đè `~/.claude.json` sang bất cứ đâu.
  - Không đụng bộ `portable/` (bản cho agent ngoài Claude Code) — khác mục đích.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ | đã chạy 3 truy vấn, cần luật MCP scope + marketplace local |
| Interview | CÓ | đã chạy 1 vòng 5 câu, user đã trả lời đủ |
| Spec | CÓ | lane full |
| Plan | CÓ | lane full |
| Implement | CÓ | mode do user chốt khi duyệt plan |
| QC độc lập (agent) | CÓ | bundle ghi ra ngoài repo, cần người thứ hai kiểm |
| Report | CÓ | lane full, ≤10 dòng |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Version 0.7.0 | `.claude-plugin/plugin.json` | `test_docs_consistency.py` xanh |
| 2 | Entry changelog 0.7.0 | `CHANGELOG.md` | mục đầu file là `## 0.7.0` |
| 3 | Script export | `scripts/claude_export.py` | `build` và `check` chạy exit 0 |
| 4 | Test script export | `tests/test_claude_export.py` | suite đầy đủ xanh |
| 5 | Hướng dẫn rút gọn | `claude-export/INSTRUCTIONS.md` | `doc_lint.py` exit 0 |
| 6 | Template README có bước MCP | `claude-export/README.template.md` | chứa `claude mcp add-json` |
| 7 | Template manifest 8 khoá | `claude-export/MANIFEST.template.json` | `json.tool` exit 0 |
| 8 | Bundle mới | `~/Documents/claude-code-export` | `check` báo 0 mục lệch |
| 9 | Zip mới | `~/Documents/claude-code-export.zip` | `unzip -t` exit 0 |
| 10 | Log lần chạy | `claude-export/EXPORT_LOG.md` | có 2 dòng mốc 2026-08-05 |

## 3. Cách tiếp cận & lý do

- Chọn: một script Python duy nhất thay 7 bước tay; bản copy repo dùng `git clone`;
  MCP xuất ra `config/mcp-servers.json` rồi khôi phục bằng `claude mcp add-json --scope user`;
  `manifest.json` ghi `plugin_version` + `repo_commit` + sha256 từng file config để `check`
  so lại được.
- Vì:
  - `git clone` chỉ lấy file tracked → xoá sạch một lúc 4 lỗi (`graphify-out/20*/` 15 MB,
    `docs/tdq/state.json`, `.tdq-turn.jsonl`, `.DS_Store`) mà vẫn giữ `.git` user yêu cầu.
    Bundle từ 17 MB còn ≈6 MB + 8 MB `.git`.
  - Header MCP máy nguồn là `Bearer ${TAVILY_API_KEY_PRIMARY}` — biến môi trường, không
    phải key thật → copy được mà không lộ secret.
  - Docs chính thức: MCP scope `user` nằm ở `~/.claude.json` key `mcpServers`; issue
    anthropics/claude-code#15797 cấm ghi đè cả file đó → phải add lại bằng CLI.
  - `.remember/` là untracked nên `git clone` không mang theo → copy riêng, lọc `tmp/`+`logs/`.
- Đã loại:
  - Giữ 7 bước thủ công — chính là nguyên nhân 4/8 lỗi: danh sách loại trừ chỉ là văn bản,
    không có gì thi hành.
  - `rsync --exclude` liệt kê tay — rsync không đọc `.gitignore`, đã chứng minh sót.
  - Copy đè `~/.claude.json` — mất `oauthAccount`/`machineID` máy đích (issue 15797).

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung phase analyze |
| tdq-spec | plugin:tdq-workflow | DÙNG | viết chính spec này |
| tdq-plan | plugin:tdq-workflow | DÙNG | viết plan sau khi duyệt spec |
| tdq-build | plugin:tdq-workflow | DÙNG | thực thi plan, QC, report |
| tdq-conventions | plugin:tdq-workflow | NỀN | quy ước chung mọi phase |
| tdq-status | plugin:tdq-workflow | KHÔNG | khác lĩnh vực |
| graphify | user | DÙNG | rebuild code graph cuối turn đổi code |
| claude-md-improver | plugin:claude-md-management | KHÔNG | khác lĩnh vực |
| frontend-design | plugin:frontend-design | KHÔNG | khác lĩnh vực |
| writing-hookify-rules | plugin:hookify | KHÔNG | khác lĩnh vực |
| build-mcp-app | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| build-mcp-server | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| build-mcpb | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực |
| playground | plugin:playground | KHÔNG | khác lĩnh vực |
| agent-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| command-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| hook-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| mcp-integration | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| plugin-settings | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| plugin-structure | plugin:plugin-dev | KHÔNG | khác lĩnh vực — manifest đã có, không tạo plugin mới |
| skill-development | plugin:plugin-dev | KHÔNG | khác lĩnh vực |
| remember | plugin:remember | NỀN | hook tự chạy cuối phiên |
| skill-creator | plugin:skill-creator | KHÔNG | khác lĩnh vực — không tạo skill mới |
| tavily-best-practices | plugin:tavily | KHÔNG | khác lĩnh vực — không viết tích hợp Tavily |
| tavily-cli | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — dùng MCP |
| tavily-crawl | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — không crawl site |
| tavily-dynamic-search | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — search tĩnh đủ |
| tavily-extract | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — snippet đã đủ |
| tavily-map | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — không map site |
| tavily-research | plugin:tavily | KHÔNG | spec §3 đã chọn cách khác tốt hơn — chưa đủ 2 dấu hiệu deep search |
| tavily-search | plugin:tavily | DÙNG | 3 truy vấn phase analyze |
| update-config | built-in | KHÔNG | user đã cấm — không đổi settings máy nguồn (§1 ngoài phạm vi) |
| Explore | built-in | KHÔNG | spec §3 đã chọn cách khác tốt hơn — phạm vi file đã xác định |
| Plan | built-in | KHÔNG | spec §3 đã chọn cách khác tốt hơn — plan viết bằng tdq-plan |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: `claude_export.py` in mỗi bước kèm timestamp ISO ra stderr,
  tắt bằng `--quiet`, chi tiết hơn bằng `--verbose`.
- Không placeholder, không TODO stub trong code. Hai placeholder API key trong bundle là
  **chủ đích** và phải giữ nguyên chữ.
- Mỗi thành phần có unit test riêng, chạy bằng một lệnh:
  `cd tests && python3 -m unittest discover -s . -p "test_*.py"`.
- Chống lộ secret: `build` quét bundle vừa sinh, thấy chuỗi khớp giá trị thật của
  `TAVILY_API_KEY_PRIMARY`/`BACKUP` thì xoá bundle và exit khác 0.
- Mọi lệnh thí nghiệm ghi state phải kèm `TDQ_PROJECT_DIR=<thư mục tạm>`.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Ghi đè nhầm thư mục ngoài repo | mất dữ liệu user | `build` chỉ ghi đè khi đích trống hoặc có `manifest.json` do chính script sinh; đích lạ → exit khác 0 |
| Lộ API key vào bundle | rò rỉ secret | thay placeholder + quét lại bundle sau khi sinh, fail thì xoá |
| `git clone` mất file untracked cần thiết | bundle thiếu `.remember` | copy `.remember` riêng, có test đếm file |
| `~/.claude.json` bị sửa nhầm | hỏng oauth máy nguồn | script chỉ ĐỌC file này, không mở chế độ ghi |
| Test đụng `~/.claude` thật | hỏng cấu hình máy nguồn | test dùng thư mục tạm, tiêm đường dẫn qua tham số |
| Bundle cũ 2,2 MB zip bị xoá trước khi bundle mới xong | mất bản lùi | sinh zip mới ra file tạm rồi mới đổi tên đè |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Version + changelog | `cd tests && python3 -m unittest test_docs_consistency` | xanh, `plugin.json` = `0.7.0` |
| Q2 | Suite đầy đủ | `cd tests && python3 -m unittest discover -s . -p "test_*.py"` | 0 fail, số test ≥ 521 |
| Q3 | Lint tài liệu | `python3 scripts/doc_lint.py claude-export skills portable docs/tdq` | exit 0 |
| Q4 | Bundle không rác | `find <dest> -name '.DS_Store' -o -name 'state.json' -o -path '*graphify-out/20*'` | không ra dòng nào |
| Q5 | Bundle có `.git` | `git -C <dest>/tdqworkflow-repo log --oneline -1` | in đúng commit HEAD máy nguồn |
| Q6 | Bundle có MCP | `python3 -c "import json;d=json.load(open('<dest>/config/mcp-servers.json'));print(sorted(d))"` | in `['tavily-backup', 'tavily-primary']` |
| Q7 | Không lộ secret | `grep -rF "<giá trị key thật>" <dest>` | 0 kết quả (chạy bằng biến, không in ra) |
| Q8 | manifest đủ khoá | `python3 -c "import json;print(sorted(json.load(open('<dest>/manifest.json'))))"` | có `plugin_version`, `repo_commit`, `exported_at`, `source_files` |
| Q9 | `check` báo sạch ngay sau `build` | `python3 scripts/claude_export.py check --dest <dest>` | exit 0, in `0 mục lệch` |
| Q10 | `check` bắt được drift | sửa 1 file nguồn trong thư mục tạm rồi chạy lại `check` | exit khác 0, nêu đúng tên file |
| Q11 | Zip hợp lệ | `unzip -t ~/Documents/claude-code-export.zip` | `No errors detected` |
| Q12 | Log export | `tail -2 claude-export/EXPORT_LOG.md` | 2 dòng mốc 2026-08-05 |

DoD: cả Q1–Q12 PASS · bundle `~/Documents/claude-code-export` đã ghi đè xong và zip sinh
lại · 8 lỗ hổng đã đo đều có ít nhất một hạng mục QC chứng minh đã vá · report ≤10 dòng
nêu rõ số đo trước/sau · không có key thật ở bất kỳ đâu trong bundle, log hay report.

## 7. Câu hỏi còn mở

- Q3 chạy thật ra exit 1 vì nợ cũ: `docs/tdq` còn 104 vi phạm R5/R2 ở request, plan,
  knowledge, research của các request TRƯỚC. File thuộc request này lint sạch (exit 0).
  Không sửa nợ cũ trong request này vì `docs/tdq/requests/*` chứa nguyên văn lời user,
  viết lại cho ngắn câu là làm sai bản ghi. Cần một request dọn nợ riêng, phạm vi
  knowledge/research/plan cũ, chừa requests.
- `git clone` chỉ lấy commit đã có, nên bundle phải sinh SAU khi commit. Bundle mang
  commit tại thời điểm build, không mang phần tick plan và report viết sau đó.
- QC phát hiện: `check` chỉ đo drift phía NGUỒN, không kiểm tính toàn vẹn của chính
  bundle. Xoá `tdqworkflow-repo/` hay sửa file ngay trong bundle thì `check` vẫn báo
  `0 mục lệch`. Đúng câu chữ Q10 nhưng vẫn là lỗ hổng khi bundle rơi rụng file lúc
  truyền sang máy khác. Cần request sau thêm lệnh `verify --dest` hash lại chính bundle.
- Q3 trong §6 ghi PASS = exit 0 trên toàn `docs/tdq`, mâu thuẫn với nợ cũ nêu ở trên.
  Đọc Q3 theo nghĩa: 0 vi phạm thuộc file của request này (đo được 0/101).
