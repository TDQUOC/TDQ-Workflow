# QC — Spec có sơ đồ Trước/Sau, subagent chỉ đọc, DoD bám nghiệp vụ
Ngày: 2026-11-02 · Plan: ../plan/2026-11-02-1157-nang-cap-spec-subagent.md · Vòng: 1 (+ fix QC1.1, QC1.2)
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Mức QC: `ultra` — DoD + trọn suite + smoke + runtime + QC độc lập.

| # | Hạng mục | Lệnh đã chạy | Kết quả | PASS/FAIL |
|---|---|---|---|---|
| Q1 | Spec template buộc mục Trước/Sau do sơ đồ dẫn | `pytest tests/test_spec_template.py -q` | 9 passed | PASS |
| Q2 | HTML Trước/Sau + binding | `tdq_archify.py verify ...` | binding `current`; manifest `stale` vì source đổi sau render (đúng thiết kế, xem dưới) | PASS |
| Q3 | Pipeline nhanh cùng luật | `pytest tests/test_archify_workflow_contract.py -q` | 9 passed, 4 subtests | PASS |
| Q4 | Subagent ghi src trước implement bị chặn | `pytest tests/test_edit_gate.py -k subagent_spec_src` | 1 passed (đỏ trước khi sửa: 1 failed) | PASS |
| Q5 | Subagent vẫn ghi được docs | `pytest tests/test_edit_gate.py -k subagent_docs` | 1 passed | PASS |
| Q6 | Luồng cũ giữ nguyên | `tdq_test.py tron-bo` + chạy riêng `test_archify_e2e.py` | 3960 passed, 10 skipped, 2518 subtests; 3 failed là `test_archify_e2e` (chạy riêng: 2/2 passed 15,30 s trên cả `dev` và nhánh này) | PASS (lệch #1, chờ duyệt) |
| Q7 | Luật subagent + luật DoD có mặt | `pytest tests/test_luat_subagent_pr.py tests/test_spec_template.py -k "subagent or dod"` | 6 passed | PASS |
| Q8 | Report có thân PR | `pytest tests/test_luat_subagent_pr.py -k pr` | 3 passed | PASS |
| Q9 | HTML đọc được bằng mắt | Chrome DevTools: đo SVG + ảnh chụp | vòng 1 FAIL (2 sơ đồ 0×0, chrome tiếng Trung) → QC1.1 → 4 sơ đồ 961×80, 1246×80, 844×280, 1080×280; `lang=en` | PASS (sau fix) |
| Q10 | Diff tối thiểu | `git diff --stat dev -- scripts/` | 0 dòng; 14 file, +158/−21; không hàm/lớp thừa | PASS |
| QC-F1 | Trọn suite | `tdq_test.py tron-bo` + `tdq_test.py so` | 2/3 lượt trong ngân sách, 0 bỏ sót bán kính; vòng 1 có 7 lỗi do request → QC2.1 sửa về 0 | PASS (lệch #1 ở `archify_e2e`) |
| QC-F2 | Hồi quy vùng chạm | 14 file test vùng chạm | 199 passed, 382 subtests in 14,64 s | PASS |
| QC-F3 | Ràng buộc kiến trúc §5 | đọc diff | xem dưới | PASS |
| QC-F4 | Clean code | 5 câu SOLID | xem dưới | PASS |
| Smoke | Hook thật qua CLI, project tạm | `python docs/tdq/artifacts/.../smoke_edit_gate.py` (trần 120 s) | SMOKE PASS, 485 ms | PASS |
| Runtime | Hook trong phiên Claude Code thật | — | CHƯA KIỂM: hook phiên này nạp từ cache plugin 0.85.1, không từ repo | CHƯA KIỂM |
| QC độc lập | `tdq-qc-tester` | 6 mục | PASS 6/6, 5 lỗi nhỏ D1–D5 | PASS |

## Bằng chứng

### Q2
```
binding: current (0 lý do) · manifest: stale — "Source file modified: hooks/scripts/edit_gate.py, skills/..., tests/..."
```
Manifest ghi dấu vân tay source lúc render (trước implement). Sửa source trong implement làm nó stale — đúng hành vi của `archify-lifecycle.md` ("refresh after source changes"). Binding với spec vẫn `current`.

### Q4 — đỏ → xanh
```
trước sửa: FAILED tests/test_edit_gate.py::TestEditGateSubagentChiDoc::test_subagent_spec_src_bi_chan — 1 failed, 3 passed
sau sửa:   40 passed, 3 subtests passed in 4.95s
```

### Q9 — vòng 1 FAIL, fix QC1.1
```
vòng 1: spec-truoc SVG 0×0, spec-sau SVG 0×0 (sơ đồ có `lane`), document.lang = zh-CN
sau fix: lang=en · spec-truoc 961×80 · spec-sau 1246×80 · sub-truoc 844×280 · sub-sau 1080×280
```
Ảnh: `docs/tdq/qc/2026-11-02-1157-nang-cap-spec-subagent-preview.png`.

### Smoke
```
subagent src: deny=True team=True
subagent docs: deny=False team=False
main src: deny=False team=False
SMOKE PASS · exit=0 ms=485
```

### QC-F3 — ràng buộc kiến trúc
- `scripts/` không import `hooks/`: không file `scripts/` nào đổi (Q10). PASS.
- Không hook nào chặn vì "chưa duyệt": lý do chặn mới là "subagent sửa project trước implement". PASS.
- `skills/` chỉ nhắc tên lệnh: archify-ba/archify-quick chỉ chứa lệnh `tdq_archify.py`, không chép code. PASS.

### QC-F4 — 5 câu SOLID (edit_gate.py)
- SRP: có — nhánh mới chỉ làm một việc (chặn subagent trước implement).
- OCP: có — thêm phase miễn chặn = thêm một phần tử tuple.
- LSP: có — đi qua `block()` chung, cùng hợp đồng deny như các nhánh khác.
- ISP: có — chỉ đọc `payload["agent_id"]`, `abs_target`, `state`.
- DIP: có — dùng `block`, `within`, `effective_phase` có sẵn.

### QC độc lập — lỗi nhỏ đã xử lý
- D1 nhãn evidence cả trang: sửa câu luật `archify-ba.md` — trang là đề xuất thiết kế, `planned` cho cả trang, chữ phụ trợ của sơ đồ Trước nêu file nguồn.
- D2 "Bắt buộc Mermaid": sửa thành "Mermaid dự phòng" (QC1.2).
- D3 hai dòng checklist trùng ý: giữ — dòng cũ khoá bởi test cũ, dòng mới riêng cho HTML.
- D4 docstring `edit_gate.py`: sửa (QC1.2).
- D5 thiếu newline cuối `tests/test_edit_gate.py`: sửa.

## Lệch spec chờ duyệt
- `#1 · Q6 · ngưỡng "tron-bo 0 failed" → đo được "3960 passed, 10 skipped, 2518 subtests; 3 failed là test_archify_e2e (native Chrome updater IPC 0x5 khi chạy giữa suite; chạy riêng 2/2 passed 15,30 s trên cả dev và nhánh này)" · phương án: không sửa test cũ ngoài phạm vi`

## Kết luận
PASS toàn bộ (Q6 PASS với lệch #1 chờ user duyệt; Runtime trong phiên thật: CHƯA KIỂM do phiên đang nạp hook từ cache plugin 0.85.1).
