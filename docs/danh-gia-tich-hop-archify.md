# Báo Cáo Đánh Giá Chuyên Sâu: Khả Năng Tích Hợp Archify Vào TDQ-Workflow

> **Thời điểm lập:** 2026-10-24  
> **Trạng thái:** Báo cáo nghiên cứu kiến trúc (Read-only / Architectural RFC)  
> **Mục tiêu:** Phân tích năng lực hỗ trợ của Archify đối với Graphify và tính khả thi của việc sử dụng Archify để trực quan hóa kiến trúc sơ bộ ngay từ bước `spec` trong TDQ-Workflow trước khi viết mã.

---

## 1. Tóm Tắt Định Hướng (Executive Summary)

Dựa trên việc khảo sát sâu toàn bộ mã nguồn của **`Archify v3.2.0`** (tại `C:\Users\admin\Documents\archify`) và **`TDQ-Workflow v0.81.0`**, chúng tôi xác nhận hai kết luận kiến trúc then chốt:

1. **Về việc hỗ trợ `Graphify`:**
   - `Graphify` là công cụ xuất sắc ở tầng trích xuất tĩnh (AST extraction, Call Graph, Louvain community, trích xuất quan hệ phụ thuộc).
   - Tuy nhiên, tầng hiển thị hiện tại của Graphify (`CALLFLOW.html`, `GRAPH_TREE.html`) tồn tại điểm nghẽn lớn: phụ thuộc vào thư viện Mermaid.js tải từ CDN mạng ngoài (`cdn.jsdelivr.net`), sơ đồ tĩnh không tương tác sâu, dễ rối/chồng chéo nhãn khi đồ thị vượt quá 20–30 nút.
   - `Archify` đóng vai trò hoàn hảo như một **Interactive Architecture Console & Layout Compiler** (A* orthogonal routing, zero-network standalone HTML, Semantic Passport, Upstream/Downstream Reachability, Route-probe tìm đường gọi ngắn nhất, và hiệu ứng motion dòng chảy). Hai hệ thống tạo thành mô hình: **Graphify trích xuất dữ liệu $\rightarrow$ Archify biên dịch & trực quan hóa tương tác offline**.

2. **Về việc sử dụng ở bước `spec` (Trước khi triển khai code):**
   - **Archify không chỉ dùng cho dự án có sẵn mà sinh sơ bộ kiến trúc ở bước `spec` chính là điểm ngọt nguyên bản (sweet spot) của nó.**
   - Triết lý cốt lõi của Archify là biến ý tưởng, quy trình và thiết kế sơ bộ thành trang HTML tương tác hoàn chỉnh mà không đòi hỏi phải có mã nguồn hay commit Git từ trước (thông qua chế độ `illustrative` / `conceptual`).
   - Trong TDQ-Workflow, Archify có thể trực tiếp nâng cấp mục **§2b (Ranh giới module)** và **§2c (Luồng hoạt động & Sơ đồ kiến trúc)** của bản spec, sinh ra file HTML xem trước (`docs/tdq/spec/<slug>-preview.html`) giúp lập trình viên và người dùng duyệt trực quan toàn cảnh luồng nghiệp vụ trước khi bước vào Phase `implement`.

---

## 2. Bản Chất & Cơ Chế Hoạt Động Của Archify (`v3.2.0`)

