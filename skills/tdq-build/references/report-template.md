# Report template

## Bốn bước thi hành

This is the whole of Part C of [SKILL.md](../SKILL.md) — moved here so the skill body does not
carry this branch on every call. On entering phase `report` you **must** read all four steps
below before writing the report; working from memory is banned.

7. Viết `docs/tdq/reports/<slug>.md` — tiếng Việt, KHÔNG giới hạn cứng số dòng, khuyến
   nghị ~10-20 dòng. Template: section `## Khuôn` in this file. The timing table is
   **mandatory**: run `tdq_timing.py show` and paste the whole table into the report; never
   estimate the numbers yourself.

8. Close the books: tick any leftover checkbox, change the plan header to HOÀN THÀNH, then run
   `tdq_finish.py --files <file vừa sửa> --log "<tóm tắt report>"` (working log + graphify).

9. Present the report in chat (verbatim, or a short summary plus the path).

10. **Ask the user whether to commit** — mandatory; never commit the final result on your own
    (the single exception: an unblocking commit during build under the Hard rules, which must
    be listed in the report). Merge it with step 9 into ONE block following
    [user-facing-block.md](../../tdq-conventions/references/user-facing-block.md):
    ```
    Tôi đã làm xong yêu cầu của bạn.

    **Đã làm:** <gạch đầu dòng ngắn>.
    **Kết quả kiểm:** <số hạng mục QC, kết quả test>.

    Xem đầy đủ tại: `docs/tdq/reports/<slug>.md`

    ---

    **Bạn có muốn tôi commit phần thay đổi này không?**

    ➤ Trả lời: nhắn "commit" (tôi commit, không push) hoặc "chưa" (giữ nguyên chỗ làm việc) · Góp ý: nhắn trực tiếp
    ```
    User agrees → a message describing the change, containing NO "generated with …" and no AI
    trailer; branch named per the conventions.

Xong khi: report đã ghi và user đã được hỏi về commit.
Bước kế tiếp: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=idle`
(hoặc `reset` nếu user muốn xoá hẳn để sang request mới).

## Khuôn

(deliberate repetition — the original is step 7 of `## Bốn bước thi hành` in this file.)

`docs/tdq/reports/<slug>.md` — tiếng Việt, KHÔNG giới hạn cứng số dòng. Khuyến nghị
**càng ngắn càng tốt, tầm 10-20 dòng là ổn**; longer than that, say why (many proposals, many
tasks…) instead of cutting the truth. Compress each item into ONE line, separating ideas with
`·`, and take every number straight from real output.

```markdown
# REPORT — <tên việc> (`<slug>` · lane <lane> · mode <mode> · <n> task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** <P1 …> · <P2 …> · <P3 …>
**Kết quả:** <chỉ số> <trước> → <sau> · <chỉ số> <trước> → <sau>
**Kiểm:** <lệnh test + kết quả> · <lint> · QC <PASS x/y mục DoD, defect đã sửa>
**Đầu ra:** <đường dẫn file chính> · Backup: <đường dẫn, nếu có sửa ngoài repo>
**Giới hạn:** <cái gì chưa làm, vì sao, ảnh hưởng gì>
**Git:** <chưa commit / commit nào đã tạo>

## Thời gian

<dán nguyên output của `tdq_timing.py show`: bảng Phase · Treo tường · Model chạy · Số lần vào>
```

The two time columns differ on purpose: **treo tường** includes time spent waiting for the
user's approval, **model chạy** counts only machine work. A large gap on one phase means that
phase spent its time WAITING, not working — read the numbers before deciding what to optimise.

## Kiểm trước khi trình

- No hard cap; 10-20 lines recommended, as short as possible without dropping an item.
- Every number comes from real output, never an estimate. A measurement distorted by conditions
  gets said plainly in the "Kết quả" line.
- The "Giới hạn" line must not be left empty while work remains unfinished — tell the truth, hide
  nothing.
- End by asking the user whether they want a commit (asked in chat, not written into the file).
