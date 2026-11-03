# BRIEF — Rà toàn bộ workflow xem đã tối ưu cho LLM chưa

Ngày: 2026-08-14

## Nguyên văn

> okay bây giờ tôi cần mở request để scan toàn bộ workflow và check từng phần xem đã LLM
> optimize chưa, đã tối ưu để optimize runtime, context cost chưa. Yêu cầu bắt buộc phải
> đảm bảo giữ đủ behavior và rule của workflow để đảm bảo output của workflow vẫn giữ đúng
> chất lượng đầy đủ, không đổi quality

**Cách hiểu đầu tiên**

- Mục tiêu: soát từng phần của bộ workflow TDQ (skills, hooks, scripts, agents, portable)
  theo hai trục — (a) prompt/tài liệu đã viết theo kiểu LLM đọc hiệu quả chưa,
  (b) runtime và context cost đã tối ưu chưa — rồi chỉ ra chỗ phí và cách sửa.
- Ràng buộc cứng user nêu: **không được đổi behavior, không được nới rule, chất lượng
  output của workflow phải giữ nguyên**. Mọi đề xuất phải chứng minh được là vô hại.
- Phạm vi đoán: `skills/` 28 file ~1.844 dòng · `hooks/scripts/` 6 file 939 dòng ·
  `scripts/` ~4.759 dòng · `agents/` 58 dòng · `portable/` 12 file.
- Chỗ chưa rõ: request này dừng ở bản đánh giá hay làm luôn phần tối ưu · đo bằng gì
  (token thật hay ước lượng) · có được đổi cấu trúc file skill không · phạm vi có gồm
  `scripts/` và `portable/` không.

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Phán quyết | Vì sao |
|---|---|---|
| skill `tdq-*` (6) | NỀN | vừa là khung chạy request, vừa là đối tượng bị soát |
| `scripts/context_surface.py` | DÙNG | công cụ sẵn có, đo đúng hai câu hỏi của request: tầng nạp + ms mỗi hook |
| `scripts/token_audit.py` | DÙNG | đo carry-cost token thật từ transcript, không phải ước lượng |
| `scripts/skill_inventory.py` | DÙNG (và là đối tượng nghi vấn) | output 39.722 ký tự — xem đo bên dưới |
| `tavily-search` | DÙNG | có ẩn số ngoài: hướng dẫn viết skill/prompt cho LLM đã đổi từ lần audit trước |
| `graphify` | DÙNG cuối turn | nếu có sửa `scripts/`, `hooks/` |
| `mem0-memory` | DÙNG | chốt xong ghi 1 fact |
| plugin Unity/figma/canva/cloudflare/mongodb… | KHÔNG | khác lĩnh vực |

### Đã đo (lệnh thật, 2026-08-14)

| Vùng | Số đo |
|---|---|
| Bề mặt tài liệu | `skills/` 28 file ≈ 112 KB · `portable/` 12 file · `agents/` 3 file |
| Luôn nạp (description) | 6 skill + 3 agent ≈ 2.040 ký tự ≈ 510 token mọi phiên |
| Nạp khi gọi skill (thân) | build 1.936 · conventions 1.820 · intake 1.844 · plan 1.563 · spec 862 · status 449 token |
| Reference nặng nhất | `scope-round.md` 1.658 · `plan-template.md` 1.538 · `quick-lane.md` 1.468 · `phases.md` 1.302 token |
| Hook mỗi lượt | prompt_context 57 ms/128 B · stop_gate 57 ms/0 B · edit_gate 29 ms/402 B · bash_gate 31 ms/0 B · session_start 29 ms/550 B |
| Script trong turn | `skill_inventory` 89 ms nhưng **39.722 ký tự ≈ 9.900 token** đổ thẳng vào context ở bước B0 · `doc_lint` 18 ms · `tdq_state next` 34 ms |
| Đã có 5 vòng tối ưu trước | knowledge 2026-08-04 (×2), 2026-08-05 (×3), 2026-08-08 giảm over-engineer |

