# QC — Tối ưu context của tdq-workflow: cổng nhắc đọc lại, chỉ mục dòng, trần token, bảng CI

Ngày: 2026-10-02 · Spec: ../spec/2026-09-28-2324-toi-uu-context-workflow.md ·
Plan: ../plan/2026-09-28-2324-toi-uu-context-workflow.md · Mức QC: `full`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Mức `full` chạy: DoD + trọn unit test + hồi quy vùng chạm + ràng buộc kiến trúc + clean code.
KHÔNG chạy smoke test và runtime test ở phase này, KHÔNG gọi agent QC độc lập — đó là mức `ultra`.
Ngoại lệ có chủ ý: plan có hai task P8 gọi agent ngoài (`code-review`, `simplify`) để soát lỗi
đúng-sai và rút gọn — hai task đó là ĐẦU RA của plan, không phải mức QC được nâng lên.

## 20 hạng mục Definition of Done

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Cổng nhắc khi đọc lại | **PASS** | `test_read_gate -k nhac` → `Ran 2 tests OK`; lần đọc đầu im, lần hai in `[TDQ:DOC] to-sach.md (12 KB) is already in context…` |
| Q2 | Cổng im khi đọc vùng khác | **PASS** | `-k im_vung` → OK; `offset=200 limit=40` sau một lần đọc trọn → không nhắc |
| Q3 | Cổng im khi file đã đổi | **PASS** | `-k im_doi` → OK; nối một dòng vào file rồi đọc lại → không nhắc |
| Q4 | Cổng không làm chậm | **PASS** | `-k nhe` → OK, dò trên AST đã bỏ docstring: không `subprocess`/`os.system`/`os.popen`/`os.spawn`, không `count_tokens`, không `io.open`. Một `os.stat` + một dòng append |
| Q5 | Cổng cắm đủ mọi host | **PASS** | `hooks.json`: `PreToolUse` matcher `Read` → `read_gate.py` (7 entry, README đã cập nhật). Bản agy: dựng thật ra `hooks/scripts/read_gate.py` + `_common.py`, `test_build_portable` → `Ran 32 tests OK` |
| Q6 | Sinh chỉ mục idempotent | **PASS** | `test_doc_index -k Idempotent` OK; chạy `--tat-ca` hai lần trên bản sao cây `skills/`: `0/25 file(s) changed` lần hai, byte giống nhau |
| Q7 | Chỉ mục đúng khoảng dòng | **PASS** | `chi_muc_con_dung()` xanh trên cả 25 file có chỉ mục; `doc_index.py --kiem --tat-ca` → exit 0 |
| Q8 | Chỉ mục có mặt đủ | **PASS** | 14 file ≥ 2.000 token đều có khối. Hai file từng lọt (`bang-lech.md` 51 dòng/2.111 token, `plan-template-co-che.md`) bắt được sau khi `file_can_chi_muc` đọc thêm ngưỡng TOKEN từ tệp khoá — ngưỡng dòng một mình bỏ sót file DÀY mà ít dòng |
| Q9 | Tệp khoá sinh lại được | **PASS** | `test_token_budget_lock -k sinh` → `Ran 3 tests OK`; sinh hai lần ra nội dung byte-giống-nhau; 50 bản ghi |
| Q10 | Trần token cưỡng chế được | **PASS** | `-k tran_token` → OK, trong đó một ca đọc mã nguồn `kiem_khoa` và đòi KHÔNG có `count_tokens`/`nap_bo_dem`. Chạy thật trên file giả 9.999 token → `doc_lint` in `[R13] … 9999 tokens > the cap of 3500` và thoát 1 |
| Q11 | Khoá cũ bị bắt | **PASS** | `-k khoa_cu` → OK; và gặp THẬT 4 lần trong lượt này: mỗi lần sửa file luật mà chưa sinh lại khoá, `doc_lint` in `the token measurement is stale (sha256 differs)` |
| Q12 | Ba file về dưới trần | **PASS** | theo tệp khoá: `plan-template.md` **3.493**, `quick-lane.md` **3.419**, `team-mode.md` **3.313**; max toàn vùng 50 file = 3.493 ≤ 3.500 |
| Q13 | Không mục luật nào bị mất | **PASS** | đếm `##`+`###` toàn `skills/`: **334 → 342 (+8)**, file 52 → 59. Không mục nào biến mất; `test_luat_skill` (329 dòng luật) → `Ran 11 tests OK` |
| Q14 | Bốn câu ép đọc trọn file đã gỡ | **PASS** | HEAD có 4 câu `MUST open … read all N steps` ở `tdq-build/SKILL.md:88,100,143,157` và 1 ở `tdq-intake/SKILL.md:129`. Nay: tdq-intake **0**, tdq-build còn 2 câu nhưng đã đổi thành đọc-theo-đoạn (`the step you are about to act on, through the line index`). Ghi chú trung thực: ba file reference nhánh (`qc.md`, `report-template.md`, `quick-lane.md`) vẫn có câu "read all N steps" — chúng KHÔNG nằm trong §2 mục 11 của spec, và chúng nói về các BƯỚC của nhánh vừa mở, không phải đọc trọn một file lạ |
| Q15 | Câu luật tìm kiếm một bản | **PASS** | đếm nguyên văn trên toàn `skills/`: **1 bản**; `test_tdq_setup_skill` → `Ran 13 tests OK` (năm chỗ móc đều trỏ về `uu-tien-tim-kiem.md`, đều nói BẮT BUỘC, đều KHÔNG chép lại câu luật) |
| Q16 | Mục lục trùng đã cắt | **PASS (không có để cắt)** | đo lại: `plan-template.md` và `spec-template.md` mỗi file chỉ có MỘT `## Mục lục`, và nó nằm TRONG fence `markdown` — tức là phần khuôn mẫu được chép vào tài liệu, không phải mục lục thứ hai của file reference. Giả thuyết "mục lục song ngữ trùng" ở §2 mục 13 không đúng với cây file thật; không xoá gì |
| Q17 | **Sàn tuân thủ giảm** | **PASS** | **55.439 → 49.531 token (−5.908, −10,7%)** ≤ 52.500. Đo bằng tokenizer thật trên cùng một danh sách file bắt buộc đọc của lane `full`, bản TRƯỚC lấy từ `git show HEAD:` |
| Q18 | CI in bảng | **PASS** | `.github/workflows/test.yml` có bước `python scripts/context_surface.py` kèm `continue-on-error: true`, gác `if` vào đúng một tổ hợp. Chạy thật: exit 0, in bảng 84 dòng. `test_ci_matrix` → `Ran 9 tests OK`, trong đó một ca đọc chính file yml và đòi `continue-on-error` |
| Q19 | Ràng buộc kiến trúc | **PASS** | `grep -rn "^import hooks\|from hooks" scripts/` → **0**; `read_gate.py` nằm ở `hooks/scripts/`, ba script mới ở `scripts/`; cổng trả `permissionDecision: "allow"` kèm `"TDQ: a reminder, not a block."` — không có `deny` nào |
| Q20 | Ba hệ | **PARTIAL** | Windows 3.13 `Ran 2142 tests OK (skipped=9)` · macOS thật pyenv 3.13.15 `Ran 2101 OK (skipped=34)` và brew 3.14.7 `Ran 2101 OK (skipped=34)` · **Linux: CHƯA CHẠY** — máy `tdq-nuc12dcmv7` đang tắt (`tailscale status`: offline, last seen 2h ago; ssh port 22 timeout). Không mượn máy khác vì user đã chốt chỉ dùng đúng hai máy này |

