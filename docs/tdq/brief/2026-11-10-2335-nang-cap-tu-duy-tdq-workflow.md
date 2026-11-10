# Brief: Nâng cấp tư duy sâu và chất lượng TDQ Workflow

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

- **Lời người dùng:**
  - "hãy mở request xử lí tdq-workflow đẻ có tư duy sâu hơn, hiieuej quả hơn vì tôi không đánh đổi tốc độ để lấy low quality"
  - "1 nhắc nếu đọc đi đọc lại 1 đoaạn, còn nếu file dài thì cần đọc nhiều lần để có thể lấy thông tin chứ đúng ko?"
  - "1a 2a và remind AI nha 3C"
- **Mục tiêu:** Nâng cấp toàn diện cơ chế tư duy của TDQ Workflow:
  1. Vá `read_gate.py` với thuật toán Range Overlap (độ phủ ≥ 70%), phân biệt đọc file dài khám phá (cho phép) với đọc lặp lại 1 đoạn (bẫy lặp).
  2. Bổ sung cơ chế "Remind AI" trực diện qua hook nhắc nhở khi phát hiện dấu hiệu lặp, bẻ gãy vòng lặp tự hồi quy (autoregressive loop).
  3. Củng cố Soul và các skill phân tích với nguyên tắc "Reflective Thought & Hypothesis" (tư duy phản tư trước & sau khi đọc mã nguồn, đọc dải đủ rộng trọn vẹn thay vì xé vụn).
  4. Mức QC: `ultra` (DoD + unit test + smoke test + runtime test + independent QC agent).

## Hiểu & kiến thức

### Năng lực dùng được

| Skill / Công cụ | Nguồn | Quyết định | Lý do |
|---|---|---|---|
| `tdq-spec` | plugin:tdq-workflow | DÙNG | Soạn spec chi tiết các luồng kiểm soát |
| `tdq-plan` | plugin:tdq-workflow | DÙNG | Lập kế hoạch các task triển khai và test |
| `tdq-build` | plugin:tdq-workflow | DÙNG | Chạy build, test và QC mức ultra |
| `read_gate.py` | hooks/scripts | DÙNG | Mã nguồn chính cần vá thuật toán range overlap và cơ chế nhắc nhở AI |
| `tests/test_read_gate.py` | tests/ | DÙNG | Test suite kiểm chứng range overlap |

### Các quyết định kỹ thuật đã chốt

1. **Thuật toán Range Overlap trong `read_gate.py`:**
   - Lưu trữ lịch sử các dải đã đọc `[start, end]` của từng file trong session.
   - Khi có lượt đọc mới có `offset/limit`:
     - Nếu `(end - start) > 0`: tính tỉ lệ trùng lặp với từng dải đã đọc trước đó:
       `overlap = max(0, min(end, prev_end) - max(start, prev_start))`
       `overlap_ratio = overlap / (end - start)`
     - Nếu `overlap_ratio >= 0.7`: tăng bộ đếm số lần đọc lặp cho đoạn này (`repeat_count`).
     - Khi `repeat_count >= 2` (tức đọc lần 3 cùng một đoạn): Hook phát sinh `additionalContext` nhắc nhở rõ ràng: `[TDQ:DOC] Cảnh báo: Đoạn dòng {start}-{end} trong '{file}' đã được đọc {N} lần. Nội dung đoạn này đã có trong ngữ cảnh. Hãy dừng đọc lặp, tổng hợp thông tin và chuyển bước phân tích/lập kế hoạch.`
     - Nếu `repeat_count >= 5`: Cảnh báo khẩn cấp (hoặc chặn nếu host hỗ trợ) để bẻ gãy bẫy lặp.
   - Nếu đọc các đoạn mới của file dài (`overlap_ratio < 0.3`): Hook giữ im lặng hoàn toàn, cho phép đọc nhiều phân đoạn để khám phá file lớn.

2. **Cơ chế "Remind AI" và Ép tư duy phản tư (Reflective Thought):**
   - Bổ sung quy chuẩn vào Soul: Bắt buộc tự phản tư sau mỗi lần khảo sát mã nguồn. Cấm xé nhỏ thành các lượt đọc 40 dòng vụn vặt gây bẫy lặp attention.
   - Khi khảo sát file lớn, khuyến khích đọc một lần đủ rộng (150–300 dòng) bao quát logic thay vì trượt cửa sổ vi mô.

3. **Tam Giác Khảo Sát 3 Chiều đối chiếu vùng chạm:**

| Vùng file chạm | Phát hiện qua lớp nào | Tác động & quan hệ |
|---|---|---|
| `hooks/scripts/read_gate.py` | Grep / Đọc trực tiếp | Bổ sung thuật toán range overlap, đếm lượt lặp theo đoạn, phát cảnh báo nhắc AI |
| `tests/test_read_gate.py` | Test suite | Bổ sung các unit test kiểm thử: đọc nhiều đoạn file dài (im), đọc lặp 1 đoạn ≥ 2 lần (nhắc), nhắc nhở mang số liệu |
| `skills/tdq-conventions/references/soul.md` | Grep | Bổ sung quy chuẩn "Reflective Thought", cấm đọc vụn vặt, chất lượng > tốc độ |
| `skills/tdq-intake/references/quick-lane.md` | Read | Hướng dẫn đọc dải rộng trọn vẹn trong phase quick_analyze |

### Lộ trình

| Bước / Phase | CÓ-BỎ | Vì sao |
|---|---|---|
| `spec` | CÓ | Soạn spec kỹ thuật chi tiết theo chuẩn Soul |
| `plan` | CÓ | Lập kế hoạch phân tách task theo TDD |
| `implement` | CÓ | Cập nhật `read_gate.py`, test suite và tài liệu |
| `qc` (ultra) | CÓ | Chạy test suite `test_read_gate.py`, smoke test, và kiểm chứng độc lập |
| `report` | CÓ | Xuất báo cáo Markdown + Archify HTML 4 phần |

## Hỏi đáp

- Người dùng đã chốt:
  1. `1a`: Thuật toán Range Overlap ≥ 70%, cho phép đọc nhiều đoạn khác nhau của file dài, chỉ cảnh báo khi đọc lặp lại cùng một đoạn ≥ 2 lần.
  2. `2a`: Toàn diện — vá `read_gate.py` và bổ sung cơ chế nhắc nhở AI ("remind AI nha") trong quy chuẩn.
  3. `3c`: Mức QC `ultra`.
