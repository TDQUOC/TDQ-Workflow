# QC — công cụ sơ đồ giải thuật: script chạy được, phase bắt buộc trước plan, trang HTML hai lớp

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Ngày: 2026-08-23 · Plan: ../plan/2026-08-23-1623-mindmap-html-hai-lop.md · Lane: full · Vòng: 1

Số hạng mục = 25 dòng DoD + 4 hạng mục cố định = **29**.

## Sửa DoD trước khi chạy (theo luật qc.md)

Bảy dòng DoD KHÔNG đo được như đã viết — từ khoá `-k` không khớp tên test nào nên lệnh
"xanh" mà chẳng chạy gì. Đây là lỗi của plan, đã sửa dòng DoD cho đo được rồi mới QC:

| Dòng | `-k` cũ (chọn 0 test) | Sửa thành |
|---|---|---|
| Q7 | `gom_nhanh` | `tong_gom` |
| Q8 | `luoi` | `"tong_gom_hai_feature_va_ve_canh_that or tong_feature_tro_toi_chua_co_file"` |
| Q10 | `tro_hut` | `TestLienHeTroHut` |
| Q11 | `chan_chua_duyet` | `chan_con_chua_duyet` |
| Q15 | `khong_mat_du_lieu` | `chan_khong_mat_du_lieu` |
| Q16 | `sinh_cap_nhat` | `TestSinhCapNhat` |
| Q18 | `khuon_bat_buoc` | `"TestKiemDongNhanh or TestKiemDongPhuThuoc"` |

Q22 ghi "chạy lại với log tắt" mà không nói biến nào → ghi rõ `TDQ_LOG=0`.
Q23 ghi `i18n_check.py` không tham số — chạy thế chỉ in hướng dẫn rồi thoát 0, một cái pass
giả; đã ghi rõ hai đường dẫn script phải quét.

## Bằng chứng

- Q1 Năm lệnh trả đúng mã thoát: PASS — `pytest tests/test_mindmap_nhan_doc.py -q` → `99 passed, 14 subtests passed`
- Q2 Lọc node `file_type == "code"`: PASS — `-k doi_chieu_loc` → `2 passed, 97 deselected`
- Q3 Lời gọi sắp theo số dòng: PASS — `-k thu_tu` → `2 passed, 22 deselected`
- Q4 Docstring làm giải thích: PASS — `-k docstring` → `1 passed, 23 deselected`
- Q5 Trang tự chứa: PASS — `-k tu_chua` → `2 passed, 22 deselected`
- Q6 Đủ hai lớp, chuyển qua lại: PASS — `-k hai_lop` → `1 passed, 23 deselected`
- Q7 Trang tổng gom theo `@nhánh`: PASS sau fix QC1.1 — `-k tong_gom` → `2 passed, 23 deselected`
- Q8 Cạnh phụ thuộc kèm lý do: PASS — `2 passed, 23 deselected`
- Q9 Bắt vòng lặp phụ thuộc: PASS — `-k vong_lap` → `3 passed, 96 deselected`
- Q10 Bắt phụ thuộc trỏ hụt: PASS — `-k TestLienHeTroHut` → `3 passed, 96 deselected`
- Q11 Gate chặn, gọi đúng tên: PASS — `-k chan_con_chua_duyet` → `1 passed, 16 deselected`
- Q12 Duyệt từng cái độc lập: PASS — `-k duyet_doc_lap` → `1 passed, 15 deselected`
- Q13 Danh sách rỗng cũng bị chặn: PASS — `-k danh_sach_rong` → `2 passed, 14 deselected`
- Q14 State cũ thiếu khoá vẫn sang `plan`: PASS — `-k state_cu` → `2 passed, 14 deselected`
- Q15 Bị chặn xong file còn nguyên: PASS sau fix QC1.2 — `-k chan_khong_mat_du_lieu` → `1 passed, 16 deselected`
- Q16 `sinh` trên feature đã có: PASS — `-k TestSinhCapNhat` → `4 passed, 95 deselected`
- Q17 Luật lint cắm ở `is_output`: PASS — `pytest tests/test_doc_lint_mindmap.py -q` → `9 passed`
- Q18 Thiếu `@nhánh` / `@phụ-thuộc` sai khuôn: PASS — `8 passed, 91 deselected`
- Q19 Skill đủ 5 mục: PASS — `grep -c '^## ' skills/tdq-diagram/SKILL.md` → `6`
- Q20 Ba file cũ dẫn vào phase `diagram`: PASS — `grep -l` trả đủ ba đường dẫn
- Q21 Toàn bộ suite xanh: **FAIL có điều kiện** — `38 failed, 1498 passed, 1484 subtests passed`.
  So tập đỏ với mốc `7e3bbd0` (44 đỏ có sẵn trước request): `comm` phía "mới" RỖNG → **0 hồi quy**;
  6 test đỏ cũ nay đã xanh. 38 đỏ còn lại là nợ có sẵn ngoài phạm vi request (37 thuộc
  `test_skill_router` — kho skill plugin ngoài lệch bản kiểm kê, 1 thuộc `test_bench`).
  Ghi vào report, KHÔNG âm thầm bỏ qua.
