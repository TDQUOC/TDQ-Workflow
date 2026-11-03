# PLAN — Sửa luật thứ tự tìm kiếm và bắt kiểm LSP hoạt động thật

Ngày: 2026-09-03 · Spec: ../spec/2026-09-03-0053-sua-luat-va-kiem-lsp-that.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: **đội** — `tdq_bench.py mo-phong` trên chính plan này ra `Winner: đội (gap 16.2 minutes)` (16 task · 5 đợt · 32,6′ main so với 16,3′ đội). Khớp với lát cắt file: cụm 1 chỉ chạm `skills/`, cụm 2 chỉ chạm `scripts/tdq_lsp.py` + `tests/test_tdq_lsp.py`, không giao nhau. (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: XONG · QC độc lập PASS sau vòng sửa T6.1

## Mục lục

- Sai lệch so với lộ trình đã duyệt
- Quy tắc thi hành (áp cho mọi task)
- P1 — Câu luật mới và bảng phân lớp
- P2 — Bậc 7 kiểm cấu hình gốc import
- P3 — Bước kiểm bằng hiệu ứng thật ở intake
- P4 — Log & test bắt buộc
- P5 — Bundle portable và báo cáo
- Cụm song song
- Definition of Done

## Sai lệch so với lộ trình đã duyệt

Spec §1b ghi phase `diagram` = CÓ. **Phase đó không còn tồn tại**: `tdq_state.py` trả
*"Phase diagram was removed from the workflow on 2026-09-01 — use phase=spec instead"*, và
`skills/tdq-diagram/` đã bị xoá khỏi repo. Tôi viết nhầm theo bản skill cũ còn trong context.
Vậy đầu ra §2 số 9 (sơ đồ) **BỎ**, và plan này không có task nào cho nó. Spec đã niêm sha256
nên không sửa; ghi sai lệch ở đây thay vì phá niêm.

## Hợp đồng năng lực (theo §3b của spec)

- Dùng: `tdq-lsp-setup`
  - Để: cung cấp văn bản luật gốc và bảng thang bậc — đây là skill bị sửa ở P1
  - Ra: `references/uu-tien-tim-kiem.md` §1–§3 và bảng 7 bậc trong `SKILL.md`
  - Kiểm: `python3 -m pytest tests/test_tdq_lsp_skill.py -q` xanh và `doc_lint.py skills/tdq-lsp-setup` thoát 0
  - Không dùng cho: chép nội dung `LANG_CONFIG` từ script sang skill (cấm bởi `docs/kien-truc.md`)
- Dùng: `tdq-diagram`
  - Để: **KHÔNG dùng** — skill này đã bị xoá khỏi repo và phase `diagram` bị gỡ ngày 2026-09-01; spec §3b liệt kê nhầm theo bản skill cũ còn trong context
  - Ra: không đầu ra nào; đầu ra số 9 của spec §2 bị BỎ, xem mục "Sai lệch"
  - Kiểm: `python3 scripts/tdq_state.py set phase=diagram` bị từ chối — đó là bằng chứng
  - Không dùng cho: mọi việc trong plan này
- Dùng: `tdq-spec / tdq-plan / tdq-build`
  - Để: khung bất biến của lane full — spec đã duyệt, plan là file này, build chạy P1–P5
  - Ra: file spec đã niêm, file plan này, và các tick `[x]` khi thi hành
  - Kiểm: `doc_lint.py --pair <spec> <plan>` thoát 0
  - Không dùng cho: sửa spec đã niêm sha256 — sai lệch ghi ở plan, không sửa ngược
- Dùng: `tdq-qc-tester (agent)`
  - Để: chấm độc lập toàn bộ DoD Q1–Q11, vì chính request này là luật "đừng tin thang tự báo ĐẠT"
  - Ra: một bảng PASS/FAIL kèm bằng chứng lệnh, ghi vào mục `## QC` của file này
  - Kiểm: mọi dòng Q1–Q11 có PASS kèm output lệnh thật
  - Không dùng cho: tự sửa code — agent này chỉ đọc và chấm

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## P1 — Câu luật mới và bảng phân lớp

- [x] **T1.1** (e10m) Viết lại §1 của file luật gốc: câu blockquote mới phân lớp theo LOẠI
  truy vấn (quan hệ/đổi tên → `mcp__lsp__*`; tên chính xác đã biết → grep; khái niệm mơ hồ →
  lumen; chưa chắc → gọi song song rồi gộp), giữ dòng trỏ về file gốc — Test: `python3 -c` đọc
  blockquote đầu tiên của §1, khẳng định chứa đủ `mcp__lsp__`, `grep`, `lumen` và cả 3 từ khoá
  loại truy vấn
- [x] **T1.2** (e12m) Viết lại §2 thành bảng "loại truy vấn → lớp nào trước → số đo", mỗi dòng
  mang con số thật từ báo cáo `2026-09-03-0017` (15/15 và 0 dương tính giả; grep precision
  67 %; LSP hạng 13/62 ở khái niệm mơ hồ) — Test: `grep -c "15/15\|67 %\|13/62"` trên file luật
  ≥ 3
- [x] **T1.3** (e8m) Cập nhật §3 (vòng đời Ollama) cho khớp: lumen không còn được đánh thức ở
  MỌI truy vấn ký hiệu mà chỉ khi truy vấn thuộc loại khái niệm mơ hồ hoặc khi chưa phân loại
  được — Test: `grep -n "mọi truy vấn"` trên file luật không còn dòng nào bắt buộc đánh thức
- [x] **T1.4** (e10m) Thêm dòng bậc 7 vào bảng thang của `tdq-lsp-setup/SKILL.md`, nêu rõ nhóm
  A cảnh báo / nhóm B chặn; **không chép bảng `LANG_CONFIG`** sang, chỉ mô tả — Test:
  `grep -n "LANG_CONFIG" skills/tdq-lsp-setup/SKILL.md` không ra dòng nào, và bảng thang có
  đúng 7 dòng bậc

- [x] **T1.5** (e6m) *(phát sinh)* `SKILL.md` vượt trần R6 (127 > 120 dòng) sau khi thêm bậc 7 —
  gộp hai dòng "Acceptance"/"Done when" ở cuối và cập nhật "six rungs" → "seven rungs" — Test:
  `python3 scripts/doc_lint.py skills/tdq-lsp-setup` thoát 0
  - Ghi chú: gộp câu ở cuối chưa đủ (vẫn 125 dòng) — phải nén thêm §rung 6, §Ollama và dòng
    `description` ở frontmatter cho khớp bậc 7

**Xong P1 khi**: §1, §2, §3 của file luật gốc và bảng thang trong SKILL.md đều đã đổi, và
`doc_lint.py skills/tdq-lsp-setup` thoát 0.

## P2 — Bậc 7 kiểm cấu hình gốc import

- [x] **T2.1** (e14m) Thêm bảng `LANG_CONFIG` vào `scripts/tdq_lsp.py`: mỗi khoá của
  `LANG_SERVER` → (danh sách file mốc, nhóm `"A"` hoặc `"B"`). Nhóm B đúng 4 cụm ngôn ngữ:
  python, typescript+javascript, lua, c+cpp — Test: test mới khẳng định `set(LANG_CONFIG) ==
  set(LANG_SERVER)`
  - Chạm: `scripts/tdq_lsp.py`, `tests/test_tdq_lsp.py`
- [x] **T2.2** (e16m) Viết `bac7_cau_hinh_goc_import(project)`: dùng lại `do_ngon_ngu(project)`,
  với mỗi ngôn ngữ tìm file mốc ở gốc repo; thiếu ở nhóm B → `dat=False`, `chi_canh_bao=False`;
  thiếu ở nhóm A → `dat=False, chi_canh_bao=True`; phần gợi ý in **nội dung file cần tạo** kèm
  câu xin phép, không tự ghi file — Test: test mới dựng repo tạm chỉ có file `.py`, không
  `pyrightconfig.json` → bậc 7 `dat=False` và `chi_canh_bao=False`
  - Chạm: `scripts/tdq_lsp.py`, `tests/test_tdq_lsp.py`
  - Cần: T2.1
- [x] **T2.3** (e6m) Cắm bậc 7 vào `chay_kiem()` — Test: `python3 scripts/tdq_lsp.py kiem` in 7
  dòng bậc và tổng `7/7 bậc ĐẠT`, thoát 0 trên repo này
  - Chạm: `scripts/tdq_lsp.py`, `tests/test_tdq_lsp.py`
  - Cần: T2.2
- [x] **T2.4** (e8m) Test hiệu ứng thật của bậc 7: đổi tên `pyrightconfig.json` → `kiem` phải
  THIẾU và thoát 3; đổi tên lại → ĐẠT và thoát 0 — Test: chính kịch bản đó, chạy bằng một
  lệnh, khôi phục tên file trong cùng task
  - Chạm: `tests/test_tdq_lsp.py`
  - Cần: T2.3
- [x] **T2.5** (e6m) Test nhóm A không chặn: repo tạm chỉ có 3 file `.go` và không `go.mod` →
  bậc 7 cảnh báo, `kiem` vẫn thoát 0 — Test: chính assert đó
  - Chạm: `tests/test_tdq_lsp.py`
  - Cần: T2.2

**Xong P2 khi**: `kiem` in 7 bậc trên repo này và thoát 0; 4 test mới xanh.

## P3 — Bước kiểm bằng hiệu ứng thật ở intake

- [x] **T3.1** (e12m) Viết bước kiểm hiệu ứng vào `skills/tdq-intake/SKILL.md` bước 1b: sau khi
  thang ĐẠT, chọn một hàm bất kỳ đang có trong repo, gọi `mcp__lsp__find_references`, grep
  chính ký hiệu đó, ĐẠT khi số file LSP phủ ≥ số file grep; không đạt → ghi một dòng lý do vào
  brief và tụt về grep. Nêu rõ đây là **lỗi QC** nếu bỏ qua — Test: `grep -n "find_references"
  skills/tdq-intake/SKILL.md` ra dòng, và mô tả có đủ 3 phần: cách chọn, cách đối chiếu, điều
  kiện ĐẠT
- [x] **T3.2** (e10m) Chép câu luật mới của T1.1 nguyên văn vào đủ 5 chỗ móc — Test: phép kiểm
  khớp-từng-chữ giữa 5 chỗ móc và bản gốc chạy xanh
  - Cần: T1.1, T3.1
- [x] **T3.3** (e12m) Sửa test khoá luật: bỏ assert thứ tự chữ `mcp__lsp__` < `lumen` < `grep`
  (không còn thứ tự tuyến tính), thay bằng assert "đủ 3 lớp, mỗi lớp gắn đúng một loại truy
  vấn" — Test: `python3 -m pytest tests/test_tdq_lsp_skill.py -q` xanh
  - Chạm: `tests/test_tdq_lsp_skill.py`
  - Cần: T3.2

**Xong P3 khi**: 5 chỗ móc mang câu mới, `test_tdq_lsp_skill.py` xanh, intake có bước kiểm
hiệu ứng mô tả đủ để làm theo.

## P4 — Log & test bắt buộc

- [x] **T4.1** (e4m) Bậc 7 ghi log theo đúng khuôn `bậc N … → ĐẠT/THIẾU` của 6 bậc hiện có,
  qua `_log()` sẵn có, không thêm cơ chế log mới — Test: `TDQ_LOG=1 python3 scripts/tdq_lsp.py
  kiem` in dòng log cho bậc 7 đúng khuôn
  - Chạm: `scripts/tdq_lsp.py`
  - Cần: T2.3
- [x] **T4.2** (e8m) Chạy toàn bộ test suite — Test: `python3 -m pytest tests/ -q` không vượt
  mốc **101 failed / 1453 passed**, bảng file đỏ không có tên mới
  - Cần: T3.3, T4.1

- [x] **T4.3** (e10m) *(phát sinh)* 2 test đỏ MỚI do thay đổi của tôi, không có trong mốc 101:
  `test_skill_shape::test_intake_shape` (tdq-intake 137 > 120 dòng vì khối 1c) và
  `test_token_budget::test_skill_descriptions_total` (1622 > 1620 ký tự vì description bậc 7).
  Nén khối 1c và rút gọn description — Test: cả hai test trên xanh, tổng lùi về 101 failed
  - Ghi chú: nén tại chỗ không đủ (vẫn 130 > 120 dòng). Tách nội dung phép kiểm ra
    `skills/tdq-intake/references/kiem-lsp-hieu-ung.md`, SKILL.md chỉ giữ 4 dòng trỏ sang —
    đúng khuôn `references/` sẵn có của skill này. Vẫn dư 3 dòng → gộp thêm bước 1c vào 1b và
    rút hai câu dài ở bước 1 và bước 2 của Part A

## P5 — Bundle portable và báo cáo

- [x] **T5.1** (e8m) Dựng lại 3 bundle bằng lệnh, không sửa tay file nào trong đó — Test:
  `python3 scripts/build_portable.py` thoát 0 rồi 3 bundle đều mang câu luật mới và bậc 7
  - Ghi chú: `tdq_checkportable.py check` chỉ chạy được TỪ BÊN TRONG một bundle (nó tìm
    `manifest.json` ở cwd), không chạy từ gốc repo. Thay bằng phép đếm grep trên 3 thư mục:
    câu mới có mặt, câu cũ = 0 file, `bac7_cau_hinh_goc_import` có mặt
  - Chạm: `portable_claude/`, `portable_codex/`, `antigravity_portable/`
  - Cần: T4.2
- [x] **T5.2** (e14m) Viết báo cáo: trạng thái thang trước (6/6 ĐẠT trong khi độ phủ 7 %) và
  sau, câu luật cũ và mới đặt cạnh nhau, kết quả kịch bản đổi tên `pyrightconfig.json` — Test:
  `python3 scripts/doc_lint.py docs/tdq/report` thoát 0
  - Cần: T5.1

## Cụm song song

Ba cụm, cắt theo file không giao nhau:

- **Cụm 1 — tài liệu luật**: T1.1 → T1.4, rồi T3.1, T3.2. Toàn bộ chạm `skills/`.
- **Cụm 2 — thang**: T2.1 → T2.5, T4.1. Toàn bộ chạm `scripts/tdq_lsp.py` +
  `tests/test_tdq_lsp.py`.
- **Cụm 3 — hợp lưu**: T3.3, T4.2, T5.1, T5.2 — phải đợi cả hai cụm trên.

Cụm 1 và cụm 2 chạy song song thật được (không đụng file chung). Cụm 3 tuần tự. Đó là lý do
đề xuất mode `main`: trần tốc độ chỉ là 2 nhánh, mà nhánh dài nhất (cụm 2) chiếm gần nửa tổng
ước tính.

**Ghi chú về `Chạm:` của `chay_kiem`** — `mcp__lsp__find_references` trên `chay_kiem` chỉ trả
**1 tham chiếu** (trong chính file). grep tìm thêm `tests/test_tdq_lsp.py:216,221`, nơi nó bị
`mock.patch.object(tdq_lsp, "chay_kiem", …)` gọi qua **chuỗi**, không phải ký hiệu — phân tích
tĩnh không thấy được. Đã gộp hai lớp; `tests/test_tdq_lsp.py` nằm trong `Chạm:` của T2.3.

## Definition of Done

- [x] Q1 Câu luật mới có ở đủ 5 chỗ móc, khớp từng chữ — `python3 -m pytest tests/test_tdq_lsp_skill.py -q`
- [x] Q2 Câu luật nêu đủ 3 lớp, mỗi lớp gắn một loại truy vấn — cùng lệnh trên
- [x] Q3 Bậc 7 ĐẠT trên repo này — `python3 scripts/tdq_lsp.py kiem` in `7/7 bậc ĐẠT`, thoát 0
- [x] Q4 Bậc 7 bắt được lỗi thật — đổi tên `pyrightconfig.json` rồi chạy `kiem`: thoát 3
- [x] Q5 Bậc 7 phân đúng nhóm — `python3 -m pytest tests/test_tdq_lsp.py -q`
- [x] Q6 `LANG_CONFIG` phủ đúng bộ khoá của `LANG_SERVER` — cùng lệnh trên
- [x] Q7 Intake có bước kiểm hiệu ứng đủ để làm theo — `grep -n "find_references" skills/tdq-intake/references/kiem-lsp-hieu-ung.md` (T4.3 đã dời nội dung sang file `references/`; SKILL.md chỉ còn link)
- [x] Q8 Không hồi quy — `python3 -m pytest tests/ -q` ≤ 101 failed
- [x] Q9 3 bundle khớp bản gốc — `python3 scripts/tdq_checkportable.py check --root <bundle>` cho từng thư mục (script bắt buộc lệnh con và `--root`)
- [x] Q10 Tài liệu sạch — `python3 scripts/doc_lint.py docs/tdq/spec docs/tdq/plan docs/tdq/report skills/`
- [x] Q11 QC độc lập PASS toàn bộ DoD — agent `tdq-qc-tester`


## QC

QC độc lập (`tdq-qc-tester`) chạy 2026-09-03 02:05. Q1–Q6, Q8, Q10 PASS. Q7 và Q9 FAIL **ở câu
lệnh của DoD**, không ở nội dung: Q7 trỏ vào `SKILL.md` trong khi T4.3 đã dời nội dung sang
`references/kiem-lsp-hieu-ung.md`; Q9 chạy `tdq_checkportable.py` thiếu lệnh con `check` và
`--root`. Chạy đúng lệnh thì cả hai đạt — 3 bundle `CLEAN 91/140/84 file(s) match`. Hai dòng DoD
đã sửa ở trên.

QC còn kiểm chéo Q8 bằng cách so **danh sách** định danh test (cả `SUBFAILED`) chứ không chỉ tổng
số: 0 test đỏ mới, và `test_doc_lint::test_repo_docs_clean` chuyển đỏ → xanh. Dò thêm ngoài happy
path đều đúng: dự án rỗng ĐẠT; biên ngưỡng 2 file `.py` ĐẠT / 3 file `.py` THIẾU; nhóm A thiếu
`go.mod` chỉ CẢNH BÁO. Cây làm việc không đổi sau QC (`pyrightconfig.json` sha256 khớp).

- [x] **T6.1** (e8m) *(QC defect, mức thấp)* Bậc 7 che lỗi nhóm A: `thieu = thieu_b or thieu_a`
  nên khi thiếu CẢ hai nhóm, phần chi tiết chỉ in nhóm B, người đọc không biết nhóm A cũng thiếu
  — `scripts/tdq_lsp.py:400`. Sửa để chi tiết luôn liệt kê cả hai, mức nghiêm trọng vẫn do nhóm B
  quyết định — Test: repo tạm có 5 file `.py` và 5 file `.go`, không `pyrightconfig.json`, không
  `go.mod` → `dat=False`, `chi_canh_bao=False`, và `chi_tiet` chứa cả "Python" lẫn "Go"
