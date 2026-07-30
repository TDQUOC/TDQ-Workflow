# SPEC — Kiểm kê & tận dụng skill phụ trợ (tdq-workflow 0.3.3)

Ngày: 2026-07-29 · Bản: **1.1** · Request: ../requests/2026-07-29-skill-inventory.md · Lane: full
Trạng thái: CHỜ DUYỆT

> Đổi ở bản 1.1 (theo góp ý của user): quyết định `DÙNG` không được dừng ở một dòng ghi tên
> skill. Plan phải có **hợp đồng sử dụng 6 trường** ở mức task (§3 điểm 4, đầu ra 6/6b),
> và có lệnh máy đối chiếu spec §3b ↔ plan để không ai ghi cho có rồi implement mù (Q13).

## 1. Mục tiêu & phạm vi

- **Mục tiêu:** mọi request TDQ đều đi qua một bước **kiểm kê năng lực bắt buộc**, kết quả
  ghi thành artifact máy kiểm được (spec §3b), thiên lệch mặc định về phía **DÙNG**, và
  viết máy móc tới mức một model nhỏ chạy local vẫn thi hành đúng.
- **Trong phạm vi:**
  - Script kiểm kê skill trên đĩa + test.
  - Bước kiểm kê trong `tdq-intake` (cả lane full và quick) + file reference chứa khuôn.
  - Ô bắt buộc trong khuôn spec (§3b).
  - **Hợp đồng sử dụng skill 6 trường** ở mức task trong khuôn plan + lệnh đối chiếu
    spec §3b ↔ plan (mọi `DÙNG` phải có hợp đồng đầy đủ, không được ghi cho có).
  - `tdq-build`: nạp skill đã cam kết trước khi code; QC kiểm dấu vết thật.
  - Cưỡng chế bằng `doc_lint` rule **R8** (không thêm mã hook mới).
  - `PHASE_TABLE` (checklist phase `no_state` + `analyze`) và `phases.md` sinh lại.
  - `portable/` cho agent không có skill system.
  - Đóng gói 0.3.3 + CHANGELOG.
- **NGOÀI phạm vi:**
  - Viết lại các câu mơ hồ sẵn có ở `tdq-intake:41,49,51,71` và `tdq-build:32` — cùng chủ đề
    "viết cho model yếu" nhưng là request riêng, gộp vào sẽ làm phình diff và khó QC.
  - Thêm mã nhắc hook mới (`[TDQ:SKILL]`) — xem §3, đã loại.
  - Hook tự động nạp skill hộ model.
  - Sửa `~/.claude/CLAUDE.md` §10 (việc của user, không phải của plugin).

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Script kiểm kê | `scripts/skill_inventory.py` | Chạy trong repo này in đúng 7 skill (1 user + 6 plugin), exit 0 |
| 2 | Test script | `tests/test_skill_inventory.py` | ≥8 test, dựng HOME giả trong tmpdir, không đụng máy thật |
| 3 | Khuôn kiểm kê | `skills/tdq-intake/references/skill-inventory.md` | File tồn tại, ≤200 dòng (`test_reference_files_bounded`) |
| 4 | Bước B0 ở intake | `skills/tdq-intake/SKILL.md` | Có mục "Bước B0"; file ≤120 dòng (`doc_lint` R6) |
| 5 | Ô §3b trong spec | `skills/tdq-spec/references/spec-template.md` | Khối copy-paste có heading `## 3b.` + bảng 4 cột |
| 6 | Hợp đồng skill ở plan | `skills/tdq-plan/references/plan-template.md`, `skills/tdq-plan/SKILL.md` | Khuôn có bảng "Năng lực → task" + khối 6 trường `Dùng/Nạp/Để/Ra/Kiểm/Không dùng cho` |
| 6b | Lệnh đối chiếu spec ↔ plan | `scripts/doc_lint.py --pair <spec> <plan>`, `tests/test_doc_lint.py` | Mọi `DÙNG` ở spec §3b có khối 6 trường đủ trong plan; thiếu 1 trường → exit 1 nêu rõ trường nào |
| 7 | Nạp skill khi build | `skills/tdq-build/SKILL.md`, `references/qc.md` | Phần A có bước nạp; `qc.md` có hạng mục kiểm dấu vết |
| 8 | Rule R8 | `scripts/doc_lint.py`, `tests/test_doc_lint.py` | R8 bắt spec thiếu §3b; 1 fixture bẩn + 1 fixture sạch |
| 8b | Miễn trừ spec cũ | 4 file `docs/tdq/spec/2026-07-2*.md` có trước bản này | Mỗi file thêm đúng 1 dòng `<!-- doc-lint: allow R8 -->`; `doc_lint.py docs/tdq/spec` exit 0 |
| 9 | Checklist phase | `scripts/tdq_state.py` (`PHASE_TABLE`), `references/phases.md` | `next` mọi phase vẫn ≤20 dòng; `test_phase_table` xanh |
| 10 | Portable | `portable/workflow/01-intake.md`, `02-spec.md` | `test_portable_sync` xanh; có cột "tương đương nếu không có skill" |
| 11 | Đóng gói | `CHANGELOG.md`, `.claude-plugin/plugin.json` | version `0.3.3`; `plugin validate --strict` PASS |

