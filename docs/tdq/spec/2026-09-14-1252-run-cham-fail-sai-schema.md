# SPEC — `run` chấm đúng kết quả Codex khi model không theo output-schema

Ngày: 2026-09-14 · Bản: 1.0 · Brief: ../brief/2026-09-14-1252-run-cham-fail-sai-schema.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- Mục tiêu: một lượt `python3 scripts/tdq_codex.py run` mà Codex làm đúng việc và trả
  `{"xong": true}` (trần, hoặc bọc trong đúng một rào code bao trọn cả file) được chấm `xong`.
  Mọi ca còn lại — văn thường, JSON lẫn giữa chữ, `xong` khác `true`, bị chặn, quá hạn, exit ≠ 0 —
  vẫn chấm `fail`/`deny`/`timeout`; dòng log của lượt không `xong` ghi rõ mã lý do.
- Trong phạm vi:
  - Cách đọc file kết quả `ket-qua.json` (`doc_ket_qua` trong `scripts/tdq_codex.py`).
  - Phán quyết theo GIÁ TRỊ của khoá `xong`, không chỉ sự có mặt (`phan_quyet`).
  - Schema ghi ra `schema.json` trong `_cli_run` thêm `"additionalProperties": false`.
  - Dòng log một lượt (`dong_log_luot`) thêm trường `ly_do=<mã>` ở CUỐI dòng khi trạng thái ≠ `xong`.
  - Khuôn prompt cố định + đoạn "The result shape Codex must return" trong
    `skills/tdq-build/references/codex-mode.md`.
  - Sinh lại bundle bằng `scripts/build_portable.py`.
- NGOÀI phạm vi:
  - Sửa 9router hoặc cấu hình provider để schema tới được Gemini (không phải code của repo này).
  - Tìm JSON ở giữa câu chữ (người dùng chọn 1a, loại 1b).
  - Khoá thừa ngoài `xong` (vd. `{"xong": true, "ghi_chu": "…"}`): giữ nguyên hành vi hiện tại là
    CHẤP NHẬN — giá trị `xong` vẫn rõ ràng, và đổi luật này không nằm trong 4 câu đã hỏi.
  - Thứ tự "in dòng log trước, hậu kiểm vùng file sau" trong `_cli_run`: lượt bị hạ `fail` do hậu
    kiểm vẫn mang `xong` trên dòng log như hôm nay. Ghi nhận, không sửa ở request này.
  - `scripts/tdq_bench.py`: không sửa code, chỉ kiểm tương thích với dòng log mới.
  - `dung_lenh`, `hau_kiem`, `dung_codex_home`, lệnh `check`/`dong-y`.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ (đã chạy ở analyze) | gốc lỗi đã có 4 lần chạy thật + mã nguồn codex/9router; không cần thêm |
| Interview | CÓ (đã xong) | 4 câu, người dùng trả lời "1a 2a 3a 4a" |
| Spec → plan | CÓ | khung bất biến |
| Review spec/plan bằng agent `tdq-reviewer` | CÓ | đụng nguyên tắc "không biết thì phải FAIL" — cần mắt thứ hai soi ca biên của cách đọc rào code |
| Chia subagent | BỎ | 3 module nhỏ nối tiếp nhau, module 2–3 phụ thuộc module 1 |
| QC độc lập (agent `tdq-qc-tester`) | CÓ | kèm lượt `run` thật với model hiện tại |
| Report | CÓ | khung bất biến |

