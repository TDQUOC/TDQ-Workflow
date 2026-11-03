# PLAN — Đề xuất cơ chế chống quick-fix phá kiến trúc

Ngày: 2026-08-14 · Spec: ../spec/2026-08-14-chong-no-ky-thuat.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — cả 13 task cùng ghi vào đúng MỘT file đề xuất, các mục phải nhất
quán giọng văn và tên cơ chế; tách sub-agent chỉ tạo xung đột ghi và lệch tên mục.
Trạng thái plan: HOÀN THÀNH (2026-08-14, mode `main`, 13/13 task, QC 11/11 PASS)

Đặt `F=docs/tdq/knowledge/2026-08-14-chong-no-ky-thuat.md` cho toàn bộ file này.

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → chạy phép kiểm (đỏ) → viết nội dung → phép kiểm
   xanh → đổi sang `[x]` NGAY vào file này. Trạng thái: `[ ]` chưa làm · `[~]` đang làm ·
   `[x]` xong.
3. Sau mỗi phase: chạy lại các phép kiểm của phase đó, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên
   chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. **Cấm sửa mọi file trong `skills/`, `scripts/`, `hooks/`** — spec §1 để việc thực thi
   ra ngoài phạm vi. Vi phạm là Q11 đỏ.
7. Không commit/push cho đến khi user yêu cầu.

## P1 — Đo lại số thật & dựng khung

