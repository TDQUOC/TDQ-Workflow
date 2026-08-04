# SPEC — Bộ công cụ export cấu hình Claude Code sang máy khác

Ngày: 2026-08-04 · Bản: 1.0 · Request: ../requests/2026-08-04-export-claude-setup.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: có một bộ công cụ (tài liệu tĩnh, tái dùng nhiều lần) lưu trong repo
  TDQWorkflow, khi làm theo sẽ tạo ra một **bundle export** đầy đủ (manifest +
  dependency + README chi tiết) để setup Claude Code trên máy khác hoạt động
  tương đương máy nguồn hiện tại (cùng plugin/marketplace/skill/memory/CLAUDE.md,
  cùng repo TDQWorkflow) — dependency cần cài online thì có hướng dẫn theo 3 hệ
  điều hành (macOS, Linux, Windows — Windows có 2 nhánh: native và WSL2, xem §5),
  phần local (repo TDQWorkflow, skill user-level, memory) thì copy vật lý vào
  bundle. Bundle phải hoạt động được trên máy đích, bao gồm việc plugin
  `tdq-workflow` (marketplace `tdq-local`) load đúng từ vị trí repo copy mới —
  không chỉ copy file tĩnh mà bỏ qua việc path máy nguồn đã hard-code sẽ không
  còn đúng trên máy đích.
- Trong phạm vi:
  - Thư mục công cụ `claude-export/` trong repo TDQWorkflow (instruction, template
    manifest, template README) — version theo git, chạy lại được nhiều lần.
  - Nội dung cấu hình global `~/.claude/` đã lọc bỏ dữ liệu runtime/máy-cụ-thể:
    `settings.json` (secret thay placeholder), `CLAUDE.md`, `plugin-tiers.json`,
    `skills/graphify`, `.remember/`, `statusline.sh`, `scripts/plugin_tiers.py`,
    danh sách `installed_plugins.json`/`known_marketplaces.json`.
  - 2 MCP server global (`tavily-primary`, `tavily-backup`) từ `~/.claude.json`
    (chỉ cấu trúc + tên biến env, không giá trị thật).
  - Toàn bộ repo TDQWorkflow (copy vật lý, vì không có git remote).
  - Bước rewrite đường dẫn tuyệt đối `extraKnownMarketplaces.tdq-local` (trong
    `settings.json` export) và entry tương ứng trong `known_marketplaces.json`
    export để trỏ đúng vị trí thực tế của repo TDQWorkflow trên máy đích (do
    người setup chỉ định lúc chạy `INSTRUCTIONS.md`) — nếu không rewrite, plugin
    `tdq-workflow` sẽ không load được trên máy đích.
  - Danh sách CLI dependency (claude, node, python3, git, uv/uvx, graphify, tuỳ
    chọn codex + agy) kèm hướng dẫn cài cho macOS, Linux, và Windows (native —
    winget/npm — hoặc WSL2 khi cần sandboxing; theo docs chính thức, xem
    `research` §5).
  - 1 lần chạy thử thực tế theo instruction để sinh bundle mẫu, làm căn cứ QC.
