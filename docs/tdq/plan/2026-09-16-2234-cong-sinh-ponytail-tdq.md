# PLAN — Nội hoá luật Ponytail vào ruột TDQ-Workflow

Ngày: 2026-09-17 · Spec: ../spec/2026-09-16-2234-cong-sinh-ponytail-tdq.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — `tdq_bench.py simulate` đo trên chính plan này: 16 task, 3 đợt, đội 20.4 phút so với main 32.6 phút, `Winner: đội` cách 12.2 phút ở hệ số agent 1.5 (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT (2026-09-17, "duyệt plan" · mode `subagent` do user chốt bằng "A")

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Thân luật tinh gọn
- P2 — Nền cơ chế: bộ đọc-lọc + khoá mức gắt
- P3 — Ba kênh nạp luật
- P4 — Skill soi over-engineer + cổng nợ marker
- P5 — Log & test bắt buộc
- P6 — Bản ngoài + hồ sơ kiến trúc
- Cụm song song
- Luật file nóng
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau. "Xanh" ở repo này
   nghĩa là **tập tên test đỏ lệch 0 so với baseline `main` sạch** (294 đỏ là nợ cũ, spec §5).
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. **Phán quyết 1 của user:** phép kiểm viết thêm là MỘT lệnh chạy được, không dựng framework
   mới, không dựng fixture. Test đi vào `unittest` có sẵn của repo là được, nhưng không tạo
   thư mục fixture, không tạo file dữ liệu mẫu.
8. **Phán quyết 2 của user:** không task nào được miễn unit test, kể cả task một dòng.
9. **Món 8 của user:** làm cho chạy trước, refactor sau. Hàm thuần, không class mới, không
   namespace mới. Mọi hàm mới nằm trong sàn `cyclomatic ≤ 10 / cognitive ≤ 15`.
10. **Sửa khuôn lệnh test ngày 2026-09-17 — LỖI PLAN của tôi, không phải đổi ý.** Mọi dòng
    `Test:` trong plan bản đầu viết `python3 -m unittest tests.test_x`. Khuôn đó KHÔNG chạy
    được ở repo này: `tests/` không có `__init__.py` và `tests/helper.py` được import phẳng,
    nên lệnh đó luôn ra `ModuleNotFoundError: No module named 'helper'`. Đã đổi 19 chỗ sang
    `(cd tests && python3 -m unittest test_x -v)` — đúng cách repo đang chạy. Dòng DoD
    `python3 -m unittest discover tests` giữ nguyên vì nó vẫn chạy được.
11. **Nợ test có sẵn, không thuộc lượt này:** `test_rules_library.ChiMuc.test_chi_muc` đỏ vì
    `skills/tdq-build/references/rules/index.md` nhắc `bash.md` trong khi danh sách 10 file
    không có file đó. Đo trước khi tôi sửa gì trong lượt này; cố ý không sửa.

## P1 — Thân luật tinh gọn

- [x] **T1.1** (e20m) Viết thân luật tinh gọn vào hai chỗ theo `soul.md:99`: câu luật tầng 1–2
      (bậc 1 "đừng xây thứ chưa cần" + món 8 "chạy trước, refactor sau") vào **thân**
      `skills/tdq-build/SKILL.md`; bảng 7 bậc + bộ rule gọn + ví dụ RIGHT/WRONG vào
      `skills/tdq-build/references/rules/chung.md`, **bọc giữa cặp marker**
      `<!-- luat-gon:bat-dau -->` … `<!-- luat-gon:ket-thuc -->`. Nguồn dự thảo tiếng Anh:
      `docs/tdq/knowledge/2026-09-16-1447-du-thao-luat-ponytail.md`, bổ sung món 8 còn thiếu.
      Vượt trần dòng của skill thì **nâng trần** (`soul.md:101`), cấm nén luật cho vừa.
      — Test: `python3 scripts/i18n_check.py skills/tdq-build/SKILL.md skills/tdq-build/references/rules/chung.md` exit 0, và `python3 scripts/doc_lint.py skills/tdq-build/references/rules/chung.md` exit 0
  - Chạm: `skills/tdq-build/SKILL.md`, `skills/tdq-build/references/rules/chung.md` → luật tầng `skills/`, node đọc là `build_portable.py` (T6.1) và `luat_gon.py` (T2.1)
  - **Mở rộng `Chạm:` ngày 2026-09-17, lý do là số đo chứ không phải đổi ý** — thêm
    `scripts/doc_lint.py` và `tests/test_rules_library.py`: viết xong thân luật thì `SKILL.md`
    ra 160 dòng (trần `doc_lint.py:46` là 150) và `chung.md` ra 221 dòng (trần
    `tests/test_rules_library.py:62` là 150). Đây đúng tình huống `soul.md:101` đã phán trước:
    trần dòng là ràng buộc tầng 3, chạm trần thì **nâng trần**, cấm nén luật tầng 1–2 cho vừa.
    Nâng kèm ghi chú lý do + ngày tại chỗ, không nâng trần của 9 file rule còn lại.
  - **Nợ có sẵn phát hiện tại T1.1, đã sửa trong vùng:** `i18n_check.py` đỏ 3 dòng ở
    `skills/tdq-build/SKILL.md` TRƯỚC khi tôi sửa gì (đo bằng `git show HEAD:` rồi quét) — câu
    luật LSP dài 4 dòng nhưng marker `i18n-allow` chỉ đậu 1 dòng, mà `i18n_check.py:137` xét
    marker theo TỪNG dòng. Sửa bằng cách đóng marker cho 3 dòng tiếp, không đổi một chữ nào của
    câu luật. Cùng khuôn lỗi này còn ở các skill khác — ghi nợ, không sửa ngoài vùng.
- [>] **T1.2** (e8m) Test khoá hình dạng thân luật: khối giữa cặp marker tồn tại, chứa đúng 7
      bậc theo thứ tự, và chứa câu món 8; câu luật tầng 1–2 nằm trong thân `SKILL.md` chứ không
      trong reference. — Test: `(cd tests && python3 -m unittest test_than_luat -v)` xanh
  - Chạm: `tests/test_than_luat.py` → file mới, chưa node nào phụ thuộc
  - Cần: T1.1

**Xong P1 khi**: `i18n_check` exit 0 trên cả hai file, `tests.test_than_luat` xanh, và khối
marker đếm được đúng 7 bậc.

## P2 — Nền cơ chế: bộ đọc-lọc + khoá mức gắt

- [x] **T2.1** (e18m) Tạo `hooks/scripts/luat_gon.py` — **hai hàm thuần, không class**:
      `doc_than_luat(goc)` đọc khối giữa cặp marker của T1.1 (thiếu marker → trả chuỗi rỗng và
      một dòng cảnh báo, không ném lỗi), và `loc_than_luat(than, muc_gat)` lọc theo mức: `full`
      giữ đủ 7 bậc, `lite` cắt bảng cường độ và ví dụ, `ultra` giữ tất cả cộng dòng gắt thêm,
      `off` trả rỗng; mức lạ / rỗng / `None` đều trả về y như `full` (fail-closed).
      — Test: `(cd tests && python3 -m unittest test_luat_gon -v)` xanh, phủ cả 4 mức, mức lạ, và trường hợp thiếu marker
  - Chạm: `hooks/scripts/luat_gon.py`, `tests/test_luat_gon.py` → file mới; node sẽ đọc: `session_start.py` (T3.1), `subagent_start.py` (T3.3)
  - Cần: T1.1
- [~] **T2.2** (e18m) Thêm khoá `muc_gat` vào `scripts/tdq_state.py`: bốn giá trị
      `lite|full|ultra|off`, mặc định `full` khi khoá trống, giá trị lạ về `full`; đọc/ghi qua
      `tdq_state.py set muc_gat=<giá trị>`; phơi giá trị hiện tại trên mặt trạng thái để user
      thấy mình đang ở mức nào. Đây là **chủ ghi duy nhất** của `scripts/tdq_state.py` trong
      plan này. — Test: `(cd tests && TDQ_PROJECT_DIR=$(mktemp -d) python3 -m unittest test_state_muc_gat -v)` xanh
  - Chạm: `scripts/tdq_state.py`, `tests/test_state_muc_gat.py` → node bị ảnh hưởng: mọi hook đọc state qua `load()`
  - Dùng: `tdq-status`
  - Để: đặt `muc_gat` vào đúng chỗ trên mặt trạng thái user đọc, không dựng mặt hiển thị thứ hai.
    Agent ngoài không có skill system: đọc `skills/tdq-status/SKILL.md` rồi làm theo.
  - Ra: dòng mức gắt hiện ra trong đầu ra `tdq_state.py next` và trong `docs/tdq/STATE.md`
  - Kiểm: `python3 scripts/tdq_state.py next` in ra mức gắt hiện tại, exit 0
  - Không dùng cho: đổi khuôn bảng phase, đổi dòng `[TDQ:NEXT]`, hay thêm khoá state nào khác

**Xong P2 khi**: `tests.test_luat_gon` và `tests.test_state_muc_gat` xanh; `set muc_gat=off` rồi
`next` đọc lại ra `off`; `set muc_gat=xyz` ra `full`.

## P3 — Ba kênh nạp luật

- [ ] **T3.1** (e22m) Mở rộng `hooks/scripts/session_start.py`: sau khối đầu (dòng luật tuân
      thủ + khối `next`) chèn thêm **khối thân luật** đã lọc theo `muc_gat`, và ghi một dòng log
      kênh. Giữ **nguyên số** trần khối đầu 12 dòng / 600 ký tự; khai trần mới cho toàn đầu ra
      140 dòng / 7000 ký tự. Sửa **ba assertion** đang đo `len(out) <= 600` trên toàn đầu ra
      thành đo trên khối đầu, mỗi chỗ ghi chú lý do + ngày 2026-09-17 tại dòng sửa.
      — Test: `(cd tests && python3 -m unittest test_context_hooks test_token_budget -v)` xanh, có ca `source=compact`, `startup`, `resume`
  - Chạm: `hooks/scripts/session_start.py`, `tests/test_context_hooks.py`, `tests/test_token_budget.py` → node bị ảnh hưởng: sự kiện `SessionStart` của mọi phiên
  - Cần: T2.1, T2.2
  - Dùng: `tdq-lsp-setup` (mcp)
  - Để: dựng dòng `Chạm:` của ba task P3 bằng `find_references` trên ký hiệu bị sửa, vì lần
    grep hẹp ở phase analyze trượt trọn 9 ref trong `hooks/`. Nạp skill TRƯỚC bước đỏ. Agent
    ngoài không có skill system: đọc `skills/tdq-lsp-setup/SKILL.md` rồi làm theo.
  - Ra: danh sách ref thật của `render_next`, `trim`, `remind` ghi vào dòng `Chạm:` của T3.1–T3.3
  - Kiểm: `python3 scripts/tdq_lsp.py check` 7/7 ĐẠT, và mỗi đường dẫn trong `Chạm:` mở được
  - Không dùng cho: cài thêm LSP server, sửa file của plugin khác, đổi cấu hình import root
- [ ] **T3.2** (e16m) Thêm mã thứ sáu `TDQ:GON` vào danh sách mã ĐÓNG ở `hooks/scripts/_common.py`
      (spec §5 đã khai trước, đúng luật ở `hooks/scripts/_common.py:70`), rồi cho
      `hooks/scripts/prompt_context.py` in dòng nhắc ngắn đó **chỉ khi** phase là `implement`,
      trong trần 3 dòng / 200 ký tự, kèm một dòng log kênh. Không đọc thân luật ở kênh này —
      `UserPromptSubmit` chia ngân sách 30s.
      — Test: `(cd tests && python3 -m unittest test_prompt_context test_common -v)` xanh, có ca phase khác không in mã
  - Chạm: `hooks/scripts/_common.py`, `hooks/scripts/prompt_context.py`, `tests/test_prompt_context.py`, `tests/test_common.py` → node bị ảnh hưởng: mọi hook import `_common`
  - Cần: T2.2
- [ ] **T3.3** (e20m) Tạo `hooks/scripts/subagent_start.py` và khai vào `hooks/hooks.json` —
      sự kiện thứ năm `SubagentStart`, chèn thân luật đã lọc vào đầu hội thoại sub-agent, kèm
      một dòng log kênh. Payload thiếu khoá → in rỗng và **thoát mã 0** (fail-open, không chặn
      lượt). Docstring ghi thẳng: đây là **lời nhắc, không phải hàng rào** — `additionalContext`
      của sub-agent bị prune, non-compliance đo được 40–60%.
      — Test: `(cd tests && python3 -m unittest test_subagent_start -v)` xanh, có ca payload thiếu khoá và ca `muc_gat=off`
  - Chạm: `hooks/scripts/subagent_start.py`, `hooks/hooks.json`, `tests/test_subagent_start.py` → `hooks.json` lên 6 mục trên 5 sự kiện
  - Cần: T2.1, T2.2
- [ ] **T3.4** (e12m) Chống chèn hai lần: mỗi kênh dedupe theo lượt, dùng lại cơ chế đã có ở
      `already_reminded` chứ không viết cơ chế thứ hai — bug #10871 làm hook plugin chạy hai lần
      với hai PID. — Test: `(cd tests && python3 -m unittest test_kenh_luat_dedupe -v)` xanh: gọi hook hai lần cùng một lượt thì thân luật xuất hiện **đúng một lần**
  - Chạm: `tests/test_kenh_luat_dedupe.py` → file mới; phần sửa mã nằm trong T3.1–T3.3 theo luật file nóng
  - Cần: T3.1, T3.2, T3.3

**Xong P3 khi**: chạy thật cả ba hook bằng payload giả thấy thân luật trong đầu ra (kênh phiên
có ca `source=compact`); `hooks.json` đọc được bằng máy và khai 6 mục / 5 sự kiện; thân luật
xuất hiện đúng một lần mỗi lần nạp.

## P4 — Skill soi over-engineer + cổng nợ marker

- [ ] **T4.1** (e16m) Tạo `skills/tdq-lean/SKILL.md` — một skill, ba chế độ, viết tiếng Anh theo
      `docs/kien-truc.md:51`: `review` soi diff, `audit` soi cả repo, `debt` gom marker
      `ponytail:` thành sổ nợ và đánh dấu marker **không có đường nâng** là nợ thối. Frontmatter
      khai `argument-hint: "[review|audit|debt]"`. Nội dung prompt vay từ ba command
      `~/Documents/ponytail/commands/`, KHÔNG vay `/ponytail-gain`.
      — Test: `(cd tests && python3 -m unittest test_skill_lean -v)` xanh: ba mục chế độ có đủ, `argument-hint` khai đúng ba chế độ, `python3 scripts/i18n_check.py skills/tdq-lean/SKILL.md` exit 0
  - Chạm: `skills/tdq-lean/SKILL.md`, `tests/test_skill_lean.py` → file mới; node đọc: `build_portable.py` (T6.1), chỉ mục skill (T6.3)
- [x] **T4.2** (e18m) Tạo `scripts/kiem_no_marker.py` — **một lệnh chạy được, không framework,
      không fixture**: quét comment `ponytail:` trong `scripts/` và `hooks/`, marker nào thiếu
      đường nâng thì in `đường-dẫn:dòng` và thoát mã khác 0; đủ đường nâng thì mã 0. Ghi một
      dòng log có timestamp.
      — Test: `(cd tests && python3 -m unittest test_kiem_no_marker -v)` xanh (ca thiếu / ca đủ, dựng bằng thư mục tạm chứ không bằng fixture trong repo), và `python3 scripts/kiem_no_marker.py` trên repo hiện tại exit 0
  - Chạm: `scripts/kiem_no_marker.py`, `tests/test_kiem_no_marker.py` → file mới, chưa node nào phụ thuộc

**Xong P4 khi**: `tests.test_skill_lean` và `tests.test_kiem_no_marker` xanh; `kiem_no_marker.py`
trên repo hiện tại exit 0.

## P5 — Log & test bắt buộc

- [ ] **T5.1** (e12m) Khoá log service của ba kênh: mỗi kênh mỗi lần chạy ghi **một dòng** vào
      sổ lượt có sẵn (`turn_log_append`) với timestamp, tên kênh, mức gắt, số dòng luật đã chèn;
      `muc_gat=off` thì không dòng nào. Việc GHI đã gộp vào T3.1–T3.3 theo luật file nóng; task
      này viết phép kiểm. Không dựng sổ log thứ hai.
      — Test: `(cd tests && TDQ_PROJECT_DIR=$(mktemp -d) python3 -m unittest test_log_kenh_luat -v)` xanh
  - Chạm: `tests/test_log_kenh_luat.py` → file mới, chưa node nào phụ thuộc
  - Cần: T3.1, T3.2, T3.3
- [ ] **T5.2** (e10m) Đối chiếu hiệu ứng thật của state và hook: mức gắt ghi trong state đúng
      bằng mức mà hook thật nhận được, đo bằng cách đọc đĩa trực tiếp rồi chạy hook.
      — Test: `python3 scripts/tdq_state.py set muc_gat=lite` rồi chạy `session_start.py` thấy số dòng luật ít hơn ca `full`
  - Dùng: `tdq-check-status`
  - Để: đọc `docs/tdq/state.json` trực tiếp để đối chiếu với giá trị hook nhận được, thay vì
    tin dòng khai. Agent ngoài không có skill system: đọc `skills/tdq-check-status/SKILL.md` rồi làm theo.
  - Ra: một bảng 4 dòng (4 mức gắt) ghi số dòng luật hook thật in ra, dán vào file QC
  - Kiểm: bốn mức cho bốn số dòng khác nhau, `off` ra 0
  - Không dùng cho: ghi vào state (chỉ `scripts/tdq_state.py` được ghi — `docs/kien-truc.md:25`)
  - Cần: T3.1, T2.2
- [ ] **T5.3** (e10m) Chạy toàn bộ suite **đúng một lần** và đối chiếu baseline `main` sạch:
      tập tên test đỏ lệch 0 cả hai chiều. — Test: `python3 -m unittest discover tests` trên nhánh và trên worktree `main`, so hai tập tên test đỏ
  - Cần: T4.1, T4.2, T5.1

## P6 — Bản ngoài + hồ sơ kiến trúc

- [ ] **T6.1** (e10m) Sinh lại bản ngoài bằng `python3 scripts/build_portable.py` — cấm sửa tay
      (`docs/kien-truc.md:13`). — Test: `git status --porcelain portable_claude portable_codex` có thay đổi, và grep thấy thân luật mới trong cả hai bản
  - Chạm: `portable_claude/`, `portable_codex/` → bản SINH, node nguồn là `skills/`+`hooks/`+`agents/`+`scripts/`
  - Cần: T1.1, T3.1, T3.2, T3.3, T4.1
- [ ] **T6.2** (e5m) Cập nhật `docs/kien-truc.md`: dòng hook đổi từ "5 hook" sang "6 hook trên 5
      sự kiện", và thêm một dòng lịch sử ngày 2026-09-17 ghi việc nội hoá luật. — Test: `grep -c '6 hook' docs/kien-truc.md` ra ≥ 1 và `python3 scripts/doc_lint.py docs/kien-truc.md` exit 0
  - Cần: T3.3
- [ ] **T6.3** (e8m) Dựng lại chỉ mục skill để `tdq-lean` có mặt. — Test: `python3 scripts/skill_router.py --dung-kho` rồi grep `tdq-lean` trong `docs/tdq/audit/skill-index.json` ra ≥ 1
  - Cần: T4.1

**Xong P6 khi**: hai bản portable chứa thân luật mới và không có dấu sửa tay; `kien-truc.md`
ghi 6 hook; `tdq-lean` có trong chỉ mục.

## Cụm song song

Bốn cụm, cắt theo FILE chứ không theo bước thời gian:

| Cụm | Task | Vì sao chạy cùng được |
|---|---|---|
| C1 | T1.1 → T1.2 | Một chuỗi, cùng chạm hai file luật. Không chia được, và là nền của C2 |
| C2 | T2.1 ∥ T2.2 | `hooks/scripts/luat_gon.py` và `scripts/tdq_state.py` không giao nhau |
| C3 | T3.1 ∥ T3.2 ∥ T3.3, rồi T3.4 | Ba kênh, ba vùng file rời: `session_start.py`+2 test · `_common.py`+`prompt_context.py`+2 test · `subagent_start.py`+`hooks.json`+1 test. T3.4 chờ cả ba |
| C4 | T4.1 ∥ T4.2 | Skill markdown và script quét marker, không giao nhau; cũng không giao C2/C3 nên chạy được sớm |

Trần tốc độ của mode đội = **3 task song song** (cụm C3). P5 và P6 là cổ chai cố ý: chúng đọc
đầu ra của mọi cụm trước, nên `Cần:` khai đầy đủ để máy không phát sớm.

## Luật file nóng

`scripts/tdq_state.py` và ba file hook của P3 là file nóng thật. Xử theo cách **một chủ ghi
duy nhất**, không có cách thứ ba:

- `scripts/tdq_state.py` → chủ ghi duy nhất là **T2.2**. T5.2 chỉ ĐỌC qua CLI.
- `hooks/scripts/session_start.py` → chủ ghi **T3.1**. T3.4 và T5.1 chỉ thêm file test.
- `hooks/scripts/prompt_context.py`, `hooks/scripts/_common.py` → chủ ghi **T3.2**.
- `hooks/scripts/subagent_start.py`, `hooks/hooks.json` → chủ ghi **T3.3**.
- `skills/tdq-build/SKILL.md`, `skills/tdq-build/references/rules/chung.md` → chủ ghi **T1.1**.

Dòng log của ba kênh (T5.1) vì thế **không** tách thành task sửa mã riêng — nó được viết ngay
trong T3.1–T3.3, và T5.1 chỉ giữ phép kiểm.

## Definition of Done

Trỏ về §6 của spec, 13 hạng mục:

- [ ] Q1 Thân luật đủ 7 bậc + món 8, chia đúng hai chỗ theo `soul.md:99` — `(cd tests && python3 -m unittest test_than_luat)` xanh và `python3 scripts/i18n_check.py skills/tdq-build/SKILL.md skills/tdq-build/references/rules/chung.md` exit 0
- [ ] Q2 Bộ lọc: 4 mức ra 4 kết quả, `off` rỗng, mức lạ về `full` — `(cd tests && python3 -m unittest test_luat_gon)` xanh
- [ ] Q3 Kênh phiên chèn thật kể cả sau compact, trần khối đầu 12/600 giữ nguyên, toàn đầu ra ≤ 140/7000 — `(cd tests && python3 -m unittest test_context_hooks test_token_budget)` xanh
- [ ] Q4 Dòng nhắc ngắn chỉ ở phase `implement`, ≤ 3 dòng/200 ký tự, danh sách mã đúng 6 mã — `(cd tests && python3 -m unittest test_prompt_context test_common)` xanh
- [ ] Q5 Kênh sub-agent in thân luật, `hooks.json` 6 mục/5 sự kiện, payload thiếu khoá vẫn mã 0 — `(cd tests && python3 -m unittest test_subagent_start)` xanh
- [ ] Q6 Khoá `muc_gat` đọc/ghi qua CLI, mặc định và mọi đường lỗi ra `full` — `(cd tests && TDQ_PROJECT_DIR=$(mktemp -d) python3 -m unittest test_state_muc_gat)` xanh
- [ ] Q7 Skill `tdq-lean` ba chế độ, khai `argument-hint`, có trong chỉ mục — `(cd tests && python3 -m unittest test_skill_lean)` xanh và `grep -c tdq-lean docs/tdq/audit/skill-index.json` ≥ 1
- [ ] Q8 Cổng nợ marker: thiếu đường nâng ra mã khác 0 kèm `đường-dẫn:dòng`, repo hiện tại mã 0, không framework không fixture — `(cd tests && python3 -m unittest test_kiem_no_marker)` xanh và `python3 scripts/kiem_no_marker.py` exit 0
- [ ] Q9 Đo bằng hiệu ứng thật, thân luật xuất hiện đúng một lần mỗi lần nạp — `(cd tests && python3 -m unittest test_kenh_luat_dedupe)` xanh và bảng 4 mức của T5.2 dán trong file QC
- [ ] Q10 Bản portable chứa luật mới và được sinh lại; `kien-truc.md` ghi 6 hook — `python3 scripts/build_portable.py` exit 0, `grep -c '6 hook' docs/kien-truc.md` ≥ 1
- [ ] Q11 Tập test đỏ lệch 0 so với baseline `main`; ba assertion trần bị sửa có ghi chú lý do + ngày — `python3 -m unittest discover tests` hai bên rồi so tập tên, và `grep -c 2026-09-17 tests/test_context_hooks.py tests/test_token_budget.py` ≥ 3
- [ ] Q12 Không ghi ra ngoài repo, repo Ponytail không bị sửa — `git -C ~/Documents/ponytail status --porcelain` rỗng
- [ ] Q13 Luật món 8 được giữ: không class nào tính năng không cần, mỗi tính năng lần được trong ≤ 3 nhịp gọi, mọi hàm mới trong sàn phức tạp — `grep -c '^class ' hooks/scripts/luat_gon.py hooks/scripts/subagent_start.py scripts/kiem_no_marker.py` ra 0 cả ba, và đọc tay ba file mới ghi kết quả vào file QC
