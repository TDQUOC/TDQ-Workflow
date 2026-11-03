# SPEC — Rà soát mức quốc tế hoá của bộ workflow TDQ (cổng duyệt không bám một ngôn ngữ)

Ngày: 2026-08-21 · Bản: 1.1 · Brief: ../brief/2026-08-21-2311-workflow-da-ngon-ngu.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- Mục tiêu: trả lời bằng bằng chứng câu hỏi "bộ workflow này đã quốc tế hoá chưa" trên 4 mặt
  (cổng duyệt · khuôn khối in cho user · luật ngôn ngữ output · lưới test giữ tương thích
  ngược), mỗi mặt một phán quyết ĐẠT/CHƯA kèm `file:dòng`, và kèm thiết kế đề xuất cho
  request sửa sau. Đo được: mọi mã kiểm K1–K12 ở §6 đều có phán quyết và bằng chứng trích
  từ file thật.
- Trong phạm vi: đọc và chấm `hooks/scripts/`, `scripts/tdq_state.py`, các skill `tdq-*`,
  `tests/`; viết một tài liệu rà soát; đề xuất thiết kế (không thi hành).
- NGOÀI phạm vi (user chọn `2b` — chỉ check):
  - Sửa regex nhận duyệt, sửa hook, sửa `tdq_state.py`.
  - Sửa khuôn `➤ Duyệt:` trong bất kỳ file skill nào.
  - Đổi luật "Mọi output cho user: tiếng Việt".
  - Thêm/sửa test, thêm script quét tự động.
  - Dịch tài liệu sang ngôn ngữ khác.
  - Mặt E ở vòng scope ("chỉ cần chạy được") bị loại: user chọn đủ 4 mặt A–D.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Thuần nội bộ repo, không có ẩn số ngoài; phiên này cũng cấm gọi sub-agent khi user chưa yêu cầu |
| Interview | CÓ (đã xong) | Vòng scope + 5 câu, đã chốt ở brief `### Vòng 1` |
| Spec | CÓ | Chốt tiêu chí chấm TRƯỚC khi chấm, tránh chấm theo cảm tính |
| Plan | CÓ | Mỗi mặt A–D một nhóm task, mỗi task một bằng chứng |
| Implement | CÓ (dạng rà soát) | Việc thi hành là đọc code + ghi bằng chứng, không sửa file luật |
| QC độc lập (agent) | BỎ | Không đổi hành vi phần mềm; QC = kiểm lại từng `file:dòng` có thật bằng `sed -n` |
| Vòng phản chứng (validate lại) | CÓ | User bổ sung: chấm xong phải tự kiểm lại cho chắc rồi mới báo cáo — mỗi mã K1–K12 bị thử phản bác trước khi được ghi vào báo cáo |
| Full test suite | CÓ, 1 lần | Bằng chứng request này không đụng code: suite phải y hệt trước khi làm |
| Report | CÓ | Khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Tài liệu rà soát 4 mặt, mỗi mã kiểm một dòng: mã · điều đang kiểm · bằng chứng `file:dòng` · ĐẠT/CHƯA · dòng `Phản chứng:` | `docs/tdq/audit/da-ngon-ngu.md` | 12/12 mã K1–K12 có phán quyết, có bằng chứng trích được bằng `sed -n`, và có dòng `Phản chứng:` |
| 2 | Mục `## Đề xuất cho request sửa sau` trong cùng file: thiết kế cổng duyệt không bám ngôn ngữ, kèm danh sách file phải sửa và rủi ro tương thích ngược | `docs/tdq/audit/da-ngon-ngu.md` | Mỗi mã CHƯA ĐẠT có đúng một đề xuất trỏ tới nó |
| 3 | Bảng "chỗ nào đang khoá cứng tiếng Việt": liệt kê đủ các chuỗi tiếng Việt nằm trên ĐƯỜNG DUY NHẤT để qua cổng | `docs/tdq/audit/da-ngon-ngu.md` mục `## Điểm khoá cứng` | Mỗi dòng có `file:dòng` và nói rõ nếu xoá chuỗi đó thì cổng gãy ở đâu |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| M1 cổng máy | `hooks/scripts/`, `scripts/tdq_state.py` | không | 1, 3 |
| M2 khuôn in cho user | `skills/tdq-spec/`, `skills/tdq-plan/`, `skills/tdq-intake/`, `skills/tdq-status/`, `skills/tdq-build/` | M1 | 1, 3 |
| M3 luật ngôn ngữ nền | `skills/tdq-conventions/` | không | 1, 3 |
| M4 lưới tương thích ngược | `tests/`, `evals/` | M1, M2, M3 | 1, 2 |

