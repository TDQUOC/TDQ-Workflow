# QC — Ép luật tìm kiếm 4 tầng cho Claude Code và Codex

Ngày: 2026-10-03 · Spec: ../spec/2026-10-03-0015-ep-luat-tim-kiem.md ·
Plan: ../plan/2026-10-03-0015-ep-luat-tim-kiem.md · Mức QC: `full`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Mức `full` chạy: DoD + trọn unit test + hồi quy vùng chạm + ràng buộc kiến trúc + clean code.
Hai task plan gọi agent ngoài (T8.5 `code-review`, T8.6 `simplify`) là ĐẦU RA của plan, không
phải mức QC được nâng lên.

**Kết luận: PASS có điều kiện.** 21/23 hạng mục PASS. Q9 và Q19 bị chặn NGOÀI tầm (Codex chưa
đăng nhập; macOS và Linux đang tắt) — phần làm được trên máy này đã làm đủ, phần còn lại cần user.

## 23 hạng mục Definition of Done

Mọi lệnh dạng `python -m unittest discover tests -p <file> -k <nhóm>`; số in ra là kết quả thật
của lần chạy cuối (sau F1–F9 và T8.6).

| # | Hạng mục | Kết quả | Bằng chứng |
|---|---|---|---|
| Q1 | Chặn đoán mò trước tầng khái niệm | **PASS** | `test_search_rules -k doan_mo` → `Ran 13 tests OK` |
| Q2 | Không chặn tên chính xác trong cửa sổ | **PASS** | `-k cua_so` → `Ran 4 tests OK` |
| Q3 | Không chặn lọc danh sách file | **PASS** | `-k loc_file` → `Ran 6 tests OK` |
| Q4 | Mở khoá sau tầng khái niệm | **PASS** | `-k mo_khoa` → `Ran 6 tests OK` (gồm `echo graphify query x` KHÔNG mở khoá, `start_lsp` không tính) |
| Q5 | Sổ sống qua lượt | **PASS** | `test_search_observe -k qua_luot` → `Ran 6 tests OK`; ca gọi đúng `turn_log_clear` rồi đòi sổ còn |
| Q6 | Không gây kẹt | **PASS** | `test_search_gate -k chua_san_sang` → `Ran 6 tests OK`; thêm cầu dao 3 lần chặn (F2) |
| Q7 | Cổng rẻ | **PASS** | `-k nhe` → `Ran 2 tests OK`: không `subprocess`/`os.system`/`os.popen`/`os.spawn`; đúng một `open(` — mốc sẵn sàng |
| Q8 | Cổng không làm vỡ lệnh | **PASS** | `-k hong` → `Ran 12 tests OK` |
| Q9 | Codex bị chặn thật | **BỊ CHẶN NGOÀI TẦM** | `codex login status` → `Not logged in` (lần đầu: 401). Phần kiểm được: `test_codex_search_gate` → `Ran 13 tests OK` (hook ghi vào `.codex/hooks.json` với đường tuyệt đối có thật; khuôn `deny` giống `codex_edit_gate.py` đang chạy từ 2026-09-10) |
| Q10 | Codex có công cụ | **PASS** | chạy thật `codex mcp list`: `cloudcli-browser`, `lsp`, `lumen` — mục cũ còn nguyên, có file backup; `test_codex_mcp` → `Ran 10 tests OK` |
| Q11 | Bậc 3 thật | **PASS** | `test_bac3_khoi_dong` → `Ran 8 tests OK` |
| Q12 | Smoke grep đa ngôn ngữ | **PASS** | `test_smoke_ngon_ngu` → `Ran 4 tests OK` |
| Q13 | Một lệnh kiểm | **PASS** | `test_mot_lenh_kiem` → `Ran 4 tests OK` |
| Q14 | Đường dẫn tuyệt đối | **PASS** | `test_duong_dan_tuyet_doi` → `Ran 9 tests OK` |
| Q15 | Tự khởi tạo | **PASS** | `test_tu_khoi_tao -k kich_hoat` → `Ran 12 tests OK` |
| Q16 | Không chạy chồng | **PASS** | `-k chong` → `Ran 11 tests OK` |
| Q17 | Quyết định kiến trúc | **PASS** | `docs/kien-truc.md` có dòng 2026-10-03; `TDQ:SEARCH` có trong `_common.CODES` và bảng `reminder-codes.md`; `test_common` → `Ran 10 tests OK` |
| Q18 | Phát lại phiên thật | **PASS** | `search_replay.py` trên fixture excalidraw, N = 5/10/20: **bắt 11 · bắt oan 0 · lọt 0**, chặn ở lượt 4, 7, 9, 10, 11, 13, 14, 15, 20, 21, 22 — **lượt 7 và 9 bị bắt**. Xem ghi chú dưới bảng |
| Q19 | Ba hệ | **PARTIAL — bị chặn ngoài tầm** | Windows 3.13: `Ran 2336 tests in 346.107s · OK (skipped=9)`. macOS `100.105.75.71` và Linux `100.67.252.79`: `ping` không trả lời (kiểm lại 2026-10-03). Không mượn máy khác — user đã chốt chỉ dùng đúng hai máy này |
| Q20 | Ràng buộc kiến trúc | **PASS** | `grep -rn "^import hooks\|from hooks" scripts` → chỉ 2 câu văn trong docstring (+2 file `.pyc`), 0 import thật; luật thuần ở `scripts/search_rules.py`, hook ở `hooks/scripts/` |
| Q21 | Luật mở đầu | **PASS** | `-k mo_dau` → `Ran 2 tests OK` |
| Q22 | Ngoại lệ tên đã biết | **PASS** | `-k ten_trong_prompt` → `Ran 4 tests OK` |
| Q23 | Cửa sổ hết hạn | **PASS** | `-k het_han` → `Ran 3 tests OK` |

