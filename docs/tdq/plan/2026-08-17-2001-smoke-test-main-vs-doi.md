# PLAN — Smoke test có số: mode main so với mode đội

Ngày: 2026-08-17 · Spec: ../spec/2026-08-17-2001-smoke-test-main-vs-doi.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — 9/15 task cùng đụng `scripts/tdq_bench.py` (khung CLI → dựng plan → mô phỏng → quét đều là cùng một file), P3 cần hằng số của P4 và P5 cần cả hai; chuỗi phụ thuộc gần như thẳng. Riêng T4.2 gọi agent `tdq-implementer` dù mode nào — đó là đối tượng đo, không phải cách chạy. (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH (mode main)

## Quy tắc thi hành (áp cho mọi task)

1. Red → green: viết/chạy check thất bại trước, rồi code, rồi chạy lại đến pass.
2. Tick `[~]` khi bắt đầu, `[x]` ngay khi test của task xanh.
3. Chỉ chạy test của module đang sửa; full suite đúng một lần ở QC.
4. **Mọi thứ đụng git chạy trong `tempfile.TemporaryDirectory()`. Cấm tạo nhánh hay
   worktree trong repo thật.**
5. **Cấm bịa hằng số thời gian.** Thiếu file thực đo thì lệnh phải lỗi, không đặt mặc định.
6. Không placeholder, không TODO stub. Không commit/push cho đến khi user yêu cầu.
7. Giới hạn cứng của lượt chạy thật: đúng 1 đợt, tối đa 3 agent con, mỗi agent một task nhỏ.

## P1 — Khung script và log service

- [x] **T1.1** (n4 e18m) Tạo `scripts/tdq_bench.py`: khung CLI 4 lệnh con (`dung-plan`, `thuc-do`, `mo-phong`, `quet`), log service in ISO timestamp + tên lệnh + tham số ra stderr, tắt bằng `TDQ_LOG=0` — Test: `python3 scripts/tdq_bench.py --help` exit 0; chạy 1 lệnh có và không `TDQ_LOG=0`, so stderr
  - Chạm: `scripts/tdq_bench.py` → file mới, chưa node nào phụ thuộc
- [x] **T1.2** (n3 e12m) Tạo `tests/test_bench.py`: lớp khung kiểm 4 lệnh con có thật, `--help` exit 0, log service bật/tắt đúng — Test: `python3 -m pytest tests/test_bench.py -q` xanh
  - Chạm: `tests/test_bench.py` → file mới, chưa node nào phụ thuộc

**Xong P1 khi**: `tdq_bench.py --help` liệt kê đủ 4 lệnh và test khung xanh.

## P2 — Dựng plan mẫu làm bài thi

- [x] **T2.1** (n6 e25m) Lệnh `dung-plan --task N --chong R --phu-thuoc K` sinh plan TDQ hợp lệ: N task, tỉ lệ R task đụng chung file với task khác, K task nhắc mã task trước — Test: `dung-plan --task 12 --chong 0.25` rồi `doc_lint` exit 0, đếm cặp chồng file khớp tham số
  - Chạm: `scripts/tdq_bench.py`, `tests/test_bench.py`
  - Dùng: `tdq-plan`
  - Để: sinh plan đúng khuôn task + dòng `Chạm:` mà `tdq_team.py` đọc được
  - Ra: lệnh `dung-plan` trong `scripts/tdq_bench.py`
  - Kiểm: `python3 scripts/doc_lint.py <plan mẫu vừa sinh>` exit 0
  - Không dùng cho: đổi khuôn plan thật của workflow
- [x] **T2.2** (n4 e15m) Plan mẫu chạy được với công cụ thật: `tdq_team.py phan-cong` + `kiem-ke` trên plan mẫu trong repo tạm — Test: cả hai exit 0, bản đồ đủ N bản ghi, mỗi bản ghi 4 trường
  - Chạm: `scripts/tdq_bench.py`, `tests/test_bench.py`

**Xong P2 khi**: một lệnh sinh ra plan mẫu mà `tdq_team.py` phân công được, không sửa tay.

## P3 — Bộ mô phỏng hai mode

- [x] **T3.1** (n5 e20m) Nạp hằng số từ `docs/tdq/bench/<slug>-thuc-do.json`; thiếu file hoặc thiếu hằng số → lỗi rõ ràng, exit khác 0, KHÔNG in bảng — Test: chạy `mo-phong` khi chưa có file → exit khác 0 và stderr nêu tên file phải có
  - Chạm: `scripts/tdq_bench.py`, `tests/test_bench.py`
- [x] **T3.2** (n7 e30m) Công thức `T_main` và `T_đội` theo spec §3, in bảng so sánh cho một plan — Test: ví dụ 4 task/2 đợt với hằng số đặt sẵn, số máy in ra khớp số tính tay ghi trong test
  - Chạm: `scripts/tdq_bench.py`, `tests/test_bench.py`
- [x] **T3.3** (n6 e25m) Lệnh `quet`: chạy mô phỏng trên dải tỉ lệ tách được 0→100%, in bảng và chỉ ra ngưỡng đổi chiều thắng-thua — Test: bảng có ít nhất một dòng đổi chiều, dòng ngưỡng in rõ giá trị
  - Chạm: `scripts/tdq_bench.py`, `tests/test_bench.py`
- [x] **T3.4** (n4 e15m) Test biên: plan 6 task cùng đụng một file → `T_đội >= T_main` — Test: `pytest tests/test_bench.py -q -k bien` xanh
  - Chạm: `tests/test_bench.py`

**Xong P3 khi**: mô phỏng chạy được, kiểm tay khớp, và không có đường nào chạy mà thiếu hằng số thật.

## P4 — Thực đo: lấy hằng số bằng một lượt chạy thật

- [x] **T4.1** (n7 e30m) Lệnh `thuc-do`: dựng repo git tạm + plan mẫu nhỏ, chạy đủ vòng `phan-cong → cum → mo → (giao agent) → kiem → hop → don`, bấm giờ từng chặng, ghi JSON ≥3 mẫu mỗi hằng số kèm độ tản; `don` nằm trong `finally` — Test: chạy với agent giả lập (hàm stub bấm giờ), file JSON có đủ 4 hằng số và trường `so_mau`
  - Chạm: `scripts/tdq_bench.py`, `tests/test_bench.py`
- [x] **T4.2** (n6 e25m) Chạy THẬT một đợt: tối đa 3 agent `tdq-implementer` làm 3 task nhỏ rời nhau trong repo tạm, ghi `docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json` — Test: file có hằng số đo từ lượt thật, mỗi hằng số ghi rõ nguồn `that` hay `stub`
  - Chạm: `docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json`
  - Dùng: tdq-implementer (agent)
  - Để: đóng vai agent con thật để đo `t_task`, `t_phat` và tỉ lệ hỏng
  - Ra: `docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json`
  - Kiểm: file JSON có ≥3 mẫu cho mỗi hằng số, `so_mau` khác 0
  - Không dùng cho: sửa mã trong repo thật

**Xong P4 khi**: file thực đo tồn tại, mọi hằng số ghi rõ số mẫu và nguồn.

## P5 — Kết quả và kết luận

- [x] **T5.1** (n5 e20m) Bảng chất lượng 6 chỉ số cho cả hai mode: test pass · doc_lint · số lần merge xung đột · số task phải làm lại · số defect QC độc lập bắt · tỉ lệ giao/tổng — Test: bảng có đủ 6 dòng, mỗi dòng có số của cả hai mode, không ô nào bỏ trống
  - Chạm: `docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-ket-qua.md`
- [x] **T5.2** (n5 e20m) Mục `## Kết luận` trả lời đúng hai câu user hỏi, hai chiều: ngưỡng nào nên dùng đội, ngưỡng nào nên dùng `main`, kèm khoảng tin — Test: `doc_lint` exit 0; mục có cả câu "nhanh hơn:" lẫn "chất lượng:" kèm số
  - Chạm: `docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-ket-qua.md`
  - Dùng: `tdq-build`
  - Để: viết kết luận theo đúng luật báo cáo (số thật, không tuyên bố khi chưa chạy)
  - Ra: mục `## Kết luận` của file kết quả
  - Kiểm: `python3 scripts/doc_lint.py <file kết quả>` exit 0
  - Không dùng cho: đổi khuôn report của workflow
- [x] **T5.3** (n2 e8m) Ghi kết luận điểm hoà thành một fact dài hạn — Test: `search_memories` với từ khoá "điểm hoà mode đội" trả về fact vừa ghi
  - Dùng: `mem0-memory` (mcp)
  - Để: lưu ngưỡng hoàn vốn của mode đội để request sau không phải đo lại
  - Ra: một fact trong mem0, project `TDQWorkflow`
  - Kiểm: `search_memories` trả về đúng fact
  - Không dùng cho: lưu số liệu thô hay nội dung file

**Xong P5 khi**: file kết quả trả lời được hai câu của user bằng số kèm điều kiện.

## P6 — QC

- [x] **T6.1** (n6 e25m) Chạy đủ Q1–Q12 theo spec §6, ghi output thật vào `docs/tdq/qc/2026-08-17-2001-smoke-test-main-vs-doi.md` — Test: file qc có kết luận PASS/FAIL kèm output cho từng hạng mục
  - Chạm: `docs/tdq/qc/2026-08-17-2001-smoke-test-main-vs-doi.md`
- [x] **T6.2** (n5 e20m) QC độc lập Q13: agent kiểm lại toàn bộ VÀ soi riêng câu "công thức có thiên vị mode đội không" — Test: file qc có mục kết luận độc lập kèm output thật và phán quyết về công thức
  - Dùng: tdq-qc-tester (agent)
  - Để: chấm lại Q1–Q12 không tin lời khai, và phản biện công thức mô phỏng
  - Ra: mục Q13 trong file qc
  - Kiểm: mục Q13 có verdict PASS/FAIL kèm lệnh và output agent tự chạy
  - Không dùng cho: sửa code hay sửa số cho khớp kết luận

- [x] **T6.3** (n3 e8m) Vòng fix 1 — nguồn gốc số: chặn `--lap` dưới 1, ghi `cach_do` cùng `mau_may` cho từng hằng số, ép hằng số dương hữu hạn và `so_mau` ≥ 3 ngay lúc ĐỌC — Test: `thuc-do --lap 0` exit khác 0; `mo-phong` với file có `so_mau` 1 exit khác 0
  - Chạm: `scripts/tdq_bench.py`
- [x] **T6.4** (n2 e5m) Vòng fix 1 — lệnh `mo-phong`: thêm `--he-so-agent`, in hệ số trong dòng tóm tắt, báo lỗi có câu lệnh sửa khi `--plan` trỏ file không đọc được — Test: `mo-phong --he-so-agent 2` in dòng có hệ số; `--plan khong-co.md` exit khác 0
  - Chạm: `scripts/tdq_bench.py`
- [x] **T6.7** (n2 e5m) Vòng fix 1 — lệnh `quet`: thêm `--he-so-agent` và ép `--buoc` nằm trong 1–100 để không bao giờ in bảng rỗng kèm kết luận — Test: `quet --buoc 0` exit khác 0; `quet --he-so-agent 2` in dòng có hệ số
  - Chạm: `scripts/tdq_bench.py`
- [x] **T6.5** (n4 e10m) Vòng fix 1 — phần test: thêm 5 test khoá D1–D5 và sinh lại file thực đo theo schema mới — Test: `pytest tests/test_bench.py -q` xanh, số test ≥ 33
  - Chạm: `tests/test_bench.py`, `docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json`
- [x] **T6.6** (n4 e15m) Vòng fix 1 — phần văn bản: viết lại mục 1 và mục Kết luận của file kết quả cho tách bạch **đo được** với **suy ra**, điền số cho ô `main` ở mục 2, thêm bảng độ nhạy `he_so_agent` — Test: `doc_lint` file kết quả exit 0, agent QC chấm lại ra PASS
  - Chạm: `docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-ket-qua.md`, `docs/tdq/qc/2026-08-17-2001-smoke-test-main-vs-doi.md`

**Xong P6 khi**: 13 hạng mục QC đều PASS.

## Definition of Done

Trỏ về spec §6. Mỗi dòng kiểm được bằng một lệnh.

1. `python3 -m pytest tests/ -q` xanh, số test ≥ 839.
2. `python3 -m pytest tests/test_bench.py -q` xanh.
3. `python3 scripts/tdq_bench.py dung-plan --task 12 --chong 0.25` sinh plan `doc_lint` exit 0.
4. `python3 scripts/tdq_team.py phan-cong` chạy được trên plan mẫu, exit 0.
5. `python3 scripts/tdq_bench.py mo-phong` khi thiếu file thực đo → exit khác 0.
6. `docs/tdq/bench/<slug>-thuc-do.json` tồn tại, mỗi hằng số có `so_mau` ≥ 3.
7. `python3 scripts/tdq_bench.py quet` in bảng có dòng đổi chiều và ngưỡng.
8. `python3 scripts/doc_lint.py docs/tdq/bench/<slug>-ket-qua.md` exit 0.
9. `git status --short` + `git worktree list` + `git branch --list "tdq/*"` giống hệt trước và sau.
10. Chạy 1 lệnh `tdq_bench.py` có và không `TDQ_LOG=0`, stderr khác nhau đúng như luật.
11. `pytest tests/test_bench.py -q -k bien` xanh (plan không tách được thì mode đội thua).
12. File kết quả có mục `## Kết luận` chứa cả "nhanh hơn:" lẫn "chất lượng:" kèm số.
13. File qc có 13 hạng mục, tất cả PASS, trong đó Q13 do agent chạy.
14. Mọi task trong plan này tick `[x]`.
