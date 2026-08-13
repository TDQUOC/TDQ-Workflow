# SPEC — Điều tra & báo cáo: câu hỏi TDQ bị ẩn khi bật focus mode

Ngày: 2026-08-13 · Bản: 1.0 · Brief: ../brief/2026-08-13-focus-mode-an-cau-hoi.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: xác định và trình bày nguyên nhân kỹ thuật khiến câu hỏi lane/interview của
  TDQ workflow bị ẩn khi user bật focus mode (CLI `viewMode: focus` / VS Code
  `claudeCode.focusView`), có nguồn dẫn chứng (đọc code repo + tài liệu chính thức).
- Trong phạm vi: đọc `hooks/scripts/stop_gate.py`, đối chiếu với cơ chế hiển thị focus
  mode (research chính thức), viết báo cáo nguyên nhân.
- NGOÀI phạm vi: sửa `stop_gate.py` hay bất kỳ file skill/hook nào để khắc phục — user
  chỉ yêu cầu điều tra + báo cáo, chưa duyệt hướng sửa. Báo cáo sẽ nêu 1 hướng khắc phục
  khả dĩ như GỢI Ý, không tự triển khai.

## 1b. Lộ trình
Chép từ brief mục `### Lộ trình`.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã chạy) | Cần nguồn chính thức xác nhận đơn vị hiển thị của focus mode, không đoán |
| Interview | BỎ | Đọc code + research đã đủ dữ kiện chốt nguyên nhân, không còn chỗ mơ hồ |
| QC độc lập (agent) | BỎ | Không có code để test — QC bằng tự đọc lại đối chiếu nguồn |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Báo cáo nguyên nhân (root cause) | `docs/tdq/reports/2026-08-13-focus-mode-an-cau-hoi.md` + trình tóm tắt trong chat | Có đủ 3 phần: hiện tượng quan sát, cơ chế gây ra (trích dẫn code + nguồn research), 1 gợi ý hướng khắc phục (không triển khai) |

## 3. Cách tiếp cận & lý do
- Chọn: điều tra thuần đọc code + research tài liệu chính thức (KHÔNG tái hiện bug bằng
  cách bật lại focus mode thử nghiệm, vì không có công cụ chụp lại rendering CLI trong
  session này).
- Vì: `stop_gate.py` (đọc trực tiếp) đã cho thấy rõ điểm chặn Stop; research qua
  `claude-code-guide` xác nhận focus mode hoạt động theo ĐƠN VỊ TURN (chỉ hiện dòng cuối
  mỗi turn) — 2 dữ kiện này khớp đúng hiện tượng user báo (câu hỏi in trước khi hook chặn
  bị gập ẩn, chỉ dòng tóm tắt-ghi-log-xong hiện ra).
- Đã loại: research sâu thêm về "Stop hook block có mở turn mới hay không" ở tầng
  implementation nội bộ Claude Code — vì tài liệu chính thức không công khai chi tiết đó
  ([code.claude.com/docs/en/hooks.md] chỉ nói `additionalContext` được đưa lại cho model
  tiếp tục turn) và hành vi quan sát được (per-turn, chỉ hiện dòng cuối) đã đủ giải thích,
  không cần đào sâu hơn cho mục tiêu "báo cáo nguyên nhân" của request này.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| Đã xét toàn bộ skill trong kiểm kê (`skill_inventory.py`) | user/plugin/built-in | KHÔNG | khác lĩnh vực — việc thuần đọc code hook nội bộ + research hành vi CLI, không khớp domain skill nào (Unity, Figma, Adobe, base44, canva...) |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — việc thuần điều tra + viết báo cáo, không có runtime/mã nguồn chạy được nào được tạo hoặc sửa.
- Không placeholder, không TODO stub — báo cáo phải trích dẫn cụ thể (đường dẫn file:dòng, tên nguồn research), không diễn giải mơ hồ.
- Không áp dụng mục "mỗi thành phần có unit test riêng" — không có code sản xuất trong request này.

## 5. Ràng buộc & rủi ro
| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Không tái hiện được bug trực tiếp trong session (không có công cụ chụp render CLI) | Kết luận dựa suy luận logic thay vì thực nghiệm | Đối chiếu 2 nguồn độc lập (đọc code + tài liệu chính thức + tiền lệ GitHub Issue #50894) trước khi kết luận |
| Tài liệu chính thức không công khai chi tiết "Stop hook block có mở turn mới không" | Báo cáo có 1 khoảng trống nhỏ không chứng minh được 100% | Nêu rõ trong báo cáo đây là điểm không có nguồn chính thức, phần còn lại đã đủ giải thích hiện tượng |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Báo cáo có trích dẫn code thật (đường dẫn:dòng `stop_gate.py`) | Đọc lại report, đối chiếu file | Có ít nhất 1 trích dẫn đường dẫn:dòng cụ thể |
| Q2 | Báo cáo có trích nguồn research chính thức (không bịa) | Đọc lại report, đối chiếu link/nguồn agent trả về | Có ít nhất 1 nguồn (docs.claude.com hoặc GitHub Issue) |
| Q3 | `doc_lint.py` PASS trên report | `python3 scripts/doc_lint.py docs/tdq/reports/2026-08-13-focus-mode-an-cau-hoi.md` | exit 0 |

DoD: report đã viết đủ 3 phần (§2), Q1-Q3 đều PASS, đã trình tóm tắt trong chat cho user.

## 7. Câu hỏi còn mở
(rỗng)
