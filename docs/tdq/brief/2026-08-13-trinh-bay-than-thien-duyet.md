# BRIEF — Trình bày thân thiện ở hai cổng duyệt spec/plan

## Nguyên văn

Yêu cầu user (2026-08-13 19:28), kèm 2 ảnh màn hình khối trình spec và khối trình plan:

> hướng dẫn người dùng: "có thể làm nổi bật hơn để người dùng để ý" trên là spec của
> request anh đưa ra, mời anh/chị xem xét, nếu muốn xem cụ thể thì xem file <> và nếu
> duyệt vui lòng trả lời duyệt spec để tôi có thể tiếp tục triển khai và ở hình 2 ở đây
> cũng sẽ thông báo là tôi đã viết xong plan để thực hiện yêu cầu của anh/chị: nội dung
> plan có <> mời anh chị xem và review plan ở <>, nếu duyệt thì vui lòng nhắn "duyệt plan"
> và sau khi duyệt plan mới hỏi mode implement ở turn sau nhưng trình bày dễ hiểu thân
> thiện với end user hãy mở request để xử lí

### Cách hiểu đầu tiên

**Mục tiêu.** Hai khối chat ở cổng duyệt (spec và plan) hiện đang viết cho người trong
nghề: dày thuật ngữ, dòng `➤ Duyệt:` nằm lẫn giữa nội dung, người dùng cuối khó nhận ra
mình đang được hỏi gì và phải trả lời thế nào. Cần viết lại cho thân thiện, có câu dẫn
rõ ràng và làm nổi bật lời mời duyệt.

**Phạm vi đoán.**

- Khối trình spec (`tdq-spec` bước 4): thêm câu dẫn kiểu "trên là spec của yêu cầu
  anh/chị, mời xem xét; muốn xem chi tiết thì mở file `<đường dẫn>`; nếu duyệt vui lòng
  trả lời `duyệt spec` để tôi tiếp tục triển khai".
- Khối trình plan (`tdq-plan` bước 5): thêm câu dẫn kiểu "tôi đã viết xong plan để thực
  hiện yêu cầu của anh/chị; nội dung gồm `<tóm tắt>`; mời xem và review đầy đủ ở
  `<đường dẫn>`; nếu duyệt vui lòng nhắn `duyệt plan`".
- **Tách cổng mode**: hiện dòng duyệt plan bắt user nói luôn mode
  (`duyệt plan mode main`). Yêu cầu mới là user chỉ cần nhắn `duyệt plan`, rồi TURN SAU
  mới hỏi mode thực thi. Đây là thay đổi luồng, không chỉ là câu chữ.
- Làm nổi bật lời mời duyệt để user không lướt qua.

**Chỗ chưa rõ.**

1. "Nổi bật hơn" bằng cách nào — khung, emoji, in đậm, tách đoạn riêng? Chưa rõ mức độ.
2. Tách cổng mode ra turn sau làm mất luật "duyệt plan xong build ngay trong cùng turn".
   Cần chốt luồng mới: duyệt plan → hỏi mode (dừng) → user chọn mode → build.
3. Xưng hô "anh/chị" cố định hay trung tính hơn?
4. Có áp cùng kiểu trình bày cho cổng duyệt của chế độ nhanh (`duyệt nhanh`) không?

## Hiểu & kiến thức

### Năng lực dùng được

`skill_inventory.py` liệt kê 285 skill. Phán quyết theo nhóm:

| Skill | DÙNG / KHÔNG | Vì sao |
|---|---|---|
| `tdq-conventions` | NỀN | Chứa §1 giao thức turn và §4 ghi nhận duyệt — nơi luật duyệt sống. |
| `tdq-spec`, `tdq-plan` | NỀN | Bước 4/bước 5 của hai file này chính là hai khối phải sửa. |
| `tdq-build`, `tdq-intake` | NỀN | Chứa luật gộp gate và cổng duyệt chế độ nhanh, có thể bị kéo theo. |
| 279 skill còn lại (Unity, Figma, cloud, media…) | KHÔNG | Việc này thuần sửa văn bản skill + hook nội bộ, không chạm sản phẩm nào khác. |

### Bản đồ code liên quan

- `skills/tdq-spec/SKILL.md` bước 4 — khối trình spec + dòng `➤ Duyệt:`.
- `skills/tdq-plan/SKILL.md` bước 5 và bước 6 — khối trình plan, dòng `➤ Duyệt:`,
  luật "user duyệt mà không nói mode → HỎI".
- `hooks/scripts/_common.py` `APPROVE_HINTS` — nguồn duy nhất sinh câu gợi ý duyệt mà
  hook `prompt_context.py` in ra. Khoá `plan` đang là
  `nhắn "duyệt plan mode {mode}" (đổi được: main|subagent)`.
- `skills/tdq-conventions/references/approval.md` — đã có sẵn luật `approve plan` thiếu
  mode thì HỎI mode trước. Nghĩa là luồng 2 bước KHÔNG hoàn toàn mới, chỉ chưa phải mặc định.
- `tests/test_gate_merge.py` bất biến 1 — CẤM chuỗi "turn mới"/"turn tiếp theo" xuất hiện
  trong `tdq-spec`, `tdq-plan`, `tdq-build`, `tdq-intake`. Đây là rào cản trực tiếp với
  yêu cầu "hỏi mode ở turn sau".
- `tests/test_context_hooks.py` dòng 152–182 — khẳng định cứng chuỗi gợi ý
  `duyệt plan mode main|subagent`. Đổi `APPROVE_HINTS` là phải sửa test này.
