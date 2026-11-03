# PLAN — Sửa bộ workflow TDQ chạy đủ tính năng trên Windows

Ngày: 2026-09-20 · Spec: ../spec/2026-09-20-1823-sua-tdq-chay-windows.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — user chốt lúc duyệt. Máy đo đề xuất subagent (đội 24.5 phút so với main 44.8, cách 20.3 phút), user chọn làm trực tiếp; mode luôn là quyết định của user.
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Ép UTF-8 cho mọi entry point
- P2 — Tên lệnh interpreter theo hệ điều hành
- P3 — Harness test và biên xuất đường dẫn
- P4 — Layout `synced/` mới của Claude Code
- P5 — Lớp tìm kiếm
- P6 — Vệ sinh repo và ba drift
- P7 — Công cụ ngoài và lượt chạy test đầy đủ
- P8 — Bundle portable và phát hành
- P9 — Log & test bắt buộc
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
7. Mọi dòng `Test:` viết bằng tên lệnh `python3` theo quy ước repo. Máy Windows đang chạy
   request này không có tên lệnh đó, nên người thi hành thay bằng `python` khi gõ thật —
   đây chính là lỗi P2 đang sửa, và sau P2 thì dòng lệnh trong tầng luật hết phụ thuộc hệ.
8. Test của repo import `helper`, thứ chỉ nằm trên `sys.path` khi chạy qua `discover`. Nên
   dạng lệnh đúng là `-m unittest discover tests -p test_<ten>.py`, không phải
   `-m unittest tests.test_<ten>`. Phát hiện lúc chạy T1.1.

## P1 — Ép UTF-8 cho mọi entry point

- [x] **T1.1** (e10m) Viết `scripts/utf8_io.py`: ép `sys.stdout` và `sys.stderr` sang UTF-8 với
      `errors="replace"`, idempotent, im lặng khi luồng không có `reconfigure` — Test: `python3 -m unittest discover tests -p test_utf8_io.py -k ForceUtf8Test -k LogTest` xanh
  - Chạm: `scripts/utf8_io.py`, `tests/test_utf8_io.py` → file mới, chưa node nào phụ thuộc
- [x] **T1.2** (e15m) Nạp `utf8_io` vào hai chỗ dùng chung `scripts/tdq_state.py` và
      `hooks/scripts/_common.py`, phủ 18 trong 40 entry point — Test: `python3 -m unittest discover tests -p test_utf8_io.py -k chokepoint` xanh
  - Chạm: `scripts/tdq_state.py`, `hooks/scripts/_common.py`, `tests/test_utf8_io.py`
  - Cần: T1.1
- [x] **T1.3** (e12m) Thêm một dòng import `utf8_io` vào 22 entry point còn lại — Test: `python3 -m unittest discover tests -p test_utf8_io.py -k entrypoint` xanh, mọi file có `__main__` đều nạp
  - Chạm: `scripts/canvas_a4_rebuild.py`, `scripts/canvas_layout_apply.py`, `scripts/canvas_move_block.py`, `scripts/check_canvas_layout.py`, `scripts/claude_export.py`, `scripts/doc_lint.py`, `scripts/i18n_check.py`, `scripts/kiem_no_marker.py`, `scripts/luat_phan_loai.py`, `scripts/plugin_tiers.py`, `scripts/scan_block_symbols.py`, `scripts/step_audit.py`, `scripts/tdq_checkportable.py`, `scripts/tdq_codex.py`, `scripts/tdq_eval.py`, `scripts/tdq_finish.py`, `scripts/tdq_lsp.py`, `scripts/tdq_vungfile.py`, `scripts/token_audit.py`, `hooks/scripts/agy_pretooluse_gate.py`, `hooks/scripts/agy_stop_gate.py`, `tests/test_utf8_io.py`
  - Cần: T1.1

**Xong P1 khi**: chạy từng file trong 40 entry point dưới code page cp1252 không file nào ném `UnicodeEncodeError`.

## P2 — Tên lệnh interpreter theo hệ điều hành

