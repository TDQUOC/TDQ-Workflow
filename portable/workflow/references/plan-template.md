# Khuôn plan

Copy nguyên khối vào `docs/tdq/plan/<slug>.md` rồi điền.

```markdown
# PLAN — <tên việc>

Ngày: YYYY-MM-DD · Spec: ../spec/<slug>.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — <lý do 1–2 câu>
Trạng thái plan: CHỜ DUYỆT

## Năng lực → task
(Mỗi dòng DÙNG ở spec §3b phải có mặt ở đây VÀ có khối hợp đồng 6 trường trong task.)

| Skill | Task | Đầu ra bắt buộc |
|---|---|---|
| <tên> | T<x.y> | <artifact tồn tại được, kiểm bằng lệnh> |

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: viết test trước (đỏ) → code → test xanh → tick `[x]` NGAY vào file này.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — <tên phase>
- [ ] **T1.1** <việc cụ thể> — Test: <lệnh hoặc tiêu chí pass>
- [ ] **T1.2** <việc cụ thể> — Test: <...>

**Xong P1 khi**: <điều kiện đo được>

## P2 — <tên phase>
- [ ] **T2.1** <...> — Test: <...>

## Khuôn khối hợp đồng skill (đặt NGAY DƯỚI dòng task dùng skill đó, ≤7 dòng)
- [ ] **T<x.y>** <việc của task> — Test: <...>
  - Dùng: `<tên skill>`
  - Nạp: gọi skill `<tên>` TRƯỚC bước đỏ của task này. Agent ngoài không có skill
    system: đọc `<đường dẫn>/SKILL.md` rồi làm theo.
  - Để: <việc cụ thể skill lo trong task này>
  - Ra: <artifact phải tồn tại sau task, có đường dẫn>
  - Kiểm: <một lệnh chạy được, PASS đo được>
  - Không dùng cho: <việc kề bên mà skill này KHÔNG được lan sang>

## Px — Log & test bắt buộc
- [ ] **Tx.1** Log service bật mặc định (timestamp, mức log, tắt được qua config) — Test: <...>
- [ ] **Tx.2** Unit test cho từng thành phần, chạy bằng một lệnh — Test: <lệnh>

## Definition of Done
Trỏ về §6 của spec. Liệt kê lại từng hạng mục QC + lệnh kiểm.
```

## Dòng `Mode thực thi`

- Phải nằm **một dòng riêng**, không ghép vào dòng header khác — công cụ đọc dòng này.
- Đây chỉ là **đề xuất**. Mode ghi vào state là mode user nói lúc duyệt.

## Kiểm trước khi trình

- Mỗi đầu ra trong spec §2 ánh xạ tới ≥ 1 task.
- Mỗi task có đúng một việc và một cách kiểm đo được — không có task kiểu "hoàn thiện X".
- Task đầu của mỗi phase dựng được đường đi red → green sớm.
- Không task nào phụ thuộc task nằm sau nó.
