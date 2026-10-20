# BRIEF — Cập nhật tầng tìm kiếm với Graphify full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay hãy thử phân tích lại từ bộ full test thì nếu set graphify extract full và có wiki luôn thì có cần update lại tầng tìm kiếm không?

Đọc hiểu lần đầu:
- Phân tích lại kiến trúc tìm kiếm 3 tầng của TDQ Workflow dựa trên benchmark đầy đủ Photoboth360: nếu Graphify chạy `extract full` và có wiki/code-to-doc, có nên thay đổi thứ tự hoặc quy tắc chọn lớp tìm kiếm không.
- Đây là nghiên cứu và đề xuất trước; chưa thay đổi rule, hook, cấu hình hoặc behavior.
- Phải tách số liệu thực đo trong mẫu 11 file/12 truy vấn Photoboth360 khỏi giả thuyết về wiki, tài liệu và các repo khác.
- Cần cân nhắc tính mới của graph/wiki, độ tin cậy của liên kết semantic, chi phí cập nhật, rủi ro làm Graphify lấn át LSP/grep sai ngữ cảnh, và cách thử nghiệm trước khi cập nhật quy tắc.

## Hiểu & kiến thức

- Benchmark Photoboth360 đo full graph sẵn có, không đo `extract full` + wiki mới theo A/B. Phần được đo: imports P/R/F1 1.000/0.919/0.958 (57/0/5); callable 1.000/0.815/0.898 (22/0/5); scorer nội bộ top-5 scoped P/R/F1 0.286/0.857/0.429 (12/30/2); context CLI BFS P/R/F1 0.222/0.286/0.250 (4/14/10). Mẫu 11 file, 12 query do agent gán nhãn; không suy rộng toàn repo.
- Kết luận quan trọng: `_score_nodes` có thứ hạng nội bộ nhưng `graphify query` chọn seed rồi BFS/DFS để tạo context; thứ tự CLI NODE không là ranking. Vì chất lượng context CLI thấp, không có cơ sở đưa Graphify lên trước LSP/grep cho mọi truy vấn mơ hồ, càng không cho truy vấn ký hiệu/quan hệ.
- `extract full` tăng coverage graph nhưng không tự cải thiện ranking/context. Full extraction còn giữ cả cạnh/nút nhiễu nếu parser không resolve dynamic import/Schema.methods; benchmark đã thấy FN đó.
- Wiki/code-to-doc có thể bổ sung rationale/terminology, nhưng chưa được đo trên Photoboth360. Giá trị có điều kiện nếu wiki versioned, có provenance/path/line/link quan hệ rõ, được index cùng code và có freshness gate. Không được coi văn bản generated là oracle source.
- Quy tắc hiện hành đã chọn lớp theo loại câu hỏi, không phải thứ tự cứng: exact name→grep; relation/type/rename→LSP; vague concept→Graphify + grep; architecture/blast radius→Graphify. Số đo TDQ trước: LSP với cấu hình đúng có 15/15 coverage quan hệ và zero FP, grep 6 FP; LSP rank concept 13/62.
- Lumen đã được gỡ trong TDQ 0.58; benchmark hai repo cũ cho thấy thiếu Lumen không giảm đáng kể, nhưng không chứng minh Lumen vô ích hoặc Graphify full+wiki tương đương Lumen.
- Freshness là điều kiện cứng: graph stale không báo lỗi; wiki stale hoặc lệch branch còn nguy hiểm hơn vì giải thích có vẻ hợp lý. Có graph freshness ở setup/rung 7, nhưng không thấy kiểm chứng wiki freshness trong benchmark này.
- Đề xuất sơ bộ, chưa thay rule: giữ ba lớp và selector theo loại truy vấn; thêm Graphify full + wiki như một nguồn context có điều kiện cho khái niệm/kiến trúc/docs, với fallback LSP/grep và nguồn/dòng bắt buộc. Chỉ cân nhắc thay rule sau A/B trên cùng gold set: graph code-only vs full vs full+wiki, đo P/R/F1, P@k/MRR, context CLI, token/tool calls, freshness failure.

