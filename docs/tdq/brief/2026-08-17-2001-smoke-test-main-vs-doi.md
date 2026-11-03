# BRIEF — Smoke test so mode main và mode đội (subagent)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> hãy giả lập smoke test main và sub agent và thử giúp tôi ở cuối cái nào nahnh hơn và
> chất lượng cao hơn

**Cách hiểu đầu tiên.** Mode đội vừa build xong ở request `2026-08-17-1828-subagent-team-implement`
mới chỉ được kiểm bằng unit test trên plan mẫu — chưa có lần chạy thật nào. User muốn một
smoke test: lấy cùng một khối lượng công việc, chạy hai lần (một lần mode `main`, một lần
mode `subagent`), rồi kết luận bằng SỐ: bên nào nhanh hơn, bên nào chất lượng cao hơn.

**Mục tiêu.** Trả lời được hai câu, kèm bằng chứng đo được, không phải cảm nhận:
1. Nhanh hơn: đo bằng gì (treo tường, thời gian model, số lượt gọi tool)?
2. Chất lượng cao hơn: đo bằng gì (test pass, doc_lint, số defect QC độc lập bắt được,
   số lần merge xung đột)?

**Phạm vi đoán (chờ user xác nhận).**
- Chạy trên một plan mẫu dựng riêng trong repo tạm, KHÔNG đụng repo thật.
- Cùng một plan, hai lần chạy độc lập, so kết quả cuối.
- Kết quả ra một file so sánh, có bảng số.

**Chỗ chưa rõ.**
- Khối lượng công việc dùng làm bài thi: plan mẫu tổng hợp, hay một việc thật trong repo?
- "Giả lập" nghĩa là mô phỏng bằng script (đo cơ học, không gọi model thật) hay chạy thật
  agent con (tốn token, số thật hơn)?
- Có được tạo nhánh/worktree trong repo thật không, hay bắt buộc dùng repo tạm?

## Hiểu & kiến thức

### Năng lực dùng được

| Skill | Nguồn | Phán quyết | Vì sao |
|---|---|---|---|
| `tdq-intake` | plugin:tdq-workflow | DÙNG | đang chạy chính nó |
| `tdq-spec` / `tdq-plan` / `tdq-build` | plugin:tdq-workflow | DÙNG | lane full, đủ 3 cổng |
| `tdq-conventions` | plugin:tdq-workflow | DÙNG | luật chung, mọi phase nạp |
| `tdq-status` | plugin:tdq-workflow | BỎ | không phải câu hỏi trạng thái |
| `superpowers:brainstorming` | built-in | BỎ | yêu cầu đã rõ hình dạng, chỉ thiếu vài tham số |
| `mem0-memory` | plugin | DÙNG | kết quả benchmark là fact đáng nhớ dài hạn |
| Agent `tdq-implementer` | plugin:tdq-workflow | TÙY chọn user | chỉ dùng nếu user chọn chạy agent thật |
| Agent `tdq-qc-tester` | plugin:tdq-workflow | DÙNG | chấm chất lượng độc lập, không tin lời khai |

### Đọc code — cái đã có sẵn

- `scripts/tdq_team.py` (654 dòng): `phan-cong` · `kiem-ke` · `cum` · `mo` · `kiem` ·
  `hop` · `don`. Log service in ISO timestamp ra stderr, tắt bằng `TDQ_LOG=0`.
- `scripts/tdq_timing.py show`: đã đo sẵn **treo tường** và **thời gian model** theo từng
  phase, đọc từ transcript. Đây là thước đo tốc độ có sẵn, không phải dựng mới.
- `docs/tdq/timing.jsonl`: số liệu lịch sử của các request đã đóng — có thể dùng làm mốc
  so sánh cho mode `main`, vì mọi request trước nay đều chạy `main`.
- `scripts/doc_lint.py`, `tests/` (839 test): thước đo chất lượng có sẵn.

### Ẩn số bên ngoài

Research: **BỎ** — việc thuần nội bộ, mọi thứ cần đo đều nằm trong repo này và trong
transcript của chính phiên làm việc. Không có API, thư viện hay chuẩn ngoài nào cần tra.

### Phạm vi đã chốt

- Mặt CHỌN: tốc độ + độ tin cậy · chức năng (mode đội chạy thật end-to-end) · bảo trì
  (script benchmark dùng lại được)
- Mặt LOẠI: bảo mật · tương thích đa nền tảng · trải nghiệm người dùng · an toàn dữ liệu
- Bối cảnh: bài thi là plan mẫu dựng trong repo git tạm · chỉ chạy thật một lượt nhỏ để
  hiệu chỉnh · repo thật không được đụng một byte
- Mức đầu tư suy ra: **vừa** — R&D nội bộ, một người giữ, nhưng có ba mặt phải đo nên DoD
  cần cả test biên (plan không chia được đợt) lẫn đường lỗi (agent con chết giữa chừng)

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | thuần nội bộ, không có ẩn số ngoài repo |
| Interview | CÓ (xong) | 4 câu, user đã chốt: 1ABC · 2A · 3A · 4A |
| Vòng scope | CÓ (xong) | yêu cầu có từ mở "nhanh hơn"/"chất lượng cao hơn" không kèm số |
| Spec + plan | CÓ | lane full, hai cổng duyệt |
| QC độc lập (agent) | CÓ | chính bài này chấm điểm chất lượng — tự chấm là mất giá trị |
| Chạy agent thật | CÓ, một lượt nhỏ | hiệu chỉnh mô phỏng; không có nó thì số chỉ là mô hình |

## Hỏi đáp

**Q1. Bài thi bao quanh những mặt nào?** → **A + B + C**: tốc độ/độ tin cậy, chức năng
(mode đội chạy thật), bảo trì (script benchmark tái sử dụng). Loại mặt bảo mật, tương
thích, trải nghiệm, an toàn.

**Q2. "Giả lập" nghĩa là gì?** → **A — lai**: mô phỏng cơ học phần chia đợt/merge bằng
script để chạy được nhiều hình dạng plan, rồi chạy THẬT một lượt nhỏ để lấy hằng số thời
gian thật. Hệ quả: con số mô phỏng phải được hiệu chỉnh bằng số thực đo, không được bịa
hằng số.

**Q3. Khối lượng công việc lấy từ đâu?** → **A**: plan mẫu tổng hợp dựng trong repo git
tạm. Lý do user không chọn việc thật: chạy hai lần thì lần sau đã biết đáp án, bài thi
mất công bằng.

**Q4. Được đụng repo thật tới đâu?** → **A**: chỉ repo tạm, mọi nhánh và worktree nằm
trong `tempfile.TemporaryDirectory()`. Repo thật không đổi một byte.
