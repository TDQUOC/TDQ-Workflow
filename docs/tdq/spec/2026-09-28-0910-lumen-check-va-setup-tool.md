# SPEC — Bộ tìm kiếm 4 tầng: kiểm bằng hiệu ứng, reindex mỗi turn, và skill `tdq-setup`

Ngày: 2026-09-28 · Bản: 1.0 · Brief: ../brief/2026-09-28-0910-lumen-check-va-setup-tool.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- **Mục tiêu:** biến bộ tìm kiếm 4 tầng từ "có cài" thành "chứng minh được là đang trả lời đúng":
  thang bậc phải đo hiệu ứng thật của lumen chứ không đo daemon, index phải được dựng lại ở mỗi
  lần kết turn, và một skill duy nhất `tdq-setup` phải tự cài + tự kiểm + tự smoke test + ghi lại
  món nào thiếu. Đo được bằng: 8 bậc ĐẠT trên 3 hệ, và một lệnh setup chạy xong in ra bảng kết quả
  từng tầng kèm file nợ nếu có món không tự xử được.
- **Trong phạm vi:**
  - Bậc 5 sửa thứ tự phép dò (socket trước `which`), thêm phép đo vòng đi-về lumen và phép đo độ
    mới nội dung index.
  - Thêm một bậc mới cho graphify — công cụ thứ tư hiện không có bậc nào.
  - `tdq_finish` thêm bước reindex lumen ở mỗi turn; gỡ hẳn cờ `--skip-graphify`.
  - Đổi tên skill `tdq-lsp-setup` thành `tdq-setup`, kèm mọi chỗ cứng trỏ tới tên cũ.
  - `tdq-setup` cài thẳng phụ thuộc còn thiếu trong danh sách đã khai, kiểm manifest, chạy smoke
    test từng tầng, kiểm cấu hình đúng, và ghi món không tự xử được vào một file nợ.
  - Tổ chức lại luật tìm kiếm thành 4 tầng, kèm bảng phụ thuộc runtime và số đo ghi rõ tên repo.
  - Ghim bản ngắn của luật 4 tầng vào instruction user-level bằng khối có dấu mốc.
  - Dựng lại đồ thị graphify cho khớp nhánh hiện tại.
- **NGOÀI phạm vi:**
  - Chốt `docs/kien-truc.md` (đang NHÁP từ 2026-08-15) — đổi trạng thái hồ sơ kiến trúc là request
    riêng, có cổng duyệt riêng.
  - Sửa §9 của `docs/claude-md-mau.md` đang trỏ tới skill `mem0-memory` không tồn tại: chỉ **ghi
    nợ**, không sửa trong request này.
  - Truy tiếp ca N5 còn treo của request 0.52.0.
  - Cài lumen hay ollama lên máy Linux/macOS của user: hai máy đó chỉ dùng để ĐO, ràng buộc đứng
    là không làm rối môi trường của chúng.
  - Đổi model embedding — đã chốt `qwen3-embedding:0.6b` trong phiên này.
  - Vá hook plugin trên máy khác máy dev; `setup` chạy trên máy nào thì vá máy đó.
  - Sửa 70 file `docs/tdq/` lịch sử có nhắc tên skill cũ: chúng là biên bản của quá khứ.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | 4 câu ngoài repo đã trả lời xong ở phase analyze; phần còn lại là đo trên máy |
