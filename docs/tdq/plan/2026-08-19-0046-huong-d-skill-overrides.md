# PLAN — Hướng D: cắt token mô tả skill trong system prompt

Ngày: 2026-08-19 · Spec: ../spec/2026-08-19-0046-huong-d-skill-overrides.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — đề xuất, vì 1 module cấu hình (spec §2b), 5 task phụ thuộc tuyến
tính (backup → sinh đề xuất → ghi settings → đính chính → report); giao agent con cho
chuỗi tuần tự chỉ thêm chi phí brief mà không rút ngắn được gì.
Trạng thái plan: HOÀN THÀNH

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo. T1.1 chưa xong thì CẤM chạm settings.
2. Mỗi task: đánh `[~]` khi bắt đầu → chạy check trước (đỏ) → làm → check xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
5. Không commit/push cho đến khi user yêu cầu.
6. Ghi `~/.claude/settings.json` bằng `json.load` → sửa dict → `json.dump`, CẤM sửa chuỗi
   thô. Ghi xong phải parse lại để xác nhận file còn hợp lệ.

## P1 — Backup và sinh lại file đề xuất
- Dùng: `tdq-spec`, `tdq-plan`, `tdq-build`
  - Nạp: tdq-spec/tdq-plan đã dùng để viết spec+plan này; tdq-build nạp ở đầu phase implement.
  - Để: đưa request đi hết brief → spec → plan → build đúng khuôn TDQ.
  - Ra: spec/plan này, rồi 5 đầu ra §2 ở phase build.
  - Kiểm: `python3 scripts/tdq_state.py next` báo đúng phase sau mỗi lần duyệt.
  - Không dùng cho: sửa code nguồn — request này không chạm `scripts/`, `hooks/`, `skills/`.
- Dùng: `scripts/skill_tokens.py`
  - Nạp: đã chạy ở analyze (`--mo-ta`), chạy lại ở QC để đối chiếu số.
  - Để: lấy token mô tả thật, không ước lượng.
  - Ra: bảng số trong report.
  - Kiểm: `python3 scripts/skill_tokens.py --mo-ta` chạy được, ra tổng 29.788 token.
  - Không dùng cho: đo thân skill theo phase — ngoài phạm vi request này.

- [x] **T1.1** (e5m) Backup `~/.claude/settings.json` sang
  `docs/tdq/audit/settings-backup-2026-08-19.json`, giữ nguyên byte — Test: `md5` hai file
  bằng nhau và `python3 -c "import json;json.load(open(...))"` trên bản backup không lỗi
  - Chạm: `docs/tdq/audit/settings-backup-2026-08-19.json`
- [x] **T1.2** (e10m) Sinh lại `skill-overrides-de-xuat.json` chỉ giữ khoá nguồn `user`
  (261 → 33), giá trị `name-only`/`off` giữ theo bản cũ — Test: file có đúng 33 khoá và
  100% khoá thuộc nhóm nguồn `user` trong `skill-index.json`
  - Chạm: `docs/tdq/audit/skill-overrides-de-xuat.json`
  - Cần: T1.1

## P2 — Áp cấu hình
- [x] **T2.1** (e10m) Ghi `~/.claude/settings.json`: thêm `skillListingMaxDescChars: 300`,
  gộp 33 khoá của T1.2 vào `skillOverrides` sẵn có (giữ `unity-skills`) — Test: parse lại
  JSON không lỗi; `skillListingMaxDescChars` = 300; `skillOverrides` có `unity-skills` +
  đủ 33 khoá; mọi khoá cấp cao của bản backup còn nguyên
  - Chạm: `~/.claude/settings.json`
  - Cần: T1.1, T1.2

## P3 — Đính chính đề án + report
- [x] **T3.1** (e10m) Thêm mục "Đính chính 2026-08-19" vào đề án: nói rõ 87,7% sai vì
  giả định `skillOverrides` áp cho mọi skill, số đúng là 8,8%, và hai đòn bẩy mới — Test:
  `grep -c "Đính chính 2026-08-19"` ≥ 1, mục cũ về hướng D còn nguyên, `doc_lint` exit 0
  - Chạm: `docs/tdq/audit/de-an-toi-uu-context.md`
  - Cần: T2.1
- [x] **T3.2** (e8m) Viết report, nêu rõ điều kiện kiểm chứng (phải mở phiên mới) và cách
  đảo ngược — Test: `python3 scripts/doc_lint.py
  docs/tdq/reports/2026-08-19-0046-huong-d-skill-overrides.md` exit 0
  - Chạm: `docs/tdq/reports/2026-08-19-0046-huong-d-skill-overrides.md`
  - Cần: T3.1

**Xong P3 khi**: 5 đầu ra §2 tồn tại, `doc_lint` exit 0, `git status --short` không liệt kê
file nào ngoài `docs/tdq/`.

## Cụm song song

Một cụm — cả plan là một chuỗi phụ thuộc tuyến tính (spec §2b): không được ghi settings
khi chưa có backup, không sinh được nội dung đính chính khi chưa biết kết quả ghi, và
report đọc từ mục đính chính. Không có nhánh nào tách rời để chạy song song.

## QC

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Backup hợp lệ trước khi ghi | PASS | md5 backup = md5 bản gốc lúc T1.1 = `d3009679133b6146f0e34492268c92f0`; `json.load` bản backup không lỗi |
| Q2 | File đề xuất chỉ còn khoá có tác dụng | PASS | 33 khoá; danh sách khoá không thuộc nguồn `user` = rỗng |
| Q3 | Settings sau khi ghi hợp lệ và đủ khoá | PASS | parse OK · `skillListingMaxDescChars`=300 · `unity-skills`=`user-invocable-only` còn nguyên · thiếu khoá mới = rỗng · mất khoá cấp cao = rỗng (17 khoá) |
| Q4 | Đề án có đính chính, không xoá phần cũ | PASS | mục 4 cũ còn nguyên (grep `^## 4\.` = 1); mục mới ở dòng 275, nêu đúng 8,8% ở dòng 295 |
| Q5 | Không file mã nguồn nào bị đổi | PASS | `git status --short` ngoài `docs/` chỉ có `graphify-out/*` — sản phẩm sinh tự động của `tdq_finish`, không phải mã nguồn |
| Q6 | Report nêu rõ điều kiện kiểm chứng còn thiếu | PASS | report có khối cảnh báo "CHƯA XÁC NHẬN" yêu cầu mở phiên mới + cách đảo ngược |

Không có hạng mục FAIL, không cần vòng fix.
