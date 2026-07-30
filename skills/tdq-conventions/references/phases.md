# Bảng phase TDQ (tự sinh — KHÔNG sửa tay)

Sinh lại: `python3 scripts/tdq_state.py phases-doc > <file>`.
Nguồn: hằng `PHASE_TABLE` trong `scripts/tdq_state.py`.
Đang ở phase nào thì chỉ làm đúng việc của phase đó, xong chạy đúng lệnh của nó.

| phase | vào khi | việc duy nhất | lệnh chuyển tiếp | xong khi | cấm |
|---|---|---|---|---|---|
| `no_state` | Chưa có request TDQ nào đang mở | Hỏi user chọn lane rồi mở request mới | `python3 scripts/tdq_state.py init <YYYY-MM-DD-slug> <quick\|full>` | state.json có active_request và lane | Sửa code khi chưa mở request |
| `analyze` | Đã có request, lane full | Đọc code, research, interview user đến khi hết chỗ mơ hồ | `python3 scripts/tdq_state.py set phase=spec` | Không còn câu hỏi nào làm thay đổi kết quả | Viết spec khi chưa hết mơ hồ |
| `spec` | Đã phân tích xong | Viết spec, đăng ký spec_file, trình tóm tắt rồi DỪNG chờ user duyệt | `python3 scripts/tdq_state.py approve spec --by "<nguyên văn câu user>"` | spec_approved = true | Viết plan trong cùng turn với spec; tự suy diễn là user đã duyệt |
| `plan` | spec_approved = true | Hỏi mode thực thi, viết plan, đăng ký plan_file, trình rồi DỪNG chờ duyệt | `python3 scripts/tdq_state.py approve plan --mode <main\|subagent\|external> --by "<nguyên văn>"` | plan_approved = true và implement_mode khác null | Sửa code khi plan chưa duyệt; tự chọn mode thay user |
| `implement` | plan_approved = true và implement_mode đã chốt | Làm hết plan trong 1 turn, mỗi task red→green, tick [x] ngay khi pass | `python3 scripts/tdq_state.py set phase=qc` | Mọi task trong plan đã tick [x] | Dừng giữa chừng; gom tick vào cuối turn |
| `qc` | Đã implement xong | Chạy Definition of Done của spec, ghi kết quả, fail thì fix tiếp | `python3 scripts/tdq_state.py set phase=report` | Mọi mục QC trong spec PASS, có bằng chứng | Bỏ qua test fail; báo PASS khi chưa chạy |
| `report` | QC đã PASS | Viết report ≤50 dòng rồi hỏi user có commit không | `python3 scripts/tdq_state.py set phase=idle` | Report đã ghi và user đã được hỏi về commit | Tự commit hoặc push khi user chưa yêu cầu |
| `idle` | Đã xong hoặc chưa mở request | Chờ yêu cầu mới từ user | `python3 scripts/tdq_state.py init <YYYY-MM-DD-slug> <quick\|full>` | Có request mới được mở | Đè request cũ còn dở mà chưa hỏi user |
| `quick` | lane = quick | Trình mini-plan ≤10 dòng → chờ duyệt → ghi working log TRƯỚC → rồi mới implement | `python3 scripts/tdq_state.py approve quick --by "<nguyên văn câu user>"` | quick_approved = true, log đã ghi, việc đã validate | Implement trước khi ghi working log |

Lệnh nguyên văn (copy được, không có ký tự thoát):

```
no_state: python3 scripts/tdq_state.py init <YYYY-MM-DD-slug> <quick|full>
analyze: python3 scripts/tdq_state.py set phase=spec
spec: python3 scripts/tdq_state.py approve spec --by "<nguyên văn câu user>"
plan: python3 scripts/tdq_state.py approve plan --mode <main|subagent|external> --by "<nguyên văn>"
implement: python3 scripts/tdq_state.py set phase=qc
qc: python3 scripts/tdq_state.py set phase=report
report: python3 scripts/tdq_state.py set phase=idle
idle: python3 scripts/tdq_state.py init <YYYY-MM-DD-slug> <quick|full>
quick: python3 scripts/tdq_state.py approve quick --by "<nguyên văn câu user>"
```

## no_state
1. Tóm tắt yêu cầu của user thành 3–5 dòng
2. Hỏi user chọn lane: quick (việc nhỏ, rõ) hay full (Analysis→Spec→Plan→Implement→QC→Report)
3. Chạy lệnh init ở trên với slug theo công thức YYYY-MM-DD-<kebab ≤5 từ, không dấu>
4. Ghi yêu cầu nguyên văn vào docs/tdq/requests/<slug>.md

## analyze
1. Kiểm kê năng lực (B0): chạy ``\1`
2. Đọc code/doc liên quan, ghi vào docs/tdq/research/<slug>.md
3. Hỏi user mọi điểm chưa rõ, ghi vào docs/tdq/questions/<slug>.md
4. Chốt quyết định vào docs/tdq/knowledge/<slug>.md
5. Hết câu hỏi làm đổi kết quả → chạy lệnh trên

## spec
1. Viết docs/tdq/spec/<slug>.md (scope in/out, đầu ra, QC + DoD)
2. Chạy: `\1`
3. Trình tóm tắt spec ≤50 dòng trong chat
4. In: ➤ Duyệt: nhắn "duyệt spec" · Góp ý: nhắn trực tiếp — rồi DỪNG
5. User duyệt → chạy lệnh approve ở trên

## plan
1. Hỏi user mode thực thi: main (tự làm) / subagent (chia worktree) / external (giao codex|agy qua worktree)
2. Viết docs/tdq/plan/<slug>.md: mỗi task 1 việc + 1 test, có checkbox [ ]
3. Chạy: `\1`
4. Trình tóm tắt plan, in dòng mời duyệt, rồi DỪNG
5. User duyệt → chạy lệnh approve ở trên

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
1. Viết docs/tdq/reports/<slug>.md ≤50 dòng: đã làm gì, kết quả QC, giới hạn còn lại
2. Append working log docs/workinglog/<hôm nay>.md
3. Hỏi user: có commit không?

## idle
1. Có yêu cầu mới → tóm tắt, hỏi lane, chạy lệnh init ở trên

## quick
1. Trình mini-plan ≤10 dòng: việc sẽ làm, file sẽ đụng, cách validate, kèm 1 dòng 'Năng lực: <skill sẽ DÙNG hoặc không có>'
2. In: ➤ Duyệt: nhắn "duyệt quick" · Góp ý: nhắn trực tiếp — rồi DỪNG
3. User duyệt → chạy lệnh approve ở trên
4. Append summary plan vào docs/workinglog/<hôm nay>.md TRƯỚC khi sửa code
5. Implement + validate, rồi cập nhật working log
