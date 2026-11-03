# PLAN — Bộ tìm kiếm 4 tầng: kiểm bằng hiệu ứng, reindex mỗi turn, và skill `tdq-setup`

Ngày: 2026-09-28 · Spec: ../spec/2026-09-28-0910-lumen-check-va-setup-tool.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — đo bằng `tdq_bench.py simulate` trên chính plan này: đội thắng 20,2 phút (50,9 so với 30,7), 25 task chia 10 đợt, giao được 13 task, leader giữ 12 task đụng file nóng — user chốt `main` (inline implement) lúc duyệt, trái đề xuất đo được
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Thang bậc đo bằng hiệu ứng (M1)
- P2 — Kết turn: reindex và bỏ đường skip (M2)
- P3 — Skill `tdq-setup`: cài, kiểm, smoke test, ghi nợ (M3)
- P4 — Luật tìm kiếm 4 tầng và bản ghim user-level (M4)
- P5 — Dọn tên cũ (M5)
- P6 — Log & test bắt buộc
- P7 — Đo trên ba hệ
- P8 — Chuẩn bị QC
- Luật file nóng
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]`
   NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Mọi thứ chạm file NGOÀI repo (`~/.claude/CLAUDE.md`, `hooks.json` của plugin) phải viết thành
   hàm nhận đường dẫn qua tham số, và test chỉ chạy trên thư mục tạm — không test nào được đọc
   hay ghi file thật của máy.

## P1 — Thang bậc đo bằng hiệu ứng (M1)

- [x] **T1.1** (e10m) Bậc 5 dò daemon bằng socket TRƯỚC, `which` chỉ còn là đường phụ để in lệnh
  cài — vá false negative trên macOS — Test: `python -m unittest tests.test_bac_lumen_hieu_ung -k path`
  xanh, ca giả lập `shutil.which` trả None mà socket sống vẫn cho ĐẠT
  - Chạm: `scripts/tdq_lsp.py`, `tests/test_bac_lumen_hieu_ung.py` → `setup_status.py`,
    `tdq_ten_lenh.py` (nguồn: grep `tdq_lsp` trong `scripts/`, `hooks/`, `tests/`)
- [x] **T1.2** (e20m) Bậc 5 gọi một truy vấn lumen thật và đọc kết quả; không trả được kết quả nào
  thì KHÔNG ĐẠT, chi tiết nói rõ hỏng ở vòng đi-về — Test:
  `python -m unittest tests.test_bac_lumen_hieu_ung -k vong` xanh, ca lumen trả rỗng cho ra không ĐẠT
  - Chạm: `scripts/tdq_lsp.py`, `tests/test_bac_lumen_hieu_ung.py` → `setup_status.py`
  - Cần: T1.1
  - Dùng: `lumen:doctor` (mcp)
  - Để: đọc cách doctor kiểm backend và độ mới index trước khi viết phép đo, nạp skill TRƯỚC bước
    đỏ. Agent ngoài không có skill system: đọc skill của plugin lumen rồi làm theo.
  - Ra: phép đo vòng đi-về trong `scripts/tdq_lsp.py`, có trần thời gian riêng
  - Kiểm: `python -m unittest tests.test_bac_lumen_hieu_ung -k vong`
  - Không dùng cho: việc dựng lại index — đó là T2.1
- [x] **T1.3** (e20m) Bậc 5 đo độ mới NỘI DUNG index: hỏi một ký hiệu vừa sửa, không thấy thì báo
  index thiếu nội dung mới, không tin cờ tự báo của công cụ — Test:
  `python -m unittest tests.test_bac_lumen_hieu_ung -k noidung` xanh
  - Chạm: `scripts/tdq_lsp.py`, `tests/test_bac_lumen_hieu_ung.py`
  - Cần: T1.2
- [x] **T1.4** (e15m) Thêm bậc 8 cho graphify vào danh sách thang bậc: thiếu binary thì cảnh báo
  kèm lệnh cài; đồ thị cũ hơn commit mới nhất thì cảnh báo kèm lệnh dựng lại — Test:
  `python -m unittest tests.test_bac_lumen_hieu_ung -k graphify` xanh, và `tdq_lsp.py check` in
  đủ 8 dòng bậc
  - Chạm: `scripts/tdq_lsp.py`, `tests/test_bac_lumen_hieu_ung.py`, `tests/test_tdq_lsp.py` →
    hàm lắp thang bậc ở `chay_kiem` (nguồn: đọc `chay_kiem` trong `scripts/tdq_lsp.py`)
  - Cần: T1.1

**Xong P1 khi**: `python scripts/tdq_lsp.py check` in 8 bậc, và ba ca hỏng giả lập (PATH, vòng
đi-về, nội dung index) đều cho ra kết luận KHÔNG ĐẠT.

## P2 — Kết turn: reindex và bỏ đường skip (M2)

- [x] **T2.1** (e18m) Thêm `step_reindex` vào `tdq_finish`, chạy bằng CLI lumen mỗi turn, có trần
  thời gian; quá trần thì `fail` + ghi một dòng nợ, không bao giờ treo turn — Test:
  `python -m unittest tests.test_finish_reindex` xanh, gồm ca quá trần
  - Chạm: `scripts/tdq_finish.py`, `tests/test_finish_reindex.py` → `hooks/scripts/stop_gate.py`,
    `hooks/scripts/agy_stop_gate.py`, `scripts/tdq_eval.py` (nguồn: grep `tdq_finish` trong
    `scripts/`, `hooks/`, `tests/`)
  - Cần: T3.5
  - Dùng: `lumen:reindex` (mcp)
  - Để: đối chiếu cách refresh mà skill khuyến nghị trước khi chốt dùng CLI, nạp skill TRƯỚC bước
    đỏ. Agent ngoài không có skill system: đọc skill của plugin lumen rồi làm theo.
  - Ra: bước `reindex` in ra ở mọi lần kết turn, kèm dòng lý do khi `skip`
  - Kiểm: `python -m unittest tests.test_finish_reindex`
  - Không dùng cho: phép đo độ mới index của bậc 5 — đó là T1.3
- [x] **T2.2** (e10m) Gỡ cờ `--skip-graphify`: gọi kèm cờ thì báo lỗi tham số và chỉ sang cách làm
  mới; sửa ca test đang dùng cờ đó — Test: `python -m unittest tests.test_timing` xanh, và gọi
  `tdq_finish.py --skip-graphify` thoát khác 0
  - Chạm: `scripts/tdq_finish.py`, `tests/test_timing.py`, `scripts/tdq_state.py` → dòng chú giải
    ở `tdq_state.py` nói graphify dựng lại mỗi turn (nguồn: grep `--skip-graphify` và `tdq_finish`)
  - Cần: T2.1
- [x] **T2.3** (e5m) Dựng lại đồ thị graphify cho khớp nhánh hiện tại — Test:
  `graphify query --label antigravity_portable` không ra node nào
  - Chạm: `graphify-out/graph.json` → file sinh, không node nào phụ thuộc
  - Cần: T2.2

**Xong P2 khi**: kết turn hai lần liền đều in dòng `reindex`, và đồ thị không còn node trỏ vào
thư mục đã xoá.

## P3 — Skill `tdq-setup`: cài, kiểm, smoke test, ghi nợ (M3)

- [x] **T3.1** (e8m) Đổi tên thư mục `skills/tdq-lsp-setup/` thành `skills/tdq-setup/`, sửa `name:`
  và `description:` trong frontmatter cho khớp tên thư mục và cho đúng vai trò mới — Test:
  `python -m unittest tests.test_tdq_setup_skill` xanh
  - Chạm: `skills/tdq-setup/SKILL.md`, `skills/tdq-setup/references/lumen.md`
- [x] **T3.2** (e35m) Viết `scripts/tdq_setup.py`: đọc danh sách phụ thuộc đã khai, kiểm manifest
  từng món, cài thẳng món thiếu trong danh sách, kiểm cấu hình đúng — Test:
  `python -m unittest tests.test_tdq_setup -k cai` xanh, ca thiếu một món cho ra lệnh cài đã chạy
  - Chạm: `scripts/tdq_setup.py`, `tests/test_tdq_setup.py` → file mới, chưa node nào phụ thuộc
  - Cần: T1.4
  - Dùng: `update-config`
  - Để: ghi đúng khoá vào `settings.json` khi cấu hình thiếu, nạp skill TRƯỚC bước đỏ. Agent ngoài
    không có skill system: đọc `SKILL.md` của skill đó rồi làm theo.
  - Ra: hàm kiểm và sửa cấu hình trong `scripts/tdq_setup.py`
  - Kiểm: `python -m unittest tests.test_tdq_setup -k cauhinh`
  - Không dùng cho: sửa file của plugin khác — đó là T3.4, có luật riêng
- [x] **T3.3** (e30m) Smoke test từng tầng trong `tdq_setup.py`: grep, LSP, graphify, lumen — mỗi
  tầng một câu hỏi thật và một tiêu chí đạt, in thành bảng 4 dòng — Test:
  `python -m unittest tests.test_tdq_setup -k smoke` xanh
  - Chạm: `scripts/tdq_setup.py`, `tests/test_tdq_setup.py`
  - Cần: T3.2
- [x] **T3.4** (e20m) `tdq_setup.py` dò và vá hook plugin ngoài đang đè thứ tự tìm kiếm: sao lưu
  trước, chỉ gỡ khối chặn công cụ, giữ khối phiên — Test:
  `python -m unittest tests.test_tdq_setup -k hook` xanh trên fixture plugin trong thư mục tạm
  - Chạm: `scripts/tdq_setup.py`, `tests/test_tdq_setup.py`
  - Cần: T3.2
- [x] **T3.5** (e15m) Ghi nợ: món không tự xử được sinh đúng một dòng trong
  `docs/tdq/no-phu-thuoc.md`, có ngày và tên máy, chạy lại không nhân bản dòng cũ; ghi sẵn dòng nợ
  của §9 bản mẫu đang trỏ tới skill không tồn tại — Test:
  `python -m unittest tests.test_tdq_setup -k no` xanh, gồm ca chạy hai lần
  - Chạm: `scripts/tdq_setup.py`, `tests/test_tdq_setup.py`, `docs/tdq/no-phu-thuoc.md`
  - Cần: T3.2

**Xong P3 khi**: một lệnh `python scripts/tdq_setup.py` chạy xong in bảng 4 tầng kèm kết quả smoke
test, và file nợ tồn tại với ít nhất một dòng.

## P4 — Luật tìm kiếm 4 tầng và bản ghim user-level (M4)

- [x] **T4.1** (e30m) Viết lại `uu-tien-tim-kiem.md` thành luật BỐN tầng: thêm graphify, thêm bảng
  phụ thuộc runtime, ghi tên repo cạnh mọi số đo, xoá câu khẳng định không cần bước reindex — Test:
  `python -m unittest tests.test_luat_4_tang` xanh
  - Chạm: `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `tests/test_luat_4_tang.py`
  - Cần: T3.1
