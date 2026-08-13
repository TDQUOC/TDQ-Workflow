# SPEC — Vòng scope: interview đi từ tổng quát đến chi tiết

Ngày: 2026-08-14 · Bản: 1.0 · Brief: ../brief/2026-08-14-interview-hoi-scope.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: thêm một **vòng scope** đứng TRƯỚC vòng câu hỏi chi tiết của interview. Vòng
  này hỏi request bao quanh những mặt nào và hỏi bối cảnh bằng số, để vòng chi tiết chỉ
  hỏi trong đúng phần user quan tâm và spec không thiếu cũng không dư.
- Trong phạm vi: luật vòng scope (file mới), sửa `interview.md`, `analyze-full.md`,
  `quick-lane.md`, `tdq-intake/SKILL.md`, `spec-template.md`, một dòng checklist trong
  `scripts/tdq_state.py`, test cho luật mới.
- NGOÀI phạm vi: thêm rule `doc_lint` kiểm mục "NGOÀI phạm vi" của spec (user đã loại ở
  câu 4); đổi khuôn option A/B/C hiện có; đụng gate duyệt, `edit_gate.py`, luật tick;
  đổi số phase hay số gate của workflow.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã xong) | 1 truy vấn lấy khung ISO 25010 làm bộ soát mặt |
| Interview | CÓ (đã xong) | 4 câu, user chốt 1c 2a 3a-sửa 4a |
| Chia subagent | BỎ | 1 nhóm file tài liệu liên quan chặt, chia dễ lệch giọng văn |
| QC độc lập (agent) | BỎ | mọi dòng DoD kiểm được bằng lệnh |
| Report | CÓ | khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Luật vòng scope | `skills/tdq-intake/references/scope-round.md` (mới) | file tồn tại, có đủ 5 mục dưới §3, `doc_lint` exit 0 |
| 2 | Interview hai tầng | `skills/tdq-intake/references/interview.md` | có mục "Hai tầng câu hỏi" + link `scope-round.md` |
| 3 | Bước 4 lane deep | `skills/tdq-intake/references/analyze-full.md` | bước 4 nêu vòng scope chạy trước vòng chi tiết |
| 4 | Bước 1 lane express | `skills/tdq-intake/references/quick-lane.md` | bảng so sánh có dòng "Vòng scope" |
| 5 | Nhắc ở skill chính | `skills/tdq-intake/SKILL.md` | Phần B và Phần C đều nhắc vòng scope; ≤ 120 dòng |
| 6 | Neo vào spec | `skills/tdq-spec/references/spec-template.md` | §1 buộc chép mặt bị loại vào "NGOÀI phạm vi" |
| 7 | Checklist phase `analyze` | `scripts/tdq_state.py` `PHASE_GUIDE["analyze"]` | `tdq_state.py next` in dòng vòng scope |
| 8 | Test | `tests/test_scope_round.py` (mới) | `pytest tests/test_scope_round.py -q` xanh |

## 3. Cách tiếp cận & lý do

Chọn: viết luật thành một file reference riêng rồi trỏ link từ 4 chỗ đang gọi interview.

Vì: `interview.md` đang bị 3 test khoá khuôn (`test_gate_merge`, `test_user_facing_block`,
`test_skill_shape`) và `tdq-intake/SKILL.md` chỉ còn 15 dòng dưới trần 120 — nhồi luật
mới vào đó sẽ vỡ trần y như lần `mode-gate.md`. Đã loại: viết thẳng vào `interview.md`.

Nội dung `scope-round.md` gồm đúng 5 mục:

1. **Khi nào chạy** — có điều kiện, áp cho cả hai lane. Chạy khi thoả ít nhất một dấu
   hiệu: yêu cầu gọi tên cả một hệ thống/tính năng chứ không trỏ vào một hành vi cụ thể;
   soát khung 9 mặt thấy từ 2 mặt trở lên có thể áp dụng mà yêu cầu không nói gì; có từ
   mở về quy mô hay chất lượng mà không kèm số; việc chạm dữ liệu người dùng, tiền, hoặc
   API công khai. Không dấu hiệu nào → BỎ, nhưng phải ghi vào brief đúng một dòng
   `Vòng scope: BỎ — <lý do>`. Bắt buộc ghi lý do chính là hàng rào chống bỏ tuỳ hứng.
2. **Câu 1 — mặt scope.** Soát NỘI BỘ khung 9 mặt ISO/IEC 25010 (chức năng, hiệu năng,
   tương thích, trải nghiệm, độ tin cậy, bảo mật, bảo trì, linh hoạt, an toàn), rồi trình
   ra chat 3–5 mặt hợp lĩnh vực, mỗi mặt một dòng theo khuôn option sẵn có, kèm hệ quả
   một dòng dạng "chọn mặt này thì spec sẽ có <mục gì>". Cho user chọn nhiều
   (trả lời "A, C, D"), luôn có một option "chỉ cần chạy được, bỏ các mặt còn lại".
