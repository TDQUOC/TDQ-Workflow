# SPEC — sai khuôn thì lấy test làm chuẩn

Ngày: 2026-09-14 · Bản: 1.0 · Brief: ../brief/2026-09-14-1417-sai-khuon-lay-test-lam-chuan.md · Lane: full
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

- Mục tiêu: Codex có thể làm đúng việc mà vẫn trả lời sai khuôn hoặc không để lại file kết quả.
  Một lượt `python3 scripts/tdq_codex.py run` như vậy không còn làm leader bỏ một task đã xanh.
  JSON phán quyết của `run` nói rõ lý do và báo lượt nào phải chạy lại test. Leader chạy lại
  test: xanh + vùng file `dat` thì tick, đỏ thì fail như hôm nay.
- Trong phạm vi:
  - `scripts/tdq_codex.py`:
    - hằng tập mã được cứu bằng test gồm `ket-qua-sai-khuon` và `khong-co-ket-qua`;
    - hàm quyết định `can_chay_lai_test`;
    - hàm dựng dict phán quyết;
    - `_cli_run` in thêm 2 khoá `ly_do` và `can_chay_lai_test`.
  - Test đơn vị cho hàm mới, cộng test đầu-cuối cho `_cli_run` chạy bằng Codex giả. Test này trả
    luôn nợ "`_cli_run` chưa có test" của request trước.
  - Luật `skills/tdq-build/references/codex-mode.md`:
    - bước 4 đọc 2 khoá mới;
    - bước 6 thêm nhánh "cứu bằng test" và cách ghi chú lúc tick;
    - mục tự kiểm có một dòng tương ứng.
  - Một câu trong checklist mode `codex` của `scripts/tdq_state.py`, câu đang nói "Flip to [x] …
    once the test is green and the audit passes".
  - Sinh lại bundle bằng `scripts/build_portable.py`.
  - Phát hành: tăng version 0.46.1 → 0.47.0, thêm mục CHANGELOG (xoay mục cũ nhất sang lưu trữ để
    giữ dưới trần 500 dòng), commit, merge `--no-ff` vào `main`. Người dùng đã uỷ quyền trước:
    "1a và merge vào main và pump version và commit". Không push.
- NGOÀI phạm vi:
  - `run` tự chạy lệnh test (người dùng loại 1b).
  - Cứu `model-bao-chua-xong` (người dùng loại 2c). Cứu `qua-han`, `bi-chan`, `exit-khac-0`:
    không bao giờ, ở mọi phương án.
  - Trạng thái mới trong dòng log, hoặc lệnh con ghi `xong-nho-test` (người dùng loại 3b).
    Dòng log của `run` giữ nguyên, `tdq_bench.doc_log_codex` không đổi.
  - Thêm mã lý do cho lượt `xong` bị hạ `fail` do vi phạm vùng file. Tập `MA_LY_DO` giữ đóng
    6 mã; lượt đó in `ly_do: null` và `vung_file.dat: false`.
  - Push lên origin.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | thay đổi thuần nội bộ; hành vi schema của Codex CLI đã đo thật ở request `2026-09-14-1252-run-cham-fail-sai-schema` |
| Vòng scope | BỎ | một hành vi, không chạm dữ liệu user/tiền/API công khai |
| Interview | CÓ (đã xong) | 4 câu, người dùng trả lời "1a 2a 3a 4a" |
| Spec → plan | CÓ | khung bất biến |
| Chia subagent | BỎ | module 2–4 đều phụ thuộc khuôn JSON của module 1 |
| QC độc lập (agent `tdq-qc-tester`) | BỎ | các mục QC là test đơn vị + lượt Codex thật mà leader phải tự chạy (cờ đồng ý thuộc máy này); leader chạy lại toàn bộ và ghi bằng chứng |
| Report + phát hành | CÓ | kèm commit, tăng version, merge (đã uỷ quyền) |

