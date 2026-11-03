# PLAN — Nội hoá luật Ponytail vào ruột TDQ-Workflow

Ngày: 2026-09-17 · Spec: ../spec/2026-09-16-2234-cong-sinh-ponytail-tdq.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — `tdq_bench.py simulate` đo trên chính plan này: 16 task, 3 đợt, đội 20.4 phút so với main 32.6 phút, `Winner: đội` cách 12.2 phút ở hệ số agent 1.5 (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH (2026-09-17 — duyệt "duyệt plan", mode `subagent` do user chốt bằng "A"; 24 task + 1 task vá QC và 13 mục DoD đều tick, QC PASS toàn bộ)

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Thân luật tinh gọn
- P2 — Nền cơ chế: bộ đọc-lọc + khoá mức gắt
- P3 — Ba kênh nạp luật
- P4 — Skill soi over-engineer + cổng nợ marker
- P5 — Log & test bắt buộc
- P6 — Bản ngoài + hồ sơ kiến trúc
- P7 — Vá hồi quy phát hiện ở T5.3
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
- [x] **T1.2** (e8m) Test khoá hình dạng thân luật: khối giữa cặp marker tồn tại, chứa đúng 7
      bậc theo thứ tự, và chứa câu món 8; câu luật tầng 1–2 nằm trong thân `SKILL.md` chứ không
      trong reference. — Test: `(cd tests && python3 -m unittest test_than_luat -v)` xanh
  - Chạm: `tests/test_than_luat.py` → file mới, chưa node nào phụ thuộc
  - Cần: T1.1
  - **Số đo lấy được ở T1.2 ngày 2026-09-17, mọi test đọc khối luật sau này phải biết:** đếm
    bậc bằng cách khớp `^| N |` trên cả khối ra **9 bậc chứ không phải 7** — bảng
    `### Two ordered passes, never one merged judgement` trong cùng khối cũng mở dòng bằng
    `| 1 |` và `| 2 |`. Cách đúng: chỉ quét trong mục
    `### The ladder — stop at the first rung that holds`, dừng ở `###` kế tiếp. Trợ lý đã
    chứng minh test có răng bằng 6 đột biến trên bản chép nháp (bỏ bậc 5, xoá dòng
    "switchable off through config", xoá marker mở, xoá số sàn trong câu luật `SKILL.md`, đổi
    tên tiêu đề món 8, đổi tên câu luật món 8) — cả 6 đều đỏ.

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
- [x] **T2.2** (e18m) Thêm khoá `muc_gat` vào `scripts/tdq_state.py`: bốn giá trị
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

- [x] **T3.1** (e22m) Mở rộng `hooks/scripts/session_start.py`: sau khối đầu (dòng luật tuân
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
  - **LỖI PLAN của tôi, sửa ngày 2026-09-17 — trần toàn đầu ra 140 dòng / 7000 ký tự → 160
    dòng / 8200 ký tự (cùng loại với quy tắc 10).** Hai số 140/7000 tôi khai ở dòng task là số
    ƯỚC, khai lúc thân luật chưa tồn tại nên không có gì để đo. Số đo thật của thân luật sau
    lọc: `lite` 72 dòng / 4404 ký tự · `full` 133 / 6887 · `ultra` 139 / 7123. Cộng khối đầu
    (≤ 12 dòng / 600 ký tự) và dòng tiêu đề `[TDQ:GON]` thì `full` ≈ 146 dòng / 7590 ký tự và
    `ultra` ≈ 152 / 7830 — ở trần 140/7000 cả hai bị cắt đuôi, và test
    `test_lite_ngan_hon_full_ngan_hon_ultra` bắt được đúng cái cắt đó (`7000 not less than
    6992`: hai mức khác nhau bị trần bóp thành gần bằng nhau). Trần khối đầu 12/600 của spec
    §2.7 KHÔNG đổi một đơn vị nào. Căn cứ chọn bên nhường: `soul.md:101` — trần dòng là ràng
    buộc bậc 3, câu luật là bậc 1, nên nâng trần kèm lý do ghi tại chỗ chứ cấm nén luật cho
    vừa trần (đây là lần thứ ba của run này, sau `SKILL_LINE_LIMITS["tdq-build"]` 150→165 và
    `TRAN_DONG["chung.md"]` 240).
- [x] **T3.2** (e16m) Thêm mã thứ sáu `TDQ:GON` vào danh sách mã ĐÓNG ở `hooks/scripts/_common.py`
      (spec §5 đã khai trước, đúng luật ở `hooks/scripts/_common.py:70`), rồi cho
      `hooks/scripts/prompt_context.py` in dòng nhắc ngắn đó **chỉ khi** phase là `implement`,
      trong trần 3 dòng / 200 ký tự, kèm một dòng log kênh. Không đọc thân luật ở kênh này —
      `UserPromptSubmit` chia ngân sách 30s.
      — Test: `(cd tests && python3 -m unittest test_prompt_context test_common -v)` xanh, có ca phase khác không in mã
  - Chạm: `hooks/scripts/_common.py`, `hooks/scripts/prompt_context.py`, `tests/test_prompt_context.py`, `tests/test_common.py` → node bị ảnh hưởng: mọi hook import `_common`
  - Cần: T2.2
  - **Số đo và hai quyết định lấy ở T3.2 ngày 2026-09-17:**
    1. Đầu ra hiện tại của `prompt_context.py` ở phase `implement` đo được **1 dòng /
       152 ký tự** (đường project trong test là đường tmp dài). Dòng nhắc gọn dài ~170 ký
       tự, nên cộng vào là **vượt** trần 240 của spec §2.7. Cách xử lý giống T3.1: giữ
       NGUYÊN SỐ 3 dòng / 240 ký tự nhưng đo trên **khối đứng trước mốc `[TDQ:GON]`**, và
       khai trần riêng cho dòng nhắc là 3 dòng / 200 ký tự (đúng số plan đã ghi). Không
       nén dòng nhắc, không bỏ dòng `next`.
    2. Dedupe của kênh này **không đo được qua đường hook**: `main()` mở đầu bằng
       `turn_log_clear`, nên hai lần chạy hook là hai LƯỢT, mỗi lượt nhắc lại là đúng.
       Test vì thế đo ở mức hàm `_nhac_gon` (gọi hai lần cùng một payload → lần hai im
       lặng). Đây là số đo T3.4 phải biết: với bug #10871 hai PID trên cùng sự kiện
       `UserPromptSubmit`, `already_reminded` KHÔNG chặn được lần hai vì PID kia đã xoá sổ
       trước — kênh lượt chỉ dedupe trong một tiến trình. Kênh phiên và kênh sub-agent
       không có `turn_log_clear` nên dedupe thật.
    3. Nửa `CODES` của task này đã về cùng T3.1: `session_start.py` in mã `TDQ:GON` từ
       T3.1, còn dòng khai mã trong `hooks/scripts/_common.py` nằm ở đây.
    4. **LỖI PLAN của tôi (số đếm), sửa ngày 2026-09-17:** T3.1 khai "sửa **ba assertion**
       đang đo `len(out) <= 600` trên toàn đầu ra". Đo thật bằng cách chạy test là **SÁU**
       chỗ, ở bốn file: `tests/test_context_hooks.py` (3 chỗ),
       `tests/test_token_budget.py::test_session_start` (1),
       `tests/test_compliance_protocol.py::test_hooks_reuse_next` +
       `::test_session_start_budget` (2), cộng thêm
       `test_token_budget.py::test_user_prompt_submit` là chỗ thứ sáu của kênh lượt. Ba chỗ
       sau plan không thấy vì phase analyze chỉ grep trong `tests/test_context_hooks.py`.
       Cách sửa giống nhau cả sáu: giữ nguyên số trần, đổi chỗ đo sang khối trước mốc
       `[TDQ:GON]`, ghi ngày + lý do tại đúng dòng sửa.
- [x] **T3.3** (e20m) Tạo `hooks/scripts/subagent_start.py` và khai vào `hooks/hooks.json` —
      sự kiện thứ năm `SubagentStart`, chèn thân luật đã lọc vào đầu hội thoại sub-agent, kèm
      một dòng log kênh. Payload thiếu khoá → in rỗng và **thoát mã 0** (fail-open, không chặn
      lượt). Docstring ghi thẳng: đây là **lời nhắc, không phải hàng rào** — `additionalContext`
      của sub-agent bị prune, non-compliance đo được 40–60%.
      — Test: `(cd tests && python3 -m unittest test_subagent_start -v)` xanh, có ca payload thiếu khoá và ca `muc_gat=off`
  - Chạm: `hooks/scripts/subagent_start.py`, `hooks/hooks.json`, `tests/test_subagent_start.py` → `hooks.json` lên 6 mục trên 5 sự kiện
  - Cần: T2.1, T2.2
- [x] **T3.4** (e12m) Chống chèn hai lần: mỗi kênh dedupe theo lượt, dùng lại cơ chế đã có ở
      `already_reminded` chứ không viết cơ chế thứ hai — bug #10871 làm hook plugin chạy hai lần
      với hai PID. — Test: `(cd tests && python3 -m unittest test_kenh_luat_dedupe -v)` xanh: gọi hook hai lần cùng một lượt thì thân luật xuất hiện **đúng một lần**
  - Chạm: `tests/test_kenh_luat_dedupe.py` → file mới; phần sửa mã nằm trong T3.1–T3.3 theo luật file nóng
  - Cần: T3.1, T3.2, T3.3
  - Đo được 2026-09-17 (hai chuyện, không sinh task mới):
    1. `SessionStart` và `SubagentStart` dùng CHUNG một sổ lượt theo `session_id`, nên trong
       cùng một lượt của cùng một phiên, kênh nào tới trước thì kênh sau im. Đúng tinh thần
       "một cơ chế dedupe duy nhất" nên giữ nguyên, test đã khoá lại hành vi này. Giá phải
       trả có thật: `SessionStart:compact` nổ giữa lượt thì trợ lý sinh ra sau đó trong cùng
       lượt không được nhắc. Chấp nhận — hàng rào thật là `edit_gate` + audit của leader,
       kênh này chỉ là lời nhắc (issue #23885). Ghi vào report như một giới hạn đã biết.
    2. Bẫy đếm: chuỗi `| 1 |` KHÔNG dùng được làm mốc đếm số lần chèn thân luật — thân luật
       có hai bảng nên nó xuất hiện 2 lần cho 1 lần chèn. Mốc đúng là
       `| 1 | Does this need to exist at all?`.

**Xong P3 khi**: chạy thật cả ba hook bằng payload giả thấy thân luật trong đầu ra (kênh phiên
có ca `source=compact`); `hooks.json` đọc được bằng máy và khai 6 mục / 5 sự kiện; thân luật
xuất hiện đúng một lần mỗi lần nạp.

## P4 — Skill soi over-engineer + cổng nợ marker

- [x] **T4.1** (e16m) Tạo `skills/tdq-lean/SKILL.md` — một skill, ba chế độ, viết tiếng Anh theo
      `docs/kien-truc.md:51`: `review` soi diff, `audit` soi cả repo, `debt` gom marker
      `ponytail:` thành sổ nợ và đánh dấu marker **không có đường nâng** là nợ thối. Frontmatter
      khai `argument-hint: "[review|audit|debt]"`. Nội dung prompt vay từ ba command
      `~/Documents/ponytail/commands/`, KHÔNG vay `/ponytail-gain`.
      — Test: `(cd tests && python3 -m unittest test_skill_lean -v)` xanh: ba mục chế độ có đủ, `argument-hint` khai đúng ba chế độ, `python3 scripts/i18n_check.py skills/tdq-lean/SKILL.md` exit 0
  - Chạm: `skills/tdq-lean/SKILL.md`, `tests/test_skill_lean.py` → file mới; node đọc: `build_portable.py` (T6.1), chỉ mục skill (T6.3)
  - Chạm (thêm 2026-09-17, plan tôi viết thiếu): `scripts/doc_lint.py`, `tests/test_token_budget.py`
    → một skill mới không tự đăng ký được. `SKILL_LINE_LIMITS` là sổ hộ khẩu skill
    (`test_skill_shape.test_exactly_six_skills` so `os.listdir(skills)` với đúng sổ đó), nên
    thiếu một dòng ở đây là skill mới bị coi như không tồn tại. Trần tổng description cũng
    phải nới: đo thật 1790 ký tự so với trần 1620. Hai trần đều là ràng buộc tầng 3
    (`soul.md:101`), nới có ngày và có lý do tại chỗ — nhưng chỉ sau khi đã cắt description
    của `tdq-lean` một lượt (224 → 185 ký tự): cắt trước, nới sau.
- [x] **T4.2** (e18m) Tạo `scripts/kiem_no_marker.py` — **một lệnh chạy được, không framework,
      không fixture**: quét comment `ponytail:` trong `scripts/` và `hooks/`, marker nào thiếu
      đường nâng thì in `đường-dẫn:dòng` và thoát mã khác 0; đủ đường nâng thì mã 0. Ghi một
      dòng log có timestamp.
      — Test: `(cd tests && python3 -m unittest test_kiem_no_marker -v)` xanh (ca thiếu / ca đủ, dựng bằng thư mục tạm chứ không bằng fixture trong repo), và `python3 scripts/kiem_no_marker.py` trên repo hiện tại exit 0
  - Chạm: `scripts/kiem_no_marker.py`, `tests/test_kiem_no_marker.py` → file mới, chưa node nào phụ thuộc

**Xong P4 khi**: `tests.test_skill_lean` và `tests.test_kiem_no_marker` xanh; `kiem_no_marker.py`
trên repo hiện tại exit 0.

## P5 — Log & test bắt buộc

- [x] **T5.1** (e12m) Khoá log service của ba kênh: mỗi kênh mỗi lần chạy ghi **một dòng** vào
      sổ lượt có sẵn (`turn_log_append`) với timestamp, tên kênh, mức gắt, số dòng luật đã chèn;
      `muc_gat=off` thì không dòng nào. Việc GHI đã gộp vào T3.1–T3.3 theo luật file nóng; task
      này viết phép kiểm. Không dựng sổ log thứ hai.
      — Test: `(cd tests && TDQ_PROJECT_DIR=$(mktemp -d) python3 -m unittest test_log_kenh_luat -v)` xanh
  - Chạm: `tests/test_log_kenh_luat.py` → file mới, chưa node nào phụ thuộc
  - Cần: T3.1, T3.2, T3.3
  - Đo được 2026-09-17: trợ lý T5.1 báo **trường "số dòng luật đã chèn" KHÔNG có trong mã**.
    Ba kênh chỉ ghi `event`/`muc_gat` (+ `source` ở SessionStart, `agent` ở SubagentStart).
    Đúng là lỗi của tôi ở T3.1–T3.3 chứ không phải của phép kiểm: dòng task này đòi trường đó
    từ đầu. Trợ lý không viết test giả vờ đạt — đó là cách xử lý đúng. Vá ở **T5.4** dưới.

- [x] **T5.4** (e8m, thêm 2026-09-17 — task vá, không cần duyệt lại) Ba kênh ghi thêm trường
      `so_dong` = số dòng thân luật thật sự in ra, và `tests/test_log_kenh_luat.py` khoá nó ở
      cả ba kênh. `muc_gat=off` vẫn không ghi dòng nào, nên không có ca `so_dong=0`.
      — Test: `(cd tests && TDQ_PROJECT_DIR=$(mktemp -d) python3 -m unittest test_log_kenh_luat -v)` xanh với ca `so_dong` của cả ba kênh
  - Chạm: `hooks/scripts/session_start.py`, `hooks/scripts/subagent_start.py`,
    `hooks/scripts/prompt_context.py`, `tests/test_log_kenh_luat.py`
  - Cần: T5.1
- [x] **T5.2** (e10m) Đối chiếu hiệu ứng thật của state và hook: mức gắt ghi trong state đúng
      bằng mức mà hook thật nhận được, đo bằng cách đọc đĩa trực tiếp rồi chạy hook.
      — Test: `python3 scripts/tdq_state.py set muc_gat=lite` rồi chạy `session_start.py` thấy số dòng luật ít hơn ca `full`
  - Dùng: `tdq-check-status`
  - Để: đọc `docs/tdq/state.json` trực tiếp để đối chiếu với giá trị hook nhận được, thay vì
    tin dòng khai. Agent ngoài không có skill system: đọc `skills/tdq-check-status/SKILL.md` rồi làm theo.
  - Ra: một bảng 4 dòng (4 mức gắt) ghi số dòng luật hook thật in ra, dán vào file QC
  - Kiểm: bốn mức cho bốn số dòng khác nhau, `off` ra 0
  - Không dùng cho: ghi vào state (chỉ `scripts/tdq_state.py` được ghi — `docs/kien-truc.md:25`)
  - Cần: T3.1, T2.2
  - **Bảng đo thật 2026-09-17** (chạy `session_start.py` bằng payload thật, mỗi mức một
    `session_id` riêng để dedupe không che mất lần sau; giá trị đọc THẲNG từ
    `docs/tdq/state.json` chứ không tin dòng khai — luật "đĩa là bằng chứng" của
    `tdq-check-status`):

    | `muc_gat` | Giá trị trên đĩa | Số dòng thân luật hook in ra | `so_dong` trong sổ lượt |
    |---|---|---|---|
    | `off` | `off` | 0 | không có dòng nào |
    | `lite` | `lite` | 72 | 72 |
    | `full` | `full` | 133 | 133 |
    | `ultra` | `ultra` | 139 | 139 |

    Bốn mức ra bốn số khác nhau, `off` ra 0, và `so_dong` khớp đầu ra thật từng mức — đúng
    thứ T5.4 vừa thêm. Trước khi đo, `muc_gat` VẮNG trên đĩa (mặc định `full`); sau khi đo đã
    ghi lại `full` bằng CLI, hiệu lực y nguyên.
- [x] **T5.3** (e10m) Chạy toàn bộ suite **đúng một lần** và đối chiếu baseline `main` sạch:
      tập tên test đỏ lệch 0 cả hai chiều. — Test: `python3 -m unittest discover tests` trên nhánh và trên worktree `main`, so hai tập tên test đỏ
  - Cần: T4.1, T4.2, T5.1, T5.4, **và cả P7** (thêm 2026-09-17)
  - Điều kiện chạy (đo được 2026-09-17, lỗi của tôi lúc chạy gộp): **không export
    `TDQ_PROJECT_DIR`** khi chạy cả suite. `resolve_project_dir` cho env thắng payload `cwd`,
    nên biến đó rò sang các test dựng project trong thư mục tạm riêng và làm 6 test đỏ oan.
    `test_log_kenh_luat` tự ghim env cho từng lần chạy hook nên xanh cả hai cách.
  - Lần đo thứ nhất (2026-09-17): nhánh `Ran 1907 tests … failures=34, errors=4`; baseline
    `main` sạch (HEAD `4faed21`) `Ran 1802 tests … failures=291, errors=4`. So theo TÊN test
    ra **28 tên đỏ trên nhánh mà xanh trên main** — hồi quy thật, năm nguyên nhân, thành P7.
    Tạm hạ task về `[ ]`: P7 xong thì đo lại lần nữa rồi tick.
  - **Cách đếm tên, ghi lại vì lần đầu tôi đếm sai:** `unittest` in subtest thành
    `FAIL: test_x (module.Class.test_x) [tham số]`, nên bóc tên phải lấy đường dẫn trong
    ngoặc và bỏ phần `[tham số]`; đếm cả tham số thì một test parametrize hoá thành 285 "tên"
    và lệch baseline thành con số vô nghĩa. Số tên thật: nhánh 13 → 12, main 12.
  - **Lần đo thứ hai, sau P7 (2026-09-17, đây là số chốt):** nhánh
    `Ran 1907 tests in 112.9s … FAILED (failures=291, errors=4, skipped=14)`, **12 tên đỏ**;
    main `Ran 1802 tests in 109.2s … FAILED (failures=291, errors=4, skipped=15)`, **12 tên
    đỏ**. `comm` hai chiều đều RỖNG — lệch 0. Nhánh chạy hơn main 105 test: đó là các test
    lượt này thêm, và tất cả đều xanh.

## P6 — Bản ngoài + hồ sơ kiến trúc

- [x] **T6.1** (e10m) Sinh lại bản ngoài bằng `python3 scripts/build_portable.py` — cấm sửa tay
      (`docs/kien-truc.md:13`). — Test: `git status --porcelain portable_claude portable_codex` có thay đổi, và grep thấy thân luật mới trong cả hai bản
  - Chạm: `portable_claude/`, `portable_codex/` → bản SINH, node nguồn là `skills/`+`hooks/`+`agents/`+`scripts/`
  - Cần: T1.1, T3.1, T3.2, T3.3, T4.1
  - Chạm (thêm 2026-09-17, plan tôi viết thiếu): `scripts/build_portable.py`,
    `tests/test_build_portable.py`. Lần sinh đầu chỉ có `portable_claude` nhận `tdq-lean`;
    `portable_codex` và `antigravity_portable` dựng theo tuple `THU_TU_SKILL` — thứ tự ĐỌC,
    vì harness không có hệ skill thì số trong tên file chính là cơ chế định tuyến. Thêm
    `tdq-lean` ngay sau `tdq-build` (soi đúng thứ vừa build ra). Sửa bản SINH bằng tay là
    cấm, sửa bộ sinh thì không — đây là cách một skill mới lên được hai bản kia.
    Một test đỏ theo: `test_settings_co_du_5_hook_va_bien_dung` còn đòi 5 hook / 4 sự kiện.
    Mã đúng, test cũ sai → đổi tên thành `..._6_hook...` và sửa số, có lý do tại chỗ.
  - Cũng đo được: bản ngoài chở đủ thân luật (`chung.md`), `subagent_start.py` và
    `hooks.json` 6 mục ở cả `portable_claude` lẫn `portable_codex`.
- [x] **T6.2** (e5m) Cập nhật `docs/kien-truc.md`: dòng hook đổi từ "5 hook" sang "6 hook trên 5
      sự kiện", và thêm một dòng lịch sử ngày 2026-09-17 ghi việc nội hoá luật. — Test: `grep -c '6 hook' docs/kien-truc.md` ra ≥ 1 và `python3 scripts/doc_lint.py docs/kien-truc.md` exit 0
  - Cần: T3.3
- [x] **T6.3** (e8m) Dựng lại chỉ mục skill và khoá đường đọc `tdq-lean`. — Test: `python3 scripts/skill_router.py --dung-kho` exit 0 và `(cd tests && python3 -m unittest test_skill_lean -v)` xanh với ca bản đồ SKILL.md trỏ đúng `skills/tdq-lean/SKILL.md`
  - Chạm: `docs/tdq/audit/skill-index.json` → file SINH bằng `skill_router.py`, cấm sửa tay;
    `tests/test_skill_lean.py`
  - Cần: T4.1
  - **LỖI PLAN của tôi (2026-09-17, sửa tại chỗ).** Phép kiểm cũ — grep `tdq-lean` trong
    `docs/tdq/audit/skill-index.json` — KHÔNG thể xanh trong request này, và không phải vì
    thiếu việc. Đo thật: `skill_router.dung_kho` lấy hàng từ `skill_inventory.inventory`, mà
    hàm đó chỉ quét `~/.claude/skills`, `<project>/.claude/skills` và thư mục skill của
    **plugin ĐÃ CÀI** (`_plugin_skill_dirs` đọc `installed_plugins.json`: bản cài hiện tại là
    cache `tdq-local/tdq-workflow/0.47.0`, 8 skill, chưa có `tdq-lean`). Nó KHÔNG quét
    `skills/` của repo này. Dựng lại chỉ mục trong repo vì thế ra 10 bản ghi và 0 lần
    `tdq-lean` — đúng như mã định nghĩa.
    Hai đường tôi KHÔNG chọn: (1) sửa `skill_inventory` để quét thêm `skills/` của project —
    đổi nghĩa "skill đang bật" cho mọi project, một tính năng không ai đặt hàng (bậc 1 của
    luật gọn); (2) tự cài lại plugin để cache có `tdq-lean` — cài đặt là việc của người dùng,
    luật cấm tôi tự chạy lệnh cài.
    Đường đã chọn: khoá thứ CHẠY ĐƯỢC HÔM NAY — bản đồ `SKILL.md` của router đã trỏ đúng
    `skills/tdq-lean/SKILL.md` (tầng "đọc SKILL.md trực tiếp" dùng được ngay), cộng một lần
    dựng lại chỉ mục cho sạch. Việc `tdq-lean` xuất hiện trong chỉ mục là **hệ quả của lần
    cài plugin kế tiếp**, ghi vào report như một bước của người dùng chứ không phải task bỏ dở.

**Xong P6 khi**: hai bản portable chứa thân luật mới và không có dấu sửa tay; `kien-truc.md`
ghi 6 hook; bản đồ SKILL.md của router trỏ đúng `skills/tdq-lean/SKILL.md` (sửa 2026-09-17
theo ghi chú ở T6.3 — chỉ mục chỉ nhận `tdq-lean` sau lần cài plugin kế tiếp).

## P7 — Vá hồi quy phát hiện ở T5.3 (thêm 2026-09-17, task vá, không cần duyệt lại)

28 test đỏ trên nhánh mà xanh trên `main`, gom về năm nguyên nhân. Mỗi task dưới đây vá đúng
một nguyên nhân, đi red → green như mọi task khác.

- [x] **T7.1** (e4m) Hoàn `docs/tdq/audit/skill-index.json` về bản đang có trên `main`. — Test: `git diff --stat main -- docs/tdq/audit/skill-index.json` rỗng và `(cd tests && python3 -m unittest test_skill_router)` ra ĐÚNG số đỏ của `main` (285), không phải xanh
  - Chạm: `docs/tdq/audit/skill-index.json`
  - Đo được: bản trên `main` có **284 bản ghi** (dựng trên máy đang bật rất nhiều plugin),
    lần dựng lại của tôi ở T6.3 hạ xuống còn **10** và vẫn `grep -c tdq-lean` ra **0**. Nên
    lần dựng lại đó là mất trắng: nó không thêm được gì và làm ~24 test `test_skill_router`
    đỏ. Nửa hữu ích của T6.3 là ca test bản đồ SKILL.md, nửa đó giữ nguyên.
  - **LỖI PLAN của tôi lần hai, trợ lý bắt được (2026-09-17, sửa tại chỗ).** Tôi viết phép
    kiểm là "`test_skill_router` xanh". Không đạt được, và không phải vì thiếu việc: trợ lý đo
    cả hai bản trong worktree riêng và ra **bản `main` đỏ 285, bản dựng lại đỏ 24**. Lý do là
    suite này tự đá nhau trên máy hiện tại — `test_moi_duong_dan_khac_rong_deu_mo_moc` và
    `test_so_ban_ghi_khop_skill_inventory` đòi chỉ mục khớp máy ĐANG chạy (10 skill, đường dẫn
    mở được), còn `test_kho_da_dung_va_du_bon_truong` (> 100 bản ghi) và bộ đáp án của
    `TiLeTrungTest` đòi tập plugin LỚN (284). Thêm nữa 284 `duong_dan` trong bản `main` trỏ về
    home của MÁY KHÁC (`/Users/truongdinhquoc/...`) nên chết hết trên máy này.
    Vậy tiêu chuẩn đúng cho task này không phải "xanh" mà là **lệch 0 so với baseline**: file
    trùng `main` từng byte thì tập tên đỏ của module này trùng `main` theo định nghĩa. Đo lại
    sau khi hoàn nguyên: 284 bản ghi, `git diff` với `main` rỗng, `FAILED (failures=285)` —
    khớp `main`. 24 tên đỏ kia biến mất khỏi danh sách hồi quy.
  - Việc hoàn nguyên do LEADER làm, không phải trợ lý: bản dựng lại chưa từng được commit, nó
    nằm ở working tree CHÍNH — ngoài worktree của trợ lý, nên trợ lý đúng khi báo `blocked`
    thay vì tự với tay ra ngoài vùng. Không có commit nào trong worktree t7.1.
  - **Nợ ghi lại, không sửa trong lượt này:** chỉ mục này là artefact SINH nhưng được commit từ
    một máy khác, nên `test_skill_router` không thể xanh trên máy nào khác. Sửa đúng là cho
    `skill_router` dựng chỉ mục theo máy đang chạy hoặc cho test đọc đáp án theo chỉ mục thật —
    cả hai đều ngoài phạm vi request này.
- [x] **T7.2** (e4m) Gỡ dòng luật trong `NHAC_GON` khỏi sổ nợ marker: dòng đó là VĂN LUẬT nói
      marker nợ gì, không phải một entry nợ. — Test: `python3 scripts/kiem_no_marker.py` exit 0 và `(cd tests && python3 -m unittest test_kiem_no_marker)` xanh
  - Chạm: `hooks/scripts/prompt_context.py`
  - Cách vá: dùng đúng cửa thoát mà `kiem_no_marker.py` đã có (`# no-marker: allow`, chính
    file đó tự dùng cho hằng `MARKER`), không phải viết lại văn luật cho lách được grep.
- [x] **T7.3** (e5m) Ba dòng `Next step:` của `skills/tdq-lean/SKILL.md` phải nêu pha kế hoặc
      nói rõ pha không đổi — skill này chỉ báo cáo nên vế đúng là "pha không đổi". — Test: `(cd tests && python3 -m unittest test_luat_gate_chat test_skill_lean)` xanh và `python3 scripts/doc_lint.py skills/tdq-lean/SKILL.md` exit 0
  - Chạm: `skills/tdq-lean/SKILL.md`
- [x] **T7.4** (e6m) Thêm `## Mục lục` khớp đủ tiêu đề `##` vào
      `skills/tdq-build/references/rules/chung.md`: thân luật làm file dài 222 dòng, vượt trần
      100 dòng của luật reference một tầng. — Test: `(cd tests && python3 -m unittest test_reference_mot_tang)` xanh
  - Chạm: `skills/tdq-build/references/rules/chung.md`
- [x] **T7.5** (e4m) Bỏ ba comment `i18n-allow` cuối dòng mà T1.1 thêm vào câu luật chuẩn ở
      `skills/tdq-build/SKILL.md`: comment nằm TRONG câu nên phép so nguyên văn của luật ưu
      tiên tìm kiếm không còn khớp. — Test: `(cd tests && python3 -m unittest test_tdq_lsp_skill)` xanh và `python3 scripts/i18n_check.py skills/tdq-build/SKILL.md` exit 0
  - Chạm: `skills/tdq-build/SKILL.md`
  - Đo được: trên `main` cả khối câu luật chỉ cần MỘT marker ở dòng dẫn phía trên; ba comment
    thêm là dư, và dư ở đây đắt vì nó làm lệch một câu phải chép nguyên văn.
  - **Hai phép kiểm đá nhau, và tôi chọn bên nào (2026-09-17).** Bỏ ba comment thì
    `i18n_check.py skills/tdq-build/SKILL.md` báo lại 3 dòng tiếng Việt — vì `i18n_check` xét
    marker theo TỪNG dòng và chỉ có khối trong fence mới được marker ở dòng trên bao. Đo ba
    skill anh em: `tdq-plan` 3 dòng, `tdq-spec` 3 dòng, `tdq-intake` 4 dòng — cùng một nợ,
    có sẵn trên `main`. Nên bên thắng là câu luật chép nguyên văn (ràng buộc tầng 1–2), còn
    3 dòng kia trở về đúng trạng thái nợ dùng chung của repo, không phải nợ mới của lượt này.
    Đường tôi KHÔNG chọn: bọc câu luật vào fence để lách `i18n_check` — nó làm file này lệch
    khuôn ba skill anh em, và sửa `i18n_check` cho marker bao được khối prose là việc của một
    request khác.
- [x] **T7.6** (e6m) Sinh lại bản ngoài sau P7 (`python3 scripts/build_portable.py`) vì T7.2,
      T7.3, T7.4, T7.5 đều sửa file nguồn của bản sinh. — Test: `python3 scripts/build_portable.py` exit 0 và `(cd tests && python3 -m unittest test_build_portable)` xanh
  - Chạm: `portable_claude/`, `portable_codex/`, `antigravity_portable/` → bản SINH
  - Cần: T7.2, T7.3, T7.4, T7.5

- [x] **T7.7** (e6m, thêm 2026-09-17 sau lần đo lại của T5.3) Cập nhật số dòng trong
      `docs/tdq/audit/luat-hien-co.md`: thân luật T1.1 và mục lục T7.4 đẩy lệch số dòng của các
      điểm neo, tỉ lệ lệch lên 6,4% (21/329) trong khi trần của test là 5%. — Test: `(cd tests && python3 -m unittest test_luat_skill test_ranh_gioi)` xanh
  - Chạm: `docs/tdq/audit/luat-hien-co.md`
  - Cách làm: chỉ sửa SỐ DÒNG của những hàng mà chữ neo không còn nằm đúng dòng đã ghi, dò lại
    bằng chính chữ neo trong bảng. Không đổi một chữ neo nào, không thêm/bớt hàng — bảng này là
    lưới an toàn của mọi lần tối ưu workflow sau này, sửa chữ neo là tháo lưới.
  - Đo được: 21 hàng lệch, **20 hàng là do lượt này** (L006–L016 ở `tdq-build/SKILL.md` lệch 13
    dòng vì thân luật T1.1; L039–L047 ở `chung.md` lệch 11 dòng vì mục lục T7.4, riêng L046/L047
    nhảy xuống 206/208 vì khối luật chèn giữa). Hàng thứ 21 là **L286** ở `skills/tdq-plan/SKILL.md`:
    dò cả file không thấy chữ neo ở dòng nào — nợ có sẵn trên `main`, cố ý không sửa vì ngoài
    vùng request này. Sau khi sửa 20 hàng: `test_luat_skill` + `test_ranh_gioi` 26 test OK.

**Xong P7 khi**: cả năm nguyên nhân hết đỏ, bản ngoài sinh lại, và lần đo lại của T5.3 cho
lệch 0 theo chiều nhánh → main.

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

- [x] Q1 Thân luật đủ 7 bậc + món 8, chia đúng hai chỗ theo `soul.md:99` — `(cd tests && python3 -m unittest test_than_luat)` xanh và `python3 scripts/i18n_check.py skills/tdq-build/references/rules/chung.md` exit 0
      (sửa phép kiểm 2026-09-17: bỏ `skills/tdq-build/SKILL.md` khỏi vế `i18n_check` theo ghi
      chú ở T7.5 — ba dòng câu luật chuẩn là nợ i18n dùng chung của repo, có sẵn trên `main` ở
      cả `tdq-plan`, `tdq-spec`, `tdq-intake`; ép exit 0 riêng một file phải hy sinh phép so
      nguyên văn của câu luật, tức hy sinh ràng buộc nặng hơn.)
- [x] Q2 Bộ lọc: 4 mức ra 4 kết quả, `off` rỗng, mức lạ về `full` — `(cd tests && python3 -m unittest test_luat_gon)` xanh
- [x] Q3 Kênh phiên chèn thật kể cả sau compact, trần khối đầu 12/600 giữ nguyên, toàn đầu ra ≤ 160/8200 (số cũ 140/7000 là số ước, xem ghi chú sửa lỗi plan ở T3.1) — `(cd tests && python3 -m unittest test_context_hooks test_token_budget)` xanh
- [x] Q4 Dòng nhắc ngắn chỉ ở phase `implement`, ≤ 3 dòng/200 ký tự, danh sách mã đúng 6 mã — `(cd tests && python3 -m unittest test_prompt_context test_common)` xanh
- [x] Q5 Kênh sub-agent in thân luật, `hooks.json` 6 mục/5 sự kiện, payload thiếu khoá vẫn mã 0 — `(cd tests && python3 -m unittest test_subagent_start)` xanh
- [x] Q6 Khoá `muc_gat` đọc/ghi qua CLI, mặc định và mọi đường lỗi ra `full` — `(cd tests && TDQ_PROJECT_DIR=$(mktemp -d) python3 -m unittest test_state_muc_gat)` xanh
- [x] Q7 Skill `tdq-lean` ba chế độ, khai `argument-hint`, router đọc tới được — `(cd tests && python3 -m unittest test_skill_lean)` xanh, gồm ca bản đồ SKILL.md trỏ đúng `skills/tdq-lean/SKILL.md`
      (sửa phép kiểm 2026-09-17: vế `grep -c tdq-lean docs/tdq/audit/skill-index.json` ≥ 1 KHÔNG
      đo được hôm nay và cũng không đo được bằng cách làm thêm việc — chỉ mục dựng từ skill của
      plugin ĐÃ CÀI, không từ `skills/` của repo, nên bản dựng lại vẫn ra 0. Lý do đầy đủ ở T6.3
      và T7.1; `tdq-lean` vào chỉ mục sau lần cài plugin kế tiếp, ghi trong report như bước của
      người dùng.)
- [x] Q8 Cổng nợ marker: thiếu đường nâng ra mã khác 0 kèm `đường-dẫn:dòng`, repo hiện tại mã 0, không framework không fixture — `(cd tests && python3 -m unittest test_kiem_no_marker)` xanh và `python3 scripts/kiem_no_marker.py` exit 0
- [x] Q9 Đo bằng hiệu ứng thật, thân luật xuất hiện đúng một lần mỗi lần nạp — `(cd tests && python3 -m unittest test_kenh_luat_dedupe)` xanh và bảng 4 mức của T5.2 dán trong file QC
- [x] Q10 Bản portable chứa luật mới và được sinh lại; `kien-truc.md` ghi 6 hook — `python3 scripts/build_portable.py` exit 0, `grep -c '6 hook' docs/kien-truc.md` ≥ 1
- [x] Q11 Tập test đỏ lệch 0 so với baseline `main`; ba assertion trần bị sửa có ghi chú lý do + ngày — `python3 -m unittest discover tests` hai bên rồi so tập tên, và `grep -c 2026-09-17 tests/test_context_hooks.py tests/test_token_budget.py` ≥ 3
- [x] Q12 Không ghi ra ngoài repo, repo Ponytail không bị sửa — `git -C ~/Documents/ponytail status --porcelain` rỗng
- [x] Q13 Luật món 8 được giữ: không class nào tính năng không cần, mỗi tính năng lần được trong ≤ 3 nhịp gọi, mọi hàm mới trong sàn phức tạp — `grep -c '^class ' hooks/scripts/luat_gon.py hooks/scripts/subagent_start.py scripts/kiem_no_marker.py` ra 0 cả ba, và đọc tay ba file mới ghi kết quả vào file QC

## QC vòng 1 — fix

- [x] **QC1.1** (e4m) Xoá rác hook mà lượt này để lại trong repo bên thứ ba `~/Documents/ponytail` (`docs/tdq/.tdq-prompt-last.json`, `docs/tdq/.tdq-turn.jsonl`) để Q12 sạch. — Test: `git -C ~/Documents/ponytail status --porcelain` rỗng và `git -C ~/Documents/ponytail diff --stat` rỗng
  - **Q12 đỏ thật ở vòng 1, không phải phép kiểm sai.** Lúc phân tích, cwd của một số lượt là
    `~/Documents/ponytail`, nên hook TDQ (`resolve_project_dir` lấy `cwd` của payload) tự tạo
    `docs/tdq/` ở ĐÓ và ghi hai file nháp của phiên `f2639309`. Không file nào của Ponytail bị
    sửa (`git diff` rỗng cả trước lẫn sau), hai file kia là nháp của chính workflow này, không
    chứa nội dung của họ và không chứa khoá bí mật — đã đọc kiểm trước khi xoá.
  - Đã xoá `docs/tdq/` khỏi repo Ponytail; sau xoá `status --porcelain` rỗng, `diff --stat` rỗng.
  - **Gốc nằm ngoài phạm vi request này:** hook ghi state theo project của cwd là thiết kế sẵn
    có của plugin. Việc đọc một repo bên thứ ba khi TDQ đang cài sẽ luôn để lại nháp ở đó, nên
    phép kiểm Q12 phải chạy ở CUỐI lượt, không phải lúc bắt đầu. Ghi vào report như nợ đã biết.
