# PLAN — `run` chấm đúng kết quả Codex khi model không theo output-schema

Ngày: 2026-09-14 · Spec: ../spec/2026-09-14-1252-run-cham-fail-sai-schema.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — `simulate` cho main 20,4 phút so với đội 21,5 phút (hệ số agent 1,5); 6/8 task chạm `scripts/tdq_codex.py` hoặc chờ T1.4 (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH ("duyệt plan" · mode main "1a")

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Đọc kết quả, phán quyết, schema, dòng log
- P2 — Tương thích bench
- P3 — Luật & bundle
- P4 — Log & test bắt buộc, lượt thật
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy test của các file đã chạm, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Mọi lệnh test chạy dạng `env -u TDQ_LOG python3 -m unittest discover tests -p "<file>" -k <lớp>`.
8. Không in, không chép `~/.codex/config.toml`; mọi đầu ra lượt thật soát `Bearer`/`sk-` trước khi ghi vào file QC.

## P1 — Đọc kết quả, phán quyết, schema, dòng log

Cả 4 task cùng chạm `scripts/tdq_codex.py` và `tests/test_codex_run.py` (file nóng) → một chủ ghi
tuần tự, không tách song song. `Chạm:` lấy từ LSP `find_references`: `doc_ket_qua` 1 nơi gọi
(`_cli_run`) + 3 tham chiếu test; `phan_quyet` 1 + 6; `dong_log_luot` 1 + 2; không script nào
khác import 3 hàm này.

- [x] **T1.1** (e12m) `doc_ket_qua`: bóc đúng một rào code bao trọn cả nội dung đã strip (dòng mở
  ba backtick, nhãn trống hoặc `json` không phân biệt hoa thường; dòng cuối chỉ ba backtick; phần
  giữa không còn ba backtick nào) rồi mới `json.loads`; mọi dạng khác giữ nguyên văn. Lớp test mới
  `DocKetQuaRaoTest`: 5 dạng nhận (Q1) + 9 dạng từ chối, gồm nguyên văn Q13/Q21b/R1 (Q2) —
  Test: `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py" -k DocKetQuaRaoTest`
  - Chạm: `scripts/tdq_codex.py`, `tests/test_codex_run.py` → `doc_ket_qua`, `_cli_run`
- [x] **T1.2** (e14m) Hằng `MA_LY_DO` (6 mã đóng) + hàm `doc_ket_qua_ly_do` (trả dict/None kèm
  `khong-co-ket-qua` hoặc `ket-qua-sai-khuon`) + hàm `phan_quyet_ly_do` trả (trạng thái, lý do) theo
  thứ tự timeout > deny > exit > kết quả > giá trị `xong` (`is True`); `doc_ket_qua` và `phan_quyet`
  gọi lại hai hàm mới, chữ ký không đổi. Lớp test mới `PhanQuyetLyDoTest` (Q3, Q4) và lớp cũ
  `PhanQuyetTest` giữ xanh không sửa — Test: `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py" -k PhanQuyet`
  - Chạm: `scripts/tdq_codex.py`, `tests/test_codex_run.py` → `doc_ket_qua`, `phan_quyet`, `_cli_run`
  - Cần: T1.1
- [x] **T1.3** (e6m) Hàm thuần `khuon_schema()` trả schema có `additionalProperties: false`,
  `required: ["xong"]`; `_cli_run` ghi `schema.json` bằng hàm này. Lớp test mới `KhuonSchemaTest` (Q5) —
  Test: `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py" -k KhuonSchemaTest`
  - Chạm: `scripts/tdq_codex.py`, `tests/test_codex_run.py` → `_cli_run`
- [x] **T1.4** (e10m) `dong_log_luot(..., ly_do=None)` thêm `· ly_do=<mã>` sau `dau="…"` khi trạng
  thái ≠ `xong`; `_cli_run` dùng `phan_quyet_ly_do` và truyền lý do vào dòng log. Thêm test vào
  `LogTest` (Q6): có/không `ly_do`, 7 mảnh cũ còn đủ, < 300 ký tự — Test: `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py" -k LogTest`
  - Chạm: `scripts/tdq_codex.py`, `tests/test_codex_run.py` → `dong_log_luot`, `_cli_run`
  - Cần: T1.2

**Xong P1 khi**: `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py"` xanh toàn bộ.

## P2 — Tương thích bench

- [x] **T2.1** (e5m) Thêm test vào `LogCodexTest`: dòng do chính `tdq_codex.dong_log_luot` sinh ra —
  lượt `xong` được đếm đúng mã task + giây, lượt `fail` có `ly_do` bị bỏ (Q7). Không sửa `scripts/tdq_bench.py` —
  Test: `env -u TDQ_LOG python3 -m unittest discover tests -p "test_bench.py" -k LogCodexTest`
  - Chạm: `tests/test_bench.py` → `doc_log_codex` (chỉ đọc)
  - Cần: T1.4

## P3 — Luật & bundle

- [x] **T3.1** (e8m) `skills/tdq-build/references/codex-mode.md`: khuôn prompt cố định thêm câu
  "chỉ trả object JSON trần, không bọc trong rào code"; đoạn "The result shape Codex must return"
  mô tả bằng lời: nhận đúng một rào bao trọn file, chỉ `xong` = `true` là xong, lượt không xong
  ghi mã lý do (nhắc tên hằng, không chép code) (Q8) —
  Test: `python3 scripts/i18n_check.py skills/tdq-build/references/codex-mode.md` và `python3 scripts/doc_lint.py skills/tdq-build/references/codex-mode.md` không lỗi mới; `grep -c "rào code\|code fence" skills/tdq-build/references/codex-mode.md` ≥ 2
  - Cần: T1.4
- [x] **T3.2** (e6m) Sinh lại bundle bằng `python3 scripts/build_portable.py` (Q9) —
  Test: `env -u TDQ_LOG python3 -m unittest discover tests -p "test_build_portable.py"` xanh; `cmp` bản `tdq_codex.py` và `codex-mode.md` trong `portable_claude/`, `portable_codex/` với nguồn không khác
  - Chạm: `antigravity_portable/`, `portable_claude/`, `portable_codex/`, `portable_codex.zip`, `portable_src/`
  - Cần: T1.4, T3.1

## P4 — Log & test bắt buộc, lượt thật

- [x] **T4.1** (e6m) Log service: dòng log lượt trong `_cli_run` hiện `print` thẳng ra stderr, không
  tắt được — cho nó đi qua `_log_enabled()` để `TDQ_LOG=0` tắt được như spec §4, mặc định vẫn bật.
  Test `LogTest`: mặc định in dòng có timestamp + `ly_do`; `TDQ_LOG=0` không in —
  Test: `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py" -k LogTest`
  - Chạm: `scripts/tdq_codex.py`, `tests/test_codex_run.py` → `_cli_run`
  - Cần: T1.4
- [x] **T4.2** (e15m) Lượt thật với `ag/gemini-3.8-flash-medium` ở gốc repo, ghi bằng chứng vào
  `docs/tdq/qc/2026-09-14-1252-run-cham-fail-sai-schema.md`:
  Q10 — task tạo `docs/tdq/qc/q10-probe.txt` chứa `Q10-OK`, `--vung` đúng file đó → `trang_thai` = `xong`, exit 0;
  Q11 — task không thể làm ("làm cho lệnh `false` exit 0, không được sửa file nào", `--vung` rỗng) →
  `trang_thai` ≠ `xong`, dòng log có `ly_do` thuộc `MA_LY_DO`. Q10 không đạt → chạy lại tối đa 3 lượt,
  vẫn không đạt thì ghi nguyên văn `ket-qua.json` và báo user. Xoá file thăm dò, chạy `tdq_codex.py cleanup` sau cùng —
  Test: JSON in ra của từng lượt + `grep -c -e Bearer -e sk-` trên đầu ra = 0
  - Cần: T1.4, T4.1
- [x] **T4.3** (e8m) Hồi quy (Q12): test `tdq_codex` (run + CLI) và `tdq_bench` xanh; bộ đầy đủ không
  thêm fail/error so với mốc 290 fail / 4 error; `graphify extract . --code-only` —
  Test: `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_*.py"`, `-p "test_bench.py"`, `env -u TDQ_LOG python3 -m unittest discover tests 2>&1 | tail -3`
  - Cần: T2.1, T3.2, T4.1
  - Dùng: `graphify`
  - Ghi nhận khi chạy: bộ đầy đủ ra 293 fail / 4 error so với mốc 290/4 (mốc đo lại trên worktree HEAD sạch
    cùng lúc: 290/4). 3 fail thêm là `test_codex_edit_gate.TestChanNgoaiVung` (3 test "trong vùng thì không chặn"):
    test gọi hook thật với `cwd` = repo này, `edit_gate.py` đếm lượt sửa vào sổ lượt THẬT theo checksum plan và
    chặn `[TDQ:TICK]` từ lượt thứ 3 khi repo đang ở phase implement. Hook và file test không đổi so với HEAD;
    ngoài phạm vi request này, nêu trong report như nợ kỹ thuật.
  - Để: làm mới đồ thị code sau khi sửa `scripts/tdq_codex.py`, chạy SAU khi test xanh.
  - Ra: đồ thị trong `graphify-out/` cập nhật theo code mới
  - Kiểm: `graphify extract . --code-only` exit 0
  - Không dùng cho: tìm ký hiệu hay tham chiếu — việc đó dùng LSP

## Cụm song song

Một cụm: 6/8 task chạm `scripts/tdq_codex.py` hoặc phụ thuộc dòng log mà T1.4 định khuôn; T2.1 và
T3.1 tách được về file nhưng đều `Cần: T1.4`, còn T4.2 là lượt thật tuần tự.

## Definition of Done

Trỏ về §6 của spec.

- [x] Q1 5 dạng được nhận ra dict — `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py" -k DocKetQuaRaoTest`
- [x] Q2 9 dạng bị từ chối ra `None` — `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py" -k DocKetQuaRaoTest`
- [x] Q3 chỉ `xong` = `true` ra `xong` — `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py" -k PhanQuyetLyDoTest`
- [x] Q4 mã lý do đúng tập đóng, 6 test cũ `PhanQuyetTest` xanh không sửa — `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py" -k PhanQuyet`
- [x] Q5 schema có `additionalProperties: false` — `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py" -k KhuonSchemaTest`
- [x] Q6 dòng log mang `ly_do` đúng ca, tắt được bằng `TDQ_LOG=0` — `env -u TDQ_LOG python3 -m unittest discover tests -p "test_codex_run.py" -k LogTest`
- [x] Q7 bench đọc đúng dòng log mới — `env -u TDQ_LOG python3 -m unittest discover tests -p "test_bench.py" -k LogCodexTest`
- [x] Q8 luật `codex-mode.md` cập nhật, không lỗi i18n/lint mới — `python3 scripts/i18n_check.py skills/tdq-build/references/codex-mode.md`
- [x] Q9 bundle khớp nguồn — `env -u TDQ_LOG python3 -m unittest discover tests -p "test_build_portable.py"`
- [x] Q10 lượt thật làm được ra `xong` — `python3 scripts/tdq_codex.py run Q10 --prompt "<khuôn>" --vung docs/tdq/qc/q10-probe.txt`
- [x] Q11 lượt thật không làm được ra ≠ `xong` kèm `ly_do` — `python3 scripts/tdq_codex.py run Q11 --prompt "<khuôn>"`
- [x] Q12 không hồi quy — `env -u TDQ_LOG python3 -m unittest discover tests 2>&1 | tail -3`