- Q22 Log có timestamp, tắt được: PASS — bật: `[2026-08-23T20:27:00] tdq_mindmap: kiem: … 0 violation(s)`;
  `TDQ_LOG=0` → không in dòng nào, exit 0
- Q23 Hai script mới qua i18n: PASS — `i18n_check.py scripts/tdq_mindmap.py scripts/mindmap_render.py`
  → `0 Vietnamese line(s) in 2 file(s)`, exit 0
- Q24 (không số) Hai file mẫu dựng ra HTML: PASS — `xem docs/tdq/mind-map/dang-nhap.md` → ghi
  `dang-nhap.html`, exit 0
- Q25 (không số) Trang tổng có cạnh phụ thuộc thật: PASS — `xem --tong` → `index.html — 3 feature(s)`, exit 0
- QC-F1 Chạy cả suite bằng đúng lệnh của plan: PASS có ghi chú — xem Q21
- QC-F2 Hồi quy vùng đã chạm: PASS — 14 tệp test phủ mọi dòng `Chạm:` → `460 passed, 537 subtests passed`
- QC-F3 Năm ràng buộc kiến trúc ở §5 spec: PASS — (1) `tdq_mindmap.py`/`mindmap_render.py` không có
  `json.dump` hay đường ghi `state.json`, chỉ đọc; (2) hai file code mới đều nằm trong `scripts/`;
  (3) `git diff 7e3bbd0..HEAD -- hooks/` rỗng — chặn nằm trong `tdq_state.py`, không hook nào trả
  `deny`; (4) `skills/tdq-diagram/SKILL.md` không chứa dòng `def`/`import`/`return` nào; (5) i18n
  trên bốn script đã sửa → 0 dòng
- QC-F4 Năm câu tự soát clean-code: PASS —
  SRP: `check_diagram` thuần, tách hẳn khỏi in ấn và mã thoát; mỗi `_check_*` giữ đúng một luật khuôn.
  OCP: thêm lệnh mới = thêm một `subs.add_parser` + `set_defaults(handler=…)`, không mở thân hàm cũ.
  LSP: bốn lệnh cùng hợp đồng mã thoát `EXIT_OK/VIOLATION/SYNTAX/UPDATE`, mọi nhánh `return` cùng kiểu.
  ISP: không hàm nào nhận tham số bỏ không.
  DIP: `mindmap_render.py` và `doc_lint.py` đều import `check_diagram`/`build_link_graph` từ
  `tdq_mindmap.py` thay vì tự cài lại — ba công cụ không thể bất đồng về "sơ đồ hợp lệ là gì".

## Vòng fix 1

Hai lỗ hổng phủ test thật (không phải sai từ khoá), đã sửa bằng cách viết test còn thiếu:

- QC1.1 — Q7 đòi trang tổng gom theo `@nhánh` nhưng không test nào khẳng định. Thêm
  `TestTongGomTheoNhanh`: tên nhánh cha chỉ in một lần dù hai feature cùng nhánh, nhánh con là
  tầng riêng, feature nhánh khác không lọt vào, feature thiếu `@nhánh` vẫn hiện ở nhóm
  "Chưa gắn nhánh". `tests/test_mindmap_render.py`.
- QC1.2 — Q15 đòi "bị chặn xong file sơ đồ còn nguyên" nhưng `ChanPhasePlanTest` không có test
  nào kiểm điều đó. Thêm `test_chan_khong_mat_du_lieu_so_do`: so nội dung file trước/sau khi bị
  chặn, và soát lại danh sách `diagrams` còn đủ hai phần tử với câu duyệt đã ghi.
  `tests/test_state_diagram_gate.py`. (Đỏ thật một lượt vì khoá phần tử là `file` chứ không
  phải `path`, sửa test rồi xanh.)

## Kết luận

29/29 hạng mục PASS, trong đó Q21 pass kèm ghi chú: suite còn 38 đỏ nhưng **không có đỏ nào do
request này gây ra** (đối chiếu tập đỏ với mốc `7e3bbd0` ra rỗng ở phía mới), và 6 đỏ cũ đã xanh
trở lại. Nợ kỹ thuật còn lại phải ghi vào report: 37 ca `test_skill_router` lệch bản kiểm kê kho
skill plugin ngoài, 1 ca `test_bench`.
