# SPEC — Ưu tiên tra ui-ux-pro-max cho các case UI/UX
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Brief: ../brief/2026-09-03-1949-uiux-pro-max-routing.md

## 1. Mục tiêu & phạm vi

**Mục tiêu.** Khi công việc chạm tới quyết định thiết kế giao diện, Claude phải biết rằng có
sẵn `ui-ux-pro-max` như một **bộ đề xuất để TRA CỨU**, và mặc định tra nó thay vì tự chế theo
trực giác. Đích đến là đầu ra giao diện chỉn chu và nhất quán hơn giữa các phiên làm việc.

**Trong phạm vi**

- Thêm dòng UI/UX vào bảng routing của `plugin-routing.md`.
- Viết một khối luật riêng nêu ba tầng công việc UI/UX và ui-ux-pro-max nằm ở tầng nào.
- Vá `scripts/skill_inventory.py` để bước B0 nhìn thấy plugin để skill ở `.claude/skills/`.
- Dựng lại ba bundle portable để luật mới đi theo.
- Test giữ cả hai thứ trên khỏi tái phát.

**Ngoài phạm vi**

- Không sửa bất kỳ file nào BÊN TRONG plugin ui-ux-pro-max (nó là mã của bên thứ ba).
- Không thêm dữ liệu UI/UX của riêng TDQ (bảng màu, style…) — đã có sẵn ở plugin.
- Không đụng 31 skill `unity-*`: ui-ux-pro-max không có dữ liệu game, hai bên không giao nhau.
- Không dựng tầng kiểm chứng tự động (a11y/lighthouse) trong request này; chỉ TRỎ sang
  `chrome-devtools-mcp` bằng chữ.
- Không dọn văn bản pha `diagram` còn sót trong `tdq-spec`/`tdq-intake` — việc khác.

## Lộ trình

`analyze` (xong) → `spec` (đang) → `plan` → `implement` → `qc` → `report`.
**Không có pha `diagram`**: đã gỡ khỏi workflow ngày 2026-09-01, thấy ở
`scripts/tdq_state.py:73-82` (`PHASE_DA_GO = {"diagram": "spec"}`). Văn bản của `tdq-spec` và
`tdq-intake` còn nhắc pha này là luật chưa dọn theo mã, không phải bước bị bỏ ở đây.
Duyệt spec này là duyệt luôn lộ trình đó.

## 2. Đầu ra cụ thể

| # | Đầu ra | Đo bằng |
|---|---|---|
| Đ1 | Một dòng UI/UX trong bảng routing của `plugin-routing.md` | grep thấy `ui-ux-pro-max` trong bảng |
| Đ2 | Khối luật `## UI/UX — ba tầng` trong cùng file, nêu rõ tầng nào dùng, tầng nào không | test đọc file, khẳng định có đủ ba tầng và có tên `chrome-devtools-mcp` |
| Đ3 | Câu chữ mang nghĩa TRA CỨU, không mang nghĩa bắt buộc thực thi | test cấm các từ ra lệnh tuyệt đối trong khối đó |
| Đ4 | Luật ghép skill: cho phép dùng chung với `frontend-design`/`figma`/`chrome-devtools-mcp` | test thấy đủ ba tên trong khối luật |
| Đ5 | Ranh giới loại trừ: nêu rõ không áp cho Unity/game | test thấy câu loại trừ |
| Đ6 | `skill_inventory.py` nhìn thấy plugin để skill ở `.claude/skills/` | `skill_inventory.py --tat-ca` in ≥1 dòng `plugin:ui-ux-pro-max` |
| Đ7 | Ba bundle portable mang luật mới | `tdq_checkportable.py check --root <mỗi bundle>` in CLEAN |
| Đ8 | Bộ test riêng giữ Đ1–Đ6 khỏi tái phát | bộ test của request chạy xanh toàn bộ |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc |
|---|---|---|
| Luật routing | `skills/tdq-conventions/references/plugin-routing.md` | không phụ thuộc mã; là văn bản mọi phase đọc |
| Kiểm kê năng lực | `scripts/skill_inventory.py` (hàm quét thư mục skill của plugin) | đọc `~/.claude/plugins/installed_plugins.json` và các lớp settings |
| Bundle | `portable_claude/`, `portable_codex/`, `antigravity_portable/` | **sinh ra** từ `scripts/build_portable.py`; cấm sửa tay |
| Test | vùng `tests/` của repo | import `skill_inventory` từ `scripts/` |

