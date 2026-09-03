# Changelog

Mới nhất trên cùng. Ngày theo múi giờ máy phát hành.

## 0.44.0 — 2026-09-03

Luật routing biết tới UI/UX. Trước bản này bảng routing không có dòng nào cho giao diện, mà
dòng chốt bảng lại bảo "việc không khớp dòng nào thì đừng kéo plugin vào" — nên `ui-ux-pro-max`
đang bị luật cản chứ không trung lập.
Báo cáo: `docs/tdq/report/2026-09-03-1949-uiux-pro-max-routing.md`.

- **Khối luật `UI/UX — three layers`** — chia việc giao diện làm ba tầng: chiến lược sản phẩm
  (chưa plugin nào phủ), quyết định thiết kế (tầng DUY NHẤT `ui-ux-pro-max` phủ), kiểm chứng
  trên máy thật (`chrome-devtools-mcp`). Kèm một dòng mới trong bảng routing.
- **Chữ dùng là tra cứu, không phải mệnh lệnh** — plugin được mô tả là "CATALOGUE TO CONSULT,
  not a step to execute"; mặc định tra khi trúng tầng 2, bỏ qua được chỉ cần một dòng lý do.
  Có ca test cấm các từ ra lệnh tuyệt đối lọt vào khối luật.
- **Ghép được, không loại trừ nhau** — `frontend-design`, `figma`, `chrome-devtools-mcp` dùng
  chung được khi hai bên bổ trợ. Loại trừ Unity/game vì bộ dữ liệu không có dòng nào cho nó.
- **Vá `skill_inventory.py`** — thử `<installPath>/skills` rồi mới `.claude/skills`, nên bước
  B0 hết mù với plugin để skill theo bố cục thứ hai: 0 → 7 dòng `plugin:ui-ux-pro-max`, các
  nguồn plugin khác không đổi một dòng nào.
- **Dọn `CHANGELOG.md`** — cắt 0.21.0–0.24.0 sang `CHANGELOG-archive.md` để file chính về
  dưới trần 500 dòng của doc_lint R6.

## 0.43.0 — 2026-09-03

Vá bốn lỗi đa nền tảng P1–P4 mà bản rà 1648 tìm ra. Không có máy Windows, nên mọi hạng mục
Windows nghiệm thu bằng THAM SỐ giả lập: mức khẳng định cao nhất là "hàm cho ra đúng tên lệnh
khi truyền hệ Windows vào", không phải "đã chạy được trên Windows".
Báo cáo: `docs/tdq/report/2026-09-03-1733-sua-loi-da-nen-tang.md`.

- **Tên lệnh Python chọn theo hệ đích (P1)** — `tien_to_python(nen_tang)` cho `py -3` trên
  Windows, `python3` nơi khác. Hook codex/agy sinh qua hàm đó. Riêng `hooks/hooks.json` là file
  nguồn viết tay nên có lệnh sinh lại tại máy đích: `build_portable.py --sinh-hook-claude
  [--he-dich win32]`, bất biến, chạy lần hai in `already correct`.
- **Cổng gác bundle agy hết là mã chết (P2)** — `kiem_layout_agy` parse JSON và chỉ soi `~`
  trong giá trị `command`, thay vì quét văn bản thô cả file. Hết dương tính giả, nhánh "dựng ở
  máy khác" nay nổ được, và `hooks.json` hỏng cú pháp được báo thay vì im lặng.
- **README bundle agy nói rõ chuyện gắn máy dựng (P3)** — đừng copy bundle dựng sẵn, tên lệnh
  Python khác nhau giữa các hệ, lệnh kiểm lại sau khi copy. Sửa ở hằng `README_AGY`, vì file
  README của bundle là file sinh ra.
- **Dòng `Test:` của plan chạy được nơi không có tên lệnh `python3` (P4)** — token đầu đổi sang
  `sys.executable`. Giữ `shell=True` để không hỏng plan cũ, thay bằng cảnh báo khi gặp toán tử
  shell vì cú pháp `cmd.exe` khác `sh`.

## 0.42.0 — 2026-09-03

Chống conflict khi chạy sub-agent implement: năm lỗ hổng H1–H5 từ chỗ chỉ là câu chữ trong tài
liệu nay đều có hàng rào máy. Kèm đổi toàn bộ sub-command của 5 script CLI sang tên tiếng Anh.
Báo cáo: `docs/tdq/report/2026-09-03-1527-sub-agent-chong-conflict.md`.

- **Tên lệnh tiếng Anh, tên cũ thành bí danh ẩn** — `scripts/tdq_ten_lenh.py` là một nguồn sự
  thật cho 22 sub-command của `tdq_team`, `tdq_bench`, `tdq_eval`, `tdq_lsp`, `tdq_state`. Bí
  danh giải ở tầng argv nên `--help` chỉ in tên mới, còn hook/bundle/tài liệu cũ vẫn chạy đúng.
  Giá trị dữ liệu (`mo`/`dong` của sổ worktree, mã lý do như `vung-khoa`) giữ nguyên tiếng Việt.
- **`check` kiểm lại thật (H5)** — chạy chính lệnh trên dòng `Test:` của task trong worktree của
  nó. `TICK-READY` của agent con không còn là lời tự khai.
- **`merge` từ chối nhánh có test đỏ, và tự rebase trước (H2)** — rebase lên bản tích hợp mới
  nhất, hỏng thì `rebase --abort` trả worktree về nguyên trạng.
