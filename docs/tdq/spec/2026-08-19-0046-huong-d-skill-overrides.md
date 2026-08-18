# SPEC — Hướng D: cắt token mô tả skill trong system prompt

Ngày: 2026-08-19 · Bản: 1.0 · Brief: ../brief/2026-08-19-0046-huong-d-skill-overrides.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi
- Mục tiêu: giảm token mô tả skill trong system prompt bằng hai đòn bẩy cấu hình — D1
  (`skillOverrides` cho 33 skill nguồn `user`) và D2 (`skillListingMaxDescChars: 300`) —
  đồng thời SỬA lại đề án `de-an-toi-uu-context.md` vì con số 87,7% ghi ở đó không đúng.
- Trong phạm vi: sinh lại file đề xuất `skillOverrides` chỉ còn khoá có tác dụng thật;
  backup rồi ghi `~/.claude/settings.json`; ghi mục đính chính vào đề án; report.
- NGOÀI phạm vi: D3 (tắt hẳn plugin qua `/plugin`) — user chọn 1A, không làm. Hướng C, B,
  A(hybrid), E — mỗi hướng một request riêng, user đã chốt tách theo thứ tự. Không sửa
  một dòng nào trong `skills/`, `scripts/`, `hooks/`.

## 1b. Lộ trình
Chép từ brief mục `### Lộ trình`.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã xong ở analyze) | phát hiện `skillOverrides` không áp cho plugin skill |
| Đo lại bằng số thật | CÓ (đã xong ở analyze) | con số đề án cũ sai, phải đo lại trước khi làm |
| Vòng scope | CÓ (đã làm ở chat) | user chốt 1A + 2A |
| Interview chi tiết thêm | BỎ | không còn câu hỏi nào đổi kết quả |
| QC độc lập (agent) | BỎ | sửa cấu hình, kiểm bằng lệnh đo lại là đủ |
| Chia subagent | BỎ | một module cấu hình, không tách được |

## 2. Đầu ra cụ thể
| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Bản backup settings trước khi sửa | `docs/tdq/audit/settings-backup-2026-08-19.json` | file tồn tại, parse được JSON, khớp md5 bản gốc |
| 2 | File đề xuất `skillOverrides` chỉ còn khoá có tác dụng | `docs/tdq/audit/skill-overrides-de-xuat.json` (ghi đè bản 261 khoá) | đúng 33 khoá, mọi khoá có nguồn `user` |
| 3 | `~/.claude/settings.json` đã áp D1 + D2 | `~/.claude/settings.json` | có `skillListingMaxDescChars: 300`; `skillOverrides` chứa 33 khoá mới + giữ `unity-skills` sẵn có; JSON parse được |
| 4 | Mục đính chính trong đề án | `docs/tdq/audit/de-an-toi-uu-context.md` | có mục "Đính chính 2026-08-19", ghi rõ 87,7% sai và số đúng |
| 5 | Report | `docs/tdq/reports/2026-08-19-0046-huong-d-skill-overrides.md` | file tồn tại, `doc_lint` exit 0 |

## 2b. Ranh giới module
Một module cấu hình — cả 5 đầu ra cùng một chuỗi phụ thuộc tuyến tính (backup → sinh file
đề xuất → ghi settings → đính chính đề án → report), không có nhánh nào chạy song song được.

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| cấu hình + tài liệu | `~/.claude/settings.json`, `docs/tdq/audit/`, `docs/tdq/reports/` | không | 1, 2, 3, 4, 5 |

## 3. Cách tiếp cận & lý do
- Chọn: giữ nguyên cấu trúc đề án cũ, **thêm mục đính chính** thay vì sửa đè con số 87,7%
  — để lại dấu vết vì sao số cũ sai (dựa trên giả định `skillOverrides` áp cho mọi skill).
- Chọn trần 300 ký tự cho `skillListingMaxDescChars`: tiết kiệm 9.814 token (32,9%), 47
  skill mất phần đuôi liệt kê cụm từ kích hoạt — nhưng 6 skill `tdq-*` không bị chạm,
  đường search thật (MCP tool `mcp__tavily-primary__*`) không đi qua skill listing nên
  không ảnh hưởng, và 45/47 skill bị cắt thuộc lĩnh vực không dùng trong dự án này.