**Cấm chạm:** mọi file trong `~/.claude/plugins/` và
`~/Documents/Add_on_for_claude/ui-ux-pro-max-skill/` — mã của bên thứ ba, chỉ đọc.

## 3. Cách tiếp cận & lý do

**C1 — Luật viết theo hình L2: một dòng bảng + một khối luật riêng.**
Bảng routing chỉ diễn đạt được "việc này → plugin kia". Nó không nói được điều quan trọng
nhất đã đo ở pha analyze: plugin này mạnh ở tầng quyết định thiết kế, **không** có tầng kiểm
chứng trên máy thật. Nhét cả sắc thái đó vào một ô bảng thì hoặc ô phình ra, hoặc mất nghĩa.
Nên: dòng bảng để định tuyến, khối luật để nói ranh giới.

**C2 — Ngôn từ là "bộ đề xuất để tra", không phải "bước phải chạy".**
Theo bổ sung của user ở câu 1. Lý do kỹ thuật: dữ liệu của plugin là catalog quy ước đã kiểm
chứng, giá trị nằm ở chỗ ĐỐI CHIẾU trước khi quyết định. Viết thành mệnh lệnh sẽ đẻ ra thói
quen nạp cho đủ thủ tục rồi bỏ đó — vừa tốn context vừa không cải thiện đầu ra.

**C3 — Mức ràng buộc: gợi ý mạnh, bỏ qua được nhưng phải nêu lý do một dòng.**
Giống bậc của luật LSP+lumen nhưng nhẹ hơn một nấc: luật kia là lỗi QC nếu vi phạm, luật này
chỉ đòi một câu giải trình. Lý do: thiết kế có chỗ cho ý đồ riêng, còn tìm ký hiệu code thì
không.

**C4 — Cho phép ghép, cấm viết theo lối loại trừ.**
Theo bổ sung của user ở câu 3. Ba cặp ghép có thật, đã xác định ở pha analyze:
`figma` khi có file thiết kế sẵn (design-to-code), `frontend-design` khi cần hướng thị giác
có chủ đích, `chrome-devtools-mcp` cho tầng kiểm chứng (`a11y-debugging`, lighthouse) mà
ui-ux-pro-max không có. Luật phải nói "ghép được với", không nói "thay cho".

**C5 — Vá `skill_inventory.py` bằng cách thêm ĐƯỜNG DẪN DỰ PHÒNG, không đổi cấu trúc.**
Chỗ hỏng đã xác định: hàm quét ghép `<installPath>/skills`; plugin này để ở
`<installPath>/.claude/skills/`. Cách vá: thử `skills/` trước, không có thì thử
`.claude/skills/`. Không đổi chữ ký hàm, không đổi định dạng bảng in ra, nên mọi chỗ gọi cũ
không bị ảnh hưởng. Đã quét toàn bộ plugin đang bật: chỉ một plugin dùng bố cục này, nên bản
vá không làm bảng phình thêm ngoài 7 skill của nó.

**C6 — Test đọc VĂN BẢN LUẬT, không chỉ test mã.**
Đ1–Đ5 đều là câu chữ. Nếu không có test đọc file, một lần sửa tài liệu sau này sẽ lặng lẽ xoá
mất luật mà không gì báo. Test khẳng định sự có mặt của: tên plugin, ba tầng, ba tên plugin
ghép được, câu loại trừ Unity.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | plugin:tdq-workflow | NỀN | chứa file luật được sửa |
| tdq-intake / spec / plan / build | plugin:tdq-workflow | NỀN | pipeline đang chạy |
| ui-ux-pro-max (7 skill) | plugin:ui-ux-pro-max | DÙNG | đối tượng của luật; đọc mô tả 7 skill để viết đúng tên và đúng phạm vi |
| frontend-design | plugin:frontend-design | DÙNG | nêu tên trong luật ghép (Đ4) |
| figma | plugin:figma | DÙNG | nêu tên trong luật ghép (Đ4); đã có dòng routing riêng, phải không mâu thuẫn |
| chrome-devtools-mcp | plugin:chrome-devtools-mcp | DÙNG | nêu tên trong luật ghép (Đ4) làm tầng kiểm chứng |
| các skill `unity-*`, `ui-ugui/uitk/imgui` | user | KHÔNG | khác lĩnh vực |
| Đã xét 205 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu thường trực

