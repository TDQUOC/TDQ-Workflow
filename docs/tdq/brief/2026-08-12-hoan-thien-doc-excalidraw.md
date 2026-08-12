# BRIEF — Hoàn thiện product document trên Excalidraw

Ngày: 2026-08-12 · Lane: <chờ user chốt>

## Nguyên văn

> okay hãy lập request để bổ sung thêm cho đầy đủ và sắp xếp all mọi thứ đang có trên
> excalidraw thành một document hoàn chỉnh

Bối cảnh: turn trước tôi đã rà và liệt kê 8 mảng còn thiếu so với một product document
đầy đủ. User chốt: bổ sung các mảng thiếu + sắp xếp lại toàn bộ canvas thành 1 document
mạch lạc.

**Hiện có trên canvas (6 khối):**
1. Flow làm việc của plugin (flowchart lane quick/full)
2. Ưu điểm & lợi ích cho dev (10 ô)
3. Nền tảng & cách Test/Dev sản phẩm
4. Manifest & Dependency của plugin (5 panel: manifest, hooks, skills, deps, dùng-ngoài)
5. Sequence Diagram — trình tự 1 request (6 lifeline, 19 message đã đánh số)

**Thiếu (từ rà soát turn trước):**
1. Tổng quan sản phẩm — problem statement, đối tượng dùng, vị trí sản phẩm
2. Kiến trúc & cấu trúc thư mục repo
3. State machine của `docs/tdq/state.json` (transition + schema)
4. Getting Started / cài đặt (nguồn: `docs/notes/user-level-install.md`)
5. Giới hạn / known limitations
6. Roadmap / trạng thái phát triển (hiện 0.11.2)
7. Troubleshooting / FAQ
8. Ví dụ thực tế 1 request cụ thể

**Ngoài việc bổ sung:** sắp xếp lại layout toàn canvas theo thứ tự đọc của một document
(overview → kiến trúc → cách dùng → chi tiết kỹ thuật → giới hạn/FAQ), đánh số chương.

**Mục tiêu (hiểu ban đầu):** canvas Excalidraw trở thành 1 product document đọc được từ
trên xuống, không thiếu mảng nào, không chồng lấn/tràn chữ.

**Phạm vi đoán:** chỉ thao tác trên canvas Excalidraw (không phải file repo), trừ tài
liệu TDQ (brief/spec/plan/report) và working log.

**Chỗ chưa rõ:**
- Bổ sung đủ cả 8 mảng hay chỉ một số?
- Sắp xếp lại = di chuyển khối cũ, hay xoá làm lại từ đầu cho đồng bộ style?
- Có cần export ra file (`.excalidraw` / PNG) commit vào repo không?

## Hiểu & kiến thức

### Năng lực dùng được

| Skill | Phán quyết | Vì sao |
|---|---|---|
| `excalidraw-skill` (user) | DÙNG | Toàn bộ việc là vẽ/sắp xếp trên canvas Excalidraw |
| `tdq-conventions` + `tdq-spec/plan/build` | DÙNG | Lane full, bắt buộc theo khung |
| `graphify` | BỎ | Không đổi code, chỉ đổi doc/canvas |
| `mem0-memory` | DÙNG (nhẹ) | Lưu 1 fact về quyết định layout document |
| `figma-*`, `canva-*`, `adobe-*` | BỎ | Công cụ thiết kế khác, user đã chọn Excalidraw |
| Toàn bộ `unity-*` | BỎ | Không liên quan |

### Dữ kiện thật lấy từ repo (nguồn cho từng khối sẽ vẽ)

| Khối cần vẽ | Nguồn dữ kiện |
|---|---|
| State machine | `PHASE_TABLE`, `scripts/tdq_state.py:475-620` — 7 phase + nhánh `quick`; `VALID_PHASES` dòng 32 |
| Schema state.json | `docs/tdq/state.json` — `schema_version: 3`, 18 field |
| Kiến trúc thư mục | `hooks/scripts/` 6 file · `scripts/` 7 script · `skills/` 6 skill · `portable/` · `tests/` · `docs/tdq/` |
| Getting Started | `docs/notes/user-level-install.md` mục 1–5 |
| Giới hạn | `docs/tdq/reports/2026-08-11-cai-tdq-project-level.md` dòng "Giới hạn"; `user-level-install.md` mục "Lưu ý an toàn" |
| Roadmap / lịch sử | `CHANGELOG.md` — hiện 0.11.2 (2026-08-09) |
| Troubleshooting | `user-level-install.md` "Lưu ý an toàn" — hook chỉ NHẮC, không chặn; điểm chặn duy nhất là working log |