- [x] **T2.1** (e10m) Sinh lại `hooks/hooks.json` theo hệ, kiểm tính bất biến khi chạy hai lần — Test: `python3 -m unittest discover tests -p test_sua_da_nen_tang.py` xanh (17 ca đã có sẵn, phủ `tien_to_python` và tính bất biến của `sinh_hook_claude`)
  - Chạm: `hooks/hooks.json`, `scripts/build_portable.py`, `tests/test_build_portable.py`
  - Cần: T1.2
- [x] **T2.2** (e18m) Viết `ten_lenh_python(nen_tang)` trong `scripts/tdq_ten_lenh.py`, và
      `session_start.py` in một dòng quy ước CHỈ khi máy là Windows và chưa có shim — Test: `python3 -m unittest discover tests -p test_ten_lenh_he.py` xanh cho cả hai hệ
  - Chạm: `scripts/tdq_ten_lenh.py`, `hooks/scripts/session_start.py`, `tests/test_ten_lenh_he.py`
  - Cần: T1.2
- [x] **T2.3** (e20m) Thêm `tdq_checkportable.py setup --shim` cài hai file shim `python3` vào thư
      mục đứng đầu PATH, bất biến, từ chối chạy ngoài Windows; cài lên máy này — Test: `python3 -m unittest discover tests -p test_shim_python3.py` xanh, và gõ nguyên văn `python3 scripts/tdq_state.py get phase` chạy được ở Git Bash, cmd.exe, PowerShell
  - Chạm: `scripts/tdq_checkportable.py`, `tests/test_shim_python3.py`
  - Cần: T2.2
  - Dùng: `tdq-lean`
  - Để: soi xem cơ chế placeholder có làm quá tay không, chạy TRƯỚC bước đỏ của task. Agent
    ngoài không có skill system: đọc `skills/tdq-lean/SKILL.md` rồi làm theo.
  - Ra: một đoạn nhận xét trong `docs/tdq/qc/2026-09-20-1823-sua-tdq-chay-windows.md`
  - Kiểm: `python3 scripts/doc_lint.py docs/tdq/qc/2026-09-20-1823-sua-tdq-chay-windows.md` thoát 0
  - Không dùng cho: nội dung luật tìm kiếm ở P5, phần đó do số đo quyết định
- [x] **T2.4** (e10m) Kiểm sáu hook sống thật: nạp JSON qua stdin cho từng hook, đòi thoát 0 và in
      đúng khối `[TDQ:*]` — Test: `python3 -m unittest discover tests -p test_hook_windows.py` xanh
  - Chạm: `tests/test_hook_windows.py`
  - Cần: T2.1, T2.2

**Xong P2 khi**: gõ nguyên văn một lệnh `python3` của tầng luật chạy được ở cả ba shell, và sáu hook đều thoát 0.

## P3 — Harness test và biên xuất đường dẫn

- [x] **T3.1** (e12m) Set `USERPROFILE` cạnh `HOME` ở 6 file test — Test: `python3 -m unittest tests.test_skill_inventory -v` xanh, test không chạm thư mục nhà thật
  - Chạm: `tests/test_build_portable.py`, `tests/test_checkportable.py`, `tests/test_codex_cli.py`, `tests/test_codex_run.py`, `tests/test_plugin_tiers.py`, `tests/test_skill_inventory.py`
  - Cần: T1.3
- [x] **T3.2** (e15m) Chuẩn hoá dấu chéo xuôi ở biên xuất của `kiem_no_marker`, `context_surface`
      và sổ turn — Test: `python3 -m unittest tests.test_kiem_no_marker tests.test_context_surface tests.test_compliance_protocol -v` xanh
  - Chạm: `scripts/kiem_no_marker.py`, `scripts/context_surface.py`, `hooks/scripts/edit_gate.py`, `tests/test_kiem_no_marker.py`, `tests/test_context_surface.py`, `tests/test_compliance_protocol.py`
  - Cần: T1.3

