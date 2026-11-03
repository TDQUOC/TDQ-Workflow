# SPEC — Setup tự phát hiện và bật plugin tdq-workflow chưa bật ở scope user

Ngày: 2026-10-11 · Bản: 1.0 · Brief: ../brief/2026-10-11-1724-unknown-skill-plugin-chua-nap.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐÃ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi
- Mục tiêu: Ở mọi project trên máy, model không còn kẹt ở `Unknown skill: tdq-workflow:tdq-intake`.
  - `tdq_setup.py` phát hiện plugin chưa bật ở scope user và tự bật.
  - Setup báo lệch phiên bản giữa bản cài và instruction.
  - Khối ghim trong `~/.claude/CLAUDE.md` có đường dự phòng khi skill vẫn không nạp được.
- Trong phạm vi:
  1. Hàm public mới trong `scripts/plugin_tiers.py`: bật một khóa `enabledPlugins` bất kỳ trong một file settings cho trước, ghi nguyên tử + `.bak`. Lệnh `cmd_enable` (chặn theo tier) giữ nguyên hành vi.
  2. Bậc kiểm mới trong `scripts/tdq_setup.py`:
     - đọc `~/.claude/plugins/installed_plugins.json` tìm bản cài `tdq-workflow@*` scope `user`;
     - đọc `enabledPlugins` của `~/.claude/settings.json`;
     - có bản cài mà chưa bật → tự bật qua hàm ở (1), in `đã cài · bật plugin ...`;
     - không có bản cài scope user → ghi nợ kèm lệnh `/plugin install tdq-workflow@tdq-local`;
     - phiên bản bản cài ≠ `plugin.json` của gốc đang chạy setup → in `cảnh báo · ...` kèm lệnh `/plugin update tdq-workflow@<mk>`, không chặn.
  3. Thêm vào `KHOI_HUONG_DAN` một dòng dự phòng: gọi skill báo `Unknown skill` → đọc `{goc}/skills/tdq-intake/SKILL.md` trên đĩa, thay `${CLAUDE_PLUGIN_ROOT}` bằng `{goc}`, làm theo, và nhắc người dùng chạy `python3 {goc}/scripts/tdq_setup.py` để bật plugin. Đồng bộ nguyên văn sang `docs/claude-md-mau.md`.
  4. Ghi vào `docs/notes/user-level-install.md` rằng plugin phải bật ở scope user, kèm triệu chứng `Unknown skill`.
  5. Chạy setup thật trên máy này để bật plugin và cập nhật `~/.claude/CLAUDE.md` (theo 2a).
- NGOÀI phạm vi:
  - Tự chạy `/plugin install` hoặc `/plugin update`: đây là lệnh của harness, script không gọi thay được. Setup chỉ in lệnh.
  - Sửa `.claude/settings.json` của từng project.
  - Mã nguồn CloudCLI.
  - Bump phiên bản (để bước release sau, khi người dùng yêu cầu).

## 1b. Lộ trình
Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | việc nội bộ; ngữ nghĩa `enabledPlugins` đã đo thực nghiệm trên 12 phiên của máy này |
| Interview | CÓ | đã xong 2 vòng |
| QC độc lập (agent) | BỎ | mức QC full, không phải ultra |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Hàm bật khóa `enabledPlugins` dùng chung | `scripts/plugin_tiers.py` | unit test: bật khóa mới, khóa đã bật thì không ghi, có `.bak`, giữ nguyên khóa khác |
| 2 | Bậc kiểm plugin scope user trong setup | `scripts/tdq_setup.py` | unit test với HOME tạm cho 4 ca: chưa bật → bật; đã bật → không đổi; không có bản cài → nợ; lệch phiên bản → cảnh báo |
| 3 | Dòng dự phòng `Unknown skill` trong khối ghim | `scripts/tdq_setup.py`, `docs/claude-md-mau.md` | `test_claude_md_core` xanh (bản mẫu khớp nguyên văn hằng số) |
| 4 | Tài liệu cài đặt | `docs/notes/user-level-install.md` | có mục scope user + triệu chứng |
| 5 | Máy này được sửa | `~/.claude/settings.json`, `~/.claude/CLAUDE.md` | `enabledPlugins["tdq-workflow@tdq-local"] == true`; khối ghim có dòng dự phòng; setup in cảnh báo lệch 0.59.0 ≠ 0.66.0 |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| Ghi settings | `scripts/plugin_tiers.py` (kèm test riêng) | không | 1 |
| Setup | `scripts/tdq_setup.py`, `docs/claude-md-mau.md` (kèm test riêng và các test đang mock `main()`) | Ghi settings | 2, 3 |
| Tài liệu | `docs/notes/user-level-install.md` | Setup | 4 |
| Áp lên máy | `~/.claude/settings.json`, `~/.claude/CLAUDE.md` (sinh ra bởi lệnh setup, không sửa tay) | Setup | 5 |