### Research chuẩn cấu trúc documentation

Chi tiết: `docs/tdq/research/2026-08-12-hoan-thien-doc-excalidraw.md`. Chốt lại:

- **Diátaxis** — 4 loại (tutorial / how-to / reference / explanation) phải tách bạch,
  không trộn trong một khối.
- **Thứ tự đọc chuẩn**: overview → features → install/quickstart → core concepts →
  tutorial → how-to → architecture → reference → config → troubleshooting → roadmap.
  Tức là "làm tay trước, giải thích sau".
- **Riêng CLI tool**: reference cần lệnh + flag + exit code + biến môi trường; mô tả
  phải trùng help text thật (chống doc drift); changelog bắt buộc.
- **Poster one-page**: ẩn dụ bản đồ tàu điện — chỉ tuyến, điểm dừng, điểm chuyển; ký
  hiệu nhất quán; cấu trúc bản đồ nên trùng cấu trúc thư mục thật.

Đối chiếu với canvas hiện tại: 5 khối đang có phủ đúng ô "features" (ưu điểm), "how-to"
(flow lane), "reference" (manifest/dependency), "explanation" (sequence diagram, nền
tảng). Thiếu chính là đầu (overview, install) và đuôi (troubleshooting, roadmap, giới
hạn), cộng "core concepts" (state machine) ở giữa.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | CÓ (đã xong) | Cần chuẩn ngoài (Diátaxis) để chốt thứ tự chương, không tự bịa |
| Interview | CÓ (đã xong vòng 1) | 4 câu phạm vi/bố cục/lưu file — user đã chốt 1A 2A 3A 4A |
| Spec | CÓ | Khung bất biến |
| Plan | CÓ | 13 chương = 13+ task, cần checklist tick từng chương |
| Implement | CÓ | Khung bất biến |
| Chia subagent | BỎ | Tất cả thao tác đi qua một canvas Excalidraw dùng chung — nhiều agent ghi song song sẽ tranh z-order và tọa độ |
| QC | CÓ | Kiểm bằng script trên scene JSON + screenshot |
| QC độc lập (agent `tdq-qc-tester`) | BỎ | QC ở đây là kiểm hình học trên scene JSON, chạy bằng lệnh, không cần con mắt thứ hai; agent phụ không xem được canvas |
| Review sâu (`tdq-reviewer`) | BỎ | Spec ngắn, phạm vi đã chốt rõ bằng 4 câu interview |
| Report | CÓ | Khung bất biến |

## Hỏi đáp

### Vòng 1 — 2026-08-12 12:11

Đã hỏi user 4 câu, chờ trả lời:

1. Phạm vi bổ sung: đủ 8 mảng (A, đề xuất) / 5 mảng cốt lõi (B) / user chỉ định (C)
2. Xử lý 5 khối cũ: di chuyển + đánh số chương (A, đề xuất) / xoá vẽ lại đồng bộ (B)
3. Bố cục: một cột dọc đọc từ trên xuống (A, đề xuất) / lưới poster (B) / lai (C)
4. Lưu ra repo: export `.excalidraw` + PNG vào `docs/diagrams/` (A, đề xuất) / không (B)

**User trả lời 12:14 — nguyên văn: "1A 2A 3A 4A"**

1. → Bổ sung **đủ cả 8 mảng**, canvas thành 13 chương
2. → **Di chuyển + đánh số chương** cho 5 khối cũ, giữ nguyên nội dung
3. → **Một cột dọc**, đọc từ trên xuống chương 1→13
4. → **Có export** `.excalidraw` + PNG vào `docs/diagrams/`

Không còn câu hỏi nào làm đổi kết quả → đóng vòng interview, sang phase spec.
