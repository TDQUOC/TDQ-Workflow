# PLAN — Chống sót tick dòng DoD lúc đóng sổ

Ngày: 2026-08-22 · Spec: ../spec/2026-08-22-1627-chong-sot-tick-dod.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — `mo-phong` chấm đội thắng 16,2 phút (16,4 so với 32,6), 16 task chia 8 đợt, giao được 9 task (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH — mode main (user chọn "a" lúc 2026-08-22T19:23)

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Bộ đếm trong tầng CLI
- P2 — Nhắc ở hook Stop
- P3 — Hai khuôn tài liệu
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
7. CẤM đổi `_TASK_LINE` và CẤM đổi giá trị trả về sẵn có của `plan_tick_state()`. Đây là
   điều kiện Q13 của spec. Chạm nhầm thì hoàn nguyên bằng `git checkout -- <file>`.
8. Nhánh nhắc mới CẤM trả `"decision": "block"`. Đây là điều kiện Q11 của spec.

## P1 — Bộ đếm trong tầng CLI

- [x] **T1.1** (e8m) Test đỏ cho bộ đếm ô tick của mục DoD: plan có 5 ô trong mục
      `## Definition of Done`, 2 ô đã `[x]` → trả về tổng 5 xong 2; plan viết DoD không ô
      tick → tổng 0; ô tick nằm ngoài mục DoD không được đếm —
      Test: `python3 -m pytest tests/test_plan_tick.py -q -k dod` đỏ đúng lý do thiếu hàm
  - Chạm: `tests/test_plan_tick.py` → thêm class mới, chưa node nào phụ thuộc
- [x] **T1.2** (e15m) Viết `dod_tick_state(cwd)` trong `scripts/tdq_state.py`: mở file plan
      của request đang active, cắt đoạn từ dòng `## Definition of Done` tới dòng `## ` kế
      tiếp, đếm dòng khớp ô tick KHÔNG đòi mã task in đậm, trả về
      `path, exists, total, done, all_done` —
      Test: `python3 -m pytest tests/test_plan_tick.py -q -k dod` xanh
  - Chạm: `scripts/tdq_state.py`, `tests/test_plan_tick.py` → hàm mới cùng tầng với `plan_tick_state()` (nguồn: `graphify query "plan_tick_state"`)
  - Cần: T1.1
- [x] **T1.3** (e8m) Test đỏ cho bộ đọc file qc: file qc có 12 dòng bảng PASS 0 dòng FAIL →
      trả về 12 và 0; có 1 dòng FAIL → trả về đúng số FAIL; không có file → `exists` sai,
      không ném lỗi —
      Test: `python3 -m pytest tests/test_plan_tick.py -q -k qcket` đỏ đúng lý do thiếu hàm
  - Chạm: `tests/test_plan_tick.py`
  - Cần: T1.2
- [x] **T1.4** (e15m) Viết `qc_result_state(cwd)` trong `scripts/tdq_state.py`: mở
      `docs/tdq/qc/<active_request>.md`, đếm dòng bảng có ô cuối là PASS và ô cuối là FAIL,
      trả về `path, exists, passed, failed, all_pass` —
      Test: `python3 -m pytest tests/test_plan_tick.py -q -k qcket` xanh
  - Chạm: `scripts/tdq_state.py`, `tests/test_plan_tick.py` → hàm mới
  - Cần: T1.3
- [x] **T1.5** (e6m) Test chống hồi quy: chạy `plan_tick_state()` trên một plan CÓ mục DoD
      viết ô tick, kết quả số task phải y hệt plan không có mục DoD —
      Test: `python3 -m pytest tests/test_plan_tick.py -q` xanh toàn bộ
  - Chạm: `tests/test_plan_tick.py`
  - Cần: T1.4

**Xong P1 khi**: hai hàm mới có mặt, `python3 -m pytest tests/test_plan_tick.py -q` xanh.

## P2 — Nhắc ở hook Stop

- [x] **T2.1** (e10m) Test đỏ cho nhắc `[TDQ:DOD]`: dựng state phase `report`, plan còn ô
      DoD trống, file qc toàn PASS → đầu ra hook chứa `[TDQ:DOD]` —
      Test: `python3 -m pytest tests/test_stop_gate.py -q -k dod` đỏ
  - Chạm: `tests/test_stop_gate.py`
  - Cần: T1.4
- [x] **T2.2** (e18m) Cắm nhánh nhắc vào danh sách `hints` của `hooks/scripts/stop_gate.py`,
      chỉ chạy khi ĐỦ bốn điều kiện: phase thuộc `report`/`idle` · `dod_tick_state` có
      `total > 0` · chưa `all_done` · `qc_result_state` có `exists` và `all_pass`. Dòng nhắc
      nêu cả số task chưa xong lẫn số ô DoD chưa tick —
      Test: `python3 -m pytest tests/test_stop_gate.py -q -k dod` xanh
  - Chạm: `hooks/scripts/stop_gate.py`, `tests/test_stop_gate.py` → thêm nhánh vào `main()` (nguồn: `graphify affected "stop_gate" --depth 2`)
  - Cần: T2.1
- [x] **T2.3** (e12m) Test bốn cửa im lặng, mỗi cửa một test: phase `implement` · tổng ô DoD
      bằng 0 · file qc có dòng FAIL · không có file qc — cả bốn đều KHÔNG có `[TDQ:DOD]` —
      Test: `python3 -m pytest tests/test_stop_gate.py -q -k dod` xanh
  - Chạm: `tests/test_stop_gate.py`
  - Cần: T2.2
- [x] **T2.4** (e8m) Test không chặn turn: tình huống có nhắc thì đầu ra KHÔNG chứa
      `"decision": "block"`; và hai điểm chặn cũ `[TDQ:LOG]`, `[TDQ:TICK]` vẫn chặn đúng —
      Test: `python3 -m pytest tests/test_stop_gate.py -q` xanh toàn bộ
  - Chạm: `tests/test_stop_gate.py`
  - Cần: T2.2

**Xong P2 khi**: `python3 -m pytest tests/test_stop_gate.py -q` xanh và nhắc mới bắn đúng một tình huống.

## P3 — Hai khuôn tài liệu

- [x] **T3.1** (e6m) Sửa mục `## Definition of Done` trong khuôn plan: dòng DoD viết có ô
      tick, thêm một câu nêu ô tick DoD là bằng chứng đóng sổ và máy có đếm —
      Test: mục Definition of Done của khuôn có dòng mở đầu bằng ô tick
- [x] **T3.2** (e6m) Sửa bước đóng sổ (bước 8) của khuôn report: nêu rõ tick CẢ ô task lẫn
      ô DoD, và nhắc mã `[TDQ:DOD]` sẽ bắn nếu còn sót —
      Test: bước 8 nhắc cả hai loại ô

## P4 — Log & test bắt buộc

- [x] **T4.1** (e5m) Log service: nhánh nhắc mới ghi một dòng `_info` nêu lý do nhắc
      (số task chưa xong, số ô DoD chưa tick, đường dẫn plan), tắt được y hệt nhánh cũ —
      Test: chạy hook ở tình huống nhắc, stderr có dòng `stop_gate:` kèm timestamp
  - Cần: T2.2
- [x] **T4.2** (e5m) Unit test cho từng thành phần, chạy bằng một lệnh; mọi test chạm file
      dựng thư mục tạm bằng `tempfile`, CẤM chạy trên repo thật —
      Test: `python3 -m pytest tests/test_plan_tick.py tests/test_stop_gate.py -q` xanh
  - Cần: T2.4
- [x] **T4.3** (e8m) Chạy full suite đúng một lần, so với mốc nền 37 đỏ trong
      `tests/test_skill_router.py` — Test: không có đỏ mới ngoài 37 đỏ đã biết
  - Cần: T4.2, T3.2
- [x] **T4.4** (e4m) Kiểm luật ngôn ngữ ba tầng trên code và khuôn đã sửa —
      Test: `python3 scripts/i18n_check.py --kind comment --kind string --kind body` ra 0 dòng vi phạm
  - Cần: T4.3
- [x] **T4.5** (e4m) Kiểm luật tài liệu trên spec và plan —
      Test: `python3 scripts/doc_lint.py --pair docs/tdq/spec/2026-08-22-1627-chong-sot-tick-dod.md docs/tdq/plan/2026-08-22-1627-chong-sot-tick-dod.md` thoát 0
  - Cần: T4.3

## Cụm song song

Chia được hai cụm chạy song song thật:

- Cụm 1 — code (`scripts/tdq_state.py`, `hooks/scripts/stop_gate.py` và test của chúng):
  T1.1 đến T2.4. Chín task này nằm trên một chuỗi phụ thuộc thẳng — `nhac` gọi hàm mà `dem`
  vừa viết — nên phải tuần tự, không tách ra được.
- Cụm 2 — khuôn tài liệu (`plan-template.md`, `report-template.md`): T3.1, T3.2. Hai task
  này không đụng file nào của cụm 1 và không phụ thuộc hàm mới, nên chạy song song được.
- P4 phải đợi cả hai cụm.

Trần tốc độ vì thế là hai luồng, không hơn.

## Definition of Done

Trỏ về §6 của spec, 19 hạng mục. Ô tick dưới đây là bằng chứng đóng sổ — đánh `[x]` khi
hạng mục PASS và bằng chứng đã nằm trong file qc.

- [x] Q1 bộ đếm DoD đếm đúng — `python3 -m pytest tests/test_plan_tick.py -q -k dod` xanh
- [x] Q2 bỏ qua khuôn cũ — plan viết DoD không ô tick, hàm trả về tổng 0
- [x] Q3 không lẫn ô task — plan có cả hai loại ô, hàm chỉ đếm ô trong mục DoD
- [x] Q4 bộ đọc qc đếm đúng — `python3 -m pytest tests/test_plan_tick.py -q -k qcket` xanh
- [x] Q5 chịu được thiếu file qc — không có file, hàm trả về `exists` sai, không ném lỗi
- [x] Q6 nhắc bắn đúng lúc — `python3 -m pytest tests/test_stop_gate.py -q -k dod` xanh
- [x] Q7 im ở phase khác — phase `implement`, đầu ra không chứa `[TDQ:DOD]`
- [x] Q8 im khi DoD không có ô tick — tổng bằng 0, đầu ra không chứa `[TDQ:DOD]`
- [x] Q9 im khi qc chưa PASS hết — có dòng FAIL, đầu ra không chứa `[TDQ:DOD]`
- [x] Q10 nhắc nêu cả ô task — dòng nhắc có cả số task chưa xong lẫn số ô DoD chưa tick
- [x] Q11 không chặn turn — đầu ra tình huống nhắc không chứa `"decision": "block"`
- [x] Q12 điểm chặn cũ không đổi — `python3 -m pytest tests/test_stop_gate.py -q` xanh
- [x] Q13 bộ đếm task cũ không đổi — `python3 -m pytest tests/test_plan_tick.py -q` xanh
- [x] Q14 khuôn plan đã đổi — mục Definition of Done của khuôn có dòng mở đầu bằng ô tick
- [x] Q15 khuôn report đã đổi — bước 8 nhắc cả ô task lẫn ô DoD
- [x] Q16 log service — stderr có dòng `stop_gate:` kèm timestamp nêu lý do nhắc
- [x] Q17 luật ngôn ngữ — chạy ba lần, MỖI LẦN MỘT `--kind` kèm đường dẫn thật (cờ này
  không cộng dồn, thiếu path thì thoát mã 2): `--kind comment` và `--kind string` trên
  `scripts/tdq_state.py hooks/scripts/stop_gate.py`, `--kind body` trên hai khuôn skill vừa sửa — cả ba ra 0 dòng
- [x] Q18 luật tài liệu — `python3 scripts/doc_lint.py --pair <spec> <plan>` thoát 0
- [x] Q19 hồi quy — full suite giữ đúng 37 đỏ mốc nền, không đỏ mới

## QC vòng 2 — fix theo báo cáo QC độc lập

- [x] **QC2.1** Nhắc `[TDQ:DOD]` phải sống sót khi đã có 4 nhắc khác: xếp nó lên ĐẦU danh
      sách hint thay vì nối cuối — Test: `python3 -m pytest tests/test_stop_gate.py -q -k dod` xanh
  - Chạm: `hooks/scripts/stop_gate.py`, `tests/test_stop_gate.py`
- [x] **QC2.2** Ba bộ đọc mới ghi "Never raises" nhưng chỉ bắt `OSError`: plan/qc không phải
      UTF-8 làm hook `Stop` rc=1 kèm traceback — Test: `python3 -m pytest tests/test_plan_tick.py -q -k utf` xanh
  - Chạm: `scripts/tdq_state.py`, `tests/test_plan_tick.py`
- [x] **QC2.3** Hai mục `## Definition of Done` trong một plan: đếm cả hai, không chỉ mục đầu
      — Test: `python3 -m pytest tests/test_plan_tick.py -q -k trung` xanh
  - Chạm: `scripts/tdq_state.py`, `tests/test_plan_tick.py`
  - Cần: QC2.2
- [x] **QC2.4** Biến thể tiêu đề (`## definition of done`, `## Definition of Done (19)`) vẫn
      phải nhận — Test: `python3 -m pytest tests/test_plan_tick.py -q -k biento` xanh
  - Chạm: `scripts/tdq_state.py`, `tests/test_plan_tick.py`
  - Cần: QC2.3
- [x] **QC2.5** Tiêu đề DoD nằm trong khối rào ``` là khuôn mẫu, KHÔNG được đếm —
      Test: `python3 -m pytest tests/test_plan_tick.py -q -k rao` xanh
  - Chạm: `scripts/tdq_state.py`, `tests/test_plan_tick.py`
  - Cần: QC2.4
- [x] **QC2.6** Ô kết quả qc là chữ chưa kết luận (`SKIP`, `TODO`, `PENDING`, `N/A`) không
      được tính là xong — Test: `python3 -m pytest tests/test_plan_tick.py -q -k qcket` xanh
  - Chạm: `scripts/tdq_state.py`, `tests/test_plan_tick.py`
- [x] **QC2.7** Sửa dòng Q17 của mục DoD: `--kind` không cộng dồn và bắt buộc có đường dẫn,
      lệnh cũ thoát mã 2 — Test: chạy đúng nguyên văn lệnh mới, cả ba lần đều thoát 0
- [x] **QC2.8** Sửa hai dòng lệch số trong `docs/tdq/audit/luat-hien-co.md` (L309, L310) —
      Test: `python3 -m pytest tests/test_luat_skill.py -q` xanh