| Interview | BỎ | 6 câu quyết định đã chốt; không câu nào còn đổi được đầu ra |
| Vòng hỏi phạm vi | BỎ | user đã kể phạm vi thành 8 việc rời qua 5 lượt, kèm tên file |
| spec | CÓ | 8 việc, chạm 2 file ngoài repo, 1 breaking change — phải có văn bản để duyệt |
| plan | CÓ | đổi tên skill là 7 chỗ cứng phải làm đúng thứ tự |
| implement | CÓ | — |
| Chia cho sub-agent | BỎ | các việc dính nhau qua cùng vài file; chia ra là tự tạo xung đột |
| qc | CÓ, mức `full` | có breaking change và có sửa file ngoài repo |
| QC độc lập (agent) | BỎ | mức `full` không gọi; muốn có thì phải nâng `muc_qc` lên `ultra` |
| Đo lại trên Linux + macOS thật | CÓ | lỗi PATH của bậc 5 chỉ hiện trên macOS |
| report | CÓ | — |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Bậc 5 dò ollama không phụ thuộc PATH | `scripts/tdq_lsp.py` | trên máy có daemon sống nhưng `shutil.which("ollama")` trả None, bậc 5 vẫn kết luận ĐẠT |
| 2 | Bậc 5 đo vòng đi-về lumen bằng một truy vấn thật | `scripts/tdq_lsp.py` | lumen không trả được kết quả nào thì bậc 5 KHÔNG còn ĐẠT, dù ollama đang chạy |
| 3 | Bậc 5 đo độ mới NỘI DUNG index | `scripts/tdq_lsp.py` | sửa một file rồi hỏi ngay: bậc 5 phát hiện index thiếu nội dung mới, không tin cờ tự báo của công cụ |
| 4 | Bậc 8 cho graphify | `scripts/tdq_lsp.py` | thiếu binary hoặc đồ thị cũ hơn commit mới nhất thì bậc 8 báo, kèm lệnh xử lý |
| 5 | Bước reindex ở kết turn | `scripts/tdq_finish.py` | mỗi lần kết turn in một dòng `reindex` với trạng thái `ok` hoặc `skip` kèm lý do |
| 6 | Cờ `--skip-graphify` bị gỡ | `scripts/tdq_finish.py` | gọi kèm cờ đó thì lệnh báo lỗi tham số và chỉ sang cách làm mới |
| 7 | Skill đổi tên `tdq-setup` | `skills/tdq-setup/` | thư mục cũ không còn tồn tại; `name:` trong frontmatter khớp tên thư mục |
| 8 | Lệnh setup cài + kiểm + smoke test + kiểm cấu hình | `scripts/tdq_setup.py` | chạy một lệnh, in bảng 4 tầng với kết quả smoke test từng tầng |
| 9 | File nợ phụ thuộc | `docs/tdq/no-phu-thuoc.md` | món không tự cài được sinh đúng một dòng, có ngày và tên máy |
| 10 | Luật tìm kiếm 4 tầng, số đo ghi kèm tên repo | `skills/tdq-setup/references/uu-tien-tim-kiem.md` | có bảng phụ thuộc runtime, có graphify là một tầng, mỗi số đo có tên repo bên cạnh |
| 11 | Bản ghim user-level trong khối dấu mốc | `docs/claude-md-mau.md` | khối dấu mốc tồn tại; ghi lần hai không nhân bản khối |
| 12 | Đồ thị graphify dựng lại | `graphify-out/graph.json` | không node nào trỏ vào đường dẫn đã bị xoá khỏi repo |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| M1 thang bậc | `scripts/tdq_lsp.py` + unit test của module này | không | 1, 2, 3, 4 |
| M2 kết turn | `scripts/tdq_finish.py` + unit test của module này, `graphify-out/graph.json` | M1 — dùng lại phép dò của bậc 5 | 5, 6, 12 |
| M3 lệnh setup | `scripts/tdq_setup.py`, `skills/tdq-setup/SKILL.md`, `skills/tdq-setup/references/lumen.md`, `docs/tdq/no-phu-thuoc.md` + unit test của module này | M1 | 7, 8, 9 |
| M4 luật 4 tầng | `skills/tdq-setup/references/uu-tien-tim-kiem.md`, `docs/claude-md-mau.md`, `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/analyze-full.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-plan/SKILL.md`, `skills/tdq-build/SKILL.md` + phép kiểm bản mẫu instruction và unit test của module này | không | 10, 11 |
| M5 dọn tên cũ | `scripts/doc_lint.py`, `scripts/build_portable.py`, phép kiểm chống lệch của skill, `README.md`, `CHANGELOG.md` | M3 — tên mới phải tồn tại trước | 7 |

Không hai module nào khai chung một đường dẫn: M3 giữ `SKILL.md` và `references/lumen.md`, M4 giữ
`references/uu-tien-tim-kiem.md` — khác file, cùng thư mục.

## 3. Cách tiếp cận & lý do

