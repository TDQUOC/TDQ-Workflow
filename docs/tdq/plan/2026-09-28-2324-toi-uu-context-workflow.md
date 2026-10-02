# PLAN — Nạp lười đúng đoạn: cắt token workflow nạp vào phiên

Ngày: 2026-10-02 · Spec: ../spec/2026-09-28-2324-toi-uu-context-workflow.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — đo bằng `tdq_bench.py simulate` trên chính plan này: đội thắng 14,2 phút (55,0 so với 40,8), 27 task chia 7 đợt, giao được 7 task, leader giữ 20 task vì hai vùng nóng `skills/**/*.md` và `scripts/doc_lint.py` — user chốt `main` (inline implement), trái đề xuất đo được
Trạng thái plan: HOÀN THÀNH — 28/29 task; T7.4 (Linux máy thật) để ngỏ vì máy đang tắt,
lý do ghi tại chỗ ở T7.4 và ở Q20 của file QC

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Cổng nhắc đọc lại (M1)
- P2 — Script sinh chỉ mục dòng (M2)
- P3 — Cắt & dời nội dung luật (M4)
- P4 — Tệp khoá token và trần (M3)
- P5 — Bảng bề mặt ở CI (M5)
- P6 — Log & test bắt buộc
- P7 — Đo lại trước/sau và ba hệ
- P8 — Chuẩn bị QC
- Luật file nóng
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]`
   NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. **Số đo nền, chốt trước khi sửa một dòng nào** (để P7 có cái so): sàn tuân thủ lane `full`
   **57.712**; `references/` 43 file **72.680**; `SKILL.md` 9 file **18.857**; ba file vượt trần
   `plan-template` 5.067, `quick-lane` 4.356, `team-mode` 3.652.
8. Phần DỜI nội dung chỉ được **chuyển chỗ**, không được xoá chữ mang luật. P7 đếm số mục
   `##`+`###` trước/sau để chứng minh.

## P1 — Cổng nhắc đọc lại (M1)

- [x] **T1.1** (e25m) Viết `hooks/scripts/read_gate.py`: đọc payload `Read`, ghi mỗi lần đọc vào
  sổ lượt bằng `_common.observe`, và khi gặp lần đọc TRỌN một file đã đọc trong phiên mà `mtime`
  + kích thước không đổi thì in nhắc `[TDQ:DOC]` kèm số token đã tốn — Test:
  `python -m unittest tests.test_read_gate -k nhac` xanh
  - Chạm: `hooks/scripts/read_gate.py`, `tests/test_read_gate.py` → file mới, chưa node nào phụ thuộc
- [x] **T1.2** (e15m) Cổng im lặng ở hai ca: `offset`/`limit` nhắm vùng chưa đọc, và file đã đổi
  (`mtime` hoặc kích thước khác) — Test: `python -m unittest tests.test_read_gate -k im` xanh
  - Chạm: `hooks/scripts/read_gate.py`, `tests/test_read_gate.py`
  - Cần: T1.1
- [x] **T1.3** (e10m) Cổng nhắc đúng MỘT lần cho mỗi file (dùng `_common.already_reminded`), và
  không spawn tiến trình con, không đọc nội dung file được hỏi — Test:
  `python -m unittest tests.test_read_gate -k mot_lan` xanh, có ca khoá "không gọi subprocess"
  - Chạm: `hooks/scripts/read_gate.py`, `tests/test_read_gate.py`
  - Cần: T1.2
- [x] **T1.4** (e12m) Khai cổng vào `hooks/hooks.json` (`PreToolUse` matcher `Read`) và vào bản
  dựng cho host khác — Test: `python -m unittest tests.test_build_portable tests.test_tuong_thich_host`
  xanh, và bản dựng agy sinh ra có khai cổng này
  - Chạm: `hooks/hooks.json`, `scripts/build_portable.py` → `tdq_checkportable.py`, `tdq_codex.py`,
    `tdq_lsp.py`, `tests/probe_codex_hook.py` (nguồn: grep `hooks.json` trong `scripts/`, `tests/`)
  - Cần: T1.3

