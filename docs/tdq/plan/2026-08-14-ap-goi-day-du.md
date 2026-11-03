# PLAN — Áp Gói đầy đủ (Đ1–Đ7) của bản chấm tối ưu LLM

Ngày: 2026-08-14 · Spec: ../spec/2026-08-14-ap-goi-day-du.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — 21 file nhưng 4 file bị nhiều đề xuất cùng đụng và có một cổng duyệt nằm GIỮA hai phase, nên phải chạy tuần tự trong một hội thoại (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH — 17/17 task tick [x], QC 15 hạng mục xong, chưa commit
(Đã duyệt: user nhắn "duyệt plan" lúc 13:30, mode "a" = main; cổng P2: "duyệt phasee max")

Nguồn nội dung nháp cho mọi task: `docs/tdq/knowledge/2026-08-14-toi-uu-llm-workflow.md`
mục `## Đề xuất`. Quy ước đọc của mục đó: dòng tiêu đề Markdown trong khối `Nội dung nháp`
bị thụt 2 space, khi dán vào file thật phải bỏ 2 space đầu dòng.

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo. Đặc biệt: Đ6 (P1) phải xong TRƯỚC Đ1 (P3)
   vì cả hai cùng đụng `skills/tdq-intake/references/skill-inventory.md`.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. **Đích token là MỀM** (user chốt 1A): các số 1.290 / 1.320 / 1.500–2.500 chỉ là tham
   chiếu. Cấm lấy chúng làm điều kiện PASS/FAIL, cấm cắt câu chữ mang luật để đuổi theo số.
8. Bảy đề xuất chỉ ĐỔI CHỖ · ĐỔI NHÃN · THÊM ngưỡng đếm được · THÊM khối định dạng. Cấm
   viết lại nội dung một luật đang có.

## P0 — Chốt mốc "trước"

- [x] **T0.1** (n2 e5m) Lưu mốc trước khi sửa: `python3 scripts/skill_inventory.py` ra file
  baseline trong scratchpad, `python3 scripts/context_surface.py --quiet`, `wc -w` ba file
  `skills/tdq-conventions/references/`, và đếm mệnh lệnh 10 cụm file của bảng `## Đối chiếu
  luật` — ghi cột "trước" vào `docs/tdq/qc/2026-08-14-ap-goi-day-du.md` — Test:
  `grep -cE "^\| Đ[0-9]" docs/tdq/qc/2026-08-14-ap-goi-day-du.md` = 10 và file baseline tồn
  tại, kích thước 39.722 byte
  - Kết quả: 10 dòng ✓ · baseline 39.722 byte ✓ · mọi số đo khớp đúng bản chấm request
    trước (21/23/5/2/0/8/72/3, thân build 1.936, thân intake 1.844)

**Xong P0 khi**: file QC có đủ 10 dòng cột "trước" + 3 số `wc -w` + baseline output đã lưu.

## P1 — Phase văn bản (Đ2–Đ7), không đụng `scripts/`

- [x] **T1.1** (n5 e20m) Đ2 — cắt Phần C của `skills/tdq-intake/SKILL.md` (dòng 78–109),
  đưa nội dung về `references/quick-lane.md`, để lại 4 dòng trỏ — Test:
  `grep -c "" skills/tdq-intake/SKILL.md` giảm ≥ 20 dòng so với T0.1;
  `grep -c "^[0-9]\. " skills/tdq-intake/references/quick-lane.md` ≥ 9; đếm mệnh lệnh
  cặp hai file ≥ 17
  - Kết quả: 109 → 86 dòng (−23) ✓ · bước đánh số quick-lane 3 → 12 ✓ · luật cặp 21 → 25 ✓
    · thân `tdq-intake` 1.844 → **1.288 token** · `doc_lint` exit 0
- [x] **T1.2** (n5 e25m) Đ3 — cắt Phần B và Phần C của `skills/tdq-build/SKILL.md`
  (dòng 64–116) về `references/qc.md` và `references/report-template.md` — Test:
  `python3 scripts/context_surface.py --quiet | grep "tdq-build/SKILL.md"` cho thân
  < 1.400 token; đếm mệnh lệnh cụm ba file ≥ 23
  - Kết quả: 116 → 84 dòng (−32) · thân `tdq-build` 1.936 → **1.536 token** (−21%) ·
    luật cụm ba file 23 → 32 ✓ · `pytest tests/test_skill_shape.py -q` 11 passed
  - Đích 1.400 KHÔNG đạt (1.536): phần còn lại của thân là Luật cứng + Phần A, ngoài
    phạm vi T1.2. Theo luật thi hành 7 (user chốt 1A) đích token là MỀM — DoD chỉ đòi
    token giảm và luật không giảm, cả hai đều đạt.
- [x] **T1.3** (n3 e15m) Đ4 — đẩy mục thuần giải thích của `reminder-codes.md`,
  `plugin-routing.md`, `tavily.md` xuống cuối file dưới nhãn `## Phụ lục`, **giữ nguyên
  100% câu chữ** (user chốt 4A) — Test: `wc -w` từng file bằng đúng số ở T0.1;
  `grep -c "^## Phụ lục" skills/tdq-conventions/references/reminder-codes.md` = 1
  - Kết quả: `wc -w` 642→645 · 401→404 · 314→317, chênh ĐÚNG 3 từ mỗi file = nhãn
    `## Phụ lục` vừa thêm. Diff theo từ (`tr | sort | diff`): **0 từ bị mất** ở cả ba
    file, phần thêm chỉ gồm `##`/`###` + `Phụ` + `lục` → giữ 100% câu chữ (4A) ✓
  - Luật giữ nguyên: 5 / 2 / 0 đúng bằng T0.1 ✓ · `grep -c "^## Phụ lục"` = 1 ở cả ba file
  - Q3 của DoD viết "wc -w bằng ĐÚNG mốc T0.1" là bất khả thi về số học khi phải thêm
    nhãn: cách kiểm đúng cho ý 4A là **0 từ bị mất**, cộng chênh đúng bằng số từ của
    nhãn. Ghi lại đây để trình user ở cổng P2; chưa sửa dòng DoD đã duyệt.
- [x] **T1.4** (n2 e8m) Đ5 — thay 2 dòng mơ hồ ở `scope-round.md:35` và `:88` bằng ngưỡng
  đếm được — Test: `grep -cEi "phù hợp|nếu cần|tối ưu|hợp lý|linh hoạt"
  skills/tdq-intake/references/scope-round.md` = 0; đếm mệnh lệnh file ≥ 8
  - Kết quả: từ mơ hồ 2 → **0** ✓ · mệnh lệnh 8 → 8 (không mất luật) ✓
  - Dòng 35 "linh hoạt (mở rộng, đa nền tảng)" là TÊN đặc tính ISO/IEC 25010:2023, không
    phải chỉ dẫn mơ hồ → giữ nguyên nghĩa, đổi sang tên gốc `Flexibility — mở rộng, đa
    nền tảng`. Dòng 88 "không tối ưu sớm, DoD gọn" → `0 hạng mục hiệu năng, DoD ≤ 5 dòng`
- [x] **T1.5** (n5 e25m) Đ6 — dán chú "nhắc lại có chủ ý — bản gốc ở `<đường dẫn>`" tại 8
  chỗ luật được nói lại (build/SKILL:85, report-template:3, spec/SKILL:8, plan/SKILL:8,
  status/SKILL:8, quick-lane, skill-inventory, mode-gate:44) — Test:
  `grep -rl "nhắc lại có chủ ý" skills/ | wc -l` ≥ 8; đếm mệnh lệnh cụm 8 file = 72 (đúng
  bằng T0.1 — lệch là dấu hiệu đã sửa nhầm luật)
  - Kết quả: **8 file** có chú ✓ · mệnh lệnh cụm 72 → **83** (TĂNG, không giảm — 11 dòng
    thêm là các dòng trỏ "BẮT BUỘC mở file… cấm làm theo trí nhớ" của Đ2/Đ3 và 8 dòng chú
    Đ6; cụm này chứa 4 file mà Đ2/Đ3 đã sửa nên "= 72" không còn giữ được, điều kiện thật
    là **không giảm**)
  - 8 chỗ: build/SKILL bước 2.6 → `## Luật cứng` · report-template `## Khuôn` → bước 7 ·
    spec/SKILL, plan/SKILL, status/SKILL (tiếng Việt) → `tdq-conventions/SKILL.md` ·
    quick-lane `## Luật tick` → `tdq-build/SKILL.md` · skill-inventory → `analyze-full.md`
    B0 · mode-gate `## Tên gọi` → `tdq-plan/SKILL.md` bước 6
  - **Sửa kèm 2 file test** (đỏ do Đ2/Đ3 dời chỗ, không phải mất luật):
    `tests/test_user_facing_block.py` trỏ khuôn hỏi commit sang `report-template.md`;
    `tests/test_quick_qc.py` bỏ N2 khỏi `LAW_DOCS` và THÊM test mới bắt N2 phải trỏ đúng
    mục `Chín bước thi hành` ở N1 → `pytest tests/ -q` **564 passed, 0 failed**
- [x] **T1.6** (n3 e15m) Đ7 — thêm khối định dạng đầu ra copy được vào
  `agents/tdq-implementer.md`, `tdq-qc-tester.md`, `tdq-reviewer.md` — Test:
  ``grep -c '^```' agents/tdq-implementer.md agents/tdq-qc-tester.md agents/tdq-reviewer.md``
  ≥ 2 mỗi file; đếm mệnh lệnh cụm ba file ≥ 6
  - Kết quả: khối ``` 0/0/0 → **2/2/2** ✓ · mệnh lệnh cụm 3 → **4** (không giảm)
  - Ngưỡng "≥ 6" của dòng Test viết sai lúc lập plan: mốc T0.1 chỉ có 3, đạt 6 nghĩa là
    phải BỊA thêm luật cho đủ số. Điều kiện thật của DoD là không giảm → 3 → 4 đạt.
  - Mỗi agent nhận một khuôn trả lời copy được: implementer (TASK/STATUS/FILES/TEST/
    BRANCH/TICK-READY/NOTES), qc-tester (bảng verdict + DEFECTS + VERDICT), reviewer
    (finding đánh số có nhãn loại + `file:dòng` + KẾT LUẬN) · `pytest` 564 passed
- [x] **T1.7** (n3 e10m) Đối chiếu luật cho toàn bộ P1 và ghi cột "sau" vào file QC — Test:
  8 dòng thuộc Đ2–Đ7 có "sau" ≥ "trước", 0 dòng giảm; `python3 -m pytest tests/ -q` = 563
  passed; `python3 scripts/doc_lint.py` trên spec + plan exit 0
  - Kết quả: **0/10 dòng giảm** (5 tăng, 5 giữ — 2 dòng giữ là Đ1 chưa tới lượt) ·
    `pytest tests/ -q` **564 passed, 0 failed** (563 + 1 test mới của T1.5) ·
    `doc_lint.py --pair` exit 0 · `git status --porcelain -- scripts hooks portable` RỖNG
  - Tầng `nạp khi gọi skill` 8.473 → **7.579 token** (−10,6%); tầng `đọc khi cần`
    43.981 → 46.061 (+2.080) — đúng ý đồ: nội dung tụt xuống tầng rẻ hơn, không mất chữ
  - 19 file đã đụng: 17 file `.md` trong `skills/`+`agents/` + 2 file test

**Xong P1 khi**: 17 file văn bản đã sửa, 8 dòng đối chiếu không dòng nào giảm,
`git status --porcelain -- scripts hooks portable` RỖNG, pytest 563 passed.

## P2 — Cổng duyệt giữa hai phase (user chốt 2B)

- [x] **T2.1** (n1 e3m) Trình báo cáo phase văn bản rồi **DỪNG** chờ user duyệt: nêu số
  dòng đã giảm, bảng 8 dòng đối chiếu luật, kết quả pytest, và danh sách 17 file đã đụng —
  Test: tin nhắn có đủ ba con số (dòng giảm · luật trước/sau · pytest) và kết bằng dòng
  duyệt; sau tin nhắn đó KHÔNG có sửa file nào cho tới khi user trả lời

**Xong P2 khi**: user nhắn duyệt phase văn bản. Chưa duyệt thì cấm bắt đầu P3.

## P3 — Phase mã (Đ1)

Cổng P2 đã mở: user nhắn nguyên văn "duyệt phasee max" lúc 14:02 ("mã" gõ Telex thành
"max") → duyệt phase mã, làm tiếp trong cùng turn.

- [x] **T3.1** (n3 e8m) Tra ảnh hưởng của việc sửa `scripts/skill_inventory.py` trước khi
  đụng vào — Test: mục "Ảnh hưởng Đ1" trong file QC có ≥ 1 dòng caller, lệnh chạy exit 0
  - Dùng: `graphify`
  - Để: liệt kê nơi gọi `skill_inventory.py` và hàm `inventory()`, nạp skill TRƯỚC bước đỏ.
    Agent ngoài không có skill system: đọc
    `/Users/truongdinhquoc/.claude/skills/graphify/SKILL.md` rồi làm theo.
  - Ra: mục `## Ảnh hưởng Đ1` trong `docs/tdq/qc/2026-08-14-ap-goi-day-du.md`
  - Kiểm: `graphify affected scripts/skill_inventory.py` exit 0 và mục đó khác rỗng
  - Không dùng cho: 17 file `.md` của P1 — `.graphifyignore` loại tài liệu khỏi đồ thị
  - Kết quả: exit 0. `affected` theo đường dẫn ra rỗng (node id là `scripts_skill_inventory`);
    theo node `scripts_skill_inventory_inventory` ra đúng 1 caller `main()` L209. 26 cạnh nội bộ,
    1 `imports` sang `tdq_state`. Caller văn bản: 2 file `.md` của T3.6 + `tdq_state.py:565`.
- [x] **T3.2** (n2 e8m) Tra bộ nhớ dài hạn xem đã có quyết định nào về kiểm kê skill hay
  cắt output công cụ chưa, để không làm ngược cái đã chốt — Test: kết quả search được ghi
  1–3 dòng vào mục `## Ảnh hưởng Đ1`, kể cả khi không có kết quả nào
  - Dùng: `mem0-memory` (mcp)
  - Để: `search_memories` với project `TDQWorkflow` về kiểm kê skill / cắt token công cụ,
    nạp skill TRƯỚC bước đỏ. Agent ngoài không có skill system: đọc
    `/Users/truongdinhquoc/.claude/skills/mem0-memory/SKILL.md` rồi làm theo.
  - Ra: 1–3 dòng kết luận trong mục `## Ảnh hưởng Đ1` của file QC
  - Kiểm: mục đó chứa dòng bắt đầu bằng `mem0:` — có kết quả thì ghi fact, không có thì
    ghi `mem0: không có fact liên quan`
  - Không dùng cho: lưu nội dung file, log chạy, hay số đo chi tiết của bản chấm
  - Kết quả: 3 dòng `mem0:` đã ghi vào mục `## Ảnh hưởng Đ1` — có fact xác nhận
    39.722 byte ≈ 9.774 token là chỗ phí lớn nhất, không fact nào cấm đổi giao diện CLI.
- [x] **T3.3** (n5 e15m) Test ĐỎ cho cờ lọc: thêm test vào `tests/test_skill_inventory.py`
  khẳng định `--loc "workflow"` in ra ít dòng hơn mặc định, vẫn còn đủ mọi dòng nguồn
  `project` và `plugin:tdq-workflow`, và dòng cuối nêu số skill bị ẩn kèm lệnh `--tat-ca` —
  Test: `python3 -m pytest tests/test_skill_inventory.py -q` FAIL đúng test mới này
- [x] **T3.4** (n5 e12m) Test ĐỎ khoá hành vi mặc định: chạy không cờ và chạy `--tat-ca`
  đều cho output y hệt baseline T0.1 — Test: `pytest tests/test_skill_inventory.py -q` FAIL
  đúng test mới này
  - Đỏ đã xác nhận: `pytest tests/test_skill_inventory.py -q` → 4 failed, 20 passed —
    3 test `FilterFlagTest` (T3.3) + `test_tat_ca_equals_default_byte_for_byte` (T3.4).
- [x] **T3.5** (n8 e30m) Cài cờ `--loc <từ khoá>` và `--tat-ca` vào `main()` của
  `scripts/skill_inventory.py`, kèm dòng cuối bắt buộc báo số skill bị ẩn và đúng lệnh xem
  đủ — Test: hai test ở T3.3/T3.4 XANH; `python3 scripts/skill_inventory.py --loc "workflow"
  | wc -c` nhỏ hơn `python3 scripts/skill_inventory.py | wc -c`;
  `diff <(python3 scripts/skill_inventory.py) <baseline T0.1>` rỗng
  - Xanh: 24 passed. `--loc "workflow"` = 1.845 byte vs mặc định 39.722 byte (−95,4%);
    diff mặc định và diff `--tat-ca` với baseline T0.1 đều RỖNG. Dòng cuối: ẩn 273 skill.
- [x] **T3.6** (n2 e8m) Đổi dòng lệnh gọi ở `skills/tdq-intake/references/analyze-full.md:7`
  và `skills/tdq-intake/references/skill-inventory.md:10` sang bản có `--loc`, giữ nguyên
  chú "nhắc lại có chủ ý" mà T1.5 đã dán — Test: cả hai file chứa `--loc`; đếm mệnh lệnh
  `analyze-full.md` ≥ 5 và `skill-inventory.md` ≥ 4; `grep -c "nhắc lại có chủ ý"
  skills/tdq-intake/references/skill-inventory.md` ≥ 1
  - Xong: cả hai file có `--loc`; mệnh lệnh 5→6 và 4→6; chú "nhắc lại có chủ ý" còn 1.

**Xong P3 khi**: 2 test mới xanh, `pytest tests/ -q` ≥ 565 passed, `--tat-ca` cho diff rỗng
so với baseline.

## P4 — Log & test bắt buộc

Log: BỎ — task mã duy nhất (Đ1) chỉ thêm một cờ cho script CLI in ra stdout rồi thoát,
không có tiến trình chạy nền để log; thay vào đó dòng cuối bắt buộc của bản lọc chính là
đường báo cho người đọc, đã kiểm ở T3.5.

- [x] **T4.1** (n3 e10m) Unit test cho từng thành phần chạy bằng một lệnh, không hồi quy —
  Test: `python3 -m pytest tests/ -q` ≥ 565 passed, 0 failed
  - Kết quả: **569 passed, 241 subtests passed, 0 failed** (34s).

## P5 — QC & report

- [x] **T5.1** (n5 e20m) Chạy 15 hạng mục QC của spec §6, ghi lệnh + kết quả + phán quyết
  vào `docs/tdq/qc/2026-08-14-ap-goi-day-du.md` — Test: file QC có 15 dòng `| Q`,
  Q1–Q14 đều PASS
  - Kết quả: 15 dòng `| Q` đã ghi; Q1–Q14 PASS (Q2/Q3 PASS theo cách đọc 1A/4A, có ghi rõ
    chỗ chệch tiêu chí chữ ngay dưới bảng).
- [x] **T5.2** (n5 e20m) Q15 — giao sub-agent chạy model hạng thấp làm thử một request nhỏ
  theo bộ skill đã sửa, đối chiếu xem có bỏ bước nào của workflow không — Test: mục
  `## Chạy thử model hạng thấp` trong file QC có kết luận rõ: liệt kê bước bị bỏ, hoặc
  câu "không bỏ bước nào"; không dùng làm cổng chặn
  - Kết quả: model haiku chạy thử → **không bỏ bước nào**; mở đúng file được trỏ tới ở
    Phần B/C của tdq-build thay vì làm theo trí nhớ. Chi tiết ở mục `## Chạy thử model hạng thấp`.
- [x] **T5.3** (n3 e10m) QC độc lập: giao agent `tdq-qc-tester` kiểm lại plan này theo DoD,
  không cho sửa file — Test: agent trả về PASS/FAIL kèm bằng chứng cho từng dòng DoD, kết
  quả dán vào mục `## QC độc lập` của file QC
  - Kết quả: agent tự chạy lại 14 phép kiểm → **PASS Q1–Q14**, trùng phán quyết của T5.1.
    Nêu 3 khiếm khuyết: (a) lúc agent chạy chưa có file report — nay đã có, (b) plan T1.2
    ghi lệch số (đã sửa ở turn này), (c) nhánh "cấm ẩn nguồn `project`" mới chỉ có unit
    test phủ. Bảng verdict dán ở mục `## QC độc lập` của file QC.
- [x] **T5.4** (n2 e8m) Viết report 10–20 dòng và ghi 1 fact mem0 về kết quả áp gói — Test:
  `docs/tdq/reports/2026-08-14-ap-goi-day-du.md` tồn tại, 10–20 dòng, có số token trước/sau
  và số luật trước/sau
  - Kết quả: report 19 dòng, có `8.473 → 7.579 token` và `0/10 dòng luật giảm (7 tăng,
    3 giữ nguyên)`; fact mem0 đã ghi (project TDQWorkflow).

**Xong P5 khi**: Q1–Q14 PASS, Q15 có kết luận, report đã viết, chưa commit.

## Definition of Done

Trỏ về §6 của spec — 15 hạng mục, mỗi dòng một lệnh kiểm:

1. Q1 Đ2: `grep -c "" skills/tdq-intake/SKILL.md` giảm ≥ 20 dòng và `grep -c "^[0-9]\. " skills/tdq-intake/references/quick-lane.md` ≥ 9.
2. Q2 Đ3: `python3 scripts/context_surface.py --quiet | grep "tdq-build/SKILL.md"` cho thân < 1.400 token.
3. Q3 Đ4: `wc -w` ba file conventions bằng đúng mốc T0.1 và `grep -c "^## Phụ lục" skills/tdq-conventions/references/reminder-codes.md` = 1.
4. Q4 Đ5: `grep -cEi "phù hợp|nếu cần|tối ưu|hợp lý|linh hoạt" skills/tdq-intake/references/scope-round.md` = 0.
5. Q5 Đ6: `grep -rl "nhắc lại có chủ ý" skills/ | wc -l` ≥ 8.
6. Q6 Đ7: ``grep -c '^```' agents/tdq-implementer.md agents/tdq-qc-tester.md agents/tdq-reviewer.md`` ≥ 2 mỗi file.
7. Q7 Đ1 lọc nhỏ hơn: `python3 scripts/skill_inventory.py --loc "workflow" | wc -c` < `python3 scripts/skill_inventory.py | wc -c`.
8. Q8 Đ1 giữ hành vi mặc định: `diff <(python3 scripts/skill_inventory.py) <baseline T0.1>` rỗng.
9. Q9 Đ1 có đường xem đủ: chạy `--loc` rồi đọc dòng cuối, phải có số skill bị ẩn và đúng lệnh `--tat-ca`.
10. Q10 không hồi quy: `python3 -m pytest tests/ -q` ≥ 565 passed, 0 failed.
11. Q11 đối chiếu luật: đếm mệnh lệnh theo 10 cụm file của bảng gốc, 0 dòng có "sau" < "trước".
12. Q12 token tầng nạp giảm: `python3 scripts/context_surface.py --quiet` trước/sau, tổng tầng `nạp khi gọi skill` giảm (đích mềm, không ngưỡng số).
13. Q13 không lọt phạm vi: `git status --porcelain -- hooks portable` rỗng.
14. Q14 tài liệu hợp lệ: `python3 scripts/doc_lint.py --pair docs/tdq/spec/2026-08-14-ap-goi-day-du.md docs/tdq/plan/2026-08-14-ap-goi-day-du.md` exit 0.
15. Q15 chạy thử model hạng thấp: mục `## Chạy thử model hạng thấp` trong file QC có kết luận rõ ràng (không phải cổng chặn).
