# REPORT — Bộ tìm kiếm 4 tầng: kiểm bằng hiệu ứng, reindex mỗi turn, skill `tdq-setup`

Ngày: 2026-09-28 · Spec: ../spec/2026-09-28-0910-lumen-check-va-setup-tool.md ·
Plan: ../plan/2026-09-28-0910-lumen-check-va-setup-tool.md ·
QC: ../qc/2026-09-28-0910-lumen-check-va-setup-tool.md
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Đã làm

**Gốc của vấn đề không phải lumen hỏng, mà là cả bốn tầng đều được kiểm bằng câu hỏi "có tồn tại
không".** Hôm nay ollama chạy suốt, MCP `lumen` chết cả phiên (`CONNECTION_CLOSED`), bậc 5 vẫn báo
ĐẠT. Đồ thị graphify cũ 8 ngày với 34% node trỏ vào thư mục đã xoá, và không bậc nào của thang nói
gì — vì graphify chưa bao giờ có bậc.

**Bậc 5 nay đo bằng hiệu ứng.** Nó hỏi lumen một câu thật rồi đọc câu trả lời, và so dấu mốc dựng
index với file mã nguồn mới nhất. Nó cũng hết dò ollama bằng PATH: socket được hỏi trước, `which`
chỉ còn để phân biệt "cài rồi mà đang ngủ" với "chưa cài bao giờ". Lỗi PATH này đo được trên máy
macOS thật của user — `/opt/homebrew/bin/ollama` có thật, login shell thấy, nhưng `shutil.which`
từ tiến trình không-login trả `None`, nên thứ tự cũ kết luận "thiếu ollama" và in lệnh cài cho một
daemon đang phục vụ.

**Thêm bậc 8 cho graphify**, công cụ thứ tư trước nay không có bậc nào. Nó so mtime đồ thị với mã
nguồn — không so với commit mới nhất, vì `tdq_finish` dựng đồ thị TRONG lượt còn commit xảy ra SAU,
nên phép so kiểu đó sẽ cảnh báo vĩnh viễn sau mỗi lần commit.

**Reindex vào bước kết lượt, đi bằng CLI.** Lý do đi CLI có bằng chứng: lumen 0.0.42 khai
`defaultFreshnessTTL = 30s` (`cmd/stdio.go`), và auto-reindex chỉ chạy khi có ai gọi
`semantic_search` — MCP chết cả phiên thì cả tuần không ai dựng lại. Chi phí đo được: 0,2 s khi
không có gì đổi, 2,6 s cho một file sửa, nên không có ngưỡng nào cả. Cờ `--skip-graphify` bị gỡ
hẳn: chính nó làm đồ thị cũ 8 ngày.

**`tdq-lsp-setup` → `tdq-setup`, và nó nhận việc cài.** Một lệnh: kiểm 8 bậc, cài phần thiếu trong
danh sách đã khai, kiểm cấu hình, smoke test cả bốn tầng, vá hook plugin ngoài đang đè thứ tự tìm
kiếm, rồi ghi món không tự xử được vào `docs/tdq/no-phu-thuoc.md`. Sửa file của plugin khác là
đường DUY NHẤT — tài liệu Claude Code nói thẳng *"There is no way to disable an individual hook
while keeping it in the configuration"*.

**Luật tìm kiếm thành bốn tầng**, có bảng phụ thuộc runtime (tầng nào chết thì rơi xuống đâu), số
đo ghi kèm tên repo, và bản ngắn được ghim vào instruction user-level trong khối có dấu mốc.

## Kiểm

20 hạng mục DoD cộng QC-F1→F4: **PASS toàn bộ, không vòng fix nào ở phase QC.**

| Môi trường | Python | Kết quả |
|---|---|---|
| Máy dev Windows | 3.13.5 | 2077 ca, 0 fail, 0 error |
| Linux thật của user | 3.14.4 | 2054 ca, 0 fail, 0 error |
| macOS thật của user | 3.13.15 (pyenv) | 2054 ca, 0 fail, 0 error |
| macOS thật của user | 3.14.7 (brew) | 2054 ca, 0 fail, 0 error |

Hai máy thật chạy trong thư mục tạm dưới `~` rồi xoá sạch; không cài gói, không sửa cấu hình, và
**không chạm python hệ thống của Apple** — mọi lần gọi đều bằng đường dẫn tuyệt đối tới pyenv hoặc
brew. Bí mật kết nối không vào file nào của repo; file askpass (ngoài repo, quyền 700) đã xoá.

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 4 min | — | 1 |
| analyze | 21 min | — | 1 |
| spec | 1h 22min | — | 1 |
| plan | 1h 24min | — | 1 |
| implement | 1h 24min | — | 1 |
| qc | 10 min | — | 1 |
| report | 5s | — | 1 |
| **Total** | **4h 46min** | **—** | |

