# QC — kiểm chất lượng

QC là chạy thật và dán bằng chứng. Không có "chắc là ổn".

## Chạy cái gì

1. **Toàn bộ test suite** bằng đúng lệnh ghi trong plan. Dán số test pass/fail thật.
   Suite dài → chạy chế độ tóm tắt, đừng dán log dài vào chat: thêm cờ `-q` (hoặc dot
   reporter của framework), hoặc redirect ra file rồi lọc phần fail:
   `<lệnh test> > /tmp/qc-run.log 2>&1; tail -n 40 /tmp/qc-run.log` hay
   `grep -iE "fail|error" /tmp/qc-run.log`. Chỉ dán nguyên văn khi có FAIL cần bằng chứng.
2. **Từng hạng mục QC trong spec §6** — theo đúng lệnh và điều kiện PASS đã ghi.
3. **Biên & đường lỗi**: input rỗng, input sai kiểu, file thiếu, quyền bị chặn, mạng hỏng.
   Sản phẩm phải báo lỗi rõ ràng, không stack trace trần cho người dùng cuối.
4. **Log service**: bật mặc định chưa, có timestamp chưa, có đủ chi tiết debug chưa,
   tắt/giảm mức được qua config chưa.
5. **Không placeholder**: grep repo tìm `TODO`, `FIXME`, dữ liệu mock còn sót được trình
   bày như thật.
6. **Hợp đồng skill được thi hành thật**: với TỪNG khối `Dùng:` trong plan, chạy lệnh ở
   trường `Kiểm`; artifact ở trường `Ra` phải tồn tại. Không có artifact → sửa spec §3b
   dòng đó thành `KHÔNG` + lý do đóng, rồi chạy lại
   `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/doc_lint.py" --pair <spec> <plan>` đến khi exit 0.
   Sửa spec ở đây làm sha256 lệch → hook sẽ đòi duyệt lại: trình user đúng 1 dòng diff
   và xin duyệt lại spec (`approve spec`) ngay trong lượt QC, không để treo cảnh báo.

## Ghi kết quả

`docs/tdq/qc/<slug>.md`:

```markdown
# QC — <tên việc>
Ngày: YYYY-MM-DD · Plan: ../plan/<slug>.md · Vòng: 1

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | | | | |

## Bằng chứng
### Q1
```
<output thật, cắt gọn phần dài>
```

## Kết luận
<PASS toàn bộ | FAIL: liệt kê hạng mục fail và task fix đã thêm vào plan>
```

## Khi FAIL

1. Thêm task fix vào **plan đã duyệt**, mục `## QC vòng N — fix`:
   `- [ ] **QCn.1** <việc> — Test: <check>`. Không cần user duyệt lại.
2. Làm theo luật implement: red → green, tick `[x]` ngay.
3. Chạy lại **toàn bộ** QC (không chỉ hạng mục vừa fix) — fix hay gây hồi quy chỗ khác.
4. Lặp đến khi mọi hạng mục PASS.

Chỉ hỏi user khi bản fix đòi đổi phạm vi so với spec đã duyệt.