- NGOÀI phạm vi:
  - Project `Project01_LiveCaptionTranslate`, `insightfaceserverv2`, plugin
    `superpowers` (scope project gắn Project01) — không liên quan tới việc Claude
    Code hoạt động, không export.
  - Script shell tự động hoá việc cài đặt trên máy đích (`setup.sh`) — user đã từ
    chối ở vòng interview; mọi bước cài đặt máy đích đều là lệnh thủ công trong
    README, không có phần nào Claude tự chạy thay máy đích.
  - Giá trị thật của `TAVILY_API_KEY_PRIMARY`/`TAVILY_API_KEY_BACKUP`, và mọi
    token/oauth trong `~/.claude.json` (`oauthAccount`, `machineID`, `userID`) —
    không bao giờ ghi ra bundle, log, hay bất kỳ file nào.
  - Cài đặt/thực thi thật trên một máy thứ hai — spec này chỉ tạo bundle + hướng
    dẫn, không có máy thứ hai trong phạm vi phiên làm việc để chạy thử end-to-end.
  - Dữ liệu runtime/cache/máy-cụ-thể: `history.jsonl`, `sessions/`, session
    transcript (`projects/*/*.jsonl`), `debug/`, `logs/`, `cache/`,
    `shell-snapshots/`, `file-history/`, `telemetry/`, `image-cache/`,
    `paste-cache/`, `ide/`, `daemon*`, `plugins/cache/`,
    `plugins/plugin-catalog-cache.json`, `plugins/data/`, `.DS_Store`, `*.bak*`.

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | File instruction quy trình export (đọc-làm-theo, liệt kê đủ bước + lệnh cụ thể) | `claude-export/INSTRUCTIONS.md` | File tồn tại; có đủ 7 bước theo thứ tự (thu thập trạng thái máy nguồn → lọc secret/runtime → copy file local → **rewrite path marketplace `tdq-local` theo vị trí đích** → điền manifest → điền README → ghi log); mỗi bước có lệnh shell/CLI cụ thể, copy-paste chạy được, không có chỗ ghi "tuỳ chỉnh sau" |
| 2 | Template manifest máy-đọc-được | `claude-export/MANIFEST.template.json` | `python3 -m json.tool claude-export/MANIFEST.template.json` không lỗi; có đủ 5 khoá bậc 1: `plugins`, `marketplaces`, `mcp_servers`, `cli_dependencies`, `excluded` |
| 3 | Template README cho người setup máy đích | `claude-export/README.template.md` | Có đủ 6 mục theo thứ tự: giới thiệu bundle, bảng CLI dependency cần cài (3 cột OS: macOS/Linux/Windows — cột Windows nêu cả 2 nhánh native và WSL2), bước cài Claude Code CLI, bước add marketplace + cài từng plugin (danh sách khớp 100% số lượng plugin scope `user` có `enabledPlugins=true` đọc trực tiếp từ `installed_plugins.json` tại thời điểm export — không hardcode số cụ thể trong template, đối chiếu bằng Q6), bước copy file cấu hình + rewrite path `tdq-local` + điền lại 2 API key, bước verify (`claude --version`, `claude plugin list` khớp danh sách) |
| 4 | Nhật ký mỗi lần chạy export (yêu cầu §4 — log service) | `claude-export/EXPORT_LOG.md` | Có ít nhất 1 dòng entry dạng `YYYY-MM-DD HH:MM — <tóm tắt: số file copy, số plugin liệt kê, cảnh báo nếu có>` sau lần chạy thử ở đầu ra #5; nếu chạy với cờ tắt log thì KHÔNG có entry mới (xem §4) |
| 5 | Bundle export mẫu — chạy thử 1 lần theo instruction #1 | Đường dẫn ngoài repo do user xác nhận lúc build (mặc định gợi ý `~/Documents/claude-code-export/`) | Thư mục đích tồn tại đúng cấu trúc: `manifest.json` (đã điền dữ liệu thật, hợp lệ JSON), `README.md` (đã điền, không còn placeholder `<...>` chưa điền phần mô tả — chỉ còn placeholder 2 API key theo chủ đích), `config/` (copy các file mục 1 đã lọc, `settings.json` bên trong có `extraKnownMarketplaces.tdq-local` trỏ đúng đường dẫn đích), `tdqworkflow-repo/` (copy toàn bộ repo TDQWorkflow); `grep -r` giá trị thật của 2 API key trên toàn bộ thư mục bundle trả về rỗng; không chứa file/thư mục nào thuộc danh sách loại trừ ở §1 |

