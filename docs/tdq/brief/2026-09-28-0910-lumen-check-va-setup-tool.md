# BRIEF — Sửa cách kiểm lumen, ghim hướng dẫn dùng tool, và setup tự kiểm phụ thuộc

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-09-28 · Slug: 2026-09-28-0910-lumen-check-va-setup-tool

## Nguyên văn

> 1A và note vào trong workflow là sẽ ghim hướng dẫn sử dụng tool vào instruction user-level (theo
> một cách ngắn gọn nhất nhưng vẫn đủ cho AI hiểu cần dùng gì khi nào) đồng thời update lại phần
> setup cảu workflow sẽ install và check dependecy nếu thiếu thì take note lại để xử lí triệt để

Trong đó "1A" là phương án A của lượt trước: sửa cả ba thứ cho lumen (bậc 5 đo vòng đi-về + đo độ
mới của index, reindex cắm vào `tdq_finish`), dựng lại đồ thị graphify, và thêm bảng phụ thuộc
runtime vào luật tìm kiếm.

**Bổ sung cùng phiên (2026-09-28):**

> bổ sung vào luôn là sẽ re tổ chức bộ graphify lumen lsp grep trong instruction và ở bước setup
> cũng sẽ bổ sung vào instruction user-level cho case đảm bảo mọi thứ setup đầy đủ khi setup
> workflow

> tôi lại skill tdq-lsp-setup thành tdq-setup nó sẽ setup fully dependecy cho workflow luôn

> 1b 2b và sẽ đi theo rule sreach và chúng ta đã nói. và trong skill setup cũng sẽ làm điều tương
> tự, và bổ sung thêm là sau mỗi turn nhớ re index lại project nha

**Cách tôi đọc yêu cầu này — bảy việc**

1. **lumen**: bậc 5 phải đo hiệu ứng thật, không đo daemon; phải đo được index có nội dung MỚI hay
   không; reindex phải nằm trong bước kết turn cạnh graphify; phần setup phải ghi đủ cách cài.
2. **graphify**: dựng lại đồ thị cho khớp `main`, bỏ thói quen `--skip-graphify`.
3. **Ghim hướng dẫn dùng tool vào instruction user-level**: bản NGẮN NHẤT mà vẫn đủ để agent biết
   dùng gì khi nào. Cơ chế user-level sẵn có của repo là `docs/claude-md-mau.md` — bản mẫu để chép
   sang `~/.claude/CLAUDE.md`.
4. **Setup tự kiểm phụ thuộc**: `setup` phải kiểm và cài được phần thiếu; thiếu gì thì **ghi lại
   thành nợ** để xử lý triệt để chứ không im lặng bỏ qua.
5. **Tổ chức lại cả bộ 4 tầng trong instruction, và `setup` phải tự ghi vào instruction
   user-level**: không chỉ thêm một bảng, mà xếp lại chỗ đứng của grep / LSP / graphify / lumen
   trong luật; rồi bước setup phải tự bổ sung hướng dẫn đó vào instruction user-level, để "cài
   workflow" đồng nghĩa với "mọi thứ đã đủ".
6. **Đổi tên `tdq-lsp-setup` → `tdq-setup`, và nó nhận việc cài ĐỦ phụ thuộc cho workflow**: không
   còn là skill của riêng LSP mà là cửa cài đặt của cả workflow.
7. **`setup` phải dọn luôn hook của plugin khác đang đè thứ tự tìm kiếm**, đúng như việc vừa làm
   tay trong phiên này; và **reindex sau MỖI turn**, không ngưỡng.

## Hiểu & kiến thức

### Bằng chứng đo trong phiên (2026-09-28, lumen đã sống lại)

**Ba câu hỏi khái niệm, ba lần trượt** — với index vừa dựng lúc mở phiên (1177 file, 14882 chunk):

| Câu hỏi | Đáp án đúng | lumen trả về |
|---|---|---|
| "nơi đóng dấu thời gian khi user duyệt spec" | `tdq_state.py:1827` | 5/5 là tài liệu, 0 file code |
| "rút gọn đường dẫn project để header không vượt trần" (tiếng Việt) | `tdq_state.duong_hien_thi` | `setup_status_render.py::THIEU` |
| cùng câu trên, viết tiếng Anh | như trên | `tdq_vungfile._chuan`, `codex_edit_gate._chuan` |

Giả thuyết "tại tôi hỏi tiếng Việt mà model là model code" **bị loại**: tiếng Anh cũng trượt.