**Xong P3 khi**: mọi đường dẫn in ra và ghi vào sổ turn chỉ chứa dấu chéo xuôi.

## P4 — Layout `synced/` mới của Claude Code

- [x] **T4.1** (e20m) `scripts/skill_inventory.py` quét được cả layout cũ và layout
      `~/.claude/skills/synced/<uuid>/<tên>/SKILL.md` — Test: `python3 -m unittest tests.test_skill_inventory -v -k synced` xanh cho cả hai layout
  - Chạm: `scripts/skill_inventory.py`, `tests/test_skill_inventory.py`
  - Cần: T3.1
- [x] **T4.2** (e10m) `scripts/tdq_lsp.py` đọc được `~/.claude/plugins/synced/` khi không còn
      `installed_plugins.json` — Test: `python3 -m unittest tests.test_tdq_lsp -v -k plugin` xanh
  - Chạm: `scripts/tdq_lsp.py`, `tests/test_tdq_lsp.py`
  - Cần: T3.1

**Xong P4 khi**: bảng kiểm kê năng lực liệt kê được skill trên đĩa ở cả hai layout.

## P5 — Lớp tìm kiếm

- [x] **T5.1** (e8m) Thêm `.lumenignore` loại ba bundle portable — Test: `python3 -m unittest tests.test_lumenignore -v` xanh, và kết quả tìm kiếm không còn đường dẫn thuộc ba bundle
  - Chạm: `.lumenignore`, `tests/test_lumenignore.py`
- [x] **T5.2** (e15m) Thêm luật cấm mở file trước khi hỏi `find_references` vào
      `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`, viết đủ ba mục — Test: `python3 -m unittest discover tests -p test_tdq_lsp_skill.py` xanh
  - Chạm: `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`, `tests/test_rules_library.py`
  - Cần: T2.3
  - Dùng: `tdq-lsp-setup`
  - Để: giữ luật mới khớp khuôn ba mục và không đụng thứ hạng các lớp trong bảng, nạp skill
    TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc `skills/tdq-lsp-setup/SKILL.md` rồi làm theo.
  - Ra: mục luật mới trong `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md`
  - Kiểm: `python3 -m unittest tests.test_rules_library -v -k find_references` xanh
  - Không dùng cho: đổi thứ hạng các lớp, việc đó nằm ngoài phạm vi theo spec §1

**Xong P5 khi**: luật mới có đủ ba mục và kết quả lumen sạch bản sao portable.

## P6 — Vệ sinh repo và ba drift

- [x] **T6.1** (e12m) `docs/tdq/audit/skill-index.json` hết mang đường dẫn tuyệt đối: chuyển sang
      đường dẫn tương đối và bỏ qua trong git — Test: `python3 -m unittest tests.test_skill_router -v` xanh trên máy bất kỳ
  - Chạm: `scripts/skill_router.py`, `.gitignore`, `docs/tdq/audit/skill-index.json`, `tests/test_skill_router.py`
  - Cần: T4.1
- [x] **T6.2** (e10m) Đưa `docs/claude-md-mau.md` về dưới trần 3500 byte và bỏ `bash.md` thừa
      khỏi `index.md` — Test: `python3 -m unittest tests.test_claude_md_core tests.test_rules_library -v` xanh
  - Chạm: `docs/claude-md-mau.md`, `skills/tdq-build/references/rules/index.md`, `tests/test_claude_md_core.py`, `tests/test_rules_library.py`
- [x] **T6.3** (e8m) Chốt `setup_status` trả model nào là đúng rồi sửa bên lệch — Test: `python3 -m unittest tests.test_setup_status -v` xanh
  - Chạm: `scripts/setup_status.py`, `tests/test_setup_status.py`
  - Cần: T1.3

**Xong P6 khi**: không bản ghi nào trong kho skill-index mang đường dẫn của một máy, và ba drift hết đỏ.

## P7 — Công cụ ngoài và lượt chạy test đầy đủ

- [x] **T7.1** (e20m) Xin phép user từng lệnh rồi cài `pytest`, `anthropic-tokenizer`,
      `graphify`, `codex` — Test: bốn công cụ đều trả lời `--version`