- **Lệnh mới `resolve` (H4)** — chỉ đọc, in hai phía của từng file kẹt để gỡ conflict.
- **Dòng `Chạm:` thành hàng rào máy (H1)** — agent con ghi ra ngoài vùng đã khai thì bị chặn
  ngay lúc ghi, không phải lúc merge. Mode `main` không đổi hành vi.
- **`assign` cảnh báo file nóng (H3)** — đường dẫn nằm trên ≥2 dòng `Chạm:` được nêu tên trước
  khi mở nhánh nào, lúc mà cách sửa còn rẻ.

## 0.41.0 — 2026-09-03

Sửa tương thích thật với cả 3 host: Claude Code, Codex CLI 0.149, Antigravity CLI (agy) 1.1.11.
Trước bản này, bundle agy KHÔNG chạy được (hook sai đường dẫn, sai payload deny, layout không
phải plugin) và README codex thiếu hai thủ tục bắt buộc. Báo cáo:
`docs/tdq/reports/2026-09-03-1440-kiem-tuong-thich-3-host.md`.

- **`antigravity_portable/`** — dựng lại đúng chuẩn plugin agy 1.1.11: `plugin.json` ở gốc,
  `hooks.json` + `mcp_config.json` ở gốc, bỏ hẳn thư mục `config/`. **Bỏ hẳn
  `settings.json`**: file thật của người dùng giữ `model`/`colorScheme`/`trustedWorkspaces`,
  copy đè là mất cấu hình mà không thêm được hàng rào nào. README từ 6 đường cài đoán còn 3
  bước thật (copy thư mục · bật trong `config.json` · khai skill root trong `skills.json`).
- **`hooks/scripts/agy_pretooluse_gate.py`** — payload deny phát CẢ `allow_tool: false` lẫn
  `decision: "deny"` vì Google chưa công bố schema chính thức; thiếu khoá đúng thì deny bị bỏ
  qua trong im lặng. Đường dẫn `command` trong `hooks.json` nay là tuyệt đối đã bung `~` —
  dấu `~` trong nháy kép không được bung, hook chết exit 127.
- **`portable_codex/README.md`** — thêm mục trust hook (`trusted_hash` ghim NỘI DUNG hook, dựng
  lại bundle là mất trust, phải duyệt lại bằng `/hooks`) và mục export biến môi trường
  (`env_vars` chỉ khai TÊN biến, TOML không nội suy). 0.149 đã bật hooks sẵn, không cần
  `[features] hooks = true`.
- **`.claude-plugin/plugin.json`** — thêm `displayName` và `userConfig` cho 2 khoá Tavily,
  `sensitive: true` để giá trị không bao giờ hiện ra. Validator đòi thêm trường `title` (không
  có trong tài liệu).
- **`scripts/tdq_checkportable.py`** — nhận diện layout plugin agy, cảnh báo khi `hooks.json`
  còn `~` chưa bung hoặc mang `$HOME` của máy khác.
- **`tests/test_tuong_thich_host.py`** (mới) — 6 test khoá 6 điểm tương thích; 5 test agy cũ
  trong `test_build_portable.py` viết lại theo layout mới.

## 0.40.0 — 2026-09-03

Cổng hỏi bằng chat thường, dòng `Next step:` nêu tên pha kế, và đường kẻ `---` kết lượt. Kèm
phần hướng dẫn cài qua marketplace + auto-update + bump version trong `README.md`. Báo cáo:
`docs/tdq/report/2026-09-03-1220-gate-chat-va-next-pha.md`.

- **`skills/tdq-conventions/references/user-facing-block.md`** — luật cấm tool hỏi dạng popup
  (`AskUserQuestion`) chuyển từ `tdq-intake` lên tầng conventions, áp cho MỌI câu hỏi chứ không
  riêng 7 cổng duyệt; thêm thành phần 6 của khối trả lời: đúng một dòng `---` kết lượt.
- **`skills/tdq-conventions/references/approval.md`** — mục `## Hỏi xong là kết lượt`.
- **12 dòng `Next step:` trong 8 skill** — mỗi dòng nêu tên pha kế tiếp hoặc nói rõ pha không
  đổi kèm skill kế, để host không có hook vẫn đi đúng lộ trình. Lớp này là DỰ PHÒNG,
  `[TDQ:NEXT]` vẫn là đường chính.
- **`tests/test_luat_gate_chat.py`** (mới) — 7 test khoá ba luật trên; tên pha đọc thẳng từ
  `PHASE_TABLE` chứ không chép cứng.
- **`README.md`** — 3 cách cài (marketplace / `--plugin-dir` / bundle portable), mục
  `## Cập nhật` và thủ tục bump version bắt buộc mỗi lần release.

## 0.39.0 — 2026-09-03

Thang `tdq_lsp.py kiem` thêm **bậc 7** và luật thứ tự tìm kiếm đổi từ một thứ tự cứng sang chọn
lớp theo LOẠI truy vấn. Lý do: thang cũ báo **6/6 ĐẠT** trong cả trạng thái độ phủ truy vấn quan
hệ 7 % lẫn 100 % — nó kiểm sự tồn tại, không kiểm hiệu quả. Báo cáo:
`docs/tdq/report/2026-09-03-0053-sua-luat-va-kiem-lsp-that.md`.

