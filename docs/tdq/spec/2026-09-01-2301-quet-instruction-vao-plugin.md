# SPEC — Quét instruction Claude Code: chuyển gì vào plugin, xoá bớt gì

Ngày: 2026-09-01 · Bản: 1.0 · Brief: ../brief/2026-09-01-2301-quet-instruction-vao-plugin.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

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
- Mục tiêu: rà từng dòng của `~/.claude/CLAUDE.md` (57 dòng, nạp vào MỌI phiên của MỌI
  project) và `~/.claude/settings.json`, đối chiếu với 9 skill `tdq-*` + 5 hook, rồi ra
  **một báo cáo** phân loại từng dòng thành GIỮ / CHUYỂN / XOÁ, kèm phương án đưa phần
  chuyển được vào plugin `tdq-workflow` để instruction thôi phải gánh luật.
- Đo được: 57/57 dòng có phán quyết + lý do; mỗi dòng CHUYỂN chỉ đúng một đích
  (skill nào, hoặc hook nào); báo cáo kèm bản CLAUDE.md đề xuất dán được nguyên khối.
- Trong phạm vi: đọc và phân loại; đề xuất đích đến trong plugin; nêu rủi ro của từng
  dòng bị xoá; mục riêng cho `settings.json`.
- NGOÀI phạm vi (chép từ brief `### Phạm vi đã chốt`):
  - Không sửa `~/.claude/CLAUDE.md` — user chọn 2a, chỉ ra báo cáo.
  - Không sửa `~/.claude/settings.json`, kể cả chuyện API key — chỉ nêu.
  - Không thêm/sửa skill hay hook trong request này; việc đó là request sau, dựa trên
    phương án được duyệt ở báo cáo này.
  - Không đụng `CLAUDE.md` cấp project của các repo khác.

## 1b. Lộ trình
Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.
`analyze` → `spec` → `plan` → `implement` → `qc` → `report`. Một luồng duy nhất:
"rà soát và phân loại luật", không đụng code chạy được.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| B0 kiểm kê năng lực | CÓ | đất chưa có tiền lệ, không report cũ nào chạm CLAUDE.md |
| B1 đọc code | CÓ | phải biết hook/skill thật sự phát biểu luật nào mới dám nói "trùng" |
| B2 research web | BỎ | không có ẩn số ngoài repo, toàn file cục bộ |
| Interview | CÓ (xong) | đã chạy 2 vòng, user chốt `1c 2a 3a` + mục tiêu giảm lệ thuộc |
| Vòng phạm vi | CÓ (xong) | 3 mặt đã chốt, các mặt loại chép ở §1 |
| QC độc lập (agent) | BỎ | đầu ra là văn bản, QC bằng lệnh đếm + đọc lại; agent không thêm gì |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Bảng phán quyết từng dòng | báo cáo, mục "Bảng 57 dòng" | đủ 57 dòng, mỗi dòng có cột phán quyết + lý do, không dòng nào bỏ trống |
| 2 | Phương án chuyển vào plugin | báo cáo, mục "Chuyển đi đâu" | mỗi dòng CHUYỂN trỏ đúng 1 đích có thật (file skill hoặc hook đang tồn tại, hoặc đích mới có nêu lý do cần tạo) |
| 3 | Bản CLAUDE.md đề xuất | báo cáo, khối mã dán được | số dòng bản mới < 57, và mọi luật bị bỏ đều có mặt ở cột CHUYỂN của bảng §2 đầu ra 1 |
| 4 | Mục `settings.json` | báo cáo, mục riêng | nêu đủ 3 điểm: API key dạng chữ, `defaultMode`, `skipDangerousModePermissionPrompt`; KHÔNG in giá trị key |
| 5 | Mục rủi ro "cửa sổ trước khi skill nạp" | báo cáo | liệt kê được các dòng phải GIỮ vì lý do mồi khởi động |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| Nguồn-instruction | `~/.claude/CLAUDE.md`, `~/.claude/settings.json` | không | 1, 4 |
| Đích-plugin | `skills/`, `hooks/` | Nguồn-instruction | 2 |
| Báo cáo | `docs/tdq/report/2026-09-01-2301-quet-instruction-vao-plugin.md` | cả hai module trên | 1, 2, 3, 4, 5 |

Chỉ module "Báo cáo" có quyền GHI. Hai module còn lại là vùng CHỈ ĐỌC trong request này.

## 3. Cách tiếp cận & lý do
- Chọn: phân loại theo **hai câu hỏi nối tiếp** cho từng dòng —
  (a) luật này đã có ở skill/hook nào chưa?
  (b) nó có cần đúng ở cửa sổ TRƯỚC khi skill đầu tiên nạp không?
  Trùng + không cần mồi → XOÁ. Trùng + cần mồi → GIỮ (rút gọn). Chưa trùng → CHUYỂN, kèm đích.
- Vì: `hooks/scripts/prompt_context.py:139` chạy ở mọi `cwd` (`state is None` vẫn in
  `[TDQ:INTAKE]`), nên hook là lớp thi hành phổ quát duy nhất không phụ thuộc việc skill có
  được gọi hay không. Còn `skills/tdq-conventions/SKILL.md` đã chép gần trọn CLAUDE.md
  (§7≡mục 2, §8≡mục 3, §6≡mục 5, §9≡mục 6, §11≡mục 5). Hai sự thật này quyết định toàn bộ
  cách phân loại.
