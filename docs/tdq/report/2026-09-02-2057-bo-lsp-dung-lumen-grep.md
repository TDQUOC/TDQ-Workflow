# Báo cáo — Bỏ LSP chỉ dùng lumen + grep: nên không, mất bao nhiêu

**Ngày:** 2026-09-02 · Lane: quick · Plan: ../plan/2026-09-02-2057-bo-lsp-dung-lumen-grep.md
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## 0. Cách đo — và giới hạn của phép đo

Đo trên chính repo TDQWorkflow, ngày 2026-09-02, 3 loại truy vấn × 3 lớp. Mỗi lớp chỉ được
dùng **một lệnh gọi duy nhất**, đúng như khi agent thật đi tìm.

Thời gian: kẹp mỗi lệnh gọi giữa hai lần đọc đồng hồ (`time.time()`) ở hai lượt bash liền kề.
Con số thu được là **thời gian tường (wall-clock) như agent thật cảm nhận**, tức đã bao gồm
round-trip của harness, không phải thời gian ròng của công cụ. Vì cả 3 lớp đều đo bằng đúng
một cách nên so sánh giữa chúng là công bằng; nhưng đừng đọc nó như benchmark của công cụ.
Để đối chiếu: cùng lệnh grep chạy trong tiến trình Python mất **0,101 s**, còn khi kẹp qua
harness là 4,77 s — tức ~4,7 s là phí cố định của việc gọi công cụ, lớp nào cũng chịu.

## 1. Truy vấn A — tên symbol chính xác

Câu hỏi: `bac6_hook_xung_dot` ở đâu, và được dùng ở những đâu.
Ground truth (xác lập bằng `grep -rn` trên `scripts/ hooks/ tests/`): **6 vị trí** —
định nghĩa `scripts/tdq_lsp.py:284`, gọi `scripts/tdq_lsp.py:314`, dùng trong
`tests/test_tdq_lsp.py:181,189,196,204`.

| Lớp | Lệnh | Tìm đúng | Nhiễu | Thời gian |
|---|---|---|---|---|
| LSP | `find_symbol` | **1/6** — chỉ định nghĩa | 2/3 kết quả là bản sao trong bundle portable | 5,78 s |
| lumen | `semantic_search` | **1/6** — chỉ định nghĩa | 4/8 kết quả là file docs không liên quan | 9,34 s |
| grep | `grep -rn` | **6/6** | 0 (sau khi thêm `--binary-files=without-match`; không thêm thì lẫn 2 dòng `.pyc`) | 4,77 s |

Đọc bảng:
- Với **tên đã biết chính xác**, grep thắng tuyệt đối: đủ 6/6, nhanh nhất, không nhiễu.
  Đây là lớp đúng cho loại câu hỏi này, không phải LSP.
- LSP xếp bản sao trong `antigravity_portable/` và `portable_codex/` **trên** bản gốc
  `scripts/tdq_lsp.py` (0,96 — hạng ba). Repo này có 3 bundle portable nhân bản mã nguồn,
  nên xếp hạng của LSP bị loãng. Đây là đặc thù của repo này, đáng ghi nhận.
- lumen xếp đúng bản gốc lên đầu (0,79) — nhỉnh hơn LSP ở khoản xếp hạng, nhưng một nửa
  kết quả là rác và nó **không** trả về các vị trí sử dụng.
- Cần nói rõ cho công bằng: `find_symbol` vốn không phải công cụ trả lời "dùng ở đâu" —
  việc đó là `find_references`/`find_callers`, đo ở mục 3.

## 2. Truy vấn B — khái niệm mơ hồ, không có tên symbol để bám

Câu hỏi nguyên văn: *"nơi ghi trạng thái duyệt của user vào file state.json"*.
Ground truth: `scripts/tdq_state.py:1527` hàm `_cli_approve`, dòng ghi thật là **1572**
(`state[f"{target}_approved_at"] = now_iso()`).