- **`scripts/tdq_lsp.py`** — bảng `LANG_CONFIG` (file mốc gốc import cho 26 ngôn ngữ, chia nhóm
  A/B) và bậc 7 `bac7_cau_hinh_goc_import`. Nhóm B (Python, TS/JS, Lua, C/C++) thiếu file mốc thì
  **CHẶN, thoát 3** vì chỉ mục liên file chết âm thầm mà test vẫn xanh; nhóm A (`go.mod`,
  `Cargo.toml`…) chỉ cảnh báo vì thiếu là dự án không build được, tự lộ. Script chỉ in nội dung
  cần tạo và xin phép, không bao giờ tự ghi file.
- **`skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`** — luật gốc thay bằng bảng 4 loại truy
  vấn kèm số đo: quan hệ → `mcp__lsp__*` (phủ 15/15, grep chỉ precision 67 %); tên chính xác →
  grep (~0,1 s so với 3–6 s); khái niệm mơ hồ → lumen (LSP xếp đích hạng 13/62); chưa phân loại
  → gọi song song. Câu luật chép lại nguyên văn ở đủ 5 chỗ móc.
- **`skills/tdq-intake/references/kiem-lsp-hieu-ung.md`** (mới) — bước kiểm **bằng hiệu ứng** ở
  intake: so `find_references` với grep theo số file phân biệt, ĐẠT khi LSP ≥ grep. Bậc 7 bắt
  nguyên nhân đã biết, bước này bắt triệu chứng dù nguyên nhân là gì.
- **`pyrightconfig.json`** (mới) — chính file mốc mà repo này đang thiếu, đưa độ phủ truy vấn
  quan hệ từ 1/15 file lên 15/15.

## 0.38.0 — 2026-09-02

Năm luật rời `~/.claude/CLAUDE.md` về plugin, instruction toàn cục cắt 57 → **29 dòng (−49%)**.
Thứ tự bắt buộc: viết luật vào `skills/` trước, kiểm, rồi mới cắt. Phương án gốc:
`docs/tdq/report/2026-09-01-2301-quet-instruction-vao-plugin.md`.

- **`skills/tdq-conventions/`** — `approval.md` nhận luật "không tự vào plan mode" (dưới bảng
  "NOT an approval", cùng họ); `SKILL.md` §7 Git nhận luật init git/worktree và ngoại lệ tự
  commit khi build TDQ bị chặn, đặt sát dòng nó là ngoại lệ; §8 Research nhận luật mem0.
- **`scripts/doc_lint.py`** — trần R6 của `tdq-conventions` 165 → 168, đổi lấy 28 dòng bỏ khỏi
  file nạp mỗi lượt của mọi project.
- **`docs/tdq/audit/luat-hien-co.md`** — 10 neo lệch do phần chèn trên được trỏ lại đúng chỗ.

## 0.37.0 — 2026-09-01

Lane nhanh có bước phân tích HIỆN TÊN, và độ sâu của bước đó có ngưỡng rõ ràng. Trước bản này
`phase_key` nuốt mọi pha của lane nhanh về hàng `quick`, nên phân tích không nhìn thấy được ở
đâu cả. Quan trọng: đây là phương án KHÔNG thêm cổng duyệt — lane nhanh vẫn đúng một cổng.

- **`scripts/tdq_state.py`** — thêm hàng `quick_analyze` vào `PHASE_TABLE` và `PHASE_ORDER`;
  `phase_key` trả hàng đó khi `lane=quick`, `phase=analyze` và chưa duyệt. `CONG_THEO_LANE`
  và `APPROVE_TARGETS` giữ NGUYÊN — có test khoá riêng canh điều này. Thêm khoá `brief_file`
  để đăng ký đường dẫn brief, ngang hàng `spec_file`/`plan_file`.
- **`skills/tdq-intake`** — `quick-lane.md` từ 9 lên 10 bước, chèn bước ghi kết quả phân tích
  vào brief; thêm mục ngưỡng B0/B1/B2: B1 đọc code LUÔN LUÔN (LSP + lumen song song), B0 chỉ
  khi vùng chưa có tiền lệ, B2 chỉ khi có ẩn số ngoài. Bỏ B0 hay B2 phải ghi một dòng lý do
  vào `## Phạm vi` của mini-plan — bỏ im lặng là lỗi QC.
- Ngưỡng lấy từ số đo thật trên 43 request đã đóng sổ. Pha `analyze` trung vị 372 s model,
  một request lane nhanh trọn gói 533 s. Bắt cả ba bước không điều kiện làm lane nhanh chậm
  thêm ~70 %. Chi tiết: `docs/tdq/report/2026-09-01-2122-lane-nhanh-kiem-ke-nang-luc.md`.

## 0.36.0 — 2026-09-01

Gỡ hẳn pha `diagram` (sơ đồ mind map) và cổng duyệt sơ đồ khỏi quy trình. Từ bản này spec duyệt
xong là đi thẳng sang plan, không còn bước vẽ và duyệt sơ đồ chen giữa ở cả lane `full` lẫn lane
nhanh. 16 file sơ đồ đã vẽ trong `docs/tdq/mind-map/` giữ nguyên làm tư liệu; chỉ phần sinh ra
chúng bị xoá.

- **`scripts/tdq_state.py`** — bỏ `diagram` khỏi `VALID_PHASES`, `PHASE_ORDER` và `APPROVE_TARGETS`;
  xoá khoá state `diagrams` cùng `_heal_diagrams`, `_diagram_id`, `diagram_entries`,
  `diagram_pending`, `_diagram_register`, `_cli_approve_diagram`, `_cli_diagram` và dòng
  `| Diagrams |` của bảng trạng thái. Cổng vào pha `plan` nay chỉ đòi `spec_approved = true` —
  chặn thật bằng `_chan_spec_chua_duyet`, vì nhánh cũ chỉ soi danh sách sơ đồ, gỡ đi mà không
  thay thế thì plan viết được trước khi user duyệt spec.