**Xong P1 khi**: gọi `Read` hai lần cùng một file không đổi thì lượt thứ hai có dòng nhắc; đổi
file hoặc đọc vùng khác thì im lặng.

## P2 — Script sinh chỉ mục dòng (M2)

- [x] **T2.1** (e22m) Viết `scripts/doc_index.py`: quét một file `.md`, sinh khối chỉ mục
  `<!-- muc-luc-dong -->` liệt kê mỗi mục `##`/`###` kèm khoảng dòng, đặt ngay dưới dòng tiêu đề —
  Test: `python -m unittest tests.test_doc_index -k sinh` xanh
  - Chạm: `scripts/doc_index.py`, `tests/test_doc_index.py` → file mới, chưa node nào phụ thuộc
- [x] **T2.2** (e12m) Idempotent: chạy hai lần không sinh hai khối, và cập nhật đúng khoảng dòng
  khi nội dung đã đổi — Test: `python -m unittest tests.test_doc_index -k idempotent` xanh
  - Chạm: `scripts/doc_index.py`, `tests/test_doc_index.py`
  - Cần: T2.1
- [x] **T2.3** (e10m) Phép kiểm chống lệch: một test quét mọi file luật, so chỉ mục với nội dung
  thật, đỏ khi lệch — Test: `python -m unittest tests.test_doc_index -k khop` xanh
  - Chạm: `scripts/doc_index.py`, `tests/test_doc_index.py`
  - Cần: T2.2

**Xong P2 khi**: `python scripts/doc_index.py <file>` sinh chỉ mục đúng, chạy lại không nhân bản.

## P3 — Cắt & dời nội dung luật (M4)

- [x] **T3.1** (e15m) Câu luật tìm kiếm: giữ đúng một bản nguyên văn ở `uu-tien-tim-kiem.md`, 5
  chỗ còn lại thành con trỏ một dòng — Test: `grep -c "Đối tượng tìm là ký hiệu code" skills -r`
  ra đúng 1, và `python -m unittest tests.test_tdq_setup_skill` xanh
  - Chạm: `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/analyze-full.md`,
    `skills/tdq-spec/SKILL.md`, `skills/tdq-plan/SKILL.md`, `skills/tdq-build/SKILL.md`,
    `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `tests/test_tdq_setup_skill.py`
- [x] **T3.2** (e18m) Gỡ 4 câu ép đọc trọn file, thay bằng luật đọc-theo-đoạn (xem chỉ mục dòng
  rồi lấy đúng mục bằng `offset/limit`) — Test: `grep -rn "MUST open" skills` không ra dòng nào
  ép đọc trọn reference, và `python -m unittest tests.test_skill_shape tests.test_skill_lean` xanh
  - Chạm: `skills/tdq-build/SKILL.md`, `skills/tdq-intake/SKILL.md`
  - Cần: T3.1
- [x] **T3.3** (e20m) `plan-template.md` về dưới 3.500: cắt mục lục song ngữ trùng, dời mục "Cụm
  song song" và "Luật file nóng" sang `plan-template-dieu-kien.md` — Test: đo token ≤ 3.500 và số
  mục `##`+`###` của cặp file cộng lại ≥ số mục cũ
  - Chạm: `skills/tdq-plan/references/plan-template.md`,
    `skills/tdq-plan/references/plan-template-dieu-kien.md`
  - Cần: T3.2
- [x] **T3.4** (e18m) `quick-lane.md` về dưới 3.500: dời 3 mục QC và vòng fix sang
  `quick-lane-qc.md` — Test: như T3.3
  - Chạm: `skills/tdq-intake/references/quick-lane.md`, `skills/tdq-intake/references/quick-lane-qc.md`
  - Cần: T3.2
