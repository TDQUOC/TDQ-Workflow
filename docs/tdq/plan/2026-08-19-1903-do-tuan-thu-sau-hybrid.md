# PLAN — Đo hành vi tuân thủ luật sau khi chuyển thể lai

Ngày: 2026-08-19 · Spec: ../spec/2026-08-19-1903-do-tuan-thu-sau-hybrid.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — `mo-phong` chấm đội thắng 27,6 phút so với 30,5 (15 task, 9 đợt,
13/15 khai `Cần:`), nhưng chênh chỉ 2,9 phút và mô hình đó không thấy hai thứ: bảy task
cùng ghi `scripts/tdq_eval.py` nên leader giữ 6 task, và T3.3 — 120 phút thật, dài nhất
plan — là một vòng chạy tuần tự dùng chung một trần chi phí, chia cho nhiều agent thì
vỡ đúng cái trần đó. Phiên này còn có cấu hình không gọi subagent trừ khi user yêu cầu
(ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Nền bộ chạy
- P2 — Bộ ca và bộ chấm
- P3 — Chạy thật 60 phiên
- P4 — Số và kết luận
- P5 — Log & test bắt buộc
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
7. **Cấm mọi phiên đo ghi vào repo này.** Mỗi phiên chạy trong thư mục tạm có git riêng.
   Bộ chạy phải tự từ chối khi thư mục làm việc là repo TDQWorkflow.

## P1 — Nền bộ chạy
- [x] **T1.1** (e12m) Test đỏ cho log service của bộ đo: log có timestamp, bật mặc định,
  tắt được qua biến môi trường — Test: `.venv/bin/python3 -m pytest tests/test_tdq_eval.py -q`
  đỏ đúng các ca mới
  - Chạm: `tests/test_tdq_eval.py` → file mới, chưa node nào phụ thuộc
- [x] **T1.2** (e18m) Khung `scripts/tdq_eval.py`: bốn lệnh con `dung-nhanh`, `chay`, `cham`,
  `bao-cao`, log service bật mặc định — Test: các ca của T1.1 xanh
  - Chạm: `scripts/tdq_eval.py`, `tests/test_tdq_eval.py` → file mới, chưa node nào phụ thuộc
  - Cần: T1.1
- [x] **T1.3** (e20m) Lệnh `dung-nhanh`: dựng hai worktree tại `ea0cdbd` và `f620094` trong
  thư mục tạm, và từ chối chạy nếu thư mục làm việc là chính repo này — Test: hai worktree
  đều có `.claude-plugin/plugin.json`; chạy trong repo gốc thì thoát khác 0 và không tạo gì
  - Chạm: `scripts/tdq_eval.py`, `tests/test_tdq_eval.py`
  - Cần: T1.2

**Xong P1 khi**: dựng được hai nhánh trong thư mục tạm và bộ chạy tự chặn khi bị gọi sai chỗ.

## P2 — Bộ ca và bộ chấm
- [x] **T2.1** (e25m) Chốt 10 ca: mỗi ca có prompt tiếng Việt, seed state cho sandbox, và
  danh sách mã `L###` mà ca đó chấm — Test: mỗi ca chấm ít nhất 3 mã, tổng phép kiểm ≥ 30
  - Chạm: `evals/tuan-thu/` → thư mục dữ liệu mới, chưa node nào phụ thuộc
- [x] **T2.2** (e20m) Transcript mẫu cho từng phép kiểm: một mẫu ĐẠT và một mẫu VI PHẠM —
  Test: đếm mẫu khớp đúng số phép kiểm khai ở T2.1, mỗi phép kiểm đủ hai chiều
  - Chạm: `tests/mau_transcript/` → thư mục dữ liệu mới, chưa node nào phụ thuộc
  - Cần: T2.1
- [x] **T2.3** (e35m) Bộ chấm tất định: mỗi mã `L###` một hàm kiểm đọc dấu vết trong
  transcript `stream-json`, không hàm nào gọi model — Test:
  `.venv/bin/python3 -m pytest tests/test_tdq_eval.py -q` xanh trên toàn bộ mẫu của T2.2
  - Chạm: `scripts/tdq_eval.py`, `tests/test_tdq_eval.py`
  - Cần: T2.2
  - Dùng: `test-driven-development`
  - Để: viết mẫu VI PHẠM cho đỏ TRƯỚC khi viết hàm kiểm, từng phép kiểm một
  - Ra: `tests/mau_transcript/` có cặp mẫu cho mọi phép kiểm, và log chạy đỏ trước xanh sau
  - Kiểm: `.venv/bin/python3 -m pytest tests/test_tdq_eval.py -q` xanh, không ca nào bị `skip`
  - Không dùng cho: T3.3 — vòng chạy thật không phải chỗ viết test
- [x] **T2.4** (e15m) Lệnh `cham`: gom kết quả một phiên thành bản ghi JSON có mã ca, nhánh,
  lần chạy, và kết quả từng mã — Test: chấm lại một transcript mẫu ra đúng bản ghi mong đợi
  - Chạm: `scripts/tdq_eval.py`, `tests/test_tdq_eval.py`
  - Cần: T2.3

**Xong P2 khi**: mọi phép kiểm đỏ đúng trên mẫu vi phạm và xanh đúng trên mẫu đạt.

## P3 — Chạy thật 60 phiên
- [x] **T3.1** (e15m) Chạy thử một phiên thật (1 ca × 1 nhánh) qua `claude -p --plugin-dir`,
  soi transcript đủ dấu vết để chấm, đo chi phí một phiên — Test: transcript có tool call và
  chi phí phiên ra số thật, không ước lượng
  - Cần: T1.3, T2.4
- [x] **T3.2** (e10m) Trần chi phí và cơ chế chạy lại: vượt trần thì dừng, phiên lỗi bị đánh
  dấu để chạy lại — Test: giả lập vượt trần thì thoát khác 0 và không gọi thêm phiên nào
  - Chạm: `scripts/tdq_eval.py`, `tests/test_tdq_eval.py`
  - Cần: T3.1
- [x] **T3.3** (e120m) Chạy đủ 60 phiên, xen kẽ hai nhánh để nhiễu theo thời gian rơi đều —
  Test: có đúng 60 bản ghi, không bản ghi nào ở trạng thái lỗi chưa xử, số lần chạy lại ghi ra
  - Cần: T3.2

**Xong P3 khi**: 60 bản ghi JSON đầy đủ và chi phí thật nằm trong trần.

## P4 — Số và kết luận
- [x] **T4.1** (e20m) Lệnh `bao-cao`: tỉ lệ tuân thủ từng mã ở hai nhánh, số cặp lệch mỗi
  chiều, kiểm định dấu chính xác một phía — Test: trên bộ dữ liệu dựng sẵn có đáp án tính tay,
  giá trị p khớp tới bốn chữ số
  - Chạm: `scripts/tdq_eval.py`, `tests/test_tdq_eval.py`
  - Cần: T2.4
- [x] **T4.2** (e25m) Viết `docs/tdq/audit/do-tuan-thu.md` từ output thật: bảng số, cặp lệch,
  giá trị p, kết luận theo ngưỡng §3 spec, độ nhạy tối thiểu, và mọi khác biệt phụ giữa hai
  commit — Test: mọi con số trong file đối chiếu được với bản ghi JSON, không số nào gõ tay
  - Cần: T3.3, T4.1
  - Dùng: `verification-before-completion`
  - Để: cấm viết câu kết luận nào trước khi có đủ bản ghi của cả hai nhánh
  - Ra: `docs/tdq/audit/do-tuan-thu.md` có bảng số và câu kết luận kèm giá trị p
  - Kiểm: `python3 scripts/tdq_eval.py bao-cao` in ra đúng các số đang nằm trong file
  - Không dùng cho: T4.3 — phần tài liệu chạy lại không cần vòng xác minh này
- [x] **T4.3** (e10m) Lệnh chạy lại một dòng cho lưới hồi quy, kèm tài liệu ngắn ngay trong
  bộ ca — Test: chạy đúng lệnh đó trên một ca ra kết quả chấm được
  - Chạm: `evals/tuan-thu/`
  - Cần: T4.2

**Xong P4 khi**: file audit có số thật của cả hai nhánh và chạy lại được bằng một lệnh.

## P5 — Log & test bắt buộc
- [x] **T5.1** (e8m) Log service đủ ba tính chất: timestamp, mức log, tắt được qua biến môi
  trường, và bật mặc định — Test: chạy hai lần có và không có biến, output khác nhau đúng chỗ
  - Chạm: `scripts/tdq_eval.py`, `tests/test_tdq_eval.py`
  - Cần: T4.1
- [x] **T5.2** (e12m) Full suite đúng một lần, soát không test nào bị tắt hay hạ ngưỡng —
  Test: `cd tests && ../.venv/bin/python3 -m pytest -q` xanh và `git diff -- tests/` không thêm `skip`
  - Cần: T5.1

**Xong P5 khi**: log service đạt cả bốn tính chất và full suite xanh đúng một lần.

## Cụm song song

Bốn cụm. Cụm 1 là P1 và P2: cả hai đều ghi vào `scripts/tdq_eval.py`, nên T1.2, T1.3, T2.3,
T2.4, T3.2, T4.1, T5.1 đụng chung một file và KHÔNG chạy song song được. Cụm 2 là dữ liệu ca
`evals/tuan-thu/` (T2.1, T4.3). Cụm 3 là transcript mẫu `tests/mau_transcript/` (T2.2). Cụm 4
là tài liệu `docs/tdq/audit/do-tuan-thu.md` (T4.2).

Trần tốc độ mode đội rất thấp: chỉ ba task có `Chạm:` không giao nhau (T2.1, T2.2, T4.3), và
T3.3 — task dài nhất, 120 phút — là một vòng chạy tuần tự không chia được cho nhiều agent, vì
60 phiên đều gọi cùng một CLI và cùng một trần chi phí.

## Sửa phát sinh trong implement (bộ đo sai, phát hiện nhờ phiên thật)

- [x] **F1** Ca `bao-loi` không có lỗi thật: seed chung có `dem_tu` ĐÚNG, nên agent chạy thử,
  không tái hiện được, rồi dừng hỏi user — đúng issue-triage bước 2 — mà bộ chấm ghi
  L218/L220 vi-pham. Cả 6 phiên đầu của ca này 0/3 ở CẢ HAI nhánh. Sửa: thêm
  `evals/tuan-thu/bao-loi/seed/src/tien_ich.py` cắt theo đúng một dấu cách nên `dem_tu("")`
  ra 1, bộ test sẵn có vẫn xanh — Test: `CaBaoLoiTaiHienDuocTest` xanh; 6 bản ghi cũ xoá,
  chạy lại bằng seed mới.
- [x] **F2** Ca `duyet-spec` gán nhầm L136: prompt "duyệt spec" là câu duyệt RÕ RÀNG nên chạy
  `approve` là đúng luật, mà L136 chấm vi-pham cho mọi lần `approve`. Sửa: bỏ L136 khỏi ca
  này, thay bằng mã L275 (duyệt spec xong viết plan NGAY cùng turn) và viết giám khảo mới
  kèm cặp mẫu đạt/vi-phạm — Test: `L275Test` và `GanMaDungCaTest` xanh.
- [x] **F3** Giám khảo mù với `sed -i` khi biểu thức dùng `|` làm dấu phân cách: regex cũ
  chặn ngay ở `|` nên mất đường dẫn đứng sau. Phiên thật `build-tick-tung-task__lai__1` tick
  đủ ba task bằng `sed -i ''` mà bị chấm L003/L013/L145 = khong-ap-dung. Sửa: tách lệnh bằng
  `shlex`, chỉ tính là ghi khi có cờ `-i` — Test: `SedGhiFileTest` xanh; chấm lại chính
  transcript đó ra L003/L013/L145/L012 = dat, khớp file plan trong hộp cát có ba dòng `[x]`.
- [x] **F4** `cham --tat-ca`: chấm lại mọi bản ghi từ transcript đã lưu bằng bộ chấm hiện
  hành, giữ nguyên chi phí/số lượt/mã thoát. Cần vì vòng chạy dài hàng giờ, mỗi lần sửa
  giám khảo mà phải chạy lại phiên thật là đốt tiền — Test: `ChamLaiTatCaTest` xanh.

- [x] **F5** Giám khảo mù bối cảnh nên chấm oan cả hai nhánh: L218 ("yêu cầu mới khi chưa
  có request mở → phải mở brief") bị gán cho ca `duyet-spec-mo-ho` chạy ở phase `spec`, nơi
  KHÔNG có yêu cầu mới nào và mở brief mới là sai — nên mã này 0/n ở CẢ HAI nhánh, không nói
  được gì. Sửa tổng quát thay vì gọt danh sách từng ca: `cham_phien` gắn ca vào phiên, L218 và
  L220 trả `khong-ap-dung` khi `phase_dau != idle`, L136 trả `khong-ap-dung` khi prompt là câu
  duyệt rõ ràng — Test: `ApDungTheoPhaseTest` xanh; chấm lại 3 bản ghi `duyet-spec-mo-ho__lai`
  đổi từ L218 = vi-pham sang khong-ap-dung.

- [x] **F6** Thêm bốn mã đo SAU khi vòng chạy đã xong và số đã hiện: L035 (dấu vết AI trong
  commit message), L121 (đóng sổ turn bằng `tdq_finish.py` có cả `--files` lẫn `--log`), L209
  (mỗi lựa chọn đúng một dòng), L210 (khối nói với user chỉ dùng sáu ký hiệu cho phép). Chấm
  lại từ transcript đã lưu nên không tốn phiên nào, nhưng chọn thước khi đã thấy kết quả là
  chuyện khác về mặt thống kê: `bao_cao_so` tách riêng con số của bộ mã đăng ký TRƯỚC vòng chạy
  và đó là con số chốt, bốn mã này chỉ vào phần tham khảo — Test: `TachMaThemSauTest` xanh;
  file audit in cả hai giá trị p, dòng phán quyết lấy theo bộ đăng ký trước.
  Bẫy đã sập một lần khi làm F6: L210 ban đầu chấm dấu `✓` là vi phạm, mà hook TDQ BẮT phải in
  `✓ [TDQ:<MÃ>]` — cả hai nhánh cùng trượt vì tuân lệnh. Lỗi của thước, không phải của model;
  đã loại dòng đó khỏi phép kiểm.
- [x] **F7** Số lần chạy lại của một phiên không được ghi vào bản ghi nên bản ghi của phiên
  vấp-rồi-mới-xong trông y hệt phiên chạy trơn ngay lần đầu. Sửa: `chay_bo` ghi `chay_lai` vào
  bản ghi qua `ghi_lai`, `bao-cao --dem` in luôn tổng số lần chạy lại — Test:
  `test_so_lan_chay_lai_duoc_ghi_vao_ban_ghi` và `test_dem_in_ca_so_lan_chay_lai` xanh.

## Definition of Done
Trỏ về §6 spec, chín hạng mục:

- Q1 bộ chấm đúng — `.venv/bin/python3 -m pytest tests/test_tdq_eval.py -q` xanh trên mọi cặp mẫu.
- Q2 không đụng repo thật — `git status --porcelain` sau vòng chạy chỉ liệt kê đầu ra §2.
- Q3 chạy đủ — `python3 scripts/tdq_eval.py bao-cao --dem` in đúng 60 bản ghi, 0 lỗi chưa xử.
- Q4 đủ độ phủ — `python3 scripts/tdq_eval.py bao-cao --phu` in ≥ 30 phép kiểm, mỗi ca ≥ 3 mã.
- Q5 bảng số đầy đủ — `grep -c "^| L" docs/tdq/audit/do-tuan-thu.md` ra đúng số mã đã đo.
- Q6 kết luận đúng luật — `grep -n "p =\|độ nhạy" docs/tdq/audit/do-tuan-thu.md` có cả hai dòng.
- Q7 log service — `TDQ_EVAL_LOG=0 python3 scripts/tdq_eval.py bao-cao` không in dòng log nào.
- Q8 chi phí — `python3 scripts/tdq_eval.py bao-cao --chi-phi` in số thật và dưới trần đã đặt.
- Q9 chạy lại được — `python3 scripts/tdq_eval.py chay --ca <mã ca> --lan 1` ra kết quả chấm được.

Trượt Q1, Q2 hay Q6 → bỏ toàn bộ kết quả vòng chạy, không giữ số nửa vời.