- **Tương thích ngược** — state cũ mang `phase=diagram` tự nâng về `spec` kèm cảnh báo; khoá
  `diagrams` cũ bị bỏ qua im lặng và biến mất khi ghi lại. Ba lệnh cũ (`approve diagram`,
  `diagram add`, `diagram list`) thoát khác 0 và nói rõ pha đã bị gỡ, không báo lỗi cú pháp chung.
- **Xoá** `scripts/tdq_mindmap.py`, `scripts/mindmap_render.py`, `skills/tdq-diagram/`; `doc_lint.py`
  không còn import `tdq_mindmap` và không còn ngân sách token cho skill đã xoá.
- **Tài liệu luật** — `phases.md`, `tdq-spec`, `tdq-plan`, `tdq-intake` và `quick-lane.md` sạch dấu
  vết pha sơ đồ; bước 1b vẽ sơ đồ của lane nhanh đã bỏ.
- **Test** — xoá 4 file test của mind-map, sửa 5 file còn nhắc pha `diagram`, thêm
  `tests/test_state_phase.py` và `tests/test_state_diagram_removed.py` khoá chuỗi pha mới, lối báo
  lỗi tương thích ngược và bảng trạng thái.

## 0.35.0 — 2026-08-27

Trang mind-map HTML chuyển từ danh sách chữ sang sơ đồ nhìn được. Trước bản này trang feature chỉ
có một `<ol>` các bước và trang tổng chỉ có danh sách link lồng nhau — đọc được nhưng không nắm
được luồng trong một cái liếc. Bản này vẽ sơ đồ SVG tĩnh, không phụ thuộc file ngoài nên xem được
cả trong trình duyệt lẫn VS Code preview.

- **`scripts/mindmap_render.py`** — thêm `build_flow_model` (gom `B<n>` với `B<n>!` cùng số thành
  một cặp quyết định), `wrap_label` + `layout_flow` (hộp tự cao theo số dòng chữ, không cắt cụt,
  không chồng lấn), bộ helper hình dạng dùng chung `_svg_hop`/`_svg_hinh_thoi`/`_svg_vien_thuoc`/
  `_svg_nhan_nhieu_dong`/`_svg_mui_ten` và `render_flow_svg`. Sơ đồ đứng TRƯỚC danh sách bước
  trong khối cuộn ngang `overflow-x: auto`; danh sách bước cũ giữ nguyên từng chữ bên dưới.
- **Trang tổng** — `build_branch_model` + `layout_branch_tree` + `render_branch_svg` dựng cây
  nhánh tổng → nhánh con → feature thành SVG, mỗi ô feature bọc trong `<a href>` tới trang riêng,
  feature chưa có sơ đồ vẽ nét đứt và mờ, không gắn link. Danh sách link cũ không xoá, lùi xuống
  dưới sơ đồ. `_render_dependency_svg` chuyển sang helper chung và **bỏ cắt cụt `label[:34]`**.
- Log service in số node và số cạnh mỗi lần dựng, tắt bằng `TDQ_LOG=0`.
- **Test** `tests/test_mindmap_render.py` 88 pass — khoá điều kiện không mất một chữ nào của mọi
  bước trong cả 7 file sơ đồ thật, không hộp nào chồng lấn, không mã màu cứng, không thẻ trỏ ra
  ngoài (`<script src`, `<link href`, `http(s)://`).

## 0.34.0 — 2026-08-26

Luật tìm kiếm code đổi từ tuần tự sang song song. Trước bản này agent-lsp chạy trước, lumen chỉ
được gọi khi LSP trả rỗng — đúng cho câu hỏi có tên symbol nhưng bỏ lỡ câu hỏi khái niệm không
tên trong cùng một lượt tìm. Bản này gọi cả hai cùng lúc, gộp kết quả trước khi đọc.

- **`skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`** — câu luật gốc đổi thành "gọi song
  song `mcp__lsp__*` và lumen cho mọi câu hỏi tìm ký hiệu code, gộp kết quả; grep vẫn lớp cuối".
  Điều kiện đánh thức Ollama đổi theo: không còn chờ LSP rỗng, chạy ngay mỗi câu hỏi tìm code —
  vẫn đánh thức-rồi-tắt, không thường trực. Ghi rõ lumen tự incremental-reindex theo Merkle root
  hash khi index cũ nên không cần thêm bước/script reindex riêng.
- Đồng bộ nguyên văn câu luật vào 5 chỗ móc (`tdq-intake` x2, `tdq-spec`, `tdq-plan`,
  `tdq-build`), hai bản portable cuốn theo qua `build_portable.py`.
- **Test** `tests/test_tdq_lsp_skill.py` xanh (4 test, 10 subtest) sau khi đổi.

## 0.33.0 — 2026-08-24

Phase `implement` được gác ở chỗ kết lượt. Trước bản này luật "làm hết plan trong một lượt" chỉ
là câu chữ trong skill. Hai cổng `Stop` sẵn có đều bám vào file vừa sửa trong lượt, nên một
lượt không sửa gì mà plan còn task hở vẫn kết được. Bản này biến câu luật đó thành cổng chạy
thật.