- [x] **T3.5** (e15m) `team-mode.md` về dưới 3.500: dời ví dụ ĐÚNG/SAI và sổ worktree sang
  `team-mode-tra-cuu.md` — Test: như T3.3
  - Chạm: `skills/tdq-build/references/team-mode.md`, `skills/tdq-build/references/team-mode-tra-cuu.md`
  - Cần: T3.2
- [x] **T3.6** (e12m) `spec-template.md` và `uu-tien-tim-kiem.md`: cắt mục lục song ngữ trùng, dời
  phần hạ tầng của luật tìm kiếm (vòng đời Ollama, bảng phụ thuộc, luật hook plugin) sang
  `uu-tien-tim-kiem-ha-tang.md` — Test: `python -m unittest tests.test_luat_4_tang` xanh
  - Chạm: `skills/tdq-spec/references/spec-template.md`,
    `skills/tdq-setup/references/uu-tien-tim-kiem.md`,
    `skills/tdq-setup/references/uu-tien-tim-kiem-ha-tang.md`, `tests/test_luat_4_tang.py`
  - Cần: T3.1
- [x] **T3.7** (e10m) Sinh chỉ mục dòng cho mọi file luật ≥ 2.000 token — Test:
  `python -m unittest tests.test_doc_index -k khop` xanh trên toàn bộ `skills/`
  - Chạm: `skills/tdq-conventions/references/user-facing-block.md`,
    `skills/tdq-build/references/qc.md`, `skills/tdq-build/references/rules/chung.md`,
    `skills/tdq-plan/references/mode-gate.md`, `skills/tdq-build/references/codex-mode.md`,
    `skills/tdq-intake/references/analyze-full.md`, `skills/tdq-conventions/references/bang-lech.md`,
    `skills/tdq-intake/references/scope-round.md`, `skills/tdq-conventions/references/context-budget.md`,
    `skills/tdq-build/references/report-template.md`
  - Cần: T3.3, T3.4, T3.5, T3.6

- [x] **T3.8** (e12m) `scope-round.md` ra khỏi tập BẮT BUỘC: nói rõ trong `tdq-intake/SKILL.md`
  rằng file này chỉ đọc khi thực sự chạy vòng hỏi phạm vi — vòng đó tự nó đã là có điều kiện —
  Test: sàn tuân thủ giảm đúng 2.066 token, và `test_reference_mot_tang` vẫn xanh
  - Chạm: `skills/tdq-intake/SKILL.md`
  - Cần: T3.7
- [x] **T3.9** (e15m) `user-facing-block.md`: dời `Examples` + `Before/Sau` + `The symbols allowed`
  (965 token) sang file em tầng 1 — Test: file còn ≤ 2.200 token, và
  `python -m unittest tests.test_user_facing_block` xanh
  - Chạm: `skills/tdq-conventions/references/user-facing-block.md`,
    `skills/tdq-conventions/references/user-facing-block-vi-du.md`, `skills/tdq-conventions/SKILL.md`
  - Cần: T3.8

**Vì sao thêm hai task này sau khi plan đã duyệt** (2026-10-02): số đo ở T7.1 làm sớm cho ra sàn
54.015, thiếu 1.515 so với tiêu chí Q17. User chốt phương án A — cắt thêm cho đủ con số đã cam kết,
không sửa thước đo giữa cuộc. Hai task này là phần cắt thêm đó, đã đo trước: −2.066 và −965.

**Xong P3 khi**: ba file vượt trần đều ≤ 3.500 token, không mục luật nào mất, mọi file dài có chỉ mục.

## P4 — Tệp khoá token và trần (M3)

- [x] **T4.1** (e20m) Viết `scripts/token_budget.py`: đo token mọi file `skills/**/*.md` bằng
  tokenizer thật, ghi `docs/tdq/token-budget.json` gồm `{đường dẫn: {token, sha256}}` — Test:
  `python -m unittest tests.test_token_budget_lock -k sinh` xanh, sinh hai lần ra cùng nội dung
  - Chạm: `scripts/token_budget.py`, `docs/tdq/token-budget.json`, `tests/test_token_budget_lock.py`
    → file mới, chưa node nào phụ thuộc
  - Cần: T3.7