Luồng tính năng: (1) `run` báo lý do + cờ chạy lại test trong JSON · (2) leader chạy lại test theo
luật, xanh + `dat` thì tick kèm ghi chú · (3) ghi chú trên dòng tick để QC/report đếm được.

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Tập mã được cứu bằng test (đúng 2 mã) + hàm quyết định `can_chay_lai_test` | `scripts/tdq_codex.py` | Q1, Q2 |
| 2 | Dòng JSON của `run` có đủ 5 khoá `trang_thai`, `giay`, `vung_file`, `ly_do`, `can_chay_lai_test` | `scripts/tdq_codex.py` · `_cli_run` + hàm dựng phán quyết | Q3 |
| 3 | Test đầu-cuối `_cli_run` với Codex giả: trả sai khuôn, không có file, `{"xong": true}`, `{"xong": false}`, vi phạm vùng | file test phần CLI của `tdq_codex` (tên chốt ở plan) | Q4 |
| 4 | Luật bước 4, bước 6, mục tự kiểm + câu checklist mode `codex` | `skills/tdq-build/references/codex-mode.md`, `scripts/tdq_state.py` | Q5 |
| 5 | Bundle sinh lại khớp nguồn | `portable_claude/`, `portable_codex/`, `antigravity_portable/` | Q6 |
| 6 | Lượt `run` thật in đủ khoá mới; lượt thật trả sai khuôn được cứu bằng test | bằng chứng trong `docs/tdq/qc/2026-09-14-1417-sai-khuon-lay-test-lam-chuan.md` | Q7, Q8 |
| 7 | Không hồi quy | toàn bộ bộ test | Q9 |
| 8 | Phát hành 0.47.0, merge vào `main` | `.claude-plugin/plugin.json`, `CHANGELOG.md`, `CHANGELOG-archive.md`, manifest bundle | Q10 |

## 2b. Ranh giới module

Ranh giới lấy từ LSP `find_references` (2026-09-14):
- `phan_quyet_ly_do`: 5 tham chiếu, 2 ở `scripts` (`_cli_run` và `phan_quyet`), 3 ở `tests`.
- `_cli_run`: 1 tham chiếu (bảng lệnh con trong `tdq_codex.py`), 0 ở `tests`.
- Dòng JSON của `run` không có script nào đọc. Grep `trang_thai` chỉ gặp `tdq_eval.py`, nhưng đó là
  trường cùng tên của bộ đo khác, không đọc đầu ra của `run`.
- `_TASK_LINE` của `tdq_state.task_open_count` khớp từ đầu dòng, nên ghi chú thêm ở cuối dòng tick
  không đổi cách đếm.

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| M1 phán quyết | `scripts/tdq_codex.py` + file test phần `run` của nó (tên chốt ở plan) | không | 1, 2 |
| M2 đầu-cuối | file test phần CLI của `tdq_codex` (tên chốt ở plan) | M1 | 3 |
| M3 luật | `skills/tdq-build/references/codex-mode.md`, `scripts/tdq_state.py` | M1 (tên khoá) | 4 |
| M4 bundle & phát hành | `portable_claude/`, `portable_codex/`, `antigravity_portable/`, `.claude-plugin/plugin.json`, `CHANGELOG.md`, `CHANGELOG-archive.md` | M1, M3 | 5, 8 |

Đầu ra 6 và 7 là bằng chứng QC, chạy sau cả 4 module.

## 3. Cách tiếp cận & lý do

- Chọn — quyết định chạy lại test:
  `can_chay_lai_test = (trang_thai == "fail") VÀ (ly_do thuộc tập 2 mã) VÀ vung_file.dat`.
  Vùng file không đạt thì luôn `false`: bước 5 bắt rollback trước, chạy test trên cây bẩn là đo sai.
  Tập 2 mã khai thành một hằng cạnh `MA_LY_DO`, và mọi phần tử phải thuộc `MA_LY_DO` (có test khoá).
- Chọn — khuôn JSON: `ly_do` là mã trong `MA_LY_DO`, hoặc `null` khi `xong` hay khi `fail` chỉ do
  vùng file. `can_chay_lai_test` luôn là boolean. Thứ tự khoá: `trang_thai`, `giay`, `vung_file`,
  `ly_do`, `can_chay_lai_test`. Exit code giữ nguyên: 0 khi `xong`, 1 khi khác. `run` không tự đổi
  `fail` thành `xong`, vì chỉ test mới được nói task xong.