## 3. Cách tiếp cận & lý do
- Chọn: xây 3 tài liệu tĩnh (instruction + template manifest + template README) đặt
  cố định trong `claude-export/` của repo TDQWorkflow; khi cần export, Claude (hoặc
  người dùng) đọc `INSTRUCTIONS.md`, thu thập dữ liệu thật từ máy nguồn theo đúng
  danh sách đã khảo sát (knowledge §"Khảo sát máy nguồn"), điền vào 2 template, ghi
  log, rồi copy toàn bộ (đã điền + repo TDQWorkflow) sang thư mục đích do user chỉ
  định — không viết script binary/`setup.sh` tự động thực thi trên máy đích.
- Vì: user đã chốt ở vòng interview — (a) không muốn script tự động cài trên máy
  đích (rủi ro chạy nhầm, khó review từng bước); (b) muốn tái dùng bộ công cụ này
  cho các lần export sau khi cấu hình máy nguồn đổi (thêm plugin, đổi skill...) →
  cần lưu instruction trong repo, version theo git, thay vì làm 1 lần rồi bỏ.
  Research xác nhận `claude plugin marketplace add`/`claude plugin install` chạy
  non-interactive được (code.claude.com/docs/en/plugin-marketplaces), đủ để liệt
  kê thành lệnh cụ thể trong README mà không cần script.
- Đã loại: viết `claude-export/setup.sh` thực thi tự động toàn bộ — vì user đã từ
  chối trực tiếp ở câu hỏi "Hình thức" (vòng interview 1, câu 4).
- Đã loại: đặt bundle export thực tế ngay trong `claude-export/` của repo — vì
  bundle chứa bản copy toàn bộ repo TDQWorkflow, đặt trong chính repo sẽ gây lồng
  repo vào chính nó (đệ quy, phình dung lượng qua mỗi lần export); user đã chọn
  "thư mục riêng ngoài TDQWorkflow" ở vòng interview 1, câu 5.
- Đã loại: bỏ hẳn 2 dòng API key khỏi file export — vì user chọn giữ cấu trúc với
  placeholder tường minh (vòng interview 1, câu 2), giúp người setup máy đích thấy
  ngay cần điền gì thay vì phải tự thêm block `env` từ đầu.

