# Brief — bỏ pha sơ đồ mind map khỏi quy trình TDQ
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> tôi muốn mở reqest mới xử lí không dùng sơ đồ mind map và không có duyệt sơ đồ nữa

Cách hiểu đầu tiên:
- **Mục tiêu**: gỡ pha `diagram` (vẽ mind map + cổng duyệt từng sơ đồ) ra khỏi pipeline TDQ,
  để lane `full` chạy thẳng `analyze → spec → plan → mode → implement → qc → report`.
- **Phạm vi đoán**: `scripts/tdq_state.py` (VALID_PHASES, APPROVE_TARGETS, DIAGRAM_KEY, các
  hàm `diagram_*`, bảng checklist pha), skill `tdq-diagram`, `tdq-intake`
  (`references/analyze-full.md`, câu "MUST list phase diagram"), `tdq-spec`, `tdq-plan`,
  `tdq-conventions`, hook chặn cứng nếu có, test liên quan, docs.
- **Điểm chưa rõ**:
  1. Xoá hẳn pha diagram hay chỉ chuyển thành tuỳ chọn (mặc định tắt, bật khi user yêu cầu)?
  2. Có xoá luôn skill `tdq-diagram` + thư mục `docs/tdq/mind-map/` và các file mind-map đã có,
     hay giữ lại làm công cụ gọi thủ công?
  3. Tính năng render mind-map HTML vừa build xong (request trước) có bị gỡ theo không?

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Nguồn | Phán quyết |
|---|---|---|
| `tdq-intake` / `tdq-spec` / `tdq-plan` / `tdq-build` | plugin:tdq-workflow | DÙNG — chính pipeline đang sửa |
| `tdq-conventions` | plugin:tdq-workflow | DÙNG — `references/phases.md` là bảng pha phải sửa |
| `tdq-diagram` | plugin:tdq-workflow | ĐỐI TƯỢNG XOÁ — không gọi trong request này |
| `tdq-lsp-setup` | plugin:tdq-workflow | DÙNG — đã kiểm 6/6 bậc ĐẠT |
| `mcp__lsp__*` + lumen `semantic_search` | MCP | DÙNG — tra ký hiệu `diagram_*` trong `tdq_state.py` |
| `graphify` | project skill | DÙNG — chạy cuối turn khi đổi code |
| `superpowers:test-driven-development` | plugin | DÙNG — mọi task đỏ-xanh |
| `tavily-*` research | MCP | BỎ — việc thuần nội bộ repo, không có ẩn số ngoài |

### Hiện trạng code

Pha `diagram` là cổng chặn thứ ba của lane `full` (`spec → diagram → plan`) và cũng bắt buộc
ở lane `nhanh`. Bộ máy nằm ở:

- `scripts/tdq_state.py` (2007 dòng, 103 chỗ nhắc): `VALID_PHASES`, `APPROVE_TARGETS`,
  `DIAGRAM_KEY = "diagrams"`, `default_state`, `_heal_diagrams`, `_diagram_id`,
  `diagram_entries`, `diagram_pending`, `_diagram_register`, `_cli_approve_diagram`,
  `_cli_diagram`, cổng vào `plan`, `PHASE_ORDER`, bảng checklist pha `diagram`, dòng
  `| Diagrams |` trong bảng trạng thái, `_parse_approve_args`.
- `scripts/tdq_mindmap.py` (793 dòng) — 5 lệnh `sinh/kiem/lien-he/doi-chieu/xem`.
- `scripts/mindmap_render.py` (1457 dòng) — dựng trang HTML hai lớp.
- `scripts/doc_lint.py` — import `MIND_MAP_DIR_REL`, `check_diagram`; ngân sách token
  `"tdq-diagram": 155`.
- Skill: `tdq-diagram/SKILL.md`, `tdq-spec` (L83-86), `tdq-plan` (L10-13), `tdq-intake`
  (L98-102) + `references/quick-lane.md` (L43-48), `tdq-conventions/references/phases.md`
  (L12-13, L27).
- Test: `test_mindmap_render.py` (1235), `test_mindmap_nhan_doc.py` (913),
  `test_state_diagram_gate.py` (255), `test_doc_lint_mindmap.py` (145) — xoá theo; sửa nhẹ
  `test_next.py`, `test_e2e_chain.py`, `test_timing.py`, `test_stop_gate.py`,
  `test_tdq_eval.py`.
- Bản portable `portable_claude/` và `antigravity_portable/` chép nguyên `skills/` +
  `scripts/`, nên phải chạy lại `scripts/build_portable.py` và dọn file thừa còn sót.

### Quyết định đã chốt

1. Xoá sạch pha `diagram`: pipeline `full` còn `analyze → spec → plan → mode → implement →
   qc → report`; lane `nhanh` bỏ bước 1b vẽ sơ đồ.
2. Xoá `tdq_mindmap.py`, `mindmap_render.py`, skill `tdq-diagram` và 4 file test riêng của
   chúng.
3. GIỮ NGUYÊN `docs/tdq/mind-map/` (16 file) làm tư liệu lịch sử → `doc_lint.py` phải bỏ
   nhánh `check_diagram`, thư mục vẫn nằm trong `OUTPUT_DIRS` nên chỉ chịu R8/R10/R11/R12.
4. GIỮ NGUYÊN docs lịch sử (brief/plan/qc/report cũ) — là biên bản đã chốt.
5. GIỮ NGUYÊN `scripts/canvas_a4_*.py` + `docs/diagrams/*.excalidraw` — tính năng tài liệu
   kiến trúc, không thuộc pipeline mind-map.
6. Tương thích ngược: state cũ còn key `diagrams` → bỏ qua im lặng; gọi `approve diagram`
   hoặc `diagram add|list` → báo lỗi rõ ràng "pha diagram đã gỡ khỏi quy trình", không phải
   lỗi `unknown command` chung chung.
7. Sinh lại cả hai bản portable trong chính request này.
8. Miễn trừ: request này KHÔNG qua pha `diagram` (đang gỡ chính nó) — user chốt ở câu 6.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| analyze | CÓ | đang chạy |
| research ngoài | BỎ | việc thuần nội bộ repo, không có ẩn số cần tra ngoài |
| spec | CÓ | sửa bộ máy state + cổng duyệt, phải có cổng duyệt spec |
| diagram | BỎ | user chốt miễn trừ (câu 6A) — đây chính là pha bị gỡ |
| plan | CÓ | nhiều file, cần checklist task có test |
| mode | CÓ | hỏi main hay subagent sau khi duyệt plan |
| implement | CÓ | — |
| QC độc lập bằng agent | CÓ | sửa chính bộ máy chặn quy trình, tự QC dễ mù |
| report | CÓ | — |

## Hỏi đáp

**H1. Lane nào?** → chuyên sâu (deep/full).

**H2. Mức gỡ tới đâu?** → xoá sạch: gỡ luôn skill `tdq-diagram` và tính năng render HTML.

**H3. File sơ đồ đã có trong `docs/tdq/mind-map/`?** → giữ nguyên làm tư liệu lịch sử.

**H4. Docs lịch sử có sửa không?** → không, giữ nguyên biên bản.

**H5. `canvas_a4_*.py` + `docs/diagrams/`?** → giữ nguyên, không đụng.

**H6. State cũ còn key `diagrams`, lệnh `approve diagram` mất?** → bỏ qua im lặng key cũ;
lệnh cũ báo lỗi rõ ràng là pha đã gỡ.

**H7. Sinh lại bản portable trong request này?** → có.

**H8. Request này có phải qua pha `diagram`?** → không, miễn trừ.
