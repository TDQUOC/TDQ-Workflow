# Report — Siết QC và vòng fix cho lane quick

Slug: `2026-08-07-siet-qc-lane-quick` · Lane full · Mode `main` · Ngày 2026-08-07
Spec (bản 1.1) · Plan 6 phase / 18 task · QC `../qc/2026-08-07-siet-qc-lane-quick.md`

## Đã làm

Trước bản này lane quick chỉ nói "chạy validate" và **không có luật nào** cho tình huống
gặp bug — `qc.md` cùng luật `## QC vòng N — fix` chỉ `tdq-build` (lane full) nạp.

- **QC quick = 3 hạng mục, mặc định BẬT:** test từng task pass · đối chiếu TỪNG dòng
  Definition of Done · biên và đường lỗi cơ bản. Bằng chứng append vào mục `## QC` của
  chính file plan, không tạo file `qc/`. Nhẹ hơn full đúng 4 hạng mục.
- **Vòng fix BẮT BUỘC, không opt-out được** kể cả khi user bỏ QC · task fix ghi dưới
  `## QC vòng N — fix`, fix xong chạy lại đủ 3 hạng mục · **trần 3 vòng** — vượt trần thì
  DỪNG, báo user, đề xuất chuyển lane full, giữ `phase=implement`.
- **Cờ `approve quick --no-qc`** là đường opt-out DUY NHẤT: chỉ hợp lệ với `quick`, bắt
  buộc kèm `--by "<nguyên văn câu user>"`, ghi field `quick_qc_skipped`, log 1 dòng có
  timestamp qua `_info` (stderr, tắt được bằng `TDQ_LOG=0`). Gate duyệt: `"duyệt quick"`
  trơn = CÓ QC; muốn bỏ phải nói rõ `"duyệt quick không QC"`.
- **Đồng bộ 5 nguồn sự thật:** `tdq-intake/references/quick-lane.md` · `tdq-intake/SKILL.md` ·
  `scripts/tdq_state.py` (`PHASE_TABLE["quick"]`) · `portable/workflow/**` · 2 bản
  `phases.md` sinh bằng `phases-doc` (không sửa tay). Thêm `hooks/scripts/_common.py`
  gợi ý biến thể bỏ QC. Bump plugin `0.8.0 → 0.9.0`.

## Kết quả QC

Q1–Q8 **PASS**, bằng chứng đầy đủ trong file qc. Số chính: `test_quick_qc` 15/15 OK ·
suite `618 test`, đúng 1 failure có sẵn ngoài phạm vi · `doc_lint skills portable` exit 0 ·
`grep -l "trần 3 vòng"` = 3 file · 2 bản `phases.md` `diff` với `phases-doc` IDENTICAL ·
`next` của quick 16 dòng (trần 20). **0 vòng fix** — không hạng mục nào FAIL.
Agent `tdq-qc-tester` kiểm độc lập cũng phán quyết PASS, và sửa lại 1 số liệu Q7 của tôi
(biến thể `--no-qc` lặp là idempotent exit 0, không phải exit 2) — đã đo lại và sửa.

## Giới hạn còn lại

- 1 failure có sẵn `test_claude_md_core.test_d_ban_repo_trung_ban_da_cai`
  (`portable/claude-md/CLAUDE.md` lệch `~/.claude/CLAUDE.md` từ 2026-08-06) — spec §1 khoanh
  NGOÀI phạm vi, chưa sửa.
- `skills/tdq-intake/references/quick-lane.md` đúng 90 dòng, sát trần 90 của spec §2.
- Hành vi warn-only có sẵn: `approve quick --no-qc` khi state đang `lane=full` chỉ `⚠️`
  rồi vẫn set cờ. Spec không yêu cầu chặn nên để nguyên.
- Hook duyệt 2 lần báo câu `"duyệt spec 1.1 và duyệt plan mode main"` là không rõ, dù câu
  đó có động từ duyệt 2 lần và đủ mode. `prompt_context.py` còn hụt ở dạng câu duyệt ghép —
  đáng mở request riêng.

## Commit

**Chưa commit gì.** Không có commit gỡ chặn nào trong lúc build.
