# QC — kiểm chất lượng

QC là chạy thật và dán bằng chứng. Không có "chắc là ổn".

## Ba bước thi hành

Đây là toàn bộ Phần B của [SKILL.md](../SKILL.md) — chuyển về đây để thân skill không phải
nạp nhánh này mỗi lần gọi. Vào phase `qc` là **bắt buộc** đọc hết ba bước dưới đây trước
khi chạy hạng mục đầu tiên; cấm làm theo trí nhớ.

4. **Số hạng mục QC = số dòng Definition of Done**, cộng đúng một lần chạy full suite.
   Mỗi dòng DoD một phép kiểm bằng lệnh; không thêm hạng mục ngoài DoD.
   Chi tiết: mục `## Chạy cái gì` cùng file này. Việc lớn hoặc rủi ro cao → gọi thêm
   agent `tdq-qc-tester` cho một lượt kiểm độc lập.

5. Ghi `docs/tdq/qc/<slug>.md`: từng hạng mục DoD → PASS/FAIL kèm **bằng chứng**
   (lệnh + output thật). Không khẳng định thứ chưa chạy. (Khuôn file ở mục `## Ghi kết quả`
   cùng file này.)

6. FAIL → quay lại plan, **không cần duyệt lại**: thêm task fix vào plan dưới
   `## QC vòng N — fix` theo đúng khuôn `- [ ] **QCn.1** <việc> — Test: <check>`, làm
   theo luật Phần A (red→green, tick ngay). Rồi chạy lại hạng mục đã FAIL cộng hạng mục
   mà bản fix có thể làm hỏng, cộng full suite. Trần 3 vòng; vượt trần thì DỪNG, báo user.
   Chỉ kéo user vào giữa chừng khi bản fix đòi đổi phạm vi. (Bản đầy đủ ở mục `## Khi FAIL`
   cùng file này.)

Xong khi: mọi hạng mục QC PASS và có bằng chứng trong file qc.
Bước kế tiếp: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=report`.

## Chạy cái gì

**Số hạng mục QC = số dòng Definition of Done của plan.** Mỗi dòng DoD đúng một phép
kiểm chạy được bằng lệnh, dán output thật. Không thêm hạng mục ngoài DoD, không bớt
dòng DoD nào. DoD có dòng không kiểm được bằng lệnh → đó là lỗi của plan, sửa dòng đó
cho đo được rồi mới QC.

Cộng thêm đúng một hạng mục cố định: **toàn bộ test suite** bằng đúng lệnh ghi trong
plan, dán số pass/fail thật. Suite dài → chạy chế độ tóm tắt để khỏi dán log dài:
`<lệnh test> > /tmp/qc-run.log 2>&1; tail -n 40 /tmp/qc-run.log`. Chỉ dán nguyên văn
khi có FAIL cần bằng chứng.

Các thứ dưới đây **chỉ kiểm khi DoD chạm tới**, đừng chạy cho đủ bộ:

- Biên & đường lỗi: input rỗng, sai kiểu, file thiếu, quyền bị chặn, mạng hỏng.
- Log service: bật mặc định, có timestamp, tắt/giảm mức được qua config.
- Không placeholder: `TODO`, `FIXME`, dữ liệu mock còn sót được trình bày như thật.
- Hợp đồng skill: với TỪNG khối `Dùng:` trong plan, chạy lệnh ở trường `Kiểm`; artifact
  ở trường `Ra` phải tồn tại. Không có artifact → sửa spec §3b dòng đó thành `KHÔNG` +
  lý do đóng, rồi chạy lại
  `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/doc_lint.py" --pair <spec> <plan>` đến khi exit 0.
  Sửa spec ở đây làm sha256 lệch → hook sẽ đòi duyệt lại: trình user đúng 1 dòng diff
  và xin duyệt lại spec (`approve spec`) ngay trong lượt QC.

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
3. Chạy lại hạng mục đã FAIL, cộng hạng mục mà bản fix có thể làm hỏng, cộng test suite.
   Không chạy lại hạng mục không liên quan.
4. Lặp đến khi mọi hạng mục PASS. **Trần 3 vòng** — vượt trần thì DỪNG và báo user.

Chỉ hỏi user khi bản fix đòi đổi phạm vi so với spec đã duyệt.
