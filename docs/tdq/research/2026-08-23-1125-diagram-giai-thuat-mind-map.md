# Research: diagram giải thuật + function flow + mind map trước khi code

Ngày: 2026-08-23. Câu hỏi gốc: thiết kế diagram trước khi code, ánh xạ
sang function flow, gom behavior tree, render mind map HTML có đáng làm
không, và đã có công cụ sẵn chưa.

### 1. Tài liệu hoá luồng trước khi code có cải thiện hiểu/debug/maintain không

| Nguồn (URL) | Điều rút ra |
| --- | --- |
| https://magazine.swissinformatics.org/en/the-curious-case-of-software-documentation | Xia et al. 2018 (IEEE TSE): dev dành ~58% thời gian đọc hiểu code. |
| https://web.eecs.umich.edu/~weimerw/p/weimer-icpc2020.pdf | Prechelt et al: tài liệu design pattern gắn kèm code giúp comprehension tốt hơn. |
| https://www.researchgate.net/publication/372333112_Evaluating_Software_Documentation_Quality | Chất lượng tài liệu thiết kế được công nhận quan trọng cho comprehension. |
| https://fabric.so/blog/outdated-docs-are-worse-than-no-docs | Tài liệu lỗi thời gây hại: dẫn sai hướng, tạo "documentation paradox". |
| https://document360.com/blog/documentation-drift | 60% tài liệu lỗi thời trong 6 tháng nếu không có cơ chế đồng bộ. |

Nhận xét: bằng chứng nghiêng về có lợi nếu tài liệu ĐÚNG và ĐƯỢC CẬP NHẬT.
Rủi ro lớn nhất không phải "có hay không" mà là drift — lỗi thời còn hại
hơn không có tài liệu.

### 2. AI coding agent có làm tốt hơn nhờ bản đồ kiến trúc/code không

| Nguồn (URL) | Điều rút ra |
| --- | --- |
| https://aider.chat/docs/repomap.html | Aider dùng repo map từ AST + graph ranking, không phải RAG thường. |
| https://news.ycombinator.com/item?id=41002519 | Repo map giúp Aider đạt top-2 SWE-bench thời điểm đó, không cần RAG. |
| https://www.morphllm.com/comparisons/aider-vs-claude-code | Claude Code dùng tìm kiếm tự trị + context 1M token, khác cơ chế map tĩnh. |
| https://arxiv.org/html/2503.09089v1 | LocAgent: định vị code bằng graph giúp tăng Acc@5 và tỉ lệ fix issue thành công. |
| https://arxiv.org/html/2507.19942v1 | Prometheus: biểu diễn repo bằng knowledge graph cải thiện xử lý issue đa ngôn ngữ. |

Nhận xét: có bằng chứng thực nghiệm (LocAgent, Prometheus) rằng biểu diễn
code dạng graph/map giúp agent định vị và sửa lỗi chính xác hơn. Đây là
graph tự động từ code, không phải diagram nghiệp vụ viết tay như đề xuất.

### 3. Công cụ sẵn có — cái nào sinh tự động, cái nào viết tay

| Nguồn (URL) | Điều rút ra |
| --- | --- |
| https://github.com/scottrogowski/code2flow | code2flow: sinh call graph tự động từ AST, Python/JS/Ruby/PHP. |
| https://www.x-cmd.com/install/code2flow | code2flow tốt cho hiểu cấu trúc nhanh, không hoàn hảo với ngôn ngữ động. |
| https://www.upgradejs.com/blog/application-architecture-visualization.html | Madge và Dependency-Cruiser: sinh graph phụ thuộc module tự động từ code JS/TS. |
| https://www.in-com.com/blog/code-visualization-turn-code-into-diagrams | Diagram-as-code (Mermaid/PlantUML/D2) lưu trong repo, CI tự render lại khi code đổi. |
| https://arxiv.org/html/2602.00180v1 | GitHub Spec Kit và Amazon Kiro: viết spec/design TRƯỚC code, người duyệt từng giai đoạn. |

Nhận xét: call graph / dependency graph (code2flow, Madge,
Dependency-Cruiser) SINH TỰ ĐỘNG từ code, luôn đồng bộ vì chạy lại được.
Diagram nghiệp vụ (giải thuật, behavior tree) thì PHẢI viết tay vì mô tả
ý định con người, không suy ra được từ code. Spec-kit/Kiro là mô hình gần
nhất với ý tưởng user: spec → plan → task, có human review từng bước.

### 4. Cách trình bày — mermaid trong CLI và mind map HTML offline

| Nguồn (URL) | Điều rút ra |
| --- | --- |
| https://github.com/fasouto/termaid | termaid render Mermaid ra ASCII/Unicode ngay trong terminal, không cần trình duyệt. |
| https://qwenlm.github.io/qwen-code-docs/en/users/features/markdown-rendering | Giới hạn: cần Mermaid CLI cài thêm, ASCII chỉ là preview chứ không đúng layout gốc. |
| https://news.ycombinator.com/item?id=46804828 | Tranh luận: ASCII dễ đọc trong CLI nhưng giới hạn ký tự, kém biểu cảm hơn Mermaid render. |
| https://skillsllm.com/skill/mindmap-markmap-viewer | markmap.js: xuất mind map thành 1 file HTML tự chứa, chạy offline không cần CDN. |
| https://lobehub.com/skills/lkb-99-manus-skills-collection-mindmap | Markmap từ Markdown heading, nhúng asset sẵn trong HTML, không gọi API ngoài. |

Nhận xét: Claude Code hiển thị được code-fence mermaid dạng text nhưng
không render hình; muốn xem hình phải mở HTML. Markmap là thư viện có sẵn
để xuất mind map HTML tự chứa, không cần CDN — khớp yêu cầu offline.

## Kết luận tạm

Bằng chứng ủng hộ 2 tầng khác nhau trong ý tưởng user. Tầng graph code
(function flow, dependency) nên SINH TỰ ĐỘNG bằng code2flow/Madge hoặc
tương đương, vì tự động thì luôn đồng bộ, viết tay sẽ drift theo thời
gian (document360, fabric.so). Tầng diagram giải thuật nghiệp vụ và
behavior tree phải viết tay vì diễn tả ý định, giống mô hình spec-kit/Kiro
có human review từng bước trước khi code. Có bằng chứng thực nghiệm
(LocAgent, Prometheus, aider repomap) rằng cung cấp cấu trúc code dạng
graph giúp agent định vị và sửa lỗi chính xác hơn trên codebase lớn — ủng
hộ việc dùng lớp dữ liệu này làm nguồn cho AI truy vấn, không chỉ để
người đọc. Về trình bày, dùng markmap.js xuất HTML tự chứa offline là lựa
chọn khớp yêu cầu `docs/tdq/mind-map/`; mermaid text vẫn hữu ích để xem
nhanh trong CLI nhưng không thay được bản HTML render đầy đủ. Điểm yếu
nhất trong bằng chứng: chưa tìm được nghiên cứu định lượng riêng cho
việc vẽ diagram giải thuật nghiệp vụ (không phải sơ đồ kỹ thuật) trước
khi code — phần này chủ yếu suy ra từ khảo sát thực hành (spec-kit, Kiro)
chứ chưa có số liệu thực nghiệm độc lập.
