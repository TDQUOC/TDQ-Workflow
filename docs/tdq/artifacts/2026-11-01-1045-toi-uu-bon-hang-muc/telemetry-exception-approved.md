# Phụ lục ngoại lệ telemetry đã duyệt
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày 2026-11-01, user trả lời “duyệt” cho đề xuất bỏ qua riêng usageCount và lastUsedAt trong pluginUsage của .claude.json để tiếp tục kiểm chứng.

Phạm vi: chỉ giá trị hai trường đó ở từng entry pluginUsage; mọi trường khác, cấu trúc entry, plugin mới/xóa, các file cấu hình khác, source, dependency, quyền thường, capture và cleanup vẫn được kiểm. JSON lỗi hoặc đọc thất bại phải FAIL. Không thay đổi file cấu hình cá nhân.

Giữ nguyên spec v1.0, preview, manifest và helper cũ cùng digest đã duyệt để truy xuất lịch sử. Phụ lục này thay riêng điều khoản cấm mọi ngoại lệ guard trong lượt kiểm mới. Adapter và verifier request phải nhận diện policy mới tường minh, lưu digest raw và digest đã loại giá trị telemetry; không lưu nội dung cá nhân. Receipt FAIL cũ giữ nguyên, không nâng thành PASS. Chạy lại kiểm chứng bằng receipt mới trước tick task.

Plan tiếp tục dùng mode subagent và QC ultra. Không mở lại benchmark D9/D10; không cấp quyền commit/push mới.
