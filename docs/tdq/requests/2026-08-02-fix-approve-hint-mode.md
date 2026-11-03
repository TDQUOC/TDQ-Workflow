# REQUEST — Dòng duyệt plan gợi ý sai mode đã chốt

Ngày: 2026-08-02 · Slug: 2026-08-02-fix-approve-hint-mode

## Nguyên văn yêu cầu
"tôi đang thấy có issue là trong plan ban đầu đã chốt external nhưng ở dưới khuyến nghị
lại là duyệt plan mode main, hãy check và detect issue cho tôi" (kèm screenshot phiên
2026-08-01-fix-retry-guest: plan chốt external + engine=agy nhưng dòng duyệt in
'duyệt plan mode main (hoặc subagent, external)').

## Cách hiểu đầu tiên
- Mục tiêu: xác định vì sao dòng gợi ý duyệt luôn nêu "mode main" dù plan đã chốt external.
- Phát hiện sơ bộ: chuỗi gợi ý HARDCODE "main" ở 3 chỗ, không đọc mode đã chốt trong plan:
  1. `hooks/scripts/_common.py:24` — APPROVE_HINTS["plan"].
  2. `skills/tdq-plan/SKILL.md:48` — bước 5 in nguyên văn dòng cố định.
  3. `portable/workflow/03-plan.md:43` — bản portable cùng dòng.
- Hệ quả: user dễ gõ nhầm "duyệt plan mode main" → implement_mode bị ghi main, sai với
  mode đã chốt trong plan (external).
- Chỗ chưa rõ: user muốn chỉ DETECT (báo cáo) hay fix luôn (hint động theo mode trong plan)?