- Đã loại: phân loại theo chủ đề (git/log/research…) — vì chủ đề không nói được dòng nào
  xoá được; thứ quyết định là "đã có ở đâu" và "có cần mồi không".
- Đã loại: đề xuất xoá mạnh tay theo niềm tin vào chuỗi hook → intake → conventions — user
  chốt mức thận trọng (1a).

## 3b. Năng lực & công cụ
Chép từ brief mục `### Năng lực dùng được`.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | plugin:tdq-workflow | NỀN | khung luật đang chạy, đồng thời là ĐỐI TƯỢNG đối chiếu |
| tdq-intake | plugin:tdq-workflow | NỀN | skill mở request này |
| tdq-spec | plugin:tdq-workflow | NỀN | pha đang chạy |
| tdq-plan | plugin:tdq-workflow | NỀN | pha kế tiếp |
| tdq-build | plugin:tdq-workflow | NỀN | pha viết báo cáo |
| tdq-lsp-setup | plugin:tdq-workflow | DÙNG | thứ tự tìm kiếm khi dò luật trùng giữa skill và hook |
| mem0-memory | user | DÙNG | chốt xong ghi 1 fact "luật ở đâu" |
| Đã xét 279 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — request này không đẻ ra runtime nào, đầu ra duy nhất là một file báo cáo.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật. Mọi dòng
  "đã có ở skill X" phải kèm được đường dẫn có thật, không nói chung chung.
- Mỗi thành phần có cách kiểm riêng chạy bằng một lệnh (xem §6).
- Không in giá trị API key ra bất kỳ đâu: báo cáo, log, lệnh shell, prompt gửi model.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`, chỉ dòng việc này chạm):
- `docs/kien-truc.md:12` "Luật | `skills/` | văn bản chỉ dẫn model; không chạy được, không có
  trạng thái" — việc này chạm ở phần đề xuất đích đến: luật chuyển đi phải rơi vào `skills/`,
  không được nhét thành logic trong `scripts/`.
- `docs/kien-truc.md:15` "Hook | `hooks/scripts/` | 5 hook cắm vào Claude Code, nhắc mã
  `[TDQ:*]` và chặn khi thiếu bằng chứng" — chạm ở phần đề xuất dùng hook làm lớp mồi.
- `docs/kien-truc.md:23` "`skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội
  dung script vào skill" — chạm ở khuôn các dòng đề xuất viết vào skill.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Kết luận "đã trùng" sai → đề xuất xoá một luật thật sự chưa có ở đâu | mất luật ở mọi project | mỗi dòng XOÁ phải kèm đường dẫn + số dòng nơi luật còn sống; QC dò lại bằng grep |
| Bỏ sót cửa sổ trước khi skill nạp | luật đúng trên giấy nhưng không tới nơi ở tầng `nhỏ` | mục riêng ở đầu ra 5, và mức thận trọng 1a giữ lại dòng mồi |
| Báo cáo đề xuất đích chưa tồn tại (skill/hook chưa có) | request sau không thi hành được | mỗi đích phải là file có thật, hoặc ghi rõ "đích MỚI" + lý do |
| Nêu `settings.json` kèm giá trị key | lộ credential | luật §4 cấm tuyệt đối; QC grep chuỗi `tvly-` trong báo cáo phải ra 0 |
| Việc trôi thành "sửa luôn CLAUDE.md" | vượt phạm vi user chốt 2a | §1 NGOÀI phạm vi ghi rõ; DoD kiểm `git status` không có file ngoài repo |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Bảng phán quyết đủ dòng | bảng có đúng 57 dòng dữ liệu, không dòng nào thiếu phán quyết hoặc thiếu lý do |
| Q2 | Mỗi dòng XOÁ có bằng chứng còn sống | mọi dòng XOÁ đều dẫn được `<file>:<dòng>` trong `skills/` hoặc `hooks/`, và dẫn đó kiểm lại bằng grep thì thấy thật |
| Q3 | Mỗi dòng CHUYỂN có đích tồn tại | đích là file có thật, hoặc được đánh dấu "đích MỚI" kèm lý do |
| Q4 | Không lộ credential | báo cáo không chứa chuỗi giá trị key nào |
| Q5 | Bản CLAUDE.md đề xuất nhất quán | số dòng < 57, và mọi luật bị bỏ đều xuất hiện ở cột CHUYỂN/XOÁ của bảng |
| Q6 | Không vượt phạm vi | không file nào ngoài repo bị sửa; trong repo chỉ có file của request này |
| Q7 | Lint tài liệu | `doc_lint` trên các file của request thoát 0 |

DoD:
- Báo cáo tồn tại, có đủ 5 đầu ra ở §2.
- Q1–Q7 đều PASS, bằng chứng ghi vào mục QC của plan.
- `~/.claude/CLAUDE.md` và `~/.claude/settings.json` giữ nguyên, không bị sửa.
- Working log của ngày có mục cho request này.

## 7. Câu hỏi còn mở
(Rỗng.)
