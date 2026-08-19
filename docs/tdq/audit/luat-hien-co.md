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

## 3. Bảng luật

| mã | nguồn | nội dung |
|---|---|---|
| L001 | `skills/tdq-build/SKILL.md:13` | Vào build NGAY trong turn user duyệt plan, rồi chạy end-to-end trong MỘT turn.** Không |
| L002 | `skills/tdq-build/SKILL.md:18` | (message mô tả thay đổi, KHÔNG push, liệt kê commit đó trong report). |
| L003 | `skills/tdq-build/SKILL.md:22` | `- [x]` TRƯỚC khi bắt task sau. Cấm gom tick cuối turn. Ba trạng thái: `[ ]` chưa làm · |
| L004 | `skills/tdq-build/SKILL.md:27` | `eNm` các task chưa xong. Giữ nguyên khi tick, không chấm lại giữa chừng, và nó KHÔNG |
| L005 | `skills/tdq-build/SKILL.md:30` | Red → green.** Mỗi task: chạy/viết check trước (phải fail), rồi code, rồi chạy lại đến pass. |
| L006 | `skills/tdq-build/SKILL.md:49` | Nhận báo cáo thì `kiem` rồi `hop`, tick `[x]` NGAY, `don`, rồi quay lại `cum`. |
| L007 | `skills/tdq-build/SKILL.md:50` | Mặc định là GIAO. Chỉ được giữ task lại cho mình khi khớp đúng 1 trong 4 nhóm lý do |
| L008 | `skills/tdq-build/SKILL.md:42` | [references/team-mode.md](references/team-mode.md) — **BẮT BUỘC mở đọc trước khi |
| L009 | `skills/tdq-build/SKILL.md:56` | phân công; cấm làm theo trí nhớ.** |
| L010 | `skills/tdq-build/SKILL.md:57` | Mode là thứ USER đã nói lúc duyệt. Thiếu mode, hoặc bạn nghĩ mode khác hợp hơn → **DỪNG và HỎI**. |
| L011 | `skills/tdq-build/SKILL.md:62` | `- [~]` chỉ dành cho task LEADER tự làm và vẫn chỉ được đúng một. |
| L012 | `skills/tdq-build/SKILL.md:71` | để dành, chạy đúng 1 lần ở QC. Dán kết quả thật, cấm tuyên bố xong khi chưa chạy. |
| L013 | `skills/tdq-build/SKILL.md:72` | Đổi `- [~]` thành `- [x]` cho task đó trong plan NGAY — mode `subagent` thì main |
| L014 | `skills/tdq-build/SKILL.md:86` | [references/qc.md](references/qc.md) mục `## Ba bước thi hành`. **BẮT BUỘC mở file đó và |
| L015 | `skills/tdq-build/SKILL.md:87` | đọc hết ba bước trước khi chạy hạng mục đầu tiên; cấm làm theo trí nhớ.** Cùng file đó có |
| L016 | `skills/tdq-build/SKILL.md:97` | BẮT BUỘC mở file đó và đọc hết bốn bước trước khi viết report; cấm làm theo trí nhớ.** |
| L017 | `skills/tdq-build/references/qc.md:16` | Đây là toàn bộ Phần B của [SKILL.md](../SKILL.md) — chuyển về đây để thân skill không phải |
| L018 | `skills/tdq-build/references/qc.md:17` | nạp nhánh này mỗi lần gọi. Vào phase `qc` là **bắt buộc** đọc hết ba bước dưới đây trước |
| L019 | `skills/tdq-build/references/qc.md:18` | khi chạy hạng mục đầu tiên; cấm làm theo trí nhớ. |
| L020 | `skills/tdq-build/references/qc.md:33` | mà bản fix có thể làm hỏng, cộng full suite. Trần 3 vòng; vượt trần thì DỪNG, báo user. |
| L021 | `skills/tdq-build/references/qc.md:51` | chứa node bị ảnh hưởng. Node không có test → ghi `KHÔNG CÓ TEST: <node>` vào file |
| L022 | `skills/tdq-build/references/qc.md:52` | QC; đó là nợ kỹ thuật phải nêu trong report, không được tính là PASS. |
| L023 | `skills/tdq-build/references/qc.md:53` | QC-F3 — ràng buộc kiến trúc: mỗi dòng trong khối "Ràng buộc kiến trúc phải giữ" ở |
| L024 | `skills/tdq-build/references/qc.md:58` | đáp án. Không chạm mã nguồn → ghi `KHÔNG ÁP DỤNG — không sửa file code`. |
| L025 | `skills/tdq-build/references/qc.md:65` | Log service: bật mặc định, có timestamp, tắt/giảm mức được qua config. |
| L026 | `skills/tdq-build/references/qc.md:68` | ở trường `Ra` phải tồn tại. Không có artifact → sửa spec §3b dòng đó thành `KHÔNG` + |
| L027 | `skills/tdq-build/references/qc.md:108` | Lặp đến khi mọi hạng mục PASS. **Trần 3 vòng** — vượt trần thì DỪNG và báo user. |
| L028 | `skills/tdq-build/references/report-template.md:5` | Đây là toàn bộ Phần C của [SKILL.md](../SKILL.md) — chuyển về đây để thân skill không phải |
| L029 | `skills/tdq-build/references/report-template.md:6` | nạp nhánh này mỗi lần gọi. Vào phase `report` là **bắt buộc** đọc hết bốn bước dưới đây |
| L030 | `skills/tdq-build/references/report-template.md:7` | trước khi viết report; cấm làm theo trí nhớ. |
| L031 | `skills/tdq-build/references/report-template.md:9` | Viết `docs/tdq/reports/<slug>.md` — tiếng Việt, KHÔNG giới hạn cứng số dòng, khuyến |
| L032 | `skills/tdq-build/references/report-template.md:10` | nghị ~10-20 dòng. Khuôn: mục `## Khuôn` cùng file này. Bảng thời gian là **bắt buộc**: |
| L033 | `skills/tdq-build/references/report-template.md:18` | Hỏi user có commit không** — bắt buộc, không tự commit thành quả cuối (ngoại lệ duy |
| L034 | `skills/tdq-build/references/report-template.md:19` | nhất: commit gỡ chặn giữa build theo Luật cứng, phải liệt kê trong report). Gộp chung |
| L035 | `skills/tdq-build/references/report-template.md:36` | User đồng ý → message mô tả thay đổi, KHÔNG chứa "generated with …" hay trailer AI; |
| L036 | `skills/tdq-build/references/report-template.md:47` | `docs/tdq/reports/<slug>.md` — tiếng Việt, KHÔNG giới hạn cứng số dòng. Khuyến nghị |
| L037 | `skills/tdq-build/references/report-template.md:70` | chỉ tính lúc máy làm. Lệch lớn ở một phase nghĩa là phase đó tốn thời gian CHỜ, không phải |
| L038 | `skills/tdq-build/references/report-template.md:77` | Dòng "Giới hạn" không được bỏ trống khi còn việc dang dở — nói thật, không giấu. |
| L039 | `skills/tdq-build/references/rules/chung.md:14` | SonarQube 10/15(25); ESLint để 20, Microsoft CA1502 để 25 nên phải chốt một mức. |
| L040 | `skills/tdq-build/references/rules/chung.md:20` | Mọi lần viết hoặc sửa code, bất kể ngôn ngữ — kể cả script nhỏ và test. |
| L041 | `skills/tdq-build/references/rules/chung.md:27` | ba nhóm còn lại. Ba câu hỏi bắt buộc trước khi nộp code: |
| L042 | `skills/tdq-build/references/rules/chung.md:29` | Tên nói đúng việc chưa?** Tên hàm/biến đọc lên phải ra đúng việc nó làm. |
| L043 | `skills/tdq-build/references/rules/chung.md:38` | Hàm vượt ngưỡng → tách hàm nhỏ, KHÔNG nới ngưỡng tại chỗ. |
| L044 | `skills/tdq-build/references/rules/chung.md:39` | Cách ghi đè ngưỡng: chỉ được ghi đè bằng một dòng trong spec của request (kèm số mới |
| L045 | `skills/tdq-build/references/rules/chung.md:40` | và lý do), vì default mỗi tool mỗi khác; cấm ghi đè bằng thoả thuận miệng trong chat. |
| L046 | `skills/tdq-build/references/rules/chung.md:47` | lỗi phải được xử lý hoặc log rồi ném tiếp — cấm `catch` rỗng. |
| L047 | `skills/tdq-build/references/rules/chung.md:49` | cấm ghi PASS. |
| L048 | `skills/tdq-build/references/rules/cpp.md:24` | Interface phải nói rõ ý**: tham số con trỏ không được phép null → dùng kiểu như |
| L049 | `skills/tdq-build/references/rules/cpp.md:35` | thay cho 15; vượt 25 vẫn phải tách hàm, không nới tiếp. |
| L050 | `skills/tdq-build/references/rules/csharp.md:23` | viết `camelCase`; tên phải nêu đúng việc, không viết tắt khó hiểu. |
| L051 | `skills/tdq-build/references/rules/csharp.md:31` | Cyclomatic ≤ 10, cognitive ≤ 15 mỗi method — theo `chung.md`; C# KHÔNG thuộc nhóm |
| L052 | `skills/tdq-build/references/rules/csharp.md:33` | Mức analyzer: hai category Security và Reliability không được hạ dưới `warning`; |
| L053 | `skills/tdq-build/references/rules/csharp.md:34` | muốn đổi phải ghi vào spec của request, sửa trong `.editorconfig`. |
| L054 | `skills/tdq-build/references/rules/go.md:24` | exported viết hoa chữ đầu và phải có doc comment bắt đầu bằng chính tên đó. |
| L055 | `skills/tdq-build/references/rules/go.md:34` | Bộ linter tối thiểu phải bật: errcheck, govet, staticcheck (theo Uber Go Style Guide). |
| L056 | `skills/tdq-build/references/rules/go.md:39` | Kiểm `err` NGAY sau lời gọi trả về nó; trả lỗi lên trên thì kèm ngữ cảnh cho biết |
| L057 | `skills/tdq-build/references/rules/html.md:22` | Thẻ phải nói đúng vai trò**: dùng phần tử ngữ nghĩa đúng việc thay vì chồng `div`; |
| L058 | `skills/tdq-build/references/rules/html.md:27` | Trùng lặp là mâu thuẫn ý**: `id` phải duy nhất (`id-unique`), thuộc tính không |
| L059 | `skills/tdq-build/references/rules/html.md:34` | Trang mới bắt buộc doctype HTML5 (`doctype-html5`) và doctype đứng đầu file |
| L060 | `skills/tdq-build/references/rules/html.md:40` | Không đặt `<script>` trong `<head>` trừ khi bắt buộc (`head-script-disabled`) — |
| L061 | `skills/tdq-build/references/rules/index.md:19` | Định nghĩa nhóm lỗi Intentionality, ba câu hỏi bắt buộc và số 59,6% nằm trong |
| L062 | `skills/tdq-build/references/rules/index.md:44` | Tầng theo việc**: nạp đúng file ngôn ngữ khớp đuôi file đang sửa; cấm nạp cả 7 |
| L063 | `skills/tdq-build/references/rules/index.md:47` | cấm tự bịa rule hay mượn rule ngôn ngữ khác. |
| L064 | `skills/tdq-build/references/rules/index.md:49` | Linter không có trên máy → ghi "chưa kiểm được", cấm ghi PASS, cấm tự cài đặt. |
| L065 | `skills/tdq-build/references/rules/python.md:9` | ruff — linter mặc định của TDQ cho Python (chạy các nhóm check kiểu F/E/B); URL chính |
| L066 | `skills/tdq-build/references/rules/python.md:21` | Tên sai chuẩn hoặc mơ hồ**: hàm/biến phải `snake_case`, class `PascalCase`, hằng |
| L067 | `skills/tdq-build/references/rules/python.md:31` | (`line-length`) và phải ghi số đã chọn vào spec của request. |
| L068 | `skills/tdq-build/references/rules/python.md:40` | Hàm public có docstring 1 dòng nêu việc; hàm dùng nội bộ thì tên phải tự giải thích. |
| L069 | `skills/tdq-build/references/rules/rust.md:8` | Rust KHÔNG có "Core Guidelines"** tương đương C++: triết lý Rust là để compiler + |
| L070 | `skills/tdq-build/references/rules/rust.md:21` | `SCREAMING_SNAKE_CASE` — compiler tự warn khi lệch; tên phải nêu đúng việc. |
| L071 | `skills/tdq-build/references/rules/rust.md:30` | Cyclomatic ≤ 10, cognitive ≤ 15 mỗi hàm — theo `chung.md`; Rust KHÔNG thuộc nhóm họ C |
| L072 | `skills/tdq-build/references/rules/rust.md:32` | Mức warning: code nộp phải sạch warning của compiler và của `cargo clippy` ở mức |
| L073 | `skills/tdq-build/references/rules/rust.md:33` | mặc định; muốn allow lint nào phải ghi lý do vào spec của request. |
| L074 | `skills/tdq-build/references/rules/rust.md:39` | ở biên nơi gọi; cấm `unwrap` ngoài test. |
| L075 | `skills/tdq-build/references/rules/rust.md:42` | Chạy `cargo clippy` và sửa hết warning; compiler warning cũng phải về 0. |
| L076 | `skills/tdq-build/references/rules/them-ngon-ngu.md:13` | Task phải viết/sửa file có đuôi KHÔNG nằm trong bảng của `index.md`, và user scope |
| L077 | `skills/tdq-build/references/rules/them-ngon-ngu.md:20` | Rule mới viết ra phải trả lời được 3 câu hỏi Intentionality của `chung.md`, |
| L078 | `skills/tdq-build/references/rules/them-ngon-ngu.md:22` | Nguồn phải có thật**: mọi URL đưa vào rule phải nằm trong file research của |
| L079 | `skills/tdq-build/references/rules/them-ngon-ngu.md:23` | request; chưa tìm được nguồn thì ghi "chưa có nguồn", cấm bịa link. |
| L080 | `skills/tdq-build/references/rules/them-ngon-ngu.md:24` | Rule không nói được "vi phạm thì đo bằng gì" là rule chết — mỗi luật phải gắn |
| L081 | `skills/tdq-build/references/rules/them-ngon-ngu.md:32` | thức của ngôn ngữ nêu mức khác, và phải ghi rõ nguồn đó. |
| L082 | `skills/tdq-build/references/rules/them-ngon-ngu.md:45` | DỪNG chờ user duyệt.** User chưa duyệt thì không ghi file rule ra bất kỳ đâu. |
| L083 | `skills/tdq-build/references/rules/typescript-js.md:25` | Promise bỏ lơ lửng là nuốt lỗi**: mọi Promise phải được `await`, `return`, hoặc |
| L084 | `skills/tdq-build/references/rules/typescript-js.md:29` | `@ts-ignore`/`@ts-expect-error` trần bị `ban-ts-comment` chặn — phải kèm mô tả lý do. |
| L085 | `skills/tdq-build/references/rules/typescript-js.md:34` | ESLint mặc định 20 nên phải chỉnh về 10 trong config, không dùng default. |
| L086 | `skills/tdq-build/references/rules/typescript-js.md:42` | Khai kiểu rõ ở biên (tham số, giá trị trả về của hàm export); cấm `any` trần. |
| L087 | `skills/tdq-build/references/rules/typescript-js.md:44` | cấm gọi rồi lờ kết quả. |
| L088 | `skills/tdq-build/references/rules/typescript-js.md:45` | Directive `@ts-` nào cũng phải có mô tả lý do ngay sau directive. |
| L089 | `skills/tdq-build/references/team-mode.md:5` | Bạn là LEADER. Agent con là ĐỘI của bạn. Mặc định là GIAO; giữ task lại cho mình |
| L090 | `skills/tdq-build/references/team-mode.md:6` | phải có cớ nằm trong bảng tra bên dưới, và cái cớ đó bị máy kiểm. |
| L091 | `skills/tdq-build/references/team-mode.md:26` | Mode đội KHÔNG có nghĩa mọi task đều phải giao. Nó có nghĩa: **task nào tách được thì |
| L092 | `skills/tdq-build/references/team-mode.md:27` | phải tách**, phần còn lại leader tự làm — như một trưởng nhóm thật, không phải một |
| L093 | `skills/tdq-build/references/team-mode.md:28` | người ôm hết việc cũng không phải một người chia bừa. |
| L094 | `skills/tdq-build/references/team-mode.md:39` | `phan-cong` đọc TOÀN BỘ plan (không phải từng task một), dựng vùng file của mỗi task |
| L095 | `skills/tdq-build/references/team-mode.md:58` | \| **mặc định: GIAO** \| **không khớp 5 dòng trên** \| `python3 scripts/tdq_team.py kiem-ke` exit 0 \| |
| L096 | `skills/tdq-build/references/team-mode.md:71` | python3 scripts/tdq_team.py kiem T1.1 # dò xung đột, KHÔNG đụng repo |
| L097 | `skills/tdq-build/references/team-mode.md:78` | này nhanh hơn `main`, không phải vì agent con chạy nhanh hơn bạn. |
| L098 | `skills/tdq-build/references/team-mode.md:90` | VÙNG FILE: scripts/alpha.py, tests/test_alpha.py — CẤM sửa file ngoài danh sách này |
| L099 | `skills/tdq-build/references/team-mode.md:91` | TEST: <lệnh kiểm của task> — phải đỏ trước, xanh sau |
| L100 | `skills/tdq-build/references/team-mode.md:99` | Kèm đường dẫn spec và plan trong phần thân prompt. Agent con KHÔNG đọc được hội thoại |
| L101 | `skills/tdq-build/references/team-mode.md:100` | này — thiếu trường nào là nó phải đoán, và đoán sai thì bạn trả giá lúc merge. |
| L102 | `skills/tdq-build/references/team-mode.md:127` | Trước khi kết thúc phase implement, tất cả phải đúng: |
| L103 | `skills/tdq-build/references/team-mode.md:138` | phải có mặt trong report. Tỉ lệ giao thấp mà không có lý do trong bảng tra nghĩa là bạn |
| L104 | `skills/tdq-build/references/team-mode.md:139` | đã lách luật của user — user chọn mode đội là để có một đội, không phải một lời hứa. |
| L105 | `skills/tdq-check-status/SKILL.md:8` | Nạp [tdq-conventions](../tdq-conventions/SKILL.md). Skill này KHÔNG thuộc phase nào: gọi |
| L106 | `skills/tdq-check-status/SKILL.md:17` | Cấm tuyệt đối** `tdq_state.py` với lệnh con `init` hay `reset`, cấm xoá hay ghi đè |
| L107 | `skills/tdq-check-status/SKILL.md:19` | Chỉ được chạy lệnh vá thuộc đúng hai họ: `tdq_state.py set …` và `tdq_state.py approve …`. |
| L108 | `skills/tdq-check-status/SKILL.md:22` | Kết luận `CẦN USER QUYẾT` thì DỪNG, trình câu hỏi, cấm tự đoán ý user. |
| L109 | `skills/tdq-check-status/SKILL.md:39` | ý nghĩa và giới hạn của nó. Bảng đó là nguồn duy nhất; cấm tự nghĩ thêm chẩn đoán. |
| L110 | `skills/tdq-check-status/SKILL.md:44` | "Chạy các lệnh vá này rồi tiếp tục?" **DỪNG chờ user.** |
| L111 | `skills/tdq-check-status/SKILL.md:46` | conventions, **DỪNG chờ user**. Cấm chạy lệnh vá nào. |
| L112 | `skills/tdq-check-status/SKILL.md:49` | Lệnh nào không thuộc hai họ `set`/`approve` thì KHÔNG chạy và báo lại — đó là lỗi của |
| L113 | `skills/tdq-check-status/SKILL.md:50` | bộ dò, không phải việc để tự sửa tay. |
| L114 | `skills/tdq-check-status/SKILL.md:57` | trình lại đúng cổng đó rồi DỪNG chờ user duyệt. |
| L115 | `skills/tdq-check-status/references/bang-lech.md:10` | Ba mức: `ok` chỉ để biết · `canh-bao` nên vá trước khi đi tiếp · `chan` phải để user quyết. |
| L116 | `skills/tdq-check-status/references/bang-lech.md:11` | Cột lệnh vá là MẪU. Chỗ viết hoa gạch dưới phải thay bằng giá trị thật trước khi chạy. |
| L117 | `skills/tdq-check-status/references/bang-lech.md:16` | \| D1 \| không đọc được request nào (không có, phase = idle, hoặc state hỏng) \| ok \| Đĩa trống thì mở request mới bằng tdq-intake; đĩa còn spec/p… |
| L118 | `skills/tdq-check-status/references/bang-lech.md:18` | \| D3 \| sha256 của spec lệch với lúc duyệt (plan lệch chỉ là `ok`) \| chan \| File đã sửa sau khi duyệt — cần user duyệt lại, cấm tự approve. \| —… |
| L119 | `skills/tdq-check-status/references/bang-lech.md:32` | là chuyện hằng ngày. Đổi phạm vi plan phải nhìn bằng mắt, bảng này không bắt được. |
| L120 | `skills/tdq-check-status/references/bang-lech.md:40` | D12 chỉ có ở mode `subagent`. Dấu `[>]` là "đã giao cho agent con", KHÔNG phải lỗi — |
| L121 | `skills/tdq-conventions/SKILL.md:20` | Cuối turn có đổi repo: **bắt buộc** chạy lệnh đóng sổ |
| L122 | `skills/tdq-conventions/SKILL.md:22` | — lint đúng file → append working log → set phase → graphify. **Cấm Edit/Read rồi tự |
| L123 | `skills/tdq-conventions/SKILL.md:24` | lệnh", không phải "gọi lệnh khác để né"). Lệnh này phải là **hành động cuối** của turn, |
| L124 | `skills/tdq-conventions/SKILL.md:29` | của turn. Cấm gọi rỗng: mỗi lần gọi phải kèm `--files` và `--log` của việc vừa xong. |
| L125 | `skills/tdq-conventions/SKILL.md:31` | việc, lỗi tool) → message cuối phải in **LẠI NGUYÊN VĂN 100%** khối đó. Gồm tóm tắt, |
| L126 | `skills/tdq-conventions/SKILL.md:32` | câu hỏi, ĐỦ option, dòng `➤ Duyệt:`. Đặt NGAY SAU dòng `✓ [TDQ:<MÃ>]`. Lý do: focus mode |
| L127 | `skills/tdq-conventions/SKILL.md:34` | mất sạch câu hỏi và option. Cấm rút gọn, cấm trỏ ngược. |
| L128 | `skills/tdq-conventions/SKILL.md:45` | Hết ngân sách bước KHÔNG phải ngoại lệ: báo rồi làm tiếp. "Để turn sau cho gọn" cũng vậy. |
| L129 | `skills/tdq-conventions/SKILL.md:52` | Bảng đầy đủ (vào khi / việc duy nhất / lệnh chuyển tiếp / xong khi / cấm): |
| L130 | `skills/tdq-conventions/SKILL.md:59` | Cấm sửa tay `docs/tdq/state.json` và `docs/tdq/STATE.md` (mirror tự sinh, chỉ để đọc). |
| L131 | `skills/tdq-conventions/SKILL.md:64` | `reset` chỉ khi user đóng hẳn request. Muốn thử nghiệm workflow thì chạy vào project |
| L132 | `skills/tdq-conventions/SKILL.md:65` | rác: đặt `TDQ_PROJECT_DIR=/tmp/...` ngay trên chính lệnh đó (cấm dùng `\|\|` fallback). |
| L133 | `skills/tdq-conventions/SKILL.md:70` | User duyệt bằng chat thường — không có cú pháp bắt buộc, không có gate chặn user. |
| L134 | `skills/tdq-conventions/SKILL.md:71` | Dấu hiệu duyệt, phản ví dụ, và lệnh phải chạy: [references/approval.md](references/approval.md). |
| L135 | `skills/tdq-conventions/SKILL.md:73` | Ba luật không được phá: |
| L136 | `skills/tdq-conventions/SKILL.md:74` | Mơ hồ → **HỎI**, tuyệt đối không suy diễn là đã duyệt. |
| L137 | `skills/tdq-conventions/SKILL.md:97` | Ảnh user gửi kèm.** Turn có ảnh đính kèm VÀ phải ghi working log → copy ảnh vào |
| L138 | `skills/tdq-conventions/SKILL.md:110` | Search web: `tavily-primary` trước, luôn luôn. Failover và mẫu dùng nâng cao: |
| L139 | `skills/tdq-conventions/SKILL.md:112` | Mọi khẳng định phải có nguồn hoặc căn cứ nêu rõ. Không bịa. |
| L140 | `skills/tdq-conventions/SKILL.md:120` | Bảng model/effort mặc định theo vai + luật override: [references/subagent-tuning.md](references/subagent-tuning.md). |
| L141 | `skills/tdq-conventions/SKILL.md:125` | chỉ ảnh hưởng nhẹ. Nên luật này thuộc tầng **runtime**, không phải context cost. |
| L142 | `skills/tdq-conventions/SKILL.md:133` | Bảng cấm gộp, luật đọc lại (mềm), đọc vừa đủ, giao việc nặng cho subagent: |
| L143 | `skills/tdq-conventions/SKILL.md:140` | Clean code là hành vi thường trực, không phải cổng hỏi. Mọi lần viết/sửa code, tổ chức |
| L144 | `skills/tdq-conventions/SKILL.md:144` | Sản phẩm build ra luôn có log service bật mặc định (timestamp, đủ chi tiết debug, tắt được qua config). |
| L145 | `skills/tdq-conventions/SKILL.md:145` | Mỗi task trong plan có test riêng; task pass là tick `[x]` NGAY, không gom cuối turn. |
| L146 | `skills/tdq-conventions/references/approval.md:4` | phải phán đoán rộng tay. |
| L147 | `skills/tdq-conventions/references/approval.md:26` | \| `ok tôi hiểu rồi` \| phản hồi hiểu, không phải chấp thuận \| HỎI lại \| |
| L148 | `skills/tdq-conventions/references/approval.md:29` | \| `duyệt spec` khi đang chờ **plan** \| sai đối tượng \| Chỉ ghi spec, KHÔNG suy ra plan \| |
| L149 | `skills/tdq-conventions/references/approval.md:39` | `--by` bắt buộc trên thực tế: đó là dấu vết duy nhất nối state với hội thoại. |
| L150 | `skills/tdq-conventions/references/approval.md:40` | Duyệt lại lần nữa không phải lỗi (idempotent, exit 0). |
| L151 | `skills/tdq-conventions/references/clean-code.md:5` | Clean code ở bộ workflow này KHÔNG phải một cổng hỏi và KHÔNG phải một lượt chạy linter |
| L152 | `skills/tdq-conventions/references/clean-code.md:63` | PHÁN XÉT trên dữ liệu đã đọc. Đổi cách đọc không phải sửa cách chấm. |
| L153 | `skills/tdq-conventions/references/clean-code.md:66` | Đổi khuôn bảng in cũng phải sửa hàm đọc file. |
| L154 | `skills/tdq-conventions/references/clean-code.md:74` | Mỗi skill mới lại phải mở thân hàm ra sửa. |
| L155 | `skills/tdq-conventions/references/clean-code.md:82` | phải đoán, và đoán sai thì nổ ở chỗ khác. |
| L156 | `skills/tdq-conventions/references/clean-code.md:85` | SUY DIỄN của repo này, không phải trích Liskov — đừng dẫn nó như nguyên văn. |
| L157 | `skills/tdq-conventions/references/clean-code.md:93` | một file plan bất kỳ thì phải dựng một state giả, kể cả trong test. |
| L158 | `skills/tdq-conventions/references/clean-code.md:100` | SAI — một hook tự `json.dump` thẳng vào `docs/tdq/state.json`. Đổi định dạng state là phải |
| L159 | `skills/tdq-conventions/references/context-budget.md:16` | p90 12,3 s. Tổng thời gian tỉ lệ THẲNG với số bước, nên đây là tầng runtime, không phải |
| L160 | `skills/tdq-conventions/references/context-budget.md:22` | `&&`, hoặc `;` khi muốn chạy hết dù có lệnh lỗi. Cấm tách thành nhiều lượt chỉ để |
| L161 | `skills/tdq-conventions/references/context-budget.md:25` | đừng đọc lại file. Nhưng BẮT BUỘC đọc lại khi gặp một trong năm ca dưới đây. Luật này |
| L162 | `skills/tdq-conventions/references/context-budget.md:28` | điều kiện. Cấm vòng `sleep` thăm dò: mỗi vòng là một bước tròn mà không thêm thông tin. |
| L163 | `skills/tdq-conventions/references/context-budget.md:32` | Context đã bị nén — thứ còn lại là bản tóm tắt, không phải nội dung file. |
| L164 | `skills/tdq-conventions/references/context-budget.md:35` | Sắp sửa chính file đó — trước khi Edit phải có nội dung mới nhất. |
| L165 | `skills/tdq-conventions/references/context-budget.md:40` | agent có context riêng, nó phải tự đọc. |
| L166 | `skills/tdq-conventions/references/context-budget.md:46` | \| Ca \| Vì sao cấm gộp \| |
| L167 | `skills/tdq-conventions/references/context-budget.md:49` | \| Đang khoanh vùng lỗi \| gộp 5 lệnh rồi lỗi ở đâu không biết, phải chạy lại từng lệnh, tốn nhiều bước hơn \| |
| L168 | `skills/tdq-conventions/references/context-budget.md:50` | \| Lệnh phá hủy hoặc khó đảo \| xoá, ghi đè, `git reset` — phải xem kết quả lệnh trước rồi mới chạy lệnh sau \| |
| L169 | `skills/tdq-conventions/references/context-budget.md:63` | Lint đúng file.** Chạy `doc_lint.py` trên ĐÚNG file vừa sửa, cấm truyền cả thư mục |
| L170 | `skills/tdq-conventions/references/context-budget.md:65` | CLI im lặng.** `tdq_state.py init\|set\|reset` mặc định in 1 dòng; chỉ thêm `--json` |
| L171 | `skills/tdq-conventions/references/context-budget.md:68` | Cấm `cat` (dùng Read), cấm `grep -A5 -B5` khi `-c`/`-l` đã đủ trả lời. |
| L172 | `skills/tdq-conventions/references/measure-scenario.md:9` | Dùng một project thử tách biệt (không phải repo chính) để không lẫn log: |
| L173 | `skills/tdq-conventions/references/measure-scenario.md:40` | equiv-input token — đây là bằng chứng carry-cost, không phải ước lượng. |
| L174 | `skills/tdq-conventions/references/phases.md:7` | \| phase \| vào khi \| việc duy nhất \| lệnh chuyển tiếp \| xong khi \| cấm \| |
| L175 | `skills/tdq-conventions/references/phases.md:11` | \| `spec` \| Đã phân tích xong \| Viết spec (kèm mục Lộ trình), đăng ký spec_file, trình tóm tắt rồi DỪNG chờ user duyệt \| `python3 "${CLAUDE_PLUG… |
| L176 | `skills/tdq-conventions/references/phases.md:12` | \| `plan` \| spec_approved = true \| Viết plan kèm mode ĐỀ XUẤT, đăng ký plan_file, trình rồi DỪNG chờ duyệt \| `python3 "${CLAUDE_PLUGIN_ROOT}/scr… |
| L177 | `skills/tdq-conventions/references/phases.md:13` | \| `mode` \| plan_approved = true mà implement_mode chưa chốt \| Giải thích ngắn gọn 2 mode rồi hỏi user chọn, DỪNG chờ trả lời \| `python3 "${CLAU… |
| L178 | `skills/tdq-conventions/references/phases.md:18` | \| `quick` \| lane = quick \| Phân tích → mini-spec/plan gộp 1 file → chờ duyệt → ghi working log TRƯỚC → implement → QC bám DoD (mặc định BẬT) → v… |
| L179 | `skills/tdq-conventions/references/plugin-routing.md:9` | Vẫn phải **HỎI user trước** khi: cài plugin/marketplace MỚI; chạy OAuth hoặc nhập |
| L180 | `skills/tdq-conventions/references/plugin-routing.md:16` | Chỉ dùng đúng tên ở cột phải. |
| L181 | `skills/tdq-conventions/references/plugin-routing.md:51` | Muốn quay lại lazy-load cho nhẹ context: thêm tên plugin vào `on_demand` (tắt mặc định, |
| L182 | `skills/tdq-conventions/references/plugin-routing.md:53` | (cấm bật) trong `~/.claude/plugin-tiers.json` — chỉ khi user yêu cầu rõ. |
| L183 | `skills/tdq-conventions/references/reminder-codes.md:4` | những dòng dạng `[TDQ:<MÃ>] <việc phải làm>`. |
| L184 | `skills/tdq-conventions/references/reminder-codes.md:15` | \| Mã \| Nghĩa \| Việc phải làm \| Hiệu ứng hook kiểm \| |
| L185 | `skills/tdq-conventions/references/reminder-codes.md:35` | Sổ turn** `docs/tdq/.tdq-turn.jsonl` — ghi lại mọi lần sửa file đi qua tool |
| L186 | `skills/tdq-conventions/references/reminder-codes.md:52` | Project **không phải git repo** thì không có vân tay repo: chiều "đã ghi log" |
| L187 | `skills/tdq-conventions/references/reminder-codes.md:58` | đang bẩn đầu tiên, có thể không phải file vừa sửa. |
| L188 | `skills/tdq-conventions/references/soul.md:4` | dù cũ hay mới — thì sửa luật đó, không sửa soul. Muốn đổi soul phải có user duyệt. |
| L189 | `skills/tdq-conventions/references/soul.md:16` | Tầng 1 — chất lượng**: code agent làm ra phải đạt MVP thật — chạy đúng, có test, |
| L190 | `skills/tdq-conventions/references/soul.md:29` | Mọi rule và behavior phải đủ chi tiết để model thấp như Haiku đọc là làm đúng, |
| L191 | `skills/tdq-conventions/references/soul.md:33` | `## Tự kiểm` (một lệnh hoặc một câu hỏi có/không). Chỗ dễ hiểu nhầm phải kèm |
| L192 | `skills/tdq-conventions/references/soul.md:76` | \| Đổi đúng-sai của đầu ra \| 1 — chất lượng \| test trước khi sửa, cấm mock giả làm dữ liệu thật \| |
| L193 | `skills/tdq-conventions/references/soul.md:77` | \| Đổi SỐ BƯỚC (số tool call, số vòng chờ) \| 2 — runtime \| gộp tool call độc lập, cấm vòng `sleep` thăm dò \| |
| L194 | `skills/tdq-conventions/references/soul.md:81` | vừa cắt bước vừa cắt token → tầng 2, không phải tầng 3. |
| L195 | `skills/tdq-conventions/references/soul.md:83` | Hệ quả về chỗ đặt: luật tầng 1 và tầng 2 phải nằm trong thân skill được nạp mỗi turn; |
| L196 | `skills/tdq-conventions/references/soul.md:85` | của skill là ràng buộc tầng 3 — gặp trần thì nới trần, cấm nén luật tầng 2 cho vừa. |
| L197 | `skills/tdq-conventions/references/soul.md:93` | Lệnh: `python3 -m pytest tests/test_soul_rules.py -q` phải xanh. |
| L198 | `skills/tdq-conventions/references/subagent-tuning.md:10` | \| `model` \| frontmatter agent (mặc định) **và** tham số `model` của Agent tool khi gọi \| **Có** — tham số lúc gọi đè frontmatter \| |
| L199 | `skills/tdq-conventions/references/subagent-tuning.md:20` | \| `tdq-qc-tester` \| inherit \| high \| phải nghi ngờ và đào biên, không chỉ chạy lại lệnh \| |
| L200 | `skills/tdq-conventions/references/subagent-tuning.md:36` | \| Viết code, sửa logic, thiết kế, review, QC \| bỏ trống (giữ mặc định của agent) \| |
| L201 | `skills/tdq-conventions/references/subagent-tuning.md:39` | Ghi lý do override vào working log khi lệch khỏi mặc định — 1 dòng là đủ. |
| L202 | `skills/tdq-conventions/references/subagent-tuning.md:45` | NGAY CẢ KHI user đang để phiên ở `high`. Chỉ đặt `low` cho agent thuần cơ học. |
| L203 | `skills/tdq-conventions/references/subagent-tuning.md:47` | Muốn effort thật sự thay đổi theo task thì phải tách agent thành nhiều biến thể — |
| L204 | `skills/tdq-conventions/references/subagent-tuning.md:55` | frontmatter (khi agent active) > mức của phiên > mặc định model. Tra 2026-08-04. |
| L205 | `skills/tdq-conventions/references/user-facing-block.md:4` | không phải người trong nghề: họ cần biết đang xem cái gì, xem chi tiết ở đâu, và phải |
| L206 | `skills/tdq-conventions/references/user-facing-block.md:43` | thêm ký tự đánh dấu**, không phải viết lại chữ: bảy luật dưới đây không cho phép đổi, |
| L207 | `skills/tdq-conventions/references/user-facing-block.md:55` | chỉ được in đậm bên trong phần nội dung, không đụng vào phần `- A (đề xuất): `. |
| L208 | `skills/tdq-conventions/references/user-facing-block.md:60` | Không emoji** ở bất kỳ thành phần nào. Dấu `➤` giữ nguyên, nó không phải emoji. |
| L209 | `skills/tdq-conventions/references/user-facing-block.md:62` | Cấm gộp lựa chọn vào đoạn văn. |
| L210 | `skills/tdq-conventions/references/user-facing-block.md:71` | Trong khối in ra cho user chỉ được dùng đúng sáu ký hiệu ngoài ASCII: |
| L211 | `skills/tdq-conventions/references/user-facing-block.md:82` | Ký tự nào không nằm trong bảng thì không được thêm vào, kể cả khi nhìn có vẻ vô hại. |
| L212 | `skills/tdq-conventions/references/user-facing-block.md:85` | (`─` `│` `├` `└` `┌` `┬` `┐`) cũng bị cấm: chúng đòi canh cột, mà bề rộng terminal thì |
| L213 | `skills/tdq-conventions/references/user-facing-block.md:95` | <!-- Khối "Trước" cố tình sai khuôn: nó là ví dụ đối chiếu, không phải mẫu để chép. --> |
| L214 | `skills/tdq-conventions/references/worklog-images.md:3` | Áp dụng khi turn có ảnh đính kèm **và** turn đó phải ghi working log (có đổi repo). |
| L215 | `skills/tdq-conventions/references/worklog-images.md:14` | truyền cho `--log`, cạnh câu mô tả ảnh đó. Không bắt buộc đặt ở đầu chuỗi. |
| L216 | `skills/tdq-intake/SKILL.md:24` | Luật thoát (bắt buộc).** Giữa chừng vi phạm bất kỳ điều kiện nào → DỪNG tay, nói rõ |
| L217 | `skills/tdq-intake/SKILL.md:25` | điều kiện nào vỡ, rồi mở request bình thường từ Phần A. Cấm làm tiếp ở tầng `nhỏ`. |
| L218 | `skills/tdq-intake/SKILL.md:29` | Định nghĩa "yêu cầu mới": MỌI prompt của user khi KHÔNG có request mở — request mở |
| L219 | `skills/tdq-intake/SKILL.md:47` | cỡ/nhu cầu (`Cỡ:/Cần:`) là bước NỘI BỘ — dùng để chọn phương án đề xuất, KHÔNG in dòng |
| L220 | `skills/tdq-intake/SKILL.md:53` | DỪNG chờ user trả lời.** Không tự chọn lane. |
| L221 | `skills/tdq-intake/SKILL.md:83` | rồi sang [tdq-spec](../tdq-spec/SKILL.md) — cùng turn nếu interview đã xong, còn phải |
| L222 | `skills/tdq-intake/SKILL.md:88` | Chế độ nhanh = rút gọn, KHÔNG cắt bước tư duy. Chín bước thi hành — từ phân tích tới hỏi |
| L223 | `skills/tdq-intake/SKILL.md:90` | `## Chín bước thi hành`. **BẮT BUỘC mở file đó và đọc hết chín bước trước khi làm bước 1; |
| L224 | `skills/tdq-intake/SKILL.md:91` | cấm làm theo trí nhớ.** Cùng file đó có luôn khuôn mini-plan, luật tick, luật QC và vòng fix. |
| L225 | `skills/tdq-intake/references/analyze-full.md:20` | này rồi trình user chốt; chưa chốt thì mọi dòng trong đó là gợi ý, không phải luật. |
| L226 | `skills/tdq-intake/references/analyze-full.md:22` | dòng "tầng X không được gọi tầng Y" kèm lý do. `## Hub`: 5 node nhiều liên kết nhất |
| L227 | `skills/tdq-intake/references/analyze-full.md:23` | kèm số bậc, lấy từ `graphify god-nodes`; sửa node trong đó là rủi ro cao, phải khai |
| L228 | `skills/tdq-intake/references/analyze-full.md:24` | ở dòng `Chạm:` của plan. `## Đã chốt`: quyết định đã đóng kèm ngày; muốn đổi phải |
| L229 | `skills/tdq-intake/references/analyze-full.md:27` | Luật ĐỌC đồ thị graphify** (gợi ý có điều kiện, KHÔNG bắt buộc mỗi lần analyze): |
| L230 | `skills/tdq-intake/references/analyze-full.md:37` | (luật failover ở [tavily.md](../../tdq-conventions/references/tavily.md)). Mặc định giao |
| L231 | `skills/tdq-intake/references/analyze-full.md:40` | Kết quả tavily thô nằm lại context tốn ~14M token/2 session — đó là lý do bắt buộc. |
| L232 | `skills/tdq-intake/references/analyze-full.md:42` | Bỏ qua chỉ khi việc thuần nội bộ, không có ẩn số bên ngoài. |
| L233 | `skills/tdq-intake/references/analyze-full.md:58` | chia subagent…). Khung bất biến không được bỏ: phân tích → spec/plan → implement → |
| L234 | `skills/tdq-intake/references/analyze-full.md:71` | rồi sang [tdq-spec](../../tdq-spec/SKILL.md) — cùng turn nếu interview đã xong, còn phải |
| L235 | `skills/tdq-intake/references/interview.md:8` | có điều kiện, luật đầy đủ ở [scope-round.md](scope-round.md). Bỏ thì phải ghi lý do. |
| L236 | `skills/tdq-intake/references/interview.md:51` | Cấm gộp** nhiều option vào một dòng hay nhét vào đoạn văn dạng `(a) … · (b) …`. |
| L237 | `skills/tdq-intake/references/interview.md:90` | Còn một câu làm đổi → hỏi tiếp vòng nữa. Cấm chuyển sang viết spec khi còn chỗ phải đoán. |
| L238 | `skills/tdq-intake/references/issue-triage.md:3` | Áp dụng khi yêu cầu mới là **báo lỗi** chứ không phải làm tính năng: "chạy sai", "bị treo", |
| L239 | `skills/tdq-intake/references/issue-triage.md:20` | Chốt căn cứ rồi mới lập spec.** Spec fix phải nêu được nguyên nhân gốc, cách sửa, |
| L240 | `skills/tdq-intake/references/lane-decision.md:25` | \| Yêu cầu đã rõ chưa \| rõ, không phải hỏi gì \| còn chỗ mơ hồ / cần research \| |
| L241 | `skills/tdq-intake/references/quick-lane.md:3` | Chế độ nhanh khác chế độ chuyên sâu ở chỗ **gộp tài liệu và gộp gate**, không phải ở |
| L242 | `skills/tdq-intake/references/quick-lane.md:5` | làm đổi kết quả đều GIỮ. Chỉ bỏ khi việc thuần nội bộ hoặc đã rõ hết — và phải nói rõ |
| L243 | `skills/tdq-intake/references/quick-lane.md:16` | \| QC \| file `qc/<slug>.md` \| mỗi dòng DoD một phép kiểm, ghi vào mục ## QC của plan (mặc định BẬT) \| |
| L244 | `skills/tdq-intake/references/quick-lane.md:40` | Đây là toàn bộ Phần C của [SKILL.md](../SKILL.md) — chuyển về đây để thân skill không phải |
| L245 | `skills/tdq-intake/references/quick-lane.md:41` | nạp nhánh này mỗi lần gọi. Vào chế độ nhanh là **bắt buộc** đọc hết chín bước dưới đây |
| L246 | `skills/tdq-intake/references/quick-lane.md:42` | trước khi làm bước 1; cấm làm theo trí nhớ. |
| L247 | `skills/tdq-intake/references/quick-lane.md:57` | In đúng dòng: `➤ Duyệt: nhắn "duyệt nhanh" (bỏ QC: "duyệt nhanh không QC"; "duyệt quick" vẫn chạy — duyệt xong implement ngay) · Góp ý: nhắn trực t… |
| L248 | `skills/tdq-intake/references/quick-lane.md:71` | `[x]` NGAY khi test xanh — cấm gom tick cuối turn. Rồi chạy **QC** (mặc định BẬT): mỗi dòng DoD một |
| L249 | `skills/tdq-intake/references/quick-lane.md:78` | fix có thể làm hỏng. Có trần 3 vòng — vượt trần thì DỪNG, báo user, đề xuất chuyển lane |
| L250 | `skills/tdq-intake/references/quick-lane.md:146` | Đổi `[~]`/`[>]` → `[x]` **NGAY**, không đợi task sau. |
| L251 | `skills/tdq-intake/references/quick-lane.md:148` | Chỉ một task mang `[~]` tại một thời điểm. **Cấm gom tick vào cuối turn** — chế độ nhanh (express) |
| L252 | `skills/tdq-intake/references/quick-lane.md:151` | Hàng rào: `hooks/scripts/edit_gate.py` **CHẶN** (deny) mọi lần sửa file ngoài `docs/` và |
| L253 | `skills/tdq-intake/references/quick-lane.md:159` | Mặc định **BẬT**. Làm ngay sau khi implement xong, **số hạng mục bằng số dòng DoD** |
| L254 | `skills/tdq-intake/references/quick-lane.md:177` | User im lặng về QC = CÓ QC. Khi đó mục `## QC` vẫn phải có, đúng 1 dòng: |
| L255 | `skills/tdq-intake/references/quick-lane.md:191` | Trần 3 vòng.** Vượt trần → DỪNG, báo user, đề xuất chuyển chế độ chuyên sâu (deep). Giữ |
| L256 | `skills/tdq-intake/references/quick-lane.md:192` | `phase=implement`, KHÔNG chạy `set phase=idle`. |
| L257 | `skills/tdq-intake/references/scope-round.md:29` | Không dấu hiệu nào → BỎ vòng scope, đi thẳng vòng chi tiết. Khi BỎ, brief phải có đúng |
| L258 | `skills/tdq-intake/references/scope-round.md:30` | một dòng, không được im lặng: |
| L259 | `skills/tdq-intake/references/scope-round.md:36` | Dòng lý do bắt buộc này là hàng rào: "có điều kiện" nghĩa là có tiêu chí, không phải tuỳ |
| L260 | `skills/tdq-intake/references/scope-round.md:64` | Mặt nào yêu cầu đã nói rõ rồi thì KHÔNG đưa vào option, ghi thẳng là đã chốt. |
| L261 | `skills/tdq-intake/references/scope-round.md:68` | CẤM hỏi mức độ trừu tượng.** Không hỏi "bạn muốn gọn nhất, vừa đủ, hay đầy đủ chuyên |
| L262 | `skills/tdq-intake/references/scope-round.md:81` | \| Ràng buộc nền tảng \| thiết bị, OS, engine, thư viện bắt buộc \| không ràng buộc · một nền tảng · nhiều nền tảng \| |
| L263 | `skills/tdq-intake/references/scope-round.md:101` | Suy xong phải in đúng một dòng, đặt kèm khối câu hỏi của vòng chi tiết: |
| L264 | `skills/tdq-intake/references/scope-round.md:107` | Dòng này để user cãi được ngay nếu bạn suy sai. Nó **không** phải một cổng duyệt mới — |
| L265 | `skills/tdq-intake/references/skill-inventory.md:15` | Cờ `--loc` cắt bảng còn phần liên quan, KHÔNG bao giờ ẩn skill nguồn `project` hay |
| L266 | `skills/tdq-intake/references/skill-inventory.md:17` | BẮT BUỘC chạy lại `--tat-ca` rồi mới phán quyết. |
| L267 | `skills/tdq-intake/references/skill-inventory.md:34` | \| Đã xét <N> skill khác \| user/plugin/built-in \| KHÔNG \| khác lĩnh vực \| |
| L268 | `skills/tdq-intake/references/skill-inventory.md:37` | Ví dụ dòng đã điền (KHÔNG chép vào bảng thật): |
| L269 | `skills/tdq-intake/references/skill-inventory.md:39` | `\| Đã xét 240 skill khác \| plugin \| KHÔNG \| khác lĩnh vực \|` |
| L270 | `skills/tdq-intake/references/skill-inventory.md:51` | \| Khớp đúng 1 trong 4 lý do loại ở bảng dưới \| `KHÔNG` + lý do \| |
| L271 | `skills/tdq-intake/references/skill-inventory.md:61` | \| `user đã cấm` \| User đã nói không dùng \| |
| L272 | `skills/tdq-intake/references/skill-inventory.md:65` | `DÙNG` → spec chép dòng đó vào mục `## 3b` · plan phải có **khối hợp đồng 5 trường** |
| L273 | `skills/tdq-intake/references/skill-inventory.md:67` | `KHÔNG` → chép nguyên dòng vào spec §3b, không cần gì thêm. |
| L274 | `skills/tdq-plan/SKILL.md:3` | description: Biến spec thành plan checkbox, mỗi task một test: DỪNG chờ user duyệt plan, rồi hỏi cách chạy và build cùng turn. Dùng khi spec chế độ… |
| L275 | `skills/tdq-plan/SKILL.md:10` | Yêu cầu `spec_approved = true`. User duyệt spec xong là viết plan NGAY trong cùng turn. |
| L276 | `skills/tdq-plan/SKILL.md:40` | Mọi task tạo/sửa file mã nguồn phải có dòng `Chạm:` ngay dưới nó**, liệt kê đường |
| L277 | `skills/tdq-plan/SKILL.md:52` | `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/doc_lint.py" --pair <spec> <plan>` phải exit 0. |
| L278 | `skills/tdq-plan/SKILL.md:59` | Không** set `implement_mode` ở đây — trường đó chỉ được ghi khi ghi nhận duyệt. |
| L279 | `skills/tdq-plan/SKILL.md:61` | Trình bày & DỪNG.** Viết khối trình plan theo |
| L280 | `skills/tdq-plan/SKILL.md:79` | Phần nội dung ≤ 10 dòng, là tóm tắt THẬT — cấm thay bằng thông báo suông kiểu "đã ghi |
| L281 | `skills/tdq-plan/SKILL.md:81` | trước đoạn trích: "(khuôn mẫu — áp dụng cho các lần hỏi sau, không phải câu hỏi của |
| L282 | `skills/tdq-plan/SKILL.md:84` | User duyệt → ghi nhận NGAY, rồi hỏi cách chạy trong CÙNG turn:** |
| L283 | `skills/tdq-plan/SKILL.md:90` | Cấm hỏi lại thứ user vừa nói. |
| L284 | `skills/tdq-plan/SKILL.md:91` | Chưa nói mode → state dừng ở phase `mode`, in khối hỏi rồi DỪNG. Khuôn nguyên văn — |
| L285 | `skills/tdq-plan/SKILL.md:95` | Ngay dưới hai option phải có đoạn **"Vì sao đề xuất"** dài 1–3 dòng. Cấm nói chung |
| L286 | `skills/tdq-plan/SKILL.md:101` | User trả lời → chạy lại lệnh trên kèm `--mode <main\|subagent>` rồi build LUÔN cùng |
| L287 | `skills/tdq-plan/SKILL.md:102` | turn. Mode chốt là mode user NÓI (khác đề xuất cũng được); cấm tự chọn thay user. |
| L288 | `skills/tdq-plan/SKILL.md:107` | rồi sang [tdq-build](../tdq-build/SKILL.md) **NGAY trong cùng turn**. |
| L289 | `skills/tdq-plan/references/mode-gate.md:27` | Dài 1–3 dòng, đặt ngay dưới hai option. Cấm nói chung chung. Mọi câu phải dựa trên |
| L290 | `skills/tdq-plan/references/mode-gate.md:39` | Kết bằng đúng một câu nói vì sao KHÔNG chọn phương án còn lại. |
| L291 | `skills/tdq-plan/references/mode-gate.md:48` | Mode B là mô hình lai, không phải "mọi task đều đẩy cho agent con". Leader vẫn tự làm |
| L292 | `skills/tdq-plan/references/mode-gate.md:50` | `file-luat`, `hop-dong`. Phần còn lại bắt buộc phải giao — và `scripts/tdq_team.py` |
| L293 | `skills/tdq-plan/references/mode-gate.md:56` | phải tổng số task, mới quyết định B có nhanh hơn A hay không. Luật đầy đủ của mode đội: |
| L294 | `skills/tdq-plan/references/plan-template.md:31` | `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong. |
| L295 | `skills/tdq-plan/references/plan-template.md:32` | Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau. |
| L296 | `skills/tdq-plan/references/plan-template.md:33` | Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó. |
| L297 | `skills/tdq-plan/references/plan-template.md:56` | Vì vậy **mọi task tạo hoặc sửa file mã nguồn đều phải có dòng `Chạm:`**, kể cả task tạo |
| L298 | `skills/tdq-plan/references/plan-template.md:57` | file mới. Đường dẫn phải nằm trong backtick và phải là đường dẫn thật tính từ gốc repo. |
| L299 | `skills/tdq-plan/references/plan-template.md:59` | leader phải tự làm, mất chỗ chạy song song. Task chỉ sửa tài liệu thì bỏ dòng này. |
| L300 | `skills/tdq-plan/references/plan-template.md:60` | Node nằm trong mục `## Hub` của `docs/kien-truc.md` → task phải thêm một dòng DoD kiểm |
| L301 | `skills/tdq-plan/references/plan-template.md:87` | khác nhau, nên chúng KHÔNG được đụng chung một file — git không hề cảnh báo, tới lúc |
| L302 | `skills/tdq-plan/references/plan-template.md:107` | Ra: <artifact phải tồn tại sau task, có đường dẫn> |
| L303 | `skills/tdq-plan/references/plan-template.md:109` | Không dùng cho: <việc kề bên mà skill này KHÔNG được lan sang> |
| L304 | `skills/tdq-plan/references/plan-template.md:111` | Luật nhãn `(mcp)` — BẮT BUỘC ghi ngay khi lập plan: skill nào cần MCP tool lúc |
| L305 | `skills/tdq-plan/references/plan-template.md:112` | chạy (gọi server MCP, ví dụ tavily/notion) → dòng `Dùng:` phải kết thúc bằng nhãn |
| L306 | `skills/tdq-plan/references/plan-template.md:114` | này để biết task nào buộc phải do Claude tự làm, không giao sub-agent thiếu MCP. |
| L307 | `skills/tdq-plan/references/plan-template.md:117` | Phase này bắt buộc **chỉ khi việc này có runtime** — tức có ít nhất một task tạo hoặc sửa |
| L308 | `skills/tdq-plan/references/plan-template.md:121` | [ ] **Tx.1** Log service bật mặc định (timestamp, mức log, tắt được qua config) — Test: <...> |
| L309 | `skills/tdq-plan/references/plan-template.md:132` | chạy, không phải thời gian người chờ). Đơn vị luôn là phút, số nguyên 1–999, không viết |
| L310 | `skills/tdq-plan/references/plan-template.md:140` | `eNm` KHÔNG đổi luật tick `[ ] [~] [x]` và không phải cam kết thời gian với user. |
| L311 | `skills/tdq-spec/SKILL.md:3` | description: Viết spec tiếng Việt cho request TDQ, đăng ký vào state, trình rồi DỪNG chờ duyệt; duyệt xong viết plan cùng turn. Dùng khi chế độ chu… |
| L312 | `skills/tdq-spec/SKILL.md:15` | Mục bắt buộc: mục tiêu & phạm vi (in/out) · **Lộ trình** (chép từ brief: phase |
| L313 | `skills/tdq-spec/SKILL.md:20` | yêu cầu bắt buộc (log service bật mặc định, không placeholder, test cho từng phần) · |
| L314 | `skills/tdq-spec/SKILL.md:22` | Mục "câu hỏi còn mở" PHẢI rỗng — còn câu hỏi thì quay lại phase `analyze`. |
| L315 | `skills/tdq-spec/SKILL.md:34` | Trình bày & DỪNG.** Viết khối trình spec theo |
| L316 | `skills/tdq-spec/SKILL.md:53` | Phần nội dung ≤ 50 dòng và phải là tóm tắt THẬT — cấm thay bằng câu thông báo suông |
| L317 | `skills/tdq-spec/SKILL.md:57` | hỏi sau, không phải câu hỏi của turn này)". Mục đích: đọc lại transcript không nhầm là |
| L318 | `skills/tdq-spec/SKILL.md:62` | User duyệt → ghi nhận NGAY:** |
| L319 | `skills/tdq-spec/SKILL.md:71` | rồi sang [tdq-plan](../tdq-plan/SKILL.md) **NGAY trong cùng turn** — không bắt user |
| L320 | `skills/tdq-spec/references/spec-template.md:4` | áp dụng, nhưng phải nói rõ **vì sao** không áp dụng. |
| L321 | `skills/tdq-spec/references/spec-template.md:33` | BẮT BUỘC chép các mặt bị loại ở brief `### Phạm vi đã chốt` vào đây> |
| L322 | `skills/tdq-spec/references/spec-template.md:70` | Phán quyết chỉ nhận: DÙNG / KHÔNG (+ 1 trong 4 lý do đóng) / NỀN (skill khung đang chạy). |
| L323 | `skills/tdq-spec/references/spec-template.md:75` | \| Đã xét <N> skill khác \| user/plugin/built-in \| KHÔNG \| khác lĩnh vực \| |
| L324 | `skills/tdq-spec/references/spec-template.md:78` | Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config. |
| L325 | `skills/tdq-spec/references/spec-template.md:79` | Dòng này bắt buộc **chỉ khi việc này có runtime** — tức plan sẽ có ít nhất một task tạo |
| L326 | `skills/tdq-spec/references/spec-template.md:89` | Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ những dòng việc này |
| L327 | `skills/tdq-spec/references/spec-template.md:93` | Không chạm dòng nào → ghi `Ràng buộc kiến trúc phải giữ: không chạm dòng nào — <lý do |
| L328 | `skills/tdq-spec/references/spec-template.md:136` | Điều kiện PASS ở §6 đo được bằng lệnh, không phải cảm tính. |
| L329 | `skills/tdq-spec/references/spec-template.md:142` | \| Câu hỏi \| Trả lời phải nằm ở \| |

**Tổng: 329 điểm neo** trên 41 file skill.