- [x] **T4.2** (e15m) Cập nhật năm chỗ trích luật cho khớp bản mới và khớp tên skill mới — Test:
  `python -m unittest tests.test_tdq_setup_skill` xanh (phép kiểm chống lệch năm chỗ)
  - Chạm: `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/analyze-full.md`,
    `skills/tdq-spec/SKILL.md`, `skills/tdq-plan/SKILL.md`, `skills/tdq-build/SKILL.md`
  - Cần: T4.1
- [x] **T4.3** (e20m) Ghim bản ngắn 4 tầng vào `docs/claude-md-mau.md` trong khối có dấu mốc, và
  NÂNG trần byte kèm chú giải lý do — Test: `python -m unittest tests.test_claude_md_core` xanh, và
  ghi hai lần chỉ còn một khối
  - Chạm: `docs/claude-md-mau.md`, `tests/test_claude_md_core.py`, `scripts/tdq_setup.py`
  - Cần: T4.1, T3.2

**Xong P4 khi**: luật có đủ bốn tầng kèm bảng phụ thuộc, và bản mẫu có đúng một khối dấu mốc.

## P5 — Dọn tên cũ (M5)

- [x] **T5.1** (e10m) Sửa bảng trần dòng của `doc_lint` và danh sách thứ tự nạp của
  `build_portable` sang tên skill mới — Test: `python -m unittest tests.test_doc_lint` xanh và
  `python scripts/build_portable.py --sinh-agy` chạy được
  - Chạm: `scripts/doc_lint.py`, `scripts/build_portable.py`
  - Cần: T3.1
