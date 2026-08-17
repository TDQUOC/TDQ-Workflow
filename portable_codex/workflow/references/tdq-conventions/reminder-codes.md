# Mã nhắc của hook

Hook TDQ **không chặn** (trừ đúng một trường hợp ở cuối). Nó chèn vào ngữ cảnh
những dòng dạng `[TDQ:<MÃ>] <việc phải làm>`.

**Luật:** thấy `[TDQ:<MÃ>]` → làm việc trong đó **TRƯỚC** mọi việc khác của turn,
xong in `✓ [TDQ:<MÃ>] <đã làm gì>`.

Dòng `✓` là để user đọc. Hook **không** đọc nó — hook kiểm bằng hiệu ứng thật
(file nào đã sửa, lệnh nào đã chạy), nên in `✓` mà không làm thì vẫn bị nhắc lại
ở cuối turn.

## Bảng 5 mã (danh sách đóng)

| Mã | Nghĩa | Việc phải làm | Hiệu ứng hook kiểm |
|---|---|---|---|
| `TDQ:NEXT` | Đầu turn / đầu session | Chạy `tdq_state.py next`, bám theo output | có lệnh `tdq_state.py next` đã chạy |
| `TDQ:APPROVE` | Đang chờ duyệt hoặc user vừa duyệt | Ghi nhận duyệt, hoặc HỎI nếu mơ hồ — xem [approval.md](approval.md) | trường `*_approved` chuyển true |
| `TDQ:LOG` | Repo đã đổi mà working log hôm nay chưa có | Append entry vào cuối `docs/workinglog/<hôm nay>.md` | đã sửa đúng file log đó |
| `TDQ:STATE` | Định sửa tay state | Dùng `tdq_state.py set\|approve\|init\|reset` | có lệnh `tdq_state.py` đã chạy |
| `TDQ:GIT` | Tên branch/worktree hoặc commit message phạm quy ước | Đổi tên/sửa message trước khi chạy | — (nhắc lại ở Stop) |

## Điểm chặn duy nhất

Hook `Stop` chặn kết thúc turn khi: turn này **đã sửa file ngoài** `docs/workinglog/`
mà **chưa** append working log hôm nay. Cách gỡ: append entry rồi kết thúc lại.
Mọi mã khác chỉ nhắc, không chặn.

## Phụ lục

### Hook nhìn thấy thay đổi bằng cách nào

Hai nguồn bằng chứng độc lập, chỉ cần một nguồn xác nhận là đủ:

1. **Sổ turn** `docs/tdq/.tdq-turn.jsonl` — ghi lại mọi lần sửa file đi qua tool
   Edit/Write và mọi lệnh `tdq_state.py` đã chạy.
2. **Ảnh chụp đĩa** — đầu turn hook lưu `sha256` của working log hôm nay cùng vân
   tay `git status` + `git diff HEAD`; cuối turn so lại.

Nguồn 2 khiến cách ghi không còn quan trọng: append log bằng `cat >>`, `tee`,
`sed -i` hay heredoc đều được công nhận, và sửa repo hoàn toàn bằng shell vẫn bị
đòi ghi log.

Vân tay repo **loại trừ** `docs/tdq/` và `docs/workinglog/` ngay từ pathspec của
git — sổ sách workflow đổi gần như mỗi turn, tính vào thì turn chỉ đọc cũng bị
đòi ghi log. Việc loại trừ áp cho cả quyết định lẫn tên file nêu trong lời chặn.
File untracked được lấy dấu bằng **nội dung** (≤256 KB), nên `touch` hay ghi đè
y hệt byte không bị coi là thay đổi.

Giới hạn đã biết:

- Project **không phải git repo** thì không có vân tay repo: chiều "đã ghi log"
  vẫn nhận ra, còn chiều "repo đã đổi" chỉ dựa vào sổ turn như trước.
- Sửa file trong `docs/tdq/` bằng tool Edit vẫn được sổ turn ghi nhận như thường.
- File bị `.gitignore` che thì vân tay repo không thấy.
- File untracked >256 KB chỉ lấy dấu `size:mtime`, có thể báo động giả.
- Tên file trong lời chặn là **gợi ý**: không có file mới xuất hiện thì nêu file
  đang bẩn đầu tiên, có thể không phải file vừa sửa.
- **2 phiên Claude Code cùng chạy trên 1 worktree chính**: vân tay repo là ảnh chụp
  đĩa dùng chung cho cả worktree, không phân biệt phiên nào sửa. Phiên A không đổi
  code vẫn có thể bị tính oan "đã đổi repo" nếu phiên B ghi đè file giữa lúc phiên A
  đang chạy. Tránh bằng cách không chạy song song 2 phiên trên cùng một worktree.
