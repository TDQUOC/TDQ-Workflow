# TDQ Workflow trên OpenCode

Adapter nằm ở `.opencode/plugins/tdq-workflow.js`. Nó ĐỌC thẳng `skills/` ở gốc repo này —
không có bản sao nào được dựng ra, nên skill bạn thấy trong OpenCode luôn là skill mới nhất.

## Cài

1. Clone repo này về máy, ví dụ `~/code/TDQ-Workflow`.
2. Khai adapter trong `opencode.json` của project hoặc của user:

   ```json
   {
     "plugin": ["~/code/TDQ-Workflow/.opencode/plugins/tdq-workflow.js"]
   }
   ```

3. Mở lại OpenCode. Chín skill `tdq-*` xuất hiện trong danh sách skill, và mỗi phiên mới nhận
   thêm một khối `<TDQ_WORKFLOW>` nhắc mở `tdq-intake` trước mọi việc.

Cập nhật là `git pull` — không có bước dựng lại nào.

## Yêu cầu

Node. Adapter viết bằng JavaScript thuần, **không dùng package npm nào**, chỉ `node:path`,
`node:fs` và `node:url`. Đây là chỗ duy nhất trong repo cần Node lúc chạy; phần còn lại của bộ
workflow chạy bằng Python thư viện chuẩn.

## Kiểm nhanh

```
node -e "import('./.opencode/plugins/tdq-workflow.js').then(m => console.log(m.docSkill().length))"
```

In ra số skill đọc được. Bằng 0 nghĩa là đường dẫn sai — adapter tìm `skills/` theo vị trí của
chính nó (`../../skills`), nên nó phải nằm nguyên trong repo chứ không copy đi nơi khác.

## Khi có lỗi

Adapter bọc try/catch quanh mọi bước và **không bao giờ ném ra ngoài**. Một plugin ném lỗi lúc
kích hoạt sẽ kéo sập cả thế hệ plugin của host, kể cả plugin cung cấp model, và người dùng mất
sạch model trong TUI. Nên khi có trục trặc, adapter bỏ qua phần hỏng rồi ghi một dòng ra stderr:

```
[2026-09-21T01:20:00] tdq-workflow: host từ chối skill "tdq-build": ...
```

Tắt log bằng `TDQ_LOG=0`.
