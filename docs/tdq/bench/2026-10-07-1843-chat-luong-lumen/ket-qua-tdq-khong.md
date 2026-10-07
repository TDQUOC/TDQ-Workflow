# Kết quả nhánh KHÔNG LUMEN

| # | Vị trí chính (file:dòng, hàm) | Vị trí phụ | Số lượt tool | Tool đã dùng |
|---|---|---|---|---|
| 1 | scripts/utf8_io.py:67 force_utf8 | hooks/scripts/codex_edit_gate.py:43 | 2* | Grep, Bash(grep) |
| 2 | scripts/tdq_state.py:490 _atomic_write | scripts/plugin_tiers.py:98 | 2* | Grep, Bash(grep) |
| 3 | scripts/doc_dup.py:121 _gop_lien_ke | scripts/doc_dup.py:137 quet | 1* | Bash(grep) |
| 4 | scripts/tdq_state.py:526 xoa_cay (_thu_lai:539) | - | 2* | Grep, Bash(grep) |
| 5 | scripts/tdq_state.py:1516 duong_hien_thi | - | 2* | Bash(grep) x2 |
| 6 | hooks/scripts/prompt_context.py:87 looks_like_approval | - | 1* | Bash(grep) |
| 7 | hooks/scripts/prompt_context.py:140 mode_from_answer | prompt_context.py:126 thu_tu_mode | 1* | Bash(grep) |
| 8 | hooks/scripts/codex_edit_gate.py:84 tach_duong_ghi_shell | - | 3* | Bash(grep), Grep, Bash(sed) |
| 9 | hooks/scripts/stop_gate.py:200 _chan_chua_xong | stop_gate.py:178 _streak_bump | 2* | Bash(grep), Bash(sed) |
| 10 | scripts/tdq_state.py:564 sha256_noi_dung | - | 2* | Bash(grep), Bash(sed) |
| 11 | scripts/tdq_state.py:648 _untracked_mark | - | 1* | Bash(grep) |
| 12 | hooks/scripts/stop_gate.py:76 _log_changed | - | 2* | Bash(grep), Bash(sed) |

\* Nhiều lượt gọi được dùng chung cho nhiều câu (grep gộp từ khoá); cột ghi số lượt có góp phần cho câu đó, nên cộng cột sẽ lớn hơn tổng thật.

- Tổng số lượt tool thật: 8 (2 Grep, 6 Bash) + 1 Write ghi file kết quả.
- Số lượt bị hook chặn: 0.
- Câu 4, 6, 11 chưa đọc thân hàm để kiểm tra, chỉ dựa vào tên hàm/ngữ cảnh grep.
- đã gọi lumen: 0 lần
