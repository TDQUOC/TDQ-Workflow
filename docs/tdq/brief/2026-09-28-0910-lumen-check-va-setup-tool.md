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

**Cách tôi đọc yêu cầu này — sáu việc**

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
4. **Có ép reindex ở mỗi lần kết turn hay không** — đo xong thì rào cản không còn là thời gian
   (2,6 s cho một file sửa, 0,2 s khi không có gì đổi), mà là turn sửa nhiều file: ~0,21 s/chunk.
   Cần chốt: cắm thẳng, hay chỉ cắm khi số chunk thay đổi dưới một ngưỡng.
5. **Đổi tên rồi có giữ tên cũ làm bí danh không** — người đang cài bản cũ gõ `tdq-lsp-setup` sẽ
   không thấy gì. Giữ một dòng trỏ sang tên mới, hay đổi dứt điểm và ghi vào CHANGELOG là breaking.
6. **`setup` ghi instruction user-level bằng cách nào** — `~/.claude/CLAUDE.md` là file toàn cục của
   user, có thể đã có nội dung riêng. Ba lối: chèn một khối có dấu mốc (`<!-- TDQ:TOOLS -->`) để lần
   sau ghi lại đúng khối đó; ghi ra file riêng rồi nhắc user tự `@import`; hay chỉ in ra để user dán.

## Hỏi đáp

*(điền ở phase analyze)*
