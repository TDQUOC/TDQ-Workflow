| # | Vị trí chính (file:dòng, hàm) | Vị trí phụ | Số lượt tool | Tool đã dùng |
|---|---|---|---|---|
| 1 | scripts/utf8_io.py:67, force_utf8 | utf8_io.py:89 _force_once | 1+g | lumen |
| 2 | scripts/tdq_state.py:490, _atomic_write | — | 1 | lumen |
| 3 | scripts/doc_dup.py:137, quet | doc_dup.py:121 _gop_lien_ke | 1+g | lumen |
| 4 | scripts/tdq_state.py:526, xoa_cay | — | 1+g | lumen |
| 5 | scripts/tdq_state.py:1516, duong_hien_thi | — | 1 | lumen |
| 6 | hooks/scripts/prompt_context.py:87, looks_like_approval | — | 1 | lumen |
| 7 | hooks/scripts/prompt_context.py:140, mode_from_answer | prompt_context.py:126 thu_tu_mode | 2+g | lumen, Read |
| 8 | hooks/scripts/codex_edit_gate.py:84, tach_duong_ghi_shell | scripts/tdq_eval.py:260 _duong_dan_ghi_bash | 1 | lumen |
| 9 | hooks/scripts/stop_gate.py:200, _chan_chua_xong | stop_gate.py:178 _streak_bump | 2+g | lumen, Grep |
| 10 | scripts/tdq_state.py:564, sha256_noi_dung | — | 2+g | lumen, Read |
| 11 | scripts/tdq_state.py:648, _untracked_mark | — | 1+g | lumen |
| 12 | hooks/scripts/stop_gate.py:76, _log_changed | hooks/scripts/agy_stop_gate.py:103 _log_changed | 1+g | lumen |

g = 1 lượt Grep chung (tìm dòng def cho nhiều câu), đếm một lần. Thêm 1 ToolSearch nạp schema lumen.

Tổng số lượt tool: 17 (12 lumen + 1 Grep chung + 1 Grep + 2 Read + 1 ToolSearch), không tính lượt Write file kết quả.