3. **Câu 2 — bối cảnh bằng số.** 2–4 câu ngắn chọn theo lĩnh vực từ bộ mẫu: môi trường
   chạy và phiên bản target; quy mô đồng thời (CCU, RPS, số bản ghi); giai đoạn R&D hay
   product; vòng đời và ai bảo trì; ràng buộc nền tảng/thiết bị. Mỗi câu vẫn theo khuôn
   A/B/C với các mức số cụ thể, cộng một option "tôi tự gõ số". **Cấm** hỏi thẳng kiểu
   "bạn muốn gọn hay đầy đủ chuyên nghiệp".
4. **Suy ra mức đầu tư.** Bảng ánh xạ bối cảnh → mức: R&D/prototype, quy mô nhỏ, một
   người bảo trì → làm lõi, không tối ưu sớm, DoD gọn. Product, quy mô lớn hoặc chạm
   tiền/dữ liệu người dùng → mặt hiệu năng và độ tin cậy vào thẳng DoD, có hạng mục QC
   riêng. Agent phải in một dòng `Tôi hiểu là: <mức đầu tư> vì <bối cảnh>` để user cãi
   được, đặt kèm khối câu hỏi vòng chi tiết — không dựng thêm gate duyệt mới.
5. **Ghi lại.** Brief mục `## Hiểu & kiến thức` thêm `### Phạm vi đã chốt` gồm 4 dòng:
   mặt CHỌN, mặt LOẠI, bối cảnh (số), mức đầu tư suy ra. Spec §1 `NGOÀI phạm vi` phải
   chép lại các mặt LOẠI.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake / tdq-spec / tdq-plan / tdq-build | project | NỀN | khung workflow đang chạy, cũng là thứ bị sửa |
| mem0-memory | user | DÙNG | ghi 1 fact quy ước vòng scope, task riêng trong plan |
| graphify | user | DÙNG | chạy cuối turn vì có sửa `scripts/tdq_state.py` |
| Đã xét 62 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service: GIỮ NGUYÊN. Việc này chỉ sửa một chuỗi checklist trong `tdq_state.py`,
  không thêm runtime mới; QC có một hạng mục kiểm `_warn` vẫn in timestamp và `TDQ_LOG=0`
  vẫn tắt được.
- Không placeholder, không TODO stub trong file luật mới — mọi mục phải có nội dung thật.
- Mỗi thay đổi có test riêng, chạy được bằng một lệnh.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| "Có điều kiện" thành tuỳ hứng, agent bỏ vòng scope cho nhanh | Đúng lại vấn đề user muốn sửa | Dấu hiệu kích hoạt viết thành danh sách đóng; BỎ thì bắt buộc ghi một dòng lý do vào brief |
| Vòng scope làm interview dài thêm, user mệt | Chậm mở request | Trần cứng: câu 1 tối đa 5 mặt, câu 2 tối đa 4 câu, gộp chung MỘT khối chat |
| `tdq-intake/SKILL.md` vượt trần 120 dòng | `doc_lint` exit 1, chặn turn | Luật nằm ở file reference; SKILL.md chỉ thêm tối đa 4 dòng; QC đo `wc -l` |
| Khuôn mới phá test khuôn đang khoá `interview.md` | Full suite đỏ | Chạy `test_gate_merge`, `test_user_facing_block`, `test_skill_shape` ngay sau mỗi lần sửa |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | File luật có mặt, đủ 5 mục | `grep -c "^## " skills/tdq-intake/references/scope-round.md` | ≥ 5 |
| Q2 | Có danh sách dấu hiệu kích hoạt và luật ghi lý do khi BỎ | `grep -c "Vòng scope: BỎ" scope-round.md` | ≥ 1 |
| Q3 | Cấm hỏi "gọn hay đầy đủ", có câu bối cảnh bằng số | `grep -c "CCU" scope-round.md` | ≥ 1 |
| Q4 | `interview.md` có tầng tổng quát + link file mới | `grep -c "scope-round.md" skills/tdq-intake/references/interview.md` | ≥ 1 |
| Q5 | `analyze-full.md` và `quick-lane.md` đều trỏ vòng scope | `grep -l "scope-round" ...` | ra đủ 2 file |
| Q6 | `SKILL.md` nhắc vòng scope và chưa vượt trần | `grep -c "vòng scope" SKILL.md` ≥ 1 và `wc -l` ≤ 120 | cả hai đúng |
| Q7 | `spec-template.md` buộc chép mặt bị loại | `grep -c "mặt bị loại" spec-template.md` | ≥ 1 |
| Q8 | Checklist phase `analyze` in dòng vòng scope | `python3 scripts/tdq_state.py next` ở phase `analyze` | output chứa "scope" |
| Q9 | Log service còn nguyên | gọi `_warn` mặc định, rồi `TDQ_LOG=0` | 1 dòng có timestamp / 0 dòng |
| Q10 | Full suite | `python3 -m pytest tests/ -q` | không có `failed`, số test ≥ 552 |
| Q11 | Lint tài liệu | `python3 scripts/doc_lint.py <các file .md đã sửa>` | exit 0 |

DoD: 11 hạng mục trên PASS hết, mọi task trong plan tick `[x]`, có file
`docs/tdq/qc/2026-08-14-interview-hoi-scope.md` kèm bằng chứng thật.

## 7. Câu hỏi còn mở

(Rỗng.)