- [x] **T4.2** (e18m) `doc_lint` thêm rule trần token: đọc tệp khoá, so `sha256` để biết số đo còn
  đúng, báo lỗi khi file vượt 3.500 token hoặc khi khoá đã cũ — chạy được KHÔNG cần tokenizer —
  Test: `python -m unittest tests.test_doc_lint -k tran_token` xanh, gồm ca không có tokenizer
  - Chạm: `scripts/doc_lint.py`, `tests/test_doc_lint.py` → `tdq_finish.py`, `token_audit.py`,
    `tests/test_bench.py`, `tests/test_skill_lean.py`, `tests/test_skill_shape.py`,
    `tests/test_tdq_finish.py` (nguồn: grep `doc_lint` trong `scripts/`, `hooks/`, `tests/`)
  - Cần: T4.1
- [x] **T4.3** (e10m) `tdq_finish` sinh lại tệp khoá khi có file `.md` của `skills/` đổi, để khoá
  không bao giờ cũ một cách im lặng — Test: `python -m unittest tests.test_tdq_finish -k khoa` xanh
  - Chạm: `scripts/tdq_finish.py`, `tests/test_tdq_finish.py`
  - Cần: T4.2

**Xong P4 khi**: `doc_lint` đỏ khi một file reference vượt trần, và đỏ khi tệp khoá cũ.

## P5 — Bảng bề mặt ở CI (M5)

- [x] **T5.1** (e10m) Thêm một bước vào `.github/workflows/test.yml` chạy `context_surface.py` và
  in bảng; bước này KHÔNG được làm đỏ build — Test: bước có `continue-on-error: true` và lệnh đúng
  - Chạm: `.github/workflows/test.yml`
  - Cần: T4.3

## P6 — Log & test bắt buộc

- [x] **T6.1** (e12m) Log service của ba file mới: timestamp, đủ chi tiết debug, tắt được bằng
  `TDQ_LOG=0` như mọi script khác của repo — Test: ba lệnh
  `python -m unittest discover tests -p "test_read_gate.py" -k log` (và `test_doc_index.py`,
  `test_token_budget_lock.py`) xanh. Dạng `discover` chứ không phải dạng chấm
  `tests.test_read_gate`: `tests/` cố ý KHÔNG là package (mọi test `from helper import ROOT`),
  nên dạng chấm không nạp được `helper` — chính là lỗi gặp khi chạy thử câu Test gốc.
  - Chạm: `hooks/scripts/read_gate.py`, `scripts/doc_index.py`, `scripts/token_budget.py`
  - Cần: T5.1
- [x] **T6.2** (e15m) Trọn bộ test chạy bằng một lệnh và xanh — Test:
  `python -m unittest discover -s tests -q`
  - Cần: T6.1

## P7 — Đo lại trước/sau và ba hệ

- [x] **T7.1** (e15m) Đo lại sàn tuân thủ lane `full` và tổng `references/`, so với số nền ở quy
  tắc 7 — Test: sàn ≤ **52.500** token (trước 57.712); nếu KHÔNG đạt thì hoàn tác phần dời theo
  đúng mục rủi ro số 1 của spec
  - Cần: T6.2
- [x] **T7.2** (e8m) Đếm số mục `##`+`###` của toàn vùng `skills/` trước và sau — Test: số sau ≥
  số trước (chứng minh chỉ DỜI, không xoá luật)
  - Cần: T7.1
- [x] **T7.3** (e10m) Chạy trọn bộ test trên Windows — Test:
  `python -m unittest discover -s tests -q` không fail, không error
  - Cần: T7.2
