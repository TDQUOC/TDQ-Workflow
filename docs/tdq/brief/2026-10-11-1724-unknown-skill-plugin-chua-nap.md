# BRIEF — Phân tích lỗi Unknown skill dù đã gọi đúng namespace tdq-workflow:tdq-intake
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> tôi có gặp tình trạng này hãy mở request phân tích xem tại sao
> [Ảnh: model gọi `Skill({skill: "tdq-workflow:tdq-intake"})` → `Error: Unknown skill: tdq-workflow:tdq-intake`; gọi lại `Skill({skill: "tdq-intake"})` → `Error: Unknown skill: tdq-intake`; model ghi "Skill TDQ chưa được nạp trong phiên này, nên mình đọc trực tiếp file skill trên đĩa".]

**Cách hiểu ban đầu:**
- Mục tiêu: tìm nguyên nhân gốc khiến CẢ HAI dạng tên skill đều báo `Unknown skill`, sau bản sửa namespace 0.66.0.
- Loại: báo lỗi (bug report) → áp `references/issue-triage.md`.
- Bằng chứng thu được lúc mở request (2026-10-11 17:24):
  - `~/.claude/settings.json` → `enabledPlugins` chỉ có `pyright-lsp`, `typescript-lsp` (true) và `figma@synced` (false). **Không có `tdq-workflow@tdq-local`.**
  - `~/.claude/plugins/installed_plugins.json` → `tdq-workflow@tdq-local` cài scope user ở bản **0.59.0**. Có 4 project cài scope project ở bản 0.58.0: `excalidraw`, `WhisperLiveKit`, `claudecodeui`, `TDQ_Monitor_Online`.
  - Cache `plugins/cache/tdq-local/tdq-workflow/0.59.0/skills/` có đủ 9 thư mục skill → file có trên đĩa nhưng harness không nạp.
  - Danh sách skill của chính phiên hiện tại (repo TDQ-Workflow) cũng KHÔNG có skill `tdq-workflow:*` → tái hiện được ngay trên máy này.
  - `~/.claude/CLAUDE.md` đã mang chữ `tdq-workflow:tdq-intake` (đồng bộ từ repo dev 0.66.0). Instruction vì thế đi trước bản plugin đang cài, nên model gọi đúng tên nhưng skill không tồn tại trong phiên.
- Phạm vi đoán: cấu hình bật/tắt plugin (enabledPlugins user/project), cách `tdq_setup.py` ghim instruction vào `~/.claude/CLAUDE.md` mà không kiểm plugin đã bật/nạp, và có thể hook `[TDQ:INTAKE]` chỉ dẫn gọi skill không có trong listing.
- Chỗ chưa rõ:
  - Ảnh chụp từ project nào (trang combo / `ModelSelectModal`)? Project đó có cài plugin scope project không, và host là Claude Code CLI hay CloudCLI?
  - Plugin bị tắt chủ động (`/plugin disable`) hay chưa từng được bật ở scope user?
  - Hướng xử lý mong muốn: chỉ phân tích + hướng dẫn bật lại, hay sửa luôn để workflow tự phát hiện "plugin chưa nạp" và rơi về đọc file skill trên đĩa / cảnh báo người dùng?

## Hiểu & kiến thức

### Năng lực dùng được

| Skill | Nguồn | Phán |
|---|---|---|
| `skill_inventory.py` (hàm gộp `enabledPlugins` 3 tầng) | script repo | DÙNG — tái dùng logic gộp, không viết lại |
| `plugin_tiers.py` (ghi `enabledPlugins` an toàn) | script repo | DÙNG — nếu chọn tự bật plugin |
| `update-config` | built-in | KHÔNG — sửa settings qua script setup, không qua harness |
| skill `plugin:tdq-workflow` | plugin | không có trong phiên này (chính là lỗi đang điều tra) |

### Nguyên nhân gốc (đã chốt bằng chứng)

1. **Plugin chỉ được bật theo project, không bật ở scope user.**
   - `WhisperLiveKit/.claude/settings.json` và `claudecodeui/.claude/settings.json` có `enabledPlugins: {"tdq-workflow@tdq-local": true}` (đi kèm bản cài scope project 0.58.0).
   - `~/.claude/settings.json` không có khóa này ở MỌI bản sao lưu (09/20, 10/07 ×2, 10/09 "Copy", hiện tại). Bản cài scope user 0.59.0 chỉ nằm trên đĩa và chưa bao giờ được bật. Người dùng xác nhận không hề tắt.
   - `9routerfork` không có thư mục `.claude/`, nên plugin không được bật ở tầng nào và harness không nạp skill lẫn hook.
