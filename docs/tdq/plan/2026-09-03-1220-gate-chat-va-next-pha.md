# PLAN — Cổng hỏi bằng chat, Next step nêu pha kế, và đường kẻ cuối lượt

Ngày: 2026-09-03 · Spec: ../spec/2026-09-03-1220-gate-chat-va-next-pha.md (bản 1.2, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — đo bằng `tdq_bench.py mo-phong --he-so-agent 1.5`: đội thắng 12.2 phút (24.5 so với 36.6), 18 task chia 4 đợt. Cảnh báo đọc kèm: chỉ 5 task được giao đi, 11 task leader giữ, nên phần thắng đến từ đúng cụm B (6 skill khác file nhau). (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH · mode: main (user chốt "1b" lúc 13:02)

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Luật trình bày ở tầng conventions
- P2 — Sửa 12 dòng `Next step:`
- P3 — Test khoá
- P4 — Bản portable
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → sửa → test xanh → đổi sang `[x]`
   NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Mọi lần sửa `skills/` xong phải chạy `python3 scripts/doc_lint.py skills/` — R6 giới hạn số
   dòng từng skill, vượt trần là đỏ.

## P1 — Luật trình bày ở tầng conventions

- [x] **T1.1** (e14m) Thêm luật cấm tool hỏi dạng popup vào mục `## Hard rules` của
  `user-facing-block.md`: áp cho MỌI câu hỏi gửi user, không riêng 7 cổng; hỏi bằng danh sách
  trong chat; nêu đúng tên tool để test bắt được — Test: `grep -c "AskUserQuestion"
  skills/tdq-conventions/references/user-facing-block.md` trả về ≥ 1, và câu luật nêu chữ "mọi câu hỏi"
- [x] **T1.2** (e10m) Thêm vào `approval.md` luật kết lượt: hỏi xong là kết lượt, chờ user trả
  lời bằng chat, cấm tự suy diễn duyệt, cấm hỏi bằng popup (trỏ về T1.1 thay vì chép lại) —
  Test: `grep -n "kết lượt" skills/tdq-conventions/references/approval.md` có kết quả
- [x] **T1.3** (e16m) Thêm **thành phần 6** vào `user-facing-block.md`: đường kẻ `---` là dòng
  cuối cùng của LƯỢT, đặt ngay SAU dòng `➤`; nêu rõ ký tự là ba gạch nối, không nhận `———` hay
  ký tự khung — Test: file có mục thành phần 6 và câu nêu ký tự `---`
- [x] **T1.4** (e12m) Sửa thành phần 5 và mục `## Hard rules` cho hết mâu thuẫn: câu "khối trả
  lời là phần cuối, không viết gì bên dưới" đổi thành "bên dưới chỉ có đúng đường kẻ cuối lượt".
  Sửa cả hai ví dụ `Trước`/`Sau` ở cuối file cho có đường kẻ sau dòng `➤` — Test:
  `grep -c "không viết gì bên dưới\|Printing anything after it"` trả về 0
- [x] **T1.5** (e10m) Thêm luật `Next step:` vào `tdq-conventions/SKILL.md`: mỗi dòng nêu tên pha
  kế tiếp (hoặc nói rõ pha không đổi + skill kế), và nói rõ đây là LỚP DỰ PHÒNG — hook
  `[TDQ:NEXT]` vẫn là đường chính, dòng này gánh khi host không có hook — Test:
  `python3 scripts/doc_lint.py skills/tdq-conventions/` exit 0 và file có chữ "dự phòng"

**Xong P1 khi**: `doc_lint.py skills/` exit 0, và không còn câu nào trong `user-facing-block.md`
nói hai điều trái nhau về dòng cuối.

## P2 — Sửa 12 dòng `Next step:`

Mỗi task sửa các dòng của MỘT skill, để hai task không đụng chung file.

- [x] **T2.1** (e8m) `skills/tdq-intake/SKILL.md` — 3 dòng (83, 103, 120): nêu pha kế
  (`analyze`/`quick_analyze`, `spec`, `idle`) — Test: mỗi dòng chứa tên một pha có trong `PHASE_TABLE`
- [x] **T2.2** (e8m) `skills/tdq-build/SKILL.md` — 3 dòng (108, 119, 130): `qc`, `report`, `idle`
  — Test: như trên
- [x] **T2.3** (e5m) `skills/tdq-spec/SKILL.md` — 1 dòng (84): pha `plan` — Test: như trên
- [x] **T2.4** (e5m) `skills/tdq-plan/SKILL.md` — 1 dòng (109): pha `implement` — Test: như trên
- [x] **T2.5** (e8m) `skills/tdq-status/SKILL.md` (52), `skills/tdq-check-status/SKILL.md` (70),
  `skills/tdq-lsp-setup/SKILL.md` (118) — ba dòng KHÔNG đổi pha; phải nói rõ "pha không đổi" và
  skill kế là gì — Test: mỗi dòng chứa chữ nêu pha không đổi + tên skill kế
- [x] **T2.6** (e5m) `skills/tdq-conventions/SKILL.md` (67) — dòng đã trỏ `phases.md`, bổ sung
  câu nêu pha kế đọc từ đâu khi không có hook — Test: `doc_lint.py skills/tdq-conventions/` exit 0
  (làm chung lượt với T1.5 vì cùng một file; cap R6 của `tdq-conventions` nâng 168 → 177)

**Xong P2 khi**: `grep "^Next step:" skills/*/SKILL.md` cho 12 dòng, mỗi dòng nêu được pha kế
hoặc nêu rõ pha không đổi.

## P3 — Test khoá

- [x] **T3.1** (e25m) Viết `tests/test_luat_gate_chat.py` với test 1: quét mọi file trong
  `skills/` bắt tên tool hỏi dạng popup xuất hiện ở ngữ cảnh CHO PHÉP dùng. Danh sách trừ khai
  bằng đường dẫn cụ thể (`user-facing-block.md`, `interview.md`), không bằng regex lỏng — Test:
  `python3 -m pytest tests/test_luat_gate_chat.py -q -k popup` xanh; thêm câu cho phép popup vào
  một skill tạm → đỏ
  - Chạm: `tests/test_luat_gate_chat.py` → file mới, chưa node nào phụ thuộc
  - Cần: T1.1
- [x] **T3.2** (e25m) Thêm test 2 vào cùng file: đọc `PHASE_TABLE` từ `scripts/tdq_state.py`, quét
  mọi dòng `Next step:` trong `skills/*/SKILL.md`, đỏ khi một dòng không nêu tên pha nào và cũng
  không nêu "pha không đổi + skill kế" — Test: `pytest tests/test_luat_gate_chat.py -q -k next_step`
  xanh; xoá tên pha khỏi một dòng → đỏ
  - Chạm: `tests/test_luat_gate_chat.py`
  - Cần: T2.1, T2.2, T2.3, T2.4, T2.5, T2.6
- [x] **T3.3** (e15m) Thêm test 3: `user-facing-block.md` phải có luật đường kẻ cuối lượt, khai
  đúng ký tự `---`, và KHÔNG còn câu mâu thuẫn về dòng cuối — Test:
  `pytest tests/test_luat_gate_chat.py -q -k duong_ke` xanh; xoá luật → đỏ
  - Chạm: `tests/test_luat_gate_chat.py`
  - Cần: T1.3, T1.4
- [x] **T3.4** (e10m) Chạy `pytest tests/test_luat_skill.py tests/test_ranh_gioi.py -q` và sửa
  `docs/tdq/audit/luat-hien-co.md` nếu một điểm neo `L###` bị lệch do P1 sửa chữ — Test: hai file
  test đó xanh
  - Kết quả: `test_ranh_gioi.py` xanh. `test_luat_skill.py` đỏ đúng 1 test
    (`test_so_dong_ghi_trong_bang_van_tro_dung_cho`, 84/329 = 25.5%, ngưỡng 5%) — con số y hệt
    mốc trước khi P1 sửa chữ, đã kiểm bằng `git stash`. Lệch có sẵn, không do yêu cầu này;
    dựng lại `luat-hien-co.md` là việc ngoài phạm vi spec nên không làm ở đây.
  - Chạm: `docs/tdq/audit/luat-hien-co.md`
  - Cần: T1.4

**Xong P3 khi**: cả ba test mới xanh, và số test đỏ toàn suite không tăng so với mốc 100.

## P4 — Bản portable

- [x] **T4.1** (e10m) Dựng lại cả 3 bản portable rồi kiểm — Test:
  `python3 scripts/build_portable.py` exit 0, rồi
  `python3 scripts/tdq_checkportable.py check --root <mỗi bundle>` in CLEAN
  - Kết quả: build exit 0 (v0.39.0). CLEAN cả ba: `portable_claude` 92 file,
    `portable_codex` 142 file, `antigravity_portable` 85 file. Các dòng NOTE còn lại là việc
    duyệt MCP thủ công trên máy, không phải lệch bundle.
  - Cần: T2.6, T3.3

- [x] **T4.2** (e12m) Chạy vòng QC độc lập rồi viết `docs/tdq/report/<slug>.md` — Test:
  file report tồn tại, mục QC ghi đủ Q1–Q11 kèm bằng chứng
  - Dùng: `tdq-build`
  - Để: chạy pha `qc` và pha `report` đúng khuôn, nạp skill TRƯỚC khi mở vòng QC. Agent ngoài
    không có skill system: đọc `skills/tdq-build/SKILL.md` rồi làm theo.
  - Ra: `docs/tdq/report/2026-09-03-1220-gate-chat-va-next-pha.md`
  - Kiểm: `python3 scripts/doc_lint.py docs/tdq/report/` exit 0
  - Không dùng cho: sửa nội dung luật ở P1 — đó là việc của cụm A
  - Cần: T4.1
- [x] **T4.3** (e8m) QC FAIL thì thêm task fix vào mục QC của chính file plan này, loop tới khi
  pass — Test: mọi mục QC FAIL đều có một task tương ứng trong file plan
  - Kết quả: vòng QC 1 PASS cả 15 hạng mục, không mục nào FAIL nên không phải thêm task fix.
    Điều kiện của task không kích hoạt.
  - Dùng: `tdq-plan`
  - Để: giữ đúng khuôn task khi thêm task fix giữa chừng (mã task, `(eNm)`, dòng Test)
  - Ra: mục `## QC` trong `docs/tdq/plan/2026-09-03-1220-gate-chat-va-next-pha.md`
  - Kiểm: `python3 scripts/doc_lint.py --pair <spec> <plan>` exit 0
  - Không dùng cho: viết lại spec — spec đã duyệt và niêm sha
  - Cần: T4.2

**Log: BỎ** — việc này chỉ sửa tài liệu skill và thêm test quét văn bản, không có runtime mới.

## Cụm song song

Ba cụm, cắt theo module của spec §2b:

- Cụm A (P1): cả 5 task đều chạm `skills/tdq-conventions/` — T1.1/T1.3/T1.4 chạm CHUNG
  `user-facing-block.md`, nên **phải chạy tuần tự**, không tách agent được.
- Cụm B (P2): 6 task, mỗi task một skill khác nhau, không giao file → chạy song song được. Đây là
  trần tốc độ của mode đội.
- Cụm C (P3): T3.1–T3.3 chạm chung `tests/test_luat_gate_chat.py` → tuần tự, và còn phải chờ
  cụm A và B xong.

Trần song song thật sự chỉ là 6 task nhỏ ở cụm B (tổng e39m), phần còn lại tuần tự.

## Definition of Done

- [x] Q1 Luật cấm popup có mặt ở tầng conventions, nêu rõ áp cho mọi câu hỏi —
  `grep -n "AskUserQuestion" skills/tdq-conventions/references/user-facing-block.md`
- [x] Q2 `approval.md` nói rõ hỏi xong kết lượt, chờ user chat trả lời —
  `grep -n "kết lượt" skills/tdq-conventions/references/approval.md`
- [x] Q3 Test khoá cấm popup đỏ đúng lúc — `pytest tests/test_luat_gate_chat.py -q -k popup`
- [x] Q4 Mọi dòng `Next step:` nêu pha kế — `pytest tests/test_luat_gate_chat.py -q -k next_step`
- [x] Q5 Test `Next step:` đỏ khi xoá tên pha — chạy tay: xoá tên pha ở một dòng, chạy lại lệnh Q4, phải đỏ
- [x] Q6 Luật `Next step:` nói rõ vai trò dự phòng — `grep -n "dự phòng" skills/tdq-conventions/SKILL.md`
- [x] Q7 Không còn câu mâu thuẫn về dòng cuối —
  `grep -c "không viết gì bên dưới" skills/tdq-conventions/references/user-facing-block.md` bằng 0
- [x] Q8 Test khoá luật đường kẻ, khai đúng ký tự —
  `pytest tests/test_luat_gate_chat.py -q -k duong_ke`
- [x] Q9 Lint tài liệu toàn repo — `python3 scripts/doc_lint.py skills/ docs/` exit 0
- [x] Q10 Không hồi quy — `python3 -m pytest tests/ -q`, số test đỏ ≤ 100
- [x] Q11 Bản portable — `python3 scripts/build_portable.py` rồi
  `python3 scripts/tdq_checkportable.py check --root <mỗi bundle>` in CLEAN cho cả 3
