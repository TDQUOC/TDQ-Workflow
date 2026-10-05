# Hồ sơ kiến trúc — TDQ Workflow

Trạng thái: **NHÁP — chờ user chốt** (sinh 2026-08-15 trong phase analyze của request
`2026-08-15-toi-uu-thoi-gian-phase`). Chưa chốt thì mọi dòng ở đây là gợi ý, không phải luật.

Nguồn sinh: cây thư mục repo · `graphify god-nodes` · `.graphifyignore`.

## Tầng

| Tầng | Thư mục | Trách nhiệm |
|---|---|---|
| Luật | `skills/` | văn bản chỉ dẫn model; không chạy được, không có trạng thái |
| Adapter | `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/`, `.opencode/plugins/` | khai cho từng host đường tới `skills/` dùng chung — không chép nội dung; Antigravity không đọc thẳng repo nên layout của nó SINH tại máy người dùng bằng `scripts/build_portable.py --sinh-agy` |
| CLI | `scripts/` | mọi hành vi chạy được: state, kết turn, lint, quét rule, đo token |
| Hook | `hooks/scripts/` | 6 hook trên 5 sự kiện cắm vào Claude Code, nhắc mã `[TDQ:*]` và chặn khi thiếu bằng chứng |
| Test | `tests/` | khoá hành vi của tầng CLI, tầng hook và tính nhất quán của tầng luật |
| Dữ liệu request | `docs/tdq/` | brief, spec, plan, qc, report, state — dữ liệu, không phải code |

## Luật gọi

- `hooks/` được gọi `scripts/`; `scripts/` **không** được import `hooks/` — hook chạy trong
  tiến trình của Claude Code, kéo ngược sẽ buộc CLI phụ thuộc môi trường hook.
