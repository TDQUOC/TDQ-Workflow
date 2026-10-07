# PLAN — Phân tích: bỏ Lumen thì TDQ trên Claude Code và Codex còn chạy ổn không

Ngày: 2026-10-07 · Spec: ../spec/2026-10-07-1843-phan-tich-bo-lumen.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — user chọn "1b" (inline) lúc duyệt; đề xuất ban đầu là subagent theo `tdq_bench simulate` (chênh 4,0 phút)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Bản đồ phụ thuộc
- P2 — Chuẩn bị Lumen sống cho nhánh CÓ
- P3 — Đo chất lượng 2 nhánh × 2 repo
- P4 — Thử 2 host khi Lumen vắng
- P5 — Báo cáo
- Px — Log & test bắt buộc
- Cụm song song
- Bộ câu hỏi đo (user xem trước khi duyệt)
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo; cụm song song ghi ở mục riêng.
2. Mỗi task: đánh `[~]` khi bắt đầu → làm → kiểm theo cột Test → đổi `[x]` NGAY vào file này.
3. Request không sửa mã: không có `tdq_test.py vung-cham` theo task; trọn bộ chỉ chạy ở QC (Q8).
4. Lệnh nào chạm state của workflow (`tdq_finish.py`, `tdq_setup.py`) phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. Không sửa file cấu hình của user: giả lập chỉ bằng cờ theo lần chạy (`--settings`, `-c`, `USERPROFILE`/`PATH` tạm). Cờ không ăn → `lech add`, rồi mới sửa file có bản sao.
6. QC FAIL → thêm task fix vào mục QC của file này, loop đến khi pass.
7. Không commit/push cho đến khi user yêu cầu.

## P1 — Bản đồ phụ thuộc
- [x] **T1.1** (e25m) Đi qua 51 file nhắc lumen (ngoài `docs/`, `graphify-out/`, `claude-export/`, `.git`): LSP `find_references` cho `_binary_lumen`, `step_reindex`, `LUMEN`, `TANG_KHAI_NIEM`, `khai_mcp_codex`; grep cho câu luật chữ. Mỗi điểm: file:dòng → GÃY/ỒN/ỔN × Claude Code/Codex + bằng chứng. Ghi `docs/tdq/research/2026-10-07-1843-phan-tich-bo-lumen.md` — Test: số file có dòng xếp loại hoặc lý do loại = 51

  - Dùng: tdq-setup (tham chiếu `uu-tien-tim-kiem.md`, `lumen.md`)
  - Để: lấy luật 4 tầng (`uu-tien-tim-kiem.md`) và cấu hình lumen (`lumen.md`) làm chuẩn xếp loại, nạp skill TRƯỚC khi xếp loại
  - Ra: cột "luật chữ" trong `docs/tdq/research/2026-10-07-1843-phan-tich-bo-lumen.md`
  - Kiểm: mọi câu luật nhắc lumen trong 2 file đó có dòng xếp loại
  - Không dùng cho: chạy cài đặt/sửa máy

**Xong P1 khi**: bảng phủ đủ 51 file.

## P2 — Chuẩn bị Lumen sống cho nhánh CÓ
- [x] **T2.1** (e15m) Đánh thức ollama (`OLLAMA_HOST=http://localhost:11434`, model `qwen3-embedding:0.6b`), `lumen index` TDQ-Workflow và `claudecodeui`, ghi thời gian index vào `docs/tdq/bench/2026-10-07-1843-chat-luong-lumen/chuan-bi.md` — Test: `lumen search "<một câu>" -p <repo> -n 1` trả `<result:file` ở cả 2 repo
  - Dùng: `lumen:doctor` (mcp)
  - Để: xác nhận backend + index tươi trước khi đo, nạp skill TRƯỚC khi index
  - Ra: `docs/tdq/bench/2026-10-07-1843-chat-luong-lumen/chuan-bi.md`
  - Kiểm: `lumen search` trả kết quả ở cả 2 repo
  - Không dùng cho: sửa cấu hình lumen của user
- [x] **T2.2** (e2m) Ghi lại cấu hình lumen dùng khi đo vào `chuan-bi.md` — Test: file có model + endpoint
  - Cần: T2.1
  - Dùng: `lumen:reindex` (mcp)
  - Để: index lại nếu doctor báo cũ
  - Ra: dòng "index tươi lúc …" trong `chuan-bi.md`
  - Kiểm: `index_status` báo không stale
  - Không dùng cho: dựng lại sạch (clean rebuild) khi không cần

## P3 — Đo chất lượng 2 nhánh × 2 repo
Mỗi task là một agent nhận 12 câu (KHÔNG kèm đáp án), trả về cho từng câu: vị trí tìm được, danh sách tool đã gọi, số lượt tool. Agent nhánh KHÔNG bị cấm mọi tool tên chứa `lumen`.
- [x] **T3.1** (e15m) Agent nhánh CÓ — TDQ-Workflow → `ket-qua-tdq-co.md` — Test: đủ 12 dòng kết quả
  - Cần: T2.2
- [x] **T3.2** (e15m) Agent nhánh KHÔNG — TDQ-Workflow → `ket-qua-tdq-khong.md` — Test: đủ 12 dòng, 0 lời gọi lumen
- [x] **T3.3** (e15m) Agent nhánh CÓ — claudecodeui → `ket-qua-ccui-co.md` — Test: đủ 12 dòng kết quả
  - Cần: T2.2