## 3. Cách tiếp cận & lý do

**Chọn: hai nguồn kiểm kê + fail-open về phía DÙNG + cưỡng chế bằng lint.**

1. **Hai nguồn, vì một nguồn nào cũng thiếu.** Đo thật: script quét đĩa ra **7** skill,
   context có **18**. Skill built-in (`dataviz`, `security-review`, `artifact-design`…)
   không tồn tại trên đĩa. Ngược lại, subagent trong worktree và agent ngoài không đọc được
   context của phiên chính. Vì vậy: **script lo phần đĩa** (kiểm chứng được, tái lập được),
   **model chép thêm phần built-in từ danh sách skill đang thấy**, và script in sẵn một dòng
   nhắc cố định ở cuối bảng để model yếu không quên bước chép.

2. **Quy tắc 1% viết thành luật máy chạy được.** Tách "xét" khỏi "dùng":
   - **Xét là 100% bắt buộc**: mọi skill trong bảng phải có đúng một dòng phán quyết.
   - **Loại chỉ bằng 4 lý do đóng**: `khác lĩnh vực` · `spec §3 đã chọn cách khác tốt hơn` ·
     `thiếu quyền/công cụ skill đó cần` · `user đã cấm`.
   - **Mặc định khi phân vân = DÙNG.** Không khớp gọn vào 1 trong 4 lý do → ghi `DÙNG`.
   Lý do: bắt model tự lượng hoá "1%" là thứ model yếu luôn làm sai; enum đóng + mặc định
   fail-open cho ra đúng hành vi mong muốn mà không cần model suy luận xác suất.

3. **Cưỡng chế bằng `doc_lint` R8, không bằng hook.** Bộ 5 mã nhắc là tập đóng và có trần
   token cứng (spec §2.7); thêm mã thứ 6 tốn ngân sách mỗi turn để phục vụ một bước chỉ chạy
   một lần mỗi request. Lint chạy trong QC, chặn đúng lúc, không tốn token của model.
   R8 **chỉ** soi file nằm dưới thư mục `spec/` (không đụng `skills/`, `portable/`), nên lệnh
   QC đổi thành `python3 scripts/doc_lint.py skills portable docs/tdq/spec`. Bốn spec viết
   trước bản này được miễn trừ bằng đúng cơ chế `<!-- doc-lint: allow R8 -->` sẵn có — miễn
   trừ tường minh, không sửa lịch sử và không cần ngoại lệ chôn trong code.