### Phạm vi đã chốt
- Mặt CHỌN: độ tin cậy/freshness; chi phí & thời gian; wiki & provenance; quy tắc tìm kiếm.
- Mặt LOẠI: thay LSP/grep, fallback tự động về code-only, dùng wiki generated làm oracle source, xử lý dữ liệu/money/public API.
- Bối cảnh: mỗi thay đổi code hoặc tài liệu phải full extract đồng bộ; lỗi backend/extract fail-closed và thông báo trực tiếp; QC full.
- Mức đầu tư suy ra: đầy đủ — vì thay đổi hook + rule toàn workflow, có chi phí API/runtime và quyết định fail-closed ảnh hưởng khả năng làm việc.

### Quyết định đã chốt
- Hành vi “luôn full” nghĩa là full semantic extraction trên mọi thay đổi code/tài liệu, không được tự degrade `--code-only`.
- Fail-closed nghĩa là graph/wiki hiện tại bị coi stale/không đủ điều kiện khi lần extract mới lỗi; terminal/chat phải nhận dòng thông báo có nguyên nhân, và hướng dẫn dùng LSP + grep.
- Wiki là artifact derived tách khỏi input corpus; mọi nội dung wiki phải nêu generation fingerprint và các liên kết source/provenance. Wiki export được tạo sau extract/cluster thành công.
- Selector tìm kiếm không được đảo ngay; thay đổi rule phụ thuộc benchmark A/B đặt trước trong spec: code-only vs full vs full+wiki, cùng corpus/gold và có chi phí/tính mới.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| spec → plan | CÓ | Hook, state freshness, wiki provenance và selector rule cần ranh giới/DoD đo được. |
| Benchmark A/B chuẩn bị trong spec/plan | CÓ | Là điều kiện trước khi cập nhật selector; không suy từ benchmark code-only hiện có. |
| Implement | CÓ | Thay `tdq_finish`, setup, rung freshness, test/hook/docs/rule theo plan đã duyệt. |
| QC full | CÓ | Chạy test vùng chạm, kiểm fail-closed và artifact/wiki trong môi trường local/có backend phù hợp; không nuốt lỗi API. |
| Research web/subagent | BỎ | Semantics cần dùng đã kiểm từ Graphify cài cục bộ và source workflow; không có ẩn số ngoài repo. |
| Independent QC agent | BỎ | QC full đủ test vùng chạm; agent không có lợi thế để xác minh API/cost khi chưa có ngân sách live run. |

### Năng lực dùng được

| Năng lực | Nguồn | Dùng? | Lý do |
|---|---|---|---|
| `tdq-intake` / `tdq-spec` / `tdq-plan` / `tdq-build` | plugin TDQ | Có | Workflow, spec, plan, triển khai hook và QC. |
| `tdq-setup` | plugin TDQ | Có | Kiểm rung search, cập nhật kiểm tra freshness theo thay đổi hook. |
| agent-lsp | MCP | Có giới hạn | Tìm/đọc symbol và blast radius; kiểm chứng cross-file Python đang trượt, user đã cho phép bypass request này. |
| Graphify CLI/package source | môi trường cài đặt | Có | Xác minh semantics `extract`, `--code-only`, wiki export, scorer/context. |
| `dataviz` | built-in | Có điều kiện | Chỉ dùng nếu cập nhật HTML/báo cáo số liệu. |
| Nghiên cứu web/sub-agent | bên ngoài | Bỏ | Đang phân tích hành vi của Graphify cài cục bộ và workflow nội bộ; chưa có ẩn số ngoài repo. |

### Phát hiện kỹ thuật ban đầu

