# SPEC — Smoke test có số: mode main so với mode đội, nhanh hơn ở đâu và chất lượng ra sao

Ngày: 2026-08-17 · Bản: 1.0 · Brief: ../brief/2026-08-17-2001-smoke-test-main-vs-doi.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: trả lời hai câu bằng SỐ đo được, không bằng cảm nhận — (a) mode nào nhanh
  hơn và **nhanh hơn trong điều kiện nào**, (b) mode nào cho chất lượng cao hơn theo
  thước đo đã định trước. Kết quả phải kèm điểm hoà (crossover): dưới ngưỡng đó mode đội
  thua, trên ngưỡng đó mode đội thắng.
- Trong phạm vi: bộ mô phỏng cơ học chạy được nhiều hình dạng plan · một lượt chạy THẬT
  nhỏ để hiệu chỉnh hằng số · bảng so sánh + kết luận · script benchmark dùng lại được.
- NGOÀI phạm vi (mặt LOẠI ở vòng scope): bảo mật · tương thích đa nền tảng · trải nghiệm
  người dùng · an toàn dữ liệu. Ngoài ra: KHÔNG đổi thuật toán chia đợt của `tdq_team.py`
  ở request này — đo trước, sửa sau (nếu số cho thấy cần thì mở request riêng).

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | thuần nội bộ, không có ẩn số ngoài repo |
| Interview | CÓ (xong) | 4 câu đã chốt: 1ABC · 2A · 3A · 4A |
| Vòng scope | CÓ (xong) | yêu cầu có từ mở "nhanh hơn"/"chất lượng cao hơn" không kèm số |
| Chạy agent thật | CÓ, một lượt nhỏ | lấy hằng số thời gian thật để hiệu chỉnh mô phỏng |
| QC độc lập (agent) | CÓ | bài này chấm điểm chất lượng — tự chấm là mất giá trị |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Bộ dựng plan mẫu: sinh plan N task với tỉ lệ chồng file và chuỗi phụ thuộc đặt được | `scripts/tdq_bench.py` (lệnh `dung-plan`) | sinh 1 plan 12 task, `doc_lint` exit 0, `tdq_team.py phan-cong` đọc được |
| 2 | Bộ mô phỏng hai mode, ra thời gian mô hình | `scripts/tdq_bench.py` (lệnh `mo-phong`) | in bảng `main` vs `đội` cho một plan, số khớp công thức kiểm tay |
| 3 | Quét nhiều hình dạng plan, tìm điểm hoà | `scripts/tdq_bench.py` (lệnh `quet`) | in bảng theo tỉ lệ tách được 0→100%, chỉ ra ngưỡng đổi chiều |
| 4 | Lượt chạy THẬT một đợt nhỏ trong repo tạm, đo hằng số | `docs/tdq/bench/<slug>-thuc-do.json` | file có ≥3 hằng số đo được, mỗi hằng số kèm số mẫu |
| 5 | Hiệu chỉnh: mô phỏng dùng hằng số thực đo, không dùng số bịa | `scripts/tdq_bench.py` đọc file ở (4) | chạy `mo-phong` khi thiếu file → báo lỗi rõ, không tự bịa hằng số |
| 6 | Bảng chất lượng hai mode | `docs/tdq/bench/<slug>-ket-qua.md` | đủ 6 chỉ số chất lượng ở §6, mỗi chỉ số có số của cả hai mode |
| 7 | Kết luận trả lời đúng hai câu của user | cùng file (6), mục `## Kết luận` | có câu trả lời "nhanh hơn: …" và "chất lượng: …" kèm điều kiện |
| 8 | Log service của `tdq_bench.py` | `scripts/tdq_bench.py` | có timestamp ISO ở stderr, tắt bằng `TDQ_LOG=0` |
| 9 | Unit test cho mọi thành phần trên | `tests/test_bench.py` | `python3 -m pytest tests/test_bench.py -q` xanh |

## 3. Cách tiếp cận & lý do

- Chọn: **mô hình hàng đợi hiệu chỉnh bằng thực đo**. Mô phỏng tính thời gian theo công
  thức dưới đây; mọi hằng số trong công thức lấy từ lượt chạy thật, không đặt tay.

  ```
  T_main = Σ(mọi task) t_task + n_task × t_tick
  T_đội  = Σ(mỗi đợt) [ t_phat + max(t_task trong đợt) + t_kiem + t_hop ] + t_don
           + max(0, Σ t_task(tu_lam) − Σ_đợt max(t_task))      # phần leader làm chen vào
  ```

  Ý nghĩa: mode đội trả trước một khoản phí cố định mỗi đợt (`t_phat`, `t_kiem`, `t_hop`)
  để đổi lấy việc chỉ phải chờ task CHẬM NHẤT của đợt thay vì tổng cả đợt. Phí đó chỉ
  hoàn vốn khi mỗi đợt đủ rộng. Điểm hoà chính là thứ bài thi này phải tìm ra.
- Vì: chạy thật hai lượt đầy đủ (phương án C ở câu 2) cho đúng một điểm dữ liệu, tốn
  token nhất mà không trả lời được câu "nhanh hơn trong điều kiện nào". Mô phỏng hiệu
  chỉnh cho cả một đường cong, và vẫn neo vào số thật.
- Đã loại: (a) mô phỏng thuần bằng hằng số đoán — số đẹp nhưng vô nghĩa; (b) chạy thật
  hai lượt trên việc thật trong repo — lượt sau đã biết đáp án nên không công bằng, và
  vi phạm giới hạn "chỉ repo tạm" user vừa chốt.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đang chạy, đã mở request |