**Phép thử quyết định — nguyên nhân là index thiếu nội dung mới:**

| Ký hiệu | Vị trí hiện tại | Commit | lumen tìm được? |
|---|---|---|---|
| `normalize_muc_gat` | `tdq_state.py:165` | 0.48.0 | CÓ — đúng dòng 165-180 |
| `normalize_muc_qc` | `tdq_state.py:190` | 23/09 (0.51.0) | CÓ — đúng dòng 190-201 |
| `duong_hien_thi` | `tdq_state.py:1475` | **27/09** (0.52.0) | **KHÔNG** — tìm đúng tên cũng không ra |

Cùng một file: index có nội dung tới 23/09, thiếu phần sửa 27/09. Nên ba lần trượt trên không phải
lỗi model, không phải lỗi ngôn ngữ, mà là **index thiếu nội dung mới của một file đã từng index**.

**Và công cụ không tự biết:** `index_status` trước khi reindex báo `Last indexed: 2026-09-21` kèm
**`Stale: no`**, cộng `Files: 1153 | Indexed: 1177` — tức nó còn giữ 24 file đã bị xoá.

### Vì sao bậc 5 hiện tại không bắt được

Bậc 5 hỏi "ollama có chạy không". Hôm nay ollama chạy suốt, mà MCP `lumen` chết cả phiên
(`CONNECTION_CLOSED`) và bậc 5 vẫn báo ĐẠT. Cùng lỗ hổng mà phép kiểm hiệu ứng ở intake bước 1b đã
vá cho LSP: thang bậc chỉ kiểm **có tồn tại**, không kiểm **có trả lời đúng**.

### Đối chiếu: graphify cùng bệnh, khác mức

Đồ thị TDQ cũ 8 ngày, 34% node (845/2415) trỏ vào `antigravity_portable/` đã xoá. Nguyên nhân là
`tdq_finish --skip-graphify` được gọi hơn 10 lần trong một phiên. Hai công cụ index đều chết theo
cùng một kiểu: **không ai dựng lại, và không ai bị chặn vì không dựng lại**.

Số đo giá trị hai công cụ (chi tiết ở `docs/tdq/knowledge/2026-09-28-do-lai-bo-tim-kiem-4-tang.md`):
graphify `affected --depth 1` rẻ hơn `grep -rn` **3.4×** và 0 dương tính giả; lumen ở chế độ
`summary: true` chỉ ~1.2 KB một truy vấn — **rẻ nhất trong bộ 4 tầng**. Nên chi phí thật của cả hai
không phải token, mà là **hạ tầng và kỷ luật dựng lại**.

### Bảng phụ thuộc runtime (thứ luật hiện chưa có)

| Tầng | Phụ thuộc | Chết thì rơi xuống |
|---|---|---|
| grep | không gì | — (nó là sàn) |
| LSP | server + `pyrightconfig.json` | grep, mất kiểu và diagnostics |
| graphify | `graph.json` mới | LSP nhiều vòng, đắt hơn |
| lumen | ollama + model + index có nội dung mới | grep nhiều từ khoá, hoặc đọc `docs/` |

### Đo lại sau khi đổi model + dựng lại index (2026-09-28, cùng phiên)

User chốt `qwen3-embedding:0.6b` làm model chung. Windows trước đó chạy
`ordis/jina-embeddings-v2-base-code`; khai model mới ở `~/.config/lumen/config.yaml` rồi dựng lại:
**1178 file, 14891 chunk, 9m39s**.

| Câu hỏi | Đáp án đúng | Trước (jina + index cũ) | Sau (qwen3 + index mới) |
|---|---|---|---|
| "rút gọn đường dẫn project để header không vượt trần" (VI) | `tdq_state.duong_hien_thi` | `setup_status_render.THIEU` | **đúng, hạng 1** — `tdq_state.py:1475-1499` · 0.82 |
| cùng câu, viết tiếng Anh | như trên | `tdq_vungfile._chuan` | **đúng, hạng 1** · 0.75 |
| "nơi đóng dấu thời gian khi user duyệt spec" (VI) | `tdq_state.py:1827` | 5/5 là tài liệu | vẫn 4/4 tài liệu — **còn trượt** |
| cùng ý, viết tiếng Anh sát code ("record the approval timestamp into state") | như trên | chưa đo | **đúng, hạng 1** — `_cli_approve` · 0.83 |
| tra ĐÚNG TÊN ký hiệu `duong_hien_thi` | như trên | trượt | vẫn trượt — top là `tdq-workflow.js::moDauPhien` 0.75 |

