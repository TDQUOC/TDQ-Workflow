# Danh mục luật hiện có của bộ workflow TDQ

Ngày: 2026-08-17 · Request: 2026-08-17-2121-toi-uu-context-workflow
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## 1. File này là gì

Bản kiểm kê MỌI dòng mang tính mệnh lệnh trong `skills/`, mỗi dòng một mã `L###` kèm
`file:dòng` nguồn. Đây là **lưới an toàn** cho mọi việc tối ưu sau này: muốn rút gọn hay
dịch bộ skill sang tiếng Anh thì phải chứng minh được từng dòng dưới đây vẫn còn hiệu lực,
chứ không dựa vào cảm giác "đọc thấy vẫn đủ ý".

## 2. Cách trích — và giới hạn của cách trích

Tiêu chí máy: dòng không rỗng, không phải heading, không nằm trong khối mã, và chứa ít
nhất một dấu mệnh lệnh (`BẮT BUỘC`, `CẤM`, `PHẢI`, `KHÔNG`, `LUÔN`, `DỪNG`, `NGAY`,
`chỉ được`, `tuyệt đối`, `mặc định`…).

Ba giới hạn phải nói thẳng, vì chúng quyết định file này dùng được tới đâu:

1. **Một luật có thể trải nhiều dòng** → bị tách thành nhiều mã `L###`. Số dòng ở đây
   KHÔNG phải số luật độc lập, nó là số *điểm neo kiểm được*.
2. **Luật viết không có dấu mệnh lệnh sẽ lọt lưới.** Ví dụ câu kể ngầm định nghĩa vụ.
   Nên đây là chặn dưới, không phải bản đầy đủ tuyệt đối.
3. **Trích theo `file:dòng` nên sửa file là lệch số dòng.** `tests/test_luat_skill.py`
   khoá bằng NỘI DUNG chứ không bằng số dòng, chính vì lý do này.
4. **Có dương tính giả.** Dấu mệnh lệnh nằm trong ô tiêu đề bảng cũng bị bắt — ví dụ
   `L166` là dòng tiêu đề `| Ca | Vì sao cấm gộp |`, không phải một luật. Nên 329 là
   **cận trên** của số điểm neo, và mọi kết luận rút từ file này phải đọc là "không
   nhiều hơn 329", không được đọc là "đúng 329 luật".

## 2b. Cột `neo bản mới` (thêm 2026-08-19)

Cột thứ tư để dành cho việc viết lại bộ skill sang tiếng Anh. Ô rỗng nghĩa là luật vẫn
đang mang câu tiếng Việt ở cột `nội dung`, và `tests/test_luat_skill.py` dò đúng câu đó.
Viết lại một luật thì chép đoạn đầu của câu MỚI vào cột này — từ lúc đó lưới dò theo
chữ mới, chữ cũ được phép biến mất.

Hai hàng rào đi kèm, nếu không thì cột này thành cửa hậu để tháo lưới:

- Mã mang nhãn `user-facing` ở [ranh-gioi-luat.md](ranh-gioi-luat.md) CẤM có neo mới —
  đó là những dòng phải giữ nguyên tiếng Việt.
- Neo mới phải dài ít nhất 40 ký tự, bằng đúng ngưỡng của neo cũ, để không khớp bừa.

Chép neo mới thì chép NGUYÊN đoạn đầu của dòng trong file, kể cả ký hiệu markdown như
`**`. Bỏ dấu sao đi là 40 ký tự đầu lệch và lưới báo mất luật dù luật vẫn nằm đó — lỗi
này đã gặp thật lúc thử nghiệm ở T2.6.

## 3. Bảng luật