- **Cổng `[TDQ:UNFINISHED]` trong `hooks/scripts/stop_gate.py`** — còn ở phase `implement` mà
  plan trên đĩa còn task hở thì `Stop` trả `decision: block`. Payload trả kèm
  `stop_hook_active: false` nên cổng nạp đạn lại, chặn được cả lượt lặp. Ba ca vẫn im lặng đi
  qua: đang chờ người dùng, còn task `[>]` giao cho sub-agent, hoặc đã khai tạm hoãn.
- **Khoá `implement_pause` và hai lệnh `tam-hoan --ly-do "<vì sao>"` / `tiep-tuc`** trong
  `scripts/tdq_state.py` — đường dừng hợp lệ duy nhất. Hook không tự biết lỗi có tự sửa được
  hay không, nên người dừng phải khai lý do, và lý do đó được in ra cho người dùng.
- **Bộ đếm chặn liên tiếp** khoá theo sha của plan: ba lần không tiến triển thì cổng hạ xuống
  nhắc `[TDQ:STUCK]` để phiên không kẹt vĩnh viễn; đếm về 0 ngay khi một checkbox nhúc nhích.
- **Luật viết vào `skills/tdq-build/SKILL.md` và bảng phase** (sinh từ hằng `PHASE_TABLE`), hai
  bản portable cuốn theo.

## 0.32.0 — 2026-08-23

Sơ đồ giải thuật thành cổng bắt buộc trước khi viết plan. Trước bản này workflow đi thẳng từ
spec sang plan: người duyệt phải đọc bảng task để đoán ra luồng chạy. "Sơ đồ" nếu có thì cũng
chỉ là chữ trong file, không ai kiểm được nó còn khớp code hay không. Bản này bổ sung đủ ba
mảnh: một script chạy được, một phase có cổng chặn thật, và một trang HTML hai lớp — người
duyệt xem lớp nghiệp vụ, người sửa code xem lớp chi tiết.

- **`scripts/tdq_mindmap.py` — 5 lệnh** `sinh` / `kiem` / `lien-he` / `doi-chieu` / `xem`.
  `kiem` bắt sai khuôn (thiếu `@nhánh`, `@phụ-thuộc` sai định dạng, bước không đánh số);
  `lien-he` bắt vòng lặp phụ thuộc và phụ thuộc trỏ hụt; `doi-chieu` so sơ đồ với `graph.json`
  (lọc node theo `file_type == "code"`, cảnh báo khi `built_at_commit` lệch `HEAD` chứ không tự
  chạy lại graphify). Bốn mã thoát dùng chung: `0` sạch, `1` vi phạm, `2` sai cú pháp, `3` cần
  cập nhật.
- **Phase `diagram` chen giữa `spec` và `plan`** — chuỗi phase 10 → 11 bậc. Cổng nằm trong
  `scripts/tdq_state.py`, không phải hook — theo luật hook chỉ nhắc chứ không `deny`. `set
  phase=plan` bị từ chối khi danh sách sơ đồ rỗng hoặc còn cái chưa duyệt. Chặn xong thì gọi
  đích danh từng file thiếu, không xoá gì. State cũ chưa có khoá này vẫn đi qua bình thường.
- **Trang HTML hai lớp** — `scripts/mindmap_render.py` dựng lớp nghiệp vụ (thứ người duyệt đọc)
  và lớp chi tiết mỗi function một step, sinh từ `graph.json` với docstring làm lời giải thích;
  `--tong` cho trang tổng gom theo `@nhánh` kèm lưới phụ thuộc. Trang tự chứa, không cần mạng.
- **Skill `tdq-diagram`** mới, ba skill cũ (`tdq-spec`, `tdq-plan`, `tdq-intake`) dẫn vào phase
  mới. `doc_lint.py` và `mindmap_render.py` cùng import `check_diagram`/`build_link_graph` từ
  `tdq_mindmap.py` nên ba công cụ không thể bất đồng về "sơ đồ hợp lệ là gì".
- **Test** 1444 → 1498 xanh (54 test mới). Tập đỏ đối chiếu mốc `7e3bbd0` ra rỗng phía mới:
  0 hồi quy, 6 đỏ cũ nay xanh.

## 0.31.0 — 2026-08-23

Bộ workflow có lớp tìm kiếm bằng LSP. Trước bản này mọi phase đi tìm ký hiệu đều rơi về grep:
đúng chữ nhưng không biết chữ đó là định nghĩa hay chỉ là một lần gọi, càng không lần được ai
đang dùng nó. Máy đã có `agent-lsp` nhưng không có gì trong repo nói cho Claude biết nó tồn
tại, phải cài gì để nó chạy được với ngôn ngữ của project, hay khi nào thì dùng nó thay grep.
Bản này viết đủ ba mảnh đó: cách dựng, cách kiểm, và luật thứ tự ưu tiên.

- **Skill mới `skills/tdq-lsp-setup/`** — thang 6 bậc cài đặt (binary → language server → cấu
  hình MCP → đăng ký → Ollama → hook ngoài). Kèm bảng 30 ngôn ngữ `agent-lsp` hỗ trợ, mỗi dòng
  một lệnh cài language server. Cuối skill là mục runbook chép nguyên 5 bước đã chạy thật trên
  máy này: đổi máy hay thêm ngôn ngữ thì đọc lại mà làm, không phải dò lại từ đầu.
- **`scripts/tdq_lsp.py`** — 3 lệnh `kiem` / `danh-thuc` / `nha`. Bậc 1–4 thiếu là chặn, bậc 5–6
  chỉ cảnh báo. Script **không bao giờ tự cài**: nó in lệnh cài ra và để user quyết, vì cài đặt
  ngoài repo là việc của người dùng chứ không phải của agent.