- [ ] **T7.4** (e12m) Chạy trọn bộ test trên máy Linux thật, thư mục tạm, xoá sạch sau khi đo —
  Test: không fail không error, và sau khi đo không gói nào được cài
  - Cần: T7.3
  - **CHẶN 2026-10-02 17:4x**: máy Linux `tdq-nuc12dcmv7` (100.67.252.79) đang TẮT —
    `tailscale status` ghi "offline, last seen 2h ago", ssh port 22 timeout. Trong tailnet còn
    `vps-tdq` đang bật, nhưng user đã chốt chỉ được dùng ĐÚNG hai máy này để thử môi trường, nên
    không mượn máy khác. Phần Linux còn job `ubuntu-latest` × 2 bản Python ở CI che, nhưng đó là
    máy sạch của GitHub chứ không phải máy thật của user — task này mở lại khi máy bật.
- [x] **T7.5** (e12m) Chạy trọn bộ test trên máy macOS thật bằng python của pyenv/brew theo đường
  dẫn tuyệt đối — Test: không fail không error, không chạm python hệ thống của Apple
  - Cần: T7.3

**Xong P7 khi**: sàn tuân thủ ≤ 52.500, số mục luật không giảm, ba hệ xanh.

## P8 — Chuẩn bị QC

- [x] **T8.1** (e12m) Soát lỗi đúng-sai trên toàn bộ thay đổi — Test: mọi phát hiện được xử lý
  hoặc ghi lý do bác bỏ vào file QC
  - Dùng: `code-review`
  - Để: tìm lỗi đúng-sai ở ba file mã mới và ở rule mới của `doc_lint`, nạp skill TRƯỚC khi mở
    phase qc. Agent ngoài không có skill system: đọc `SKILL.md` của skill đó rồi làm theo.
  - Ra: danh sách phát hiện kèm phán quyết, trong `docs/tdq/qc/<slug>.md`
  - Kiểm: mục QC của file đó có ít nhất một dòng cho mỗi phát hiện
  - Không dùng cho: việc rút gọn code — đó là T8.2
  - Cần: T7.5
- [x] **T8.2** (e10m) Rút gọn phần trùng lặp sau khi 5 module xong — Test: trọn bộ test vẫn xanh
  - Dùng: `simplify`
  - Để: gỡ trùng lặp trong mã mới viết, nạp skill TRƯỚC khi sửa. Agent ngoài không có skill
    system: đọc `SKILL.md` của skill đó rồi làm theo.
  - Ra: mã đã rút gọn, không đổi hành vi
  - Kiểm: `python -m unittest discover -s tests -q`
  - Không dùng cho: việc săn lỗi đúng-sai — đó là T8.1
  - Cần: T8.1

## Luật file nóng

Hai vùng nóng, xử theo cách **nâng lên đợt sớm**:

- `skills/**/*.md` bị **7 task** chạm (T3.1–T3.7). T3.1 (dedup câu luật) và T3.2 (gỡ câu ép đọc)
  chạy TRƯỚC để các file ổn định, rồi T3.3–T3.6 mới dời mục, và T3.7 sinh chỉ mục sau cùng — vì
  chỉ mục phụ thuộc số dòng cuối cùng.
- `scripts/doc_lint.py` bị **1 task** chạm nhưng có **6 file test đọc nó**; T4.2 phải chạy sau khi
  tệp khoá đã tồn tại (T4.1), nếu không mọi test đọc `doc_lint` sẽ đỏ hàng loạt.

## Cụm song song

Ba cụm không giao nhau về file:

- Cụm A: `hooks/scripts/read_gate.py` + `hooks/hooks.json` + `build_portable.py` (P1)
- Cụm B: `scripts/doc_index.py` (P2)
- Cụm C: `skills/**/*.md` (P3)

Cụm A và B độc lập hoàn toàn và chạy song song được. Cụm C phải đi sau B (cần script sinh chỉ mục)
và P4 phải đi sau C (khoá token chỉ đúng khi nội dung đã chốt).

