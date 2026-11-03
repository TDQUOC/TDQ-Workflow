# BRIEF — Đo trước ở spec/plan, implement chạy hết plan trong một lượt

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> Hiện tại có tjnhf trạng như này khi implemenr tôi muốn update lại bộ workflow sẽ sẽ cố gắng
> smoke và estimate trong spec plan trước để implement thì soul là sẽ cố gắng implement all plan
> trong 1 turn hạn chế ngưng, chỉ ngưng trong trường hợp rất bất khả kháng

Kèm ảnh chụp một phiên excalidraw: agent dừng giữa implement ở T8.1 vì installer đo ra 232 MB
(WebView2 offline của Microsoft đã 212 MB, app ~20 MB), vượt ngưỡng Q9 ≤ 200 MB của spec. Agent
coi đổi ngưỡng là đổi spec nên dừng và hỏi (đề xuất nâng lên 250 MB).

**Đọc lần đầu**

- Mục tiêu: (1) ngưỡng số trong DoD phải được smoke/ước lượng TRƯỚC khi duyệt spec/plan, để mâu
  thuẫn kiểu 212 MB > 200 MB lộ ra lúc còn rẻ; (2) đã vào implement thì làm hết plan trong một
  lượt, chỉ dừng khi thật sự bất khả kháng.
- Phạm vi đoán: luật `tdq-spec`, `tdq-plan`, `tdq-build`; ngoại lệ dừng số 1 ở
  `tdq-conventions/SKILL.md` mục 7; `hooks/scripts/stop_gate.py` (đã chặn `TDQ:UNFINISHED`, có
  đường `implement_pause`); `doc_lint.py` cho spec.
- Gốc lỗi sơ bộ: ngoại lệ 1 "spec/plan scope change" quá rộng — một ngưỡng trượt cũng lọt vào đó;
  và không bước nào bắt buộc đo ngưỡng trước khi duyệt.

**User đã chốt (2026-10-03, câu hỏi đầu)**

1. Request cũ: commit + merge về main — đã làm (`287fc51`).
2. Gặp lệch spec lúc implement: **tự chọn phương án đề xuất, làm tiếp**; ghi "lệch spec" (số đo,
   phương án đã chọn, lý do) vào plan/QC; đến report mới hỏi user duyệt lệch hoặc quay lại.
3. Đo trước: **mọi ngưỡng số trong DoD** phải kèm số đo thật hoặc ước lượng có nguồn + biên an
   toàn; không đo được → ghi rủi ro kèm phương án dự phòng chọn sẵn.
4. Cưỡng chế: **luật + lint + hook** — `doc_lint` bắt spec có ngưỡng thiếu cột đo trước; stop gate
   thu hẹp ngoại lệ dừng, lệch spec không còn là lý do dừng hợp lệ.

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Nguồn | Dùng? | Vì sao |
|---|---|---|---|
| `tdq-spec`, `tdq-plan`, `tdq-build`, `tdq-conventions` | plugin:tdq-workflow | CÓ | chính là vùng sửa |
| `code-review`, `simplify` | built-in | CÓ | soát lỗi đúng-sai và rút gọn ở cuối plan, như request trước |
| `skill_inventory --loc` | script | đã chạy | không skill trên đĩa nào khớp ngoài bộ tdq |
| Research web (tavily) | — | BỎ | việc thuần nội bộ, không có ẩn số bên ngoài |

### Mã hiện có (đọc 2026-10-03)

- **Cổng `Stop` đã có:** `hooks/scripts/stop_gate.py::unfinished_reason` chặn `[TDQ:UNFINISHED]`
  khi phase `implement` còn task mở. Lối ra hợp lệ duy nhất: `tdq_state.py pause --ly-do "<…>"`
  (`_cli_implement_pause`) — nhận BẤT KỲ lý do nào, không phân loại.
- **Lỗ 1 — ngoại lệ dừng quá rộng.** `tdq-build/SKILL.md` (Hard rules) và `tdq-conventions/SKILL.md`
  mục 7 cho dừng khi "spec/plan scope change". Một ngưỡng DoD trượt (232 MB > 200 MB) được agent
  xếp vào đó → dừng hỏi là ĐÚNG LUẬT hiện tại.