- **Luật "LSP trước · lumen khi LSP rỗng · grep cuối"** móc vào 5 chỗ: intake, analyze-full,
  spec, plan, build. Câu luật viết một chỗ, 4 chỗ kia trích nguyên văn, và
  `tests/test_tdq_lsp_skill.py` so từng chữ — sửa một chỗ mà quên chỗ còn lại là đỏ ngay.
- **Bản portable sinh lại cả hai** — `portable_claude` chép nguyên cây nên tự có skill mới;
  `portable_codex` phải đăng ký vào `THU_TU_SKILL` của `scripts/build_portable.py` vì số đầu tên
  file workflow chính là cơ chế định tuyến cho harness không có hệ thống skill. Thêm một skill
  là số dịch hết, nên hai test khoá cứng `03-spec`/`06-checkportable` đổi sang dò theo đuôi tên.



Câu hỏi trắc nghiệm luôn có số ở đầu. Trước bản này luật đánh số ĐÃ tồn tại: `scope-round.md`
viết rõ "gộp câu 1 và các câu bối cảnh vào một khối, đánh số liên tục". Nhưng nó chỉ nằm ở
hai file con đi hỏi, chưa bao giờ được nâng lên file khuôn gốc. Hệ quả: khối chỉ có một câu
(`lane-decision.md`, `mode-gate.md`) không có số nào. Hai danh sách trong cùng một message vì
thế cùng mở đầu bằng `A`, user trả lời một chữ cái thì không biết thuộc câu nào. Đây là lỗi
VI PHẠM luật sẵn có, không phải lỗi thiếu luật — nên bản này vá đúng hai chỗ hổng đó.

- **Luật trang trí thứ 8** trong `skills/tdq-conventions/references/user-facing-block.md`: mọi
  câu có danh sách option đều mở đầu bằng `<số>. `, số chạy liên tục trong cả khối, **áp cả
  khi khối chỉ có đúng MỘT câu**. Không có ngoại lệ cho ca một câu: chữ cái không có số đứng
  trước là mơ hồ ngay khi câu thứ hai xuất hiện. Cấm luôn việc gộp hai câu vào một số.
- **Bước tự-soát bắt buộc trước khi gửi** trong mục "Hard rules" của cùng file: khối có ít
  nhất một danh sách option thì phải đọc lại bản nháp và trả lời ba câu. Mọi câu đã có số
  chưa · số có liên tục, không trùng không nhảy chưa · mỗi option có riêng một dòng chưa. Đây
  là mảnh còn thiếu thật sự: luật đã viết ra mà vẫn trôi vì không ai đọc lại bản nháp.
- **Năm file mẫu khớp theo**: `interview.md` bỏ điều kiện "several questions in one round" và
  đổi dòng hướng dẫn trả lời sang ví dụ `"1a 2b"` · `scope-round.md` nói rõ câu 1 là `1.`,
  câu bối cảnh đầu tiên là `2.` · `lane-decision.md` và `mode-gate.md` thêm dòng số trước khối
  option, dòng ➤ đổi thành `nhắn "1a" / "1b"` · `approval.md` khớp lại cách hỏi mode.
- **Luật được khoá bằng test, không bằng trí nhớ**: `test_hard_rules_giu_buoc_tu_soat` bắt mục
  "Hard rules" phải giữ bước tự-soát và đúng ba câu soát đánh số; `test_user_facing_block.py`
  nâng từ bảy lên tám luật. Trước đó xoá sạch bước tự-soát khỏi file luật mà cả suite vẫn xanh.
- **`~/.claude/CLAUDE.md` mục 1** đồng bộ cùng nội dung — luật gốc nằm ngoài repo nên phải sửa
  tay, có ghi trong report.
- **Neo `docs/tdq/audit/luat-hien-co.md` refresh 33 dòng**: chèn luật 8 đẩy mọi neo phía dưới
  xuống, tỉ lệ lệch lên 10% so với ngưỡng 5%. Chữ neo còn nguyên cả 33 — máy đối chiếu bằng
  chữ, số dòng chỉ để người mở đúng chỗ — nên refresh bằng chính hàm dò neo của test.

## 0.29.0 — 2026-08-22

Đóng sổ mà còn ô tick trống thì hook nhắc. Trước bản này `plan_tick_state()` chỉ đếm ô có mã
task in đậm, nên mọi dòng Definition of Done đều vô hình: plan tick đủ task là `all_done` bật
True dù cả 19 dòng DoD còn trống. Chốt chặn `[TDQ:TICK]` lại chỉ bắn ở phase `implement` và
`qc` — đúng lúc đóng sổ ở `report` thì không còn ai canh, bảo hiểm duy nhất là một câu văn
xuôi trong khuôn report dựa vào trí nhớ của model.

- **Nhắc `[TDQ:DOD]` ở phase `report` và `idle`**: bắn khi QC đã PASS sạch mà ô tick còn
  trống, nêu cả số task lẫn số dòng DoD còn lại. Nó **chỉ nhắc, không chặn** — turn vẫn kết
  thúc bình thường. Nhắc xếp đầu danh sách hint để không bị cắt mất khi đã có bốn nhắc khác.
- **Ba bộ đọc riêng trong `scripts/tdq_state.py`**: `dod_tick_state()`, `qc_result_state()`,
  `task_open_count()`. Cố ý KHÔNG nới `_TASK_LINE`: bốn nơi phụ thuộc hợp đồng trả về của
  `plan_tick_state()`, nới ra là lệch `all_done` và lệch cả ETA của status line.