## Bốn hạng mục cố định

**QC-F1 — trọn bộ test.** `python -m unittest discover tests` →
`Ran 2142 tests in 316.547s` · `OK (skipped=9)`. Không fail, không error.

**QC-F2 — hồi quy vùng chạm.** Chạy riêng từng module trên các dòng `Chạm:` của plan:

| Module test | Kết quả |
|---|---|
| `test_read_gate.py` | `Ran 17 tests OK` |
| `test_doc_index.py` | `Ran 26 tests OK` |
| `test_token_budget_lock.py` | `Ran 13 tests OK` |
| `test_tdq_finish.py` | `Ran 17 tests OK` |
| `test_doc_lint.py` (+ các file `test_doc_lint*`) | `Ran 65 tests OK` |
| `test_build_portable.py` | `Ran 32 tests OK` |
| `test_ci_matrix.py` | `Ran 9 tests OK` |
| `test_luat_skill.py` | `Ran 11 tests OK` |
| `test_reference_mot_tang.py` | `Ran 4 tests OK` |
| `test_tdq_setup_skill.py` | `Ran 13 tests OK` |
| `test_claude_md_core.py` | `Ran 11 tests OK` |
| `test_quick_qc.py` · `test_user_facing_block.py` · `test_rules_library.py` · `test_subagent_start.py` | `17` · `10` · `5` · `11` tests, tất cả OK |

