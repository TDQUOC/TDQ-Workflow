# Research: Cấu trúc documentation đầy đủ cho developer tool (CLI plugin)

Ngày: 2026-08-12 — công cụ: tavily-primary (4 truy vấn khác góc nhìn)

## Truy vấn 1 — Diátaxis framework (tutorial / how-to / reference / explanation)

Nguồn:
- https://diataxis.fr
- https://bssw.io/items/diataxis-a-systematic-approach-to-technical-documentation-authoring
- https://blog.sequinstream.com/we-fixed-our-documentation-with-the-diataxis-framework
- https://www.youtube.com/watch?v=0BqucaRwHhA

Rút ra:
- 4 nhu cầu người đọc → 4 loại nội dung TÁCH BẠCH: **Tutorial** (học bằng cách làm),
  **How-to guide** (giải quyết một vấn đề cụ thể), **Reference** (tra cứu, khô, chính xác),
  **Explanation** (hiểu vì sao, kiến trúc/nguyên lý).
- Lưới 2 chiều: Acquisition↔Application, Action↔Cognition. Tutorial+Explanation phục vụ
  "học"; How-to+Reference phục vụ "đang làm việc".
- Nguyên tắc: **một trang một ý định**, không trộn loại; cross-link giữa các loại.
- Kinh nghiệm thực tế (Sequin): bắt đầu bằng trải nghiệm tay chân (quickstart) chứ không
  phải giải thích; quickstart phải cắt gọn về đúng MỘT "aha moment"; reference nên đứng
  riêng hẳn; "guides" nửa tutorial nửa how-to là mùi lỗi cấu trúc.

## Truy vấn 2 — Checklist section chuẩn của product/software documentation

Nguồn:
- https://dev.to/georgekobaidze/15-essential-sections-every-readme-needs-give-your-project-what-it-deserves-fie
- https://www.altexsoft.com/blog/technical-documentation-in-software-development-types-best-practices-and-tools
- https://www.archbee.com/blog/software-documentation
- https://questsys.com/app-dev-blog/software-documentation-types-and-best-practices

Rút ra:
- Bộ section README/product chuẩn: Title + Introduction → Table of Contents → About
  (vấn đề giải quyết) → Features → Tech Stack → Architecture → Project Structure →
  Getting Started (cài + chạy) → Configuration → Security → Contributing → What's Next
  (roadmap) → License → Acknowledgements → Author.
- Phân loại lớn: **product documentation** (system docs + user docs) vs **process
  documentation** (roadmap, changelog, chuẩn, quy ước).
- Nhóm nội dung theo Archbee: user/product docs (getting started, tutorial, how-to, FAQ,
  troubleshooting, release notes); developer docs (API/CLI reference, SDK, integration,
  code sample); architecture & design (system overview, diagram, ADR, deployment model);
  process & lifecycle (roadmap, changelog, conventions).
- SAD (tài liệu kiến trúc) gồm: Overview & background → Product description (yêu cầu
  chức năng/phi chức năng) → High-level architecture + lý do quyết định + ràng buộc, kèm
  sơ đồ.
- Tiêu chí "docs tốt": đúng đối tượng, dễ tìm (cấu trúc + search + navigation), có
  version khớp bản ship, style nhất quán, có ví dụ.

## Truy vấn 3 — Best practice riêng cho CLI tool

Nguồn:
- https://document360.com/blog/cli-documentation
- https://clig.dev (Command Line Interface Guidelines)
- https://developers.google.com/style/code-syntax
- https://www.thoughtworks.com/en-us/insights/blog/engineering-effectiveness/elevate-developer-experiences-cli-design-guidelines

Rút ra:
- CLI docs KHÁC API docs: không có request/response, thay bằng **exit code, biến môi
  trường, stdin/stdout, flag, argument**. Phải chính xác tới từng chuỗi ký tự người dùng gõ.
- Khuôn một trang CLI reference: `tên – mô tả một dòng bắt đầu bằng động từ` → synopsis →
  arguments → options/flags → ví dụ copy-paste chạy được → exit codes → xem thêm.
- Mô tả một dòng trong docs phải TRÙNG với help text trong terminal (single-sourcing để
  tránh doc drift).
- Ba kênh tài liệu song song: help trong terminal (`--help`), man page, web docs. Web docs
  để search/link; terminal docs để nhanh + khớp version + offline.
- clig.dev: đưa flag/lệnh phổ biến nhất lên ĐẦU help text (như `git`).
- **Changelog là bắt buộc** cho CLI: người dùng cần biết breaking change, lệnh mới, tham số mới.
- Docs nên "agent-readable": cấu trúc rõ, plain text, nhiều ví dụ.
- Nhất quán cấu trúc lệnh (`tool <noun> <verb>`), theo quy ước ngành (`-v/--verbose`).

## Truy vấn 4 — Tổ chức dạng one-page visual / bản đồ tài liệu

Nguồn:
- https://webstyleguide.com/4-information-architecture.html
- https://www.knowledgeowl.com/blog/posts/information-architecture
- https://help.zeroheight.com/hc/en-us/articles/36474095888923-How-to-structure-your-documentation-s-information-architecture-IA

Rút ra:
- Site diagram/site map là tài liệu lõi khi lập kế hoạch: vừa thể hiện phân cấp người dùng
  thấy, vừa phản chiếu cấu trúc thư mục/file thật (nên trùng nhau).
- Ẩn dụ **bản đồ tàu điện ngầm London**: bản đồ tốt KHÔNG vẽ hết mọi đường hầm — chỉ vẽ
  các tuyến (categories), vùng (zones), điểm dừng (units of content) và điểm chuyển tuyến
  (connections) mà người đi cần. Với poster one-page: chọn đúng lớp thông tin cho ngữ
  cảnh, cắt phần thừa, nếu không người xem bị quá tải.
- Bố cục phân cấp gợi ý cho bản đồ: nhóm (group) → chuyên mục (category) → trang (page) →
  tab trong trang. Mỗi node nên có nhãn ngắn + ký hiệu nhất quán (visual vocabulary kiểu
  Jesse James Garrett: page, page stack, link, decision point).
- IA giống tảng băng: phần nhìn thấy là category + navigation + link; phần chìm là taxonomy
  và quan hệ — poster nên vẽ phần nhìn thấy, còn quan hệ thì thể hiện bằng mũi tên/lối đi.

## Kết luận — thứ tự section đề xuất

1. Overview / What & Why (vấn đề giải quyết, ai dùng)
2. Features / Capability map
3. Install & Getting Started (quickstart 1 "aha moment")
4. Core Concepts / Glossary
5. Tutorials (học bằng làm)
6. How-to guides (theo tình huống)
7. Architecture & Data flow (sơ đồ, ADR, lý do quyết định)
8. Reference (lệnh/flag/exit code, config, hooks, biến môi trường, cấu trúc thư mục)
9. Configuration & Integration
10. Troubleshooting / FAQ
11. Roadmap, Changelog / Release notes, Contributing, License

Ba trục ngang xuyên suốt: cross-link giữa 4 loại Diátaxis, ví dụ chạy được ở mọi trang,
version khớp bản ship.