- **Bốn cửa im lặng** giữ cho hook chạy ở user scope không cằn nhằn nhầm: sai phase · mục DoD
  không dùng ô tick (plan viết trước đây đếm 0, không bao giờ bị nhắc) · đã tick đủ · file qc
  chưa có, còn FAIL, hoặc còn hạng mục chưa kết luận.
- **Hai khuôn skill cập nhật theo**: plan bắt DoD viết dạng ô tick, report bước 8 nói rõ phải
  tick CẢ HAI loại ô — ô task từng phase và ô Definition of Done.
- **Bộ dò trùng lặp tài liệu `scripts/doc_dup.py`**: cắt shingle, gộp khối, đếm token bằng bộ
  đếm thật trong `.venv-tokens`; thiếu thư viện thì thoát mã 3 chứ không lùi về ước lượng
  ký-tự-chia-bốn. Kèm hồ sơ rà soát bốn mặt và bảng top 10 đề xuất tối ưu.

## 0.28.0 — 2026-08-22

Worktree do workflow đẻ ra không còn nằm lại ăn disk. Trước bản này, mode đội tạo worktree
cho từng task rồi bỏ đó: không ai nhớ có bao nhiêu cái, cái nào merge rồi, cái nào còn việc
chưa commit. Nay có sổ, có lệnh quét, và có ba chốt kiểm không cho quên.

- **Sổ worktree sống xuyên request**: `docs/tdq/worktrees.json` (máy đọc) +
  `docs/tdq/worktrees.md` (người đọc), ghi qua đúng một cửa là `scripts/tdq_team.py`.
  Module `scripts/tdq_worktree_registry.py` (mới) thuần dữ liệu, không gọi git một lần nào,
  nên ba nơi đọc nó — lệnh đội, cổng state, hook — dùng chung một khuôn. Cả hai file đã
  gitignore: chúng chứa đường dẫn tuyệt đối của máy bạn.
- **Lệnh mới `soat` / `soat --don`**: quét mọi worktree của MỌI request, in bảng tuổi ·
  dung lượng · sạch · đã merge, cảnh báo khi tổng vượt 500 MB hoặc một worktree quá 7 ngày.
  Chỉ đụng tới bên trong `.tdq-worktrees/`; thư mục ngoài vùng đó chỉ được liệt kê, không
  bao giờ bị xoá — nó có thể là chỗ làm việc của chính bạn.
- **Xoá cần đủ ba điều kiện**, không bao giờ theo cảm tính: sạch · nhánh đã nằm trong nhánh
  tích hợp · git không giữ khoá. Thiếu một điều là KHÔNG xoá gì cả. `hop` tự dọn worktree và
  nhánh task khi đủ ba, giữ nhánh tích hợp.
- **Worktree chưa dọn được luôn kèm đường ra**: khối `NOT CLEANED UP YET` in cuối kết quả
  lệnh, mỗi lý do chặn có ít nhất một phương án chạy được thật. Skill bắt đặt khối đó ở cuối
  turn theo `doc_lang` của user, lệnh giữ nguyên văn. Năm lý do đóng: còn việc chưa commit ·
  file bị gitignore mà không sinh lại được · chưa merge · git khoá · git từ chối vì lý do
  khác. Lý do thứ hai đáng giá nhất: một `.env` bị `git worktree remove` xoá là mất hẳn.
- **Ba chốt không cho quên**: `hop` kiểm ngay sau khi merge · `tdq_state.py set phase=qc`
  từ chối mở khi sổ còn dòng mở · hook in một dòng `[TDQ:WORKTREE]` mỗi turn cho tới khi
  sạch. Sổ thiếu hoặc hỏng thì cả ba đều im lặng đi tiếp, không bao giờ giết turn.
- QC độc lập chạy 2 lượt, bắt 16 khiếm khuyết, sửa 15 qua 3 vòng fix. Đáng kể nhất: `mo`
  kiểm ghi được sổ TRƯỚC khi tạo worktree nên không đẻ worktree mồ côi. Kế đó là bỏ
  `--force` khỏi mọi `worktree remove`, để git giữ vai lưới an toàn cuối. Chi tiết:
  `docs/tdq/qc/2026-08-22-1033-quan-ly-worktree.md`.

Còn nợ: vẫn chưa chấm lại bộ `evals/tuan-thu` trên cây đã dịch (nợ từ 0.27.0).

## 0.27.0 — 2026-08-22

Bộ workflow nói được với người dùng ở mọi ngôn ngữ. Luật viết bằng tiếng Anh — thứ model
đọc chính xác nhất và tốn ít token nhất — còn tài liệu sinh ra cùng mọi câu nói với user
đi theo ngôn ngữ của chính user. Trước bản này, muốn dùng workflow là phải đọc được tiếng
Việt.

- **Ngôn ngữ chia 3 tầng**, ghi ở mục `## 0. Language` của `tdq-conventions/SKILL.md`:
  luật (`skills/`, `agents/`, chú thích + docstring của `hooks/` và `scripts/`) và chuỗi
  máy in ra viết TIẾNG ANH cố định, không bảng tra i18n; tài liệu và lời thoại viết theo
  trường `doc_lang`.
- `doc_lang` khai đúng một lần lúc mở request — `tdq_state.py init <slug> <lane> --lang <mã>`
  — và cố định suốt request. Thiếu cờ hoặc state cũ không có trường thì lùi về `vi`, state
  đời trước đọc lên không lỗi.