## 3. Cách tiếp cận & lý do

- Chọn: rà theo **mã kiểm cố định K1–K12 viết trước khi đọc code**, mỗi mã một câu hỏi
  đóng có thể trả lời bằng một đoạn trích file.
- Chọn: **hai lượt — chấm rồi phản chứng.** Lượt 1 chấm và ghi bằng chứng. Lượt 2 (bắt buộc,
  chạy sau khi lượt 1 xong toàn bộ) đi ngược từng mã và cố PHẢN BÁC phán quyết của chính
  mình: mã ĐẠT thì tìm một đường vào làm nó gãy, mã CHƯA ĐẠT thì tìm một đường khác trong
  repo khiến nó vẫn chạy được. Mã nào đổi phán quyết sau lượt 2 thì ghi cả hai lượt và nói
  rõ vì sao đổi. Chỉ sau lượt 2 mới được viết report.
- Vì: đây là câu hỏi "đã đạt chưa", nên rủi ro lớn nhất là chấm theo cảm giác, và sai lệch
  hay đến từ chỗ chỉ nhìn một đường vào. Lượt phản chứng là cái bắt lỗi đó.
- Vì: chốt mã kiểm trong spec (spec bị niêm sha256 khi duyệt) làm tiêu chí không đổi được
  sau khi đã thấy kết quả.
- Đã loại: viết script quét tự động — vì user chốt `2b` (chỉ check), script là code mới, thuộc
  request sửa sau; đề xuất nó ở đầu ra §2 mục 2.
- Đã loại: sửa luôn cổng cho nhanh — user nói rõ sửa để request sau.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | Skill khung đang chạy (analyze) |
| tdq-spec | plugin:tdq-workflow | NỀN | Skill khung viết file này |
| tdq-plan | plugin:tdq-workflow | DÙNG | Viết plan cho 4 module |
| tdq-build | plugin:tdq-workflow | DÙNG | Thi hành rà soát + QC + report |
| tdq-conventions | plugin:tdq-workflow | DÙNG | Là đối tượng chấm ở M3, đồng thời cấp luật khối cuối turn |
| tdq-status | plugin:tdq-workflow | DÙNG | Đối tượng chấm ở M2 (SKILL.md:42 in dòng `➤ Duyệt:`) |
| Đã xét 280 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service: BỎ — request này không tạo/sửa file mã nguồn chạy được, đầu ra là tài liệu.
- Không placeholder: mọi ô bằng chứng phải là trích dẫn thật, cấm ghi "đang kiểm"/"TBD".
- Mỗi mặt A–D có ít nhất 2 mã kiểm, không mặt nào chỉ chấm bằng một quan sát.
- Không báo cáo phán quyết nào chưa qua lượt phản chứng.
- Mọi con số/đường dẫn trong tài liệu lấy từ output lệnh thật, không ước lượng.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`, chỉ dòng việc này chạm tới):

- "`skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill" —
  việc này chạm ở chỗ so khuôn `➤ Duyệt:` giữa `skills/*` và `scripts/tdq_state.py`.
- "hook chỉ nhắc và kiểm bằng hiệu ứng thật, không trả `deny` vì lý do 'chưa duyệt'"
  (đã chốt 2026-07-29) — việc này chạm ở `hooks/scripts/bash_gate.py`, `stop_gate.py`.
- "bỏ hẳn skill duyệt, duyệt bằng chat thường" (đã chốt 2026-07-29) — mọi đề xuất phải giữ
  đường duyệt bằng chat, không được đẻ lại skill duyệt.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Chấm rộng tay: coi "có regex tiếng Anh" là đã quốc tế hoá | Kết luận sai, request sửa sau làm hụt | K1–K12 hỏi "có ĐƯỜNG NÀO không cần từ tiếng Việt/Anh không", không hỏi "có tiếng Anh chưa" |
