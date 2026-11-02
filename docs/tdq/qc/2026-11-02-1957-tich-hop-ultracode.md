# QC — Tích hợp Ultracode vào TDQ Workflow
Ngày: 2026-11-02 · Plan: ../plan/2026-11-02-1957-tich-hop-ultracode.md · Vòng: 2
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

| # | Hạng mục | Bằng chứng | Kết quả |
|---|---|---|---|
| Q1 | Suffix routing canonical | `pytest test_ultracode_routing -k lane` | PASS |
| Q2 | Express hữu hạn, một gate | `pytest test_ultracode_routing -k express` | PASS |
| Q3 | Deep không state/gate mới | `pytest test_ultracode_routing -k deep` | PASS |
| Q4 | State/Git/worktree ownership | contract + team-mode tests | PASS |
| Q5 | Edit/Bash mutation gate | 91 gate tests + 73 subtests; false-positive/bypass fix | PASS |
| Q6 | Completion accounting | contract tests; incomplete receipt=`complete=false` | PASS |
| Q7 | No ceiling, finite run | contract test; không budget loop | PASS |
| Q8 | Ba host | interactive UNSUPPORTED có fallback; `claude -p` PARTIAL; SDK UNSUPPORTED | PASS (trung thực) |
| Q9 | Eval KEEP/DROP | eval-plan valid + report quality-first | PASS có điều kiện |
| Q10 | Full regression | 3.991 test, 5 skip, 0 fail; receipt details_complete=true | PASS |
| Q11 | Ponytail | không script/agent/state/lane/phase/worktree manager mới | PASS |
| QC-F1 | Full suite | receipt `2331af0c12dd4d91943b645bc2fa35d6`, exit 0 | PASS |
| QC-F2 | Vùng chạm | 234 pass + 26 subtests; gate 91 + 73 subtests | PASS |
| QC-F3 | Kiến trúc | TDQ leader duy nhất giữ state/Git; Workflow không native worktree | PASS |
| QC-F4 | Clean code | guard clause trực tiếp, không abstraction/dependency mới | PASS |

## Bằng chứng chính

- Full receipt: `docs/tdq/cache/test-runs/37682fd645624a59/2331af0c12dd4d91943b645bc2fa35d6/result.json` — PASS, 3991 run, 5 skip, 0 failure, exit 0.
- Visual: `docs/tdq/qc/2026-11-02-1957-tich-hop-ultracode-preview.png` — 4 sơ đồ kích thước >0, lang=en, console 0 lỗi.
- Runtime interactive: `docs/tdq/artifacts/2026-11-02-1957-tich-hop-ultracode/runtime-interactive.json` — UNSUPPORTED, structured fallback; không giả PASS.
- Hosts: `runtime-hosts.json` — print PARTIAL, SDK UNSUPPORTED.
- Eval: `eval-report.md` — routing/review KEEP; implement KEEP có điều kiện; token ceiling DROP theo user.
- QC độc lập lần 1 FAIL đã phát hiện Bash false-positive/bypass, receipt inconsistency và reset gap; toàn bộ defect đã sửa, module fail chạy lại 50 pass + 58 subtests.

## Clean-code 5 câu

- SRP: Có — gate chỉ phân loại mutation trước implement.
- OCP: Có — regex/prompt contract mở rộng theo dữ liệu, không nhánh kiến trúc mới.
- LSP: Có — không inheritance; các nhánh giữ cùng deny/allow contract.
- ISP: Có — chỉ dùng payload/state/path cần thiết.
- DIP: Có — tái dùng `block`, TDQ leader, `tdq_team.py`, reviewer/implementer hiện có.

## Lệch spec chờ duyệt

Không có.

## Kết luận

PASS toàn bộ Q1–Q11 và QC-F1–F4. Runtime unsupported được ghi đúng terminal verdict và fallback, không tính PASS giả.
