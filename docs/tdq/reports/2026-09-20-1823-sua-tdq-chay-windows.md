# REPORT — Sửa bộ workflow TDQ chạy đủ tính năng trên Windows (`2026-09-20-1823-sua-tdq-chay-windows` · lane full · mode main · 22/22 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 thêm `scripts/utf8_io.py` ép UTF-8, nạp qua 2 chỗ dùng chung + 21 entry point · P2 shim `python3` qua `tdq_checkportable.py setup --shim`, dời `ten_lenh_python` về `tdq_ten_lenh.py`, thêm dòng quy ước trong header hook · P3 set `USERPROFILE` cạnh `HOME`, chuẩn hoá dấu chéo ở biên xuất · P4 đọc được layout `synced/` mới của Claude Code · P5 thêm `.lumenignore` và luật cấm mở file trước khi hỏi `find_references` · P6 vá kho skill-index, trần `claude-md-mau`, chỉ mục rule, drift `setup_status` · P7 cài 4 công cụ ngoài rồi vá 6 lỗi Windows thật trong code sản phẩm · P8 bump 0.49.0 + CHANGELOG, xoá `portable_codex.zip` lỗi thời · QC1.1 vá lỗi line-ending làm hỏng phép kiểm bundle trên mọi máy Windows.

**Kết quả:** test 670 fail / 97 error → **0 fail / 0 error** (1907 → 1983 ca, 17 skip) · hook sống 0/6 → **6/6** trên Python Windows mặc định, không cần biến môi trường · kiểm kê năng lực B0 trên máy này 0 → **11 skill** · index lumen 1488 → 1140 file, 27318 → 14503 chunk · lệnh `python3` của tầng luật chạy được ở Git Bash, cmd.exe, PowerShell.

**Kiểm:** `python3 -m unittest discover tests` → `Ran 1983 tests · OK (skipped=17)` · `doc_lint.py` 0 vi phạm trên brief, spec, plan, QC, CHANGELOG · `tdq_checkportable.py check` CLEAN cả ba bundle · QC **PASS 17/17 mục DoD + 4/4 mục cố định**, 1 vòng fix.

**Đầu ra:** `scripts/utf8_io.py` · `scripts/tdq_ten_lenh.py` · `scripts/tdq_checkportable.py` · `scripts/tdq_state.py` · `scripts/tdq_codex.py` · `hooks/scripts/_common.py` · `hooks/scripts/session_start.py` · `.gitattributes` · `.lumenignore` · 5 file test mới. Backup ngoài repo: `~/.claude.json.bak-20260920-191811` và `~/.claude/settings.json.bak-20260920-191811`.

**Sáu lỗi Windows trong code sản phẩm, tìm ra lúc làm chứ không có trong phân tích:** `skill_tokens` trỏ venv vào `bin/python` thay vì `Scripts/python.exe` · `shutil.rmtree` không xoá nổi file read-only mà git đánh dấu, thêm `tdq_state.xoa_cay` dùng ở 4 chỗ · `tdq_eval.dau_nhiem` trộn ngữ nghĩa đường dẫn host với transcript POSIX · `tdq_codex` gọi tên trần `codex` mà `CreateProcess` không tra `PATHEXT` · **`CreateProcess` không chạy được file `.cmd`**, nên mode codex chưa bao giờ chạy được trên Windows vì npm cài đúng dạng đó · harness codex giả là script không đuôi.

**Giới hạn:**
- **Ba bundle portable vẫn mang nội dung 0.48.0**, chưa có `utf8_io.py`. Phán quyết `2a` của user: đây là bước phát hành, phải chạy `python3 scripts/build_portable.py` trên macOS hoặc Linux, vì bản agy nướng cứng thư mục nhà của máy dựng.
- **Chưa chạy được lần nào trên macOS/Linux.** Mọi nhánh POSIX của các thay đổi đã được gọi thử bằng tham số hệ và đều là no-op hoặc trả đúng giá trị cũ, nhưng đó không thay thế một lượt chạy thật.
- **Suite xanh một phần nhờ 4 công cụ ngoài đã cài** (`pytest`, `anthropic-tokenizer`, `graphify`, `codex`). Runner sạch sẽ đỏ khoảng 30 ca vì các ca đó *fail* khi thiếu công cụ thay vì *skip*.
- Hai node chưa có test riêng, đã khai ở QC-F2: `tdq_codex.boc_lenh` và `tdq_state.xoa_cay`, cả hai được phủ gián tiếp.
- Spec đổi một lần lên bản 1.1 giữa chừng: cách tiếp cận placeholder của bản 1.0 không thực hiện được vì Claude Code đọc thẳng `skills/**/SKILL.md` từ đĩa, hook không rewrite được. User duyệt lại.

**Git:** chưa commit. 63 file đang sửa trên nhánh `bugfix/tdq-chay-tren-windows`, chưa hợp về `main`.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 7s | — | 1 |
| analyze | 1h 31min | — | 1 |
| spec | 6 min | — | 1 |
| plan | 4 min | — | 1 |
| mode | 26s | — | 1 |
| implement | 4h 06min | — | 1 |
| qc | 8 min | — | 1 |
| report | 10s | — | 1 |
| **Total** | **5h 56min** | **—** | |

Cột model time là `—` vì không đọc được transcript của phiên này. Phase `analyze` chiếm 1h31 chủ
yếu là chờ user trả lời 4 vòng phỏng vấn cộng thời gian cài và đo lớp tìm kiếm LSP/lumen.