- `skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill —
  hai bản chép tay sẽ lệch nhau và không có phép kiểm nào bắt được.
- Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`; mọi nơi khác chỉ đọc qua CLI.
- File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/` — thư mục khác bị
  `.graphifyignore` loại nên đồ thị không thấy. Ngoại lệ duy nhất: adapter của host (xem mục
  `Đã chốt`, 2026-09-21), vì đường dẫn do host quy định chứ không do repo chọn.
- `tests/` gọi được vào mọi tầng; không tầng nào được import `tests/`.

## Hub

5 node nhiều liên kết nhất (`graphify god-nodes`) — sửa các node này là rủi ro cao, phải
khai ở dòng `Chạm:` của plan:

| # | Node | Số bậc |
|---|---|---|
| 1 | `Changelog` | 28 |
| 2 | `main()` | 20 |
| 3 | `cli()` | 17 |
| 4 | `log()` | 17 |
| 5 | `cmd_build()` | 17 |

## Đã chốt

- 2026-07-29: gom 10 skill còn 6; bỏ hẳn skill duyệt, duyệt bằng chat thường.
- 2026-07-29: hook chỉ nhắc và kiểm bằng hiệu ứng thật, không trả `deny` vì lý do "chưa duyệt".
- 2026-08-13: `CHANGELOG.md` giữ dưới trần 500 dòng của `doc_lint` R6; phần cũ xoay vào
  `docs/archive/CHANGELOG-*.md`.
- 2026-08-14: `skills/tdq-conventions/references/soul.md` là luật gốc đứng trên mọi luật;
  đổi soul phải có user duyệt.
- 2026-08-22: ngôn ngữ chia 3 tầng — luật trong `skills/`, `agents/`, chú thích/docstring
  của `hooks/` + `scripts/` và chuỗi máy in ra đều viết TIẾNG ANH cố định (không bảng
  tra i18n); tài liệu sinh cho user và lời thoại viết theo `doc_lang` khai một lần lúc
  `init`, mặc định `vi`, cố định suốt request. `scripts/i18n_check.py` gác tầng 1-2,
  cụm `i18n-allow` là cửa miễn cho chuỗi user thấy giữ nguyên từng chữ.
- 2026-09-17: nội hoá luật "build less than asked" — thân luật ở
  `skills/tdq-build/references/rules/chung.md`, đọc–lọc bằng `hooks/scripts/luat_gon.py` theo
  `muc_gat` (`off/lite/full/ultra`, mặc định `full`). Ba kênh bơm: `SessionStart` và
  `SubagentStart` mang thân luật, `UserPromptSubmit` chỉ một dòng con trỏ ở phase `implement`.
  Thêm mã thứ sáu `TDQ:GON`; đây là lời nhắc chứ không phải hàng rào (issue #23885:
  `additionalContext` của sub-agent bị prune).
- 2026-09-21: bỏ mô hình chép — ba bundle dựng sẵn trong repo, mỗi host một bản sao — học theo
  cách superpowers tổ chức: một nguồn `skills/`, mỗi host một adapter mỏng. Đường dẫn adapter do host quy định — `.codex-plugin/`, `.agents/plugins/`,
  `.opencode/plugins/` — nên đây là ngoại lệ của luật "code mới chỉ nằm trong `scripts/` hoặc
  `hooks/`". Adapter OpenCode là JavaScript thuần, không package npm, bọc try/catch mọi bước.
- 2026-10-03 (yêu cầu 1907): **trọn bộ test chỉ chạy ở 2 cổng.** QC-F1 (thay lần chạy riêng "xong
  mọi task", vì code không đổi giữa hai lần) và một lần sau vòng sửa QC CUỐI khi có sửa. Giữa các
  bước, `scripts/tdq_test.py vung-cham` chạy vùng chạm cộng bán kính do máy tính: nhắc tên/đường dẫn,
  import bắc cầu đọc bằng AST, test quét thư mục cha. Rơi về trọn bộ khi bán kính ≥ 60% số module test
  hoặc có file sửa ngoài `scripts/ hooks/ skills/ tests/ agents/` — không chắc thì chạy hết (soul:
  chất lượng > thời gian chạy). `scripts/` chỉ đọc nguồn `hooks/scripts/` bằng AST, không import —
  luật import 2026-07 vẫn đứng. Sổ bỏ sót: module QC-F1 đỏ mà `vung-cham` chưa từng chọn trong request
  bị ghi và báo, nên bán kính được đo chứ không được tin. `next` chỉ NHẮC khi trọn bộ chạy quá ngân
  sách cổng — không hook nào chặn (user chọn; dòng 2026-07-29 vẫn đứng). Đo gốc: 59 lần trọn bộ qua
  8 request (TB 7,4), hai request gần nhất đã 2–3; sửa hub (`tdq_state.py`) chạm ~96–98/127 module
  nên ở đó trọn bộ là đúng, sửa file lá/file luật chạm ~7–17 module.
- 2026-10-03 (yêu cầu 0732): **đo trước ở spec, không dừng giữa chừng vì ngưỡng.** Lệnh
  `approve spec` TỪ CHỐI khi luật R14 của `doc_lint` đỏ — mọi ngưỡng số ở §6 của spec mới phải có
  `Đo trước` và `Dự phòng nếu trượt`. Cổng nằm ở LỆNH duyệt, không ở hook, nên dòng 2026-07-29
  ("không hook nào chặn vì chưa duyệt") vẫn đứng; và nó không tái tạo bế tắc 0.2.0 vì spec cũ
  im lặng và user luôn có `--bo-qua-do "<lý do>"`. Ngoại lệ dừng thu về 4 loại khai bằng
  `pause --loai` (mat-truy-cap · pha-huy · dau-vao-user · tran-qc); ngưỡng trượt lúc chạy thì
  `lech add` rồi làm tiếp, report hỏi duyệt. Hook `ask_gate.py` (`TDQ:ASK`) chỉ NHẮC khi gọi
  `AskUserQuestion` ở implement/qc — user chọn không chặn — và không trả `permissionDecision`.
  Ca gốc: một phiên excalidraw dừng giữa implement để hỏi nâng ngưỡng installer 200 → 250 MB.
- 2026-10-03: **thêm một điểm chặn** (cạnh nhật ký ở `Stop` và `TDQ:TICK`/`TDQ:TEAM` của
  `edit_gate`) — `hooks/scripts/search_gate.py` trả `deny` (mã
  `TDQ:SEARCH`) cho một lần tìm code đi tắt tầng khái niệm. Dòng 2026-07-29 vẫn đứng: không hook
  nào chặn vì lý do "chưa duyệt"; đây là lý do KHÁC. Ba luật xét theo thứ tự: (1) miễn cho lọc danh
  sách file và cho tên có nguyên văn trong prompt của user; (2) request chưa gọi lumen/LSP/graphify
  lần nào → chặn; (3) quá N lần tìm kể từ lần gọi gần nhất mà mẫu có hình đoán mò → chặn. Cổng
  KHÔNG chặn khi tầng khái niệm chưa dựng xong — chặn mà không có đường đúng để đi là kẹt. Lý do
  phải chặn chứ không nhắc: user yêu cầu "buộc phải tuân theo", và `PreToolUse` của Codex chỉ có
  `deny`. Đo trên phiên thật 2026-10-02: ~20 lần tìm qua 4 request, 0 lumen, 0 LSP.
- 2026-09-23: mức QC là quyết định của USER, không phải suy luận của agent. Khoá `muc_qc`
  (`lite|full|ultra|off`, mặc định `full`, fail-closed) được hỏi ở cuối phase `analyze` — trước
  khi viết spec §6 — và tại cổng duyệt của lane express. Bảng "mức nào chạy loại kiểm nào" có
  đúng một bản, ở `skills/tdq-build/references/qc.md`. Mức `off` tồn tại nhưng KHÔNG bao giờ
  được bày ra trong danh sách lựa chọn. Cờ `--no-qc` của `approve quick` bị gỡ cùng ngày: một
  cơ chế duy nhất cho cả hai lane.
