# BRIEF — Áp Gói đầy đủ (Đ1–Đ7) của bản chấm tối ưu LLM

Ngày: 2026-08-14

## Nguyên văn

> okay vậy chọn A một request Gói đầy đủ, nhưng chia hai phase trong cùng plan — phase văn
> bản (Đ2–Đ7) xong và xanh trước, phase Đ1 (sửa skill_inventory.py + 2 test) sau. Được cả
> chất lượng lẫn tách rủi ro.

Hai turn trước đó đã chốt bối cảnh: user hỏi request cũ đã optimize chưa (chưa — dừng ở
đề xuất), rồi hỏi gói nào đảm bảo rule/behavior nhất, và chốt Gói đầy đủ vì cột "tác động
model hạng thấp" của cả 7 đề xuất đều "tốt hơn" hoặc "giữ nguyên", không đề xuất nào xấu.

**Cách hiểu đầu tiên**

- Mục tiêu: THỰC THI bảy đề xuất Đ1–Đ7 đã viết sẵn ở
  `docs/tdq/knowledge/2026-08-14-toi-uu-llm-workflow.md`, đúng thứ tự hai phase:
  1. Phase văn bản — Đ2, Đ3, Đ4, Đ5, Đ6, Đ7: chỉ sửa `.md` trong `skills/` và `agents/`.
     Phải xanh hết rồi mới sang phase sau.
  2. Phase mã — Đ1: thêm chế độ lọc cho `scripts/skill_inventory.py`, kèm 2 test (một cho
     cờ mới, một giữ nguyên hành vi mặc định).
- Ràng buộc kế thừa nguyên vẹn từ request trước: **không luật nào biến mất**, mọi thay đổi
  phải giữ cột "sau" ≥ cột "trước" ở bảng `## Đối chiếu luật`, và ưu tiên khi xung đột là
  **tuân thủ thắng cắt token**.
- Phạm vi đoán: `skills/` (khoảng 12 file bị đụng) · `agents/` 3 file · `scripts/skill_inventory.py`
  · `tests/` (thêm test cho Đ1). Không đụng `hooks/`, không đụng `portable/`.
- Đích số đã có sẵn từ bản chấm: thân `tdq-intake` 1.844 → ≈ 1.290 token · thân `tdq-build`
  1.936 → ≈ 1.320 token · `skill_inventory.py` 9.774 → ≈ 1.500–2.500 token mỗi lần analyze
  · mệnh lệnh tuyệt đối tăng ròng +11.
- Chỗ chưa rõ: có bắt buộc đạt đúng các con số token trên không hay chỉ cần "giảm và không
  mất luật" · phase văn bản có cần một cổng duyệt riêng trước khi sang phase mã không ·
  có chạy thử một request thật bằng model hạng thấp để nghiệm thu không (bản chấm đã nêu
  đây là giới hạn của bộ bằng chứng tĩnh) · Đ4 đẩy mục giải thích xuống phụ lục thì có
  được xoá bớt chữ không hay giữ nguyên 100% câu chữ.

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê ngày 2026-08-14: 284 skill trên đĩa, cộng skill built-in trong
context. Không xoá bảng này kể cả khi không có dòng DÙNG nào.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| graphify | user | DÙNG | phase Đ1: tra ai gọi `skill_inventory.py` trước khi thêm cờ; và `extract . --code-only` cuối turn có đổi mã |
| mem0-memory | user | DÙNG | search trước khi chốt cách làm Đ1; ghi 1 fact sau khi áp xong |
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-status, tdq-conventions | plugin:tdq-workflow | NỀN | chính workflow đang chạy — và cũng chính là đối tượng bị sửa |
| tavily-search, tavily-research, tavily-cli, tavily-extract, tavily-crawl, tavily-map, tavily-dynamic-search, tavily-best-practices | plugin:tavily | KHÔNG | khác lĩnh vực — việc thuần nội bộ, ẩn số bên ngoài đã research xong ở request trước |
| Đã xét 268 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Đã đo

Số đo lấy nguyên từ `docs/tdq/knowledge/2026-08-14-toi-uu-llm-workflow.md` (đo thật ngày
2026-08-14), không đo lại:

- Bề mặt context: `luôn nạp` 1.380 token · `nạp khi gọi skill` 8.473 · `đọc khi cần` 43.981.
- Thân skill nặng nhất: `tdq-build` 1.936 · `tdq-conventions` 1.820 · `tdq-intake` 1.844.
- `skill_inventory.py` in ra 39.722 byte ≈ 9.774 token mỗi lần analyze; hôm nay 284 dòng
  skill, 31 nguồn.
- Hook: trung vị cao nhất 56,2 ms, tổng đầu ra 2.075 byte/lượt — không đề xuất nào đụng hook.
- Tổng `skills/`: 28 file, 205 mệnh lệnh tuyệt đối (lệnh đếm ở mục `## Công cụ đo lại`).

### File bị đụng — hai phase

Phase 1 (văn bản, Đ2–Đ7) — 17 file, **không** đụng `scripts/`, `hooks/`, `tests/`, `portable/`:

- `skills/tdq-intake/`: `SKILL.md` · `references/quick-lane.md` · `references/scope-round.md`
  · `references/skill-inventory.md`
- `skills/tdq-build/`: `SKILL.md` · `references/qc.md` · `references/report-template.md`
- `skills/tdq-conventions/references/`: `reminder-codes.md` · `plugin-routing.md` · `tavily.md`
- `skills/tdq-spec/SKILL.md` · `skills/tdq-plan/SKILL.md` ·
  `skills/tdq-plan/references/mode-gate.md` · `skills/tdq-status/SKILL.md`
- `agents/`: `tdq-implementer.md` · `tdq-qc-tester.md` · `tdq-reviewer.md`

Phase 2 (mã, Đ1) — 4 file: `scripts/skill_inventory.py` (thêm cờ) ·
`tests/test_skill_inventory.py` (thêm 2 test) · `skills/tdq-intake/references/analyze-full.md:7`
và `skills/tdq-intake/references/skill-inventory.md:10` (đổi dòng lệnh gọi).

Chú ý phụ thuộc: `skill-inventory.md` bị cả hai phase đụng — Đ6 sửa nó ở phase 1 (khai
nhắc lại), Đ1 sửa dòng lệnh ở phase 2. Phải sửa theo đúng thứ tự, không gộp.

### Phạm vi đã chốt

- Mặt CHỌN: bảo trì (độ rõ của luật cho model đọc) · hiệu năng (chi phí context) · chức năng
  (hành vi lọc mới của Đ1) · độ tin cậy (không luật nào biến mất).
- Mặt LOẠI: bảo mật · trải nghiệm người dùng cuối · tương thích đa nền tảng · an toàn ·
  linh hoạt — không mặt nào bị request chạm tới; `portable/` và `hooks/` NGOÀI phạm vi.
- Bối cảnh: 28 file skill · 205 luật · 563 test đang xanh · 1 người giữ repo · workflow
  chạy thật mỗi ngày.
- Mức đầu tư suy ra: **vừa** cho phase văn bản (cắt–dán nguyên khối, kiểm bằng đếm luật),
  **đầy đủ** cho phase Đ1 — vì `skill_inventory.py` chạy ở MỌI request lane full, nên rủi
  ro "lọc mất một năng lực đáng dùng" phải thành hạng mục QC riêng có test.

Vòng scope: BỎ — request trỏ thẳng vào bảy đề xuất đã viết sẵn, mỗi đề xuất đã có sẵn
file đích, nội dung nháp, lệnh kiểm và hai cột tác động, nên không dấu hiệu nào trong 4
dấu hiệu của `scope-round.md` bật; phạm vi và bối cảnh suy được hết từ tài liệu nguồn.

### Research

BỎ — nghiên cứu ngoài đã làm trọn ở request trước, nằm ở
`docs/tdq/research/2026-08-14-toi-uu-llm-workflow.md` và 6 nguồn ở mục `## Nguồn` của
knowledge doc. Request này không có ẩn số bên ngoài mới: mọi thay đổi đều là văn bản nội
bộ cộng một cờ CLI thuần Python chuẩn.

### Ràng buộc kế thừa (bất biến)