- Chọn — tách hàm dựng phán quyết ra khỏi `_cli_run`, để khuôn JSON được test không cần tiến trình con.
- Chọn — test đầu-cuối: repo git tạm có 1 commit, `CODEX_HOME` giả trỏ vào thư mục tạm (theo cách
  `KiemSongThatTest` đang làm), một `codex` giả trên `PATH` ghi nội dung chọn trước vào file sau cờ
  kết quả. Test không bao giờ đọc `~/.codex` thật.
- Chọn — luật:
  - Bước 4 đọc `trang_thai`, `ly_do`, `can_chay_lai_test`, `vung_file`.
  - Bước 6: `can_chay_lai_test` là `true` thì chạy lại test. Xanh → tick `[x]`, ghi chú
    `(cứu bằng test · ly_do=<mã>)` ở cuối dòng task. Đỏ → task fail, xử lý như fail thường.
  - Mọi lượt khác giữ luật cũ.
- Vì: bước 6 đã coi test là thước đo, nhưng leader chỉ thấy `fail` nên không biết lượt nào đáng đo
  lại. Khoá mới đưa tín hiệu đó vào đúng chỗ leader đọc, và không phụ thuộc công tắc `TDQ_LOG`.
- Đã loại:
  - `run` nhận `--lenh-test` (1b): test bị chạy 2 lần, script phải chạy lệnh do prompt đưa vào.
  - Chỉ sửa luật (1c): leader phải đọc stderr, tín hiệu mất khi `TDQ_LOG=0`.
  - Cứu `model-bao-chua-xong` (2c): model tự nhận chưa xong là bằng chứng ngược, không phải
    "không biết".
  - Thêm trạng thái `xong-nho-test` (3b): thêm lệnh và trạng thái mới cho một số đo bench chưa ai cần.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG. Kiểm kê ngày 2026-09-14: 10 skill
trên đĩa, cộng skill built-in trong context.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | phase analyze |
| tdq-spec | plugin:tdq-workflow | NỀN | phase spec |
| tdq-plan | plugin:tdq-workflow | NỀN | phase plan |
| tdq-build | plugin:tdq-workflow | NỀN | implement/QC/report; chứa file luật bị sửa |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật chung, state, duyệt |
| tdq-lsp-setup | plugin:tdq-workflow | NỀN | thứ tự tìm ký hiệu code |
| Đã xét 4 skill khác | plugin/user/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: dòng log lượt hiện có vẫn đủ timestamp, mã task, model, CODEX_HOME,
  thời gian, trạng thái, sha256 prompt và `ly_do`; request này không đổi dòng log. Bật/tắt vẫn qua
  biến môi trường `TDQ_LOG`. Dòng JSON phán quyết in ra stdout ở mọi giá trị công tắc, vì đó là
  đầu ra của lệnh, không phải log.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật. Codex giả chỉ nằm
  trong test. Bằng chứng §2 dòng 6 là lượt `codex` thật.
- Mỗi thành phần có unit test riêng, đi red → green, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo
  `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong
  `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`):
- "`skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill" — chạm ở
  `codex-mode.md`: chỉ nêu tên khoá JSON và tên mã, không chép code.
- "chú thích/docstring của `hooks/` + `scripts/` và chuỗi máy in ra đều viết TIẾNG ANH cố định" —
  chạm ở docstring mới trong `tdq_codex.py` và câu checklist trong `tdq_state.py`. Tên khoá JSON là
  định danh máy không dấu, cùng kiểu `trang_thai`/`vung_file`.
- "Luật bản ngoài … SINH bằng `scripts/build_portable.py` … không sửa tay" — chạm ở đầu ra 5.
- "`CHANGELOG.md` giữ dưới trần 500 dòng của `doc_lint` R6" — chạm ở đầu ra 8 (hiện 498 dòng).

