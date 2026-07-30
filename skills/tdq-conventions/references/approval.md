# Ghi nhận duyệt

User duyệt bằng chat thường. Việc của agent là **nhận đúng** và **ghi lại**, không
phải phán đoán rộng tay.

## Là câu duyệt khi có ĐỦ hai phần

1. Từ đồng ý: `duyệt` · `ok` · `oke` · `đồng ý` · `chốt` · `approve` · `làm đi` · `tiến hành`
2. Đối tượng đang chờ duyệt: `spec` · `plan` · `quick` / `mini-plan`,
   hoặc đại từ trỏ rõ ràng: `cái này`, `cái đó`, `cái trên`.

Ví dụ ĐÚNG:

| Câu user | Ghi nhận |
|---|---|
| `duyệt spec` | `approve spec` |
| `ok plan, mode main` | `approve plan --mode main` |
| `chốt cái này` (đang chờ quick) | `approve quick` |
| `đồng ý, tiến hành plan mode subagent` | `approve plan --mode subagent` |
| `duyệt plan mode external codex` | `approve plan --mode external` (engine ghi trong plan) |

## KHÔNG phải câu duyệt (phản ví dụ)

| Câu user | Vì sao | Phải làm |
|---|---|---|
| `ok` | thiếu đối tượng, có thể chỉ là "tôi nghe rồi" | HỎI lại |
| `ok tôi hiểu rồi` | phản hồi hiểu, không phải chấp thuận | HỎI lại |
| `spec ok chưa?` | câu hỏi (có `?`) | Trả lời, chờ tiếp |
| `plan này duyệt chưa` | hỏi tình trạng, có `chưa` | Trả lời, chờ tiếp |
| `duyệt spec` khi đang chờ **plan** | sai đối tượng | Chỉ ghi spec, KHÔNG suy ra plan |

Mơ hồ → **HỎI**. Không bao giờ tự duyệt thay user.

## Lệnh phải chạy NGAY khi nhận ra

```
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve <spec|plan|quick> [--mode main|subagent|external] --by "<nguyên văn câu user>"
```

- `--by` bắt buộc trên thực tế: đó là dấu vết duy nhất nối state với hội thoại.
- Duyệt lại lần nữa không phải lỗi (idempotent, exit 0).
- `approve plan` mà user chưa nói mode → **HỎI mode trước**, đừng đoán.
- Mỗi lần duyệt cũng ghi 1 dòng vào `docs/workinglog/<hôm nay>.md`
  (duyệt gì, lúc nào, nguyên văn câu user).