| tdq-spec | plugin:tdq-workflow | NỀN | đang viết chính file này |
| tdq-plan | plugin:tdq-workflow | DÙNG | viết plan cho 9 đầu ra ở §2 |
| tdq-build | plugin:tdq-workflow | DÙNG | thực thi plan, QC, report |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật chung, mọi phase nạp |
| tdq-qc-tester (agent) | plugin:tdq-workflow | DÙNG | chấm Q13 độc lập, không tin lời khai |
| tdq-implementer (agent) | plugin:tdq-workflow | DÙNG | đóng vai agent con trong lượt chạy thật (đầu ra §2.4) |
| mem0-memory | plugin | DÙNG | ghi lại kết luận điểm hoà làm fact dài hạn |
| Đã xét 278 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: `scripts/tdq_bench.py` in ISO timestamp + tên lệnh con +
  tham số ra stderr, tắt bằng `TDQ_LOG=0` — giống hệt `tdq_team.py`.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật. Riêng bài
  này thêm một luật cứng: **cấm bịa hằng số thời gian**. Thiếu file thực đo thì
  `mo-phong` phải báo lỗi và dừng, không được đặt giá trị mặc định cho có.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`.
- Mọi thứ đụng git chạy trong `tempfile.TemporaryDirectory()`. Cấm tạo nhánh hay worktree
  trong repo thật.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`, chỉ dòng việc này chạm):

- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — việc này chạm ở
  `scripts/tdq_bench.py`.
- "`tests/` gọi được vào mọi tầng; không tầng nào được import `tests/`" — chạm ở
  `tests/test_bench.py`.
- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`" — `tdq_bench.py` chỉ ĐỌC
  state, không ghi.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Lượt chạy thật quá nhỏ, hằng số nhiễu | điểm hoà lệch, kết luận sai | mỗi hằng số lấy ≥3 mẫu, ghi cả số mẫu lẫn độ tản vào file thực đo; kết luận nêu rõ khoảng tin, không nêu một con số trần trụi |
| Mô phỏng thiên vị mode đội (bỏ quên phí ẩn) | kết luận đẹp nhưng sai | công thức tính đủ 4 loại phí (`phat`, `kiem`, `hop`, `don`); QC có hạng mục riêng kiểm tay công thức trên ví dụ nhỏ |
| Agent con thất bại giữa lượt chạy thật | thiếu mẫu, kẹt worktree | đo cả ca hỏng và tính nó vào chất lượng; `don` chạy trong `finally` |
| Kết luận bị đọc thành "mode đội vô dụng" | user bỏ mất công cụ vừa build | kết luận BẮT BUỘC nêu điều kiện hai chiều: ngưỡng nào nên dùng đội, ngưỡng nào nên dùng main |
| Chạy thật tốn token ngoài dự tính | phình chi phí | giới hạn cứng: đúng 1 đợt, tối đa 3 agent con, mỗi agent một task nhỏ |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Test suite không đỏ | `python3 -m pytest tests/ -q` | pass, số test ≥ 839 |
| Q2 | Dựng plan mẫu đúng tham số | `tdq_bench.py dung-plan --task 12 --chong 0.25` | plan 12 task, số cặp chồng file khớp tham số, `doc_lint` exit 0 |
| Q3 | Plan mẫu chạy được với công cụ thật | `tdq_team.py phan-cong` + `kiem-ke` trên plan mẫu | exit 0, bản đồ đủ 12 bản ghi |
| Q4 | Công thức mô phỏng kiểm tay được | ví dụ 4 task, 2 đợt, số đặt sẵn | số máy in ra khớp số tính tay trong file QC |
| Q5 | Cấm bịa hằng số | chạy `mo-phong` khi chưa có file thực đo | báo lỗi rõ, exit khác 0, KHÔNG in bảng |
| Q6 | Lượt chạy thật có số thật | đọc `docs/tdq/bench/<slug>-thuc-do.json` | ≥3 hằng số, mỗi hằng số ≥3 mẫu, có ghi độ tản |
| Q7 | Quét ra được điểm hoà | `tdq_bench.py quet` | bảng có ít nhất một dòng đổi chiều thắng-thua, in rõ ngưỡng |
| Q8 | Chất lượng đo đủ 6 chỉ số | file kết quả | test pass · doc_lint · số lần merge xung đột · số task phải làm lại · số defect QC độc lập bắt · tỉ lệ giao/tổng — cả hai mode đều có số |
| Q9 | Repo thật không bị đụng | `git status --short`, `git worktree list`, `git branch --list "tdq/*"` trước/sau | giống hệt trước và sau, không nhánh `tdq/*` |
| Q10 | Log service | chạy 1 lệnh có và không `TDQ_LOG=0` | có timestamp ISO ở stderr; `TDQ_LOG=0` im hoàn toàn |
| Q11 | Kết luận trả lời đúng câu user hỏi | đọc mục `## Kết luận` | có câu "nhanh hơn: …" kèm điều kiện và "chất lượng: …" kèm số, không có câu chung chung |
| Q12 | Test biên: plan không tách được | plan 6 task cùng đụng 1 file | mô phỏng cho `T_đội ≥ T_main`, kết luận khuyến nghị mode `main` |
| Q13 | QC độc lập | agent `tdq-qc-tester` chạy lại Q1–Q12 | kết luận PASS kèm output thật, và soi riêng công thức có thiên vị không |

**DoD:** Q1–Q13 đều PASS · mọi task trong plan tick `[x]` · file kết quả trả lời được
hai câu của user bằng số kèm điều kiện · hằng số mô phỏng đều đến từ thực đo, không có
số nào đặt tay · repo thật không đổi một byte · script benchmark chạy lại được bằng một
lệnh cho hình dạng plan bất kỳ.

## 7. Câu hỏi còn mở

(rỗng)