- **Lỗ 2 — câu hỏi giữa lượt không bị cổng nào thấy.** Ảnh chụp cho thấy agent dừng bằng
  `AskUserQuestion` ngay trong lượt — không phải sự kiện `Stop`, nên `stop_gate` không can thiệp.
  `hooks.json` không có matcher nào cho `AskUserQuestion`.
- **Lỗ 3 — spec không bắt đo ngưỡng.** Khuôn §6 (`tdq-spec/references/spec-template.md`) chỉ có
  `# | Hạng mục kiểm | Điều kiện PASS`. `doc_lint.py` với file trong `docs/tdq/spec/` chỉ chạy
  R8/R10/R11/R12; không luật nào đòi bằng chứng cho một ngưỡng số. `approve spec` không gọi lint.
- **Chỗ gắn được:** luật mới R14 trong `doc_lint.py` (nhánh `is_output`, giới hạn thư mục `spec/`);
  `approve spec` có thể từ chối khi R14 đỏ; PreToolUse `AskUserQuestion` qua `_common.block()`.
- Ràng buộc kiến trúc: `docs/kien-truc.md` 2026-07-29 — không hook nào chặn vì "chưa duyệt";
  mỗi điểm chặn mới cần một dòng quyết định có ngày. Mọi deny đi qua `_common.block()`.

### Đã chốt

- Đo trước ở spec: §6 thêm cột **Đo trước** (số đo thật hoặc ước lượng + nguồn + biên) và cột
  **Dự phòng nếu trượt** (phương án chọn sẵn). Luật lint mới R14 bắt hàng có ngưỡng số mà thiếu
  hai cột đó; `approve spec` từ chối khi R14 đỏ (lối thoát `--bo-qua-do "<lý do>"` cho user).
- Gặp lệch spec lúc implement/qc: áp phương án dự phòng (hoặc phương án đề xuất), ghi bằng lệnh
  `tdq_state.py lech …` vào state, làm tiếp tới hết plan; QC ghi "PASS (lệch, chờ duyệt)";
  report hỏi user duyệt từng lệch. User bác một lệch → thêm task fix vào plan (quy tắc 5), quay
  lại implement trong cùng request.
- `pause` chỉ nhận 4 loại bất khả kháng: mất truy cập/công cụ hỏng · việc phá huỷ khó đảo ngược ·
  đầu vào chỉ user có · vòng sửa QC chạm trần 3. "Đổi phạm vi spec" bị gỡ khỏi danh sách dừng.
- `AskUserQuestion` ở phase implement/qc: hook **chỉ nhắc**, không chặn (user chọn).

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | BỎ | việc thuần nội bộ, không có ẩn số bên ngoài |
| Vòng phạm vi | BỎ | câu hỏi đầu đã chốt cả bốn mặt (xử lý lệch, mức đo, cưỡng chế, request cũ) |
| Interview chi tiết | CÓ | một vòng, 4 câu, hết câu hỏi |
| Spec → plan | CÓ | khung bất biến |
| Soát lỗi `code-review` + rút gọn `simplify` | CÓ | việc này sửa luật dừng và cổng duyệt của mọi request sau |
| QC độc lập bằng agent | BỎ | mức QC `full`, không phải `ultra` |

Luồng tính năng: (1) đo trước ở spec + R14 + cổng `approve spec` · (2) lệnh `lech` + QC/report
hiển thị lệch · (3) `pause` phân loại đóng + sửa luật dừng · (4) hook nhắc `AskUserQuestion`.

## Hỏi đáp

| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | Request cũ chưa commit? | Commit + merge về main |
| 2 | Gặp ngưỡng spec không đạt lúc implement? | Tự chọn phương án đề xuất, làm tiếp, hỏi ở report |
| 3 | Đo trước tới mức nào? | Mọi ngưỡng số trong DoD |
| 4 | Cưỡng chế bằng gì? | Luật + lint + hook |
| 5 | `AskUserQuestion` giữa lượt ở implement/qc? | Chỉ nhắc, không chặn |
| 6 | Lý do dừng bất khả kháng? | Cả 4: mất truy cập/công cụ hỏng · phá huỷ khó đảo ngược · đầu vào chỉ user có · QC chạm trần 3 |
| 7 | Cổng spec? | `approve spec` từ chối khi R14 đỏ |
| 8 | Mức QC? | `full` |
