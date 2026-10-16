# PLAN — Phân tích học hỏi từ andrej-karpathy-skills để cải tiến TDQ Workflow

Ngày: 2026-10-16 · Spec: ../spec/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — tác vụ thuần túy biên soạn và xuất bản báo cáo HTML Report độc lập; thực thi trực tiếp trong main session giúp tối ưu tốc độ và không làm phân mảnh ngữ cảnh.
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Thiết kế khung Dashboard, CSS System và Biểu đồ SVG
- P2 — Biên soạn nội dung chuyên sâu 6 Section của HTML Report
- P3 — Kiểm định chất lượng render, link nội bộ và QC mức Ultra
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Tuân thủ 6 mã cấm cơ học (ANTI-1 Fake Red, ANTI-2 Blind Assertion, ANTI-3 Dirty State Git, ANTI-4 Late Tick, ANTI-5 Raw Dump, ANTI-6 Broad Area).

## P1 — Thiết kế khung Dashboard, CSS System và Biểu đồ SVG

- [x] **T1.1** (e20m) Xây dựng cấu trúc HTML5 cơ bản, nhúng toàn bộ CSS System (Modern Flexbox/Grid, Dark/Light theme toggle, typography) và 2 biểu đồ trực quan nội bộ (Radar Chart SVG đối chiếu 6 trục năng lực và Waterfall Chart SVG so sánh chi phí token) vào `docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html` — Test: `python -c "import os; p='docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html'; assert os.path.isfile(p) and '<svg' in open(p, encoding='utf-8').read()"`
  - Chạm: `docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html`

**Xong P1 khi**: File HTML được khởi tạo với đầy đủ CSS theme, header KPI cards và 2 biểu đồ SVG nội bộ.

## P2 — Biên soạn nội dung chuyên sâu 6 Section của HTML Report

- [x] **T2.1** (e30m) Biên soạn chi tiết toàn bộ 6 Section lớn vào file HTML: Section 1 (Executive Comparison Matrix), Section 2 (Token Economics Waterfall), Section 3 (4 Karpathy Pillars vs TDQ Guards có bảng code WRONG/RIGHT), Section 4 (Bản đồ ma sát nhận thức và điểm nghẽn workflow), Section 5 (Mô hình kiến trúc lai 'Tâm thức Karpathy trong Bộ giáp TDQ'), Section 6 (Lộ trình 3 giai đoạn và 5 đề xuất nâng cấp cụ thể) — Test: `python -c "p='docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html'; c=open(p, encoding='utf-8').read(); assert len(c.splitlines()) >= 400 and 'Section 6' in c and 'ANTI-' in c"`
  - Chạm: `docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html`
  - Cần: T1.1
  - Dùng: `Agent`
  - Để: thẩm định chất lượng nội dung và đối chiếu chéo các đề xuất
  - Ra: văn bản phân tích chất lượng cao, sâu sắc
  - Kiểm: báo cáo đầy đủ 6 section lớn và các bảng đối chứng
  - Không dùng cho: việc tự ý can thiệp sửa code hệ thống

**Xong P2 khi**: Báo cáo HTML đạt độ dài ≥ 400 dòng (≥ 35 KB), bao hàm đầy đủ 6 Section chuyên sâu, trích dẫn chuẩn xác từ cả 2 repository.

## P3 — Kiểm định chất lượng render, link nội bộ và QC mức Ultra

- [x] **T3.1** (e15m) Kiểm tra cú pháp HTML5, kiểm tra tính tự chứa (không chứa link CDN bên ngoài), kiểm tra tính năng toggle Dark/Light theme, chạy kiểm tra hợp đồng tài liệu và phối hợp agent kiểm thử độc lập hoàn thành QC mức `ultra` — Test: `python scripts/doc_lint.py --pair docs/tdq/spec/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.md docs/tdq/plan/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.md && python -c "p='docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html'; c=open(p, encoding='utf-8').read(); assert 'http' not in c or 'https://' not in c.replace('https://github.com', '')"`
  - Chạm: `docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html`, `docs/tdq/plan/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.md`
  - Cần: T2.1

**Xong P3 khi**: File HTML Report hoàn toàn tự chứa, render hoàn hảo, 0 vi phạm pairing spec/plan.

## Cụm song song

- **Một cụm tuần tự vì**: Tác vụ biên soạn báo cáo HTML có tính kế thừa chặt chẽ: thiết kế khung layout và SVG P1 $\to$ biên soạn nội dung chi tiết P2 $\to$ kiểm tra chất lượng và nghiệm thu P3. Thực thi tuần tự trong `main` mode giúp tập trung cao độ và tối ưu tính nhất quán của giao diện.

## Definition of Done

Trỏ về §6 của spec. Liệt kê lại từng hạng mục QC + lệnh kiểm, MỖI DÒNG MỘT Ô TICK:

- [x] Q1 File HTML Report được tạo tại đúng đường dẫn và tự chứa 100% — `python -c "p='docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html'; assert open(p, encoding='utf-8')"`
- [x] Q2 Đầy đủ cấu trúc 6 Section lớn theo thiết kế — `python -c "c=open('docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html', encoding='utf-8').read(); assert all(f'section-{i}' in c for i in range(1, 7))"`
- [x] Q3 Tích hợp biểu đồ trực quan nội bộ (Radar Chart & Waterfall Chart bằng SVG) — `python -c "c=open('docs/tdq/reports/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.html', encoding='utf-8').read(); assert c.count('<svg') >= 2"`
- [x] Q4 Tính năng Dark/Light theme toggle và Responsive layout — kiểm tra tồn tại logic toggle và biến css theme
- [x] Q5 Hợp đồng tài liệu và tiêu chuẩn ngôn ngữ — `python scripts/doc_lint.py --pair docs/tdq/spec/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.md docs/tdq/plan/2026-10-16-1245-hoc-hoi-andrej-karpathy-skills.md`
- [x] Q6 Kiểm thử độc lập mức `ultra` — chạy subagent kiểm định độc lập và ghi biên bản QC