**Không được đọc bảng này thành "qwen3 hơn jina".** Hai biến đổi cùng lúc (model + độ mới index),
mà phép thử ở mục trên đã chứng minh index cũ KHÔNG chứa `duong_hien_thi` — nên riêng độ mới đã đủ
giải thích ba lần trượt cũ. Điều bảng này chứng minh được, và là điều cần cho spec:

1. Với index MỚI, tra đúng tên ký hiệu vẫn trượt → đó là bản chất embedding, không phải lỗi setup.
   Luật "tên chính xác thì dùng grep" được số đo chống lưng, không còn là câu nói suông.
2. Câu hỏi khái niệm diễn đạt sát cách code đặt tên thì lumen trả lời đúng hạng 1; diễn đạt xa
   (câu VI thứ ba) thì trượt. Hướng dẫn tool ghim ở user-level nên nói đúng chỗ này.
3. **Reindex mặc định là TĂNG TRƯỞNG, không phải dựng lại.** 9m39s là lần lạnh — đổi model sinh DB
   mới nên phải embed cả 14891 chunk. Đo tiếp trên chính index đó:

   | Lần chạy | lumen báo | Thời gian |
   |---|---|---|
   | có 1 file vừa sửa | `1 modified (1178 total)` · 12 chunk | **2.6 s** |
   | không có gì thay đổi | `already fresh` · 0 chunk | **0.2 s** |

   Nó dò bằng hash gốc (`root hash changed`), và `--force` mới là cờ dựng lại toàn bộ. Nên câu
   "đắt hơn graphify 36 lần" chỉ đúng cho lần lạnh; ở bước kết turn thì reindex **rẻ hơn graphify**
   (graphify dựng lại toàn đồ thị 16.5 s mỗi lần). Suất đo được là ~0,21 s/chunk, nên một turn sửa
   10 file cỡ 150 chunk vào khoảng 30 s — đây là phần cần cân, không phải bản thân việc cắm vào.

### Hiện trạng ba máy (đo ngày 2026-09-28, chỉ đọc)

| Máy | ollama | model `qwen3-embedding:0.6b` | `~/.config/lumen/config.yaml` |
|---|---|---|---|
| Windows (máy dev) | chạy | có | có — vừa đổi sang qwen3 |
| Linux | chạy, 12 model | có | **trước đó KHÔNG có** — nay đã ghi, 1 server localhost |
| macOS | chạy (Ollama.app, không có CLI trong PATH) | có | **đã có từ trước, vốn đã là qwen3** |

Nên "đặt làm default mọi máy" thực ra chỉ là kéo Windows về đúng hàng: macOS đã dùng model này từ
trước. Cấu hình macOS còn khai 2 server failover với primary là một ollama máy thứ ba qua Tailscale
— máy đó **không với tới được** từ máy dev, nên không kiểm được nó có model này hay không; nếu
không có thì macOS tự rơi về server localhost.

Việc này cũng phơi ra thứ thuộc phạm vi request: mỗi máy phải sửa cấu hình bằng tay, không có lệnh
nào của repo làm. Đây đúng là phần `setup` phải nhận.

### Hiện trạng chỗ sẽ sửa (đo 2026-09-28) — cho việc 5

| Thứ | Hiện trạng | Vấn đề cho việc 5 |
|---|---|---|
| `skills/tdq-lsp-setup/` | tên là **lsp**-setup, nhưng thực chất là nơi cài cả bộ tìm kiếm: thang 7 bậc gồm binary, lsp MCP, language server, quyền tool, **lumen**, xung đột hook, import-root | Tên và nội dung đã lệch nhau; graphify **không có bậc nào** dù nó là một trong 4 tầng |
| `references/uu-tien-tim-kiem.md` | 151 dòng, luật thứ tự tìm kiếm, "binding on every phase" | Chưa có bảng phụ thuộc runtime, chưa có số đo theo loại repo, chưa nói tra đúng tên thì dùng grep |
| `docs/claude-md-mau.md` | **3533 / 3800 byte** — còn 267 byte | Nhồi bản hướng dẫn 4 tầng vào đây là chạm trần; phải cắt chỗ khác hoặc nâng trần |
| `scripts/setup_status.py` | có `thu_dependency()` và `thu_lumen()` | Đã biết KIỂM, nhưng không ai ghi instruction user-level và không ai ghi nợ |