- **Chọn:** kiểm bằng **hiệu ứng** ở mọi tầng, và **reindex bằng CLI** ở bước kết turn.
- **Vì:**
  - Thang bậc hiện tại chỉ kiểm "có tồn tại". Đo được: hôm nay ollama chạy suốt, MCP `lumen` chết
    cả phiên (`CONNECTION_CLOSED`), bậc 5 vẫn báo ĐẠT. Cùng lỗ hổng mà phép kiểm hiệu ứng ở intake
    bước 1b đã vá cho LSP từ 2026-09-03.
  - Reindex phải đi bằng CLI, không qua MCP: mã nguồn plugin 0.0.42 (`cmd/stdio.go:127`) khai
    `defaultFreshnessTTL = 30 * time.Second` — trong cửa sổ đó Merkle không được đi lại, nên nội
    dung mới vắng mặt mà công cụ vẫn báo fresh. CLI làm phép đi Merkle thật: đo được 2,6 s cho một
    file sửa, 0,2 s khi không có gì đổi, so với 16,5 s của graphify dựng lại toàn đồ thị.
  - Auto-reindex của lumen là **lazy, ăn theo lời gọi** `semantic_search`: MCP chết cả phiên thì cả
    tuần không ai dựng lại — đúng cái đã xảy ra, index 21/09 thiếu nội dung 27/09.
  - Sửa file plugin là đường DUY NHẤT để chặn hook đè thứ tự tìm kiếm: tài liệu Claude Code nói
    thẳng *"There is no way to disable an individual hook while keeping it in the configuration"*,
    chỉ có công tắc tổng `disableAllHooks`. Nên `setup` phải tự dò và tự vá lại sau mỗi lần plugin
    lên bản mới, vì phiên bản nằm trong đường dẫn thư mục cache.
  - Trần byte của bản mẫu được NÂNG, không nén luật: tiền lệ đã chốt trong
    phép kiểm bản mẫu instruction — *"a size cap is a tier-3 constraint, so hitting it means
    RAISING THE CAP, never compressing a law to fit"*.
- **Đã loại:**
  - Chỉ sửa câu §3 của luật cho nhẹ đi — vì câu đó khẳng định sai chiều ("không cần bước reindex
    nào"), giữ lại dạng nhẹ là giữ lại lý do để tiếp tục không reindex.
  - Ngưỡng số chunk để quyết định có reindex hay không — 0,2 s khi không có gì đổi, nên ngưỡng là
    phức tạp không mua được gì.
  - Nhúng một file riêng vào `~/.claude/CLAUDE.md` bằng cú pháp import — hoạt động thật (4 hop,
    user-scope không cần duyệt) nhưng file được nhúng vẫn nạp lúc launch, nên không tiết kiệm
    context; khối dấu mốc ít phần động hơn.
  - Giữ bí danh cho tên skill cũ — repo là một nguồn, không ai import tên skill từ ngoài.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `lumen:doctor` | plugin:lumen | DÙNG | đọc trước khi viết phép đo vòng đi-về của bậc 5 (đầu ra 2) |
| `lumen:reindex` | plugin:lumen | DÙNG | đối chiếu cách refresh trước khi cắm bước reindex (đầu ra 5) |
| `update-config` | built-in | DÙNG | khi `setup` phải ghi `settings.json` (đầu ra 8) |
| `code-review` | built-in | DÙNG | phase qc, phần clean code của mức `full` |
| `simplify` | built-in | DÙNG | phase qc, sau khi 5 module xong |
| Đã xét 21 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config — request này
  có runtime (`scripts/tdq_setup.py` là file mã nguồn chạy được), nên dòng này áp dụng.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`, và
  bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`, chỉ những dòng việc này chạm tới):

- *"`skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill"* —
  việc này chạm ở `skills/tdq-setup/SKILL.md`, nên mọi logic cài và kiểm nằm ở
  `scripts/tdq_setup.py`.
- *"File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`"* — chạm ở file mới
  `scripts/tdq_setup.py`.
- *"`scripts/` **không** được import `hooks/`"* — chạm ở `scripts/tdq_setup.py` khi nó dò hook của
  plugin ngoài: nó ĐỌC file JSON của plugin, không import module hook nào.
- *"Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`"* — chạm ở chỗ `tdq_setup.py` ghi
  `docs/tdq/no-phu-thuoc.md`: file nợ là file riêng, không phải state.
- Hồ sơ kiến trúc vẫn mang trạng thái **NHÁP — chờ user chốt**, nên bốn dòng trên được dùng như
  ràng buộc mạnh, không như luật đã đóng.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| `setup` tự cài mà cài sai thứ | làm bẩn máy user | chỉ cài đúng danh sách khai trong skill; món ngoài danh sách chỉ được GHI NỢ; tuyệt đối không chạm python hệ thống của Apple |
