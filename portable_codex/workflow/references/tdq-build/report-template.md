# Report template

## Table of contents

- The execution steps
- The report shape
- Thời gian
- Check before presenting

## The execution steps

This is the whole of Part C of [SKILL.md](../SKILL.md) — moved here so the skill body does not
carry this branch on every call. On entering phase `report` you **must** read all four steps
below before writing the report; working from memory is banned.

<!-- doc-lint: allow R1 -->
7. Write `docs/tdq/reports/<slug>.md` — in the user's document language, with NO hard line
   limit; ~10-20 lines recommended. Template: section `## The report shape` in this file. The timing table is
   **mandatory**: run `tdq_timing.py show` and paste the whole table into the report; never
   estimate the numbers yourself.

8. Close the books: tick the leftover boxes of BOTH kinds — the task boxes in each phase AND
   the Definition of Done boxes — change the plan header to HOÀN THÀNH, then run <!-- i18n-allow: canonical status value -->
   `tdq_finish.py --files <edited files> --log "<report summary>"` (working log + graphify).
   The two kinds are counted separately, and the DoD one is the one that gets forgotten: QC
   signs off every item while the boxes stay `[ ]`. Hook `Stop` reminds with `[TDQ:DOD]`
   when the books close on an open box, but the reminder is a net, not a substitute — tick
   as each item passes.

9. Present the report in chat (verbatim, or a short summary plus the path).

10. **Ask the user whether to commit** — mandatory; never commit the final result on your own
    (the single exception: an unblocking commit during build under the Hard rules, which must
    be listed in the report). Merge it with step 9 into ONE block following
    [user-facing-block.md](../../tdq-conventions/references/user-facing-block.md):
    <!-- i18n-allow: chat block written in the default document language -->
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

11. **Merge the request branch back** — this happens on BOTH answers, so long as state holds a
    `nhanh_request`. The branch was opened at step 3b of `tdq-intake`; leaving it behind is what
    used to breed orphan branches.
    - `"commit"` → commit on the request branch first, then:
      ```
      git switch <nhanh_goc>
      git merge --no-ff <nhanh_request>
      git branch -d <nhanh_request>
      ```
    - `"chưa"` → no new commit, but everything ALREADY committed on the request branch still
      merges back with the same three commands. What is not committed lives in the working tree
      and would be dragged along by `git switch`, so run `git status --porcelain` first: not
      empty → STOP, print the dirty files, ask the user, and do not switch. Same shape as the
      dirty-repo rule at step 3b.
    - Merge conflict, or `git branch -d` refuses → do NOT force. Report it and ask the user.
    - Then clear the three keys:
      ```
      python3 "./scripts/tdq_state.py" set loai_request=null nhanh_goc=null nhanh_request=null
      ```
    No `nhanh_request` in state (tier `nhỏ`, or a project with no git) → skip this step entirely.

Done when: the report is written, the user has been asked about the commit, and the request
branch has been merged back into `nhanh_goc`.
Next step: `python3 "./scripts/tdq_state.py" set phase=idle`
(or `reset` when the user wants the slate wiped for a new request).

## The report shape

(deliberate repetition — the original is step 7 of `## The execution steps` in this file.)

`docs/tdq/reports/<slug>.md` — in the user's document language, with NO hard line limit.
**As short as possible, around 10-20 lines**; longer than that, say why (many proposals, many
tasks…) instead of cutting the truth. Compress each item into ONE line, separating ideas with
`·`, and take every number straight from real output.

<!-- i18n-allow: report template written in the default document language -->
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

<dán nguyên output của `tdq_timing.py show`: bảng Phase · Wall clock · Model time · Times entered>
```

The two time columns differ on purpose: **wall clock** includes time spent waiting for the
user's approval, **model time** counts only machine work. A large gap on one phase means that
phase spent its time WAITING, not working — read the numbers before deciding what to optimise.

## Check before presenting

- No hard cap; 10-20 lines recommended, as short as possible without dropping an item.
- Every number comes from real output, never an estimate. A measurement distorted by conditions
  gets said plainly in the "Kết quả" line. <!-- i18n-allow: canonical line name of the report -->
- The "Giới hạn" line must not be left empty <!-- i18n-allow: canonical line name of the report --> while work remains unfinished — tell the truth, hide
  nothing.
- End by asking the user whether they want a commit (asked in chat, not written into the file).
