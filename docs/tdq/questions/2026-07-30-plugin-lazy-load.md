# QUESTIONS — Tối ưu plugin user-level + lazy-load

## Vòng 1 (12:05 — đã trả lời 12:3x, đóng vòng)

Đề xuất chia tier trình kèm trong chat (bảng luôn-bật / bật-khi-cần).

| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | Ranh giới tier: đồng ý danh sách đề xuất (tắt mặc định 16 plugin domain ≈145 skill), hay đổi plugin nào giữa 2 tier? | **Đồng ý đề xuất** |
| 2 | learning-output-style đang xung đột luật "implement 1 turn" của TDQ — tắt hay giữ? | **Tắt** |
| 3 | Khi việc khớp plugin đang tắt: Claude tự chạy `claude plugin enable` rồi nhắc bạn gõ `/reload-plugins`, hay chỉ đề xuất lệnh để bạn tự chạy? | **Custom**: Claude đề xuất và HỎI ở bước interview; user okay → tự chạy bật; khi **end session tự động tắt lại** |
| 4 | Sửa `~/.claude/CLAUDE.md`: chỉ THÊM mục "Năng lực & plugin (lazy-load)" (tách riêng), hay gộp luôn việc viết lại §10 TDQ còn treo (T7.2 của 0.3.0)? | **Gộp cả §10** (T7.2 vào scope request này) |

Không còn câu hỏi làm đổi kết quả → đóng interview. Chi tiết kỹ thuật còn lại
(SessionEnd không bắn khi crash → reset bù ở SessionStart matcher `startup`;
vị trí script nguồn trong repo này + copy sang `~/.claude/scripts/`) là quyết định
thiết kế, sẽ ghi rõ trong spec.

Ghi chú ngữ cảnh:
- playwright: 0 SKILL.md trên đĩa, tool MCP được defer → luôn-bật gần như miễn phí,
  xếp tier luôn-bật, không cần hỏi.
- feature-dev: không tắt riêng agent code-reviewer được (giới hạn harness) → giữ cả
  plugin theo phán quyết nhóm 5; instruction sẽ định tuyến "review" về built-in.