| Sửa file ngoài repo | CI không kiểm được, và ghi sai là mất nội dung của user | mọi hàm nhận đường dẫn qua tham số, test chạy trên thư mục tạm; ghi vào bản instruction chỉ trong khối dấu mốc; sao lưu file plugin trước khi vá |
| Reindex ở turn sửa nhiều file kéo dài | kết turn chậm | suất đo được 0,21 s/chunk; đặt trần thời gian cho bước reindex, hết trần thì bước đó `fail` và ghi nợ, không bao giờ treo turn |
| Đổi tên skill là breaking change | ai đang gọi tên cũ sẽ không thấy gì | khai breaking ở dòng đầu mục CHANGELOG; test khoá tên mới; 7 chỗ cứng liệt kê trong plan |
| Bậc mới làm thang bậc chậm hơn | intake bước 1b chạy mỗi request | mỗi phép đo mới có trần thời gian riêng; bậc graphify chỉ so mốc thời gian, không dựng lại đồ thị |
| Model `qwen3-embedding:0.6b` được lumen xếp "Untested" | chất lượng tìm có thể lệch về sau | bậc 5 in tên model đang dùng vào kết quả, để một lần hồi quy còn truy được nguyên nhân |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Bậc 5 không phụ thuộc PATH | giả lập `which` trả None mà daemon vẫn sống thì bậc 5 ĐẠT, và không in lệnh cài nào |
| Q2 | Bậc 5 bắt được lumen không trả lời | giả lập lumen trả rỗng hoặc lỗi thì bậc 5 không ĐẠT, chi tiết nói rõ là vòng đi-về thất bại |
| Q3 | Bậc 5 bắt được index thiếu nội dung mới | dựng ca một file mới chưa có trong index thì bậc 5 không ĐẠT, và không tin cờ tự báo của công cụ |
| Q4 | Bậc graphify | thiếu binary thì cảnh báo kèm lệnh cài; đồ thị cũ hơn commit mới nhất thì cảnh báo kèm lệnh dựng lại |
| Q5 | Reindex vào kết turn | chạy kết turn hai lần liền: lần có file sửa báo `ok`, lần không đổi gì vẫn báo `ok` và không quá trần thời gian |
| Q6 | Reindex không treo turn | ép quá trần thời gian thì bước đó `fail`, lệnh kết turn vẫn thoát, và một dòng nợ được ghi |
| Q7 | Cờ bỏ graphify đã biến mất | gọi kèm cờ đó thì thoát khác 0 và thông báo chỉ sang cách làm mới |
| Q8 | Đổi tên trọn vẹn | không còn chuỗi tên cũ trong mã, trong skill, trong phép kiểm và trong `README.md`; bảng trần dòng và danh sách thứ tự nạp đều mang tên mới |
| Q9 | `setup` cài, kiểm và smoke test | một lệnh, in bảng 4 tầng; mỗi tầng có kết quả smoke test riêng; tầng nào thiếu thì có lệnh cài đã chạy hoặc một dòng nợ |
| Q10 | File nợ | món không tự xử được sinh đúng một dòng có ngày và tên máy; chạy lại không nhân bản dòng cũ |
| Q11 | `setup` vá được hook plugin đè thứ tự tìm kiếm | dựng fixture plugin có khối chặn trên `Grep` thì sau khi chạy, khối đó biến mất, khối `SessionStart` còn nguyên, bản sao lưu tồn tại |
| Q12 | Luật 4 tầng | luật có graphify là một tầng, có bảng phụ thuộc runtime, và mọi số đo có tên repo bên cạnh |
| Q13 | Năm chỗ trích luật không lệch | phép kiểm chống lệch của repo vẫn xanh sau khi đổi tên và sửa luật |
| Q14 | Khối ghim user-level | ghi hai lần vào cùng một file chỉ còn một khối; nội dung ngoài khối không đổi một byte |
| Q15 | Trần byte bản mẫu | trần được NÂNG kèm chú giải lý do; không luật nào trong bản mẫu bị cắt để vừa trần |
| Q16 | Đồ thị graphify | không node nào trỏ vào đường dẫn không còn trong repo |
| Q17 | Ba hệ | trọn bộ test xanh trên Windows, Linux thật và macOS thật; riêng ca PATH của Q1 phải chạy thật trên macOS |
| Q18 | Không làm rối môi trường hai máy đo | sau khi đo: không gói nào được cài, không cấu hình nào bị sửa, thư mục tạm đã xoá, python của Apple không bị gọi tới |
| Q19 | Ràng buộc kiến trúc | `scripts/` không import `hooks/`; skill mới không chép nội dung script; file code mới nằm trong `scripts/` |
| Q20 | Nợ đã khai | §9 của bản mẫu trỏ tới skill không tồn tại được ghi vào file nợ, không bị sửa lặng lẽ |

DoD: 12 đầu ra ở §2 có thật và đo được · 20 hạng mục Q1–Q20 PASS · trọn bộ test xanh trên 3 hệ ·
`doc_lint` và phép kiểm i18n xanh · `docs/tdq/no-phu-thuoc.md` tồn tại và có ít nhất dòng nợ của
§9 bản mẫu · CHANGELOG khai breaking change ở dòng đầu mục · working log của mọi turn đã ghi · hai
máy đo được trả về đúng trạng thái trước khi đo.

## 7. Câu hỏi còn mở

Không còn câu nào — 6 câu quyết định đã chốt ở cuối phase analyze, ghi trong brief mục `## Hỏi đáp`.