- Đã dịch: 44 file `skills/**/*.md`, 3 file `agents/*.md`, toàn bộ `hooks/` và `scripts/`.
  Đếm bằng `i18n_check.py`: `skills/`+`agents/` 1127 → 0 dòng tiếng Việt, `hooks/`+`scripts/`
  3099 → 0. Description của 7 skill dài thêm về ký tự (1063 → 1334) nhưng **giảm nửa về
  token** (628 → 304, đo bằng `anthropic-tokenizer`) — đây là phần luôn nằm trong system prompt.
- `scripts/i18n_check.py` (mới): quét một vùng đường dẫn, tách 3 loại dòng
  (`--kind comment|string|body`), exit 1 khi còn sót. Cụm `i18n-allow` trên dòng là cửa
  miễn cho chuỗi user thấy phải giữ nguyên từng chữ; một dòng chú thích HTML ngay trên
  khối ``` miễn cho cả khối khuôn mẫu.
- Cổng duyệt nhận **tiếng Anh** ("approve spec", "approve plan") và **một chữ cái** `a`–`d`
  ở cổng mode, đúng như bộ ca âm cũ vẫn phải trượt. Hai ca eval mới
  (`duyet-spec-tieng-anh`, `duyet-bang-chu-cai`) khoá hai đường này; bộ `evals/tuan-thu`
  đi từ 10 lên 12 ca.
- Gộp 6 commit chưa phát hành trước đó. Về context: bộ skill chuyển thể lai · thước đo
  đếm token thật cộng luật cắt output · phẳng hoá reference về tầng 1. Về lỗi đọc plan:
  `doc_plan` không còn nuốt dòng `Chạm:`/`Cần:` khi mô tả task xuống dòng · mã task có
  chữ sau số (`T2A.1`, `T2.4b`) không còn vô hình.

Còn nợ: chưa chấm lại bộ `evals/tuan-thu` trên cây đã dịch — xem mục "Giới hạn" của
`docs/tdq/reports/2026-08-21-2351-quoc-te-hoa-workflow.md`.

## 0.26.0 — 2026-08-18

Cổng duyệt thôi kêu oan. Đo trên 58 request có spec: 7 ca phải xin duyệt lại, trong đó
5 ca là hệ quả của chính thiết kế chứ không phải người dùng làm sai
(`docs/tdq/reports/2026-08-18-2050-spec-doi-sau-khi-duyet.md`). Cổng kêu vì lý do vô hại
nhiều lần thì lúc nó kêu đúng cũng không còn ai nghe.

- `tdq_state.sha256_noi_dung()`: `spec_sha256`/`plan_sha256` băm PHẦN NỘI DUNG, tính từ
  heading `##` đầu tiên. Vùng đầu file (Ngày, Bản, Trạng thái, đường dẫn brief) là sổ sách
  của chính workflow — ghi sổ không còn bị coi là "tài liệu đổi sau khi duyệt". Không có
  heading `##` thì băm cả file. Ba nơi so băm (`tdq_state`, hook `prompt_context`,
  `tdq_checkstatus` ca lệch D3) dùng chung đúng một hàm.
- `doc_lint` rule **R11**: spec có slug từ 2026-08-19 trở đi không được ghi đường dẫn
  `tests/test_*` hay cờ `-k` trong §6 — spec giữ ĐIỀU KIỆN PASS, lệnh kiểm là việc của
  plan. 58 spec sẵn có không bị đụng tới.
- Khuôn spec §6 đổi cột "Cách kiểm" thành "Điều kiện PASS", có bảng ĐÚNG/SAI;
  `qc.md` bỏ đoạn dặn chịu đựng sha lệch.
- `tdq_state.cong_dang_cho()`: cổng duyệt còn thiếu tính theo ĐÚNG lane, `stop_gate` và
  `edit_gate` dùng chung. Trước đó `stop_gate` duyệt danh sách cứng
  `("spec", "plan", "quick")` nên lane quick — vốn không có cổng `spec` — luôn bị nhắc
  "spec vẫn chưa được ghi nhận duyệt", kể cả với request đã duyệt và đã đóng sổ.
  `edit_gate` khi lane rỗng/lạ nay nhắc cổng đầu tiên thay vì im lặng.

## 0.25.0 — 2026-08-18

Mode đội: leader chia việc, agent con chạy song song — và tính modular chuyển thành thuộc
tính của TÀI LIỆU, không còn phụ thuộc mode thực thi.

- `scripts/tdq_team.py`: bản đồ phân công (`phan-cong`, `kiem-ke`, `cum`, `mo`, `kiem`,
  `hop`, `don`), trần 4 nhánh một đợt. Hook `[TDQ:TEAM]` chặn leader tự gõ code của task
  đã hứa giao; file ngoài project được miễn vì bản đồ không nói gì về vùng đó.
- `scripts/tdq_bench.py`: đo và mô phỏng main so với đội, `mo-phong --plan <file>` đọc plan
  thật để cổng đề xuất mode không phải chép lại luật chia đợt.
- Khuôn spec thêm mục ranh giới module; plan luôn khai `Chạm:` và dựng `## Cụm song song`.
  Lane quick được sinh agent con khi mini-plan có từ 3 task tách rời trở lên.
- `scripts/skill_router.py`, `scripts/skill_tokens.py`: đo và định tuyến chi phí context
  của bộ skill.