Không cần tải hay cài gói nào. Model dùng cho QC là `ag/gemini-3.8-flash-medium`, cờ đồng ý đã bật
sẵn và không đổi. Chi phí: tối đa 4 lượt gọi thật.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Leader tick lượt sai khuôn mà không chạy lại test | task hỏng được tính xong | luật bước 6 bắt chạy lại; `can_chay_lai_test` không bao giờ tự đổi `trang_thai` sang `xong`; exit vẫn 1 |
| Cứu nhầm lượt vi phạm vùng file | file lạc bị giữ lại | `can_chay_lai_test` = `false` khi `vung_file.dat` = `false`; có test đầu-cuối riêng |
| Test đầu-cuối đọc/copy `~/.codex/config.toml` thật (có khoá sống) | lộ bí mật vào thư mục tạm/log | `CODEX_HOME` giả qua biến môi trường; test khẳng định file config trong home tạm là bản giả |
| Không ép được model thật trả sai khuôn ở Q8 | thiếu bằng chứng lượt cứu thật | prompt dặn trả lời bằng câu chữ thường; thử tối đa 3 lượt; không ra sai khuôn thì ghi nguyên văn kết quả và báo trong report, Q4 vẫn phủ nhánh này |
| CHANGELOG vượt 500 dòng | `doc_lint` R6 đỏ | xoay mục cũ nhất sang `CHANGELOG-archive.md` trước khi thêm mục mới |
| Bộ test đầy đủ có sẵn fail do sổ lượt thật (`test_codex_edit_gate`) | nhầm là hồi quy | so với mốc đo trên HEAD cùng lúc, như request trước |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Tập mã cứu được | đúng 2 mã `ket-qua-sai-khuon`, `khong-co-ket-qua`; mọi phần tử thuộc `MA_LY_DO` |
| Q2 | Hàm quyết định | `true` chỉ khi `fail` + mã thuộc tập + vùng `dat`; `false` với `xong`, `timeout`, `deny`, `exit-khac-0`, `model-bao-chua-xong`, và với mã cứu được nhưng vùng không `dat` |
| Q3 | Khuôn JSON | đúng 5 khoá theo thứ tự đã chốt; `ly_do` là `null` khi `xong`; `can_chay_lai_test` là boolean; exit 0 chỉ khi `xong` |
| Q4 | Đầu-cuối `_cli_run` | Codex giả trả văn thường → `fail`/`ket-qua-sai-khuon`/`true`, exit 1 · không ghi file → `fail`/`khong-co-ket-qua`/`true` · `{"xong": true}` → `xong`/`null`/`false`, exit 0 · `{"xong": false}` → `fail`/`model-bao-chua-xong`/`false` · sai khuôn + ghi file ngoài vùng → `can_chay_lai_test` `false`, `vung_file.dat` `false`; không test nào đọc `~/.codex` thật |
| Q5 | Luật | `codex-mode.md` bước 4 nêu 2 khoá mới; bước 6 nêu nhánh cứu bằng test và khuôn ghi chú `(cứu bằng test · ly_do=<mã>)`; mục tự kiểm có dòng tương ứng; câu checklist mode `codex` trong `tdq_state.py` nêu nhánh này; `i18n_check` và `doc_lint` không báo lỗi mới |
| Q6 | Bundle | sinh lại bằng `build_portable.py`; bản `codex-mode.md`, `tdq_codex.py`, `tdq_state.py` trong bundle khớp nguồn (bản Antigravity khác đúng kiểu viết lại đường dẫn); test portable xanh |
| Q7 | Lượt thật — xong | `run` thật trên task scratch làm được → JSON có đủ 5 khoá, `xong`, `ly_do` `null`, `can_chay_lai_test` `false` |
| Q8 | Lượt thật — cứu bằng test | `run` thật với prompt đòi trả câu chữ thường → `fail`, `ly_do` thuộc tập 2 mã, `can_chay_lai_test` `true`; leader chạy lại phép kiểm của task → xanh; hoặc ghi rõ lý do không tái hiện được theo §5 |
| Q9 | Hồi quy | test `tdq_codex` (run + CLI), `tdq_bench`, `tdq_state` xanh; bộ đầy đủ không có fail/error MỚI so với mốc HEAD đo cùng lúc |
| Q10 | Phát hành | version 0.47.0 ở `plugin.json` và mọi manifest bundle; `CHANGELOG.md` ≤ 500 dòng có mục 0.47.0; `doc_lint` CHANGELOG sạch; nhánh đã merge `--no-ff` vào `main` và bị xoá; không push |

DoD: Q1–Q10 PASS có bằng chứng ghi trong file QC; plan tick hết; không bí mật nào vào file hay
commit; working log ghi đủ.

## 7. Câu hỏi còn mở

(rỗng)