**Một mâu thuẫn phải chốt trước khi viết spec.** `skills/tdq-lsp-setup/SKILL.md` đang khai luật cứng:
*"Never install anything, never edit another plugin's files, without the user saying yes first"* —
`tdq_lsp.py` chỉ CHẨN ĐOÁN rồi in ra lệnh, người mới chạy. Yêu cầu "setup sẽ install" đi ngược đúng
câu đó, và "setup tự ghi vào instruction user-level" là **ghi vào file ngoài repo** (`~/.claude/`).
Cả hai đều hợp lý khi chính user gõ lệnh setup, nhưng phải viết ranh giới ra thành luật mới, không
để hai câu luật đá nhau.

### Giá của việc đổi tên skill (đo 2026-09-28) — cho việc 6

`tdq-lsp-setup` xuất hiện **200 lần trong 90 file**, nhưng phần phải sửa thật thì nhỏ: 70 file là
`docs/tdq/` lịch sử (brief/spec/plan/report cũ — **không được sửa**, chúng là biên bản của quá khứ),
cộng `__pycache__` và `graphify-out/graph.json` là thứ sinh ra.

| Chỗ phải sửa | Vì sao nó là chỗ CỨNG |
|---|---|
| `skills/tdq-lsp-setup/` → `skills/tdq-setup/` | tên thư mục phải khớp `name:` trong frontmatter, nếu không host không nạp skill |
| `skills/tdq-lsp-setup/SKILL.md` frontmatter + thân | `description` là thứ host đọc để quyết định gọi skill |
| `scripts/doc_lint.py:61` | bảng trần dòng cho từng skill: `"tdq-lsp-setup": 120` — đổi tên mà quên là mất trần |
| `scripts/build_portable.py:189` | danh sách skill theo THỨ TỰ nạp, kèm chú giải "read before intake" |
| `skills/tdq-intake`, `tdq-spec`, `tdq-plan`, `tdq-build` | 5 chỗ trích luật tìm kiếm bằng đường dẫn tương đối |
| `tests/test_tdq_lsp_skill.py` | chính tên file mang tên cũ, và nó khoá đường dẫn `GOC` |
| `README.md`, `CHANGELOG.md` | mặt ngoài của repo |

Đổi tên cũng là cơ hội đúng lúc cho việc 5: thang bậc hiện có **7 bậc và không bậc nào là graphify**.
Nếu skill đã tên `tdq-setup` thì thiếu bậc graphify là lỗi rõ ràng, không còn bào chữa được bằng
"skill này chỉ lo LSP".

### Chỗ cần hỏi user trước khi viết spec

1. **`setup` được phép cài gì** — luật đứng của repo là "không bao giờ tự cài khi chưa hỏi". Lệnh
   `setup` do user gõ nên cài trong đó là hợp lệ, nhưng hỏi từng gói hay cài thẳng cả nhóm là ranh
   giới cần user chốt.
2. **Nợ thiếu phụ thuộc ghi vào đâu** — file riêng, hay `docs/tdq/audit/`, hay in ra rồi để user tự
   xử lý.
3. **Bản ngắn của hướng dẫn tool dài bao nhiêu** — `docs/claude-md-mau.md` đang có trần 3800 byte;
   thêm bảng 4 tầng vào đó là chạm trần.
4. **Đổi tên rồi có giữ tên cũ làm bí danh không** — người đang cài bản cũ gõ `tdq-lsp-setup` sẽ
   không thấy gì. Giữ một dòng trỏ sang tên mới, hay đổi dứt điểm và ghi vào CHANGELOG là breaking.
5. **`setup` ghi instruction user-level bằng cách nào** — `~/.claude/CLAUDE.md` là file toàn cục của
   user, có thể đã có nội dung riêng. Ba lối: chèn một khối có dấu mốc (`<!-- TDQ:TOOLS -->`) để lần
   sau ghi lại đúng khối đó; ghi ra file riêng rồi nhắc user tự `@import`; hay chỉ in ra để user dán.

### Năng lực dùng được (B0)

`skill_inventory.py` **không thấy skill của chính repo** (nguồn `project` / `plugin:tdq-workflow`)
vì plugin `tdq-workflow` chưa được cắm vào phiên này — đúng phát hiện của report 0.52.0. Nên bảng
dưới ghép từ hai nguồn: kiểm kê trên đĩa, cộng skill built-in thấy trong context.