- Dịch vụ log BẬT: mỗi lượt đổi repo đều đóng sổ bằng `tdq_finish.py`.
- Không placeholder: thiếu thông tin thì hỏi, không viết tạm.
- Mỗi phần có test riêng (Đ8).
- Luật viết bằng tiếng Anh theo tầng "Rules" của `tdq-conventions §0`; tài liệu và đối thoại
  bằng `doc_lang`.

## 5. Ràng buộc & rủi ro

**R1** — Cấm sửa file bên trong plugin ui-ux-pro-max và cấm sửa tay file trong ba bundle.
**R2** — Luật mới không được mâu thuẫn dòng `figma` đã có trong bảng routing.
**R3** — Không làm nặng context: khối luật đủ ngắn để đọc trong một hơi, không chép lại
catalog của plugin vào repo.
**R4** — Bản vá `skill_inventory.py` không đổi chữ ký hàm và không đổi định dạng đầu ra.

**Ru1** — *Luật bị viết thành mệnh lệnh.* Hậu quả: nạp cho đủ thủ tục, tốn context, đầu ra
không khá hơn. Chặn bằng Đ3 — test cấm từ ra lệnh tuyệt đối trong khối luật.
**Ru2** — *Bản vá kéo theo hàng trăm skill rác từ cache.* Đã đo: chỉ một plugin dùng bố cục
`.claude/skills/`, và hàm quét chỉ đi qua plugin ĐANG BẬT. Chặn bằng test đếm số dòng thêm.
**Ru3** — *Sửa README/luật trong bundle rồi bị build ghi đè.* Bẫy đã gặp ở request trước.
Chặn bằng R1 + Đ7: chỉ sửa nguồn rồi dựng lại.
**Ru4** — *Luật đúng nhưng không ai đọc tới.* `plugin-routing.md` được nạp qua
`tdq-conventions`, mà mọi skill `tdq-*` đều nạp file này — nên đường tới luật là có thật.

## 6. QC & Definition of Done

1. Bảng routing có dòng UI/UX nêu đúng tên `ui-ux-pro-max`.
2. Khối luật nêu đủ ba tầng: chiến lược sản phẩm / quyết định thiết kế / kiểm chứng.
3. Khối luật nói rõ ui-ux-pro-max chỉ phủ tầng giữa.
4. Khối luật dùng từ ngữ tra cứu, không có từ ra lệnh tuyệt đối.
5. Khối luật nêu mức ràng buộc: mặc định tra, bỏ qua được nếu nêu lý do một dòng.
6. Khối luật nêu đủ ba plugin ghép được: `frontend-design`, `figma`, `chrome-devtools-mcp`.
7. Khối luật nêu câu loại trừ Unity/game.
8. `skill_inventory.py --tat-ca` in ≥1 dòng nguồn `plugin:ui-ux-pro-max`.
9. Bản vá không đổi số dòng của các nguồn plugin khác (đo trước/sau).
10. Bộ test riêng của request chạy xanh toàn bộ.
11. `pytest -q` toàn repo không vượt mốc đỏ có sẵn.
12. Ba bundle dựng lại, `tdq_checkportable.py check` in CLEAN cho cả ba.
13. `doc_lint.py` exit 0 trên brief, spec, plan, QC.
14. `git status` không liệt kê file nào trong `~/.claude/plugins/` hay thư mục nguồn của
    plugin ui-ux-pro-max (kiểm bằng mắt: hai nơi đó nằm ngoài repo).

## 7. Câu hỏi còn treo

Không còn.