### Phạm vi đã chốt

- Mặt CHỌN: chi phí context · cách viết cho LLM · runtime · bằng chứng giữ nguyên
  behavior · **độ tuân thủ của model yếu** (user bổ sung ở vòng scope)
- Mặt LOẠI: chỉ báo cáo suông (không đề xuất cách sửa) · thực thi bản sửa trong request
  này · `scripts/` · `portable/` · `tests/`
- Bối cảnh: dừng ở bản đánh giá + đề xuất · phạm vi `skills/` + `hooks/` + `agents/` ·
  không đặt mốc số bắt buộc · bằng chứng = 563 test hiện có + bảng đối chiếu từng luật
- Mức đầu tư suy ra: **vừa** — plugin đang chạy thật hằng ngày nhưng request dừng ở tài
  liệu, không đụng runtime, nên không cần hạng mục QC hiệu năng có ngưỡng số

### Research

Tóm tắt ở `../research/2026-08-14-toi-uu-llm-workflow.md`. Điểm quyết định: chuẩn viết
skill nói mức chi tiết phải nhắm vào model YẾU NHẤT được hỗ trợ, nên "cắt token" và
"model yếu vẫn tuân rule" kéo ngược nhau — spec phải chốt cách xử lý xung đột này.

## Hỏi đáp

### Vòng 1 — scope

**Hỏi**: 5 mặt + 4 câu bối cảnh.
**Đáp**: 1 → A, B, C, D · 2 → A (dừng ở đề xuất) · 3 → A (`skills/`+`hooks/`+`agents/`) ·
4 → B (không đặt mốc) · 5 → A (pytest + bảng đối chiếu luật). Bổ sung: phải phân tích và
tổ chức workflow chi tiết, dễ áp dụng, để **model thấp vẫn tuân đủ rule và behavior**.

### Vòng 2 — chi tiết

**Hỏi**: 5 câu (định nghĩa "model thấp" · ưu tiên khi cắt-token chọi tuân-thủ · có được
đổi cấu trúc file không · kiểu trình bày đầu ra · có kèm công cụ tự đo lại không).
**Đáp**: 1 → A, mở rộng: không chỉ Haiku mà **mọi model cùng hạng thấp** (vd bản rẻ của
GPT-5.3, model local) — tiêu chí là "đủ chi tiết, dễ áp dụng để model hạng thấp vẫn chạy
đúng" · 2 → A (ưu tiên tuân thủ, chỉ cắt phần lý lẽ) · 3 → A (được đổi cấu trúc file) ·
4 → A (bảng chấm + 3 gói + 1 khuyến nghị) · 5 → A (kèm nháp công cụ đo lại).

Ghi chú phạm vi: tiêu chí "model hạng thấp" áp cho `skills/`+`hooks/`+`agents/` như câu 3
đã chốt. `portable/` (đường dành cho agent ngoài Claude) vẫn NGOÀI phạm vi; đề xuất sẽ
ghi một dòng nêu việc áp cùng tiêu chí cho `portable/` là request riêng.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ — đã xong | có ẩn số ngoài: chuẩn viết skill và cách viết cho model nhỏ |
| Interview | CÓ — 2 vòng, đã xong | scope + chi tiết, không còn câu hỏi làm đổi kết quả |
| Spec → plan → implement → report | CÓ | khung bất biến, không được cắt |
| QC độc lập bằng agent | BỎ | đầu ra là một file Markdown, mọi dòng DoD kiểm được bằng `grep`/lệnh — thêm agent là thêm vòng, không thêm bảo đảm |
| Chia sub-agent để implement | BỎ | mọi task ghi vào cùng một file đề xuất, tách ra chỉ gây xung đột ghi |
| Sửa `skills/`, `hooks/`, `agents/` | BỎ | user chốt câu 2 = dừng ở bản đánh giá + đề xuất |
| `graphify extract` cuối turn | BỎ | không có file mã nguồn nào đổi |