Ranh giới lấy từ import thật: `tdq_setup.py` hiện chưa import `plugin_tiers`; sau khi sửa, `tdq_setup → plugin_tiers` là cạnh mới duy nhất. Các test hiện có của `main()` đều đang mock các bước của `main()` (`ghim_huong_dan_tool`, `va_hook_xung_dot`...), nên phải mock thêm bậc mới để test không ghi vào HOME thật.

## 3. Cách tiếp cận & lý do
- Chọn: bật ở tầng **user** (`~/.claude/settings.json`), và chỉ xét bản cài scope `user`.
  - Vì: instruction được ghim ở cấp user nên áp cho mọi repo; tầng bật plugin phải khớp tầng của instruction. Bằng chứng: 12 phiên, project có `enabledPlugins` thì nạp được skill, project không có thì `Unknown skill`.
- Chọn: tái dùng `_write_settings` của `plugin_tiers.py` qua một hàm public mới.
  - Vì: đã có ghi nguyên tử + `.bak` và đã có test; viết lại lần hai sẽ có hai bản lệch nhau.
- Chọn: dòng dự phòng trong `CLAUDE.md`.
  - Vì: ở project chưa bật plugin thì hook không chạy, và `~/.claude/CLAUDE.md` là kênh duy nhất tới được model. Không có dòng này, model tự bịa cách làm (đúng như ảnh chụp).
- Chọn: tôn trọng `TDQ_KHONG_CHAM_MAY=1` (đã có `_khong_cham_may()`): khi bật thì bậc mới chỉ báo, không ghi.
- Đã loại: ghi `enabledPlugins` vào settings của từng project — phải lặp ở mọi repo, sót một repo là lỗi quay lại.
- Đã loại: cảnh báo bằng hook — hook thuộc plugin, plugin chưa bật thì hook không chạy.
- Đã loại: tự gọi `claude plugin install/update` từ script — đây là thao tác harness có tương tác, chạy ngầm từ setup dễ treo và vượt quyền người dùng.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-setup` | project | DÙNG | khung bậc kiểm + ghim instruction mà request này mở rộng |
| `tdq-conventions` | project | NỀN | quy ước pipeline, clean code |
| Đã xét 15 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service: bậc mới ghi log qua `_log()` sẵn có của `tdq_setup.py` (có timestamp, tắt bằng `TDQ_LOG=0` / `--khong-log`). Mỗi lần ghi settings log khóa, giá trị cũ → mới, đường dẫn file.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh (lệnh cụ thể ghi ở plan).
- Code viết ra bám 5 nguyên tắc SOLID theo
  `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong
  `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ những dòng việc này chạm tới):
- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — không tạo file code mới; chỉ sửa `scripts/plugin_tiers.py`, `scripts/tdq_setup.py`.
- "`scripts/` không được import `hooks/`" — cạnh mới là `scripts → scripts`, giữ đúng.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Test của `main()` ghi vào `~/.claude/settings.json` thật | hỏng settings người dùng | bậc mới nhận `home` làm tham số; mock trong cả 3 file test của `main()`; ca test dùng thư mục tạm |
| `settings.json` không đọc được / `enabledPlugins` không phải object | ghi đè mất cấu hình | không ghi, chỉ ghi nợ (giống `cmd_enable`) |
| Có nhiều marketplace (`tdq-workflow@tdq-local`, `@inline`) | bật nhầm khóa | lấy đúng khóa của bản cài scope `user` trong `installed_plugins.json`; bỏ qua `@inline` (cài qua `--plugin-dir`, không có trong file này) |
| Khối ghim dài thêm 1 dòng | tốn context mọi phiên | 1 dòng duy nhất, ≤ 300 ký tự |
| Bật plugin xong nhưng phiên đang mở chưa nạp | người dùng tưởng chưa sửa | setup in nhắc "mở phiên mới để nạp plugin" |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Điều kiện PASS | Đo trước | Dự phòng nếu trượt |
|---|---|---|---|---|
| Q1 | Hàm bật khóa | test bật mới / đã bật / file hỏng đều xanh; `.bak` có nội dung cũ | — | — |
| Q2 | Bậc kiểm plugin | 4 ca ở §2 #2 xanh, không ca nào chạm HOME thật | — | — |
| Q3 | Khối ghim | `test_claude_md_core` xanh; dòng dự phòng ≤ 300 ký tự | ước 220 ký tự (đếm bản nháp câu ở §1 (3)), biên ±40 | rút gọn câu, bỏ mệnh đề nhắc chạy setup |
| Q4 | Hồi quy vùng chạm | mọi test của setup, ghi settings, khối ghim, tự khởi tạo, tự cập nhật và nhất quán tài liệu xanh | — | — |
| Q5 | Áp lên máy | sau `python3 scripts/tdq_setup.py`: `enabledPlugins` có `tdq-workflow@tdq-local: true`, có `settings.json.bak`, in cảnh báo lệch phiên bản | — | — |

DoD:
- Q1–Q5 đạt.
- `doc_lint` của spec/plan xanh; drift mốc luật không tăng.
- Báo cáo nêu rõ việc người dùng còn phải tự làm: `/plugin update tdq-workflow@tdq-local` và mở phiên mới.

## 7. Câu hỏi còn mở
(Trống)