- [x] **T3.4** (e15m) Agent nhánh KHÔNG — claudecodeui → `ket-qua-ccui-khong.md` — Test: đủ 12 dòng, 0 lời gọi lumen
- [x] **T3.5** (e12m) Chấm theo đáp án, ghi token từng agent, áp luật kết luận §3 mục 3 của spec cho từng repo → `tong-hop.md` — Test: mỗi repo có số trúng/trượt 2 nhánh, tỉ lệ token, và một câu kết luận theo luật
  - Cần: T3.1, T3.2, T3.3, T3.4

**Xong P3 khi**: `tong-hop.md` có kết luận cho cả 2 repo.

## P4 — Thử 2 host khi Lumen vắng
Thư mục ra: `docs/tdq/bench/2026-10-07-1843-hai-host-khong-lumen/`.
- [x] **T4.1** (e2m) `sha256sum ~/.codex/config.toml ~/.claude/settings.json` → `sha-truoc.txt` — Test: file có 2 dòng hash
- [x] **T4.2** (e12m) Claude Code: `claude -p --settings '{"enabledPlugins":{"lumen@claude-plugins-official":false}}'` trong TDQ-Workflow, prompt bắt phải tìm code một câu khái niệm; ghi output, danh sách MCP tool thấy được, có/không `[TDQ:SEARCH]` chặn, tầng nào mở khoá → `claude-code.md` — Test: output thật có trong file, không có tool `lumen` nào được liệt kê
  - Cần: T4.1
- [x] **T4.3** (e12m) Codex: `codex exec -c 'mcp_servers.lumen.command="C:/khong-ton-tai/lumen.exe"'` trong TDQ-Workflow, cùng prompt; ghi lỗi/cảnh báo khởi động MCP, hành vi search gate → `codex.md` — Test: output thật có trong file, ghi rõ phiên chạy hết hay dừng
  - Cần: T4.1
- [x] **T4.4** (e10m) Script TDQ với binary vắng (`USERPROFILE` tạm, `PATH` không lumen, `TDQ_PROJECT_DIR` là bản sao tạm của repo): `tdq_lsp.py check`, `tdq_finish.py`, `tdq_setup.py` (chế độ kiểm), `setup_status.py` → `script-tdq.md` — Test: mỗi lệnh có exit code + output, ghi có/không traceback
- [x] **T4.5** (e2m) Hash lại → `sha-sau.txt`, so với `sha-truoc.txt`; xác nhận plugin lumen vẫn `true` — Test: 2 hash trùng
  - Cần: T4.2, T4.3, T4.4

**Xong P4 khi**: 3 biên bản có output thật, hash trùng.

## P5 — Báo cáo
- [x] **T5.1** (e20m) Viết `docs/tdq/report/2026-10-07-1843-phan-tich-bo-lumen.md`: có/không cho từng host, bảng GÃY/ỒN/ỔN rút gọn, kết luận chất lượng theo luật, danh sách đề xuất sửa (mỗi dòng: file + bằng chứng ở P1/P3/P4) — Test: mỗi đề xuất có ít nhất một liên kết tới file bằng chứng
  - Cần: T1.1, T3.5, T4.5

## Px — Log & test bắt buộc
Log: BỎ — request chỉ ra tài liệu và số đo, không có mã chạy được.
- [x] **Tx.1** (e8m) Trọn bộ test, so tập module đỏ với mốc (3 module: `test_codex_edit_gate.py`, `test_codex_hooks_json.py`, `test_finish_reindex.py`) — Test: `python3 scripts/tdq_test.py tron-bo` → tập đỏ ⊆ mốc

## Cụm song song
Ba cụm độc lập, gộp ở P5:
- Cụm A: P1 (đọc mã, main).
- Cụm B: P2 → P3 (T3.1–T3.4 song song 4 agent, T3.5 sau cùng).
- Cụm C: P4 (chạy tiến trình ngoài; T4.2 và T4.3 song song được).
Không có file nóng: mỗi task ghi một file riêng.

## Bộ câu hỏi đo (user xem trước khi duyệt)
- TDQ-Workflow: `docs/tdq/bench/2026-10-07-1843-chat-luong-lumen/cau-hoi-tdq-workflow.md`
- claudecodeui: `docs/tdq/bench/2026-10-07-1843-chat-luong-lumen/cau-hoi-claudecodeui.md`

## Definition of Done
Trỏ về §6 của spec, mỗi dòng một lệnh kiểm:

- [x] Q1 bản đồ phủ 51 file — `grep -c` số dòng file trong bảng của research = 51
- [x] Q2 bộ đo đủ 12 câu/repo, 4 lần chạy có kết quả từng câu — đếm dòng trong 2 file câu hỏi + 4 file kết quả
- [x] Q3 kết luận áp đúng luật định trước — `tong-hop.md` có trúng/trượt + tỉ lệ token + câu kết luận cho mỗi repo
- [x] Q4 thử Claude Code có output thật — `claude-code.md` chứa output nguyên văn + lệnh
- [x] Q5 thử Codex có output thật — `codex.md` chứa output nguyên văn + lệnh
- [x] Q6 script TDQ khi binary vắng không traceback — `grep -c Traceback script-tdq.md` = 0 (hoặc traceback được xếp GÃY trong báo cáo)
- [x] Q7 máy về như cũ — `diff sha-truoc.txt sha-sau.txt` rỗng
- [x] Q8 hồi quy — `python3 scripts/tdq_test.py tron-bo` đỏ ⊆ 3 module mốc
- [x] Q9 báo cáo đủ — báo cáo có mục kết luận cho 2 host và mỗi đề xuất có liên kết bằng chứng
