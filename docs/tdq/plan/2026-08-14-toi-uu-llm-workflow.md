# PLAN — Chấm toàn bộ workflow theo hướng LLM đọc & chi phí context

Ngày: 2026-08-14 · Spec: ../spec/2026-08-14-toi-uu-llm-workflow.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — cả 15 task cùng ghi vào đúng MỘT file đề xuất và phải dùng chung một thang điểm; tách sub-agent sẽ lệch tiêu chí chấm giữa các mục và gây xung đột ghi.
Trạng thái plan: ĐÃ DUYỆT — user nhắn "duyệt plan", mode "a" = main

Đặt `F=docs/tdq/knowledge/2026-08-14-toi-uu-llm-workflow.md` cho toàn bộ file này.

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo. Thang chấm (P1) phải chốt TRƯỚC khi
   nhìn số đo (P2), để không chấm chiều theo kết quả.
2. Mỗi task: đánh `[~]` khi bắt đầu → chạy phép kiểm (đỏ) → viết nội dung → phép kiểm
   xanh → đổi `[x]` NGAY vào file này. Trạng thái: `[ ]` chưa làm · `[~]` đang làm ·
   `[x]` xong.
3. Sau mỗi phase: chạy lại phép kiểm của phase đó, xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên
   chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. **Cấm sửa mọi file trong `skills/`, `hooks/`, `agents/`, `scripts/`** — spec §1 để việc
   thực thi ra ngoài phạm vi. Vi phạm là Q11 đỏ.
7. Mọi con số vào `$F` phải là output của một lệnh đã chạy thật. Số ước lượng phải gắn
   nhãn "ước tính" ngay tại chỗ.
8. Không commit/push cho đến khi user yêu cầu.

## P1 — Chốt thang chấm & dựng khung

- [x] **T1.1** (n3 e10m) Viết mục `## Thang chấm`: 6 tiêu chí R1–R6, mỗi dòng đủ 4 cột
      (mã · chấm cái gì · lệnh đo · thế nào là đạt). Sáu tiêu chí: R1 tầng nạp đúng ·
      R2 mật độ luật · R3 luật trùng giữa các file · R4 thuật ngữ nhất quán ·
      R5 sẵn sàng cho model hạng thấp · R6 runtime mỗi turn — Test:
      `grep -c "^| R[1-6] " $F` = 6 và không dòng nào có ô "lệnh đo" rỗng
- [x] **T1.2** (n2 e6m) Dựng `$F` với đúng 9 mục `## ` theo spec §2 (`Thang chấm`,
      `Bảng chấm skills`, `Bảng chấm hooks & agents`, `Chỗ phí`, `Đề xuất`,
      `Đối chiếu luật`, `Gói`, `Công cụ đo lại`, `Nguồn`) — Test: `grep -c "^## " $F` = 9

**Xong P1 khi**: Q1 và Q2 PASS.

## P2 — Đo thật rồi chấm

- [x] **T2.1** (n5 e15m) Chạy đủ bộ lệnh đo của 6 tiêu chí và lưu số thô vào scratchpad:
      `context_surface.py` (bảng bề mặt) và `--hooks --runs 9`, đếm mệnh lệnh tuyệt đối
      trên từng file, đếm biến thể thuật ngữ, đếm khối checklist copy được — Test: mỗi
      tiêu chí R1–R6 có ít nhất một output lệnh thật, không tiêu chí nào phải đoán
- [x] **T2.2** (n5 e18m) Mục `## Bảng chấm skills`: một dòng cho MỖI file `.md` trong
      `skills/`, cột file · tầng nạp · token · điểm R1–R6 · chỗ phí lớn nhất — Test: số
      dòng `| skills/` bằng `find skills -name "*.md" | wc -l` (28)
- [x] **T2.3** (n3 e10m) Mục `## Bảng chấm hooks & agents`: 6 hook (kèm ms trung vị đo
      lại) và 3 agent — Test: `grep -c "^| hooks/\|^| agents/" $F` = 9
- [x] **T2.4** (n3 e10m) Đọc 2 knowledge tối ưu gần nhất (`2026-08-05-toi-uu-token-vong-2`,
      `2026-08-08-giam-over-engineer-workflow`) và đánh dấu chỗ nào đã cắt rồi để không
      đề xuất trùng — Test: mục `## Chỗ phí` có ít nhất một dòng ghi rõ trạng thái so với
      vòng trước ("mới" hoặc "đã cắt ở <ngày>, còn dư <số>")

**Xong P2 khi**: Q3, Q4 PASS.

## P3 — Chỗ phí, đề xuất, đối chiếu luật

- [x] **T3.1** (n5 e15m) Mục `## Chỗ phí`: tối đa 8 mục `| F<n> |`, mỗi mục một số đo và
      một vị trí `file:line` hoặc đường dẫn — Test: 100% dòng `| F<n> |` chứa ≥ 1 chữ số
      và chuỗi đường dẫn
- [x] **T3.2** (n8 e25m) Mục `## Đề xuất`: mỗi khối `### Đ<n>` đủ 7 trường `- Chặn:` ·
      `- Chèn vào:` · `- Mức:` · `- Nội dung nháp:` · `- Cách kiểm:` ·
      `- Tác động token:` · `- Tác động model hạng thấp:`. Đề xuất nào sửa luật đang có
      phải trích nguyên văn dòng bị thay. Đề xuất làm xấu cột model hạng thấp bị loại
      ngay tại chỗ — Test: 7 lệnh `grep -c "^- <trường>:" $F` ra cùng một số, bằng
      `grep -c "^### Đ" $F`
