# QC — kiểm chất lượng

QC là chạy thật và dán bằng chứng. Không có "chắc là ổn".

## Ba bước thi hành

Đây là toàn bộ Phần B của [SKILL.md](../SKILL.md) — chuyển về đây để thân skill không phải
nạp nhánh này mỗi lần gọi. Vào phase `qc` là **bắt buộc** đọc hết ba bước dưới đây trước
khi chạy hạng mục đầu tiên; cấm làm theo trí nhớ.

4. **Số hạng mục QC = số dòng Definition of Done**, cộng bốn hạng mục cố định
   QC-F1→F4. Mỗi dòng DoD một phép kiểm bằng lệnh; ngoài các
   hạng mục cố định, không thêm gì ngoài DoD.
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
Bước kế tiếp: `python3 "./scripts/tdq_state.py" set phase=report`.

## Chạy cái gì

**Số hạng mục QC = số dòng Definition of Done của plan, cộng bốn hạng mục cố định.**
Mỗi dòng DoD đúng một phép kiểm chạy được bằng lệnh, dán output thật. Không bớt dòng
DoD nào. DoD có dòng không kiểm được bằng lệnh → đó là lỗi của plan, sửa dòng đó cho
đo được rồi mới QC. Bốn hạng mục cố định luôn chạy, không phụ thuộc DoD:

- QC-F1 — toàn bộ test suite bằng đúng lệnh ghi trong plan, dán số pass/fail thật.
  Suite dài → `<lệnh test> > /tmp/qc-run.log 2>&1; tail -n 40 /tmp/qc-run.log`, chỉ
  dán nguyên văn khi có FAIL cần bằng chứng.
- QC-F2 — hồi quy vùng chạm: với mỗi dòng `Chạm:` trong plan, chạy test của module
  chứa node bị ảnh hưởng. Node không có test → ghi `KHÔNG CÓ TEST: <node>` vào file
  QC; đó là nợ kỹ thuật phải nêu trong report, không được tính là PASS.
- QC-F3 — ràng buộc kiến trúc: mỗi dòng trong khối "Ràng buộc kiến trúc phải giữ" ở
  spec §5 là một phép kiểm rằng bản thay đổi không phá dòng đó.
- QC-F4 — clean code: turn này có sửa file mã nguồn thì trả lời 5 câu ở mục
  `## Tự kiểm` của `skills/tdq-conventions/references/clean-code.md`, ghi từng đáp án
  có/không vào file qc. Câu nào "không" → sửa code rồi ghi chỗ đã sửa, không sửa
  đáp án. Không chạm mã nguồn → ghi `KHÔNG ÁP DỤNG — không sửa file code`.

Ngoài các hạng mục trên, không thêm hạng mục nào ngoài DoD.

Các thứ dưới đây **chỉ kiểm khi DoD chạm tới**, đừng chạy cho đủ bộ:

- Biên & đường lỗi: input rỗng, sai kiểu, file thiếu, quyền bị chặn, mạng hỏng.
- Log service: bật mặc định, có timestamp, tắt/giảm mức được qua config.
- Không placeholder: `TODO`, `FIXME`, dữ liệu mock còn sót được trình bày như thật.
- Hợp đồng skill: với TỪNG khối `Dùng:` trong plan, chạy lệnh ở trường `Kiểm`; artifact
  ở trường `Ra` phải tồn tại. Không có artifact → sửa spec §3b dòng đó thành `KHÔNG` +
  lý do đóng, rồi chạy lại
  `python3 "./scripts/doc_lint.py" --pair <spec> <plan>` đến khi exit 0.
  Sửa §3b là sửa NỘI DUNG spec nên sha vẫn lệch và hook vẫn đòi duyệt lại — đúng như
  thiết kế: đổi phán quyết một năng lực là đổi ý định, phải hỏi user. Trình đúng 1 dòng
  diff rồi xin duyệt lại (`approve spec`) ngay trong lượt QC. Ngược lại, sửa dòng sổ
  sách đầu file (Ngày, Bản, Trạng thái) KHÔNG còn làm lệch sha kể từ 2026-08-19. Và §6
  không còn chứa lệnh kiểm để mà sai tên. Hai nguồn "duyệt lại vì lý do vô hại" đã được
  cắt ở gốc.

## Ghi kết quả

`docs/tdq/qc/<slug>.md`:

```markdown
# QC — <tên việc>
Ngày: YYYY-MM-DD · Plan: ../plan/<slug>.md · Vòng: 1
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

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