- [x] **T5.2** (e8m) Đổi tên file phép kiểm chống lệch của skill sang tên mới và sửa đường dẫn gốc
  bên trong — Test: `python -m unittest tests.test_tdq_setup_skill` xanh
  - Chạm: `tests/test_tdq_setup_skill.py`
  - Cần: T4.2
- [x] **T5.3** (e10m) Sửa `README.md` và khai breaking change ở dòng đầu mục `CHANGELOG.md` — Test:
  `grep -rn "tdq-lsp-setup" scripts skills tests README.md` không ra dòng nào
  - Cần: T5.1, T5.2

**Xong P5 khi**: không còn chuỗi tên cũ trong mã, skill, phép kiểm và `README.md`.

## P6 — Log & test bắt buộc

- [x] **T6.1** (e10m) Log service của `tdq_setup.py` bật mặc định: timestamp, đủ chi tiết debug,
  tắt được qua biến môi trường như các script khác của repo — Test:
  `python -m unittest tests.test_tdq_setup -k log` xanh, gồm ca tắt log
  - Chạm: `scripts/tdq_setup.py`, `tests/test_tdq_setup.py`
  - Cần: T3.2
- [x] **T6.2** (e15m) Trọn bộ test chạy bằng một lệnh và xanh — Test: `python -m unittest discover -s tests -q`
  - Cần: T5.3

