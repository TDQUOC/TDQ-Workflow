# Request: state phải luôn nằm ở project root (chống "state bóng")

**Ngày:** 2026-07-28 · **Lane:** quick

## Nguyên văn
> có, mở request quick cho fix này

(fix được đề xuất sau sự cố "duyệt quick không được ghi nhận" ở repo `insightfaceserverv2`)

## Bằng chứng
Repo `insightfaceserverv2` có 3 file state cùng lúc:

| Đường dẫn | quick_approved | updated_at |
|---|---|---|
| `docs/tdq/` (gốc — hook dùng) | true | 18:16:51 |
| `frontend/docs/tdq/` | false | 18:12:25 |
| `frontend/src/features/checkin/docs/tdq/` | false | 17:48:04 |

## Nguyên nhân
`tdq_state.py` lấy project dir = `TDQ_PROJECT_DIR` hoặc `os.getcwd()`. Chạy CLI khi đang ở thư mục con
(vd `cd frontend && python3 …/tdq_state.py init …`) → tạo mới state ngay tại thư mục con. Hook luôn chạy
với cwd = repo root nên ghi/đọc state gốc; model đọc state bóng → kết luận sai "chưa duyệt" và dừng giữa
chừng dù user đã duyệt.

## Mong muốn
CLI và hook luôn giải về **một** state duy nhất ở project root; nếu repo có nhiều state thì cảnh báo rõ.

## Ràng buộc
- Không đổi hành vi gate duyệt.
- `TDQ_PROJECT_DIR` (dùng trong test) vẫn phải được tôn trọng tuyệt đối.
