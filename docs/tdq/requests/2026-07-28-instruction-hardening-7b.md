# REQUEST — Hook = remind, bỏ skill tdq-approve, instruction/skills đủ chi tiết cho model yếu (7B)

Ngày: 2026-07-28 · Người yêu cầu: user · Trạng thái: intake (chờ chọn lane)

## Nguyên văn yêu cầu

> tôi muốn setup là hook là remind agent và intruction báo agent phải tuân theo và thực thi theo reminder của hook và tôi nghĩ skikk tdq-workflow:tdq-approve có vẻ ko cần thiết vì tôi muốn agent sẽ hiểu theo câu trả lời tự nhiên khi ừoười dùng báo duyệt thì duyệt, và tôi muốn đi trong bộ instruction và skills sẽ hướng dẫn chi tiết bước nào làm gì để ổn định đến mức một model yếu như 7B cũng có thể tận dụng và đi theo bộ workflow này tốt

## Hiểu ban đầu (first read)

Ba mục tiêu, cùng một hướng: chuyển sức nặng từ "cơ chế chặn" sang "chỉ dẫn rõ ràng + lời nhắc bắt buộc tuân theo".

1. **Hook = remind agent.** Giữ nguyên kiến trúc 0.2.0 (`permissionDecision: "allow"` + `additionalContext`), nhưng nội dung nhắc phải là **mệnh lệnh thực thi được** (bước tiếp theo + lệnh cụ thể), không phải câu cảnh báo chung chung.
2. **Instruction bắt agent tuân theo hook.** Bộ instruction (user-level `CLAUDE.md` + `tdq-conventions`) phải có luật minh thị: mọi dòng `[TDQ] …` từ hook là chỉ thị bắt buộc, phải thực thi ngay ở turn đó trước khi làm việc khác. Hiện tại chưa có luật này — hook nhắc nhưng không có gì buộc agent làm theo.
3. **Bỏ skill `tdq-approve`.** Duyệt = câu nói tự nhiên của user; agent tự nhận diện và ghi state. Skill slash command là lớp dư thừa.
4. **Viết lại instruction/skills theo chuẩn "7B đọc cũng làm đúng"**: mỗi bước là một hành động đơn, có lệnh copy-paste được, có điều kiện vào/ra rõ ràng, không ẩn dụ, không "tuỳ tình huống", có ví dụ cụ thể và bảng quyết định thay cho văn xuôi.

## Ràng buộc đã biết

- Không quay lại `deny`; điểm chặn duy nhất vẫn là Stop hook (working log).
- Dấu vết duyệt (`*_approved_by` + working log) phải giữ.
- Skills là ngữ cảnh nạp vào token budget → chi tiết hơn nhưng phải kiểm soát độ dài (đã có `docs/qc/skill-budget.md` thời v0.1).

## Việc liên quan đang mở (từ đợt rà soát 2026-07-28)

Đề xuất gộp vào cùng request này vì cùng chạm một nhóm file:
- T1 `~/.claude/CLAUDE.md` §10 còn luật gate cứng (mâu thuẫn 0.2.0) — cần user cho phép sửa.
- T2 `docs/notes/user-level-install.md` §3 + "Lưu ý an toàn" còn mô tả hook chặn.
- T3 `docs/tdq/state.json` bị gitignore → dấu vết duyệt không bền.
- T4 chưa có `CHANGELOG.md`.
- C1 `tdq-start:33` "the hook confirms"; C2 `tdq-plan:8` "hooks enforce"; C3 marketplace.json "gate duyệt cứng"; C4 README dòng 3; C5 `tdq-status` chưa hiện `implement_mode`/`*_approved_by`.
- D1 doc v0.1 ở `docs/{spec,plan,qc,reports}/` + `idea.md` cần archive; D2 xoá `docs/.DS_Store`.

## Câu hỏi chờ user

1. Lane: quick hay full?
2. Có cho phép sửa `~/.claude/CLAUDE.md` §10 không?
3. Có gộp các mục rà soát ở trên vào request này không?