- Chọn ghi trực tiếp vào settings (user duyệt 2A) kèm backup vào repo — có backup thì
  đảo ngược là chép lại một file, không phụ thuộc trí nhớ.
- Đã loại: D3 tắt hẳn plugin — user không chọn, và mất hẳn năng lực là thiệt hại không
  đảo ngược bằng một dòng cấu hình như hai đòn bẩy kia.
- Đã loại: sửa đè con số 87,7% trong đề án — mất dấu vết vì sao sai, lần sau dễ sai lại.

## 3b. Năng lực & công cụ
| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-spec`, `tdq-plan`, `tdq-build` | plugin:tdq-workflow | DÙNG | chạy phase tương ứng |
| `tdq-conventions` | plugin:tdq-workflow | NỀN | skill khung |
| `scripts/skill_tokens.py` | project | DÙNG | đo token mô tả, kiểm số trước/sau |
| Đã xét 280+ skill khác | plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc
- Log service: BỎ — không tạo/sửa file mã nguồn chạy được; chỉ cấu hình + tài liệu.
- Không placeholder, không TODO stub.
- **Backup trước khi ghi settings** — không có backup thì cấm ghi.
- Giữ nguyên mọi khoá sẵn có trong settings, kể cả `unity-skills` user tự đặt trước đó.
- Không áp SOLID/rule ngôn ngữ — không có code trong phạm vi.

## 5. Ràng buộc & rủi ro
Ràng buộc kiến trúc phải giữ: không sửa `skills/`, `scripts/`, `hooks/` — request này chỉ
chạm cấu hình ngoài repo và tài liệu trong `docs/tdq/`.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Ghi hỏng `~/.claude/settings.json` làm Claude Code không mở được phiên | chặn toàn bộ công việc của user trên mọi project | backup trước; ghi bằng `json.dump` từ dict đã parse, không sửa chuỗi; parse lại file sau khi ghi để xác nhận hợp lệ |
| Cắt mô tả 300 ký tự làm model chọn sai skill | sai trục chất lượng — trục cao nhất theo soul | đã đo: 47 skill bị chạm, 45 thuộc lĩnh vực không dùng, `tdq-*` và đường MCP tavily không ảnh hưởng; đảo ngược bằng xoá 1 dòng |
| `skillOverrides`/`skillListingMaxDescChars` không có tác dụng thật (tiền sử issue #50631) | tưởng đã tiết kiệm mà thực tế không | ghi rõ trong report rằng cần kiểm chứng ở PHIÊN MỚI (cấu hình chỉ đọc lúc mở phiên), không tuyên bố đã tiết kiệm khi chưa thấy |
| Đề án cũ tiếp tục bị đọc và tin con số 87,7% | request sau lặp lại sai lầm | mục đính chính đặt ngay tại chỗ, nói thẳng số nào sai và vì sao |

## 6. QC & Definition of Done
| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Có backup settings hợp lệ trước khi ghi | file backup parse được JSON và khớp md5 bản gốc |
| Q2 | File đề xuất chỉ còn khoá có tác dụng | đúng 33 khoá, 100% khoá thuộc nguồn `user` |
| Q3 | Settings sau khi ghi vẫn hợp lệ và đủ khoá | parse được JSON; có `skillListingMaxDescChars` = 300; `skillOverrides` giữ `unity-skills` và có đủ 33 khoá mới; mọi khoá cấp cao sẵn có còn nguyên |
| Q4 | Đề án có mục đính chính, không xoá phần cũ | mục cũ về hướng D còn nguyên, mục đính chính nằm sau và nêu đúng số 8,8% |
| Q5 | Không file mã nguồn nào bị đổi | `git status --short` không liệt kê file nào ngoài `docs/tdq/` |
| Q6 | Report nói rõ điều kiện kiểm chứng còn thiếu | report ghi rõ phải mở phiên mới mới xác nhận được mức tiết kiệm thật |

DoD: 5 đầu ra §2 tồn tại, đạt Q1-Q6, user biết chính xác phải làm gì để xác nhận kết quả
(mở phiên mới) và biết cách đảo ngược nếu không ưng.

## 7. Câu hỏi còn mở
(rỗng)