Cột model time trống vì `tdq_timing.py` tìm thư mục transcript theo tên dạng POSIX trong khi máy
Windows lưu ở `C--Users-...`. Nợ có sẵn từ hai request trước, vẫn chưa sửa.

## Hai vòng soát tìm ra thứ tôi tự làm hỏng

`code-review` mức `high` ra **8 phát hiện**, bốn agent `simplify` ra **21 phát hiện**. Vá 22, bỏ 2
có lý do (ghi trong QC). Ba cái đáng kể nhất đều là lỗi của chính bản đầu tôi viết:

- **Bậc 5 GHI trong lúc chẩn đoán.** Nó chạy `lumen index` để đo độ mới, mà `chay_kiem` chạy ở
  bước 1b của MỌI request và cả trong trang trạng thái — nên một hàm-chỉ-để-đọc đi sửa máy user, và
  index bị dựng **hai lần mỗi lượt**. Nay nó chỉ so dấu mốc do `tdq_finish` để lại. Thang 8 bậc từ
  2–10 s xuống **1,47 s**.
- **Danh sách lệnh được phép cài chỉ soi tiền tố đầu chuỗi**, trong khi bậc 3 nối lệnh nhiều ngôn
  ngữ bằng ` ; ` và `_chay_lenh` chạy qua shell: `brew install llvm ; gem install solargraph` lọt
  cả vế sau. Nay `shell=False` + `shlex`, và mọi chuỗi có ký tự shell bị từ chối thẳng.
- **`step_reindex` thiếu cổng ollama.** Chính luật §3 bảo NHẢ daemon ngay sau khi hỏi lumen, nên
  đúng những lượt vừa dùng lumen là những lượt bước này `fail` và đẻ thêm một dòng nợ.

## Ba chỗ làm khác plan

- **T2.1 khai `Cần: T3.5`, một task ở phase sau.** Plan của tôi tự mâu thuẫn với luật "thứ tự phase
  là thứ tự phụ thuộc". Tôi đi theo đồ thị `Cần:` chứ không theo số phase: làm T3.1/T3.2/T3.5 trước
  rồi mới quay lại T2.1.
- **Đổi tên skill làm cùng lúc với phần vỡ của nó ở P5**, thay vì cách nhau hai phase như plan
  viết. Giữa hai mốc đó bộ test đỏ, mà luật buộc suite phải xanh sau mỗi phase — hai việc này không
  tách rời được.
- **Mode `main` trái với số đo.** `simulate` cho đội thắng 20,2 phút và tôi đã đề xuất đội; user
  chọn inline. Ghi lại để lần sau đối chiếu ước lượng với thực tế.

## Còn hạn chế

- **122 dòng chú thích/chuỗi in ra của hai file mới còn tiếng Việt**, lệch quyết định ngôn ngữ 3
  tầng (2026-08-22). Không sửa trong request này vì không test nào gác i18n trên `scripts/` và repo
  đang lẫn sẵn (`tdq_lsp.py` 161 dòng, `tdq_state.py` 42 dòng) — dọn lẻ một file làm vùng đó lệch
  hơn với hàng xóm. Đã khai thành nợ.
- **Bản sao lưu `hooks.json.truoc-tdq.bak` chưa có đường lùi.** `tdq_setup.py` ghi ra nhưng không
  có lệnh nào khôi phục từ nó. Nên có một cờ `--go-va`.
- **Vá hook plugin không sống qua một lần update lumen**: phiên bản nằm trong đường dẫn cache, nên
  bản mới sinh thư mục mới kèm hook cũ. Thiết kế đã tính (chạy lại mỗi lần setup), nhưng nghĩa là
  giữa hai lần setup thì hook cũ có hiệu lực.
- **Danh sách cho phép cài vẫn ở tầng chuỗi.** Cách đúng tầng là `lenh_cai` mang cấu trúc argv
  ngay từ chỗ sinh ra nó; việc đó lan ra mọi bậc nên để lại thành hướng cho sau.
- **Bậc 5 phụ thuộc dấu mốc do `tdq_finish` để lại.** Ai dựng index bằng tay ngoài workflow thì bậc
  5 vẫn báo cũ cho tới lần kết lượt kế tiếp.
- **Chưa merge về `main`.** Nhánh `feature/tdq-setup-bo-4-tang`, gốc `main`.