2. **Bảng 12 phiên gần nhất khớp đúng quy luật:** phiên ở project có `enabledPlugins` (WhisperLiveKit, claudecodeui) → skill có trong listing và gọi được. Phiên ở project không có (9routerfork `sdk-ts` ×3 lỗi, LLMSpeechToText ×2, TestVideoEditLocal ×1) → `Unknown skill`, listing trống. Host (CLI hay `sdk-ts`/CloudCLI) không phải biến quyết định: WhisperLiveKit chạy `sdk-ts` vẫn tốt.
3. **Instruction toàn cục nhưng plugin cục bộ.** `tdq_setup.py` ghim `KHOI_HUONG_DAN` vào `~/.claude/CLAUDE.md` (áp mọi repo), ra lệnh "BẮT BUỘC mở bằng `tdq-workflow:tdq-intake`". Ở project chưa bật plugin, model làm đúng lệnh nhưng gặp skill không tồn tại. Hook `[TDQ:*]` cũng không chạy (hook là của plugin), nên `~/.claude/CLAUDE.md` là kênh DUY NHẤT tới được model ở đó.
4. **`tdq_setup.py` không kiểm plugin đã bật chưa.** Grep `enabledPlugins` trong `scripts/` chỉ thấy ở `skill_inventory.py` và `plugin_tiers.py`; setup không có bậc nào kiểm việc này. Setup báo "ĐẠT 7/8" trong khi skill không nạp được.
5. **Phụ:** bản cài scope user 0.59.0 và scope project 0.58.0 cũ hơn instruction 0.66.0 (do setup chạy từ repo dev). Đây không phải nguyên nhân của `Unknown skill` (0.58 vẫn có skill `tdq-intake`), nhưng là một kiểu lệch nữa mà setup không báo.

### Hướng sửa khả dĩ

- (i) Thêm bậc kiểm vào setup: gộp `enabledPlugins` 3 tầng (tái dùng `skill_inventory`). Nếu `tdq-workflow@*` chưa bật ở scope user → báo nợ / đề nghị bật.
- (ii) Thêm dòng dự phòng vào khối ghim: "`Unknown skill` → plugin chưa bật ở project này: đọc `{goc}/skills/tdq-intake/SKILL.md` trên đĩa và nhắc người dùng bật".
- (iii) Cảnh báo lệch phiên bản giữa instruction và bản plugin đã cài.
- Khắc phục ngay cho máy này (không cần code): thêm `"tdq-workflow@tdq-local": true` vào `~/.claude/settings.json` và `/plugin update tdq-workflow@tdq-local`.

### Hướng đã chốt (vòng 2)

- Làm cả (i), (ii), (iii).
- Setup tự bật plugin ở scope user: ghi `enabledPlugins["tdq-workflow@<mk>"] = true` vào `~/.claude/settings.json`, sao lưu `.bak` trước, dùng lại các hàm ghi của `plugin_tiers.py` (`_write_settings`, `_key_for` hiện còn private và bị chặn theo tier) qua một hàm public mới.
- Lệch phiên bản giữa bản cài scope user và `plugin.json` của gốc đang chạy setup → cảnh báo không chặn, kèm lệnh `/plugin update`.
- Chưa có bản cài scope user → không tự cài được (cần lệnh harness) → ghi nợ kèm lệnh `/plugin install tdq-workflow@tdq-local`.
- Đã loại: viết sang `.claude/settings.json` của từng project. Lý do: instruction nằm ở cấp user, nên sửa đúng tầng user một lần là phủ được mọi repo.
- Đã loại: dùng hook để cảnh báo. Lý do: hook là của plugin, nên plugin chưa bật thì hook cũng không chạy.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | việc nội bộ; ngữ nghĩa `enabledPlugins` đã đo thực nghiệm trên 12 phiên của máy này |
| Interview | CÓ | đã xong 2 vòng |
| spec → plan | CÓ | khung bất biến |
| QC độc lập (agent) | BỎ | mức QC full, không phải ultra |

Mức QC: **full** (4a).

Vòng phạm vi: bỏ qua, vì request chỉ chạm một vùng (setup + khối ghim) và đã đo đủ bối cảnh bằng số ở trên.

## Hỏi đáp

- Ảnh chụp từ đâu? → project `9routerfork` (transcript cho thấy `entrypoint: sdk-ts`).
- Plugin có bị tắt chủ động không? → Không hề tắt.
- Pipeline → deep (1a), loại bugfix.
- Sửa phần nào? → 1a: cả bậc kiểm trong setup lẫn dòng dự phòng trong khối ghim.
- Plugin chưa bật → 2a: setup tự ghi `enabledPlugins` cấp user, có `.bak`.
- Lệch phiên bản → 3a: cảnh báo không chặn.
- Mức QC → 4a: full.