4. **`DÙNG` là một hợp đồng, không phải một cái nhãn.** Ghi tên skill rồi implement mù thì
   không hơn gì không ghi. Mỗi skill `DÙNG` ở spec §3b phải nở thành một khối **6 trường
   cố định**, đặt ngay trong task của plan — sáu trường trả lời sáu câu mà model yếu hay
   trượt: *dùng cái gì · nạp lúc nào và bằng lệnh gì · để làm gì · phải đẻ ra artifact nào ·
   kiểm bằng lệnh nào · cấm lan sang việc gì*:

   ```markdown
   ## Năng lực → task
   | Skill | Task | Đầu ra bắt buộc |
   |---|---|---|
   | dataviz | T3.2 | `src/chart.tsx` ghi tên palette ở comment đầu file |

   - [ ] **T3.2** Vẽ biểu đồ tồn kho theo tháng
     - Dùng: `dataviz`
     - Nạp: gọi skill `dataviz` TRƯỚC bước đỏ của task này.
       Agent ngoài không có skill system: đọc `<đường-dẫn>/SKILL.md` rồi làm theo.
     - Để: chọn dạng biểu đồ + bảng màu cho chuỗi thời gian.
     - Ra: `src/chart.tsx`, dòng đầu ghi `// palette: <tên>`.
     - Kiểm: `grep -n "^// palette:" src/chart.tsx` khớp tên trong `references/palette.md`.
     - Không dùng cho: layout trang, chọn font.
   ```

   Ràng buộc máy kiểm: `doc_lint.py --pair <spec> <plan>` đối chiếu hai file — mỗi `DÙNG`
   ở §3b phải có ≥1 khối, mỗi khối phải đủ 6 trường. Đây là bản sao của luật sẵn có
   "mọi đầu ra §2 phải ánh xạ ≥1 task" (`tdq-plan/SKILL.md:30`), áp cho năng lực.
   Trường **Ra** và **Kiểm** là thứ khiến QC bắt được "ghi cho có": không có artifact thì
   dòng `DÙNG` đó phải sửa lại thành `KHÔNG — <lý do>`, chứ không được để lửng.

**Đã loại:**
- *Chỉ dùng script* — bỏ sót 11 skill built-in (đo 7/18).
- *Chỉ dùng context list* — subagent/portable không thấy, và không có gì để QC đối chiếu.
- *Thêm mã hook `[TDQ:SKILL]`* — phá tập mã đóng, tốn token mỗi turn.
- *Quét `find ~/.claude -name SKILL.md`* — ra **152** file vì cache giữ mọi version cũ.

## 3b. Năng lực & công cụ

Bảng của chính spec này (dogfood khuôn mới). Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `security-review` | built-in | **DÙNG** | QC Q9: script đọc `settings.json`, `installed_plugins.json` và ghép đường dẫn từ dữ liệu ngoài |
| `tdq-intake/spec/plan/build/conventions` | plugin | NỀN | Chính workflow đang chạy |
| `graphify` | user | KHÔNG | spec §3 đã chọn cách khác tốt hơn: 6 file skill đọc trực tiếp, rẻ hơn dựng graph |
| `simplify` | built-in | KHÔNG | spec §3 đã chọn cách khác tốt hơn: `doc_lint` + trần dòng đã ép độ gọn |
| `claude-api`, `dataviz`, `artifact-design`, `artifact-capabilities`, `run`, `init`, `loop`, `schedule`, `update-config`, `keybindings-help`, `fewer-permission-prompts`, `review` | built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- **Log service bật mặc định**: `skill_inventory.py` cảnh báo ra stderr kèm timestamp khi
  thiếu/hỏng `settings.json`, `installed_plugins.json`, hoặc thư mục skill không đọc được;
  tắt bằng `TDQ_LOG=0`. Dùng lại `_warn/_info` của `tdq_state.py`, không viết logger thứ hai.
- **Không placeholder**: script thiếu dữ liệu thì in bảng rỗng + cảnh báo, cấm bịa tên skill.
- **Exit code**: luôn `0` cho mọi trục trặc dữ liệu; `2` chỉ khi gõ sai cú pháp lệnh
  (giống hợp đồng của `tdq_state.py`).
- **Mỗi thành phần một unit test**, chạy bằng `python3 -m unittest discover tests`.
- **Câu chữ cho model yếu** (áp cho mọi dòng mới ở mục 3–7 của §2): động từ mệnh lệnh đứng
  đầu; một dòng một hành động; mọi lựa chọn là enum đóng; có mặc định khi phân vân; điều kiện
  "xong" là artifact tồn tại; số cụ thể thay tính từ; không dùng từ mơ hồ mà `spec-template.md`
  đã cấm ("phù hợp", "tối ưu", "nếu cần", "thật sự").

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Plugin `scope: "project"` của project khác lọt vào bảng | Kiểm kê sai, model nạp skill không tồn tại | Lọc `projectPath` ≠ project đang chạy; test riêng |
| `enabledPlugins` nằm ở 3 tầng settings | Bỏ sót skill đang bật ở mức project | Gộp `~/.claude/settings.json` + `<project>/.claude/settings{,.local}.json`, tầng sau đè tầng trước; test riêng |
| Cache plugin giữ mọi version cũ (152 file) | Bảng rác, tốn token | Chỉ đọc `installPath` của bản đang cài; test có 2 version giả |
| Trần token skill | `doc_lint` R6 / `test_token_budget` đỏ | intake còn 40 dòng trống/120; chi tiết đặt ở `references/`; đo lại trong QC |
| `next` vượt 20 dòng khi thêm checklist | `test_token_budget::test_next_output` đỏ | Thêm tối đa 1 mục/phase, đo trong QC |
| Bảng phình khi user cài nhiều plugin | Spec loãng, model yếu bỏ cuộc | >20 skill: ghi riêng từng dòng `DÙNG`, gom các `KHÔNG` cùng lý do vào một dòng |
| Khối 6 trường làm plan phình | Plan khó đọc | Khối chỉ viết cho skill `DÙNG` (thường 0–2 cái); mỗi trường đúng 1 dòng, tối đa 7 dòng/khối |
| Điền hợp đồng cho có, không dùng thật | Mất giá trị, tưởng đã dùng | Trường **Ra** phải là artifact tồn tại được; QC chạy trường **Kiểm** như một hạng mục DoD |
| Model yếu bỏ qua bước kiểm kê | Mất toàn bộ giá trị | R8 chặn ở QC; `PHASE_TABLE` nhắc mỗi lần chạy `next` |
| Nạp skill thừa vì fail-open | Tốn token, lạc đề | QC đòi **dấu vết thật** cho mỗi dòng `DÙNG`; không có dấu vết → sửa lại thành `KHÔNG` kèm lý do |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Toàn bộ suite | `python3 -m unittest discover tests` | OK, tổng ≥ 215 test |
| Q2 | Script trên máy thật | `python3 scripts/skill_inventory.py` | In 7 skill (1 user + 6 plugin), có dòng nhắc built-in, exit 0 |
| Q3 | Lọc scope + cache | `python3 -m unittest test_skill_inventory` | ≥8 test OK, gồm 1 test plugin `scope: project` của project khác và 1 test 2 version trong cache |
| Q4 | Log service | Xoá quyền đọc `installed_plugins.json` giả rồi chạy | Có dòng ⚠️ kèm timestamp, exit 0; `TDQ_LOG=0` thì stderr rỗng |
| Q5 | Lint R8 | `python3 -m unittest test_doc_lint` · `python3 scripts/doc_lint.py skills portable docs/tdq/spec` | Fixture thiếu §3b → R8 báo lỗi; fixture đủ → im; repo thật exit 0 (spec cũ đã miễn trừ) |
| Q6 | Trần token | `python3 -m unittest test_token_budget test_skill_shape` | Xanh; `tdq-intake` ≤120 dòng, reference mới ≤200 dòng, `next` ≤20 dòng |
| Q7 | Phase table đồng bộ | `python3 -m unittest test_phase_table` | `phases.md` (skills + portable) khớp `PHASE_TABLE` |
| Q8 | Portable đồng bộ | `python3 -m unittest test_portable_sync test_docs_consistency` | Xanh; version ↔ changelog khớp |
| Q9 | Rà bảo mật script | Skill `security-review` trên diff của `skill_inventory.py` | Không phát hiện lỗi mức cao; phát hiện thì thêm task fix và sửa |
| Q10 | Thử bằng model yếu | Đưa `references/skill-inventory.md` + khuôn §3b cho một lượt đọc "chỉ làm theo chữ" | Điền được bảng mà không cần suy luận ngoài văn bản; chỗ nào phải đoán → viết lại chỗ đó |
| Q11 | Đóng gói | `claude plugin validate . --strict` | PASS, version 0.3.3 |
| Q12 | Không hồi quy hook | `python3 -m unittest test_stop_gate test_turn_snapshot test_e2e_chain` | Xanh — request này không đụng hook |
| Q13 | Hợp đồng skill khớp | `python3 scripts/doc_lint.py --pair docs/tdq/spec/<slug>.md docs/tdq/plan/<slug>.md` | exit 0: mọi `DÙNG` ở §3b có khối đủ 6 trường; test có 1 cặp thiếu trường → exit 1 nêu đúng tên trường |
| Q14 | Hợp đồng được thi hành thật | Chạy trường **Kiểm** của từng khối trong plan của chính request này | Mỗi khối cho ra artifact ghi ở trường **Ra**; không có → sửa §3b thành `KHÔNG` kèm lý do rồi chạy lại Q13 |

**DoD:** đủ 13 đầu ra ở §2 · Q1–Q14 PASS có bằng chứng trong `docs/tdq/qc/<slug>.md` ·
plan tick đủ 100% · report ≤50 dòng · working log đã append · plugin 0.3.3 cài lại được.

## 7. Câu hỏi còn mở

(RỖNG)
