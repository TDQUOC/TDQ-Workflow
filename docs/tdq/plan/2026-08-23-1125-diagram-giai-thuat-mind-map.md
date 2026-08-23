# PLAN — báo cáo phân tích: dựng diagram giải thuật trước khi code

Ngày: 2026-08-23 · Spec: ../spec/2026-08-23-1125-diagram-giai-thuat-mind-map.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — `mo-phong` cho winner là đội nhưng chỉ hơn 0.9 phút trên 22.4 phút, nằm trong sai số; spec §1b user đã duyệt ghi rõ BỎ chia subagent vì đầu ra là một tài liệu mạch lạc (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH · duyệt lúc (2026-08-23T11:57:19+07:00, user nhắn "duyệt plan")

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Lược đồ và ví dụ bốn lớp
- P2 — Trả lời sáu câu
- P3 — Hai file mẫu
- P4 — Kiểm và đóng sổ
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → chạy phép kiểm trước (phải đỏ) → làm → kiểm lại xanh →
   đổi sang `[x]` NGAY vào file này. Trạng thái: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy `doc_lint.py` trên mọi file đã đụng, phải sạch mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Mọi kết luận trong báo cáo mở đầu bằng `**Kết luận:**` và cùng đoạn phải có URL nguồn
   hoặc chữ `suy luận`. Đây là thứ hạng mục Q2 đếm bằng máy.

## P1 — Lược đồ và ví dụ bốn lớp

- [x] **T1.1** (e12m) Chốt lược đồ dữ liệu mind-map và viết mục `## Lược đồ dữ liệu` vào báo
  cáo: bốn lớp là gì, mỗi nút có trường nào, quan hệ cha con khai thế nào, chỗ nào máy đối
  chiếu được với code thật — Test: `grep -c '^| \`' <báo cáo>` trong mục lược đồ ≥ 8 dòng trường
  - Chạm: `docs/tdq/knowledge/2026-08-23-diagram-truoc-khi-code.md` → file mới, chưa node nào phụ thuộc
- [x] **T1.2** (e15m) Vẽ ví dụ luồng login đủ bốn lớp vào mục `## Ví dụ: luồng login`: lớp
  giải thuật, lớp function flow phía client, lớp function flow phía server, và vị trí của
  luồng này trong cây tổng của project — Test: bốn tiêu đề con `### Lớp` đều tồn tại
  - Chạm: `docs/tdq/knowledge/2026-08-23-diagram-truoc-khi-code.md`
  - Cần: T1.1
  - Dùng: `tdq-lsp-setup`
  - Để: lấy quan hệ hàm thật khi minh hoạ lớp function flow, thay vì bịa tên hàm; nạp skill
    TRƯỚC bước kiểm. Agent ngoài không có skill system: đọc
    `skills/tdq-lsp-setup/SKILL.md` rồi làm theo.
  - Ra: mục `### Lớp 2 — function flow` trong báo cáo, tên hàm lấy từ code thật hoặc khai rõ là hư cấu minh hoạ
  - Kiểm: `python3 scripts/tdq_lsp.py kiem` exit 0, hoặc mục ghi rõ ví dụ là hư cấu minh hoạ
  - Không dùng cho: dựng ngược mind-map cho repo này — đó là việc của request build sau

**Xong P1 khi**: báo cáo có mục lược đồ và mục ví dụ, `doc_lint.py` sạch.

## P2 — Trả lời sáu câu

- [x] **T2.1** (e15m) Viết mục `## 1.` và `## 2.`: ý tưởng có giúp dev kiểm soát project
  không, và có giúp Claude Code xử lý dự án lớn hơn không — mỗi kết luận gắn URL nguồn từ
  file research, chỗ không có số đo thì gắn nhãn `suy luận` — Test: hai mục tồn tại, mỗi
  đoạn `**Kết luận:**` đều có URL hoặc chữ `suy luận`
  - Chạm: `docs/tdq/knowledge/2026-08-23-diagram-truoc-khi-code.md`
  - Cần: T1.2
- [x] **T2.2** (e15m) Viết mục `## 3.` và `## 4.`: có nên thêm vào tdq-workflow không, và
  nếu nên thì chèn vào phase nào. Phải nêu cái giá phải trả của vị trí được chọn, không chỉ
  chép lại ý user — Test: mục 4 có tiểu mục `### Cái giá phải trả`
  - Chạm: `docs/tdq/knowledge/2026-08-23-diagram-truoc-khi-code.md`
  - Cần: T2.1
- [x] **T2.3** (e8m) Viết mục `## 5.`: trình bày text-diagram trong chat có ổn không, kèm
  một khuôn mẫu thật để user nhìn thấy giới hạn của chữ trong giao diện dòng lệnh — Test:
  mục 5 chứa ít nhất một khối mã minh hoạ khuôn text-diagram
  - Chạm: `docs/tdq/knowledge/2026-08-23-diagram-truoc-khi-code.md`
  - Cần: T2.2
- [x] **T2.4** (e15m) Viết mục `## 6. Phương án đề xuất`: các bước cụ thể, ai làm gì, file
  sinh ra ở đâu, và ít nhất một phương án bị loại kèm lý do — Test: mục 6 có tiểu mục
  `### Phương án bị loại`
  - Chạm: `docs/tdq/knowledge/2026-08-23-diagram-truoc-khi-code.md`
  - Cần: T2.3
- [x] **T2.5** (e15m) Viết mục `## Phản biện` với ít nhất ba tiểu mục `### Điểm yếu`, mỗi
  điểm kèm cách giảm; và mục `## Đối chiếu công cụ sẵn có` dạng bảng ít nhất bốn công cụ,
  mỗi dòng nói vì sao không dùng thẳng — Test: đếm được ba `### Điểm yếu` và bốn dòng bảng
  - Chạm: `docs/tdq/knowledge/2026-08-23-diagram-truoc-khi-code.md`
  - Cần: T2.4

**Xong P2 khi**: sáu mục đánh số đủ, mục phản biện và mục đối chiếu đủ, `doc_lint.py` sạch.

## P3 — Hai file mẫu

- [x] **T3.1** (e8m) Viết `docs/tdq/mind-map/vi-du-login.json` theo đúng lược đồ chốt ở T1.1
  — Test: `python3 -c "import json;json.load(open('docs/tdq/mind-map/vi-du-login.json'))"` exit 0
  - Chạm: `docs/tdq/mind-map/vi-du-login.json` → file mới, chưa node nào phụ thuộc
  - Cần: T1.1
- [x] **T3.2** (e20m) Viết `docs/tdq/mind-map/vi-du-login.html`: cây thu gọn mở rộng được,
  toàn bộ CSS và JS nội tuyến, không tham chiếu tài nguyên ngoài, và dòng khai "bản viết
  tay" hiện ngay đầu trang — Test: `grep -c "https\?://" <file html>` bằng 0
  - Chạm: `docs/tdq/mind-map/vi-du-login.html` → file mới, chưa node nào phụ thuộc
  - Cần: T3.1
  - Dùng: `artifact-diagramming`
  - Để: chọn cách bày cây cho dễ đọc ở màn hình hẹp, nạp skill TRƯỚC khi viết HTML. Agent
    ngoài không có skill system: đọc phần hướng dẫn sơ đồ của skill rồi làm theo.
  - Ra: `docs/tdq/mind-map/vi-du-login.html`
  - Kiểm: mở file bằng trình duyệt khi đã ngắt mạng, cây hiện đủ bốn lớp
  - Không dùng cho: xuất bản file này thành Artifact trên claude.ai — user chưa yêu cầu

**Xong P3 khi**: hai file tồn tại, JSON đọc được, HTML không có tham chiếu ngoài.

## P4 — Kiểm và đóng sổ

Log: BỎ — request này không sinh file mã nguồn chạy được, chỉ có tài liệu, một file dữ liệu
và một trang tĩnh, nên không có runtime để bật log.

- [x] **T4.1** (e5m) Chạy `doc_lint.py` trên báo cáo và đếm số dòng — Test:
  `python3 scripts/doc_lint.py <báo cáo>` exit 0 và `wc -l < <báo cáo>` ≤ 250
- [x] **T4.2** (e15m) Chạy đủ mười ba hạng mục Q1–Q13 của spec §6, ghi bằng chứng từng hạng
  mục vào `docs/tdq/qc/2026-08-23-1125-diagram-giai-thuat-mind-map.md` — Test: file QC có
  đúng mười ba dòng kết quả, không dòng nào FAIL

- [x] **T4.3** (e3m) Ghi một fact ngắn về quyết định kiến trúc của request này vào bộ nhớ dài
  hạn, để lần sau không phải phân tích lại từ đầu — Test: tìm lại được fact vừa ghi
  - Cần: T4.2
  - Dùng: `mem0-memory` (mcp)
  - Để: ghi đúng MỘT fact ngắn gồm kết luận nên hay không nên thêm bước diagram, và vị trí
    chèn được chọn; nạp skill TRƯỚC khi ghi. Agent ngoài không có skill system: đọc
    `~/.claude/skills/mem0-memory/SKILL.md` rồi làm theo.
  - Ra: một bản ghi mem0 với `project` là `TDQWorkflow`
  - Kiểm: `mcp__mem0__search_memories` với từ khoá `diagram` trả về đúng fact vừa ghi
  - Không dùng cho: chép cả báo cáo vào mem0 — chỉ một fact ngắn, không dán tài liệu

**Xong P4 khi**: file QC tồn tại, mười ba hạng mục đều PASS, fact mem0 đã ghi.

## Cụm song song

Hai cụm. Cụm `bao-cao` gồm T1.1, T1.2, T2.1 đến T2.5, T4.1 — chín task này ghi vào CÙNG một
file nên buộc phải chạy nối tiếp, không cắt song song được. Cụm `vi-du-mind-map` gồm T3.1 và
T3.2, chạm hai file riêng, chạy song song với cụm trên được sau khi T1.1 xong.

Trần tốc độ của mode đội vì thế là hai luồng, mà luồng dài là chín task nối tiếp. Đó là lý do
dòng `Mode thực thi` đề xuất `main`.

## Definition of Done

- [x] Q1 Báo cáo có đúng sáu mục đánh số khớp sáu câu — `grep -c "^## [1-6]\." <báo cáo>` bằng 6
- [x] Q2 Mỗi kết luận có nguồn hoặc nhãn suy luận — mọi đoạn chứa `**Kết luận:**` cũng chứa `http` hoặc `suy luận`
- [x] Q3 Có ít nhất ba điểm yếu kèm cách giảm — `grep -c "^### Điểm yếu" <báo cáo>` ≥ 3
- [x] Q4 Bảng đối chiếu có ít nhất bốn công cụ — đếm dòng bảng trong mục `## Đối chiếu công cụ sẵn có` ≥ 4
- [x] Q5 Ví dụ có đủ bốn lớp — bốn tiêu đề `### Lớp` tồn tại trong mục ví dụ
- [x] Q6 Đề xuất nêu rõ vị trí chèn — mục 6 có tiểu mục `### Phương án bị loại` và nêu tên phase
- [x] Q7 Ràng buộc tự chứa được giữ — mục 6 không nhắc `npm install`, `pip install`, hay CDN như thứ bắt buộc
- [x] Q8 File dữ liệu mẫu đọc được — `python3 -c "import json;json.load(open('docs/tdq/mind-map/vi-du-login.json'))"` exit 0
- [x] Q9 Lược đồ khớp báo cáo — mọi khoá trong JSON đều xuất hiện ở mục `## Lược đồ dữ liệu`
- [x] Q10 HTML chạy offline — `grep -c "https\?://" docs/tdq/mind-map/vi-du-login.html` bằng 0
- [x] Q11 HTML khai rõ là bản mẫu — `head -40 docs/tdq/mind-map/vi-du-login.html | grep -c "viết tay"` ≥ 1
- [x] Q12 Tài liệu sạch linter — `python3 scripts/doc_lint.py` exit 0 trên báo cáo, spec, plan, file QC
- [x] Q13 Báo cáo không quá dài — `wc -l < <báo cáo>` ≤ 250