- [x] **T3.3** (n5 e12m) Mục `## Đối chiếu luật`: với MỖI file bị đề xuất đụng, đếm số
      mệnh lệnh trước và sau khi áp nháp, cột "sau" không được nhỏ hơn cột "trước" —
      Test: 0 dòng có "sau" < "trước", và tổng hai cột đều là số đếm được bằng lệnh

**Xong P3 khi**: Q5, Q6, Q7 PASS.

## P4 — Gói, công cụ đo lại, nguồn

- [x] **T4.1** (n5 e12m) Mục `## Gói`: `### Gói tối thiểu` / `### Gói vừa` /
      `### Gói đầy đủ` cộng đúng một dòng `Khuyến nghị: …`; gói tối thiểu chỉ gồm đề xuất
      thuần văn bản, không đụng script — Test: `grep -c "^### Gói" $F` = 3 và
      `grep -c "^Khuyến nghị: " $F` = 1
- [x] **T4.2** (n3 e10m) Mục `## Công cụ đo lại`: nháp mở rộng `scripts/context_surface.py`
      (thêm cột nào, đọc gì, in gì) kèm lệnh chạy — chỉ là nháp trong tài liệu, cấm sửa
      file script — Test: lệnh nêu trong mục này chạy thử được, exit code khác 127, và
      `git status --porcelain -- scripts` rỗng
- [x] **T4.3** (n2 e6m) Mục `## Nguồn`: URL cho mọi chuẩn ngoài được viện dẫn, cộng một
      dòng nêu việc áp cùng tiêu chí cho `portable/` là request riêng — Test:
      `grep -c "^- https\?://" $F` ≥ 6

**Xong P4 khi**: Q8, Q9, Q10 PASS.

## P5 — Log, test, QC, report

Log: BỎ — request này chỉ tạo tài liệu Markdown, không có file mã nguồn chạy được.

- [x] **T5.1** (n2 e6m) Chạy full test suite và xác nhận không vượt phạm vi — Test:
      `git status --porcelain -- skills hooks agents scripts` rỗng và
      `python3 -m pytest tests/ -q` không có `failed`, số test ≥ 563
- [x] **T5.2** (n3 e12m) Chạy đủ 12 hạng mục Q1–Q12, ghi lệnh và bằng chứng vào
      `docs/tdq/qc/2026-08-14-toi-uu-llm-workflow.md` — Test: file QC có 12 dòng kết quả,
      12/12 PASS
- [x] **T5.3** (n2 e8m) Viết report 10–20 dòng và ghi một fact ngắn — Test:
      `docs/tdq/reports/2026-08-14-toi-uu-llm-workflow.md` tồn tại và
      `python3 scripts/doc_lint.py $F <spec> <plan>` exit 0
  - Dùng: `mem0-memory` (mcp)
  - Để: lưu đúng một fact "thang chấm 6 tiêu chí + gói khuyến nghị của bản rà workflow
    nằm ở `$F`", project = `TDQWorkflow`, nạp skill TRƯỚC bước đỏ. Agent ngoài không có
    skill system: đọc `~/.claude/skills/mem0-memory/SKILL.md` rồi làm theo.
  - Ra: một memory mới trong mem0, project `TDQWorkflow`
  - Kiểm: `search_memories` truy vấn "thang chấm workflow" trả về fact vừa ghi
  - Không dùng cho: lưu nội dung đầy đủ của bảng chấm hay bất kỳ đoạn văn dài nào

**Xong P5 khi**: Q11, Q12 PASS và report đã ghi.

## Definition of Done

Trỏ về §6 của spec. Mười hai hạng mục, mỗi dòng một lệnh kiểm:

1. Q1 — `grep -c "^## " $F` = 9.
2. Q2 — `grep -c "^| R[1-6] " $F` = 6, không ô "lệnh đo" nào rỗng.
3. Q3 — số dòng `| skills/` trong `$F` bằng `find skills -name "*.md" | wc -l`.
4. Q4 — `grep -c "^| hooks/\|^| agents/" $F` = 9.
5. Q5 — mọi dòng `| F<n> |` có ≥ 1 chữ số và một đường dẫn.
6. Q6 — 7 lệnh `grep -c` cho 7 trường của khối đề xuất ra cùng một số, bằng
   `grep -c "^### Đ" $F`.
7. Q7 — bảng `## Đối chiếu luật` có 0 dòng "luật sau" < "luật trước".
8. Q8 — `grep -c "^### Gói" $F` = 3 và `grep -c "^Khuyến nghị: " $F` = 1.
9. Q9 — lệnh ở mục `## Công cụ đo lại` chạy thử exit code khác 127.
10. Q10 — `grep -c "^- https\?://" $F` ≥ 6.
11. Q11 — `git status --porcelain -- skills hooks agents scripts` rỗng và
    `python3 -m pytest tests/ -q` không có `failed`, số test ≥ 563.
12. Q12 — `python3 scripts/doc_lint.py $F docs/tdq/spec/2026-08-14-toi-uu-llm-workflow.md
    docs/tdq/plan/2026-08-14-toi-uu-llm-workflow.md` exit 0.