Luồng tính năng: (1) đọc `ket-qua.json` · (2) phán quyết theo giá trị `xong` kèm mã lý do ·
(3) khuôn schema gửi đi · (4) dòng log mang lý do · (5) luật trong `codex-mode.md` + bundle.

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Đọc kết quả nhận JSON trần hoặc JSON trong đúng một rào code bao trọn file | `scripts/tdq_codex.py` · `doc_ket_qua` | Q1, Q2 |
| 2 | Phán quyết chỉ `xong` khi `xong` là boolean `true`; mỗi ca không `xong` có một mã lý do trong tập đóng | `scripts/tdq_codex.py` · `phan_quyet` + hàm trả kèm lý do | Q3, Q4 |
| 3 | `schema.json` mang `"additionalProperties": false` | `scripts/tdq_codex.py` · `_cli_run` | Q5 |
| 4 | Dòng log lượt không `xong` kết thúc bằng `· ly_do=<mã>`; `tdq_bench` vẫn đọc đúng | `scripts/tdq_codex.py` · `dong_log_luot`, `_cli_run` | Q6, Q7 |
| 5 | Khuôn prompt dặn "không bọc rào code"; đoạn luật khuôn kết quả mô tả đúng cách đọc mới | `skills/tdq-build/references/codex-mode.md` | Q8 |
| 6 | Bundle sinh lại khớp nguồn | `portable_claude/`, `portable_codex/`, `portable_src/`, `portable_codex.zip` | Q9 |
| 7 | Lượt `run` thật với `ag/gemini-3.8-flash-medium`: việc làm được → `xong`; việc không làm được → không `xong` kèm lý do | ghi bằng chứng vào `docs/tdq/qc/2026-09-14-1252-run-cham-fail-sai-schema.md` | Q10, Q11 |

## 2b. Ranh giới module

Ranh giới lấy từ LSP `find_references` (2026-09-14): `phan_quyet` 1 nơi gọi trong `scripts`
(`_cli_run`) + 6 tham chiếu `tests`; `doc_ket_qua` 1 nơi gọi (`_cli_run`) + 3 tham chiếu `tests`;
`dong_log_luot` 1 nơi gọi (`_cli_run`) + 2 tham chiếu `tests` (khớp grep trong file test phần `run`).
Không script nào khác gọi 3 hàm này; `tdq_bench` chỉ đọc chuỗi log, không import `tdq_codex`.

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| M1 phán quyết | `scripts/tdq_codex.py` + file test phần `run` của nó (tên chốt ở plan) | không | 1, 2, 3, 4 |
| M2 tương thích bench | file test của `tdq_bench` (tên chốt ở plan) | M1 (khuôn dòng log) | 4 |
| M3 luật & bundle | `skills/tdq-build/references/codex-mode.md`, `portable_claude/`, `portable_codex/`, `portable_src/`, `portable_codex.zip` | M1 | 5, 6 |

Đầu ra 7 là bằng chứng QC, chạy sau cả 3 module.

## 3. Cách tiếp cận & lý do

- Chọn — đọc kết quả:
  1. Đọc file, strip. Rỗng / không mở được → lý do `khong-co-ket-qua`.
  2. Nếu nội dung đã strip MỞ bằng một dòng rào (ba dấu backtick, nhãn ngôn ngữ trống hoặc `json`,
     không phân biệt hoa thường) VÀ KẾT THÚC bằng một dòng chỉ gồm ba dấu backtick VÀ phần giữa
     không chứa thêm ba dấu backtick nào → lấy phần giữa. Mọi dạng khác giữ nguyên văn bản.
  3. `json.loads` phần đã chọn; hỏng hoặc không phải object → lý do `ket-qua-sai-khuon`.
- Chọn — phán quyết (thứ tự giữ nguyên như hôm nay):
  `qua-han` → `timeout` · dấu hiệu chặn → `deny` (`bi-chan`) · exit ≠ 0 → `fail` (`exit-khac-0`) ·
  không có kết quả → `fail` (`khong-co-ket-qua`) · sai khuôn → `fail` (`ket-qua-sai-khuon`) ·
  thiếu khoá `xong` hoặc `xong` không phải boolean → `fail` (`ket-qua-sai-khuon`) ·
  `xong` là `false` → `fail` (`model-bao-chua-xong`) · `xong` là `true` → `xong`, không lý do.
  Tập mã lý do là ĐÓNG (6 mã: `qua-han`, `bi-chan`, `exit-khac-0`, `khong-co-ket-qua`,
  `ket-qua-sai-khuon`, `model-bao-chua-xong`), khai thành một hằng trong `tdq_codex.py`.
  Kiểm boolean bằng `is True` — trong Python `1 == True`, so bằng `==` sẽ nhận nhầm `1`.