- `~/.claude/CLAUDE.md` §6 — "duyệt plan kèm mode (main | subagent) → build ngay turn đó".
  Luật cá nhân của user, mâu thuẫn với luồng 2 bước nếu không sửa kèm.

### Research

BỎ. Việc thuần nội bộ: chỉ đụng văn bản skill, hằng chuỗi trong hook và test của chính
repo này. Không có ẩn số về thư viện, API hay phiên bản bên ngoài.

## Hỏi đáp

### Vòng 1 (2026-08-13 19:31)

1. Luồng duyệt plan → mode: 2 bước có điều kiện / 2 bước cứng / giữ 1 bước.
2. Mức làm nổi bật khối duyệt: khối riêng có đường kẻ / thêm emoji / chỉ thêm câu dẫn.
3. Xưng hô với người dùng cuối: "bạn" hay "anh/chị".
4. Phạm vi: có áp cho cả cổng duyệt của chế độ nhanh không.

**Trả lời (19:35):** *"1 B nên tách ra duyệt plan xong mới qua phase hỏi mode và khi chọn
mode xong sẽ implement; 2A: 3A; 4A"*

- **Chốt 1 = B (2 bước cứng).** Duyệt plan xong sang bước hỏi mode; chọn mode xong mới
  implement. Kéo theo: phải sửa bất biến `test_gate_merge.py` và `CLAUDE.md` §6.
- **Chốt 2 = A.** Khối duyệt tách riêng cuối tin nhắn, có đường kẻ ngăn + tiêu đề in đậm,
  KHÔNG emoji.
- **Chốt 3 = A.** Xưng hô "bạn".
- **Chốt 4 = A.** Áp cho cả 3 cổng: spec, plan, chế độ nhanh.

### Vòng 2 (2026-08-13 19:36)

1. "Phase hỏi mode" là phase THẬT trong `PHASE_TABLE` hay chỉ là một bước trong phase `plan`.
2. Khi user tự nói mode ngay trong câu duyệt plan thì vẫn hỏi lại hay đi thẳng.

**Trả lời (19:38):** *"1A 2A và ở bước hỏi mode cần giải thích sơ bộ 2 mode và apply
hướng dẫn và xử lí ở mọi phase giao tiếp để UX thân thiện với người dùng"*

- **Chốt 1 = A.** Thêm phase THẬT tên `mode` vào `PHASE_TABLE`, nằm giữa `plan` và `implement`.
- **Chốt 2 = A.** User tự nói mode trong câu duyệt → ghi nhận cả hai, bỏ qua phase `mode`,
  vào implement luôn.
- **Bổ sung 1.** Khối hỏi mode phải giải thích sơ bộ hai mode `main` và `subagent` bằng
  lời dễ hiểu, không bắt user tự tra nghĩa.
- **Bổ sung 2.** Khuôn trình bày thân thiện áp cho **mọi chỗ giao tiếp với user**, không
  riêng 3 cổng duyệt: câu hỏi chọn pipeline, các vòng interview, cổng spec, cổng plan,
  cổng mode, cổng chế độ nhanh, và câu hỏi commit cuối request.

### Vòng 3

Không còn câu hỏi nào làm đổi kết quả. Kết thúc interview.

### Chốt thiết kế

1. **Phase `mode` mới** trong `PHASE_TABLE`: vào khi `plan_approved = true` mà
   `implement_mode` chưa chốt · việc duy nhất là giải thích + hỏi mode · lệnh chuyển tiếp
   `approve plan --mode <main|subagent>` · cấm sửa code và cấm tự chọn thay user.
   Phase `plan` đổi lệnh chuyển tiếp thành `approve plan --by "<nguyên văn>"` (không mode)
   rồi `set phase=mode`.
2. **`approve plan` thiếu `--mode` là hợp lệ**, không còn là trường hợp bất thường.
3. **Một khuôn khối user-facing dùng chung** đặt trong `tdq-conventions`: đường kẻ ngăn,
   tiêu đề in đậm, câu dẫn xưng "bạn", đường dẫn file đầy đủ, dòng `➤` cuối cùng. Không emoji.
4. **`APPROVE_HINTS`** trong `_common.py`: khoá `plan` bỏ phần mode; thêm khoá `mode`.
5. **Nới bất biến `test_gate_merge.py`**: vẫn cấm bắt user chờ thêm turn ở chặng
   spec → plan và chặng mode → build; riêng chặng plan → mode thì được phép, vì đó chính
   là thứ user vừa chốt.
6. **Đồng bộ tài liệu kéo theo**: `references/phases.md` (tự sinh, 2 bản),
   `portable/workflow/*`, `docs/claude-md-mau.md`, và `~/.claude/CLAUDE.md` §6 của user
   (file ngoài repo, không track git — sẽ nêu rõ trong spec để user duyệt cùng).

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Research web | BỎ | Thuần nội bộ, không có ẩn số thư viện/API bên ngoài. |
| Interview | XONG | 2 vòng, đã hết câu hỏi làm đổi kết quả. |
| Spec + plan | CÓ | Khung bất biến. |
| Implement | CÓ | Đụng `PHASE_TABLE`, hook, nhiều file skill và tài liệu tự sinh. |
| QC theo DoD | CÓ | Khung bất biến; có sửa hằng máy đọc nên phải chạy full suite. |
| Agent `tdq-qc-tester` | BỎ | DoD kiểm được hết bằng lệnh, không có vùng mờ cần người kiểm độc lập. |
| Chia subagent | BỎ | Các task đụng chung `tdq_state.py`, `_common.py` và phụ thuộc chặt. |
| Report | CÓ | Khung bất biến. |