## P7 — Đo trên ba hệ

- [x] **T7.1** (e8m) Chạy trọn bộ test trên Windows — Test: `python -m unittest discover -s tests -q`
  không fail, không error
  - Cần: T6.2
- [x] **T7.2** (e12m) Chạy trọn bộ test trên máy Linux thật, trong thư mục tạm, xoá sạch sau khi
  đo — Test: kết quả không fail không error, và sau khi đo không gói nào được cài
  - Cần: T7.1
- [x] **T7.3** (e15m) Chạy trọn bộ test trên máy macOS thật, và chạy THẬT ca PATH của bậc 5 ở đó —
  Test: bậc 5 kết luận ĐẠT trên Mac dù tiến trình không-login không thấy binary trong PATH; python
  hệ thống của Apple không bị gọi tới
  - Cần: T7.1

**Xong P7 khi**: ba hệ đều xanh, và hai máy đo được trả về đúng trạng thái trước khi đo.

## P8 — Chuẩn bị QC

- [x] **T8.1** (e10m) Soát lỗi đúng-sai trên toàn bộ thay đổi — Test: mọi phát hiện được xử lý hoặc
  ghi lý do bác bỏ vào file QC
  - Dùng: `code-review`
  - Để: tìm lỗi đúng-sai trong 5 module vừa sửa, nạp skill TRƯỚC khi mở phase qc. Agent ngoài không
    có skill system: đọc `SKILL.md` của skill đó rồi làm theo.
  - Ra: danh sách phát hiện, mỗi dòng có phán quyết, trong `docs/tdq/qc/<slug>.md`
  - Kiểm: mục QC của file đó có ít nhất một dòng cho mỗi phát hiện
  - Không dùng cho: việc rút gọn code — đó là T8.2
  - Cần: T7.3
- [x] **T8.2** (e10m) Rút gọn phần trùng lặp sau khi 5 module xong — Test: trọn bộ test vẫn xanh
  sau khi rút gọn
  - Dùng: `simplify`
  - Để: gỡ trùng lặp và chỗ rườm rà trong mã mới viết, nạp skill TRƯỚC khi sửa. Agent ngoài không
    có skill system: đọc `SKILL.md` của skill đó rồi làm theo.
  - Ra: mã đã rút gọn, không đổi hành vi
  - Kiểm: `python -m unittest discover -s tests -q`
  - Không dùng cho: việc săn lỗi đúng-sai — đó là T8.1
  - Cần: T8.1

