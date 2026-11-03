# REQUEST — Tự chọn theo đề xuất khi gặp chặn kỹ thuật giữa build

Ngày: 2026-08-02 · Slug: 2026-08-02-auto-pick-recommended

## Nguyên văn yêu cầu
"ngoài ra tôi muốn mỗi khi có issue như này thì claude tự đgộn chọn theo đề xuất thay vì
phải hỏi lại" (kèm screenshot: giữa build external gặp chặn worktree thiếu 4.500 dòng
chưa commit, Claude dừng hỏi 3 option dù đã có option "(Đề xuất)").

## Cách hiểu đầu tiên
- Mục tiêu: khi gặp chặn KỸ THUẬT giữa build mà bản thân đã có phương án đề xuất rõ →
  tự chọn phương án đề xuất, log lại quyết định, làm tiếp — không dừng turn hỏi user.
- Ranh giới cần giữ: vẫn PHẢI hỏi khi (a) đổi phạm vi spec/plan, (b) hành động phá hủy/
  khó đảo (vd tự commit — CLAUDE.md cấm), (c) thiếu input chỉ user có.
- Ảnh hưởng: sửa luật trong skill tdq-build (mục "Luật cứng" + nhánh external),
  có thể cả tdq-conventions; screenshot là case commit — case đó đề xuất số 1 là
  "commit việc cũ" vốn bị cấm tự làm → cần định nghĩa rõ đề xuất tự chọn phải nằm
  trong quyền hạn sẵn có.
- Chưa rõ: user có muốn nới cả luật "hỏi commit" không, hay giữ cấm tự commit?