1. Không luật nào biến mất. Cột "sau" ≥ cột "trước" ở mọi dòng bảng đối chiếu.
2. Xung đột giữa cắt token và độ tuân thủ → **tuân thủ thắng**.
3. `hooks/` và `portable/` không được đụng.
4. Không commit, không push khi user chưa yêu cầu.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research thêm | BỎ | đã làm trọn ở request trước, không ẩn số mới |
| Spec | CÓ | khung bất biến |
| Plan (một plan, hai phase) | CÓ | đúng thứ user chốt: văn bản xanh trước, mã sau |
| Implement | CÓ | khung bất biến |
| Review sâu spec/plan bằng `tdq-reviewer` | CÓ | plan đụng 21 file và chính bộ skill đang chạy — sai một chỗ là hỏng workflow |
| QC độc lập bằng `tdq-qc-tester` | CÓ | QC phải đếm lại luật và chạy 563 test trên bản đã sửa, tách khỏi người sửa |
| Chia sub-agent để implement | BỎ | 17 file văn bản có phụ thuộc thứ tự (Đ6 và Đ1 cùng đụng `skill-inventory.md`), chia song song dễ ghi đè nhau |
| Chạy thật bằng model hạng thấp để nghiệm thu | CÓ | user chọn 3B — sub-agent model rẻ chạy thử theo bộ skill mới, bù đúng giới hạn của bằng chứng tĩnh |
| Cổng duyệt giữa phase văn bản và phase Đ1 | CÓ | user chọn 2B — dừng báo cáo, chờ duyệt rồi mới đụng mã |
| Report | CÓ | khung bất biến |

### Kiểm cổng

- Làm ra gì: 17 file văn bản đã chuyển/siết, cộng một cờ lọc mới cho `skill_inventory.py`
  và 2 test. Output cụ thể: bảng đối chiếu luật trước/sau với 0 dòng giảm.
- Cần model/download/cài đặt: KHÔNG — thuần Python chuẩn và sửa Markdown.
- Phạm vi QC: đếm luật trước/sau · `pytest tests/` giữ 563 passed · `doc_lint.py` ·
  `diff` đầu ra `skill_inventory.py` mặc định trước/sau · `git status` không lọt file ngoài
  phạm vi.

## Hỏi đáp

Vòng chi tiết — 4 câu. User trả lời nguyên văn: `1A 2B 3B 4A 5A`.

1. **Đích token là ràng buộc cứng hay mềm?** → **A: mềm.** DoD chỉ cần "token giảm" và
   "số luật không giảm"; KHÔNG chốt con số 1.290 / 1.320 / 1.500–2.500. Các số đó chỉ còn
   là tham chiếu, không được dùng làm điều kiện PASS/FAIL, để tránh vì đuổi theo số mà
   cắt vào câu chữ mang luật.
2. **Có cổng duyệt riêng giữa hai phase không?** → **B: CÓ.** Phase văn bản (Đ2–Đ7) xong,
   chạy QC riêng của nó, DỪNG và báo cáo, chờ user duyệt rồi mới bắt đầu phase Đ1. Đây là
   một cổng duyệt THÊM, nằm giữa implement, không thay thế cổng duyệt spec/plan/mode.
3. **Nghiệm thu có chạy thật bằng model hạng thấp không?** → **B: CÓ.** Thêm task giao
   sub-agent chạy model rẻ làm thử một request nhỏ theo bộ skill đã sửa, rồi đối chiếu
   xem có bỏ bước nào của workflow không. User yêu cầu rõ nên được phép gọi sub-agent.
   Kết quả có tính ngẫu nhiên → là hạng mục QC quan sát, không phải cổng chặn cứng.
4. **Đ4 được xoá chữ không?** → **A: giữ nguyên 100% câu chữ.** Chỉ đổi chỗ và thêm nhãn
   phụ lục. Token giảm vì người/model đọc dừng sớm, KHÔNG vì xoá. Hệ quả: Đ4 phải kiểm
   được bằng `diff` số từ trước/sau bằng nhau.
5. **Bổ sung gì không?** → **A: không.**

Hết câu hỏi làm đổi kết quả → đủ điều kiện sang phase `spec`.