| Lớp | Lệnh | Kết quả | Thời gian |
|---|---|---|---|
| lumen | `semantic_search` với đúng câu hỏi tiếng Việt | **trượt đích** — trả `save` (dòng 424), là hàm ghi file chung, không phải chỗ ghi cờ duyệt. 4/8 kết quả là bản sao portable | 7,10 s |
| LSP | `find_symbol "approve"` | có đích, nhưng xếp **hạng 28 / 78 kết quả** | 4,56 s |
| grep | `grep -rn "approved_at"` | **trúng dòng 1572** ngay trong 7 dòng đầu | 4,94 s |

Đây là mục cho thấy rõ nhất giới hạn của từng lớp, và cả ba đều lộ nhược điểm:

- **lumen là lớp duy nhất nhận thẳng câu hỏi mơ hồ tiếng Việt** — không cần đoán từ khoá.
  Nhưng nó trả về thứ *nghe giống* (ghi state) chứ không phải thứ *đúng* (ghi cờ duyệt).
- **LSP không nhận được câu hỏi này.** Nó chỉ tra theo tên, nên tôi đã phải tự dịch khái niệm
  thành từ khoá `approve` trước — tức phần khó nhất của câu hỏi do người làm, không phải công
  cụ. Trả 78 kết quả cho một câu hỏi có một đáp án là chi phí context rất lớn.
- **grep trúng đích nhanh nhất, nhưng chỉ vì tôi đã biết sẵn token `approved_at`.** Với repo
  lạ, bước biết-token đó chính là bước không có. Không được ghi công cho grep phần việc mà
  người dùng đã làm hộ nó.

## 3. Truy vấn C — quan hệ: "ai gọi hàm này"

Câu hỏi: những đâu gọi `load()` của `scripts/tdq_state.py:303`.

Ground truth dựng bằng **phân tích AST** (đọc `import`, phân biệt `tdq_state.load` với mọi
`load` khác), không dùng lớp nào trong ba lớp đang đo, để phép đo không tự chấm điểm mình:
**27 lệnh gọi, nằm ở 12 file** — `tdq_state.py` (12), 5 file hook, `tdq_checkstatus.py`,
`tdq_team.py` (2), `tdq_timing.py`, `tests/helper.py`, `test_check_status.py`, `test_state.py` (4).

Đơn vị so sánh là **số file gọi tìm được / 12**, vì ba lớp đếm khác nhau (LSP đếm hàm gọi,
grep đếm dòng, lumen đếm chunk) nên chỉ mức file mới so được.

| Lớp | Lệnh | Recall | Nhiễu | Thời gian |
|---|---|---|---|---|
| LSP | `find_callers` incoming | **1/12 file (8%)** — 13 hàm gọi nhưng **toàn bộ nằm trong chính `tdq_state.py`**; không thấy một caller khác file nào | 0 | 5,93 s |
| lumen | `semantic_search` | **3/12 file (25%)** — `tdq_state.py`, `tdq_checkstatus.py`, `tests/helper.py` | 7/15 kết quả là bản sao portable | 6,33 s |
| grep | `grep -rn '\bload('` lọc `json.load` | **12/12 file (100%)** | 6 file dương tính giả (precision 67%); 46 dòng thô cho 27 lệnh gọi thật | ~5 s |

Đây là kết quả **ngược hẳn dự đoán của luật hiện hành**. `uu-tien-tim-kiem.md` mục 2 ghi
"ai gọi hàm này: LSP chính xác, lumen chịu" — nhưng đo thật thì LSP là lớp **tệ nhất** ở
đúng câu hỏi lẽ ra là sở trường của nó.

Cần nói thẳng nguyên nhân, vì nó đổi cách đọc kết luận: 8% này gần như chắc chắn **không
phải giới hạn của LSP nói chung mà là lỗi cấu hình của repo này** — `find_callers` chỉ nhìn
thấy trong phạm vi một file, tức workspace của language server chưa phủ `hooks/` và `tests/`,
hoặc server Python đang chạy không dựng chỉ mục liên file. Hệ quả nghiêm trọng hơn con số:
nếu cross-file index không có thì `rename_symbol` và `blast_radius` — hai thứ đáng giá nhất
của LSP — **cũng đang không đáng tin trên repo này**, dù thang `tdq_lsp.py kiem` vẫn báo 6/6.
Thang đó kiểm sự tồn tại của các bậc, không kiểm chất lượng chỉ mục.