| Năng lực | Nguồn | Phán quyết |
|---|---|---|
| `lumen:doctor` | `plugin:lumen` | **DÙNG** — đọc trước khi tự viết phép kiểm bậc 5; nó là bản tham chiếu "kiểm lumen bằng hiệu ứng thật" |
| `lumen:reindex` | `plugin:lumen` | **DÙNG** — mô tả của nó ("prefer MCP-driven refresh, CLI chỉ cho clean rebuild") định hình cách cắm reindex |
| `update-config` | built-in | **DÙNG** khi phải ghi `settings.json` (env `LUMEN_EMBED_MODEL`) |
| `code-review`, `simplify` | built-in | **DÙNG ở phase qc** nếu mức QC là `ultra` |
| `skill-creator` | user | BỎ — đổi tên skill ở đây là việc file + test của repo, không cần bộ sinh skill |
| `Explore`, `Plan` (agent) | built-in | BỎ — phạm vi đã đọc xong bằng LSP/grep trong phase này |
| `docx`, `pptx`, `xlsx`, `pdf`, `google-workspace`, `docs`, `morning`, `dataviz`, `bao-cao-tan-an-hoi`, `session-handoff`, `import-memory`, `init`, `run`, `claude-api`, `fewer-permission-prompts` | user / built-in | BỎ — không đầu ra nào của request thuộc các dạng này |

### Điều tra code — mười phát hiện

**Về bậc 5 (việc 1)**

1. **Bậc 5 có một false negative thật trên macOS.** `bac5_lumen()` hỏi `shutil.which("ollama")`
   TRƯỚC cả phép probe socket. Đo trên máy Mac của user: `/opt/homebrew/bin/ollama` tồn tại,
   login shell tìm ra, nhưng `python3 -c "shutil.which('ollama')"` trả **None** — PATH của tiến
   trình không-login không có `/opt/homebrew/bin`. Hệ quả kép: bậc 5 báo "thiếu ollama" và in
   `brew install ollama`, còn theo yêu cầu mới thì `setup` sẽ đi **cài lại thứ đã có sẵn**.
   Phép probe socket (`_ollama_dang_chay`) không phụ thuộc PATH, nên thứ tự hiện tại là ngược.
2. **Bậc 5 chưa hỏi lumen câu nào.** Nó kiểm 4 thứ tồn tại: binary ollama, manifest model trên
   đĩa, socket daemon, binary lumen. Không vòng đi-về MCP, không một phép đo nào về nội dung
   index. Đó đúng là lỗ hổng làm nó báo ĐẠT suốt phiên mà MCP `lumen` chết.

**Về reindex (việc 1 + 7)**

3. **Chính luật đang cấm việc user vừa yêu cầu.** §3 bước 3 của `uu-tien-tim-kiem.md` viết:
   *"lumen's `semantic_search` auto-reindexes the project incrementally … no separate reindex step
   or script is needed to keep data fresh."* Câu đó là lý do không ai cắm reindex vào kết turn, và
   nó trái bằng chứng hôm nay (index 21/09 thiếu nội dung 27/09 mà vẫn báo `Stale: no`). Nguyên nhân
   đã tìm ra ở mục research bên dưới, và là **hai** cái bẫy riêng biệt chứ không phải một: auto-
   reindex là lazy, ăn theo lời gọi `semantic_search` (MCP chết cả phiên thì cả tuần không ai dựng
   lại), cộng một cache TTL 30 giây che mắt phép đo staleness trong cửa sổ ngắn. Câu luật ở §3 phải
   bị xoá, không phải sửa nhẹ.
4. **`tdq_finish` có khuôn sẵn để cắm.** Mọi bước là một hàm `step_*` trả `Step(tên, trạng thái,
   chi tiết)` với 3 trạng thái `ok|skip|fail`. Một điểm khác phải để ý: `step_graphify` chỉ chạy
   khi có file **CODE** đổi (`--code-only`), còn lumen index cả `docs/` — nên điều kiện chạy của
   hai bước không được sao chép của nhau.

**Về tổ chức lại luật (việc 5)**

5. **graphify xuất hiện 0 lần trong luật tìm kiếm**, dù có trong 6 file skill khác như một bước
   sổ sách. Doctrine đang là luật **ba tầng** trong khi repo thực tế chạy **bốn công cụ**.