- Chọn — giữ giao diện: `phan_quyet(...)` vẫn trả một chuỗi trạng thái (6 tham chiếu test đang
  dùng giữ nguyên); thêm một hàm trả cặp (trạng thái, lý do) để `_cli_run` dùng, `phan_quyet` gọi
  lại hàm đó. `doc_ket_qua` vẫn trả dict hoặc `None` theo cách tương tự.
- Chọn — dòng log: thêm `· ly_do=<mã>` SAU `dau="…"` chỉ khi trạng thái ≠ `xong`. Regex
  `MAU_LOG_LUOT` của `tdq_bench` neo ở đầu dòng (`luot … · <giây>s · <trạng thái> ·`) nên trường
  thêm ở cuối không làm lệch; lượt `fail` vẫn bị loại khỏi mẫu thời gian như hôm nay.
- Vì: research xác nhận `codex` không kiểm đầu ra theo schema và 9router bỏ schema với model `ag/`
  (brief § Research, mục 2–3) → wrapper phải tự đọc cho đúng. R2/R3 cho thấy ca thật là rào code
  quanh JSON đúng; nhận đúng MỘT rào bao trọn file thì sửa được ca đó mà văn thường vẫn `fail`.
  `additionalProperties: false` là điều kiện của strict mode OpenAI thật (research mục 4).
- Đã loại:
  - Tìm object JSON đầu tiên trong văn bản — người dùng loại (1b); đọc nhầm câu chỉ nhắc tới JSON.
  - Chỉ dặn thêm trong prompt — người dùng loại (1c); router không ép khuôn nên vẫn fail ngẫu nhiên.
  - Đổi chữ ký `doc_ket_qua`/`phan_quyet` thành trả tuple — phải sửa 9 tham chiếu test không vì lý do hành vi.
  - Thêm trạng thái mới (ngoài 4 trạng thái) — người dùng chọn giữ `fail` + lý do (4a).

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG. Kiểm kê ngày 2026-09-14: 10 skill
trên đĩa, cộng skill built-in trong context.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | khung workflow đang chạy |
| tdq-spec | plugin:tdq-workflow | NỀN | khung workflow đang chạy |
| tdq-plan | plugin:tdq-workflow | NỀN | khung workflow đang chạy |
| tdq-build | plugin:tdq-workflow | NỀN | khung workflow đang chạy |
| tdq-conventions | plugin:tdq-workflow | NỀN | khung workflow đang chạy |
| tdq-lsp-setup | plugin:tdq-workflow | NỀN | khung workflow đang chạy |
| tdq-status | plugin:tdq-workflow | NỀN | khung workflow đang chạy |
| tdq-check-status | plugin:tdq-workflow | NỀN | khung workflow đang chạy |
| graphify | user | DÙNG | cuối turn có sửa code: `graphify extract . --code-only` giữ đồ thị mới |
| Đã xét 1 skill khác | user/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: dòng log lượt đã có timestamp, mã task, model thật, CODEX_HOME, thời
  gian, trạng thái, sha256 prompt; request này thêm mã lý do. Bật/tắt vẫn qua cơ chế `log()` hiện
  có (biến môi trường `TDQ_LOG`), không thêm cờ mới.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật. Bằng chứng §2 dòng 7
  là lượt `codex` thật qua provider của máy.
- Mỗi thành phần có unit test riêng, đi red → green, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo
  `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong
  `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`):
- "`skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill" — việc
  này chạm ở `codex-mode.md`: mô tả luật đọc bằng lời, không chép code hay regex.
- "chú thích/docstring của `hooks/` + `scripts/` và chuỗi máy in ra đều viết TIẾNG ANH cố định …
  `scripts/i18n_check.py` gác tầng 1-2" — chạm ở docstring/chú thích mới trong `tdq_codex.py`;
  mã lý do là định danh máy không dấu, cùng kiểu với `xong`/`fail`/`luot` đang có.
- "Luật bản ngoài … SINH bằng `scripts/build_portable.py` … không sửa tay" — chạm ở đầu ra 6.