## 4. Research ngoài (B2)

Digest từ sub-agent, mỗi ý có nguồn:

- Embedding search bản chất là truy hồi **top-k theo độ tương đồng**: trả về k đoạn giống
  nhất, **không có khái niệm "đã đủ mọi call site"** — Sourcegraph, *Semantic Code Search:
  What it is and how it works* (sourcegraph.com/blog/semantic-code-search-what-it-is-and-how-it-works).
- Chỉ mục vector bị cũ sau refactor lớn, phải reindex — *Code search for AI agents*
  (zzet.org/gortex/grep-replacement-for-ai-agents/).
- LSP cho cái text và embedding về nguyên tắc không cho: resolve theo scope và binding thật,
  phân biệt trùng tên/shadowing/overload, suy kiểu, rename an toàn, diagnostics — các request
  `textDocument/references`, `callHierarchy`, `rename`, `publishDiagnostics` trong
  *LSP Specification 3.17* (microsoft.github.io/language-server-protocol).
- **Sourcegraph đã bỏ embeddings cho Cody Enterprise**, chuyển sang keyword/regex/structural
  cộng code intelligence SCIP (sourcegraph.com/docs/cody/faq). Aider dùng tree-sitter + xếp
  hạng đồ thị thay vì embeddings (aider.chat/2023/10/22/repomap.html).
- Chiều ngược lại: Cursor đo semantic search **cộng thêm** trên grep giúp accuracy **+12,5%**
  trung bình (6,5–23,5% tuỳ model), và +2,6% ở repo từ 1000 file trở lên
  (cursor.com/blog/semsearch).
- **Không tìm thấy** số liệu công khai so recall/precision của semantic search với
  find-references trên cùng bộ test. CodeSearchNet chỉ đo MRR cho truy vấn ngôn ngữ tự nhiên
  → đoạn mã, không đo tính đầy đủ.

Ghi chú đọc: nguồn Cursor nói semantic search **cộng vào** grep, không thay grep — trùng
với kết quả đo ở mục 1–3.

## 5. Trả lời câu hỏi 2 — chất lượng giảm bao nhiêu

Cách tính: mỗi loại truy vấn lấy **recall so với ground truth**, rồi so hai đường ống.
Đường ống là hợp của các lớp nó có (agent gộp kết quả trước khi đọc, đúng như luật hiện hành).

| Truy vấn | LSP đơn | lumen đơn | grep đơn | Hiện tại LSP+lumen+grep | Bỏ LSP: lumen+grep |
|---|---|---|---|---|---|
| A — tên symbol chính xác | 17 % | 17 % | 100 % | **100 %** | **100 %** |
| B — khái niệm mơ hồ | trúng, hạng 28/78 | trượt | trúng | **trúng** | **trúng** |
| C — ai gọi hàm này | 8 % | 25 % | 100 % | **100 %** | **100 %** |

**Con số trả lời: 0 %.** Trên ba loại truy vấn tìm-kiếm này, đo trên repo này, bỏ LSP
**không mất gì đo được** — vì grep đã đạt recall 100 % ở cả hai câu có ground truth đếm được,
và LSP không đóng góp một kết quả nào mà grep hoặc lumen không có.

Về tốc độ — đúng động cơ bạn nêu: LSP 4,56–5,93 s, lumen 6,33–9,34 s, grep ~4,8–5 s mỗi lệnh.
Chênh lệch dưới ~5 s ở đây nằm trong nhiễu của round-trip harness, nên **không lớp nào nhanh
hơn hẳn**. Luật hiện hành bắt gọi **song song LSP + lumen rồi mới grep**, tức mỗi truy vấn
symbol tốn ít nhất 2 lệnh gọi thay vì 1. Bỏ LSP cắt được đúng một lệnh gọi mỗi lần tìm, và
cắt luôn phần output rất tốn context của nó (truy vấn B trả **78 kết quả** cho một câu hỏi có
một đáp án).

