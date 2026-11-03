# SPEC — Trình bày lại full chat sau khi bị hook chặn

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-13 · Bản: 1.0 · Brief: ../brief/2026-08-13-trinh-lai-sau-hook-chan.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: khi turn còn chạy tiếp sau lúc đã in khối user-facing (bị hook chặn, tự phát
  hiện thiếu việc, lỗi tool), message cuối cùng của turn phải chứa **nguyên văn 100%**
  khối đó, để focus mode (chỉ hiện message cuối) không làm user mất câu hỏi và option.
- Trong phạm vi: (a) thêm luật "in lại nguyên văn" vào `skills/tdq-conventions/SKILL.md`
  §1; (b) sửa câu `reason` của hai điểm chặn trong `hooks/scripts/stop_gate.py` để chính
  lời chặn ra lệnh in lại; (c) bổ sung test cho câu `reason` mới.
- NGOÀI phạm vi: `hooks/scripts/edit_gate.py` và `bash_gate.py` — hai hook này chặn ở
  PreToolUse (giữa turn), model vẫn in khối user-facing sau đó nên không gây ẩn.
  Không đổi điều kiện chặn, không đổi thời điểm chặn của `stop_gate.py` — chỉ đổi câu chữ
  trong `reason`. Không sửa các skill con `tdq-*` (đã nạp `tdq-conventions`, tự thừa hưởng).

## 1b. Lộ trình
Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Thuần nội bộ: hành vi focus mode đã có trong system prompt, cơ chế hook đọc thẳng mã nguồn |
| Interview | XONG | 1 vòng, 3 câu, user chốt "1A 2A 3A"; không còn câu làm đổi kết quả |
| spec → plan → implement → report | CÓ | Khung bất biến |
| QC độc lập (agent `tdq-qc-tester`) | BỎ | 2 file, kiểm bằng `doc_lint` + `pytest` là đủ; QC ở main chạy được cùng lệnh |
| Chia subagent lúc implement | BỎ | 2 file liên quan chặt nhau, chia ra tốn hơn làm thẳng |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Luật "in lại nguyên văn khối user-facing" | `skills/tdq-conventions/SKILL.md` §1 | `doc_lint.py` exit 0 và văn bản nêu đủ 3 ý: khi nào in lại, in lại cái gì, đặt ở đâu |
| 2 | `reason` mới của điểm chặn `[TDQ:LOG]` | `hooks/scripts/stop_gate.py` | Chuỗi chứa `tdq_finish.py` và cụm `in LẠI NGUYÊN VĂN`; độ dài ≤ 300 ký tự |
| 3 | `reason` mới của điểm chặn `[TDQ:TICK]` | `hooks/scripts/stop_gate.py` | Chuỗi chứa cụm `in LẠI NGUYÊN VĂN`; độ dài ≤ 300 ký tự |
| 4 | Test cho hai `reason` mới | `tests/test_stop_gate.py` | `python3 -m pytest tests/test_stop_gate.py` exit 0, có test tên chứa `reprint` |

## 3. Cách tiếp cận & lý do
- Chọn: hai lớp cùng lúc (user chốt 1A = V3). Lớp quy ước ghi ở `tdq-conventions` để mọi
  skill thừa hưởng; lớp hook nhét mệnh lệnh vào chính câu `reason` — câu này được harness
  chèn thẳng vào ngữ cảnh ĐÚNG lúc bị chặn, nên khó bị bỏ qua hơn văn bản skill.
- Vì: request `2026-08-13-fix-cau-hoi-focus-mode` chỉ có lớp quy ước phòng ngừa và đã bị
  quên 2 lần ngay trong phiên đó. Lớp quy ước một mình không đủ.
- Nhân tiện sửa một mâu thuẫn tồn đọng: `reason` hiện tại của `[TDQ:LOG]` vẫn bảo "Thêm
  mục `## HH:MM — <việc>` ở CUỐI file", trái với luật mới cấm Edit tay working log. Thay
  bằng lệnh `tdq_finish.py`. Việc thay này còn giúp câu ngắn lại, đủ chỗ cho mệnh lệnh mới.
