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
| `implement` | plan_approved = true và implement_mode đã chốt | Làm hết plan trong 1 turn, mỗi task red→green, tick [x] ngay khi pass | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=qc` | Mọi task trong plan đã tick [x] | Dừng giữa chừng; gom tick vào cuối turn |
| `qc` | Đã implement xong | Chạy Definition of Done của spec, ghi kết quả, fail thì fix tiếp | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=report` | Mọi mục QC trong spec PASS, có bằng chứng | Bỏ qua test fail; báo PASS khi chưa chạy |
| `report` | QC đã PASS | Viết report ngắn gọn (khuyến nghị 10-20 dòng, không giới hạn cứng) rồi hỏi user có commit không | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=idle` | Report đã ghi và user đã được hỏi về commit | Tự commit hoặc push khi user chưa yêu cầu |
| `idle` | Đã xong hoặc chưa mở request | Chờ yêu cầu mới từ user | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" init <YYYY-MM-DD-slug> <quick\|full>` | Có request mới được mở | Đè request cũ còn dở mà chưa hỏi user |
| `quick` | lane = quick | Phân tích → mini-spec/plan gộp 1 file → chờ duyệt → ghi working log TRƯỚC → implement → QC 3 hạng mục (mặc định BẬT) → vòng fix nếu FAIL | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" approve quick [--no-qc] --by "<nguyên văn câu user>"` | quick_approved = true, log đã ghi, mục ## QC trong plan đã có (bằng chứng hoặc dòng BỎ theo yêu cầu user), không còn test đỏ, phase đã về idle | Implement trước khi ghi working log; đóng việc khi còn test đỏ hoặc còn bug đã biết; chạy set phase=idle khi đã vượt trần 3 vòng fix mà chưa báo user |

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

## no_state
1. Tóm tắt yêu cầu của user thành 3–5 dòng
2. Hỏi user chọn lane: quick (việc nhỏ, rõ) hay full (Analysis→Spec→Plan→Implement→QC→Report)
3. Chạy lệnh init ở trên với slug theo công thức YYYY-MM-DD-<kebab ≤5 từ, không dấu>
4. Ghi yêu cầu nguyên văn vào docs/tdq/requests/<slug>.md

## analyze
1. Kiểm kê năng lực (B0): chạy `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/skill_inventory.py"`, điền bảng phán quyết vào docs/tdq/knowledge/<slug>.md mục 'Năng lực dùng được'
2. Đọc code/doc liên quan, ghi vào docs/tdq/research/<slug>.md
3. Hỏi user mọi điểm chưa rõ, ghi vào docs/tdq/questions/<slug>.md
4. Chốt quyết định vào docs/tdq/knowledge/<slug>.md
5. Hết câu hỏi làm đổi kết quả → chạy lệnh trên

## spec
1. Viết docs/tdq/spec/<slug>.md (scope in/out, đầu ra, Lộ trình, QC + DoD)
2. Chạy: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set spec_file=docs/tdq/spec/<slug>.md`
3. Trình tóm tắt spec ≤50 dòng trong chat
4. In: ➤ Duyệt: nhắn "duyệt spec" · Góp ý: nhắn trực tiếp — rồi DỪNG
5. User duyệt → chạy lệnh approve ở trên NGAY, rồi viết plan trong CÙNG turn (không bắt user nhắn thêm câu nào)

## plan
1. ĐỀ XUẤT mode thực thi ngay trong plan (main|subagent) + lý do — không hỏi riêng một lượt; user chốt mode lúc duyệt
2. Viết docs/tdq/plan/<slug>.md: mỗi task 1 việc + 1 test, có checkbox [ ]
3. Chạy: `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set plan_file=docs/tdq/plan/<slug>.md`
4. Trình tóm tắt plan, in dòng mời duyệt kèm mode đề xuất, rồi DỪNG
5. User duyệt kèm mode → chạy lệnh approve ở trên NGAY, rồi build trong CÙNG turn

## implement
1. Làm task theo đúng thứ tự trong plan
2. Mỗi task: viết test (đỏ) → code → test xanh → tick [x] vào plan NGAY
3. Không dừng giữa chừng để hỏi 'có tiếp không'
4. Xong hết task → chạy lệnh trên

## qc
1. Chạy đủ mục QC trong spec, ghi bằng chứng vào docs/tdq/qc/<slug>.md
2. FAIL → thêm task fix vào plan (không cần duyệt lại) rồi làm tiếp
3. Lặp đến khi mọi mục PASS

## report
1. Viết docs/tdq/reports/<slug>.md ngắn gọn (khuyến nghị 10-20 dòng): đã làm gì, kết quả QC, giới hạn còn lại
2. Append working log docs/workinglog/<hôm nay>.md
3. Hỏi user: có commit không?

## idle
1. Có yêu cầu mới → tóm tắt, hỏi lane, chạy lệnh init ở trên

## quick
1. Phân tích: đọc code liên quan; có ẩn số bên ngoài (thư viện, API, phiên bản) → web search qua tavily-primary trước khi viết gì
2. Interview khi còn câu hỏi làm ĐỔI kết quả — theo luật interview.md, kết thúc mỗi vòng bằng câu 'Bạn muốn bổ sung thêm gì không?'
3. Viết mini-spec/plan GỘP vào docs/tdq/plan/<slug>.md (≤40 dòng: scope in/out, task có test, DoD) rồi trình tóm tắt ≤10 dòng trong chat, kèm 1 dòng 'Năng lực: <skill sẽ DÙNG hoặc không có>'
4. In: ➤ Duyệt: nhắn "duyệt quick" (bỏ QC: "duyệt quick không QC") · Góp ý: nhắn trực tiếp — rồi DỪNG
5. User duyệt → chạy lệnh approve ở trên (--no-qc CHỈ khi user nói rõ bỏ QC, im lặng về QC = CÓ QC)
6. Append summary plan vào docs/workinglog/<hôm nay>.md TRƯỚC khi sửa code
7. Implement từng task red→green, tick [x] ngay khi task pass
8. QC 3 hạng mục — test từng task pass · đối chiếu TỪNG dòng DoD · biên và đường lỗi cơ bản (input rỗng, sai kiểu, file thiếu) — ghi bằng chứng vào mục ## QC của plan; quick_qc_skipped = true thì mục ## QC chỉ có 1 dòng 'BỎ theo yêu cầu user: "<nguyên văn>"'
9. QC FAIL hoặc thấy bug → BẮT BUỘC fix (không opt-out được, kể cả khi bỏ QC): thêm task vào mục ## QC vòng N — fix của plan, fix xong chạy lại ĐỦ 3 hạng mục; trần 3 vòng, vượt trần thì DỪNG báo user và đề xuất chuyển lane full
10. Đóng việc: chạy `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/tdq_state.py" set phase=idle` — terminal của lane quick
