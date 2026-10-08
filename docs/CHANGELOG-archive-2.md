# Changelog — bản lưu trữ 2

Các bản 0.42.0 đến 0.37.0, tách khỏi `CHANGELOG.md` ngày 2026-10-03 (0.39.0 ngày 2026-10-05, 0.40.0 ngày 2026-10-07, 0.42.0–0.41.0 ngày 2026-10-08) để file chính dưới trần R6
500 dòng (`docs/CHANGELOG-archive.md` đã đầy). Mới nhất trên cùng, chữ nghĩa copy nguyên văn.
Lần tách sau: chuyển các bản cũ nhất còn trong `CHANGELOG.md` vào ĐẦU file này.

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