- [x] **T7.2** (e25m) Chạy full suite trên Windows, vá mọi ca còn đỏ — Test: `python3 -m unittest discover tests` báo 0 fail, 0 error
  - Chạm: `tests/`
  - Cần: T6.1, T6.2, T6.3, T7.1

**Xong P7 khi**: một lượt chạy đầy đủ trên Windows cho 0 fail và 0 error.

## P8 — Bundle portable và phát hành

- [x] **T8.1** (e15m) Dựng lại ba bundle portable — Test: `python3 scripts/tdq_checkportable.py check` báo sạch cho cả ba
  - Chạm: `portable_claude/`, `portable_codex/`, `antigravity_portable/`
  - Cần: T7.2
  - **HOÃN CÓ CHỦ Ý — user phán quyết `2a` ngày 2026-09-21: coi đây là bước phát hành.** Lệnh chạy đúng và cả ba bundle báo CLEAN, nhưng bản dựng từ
    máy Windows KHÔNG được commit: bundle agy nướng cứng thư mục nhà của máy dựng, nên nó ra
    `py -3 C:\Users\admin/.gemini/...` thay vì `python3 /Users/tdq/.gemini/...`. Đẩy bản đó lên
    repo là làm hỏng bundle của mọi người dùng macOS và Linux. Đã trả ba thư mục về bản commit.
    Đây là bước phát hành, phải chạy trên máy macOS hoặc Linux: `python3 scripts/build_portable.py`.
- [x] **T8.2** (e10m) Bump version, ghi CHANGELOG, xoá `portable_codex.zip` lỗi thời — Test: `python3 scripts/doc_lint.py CHANGELOG.md` thoát 0 và file dưới 500 dòng
  - Chạm: `.claude-plugin/plugin.json`, `CHANGELOG.md`, `portable_codex.zip`
  - Cần: T8.1

**Xong P8 khi**: ba bundle sạch, version tăng, CHANGELOG có mục mới.

## P9 — Log & test bắt buộc

- [x] **T9.1** (e8m) `scripts/utf8_io.py` có log service bật mặc định, tắt được bằng `TDQ_LOG=0` — Test: `python3 -m unittest tests.test_utf8_io -v -k log` xanh
  - Chạm: `scripts/utf8_io.py`, `tests/test_utf8_io.py`
  - Cần: T1.1
- [x] **T9.2** (e10m) Mỗi thành phần mới có unit test riêng chạy bằng một lệnh — Test: `python3 -m unittest discover tests` xanh
  - Chạm: `tests/`
  - Cần: T7.2

## Cụm song song

Kết luận: **5 đợt, 10 trong 22 task giao được**, theo `tdq_bench.py simulate` chạy trên chính
file này với hệ số agent 1.5.

Bản nháp đầu của mục này viết "một cụm", lập luận rằng P1 chạm gần hết `scripts/` nên mọi đợt
song song đều đụng file nóng. Đó là áng chừng bằng mắt và nó SAI. Hai điều sửa nó:

- `Chạm:` của T1.3 lúc đầu khai cả thư mục `scripts/` thay vì 21 file thật. Khai thô làm máy
  chia đợt hiểu sai vùng va chạm. Sau khi liệt kê đúng từng file, kết quả vẫn là đội thắng —
  20.3 phút thay vì 22.3, tức lập luận "file nóng" không đủ sức lật.
- Mọi task từ P3 trở đi đều khai `Cần: T1.3` hoặc hậu duệ của nó, nên chúng nằm ở đợt SAU khi
  P1 đã đóng băng. Lúc đó `scripts/skill_inventory.py` của T4.1 và `scripts/tdq_lsp.py` của
  T4.2 là hai file rời nhau thật sự.

Các cặp chạy song song được sau khi P1 đóng băng: T4.1 với T4.2 · T5.1 với T5.2 · T6.2 với T6.3.
Phần leader phải tự giữ là P1 trọn vẹn, T2.3 (chạm cả tầng `skills/`), T7.2 và T9.2 (cùng chạm
`tests/`).

