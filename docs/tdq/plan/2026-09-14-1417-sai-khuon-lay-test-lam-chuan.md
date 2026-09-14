# PLAN — sai khuôn thì lấy test làm chuẩn

Ngày: 2026-09-14 · Spec: ../spec/2026-09-14-1417-sai-khuon-lay-test-lam-chuan.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — `simulate` hệ số 1.5: đội 15.3 phút, main 20.4 phút, đội thắng 5.0 phút; spec §1b từng ghi BỎ chia subagent vì P1 dồn một file nóng, nên chênh lệch nhỏ này user cân nhắc (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH (mode main)

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Phán quyết và khuôn JSON
- P2 — Test đầu-cuối `_cli_run`
- P3 — Luật, checklist, bundle
- P4 — Log & test bắt buộc, lượt thật, hồi quy
- P5 — Phát hành 0.47.0
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy test của các file đã chạm, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Commit, tăng version và merge vào `main` đã được uỷ quyền trước ("1a và merge vào main và pump
   version và commit") — làm ở bước report. Không push.
7. Mọi lệnh test chạy dạng `env -u TDQ_LOG python3 -m unittest discover tests -p "<file>" -k <lớp>`.
8. Không in, không chép `~/.codex/config.toml`; test chỉ dùng `CODEX_HOME` giả; mọi đầu ra lượt thật
   soát `Bearer`/`sk-` trước khi ghi vào file QC.

## P1 — Phán quyết và khuôn JSON

Hai task cùng chạm `scripts/tdq_codex.py` và `tests/test_codex_run.py` (file nóng) → một chủ ghi,
tuần tự. `Chạm:` lấy từ LSP `find_references`: `phan_quyet_ly_do` có 2 nơi gọi trong `scripts`
(`_cli_run`, `phan_quyet`) + 3 tham chiếu test; `_cli_run` chỉ được bảng lệnh con gọi; không script
nào đọc dòng JSON của `run`.

- [x] **T1.1** (e8m) Hằng `MA_LY_DO_CHAY_LAI_TEST = ("khong-co-ket-qua", "ket-qua-sai-khuon")` đặt
  cạnh `MA_LY_DO` + hàm thuần `can_chay_lai_test(trang_thai, ly_do, vung_dat)` → `True` chỉ khi
  `trang_thai == "fail"`, `ly_do` thuộc hằng, `vung_dat is True`. Lớp test mới `ChayLaiTestTest`:
  tập đúng 2 mã và là tập con của `MA_LY_DO` (Q1); bảng ca `xong`/`timeout`/`deny`/`exit-khac-0`/
  `model-bao-chua-xong`/2 mã cứu được × vùng đạt/không đạt (Q2) —
  Test: `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py" -k ChayLaiTestTest`
  - Chạm: `scripts/tdq_codex.py`, `tests/test_codex_run.py` → hằng mới, hàm mới, chưa nơi nào gọi
- [x] **T1.2** (e10m) Hàm thuần `dung_phan_quyet(trang_thai, giay, ly_do, ket_qua_vung)` trả dict đúng
  thứ tự khoá `trang_thai`, `giay`, `vung_file`, `ly_do`, `can_chay_lai_test`; `ly_do` = `None` khi
  `xong`. `_cli_run` in dict này thay cho dict viết tay, exit code giữ nguyên. Lớp test mới
  `PhanQuyetJsonTest`: thứ tự khoá, `ly_do` `None` khi `xong`, `can_chay_lai_test` luôn là `bool`,
  lượt `xong` bị hạ `fail` do vùng → `ly_do` `None` + `can_chay_lai_test` `False` (Q3) —
  Test: `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py" -k PhanQuyetJsonTest`
  - Chạm: `scripts/tdq_codex.py`, `tests/test_codex_run.py` → `_cli_run`, `can_chay_lai_test`
  - Cần: T1.1

**Xong P1 khi**: `test_codex_run.py` toàn file xanh.

## P2 — Test đầu-cuối `_cli_run`

- [x] **T2.1** (e20m) Lớp test mới `RunDauCuoiTest` trong `tests/test_codex_cli.py`:
  - Dựng môi trường: repo git tạm có 1 commit; `CODEX_HOME` giả chứa `config.toml` giả; cờ đồng ý
    + model `m-test` ghi bằng `dat_co_dong_y`.
  - Codex giả trên `PATH` là file mới, riêng với `_codex_gia` của `check`. Nó ghi nội dung chọn trước
    vào file sau cờ `CO_EXEC["ket_qua"]` và tuỳ ca tạo thêm một file trong hoặc ngoài vùng.
  - Gọi `tdq_codex.py run <ma> --prompt p --vung <file> --da-thay-do` bằng tiến trình con.
  - 5 ca (Q4):
    - văn thường → `fail`/`ket-qua-sai-khuon`/`true`, exit 1;
    - không ghi file → `fail`/`khong-co-ket-qua`/`true`;
    - `{"xong": true}` → `xong`/`null`/`false`, exit 0;
    - `{"xong": false}` → `fail`/`model-bao-chua-xong`/`false`;
    - văn thường + file ngoài vùng → `can_chay_lai_test` `false`, `vung_file.dat` `false`.
  - Khẳng định `config.toml` trong home tạm là bản giả, và `HOME` của tiến trình con trỏ vào thư mục tạm.
  - Test: `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_cli.py" -k RunDauCuoiTest`
  - Chạm: `tests/test_codex_cli.py` → lớp test mới; đọc `_cli_run`, `dung_phan_quyet`
  - Cần: T1.2

**Xong P2 khi**: `test_codex_cli.py` toàn file xanh.

## P3 — Luật, checklist, bundle

- [x] **T3.1** (e8m) `skills/tdq-build/references/codex-mode.md`:
  - bước 4 nêu 4 khoá leader đọc (`trang_thai`, `ly_do`, `can_chay_lai_test`, `vung_file`);
  - bước 6 thêm nhánh: `can_chay_lai_test` = `true` → chạy lại test; xanh → tick `[x]` kèm ghi
    chú `(cứu bằng test · ly_do=<mã>)` ở cuối dòng task; đỏ → fail như thường;
  - `run` không bao giờ tự đổi `fail` thành `xong`;
  - mục tự kiểm tách sang T3.4 (cổng TICK chặn sau 3 lần sửa liền, việc nhỏ hơn thì tick sớm hơn).
  - Test: `grep -c "can_chay_lai_test" skills/tdq-build/references/codex-mode.md` ≥ 3 · `grep -c "cứu bằng test" skills/tdq-build/references/codex-mode.md` ≥ 1 · `python3 scripts/i18n_check.py skills/tdq-build/references/codex-mode.md` exit 0 · `python3 scripts/doc_lint.py skills/tdq-build/references/codex-mode.md` exit 0
  - Cần: T1.2
- [x] **T3.2** (e4m) (i18n exit 1 do 7 dòng có sẵn ở HEAD, giống hệt; dòng mới có `# i18n-allow`, không thêm dòng nào) Câu checklist mode `codex` trong `scripts/tdq_state.py` ("Flip to [x] … once the
  test is green and the audit passes") thêm vế tiếng Anh: `run` in `can_chay_lai_test: true` thì
  chạy lại test, xanh + audit đạt vẫn tick và ghi chú lý do cứu —
  Test: `grep -c "can_chay_lai_test" scripts/tdq_state.py` = 1 · `python3 scripts/i18n_check.py scripts/tdq_state.py` exit 0 · `env -u TDQ_LOG python3 -m unittest discover tests -p "test_state.py"` không thêm fail so với trước khi sửa
  - Chạm: `scripts/tdq_state.py` → chuỗi checklist mode `codex`, không đổi hàm
  - Cần: T1.2
- [x] **T3.4** (e2m) Mục tự kiểm của `codex-mode.md` thêm mục 6: lượt `fail` có
  `can_chay_lai_test: true` đã được chạy lại test, tick nhờ đó mang ghi chú `(cứu bằng test · ly_do=<mã>)` —
  Test: `grep -c "all six must hold" skills/tdq-build/references/codex-mode.md` = 1 · `grep -c "cứu bằng test" skills/tdq-build/references/codex-mode.md` ≥ 2 · `python3 scripts/i18n_check.py skills/tdq-build/references/codex-mode.md` exit 0
  - Cần: T3.1
- [x] **T3.3** (e6m) Sinh lại bundle bằng `python3 scripts/build_portable.py` (Q6) —
  Test: `env -u TDQ_LOG python3 -m unittest discover tests -p "test_build_portable.py"` · `cmp` bản `tdq_codex.py`, `tdq_state.py`, `codex-mode.md` trong `portable_claude/`, `portable_codex/` với nguồn
  - Chạm: `portable_claude/`, `portable_codex/`, `antigravity_portable/`
  - Cần: T1.2, T3.1, T3.2

**Xong P3 khi**: test portable xanh, các bản sao khớp nguồn.

## P4 — Log & test bắt buộc, lượt thật, hồi quy

- [x] **T4.1** (e6m) Log service: dòng log lượt giữ nguyên (không đổi `dong_log_luot`), bật mặc định,
  tắt bằng `TDQ_LOG=0`; dòng JSON phán quyết vẫn in ra stdout khi `TDQ_LOG=0`. Thêm 1 ca vào
  `RunDauCuoiTest`: `TDQ_LOG=0` → stdout vẫn có đủ 5 khoá, stderr không có dòng `luot`; ca mặc
  định → stderr có dòng `luot … · ly_do=ket-qua-sai-khuon` —
  Test: `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_cli.py" -k RunDauCuoiTest` · `-p "test_codex_run.py" -k LogTest`
  - Chạm: `tests/test_codex_cli.py` → lớp `RunDauCuoiTest`
  - Cần: T2.1
- [x] **T4.2** (e15m) Lượt thật với `ag/gemini-3.8-flash-medium` ở gốc repo, ghi bằng chứng vào
  `docs/tdq/qc/2026-09-14-1417-sai-khuon-lay-test-lam-chuan.md`:
  - Q7: task tạo `docs/tdq/qc/q7-probe.txt` chứa `Q7-OK`, khuôn prompt cố định, `--vung` đúng file đó
    → JSON đủ 5 khoá, `xong`, `ly_do` `null`, `can_chay_lai_test` `false`.
  - Q8: task tạo `docs/tdq/qc/q8-probe.txt` chứa `Q8-OK`, prompt dặn "trả lời bằng một câu tiếng Việt
    thường, KHÔNG trả JSON" → `fail`, `ly_do` thuộc 2 mã, `can_chay_lai_test` `true`; leader chạy lại
    phép kiểm `grep -qx Q8-OK docs/tdq/qc/q8-probe.txt` → xanh. Không tái hiện sau 3 lượt → ghi
    nguyên văn `ket-qua.json` từng lượt, nêu trong report.
  - Dọn: xoá file thăm dò, chạy `python3 scripts/tdq_codex.py cleanup`.
  - Test: JSON in ra của từng lượt + `grep -c -e Bearer -e sk-` trên đầu ra = 0
  - Cần: T1.2, T3.1
- [x] **T4.3** (e10m) (nhánh 1802 test · 294 fail · 4 error; HEAD 1785 · 291 · 4; 3 fail chỉ ở nhánh đều là `test_codex_edit_gate.TestChanNgoaiVung`, chạy riêng xanh ở cả nhánh lẫn HEAD — lệch thứ tự chạy, diff không chạm hook) Hồi quy (Q9): test `tdq_codex` (run + CLI), `tdq_bench`, `tdq_state` xanh; bộ
  đầy đủ không có fail/error MỚI so với mốc HEAD đo cùng lúc trên worktree tách rời;
  `graphify extract . --code-only` —
  Test: `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_*.py"` · `-p "test_bench.py"` · `-p "test_state.py"` · `env -u TDQ_LOG python3 -m unittest discover tests 2>&1 | tail -3` trên nhánh và trên worktree HEAD
  - Cần: T3.3, T4.1

## P5 — Phát hành 0.47.0

- [x] **T5.0** (e3m) Chuyển mục `## 0.26.0` từ `CHANGELOG.md` sang đầu phần cũ của `CHANGELOG-archive.md`
  (tách từ T5.1: cổng TICK chặn lần sửa thứ 4 liền không tick) —
  Test: `grep -c "^## 0.26.0" CHANGELOG.md` = 0 · `grep -c "^## 0.26.0" CHANGELOG-archive.md` = 1 · `python3 scripts/doc_lint.py CHANGELOG.md CHANGELOG-archive.md` exit 0
  - Chạm: `CHANGELOG.md`, `CHANGELOG-archive.md`
- [x] **T5.1** (e10m) Tăng version 0.46.1 → 0.47.0:
  - `.claude-plugin/plugin.json` lên 0.47.0;
  - chuyển mục cũ nhất (`## 0.26.0`) từ `CHANGELOG.md` sang đầu phần cũ của `CHANGELOG-archive.md`,
    giữ đúng thứ tự mới → cũ;
  - thêm mục `## 0.47.0 — 2026-09-14` ở đầu `CHANGELOG.md`;
  - `python3 scripts/build_portable.py` để lan version sang manifest bundle.
  - Test: `wc -l CHANGELOG.md` ≤ 500 · `python3 scripts/doc_lint.py CHANGELOG.md` exit 0 · `grep -n '"version"' .claude-plugin/plugin.json antigravity_portable/plugin.json portable_codex/manifest.json` ra 0.47.0 · `env -u TDQ_LOG python3 -m unittest discover tests -p "test_build_portable.py"` · `-p "test_claude_export.py"` · `-p "test_docs_consistency.py"` xanh
  - Chạm: `.claude-plugin/plugin.json`, `CHANGELOG.md`, `CHANGELOG-archive.md`, `portable_claude/`, `portable_codex/`, `antigravity_portable/`
  - Cần: T4.3

Commit trên nhánh, merge `--no-ff` vào `main`, xoá nhánh là bước 11 của report (đã uỷ quyền), không
phải task của plan; bằng chứng ghi trong report.

## Cụm song song

Một cụm: T1.1–T1.2 cùng chủ ghi `scripts/tdq_codex.py`; T2.1, T3.1, T3.2 tách được về file nhưng
đều `Cần: T1.2`; T3.3 và T5.1 cùng ghi các thư mục bundle; T4.2 là lượt thật tuần tự.

## Definition of Done

Trỏ về §6 của spec.

- [x] Q1 tập 2 mã cứu được, là tập con `MA_LY_DO` — `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py" -k ChayLaiTestTest`
- [x] Q2 hàm quyết định đúng mọi ca trạng thái × vùng — `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py" -k ChayLaiTestTest`
- [x] Q3 khuôn JSON 5 khoá đúng thứ tự, `ly_do` `null` khi `xong` — `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py" -k PhanQuyetJsonTest`
- [x] Q4 đầu-cuối `_cli_run` 5 ca, không đọc `~/.codex` thật — `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_cli.py" -k RunDauCuoiTest`
- [x] Q5 luật + checklist cập nhật, không lỗi i18n/lint mới — `python3 scripts/i18n_check.py skills/tdq-build/references/codex-mode.md scripts/tdq_state.py`
- [x] Q6 bundle khớp nguồn — `env -u TDQ_LOG python3 -m unittest discover tests -p "test_build_portable.py"`
- [x] Q7 lượt thật làm được ra `xong` với 5 khoá — `python3 scripts/tdq_codex.py run Q7 --prompt "<khuôn>" --vung docs/tdq/qc/q7-probe.txt --da-thay-do`
- [x] Q8 lượt thật sai khuôn được cứu bằng test — `python3 scripts/tdq_codex.py run Q8 --prompt "<khuôn + trả câu chữ>" --vung docs/tdq/qc/q8-probe.txt --da-thay-do`
- [x] Q9 không hồi quy — `env -u TDQ_LOG python3 -m unittest discover tests 2>&1 | tail -3`
- [x] Q10 phát hành 0.47.0, CHANGELOG ≤ 500 dòng, merge vào `main` không push — `python3 scripts/doc_lint.py CHANGELOG.md`
