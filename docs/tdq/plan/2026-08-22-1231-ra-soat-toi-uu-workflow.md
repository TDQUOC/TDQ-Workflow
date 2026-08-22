# PLAN — Rà soát toàn bộ workflow sau đợt chuyển tiếng Anh, ra danh sách đề xuất tối ưu

Ngày: 2026-08-22 · Spec: ../spec/2026-08-22-1231-ra-soat-toi-uu-workflow.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — `mo-phong` chấm đội thắng 12,1 phút (26,5 so với 38,7), 19 task chia 6 đợt, giao được 6 task (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH — mode main (user chọn "a" lúc 2026-08-22T12:48)

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Công cụ dò trùng lặp
- P2 — Đo bốn mặt và ghi mốc nền
- P3 — Bảng top 10 đề xuất
- P4 — Log & test bắt buộc
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
7. CẤM sửa bất kỳ file nào trong `skills/`, `agents/`, `hooks/`. Đây là điều kiện Q9 của spec.
   Chạm nhầm một file thì hoàn nguyên ngay bằng `git checkout -- <file>` rồi ghi vào working log.

## P1 — Công cụ dò trùng lặp

- [x] **T1.1** (e10m) Viết test đỏ cho bộ dò shingle: hai file có 3 dòng giống nhau thì
      phải ra đúng một cặp; đổi một chữ trong đoạn thì không ra cặp nào —
      Test: `python3 -m pytest tests/test_doc_dup.py -q -k shingle` đỏ đúng lý do thiếu module
  - Chạm: `tests/test_doc_dup.py` → file mới, chưa node nào phụ thuộc
- [x] **T1.2** (e25m) Viết `scripts/doc_dup.py`: quét vùng file khai bằng `--vung`, cắt
      shingle `--min-dong` dòng liền nhau (mặc định 3), gộp shingle kề nhau thành khối, in
      bảng markdown `file A | dòng | file B | dòng | số dòng | token` ra stdout —
      Test: `python3 -m pytest tests/test_doc_dup.py -q -k shingle` xanh
  - Chạm: `scripts/doc_dup.py`, `tests/test_doc_dup.py` → tạo `main()`, `log()`, `cli()` (nguồn: `docs/kien-truc.md` mục Hub)
  - Cần: T1.1
- [x] **T1.3** (e12m) Đếm token khối trùng bằng bộ đếm thật trong `.venv-tokens/`, y hệt
      cách `skill_tokens.py` làm; thiếu thư viện thì thoát mã 3 kèm câu báo lỗi, CẤM lùi về
      ước lượng ký-tự-chia-bốn — Test: `python3 -m pytest tests/test_doc_dup.py -q -k token` xanh
  - Chạm: `scripts/doc_dup.py`, `tests/test_doc_dup.py`
  - Cần: T1.2
- [x] **T1.4** (e8m) Log service: timestamp ISO ra stderr, bật mặc định, tắt bằng `--quiet`
      hoặc `TDQ_DUP_LOG=0`, bảng luôn ra stdout — Test: `python3 -m pytest tests/test_doc_dup.py -q -k log` xanh
  - Chạm: `scripts/doc_dup.py`, `tests/test_doc_dup.py`
  - Cần: T1.2
- [x] **T1.5** (e6m) Chốt mã thoát: 0 chạy xong · 2 sai cú pháp · 3 thiếu thư viện đếm —
      cùng hợp đồng với `context_surface.py` — Test: `python3 -m pytest tests/test_doc_dup.py -q -k thoat` xanh
  - Chạm: `scripts/doc_dup.py`, `tests/test_doc_dup.py`
  - Cần: T1.3

**Xong P1 khi**: `python3 scripts/doc_dup.py --vung skills --vung agents --vung docs/claude-md-mau.md`
thoát 0 và in bảng có ít nhất một cặp.

## P2 — Đo bốn mặt và ghi mốc nền

- [x] **T2.1** (e6m) Ghi mục `## Mốc nền` của hồ sơ audit: chép nguyên output của
      `context_surface.py --quiet` và `skill_tokens.py --theo-phase`, ghi ngày đo —
      Test: đọc lại file, mỗi bảng có một dòng `Nguồn: <lệnh>` ngay dưới
- [x] **T2.2** (e10m) Mục A — context cost: xếp hạng file theo token nhân tầng nạp, chỉ ra
      5 file đắt nhất và phần cắt được của từng file — Test: bảng có đủ 5 dòng, mỗi dòng có số token
  - Cần: T2.1
- [x] **T2.3** (e15m) Mục B — trùng lặp: chạy `doc_dup.py`, chép bảng, rồi loại tay từng cặp
      là khuôn mẫu chung chứ không phải trùng thật, ghi lý do loại từng cặp —
      Test: mỗi cặp bị loại có đúng một dòng lý do
  - Cần: T1.5, T2.1
- [x] **T2.4** (e10m) Mục C — runtime: chạy `step_audit.py` trên các phiên request đã đóng
      (KHÔNG lấy phiên đang chạy), ghi rõ lấy phiên nào — Test: bảng có cột số step và dòng ghi phiên nguồn
  - Cần: T2.1
- [x] **T2.5** (e12m) Mục D — chất lượng bản dịch: chạy `i18n_check.py` cả ba kind, cộng đọc
      tay bảy thân SKILL.md, liệt kê câu tối nghĩa và thuật ngữ lệch —
      Test: mỗi mục liệt kê trích đúng nguyên văn câu và đường dẫn kèm số dòng
  - Cần: T2.1

**Xong P2 khi**: hồ sơ audit có đủ bốn mục A, B, C, D, mục nào cũng mở đầu bằng một bảng số có nguồn.

## P3 — Bảng top 10 đề xuất

- [x] **T3.1** (e20m) Viết mục `## Top 10 đề xuất`: đúng 10 dòng, 5 cột — đề xuất · token
      tiết kiệm ước tính · luật gốc bị chạm · phép kiểm bắt được nếu vỡ · hạng rủi ro.
      Đề xuất nào đụng nội dung luật thì loại khỏi bảng — Test: đếm được đúng 10 dòng, không ô nào trống
  - Cần: T2.2, T2.3, T2.4, T2.5
- [x] **T3.2** (e5m) Cộng tổng token tiết kiệm ước tính, ghi một dòng kết kèm phần trăm so
      với trần 59.486 token — Test: số tổng bằng đúng tổng cột 2 của bảng
  - Cần: T3.1
- [x] **T3.3** (e8m) Đối chiếu từng đề xuất với `soul.md`: đề xuất nào chạm luật gốc thì
      đánh dấu riêng và ghi rõ phải có user duyệt — Test: mọi dòng chạm soul đều có dấu
  - Cần: T3.1

## P4 — Log & test bắt buộc

- [x] **T4.1** (e5m) Log service của `doc_dup.py` đã bật mặc định và tắt được — kiểm lại lần
      cuối sau khi code đã ổn định — Test: `TDQ_DUP_LOG=0 python3 scripts/doc_dup.py --vung skills 2>&1 1>/dev/null` rỗng
  - Cần: T1.4
- [x] **T4.2** (e6m) Unit test cho từng thành phần, chạy bằng một lệnh; mọi test chạm file
      phải dựng thư mục tạm bằng `tempfile`, CẤM chạy trên repo thật —
      Test: `python3 -m pytest tests/test_doc_dup.py -q` xanh
  - Cần: T1.5
- [x] **T4.3** (e8m) Chạy full suite đúng một lần, so với mốc nền 37 đỏ trong
      `tests/test_skill_router.py` — Test: không có đỏ mới ngoài 37 đỏ đã biết
  - Cần: T4.2
- [x] **T4.4** (e4m) Kiểm luật ngôn ngữ ba tầng trên file mới —
      Test: `python3 scripts/i18n_check.py --kind comment --kind string` ra 0 dòng vi phạm
  - Cần: T1.5
- [x] **T4.5** (e4m) Kiểm luật tài liệu trên spec, plan, audit —
      Test: `python3 scripts/doc_lint.py --pair <spec> <plan>` và lint file audit đều thoát 0
  - Cần: T3.3
- [x] **T4.6** (e3m) Xác nhận không sửa file workflow nào —
      Test: `git status --porcelain skills agents hooks` in ra rỗng
  - Cần: T3.3

## Cụm song song

Chia được ba cụm, nhưng chỉ hai cụm chạy song song thật:

- Cụm 1 — công cụ (`scripts/doc_dup.py`, `tests/test_doc_dup.py`): T1.1 đến T1.5. Năm task
  này đụng chung đúng hai file nên phải chạy tuần tự trong cùng một cụm, không tách ra được.
- Cụm 2 — đo ba mặt A, C, D (T2.2, T2.4, T2.5): ba task này chỉ ghi vào ba mục khác nhau của
  cùng một file hồ sơ, không phụ thuộc công cụ mới, nên chạy song song với cụm 1 được.
- Cụm 3 — mặt B và toàn bộ P3, P4: phải đợi cả cụm 1 lẫn cụm 2 xong.

Trần tốc độ vì thế là hai luồng, không hơn: một luồng viết code, một luồng đo. Cả ba task
của cụm 2 đều ghi vào cùng một file `docs/tdq/audit/2026-08-22-toi-uu-workflow.md`, nên nếu
chạy mode đội thì ba task đó phải do leader tự làm, không tách worktree được.

## Definition of Done

Trỏ về §6 của spec, 12 hạng mục:

- Q1 công cụ chạy được — `python3 scripts/doc_dup.py --vung skills --vung agents` thoát 0, bảng có ≥ 1 cặp
- Q2 log service — `sh -c 'TDQ_DUP_LOG=0 python3 scripts/doc_dup.py --vung skills 2>&1 1>/dev/null'` rỗng (bọc `sh -c` vì zsh bật MULTIOS sẽ nhân đôi stdout)
- Q3 bộ đếm token — chạy với PYTHONPATH chặn thư viện đếm thì thoát đúng mã 3
- Q4 unit test — `python3 -m pytest tests/test_doc_dup.py -q` xanh
- Q5 hồ sơ đủ bốn mặt — `grep -c '^## Mặt' docs/tdq/audit/2026-08-22-toi-uu-workflow.md` ra 4
- Q6 mọi con số có nguồn — mỗi bảng có dòng `Nguồn:` ngay dưới, chạy lại lệnh ra đúng số ấy
- Q7 top 10 đúng khuôn — đếm đúng 10 dòng bảng, không ô nào trống
- Q8 không đề xuất nào đổi luật — đọc từng dòng cột "luật gốc bị chạm", mọi dòng chỉ đụng cách viết
- Q9 không sửa file workflow — `git status --porcelain skills agents hooks` rỗng
- Q10 luật ngôn ngữ — `python3 scripts/i18n_check.py --kind comment --kind string` ra 0 dòng
- Q11 luật tài liệu — `python3 scripts/doc_lint.py` trên spec, plan, audit, report thoát 0
- Q12 hồi quy — full suite giữ đúng 37 đỏ mốc nền, không đỏ mới
