# Quét lại instruction Claude Code — chuyển gì vào plugin, xoá bớt gì

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay bây giờ tôi muốn mở request để xử scan lại 1 vòng xem instruction của claude code, có gì
> có thể đưa vòa plugin và xóa bớt ở instruciton không?

Đọc lần đầu:
- **Mục tiêu**: giảm kích thước `~/.claude/CLAUDE.md` (57 dòng, nạp vào MỌI phiên, mọi project)
  bằng cách đẩy phần nào đẩy được xuống plugin `tdq-workflow` (skill nạp theo nhu cầu).
- **Phạm vi đoán**: `~/.claude/CLAUDE.md` (nguồn), `skills/tdq-*` + `hooks/` (đích).
- **Chỗ chưa rõ**:
  - Chỉ quét file CLAUDE.md global, hay cả settings/hook/permission của Claude Code?
  - Kết quả muốn là BÁO CÁO đề xuất, hay sửa luôn CLAUDE.md?
  - Sửa CLAUDE.md là sửa file NGOÀI repo — cần user xác nhận riêng.

## Hiểu & kiến thức

Chốt phạm vi (user: `1c 2a 3a`): quét `~/.claude/CLAUDE.md` + `~/.claude/settings.json`, đối
chiếu với 9 skill `tdq-*`; đầu ra là **báo cáo đề xuất**, KHÔNG sửa file; lane chuyên sâu.

### B0 — kiểm kê năng lực
Không report/audit cũ nào chạm `~/.claude/CLAUDE.md` (grep `docs/tdq/report`, `docs/tdq/audit`
chỉ thấy `skill-index.json`). Đây là đất chưa có tiền lệ → làm mới hoàn toàn. Thứ tái dùng
được: `skills/tdq-conventions/references/context-budget.md` (khung "chi phí bước vs chi phí
context") và `soul.md` (thứ tự ưu tiên chất lượng > runtime > context).

### B1 — đọc code, ba phát hiện quyết định
1. **Hook là lớp thi hành phổ quát, không phải skill.** `hooks/scripts/prompt_context.py:139`
   chạy ở MỌI `cwd`: `state = load(cwd)`, `state is None` → vẫn in `[TDQ:INTAKE]`. Nghĩa là
   luật "mọi prompt mới → tdq-intake" đã được hook nhắc mỗi lượt ở mọi project, không cần
   CLAUDE.md nhắc lại. `session_start.py:21` in luật `[TDQ:<CODE>]` + "state chỉ qua
   tdq_state.py" mỗi phiên. `bash_gate.py` chặn cứng commit chứa "generated with"/Co-Authored-By.
2. **`skills/tdq-conventions/SKILL.md` (164 dòng) đã chép gần trọn CLAUDE.md.** Đối chiếu:
   §7 Git ≡ CLAUDE.md mục 2; §8 Research ≡ mục 3 (cả câu cấm API key); §6 Working log ≡ mục 5;
   §9 Sub-agents ≡ mục 6 dòng cuối; §11 Quality ≡ mục 5 (log service) + luật tick `[x]`;
   §10 ≡ luật gộp batch. Trùng lặp là thật, không phải suy đoán.
3. **Chuỗi nạp**: hook → `tdq-intake` → dòng đầu SKILL.md "Load tdq-conventions first". Nên
   mọi luật nằm trong conventions đều tới nơi — MIỄN LÀ intake được gọi. Khoảng hở duy nhất:
   cửa sổ trước khi skill đầu tiên nạp (kể cả tầng `nhỏ` trả lời tại chỗ).

→ Tiêu chí phân loại rút ra: một dòng CLAUDE.md chỉ xoá được khi nó (a) đã có trong skill/hook
VÀ (b) không cần đúng ở cửa sổ trước khi skill nạp. Dòng nào là "mồi khởi động" thì phải ở lại
dù đã trùng.

### B2 — nghiên cứu ngoài
BỎ B2: không có ẩn số ngoài repo — toàn bộ đối tượng là file cục bộ đã đọc trực tiếp.

### Ghi nhận ngoài phạm vi (an ninh)
`~/.claude/settings.json` để **2 API key Tavily ở dạng chữ thường trong `env`**. Không in giá
trị ra đây theo luật cấm lộ key. Đây là quan sát, sẽ nêu trong báo cáo, không tự sửa.

### Phạm vi đã chốt
Vòng phạm vi chạy ở turn trước, user trả `1c 2a 3a` + bổ sung mục tiêu "lên phương án chuyển
qua plugin tdq-workflow để không quá lệ thuộc vào instruction". Chốt:
- Quét: `~/.claude/CLAUDE.md` + `~/.claude/settings.json` + đối chiếu 9 skill `tdq-*`.
- Mức mạnh tay: **thận trọng** — chỉ xoá dòng vừa trùng vừa được hook/gate chặn cứng; dòng chỉ
  trùng ở skill thì rút thành 1 dòng trỏ.
- Độ sâu: bảng **từng dòng** cho cả 57 dòng + bản CLAUDE.md đề xuất dán được.
- `settings.json`: một mục riêng (API key dạng chữ, `defaultMode: bypassPermissions`,
  `skipDangerousModePermissionPrompt`).
- Mặt bị LOẠI: không sửa `~/.claude/CLAUDE.md`, không sửa `settings.json`, không thêm/sửa skill
  hay hook trong request này — đầu ra chỉ là báo cáo (user chọn 2a).

### Năng lực dùng được

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | plugin:tdq-workflow | NỀN | khung luật đang chạy, đồng thời là ĐỐI TƯỢNG đối chiếu |
| tdq-intake | plugin:tdq-workflow | NỀN | skill mở request này |
| tdq-spec / tdq-plan / tdq-build | plugin:tdq-workflow | NỀN | các pha kế tiếp của lộ trình |
| tdq-lsp-setup | plugin:tdq-workflow | DÙNG | thứ tự tìm kiếm khi dò luật trùng giữa skill và hook |
| mem0-memory | user | DÙNG | quyết định kiến trúc "luật ở đâu" đáng ghi 1 fact sau khi chốt |
| Đã xét 279 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Lộ trình
`analyze` → `spec` → `plan` → `implement` (viết báo cáo) → `qc` → `report`. Duyệt spec là duyệt
luôn lộ trình này. Request chỉ đẻ ra 1 luồng: "rà soát và phân loại luật", không đụng code chạy.

## Hỏi đáp

(vòng phỏng vấn — chờ user trả lời)