## Luật file nóng

`scripts/tdq_lsp.py` bị **5 task** chạm (T1.1–T1.4 và gián tiếp T3.2 qua import), và
`scripts/tdq_setup.py` bị **6 task** chạm (T3.2–T3.5, T4.3, T6.1). Cả hai xử theo cách **nâng lên
đợt sớm**: T1.1 ổn định lại phép dò trước, T3.2 dựng khung file mới trước, mọi task sau nhánh ra từ
file đã ổn định. Không task nào được sửa hai file đó song song với task khác.

## Cụm song song

Ba cụm không giao nhau về file:

- Cụm A: `scripts/tdq_lsp.py` (P1)
- Cụm B: `scripts/tdq_setup.py` + `skills/tdq-setup/` (P3)
- Cụm C: `docs/claude-md-mau.md` + năm file skill trích luật (P4)

Tôi đã định viết "một cụm, không chạy song song" vì hai file nóng ở trên. Phép đo bác lại điều đó:
`simulate` đọc chính các dòng `Chạm:` này, tự giữ 12 task đụng file nóng cho leader, và vẫn giao
được 13 task còn lại — đội thắng 20,2 phút. Nên ràng buộc file nóng đã được máy tính vào rồi, và
trần song song thật là 13 task chứ không phải 2 nhánh như tôi ước lượng bằng mắt.

## Definition of Done

- [x] Q1 Bậc 5 không phụ thuộc PATH — `python -m unittest tests.test_bac_lumen_hieu_ung -k path`
- [x] Q2 Bậc 5 bắt được lumen không trả lời — `python -m unittest tests.test_bac_lumen_hieu_ung -k vong`
- [x] Q3 Bậc 5 bắt được index thiếu nội dung mới — `python -m unittest tests.test_bac_lumen_hieu_ung -k noidung`
- [x] Q4 Bậc graphify — `python -m unittest tests.test_bac_lumen_hieu_ung -k graphify`
- [x] Q5 Reindex vào kết turn — `python -m unittest tests.test_finish_reindex -k ok`
- [x] Q6 Reindex không treo turn — `python -m unittest tests.test_finish_reindex -k tran`
- [x] Q7 Cờ bỏ graphify đã biến mất — `python scripts/tdq_finish.py --skip-graphify --dry-run` thoát khác 0
- [x] Q8 Đổi tên trọn vẹn — `grep -rn "tdq-lsp-setup" scripts skills tests README.md` không ra dòng nào
- [x] Q9 `setup` cài, kiểm và smoke test — `python -m unittest tests.test_tdq_setup -k smoke`
- [x] Q10 File nợ — `python -m unittest tests.test_tdq_setup -k no`
- [x] Q11 `setup` vá được hook plugin — `python -m unittest tests.test_tdq_setup -k hook`
- [x] Q12 Luật 4 tầng — `python -m unittest tests.test_luat_4_tang`
- [x] Q13 Năm chỗ trích luật không lệch — `python -m unittest tests.test_tdq_setup_skill`
- [x] Q14 Khối ghim user-level — `python -m unittest tests.test_claude_md_core -k khoi`
- [x] Q15 Trần byte bản mẫu — `python -m unittest tests.test_claude_md_core -k byte`
- [x] Q16 Đồ thị graphify — `graphify query --label antigravity_portable` không ra node nào
- [x] Q17 Ba hệ — `python -m unittest discover -s tests -q` trên Windows, Linux và macOS
- [x] Q18 Không làm rối môi trường hai máy đo — kiểm sau khi đo: không gói mới, không cấu hình đổi, thư mục tạm đã xoá
- [x] Q19 Ràng buộc kiến trúc — `grep -rn "import hooks" scripts` không ra dòng nào
- [x] Q20 Nợ đã khai — `grep -n "mem0" docs/tdq/no-phu-thuoc.md` ra đúng một dòng
