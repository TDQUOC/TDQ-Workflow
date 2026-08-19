# PLAN — hướng A hybrid: luật lý luận tiếng Anh, khuôn user-facing tiếng Việt

Ngày: 2026-08-19 · Spec: ../spec/2026-08-19-1616-huong-a-dich-hybrid.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — `mo-phong` chấm đội thắng 22,5 phút so với 38,7 (19 task, 6 đợt,
17/19 khai `Cần:`), nhưng số đó chỉ đếm thời gian, không đếm rủi ro: sáu task P3 cùng
soi một bảng phân loại nghĩa, giao rời sáu agent thì mỗi agent chỉ thấy phần của mình.
Phiên này còn có cấu hình không gọi subagent trừ khi user yêu cầu (ĐỀ XUẤT, user chốt
lúc duyệt — chọn đội chính là lời yêu cầu đó)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Gate ngôn ngữ đầu ra
- P2 — Phân loại ranh giới và lưới khoá song ngữ
- P3 — Viết lại bộ skill
- P4 — Đo, đồng bộ, kiểm cuối
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. **Cấm sửa chữ trong `skills/` trước khi P2 xong.** Lưới khoá hiện hành neo vào câu
   tiếng Việt; động vào chữ trước khi dựng lại lưới là mất bằng chứng.

## P1 — Gate ngôn ngữ đầu ra
- [x] **T1.1** (e12m) Test đỏ cho rule ngôn ngữ: file trong thư mục output viết lẫn đoạn
  văn tiếng Anh thì lint đỏ và nêu đúng số dòng; khối mã, bảng định danh và đoạn trích
  đánh dấu thì KHÔNG đỏ — Test: `.venv/bin/python3 -m pytest tests/test_doc_lint.py -q`
  đỏ đúng các ca mới
  - Chạm: `tests/test_doc_lint.py`
- [x] **T1.2** (e25m) Cài rule R12 vào linter, chỉ áp cho `OUTPUT_DIRS`, có ngưỡng số
  dòng liên tiếp và ngưỡng số từ để tránh báo oan — Test: các ca của T1.1 xanh
  - Chạm: `scripts/doc_lint.py`, `tests/test_doc_lint.py`
  - Cần: T1.1
- [x] **T1.3** (e10m) Chạy R12 trên toàn bộ `docs/tdq/` và `docs/workinglog/` hiện có,
  chỉnh ngưỡng tới khi không còn báo oan, ghi số vào working log — Test:
  `python3 scripts/doc_lint.py docs/tdq docs/workinglog` thoát 0
  - Cần: T1.2

**Xong P1 khi**: R12 bắt được ca lẫn tiếng Anh và không báo oan trên mọi file sinh ra hiện có.

## P2 — Phân loại ranh giới và lưới khoá song ngữ
- [x] **T2.1** (e15m) Test đỏ cho bộ phân loại: mỗi mã `L###` nhận đúng một nhãn, dòng
  thuộc khối khuôn hoặc ví dụ few-shot phải ra nhãn user-facing — Test:
  `.venv/bin/python3 -m pytest tests/test_ranh_gioi.py -q` đỏ đúng các ca mới
  - Chạm: `tests/test_ranh_gioi.py`
- [x] **T2.2** (e30m) Viết `scripts/luat_phan_loai.py`: đọc bảng điểm neo, gợi ý nhãn
  theo dấu hiệu, in bảng nháp, log có timestamp và tắt được qua biến môi trường — Test:
  các ca của T2.1 xanh
  - Chạm: `scripts/luat_phan_loai.py`, `tests/test_ranh_gioi.py`
  - Cần: T2.1
- [x] **T2.3** (e60m) Người soát từng dòng trong 329 mã, chốt nhãn và ghi câu tương ứng
  vào `docs/tdq/audit/ranh-gioi-luat.md` — Test: bảng có đúng 329 dòng, mỗi dòng một nhãn
  - Cần: T2.2
- [x] **T2.4** (e20m) Test khoá bảng phân loại: phủ đủ 329 mã, không mã nào thiếu hoặc
  mang hai nhãn — Test: `.venv/bin/python3 -m pytest tests/test_ranh_gioi.py -q` xanh
  - Chạm: `tests/test_ranh_gioi.py`
  - Cần: T2.3
- [x] **T2.5** (e35m) Lưới khoá song ngữ: thêm cột neo bản mới vào bảng điểm neo, sửa bộ
  kiểm để đối chiếu theo cột đó thay vì chỉ theo câu tiếng Việt — Test:
  `.venv/bin/python3 -m pytest tests/test_luat_skill.py -q` xanh
  - Chạm: `docs/tdq/audit/luat-hien-co.md`, `tests/test_luat_skill.py`
  - Cần: T2.4
- [x] **T2.6** (e10m) Chứng minh lưới không rỗng: xoá thử một luật khỏi một skill, lưới
  phải đỏ và nêu đúng mã, rồi khôi phục — Test: dán cả output đỏ lẫn output xanh sau khôi phục
  - Cần: T2.5
- [x] **T2.7** (e5m) ĐIỂM CHỐT: trình user số đo và kết quả P1+P2, chờ quyết đi hay dừng
  — Test: user trả lời rõ ràng, ghi nguyên văn vào plan
  - Cần: T2.6

**Xong P2 khi**: bảng phân loại phủ đủ 329 mã, lưới khoá đỏ đúng mã khi thử xoá luật, và
user đã quyết đi tiếp hay dừng.