## 3b. Năng lực & công cụ
Chép từ `knowledge/2026-08-04-export-claude-setup.md` mục "Năng lực dùng được".

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-build, tdq-conventions, tdq-intake, tdq-plan, tdq-spec, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy request này |
| update-config | built-in | DÙNG | tham chiếu cấu trúc `settings.json` khi viết `INSTRUCTIONS.md`/`README.template.md` (đầu ra #1, #3) |
| keybindings-help | built-in | DÙNG | xác nhận không có `keybindings.json` cần export (đã khảo sát); tham chiếu nếu máy nguồn có sau này |
| remember (remember, remember:doctor) | plugin:remember / built-in | DÙNG | copy `.remember/` vào bundle (đầu ra #5), doctor kiểm tình trạng memory trước khi copy |
| plugin-dev:plugin-structure | plugin:plugin-dev | DÙNG | tham chiếu chuẩn `plugin.json`/`marketplace.json` khi viết `MANIFEST.template.json` (đầu ra #2) |
| tavily-search | plugin:tavily | DÙNG | đã dùng ở phase analyze (research 4 truy vấn), không dùng thêm ở phase build |
| graphify, frontend-design, hookify:writing-rules, hookify:configure, hookify:help, hookify:hookify, hookify:list, mcp-server-dev:build-mcp-app, mcp-server-dev:build-mcp-server, mcp-server-dev:build-mcpb, plugin-dev:agent-development, plugin-dev:command-development, plugin-dev:hook-development, plugin-dev:mcp-integration, plugin-dev:plugin-settings, plugin-dev:skill-development, plugin-dev:create-plugin, skill-creator, tavily-best-practices, tavily-cli, tavily-crawl, tavily-dynamic-search, tavily-extract, tavily-map, tavily-research, feature-dev:feature-dev, code-review:code-review, claude-md-management:revise-claude-md, claude-md-management:claude-md-improver, agent-sdk-dev:new-sdk-app, dataviz, artifact-design, artifact-diagramming, artifact-capabilities, simplify, fewer-permission-prompts, loop, schedule, claude-api, run, init, review, security-review | built-in/plugin (nhiều nguồn) | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service bật mặc định: mỗi lần chạy `INSTRUCTIONS.md` để (tái) tạo bundle phải
  append 1 entry có timestamp vào `claude-export/EXPORT_LOG.md` (đầu ra #4) — đây là
  "log service" của bộ công cụ này (không phải service chạy nền, mà là nhật ký bắt
  buộc theo mỗi lần thực thi instruction). Cơ chế tắt cụ thể: biến môi trường
  `TDQ_EXPORT_NO_LOG=1` đặt trước khi chạy bước ghi log trong `INSTRUCTIONS.md` —
  `INSTRUCTIONS.md` phải nêu rõ biến này ở bước ghi log (bước 7) kèm ví dụ lệnh,
  và nêu rõ đây là ngoại lệ có chủ đích (không phải mặc định).
- Không placeholder mô tả kiểu "TODO", "sẽ bổ sung sau" trong `README.template.md`
  hay `INSTRUCTIONS.md` — placeholder DUY NHẤT được phép là chỗ điền 2 API key
  (đã có lý do rõ ràng ở §3).
- Không mock dữ liệu: manifest bundle mẫu (đầu ra #5) phải chứa dữ liệu THẬT đọc từ
  máy nguồn tại thời điểm chạy, không phải dữ liệu ví dụ tĩnh chép tay.
- Mỗi đầu ra ở §2 có ít nhất 1 hạng mục QC tương ứng ở §6, kiểm bằng lệnh — không
  kiểm bằng cảm tính.

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Vô tình ghi giá trị thật của API key/token vào bundle hoặc log | Rò rỉ secret nếu bundle được chia sẻ | `INSTRUCTIONS.md` quy định rõ bước lọc secret TRƯỚC bước copy; đầu ra #5 có tiêu chí QC `grep` giá trị thật trả về rỗng (§2 dòng 5, §6) |
| Đường dẫn tuyệt đối `extraKnownMarketplaces.tdq-local` trong `settings.json`/`known_marketplaces.json` export vẫn trỏ về vị trí repo trên MÁY NGUỒN, không tự đổi khi copy sang máy đích | Plugin `tdq-workflow` (đang chạy chính request này) không load được trên máy đích — mâu thuẫn trực tiếp với mục tiêu §1 | `INSTRUCTIONS.md` có bước rewrite path riêng (bước 4/7, bắt buộc, không tuỳ chọn); QC Q8 kiểm path trong bundle khớp đúng vị trí đích thực tế |
| README đa nền (macOS/Linux/Windows) thiếu chính xác cho Linux/Windows vì máy nguồn là macOS, không kiểm thử trực tiếp được lệnh trên 2 OS kia | Người dùng máy Linux/Windows làm theo README bị lỗi | Đã research và xác nhận qua nguồn chính thức (`research` §5-6): Windows có 3 lựa chọn chính thức (native qua winget/npm — không cần WSL —, WSL2 khuyến nghị khi cần sandbox, WSL1 fallback); Codex CLI có 4 cách cài chính thức đa nền, dùng npm làm phương án chung cho cả 3 OS. README dùng đúng các lệnh chính thức này thay vì đoán; ghi rõ trong README dòng nào đã test trực tiếp (macOS) vs chỉ đối chiếu tài liệu chính thức (Linux/Windows) |
| Repo TDQWorkflow không có git remote → copy vật lý repo vào bundle có thể copy luôn thư mục `.git` nặng hoặc dữ liệu chưa commit | Bundle nặng không cần thiết, hoặc lộ file chưa commit không mong muốn | `INSTRUCTIONS.md` quy định copy qua `git archive`/`rsync` loại trừ `.git` nếu không cần lịch sử, hoặc copy nguyên `.git` nếu cần giữ lịch sử — chốt cách nào ở bước plan (không phải quyết định đổi kết quả, chỉ là chi tiết kỹ thuật) |
| Danh sách plugin cài lại thủ công từng dòng dễ gõ sai tên/marketplace | Máy đích thiếu hoặc cài sai plugin so với máy nguồn | README liệt kê nguyên văn từ `installed_plugins.json`/`known_marketplaces.json` đọc trực tiếp lúc điền manifest, không gõ tay lại từ trí nhớ; QC Q6 đối chiếu số lượng khớp 100% |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | `INSTRUCTIONS.md` đủ 6 bước, mỗi bước có lệnh cụ thể | Đọc thủ công + đối chiếu checklist 6 bước trong §2 dòng 1 | Đủ 6 bước, không bước nào thiếu lệnh |
| Q2 | `MANIFEST.template.json` là JSON hợp lệ, đủ 5 khoá | `python3 -m json.tool claude-export/MANIFEST.template.json` | Exit 0; có đủ `plugins`, `marketplaces`, `mcp_servers`, `cli_dependencies`, `excluded` |
| Q3 | `README.template.md` đủ 6 mục theo thứ tự | Đọc thủ công + đối chiếu §2 dòng 3 | Đủ 6 mục, đúng thứ tự |
| Q4 | Bundle mẫu (đầu ra #5) không chứa giá trị thật của 2 API key | `grep -r` giá trị thật 2 key trên toàn bộ thư mục bundle | Kết quả rỗng |
| Q5 | Bundle mẫu có đủ cấu trúc thư mục | `ls` đối chiếu `manifest.json`, `README.md`, `config/`, `tdqworkflow-repo/` | Đủ cả 4, không thiếu |
| Q6 | Manifest trong bundle mẫu khớp trạng thái thực máy nguồn | Đối chiếu số lượng + tên plugin/marketplace trong `manifest.json` với `installed_plugins.json`/`known_marketplaces.json` sống tại thời điểm chạy | Khớp 100% số lượng và tên (trừ `superpowers` — ngoài phạm vi, đã loại ở §1) |
| Q7 | `EXPORT_LOG.md` có entry cho lần chạy thử | Đọc file, kiểm định dạng timestamp | Có ít nhất 1 dòng entry hợp lệ |
| Q8 | Path `extraKnownMarketplaces.tdq-local` trong bundle mẫu khớp đúng vị trí thực tế của `tdqworkflow-repo/` sau copy (không còn trỏ về đường dẫn máy nguồn) | Đọc `config/settings.json` trong bundle, so `extraKnownMarketplaces.tdq-local` với đường dẫn tuyệt đối thật của `tdqworkflow-repo/` trong cùng bundle | Hai đường dẫn khớp tuyệt đối |
| Q9 | Cơ chế tắt log (`TDQ_EXPORT_NO_LOG=1`) hoạt động đúng | Chạy `INSTRUCTIONS.md` bước ghi log 1 lần có đặt biến, 1 lần không đặt biến; đối chiếu `EXPORT_LOG.md` trước/sau mỗi lần | Có đặt biến → không thêm entry mới; không đặt biến → thêm đúng 1 entry mới |
| Q10 | Bundle mẫu không lẫn dữ liệu runtime/cache/máy-cụ-thể thuộc danh sách loại trừ ở §1 | `find`/`ls -R` bundle mẫu, đối chiếu từng tên trong danh sách loại trừ §1 (`history.jsonl`, `sessions/`, `cache/`, `logs/`, `machineID`, `oauthAccount`, ...) | Không tìm thấy bất kỳ mục nào trong danh sách loại trừ bên trong bundle |

DoD: cả 10 hạng mục Q1–Q10 PASS; `claude-export/` đã commit vào repo TDQWorkflow (nội
dung không chứa secret thật — kiểm lại bằng Q4 áp dụng luôn cho `claude-export/`);
bundle mẫu đã sinh ra thành công tại đường dẫn đích cho lần chạy thử.

## 7. Câu hỏi còn mở
(Rỗng — không còn câu hỏi nào làm đổi kết quả.)
