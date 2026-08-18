# SPEC — Bịt 3 lỗ hổng tick checkbox ở chế độ chuyên sâu

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-13 · Bản: 1.0 · Brief: ../brief/2026-08-13-ra-soat-tick-che-do-sau.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: hàng rào tick checkbox ở chế độ chuyên sâu (deep) bịt được 3 đường né đã
  xác nhận qua đọc code — không còn cách nào để một loạt task hiện `[x]` cùng lúc mà
  không phản ánh tiến độ thật.
- Trong phạm vi:
  - Chặn "một `[~]` đứng yên xuyên suốt" (đếm số lần sửa mã nguồn kể từ lần checkbox
    đổi gần nhất, vượt ngưỡng thì chặn tiếp).
  - Chặn "nhiều task cùng mang `[~]`" (hiện chỉ có ở văn bản `forbidden`, chưa có code).
  - Đổi luật giao việc mode `subagent`: mỗi lần gọi agent `tdq-implementer` chỉ giao
    đúng 1 task; main agent tick `[x]` ngay sau mỗi báo cáo, trước khi gọi agent kế.
- NGOÀI phạm vi:
  - Không đổi cơ chế mode `main` (đã đúng luật "tick ngay" từ trước).
  - Không đổi lane chế độ nhanh (đã vá ở request `2026-08-12-siet-tick-lane-quick`,
    dùng chung 2 hook nên tự động hưởng bản vá này).
  - Không đổi cơ chế `stop_gate.py` — hai điểm chặn mới nằm ở `edit_gate.py` (chặn
    sớm hơn, đúng chỗ hành vi xảy ra).

## 1b. Lộ trình
| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Thuần nội bộ (hook Python + tài liệu markdown), không ẩn số bên ngoài. |
| Interview | CÓ (đã xong ở phase analyze) | 4 câu về ưu tiên vá và cách vá — user đã chọn A cho cả 4. |
| QC độc lập (agent `tdq-qc-tester`) | BỎ | Việc không lớn/rủi ro cao (theo tiêu chí `tdq-build/references/qc.md`); QC bám DoD trong plan là đủ. |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Chặn "nhiều task cùng `[~]`" | `hooks/scripts/edit_gate.py` | Test mới: plan có ≥2 task `[~]` → sửa mã nguồn bị `deny` kèm `TDQ:TICK`. |
| 2 | Chặn "sửa liên tiếp không tick" | `hooks/scripts/edit_gate.py` | Test mới: 3 lần sửa mã nguồn liên tiếp mà checkbox không đổi → lần thứ 4 bị `deny`. |
| 3 | `plan_tick_state` báo thêm số task đang `[~]` | `scripts/tdq_state.py` | Test mới trong `tests/test_plan_tick.py`: field `doing_count` đúng giá trị đếm được. |
| 4 | Luật giao subagent theo từng task | `skills/tdq-build/SKILL.md`, `skills/tdq-plan/SKILL.md` | Đọc lại: câu "mỗi agent một task, tick ngay sau báo cáo" thay cho "mỗi agent một phase/nhóm task". |
| 5 | Mô tả agent khớp luật mới | `agents/tdq-implementer.md` | Đọc lại: mô tả nhận đúng 1 task, không còn "phase/task-group". |

## 3. Cách tiếp cận & lý do
- Chọn: vá cả 2 điểm ở tầng `edit_gate.py` (PreToolUse, chặn trước khi tool chạy) thay
  vì `stop_gate.py` (Stop, chặn cuối turn) — vì hành vi cần chặn xảy ra NGAY lúc sửa
  code, chặn sớm hơn giữ đúng tinh thần "tick ngay", không đợi tới cuối turn mới báo.
- Cơ chế đếm streak: mỗi lần `edit_gate` cho qua một lần sửa mã nguồn (không phải
  test/docs) mà state hợp lệ (đúng 1 task `[~]`), ghi thêm `observe(kind="code_edit",
  plan_sha=<sha hiện tại>)` vào sổ turn `.tdq-turn.jsonl`. Lần gọi kế tiếp đếm số dòng
  `code_edit` có `plan_sha` TRÙNG với sha hiện tại (tức plan chưa đổi từ lần đó tới
  giờ) — đủ ngưỡng thì chặn. Plan đổi (tick hoặc sửa nội dung) → sha đổi → đếm lại từ 0.
  Vì: tái dùng đúng sổ turn đã có (`_common.observe`/`turn_log_append`), không cần hạ
  tầng lưu trữ mới; nhất quán với cách `stop_gate` đang dùng `plan_sha` để so sánh.
  Đã loại: đếm theo thời gian (giây) — bị loại vì tốc độ sửa code khác nhau theo độ
  phức tạp task, đếm theo số lần sửa ổn định hơn và không cần đồng hồ hệ thống.
