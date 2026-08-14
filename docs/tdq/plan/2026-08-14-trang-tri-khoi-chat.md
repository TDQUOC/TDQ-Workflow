# PLAN — Trang trí khối chat cuối trả lời user

Ngày: 2026-08-14 · Spec: ../spec/2026-08-14-trang-tri-khoi-chat.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — 16 file nhưng phụ thuộc một chiều chặt (khuôn gốc → 8 skill → 3 portable phải khớp từng luật), và 5 task khác nhau cùng sửa `tests/test_user_facing_block.py`; chia song song sẽ đụng file. (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH — 18/18 task tick `[x]`, QC 3 vòng xong, report đã viết

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. **Luật giữ chữ (spec §4):** mọi task sửa văn bản chỉ được thêm ký tự trang trí
   (`*`, `` ` ``, tiền tố `- `) và xuống dòng. Cấm sửa, xoá, thêm từ.

## P0 — Lưới an toàn trước khi siết

- [x] **T0.1** (n3 e8m) Viết `scripts/scan_block_symbols.py` quét mọi ký tự Unicode loại `P*`/`S*` ngoài ASCII trong 12 file phạm vi kiểm (khuôn gốc + 8 skill + 3 portable), in bảng `ký tự | codepoint | số lần | file`; lưu kết quả vào `docs/tdq/qc/2026-08-14-trang-tri-khoi-chat.md` mục `## Quét ký tự trước khi siết` — Test: `python3 scripts/scan_block_symbols.py` exit 0 và in ≥ 1 dòng dữ liệu; mục QC tồn tại (`grep -c 'Quét ký tự trước khi siết' docs/tdq/qc/2026-08-14-trang-tri-khoi-chat.md` = 1)
- [x] **T0.2** (n5 e20m) Với mỗi ký tự T0.1 tìm ra mà KHÔNG thuộc `➤ · —`: tra nguồn xem nó có render đúng trên cả ba mặt không, rồi quyết một trong hai — đưa vào whitelist (có nguồn) hoặc thay bằng ký tự ASCII (không có nguồn), ghi quyết định + nguồn vào cùng mục QC. Quét ra 0 ký tự lạ thì ghi đúng một dòng "không có ký tự ngoài whitelist" và tick xong — Test: mọi ký tự lạ trong bảng T0.1 đều có ô "quyết định" và ô "nguồn" khác rỗng
  - Dùng: `tavily-search` (mcp)
  - Để: tra khả năng render của từng ký tự lạ trên terminal / desktop app / IDE extension; nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc `skills/tavily-search/SKILL.md` rồi làm theo.
  - Ra: các dòng "quyết định + nguồn" trong `docs/tdq/qc/2026-08-14-trang-tri-khoi-chat.md` mục `## Quét ký tự trước khi siết`
  - Kiểm: `grep -c 'nguồn:' docs/tdq/qc/2026-08-14-trang-tri-khoi-chat.md` ≥ số ký tự lạ tìm được
  - Không dùng cho: tra lại những thứ research phase analyze đã kết luận (màu, cỡ chữ, bảng) — đã chốt ở spec §1
  - Dùng: `claude-code-guide`
  - Để: đối chiếu kết luận tavily bằng nguồn nội bộ về hành vi render của Claude Code, chỉ cho ký tự lạ chưa có nguồn công khai. Agent ngoài không có skill system: bỏ qua bước này và ghi "không đối chiếu được".
  - Ra: một dòng đối chiếu cho mỗi ký tự lạ, trong cùng mục QC
  - Kiểm: mỗi ký tự lạ có ít nhất một dòng bắt đầu bằng `đối chiếu:` trong mục QC
  - Không dùng cho: quyết định thay mặt user về việc nới whitelist — luật 2A đã chốt cách quyết

  - Kết quả T0.1: `scripts/scan_block_symbols.py` (2 chế độ: toàn file và `--chi-khoi`). Toàn file 11 ký hiệu / 8 ngoài whitelist; chỉ khối mẫu 6 ký hiệu / 3 ngoài whitelist. Đây là số đo tại thời điểm T0.1, khi bản portable của khuôn chưa tồn tại và whitelist mới có 3 ký tự. Chạy lại sau khi làm xong ra 17 / 11 (toàn file) và 6 / 0 (chỉ khối).
  - Kết quả T0.2: whitelist chốt **6 ký tự** `➤ · — → – …` (thêm 3 ký tự có bằng chứng chạy thật); loại `▸`; phát hiện `⏳` `✔` ở `tdq-status/SKILL.md:26` là emoji lọt lưới → sinh task QC0.1. Không gọi tavily/claude-code-guide vì luật 2A đã quyết bằng bằng chứng trong repo — lý do ghi ở file QC.

**Xong P0 khi**: bảng quét có mặt trong file QC và không còn ký tự nào chưa có quyết định. — ĐẠT

## P1 — Khuôn gốc

- [x] **T1.1** (n5 e15m) Thêm vào `tests/test_user_facing_block.py` hàm `test_rules_table_and_seven_rules`: khuôn phải có bảng cấu trúc ≥ 6 dòng `| ` (1 tiêu đề + 5 thành phần), đúng 7 dòng luật khớp `^[1-7]\. `, và cả hai tiêu đề `### Trước` / `### Sau` — Test: `python3 -m pytest tests/test_user_facing_block.py -k rules_table -q` ĐỎ trước T1.2, XANH sau
- [x] **T1.2** (n5 e20m) Viết lại `skills/tdq-conventions/references/user-facing-block.md`: giữ nguyên 5 thành phần và 7 chỗ phải dùng, thêm bảng "thành phần → cấu trúc trình bày dùng", 7 luật trang trí đánh số theo spec §3, mục whitelist đúng 6 ký tự chốt ở T0.2 (`➤ · — → – …`) kèm lý do loại `▸`, và khối mẫu `### Trước` / `### Sau` — Test: T1.1 xanh + `python3 -m pytest tests/test_user_facing_block.py -q` xanh

**Xong P1 khi**: T1.1 xanh và khuôn gốc đã có đủ bảng, 7 luật, whitelist, khối mẫu trước/sau.

## P2 — 8 file skill

- [x] **T2.1** (n5 e15m) Thêm hàm `test_sample_blocks_follow_rules`: quét mọi khối ``` trong 8 file skill có khối mẫu, kiểm luật 1 (nhãn trường in đậm, dấu hai chấm nằm trong cặp sao), luật 3 (đường dẫn sau `Xem đầy đủ tại: ` bọc backtick), luật 7 (dòng `➤` là dòng cuối khối), và không chứa `~~`, `<span`, `\x1b[`, `^#{1,6} `, ký tự `─│┌┬┐├└` — Test: `python3 -m pytest tests/test_user_facing_block.py -k sample_blocks -q` ĐỎ trước T2.2
- [x] **T2.2** (n5 e25m) Áp 7 luật vào khối mẫu của 8 file: `tdq-spec/SKILL.md`, `tdq-plan/SKILL.md`, `tdq-plan/references/mode-gate.md`, `tdq-intake/references/lane-decision.md`, `tdq-intake/references/quick-lane.md`, `tdq-intake/references/interview.md`, `tdq-build/references/report-template.md`, `tdq-status/SKILL.md` — Test: T2.1 xanh, và với từng file `diff <(git show HEAD:<f> | sed 's/[*`]//g; s/^- //' | tr -s '[:space:]' '\n' | sort) <(sed 's/[*`]//g; s/^- //' <f> | tr -s '[:space:]' '\n' | sort) | grep -c '^<'` = 0

**Xong P2 khi**: T2.1 xanh với cả 8 file và không file nào mất từ.

## P3 — 3 file mã sinh chuỗi

- [x] **T3.1** (n5 e12m) Thêm hàm `test_code_generated_blocks_conform`: import `hooks/scripts/_common.py`, gọi hàm sinh dòng gợi ý cho cả nhánh duyệt và nhánh chọn mode, kiểm chuỗi trả về khớp luật 7 và chỉ chứa ký tự whitelist; đồng thời kiểm 3 chuỗi máy đang bắt còn nguyên (`· Góp ý: nhắn trực tiếp`, `plan đề xuất {mode}`, `➤ Duyệt: `) — Test: `python3 -m pytest tests/test_user_facing_block.py -k code_generated -q` ĐỎ trước T3.2
- [x] **T3.2** (n5 e15m) Rà đúng 5 chỗ sinh chuỗi (`scripts/tdq_state.py` 2 chỗ, `hooks/scripts/_common.py` 2 chỗ, `hooks/scripts/stop_gate.py` 1 chỗ): chỗ nào lệch 7 luật thì sửa, chỗ nào đã đúng thì ghi một dòng "không đổi" vào file QC; cấm đổi byte của 3 chuỗi máy bắt — Test: T3.1 xanh + `python3 -m pytest tests/test_context_hooks.py -q` xanh

**Xong P3 khi**: T3.1 và `tests/test_context_hooks.py` cùng xanh.

## P4 — 3 file portable

- [x] **T4.1** (n5 e10m) Thêm hàm `test_portable_matches_source`: `portable/workflow/references/user-facing-block.md` phải chứa đủ 7 luật và cùng whitelist như khuôn gốc; `02-spec.md` và `03-plan.md` phải chứa khối mẫu khớp luật 1/3/7 — Test: `python3 -m pytest tests/test_user_facing_block.py -k portable -q` ĐỎ trước T4.2
- [x] **T4.2** (n3 e12m) Đồng bộ 3 file portable theo khuôn gốc bản mới — Test: T4.1 xanh + diff từng từ (như T2.2) = 0 với cả 3 file

**Xong P4 khi**: T4.1 xanh và 3 file portable không mất từ.

## P5 — Log & test bắt buộc

Log: BỎ — request chỉ sửa chuỗi hiển thị trong 3 file mã vốn đã có log sẵn (`_info()` ở
`stop_gate.py`), không thêm và không bớt một dòng log nào.

- [x] **T5.1** (n5 e12m) Thêm hàm `test_symbol_whitelist`: mọi ký tự Unicode loại `P*`/`S*` ngoài ASCII trong **nội dung khối ```** của 12 file phạm vi kiểm phải thuộc whitelist chốt ở T0.2 (phạm vi khối, không phải cả file — lý do ở file QC); chữ tiếng Việt (loại `L*`) không bị đụng — Test: `python3 -m pytest tests/test_user_facing_block.py -k whitelist -q` xanh, và thử chèn `▸` vào khuôn thì test phải ĐỎ (rồi hoàn tác)
- [x] **T5.2** (n1 e5m) Chạy full suite đúng một lần — Test: `python3 -m pytest tests/ -q` → 0 failed và số test ≥ 569

**Xong P5 khi**: toàn bộ suite xanh, số test không giảm so với mốc 569 của bản 0.16.0.

## Definition of Done

Trỏ về §6 của spec (10 hạng mục). Liệt kê lại kèm lệnh kiểm:

| # | Hạng mục | Lệnh kiểm |
|---|---|---|
| Q1 | Mặt A — bảng cấu trúc đủ 5 thành phần | `grep -A9 'Thành phần' skills/tdq-conventions/references/user-facing-block.md \| grep -c '^| '` ≥ 6 |
| Q2 | Mặt A — đủ 7 luật đánh số | `grep -cE '^[1-7]\. ' <khuôn>` = 7 |
| Q3 | Mặt A — có khối mẫu trước/sau | `grep -c '### Trước\|### Sau' <khuôn>` = 2 |
| Q4 | Mặt B — không cấu trúc rủi ro trong khối mẫu | `grep -nE '~~\|<span\|\x1b\[\|^#{1,6} \|[─│┌┬┐├└]' <khuôn> <8 file skill>` → 0 kết quả |
| Q5 | Mặt B + 3B — whitelist ký hiệu | `python3 -m pytest tests/test_user_facing_block.py -q` xanh, có hàm `test_symbol_whitelist` |
| Q6 | Mặt D — chuỗi máy bắt còn nguyên | `grep -c '· Góp ý: nhắn trực tiếp' hooks/scripts/_common.py` ≥ 2 và `grep -c 'plan đề xuất {mode}' hooks/scripts/_common.py` = 1 |
| Q7 | Mặt D — test cũ không đỏ, không giảm số test | `python3 -m pytest tests/ -q` → 0 failed, ≥ 569 test |
| Q8 | Mặt C — 11 file trỏ về khuôn gốc | `grep -l 'user-facing-block' <11 file>` đủ 11 |
| Q9 | Mặt C — portable khớp khuôn gốc | `python3 -m pytest tests/test_user_facing_block.py -k portable -q` xanh |
| Q10 | 3A — 0 từ nội dung bị mất | diff từng từ (đã chuẩn hoá bỏ `*`, `` ` ``, tiền tố `- `) → `grep -c '^<'` = 0 với mọi file đã sửa |

Ngoài 10 hạng mục: một lượt QC độc lập bằng agent `tdq-qc-tester`, mọi phát hiện của nó
được xử lý từng cái (sửa, hoặc ghi rõ vì sao không sửa) trong `docs/tdq/qc/<slug>.md`.

## QC vòng 0 — fix lỗi T0.2 lộ ra

- [x] **QC0.1** (n4 e15m) Mở rộng phép cấm emoji: thay `skills/tdq-status/SKILL.md:26` hai ký tự `✔` `⏳` bằng cấu trúc formal (chữ + `·`), vá dải `EMOJI` trong `tests/test_user_facing_block.py` để phủ U+23F3 và U+2714, và quét phép cấm đó trên cả 12 file phạm vi thay vì chỉ file khuôn — Test: `python3 -m pytest tests/test_user_facing_block.py -k emoji -q` xanh, và `grep -c '✔\|⏳' -r skills/ portable/` = 0

## QC vòng 1 — fix

- [x] **QC1.1** (n2 e10m) Q8 FAIL (8/11 file trỏ về khuôn): thêm dòng trỏ khuôn vào `skills/tdq-status/SKILL.md` và `portable/workflow/02-spec.md`, mở rộng `POINTERS` trong test lên 9 file skill cộng 2 file portable — Test: `python3 -m pytest tests/test_user_facing_block.py -k points_here -q` xanh và Q8 đếm được 10/11 (file khuôn gốc không tự trỏ về chính nó)

## QC vòng 2 — fix phát hiện của agent `tdq-qc-tester`

- [x] **QC2.1** (n2 e8m) Sửa markdown vỡ ở `skills/tdq-intake/references/lane-decision.md` dòng 56-57: bỏ cặp sao lồng trong đoạn in nghiêng, trả hai dòng về đúng dạng in nghiêng nguyên khối — Test: `grep -c '\*\*_' skills/tdq-intake/references/lane-decision.md` = 0, và diff từng từ so với `HEAD` = 0
- [x] **QC2.2** (n3 e12m) Bịt điểm mù của luật 1: thêm regex `NHAN_SAI` bắt dạng `**Nhãn**:` (dấu hai chấm nằm ngoài cặp sao) mà `LABEL` bỏ sót — Test: chèn `**Mục tiêu**: <1–2 câu>.` vào khối mẫu của `skills/tdq-spec/SKILL.md` thì `pytest tests/test_user_facing_block.py` ĐỎ đúng thông báo luật 1; hoàn tác thì xanh
- [x] **QC2.3** (n2 e10m) Chặn phép kiểm chạy rỗng: thêm bảng `SO_KHOI` chốt số khối mẫu của từng file, `kiem_khoi_mau` so số đếm trước khi kiểm nội dung — Test: xoá khối mẫu trong `skills/tdq-plan/SKILL.md` thì test ĐỎ với thông báo "số khối mẫu đổi từ 1 thành 0"; hoàn tác thì xanh
- [x] **QC2.4** (n1 e10m) Ghi bốn phát hiện còn lại vào `docs/tdq/qc/2026-08-14-trang-tri-khoi-chat.md` mục `## Vòng QC độc lập` — Test: `grep -c 'Vòng QC độc lập' docs/tdq/qc/2026-08-14-trang-tri-khoi-chat.md` = 1