- Đã loại: chỉ sửa quy ước (V1) — user từ chối, vì đó đúng là phương án đã thất bại.
  Chỉ sửa hook (V2) — user từ chối, vì hook chỉ nói lúc bị chặn, không dạy được luật chung.
  Lưu khối user-facing ra file tạm để hook đọc và trả lại — loại vì vẫn phải nhớ ghi file,
  cùng điểm yếu "phải nhớ" như V1, mà thêm hẳn một file trạng thái phải bảo trì.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions, tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-status | plugin:tdq-workflow | NỀN | chính workflow đang chạy |
| Đã xét toàn bộ skill còn lại trong kiểm kê | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — không tạo runtime mới. `stop_gate.py` đã có sẵn `_info` ghi lý do mỗi
  lần chặn (dòng 138, 157); phần sửa chỉ đụng câu chữ `reason`, không đụng đường log đó.
- Không placeholder: câu chữ mới phải nêu HÀNH ĐỘNG cụ thể (in lại cái gì, đặt ở đâu),
  không nói chung chung "nhớ trình bày lại".
- Test: đầu ra #2 và #3 có test trong `tests/test_stop_gate.py`, chạy bằng một lệnh
  `python3 -m pytest tests/test_stop_gate.py`.

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| `reason` dài quá trần 300 ký tự nêu ở docstring `stop_gate.py` | Lời chặn bị coi là vi phạm quy ước của chính repo | Đã đo trước: bản mới `[TDQ:LOG]` 267 ký tự, `[TDQ:TICK]` 191 ký tự; DoD có hạng mục đo lại bằng lệnh |
| Test hiện có so khớp nguyên văn `reason` cũ sẽ đỏ | `pytest` fail sau khi sửa | Chạy cả `tests/test_stop_gate.py` lẫn `tests/test_compliance_protocol.py`, `tests/test_hook_resilience.py`, `tests/test_e2e_chain.py` (4 file có nhắc `stop_gate`), sửa chỗ so khớp cứng |
| Luật mới vẫn không có máy ép: model có thể in lại thiếu | Vẫn tái diễn ẩn nội dung | Chấp nhận có ý thức — hook nhắc đúng lúc là mức ép mạnh nhất khả thi mà không cần harness hỗ trợ |
| `skills/tdq-conventions/SKILL.md` đang sát trần 120 dòng của `doc_lint` R6 | Không thêm được chữ | Viết luật mới cô đọng, cắt chữ thừa ở §1 nếu cần; DoD có `doc_lint` exit 0 |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Luật mới có mặt và đủ ý (đầu ra #1) | Đọc `skills/tdq-conventions/SKILL.md` §1 | Nêu đủ 3 ý: khi nào in lại · in lại nguyên văn khối nào · đặt SAU dòng `✓ [TDQ:<MÃ>]` |
| Q2 | `doc_lint` trên file skill đã sửa | `python3 scripts/doc_lint.py skills/tdq-conventions/SKILL.md` | exit 0 |
| Q3 | Hai `reason` mới đúng nội dung (đầu ra #2, #3) | `grep -c "in LẠI NGUYÊN VĂN" hooks/scripts/stop_gate.py` | ra `2` |
| Q4 | Hai `reason` mới trong trần 300 ký tự | `python3 -m pytest tests/test_stop_gate.py -k reprint` | exit 0 |
| Q5 | Không làm đỏ test cũ | `python3 -m pytest tests/ -q` | exit 0 |

DoD: Q1–Q5 PASS; `stop_gate.py` không đổi điều kiện/thời điểm chặn (chỉ đổi câu `reason`);
report tổng kết đúng 10–20 dòng.

## 7. Câu hỏi còn mở
(rỗng)
