# PLAN — Rà soát mức quốc tế hoá của bộ workflow TDQ

Ngày: 2026-08-21 · Spec: ../spec/2026-08-21-2311-workflow-da-ngon-ngu.md (bản 1.1, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — `tdq_bench mo-phong` chấm đội thắng 8,1 phút (28,5 → 20,4), NHƯNG mô phỏng chia đợt theo dòng `Chạm:` mà task tài liệu không có dòng đó, nên nó không thấy 14/14 task đều ghi vào cùng một file `docs/tdq/audit/da-ngon-ngu.md`; chạy song song là merge vỡ. (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Chốt mốc & khung tài liệu
- P2 — Lượt 1: chấm 12 mã kiểm
- P3 — Lượt 2: phản chứng
- P4 — Tổng hợp: điểm khoá cứng & đề xuất
- P5 — Log & test bắt buộc
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo. P3 chỉ chạy khi P2 xong TOÀN BỘ.
2. Mỗi task: đánh `[~]` khi bắt đầu → chạy lệnh kiểm (đỏ/chưa có bằng chứng) → làm → kiểm
   lại xanh → đổi `[x]` NGAY vào file này.
3. **Chỉ được ghi file trong `docs/tdq/`.** Task nào định sửa `hooks/`, `scripts/`,
   `skills/`, `tests/` là DỪNG — spec §1 đã loại ra khỏi phạm vi.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Mọi bằng chứng ghi dạng `đường/dẫn:dòng` và phải trích lại được bằng `sed -n`.

## P1 — Chốt mốc & khung tài liệu

- [x] **T1.1** (e5m) Tạo `docs/tdq/audit/da-ngon-ngu.md` với mục `## Mốc`: commit HEAD, output `git status --short`, số pass/fail của full suite lúc bắt đầu — Test: `grep -c "^" docs/tdq/audit/da-ngon-ngu.md` > 0 và mục `## Mốc` chứa commit id 7 ký tự có thật (`git rev-parse --short HEAD` khớp)
- [x] **T1.2** (e6m) Dựng khung 12 mã K1–K12 trong tài liệu: mỗi mã một khối `### Kx` với 4 dòng trống sẵn `Câu hỏi:` `Bằng chứng:` `Phán quyết:` `Phản chứng:` — Test: `grep -c "^### K" docs/tdq/audit/da-ngon-ngu.md` trả về 12

**Xong P1 khi**: file audit có mục `## Mốc` với số thật và đủ 12 khối `### K`.

## P2 — Lượt 1: chấm 12 mã kiểm

- [x] **T2.1** (e15m) Module M1 (cổng máy): chấm K1–K5 bằng cách đọc `hooks/scripts/prompt_context.py`, `bash_gate.py`, `stop_gate.py`, `scripts/tdq_state.py`; kết bằng một lượt grep toàn repo cho `looks_like_approval` để bắt chỗ gọi ngoài 4 file trên — Test: 5 khối K1–K5 có `Bằng chứng:` kèm `file:dòng` và `Phán quyết:` ∈ {ĐẠT, CHƯA}
- [x] **T2.2** (e12m) Module M2 (khuôn in cho user): chấm K6–K7 — đếm đủ số file luật chép tay khuôn `➤ Duyệt:` bằng grep toàn repo, xác định có nguồn duy nhất hay không — Test: khối K7 ghi con số đếm được và liệt kê đủ ngần ấy `file:dòng`
  - Dùng: `tdq-status`
  - Để: lấy nguyên văn dòng `➤ Duyệt:` mà skill này quy định (SKILL.md:42) làm một mẫu đối chiếu của K7
  - Ra: một dòng bằng chứng `skills/tdq-status/SKILL.md:<dòng>` trong khối K7
  - Kiểm: `sed -n '42p' skills/tdq-status/SKILL.md` khớp chuỗi trích trong tài liệu
  - Không dùng cho: báo trạng thái request hiện tại — task này chỉ đọc luật của nó, không chạy nó
- [x] **T2.3** (e10m) Module M3 (luật ngôn ngữ nền): chấm K8–K9 — đếm số file có luật "Mọi output cho user: tiếng Việt", xác định có luật nào cho phép bám ngôn ngữ user không — Test: khối K9 ghi con số đếm được, mỗi file một dòng `file:dòng`
  - Dùng: `tdq-conventions`
  - Để: đọc luật gốc về ngôn ngữ output và khối cuối turn (`SKILL.md`, `references/user-facing-block.md`) làm đối tượng chấm K8–K9
  - Ra: các dòng bằng chứng trỏ vào `skills/tdq-conventions/` trong khối K8 và K9
  - Kiểm: mỗi dòng bằng chứng trích lại được bằng `sed -n '<dòng>p' <file>`
  - Không dùng cho: sửa bất kỳ dòng luật nào trong `skills/tdq-conventions/` — request này chỉ đọc
- [x] **T2.4** (e12m) Module M4 (lưới tương thích ngược): chấm K10–K12 — đếm file test khoá chuỗi tiếng Việt của cổng duyệt, tìm test khẳng định "câu duyệt cũ vẫn qua cổng", soát `evals/tuan-thu/` xem có ca ngôn ngữ khác không — Test: khối K10 ghi số file đếm được bằng lệnh grep dán kèm; K11, K12 có phán quyết
- [x] **T2.5** (e6m) Điền mục `## Bảng tổng` gom 12 phán quyết lượt 1 vào một bảng — Test: bảng có đúng 12 dòng, `grep -c "^| K" docs/tdq/audit/da-ngon-ngu.md` = 12

**Xong P2 khi**: 12/12 khối có `Bằng chứng:` và `Phán quyết:`, chưa mã nào có `Phản chứng:`.

## P3 — Lượt 2: phản chứng

- [x] **T3.1** (e20m) Đi ngược từng mã K1–K12: mã ĐẠT thì tìm một đường vào làm nó gãy, mã CHƯA thì tìm đường khác trong repo khiến nó vẫn chạy được; ghi dòng `Phản chứng:` nói rõ đã thử gì và kết quả — Test: `grep -c "^Phản chứng:" docs/tdq/audit/da-ngon-ngu.md` = 12, không dòng nào rỗng hay ghi "chưa thử"
  - Cần: T2.1, T2.2, T2.3, T2.4
- [x] **T3.2** (e8m) Mã nào đổi phán quyết sau phản chứng → ghi cả hai lượt kèm lý do đổi, cập nhật `## Bảng tổng`; không mã nào đổi thì ghi một dòng `Không mã nào đổi phán quyết sau lượt 2` — Test: bảng tổng khớp phán quyết cuối của cả 12 khối (đối chiếu bằng mắt trên output `grep "^Phán quyết:"`)
  - Cần: T3.1

**Xong P3 khi**: mọi phán quyết trong tài liệu là phán quyết SAU phản chứng.

## P4 — Tổng hợp: điểm khoá cứng & đề xuất

- [x] **T4.1** (e12m) Viết mục `## Điểm khoá cứng`: mỗi chuỗi tiếng Việt nằm trên đường DUY NHẤT để qua cổng một dòng, kèm `file:dòng` và câu "xoá chuỗi này thì cổng gãy ở đâu" — Test: mỗi dòng có backtick đường dẫn + số dòng, và có mệnh đề hệ quả
  - Cần: T3.2
- [x] **T4.2** (e15m) Viết mục `## Đề xuất cho request sửa sau`: mỗi mã CHƯA ĐẠT đúng một đề xuất, mỗi đề xuất nêu file phải sửa, cách giữ song song câu duyệt tiếng Việt cũ, và test cũ nào phải vẫn xanh — Test: số đề xuất = số mã CHƯA trong bảng tổng; mỗi đề xuất có dòng `Tương thích ngược:`
  - Cần: T3.2
  - Dùng: `tdq-build`
  - Để: giữ luật một-turn, luật tick và luật QC bám DoD khi thi hành P2–P5
  - Ra: `docs/tdq/qc/2026-08-21-2311-workflow-da-ngon-ngu.md` sau phase QC
  - Kiểm: `python3 scripts/doc_lint.py docs/tdq/qc/2026-08-21-2311-workflow-da-ngon-ngu.md` exit 0
  - Không dùng cho: sửa code sản phẩm — request này không có task nào sửa file ngoài `docs/tdq/`

**Xong P4 khi**: 3 đầu ra ở spec §2 đều có mặt trong tài liệu.

## P5 — Log & test bắt buộc

- [x] **T5.1** (e5m) Chạy full test suite đúng một lần, so với số chụp ở T1.1 — Test: `python3 -m pytest tests/ -q 2>&1 | tail -3` cho số pass/fail bằng đúng mốc T1.1
  - Cần: T4.2
- [x] **T5.2** (e4m) Chứng minh không đụng file ngoài `docs/tdq/`: dán `git status --short` vào cuối tài liệu, đối chiếu với mốc T1.1 — Test: mọi đường dẫn MỚI xuất hiện so với mốc đều nằm dưới `docs/tdq/`
  - Cần: T5.1
- [x] **T5.3** (e3m) `doc_lint` sạch cho spec + plan + audit — Test: `python3 scripts/doc_lint.py --pair docs/tdq/spec/2026-08-21-2311-workflow-da-ngon-ngu.md docs/tdq/plan/2026-08-21-2311-workflow-da-ngon-ngu.md` và `python3 scripts/doc_lint.py docs/tdq/audit/da-ngon-ngu.md` đều exit 0
  - Cần: T5.2
  - Dùng: `tdq-plan`
  - Để: giữ đúng khuôn task/`Cần:`/DoD của file plan này khi QC FAIL phải thêm task fix
  - Ra: `docs/tdq/plan/2026-08-21-2311-workflow-da-ngon-ngu.md` qua được lint cặp
  - Kiểm: `python3 scripts/doc_lint.py --pair docs/tdq/spec/2026-08-21-2311-workflow-da-ngon-ngu.md docs/tdq/plan/2026-08-21-2311-workflow-da-ngon-ngu.md` exit 0
  - Không dùng cho: viết plan cho request khác, hay đổi phạm vi spec đã niêm

Log service: BỎ — request này không tạo/sửa file mã nguồn chạy được (spec §4).

## Cụm song song

Một cụm duy nhất về mặt ghi file: **mọi task đều ghi vào cùng một file** `docs/tdq/audit/da-ngon-ngu.md`,
nên không task nào chạy song song được mà không đụng nhau. Đọc thì tách được (M1–M4 đọc 4
vùng file rời nhau), nhưng phần ghi vẫn phải nối tiếp. Kết luận: một cụm, chạy tuần tự.

## Definition of Done

Mỗi dòng kiểm được bằng một lệnh; QC đếm hạng mục theo đúng số dòng này (spec §6 Q1–Q8).

- [ ] Q1 · 12 mã có phán quyết: `grep -c "^Phán quyết: " docs/tdq/audit/da-ngon-ngu.md` = 12 và `grep -c "chưa rõ" docs/tdq/audit/da-ngon-ngu.md` = 0
- [ ] Q2 · bằng chứng trích lại được: rút 5 dòng `file:dòng` bất kỳ, `sed -n '<dòng>p' <file>` khớp nội dung ghi trong tài liệu
- [ ] Q3 · mỗi mã CHƯA có đúng một đề xuất: số dòng `CHƯA` trong bảng tổng = số khối `### Đề xuất`
- [ ] Q4 · đề xuất giữ tương thích ngược: mỗi khối `### Đề xuất` có dòng `Tương thích ngược:` nêu test cũ phải vẫn xanh
- [ ] Q5 · không sửa file ngoài `docs/tdq/`: `git status --short` không có đường dẫn mới ngoài `docs/tdq/`
- [ ] Q6 · suite y hệt mốc: `python3 -m pytest tests/ -q` cho số pass/fail bằng mốc T1.1
- [ ] Q7 · lượt phản chứng đủ 12 mã: `grep -c "^Phản chứng: " docs/tdq/audit/da-ngon-ngu.md` = 12
- [ ] Q8 · lint sạch: `doc_lint --pair <spec> <plan>` và `doc_lint <audit>` cùng exit 0