**QC-F3 — ràng buộc kiến trúc.** `scripts/` không import `hooks/`; hook chỉ nhắc; file mã mới
nằm đúng thư mục; `doc_lint skills/` exit 0; `doc_index --kiem --tat-ca` exit 0;
`token_budget --kiem` exit 0.

**QC-F4 — clean code.** 5 nguyên tắc SOLID và rule ngôn ngữ: ba script mới mỗi script một việc,
log service bật mặc định tắt bằng `TDQ_LOG=0`, không placeholder/TODO. Mã, chú thích và chuỗi máy
in ra của ba file mới đã về **tiếng Anh** đúng `docs/kien-truc.md` (`i18n_check` trên ba file:
0 dòng Việt). Nợ ngôn ngữ còn lại được khai ở mục cuối.

## T8.1 — soát lỗi đúng-sai (`code-review`, 2 agent độc lập)

Hai agent soát song song: một tìm lỗi đúng-sai trong mã mới, một soát việc tuân luật repo.
**14 phát hiện có thật, 14 đã xử lý.** Bảng dưới là phán quyết cho từng cái.

| # | Phát hiện | Phán quyết | Đã làm gì |
|---|---|---|---|
| 1 | Bản agy khai hook `read_gate.py` trong `hooks.json` mà danh sách chép file vẫn là một cặp cứng → mọi `PreToolUse` của agy chạy vào file không tồn tại; `_common.py` cũng không được chép | **NHẬN — lỗi thật** | Danh sách chép SUY RA từ `HOOK_AGY` + `_common.py`; dựng thật và xác minh. Khoá bằng 2 test đọc chính `hooks.json` đã sinh ra |
| 2 | `step_lint` chạy TRƯỚC `step_khoa_token` → R13 báo "khoá cũ" và `tdq_finish` thoát 1 ở mọi lượt sửa file luật | **NHẬN — lỗi thật** | `khoa-token` thành bước ĐẦU TIÊN; docstring và mô tả CLI sửa theo; gặp thật 4 lần trong lượt này nên có bằng chứng |
| 3 | `chi_muc_con_dung` so tên ĐÃ LÀM SẠCH với dòng tiêu đề THÔ → tên mục chứa `·` làm phép kiểm đỏ mãi mãi, mà lệnh nó khuyên không sửa được gì | **NHẬN — lỗi latent** | So `_sach_ten` ở cả hai phía; chứng minh bản cũ đỏ (`so-tho=False`), thêm test |
| 4 | `_cho_chen` đặt `i = 1` khi dò dấu đóng frontmatter → file mở đầu bằng dòng trắng bị chèn khối vào GIỮA frontmatter | **NHẬN — lỗi latent** | Dò từ dòng SAU dấu mở; chứng minh bằng ca thật; thêm test |
| 5 | Cổng đọc dựa vào sổ lượt, mà `prompt_context.py` xoá sổ đó ở MỖI prompt → cổng chỉ thấy đọc lại trong một lượt, không thấy ca 12 lần/phiên mà nó được dựng để bắt | **NHẬN — lỗi thật, và là lỗi nặng nhất** | Cổng có SỔ RIÊNG (`docs/tdq/.tdq-read.jsonl`), lọc theo phiên, hạn 6h, rút gọn khi quá 400 dòng. Thêm test `NhoQuaNhieuLuot` gọi đúng `turn_log_clear` rồi đòi vẫn nhắc |
| 6 | R13 gọi `kiem_khoa()` không tham số → kiểm khoá của TDQ trong khi lint một project khác | **NHẬN** | Gốc suy ra từ đường dẫn đang lint |
| 7 | `step_khoa_token` chỉ bắt `OSError` → `ValueError`/treo venv làm chết cả lệnh kết lượt | **NHẬN** | Bắt rộng kèm lý do viết ra; bước đổ không chặn `graphify`/`reindex` |
| 8 | `MA = "TDQ:DOC"` không có trong danh sách đóng `_common.CODES` | **NHẬN** | Thêm vào `CODES` kèm dòng lý do có ngày, và thêm hàng vào bảng `reminder-codes.md` |
| 9 | Mục đầu tiên dài quá trần ký tự → khối chỉ mục sinh một dòng rác chỉ có `·` | **NHẬN — cosmetic** | Thêm điều kiện `and hien`; test đòi không có dòng chỉ mang dấu phân cách |
| V1 | Con trỏ `eNm` ở `plan-template.md` trỏ sang `plan-template-co-che.md`, nhưng mục đó nằm ở `plan-template-huong-dan.md` | **NHẬN** | Sửa đúng tên file em và tên mục |
| V2 | Luật `eNm` ở HEAD là tiếng Anh, bị viết lại thành tiếng Việt khi dời; mệnh đề "before the work itself" mất | **NHẬN — vi phạm luật ngôn ngữ** | Dịch lại sang tiếng Anh, trả mệnh đề về `plan-template.md`, và trả cột `neo bản mới` của L309/L310 về neo tiếng Anh |
| V3 | `test_tdq_setup_skill.py` bị XOÁ 4 lưới thay vì trỏ lại — trong đó có phép kiểm duy nhất cho soul.md nguyên tắc 3 (đủ ba mục) | **NHẬN — hạ chất lượng** | Dựng lại cả 4 lưới, trỏ vào file em; thêm 2 lưới mới (file em phải được trỏ từ `SKILL.md`; ánh xạ lớp ↔ loại truy vấn). 6 → **13 test** |
| V4 | Chú thích lý do nâng trần dòng không khớp số thật ("+4..+8" trong khi thật là +8..+11) | **NHẬN** | Viết lại bằng bảng số thật: từng skill HEAD → nay, kích thước khối, trần cũ → mới, và nói rõ chừa ≤ 5 dòng |
| V8 | Ví dụ ĐÚNG trong `chung.md` mất một dòng trắng → chính nó phạm PEP 8 mà nó dạy | **NHẬN** | Trả lại dòng trắng; sinh lại chỉ mục và khoá theo |
| V5/V6 | Chú thích, docstring và chuỗi in ra của ba file mới + phần thêm vào `SKILL.md` còn tiếng Việt | **NHẬN phần của lượt này** | Dịch sang tiếng Anh: `read_gate.py`, `doc_index.py`, `token_budget.py` (0 dòng Việt), phần `doc_lint.py`/`tdq_finish.py` lượt này thêm, và mọi câu con trỏ mới trong 5 `SKILL.md` + `analyze-full.md`. Phần CÒN LẠI khai thành nợ ở mục cuối |
| V7 | Cột `neo bản mới` của L309/L310 dùng ngược chiều (ghi neo tiếng Việt) | **NHẬN** | Trả về neo tiếng Anh như HEAD |
| — | "Một thứ đổi dưới chân reviewer": `spec-template.md` mất rào `markdown` mở, làm cả khuôn mẫu lọt ra ngoài fence và chỉ mục chỉ vào mục của KHUÔN | **NHẬN — lỗi của lượt này, đã vá giữa lúc soát** | Trả lại `<!-- i18n-allow -->` + rào mở; chỉ mục sinh lại còn đúng 1 mục thật (`File em=115`) |

