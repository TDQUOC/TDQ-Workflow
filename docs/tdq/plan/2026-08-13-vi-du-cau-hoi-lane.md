# PLAN — Ví dụ & hướng dẫn thân thiện cho câu hỏi kiểu A/B/C

Ngày: 2026-08-13 · Spec: ../spec/2026-08-13-vi-du-cau-hoi-lane.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — 4 file văn bản nhỏ, phụ thuộc nhau về câu chữ (khối hint dùng
chung ở P1 phải nhất quán với cách rà 3 dòng `➤ Duyệt:` ở P2); giao subagent dễ lệch
văn phong giữa các file hơn là tiết kiệm được gì. (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite của module đang sửa, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Đổi khối hint dùng chung trong `interview.md`
- [x] **T1.1** (n2 e5m) Đổi khối "Dòng hướng dẫn trả lời" cuối
  `skills/tdq-intake/references/interview.md`: từ 1 câu chung chung sang 2 phần — nguyên
  tắc ("gõ chữ cái A/B/C, hoặc gõ nguyên câu tự nhiên khớp ý bạn chọn") + 1 dòng ví dụ
  trung tính minh hoạ cả 2 cách (không gắn cứng nội dung theo 1 lane/mode cụ thể) —
  Test: đọc lại file, khối mới ≤ 3 dòng, có cả ví dụ gõ tắt lẫn ví dụ câu tự nhiên,
  `python3 scripts/doc_lint.py skills/tdq-intake/references/interview.md` exit 0

**Xong P1 khi**: đọc lại đúng khuôn 2 phần, doc_lint sạch.

## P2 — Rà & kết luận 3 dòng `➤ Duyệt:` riêng lẻ
- [x] **T2.1** (n2 e5m) Đọc dòng `➤ Duyệt: nhắn "duyệt spec" · Góp ý: nhắn trực tiếp` ở
  `skills/tdq-spec/SKILL.md` bước 4 — **KẾT LUẬN: SỬA** — thêm vế "(duyệt xong viết plan
  ngay)" vì dòng gốc chỉ nói gõ gì, chưa nói dẫn tới gì tiếp theo — Test: đọc lại dòng
  kết luận trong task, nếu SỬA thì `doc_lint.py skills/tdq-spec/SKILL.md` exit 0 → PASS
- [x] **T2.2** (n2 e5m) Đọc dòng `➤ Duyệt: nhắn "duyệt plan mode <mode đề xuất>" (đổi
  được: main|subagent) · Góp ý: nhắn trực tiếp` ở `skills/tdq-plan/SKILL.md` bước 5 —
  **KẾT LUẬN: SỬA** — thêm vế "— duyệt xong build ngay" cùng lý do như T2.1 — Test: đọc
  lại dòng kết luận, nếu SỬA thì `doc_lint.py skills/tdq-plan/SKILL.md` exit 0 → PASS
- [x] **T2.3** (n2 e5m) Đọc dòng `➤ Duyệt: nhắn "duyệt nhanh" (bỏ QC: "duyệt nhanh không
  QC"; "duyệt quick" vẫn chạy) · Góp ý: nhắn trực tiếp` ở `skills/tdq-intake/SKILL.md`
  bước 4 Phần C (SỬA đường dẫn so với đề xuất ban đầu — dòng này thật ra nằm ở
  `SKILL.md`, không phải `references/quick-lane.md`, phát hiện lúc chạy task) —
  **KẾT LUẬN: SỬA** — thêm vế "— duyệt xong implement ngay" cùng lý do như T2.1 — Test:
  đọc lại dòng kết luận, nếu SỬA thì `doc_lint.py skills/tdq-intake/SKILL.md` exit 0 → PASS

**Xong P2 khi**: cả 3 task có dòng kết luận rõ ràng (GIỮ NGUYÊN/SỬA + lý do), file nào
SỬA thì doc_lint sạch.

## P3 — Log & test bắt buộc
Log: BỎ — việc này chỉ sửa 4 file tài liệu markdown hướng dẫn, không tạo/sửa file mã
nguồn chạy được, không có runtime.
- [x] **T3.1** (n1 e3m) Chạy gộp `doc_lint.py` cho mọi file đã đổi ở P1+P2 (SỬA đường dẫn
  file thứ 4 so với plan gốc — dùng `skills/tdq-intake/SKILL.md` theo đúng T2.3) — Test:
  `python3 scripts/doc_lint.py skills/tdq-intake/references/interview.md skills/tdq-spec/SKILL.md skills/tdq-plan/SKILL.md skills/tdq-intake/SKILL.md`

**Xong P3 khi**: lệnh trên exit 0 cho mọi file trong danh sách.

## Definition of Done
Trỏ về §6 của spec `2026-08-13-vi-du-cau-hoi-lane.md`.

| # | Hạng mục | Lệnh kiểm | PASS khi |
|---|---|---|---|
| Q1 | Khối hint `interview.md` đúng khuôn mới | Đọc file | Có nguyên tắc + ví dụ trung tính, ≤ 3 dòng, không gắn cứng 1 lane |
| Q2 | 3 dòng `➤ Duyệt:` đã rà, có kết luận | Đọc plan mục P2 | Đủ 3 file, mỗi dòng ghi rõ GIỮ NGUYÊN/SỬA + lý do |
| Q3 | doc_lint sạch cho các file đã sửa | `python3 scripts/doc_lint.py <từng file đổi>` | Exit 0, không lỗi |
| Q4 | Không phá cấu trúc khuôn A/B/C hiện có | Đọc lại `interview.md` toàn bộ | Các khối khuôn hỏi A/B/C phía trên không đổi, chỉ đổi đúng khối hint cuối |