## Luật file nóng

Ba đường dẫn bị từ 2 task trở lên khai ở `Chạm:`:

| Đường dẫn | Task | Cách xử lý |
|---|---|---|
| `hooks/scripts/_common.py` | T1.2, T2.2 | nâng lên đợt sớm — T1.2 ở P1 làm xong và đóng băng trước khi T2.2 chạm |
| `tests/` | T7.2, T9.2 | một chủ ghi duy nhất — T7.2 là chủ, T9.2 chỉ chạy lại lệnh kiểm |
| `skills/` | T5.2 | hết nóng từ bản spec 1.1 — T2.3 không còn chạm `skills/` nữa |

## Definition of Done

- [x] Q1 Module ép UTF-8 idempotent và không ném lỗi khi luồng đã UTF-8 — `python3 -m unittest tests.test_utf8_io -v`
- [x] Q2 Không entry point nào ném `UnicodeEncodeError` dưới cp1252 — `python3 -m unittest tests.test_utf8_io -v -k entrypoint`
- [x] Q3 Sáu hook thoát 0 và in đúng khối `[TDQ:*]` — `python3 -m unittest tests.test_hook_windows -v`
- [x] Q4 Sinh lại `hooks.json` hai lần không đổi nội dung — `python3 -m unittest tests.test_build_portable -v -k sinh_hook`
- [x] Q5 Shim làm lệnh `python3` nguyên văn chạy được ở cả ba shell — `python3 -m unittest discover tests -p test_shim_python3.py`
- [x] Q6 Lưới an toàn chỉ in trên Windows chưa có shim — `python3 -m unittest discover tests -p test_ten_lenh_he.py`
- [x] Q7 Harness test đọc thư mục nhà giả — `python3 -m unittest tests.test_skill_inventory -v`
- [x] Q8 Biên xuất chỉ dùng dấu chéo xuôi — `python3 -m unittest tests.test_kiem_no_marker tests.test_context_surface -v`
- [x] Q9 Kho skill-index không mang đường dẫn của một máy — `python3 -m unittest tests.test_skill_router -v`
- [x] Q10 Kiểm kê năng lực đọc được cả hai layout — `python3 -m unittest tests.test_skill_inventory -v -k synced`
- [x] Q11 Full suite trên Windows 0 fail 0 error — `python3 -m unittest discover tests`
- [x] Q12 Không ca nào từ xanh chuyển sang đỏ — `python3 -m unittest discover tests` đối chiếu với mốc đầu request
- [x] Q13 Ba bundle portable sạch — `python3 scripts/tdq_checkportable.py check`
- [x] Q14 Luật `find_references` có đủ ba mục — `python3 -m unittest discover tests -p test_tdq_lsp_skill.py`
- [x] Q15 Kết quả lumen sạch bản sao portable — `python3 -m unittest discover tests -p test_lumenignore.py`
- [x] Q16 Version tăng và CHANGELOG dưới trần — `python3 scripts/doc_lint.py CHANGELOG.md`
- [x] Q17 Mọi tài liệu của request lint sạch — `python3 scripts/doc_lint.py docs/tdq/brief docs/tdq/spec docs/tdq/plan docs/tdq/qc`

## QC vòng 1 — fix

- [x] **QC1.1** Khai `-text` cho ba bundle trong `.gitattributes`, rồi lấy lại bytes gốc — Test: `python3 scripts/tdq_checkportable.py check --root <bundle>` không còn dòng `DRIFT` nào
  - Chạm: `.gitattributes`
  - Vì sao: `core.autocrlf=true` là mặc định của Git for Windows, nó đổi LF thành CRLF lúc
    checkout. Manifest giữ sha256 của bytes LF dựng trên macOS, nên mọi clone Windows đều thấy
    bundle lệch toàn bộ dù file đúng nguyên vẹn. Đây là lỗi có sẵn, không phải do request này.