`simulate` đã chạy trên chính plan này và nói: **7 đợt, giao được 7 task, leader giữ 20**. Con số
20-giữ-lại khớp đúng với mục "Luật file nóng" ở trên — 7 task cùng chạm `skills/**/*.md` thì không
worktree nào cứu được. Đội vẫn thắng 14,2 phút vì leader làm việc của mình trong lúc 7 task kia
chạy (19,3 phút làm xen kẽ), không phải vì chia được nhiều.

## Definition of Done

Lệnh dạng chấm (`python -m unittest tests.test_x`) KHÔNG chạy được: `tests/` cố ý không là
package, nên `from helper import ROOT` không nạp được. Mọi lệnh dưới đây là dạng `discover`,
đúng cách repo vẫn chạy — sửa sau khi chạy thử thật, không sửa cho đẹp.

- [x] Q1 Cổng nhắc khi đọc lại — `python -m unittest discover tests -p test_read_gate.py -k nhac`
- [x] Q2 Cổng im lặng khi đọc vùng khác — `… -p test_read_gate.py -k im_vung`
- [x] Q3 Cổng im lặng khi file đã đổi — `… -p test_read_gate.py -k im_doi`
- [x] Q4 Cổng không spawn tiến trình, không đọc nội dung file — `… -p test_read_gate.py -k nhe`
- [x] Q5 Cổng được cắm đủ mọi host — `… -p test_build_portable.py` (32 ca) + bản agy dựng thật có
  `hooks/scripts/read_gate.py` và `_common.py`
- [x] Q6 Sinh chỉ mục idempotent — `… -p test_doc_index.py -k Idempotent`
- [x] Q7 Chỉ mục đúng khoảng dòng — `… -p test_doc_index.py -k Khop` + `doc_index.py --kiem
  --tat-ca` thoát 0
- [x] Q8 Chỉ mục có mặt đủ — `… -p test_doc_index.py -k CoMat`; 14/14 file ≥ 2.000 token có khối
- [x] Q9 Tệp khoá sinh lại được — `… -p test_token_budget_lock.py -k sinh`
- [x] Q10 Trần token cưỡng chế được — `… -p test_token_budget_lock.py -k tran_token` (rule R13
  nằm ở `doc_lint`, test của nó ở file khoá token)
- [x] Q11 Khoá cũ bị bắt — `… -p test_token_budget_lock.py -k khoa_cu`
- [x] Q12 Ba file về dưới trần — `python scripts/token_budget.py --kiem` thoát 0; max 3.493
- [x] Q13 Không mục luật nào bị mất — đếm `##`+`###` toàn `skills/`: 334 → 342
- [x] Q14 Bốn câu ép đọc trọn file đã gỡ — `grep -rn "MUST open" skills` → 0 dòng
- [x] Q15 Câu luật tìm kiếm một bản — đếm nguyên văn trên `skills/` = 1
- [x] Q16 Mục lục trùng đã cắt — đo lại: không có mục lục trùng nào để cắt (cái thứ hai nằm
  TRONG fence khuôn mẫu), xem Q16 ở file QC
- [x] Q17 Sàn tuân thủ giảm — đo bằng tokenizer thật trên danh sách file bắt buộc đọc của lane
  `full`, bản TRƯỚC lấy từ `git show HEAD:`: 55.439 → **49.531** ≤ 52.500. KHÔNG dùng
  `skill_tokens.py --theo-phase`: nó in CEILING (81.913, gộp mọi reference) và `--project` của nó
  chỉ áp cho `--mo-ta`, nên không so được trước/sau
- [x] Q18 CI in bảng — bước `context_surface` có trong `.github/workflows/test.yml` kèm
  `continue-on-error: true`; `… -p test_ci_matrix.py` khoá cả hai
- [x] Q19 Ràng buộc kiến trúc — `grep -rn "^import hooks\|from hooks" scripts` → 0 dòng
- [ ] Q20 Ba hệ — Windows `Ran 2141 OK` · macOS pyenv 3.13.15 và brew 3.14.7 `Ran 2101 OK` ·
  **Linux CHƯA**: máy thật đang tắt (xem ghi chú CHẶN ở T7.4)
