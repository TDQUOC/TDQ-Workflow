# QC — Chấm toàn bộ workflow theo hướng LLM đọc & chi phí context

Ngày: 2026-08-14 · Plan: ../plan/2026-08-14-toi-uu-llm-workflow.md
Đặt `F=docs/tdq/knowledge/2026-08-14-toi-uu-llm-workflow.md`,
`S=docs/tdq/spec/2026-08-14-toi-uu-llm-workflow.md`,
`P=docs/tdq/plan/2026-08-14-toi-uu-llm-workflow.md`.

| # | Hạng mục | Lệnh | Kết quả | Phán quyết |
|---|---|---|---|---|
| Q1 | Đủ 9 mục `## ` theo spec §2 | `grep -c "^## " $F` | `9` | PASS |
| Q2 | Thang chấm đủ 6 tiêu chí, không ô "lệnh đo" rỗng | `grep -c "^\| R[1-6] " $F` · `awk -F'\|'` cột 4 | `6` · `0` ô rỗng | PASS |
| Q3 | Chấm đủ mọi file skill | `grep -c "^\| skills/" $F` vs `find skills -name "*.md" \| wc -l` | `28` vs `28` | PASS |
| Q4 | Chấm đủ 6 hook + 3 agent | `grep -cE "^\| hooks/\|^\| agents/" $F` | `9` | PASS |
| Q5 | Mọi dòng chỗ phí có số đo và đường dẫn | `grep '^\| F[0-9]' $F` lọc dòng thiếu chữ số / thiếu path | 8 dòng · `0` thiếu số · `0` thiếu path | PASS |
| Q6 | Mọi đề xuất đủ 7 trường | 7 lệnh `grep -c "^- <trường>:" $F` vs `grep -c "^### Đ" $F` | `7 7 7 7 7 7 7` vs `7` | PASS |
| Q7 | Không đề xuất nào làm giảm số luật | regex bắt `\| Đn \| … \| trước \| sau \|` rồi so sánh | `10` dòng, `0` dòng "sau" < "trước" | PASS |
| Q8 | Đúng 3 gói và đúng 1 khuyến nghị | `grep -c "^### Gói" $F` · `grep -c "^Khuyến nghị: " $F` | `3` · `1` | PASS |
| Q9 | Lệnh ở mục Công cụ đo lại chạy được | chạy nguyên khối `python3 -c '…'` trong mục | exit `0`, in `tong file: 28 tong luat: 205` — khớp bảng chấm | PASS |
| Q10 | Đủ nguồn ngoài | `grep -c "^- https\?://" $F` | `6` | PASS |
| Q11 | Không vượt phạm vi + test xanh | `git status --porcelain -- skills hooks agents scripts` · `python3 -m pytest tests/ -q` | rỗng · `563 passed, 244 subtests passed` | PASS |
| Q12 | Bộ tài liệu hợp lệ | `python3 scripts/doc_lint.py $F $S $P` | exit `0` | PASS |

**Kết quả: 12/12 PASS.**

Ghi chú Q11: request này chốt phạm vi "dừng ở đề xuất", nên `skills/`, `hooks/`,
`agents/`, `scripts/` phải sạch tuyệt đối — đây là hạng mục quan trọng nhất của bản QC,
không phải hạng mục thủ tục.

Ghi chú Q1: bốn dòng tiêu đề Markdown nằm trong khối `Nội dung nháp` của mục `## Đề xuất`
được thụt 2 space có chủ ý, để không bị đếm lẫn vào 9 mục của chính tài liệu. Quy ước này
ghi ngay đầu mục `## Đề xuất`.
