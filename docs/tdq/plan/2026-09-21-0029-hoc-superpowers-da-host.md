# PLAN — Học cách tổ chức của superpowers: một nguồn, adapter mỏng, chạy đa nền tảng

Ngày: 2026-09-21 · Spec: ../spec/2026-09-21-0029-hoc-superpowers-da-host.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — máy đo trên chính plan này cho main thắng 3.2 phút; 12 task nhưng chuỗi phụ thuộc tuyến tính nên máy phải chia tới 9 đợt, leader chỉ giữ 3 task và phần chờ đợt nuốt hết phần song song (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Adapter cho từng host
- P2 — Gỡ mô hình chép
- P3 — Test không cần công cụ ngoài
- P4 — CI ba hệ
- P5 — Tài liệu và phát hành
- P6 — Log & test bắt buộc
- Cụm song song
- Luật file nóng
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit hay push cho đến khi user yêu cầu.
7. Test của repo import `helper`, thứ chỉ nằm trên `sys.path` khi chạy qua `discover`. Dạng lệnh
   đúng là `-m unittest discover tests -p test_<ten>.py`.
8. Xoá thư mục bundle là thao tác khó lùi. Chỉ xoá SAU khi adapter thay thế đã xanh, và chỉ bằng
   `git rm -r`, không bao giờ bằng `rm -rf` trần — để lịch sử giữ được bản cũ.

## P1 — Adapter cho từng host

- [x] **T1.1** (e12m) Viết `.agents/plugins/marketplace.json` và `.codex-plugin/plugin.json`, trỏ `"url": "./"` và `"skills": "./skills/"` — Test: `python3 -m unittest discover tests -p test_adapter_host.py -k codex` xanh, và `codex plugin list` in ra `tdq-workflow`
  - Chạm: `.agents/plugins/marketplace.json`, `.codex-plugin/plugin.json`, `tests/test_adapter_host.py`
- [x] **T1.2** (e30m) Viết `.opencode/plugins/tdq-workflow.js`: JavaScript thuần, đọc `skills/*/SKILL.md`, trả khuôn context của OpenCode, không import package ngoài — Test: `python3 -m unittest discover tests -p test_adapter_host.py -k opencode` xanh, chạy thật bằng `node`
  - Chạm: `.opencode/plugins/tdq-workflow.js`, `.opencode/INSTALL.md`, `tests/test_adapter_host.py`
  - Cần: T1.1

**Xong P1 khi**: cả hai adapter nạp được, và không adapter nào phụ thuộc file trong ba bundle.

## P2 — Gỡ mô hình chép

- [x] **T2.1** (e25m) Viết lệnh sinh layout agy theo yêu cầu vào `~/.gemini/config/plugins/tdq-workflow/`, bất biến, từ chối ghi đè thứ không phải của mình — Test: `python3 -m unittest discover tests -p test_sinh_agy.py` xanh
  - Chạm: `scripts/build_portable.py`, `tests/test_sinh_agy.py`
  - Cần: T1.2
- [x] **T2.2** (e8m) `git rm -r` ba thư mục bundle — Test: `python3 -m unittest discover tests -p test_adapter_host.py -k khong_con_bundle` xanh, `git ls-files` không còn đường dẫn nào thuộc ba thư mục
  - Chạm: `portable_claude/`, `portable_codex/`, `antigravity_portable/`
  - Cần: T2.1
- [x] **T2.3** (e25m) Thu gọn `scripts/build_portable.py`: giữ `tien_to_python`, `sinh_hook_claude` và lệnh sinh agy, cắt toàn bộ phần dựng bundle — Test: `python3 -m unittest discover tests -p test_sua_da_nen_tang.py` xanh (17 ca cũ), và không hàm nào còn lại mà không có nơi gọi
  - Chạm: `scripts/build_portable.py`, `tests/test_build_portable.py`
  - Cần: T2.2
  - Dùng: `tdq-lean`
  - Để: soi phần nào của 1077 dòng còn lý do tồn tại, nạp skill TRƯỚC bước đỏ. Agent ngoài không
    có skill system: đọc `skills/tdq-lean/SKILL.md` rồi làm theo.
  - Ra: một đoạn nhận xét trong `docs/tdq/qc/2026-09-21-0029-hoc-superpowers-da-host.md`
  - Kiểm: `python3 scripts/doc_lint.py docs/tdq/qc/2026-09-21-0029-hoc-superpowers-da-host.md` thoát 0
  - Không dùng cho: nội dung adapter ở P1, phần đó do API của host quyết định
- [x] **T2.4** (e15m) `scripts/tdq_checkportable.py` bỏ phần đòi `manifest.json` của bundle, giữ `setup --shim` và phần kiểm môi trường — Test: `python3 -m unittest discover tests -p test_checkportable.py` xanh và `test_shim_python3.py` xanh
  - Chạm: `scripts/tdq_checkportable.py`, `tests/test_checkportable.py`
  - Cần: T2.3
- [x] **T2.5** (e10m) Vá phần T2.3 bỏ sót — thêm lúc thi hành (quy tắc 5): chạy `build_portable.py` không cờ vẫn dựng `antigravity_portable/` NGAY TRONG repo, và `--only` được nhận rồi lờ đi — Test: `python3 -m unittest discover tests -p test_build_portable.py -k TestCLI` xanh (không cờ thoát 2, `--dest` trỏ vào repo bị từ chối)
  - Chạm: `scripts/build_portable.py`, `tests/test_build_portable.py`
  - Cần: T2.4

**Xong P2 khi**: repo không còn file nhân bản nào, và mọi lệnh còn lại đều có nơi gọi.

## P3 — Test không cần công cụ ngoài

- [x] **T3.1** (e20m) Đổi các ca phụ thuộc `pytest`, `anthropic-tokenizer`, `graphify`, `codex` sang `skipUnless` — Test: chạy suite với PATH không có bốn công cụ, được 0 fail 0 error
  - Chạm: `tests/test_codex_cli.py`, `tests/test_codex_run.py`, `tests/test_doc_dup.py`, `tests/test_check_canvas_layout.py`, `tests/test_team_chong_conflict.py`, `tests/helper.py`
  - Cần: T2.4
- [x] **T3.2** (e20m) Mọi lời gọi `subprocess` ở chế độ văn bản khai `encoding="utf-8"` — thêm lúc thi hành (quy tắc 5): chạy suite không có `PYTHONUTF8=1` thì 273 ca lỗi vì bên đọc giải mã bằng cp1252, cả ở `scripts/` (vd `tdq_finish.py` đọc đầu ra `doc_lint`) — Test: `python3 -m unittest discover tests -p test_ma_hoa_subprocess.py` xanh, và suite xanh khi KHÔNG đặt `PYTHONUTF8`
  - Chạm: `scripts/*.py`, `tests/*.py`, `tests/test_ma_hoa_subprocess.py`
  - Cần: T3.1

**Xong P3 khi**: một máy chưa cài công cụ nào vẫn chạy suite xanh, và số `skip` nói rõ phần chưa phủ.

## P4 — CI ba hệ

- [x] **T4.1** (e20m) Viết `.github/workflows/test.yml`: matrix 3 hệ điều hành × Python 3.10 và 3.13, chạy trọn suite, không cài công cụ ngoài — Test: `python3 -m unittest discover tests -p test_ci_matrix.py` xanh (kiểm khuôn YAML và đủ 6 tổ hợp)
  - Chạm: `.github/workflows/test.yml`, `tests/test_ci_matrix.py`
  - Cần: T3.1

**Xong P4 khi**: file workflow khai đủ 6 tổ hợp và chạy đúng lệnh suite của repo.

## P5 — Tài liệu và phát hành

- [x] **T5.1** (e18m) Viết lại phần cài đặt của `README.md` theo bốn host, và cập nhật `docs/kien-truc.md`: bỏ tầng "luật bản ngoài", thêm ngoại lệ đường dẫn adapter vào `## Đã chốt` — Test: `python3 -m unittest discover tests -p test_docs_consistency.py` xanh, `doc_lint.py README.md` thoát 0
  - Chạm: `README.md`, `docs/kien-truc.md`, `tests/test_docs_consistency.py`
  - Cần: T4.1
- [x] **T5.2** (e10m) Bump version, ghi mục CHANGELOG — Test: `python3 scripts/doc_lint.py CHANGELOG.md` thoát 0 và file dưới 500 dòng
  - Chạm: `.claude-plugin/plugin.json`, `CHANGELOG.md`
  - Cần: T5.1

**Xong P5 khi**: không dòng tài liệu nào còn mô tả ba bundle như cách cài hiện hành.

## P6 — Log & test bắt buộc

- [x] **T6.1** (e8m) Lệnh sinh agy và adapter OpenCode đều có log service bật mặc định, tắt được qua config — Test: `python3 -m unittest discover tests -p test_sinh_agy.py -k log` xanh
  - Chạm: `scripts/build_portable.py`, `.opencode/plugins/tdq-workflow.js`, `tests/test_sinh_agy.py`
  - Cần: T5.2
- [x] **T6.2** (e10m) Mỗi thành phần mới có unit test riêng, chạy bằng một lệnh — Test: `python3 -m unittest discover tests` xanh
  - Chạm: `tests/`
  - Cần: T6.1

## QC vòng 1 — fix

- [x] **QC1.1** Q6 FAIL: `build_portable.py` 1077 → 743 dòng (giảm 31%, chưa tới một nửa), và lượt đo ở T2.3 chỉ đo HÀM — 9 hằng không còn nơi dùng (61 dòng: `AGENTS_MD`, `HOOK_CODEX`, `SOURCE_DIRS`, `FILE_HOOK_AGY`, …) cùng tham số `bo_qua_them` của `copy_loc` vẫn nằm lại. Cắt phần chết, khoá bằng một test đo khả năng với tới từ `main` cho cả hàm lẫn hằng — Test: `python3 -m unittest discover tests -p test_build_portable.py -k khong_con_ten_chet` xanh
  - Chạm: `scripts/build_portable.py`, `tests/test_build_portable.py`

## Cụm song song

Mục này bắt buộc có trong mọi plan. Kết luận ở đây: **hai cụm, nhưng cụm thứ hai chỉ có một task**.

Chuỗi phụ thuộc gần như tuyến tính vì mọi thứ sau P2 đều đứng sau việc xoá bundle: `test_docs_consistency`
đọc cây thư mục, `tdq_checkportable` mất nguồn kiểm, CI chạy suite đã đổi. Cặp duy nhất tách rời
thật sự là **T1.1 với T1.2**: một cái là JSON manifest cho Codex, một cái là JavaScript cho
OpenCode, không chung file nào. Hai task đó chạy song song được; phần còn lại thì không.

Cặp `T5.1` và `T5.2` chạm hai tập file rời nhau, nhưng T5.2 phải đọc bản README đã viết lại để
ghi CHANGELOG cho khớp, nên giữ tuần tự.

## Luật file nóng

Hai đường dẫn bị từ 2 task trở lên khai ở `Chạm:`:

| Đường dẫn | Task | Cách xử lý |
|---|---|---|
| `scripts/build_portable.py` | T2.1, T2.3, T6.1 | một chủ ghi duy nhất — T2.3 là chủ, T2.1 chỉ thêm lệnh mới và T6.1 chỉ thêm log vào lệnh đó |
| `tests/test_adapter_host.py` | T1.1, T1.2, T2.2 | nâng lên đợt sớm — T1.1 tạo file, hai task sau thêm lớp test vào bản đã ổn định |

## Definition of Done

- [x] Q1 Adapter Codex nạp được — `codex plugin marketplace add . && codex plugin list`
- [x] Q2 Adapter OpenCode chạy được — `python3 -m unittest discover tests -p test_adapter_host.py -k opencode`
- [x] Q3 Adapter OpenCode không kéo phụ thuộc — `python3 -m unittest discover tests -p test_adapter_host.py -k phu_thuoc`
- [x] Q4 Lệnh sinh layout agy bất biến — `python3 -m unittest discover tests -p test_sinh_agy.py`
- [x] Q5 Ba bundle biến khỏi repo — `git ls-files | grep -c portable_ || true`
- [x] Q6 `build_portable.py` không còn tên chết — `python3 -m unittest discover tests -p test_build_portable.py -k khong_con_ten_chet`
- [x] Q7 `tdq_checkportable.py` hết đòi manifest — `python3 scripts/tdq_checkportable.py check`
- [x] Q8 CI khai đủ 6 tổ hợp — `python3 -m unittest discover tests -p test_ci_matrix.py`
- [x] Q9 Suite xanh trên máy chưa cài công cụ ngoài — `python3 -m unittest discover tests` với PATH đã lược bốn công cụ
- [x] Q10 Không ca nào từ xanh chuyển sang đỏ — `python3 -m unittest discover tests` đối chiếu mốc 1983 ca
- [x] Q11 Tài liệu khớp kiến trúc — `python3 -m unittest discover tests -p test_docs_consistency.py`
- [x] Q12 Version tăng và CHANGELOG dưới trần — `python3 scripts/doc_lint.py CHANGELOG.md`
- [x] Q13 Lint tài liệu request — `python3 scripts/doc_lint.py docs/tdq/brief docs/tdq/spec docs/tdq/plan docs/tdq/qc`
