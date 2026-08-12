# TDQ STATE (tự sinh — không sửa tay)
Cập nhật: 2026-08-12T18:53:44+07:00 · Project: /Users/truongdinhquoc/Documents/TDQWorkflow · schema 3

| Trường | Giá trị |
|---|---|
| Request | 2026-08-12-commit-doi-ten-lane |
| Lane | quick |
| Phase | implement |
| Spec | (chưa có) |
| Plan | (chưa có) |
| Duyệt quick | ✔ đã duyệt |
| Mode thực thi | (chưa chốt) |

## Đang ở đâu
lane = quick. Cấm: Implement trước khi ghi working log; gom tick vào cuối turn hoặc để nhiều task cùng mang [~]; đóng việc khi còn test đỏ hoặc còn bug đã biết; chạy set phase=idle khi đã vượt trần 3 vòng fix mà chưa báo user.

## Việc tiếp theo
Phân tích → mini-spec/plan gộp 1 file → chờ duyệt → ghi working log TRƯỚC → implement → QC bám DoD (mặc định BẬT) → vòng fix nếu FAIL.
```
python3 scripts/tdq_state.py approve quick [--no-qc] --by "<nguyên văn câu user>"
```
Xong khi: quick_approved = true, log đã ghi, mục ## QC trong plan đã có (bằng chứng hoặc dòng BỎ theo yêu cầu user), không còn test đỏ, phase đã về idle

> Ghi state chỉ bằng `python3 scripts/tdq_state.py …`. Không chắc đang ở đâu → chạy `tdq_state.py next`.