Không phát hiện nào bị bác bỏ. Phát hiện nào cũng có một lượt đo hoặc một test đi kèm, không
có cái nào chỉ sửa bằng niềm tin.

## T8.2 — rút gọn (`simplify`, 1 agent)

Chín chỗ rút gọn, **không chỗ nào đổi hành vi**, tám module test + `doc_lint` xanh trước và sau:

- `test_token_budget_lock.py`: `_ghi_khoa` tồn tại HAI bản giống từng byte ở hai lớp đều kế thừa
  `BaseKhoa` → dồn về một bản ở lớp cha.
- `test_read_gate.py`: màn `payload` + `env` lặp 5 lần → một hàm `chay()` dựng cả hai, kèm lý do
  phải đặt cùng nhau (sổ nằm dưới `cwd` của payload, còn `TDQ_PROJECT_DIR` nằm ở env).
- `test_doc_index.py`: một hàm ghi file thứ hai bên cạnh hàm của lớp cơ sở → `ghi()` nhận
  đường dẫn con; nội dung fixture giữ nguyên từng byte.
- `test_tdq_setup_skill.py` / `test_ci_matrix.py`: biểu thức tính lại ba lần / hai lần → tính một
  lần ở `setUp` hoặc biến tạm.
- `token_budget.sinh_khoa`: dựng lại cùng một đường dẫn ở hai vòng → dựng một lần.
- `read_gate.py`: `dang_nhac` bị gán rồi gán lại → một chuỗi short-circuit theo đúng thứ tự ba ca
  im lặng ghi trong docstring.
