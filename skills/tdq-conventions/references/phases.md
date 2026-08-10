# Bảng phase TDQ (tự sinh — KHÔNG sửa tay)

Sinh lại: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" phases-doc --plugin-root > <file>`.
Nguồn: hằng `PHASE_TABLE` trong `scripts/tdq_state.py`.
Đang ở phase nào thì chỉ làm đúng việc của phase đó, xong chạy đúng lệnh của nó.

| phase | vào khi | việc duy nhất | lệnh chuyển tiếp | xong khi | cấm |
|---|---|---|---|---|---|
| `no_state` | Chưa có request TDQ nào đang mở | Hỏi user chọn lane rồi mở request mới | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" init <YYYY-MM-DD-slug> <quick\|full>` | state.json có active_request và lane | Sửa code khi chưa mở request |
| `analyze` | Đã có request, lane full | Đọc code, research, interview user đến khi hết chỗ mơ hồ | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=spec` | Không còn câu hỏi nào làm thay đổi kết quả | Viết spec khi chưa hết mơ hồ |
| `spec` | Đã phân tích xong | Viết spec (kèm mục Lộ trình), đăng ký spec_file, trình tóm tắt rồi DỪNG chờ user duyệt | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve spec --by "<nguyên văn câu user>"` | spec_approved = true | Tự suy diễn là user đã duyệt; bắt user nhắn thêm một turn nữa mới viết plan |
| `plan` | spec_approved = true | Viết plan kèm mode ĐỀ XUẤT, đăng ký plan_file, trình rồi DỪNG chờ duyệt | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve plan --mode <main\|subagent> --by "<nguyên văn>"` | plan_approved = true và implement_mode khác null | Sửa code khi plan chưa duyệt; tự chọn mode thay user; bắt user nhắn thêm một turn nữa mới build |
| `implement` | plan_approved = true và implement_mode đã chốt | Làm hết plan trong 1 turn, mỗi task đánh [~] khi bắt đầu, red→green, đổi [x] ngay khi pass | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=qc` | Mọi task trong plan đã tick [x] | Dừng giữa chừng; gom tick vào cuối turn; để nhiều task cùng mang [~] |
| `qc` | Đã implement xong | Chạy Definition of Done của spec, ghi kết quả, fail thì fix tiếp | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=report` | Mọi mục QC trong spec PASS, có bằng chứng | Bỏ qua test fail; báo PASS khi chưa chạy |
| `report` | QC đã PASS | Viết report ngắn gọn (khuyến nghị 10-20 dòng, không giới hạn cứng) rồi hỏi user có commit không | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=idle` | Report đã ghi và user đã được hỏi về commit | Tự commit hoặc push khi user chưa yêu cầu |
| `idle` | Đã xong hoặc chưa mở request | Chờ yêu cầu mới từ user | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" init <YYYY-MM-DD-slug> <quick\|full>` | Có request mới được mở | Đè request cũ còn dở mà chưa hỏi user |
| `quick` | lane = quick | Phân tích → mini-spec/plan gộp 1 file → chờ duyệt → ghi working log TRƯỚC → implement → QC bám DoD (mặc định BẬT) → vòng fix nếu FAIL | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve quick [--no-qc] --by "<nguyên văn câu user>"` | quick_approved = true, log đã ghi, mục ## QC trong plan đã có (bằng chứng hoặc dòng BỎ theo yêu cầu user), không còn test đỏ, phase đã về idle | Implement trước khi ghi working log; đóng việc khi còn test đỏ hoặc còn bug đã biết; chạy set phase=idle khi đã vượt trần 3 vòng fix mà chưa báo user |

Lệnh nguyên văn (copy được, không có ký tự thoát):

```
no_state: python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" init <YYYY-MM-DD-slug> <quick|full>
analyze: python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=spec
spec: python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve spec --by "<nguyên văn câu user>"
plan: python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve plan --mode <main|subagent> --by "<nguyên văn>"
implement: python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=qc
qc: python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=report
report: python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=idle
idle: python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" init <YYYY-MM-DD-slug> <quick|full>
quick: python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve quick [--no-qc] --by "<nguyên văn câu user>"
```

Checklist chi tiết của phase đang chạy: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" next`.
