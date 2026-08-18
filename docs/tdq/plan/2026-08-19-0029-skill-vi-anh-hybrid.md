# PLAN — Hybrid skill: luật tiếng Anh, giao tiếp user tiếng Việt

Ngày: 2026-08-19 · Spec: ../spec/2026-08-19-0029-skill-vi-anh-hybrid.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — đề xuất, vì 1 module duy nhất (đã chốt ở spec §2b), 2 task tuần tự
phụ thuộc thẳng (report đọc đầu ra của mục đề án); dựng agent con cho 2 task nối tiếp
tốn brief hơn phần tiết kiệm.
Trạng thái plan: HOÀN THÀNH

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
5. Không commit/push cho đến khi user yêu cầu.

## P1 — Cập nhật đề án + viết report
- Dùng: `tdq-spec`, `tdq-plan`, `tdq-build`
  - Nạp: đã dùng tdq-spec/tdq-plan để viết spec+plan này; tdq-build nạp ở đầu phase implement kế tiếp.
  - Để: đưa request đi hết brief → spec → plan → build đúng khuôn TDQ.
  - Ra: chính spec/plan này, rồi report + audit ở phase build.
  - Kiểm: `python3 scripts/tdq_state.py next` báo đúng phase kế tiếp sau mỗi lần duyệt.
  - Không dùng cho: sửa code nguồn — request này không chạm dòng code nào.
- Dùng: `tavily-primary`
  - Nạp: đã chạy 5 truy vấn ở phase analyze.
  - Để: tìm pattern hybrid + đối chứng superpowers, giải mâu thuẫn 2 nghiên cứu đá nhau.
  - Ra: `docs/tdq/research/2026-08-19-0029-skill-vi-anh-hybrid.md`.
  - Kiểm: file research đã có đủ 5 mục truy vấn + nguồn.
  - Không dùng cho: research lại ở phase build — số liệu đã chốt từ analyze.

- [x] **T1.1** (e10m) Thêm mục mới vào CUỐI `de-an-toi-uu-context.md` (SAU mục "Vòng
  2026-08-19" của request trước, không viết đè): trả lời có pattern hybrid không, vì sao
  superpowers "có vẻ ổn", điều kiện cần trước khi patch thật — Test: `grep -c "Vòng
  2026-08-19 (2)"` docs/tdq/audit/de-an-toi-uu-context.md ≥ 1, `doc_lint` exit 0
  - Chạm: `docs/tdq/audit/de-an-toi-uu-context.md`
- [x] **T1.2** (e8m) Viết report `docs/tdq/reports/2026-08-19-0029-skill-vi-anh-hybrid.md`
  trả lời trực tiếp 2 câu hỏi user đã hỏi — Test: `python3 scripts/doc_lint.py
  docs/tdq/reports/2026-08-19-0029-skill-vi-anh-hybrid.md` exit 0
  - Chạm: `docs/tdq/reports/2026-08-19-0029-skill-vi-anh-hybrid.md`
  - Cần: T1.1

**Xong P1 khi**: cả hai file đầu ra tồn tại, `doc_lint` exit 0, `git status --short --
docs/tdq` chỉ liệt kê file trong `docs/tdq/`.

## Cụm song song

Một cụm — cả plan chỉ 1 module (spec §2b), T1.2 phụ thuộc thẳng đầu ra của T1.1, không có
nhánh nào tách rời được để chạy song song.

## QC
(điền lúc build)

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Đề án cũ có mục mới, không viết đè mục "Vòng 2026-08-19" của request trước | PASS | 2 heading riêng: dòng 196 "Vòng 2026-08-19" (giữ nguyên), dòng 238 "Vòng 2026-08-19 (2)" (mới, nối tiếp) |
| Q2 | Report trả lời trực tiếp 2 câu hỏi user đặt ra | PASS | Report có 2 mục "Câu hỏi 1" / "Câu hỏi 2" ứng đúng 2 câu user hỏi |
| Q3 | doc_lint sạch trên cả 2 file đầu ra | PASS | Cả hai file lint riêng ra "tổng 0 vi phạm, exit 0" |
| Q4 | Không file mã nguồn nào bị đổi | PASS | `git status --short -- docs/tdq` chỉ liệt file trong docs/tdq/ |
