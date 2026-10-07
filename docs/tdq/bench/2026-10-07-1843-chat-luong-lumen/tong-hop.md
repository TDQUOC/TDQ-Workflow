# Tổng hợp đo chất lượng tìm kiếm: CÓ và KHÔNG Lumen — 2026-10-07

Nguồn: `cau-hoi-*.md` (đáp án), `ket-qua-{tdq,ccui}-{co,khong}.md` (kết quả thô), `chuan-bi.md`.
Token và thời gian lấy từ thông báo kết thúc của từng agent (`subagent_tokens`, `tool_uses`, `duration_ms`).

## Cách chấm
- **Trúng đủ**: vị trí chính của agent là đích chính của đáp án (cùng hàm; lệch 1 dòng trong cùng hàm vẫn tính).
- **Trúng một phần**: vị trí chính của agent chỉ là "vị trí phụ chấp nhận" (kể cả khi agent ghi đích chính ở cột phụ).
- **Trượt**: không chạm đích chính lẫn vị trí phụ.

## Từng câu

| # | TDQ CÓ | TDQ KHÔNG | ccui CÓ | ccui KHÔNG |
|---|---|---|---|---|
| 1 | đủ | đủ | đủ | đủ |
| 2 | đủ | đủ | một phần (`handleHistoryKeyDown:138`) | một phần (`handleHistoryKeyDown:138`) |
| 3 | đủ | một phần (`_gop_lien_ke:121`, đích ở cột phụ) | đủ | đủ |
| 4 | đủ | đủ | đủ | đủ |
| 5 | đủ | đủ | đủ | đủ |
| 6 | đủ | đủ | đủ | đủ |
| 7 | đủ | đủ | đủ | đủ |
| 8 | đủ | đủ | đủ | một phần (`resolveClaudeWrapperBinary:35`, đích ở cột phụ) |
| 9 | đủ | đủ | đủ | đủ |
| 10 | đủ | đủ | đủ | đủ |
| 11 | đủ | đủ | đủ (`:135`, cùng hàm) | đủ |
| 12 | đủ | đủ | đủ | đủ |

## Số tổng

| Repo | Nhánh | Trúng đủ | Một phần | Trượt | Token agent | Lượt tool | Thời gian |
|---|---|---|---|---|---|---|---|
| TDQ-Workflow | CÓ lumen | 12 | 0 | 0 | 48.220 | 18 | 53 s |
| TDQ-Workflow | KHÔNG lumen | 11 | 1 | 0 | 42.571 | 9 | 51 s |
| claudecodeui | CÓ lumen | 11 | 1 | 0 | 53.246 | 25 | 72 s |
| claudecodeui | KHÔNG lumen | 10 | 2 | 0 | 56.643 | 30 | 95 s |

## Áp luật kết luận (spec §3 mục 3)
"Giảm đáng kể" khi nhánh KHÔNG trượt nhiều hơn nhánh CÓ ≥ 2 câu/12, HOẶC token nhánh KHÔNG ≥ 1,5× nhánh CÓ.

- **TDQ-Workflow**: trượt 0 so với 0 (tính cả một phần: 1 so với 0, chênh 1). Token KHÔNG/CÓ = 42.571 / 48.220 = **0,88×**. → **KHÔNG giảm đáng kể.**
- **claudecodeui**: trượt 0 so với 0 (tính cả một phần: 2 so với 1, chênh 1). Token KHÔNG/CÓ = 56.643 / 53.246 = **1,06×**. → **KHÔNG giảm đáng kể.**

Ngay cả khi đếm "một phần" là trượt (cách chấm khắt khe nhất), chênh lệch vẫn chỉ 1 câu mỗi repo, dưới ngưỡng 2.

## Giới hạn của phép đo — đọc trước khi trích số
1. **Bộ câu hỏi thiên về grep.** Hai agent soạn câu hỏi đã tìm đích bằng grep/Read (cấm lumen), nên mọi đích đều *grep tìm được*. Câu hỏi lại mô tả hành vi rất cụ thể ("…", "Windows", "mũi tên lên") — từ khoá tốt cho grep. Câu hỏi mơ hồ hơn thật ngoài đời có thể cho lumen lợi thế lớn hơn.
2. **Search gate không bị thử thách.** Hai nhánh KHÔNG bị chặn 0 lần: sổ tìm kiếm của request này đã ghi lời gọi lumen từ trước (phiên chính), nên grep đã được mở khoá. Hành vi gate khi KHÔNG có lumen được đo riêng ở `../2026-10-07-1843-hai-host-khong-lumen/`.
3. **graphify không chạy ở nhánh ccui KHÔNG** — Bash của agent dính lỗi môi trường `fnm` (lỗi máy, không phải do lumen). Nhánh đó thực chất là "chỉ grep + Read".
4. **Lỗi lumen gặp khi đo**: 3 lời gọi `semantic_search` với `path` là thư mục con báo `k value in knn query too large`; agent phải gọi lại với gốc repo (đã tính vào lượt tool của nhánh CÓ).
5. Cỡ mẫu 12 câu/repo, 1 lần chạy/nhánh, model agent mặc định. Không ngoại suy ra mọi repo.