| mã | nguồn | nội dung | neo bản mới |
|---|---|---|---|
| L001 | `skills/tdq-build/SKILL.md:13` | Vào build NGAY trong turn user duyệt plan, rồi chạy end-to-end trong MỘT turn.** Không | - **Enter build IN THE SAME TURN the user approves the plan, then run end-to-end in ONE |
| L002 | `skills/tdq-build/SKILL.md:20` | (message mô tả thay đổi, KHÔNG push, liệt kê commit đó trong report). | commit in the report). Stop and ask only for: a spec/plan scope change, destructive or |
| L003 | `skills/tdq-build/SKILL.md:24` | `- [x]` TRƯỚC khi bắt task sau. Cấm gom tick cuối turn. Ba trạng thái: `[ ]` chưa làm · | `- [x]` BEFORE the next task starts. Never batch ticks at the end of a turn. Three states: |
| L004 | `skills/tdq-build/SKILL.md:30` | `eNm` các task chưa xong. Giữ nguyên khi tick, không chấm lại giữa chừng, và nó KHÔNG | the sum of `eNm` over unfinished tasks. Keep it as-is when ticking, do not re-score midway, |
| L005 | `skills/tdq-build/SKILL.md:33` | Red → green.** Mỗi task: chạy/viết check trước (phải fail), rồi code, rồi chạy lại đến pass. | - **Red → green.** Every task: run/write the check first (it must fail), then code, then rerun |
| L006 | `skills/tdq-build/SKILL.md:56` | Nhận báo cáo thì `kiem` rồi `hop`, tick `[x]` NGAY, `don`, rồi quay lại `cum`. | On receiving a report, run `kiem` then `hop`, tick `[x]` IMMEDIATELY, `don`, then back to |
| L007 | `skills/tdq-build/SKILL.md:57` | Mặc định là GIAO. Chỉ được giữ task lại cho mình khi khớp đúng 1 trong 4 nhóm lý do | `cum`. The default is DELEGATE. You may keep a task only when it matches exactly one group |
| L008 | `skills/tdq-build/SKILL.md:61` | [references/team-mode.md](references/team-mode.md) — **BẮT BUỘC mở đọc trước khi | Full rules (decision table, delegation prompt template, ĐÚNG/SAI examples, self-check): |
| L009 | `skills/tdq-build/SKILL.md:63` | phân công; cấm làm theo trí nhớ.** | assigning; working from memory is banned.** |
| L010 | `skills/tdq-build/SKILL.md:64` | Mode là thứ USER đã nói lúc duyệt. Thiếu mode, hoặc bạn nghĩ mode khác hợp hơn → **DỪNG và HỎI**. | The mode is what the USER said at approval. Missing mode, or you think another mode fits |
| L011 | `skills/tdq-build/SKILL.md:70` | `- [~]` chỉ dành cho task LEADER tự làm và vẫn chỉ được đúng một. | allowed); `- [~]` is only for a task the LEADER does personally, and still only one. |
| L012 | `skills/tdq-build/SKILL.md:81` | để dành, chạy đúng 1 lần ở QC. Dán kết quả thật, cấm tuyên bố xong khi chưa chạy. | saved for exactly one run at QC. Paste the real output; never declare done unrun. |
| L013 | `skills/tdq-build/SKILL.md:82` | Đổi `- [~]` thành `- [x]` cho task đó trong plan NGAY — mode `subagent` thì main | 6. Turn `- [~]` into `- [x]` for that task in the plan IMMEDIATELY — in mode `subagent` the |
| L014 | `skills/tdq-build/SKILL.md:98` | [references/qc.md](references/qc.md) mục `## Ba bước thi hành`. **BẮT BUỘC mở file đó và | [references/qc.md](references/qc.md) under `## Ba bước thi hành`. **BẮT BUỘC mở file đó và |
| L015 | `skills/tdq-build/SKILL.md:99` | đọc hết ba bước trước khi chạy hạng mục đầu tiên; cấm làm theo trí nhớ.** Cùng file đó có | file and read all three steps before running the first item; working from memory is banned.** |
| L016 | `skills/tdq-build/SKILL.md:108` | BẮT BUỘC mở file đó và đọc hết bốn bước trước khi viết report; cấm làm theo trí nhớ.** | The four execution steps — from writing the report to asking the user about a commit — live in |
| L017 | `skills/tdq-build/references/qc.md:16` | Đây là toàn bộ Phần B của [SKILL.md](../SKILL.md) — chuyển về đây để thân skill không phải | This is the whole of Part B of [SKILL.md](../SKILL.md) — moved here so the skill body does not |
| L018 | `skills/tdq-build/references/qc.md:17` | nạp nhánh này mỗi lần gọi. Vào phase `qc` là **bắt buộc** đọc hết ba bước dưới đây trước | carry this branch on every call. On entering phase `qc` you **must** read all three steps below |
| L019 | `skills/tdq-build/references/qc.md:18` | khi chạy hạng mục đầu tiên; cấm làm theo trí nhớ. | before running the first item; working from memory is banned. |
| L020 | `skills/tdq-build/references/qc.md:34` | mà bản fix có thể làm hỏng, cộng full suite. Trần 3 vòng; vượt trần thì DỪNG, báo user. | item the fix could have broken, plus the full suite. Cap of 3 rounds; over the cap, STOP and |
| L021 | `skills/tdq-build/references/qc.md:53` | chứa node bị ảnh hưởng. Node không có test → ghi `KHÔNG CÓ TEST: <node>` vào file | module holding the affected node. A node with no test → write `KHÔNG CÓ TEST: <node>` into the |
| L022 | `skills/tdq-build/references/qc.md:54` | QC; đó là nợ kỹ thuật phải nêu trong report, không được tính là PASS. | QC file; that is technical debt to raise in the report and must not count as PASS. |
| L023 | `skills/tdq-build/references/qc.md:55` | QC-F3 — ràng buộc kiến trúc: mỗi dòng trong khối "Ràng buộc kiến trúc phải giữ" ở | - QC-F3 — architectural constraints: every line of the "Ràng buộc kiến trúc phải giữ" block in |
| L024 | `skills/tdq-build/references/qc.md:60` | đáp án. Không chạm mã nguồn → ghi `KHÔNG ÁP DỤNG — không sửa file code`. | answer. No source file touched → write `KHÔNG ÁP DỤNG — không sửa file code`. |
| L025 | `skills/tdq-build/references/qc.md:68` | Log service: bật mặc định, có timestamp, tắt/giảm mức được qua config. | - Log service: on by default, timestamped, switchable off/down through config. |
| L026 | `skills/tdq-build/references/qc.md:71` | ở trường `Ra` phải tồn tại. Không có artifact → sửa spec §3b dòng đó thành `KHÔNG` + | artifact in its `Ra` field must exist. No artifact → change that spec §3b line to `KHÔNG` plus |
| L027 | `skills/tdq-build/references/qc.md:113` | Lặp đến khi mọi hạng mục PASS. **Trần 3 vòng** — vượt trần thì DỪNG và báo user. | 4. Repeat until every item PASSes. **Cap of 3 rounds** — over the cap, STOP and tell the user. |
| L028 | `skills/tdq-build/references/report-template.md:5` | Đây là toàn bộ Phần C của [SKILL.md](../SKILL.md) — chuyển về đây để thân skill không phải | This is the whole of Part C of [SKILL.md](../SKILL.md) — moved here so the skill body does not |
| L029 | `skills/tdq-build/references/report-template.md:6` | nạp nhánh này mỗi lần gọi. Vào phase `report` là **bắt buộc** đọc hết bốn bước dưới đây | carry this branch on every call. On entering phase `report` you **must** read all four steps |
| L030 | `skills/tdq-build/references/report-template.md:7` | trước khi viết report; cấm làm theo trí nhớ. | below before writing the report; working from memory is banned. |
| L031 | `skills/tdq-build/references/report-template.md:10` | Viết `docs/tdq/reports/<slug>.md` — tiếng Việt, KHÔNG giới hạn cứng số dòng, khuyến | 7. Write `docs/tdq/reports/<slug>.md` — in the user's document language, with NO hard line |
| L032 | `skills/tdq-build/references/report-template.md:11` | nghị ~10-20 dòng. Khuôn: mục `## Khuôn` cùng file này. Bảng thời gian là **bắt buộc**: | limit; ~10-20 lines recommended. Template: section `## The report shape` in this file. |
| L033 | `skills/tdq-build/references/report-template.md:25` | Hỏi user có commit không** — bắt buộc, không tự commit thành quả cuối (ngoại lệ duy | 10. **Ask the user whether to commit** — mandatory; never commit the final result on your own |
| L034 | `skills/tdq-build/references/report-template.md:26` | nhất: commit gỡ chặn giữa build theo Luật cứng, phải liệt kê trong report). Gộp chung | (the single exception: an unblocking commit during build under the Hard rules, which must |
| L035 | `skills/tdq-build/references/report-template.md:44` | User đồng ý → message mô tả thay đổi, KHÔNG chứa "generated with …" hay trailer AI; | User agrees → a message describing the change, containing NO "generated with …" and no AI |
| L036 | `skills/tdq-build/references/report-template.md:10` | `docs/tdq/reports/<slug>.md` — tiếng Việt, KHÔNG giới hạn cứng số dòng. Khuyến nghị | `docs/tdq/reports/<slug>.md` — in the user's document language, with NO hard line limit. |
| L037 | `skills/tdq-build/references/report-template.md:79` | chỉ tính lúc máy làm. Lệch lớn ở một phase nghĩa là phase đó tốn thời gian CHỜ, không phải | user's approval, **model time** counts only machine work. A large gap on one phase means that |
| L038 | `skills/tdq-build/references/report-template.md:87` | Dòng "Giới hạn" không được bỏ trống khi còn việc dang dở — nói thật, không giấu. | - The "Giới hạn" line must not be left empty while work remains unfinished — tell the truth, hide |
| L039 | `skills/tdq-build/references/rules/chung.md:14` | SonarQube 10/15(25); ESLint để 20, Microsoft CA1502 để 25 nên phải chốt một mức. | defaults to 10/15(25); ESLint uses 20 and Microsoft CA1502 uses 25, so one level must be |
| L040 | `skills/tdq-build/references/rules/chung.md:21` | Mọi lần viết hoặc sửa code, bất kể ngôn ngữ — kể cả script nhỏ và test. | - Every time you write or change code, in any language — small scripts and tests included. |
| L041 | `skills/tdq-build/references/rules/chung.md:28` | ba nhóm còn lại. Ba câu hỏi bắt buộc trước khi nộp code: | BEFORE the other three. Three mandatory questions before submitting code: |
| L042 | `skills/tdq-build/references/rules/chung.md:30` | Tên nói đúng việc chưa?** Tên hàm/biến đọc lên phải ra đúng việc nó làm. | 1. **Does the name say what it does?** A function/variable name must read as the work it does. |
| L043 | `skills/tdq-build/references/rules/chung.md:39` | Hàm vượt ngưỡng → tách hàm nhỏ, KHÔNG nới ngưỡng tại chỗ. | - A function over the threshold → split it, NEVER widen the threshold in place. |
| L044 | `skills/tdq-build/references/rules/chung.md:40` | Cách ghi đè ngưỡng: chỉ được ghi đè bằng một dòng trong spec của request (kèm số mới | - How to override a threshold: only by one line in the request's spec (with the new number and |
| L045 | `skills/tdq-build/references/rules/chung.md:41` | và lý do), vì default mỗi tool mỗi khác; cấm ghi đè bằng thoả thuận miệng trong chat. | the reason), because every tool's default differs; overriding by a spoken agreement in chat |
| L046 | `skills/tdq-build/references/rules/chung.md:51` | lỗi phải được xử lý hoặc log rồi ném tiếp — cấm `catch` rỗng. | errors must be handled or logged and rethrown — an empty `catch` is banned. |
| L047 | `skills/tdq-build/references/rules/chung.md:53` | cấm ghi PASS. | linter, write "not checked yet" and never write PASS. |
| L048 | `skills/tdq-build/references/rules/cpp.md:26` | Interface phải nói rõ ý**: tham số con trỏ không được phép null → dùng kiểu như | 1. **An interface must state its intent**: a pointer parameter that may not be null → use a |
| L049 | `skills/tdq-build/references/rules/cpp.md:39` | thay cho 15; vượt 25 vẫn phải tách hàm, không nới tiếp. | the widened level of 25 instead of 15; past 25 the function still gets split, never widened |
| L050 | `skills/tdq-build/references/rules/csharp.md:23` | viết `camelCase`; tên phải nêu đúng việc, không viết tắt khó hiểu. | parameters use `camelCase`; a name must state the work, with no cryptic abbreviations. |
| L051 | `skills/tdq-build/references/rules/csharp.md:31` | Cyclomatic ≤ 10, cognitive ≤ 15 mỗi method — theo `chung.md`; C# KHÔNG thuộc nhóm | - Cyclomatic ≤ 10, cognitive ≤ 15 per method — per `chung.md`; C# is NOT part of the C family |
| L052 | `skills/tdq-build/references/rules/csharp.md:33` | Mức analyzer: hai category Security và Reliability không được hạ dưới `warning`; | - Analyzer severity: the Security and Reliability categories must never drop below `warning`; |
| L053 | `skills/tdq-build/references/rules/csharp.md:34` | muốn đổi phải ghi vào spec của request, sửa trong `.editorconfig`. | changing that has to be recorded in the request's spec and edited in `.editorconfig`. |
| L054 | `skills/tdq-build/references/rules/go.md:24` | exported viết hoa chữ đầu và phải có doc comment bắt đầu bằng chính tên đó. | identifier is capitalised and must carry a doc comment starting with that very name. |
| L055 | `skills/tdq-build/references/rules/go.md:35` | Bộ linter tối thiểu phải bật: errcheck, govet, staticcheck (theo Uber Go Style Guide). | - The minimum linter set that must be enabled: errcheck, govet, staticcheck (per the Uber Go |
| L056 | `skills/tdq-build/references/rules/go.md:41` | Kiểm `err` NGAY sau lời gọi trả về nó; trả lỗi lên trên thì kèm ngữ cảnh cho biết | 2. Check `err` IMMEDIATELY after the call returning it; when passing an error up, wrap it with |
| L057 | `skills/tdq-build/references/rules/html.md:20` | Thẻ phải nói đúng vai trò**: dùng phần tử ngữ nghĩa đúng việc thay vì chồng `div`; | 1. **A tag must state its role**: use the semantic element for the job instead of stacking |
| L058 | `skills/tdq-build/references/rules/html.md:26` | Trùng lặp là mâu thuẫn ý**: `id` phải duy nhất (`id-unique`), thuộc tính không | 3. **Duplication is contradictory intent**: `id` must be unique (`id-unique`), attributes must |
| L059 | `skills/tdq-build/references/rules/html.md:33` | Trang mới bắt buộc doctype HTML5 (`doctype-html5`) và doctype đứng đầu file | - A new page must use the HTML5 doctype (`doctype-html5`) with the doctype first in the file |
| L060 | `skills/tdq-build/references/rules/html.md:39` | Không đặt `<script>` trong `<head>` trừ khi bắt buộc (`head-script-disabled`) — | 2. Do not put `<script>` in `<head>` unless required (`head-script-disabled`) — render-blocking |
| L061 | `skills/tdq-build/references/rules/index.md:22` | Định nghĩa nhóm lỗi Intentionality, ba câu hỏi bắt buộc và số 59,6% nằm trong | The definition of the Intentionality group, the three mandatory questions and the 59,6% figure |
| L062 | `skills/tdq-build/references/rules/index.md:50` | Tầng theo việc**: nạp đúng file ngôn ngữ khớp đuôi file đang sửa; cấm nạp cả 7 | 2. **Per-job tier**: load exactly the language file matching the extension being edited; |
| L063 | `skills/tdq-build/references/rules/index.md:53` | cấm tự bịa rule hay mượn rule ngôn ngữ khác. | inventing a rule or borrowing another language's rules is banned. |
| L064 | `skills/tdq-build/references/rules/index.md:55` | Linter không có trên máy → ghi "chưa kiểm được", cấm ghi PASS, cấm tự cài đặt. | Linter missing on the machine → write "not checked yet", never write PASS, never install it |
| L065 | `skills/tdq-build/references/rules/python.md:9` | ruff — linter mặc định của TDQ cho Python (chạy các nhóm check kiểu F/E/B); URL chính | - ruff — TDQ's default Python linter (runs the F/E/B style check groups); its official URL is |
| L066 | `skills/tdq-build/references/rules/python.md:22` | Tên sai chuẩn hoặc mơ hồ**: hàm/biến phải `snake_case`, class `PascalCase`, hằng | 1. **Off-standard or vague names**: functions/variables must be `snake_case`, classes |
| L067 | `skills/tdq-build/references/rules/python.md:34` | (`line-length`) và phải ghi số đã chọn vào spec của request. | (`line-length`) and must record the chosen number in the request's spec. |
| L068 | `skills/tdq-build/references/rules/python.md:43` | Hàm public có docstring 1 dòng nêu việc; hàm dùng nội bộ thì tên phải tự giải thích. | 5. Public functions carry a one-line docstring stating the job; internal helpers must be |
| L069 | `skills/tdq-build/references/rules/rust.md:8` | Rust KHÔNG có "Core Guidelines"** tương đương C++: triết lý Rust là để compiler + | **Rust has NO "Core Guidelines"** equivalent to C++: the Rust philosophy is to let the |
| L070 | `skills/tdq-build/references/rules/rust.md:22` | `SCREAMING_SNAKE_CASE` — compiler tự warn khi lệch; tên phải nêu đúng việc. | constants `SCREAMING_SNAKE_CASE` — the compiler warns on drift by itself; a name must state |
| L071 | `skills/tdq-build/references/rules/rust.md:33` | Cyclomatic ≤ 10, cognitive ≤ 15 mỗi hàm — theo `chung.md`; Rust KHÔNG thuộc nhóm họ C | - Cyclomatic ≤ 10, cognitive ≤ 15 per function — per `chung.md`; Rust is NOT in the C family |
| L072 | `skills/tdq-build/references/rules/rust.md:35` | Mức warning: code nộp phải sạch warning của compiler và của `cargo clippy` ở mức | - Warning level: submitted code must be free of compiler warnings and of default-level |
| L073 | `skills/tdq-build/references/rules/rust.md:36` | mặc định; muốn allow lint nào phải ghi lý do vào spec của request. | `cargo clippy` warnings; allowing any lint requires a reason in the request's spec. |
| L074 | `skills/tdq-build/references/rules/rust.md:42` | ở biên nơi gọi; cấm `unwrap` ngoài test. | calling boundary; `unwrap` outside tests is banned. |
| L075 | `skills/tdq-build/references/rules/rust.md:45` | Chạy `cargo clippy` và sửa hết warning; compiler warning cũng phải về 0. | 5. Run `cargo clippy` and fix every warning; compiler warnings must also reach 0. |
| L076 | `skills/tdq-build/references/rules/them-ngon-ngu.md:14` | Task phải viết/sửa file có đuôi KHÔNG nằm trong bảng của `index.md`, và user scope | - A task must write/change a file whose extension is NOT in `index.md`'s table, and user scope |
| L077 | `skills/tdq-build/references/rules/them-ngon-ngu.md:21` | Rule mới viết ra phải trả lời được 3 câu hỏi Intentionality của `chung.md`, | 1. A new rule must be able to answer `chung.md`'s 3 Intentionality questions; do not copy a |
| L078 | `skills/tdq-build/references/rules/them-ngon-ngu.md:23` | Nguồn phải có thật**: mọi URL đưa vào rule phải nằm trong file research của | 2. **Sources must be real**: every URL put into a rule must exist in the request's research |
| L079 | `skills/tdq-build/references/rules/them-ngon-ngu.md:24` | request; chưa tìm được nguồn thì ghi "chưa có nguồn", cấm bịa link. | file; where no source was found, write "chưa có nguồn" — inventing a link is banned. |
| L080 | `skills/tdq-build/references/rules/them-ngon-ngu.md:25` | Rule không nói được "vi phạm thì đo bằng gì" là rule chết — mỗi luật phải gắn | 3. A rule that cannot say "how a violation is measured" is a dead rule — every rule attaches to |
| L081 | `skills/tdq-build/references/rules/them-ngon-ngu.md:34` | thức của ngôn ngữ nêu mức khác, và phải ghi rõ nguồn đó. | language's official source states a different level, and cite that source. |
| L082 | `skills/tdq-build/references/rules/them-ngon-ngu.md:47` | DỪNG chờ user duyệt.** User chưa duyệt thì không ghi file rule ra bất kỳ đâu. | 4. **STOP and wait for the user to approve.** Until the user approves, the rule file is written nowhere. |
| L083 | `skills/tdq-build/references/rules/typescript-js.md:26` | Promise bỏ lơ lửng là nuốt lỗi**: mọi Promise phải được `await`, `return`, hoặc | 2. **A floating Promise swallows errors**: every Promise must be `await`ed, `return`ed, or |
| L084 | `skills/tdq-build/references/rules/typescript-js.md:30` | `@ts-ignore`/`@ts-expect-error` trần bị `ban-ts-comment` chặn — phải kèm mô tả lý do. | `@ts-ignore`/`@ts-expect-error` is blocked by `ban-ts-comment` — it must carry a reason. |
| L085 | `skills/tdq-build/references/rules/typescript-js.md:35` | ESLint mặc định 20 nên phải chỉnh về 10 trong config, không dùng default. | defaults to 20, so set it back to 10 in the config; never keep the default. |
| L086 | `skills/tdq-build/references/rules/typescript-js.md:43` | Khai kiểu rõ ở biên (tham số, giá trị trả về của hàm export); cấm `any` trần. | 2. Declare types at the boundary (parameters and return values of exported functions); a bare |
| L087 | `skills/tdq-build/references/rules/typescript-js.md:46` | cấm gọi rồi lờ kết quả. | deliberate drop — calling and ignoring the result is banned. |
| L088 | `skills/tdq-build/references/rules/typescript-js.md:47` | Directive `@ts-` nào cũng phải có mô tả lý do ngay sau directive. | 4. Every `@ts-` directive must carry a reason right after the directive. |
| L089 | `skills/tdq-build/references/team-mode.md:5` | Bạn là LEADER. Agent con là ĐỘI của bạn. Mặc định là GIAO; giữ task lại cho mình | You are the LEADER. Sub-agents are your TEAM. The default is DELEGATE; keeping a task for |
| L090 | `skills/tdq-build/references/team-mode.md:6` | phải có cớ nằm trong bảng tra bên dưới, và cái cớ đó bị máy kiểm. | yourself needs a reason from the lookup table below, and that reason is machine-checked. |
| L091 | `skills/tdq-build/references/team-mode.md:27` | Mode đội KHÔNG có nghĩa mọi task đều phải giao. Nó có nghĩa: **task nào tách được thì | Team mode does NOT mean every task must be delegated. It means: **whatever can be split must |
| L092 | `skills/tdq-build/references/team-mode.md:28` | phải tách**, phần còn lại leader tự làm — như một trưởng nhóm thật, không phải một | be split**, and the leader does the rest — like a real team lead, neither someone who hoards |
| L093 | `skills/tdq-build/references/team-mode.md:29` | người ôm hết việc cũng không phải một người chia bừa. | all the work nor someone who scatters it blindly. |
| L094 | `skills/tdq-build/references/team-mode.md:40` | `phan-cong` đọc TOÀN BỘ plan (không phải từng task một), dựng vùng file của mỗi task | `phan-cong` reads the ENTIRE plan (not one task at a time), builds each task's file region from |
| L095 | `skills/tdq-build/references/team-mode.md:60` | \| **mặc định: GIAO** \| **không khớp 5 dòng trên** \| `python3 scripts/tdq_team.py kiem-ke` exit 0 \| | \| **mặc định: GIAO** \| **matches none of the 5 rows above** \| `python3 scripts/tdq_team.py kiem-ke` exit 0 \| |
| L096 | `skills/tdq-build/references/team-mode.md:73` | python3 scripts/tdq_team.py kiem T1.1 # dò xung đột, KHÔNG đụng repo | python3 scripts/tdq_team.py kiem T1.1      # probe for conflicts, does NOT touch the repo |
| L097 | `skills/tdq-build/references/team-mode.md:80` | này nhanh hơn `main`, không phải vì agent con chạy nhanh hơn bạn. | mode beats `main`, not because sub-agents type faster than you. |
| L098 | `skills/tdq-build/references/team-mode.md:93` | VÙNG FILE: scripts/alpha.py, tests/test_alpha.py — CẤM sửa file ngoài danh sách này |  |
| L099 | `skills/tdq-build/references/team-mode.md:94` | TEST: <lệnh kiểm của task> — phải đỏ trước, xanh sau |  |
| L100 | `skills/tdq-build/references/team-mode.md:102` | Kèm đường dẫn spec và plan trong phần thân prompt. Agent con KHÔNG đọc được hội thoại | Include the spec and plan paths in the prompt body. A sub-agent CANNOT read this conversation — |
| L101 | `skills/tdq-build/references/team-mode.md:103` | này — thiếu trường nào là nó phải đoán, và đoán sai thì bạn trả giá lúc merge. | a missing field means it has to guess, and a wrong guess is paid for at merge time. |
| L102 | `skills/tdq-build/references/team-mode.md:165` | Trước khi kết thúc phase implement, tất cả phải đúng: | Before ending phase implement, all of these must hold: |
| L103 | `skills/tdq-build/references/team-mode.md:177` | phải có mặt trong report. Tỉ lệ giao thấp mà không có lý do trong bảng tra nghĩa là bạn | total?** That number must appear in the report. A low delegation ratio with no reason from the |
| L104 | `skills/tdq-build/references/team-mode.md:178` | đã lách luật của user — user chọn mode đội là để có một đội, không phải một lời hứa. | lookup table means you worked around the user's rule — the user picked team mode to get a team, |
| L105 | `skills/tdq-check-status/SKILL.md:8` | Nạp [tdq-conventions](../tdq-conventions/SKILL.md). Skill này KHÔNG thuộc phase nào: gọi | Load [tdq-conventions](../tdq-conventions/SKILL.md). This skill belongs to NO phase |
| L106 | `skills/tdq-check-status/SKILL.md:18` | Cấm tuyệt đối** `tdq_state.py` với lệnh con `init` hay `reset`, cấm xoá hay ghi đè | **Absolutely banned:** `tdq_state.py` with subcommand `init` or `reset`, and equally banned is |
| L107 | `skills/tdq-check-status/SKILL.md:21` | Chỉ được chạy lệnh vá thuộc đúng hai họ: `tdq_state.py set …` và `tdq_state.py approve …`. | - Only patch commands from exactly two families may run: `tdq_state.py set …` and |
| L108 | `skills/tdq-check-status/SKILL.md:25` | Kết luận `CẦN USER QUYẾT` thì DỪNG, trình câu hỏi, cấm tự đoán ý user. | Verdict `CẦN USER QUYẾT` → STOP, present the question; guessing what the user wants is banned. |
| L109 | `skills/tdq-check-status/SKILL.md:44` | ý nghĩa và giới hạn của nó. Bảng đó là nguồn duy nhất; cấm tự nghĩ thêm chẩn đoán. | its meaning and its limits. That table is the only source; inventing extra diagnoses is |
| L110 | `skills/tdq-check-status/SKILL.md:49` | "Chạy các lệnh vá này rồi tiếp tục?" **DỪNG chờ user.** | `VÁ RỒI TIẾP TỤC` → print the `## Lệnh vá đề xuất` block and ask the user exactly one |
| L111 | `skills/tdq-check-status/SKILL.md:52` | conventions, **DỪNG chờ user**. Cấm chạy lệnh vá nào. | template of conventions, **STOP and wait for the user**. Run no patch command at all. |
| L112 | `skills/tdq-check-status/SKILL.md:55` | Lệnh nào không thuộc hai họ `set`/`approve` thì KHÔNG chạy và báo lại — đó là lỗi của | A command outside the two families `set`/`approve` must NOT be run; report it instead — |
| L113 | `skills/tdq-check-status/SKILL.md:56` | bộ dò, không phải việc để tự sửa tay. | that is a bug in the detector, not something to fix by hand. |
| L114 | `skills/tdq-check-status/SKILL.md:63` | trình lại đúng cổng đó rồi DỪNG chờ user duyệt. | means re-presenting that exact gate, then STOPPING for the user's approval. |
| L115 | `skills/tdq-check-status/references/bang-lech.md:11` | Ba mức: `ok` chỉ để biết · `canh-bao` nên vá trước khi đi tiếp · `chan` phải để user quyết. | Three levels: `ok` for information only · `canh-bao` should be patched before moving on · |
| L116 | `skills/tdq-check-status/references/bang-lech.md:13` | Cột lệnh vá là MẪU. Chỗ viết hoa gạch dưới phải thay bằng giá trị thật trước khi chạy. | The patch-command column is a TEMPLATE. Every UPPERCASE_UNDERSCORED slot must be replaced |
| L117 | `skills/tdq-check-status/references/bang-lech.md:20` | \| D1 \| không đọc được request nào (không có, phase = idle, hoặc state hỏng) \| ok \| Đĩa trống thì mở request mới bằng tdq-intake; đĩa còn spec/p… |  |
| L118 | `skills/tdq-check-status/references/bang-lech.md:22` | \| D3 \| sha256 của spec lệch với lúc duyệt (plan lệch chỉ là `ok`) \| chan \| File đã sửa sau khi duyệt — cần user duyệt lại, cấm tự approve. \| —… |  |
| L119 | `skills/tdq-check-status/references/bang-lech.md:36` | là chuyện hằng ngày. Đổi phạm vi plan phải nhìn bằng mắt, bảng này không bắt được. | the plan is an everyday event. A change in the plan's SCOPE has to be seen by eye — this |
| L120 | `skills/tdq-check-status/references/bang-lech.md:46` | D12 chỉ có ở mode `subagent`. Dấu `[>]` là "đã giao cho agent con", KHÔNG phải lỗi — | - D12 only exists in mode `subagent`. The mark `[>]` means "handed to a sub-agent", it is NOT |
| L121 | `skills/tdq-conventions/SKILL.md:37` | Cuối turn có đổi repo: **bắt buộc** chạy lệnh đóng sổ | A turn that changed the repo MUST end with the closing command |
| L122 | `skills/tdq-conventions/SKILL.md:39` | — lint đúng file → append working log → set phase → graphify. **Cấm Edit/Read rồi tự | — lint those files → append the working log → set phase → graphify. **Never Edit/Read the working log and append by |
| L123 | `skills/tdq-conventions/SKILL.md:41` | lệnh", không phải "gọi lệnh khác để né"). Lệnh này phải là **hành động cuối** của turn, | dodge it". This command is the **last action** of the turn; it runs BEFORE the closing chat block |
| L124 | `skills/tdq-conventions/SKILL.md:44` | của turn. Cấm gọi rỗng: mỗi lần gọi phải kèm `--files` và `--log` của việc vừa xong. | only the LAST call must be the final action. Never call it empty: every call carries `--files` and `--log` |
| L125 | `skills/tdq-conventions/SKILL.md:47` | việc, lỗi tool) → message cuối phải in **LẠI NGUYÊN VĂN 100%** khối đó. Gồm tóm tắt, | missed work, a tool failed. The LAST message must then reprint that block **WORD FOR WORD, 100%**: |
| L126 | `skills/tdq-conventions/SKILL.md:48` | câu hỏi, ĐỦ option, dòng `➤ Duyệt:`. Đặt NGAY SAU dòng `✓ [TDQ:<MÃ>]`. Lý do: focus mode | the summary, the question, EVERY option, the approval line. Put it RIGHT AFTER the |
| L127 | `skills/tdq-conventions/SKILL.md:51` | mất sạch câu hỏi và option. Cấm rút gọn, cấm trỏ ngược. | entirely. Shortening is banned; pointing backwards is banned. |
| L128 | `skills/tdq-conventions/SKILL.md:63` | Hết ngân sách bước KHÔNG phải ngoại lệ: báo rồi làm tiếp. "Để turn sau cho gọn" cũng vậy. | Running out of step budget is NOT an exception: report it and carry on. |
| L129 | `skills/tdq-conventions/SKILL.md:71` | Bảng đầy đủ (vào khi / việc duy nhất / lệnh chuyển tiếp / xong khi / cấm): | Full table (entry condition / single job / transition command / done when / forbidden): |
| L130 | `skills/tdq-conventions/SKILL.md:79` | Cấm sửa tay `docs/tdq/state.json` và `docs/tdq/STATE.md` (mirror tự sinh, chỉ để đọc). | Hand-editing `docs/tdq/state.json` or `docs/tdq/STATE.md` is forbidden (generated mirror, read-only). |
| L131 | `skills/tdq-conventions/SKILL.md:84` | `reset` chỉ khi user đóng hẳn request. Muốn thử nghiệm workflow thì chạy vào project | `reset` only when the user closes a request for good. To experiment with the workflow, aim at a throwaway project: |
| L132 | `skills/tdq-conventions/SKILL.md:85` | rác: đặt `TDQ_PROJECT_DIR=/tmp/...` ngay trên chính lệnh đó (cấm dùng `\|\|` fallback). | put `TDQ_PROJECT_DIR=/tmp/...` on that very command (no `\\|\\|` fallback). |
| L133 | `skills/tdq-conventions/SKILL.md:90` | User duyệt bằng chat thường — không có cú pháp bắt buộc, không có gate chặn user. | The user approves in ordinary chat — no required syntax, no gate that blocks the user. |
| L134 | `skills/tdq-conventions/SKILL.md:91` | Dấu hiệu duyệt, phản ví dụ, và lệnh phải chạy: [references/approval.md](references/approval.md). | Signals, counter-examples, and the command to run: [references/approval.md](references/approval.md). |
| L135 | `skills/tdq-conventions/SKILL.md:93` | Ba luật không được phá: | Three rules that must never break, whatever else changes: |
| L136 | `skills/tdq-conventions/SKILL.md:94` | Mơ hồ → **HỎI**, tuyệt đối không suy diễn là đã duyệt. | Ambiguous wording → **ASK**; never infer that approval was given. |
| L137 | `skills/tdq-conventions/SKILL.md:118` | Ảnh user gửi kèm.** Turn có ảnh đính kèm VÀ phải ghi working log → copy ảnh vào | **Images the user attached.** A turn with attached images that must also write a working log |
| L138 | `skills/tdq-conventions/SKILL.md:130` | Search web: `tavily-primary` trước, luôn luôn. Failover và mẫu dùng nâng cao: | Web search goes through `tavily-primary` first, always. Failover and advanced patterns: |
| L139 | `skills/tdq-conventions/SKILL.md:132` | Mọi khẳng định phải có nguồn hoặc căn cứ nêu rõ. Không bịa. | Every claim needs a source or a stated basis. Never invent one. |
| L140 | `skills/tdq-conventions/SKILL.md:140` | Bảng model/effort mặc định theo vai + luật override: [references/subagent-tuning.md](references/subagent-tuning.md). | Default model/effort per role plus the override rule: [references/subagent-tuning.md](references/subagent-tuning.md). |
| L141 | `skills/tdq-conventions/SKILL.md:145` | chỉ ảnh hưởng nhẹ. Nên luật này thuộc tầng **runtime**, không phải context cost. | That is why this rule belongs to the **runtime** tier, not to context cost. |
| L142 | `skills/tdq-conventions/SKILL.md:152` | Bảng cấm gộp, luật đọc lại (mềm) + phân biệt vì LUẬT / vì QUÊN, trần output MCP, đọc vừa đủ, giao việc nặng cho subagent: | Cases where batching is banned, the (soft) re-read rule with RULE-vs-FORGOT, the MCP output ceiling |
| L143 | `skills/tdq-conventions/SKILL.md:159` | Clean code là hành vi thường trực, không phải cổng hỏi. Mọi lần viết/sửa code, tổ chức | Clean code is standing behaviour, not a gate you ask about. Every time you write or change code |
| L144 | `skills/tdq-conventions/SKILL.md:163` | Sản phẩm build ra luôn có log service bật mặc định (timestamp, đủ chi tiết debug, tắt được qua config). | Anything built ships a log service on by default (timestamps, enough detail to debug, switchable off through config). |
| L145 | `skills/tdq-conventions/SKILL.md:164` | Mỗi task trong plan có test riêng; task pass là tick `[x]` NGAY, không gom cuối turn. | Every task in a plan has its own test; a passing task is ticked `[x]` IMMEDIATELY, never batched at the end of the turn. |
| L146 | `skills/tdq-conventions/references/approval.md:4` | phải phán đoán rộng tay. | and **record it** — never to judge generously on the user's behalf. |
| L147 | `skills/tdq-conventions/references/approval.md:31` | \| `ok tôi hiểu rồi` \| phản hồi hiểu, không phải chấp thuận \| HỎI lại \| | \| `ok, I get it` (vi `ok tôi hiểu rồi`) \| acknowledges understanding, not consent \| ASK again \| |
| L148 | `skills/tdq-conventions/references/approval.md:34` | \| `duyệt spec` khi đang chờ **plan** \| sai đối tượng \| Chỉ ghi spec, KHÔNG suy ra plan \| | \| `approve the spec` while **plan** is pending \| wrong object \| Record spec only, NEVER infer plan \| |
| L149 | `skills/tdq-conventions/references/approval.md:44` | `--by` bắt buộc trên thực tế: đó là dấu vết duy nhất nối state với hội thoại. | `--by` is mandatory in practice: it is the only trace tying state back to the conversation. |
| L150 | `skills/tdq-conventions/references/approval.md:45` | Duyệt lại lần nữa không phải lỗi (idempotent, exit 0). | Approving twice is not an error (idempotent, exit 0). |
| L151 | `skills/tdq-conventions/references/clean-code.md:5` | Clean code ở bộ workflow này KHÔNG phải một cổng hỏi và KHÔNG phải một lượt chạy linter | In this workflow clean code is NOT a gate you ask about and NOT one linter run at the end of a |
| L152 | `skills/tdq-conventions/references/clean-code.md:64` | PHÁN XÉT trên dữ liệu đã đọc. Đổi cách đọc không phải sửa cách chấm. | only JUDGES data already read. Changing how it reads is not changing how it scores. |
| L153 | `skills/tdq-conventions/references/clean-code.md:67` | Đổi khuôn bảng in cũng phải sửa hàm đọc file. | the table. Changing the printed table shape forces editing the file-reading function. |
| L154 | `skills/tdq-conventions/references/clean-code.md:75` | Mỗi skill mới lại phải mở thân hàm ra sửa. | Every new skill forces the function body open again. |
| L155 | `skills/tdq-conventions/references/clean-code.md:84` | phải đoán, và đoán sai thì nổ ở chỗ khác. | guess, and a wrong guess blows up somewhere else. |
| L156 | `skills/tdq-conventions/references/clean-code.md:87` | SUY DIỄN của repo này, không phải trích Liskov — đừng dẫn nó như nguyên văn. | reading above is an INFERENCE by this repo, not a quotation of Liskov — do not cite it as her |
| L157 | `skills/tdq-conventions/references/clean-code.md:96` | một file plan bất kỳ thì phải dựng một state giả, kể cả trong test. | other plan file then means building a fake state, even in a test. |
| L158 | `skills/tdq-conventions/references/clean-code.md:103` | SAI — một hook tự `json.dump` thẳng vào `docs/tdq/state.json`. Đổi định dạng state là phải | WRONG — a hook that `json.dump`s straight into `docs/tdq/state.json`. Changing the state format |
| L159 | `skills/tdq-conventions/references/context-budget.md:21` | p90 12,3 s. Tổng thời gian tỉ lệ THẲNG với số bước, nên đây là tầng runtime, không phải | 12.3 s. Total time scales DIRECTLY with the number of steps, so this is the runtime tier, not |
| L160 | `skills/tdq-conventions/references/context-budget.md:28` | `&&`, hoặc `;` khi muốn chạy hết dù có lệnh lỗi. Cấm tách thành nhiều lượt chỉ để | command joined by `&&`, or `;` when you want them all to run even if one fails. Never split |
| L161 | `skills/tdq-conventions/references/context-budget.md:31` | đừng đọc lại file. Nhưng BẮT BUỘC đọc lại khi gặp một trong năm ca dưới đây. Luật này | context, do not re-read the file. But you MUST re-read on any of the five cases below. This |
| L162 | `skills/tdq-conventions/references/context-budget.md:34` | điều kiện. Cấm vòng `sleep` thăm dò: mỗi vòng là một bước tròn mà không thêm thông tin. | the background and wait on a condition. No `sleep` polling loop: each round is a whole step |
| L163 | `skills/tdq-conventions/references/context-budget.md:39` | Context đã bị nén — thứ còn lại là bản tóm tắt, không phải nội dung file. | Context has been compacted — what remains is a summary, not the file's content. |
| L164 | `skills/tdq-conventions/references/context-budget.md:43` | Sắp sửa chính file đó — trước khi Edit phải có nội dung mới nhất. | You are about to edit that very file — before an Edit you must hold the latest content. |
| L165 | `skills/tdq-conventions/references/context-budget.md:48` | agent có context riêng, nó phải tự đọc. | sub-agent — an agent has its own context and must read for itself. |
| L166 | `skills/tdq-conventions/references/context-budget.md:83` | \| Ca \| Vì sao cấm gộp \| | \| Case \| Why batching it is banned here \| |
| L167 | `skills/tdq-conventions/references/context-budget.md:86` | \| Đang khoanh vùng lỗi \| gộp 5 lệnh rồi lỗi ở đâu không biết, phải chạy lại từng lệnh, tốn nhiều bước hơn \| | \| Isolating a failure \| batch 5 commands and you cannot tell which failed, so you rerun them one by one — more steps, not fewer \| |
| L168 | `skills/tdq-conventions/references/context-budget.md:87` | \| Lệnh phá hủy hoặc khó đảo \| xoá, ghi đè, `git reset` — phải xem kết quả lệnh trước rồi mới chạy lệnh sau \| | \| Destructive or hard-to-undo commands \| delete, overwrite, `git reset` — you must see the previous command's result before running the next \| |
| L169 | `skills/tdq-conventions/references/context-budget.md:102` | Lint đúng file.** Chạy `doc_lint.py` trên ĐÚNG file vừa sửa, cấm truyền cả thư mục | Lint the exact file.** Run `doc_lint.py` on EXACTLY the file you just changed, never pass a |
| L170 | `skills/tdq-conventions/references/context-budget.md:105` | CLI im lặng.** `tdq_state.py init\|set\|reset` mặc định in 1 dòng; chỉ thêm `--json` | Quiet CLI.** `tdq_state.py init\|set\|reset` prints one line by default; add `--json` only |
| L171 | `skills/tdq-conventions/references/context-budget.md:109` | Cấm `cat` (dùng Read), cấm `grep -A5 -B5` khi `-c`/`-l` đã đủ trả lời. | `offset`/`limit`. No `cat` (use Read), no `grep -A5 -B5` when `-c`/`-l` already answers. |
| L172 | `skills/tdq-conventions/references/measure-scenario.md:9` | Dùng một project thử tách biệt (không phải repo chính) để không lẫn log: | Use a separate throwaway project, not the main repo, so the logs stay unmixed: |
| L173 | `skills/tdq-conventions/references/measure-scenario.md:40` | equiv-input token — đây là bằng chứng carry-cost, không phải ước lượng. | the percentage drop in total equiv-input tokens — that is carry-cost evidence, not an estimate. |
| L174 | `skills/tdq-conventions/references/phases.md:7` | \| phase \| vào khi \| việc duy nhất \| lệnh chuyển tiếp \| xong khi \| cấm \| | \| phase \| entered when \| the single job \| command onward \| done when \| forbidden \|… |
| L175 | `skills/tdq-conventions/references/phases.md:11` | \| `spec` \| Đã phân tích xong \| Viết spec (kèm mục Lộ trình), đăng ký spec_file, trình tóm tắt rồi DỪNG chờ user duyệt \| `python3 "${CLAUDE_PLUG… | \| `spec` \| Analysis is finished \| Write the spec (with its roadmap section), register spec_file, pre… |
| L176 | `skills/tdq-conventions/references/phases.md:12` | \| `plan` \| spec_approved = true \| Viết plan kèm mode ĐỀ XUẤT, đăng ký plan_file, trình rồi DỪNG chờ duyệt \| `python3 "${CLAUDE_PLUGIN_ROOT}/scr… | \| `plan` \| spec_approved = true \| Write the plan with a PROPOSED mode, register plan_file, present i… |
| L177 | `skills/tdq-conventions/references/phases.md:13` | \| `mode` \| plan_approved = true mà implement_mode chưa chốt \| Giải thích ngắn gọn 2 mode rồi hỏi user chọn, DỪNG chờ trả lời \| `python3 "${CLAU… | \| `mode` \| plan_approved = true but implement_mode is not settled \| Explain the 2 modes briefly, ask… |
| L178 | `skills/tdq-conventions/references/phases.md:18` | \| `quick` \| lane = quick \| Phân tích → mini-spec/plan gộp 1 file → chờ duyệt → ghi working log TRƯỚC → implement → QC bám DoD (mặc định BẬT) → v… | \| `quick` \| lane = quick \| Analyse → a mini spec/plan merged into one file → wait for approval → write the working log FIRST → im… |
| L179 | `skills/tdq-conventions/references/plugin-routing.md:9` | Vẫn phải **HỎI user trước** khi: cài plugin/marketplace MỚI; chạy OAuth hoặc nhập | You must still **ASK the user first** before: installing a NEW plugin/marketplace; running |
| L180 | `skills/tdq-conventions/references/plugin-routing.md:17` | Chỉ dùng đúng tên ở cột phải. | Use only the exact names in the right column. |
| L181 | `skills/tdq-conventions/references/plugin-routing.md:53` | Muốn quay lại lazy-load cho nhẹ context: thêm tên plugin vào `on_demand` (tắt mặc định, | To go back to lazy-load for a lighter context: add the plugin name to `on_demand` (off by |
| L182 | `skills/tdq-conventions/references/plugin-routing.md:55` | (cấm bật) trong `~/.claude/plugin-tiers.json` — chỉ khi user yêu cầu rõ. | `always_off` (never enabled) in `~/.claude/plugin-tiers.json` — only when the user asks for it |
| L183 | `skills/tdq-conventions/references/reminder-codes.md:4` | những dòng dạng `[TDQ:<MÃ>] <việc phải làm>`. | `[TDQ:<CODE>] <the job to do>` into the context. |
| L184 | `skills/tdq-conventions/references/reminder-codes.md:15` | \| Mã \| Nghĩa \| Việc phải làm \| Hiệu ứng hook kiểm \| | \| Code \| Meaning \| What to do \| Effect the hook checks \| |
| L185 | `skills/tdq-conventions/references/reminder-codes.md:35` | Sổ turn** `docs/tdq/.tdq-turn.jsonl` — ghi lại mọi lần sửa file đi qua tool | Turn ledger** `docs/tdq/.tdq-turn.jsonl` — records every file edit that went through the |
| L186 | `skills/tdq-conventions/references/reminder-codes.md:52` | Project **không phải git repo** thì không có vân tay repo: chiều "đã ghi log" | A project that is **not a git repo** has no repo fingerprint: the "log was written" direction |
| L187 | `skills/tdq-conventions/references/reminder-codes.md:59` | đang bẩn đầu tiên, có thể không phải file vừa sửa. | first dirty file, which may not be the file you just edited. |
| L188 | `skills/tdq-conventions/references/soul.md:4` | dù cũ hay mới — thì sửa luật đó, không sửa soul. Muốn đổi soul phải có user duyệt. | is the law that gets fixed; soul does not. Changing soul requires the user's approval. |
| L189 | `skills/tdq-conventions/references/soul.md:27` | Tầng 1 — chất lượng**: code agent làm ra phải đạt MVP thật — chạy đúng, có test, | - **Tier 1 — quality**: the code the agent produces must be a real MVP — it runs, it has |
| L190 | `skills/tdq-conventions/references/soul.md:41` | Mọi rule và behavior phải đủ chi tiết để model thấp như Haiku đọc là làm đúng, | Every rule and behaviour must be detailed enough that a low model like Haiku reads it and does |
| L191 | `skills/tdq-conventions/references/soul.md:45` | `## Tự kiểm` (một lệnh hoặc một câu hỏi có/không). Chỗ dễ hiểu nhầm phải kèm | `## Self-check` (one command, or one yes/no question). Anywhere easy to misread must carry a |
| L192 | `skills/tdq-conventions/references/soul.md:92` | \| Đổi đúng-sai của đầu ra \| 1 — chất lượng \| test trước khi sửa, cấm mock giả làm dữ liệu thật \| | \| The correctness of the output \| 1 — quality \| test before fixing, no fake mock passed off as real data \| |
| L193 | `skills/tdq-conventions/references/soul.md:93` | \| Đổi SỐ BƯỚC (số tool call, số vòng chờ) \| 2 — runtime \| gộp tool call độc lập, cấm vòng `sleep` thăm dò \| | \| The NUMBER OF STEPS (tool calls, waiting rounds) \| 2 — runtime \| batch independent tool calls, no `sleep` polling loop \| |
| L194 | `skills/tdq-conventions/references/soul.md:97` | vừa cắt bước vừa cắt token → tầng 2, không phải tầng 3. | tool-calls law cuts both steps and tokens → tier 2, not tier 3. |
| L195 | `skills/tdq-conventions/references/soul.md:99` | Hệ quả về chỗ đặt: luật tầng 1 và tầng 2 phải nằm trong thân skill được nạp mỗi turn; | Consequence for placement: tier 1 and tier 2 laws must live in the body of a skill loaded every |
| L196 | `skills/tdq-conventions/references/soul.md:101` | của skill là ràng buộc tầng 3 — gặp trần thì nới trần, cấm nén luật tầng 2 cho vừa. | is a tier 3 constraint — hitting the cap means raising the cap, never compressing a tier 2 law |
| L197 | `skills/tdq-conventions/references/soul.md:110` | Lệnh: `python3 -m pytest tests/test_soul_rules.py -q` phải xanh. | - Command: `python3 -m pytest tests/test_soul_rules.py -q` must be green. |
| L198 | `skills/tdq-conventions/references/subagent-tuning.md:10` | \| `model` \| frontmatter agent (mặc định) **và** tham số `model` của Agent tool khi gọi \| **Có** — tham số lúc gọi đè frontmatter \| | \| `model` \| agent frontmatter (default) **and** the Agent tool's `model` parameter at call time \| **Yes** — the call parameter overrides frontmatter \| |
| L199 | `skills/tdq-conventions/references/subagent-tuning.md:20` | \| `tdq-qc-tester` \| inherit \| high \| phải nghi ngờ và đào biên, không chỉ chạy lại lệnh \| | \| `tdq-qc-tester` \| inherit \| high \| must be suspicious and dig at the edges, not just rerun a command \| |
| L200 | `skills/tdq-conventions/references/subagent-tuning.md:36` | \| Viết code, sửa logic, thiết kế, review, QC \| bỏ trống (giữ mặc định của agent) \| | \| Writing code, fixing logic, design, review, QC \| leave empty (keep the agent's default) \| |
| L201 | `skills/tdq-conventions/references/subagent-tuning.md:39` | Ghi lý do override vào working log khi lệch khỏi mặc định — 1 dòng là đủ. | Record the reason for an override in the working log whenever you deviate from the default — |
| L202 | `skills/tdq-conventions/references/subagent-tuning.md:46` | NGAY CẢ KHI user đang để phiên ở `high`. Chỉ đặt `low` cho agent thuần cơ học. | WHEN the user has the session on `high`. Only set `low` on purely mechanical agents. |
| L203 | `skills/tdq-conventions/references/subagent-tuning.md:48` | Muốn effort thật sự thay đổi theo task thì phải tách agent thành nhiều biến thể — | Making effort genuinely vary per task would require splitting each agent into several variants — |
| L204 | `skills/tdq-conventions/references/subagent-tuning.md:56` | frontmatter (khi agent active) > mức của phiên > mặc định model. Tra 2026-08-04. | frontmatter (when the agent is active) > session level > model default. Checked 2026-08-04. |
| L205 | `skills/tdq-conventions/references/user-facing-block.md:4` | không phải người trong nghề: họ cần biết đang xem cái gì, xem chi tiết ở đâu, và phải | is an end user, not a colleague from the trade: they need to know what they are looking at, where |
| L206 | `skills/tdq-conventions/references/user-facing-block.md:48` | thêm ký tự đánh dấu**, không phải viết lại chữ: bảy luật dưới đây không cho phép đổi, | **adding markup characters**, never rewriting words: the seven rules below allow no word of the |
| L207 | `skills/tdq-conventions/references/user-facing-block.md:61` | chỉ được in đậm bên trong phần nội dung, không đụng vào phần `- A (đề xuất): `. | only inside the content part, never on the `- A (đề xuất): ` part itself. <!-- i18n-allow: sample string of the default language --> |
| L208 | `skills/tdq-conventions/references/user-facing-block.md:87` | Không emoji** ở bất kỳ thành phần nào. Dấu `➤` giữ nguyên, nó không phải emoji. | - **No emoji** in any component. The `➤` character stays; it is not an emoji. |
| L209 | `skills/tdq-conventions/references/user-facing-block.md:89` | Cấm gộp lựa chọn vào đoạn văn. | Merging options into a paragraph is banned. |
| L210 | `skills/tdq-conventions/references/user-facing-block.md:106` | Trong khối in ra cho user chỉ được dùng đúng sáu ký hiệu ngoài ASCII: | A block printed for the user may use exactly six non-ASCII symbols: |
| L211 | `skills/tdq-conventions/references/user-facing-block.md:117` | Ký tự nào không nằm trong bảng thì không được thêm vào, kể cả khi nhìn có vẻ vô hại. | A character outside the table must not be added, however harmless it looks. `▸` is excluded for |
| L212 | `skills/tdq-conventions/references/user-facing-block.md:120` | (`─` `│` `├` `└` `┌` `┬` `┐`) cũng bị cấm: chúng đòi canh cột, mà bề rộng terminal thì | (`─` `│` `├` `└` `┌` `┬` `┐`) are banned too: they demand column alignment, and terminal width |
| L213 | `skills/tdq-conventions/references/user-facing-block.md:131` | <!-- Khối "Trước" cố tình sai khuôn: nó là ví dụ đối chiếu, không phải mẫu để chép. --> | <!-- i18n-allow — the "Trước" block is deliberately off-shape: it is the counter-example, not a template to copy. --> |
| L214 | `skills/tdq-conventions/references/worklog-images.md:3` | Áp dụng khi turn có ảnh đính kèm **và** turn đó phải ghi working log (có đổi repo). | Applies when a turn has attached images **and** that turn must write a working log (the repo |
| L215 | `skills/tdq-conventions/references/worklog-images.md:14` | truyền cho `--log`, cạnh câu mô tả ảnh đó. Không bắt buộc đặt ở đầu chuỗi. | passed to `--log`, next to the sentence describing that image. It need not lead the string. |
| L216 | `skills/tdq-intake/SKILL.md:25` | Luật thoát (bắt buộc).** Giữa chừng vi phạm bất kỳ điều kiện nào → DỪNG tay, nói rõ | **Escape rule (mandatory).** Break any condition midway → STOP, name the condition that |
| L217 | `skills/tdq-intake/SKILL.md:26` | điều kiện nào vỡ, rồi mở request bình thường từ Phần A. Cấm làm tiếp ở tầng `nhỏ`. | broke, then open a normal request from Part A. Never keep going at tier `nhỏ`. |
| L218 | `skills/tdq-intake/SKILL.md:30` | Định nghĩa "yêu cầu mới": MỌI prompt của user khi KHÔNG có request mở — request mở | Definition of a "new request": ANY user prompt while NO request is open — open means |
| L219 | `skills/tdq-intake/SKILL.md:49` | cỡ/nhu cầu (`Cỡ:/Cần:`) là bước NỘI BỘ — dùng để chọn phương án đề xuất, KHÔNG in dòng | Judging size/need (`Cỡ:/Cần:`) is an INTERNAL step — it picks which option you |
| L220 | `skills/tdq-intake/SKILL.md:57` | DỪNG chờ user trả lời.** Không tự chọn lane. | **STOP and wait for the user's answer.** Never pick the lane yourself. |
| L221 | `skills/tdq-intake/SKILL.md:89` | rồi sang [tdq-spec](../tdq-spec/SKILL.md) — cùng turn nếu interview đã xong, còn phải | then on to [tdq-spec](../tdq-spec/SKILL.md) — same turn if the interview is finished; if |
| L222 | `skills/tdq-intake/SKILL.md:94` | Chế độ nhanh = rút gọn, KHÔNG cắt bước tư duy. Chín bước thi hành — từ phân tích tới hỏi | Express is a shortened path, NOT a path with thinking steps cut out. The nine |
| L223 | `skills/tdq-intake/SKILL.md:97` | `## Chín bước thi hành`. **BẮT BUỘC mở file đó và đọc hết chín bước trước khi làm bước 1; | **You MUST open that file and read all nine steps before doing step 1; working from memory |
| L224 | `skills/tdq-intake/SKILL.md:98` | cấm làm theo trí nhớ.** Cùng file đó có luôn khuôn mini-plan, luật tick, luật QC và vòng fix. | is banned.** That same file also holds the mini-plan khuôn, the tick rule, the QC rule and |
| L225 | `skills/tdq-intake/references/analyze-full.md:22` | này rồi trình user chốt; chưa chốt thì mọi dòng trong đó là gợi ý, không phải luật. | in it is a suggestion, not a rule. The draft has exactly 4 sections. `## Tầng`: one |
| L226 | `skills/tdq-intake/references/analyze-full.md:23` | dòng "tầng X không được gọi tầng Y" kèm lý do. `## Hub`: 5 node nhiều liên kết nhất | line per layer with its responsibility. `## Luật gọi`: the "layer X must not call layer |
| L227 | `skills/tdq-intake/references/analyze-full.md:25` | kèm số bậc, lấy từ `graphify god-nodes`; sửa node trong đó là rủi ro cao, phải khai | from `graphify god-nodes`; editing one of them is high risk and must be declared on the |
| L228 | `skills/tdq-intake/references/analyze-full.md:26` | ở dòng `Chạm:` của plan. `## Đã chốt`: quyết định đã đóng kèm ngày; muốn đổi phải | plan's `Chạm:` line. `## Đã chốt`: closed decisions with their date; changing one needs |
| L229 | `skills/tdq-intake/references/analyze-full.md:29` | Luật ĐỌC đồ thị graphify** (gợi ý có điều kiện, KHÔNG bắt buộc mỗi lần analyze): | **When to READ the graphify graph** (conditional advice, NOT mandatory every analyze): |
| L230 | `skills/tdq-intake/references/analyze-full.md:40` | (luật failover ở [tavily.md](../../tdq-conventions/references/tavily.md)). Mặc định giao | [tavily.md](../../tdq-conventions/references/tavily.md)). By default hand it to one |
| L231 | `skills/tdq-intake/references/analyze-full.md:44` | Kết quả tavily thô nằm lại context tốn ~14M token/2 session — đó là lý do bắt buộc. | Raw tavily results left sitting in context cost ~14M tokens per 2 sessions — that is |
| L232 | `skills/tdq-intake/references/analyze-full.md:47` | Bỏ qua chỉ khi việc thuần nội bộ, không có ẩn số bên ngoài. | Skip the step only when the work is purely internal, with no external unknown. |
| L233 | `skills/tdq-intake/references/analyze-full.md:65` | chia subagent…). Khung bất biến không được bỏ: phân tích → spec/plan → implement → | review, splitting across subagents…). The invariant frame that can never be dropped: |
| L234 | `skills/tdq-intake/references/analyze-full.md:79` | rồi sang [tdq-spec](../../tdq-spec/SKILL.md) — cùng turn nếu interview đã xong, còn phải | then on to [tdq-spec](../../tdq-spec/SKILL.md) — same turn if the interview is finished; |
| L235 | `skills/tdq-intake/references/interview.md:16` | có điều kiện, luật đầy đủ ở [scope-round.md](scope-round.md). Bỏ thì phải ghi lý do. | conditionally; the full rule is in [scope-round.md](scope-round.md). Skip it and the |
| L236 | `skills/tdq-intake/references/interview.md:63` | Cấm gộp** nhiều option vào một dòng hay nhét vào đoạn văn dạng `(a) … · (b) …`. | - **Merging is banned** — never put several options onto one line or into a paragraph |
| L237 | `skills/tdq-intake/references/interview.md:112` | Còn một câu làm đổi → hỏi tiếp vòng nữa. Cấm chuyển sang viết spec khi còn chỗ phải đoán. | Stop when you re-read the question list and every remaining question **cannot** change the |
| L238 | `skills/tdq-intake/references/issue-triage.md:3` | Áp dụng khi yêu cầu mới là **báo lỗi** chứ không phải làm tính năng: "chạy sai", "bị treo", | Applies when the new request is a **bug report** rather than a feature: "chạy sai", |
| L239 | `skills/tdq-intake/references/issue-triage.md:20` | Chốt căn cứ rồi mới lập spec.** Spec fix phải nêu được nguyên nhân gốc, cách sửa, | for calling search: [tavily.md](../../tdq-conventions/references/tavily.md). |
| L240 | `skills/tdq-intake/references/lane-decision.md:26` | \| Yêu cầu đã rõ chưa \| rõ, không phải hỏi gì \| còn chỗ mơ hồ / cần research \| | \| Is the request clear \| clear, nothing to ask \| vague spots / research needed \| |
| L241 | `skills/tdq-intake/references/quick-lane.md:3` | Chế độ nhanh khác chế độ chuyên sâu ở chỗ **gộp tài liệu và gộp gate**, không phải ở | Express differs from the deep pipeline by **merging the documents and merging the |
| L242 | `skills/tdq-intake/references/quick-lane.md:5` | làm đổi kết quả đều GIỮ. Chỉ bỏ khi việc thuần nội bộ hoặc đã rõ hết — và phải nói rõ | unknown, and an interview whenever a question can still change the outcome are all KEPT. |
| L243 | `skills/tdq-intake/references/quick-lane.md:16` | \| QC \| file `qc/<slug>.md` \| mỗi dòng DoD một phép kiểm, ghi vào mục ## QC của plan (mặc định BẬT) \| | \| QC \| file `qc/<slug>.md` \| one check per DoD line, written into the plan's `## QC` section (ON by default) \| |
| L244 | `skills/tdq-intake/references/quick-lane.md:34` | Đây là toàn bộ Phần C của [SKILL.md](../SKILL.md) — chuyển về đây để thân skill không phải | This is the whole of Part C of [SKILL.md](../SKILL.md) — moved here so the skill body does |
| L245 | `skills/tdq-intake/references/quick-lane.md:35` | nạp nhánh này mỗi lần gọi. Vào chế độ nhanh là **bắt buộc** đọc hết chín bước dưới đây | not load this branch on every call. Entering chế độ nhanh you **MUST** read all nine steps |
| L246 | `skills/tdq-intake/references/quick-lane.md:36` | trước khi làm bước 1; cấm làm theo trí nhớ. | below before doing step 1; working from memory is banned. |
| L247 | `skills/tdq-intake/references/quick-lane.md:56` | In đúng dòng: `➤ Duyệt: nhắn "duyệt nhanh" (bỏ QC: "duyệt nhanh không QC"; "duyệt quick" vẫn chạy — duyệt xong implement ngay) · Góp ý: nhắn trực t… | ➤ Duyệt: nhắn "duyệt nhanh" (bỏ QC: "duyệt nhanh không QC"; "duyệt quick" vẫn chạy — duyệt xong implement ngay) · Góp ý: nhắn trực tiếp |
| L248 | `skills/tdq-intake/references/quick-lane.md:71` | `[x]` NGAY khi test xanh — cấm gom tick cuối turn. Rồi chạy **QC** (mặc định BẬT): mỗi dòng DoD một | `[x]` the moment the test is green — batching ticks at the end of the turn is banned. |
| L249 | `skills/tdq-intake/references/quick-lane.md:79` | fix có thể làm hỏng. Có trần 3 vòng — vượt trần thì DỪNG, báo user, đề xuất chuyển lane | could have broken. There is a 3-round cap — over the cap, STOP, tell the user, propose |
| L250 | `skills/tdq-intake/references/quick-lane.md:154` | Đổi `[~]`/`[>]` → `[x]` **NGAY**, không đợi task sau. | 3. Switch `[~]`/`[>]` → `[x]` **IMMEDIATELY**, never after the next task. |
| L251 | `skills/tdq-intake/references/quick-lane.md:156` | Chỉ một task mang `[~]` tại một thời điểm. **Cấm gom tick vào cuối turn** — chế độ nhanh (express) | Only one task carries `[~]` at a time; `[>]` may be several, at most the 4-branch cap. |
| L252 | `skills/tdq-intake/references/quick-lane.md:160` | Hàng rào: `hooks/scripts/edit_gate.py` **CHẶN** (deny) mọi lần sửa file ngoài `docs/` và | Fence: `hooks/scripts/edit_gate.py` **BLOCKS** (deny) every edit outside `docs/` and |
| L253 | `skills/tdq-intake/references/quick-lane.md:167` | Mặc định **BẬT**. Làm ngay sau khi implement xong, **số hạng mục bằng số dòng DoD** | ON by default. Run it right after implement finishes, **số hạng mục bằng số dòng DoD** of |
| L254 | `skills/tdq-intake/references/quick-lane.md:186` | User im lặng về QC = CÓ QC. Khi đó mục `## QC` vẫn phải có, đúng 1 dòng: | `--no-qc`. Silence about QC means QC HAPPENS. Section `## QC` must still exist, with exactly |
| L255 | `skills/tdq-intake/references/quick-lane.md:202` | Trần 3 vòng.** Vượt trần → DỪNG, báo user, đề xuất chuyển chế độ chuyên sâu (deep). Giữ | - **3-round cap.** Over the cap → STOP, tell the user, propose moving to the deep pipeline. |
| L256 | `skills/tdq-intake/references/quick-lane.md:203` | `phase=implement`, KHÔNG chạy `set phase=idle`. |   Keep `phase=implement`, do NOT run `set phase=idle`. |
| L257 | `skills/tdq-intake/references/scope-round.md:29` | Không dấu hiệu nào → BỎ vòng scope, đi thẳng vòng chi tiết. Khi BỎ, brief phải có đúng | No sign at all → SKIP the scope round and go straight to the detail round. When skipping, |
| L258 | `skills/tdq-intake/references/scope-round.md:30` | một dòng, không được im lặng: | the brief must carry exactly one line; silence is not allowed: |
| L259 | `skills/tdq-intake/references/scope-round.md:36` | Dòng lý do bắt buộc này là hàng rào: "có điều kiện" nghĩa là có tiêu chí, không phải tuỳ | That mandatory reason line is the fence: "conditional" means there are criteria, not that |
| L260 | `skills/tdq-intake/references/scope-round.md:67` | Mặt nào yêu cầu đã nói rõ rồi thì KHÔNG đưa vào option, ghi thẳng là đã chốt. | - An area the request already settled is NOT offered as an option; write it down as settled. |
| L261 | `skills/tdq-intake/references/scope-round.md:71` | CẤM hỏi mức độ trừu tượng.** Không hỏi "bạn muốn gọn nhất, vừa đủ, hay đầy đủ chuyên | **Asking for an abstract level is BANNED.** Never ask whether the user wants it "minimal, |
| L262 | `skills/tdq-intake/references/scope-round.md:84` | \| Ràng buộc nền tảng \| thiết bị, OS, engine, thư viện bắt buộc \| không ràng buộc · một nền tảng · nhiều nền tảng \| | \| Platform constraints \| device, OS, engine, mandatory library \| no constraint · one platform · several platforms \| |
| L263 | `skills/tdq-intake/references/scope-round.md:110` | Suy xong phải in đúng một dòng, đặt kèm khối câu hỏi của vòng chi tiết: | Once inferred, print exactly one line, together with the detail round's question block: |
| L264 | `skills/tdq-intake/references/scope-round.md:116` | Dòng này để user cãi được ngay nếu bạn suy sai. Nó **không** phải một cổng duyệt mới — | This line lets the user push back immediately if you inferred wrong. It is **not** a new |
| L265 | `skills/tdq-intake/references/skill-inventory.md:15` | Cờ `--loc` cắt bảng còn phần liên quan, KHÔNG bao giờ ẩn skill nguồn `project` hay | Flag `--loc` trims the table to the relevant part, NEVER hides a skill from source |
| L266 | `skills/tdq-intake/references/skill-inventory.md:17` | BẮT BUỘC chạy lại `--tat-ca` rồi mới phán quyết. | hidden. Suspect something is missing → you MUST re-run with `--tat-ca` before ruling. |
| L267 | `skills/tdq-intake/references/skill-inventory.md:35` | \| Đã xét <N> skill khác \| user/plugin/built-in \| KHÔNG \| khác lĩnh vực \| |  |
| L268 | `skills/tdq-intake/references/skill-inventory.md:38` | Ví dụ dòng đã điền (KHÔNG chép vào bảng thật): | A filled-in example (do NOT copy it into the real table): |
| L269 | `skills/tdq-intake/references/skill-inventory.md:41` | `\| Đã xét 240 skill khác \| plugin \| KHÔNG \| khác lĩnh vực \|` |  |
| L270 | `skills/tdq-intake/references/skill-inventory.md:54` | \| Khớp đúng 1 trong 4 lý do loại ở bảng dưới \| `KHÔNG` + lý do \| | \| It matches exactly 1 of the 4 rejection reasons below \| `KHÔNG` + the reason \| |
| L271 | `skills/tdq-intake/references/skill-inventory.md:64` | \| `user đã cấm` \| User đã nói không dùng \| | \| `user đã cấm` \| The user said not to use it \| |
| L272 | `skills/tdq-intake/references/skill-inventory.md:68` | `DÙNG` → spec chép dòng đó vào mục `## 3b` · plan phải có **khối hợp đồng 5 trường** | - `DÙNG` → the spec copies that row into section `## 3b` · the plan must carry a |
| L273 | `skills/tdq-intake/references/skill-inventory.md:71` | `KHÔNG` → chép nguyên dòng vào spec §3b, không cần gì thêm. | - `KHÔNG` → copy the row verbatim into spec §3b, nothing else needed. |
| L274 | `skills/tdq-plan/SKILL.md:3` | description: Biến spec thành plan checkbox, mỗi task một test: DỪNG chờ user duyệt plan, rồi hỏi cách chạy và build cùng turn. Dùng khi spec chế độ… | description: Turn an approved spec into a checkbox plan, one test per task: STOP and wait |
| L275 | `skills/tdq-plan/SKILL.md:10` | Yêu cầu `spec_approved = true`. User duyệt spec xong là viết plan NGAY trong cùng turn. | `spec_approved = true`. The user approves the spec → write the plan RIGHT AWAY, same turn. |
| L276 | `skills/tdq-plan/SKILL.md:42` | Mọi task tạo/sửa file mã nguồn phải có dòng `Chạm:` ngay dưới nó**, liệt kê đường | **Every task that creates or edits a source file needs a `Chạm:` line right under it**, listing |
| L277 | `skills/tdq-plan/SKILL.md:55` | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/doc_lint.py" --pair <spec> <plan>` phải exit 0. |  |
| L278 | `skills/tdq-plan/SKILL.md:63` | Không** set `implement_mode` ở đây — trường đó chỉ được ghi khi ghi nhận duyệt. | Do **NOT** set `implement_mode` here — that field is written only when approval is recorded. |
| L279 | `skills/tdq-plan/SKILL.md:65` | Trình bày & DỪNG.** Viết khối trình plan theo | **Present it, then STOP.** Write the plan block per |
| L280 | `skills/tdq-plan/SKILL.md:84` | Phần nội dung ≤ 10 dòng, là tóm tắt THẬT — cấm thay bằng thông báo suông kiểu "đã ghi | The body is ≤ 10 lines and a REAL summary — swapping it for a bare status line such as "đã ghi |
| L281 | `skills/tdq-plan/SKILL.md:85` | trước đoạn trích: "(khuôn mẫu — áp dụng cho các lần hỏi sau, không phải câu hỏi của | Quoting a whole template as an example → label it right before the excerpt, in the user's |
| L282 | `skills/tdq-plan/SKILL.md:89` | User duyệt → ghi nhận NGAY, rồi hỏi cách chạy trong CÙNG turn:** | **The user approves → record it IMMEDIATELY, then ask about the run mode in the SAME turn:** |
| L283 | `skills/tdq-plan/SKILL.md:95` | Cấm hỏi lại thứ user vừa nói. | Re-asking what the user just said is banned. |
| L284 | `skills/tdq-plan/SKILL.md:96` | Chưa nói mode → state dừng ở phase `mode`, in khối hỏi rồi DỪNG. Khuôn nguyên văn — | No mode named → state stops at phase `mode`; print the question block then STOP. |
| L285 | `skills/tdq-plan/SKILL.md:99` | Ngay dưới hai option phải có đoạn **"Vì sao đề xuất"** dài 1–3 dòng. Cấm nói chung | Right under the two options there MUST be a **"Vì sao đề xuất"** paragraph, 1–3 lines long. |
| L286 | `skills/tdq-plan/SKILL.md:104` | User trả lời → chạy lại lệnh trên kèm `--mode <main\|subagent>` rồi build LUÔN cùng | The user answers → re-run the command above with `--mode <main\|subagent>` and build LUÔN cùng |
| L287 | `skills/tdq-plan/SKILL.md:105` | turn. Mode chốt là mode user NÓI (khác đề xuất cũng được); cấm tự chọn thay user. | turn. The settled mode is the one the USER said (it may differ from your proposal); choosing |
| L288 | `skills/tdq-plan/SKILL.md:110` | rồi sang [tdq-build](../tdq-build/SKILL.md) **NGAY trong cùng turn**. | [tdq-build](../tdq-build/SKILL.md) **in that very same turn**. |
| L289 | `skills/tdq-plan/references/mode-gate.md:30` | Dài 1–3 dòng, đặt ngay dưới hai option. Cấm nói chung chung. Mọi câu phải dựa trên | 1–3 lines long, sitting right under the two options. Vague wording is banned. |
| L290 | `skills/tdq-plan/references/mode-gate.md:43` | Kết bằng đúng một câu nói vì sao KHÔNG chọn phương án còn lại. | Close with exactly one sentence saying why NOT the other option. |
| L291 | `skills/tdq-plan/references/mode-gate.md:52` | Mode B là mô hình lai, không phải "mọi task đều đẩy cho agent con". Leader vẫn tự làm | Mode B is a hybrid, not "every task pushed to a sub-agent". The leader still keeps for itself |
| L292 | `skills/tdq-plan/references/mode-gate.md:54` | `file-luat`, `hop-dong`. Phần còn lại bắt buộc phải giao — và `scripts/tdq_team.py` | `file-luat`, `hop-dong`. Everything else MUST be handed out — and `scripts/tdq_team.py kiem-ke` |
| L293 | `skills/tdq-plan/references/mode-gate.md:61` | phải tổng số task, mới quyết định B có nhanh hơn A hay không. Luật đầy đủ của mode đội: | the total task count, decides whether B beats A. Full rule of the team mode: |
| L294 | `skills/tdq-plan/references/plan-template.md:38` | `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong. |  |
| L295 | `skills/tdq-plan/references/plan-template.md:39` | Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau. |  |
| L296 | `skills/tdq-plan/references/plan-template.md:40` | Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó. |  |
| L297 | `skills/tdq-plan/references/plan-template.md:63` | Vì vậy **mọi task tạo hoặc sửa file mã nguồn đều phải có dòng `Chạm:`**, kể cả task tạo |  |
| L298 | `skills/tdq-plan/references/plan-template.md:64` | file mới. Đường dẫn phải nằm trong backtick và phải là đường dẫn thật tính từ gốc repo. |  |
| L299 | `skills/tdq-plan/references/plan-template.md:66` | leader phải tự làm, mất chỗ chạy song song. Task chỉ sửa tài liệu thì bỏ dòng này. |  |
| L300 | `skills/tdq-plan/references/plan-template.md:67` | Node nằm trong mục `## Hub` của `docs/kien-truc.md` → task phải thêm một dòng DoD kiểm |  |
| L301 | `skills/tdq-plan/references/plan-template.md:94` | khác nhau, nên chúng KHÔNG được đụng chung một file — git không hề cảnh báo, tới lúc |  |
| L302 | `skills/tdq-plan/references/plan-template.md:114` | Ra: <artifact phải tồn tại sau task, có đường dẫn> |  |
| L303 | `skills/tdq-plan/references/plan-template.md:116` | Không dùng cho: <việc kề bên mà skill này KHÔNG được lan sang> |  |
| L304 | `skills/tdq-plan/references/plan-template.md:118` | Luật nhãn `(mcp)` — BẮT BUỘC ghi ngay khi lập plan: skill nào cần MCP tool lúc |  |
| L305 | `skills/tdq-plan/references/plan-template.md:119` | chạy (gọi server MCP, ví dụ tavily/notion) → dòng `Dùng:` phải kết thúc bằng nhãn |  |
| L306 | `skills/tdq-plan/references/plan-template.md:121` | này để biết task nào buộc phải do Claude tự làm, không giao sub-agent thiếu MCP. |  |
| L307 | `skills/tdq-plan/references/plan-template.md:124` | Phase này bắt buộc **chỉ khi việc này có runtime** — tức có ít nhất một task tạo hoặc sửa |  |
| L308 | `skills/tdq-plan/references/plan-template.md:128` | [ ] **Tx.1** Log service bật mặc định (timestamp, mức log, tắt được qua config) — Test: <...> |  |
| L309 | `skills/tdq-plan/references/plan-template.md:148` | chạy, không phải thời gian người chờ). Đơn vị luôn là phút, số nguyên 1–999, không viết | runtime, not human waiting time). The unit is always minutes, an integer 1–999, never `1h` or |
| L310 | `skills/tdq-plan/references/plan-template.md:157` | `eNm` KHÔNG đổi luật tick `[ ] [~] [x]` và không phải cam kết thời gian với user. | - `eNm` changes nothing about the tick rule `[ ] [~] [x]` and is not a promise of time to user. |
| L311 | `skills/tdq-spec/SKILL.md:3` | description: Viết spec tiếng Việt cho request TDQ, đăng ký vào state, trình rồi DỪNG chờ duyệt; duyệt xong viết plan cùng turn. Dùng khi chế độ chu… | description: Write the spec for a TDQ request in the user's document language, register it |
| L312 | `skills/tdq-spec/SKILL.md:16` | Mục bắt buộc: mục tiêu & phạm vi (in/out) · **Lộ trình** (chép từ brief: phase | Sections that MUST be there: goal & scope (in/out) · **Lộ trình** (copied from the |
| L313 | `skills/tdq-spec/SKILL.md:22` | yêu cầu bắt buộc (log service bật mặc định, không placeholder, test cho từng phần) · | standing requirements (log service ON by default, no placeholder, a test per part) · |
| L314 | `skills/tdq-spec/SKILL.md:24` | Mục "câu hỏi còn mở" PHẢI rỗng — còn câu hỏi thì quay lại phase `analyze`. | The "open questions" section MUST be empty — a question left → back to phase `analyze`. |
| L315 | `skills/tdq-spec/SKILL.md:38` | Trình bày & DỪNG.** Viết khối trình spec theo | **Present it, then STOP.** Write the spec block per |
| L316 | `skills/tdq-spec/SKILL.md:58` | Phần nội dung ≤ 50 dòng và phải là tóm tắt THẬT — cấm thay bằng câu thông báo suông | The body is ≤ 50 lines and must be a REAL summary — swapping it for a bare status line |
| L317 | `skills/tdq-spec/SKILL.md:62` | hỏi sau, không phải câu hỏi của turn này)". Mục đích: đọc lại transcript không nhầm là | language: "(template — for later questions, not this turn's question)". The point: someone |
| L318 | `skills/tdq-spec/SKILL.md:67` | User duyệt → ghi nhận NGAY:** | **The user approves → record it IMMEDIATELY:** |
| L319 | `skills/tdq-spec/SKILL.md:76` | rồi sang [tdq-plan](../tdq-plan/SKILL.md) **NGAY trong cùng turn** — không bắt user | then on to [tdq-plan](../tdq-plan/SKILL.md) **NGAY trong cùng turn** — the user is not |
| L320 | `skills/tdq-spec/references/spec-template.md:4` | áp dụng, nhưng phải nói rõ **vì sao** không áp dụng. | that does not apply, but say **why** it does not apply. |
| L321 | `skills/tdq-spec/references/spec-template.md:40` | BẮT BUỘC chép các mặt bị loại ở brief `### Phạm vi đã chốt` vào đây> |  |
| L322 | `skills/tdq-spec/references/spec-template.md:77` | Phán quyết chỉ nhận: DÙNG / KHÔNG (+ 1 trong 4 lý do đóng) / NỀN (skill khung đang chạy). |  |
| L323 | `skills/tdq-spec/references/spec-template.md:82` | \| Đã xét <N> skill khác \| user/plugin/built-in \| KHÔNG \| khác lĩnh vực \| |  |
| L324 | `skills/tdq-spec/references/spec-template.md:85` | Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config. |  |
| L325 | `skills/tdq-spec/references/spec-template.md:86` | Dòng này bắt buộc **chỉ khi việc này có runtime** — tức plan sẽ có ít nhất một task tạo |  |
| L326 | `skills/tdq-spec/references/spec-template.md:96` | Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ những dòng việc này |  |
| L327 | `skills/tdq-spec/references/spec-template.md:100` | Không chạm dòng nào → ghi `Ràng buộc kiến trúc phải giữ: không chạm dòng nào — <lý do |  |
| L328 | `skills/tdq-spec/references/spec-template.md:145` | Điều kiện PASS ở §6 đo được bằng lệnh, không phải cảm tính. | - A PASS condition in §6 is measurable by a command, not by feel. |
| L329 | `skills/tdq-spec/references/spec-template.md:154` | \| Câu hỏi \| Trả lời phải nằm ở \| | \| What does this work PRODUCE? \| §1 mục tiêu + §2 bảng đầu ra \| |

**Tổng: 329 điểm neo** trên 41 file skill.
