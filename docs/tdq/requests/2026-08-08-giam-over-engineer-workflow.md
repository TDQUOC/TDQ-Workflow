# Request: giảm over-engineer & over-test cho bộ workflow

Ngày: 2026-08-08 · Lane: (chờ user chốt)

## Nguyên văn

```text
okay hãy phân tích và lên cho tôi một spec hoàn chỉnh đẻ fix những vân dề bạn đưa ra
để bộ workflow không bị over engineeer vô tích và không bị over test khi áp dụng chạy
runtime
```

Bối cảnh: 2 turn trước đã phân tích read-only toàn bộ sản phẩm TDQ 0.9.0 (không dùng
workflow). Request này là bước tiếp: biến các phát hiện đó thành spec sửa chữa.

## Hiểu ban đầu

Mục tiêu: bộ workflow **nhẹ khi chạy thật**. Cụ thể: ít token nạp mỗi vòng, ít luật
phải tuân, ít file sinh ra mỗi request, ít test vô nghĩa. Ràng buộc: KHÔNG mất các rào
an toàn đang có giá trị (gate duyệt, hook nhắc, state ghi qua CLI).

Các vấn đề đã đo được ở turn phân tích, dự kiến vào phạm vi:

1. **Context nạp mỗi vòng full ≈ 12.022 token** chỉ riêng file skill (48.091 byte),
   chưa kể external/deep-search (+16 KB). `tdq-conventions/SKILL.md` là file nặng nhất
   (7.345 byte) và được nạp ở MỌI phase.
2. **Mật độ luật quá dày**: 168 từ mệnh lệnh tuyệt đối trong `skills/`, riêng
   `tdq-conventions/SKILL.md` là 44 luật / 120 dòng (1 mệnh lệnh mỗi 2,7 dòng).
3. **Hai bản shipped mâu thuẫn nhau**: `skills/.../quick-lane.md` nói task `(mcp)` là
   hard-block không override; `portable/.../quick-lane.md` nói user đòi thì làm theo
   user. 9/10 file reference của `portable/` đã lệch khỏi bản `skills/`.
   `tests/test_portable_sync.py` chỉ so bước đánh số của 4 SKILL.md, không phủ
   `references/` → lỗ hổng để lọt.
4. **Output mỗi request nặng hơn sản phẩm**: 1 request full sinh 7 file / 417 dòng /
   37,6 KB tài liệu để giao 617 dòng / 26,8 KB code (1,4×). Nặng nhất ở spec (12,4 KB,
   viết sớm nhất) và nhẹ nhất ở report (1,9 KB, viết lúc biết nhiều nhất).
   `requests` + `knowledge` + `questions` chồng lấn nội dung.
5. **Test lệch trọng tâm**: 156 test / 746 dòng hook (1 test mỗi 4,8 dòng) trong khi
   hook chỉ có ĐÚNG MỘT điểm chặn; 72 test chỉ assert chuỗi tiếng Việt trong .md
   (không kiểm hành vi nào); 42% test (257/618) phục vụ nửa tuỳ chọn
   (external/deep-search/export). Suite hiện ĐỎ 1 test vì đọc ra `$HOME`.
6. **`doc_lint` R5 áp sai chỗ, và cửa thoát `allow` hỏng với R5.** Phát hiện khi chạy
   chính turn intake này, không phải suy đoán.
   - `tdq_finish.py` lint file request, R5 chặn vì khối trích NGUYÊN VĂN câu user dài
     42 từ. Luật viết-ngắn dành cho doc hướng dẫn bị áp lên đoạn không được phép sửa.
   - Cửa thoát chuẩn `<!-- doc-lint: allow R5 -->` HỎNG. `rule_r5` gom các dòng liền
     nhau thành một buffer nên dòng comment bị nuốt vào đoạn.
   - Hệ quả: `state["start"]` trỏ vào comment, `allowed()` soi lên dòng TRÊN comment và
     không thấy gì. Lỗi nặng thêm: 42 → 47 từ.
   - Phải lách bằng cách bọc trích dẫn trong code fence.
   - Vị trí: `scripts/doc_lint.py` `rule_r5` (dòng 162-179), `allowed` (dòng 69-73).

7. **Lane quick không còn quick**: QC 3 hạng mục mặc định bật + vòng fix bắt buộc kể cả
   khi user tắt QC + trần 3 vòng + chạy lại đủ 3 hạng mục mỗi vòng.

## Chỗ chưa rõ (cần interview)

- Ngưỡng chấp nhận: "nhẹ" là bao nhiêu? Có mục tiêu số cụ thể cho token/vòng và số test
  không, hay để tôi đề xuất?
- Nửa tuỳ chọn (external engine, deep-search, claude-export, token-audit, plugin-tiers,
  skill-inventory): giữ nguyên nhưng nạp lười, hay có cái muốn bỏ hẳn khỏi sản phẩm?
- `portable/`: còn dùng thật với agent ngoài không? Nếu không, bỏ hẳn rẻ hơn nhiều so
  với sinh tự động + test đồng bộ.
- Cắt file output mỗi request (gộp requests/knowledge/questions) — có chấp nhận mất
  dấu vết tách bạch hiện tại không?
- Sửa bộ test: được phép XOÁ test, hay chỉ được chuyển sang lint/script chạy tay?