**Ghi chú Q18.** Lần đo đầu (T2.5) ra bắt 16; số đó do bộ phát lại cũ lọc trước sự kiện "doc" nên
bỏ qua lượt 23 `graphify god-nodes` — một câu hỏi kiến trúc thật. Cổng thật mở khoá ở đó, nên năm
lượt 28, 29, 34, 35, 36 đi qua. Sau F6 bộ phát lại chạy đúng luật của cổng (cùng
`la_goi_khai_niem`, `trang_thai`, mọi lệnh shell qua luật, lần bị chặn không ăn cửa sổ) → 11 là số
trung thực. Fixture vẫn KHÔNG phân biệt được N; N = 10 chốt bằng lý lẽ (brief, mục "Chọn N").

## Bốn hạng mục cố định

**QC-F1 — trọn bộ test.** `python -m unittest discover tests` → `Ran 2336 tests in 346.107s` ·
`OK (skipped=9)`. Lần chạy trước đó bắt được một lỗi thật: bảng phát lại in chuỗi `"deny"`, vi
phạm bất biến "mọi deny đi qua `_common.block()`" (`test_no_transcript_no_deny`) → đổi nhãn thành
`blocked`, commit `1aca178`.

**QC-F2 — hồi quy vùng chạm.**

| Module test | Kết quả |
|---|---|
| `test_search_rules.py` | `Ran 57 tests OK` |
| `test_search_observe.py` | `Ran 20 tests OK` |
| `test_search_gate.py` | `Ran 24 tests OK` |
| `test_search_replay.py` | `Ran 11 tests OK` |
| `test_codex_search_gate.py` · `test_codex_mcp.py` | `13` · `10` tests OK |
| `test_tu_khoi_tao.py` | `Ran 34 tests OK` |
| `test_subagent_start.py` (10 hook / 6 event) · `test_compliance_protocol.py` | `11` · `16` tests OK |
| `test_token_budget.py` | `Ran 8 tests OK` |