- Ngưỡng streak = 3 lần sửa liên tiếp không tick thì chặn ở lần thứ 4. Vì: khớp trần
  "vòng fix" (3 vòng) đã dùng sẵn trong hệ thống, giữ nhất quán con số; đủ rộng để một
  task nhỏ có vài lần sửa/test lặp mà không bị chặn oan.
- Chặn "nhiều task `[~]`": thêm điều kiện `doing_count > 1` vào đúng khối kiểm hiện có
  trong `edit_gate.py` (`tick["exists"] and tick["total"] > 0`), tái dùng thông báo
  `TDQ:TICK` sẵn có, không thêm mã mới. Vì: cùng bản chất lỗi (checkbox không phản ánh
  đúng "đang làm gì"), gộp vào 1 mã nhắc cho gọn.
- Đổi luật subagent: giao đúng 1 task/lần gọi thay vì cả nhóm. Vì: nền tảng Agent
  không hỗ trợ báo cáo giữa chừng (xác nhận qua đọc `agents/tdq-implementer.md:16` —
  subagent bị cấm tự tick, chỉ báo cáo cuối) — muốn tick real-time thì chỉ còn cách
  giảm đơn vị giao việc xuống 1 task, main agent tick ngay khi nhận báo cáo trước khi
  gọi agent tiếp theo.
  Đã loại: giữ giao theo nhóm, subagent ghi log riêng theo từng task để main agent đọc
  giữa chừng — bị loại vì cần hạ tầng đọc file agent con ghi ra mà không chờ nó xong,
  chưa rõ nền tảng có hỗ trợ đáng tin cậy; phức tạp hơn hẳn so với lợi ích.

## 3b. Năng lực & công cụ
Đã xét 200+ skill qua `python3 scripts/skill_inventory.py` (toàn bộ thuộc mảng
Unity/Figma/Canva/Adobe/hạ tầng ngoài…), không skill nào áp cho việc sửa hook Python +
tài liệu markdown nội bộ.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| Đã xét 200+ skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — việc này sửa hook nội bộ và tài liệu markdown, không tạo runtime
  service mới; log hiện có của hook (`tdq_state._info`/`_warn`) giữ nguyên, không đổi.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh
  (`.venv/bin/python -m pytest tests/test_edit_gate.py tests/test_plan_tick.py -q`).

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Ngưỡng streak=3 chặn oan task hợp lệ có nhiều lần sửa nhỏ trong 1 task (ví dụ sửa test rồi sửa code nhiều vòng nhỏ) | Gián đoạn công việc, phải tick task dở để né chặn | `tests/**` đã miễn trừ hoàn toàn khỏi mọi đếm/chặn (giữ nguyên luật cũ); nếu QC thực tế thấy chặn oan → tăng ngưỡng ở vòng fix, không đổi kiến trúc |
| Đổi luật subagent xuống 1 task/lần gọi làm build chậm hơn (nhiều lượt gọi agent hơn) | Chế độ chuyên sâu mất lợi thế song song theo phase | Chấp nhận đánh đổi — user đã chọn ưu tiên tick đúng nhịp hơn tốc độ, ghi rõ trong spec §1 |
| `edit_gate.py` đang được cả 2 lane (nhanh + chuyên sâu) dùng chung — sửa sai có thể phá cả lane nhanh | Chặn oan/lọt cả nơi không định sửa | Chạy lại toàn bộ `tests/test_edit_gate.py` (gồm cả class cũ của lane nhanh) sau khi sửa, không chỉ test mới |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Chặn nhiều task `[~]` | `.venv/bin/python -m pytest tests/test_edit_gate.py -q -k doing` | Test mới xanh |
| Q2 | Chặn sửa liên tiếp không tick | `.venv/bin/python -m pytest tests/test_edit_gate.py -q -k streak` | Test mới xanh |
| Q3 | `doing_count` đúng | `.venv/bin/python -m pytest tests/test_plan_tick.py -q` | Xanh, gồm test mới |
| Q4 | Không phá test cũ của `edit_gate`/`stop_gate` | `.venv/bin/python -m pytest tests/test_edit_gate.py tests/test_stop_gate.py -q` | Toàn bộ xanh |
| Q5 | Tài liệu subagent nhất quán | Đọc `tdq-build/SKILL.md`, `tdq-plan/SKILL.md`, `agents/tdq-implementer.md` | Cả 3 file cùng nói "1 task/1 lần gọi agent, tick ngay" |
| Q6 | Full suite không hồi quy | `.venv/bin/python -m pytest -q` | Toàn bộ xanh, không giảm số test so với trước |

DoD: Q1–Q6 đều PASS có bằng chứng (lệnh + output thật) ghi vào `docs/tdq/qc/<slug>.md`.

## 7. Câu hỏi còn mở
(Rỗng.)