Không cần tải hay cài gói nào. Model dùng cho QC: `ag/gemini-3.8-flash-medium` qua provider
`9router` đã được người dùng đồng ý sẵn (cờ đồng ý không đổi); chi phí là 2 lượt gọi thật.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Nhận rào code quá rộng làm lọt văn bản có JSON ở giữa | lượt không rõ bị chấm `xong` | chỉ nhận khi rào MỞ ở đầu và ĐÓNG ở cuối file, không có rào thứ hai; test cho văn trước rào, văn sau rào, hai rào |
| `1`/`"true"` bị coi là `true` | lượt sai khuôn thành `xong` | so bằng `is True`; test riêng từng giá trị |
| Trường `ly_do` làm `tdq_bench` đọc sai | mẫu thời gian lệch | test `doc_log_codex` trên dòng có và không có `ly_do` |
| Model trả khác R2/R3 ở lượt QC thật (vd. văn thường) | Q10 không đạt dù code đúng | chạy lại tối đa 3 lượt; cả 3 không đạt thì ghi nguyên văn `ket-qua.json` và báo người dùng, không nới luật đọc |
| Prompt chứa khoá API bị ghi vào log | lộ bí mật trên repo công khai | giữ `mask_secrets` + chỉ sha256 như hiện tại; không in `~/.codex/config.toml` |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Đọc kết quả — dạng được nhận | JSON trần; rào có nhãn `json`; rào không nhãn; rào nhãn `JSON`; có khoảng trắng/xuống dòng quanh rào → đều ra dict |
| Q2 | Đọc kết quả — dạng bị từ chối | văn thường (nguyên văn Q13/Q21b/R1); văn trước rào; văn sau rào; hai rào; rào không đóng; rào nhãn ngôn ngữ khác `json`; JSON mảng; file rỗng; file không có → đều ra `None` |
| Q3 | Phán quyết theo giá trị `xong` | chỉ `{"xong": true}` ra `xong`; `false` → `fail`; `"true"`, `1`, `null`, thiếu khoá → `fail` |
| Q4 | Mã lý do | mỗi nhánh không `xong` trả đúng 1 mã trong tập 6 mã đóng; `xong` không mang mã; thứ tự timeout > deny > exit > kết quả giữ nguyên; 6 ca test cũ của `phan_quyet` vẫn xanh không sửa |
| Q5 | Schema | `schema.json` do `_cli_run` ghi ra có `additionalProperties` = `false`, `required` = `["xong"]` |
| Q6 | Dòng log | lượt không `xong` kết thúc bằng `· ly_do=<mã>`; lượt `xong` không có `ly_do`; 7 mảnh cũ còn đủ; dòng vẫn < 300 ký tự với prompt 200+ ký tự |
| Q7 | Tương thích bench | `doc_log_codex` đếm đúng lượt `xong` và bỏ lượt `fail` trên dòng log có `ly_do` |
| Q8 | Luật | khuôn prompt trong `codex-mode.md` có câu cấm bọc rào code; đoạn khuôn kết quả nêu: nhận đúng một rào bao trọn file, `xong` phải là `true`, lượt không `xong` ghi mã lý do; `i18n_check` và `doc_lint` không báo lỗi mới |
| Q9 | Bundle | sinh lại bằng `build_portable.py`; bản `codex-mode.md` và `tdq_codex.py` trong bundle trùng byte với nguồn; kiểm portable không báo lỗi mới |
| Q10 | Lượt thật — làm được | `run` với `ag/gemini-3.8-flash-medium` trên task scratch làm được → JSON in ra có `trang_thai` = `xong`, lệnh exit 0 |
| Q11 | Lượt thật — không làm được | `run` trên task scratch không thể xanh trong vùng file cho phép → `trang_thai` ≠ `xong`, dòng log mang `ly_do` thuộc tập đóng |
| Q12 | Hồi quy | toàn bộ test của `tdq_codex` (phần `run` và CLI) và `tdq_bench` xanh; bộ test đầy đủ không có fail/error MỚI so với mốc 290 fail / 4 error có sẵn |

DoD: Q1–Q12 PASS có bằng chứng ghi trong file QC; plan tick hết; không file bí mật nào bị commit;
working log ghi đủ.

## 7. Câu hỏi còn mở

(rỗng)