```
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                            AI AGENT / DEVELOPER (Claude Code)                               │
└──────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                               │ Sinh candidate JSON-IR / Markdown
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                        BỘ ĐIỀU PHỐI CLI (archify/bin/archify.mjs)                           │
│  Lệnh chính: finalize <type> <candidate.json> <output.html> --quality showcase --json       │
└───────┬──────────────────────────┬──────────────────────────────┬───────────────────────────┘
        │                          │                              │
        ▼                          ▼                              ▼
┌───────────────────┐    ┌─────────────────────────┐    ┌─────────────────────────────────────┐
│ 6 TẦNG VALIDATION │    │   10 NATIVE RENDERERS   │    │       EXPLAINER SUBSYSTEM           │
│ - Ajv Standalone  │    │ - architecture (A* grid)│    │ - parse.mjs (.archify.md / .json)   │
│ - Portable Path   │    │ - workflow (v2 topo)    │    │ - validate.mjs + writing linter     │
│ - Cross-Ref IDs   │    │ - sequence (lifelines)  │    │ - prepare.mjs (sources, Pele charts)│
│ - Eng. Profiles   │    │ - dataflow (compiler)   │    │ - layout.mjs (12-column packing)    │
│ - Git Evidence    │    │ - lifecycle (v3 arcs)   │    │ - render.mjs (Gzip Base64 payload)  │
│ - Route/Geometry  │    │ - erd · class · tree    │    │ - patch.mjs (sửa đúng 1 panel)      │
│   (Chống đè chữ)  │    │ - timeline · waterfall  │    └──────────────────┬──────────────────┘
└─────────┬─────────┘    └────────────┬────────────┘                       │
          └───────────────────────────┼────────────────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│              HẠ TẦNG DÙNG CHUNG & XUẤT BẢN NGUYÊN TỬ (archify/renderers/shared/)            │
│  - Giao nhận nguyên tử (atomic-output.mjs): Ghi file tạm, fs.renameSync, kiểm tra dev/ino.   │
│  - Định tuyến A* trực giao (routing.mjs): Chống cắt chéo, bo góc mượt mà, né node cản.     │
│  - Đo chữ Unicode 17.0 (text-fit.mjs): Chuẩn hóa ký tự CJK, ASCII, emoji, chống tràn nhãn.  │
│  - Kiểm định khung nhìn laptop 1440x900 (desktop-readability.mjs): Cỡ chữ chiếu >= 6px.     │
└──────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                               │ Nhúng vào archify/assets/template.html
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│               STANDALONE INTERACTIVE VIEWER RUNTIME (Zero-Network Artifact)                 │
│  - Không cần mạng (Offline 100%): Nhúng font JetBrains Mono Base64, CSS, JS runtime đầy đủ.  │
│  - Semantic Passport & Focus: Bấm vào 1 node -> Làm mờ phần thừa, hiện thông số chi tiết.   │
│  - Upstream / Downstream Reachability: Bấm xem toàn bộ luồng gọi đến hoặc bị ảnh hưởng bởi nó.│
│  - Route Probe (#route=A~B): Chọn 2 điểm bất kỳ để tự dò và highlight đường đi ngắn nhất.   │
│  - Semantic Lens & Radar: Lọc vai trò (frontend/backend/db) và bản đồ thu nhỏ (Minimap).    │
│  - Motion Governor: Hiệu ứng dòng hạt ánh sáng chạy dọc theo cạnh biểu diễn dữ liệu động.   │
│  - Export Engine: Xuất ảnh độ nét cao (PNG/SVG) hoặc quay video hoạt ảnh WebM chia sẻ.      │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Điểm khác biệt mấu chốt so với các công cụ sơ đồ truyền thống
1. **Triết lý "Claude-in-the-loop Layout Intelligence":** Từ chối các thuật toán auto-layout hộp đen (Dagre/ELK). Agent chỉ cần định hình vị trí tương đối mang tính ngữ nghĩa; Engine của Archify chịu trách nhiệm giải thuật toán A* trực giao, chống va chạm và cân bằng khoảng cách.
2. **Khả năng chạy ngoại tuyến hoàn toàn (Zero-network Artifact):** File `.html` đóng gói trọn vẹn SVG, font WOFF2 Base64, CSS/JS runtime, mở được ở mọi môi trường air-gapped không có internet.
3. **Giao nhận nguyên tử an toàn (Fail-closed Atomic Delivery):** Kiểm tra inode, ghi file tạm độc quyền và thay thế nguyên tử để không bao giờ để lại file hỏng.

---

## 3. Mối Quan Hệ Giữa Archify Và Graphify Trong TDQ-Workflow

### 3.1 Hạn chế hiện tại của Graphify về mặt hiển thị
Hiện tại, `scripts/tdq_graphify.py` thực hiện trích xuất dữ liệu mã nguồn rất mạnh mẽ thành `graphify-out/graph.json`. Tuy nhiên:
- File `CALLFLOW.html` sử dụng thẻ CDN `<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>`. Khi môi trường không có internet, sơ đồ không thể hiển thị.
- Sơ đồ Mermaid là ảnh tĩnh, khi đồ thị lớn sẽ xảy ra tình trạng dây nối cắt chéo, chữ bị đè, không có khả năng lọc theo vai trò (frontend, backend, database).
- Không hỗ trợ truy vết tương tác: khi lập trình viên muốn xem một hàm thay đổi sẽ ảnh hưởng đến những tầng nào (Blast Radius), Mermaid không hỗ trợ.

### 3.2 Khả năng Archify tiếp sức cho Graphify
Archify có thể kết hợp với Graphify theo mô hình **Pipeline 2 chặng**:
1. **Chặng 1 (Data Extraction):** Graphify quét mã nguồn, trích xuất AST, quan hệ gọi hàm và cộng đồng mô-đun vào `graphify-out/graph.json`.
2. **Chặng 2 (Interactive Synthesis):** Một bộ chuyển đổi (Adapter) chuyển các node/edge của một phân hệ trong `graph.json` sang định dạng `architecture.json` hoặc `workflow.json` của Archify:
   - Tận dụng trường `source_file` và `source_location` sẵn có của Graphify để ánh xạ thành trường `sources: [{ path, startLine, endLine }]` của Archify.
   - Biên dịch thành file HTML tương tác độc lập.

**Lợi ích thu được:**
- **Khảo sát vỡ lan tương tác (Interactive Blast Radius):** Nhờ tính năng Upstream/Downstream Reachability của Archify, dev bấm vào một controller là thấy ngay chuỗi service và repository bị ảnh hưởng sáng lên.
- **Dò đường thực thi (Route Probe):** Chọn 2 hàm bất kỳ để tìm luồng gọi ngắn nhất xuyên suốt các tầng kiến trúc.
- **Xem mã nguồn tại chỗ:** Bấm vào node trên sơ đồ để xem dẫn xuất dòng mã tương ứng trong Git.

---

## 4. Ứng Dụng Trong Bước `Spec`: Thiết Kế Kiến Trúc Sơ Bộ Trước Khi Viết Code

### 4.1 Khẳng định tính khả thi
Archify **hoàn toàn hỗ trợ thiết kế sơ bộ** khi chưa có mã nguồn. Hệ thống hỗ trợ chế độ phi thực chứng (`meta.evidence: "illustrative"`), không bắt buộc phải có commit Git hay file mã nguồn thực tế.

### 4.2 Nâng cấp trải nghiệm duyệt Spec trong TDQ-Workflow
Hiện tại, mục **§2c (Luồng & Sơ đồ kiến trúc)** của `skills/tdq-spec/SKILL.md` chỉ sử dụng khối Mermaid tĩnh trong markdown. Khi kết hợp với Archify:

1. **Quy trình sinh artifact song song:**
   - Trong phase `spec`, Agent hoàn thiện tài liệu `docs/tdq/spec/<slug>.md`.
   - Đồng thời, Agent sinh cấu trúc luồng dự kiến vào `candidate.json` (chỉ tốn khoảng 400–700 tokens LLM) và gọi CLI Archify để biên dịch ra:
     `docs/tdq/spec/<slug>-preview.html`
2. **Trải nghiệm duyệt spec của Dev & Khách hàng:**
   - Người dùng và lập trình viên mở file preview trên trình duyệt:
     - Quan sát toàn bộ ranh giới module (§2b) được phân vùng rõ ràng bằng Boundary.
     - Bật hiệu ứng Motion hạt ánh sáng để xem trực quan chuỗi sự kiện và dữ liệu di chuyển qua các thành phần.
     - Kiểm tra các nhánh rẽ lỗi (Retry / Fallback / Error Handling) được định tuyến trực giao rõ ràng.
     - Với các tác vụ Refactor, có thể sử dụng màn hình so sánh Split-view giữa kiến trúc Hiện trạng (Trước) và Thiết kế mới (Sau).

---

## 5. Bảng So Sánh Tổng Hợp

| Khía cạnh | Mermaid (Hiện tại trong Spec) | Graphify (Hiện tại trong Phân tích) | Archify (Đề xuất tích hợp) |
|---|---|---|---|
| **Vai trò chính** | Minh họa sơ đồ nhanh trong tài liệu Markdown | Trích xuất AST, xây dựng đồ thị phụ thuộc toàn repo | Biên dịch bố cục kiến trúc & Runtime tương tác cao cấp |
| **Phụ thuộc mạng** | Cần CDN khi render ra web | Cần CDN (`jsdelivr`) khi xem `CALLFLOW.html` | **Hoàn toàn Offline (Zero-network, nhúng Base64)** |
| **Bố cục & Định tuyến** | Hộp đen tự động (Dagre), dễ rối dây và đè nhãn | Thừa hưởng nguyên vẹn nhược điểm của Mermaid | **A\* trực giao né vật cản, Workflow topo compiler** |
| **Tính tương tác** | Tĩnh hoàn toàn | Tĩnh, chỉ phóng to / thu nhỏ cơ bản | **Semantic Passport, Reachability, Route-probe, Minimap** |
| **Giai đoạn Spec (Chưa có code)** | Có (viết text thủ công) | Không hỗ trợ (phải có code trên đĩa) | **Hỗ trợ tự nhiên (Sinh HTML preview từ ý tưởng/spec)** |
| **Giai đoạn Analyze (Đã có code)** | Thủ công | Tự động hóa rất tốt | Tích hợp sâu với Git SHA, trích dẫn dòng code thực |
| **Mô phỏng dòng chảy** | Không có | Không có | **Motion Governor mô phỏng hạt ánh sáng chuyển động** |
| **Độ an toàn ghi file** | Ghi đè thông thường | Ghi đè thông thường | **Atomic delivery (kiểm tra inode, chống hỏng file)** |

---

## 6. Đánh Giá Khía Cạnh Kỹ Thuật Khi Tích Hợp

1. **Chi phí Context Token:**
   - Cấu trúc JSON-IR của Archify cho sơ đồ 10–15 node chỉ chiếm ~400–700 tokens, tương đương một đoạn Mermaid chi tiết.
   - Quá trình biên dịch và nhúng tài nguyên do Node.js thực thi cục bộ, không tiêu tốn token của LLM.
2. **Môi trường & Tính khả chuyển:**
   - Archify chạy trên Node.js $\ge 18$ chuẩn ESM, không phát sinh dependency thứ ba khi phân phối, hoàn toàn tương thích với môi trường TDQ-Workflow.
3. **Bảo tồn Nguyên tắc Tinh gọn (Lean):**
   - Không bắt buộc mọi request đều phải sinh Archify:
     - `lane quick`: Tiếp tục duy trì Mermaid/text ngắn gọn để tối ưu tốc độ.
     - `lane full` hoặc khi người dùng yêu cầu: Kích hoạt Archify để tạo chốt chặn kiến trúc vững chắc.

---

## 7. Kết Luận & Khuyến Nghị

- Việc kết hợp Archify vào TDQ-Workflow là một bước nâng cấp kiến trúc mang lại giá trị thực tế cao, giải quyết trọn vẹn điểm yếu hiển thị của Graphify và đưa bước `spec` lên tiêu chuẩn trực quan hóa tương tác offline chuyên nghiệp.
- Tài liệu này được ghi lại nhằm phục vụ việc tham chiếu kiến trúc cho các đợt nâng cấp tiếp theo của TDQ-Workflow.