- `scripts/tdq_finish.py:196–205` hiện chạy `graphify extract . --code-only` sau thay đổi code. `scripts/tdq_setup.py:1137–1143` cũng khởi tạo nền bằng `--code-only`; `scripts/tdq_lsp.py:464–489` kiểm freshness chỉ so graph với file mã nguồn và đề xuất lệnh code-only.
- Graphify full CLI (`cli.py:3218–3233`) gồm detect → AST code → semantic LLM cho docs/papers/images → merge → cluster. Nếu có semantic file mà không có backend/API key thì thất bại có chủ đích (`cli.py:3603–3727`). `--mode deep` mở rộng semantic pass cho toàn bộ docs/papers/images nhưng không tự giải quyết ranking/context.
- `graphify wiki` chỉ xuất sau khi graph có community analysis; sinh bài wiki từ graph vào `graphify-out/wiki/` và index entry point (`cli.py:3078–3094`). Đây là export derived, không tự là evidence mới; nếu đưa lại vào extraction có nguy cơ tự tham chiếu/duplicate nếu không tách input/output và provenance.
- Graph current của TDQ vừa được `tdq_finish` rebuild code-only. Full extraction/wikis sẽ làm freshness không thể chỉ so source-code mtime; cần manifest/fingerprint bao gồm code, tài liệu được chọn, cấu hình ignore, backend/model/mode và wiki generator version.

## Hỏi đáp

- User chọn `1b 2a`: pipeline deep, cho phép giữ thay đổi chưa commit và bypass kiểm chứng LSP cross-file riêng request này.
- User bổ sung yêu cầu rõ: hook phải luôn `graphify extract` full, không còn chỉ `--code-only`.
- User chọn 1A+B+C+D: phạm vi gồm freshness, chi phí/thời gian, wiki/provenance và cập nhật selector tìm kiếm có benchmark A/B.
- User chọn 2A: mỗi thay đổi code hoặc tài liệu kích hoạt full extraction đồng bộ; turn chỉ hoàn tất khi graph/wiki mới thành công.
- User chọn 3A và yêu cầu thông báo: full extraction lỗi hoặc backend không khả dụng → fail-closed; `tdq_finish` trả fail/state rõ với lý do và hướng dẫn fallback LSP+grep để thông báo trực tiếp trong terminal/chat, không dùng graph/wiki cũ như fresh.
- User chọn 4A: QC full.
- Còn quyết định thay đổi outcome: full extraction semantic theo 2A sẽ gọi backend/API trên mỗi code/doc change; benchmark A/B cần các lần full run có thể tiêu token/chi phí. Cần user chốt ngân sách/lần chạy trước khi spec/plan biến đây thành lệnh thực thi.
- User chọn A: dùng endpoint/model hiện tại, tối đa 3 lần full extraction thực trong request (baseline full, full + wiki, xác nhận/failure); unit tests mock runner và không gọi API.
- User duyệt thiết kế config an toàn: bổ sung toggle custom provider, endpoint và model vào config plugin; API key không ghi file mà chỉ lấy từ biến môi trường được config tham chiếu. Khi custom provider thiếu/tắt/thiếu key, chuyển sang code-only và thông báo trực tiếp cách điền config/env để bật full + wiki.
- Quyết định này thay đổi phạm vi và mâu thuẫn policy fail-closed cũ ở riêng trường hợp provider chưa được cấu hình: code-only là degraded mode được thông báo, không được giả là full graph/wiki fresh. Spec phải tăng bản và được duyệt lại trước khi triển khai.


- Người dùng cần chọn lane trước khi lập đề xuất chính thức. Đề xuất deep vì thay rule tìm kiếm ảnh hưởng toàn workflow/hook, cần benchmark A/B với wiki và thiết kế freshness gate; express chỉ phù hợp nếu dừng ở báo cáo không thay đổi rule.
- Repo có rất nhiều tệp chưa commit (audit/HTML/benchmark/graph config); chưa có quyền giữ dirty/bỏ qua LSP riêng request này. Không tự mở branch hoặc thay đổi rule.