Nhưng con số 0 % chỉ đúng trong phạm vi nó đo. Ba giới hạn phải nói rõ:

1. Chỉ đo **tìm kiếm**. Không đo rename an toàn, diagnostics, suy kiểu, phân biệt trùng tên —
   những việc grep và lumen về nguyên tắc không làm được (mục 4, nguồn LSP 3.17).
2. Repo này là Python, quy mô vừa, tên hàm đặt riêng biệt. grep thắng đậm một phần vì thế.
   Repo nhiều trùng tên, nhiều overload, hoặc ngôn ngữ tĩnh nhiều generic thì khác.
3. grep đạt 100 % recall nhưng precision 67 % ở truy vấn C, và ở truy vấn B chỉ trúng vì
   **đã biết sẵn token**. Với repo lạ, phần "đoán ra token" là chi phí không hiện trong bảng.

## 6. Trả lời câu hỏi 3 — case nào vẫn phải dùng LSP

Không phải case tìm kiếm, mà là case **cần bảo đảm đúng**, nơi sai một chỗ là hỏng:

- **Đổi tên xuyên repo** (`rename_symbol`). grep không phân biệt được `load` của `tdq_state`
  với `json.load` — bảng mục 3 cho thấy đúng 6 file dương tính giả. Sửa hàng loạt theo grep
  là đổi nhầm.
- **Kiểm tác động trước khi sửa** (`blast_radius`, `find_references`): cần biết *đủ*, mà
  embedding top-k về bản chất không hứa đủ (mục 4, Sourcegraph).
- **Trùng tên / shadowing / overload**: cùng một chữ ở nhiều module, chỉ binding thật mới
  phân biệt được.
- **Lỗi hiện tại của file sau khi sửa** (`get_diagnostics`) và **suy kiểu của biểu thức**:
  không lớp text nào thay được.

Bốn case này có một điểm chung: câu hỏi có **một đáp án đúng duy nhất và cần đủ**. Truy vấn
khám phá ("chỗ nào xử lý retry") thì ngược lại — lumen là lớp đúng, và mục 2 cho thấy nó là
lớp duy nhất nhận thẳng câu hỏi tiếng Việt không cần đoán từ khoá.

## 7. Trả lời câu hỏi 1 — có nên bỏ không

**Khuyến nghị: hạ cấp, không bỏ.** Cụ thể:

1. **Bỏ ràng buộc "bắt buộc gọi song song LSP + lumen ở mọi truy vấn symbol".** Đo thật cho
   thấy ràng buộc này tốn thêm một lệnh gọi mỗi lần tìm mà không thêm một kết quả nào. Mặc
   định mới nên là: **tên đã biết → grep trước; câu hỏi khái niệm → lumen; LSP gọi theo yêu
   cầu.**
2. **Giữ LSP cho đúng 4 case ở mục 6**, gọi có chủ đích chứ không gọi mặc định.
3. **Việc cần làm trước cả hai điều trên**: điều tra vì sao `find_callers` chỉ thấy 1/12 file.
   Nếu cross-file index hỏng thì LSP đang không làm được cả 4 case ở mục 6, và câu "giữ LSP
   cho case nào" hiện là lý thuyết. Thang `tdq_lsp.py kiem` báo 6/6 nhưng không kiểm điều này
   — bản thân thang đo đang thiếu một bậc.

Nói thẳng cho câu hỏi (d) của bạn — LSP có thừa không: **ở dạng đang dùng thì có**, vì nó
đang bị gọi bắt buộc cho mọi truy vấn mà không đóng góp kết quả. Ở dạng đúng của nó thì không
thừa, nhưng phải sửa được điểm 3 trước đã.

Báo cáo này **không sửa luật nào**. Đổi hay không là quyết định của bạn; chọn đổi thì mở
request thi hành riêng, như 2301 → 2355.
