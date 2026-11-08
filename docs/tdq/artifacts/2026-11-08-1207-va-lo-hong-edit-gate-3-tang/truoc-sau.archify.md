# Trước/Sau — Vá lỗ hổng gate 3 tầng {#tong-quan}

@meta locale=vi

Sự cố play3clone 2026-11-08: user nhắn "1a", agent tự `approve spec`, tự `approve plan` rồi sửa `server/index.js` trong cùng một lượt. Bản vá chặn ở 3 chỗ; full fresh 4202 test PASS.

## Trước: hook chỉ nhắc {#truoc}

@workflow id=gate-truoc title="Trước: cổng chưa duyệt vẫn cho qua"
| prompt | User nhắn "1a" — không có cổng chờ, không có signal | backend |
| approve | Agent tự chạy approve spec/plan | security |
| bash | bash_gate: không signal → im lặng | security |
| edit | edit_gate: còn cổng chờ → remind (allow) | security |
| code | Mã nguồn bị sửa | backend |
| prompt > approve |
| approve > bash |
| bash > edit |
| edit > code |

## Sau: hook chặn khi không có lời duyệt của user {#sau}

@workflow id=gate-sau title="Sau: một prompt của user mở đúng một cổng"
| prompt | prompt_context ghi turn_start + signal | backend |
| bash | bash_gate: có turn_start, không signal khớp → deny | security |
| edit | edit_gate: còn cổng chờ → deny | security |
| ok | User duyệt thật → signal khớp → cho qua | backend |
| prompt > bash |
| bash > edit |
| edit > ok |

Lane quick: `quick_analyze` giờ chỉ lệnh kế là `approve quick`, không còn `set phase=implement` trước duyệt.

Host không có hook UserPromptSubmit (không `turn_start`) vẫn chỉ nhắc để không kẹt. `set phase=implement` khi plan đã duyệt (vòng fix QC) không bị chặn. Nguồn: `hooks/scripts/edit_gate.py`, `hooks/scripts/bash_gate.py`, `scripts/tdq_state.py` (`PHASE_TABLE["quick_analyze"]`), `skills/tdq-intake/references/quick-lane.md` bước 2.
