# Mini spec/plan and approval block

The mini spec/plan is written in the default document language; when `doc_lang` is not `vi`,
translate headings and labels while preserving the shape. <!-- i18n-allow: canonical Vietnamese section name below -->

```markdown
# QUICK — <tên việc>

**Ngày:** YYYY-MM-DD · Brief: ../brief/<slug>.md · Lane: quick
**Trạng thái:** CHỜ DUYỆT
**Ước tính sẽ dùng skill:** <skill sẽ DÙNG, hoặc "không có">

## Phạm vi
- Trong: <gạch đầu dòng>
- NGOÀI: <gạch đầu dòng>

## Task
- [ ] **T1** <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
- [ ] **T2** <việc cụ thể> — Test: <lệnh>

## Definition of Done
- <điều kiện đo được, có lệnh kiểm>
```

Going past 40 lines means this work is no longer quick — say so to the user and propose
moving to the deep pipeline.

Per [user-facing-block.md](../../tdq-conventions/references/user-facing-block.md), present it with
all 5 components, the approval block at the end of the message, and no emoji:

<!-- i18n-allow: sample block written in the default language -->
```
Tôi đã lên kế hoạch gọn cho yêu cầu của bạn.

**Sẽ làm:** <gạch đầu dòng ngắn>.
**Đụng tới:** <file/khu vực>.
**Kiểm thế nào:** <lệnh hoặc tiêu chí>.
**Ước tính sẽ dùng skill:** <skill sẽ DÙNG, hoặc "không có">.

Xem đầy đủ tại: `docs/tdq/plan/<slug>.md`

---

**Bạn duyệt để tôi làm luôn chứ?**

➤ Duyệt: nhắn "duyệt nhanh" kèm mức QC (vd "duyệt nhanh, QC full"); "duyệt quick" vẫn chạy — duyệt xong tôi làm ngay · Góp ý: nhắn trực tiếp
```