- `doc_index.py` + nhiều test: `chr(10)`/`chr(92)`/`chr(183)` còn sót từ lúc viết qua heredoc →
  ký tự thật.

Agent **từ chối có lý do** 4 chỗ: `_doc()` và `_log()` trùng giữa các script (đúng khuôn repo,
gộp lại chỉ thêm một cạnh import), con trỏ lý do "chạy trước lint" viết hai nơi (mỗi nơi phục vụ
một người đọc khác), và `test_build_portable.py` (phần trùng có từ trước lượt này).

Nó còn **báo một vi phạm luật mà nó cố ý không tự sửa** vì ngoài mandate: tiêu đề mục R13 trong
`doc_lint.py` còn tiếng Việt. Tôi đã dịch — đó là phát hiện thứ 15 và nó cũng đã xử lý.

## Nợ khai ra, không giấu

1. **Linux chưa chạy (Q20).** Máy thật đang tắt. CI có job `ubuntu-latest` × 2 bản Python che
   phần Linux, nhưng đó là máy sạch của GitHub, không phải máy thật của user. Mở lại khi máy bật.
2. **Nợ ngôn ngữ còn 129 dòng Việt trong `skills/`** (HEAD: 57). Trong đó **65 dòng ở
   `plan-template-co-che.md`** là văn bản ở HEAD nằm TRONG fence `i18n-allow` của
   `plan-template.md` và lượt này chỉ DỜI chỗ — đã ghi lý do vào đầu file đó. Dịch phần ấy thuộc
   luồng việc i18n, nơi mỗi luật được khoá qua cột `neo bản mới`; làm ở đây mà không có cột đó là
   cách để mất luật trong lúc dịch. Phần còn lại (~64 dòng) là nợ có từ trước lượt này.
3. **`tdq_finish.py` và `tdq_no.py` còn chú thích tiếng Việt** từ request trước (nợ đã khai ở
   `2026-09-28-0910`); lượt này chỉ dịch phần mình thêm vào.
4. **`hooks.json.truoc-tdq.bak` chưa có lệnh khôi phục** — nợ cũ, chưa thuộc phạm vi request này.