## P3 — Viết lại bộ skill
- [x] **T3.1** (e50m) Viết lại `tdq-conventions` theo hybrid — Test: lưới khoá xanh, các
  test hình dạng và trần token xanh
  - Chạm: `skills/tdq-conventions`
  - Cần: T2.7
- [x] **T3.2** (e45m) Viết lại `tdq-build` — Test: như T3.1
  - Chạm: `skills/tdq-build`
  - Cần: T2.7
- [x] **T3.3** (e45m) Viết lại `tdq-intake` — Test: như T3.1
  - Chạm: `skills/tdq-intake`
  - Cần: T2.7
- [x] **T3.4** (e30m) Viết lại `tdq-spec` — Test: như T3.1
  - Chạm: `skills/tdq-spec`
  - Cần: T2.7
- [x] **T3.5** (e30m) Viết lại `tdq-plan` — Test: như T3.1
  - Chạm: `skills/tdq-plan`
  - Cần: T2.7
- [x] **T3.6** (e10m) Viết lại `tdq-status` — Test: như T3.1
  - Chạm: `skills/tdq-status`
  - Cần: T2.7

**Xong P3 khi**: 100% điểm neo còn hiệu lực và không khối nào trộn hai loại nội dung.

## P4 — Đo, đồng bộ, kiểm cuối
- [x] **T4.1** (e15m) Đo token từng file trước và sau bằng tokenizer thật, ghi
  `docs/tdq/audit/do-hybrid.md` — Test: `python3 scripts/skill_tokens.py --theo-phase`
  ra số mới, chênh lệch ghi rõ từng file
  - Cần: T3.1, T3.2, T3.3, T3.4, T3.5, T3.6
- [x] **T4.2** (e10m) Sinh lại hai bản portable — Test:
  `.venv/bin/python3 -m pytest tests/test_build_portable.py -q` xanh
  - Chạm: `portable_claude`, `portable_codex`
  - Cần: T4.1
- [x] **T4.3** (e20m) Full suite đúng một lần, soát không test nào bị tắt, đánh dấu bỏ
  qua, hay hạ ngưỡng — Test: `cd tests && ../.venv/bin/python3 -m pytest -q` xanh, và
  `git diff -- tests/` không có dòng thêm `skip` nào
  - Cần: T4.2

**Xong P4 khi**: ba bản đồng bộ, full suite xanh, báo cáo đo có số thật.

## Cụm song song

Ba cụm. Cụm 1 là P1 (một vùng file: linter và test của nó). Cụm 2 là P2 (bảng điểm neo,
script phân loại). Cụm 3 là sáu task của P3 — sáu thư mục skill rời nhau, chạy song song
được về mặt file. Trần tốc độ mode đội nằm ở cụm 3: sáu task có `Chạm:` không giao nhau.

P4 không chia cụm: cả ba task đều đọc đầu ra của toàn bộ P3.

## Definition of Done

Trỏ về §6 spec, chín hạng mục:

- Q1 rule ngôn ngữ bắt đúng — `.venv/bin/python3 -m pytest tests/test_doc_lint.py -q` xanh.
- Q2 không báo oan — `python3 scripts/doc_lint.py docs/tdq docs/workinglog` thoát 0.
- Q3 bảng phân loại phủ đủ — `.venv/bin/python3 -m pytest tests/test_ranh_gioi.py -q` xanh.
- Q4 lưới không rỗng — output đỏ của ca xoá thử ở T2.6 có mã `L###` đúng.
- Q5 điểm neo còn hiệu lực — `.venv/bin/python3 -m pytest tests/test_luat_skill.py -q` xanh.
- Q6 ngôn ngữ đúng chỗ — bảng ranh giới soát tay, mọi dòng user-facing còn tiếng Việt.
- Q7 tiết kiệm token — `docs/tdq/audit/do-hybrid.md` ghi mức giảm ít nhất 30%.
- Q8 ba bản đồng bộ — `.venv/bin/python3 -m pytest tests/test_build_portable.py -q` xanh.
- Q9 không nới lưới cũ — `git diff -- tests/` không thêm `skip`, không hạ ngưỡng nào.

Trượt Q5, Q6 hay Q7 → lùi git, không giữ bản viết lại.

## Quyết ở T2.7

Nguyên văn user: "A" — chọn option A: đi tiếp P3, viết lại cả 6 skill + reference theo
bảng ranh giới, rồi đo ở P4.

## Bằng chứng T2.6 — lưới không rỗng

Ba phép thử, mỗi phép khôi phục ngay sau khi đo; `git status` sạch sau cả ba.

1. Xoá dòng luật `Red → green` khỏi `skills/tdq-build/SKILL.md` → đỏ, nêu đúng
   `L005 (skills/tdq-build/SKILL.md:30)`.
2. Khai neo mới cho một mã `user-facing` (L247) → đỏ ở
   `test_ma_user_facing_khong_duoc_doi_neo`, thông báo `mã user-facing bị đổi neo: ['L247']`.
3. Viết lại L005 sang tiếng Anh và khai neo mới đúng → xanh 10 test, 329 subtest. Xoá
   chính câu tiếng Anh đó đi → đỏ, vẫn nêu đúng `L005`.

Phép 3 lần đầu đỏ oan vì neo mới chép thiếu `**` của markdown. Đó là bằng chứng ngưỡng
40 ký tự có hiệu lực thật, và luật "chép nguyên cả ký hiệu" đã ghi vào `luat-hien-co.md`.
