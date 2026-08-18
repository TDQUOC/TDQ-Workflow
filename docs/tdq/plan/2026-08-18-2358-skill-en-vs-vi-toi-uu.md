# PLAN — Skill tiếng Anh vs tiếng Việt + phương án tối ưu bộ workflow

Ngày: 2026-08-19 · Spec: ../spec/2026-08-18-2358-skill-en-vs-vi-toi-uu.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
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
- Dùng: `scripts/skill_tokens.py`
  - Nạp: đã chạy ở phase analyze (đo lại token `tdq-build/SKILL.md` bản Việt/Anh).
  - Để: lấy số ký tự/token thật, không ước lượng char/4.
  - Ra: bảng số trong `docs/tdq/research/2026-08-18-2358-skill-en-vs-vi-toi-uu.md`.
  - Kiểm: bảng đã có trong file research, số khớp log lệnh đã chạy.
  - Không dùng cho: đo lại ở phase build — số đã chốt từ analyze.

- [x] **T1.1** (e10m) Thêm mục "Vòng 2026-08-19" vào CUỐI `de-an-toi-uu-context.md`: kết
  luận cuối về hướng A (khớp ngôn ngữ chỉ dẫn/nội dung, đối chiếu soul), số thực nghiệm
  mới (0,568 trên `tdq-build/SKILL.md`) — Test: `grep -c "Vòng 2026-08-19"
  docs/tdq/audit/de-an-toi-uu-context.md` ≥ 1
  - Chạm: `docs/tdq/audit/de-an-toi-uu-context.md`
- [x] **T1.2** (e8m) Viết report tổng hợp + bảng phương án patch xếp thứ tự D→C→B→A
  (E vẫn không làm) — Test: `python3 scripts/doc_lint.py
  docs/tdq/reports/2026-08-18-2358-skill-en-vs-vi-toi-uu.md` exit 0
  - Chạm: `docs/tdq/reports/2026-08-18-2358-skill-en-vs-vi-toi-uu.md`
  - Cần: T1.1

**Xong P1 khi**: cả hai file đầu ra tồn tại, `doc_lint` exit 0, `git status --short` chỉ
liệt kê file trong `docs/tdq/`.

## Cụm song song

Một cụm — cả plan chỉ 1 module (spec §2b), T1.2 phụ thuộc thẳng đầu ra của T1.1
(report tóm tắt từ chính mục vừa viết ở đề án), không có nhánh nào tách rời được để chạy
song song.

## QC


| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | 4 hướng D/C/B/E giữ nguyên nội dung so bản 08-17 | PASS | Dòng 184-188 `de-an-toi-uu-context.md` không đổi số/thứ tự so với vòng trước |
| Q2 | Report đủ tóm tắt + bảng phương án xếp thứ tự | PASS | `docs/tdq/reports/...md` có mục "Đã làm/Kết quả" + bảng D→C→B→A→E |
| Q3 | `doc_lint.py` exit 0 cả 2 file | PASS | Lệnh chạy trực tiếp, cả hai ra "tổng 0 vi phạm, exit 0" |
| Q4 | `git status --short -- docs/tdq` chỉ có docs/tdq | PASS | Output chỉ liệt 6 dòng, toàn bộ trong `docs/tdq/` |