**QC-F3 — ràng buộc kiến trúc.** `scripts/` không import `hooks/`; `search_rules.py` thuần (test
đòi không `import os/io/subprocess`, không `open(`); deny của Claude Code chỉ qua
`_common.block(..., day_du=True)`; `doc_lint skills` exit 0; `token_budget --kiem` exit 0.

**QC-F4 — clean code.** Mỗi file một việc: luật thuần / sổ / cổng / adapter Codex / dựng nền.
Log service bật mặc định, tắt bằng `TDQ_LOG=0`, có test ở mọi file mới. `i18n_check` trên 5 file
mới (`search_rules`, `search_replay`, `tdq_codex_mcp`, `search_gate`, `search_observe`) → 0 dòng
Việt. T8.6 gom hằng trùng: tên mốc sẵn sàng (3 bản → 1 ở `search_rules.MOC_SAN_SANG`) và tập tên
công cụ shell (2 bản → 1).

## T8.5 — soát lỗi đúng-sai (`code-review`, 2 agent độc lập)

**18 phát hiện, gộp trùng còn 16 việc, gom vào 9 task fix F1–F9. Không phát hiện nào bị bác.**
Mã `R1#n` là phát hiện của reviewer đúng-sai, `Vn` của reviewer tuân luật repo — như plan trích.

| Phát hiện | Nội dung | Phán quyết | Xử lý |
|---|---|---|---|
| V5 | `la_goi_khai_niem`/`trang_thai` có bản sao lệch nhau giữa sổ và bộ phát lại | NHẬN | F1: dời về `search_rules.py` thuần, dùng chung |
| R1#10 | `echo graphify query x`, commit message nhắc graphify → mở khoá giả | NHẬN — lỗi thật | F1: nhận graphify bằng phân tích lệnh (chương trình + lệnh con) |
| — | LSP tính theo danh sách loại trừ → `run_tests`, `apply_edit` mở khoá | NHẬN | F1: danh sách CHO PHÉP các tool hỏi |
| V2 | Mốc báo cả ba tầng không sẵn sàng mà cổng vẫn chặn → kẹt | NHẬN — lỗi thật | F2: đứng xuống; thêm cầu dao 3 lần chặn khi chưa ghi được lần gọi khái niệm nào |
| V3 | Cổng đứng xuống trong im lặng → agent tưởng luật vẫn giữ | NHẬN | F2: nói ra một lần mỗi lượt qua `_common.remind` |
| R1#11 | Request đã đóng (`idle`) vẫn dùng khoá request cũ → lumen cũ mở khoá mọi việc sau | NHẬN — lỗi thật | F3: `idle` → khoá phiên |
| R1#2 | Prompt và lần gọi lumen trước `init` bị quên khi request mở | NHẬN | F3: `doc_so` đọc thêm dòng `phien:` cùng phiên |
| R1#3 | `grep --help` bị coi là tìm code | NHẬN | F4 |
| R1#4 | Thân heredoc (`cat > x.sh <<EOF … grep …`) bị coi là lệnh chạy | NHẬN | F4: bỏ thân heredoc trước khi tách |
| R1#5 | Grep chỉ trong `.md`/`.txt`/`docs/` bị coi là tìm code | NHẬN | F4: đích toàn tài liệu → không phải tìm; Grep xét `glob`/`path`/`type` |
| R1#7 | `bash -c '…'`, `powershell -Command`, `cmd /c` lọt | NHẬN — lỗi thật | F4: mở shell bọc rồi phân loại bên trong |
| R1#8 | `find … -exec grep` lọt | NHẬN | F4 |
| R1#9 | `grep -f pats.txt` (danh sách đoán dời vào file) lọt | NHẬN | F4: `-f` → đoán mò; giá trị của tuỳ chọn không bị tính là đích (bắt được khi probe: `pats.txt` từng làm lệnh trông như đọc tài liệu) |
| R1#6 | Tool `PowerShell` của Claude Code không qua cổng | NHẬN — lỗi thật | F5: matcher `Bash\|Grep\|PowerShell` |
| — | Lý do deny chỉ nêu tên tool lumen của Claude Code | NHẬN | F5: nêu cả tên Codex `mcp__lumen__semantic_search` |
| V1 | Chuỗi in ra của `search_replay`, `tdq_codex_mcp` còn tiếng Việt | NHẬN — vi phạm luật ngôn ngữ | F6, F7 |
| — | Bộ phát lại đếm cả lần bị chặn vào cửa sổ, lọc trước lệnh Bash | NHẬN | F6 (đo lại Q18 → 11/0/0) |
| V4 | `graphify query` qua Bash dưới Codex không được ghi | NHẬN | F7: gắn `search_observe` vào cả shell |
| — | Cập nhật plugin → `.codex/hooks.json` có bộ thứ hai trỏ đường cũ | NHẬN — lỗi thật | F7: nhận entry theo tên script, sửa tại chỗ; chịu file hỏng |
| R1#12 | Dựng nền chạy cả ở thư mục home/gốc ổ | NHẬN | F8: chỉ project có `.git` |
| R1#13 | Khoá rỗng vừa tạo (chưa kịp ghi pid) bị coi là chết → chạy chồng | NHẬN — đua thật | F8: khoá rỗng < 10 s coi như đang giữ |
| V6 | Hồ sơ nói "đúng hai điểm chặn" trong khi `edit_gate` chặn `TDQ:TICK`/`TDQ:TEAM` | NHẬN | F9: sửa `reminder-codes.md` và `kien-truc.md` |