6. **Mọi số đo của §2 đều đo trên repo này** — đúng cái K2 của knowledge vừa phê. Phải bổ sung số
   claudecodeui, và ghi tên repo cạnh mỗi con số.
7. **Câu hỏi "trần 3800 byte" tự trả lời.** `tests/test_claude_md_core.py` đã chốt tiền lệ:
   *"a size cap is a tier-3 constraint, so hitting it means RAISING THE CAP, never compressing a
   law to fit"* — cùng phán quyết từng áp cho `chung.md` (150 → 240 dòng). Nên đây không còn là
   câu để hỏi user: **nâng trần**, không nén luật.
8. **Bản mẫu đang trỏ vào một skill không tồn tại.** §9 của `docs/claude-md-mau.md` bảo dùng skill
   `mem0-memory`; máy này không có nó (memory của phiên là file trong `~/.claude/projects/…`).
   Đúng loại "phụ thuộc thiếu thì ghi thành nợ" mà việc 4 phải xử lý.

**Về hook plugin (việc 7)**

9. **Luật đã có, chỉ thiếu người làm.** §4 của `uu-tien-tim-kiem.md` mô tả đúng từng bước tôi vừa
   làm tay (báo đường dẫn, xin phép, backup, chỉ gỡ `PreToolUse`, giữ `SessionStart`) và đã tiên
   đoán *"a plugin update reinstalls the hook under a new version directory"*. Nên việc 7 là **tự
   động hoá một luật đã tồn tại**, không phải viết luật mới.

**Về kiến trúc (việc 6)**

10. `docs/kien-truc.md` chốt: `skills/` là văn bản **không chạy được**, và **file code mới chỉ
    được nằm trong `scripts/` hoặc `hooks/`**. Nên mọi logic cài/kiểm phải ở `scripts/`, còn skill
    `tdq-setup` chỉ được **nhắc tên lệnh**. Một lưu ý: hồ sơ kiến trúc vẫn mang trạng thái
    **NHÁP — chờ user chốt** từ 15/08, nên tôi dùng nó như gợi ý mạnh, không như luật đã chốt.

### Research ngoài repo — bốn câu, và một nguyên nhân tìm ra

Sub-agent `general-purpose` chạy 4 truy vấn, tự ghi
`docs/tdq/research/2026-09-28-0910-lumen-check-va-setup-tool.md`, trả digest ≤1500 ký tự. Không có
`tavily-primary` trong phiên nên nó dùng `WebSearch`/`WebFetch` — ghi rõ trong file đó.

| # | Câu hỏi | Kết luận | Ảnh hưởng |
|---|---|---|---|
| 1 | `~/.claude/CLAUDE.md` có hỗ trợ `@path` import? | **CÓ** — relative và absolute, lồng tối đa 4 hop, user-scope không cần duyệt. Nhưng **không tiết kiệm context**: file import vẫn nạp lúc launch | câu hỏi 5 lối B là khả thi về kỹ thuật, nhưng không mua được token |
| 2 | Có cách tắt hook của MỘT plugin mà không sửa file của nó? | **KHÔNG CÓ.** Doc nói thẳng "There is no way to disable an individual hook while keeping it in the configuration"; chỉ có công tắc tổng `disableAllHooks` | **chốt việc 7**: sửa file plugin là đường duy nhất, nên `setup` buộc phải tự dò + tự vá lại |
| 3 | lumen tài liệu hoá staleness thế nào? | Merkle tree trên hash file; `semantic_search` tự refresh khi stale — **nhưng có cache TTL** | xem mục dưới |
| 4 | `qwen3-embedding:0.6b` | ctx 32K, dims tối đa 1024 (MRL 32–1024), MTEB-Code **75.41**; lumen tự xếp nó là **"Untested"** | mức "đủ tốt", và đúng là không có bảo đảm nào |

Về câu 4, digest trả về **KHÔNG KẾT LUẬN ĐƯỢC** cho ý "model yếu ở tra tên ký hiệu chính xác": Qwen
không công bố điều đó. Nên số đo hôm nay của chính repo này là bằng chứng duy nhất cho ý đó, và nó
chỉ nói về *model này trên repo này* — không được phát biểu rộng hơn (đúng luật K2).

**Nguyên nhân của cái bẫy, xác minh trên mã nguồn trong máy, không chỉ trên web.** Digest nói TTL
60 s; đọc chính bản đang cài (`cmd/stdio.go:127` của plugin 0.0.42) thì là **30 s**:

> `const defaultFreshnessTTL = 30 * time.Second` — *"how long a confirmed-fresh index is trusted
> before the merkle tree is re-walked … re-walking thousands of files on every call adds 1-3s"*

`module github.com/ory/lumen` trong `go.mod` xác nhận nguồn web đúng project. Vậy có **hai** cái bẫy
riêng biệt, và trước đó tôi gộp chúng làm một:

1. **TTL 30 giây** — sửa file rồi search ngay trong vòng 30 s của một lần "fresh" đã xác nhận thì
   Merkle không được đi lại, nên nội dung mới vắng mặt mà công cụ vẫn báo fresh. Bẫy thật, nhưng
   **hẹp**: nó không giải thích được một index cũ 7 ngày.
2. **Index cũ 7 ngày** — cái này do MCP `lumen` chết cả phiên: không lần `semantic_search` nào chạy
   thì `EnsureFresh` không bao giờ được gọi. Tức auto-reindex là **lazy và ăn theo lời gọi**; không
   ai search thì không ai dựng lại, và cả tuần trôi qua.

**Hệ quả thiết kế, có bằng chứng chống lưng:** bước reindex ở kết turn phải đi bằng **CLI**
(`lumen index <project>`), không đi qua đường MCP — CLI làm phép đi Merkle thật, đúng như đo được
sáng nay ("root hash changed", 1 file sửa, 2,6 s), nên nó không bị TTL 30 s che mắt và không phụ
thuộc MCP còn sống hay không. Điều này **lệch với mô tả của skill `lumen:reindex`** ("prefer
MCP-driven refresh") — lệch có lý do, và lý do ghi ở đây.

### Vì sao bỏ vòng hỏi phạm vi

Vòng hỏi phạm vi (`scope-round.md`) bị bỏ có lý do: phạm vi đã được user kể ra thành **bảy việc
rời** qua bốn lượt liên tiếp, kèm chỉ định cụ thể tới từng file và từng hành vi. Hỏi lại "request
này trải những vùng nào" là hỏi lại thứ user vừa nói.

## Hỏi đáp

**Lane + loại request.** Lane `full` (có spec + plan), loại `feature`. Nhánh
`feature/tdq-setup-bo-4-tang`, gốc `main`, sẽ hợp lại `main` ở bước 11 của report.

**Q4 — reindex mỗi turn hay theo ngưỡng?** → **cắm thẳng mỗi turn, không ngưỡng.** Số đo chống
lưng: 0,2 s khi không có gì đổi, 2,6 s cho một file sửa. Ngưỡng là phức tạp không mua được gì.

**Xung đột hook plugin lumen (bậc 6) → đã xử trong phiên này, user cho phép.** Plugin
`lumen@claude-plugins-official` 0.0.42 cắm `PreToolUse` matcher `Grep|Bash`, chèn câu "dùng
`semantic_search` thay cho Grep/Bash" vào **mọi** lần gọi — đá thẳng vào luật của repo, nơi grep là
sàn cho truy vấn tên chính xác (và chính số đo hôm nay cho thấy lumen tra đúng tên ký hiệu thì
trượt). Đã gỡ khối `PreToolUse`, giữ `SessionStart` (dòng "Lumen index ready" vẫn có ích), lưu bản
cũ ở `hooks.json.truoc-tdq.bak`. Bậc 6 từ CẢNH BÁO → **ĐẠT, 7/7**.

Hai điều việc 7 phải rút ra từ đây, không được để lặp lại:

1. **Sửa tay là không bền.** File nằm trong `.../cache/claude-plugins-official/lumen/0.0.42/` —
   phiên bản nằm trong đường dẫn, nên plugin lên 0.0.43 là hook cũ sống lại trong thư mục mới.
   `setup` phải tự dò và tự dọn lại, chứ không chờ ai nhớ.
2. **Chỉ dọn cái đè LÊN thứ tự tìm kiếm**, không dọn bừa hook của plugin khác. Đã kiểm: trong toàn
   bộ cache plugin chỉ có đúng khối này; `hooks-cursor.json` chỉ có `sessionStart`.

**Sáu câu chốt ở cuối phase analyze.**

| # | Câu hỏi | Chốt | Ghi chú |
|---|---|---|---|
| 1 | `setup` được phép cài gì | **Cài thẳng, không hỏi lại** — cộng kiểm manifest, smoke test và kiểm config đúng | user chọn nhãn "B" nhưng mô tả là lối C; ghi theo MÔ TẢ, xem mục dưới |
| 2 | Nợ thiếu phụ thuộc ghi vào đâu | **`docs/tdq/no-phu-thuoc.md`** — một file cố định, mỗi dòng một món kèm ngày + máy | dễ soi, dễ đóng |
| 3 | Cờ `--skip-graphify` | **Gỡ hẳn** | chính nó làm đồ thị cũ 8 ngày; gỡ cờ là gỡ luôn khả năng tái phạm |
| 4 | Tên cũ `tdq-lsp-setup` | **Đổi dứt điểm**, khai breaking trong CHANGELOG | không giữ bí danh |
| 5 | Cách ghi instruction user-level | **Khối có dấu mốc** `<!-- TDQ:TOOLS -->` … `<!-- /TDQ:TOOLS -->` trong `~/.claude/CLAUDE.md` | `@import` khả thi nhưng không mua được token nào |
| 6 | Mức QC | **`full`** — DoD + trọn unit test + hồi quy vùng chạm + ràng buộc kiến trúc + clean code, không runtime test | đã ghi `muc_qc=full` vào state |

**Câu 1 — nhãn lệch mô tả, và tôi ghi theo mô tả.** Nguyên văn: *"1B nghĩa là tôi gọi skill setup AI
sẽ tụ động cài và check mainifest và smoke test đảm bảo haojt đọng ổn và config đúng"*. Nhãn B trong
danh sách là "hỏi từng gói một", còn mô tả đó là lối C. Chốt theo mô tả: `setup` **tự cài, không hỏi
lại**, vì chính việc user gõ `setup` là sự cho phép. Hai hàng rào giữ nguyên, không thương lượng:

- Chỉ cài đúng **danh sách phụ thuộc đã khai** trong skill; thấy thiếu thứ ngoài danh sách thì ghi
  nợ, không tự ý cài thêm.
- **Không bao giờ đụng python hệ thống của Apple** (ràng buộc đứng của user, từ request trước).

Và câu 1 thêm một yêu cầu MỚI mà năm việc trước chưa có: `setup` không chỉ cài, mà phải **kiểm
manifest + smoke test từng tầng + kiểm config đúng**. Đây là việc 8.

**Một chỗ dễ lẫn giữa câu 1 và câu 6.** "Smoke test" ở câu 1 là **tính năng của sản phẩm** (setup tự
chứng minh từng tầng trả lời được), khác "smoke test" trong bảng mức QC — thứ mà mức `full` KHÔNG
chạy ở phase `qc`. Nên: phase `qc` kiểm tính năng đó bằng unit test theo đúng mức `full`, còn bản
thân đường smoke test sẽ được chạy **một lần trong phase implement** để chứng minh nó hoạt động.
Không có mâu thuẫn, nhưng phải viết ra để QC không hiểu sai mức.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| analyze | **CÓ** (đang chạy) | 10 phát hiện code + 4 câu research, không việc nào đoán |
| research thêm | **BỎ** | 4 câu ngoài repo đã trả lời xong; phần còn lại là đo trên máy, không phải tra web |
| spec | **CÓ** | 8 việc, chạm 2 file ngoài repo và 1 breaking change — phải có văn bản để duyệt |
| plan | **CÓ** | đổi tên skill là 7 chỗ cứng phải làm theo thứ tự, không được nhớ nhầm |
| implement | **CÓ** | — |
| chia cho sub-agent | **BỎ** | các việc dính nhau qua cùng vài file (`tdq_lsp.py`, luật tìm kiếm); chia ra là tự tạo xung đột |
| qc | **CÓ**, mức `full` | có breaking change + sửa file ngoài repo |
| agent QC độc lập | **BỎ** | mức `full` không gọi; muốn thì phải nâng lên `ultra` |
| đo lại trên Linux + macOS thật | **CÓ** | bậc 5 có lỗi PATH chỉ hiện trên macOS — không đo trên Mac thật thì không biết đã sửa đúng |
| report | **CÓ** | — |

Các luồng tính năng request này dựng từ đó: (1) thang bậc đo hiệu ứng thật của lumen; (2) bước
reindex ở kết turn; (3) skill `tdq-setup` cài + kiểm + smoke test + ghi nợ; (4) luật tìm kiếm 4 tầng
và bản ghim user-level.
