# BÁO CÁO — Ưu tiên tra ui-ux-pro-max cho các case UI/UX
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Spec: ../spec/2026-09-03-1949-uiux-pro-max-routing.md · Plan: ../plan/2026-09-03-1949-uiux-pro-max-routing.md · QC: ../qc/2026-09-03-1949-uiux-pro-max-routing.md

Xong 7/7 task, 18/18 hạng mục QC PASS ngay vòng 1. Trước lần này bảng routing **không có dòng
nào cho UI/UX**, mà dòng chốt bảng lại nói "việc không khớp dòng nào thì làm bằng tool sẵn có,
đừng kéo plugin vào cho tốn context" — nghĩa là luật cũ đang *cản* ui-ux-pro-max chứ không
trung lập. Đó là cái đã sửa.

## Luật mới: một dòng bảng + khối `## UI/UX — three layers`

Khối luật chia việc giao diện làm ba tầng và nói rõ ba tầng KHÔNG tra cùng một chỗ: chiến lược
sản phẩm (chưa plugin nào phủ — hỏi user, viết vào spec), quyết định thiết kế (style, bảng màu,
cặp font, token, component — tầng DUY NHẤT ui-ux-pro-max phủ), kiểm chứng trên máy thật (a11y,
lighthouse — thuộc `chrome-devtools-mcp`).

Đúng yêu cầu của bạn, chữ dùng là **"CATALOGUE TO CONSULT, not a step to execute"**: cuốn sổ
đối chiếu Claude Code mở ra khi cần một phương án có căn cứ, rồi tự quyết. Mức ràng buộc ghi
thẳng: mặc định tra khi việc rơi vào tầng 2, **bỏ qua được, chỉ cần một dòng lý do** — nhẹ hơn
đúng một nấc so với luật LSP+lumen. Khối luật có một ca test riêng cấm các từ ra lệnh tuyệt đối
(`MUST`, `mandatory`, `always load`, `never skip`), nên lần sau ai viết nặng tay là test đỏ.

Phần ghép: viết là "Combines with, never exclusive" — `frontend-design` dựng code sau khi
ui-ux-pro-max chọn màu/font/token; `figma` là nguồn sự thật khi đã có file thiết kế, plugin chỉ
lấp chỗ trống; `chrome-devtools-mcp` đo lại ở tầng 3. Loại trừ Unity/game vì bộ dữ liệu không có
dòng nào cho Unity/Unreal.

## Defect B3: kiểm kê năng lực bị mù đúng cái plugin này

`skill_inventory.py` ghép đường dẫn `<installPath>/skills`, còn ui-ux-pro-max để skill ở
`<installPath>/.claude/skills/` — nên bước B0 của MỌI request về sau sẽ không bao giờ liệt kê
nó, và luật mới sẽ vô dụng vì bảng năng lực §3b luôn khuyết. Đã vá bằng fallback: thử `skills/`
trước, không có thì thử `.claude/skills`, plugin không có thư mục nào thì không sinh dòng.

Đo thật: 0 dòng → **7 dòng** `plugin:ui-ux-pro-max`. Và bảng đếm theo từng nguồn plugin khác
cho md5 trùng khít trước/sau bản vá, nên bản vá không kéo theo skill rác — đúng rủi ro Ru2 mà
spec đã lường.

## Kiểm chứng

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | 0s | 1 |
| analyze | 18 min | 2 min | 1 |
| spec | 6 min | 2 min | 1 |
| plan | 3h 06min | 5 min | 1 |
| implement | 5 min | 5 min | 1 |
| qc | 1 min | 1 min | 1 |
| report | 3s | 2s | 1 |
| **Total** | **3h 37min** | **20 min** | |

- Bộ test riêng `tests/test_uiux_routing.py`: 11 ca xanh (7 ca văn bản luật, 3 ca hàm quét,
  1 ca canh luật đã xuống bundle — quên dựng lại là test đỏ).
- `pytest -q` toàn repo: 100 đỏ, đúng mốc đỏ có sẵn, không tăng; xanh 1531 → 1559.
  Đã đối chứng riêng `test_skill_router.py` (97 đỏ) giống hệt trước và sau bản vá.
- Ba bundle dựng lại, `tdq_checkportable.py check` in CLEAN cho cả ba (93 / 143 / 86 file).
- `doc_lint.py` exit 0 trên brief, spec, plan, QC và file luật.
- Không đụng file nào ngoài repo; plugin chỉ được ĐỌC để lấy tên 7 skill.

## Một chỗ tự quyết giữa chừng

Plan viết test theo tiếng Việt, nhưng `plugin-routing.md` là file luật viết bằng tiếng Anh. Tôi
viết khối luật bằng tiếng Anh cho khớp file và sửa các chuỗi test theo, thay vì chèn một khối
tiếng Việt lạc lõng vào giữa. Nội dung không đổi.

Plan cũng ghi T1.1 "đỏ đúng 5 ca"; tôi viết 7 ca để phủ trọn DoD 1–7 (thêm `tang_giua` và
`muc_rang_buoc`). Nhiều hơn plan, không ít hơn.

## Vẫn còn mở, không nằm trong request này

- `CHANGELOG.md` đang 517 dòng, vượt hạn 500 của doc_lint R6 — đã có từ lần bump 0.43.0.
- Văn bản `tdq-spec`/`tdq-intake` vẫn nhắc pha `diagram` đã bị gỡ ngày 2026-09-01.