Mỗi việc có test đi kèm; F4 bắt được thêm một ca lúc probe (`-f FILE`) trước khi viết test.

## T8.6 — rút gọn

Gom hằng trùng (mốc sẵn sàng, tập tên shell) về `search_rules.py`. Không đổi hành vi: trọn bộ
`2336 OK` trước và sau. Không tách thêm hàm — phần `_lenh`/`phan_loai` đã gọn sau F4.

## Sai lệch có chủ ý, đã ghi

1. Dưới Codex lần gọi khái niệm được ghi ở `PreToolUse` (Codex chưa cho hook sau-tool với MCP ổn
   định) — một lần gọi lỗi vẫn mở khoá. Chấp nhận: hướng sai là CHO QUA, không phải chặn oan.
2. `search_rules.py` không tự log; người gọi log (khoá bằng test `test_log_module_thuan_khong_tu_in`).
3. Trần ký tự đo trên NỘI DUNG; đường dẫn tuyệt đối gắn SAU trần (`lenh_cho_project`) — nếu không,
   lời nhắc ở project khác bị cắt mất chính lệnh cần chạy.

## Nợ khai ra, không giấu

1. **Q9 — Codex bị chặn trong một lượt thật.** Cần `codex login` trên Windows (hoặc Mac bật lại).
   Lệnh kiểm khi có: trong một project đã chạy `tdq-setup`, `codex exec "grep -rn 'foo\|bar\|baz' src"`
   → phải thấy `TDQ:SEARCH` deny.
2. **Q19 / T8.4 — macOS và Linux.** Hai máy tắt. CI có ma trận ba hệ nhưng là máy sạch của GitHub.
3. **T3.3 — phần `codex exec`** cùng lý do với mục 1; phần ghi config thật đã làm (Q10).
4. **`TRAN_GIAY` có thể vượt** khi một tầng treo đúng lúc chạm trần, và đua nhỏ khi rút gọn sổ
   600 dòng giữa hai phiên ghi cùng lúc — độ tin thấp, chưa tái hiện được; ghi để theo dõi.
5. **`TDQ:TICK`/`TDQ:TEAM` không có trong `_common.CODES`** — nợ có từ trước request này.
6. **`tdq_setup.py` còn chuỗi in tiếng Việt** (`ĐẠT/TRƯỢT`, `chưa kiểm`) theo khuôn sẵn có của file;
   dịch thuộc luồng i18n.