| Rà sót chỗ khoá cứng nằm ngoài 4 module | Đề xuất thiếu file, sửa sau vẫn gãy | Mỗi module kết bằng một lượt grep toàn repo cho chuỗi đặc trưng của module đó |
| Trôi việc sang sửa luôn | Vi phạm phạm vi user đã chốt | Task nào định sửa file trong `hooks/`, `scripts/`, `skills/`, `tests/` là dừng — chỉ file trong `docs/tdq/` được ghi |
| Bằng chứng lệch số dòng do file đổi giữa chừng | Tài liệu trỏ sai | Chốt HEAD lúc bắt đầu, ghi commit id vào đầu tài liệu |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | 12 mã kiểm K1–K12 đều có phán quyết ĐẠT/CHƯA | Không mã nào bỏ trống, không mã nào ghi "chưa rõ" |
| Q2 | Mỗi bằng chứng `file:dòng` trích lại được | Trích ngẫu nhiên 5 dòng bất kỳ, nội dung khớp tài liệu |
| Q3 | Mỗi mã CHƯA ĐẠT có đúng một đề xuất | Đếm số mã CHƯA = số đề xuất trỏ tới |
| Q4 | Đề xuất giữ tương thích ngược | Mỗi đề xuất nói rõ câu duyệt tiếng Việt cũ vẫn qua cổng, và nêu test cũ nào phải vẫn xanh |
| Q5 | Không sửa file ngoài `docs/tdq/` | `git status --short` chỉ hiện đường dẫn trong `docs/tdq/` (ngoài các file đã bẩn sẵn từ trước, liệt kê ở report) |
| Q6 | Full test suite y hệt trước khi làm | Số pass/fail bằng đúng số chụp lúc bắt đầu |
| Q7 | Lượt phản chứng đã chạy đủ 12 mã | Mỗi mã có dòng `Phản chứng:` ghi thứ đã thử và kết quả; mã đổi phán quyết có ghi lý do đổi |
| Q8 | `doc_lint` sạch cho spec/plan/audit/report | Lệnh lint exit 0 |

**Các mã kiểm (chốt trước khi đọc kết quả):**

| Mã | Mặt | Câu hỏi đóng |
|---|---|---|
| K1 | A cổng duyệt | Cổng `spec` có nhận được câu trả lời chỉ gồm một chữ cái không? |
| K2 | A | Cổng `plan` có nhận được chữ cái không? |
| K3 | A | Cổng `quick` có nhận được chữ cái không? |
| K4 | A | Có tồn tại đường qua cổng nào KHÔNG cần một từ tiếng Việt hay tiếng Anh cụ thể không? |
| K5 | A | `bash_gate` chặn `approve` có dùng cùng một hàm nhận diện với `prompt_context` không (sửa một chỗ là cả hai theo)? |
| K6 | B khuôn in cho user | Khuôn `➤ Duyệt:` có mời user trả lời bằng chữ cái không? |
| K7 | B | Số file luật đang chép tay khuôn `➤ Duyệt:` là bao nhiêu, có nguồn duy nhất không? |
| K8 | C ngôn ngữ output | Có luật nào cho phép trả lời theo ngôn ngữ user đang nhắn không? |
| K9 | C | Luật "Mọi output cho user: tiếng Việt" xuất hiện ở bao nhiêu file, có phải luật cứng không? |
| K10 | D lưới an toàn | Bao nhiêu file test khoá chuỗi tiếng Việt của cổng duyệt? |
| K11 | D | Có test nào khẳng định "câu duyệt cũ vẫn qua cổng" đủ dùng làm lưới tương thích ngược không? |
| K12 | D | Bộ ca `evals/tuan-thu/` có ca nào chấm hành vi cổng duyệt bằng ngôn ngữ khác không? |

DoD: file `docs/tdq/audit/da-ngon-ngu.md` tồn tại với đủ 3 đầu ra §2 · Q1–Q8 PASS · plan tick
đủ · report đã viết và user đã được hỏi về commit.

## 7. Câu hỏi còn mở

(rỗng)