- [x] **T1.1** (n3 e10m) Chạy lại 4 phép đo cho 4 khoảng trống K1–K4 của brief (số lần
      chữ "kiến trúc" trong `skills/`, nguyên văn dòng luật implement, nơi `graphify
      affected`/`god-nodes` chưa được gọi, nguyên văn luật "số hạng mục QC = số dòng
      DoD") — Test: 4 lệnh đều exit 0 và mỗi lệnh trả về một con số hoặc một dòng trích
      dẫn có `file:line`
- [x] **T1.2** (n2 e8m) Dựng `$F` với đúng 6 mục `## ` (`Khoảng trống`, `Cơ chế`, `Gói`,
      `Express`, `Áp cho project khác`, `Nguồn`) và bảng khoảng trống 4 dòng `| K1 |`…
      `| K4 |`, mỗi dòng mang số đo của T1.1 — Test: `grep -c "^## " $F` = 6 và
      `grep -c "^| K[1-4] " $F` = 4

**Xong P1 khi**: Q1 và Q2 PASS.

## P2 — Sáu khối cơ chế

Mọi khối theo đúng khuôn 5 trường ở spec §2 (`Chặn` · `Chèn vào` · `Mức` · `Nội dung
nháp` · `Cách kiểm`). Khối nào thay một dòng luật đang có phải trích nguyên dòng bị thay.

- [x] **T2.1** (n5 e18m) Mặt *ràng buộc kiến trúc*: M1 file luật kiến trúc của từng
      project (agent sinh nháp từ code + `graphify god-nodes`, user chốt) và M2 chép ràng
      buộc đó vào khuôn spec — Test: `grep -c "^### M" $F` = 2 và cả 2 khối đủ 5 trường
  - Dùng: `graphify`
  - Để: chạy `graphify god-nodes` lấy danh sách hub thật của repo này làm ví dụ minh hoạ
    trong nội dung nháp của M1. Agent ngoài không có skill system: đọc
    `~/.claude/skills/graphify/SKILL.md` rồi làm theo.
  - Ra: ít nhất 1 dòng ví dụ hub có số bậc thật nằm trong khối M1 của `$F`
  - Kiểm: `grep -c "god-nodes" $F` ≥ 1 và `graphify god-nodes` chạy lại ra cùng tên hub
  - Không dùng cho: sửa `graphify-out/`, hay chạy `graphify extract` ngoài bước đóng turn
- [x] **T2.2** (n5 e16m) Mặt *dùng lại trước khi tạo mới* và *bán kính ảnh hưởng*: M3 luật
      tìm–rồi–mới–tạo ở bước implement, M4 khai vùng chạm trong khuôn plan bằng
      `graphify affected` — Test: `grep -c "^### M" $F` = 4 và cả 4 khối đủ 5 trường
- [x] **T2.3** (n5 e18m) Mặt *cổng QC chống hồi quy*: M5 hạng mục QC cố định ngoài DoD
      (nêu rõ luật "số hạng mục QC = số dòng DoD" bị nới thế nào) và M6 cổng kiểm trùng
      lặp mức B — Test: `grep -c "^### M" $F` = 6 và cả 6 khối đủ 5 trường
  - Dùng: `sonar-duplication`
  - Để: lấy đúng tên rule và lệnh chạy thật của cổng trùng lặp để viết trường `Cách kiểm`
    của M6. Agent ngoài không có skill system: đọc
    `~/.claude/plugins/.../sonarqube/skills/sonar-duplication/SKILL.md` rồi làm theo.
  - Ra: trường `Cách kiểm` của khối M6 trong `$F` là một lệnh chạy được, không phải mô tả
  - Kiểm: lệnh trong `Cách kiểm` của M6 chạy thử được, exit code khác 127
  - Không dùng cho: quét trùng lặp toàn repo hay sửa code theo kết quả quét
- [x] **T2.4** (n3 e10m) Xác minh nguồn cho mọi tool ngoài được nêu trong 6 khối (jscpd,
      import-linter, dependency-cruiser…): còn được bảo trì và tên lệnh đúng — Test: mỗi
      tool nêu trong `$F` có ≥ 1 URL tương ứng ở mục `## Nguồn`
  - Dùng: `tavily-search` (mcp)
  - Để: kiểm tra bản phát hành gần nhất và cú pháp lệnh của từng tool ngoài trước khi đưa
    vào nháp. Agent ngoài không có skill system: đọc
    `~/.claude/skills/tavily-search/SKILL.md` rồi làm theo.
  - Ra: mục `## Nguồn` của `$F` có URL cho từng tool ngoài được nhắc tên
  - Kiểm: `grep -c "^- https\?://" $F` ≥ số tool ngoài được nhắc trong mục `## Cơ chế`
  - Không dùng cho: research thêm cơ chế mới ngoài 6 khối đã chốt ở P2
- [x] **T2.5** (n3 e10m) Soát chéo cả 6 khối: đủ 5 trường bằng nhau, mọi đường dẫn trong
      `Chèn vào` tồn tại, không khối nào `Mức: C` — Test: 5 lệnh `grep -c` của Q3 ra cùng
      một số ≥ 6, mọi đường dẫn `test -f` đúng, `grep -c "^- Mức: C" $F` = 0

**Xong P2 khi**: Q3, Q4, Q5 PASS.

## P3 — Gói, express, phạm vi áp dụng

- [x] **T3.1** (n5 e14m) Ba gói `### Gói tối thiểu` / `### Gói vừa` / `### Gói đầy đủ`
      (gói tối thiểu bắt buộc thuần luật văn bản, không script) cộng đúng một dòng
      `Khuyến nghị: …` — Test: `grep -c "^### Gói" $F` = 3 và `grep -c "^Khuyến nghị: " $F` = 1
- [x] **T3.2** (n3 e10m) Mục `## Express` nêu bản rút gọn: cơ chế nào giữ nguyên, cơ chế
      nào cắt, cắt vì sao — Test: `grep -c "^## Express" $F` = 1 và mục này gọi tên đủ 6
      mã M1–M6
- [x] **T3.3** (n3 e10m) Mục `## Áp cho project khác` (phần nào độc lập ngôn ngữ, phần nào
      phải tự chỉnh cho Unity/game) và mục `## Nguồn` — Test: cả 4 từ khoá `ràng buộc kiến
      trúc`, `dùng lại`, `bán kính ảnh hưởng`, `hồi quy` đều `grep -ci` ≥ 1

**Xong P3 khi**: Q6, Q7, Q8, Q9 PASS.

## P4 — Log & test bắt buộc

Log: BỎ — request này chỉ tạo tài liệu Markdown, không có file mã nguồn chạy được.

- [x] **T4.1** (n2 e6m) Chạy full test suite và xác nhận workflow còn nguyên vẹn — Test:
      `git status --porcelain -- skills scripts hooks` rỗng và `python3 -m pytest tests/ -q`
      không có `failed`, số test ≥ 563

## P5 — QC & report

- [x] **T5.1** (n3 e12m) Chạy đủ 11 hạng mục Q1–Q11, ghi lệnh và bằng chứng vào
      `docs/tdq/qc/2026-08-14-chong-no-ky-thuat.md` — Test: file QC có 11 dòng kết quả,
      11/11 PASS
- [x] **T5.2** (n2 e8m) Viết report 10–20 dòng và ghi một fact ngắn về đề xuất — Test:
      `docs/tdq/reports/2026-08-14-chong-no-ky-thuat.md` tồn tại và
      `python3 scripts/doc_lint.py $F <spec> <plan>` exit 0
  - Dùng: `mem0-memory` (mcp)
  - Để: lưu đúng một fact "đề xuất cơ chế chống nợ kỹ thuật nằm ở `$F`, gói khuyến nghị
    là <tên gói>", project = `TDQWorkflow`. Agent ngoài không có skill system: đọc
    `~/.claude/skills/mem0-memory/SKILL.md` rồi làm theo.
  - Ra: một memory mới trong mem0, project `TDQWorkflow`
  - Kiểm: `search_memories` với truy vấn "chống nợ kỹ thuật" trả về fact vừa ghi
  - Không dùng cho: lưu nội dung đầy đủ của đề xuất hay bất kỳ đoạn văn bản dài nào

**Xong P5 khi**: Q10, Q11 PASS và report đã ghi.

## Definition of Done

Trỏ về §6 của spec. Mười một hạng mục, mỗi dòng một lệnh kiểm:

1. Q1 — `grep -c "^## " $F` = 6.
2. Q2 — `grep -c "^| K[1-4] " $F` = 4.
3. Q3 — `grep -c "^### M" $F`, `grep -c "^- Chặn:" $F`, `grep -c "^- Chèn vào:" $F`,
   `grep -c "^- Nội dung nháp:" $F`, `grep -c "^- Cách kiểm:" $F` ra cùng một số ≥ 6.
4. Q4 — mọi đường dẫn trong trường `Chèn vào` đều `test -f` đúng, 0 lỗi.
5. Q5 — `grep -c "^- Mức: C" $F` = 0.
6. Q6 — `grep -c "^### Gói" $F` = 3.
7. Q7 — `grep -c "^Khuyến nghị: " $F` = 1.
8. Q8 — `grep -c "^## Express" $F` = 1.
9. Q9 — `grep -ci` cho `ràng buộc kiến trúc`, `dùng lại`, `bán kính ảnh hưởng`, `hồi quy`
   đều ≥ 1.
10. Q10 — `python3 scripts/doc_lint.py $F docs/tdq/spec/2026-08-14-chong-no-ky-thuat.md
    docs/tdq/plan/2026-08-14-chong-no-ky-thuat.md` exit 0.
11. Q11 — `git status --porcelain -- skills scripts hooks` rỗng và
    `python3 -m pytest tests/ -q` không có `failed`, số test ≥ 563.
