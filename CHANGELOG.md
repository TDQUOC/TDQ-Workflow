# Changelog

Mới nhất trên cùng. Ngày theo múi giờ máy phát hành.

## 0.22.0 — 2026-08-16

Clean code thôi làm cổng hỏi, thành luật thường trực. Trước bản này mỗi request chạm mã
nguồn phải trả lời "Bật clean code cho request này chứ?", rồi cuối request chạy
`scripts/code_rule_scan.py`. Cổng đó tốn một lượt hỏi mà không trả lại bảo đảm nào:
script phụ thuộc linter cài sẵn trên máy, request trước vừa báo `CHƯA KIỂM ĐƯỢC — thiếu
ruff` cho cả 5 file Python.

- Luật mới `skills/tdq-conventions/references/clean-code.md`: 5 nguyên tắc SOLID, mỗi
  nguyên tắc hai bản đọc (khi có class / khi chỉ có hàm và module) vì repo này có 4 class
  trên 280 hàm. LSP mang nhãn giới hạn: bản đọc cho hàm là suy diễn, không phải trích
  Liskov. Mỗi nguyên tắc kèm một ví dụ ĐÚNG và một ví dụ SAI trỏ vào file thật.
- `tdq-conventions/SKILL.md` §11 nạp luật này mỗi turn; trần dòng của skill nới 130 → 133.
- Gỡ cổng hỏi: `tdq-spec/SKILL.md` bỏ bước 1b, `spec-template.md` bỏ dòng
  `Clean code: BẬT|TẮT` và mục `## Khuôn hỏi clean code`.
- QC: hạng mục cố định thứ tư QC-F4 — trả lời checklist 5 câu có/không, câu nào "không"
  thì sửa code rồi ghi chỗ đã sửa. Đổi khớp ở cả `skills/` và `portable/`.
- Xoá `scripts/code_rule_scan.py`, `tests/test_code_rule_scan.py`,
  `tests/test_clean_code_workflow.py` (graphify xác nhận script là lá, không ai gọi).
- Bù kiểm bằng lệnh: `doc_lint` R9 phủ thêm `clean-code.md`, và
  `tests/test_clean_code_rule.py` (20 test) khoá hình dạng file luật.

## 0.21.0 — 2026-08-16

Skill thứ bảy: `tdq-check-status` — dò lại một request đang dở rồi tiếp tục mà không mất
dữ liệu cũ. Trước bản này, mất ngữ cảnh là mất luôn chỗ dừng: `tdq-status` chỉ đọc lại
`state.json`, mà `state.json` chính là thứ có thể sai. Ba tình huống đã gặp: session chết
phải mở session mới, đổi sang máy khác, và giao một phase cho agent ngoài rồi quay lại.

- Nguyên tắc mới: **đĩa là bằng chứng, `state.json` là lời khai**. Bộ dò đọc
  `docs/tdq/**`, git (`log -20`, `status --short`) và working log hôm nay, rồi đối chiếu
  với state. Lệch nhau thì tin đĩa.
- `scripts/tdq_checkstatus.py report [--json]`: chỉ ĐỌC, không bao giờ ghi `state.json`.
  Nó chấm 11 ca lệch D1–D11 theo một bảng cứng, không để model tự nghĩ chẩn đoán.
- Ba mức kết luận: `TIẾP TỤC ĐƯỢC` · `VÁ RỒI TIẾP TỤC` · `CẦN USER QUYẾT`.
- **Luật không mất dữ liệu.** Lệnh vá chỉ thuộc hai họ `tdq_state.py set …` và
  `tdq_state.py approve …`. Một hàm chặn nội bộ ném lỗi nếu mẫu lệnh chạm tới lệnh khởi
  tạo lại, lệnh đặt về mặc định, `rm`, `mv` hay chuyển hướng ghi đè.
- Một cổng gật duy nhất: trình báo cáo → user gật một lần → chạy hết lệnh vá → đi tiếp.
- `skills/tdq-check-status/` có 7 bước, khuôn báo cáo 6 mục và bảng D1–D11; bản
  `portable/workflow/05-check-status.md` khớp từng bước cho agent ngoài Claude Code.
- `tdq-status` giữ nguyên vai trò báo nhanh, chỉ thêm một dòng trỏ sang skill mới.
- Trần tổng `description` của skill nới 900 → 1080 ký tự cho skill thứ bảy.

## 0.20.0 — 2026-08-15

Tên file document mang thêm giờ phút, và workflow tự đếm thời gian: mỗi request tốn bao
lâu, mỗi phase tốn bao lâu. Trước bản này `state.json` chỉ có `updated_at` và ba mốc duyệt
— không suy ra được phase nào ngốn thời gian, nên mọi nhận định về "chậm ở đâu" đều là đoán.

- Slug mới: `YYYY-MM-DD-HHMM-<kebab ≤5 từ, không dấu>`, giờ chèn sau ngày để sort tên trùng
  sort thời gian. **Hai định dạng cùng sống.** Slug cũ chỉ có ngày vẫn ĐỌC được, nên 269
  file tài liệu cũ giữ nguyên tên. Nhưng `tdq_state.py init` TỪ CHỐI slug ghi mới thiếu giờ
  phút: cảnh báo suông thì chuẩn mới sẽ trôi ngay lần đầu ai đó bỏ qua.
- `scripts/tdq_state.py`: thêm `parse_slug()` (trả `(ngày, giờ-phút hoặc None, phần chữ)`),
  `schema_version` lên 4 với hai trường mới `started_at` và `phase_history`. Mỗi lần ĐỔI
  phase ghi một mốc; set lại đúng phase đang đứng thì không ghi (tránh mốc 0 giây), quay
  lại phase cũ thì ghi mốc mới — đó là cơ sở đếm "số lần vào".
- `scripts/tdq_timing.py` (mới): `show` in bảng Phase · Treo tường · Model chạy · Số lần
  vào; `status` in một dòng đồng hồ cho `tdq-status`; `close` append đúng một dòng JSON vào
  `docs/tdq/timing.jsonl`. Hai cột cố ý khác nguồn: treo tường lấy từ mốc state (gồm cả
  thời gian chờ user duyệt), model chạy cộng khoảng cách giữa các bước model trong
  transcript và bỏ khoảng > `MAX_GAP_SECONDS` (tái dùng ngưỡng của `step_audit.py`).
  Không đọc được transcript thì cột model in `—` kèm lý do, vẫn thoát 0.
- Đóng sổ tự động ở hai cửa: `init` chốt sổ request cũ TRƯỚC khi reset state (không thì mốc
  của request bỏ dở bay mất), và `tdq_finish.py --phase idle` chốt sổ khi hết request. Đóng
  sổ hai lần cho cùng một request không đẻ dòng thứ hai.
- Khuôn report bắt buộc có mục `## Thời gian`; `skills/tdq-status/SKILL.md` in thêm dòng
  `⏱` của phase đang chạy. Công thức slug đã đồng bộ ở `skills/`, `scripts/`, `portable/`.

## 0.19.0 — 2026-08-15

Cắt thời gian xử lý một request mà không đụng vào luật hay chất lượng đầu ra. Nguyên nhân
đo được: tổng thời gian tỉ lệ thẳng với SỐ BƯỚC (mỗi tool call ≈ một round-trip 3–4 s),
context chỉ ảnh hưởng nhẹ; luật gộp tool call đã có nhưng nằm trong file reference ít nạp
và bị đóng khung là "tiết kiệm context" — tầng thấp nhất của soul, nên bỏ qua vẫn hợp lệ.

- `skills/tdq-conventions/SKILL.md` §10 đổi thành "Luật một lượt (tầng 2 — runtime)":
  luật gộp chuyển hẳn vào thân skill (nạp mỗi turn) theo khuôn ba mục. Trần dòng của
  skill này nới 120 → 130 — trần dòng là ràng buộc tầng 3, không được nén luật tầng 2.
- `references/context-budget.md` tách hai phần rõ ràng: chi phí bước (tầng 2) và chi phí
  context (tầng 3). Thêm bảng **Cấm gộp** 4 ca (bước đỏ→xanh của TDD, đang khoanh vùng
  lỗi, lệnh phá hủy, lệnh sau cần kết quả lệnh trước). Sáu luật cũ giữ nguyên văn.
- Luật đọc lại file là luật **MỀM**: còn nhớ đủ thì đừng đọc lại. Nhưng có 5 ca BẮT BUỘC
  đọc lại: context bị nén, lần trước đọc một phần, file có thể đã đổi, sắp sửa chính file
  đó, nhớ không chắc. Nghi ngờ thì đọc lại — không đổi chất lượng lấy tốc độ.
- `references/soul.md` thêm mục "Xếp luật vào tầng nào": luật đổi số bước → tầng runtime,
  đổi số token → tầng context cost, đổi đúng-sai đầu ra → tầng chất lượng. Ba tầng gốc
  giữ nguyên văn. Bản `portable/AGENTS.md` có luật một lượt tương đương.
- `scripts/step_audit.py` (mới): đo 5 chỉ số chi phí bước, gom theo `requestId` — đếm theo
  bản ghi jsonl thổi phồng số bước và luôn ra 1,00 tool call mỗi lượt. `token_audit.py`
  sửa lỗi suy đường dẫn: tên project có gạch dưới cũng đổi thành `-`.
- Test: 596 → 608 (`tests/test_step_budget.py` mới, 12 test).

## 0.18.0 — 2026-08-14

Set "soul" cho bộ workflow: chất lượng code agent > runtime > context cost. Ba tầng ưu
tiên này thành luật gốc, mọi khuôn tài liệu khai nó ra, và luật cũ được rà lại theo nó.
Kèm theo là thư viện rule ngôn ngữ để model yếu cũng viết code sạch, cùng năm cơ chế
chặn nợ kiến trúc do quick-fix.

- `skills/tdq-conventions/references/soul.md` (mới): ba tầng ưu tiên kèm luật phân xử khi
  hai tầng đụng nhau. Skill nền và bản portable trỏ về đây, mỗi file đúng một dòng.
- Rà 28 file luật theo soul, biên bản ở `docs/tdq/knowledge/2026-08-14-ra-soat-luat-theo-soul.md`.
  Hai chỗ SỬA: khoá cứng phạm vi QC trong `qc.md`, và ngưỡng context trong `context-budget.md`.
- `skills/tdq-build/references/rules/` (mới, 10 file): chỉ mục + 7 file ngôn ngữ, mỗi file
  cùng một khuôn (Intentionality, mùi code, công cụ lint, nguồn chính thức có URL thật).
- `scripts/code_rule_scan.py` (mới): quét file đã đổi theo bảng rule, ba trạng thái PASS /
  LỖI / CHƯA KIỂM ĐƯỢC — thiếu công cụ lint thì báo đúng trạng thái, không PASS khống.
  Log stderr có timestamp, tắt bằng `--im`, chi tiết bằng `--chi-tiet`. Không tự cài gói.
- Cổng clean code ở phase spec: việc chạm mã nguồn thì hỏi user BẬT/TẮT, đáp án ghi vào
  spec §4. TẮT vẫn tổ chức code theo rule ngôn ngữ, chỉ bỏ bước scan cuối request.
- Năm cơ chế chống nợ kiến trúc: M1 hồ sơ `docs/kien-truc.md` sinh một lần mỗi project ·
  M2 khối "Ràng buộc kiến trúc phải giữ" trong spec §5 · M3 luật "Tìm rồi mới tạo" ở bước
  code · M4 dòng `Chạm:` trong plan lấy từ `graphify affected` · M5 ba hạng mục QC cố định
  QC-F1→F3, đồng bộ nguyên văn giữa bản skill và bản portable.
- Năm khuôn tài liệu (brief, spec, plan, qc, report) đều có dòng Soul.
- Test: 574 → 596 (306 subtest). Nghiệm thu thật bằng agent Haiku đọc rule soát file mẫu
  5 lỗi cố ý — nêu đúng 5/5, không hỏi lại câu nào.

## 0.17.0 — 2026-08-14

Trang trí khối chat cuối trả lời user: dùng markdown mà cả ba mặt (terminal, app,
extension) đều dựng được, tách nhãn khỏi nội dung, và chốt bằng test thay vì bằng trí nhớ.
Màu và cỡ chữ không làm được — ba mặt không dùng chung bộ dựng, mẫu số chung là markdown
terminal dựng được. Nguyên tắc xuyên suốt: **chỉ thêm dấu đánh dấu, không đổi một từ nào**
của nội dung đang chạy.

- `skills/tdq-conventions/references/user-facing-block.md`: viết lại. Thêm bảng 5 thành
  phần kèm cấu trúc trình bày dùng cho từng thành phần, mục `## Bảy luật trang trí`, bảng
  6 ký hiệu ngoài ASCII được phép, và ví dụ đối chiếu `### Trước` / `### Sau`.
- Luật cấm emoji giữ nguyên; chỗ nới đúng một điểm là ký hiệu Unicode, giới hạn trong sáu
  ký tự `➤ · — → – …`. Cả sáu đều có bằng chứng đang in ra cho user trong kho. Ký tự `▸`
  bị loại vì grep toàn kho ra 0 kết quả. Ký tự kẻ khung bị cấm vì đòi canh cột.
- Trang trí khối mẫu trong 8 file skill và 3 file bản portable: nhãn trường in đậm với dấu
  hai chấm nằm TRONG cặp sao, đường dẫn và tên lệnh bọc nháy ngược. Năm chỗ mã sinh chuỗi
  giữ nguyên từng byte để hook và test cũ không lệch.
- `skills/tdq-status/SKILL.md`: bỏ `✔` và `⏳` ở dòng báo trạng thái duyệt, thay bằng chữ
  in đậm. Đây là chỗ duy nhất trong kho còn dạy Claude in emoji ra cho user.
- `scripts/scan_block_symbols.py` (mới): quét ký tự Unicode loại `P*`/`S*` ngoài ASCII
  trong 12 file phạm vi, có chế độ `--chi-khoi` chỉ quét nội dung khối in cho user.
- `tests/test_user_facing_block.py`: 4 → 10 test (58 subtest). Thêm phép kiểm whitelist ký
  hiệu, phép kiểm khối mẫu theo luật 1/3/7, phép kiểm chuỗi do mã sinh, phép kiểm bản
  portable khớp khuôn gốc, và bảng `SO_KHOI` chặn trường hợp phép kiểm chạy rỗng mà vẫn
  xanh. Toàn bộ suite: 569 → 574 test.

## 0.16.0 — 2026-08-14

Cắt chi phí context của chính workflow mà không bỏ một luật nào: đếm mệnh lệnh theo 10
cụm file cho **7 cụm tăng · 3 cụm giữ nguyên · 0 cụm giảm**. Nguyên tắc áp dụng xuyên
suốt: dời văn bản xuống tầng `đọc khi cần` và để lại dòng trỏ có chữ BẮT BUỘC, tuyệt đối
không xoá luật.

- `scripts/skill_inventory.py`: thêm `--loc <từ khoá>` và `--tat-ca`. Bản lọc CẤM ẩn skill
  nguồn `project` và `plugin:tdq-workflow` (hai nguồn quyết định phán quyết DÙNG ở bước
  B0), và luôn in dòng cuối báo đã ẩn bao nhiêu kèm lệnh xem đủ. Chạy không cờ giữ nguyên
  từng byte. Bước B0 dùng `--loc`: **39.722 → 1.845 byte** mỗi lần chạy (≈ −9.300 token).
- `skills/tdq-intake/SKILL.md`: nhánh chế độ nhanh dời sang
  `references/quick-lane.md`, đánh số lại thành 12 bước. Thân 1.844 → 1.288 token.
- `skills/tdq-build/SKILL.md`: Phần B (QC) và Phần C (Report) dời xuống `references/qc.md`
  và `references/report-template.md`. Thân 1.936 → 1.536 token.
- `skills/tdq-conventions/`: phần nền/giải thích của 3 file gom vào mục `## Phụ lục`,
  **giữ nguyên 100% câu chữ** (diff theo từ: 0 từ bị mất).
- `skills/tdq-intake/references/scope-round.md`: khử 2 từ mơ hồ thành điều kiện đo được.
- 8 chỗ cố ý chép lại luật giữa các file nay có nhãn "nhắc lại có chủ ý" — chống việc
  lần sau bị nhầm là trùng lặp rồi xoá đi.
- `agents/tdq-implementer.md`, `tdq-qc-tester.md`, `tdq-reviewer.md`: thêm khối
  "Return format — copy this shape exactly".
- Tổng tầng `nạp khi gọi skill` **8.473 → 7.579 token** (−10,6%). Test 563 → 569 passed,
  0 failed. QC 15 hạng mục, Q1–Q14 PASS; một lượt QC độc lập bằng agent `tdq-qc-tester`
  chạy lại từ đầu cho cùng phán quyết. Model hạng thấp chạy thử: không bỏ bước nào.
- Chưa đụng `hooks/` và `portable/` — bản portable chưa nhận các thay đổi này.

## 0.15.1 — 2026-08-14

Bản tài liệu: đề xuất cơ chế chống quick-fix phá kiến trúc. Chưa đụng file thực thi nào
trong `skills/`, `scripts/`, `hooks/` — việc áp cơ chế vào workflow là request riêng.

- `docs/tdq/knowledge/2026-08-14-chong-no-ky-thuat.md` (mới): 4 khoảng trống đo được của
  workflow hiện tại, kèm bằng chứng `file:line`. Cộng 6 cơ chế M1–M6; mỗi cơ chế có
  nguyên văn dòng luật copy dán được, chỗ chèn `file:mục`, mức chi phí A/B, một lệnh kiểm.
- M1 hồ sơ kiến trúc mỗi project · M2 ô "Ràng buộc kiến trúc phải giữ" trong spec §5 ·
  M3 luật "tìm rồi mới tạo" thay dòng implement cũ · M4 khai `Chạm:` bằng
  `graphify affected` trong plan · M5 ba hạng mục QC cố định chống hồi quy (nới luật "số
  hạng mục QC = số dòng DoD") · M6 cổng trùng lặp `jscpd` (mức B, tuỳ chọn).
- Ba gói cộng dồn theo chi phí, khuyến nghị **Gói vừa** (M1–M5, toàn mức A, không script,
  không cổng duyệt mới). Kèm bản rút gọn cho pipeline express và phần tách rõ chỗ nào
  độc lập ngôn ngữ khi áp cho project khác (Unity, game).
- Số liệu lấy từ chạy thật: `grep` trên 1.844 dòng skill, `graphify god-nodes`,
  `graphify affected "payload_cwd"`, `jscpd` 5.0.15 (72 cặp trùng, 1.82% token, exit 0).

## 0.15.0 — 2026-08-14

Interview đi hai tầng: hỏi phạm vi tổng quát trước, rồi mới hỏi chi tiết trong đúng
những mặt user chọn — để spec không bao thiếu cũng không bao dư.

- `skills/tdq-intake/references/scope-round.md` (mới, 5 mục): khi nào chạy · câu 1 chọn
  mặt · câu 2 bối cảnh bằng số · suy mức đầu tư · ghi lại. Vòng scope chạy **có điều
  kiện** theo danh sách đóng 4 dấu hiệu kích hoạt; bỏ thì buộc ghi một dòng
  `Vòng scope: BỎ — <lý do>` vào brief. Áp cho cả lane express lẫn deep.
- Câu 1 chỉ trình 3–5 mặt hợp lĩnh vực của request, soát nội bộ theo khung 9 mặt
  ISO/IEC 25010; luôn có option "chỉ cần chạy được".
- Câu 2 hỏi bối cảnh bằng số (môi trường + bản target, CCU/RPS/số bản ghi, R&D hay
  product, vòng đời & người bảo trì, ràng buộc nền tảng), trần 4 câu. **CẤM** hỏi mức độ
  trừu tượng kiểu "gọn nhất hay đầy đủ chuyên nghiệp" — mức đầu tư do agent suy ra rồi
  nói lại bằng dòng `Tôi hiểu là: <mức> vì <bối cảnh>`, không phải cổng duyệt mới.
- Nối vào 4 chỗ gọi interview: `interview.md` (thêm mục "Hai tầng câu hỏi", tầng 2 chỉ
  hỏi trong các mặt user đã chọn), `analyze-full.md` bước 4, `quick-lane.md`,
  `tdq-intake/SKILL.md`.
- Neo kết quả: `spec-template.md` §1 buộc chép các mặt bị loại vào `NGOÀI phạm vi` (thêm
  một dòng Checklist scope); `tdq_state.py` `PHASE_GUIDE["analyze"]` thêm dòng nhắc vòng
  scope, đặt trước dòng hỏi chi tiết.
- Test: `tests/test_scope_round.py` (nội dung file luật + kiểm cả 4 chỗ gọi đã nối dây),
  `tests/test_next.py::test_next_analyze_asks_for_the_scope_round`.

## 0.14.0 — 2026-08-14

Cổng chọn cách chạy nói bằng tên nghề nghiệp, và phải giải thích vì sao đề xuất mode đó.

- `scripts/tdq_state.py`: thêm `MODE_LABELS`/`MODE_ALIASES` + `mode_label()`/
  `normalize_mode()` — mode tách hai lớp y như lane. Nhãn hiển thị: `main` → "làm trực
  tiếp (inline implement)", `subagent` → "giao trợ lý (sub-agent implement)". Định danh
  máy giữ nguyên `main|subagent` nên state cũ, plan cũ, `--mode` cũ không phải migrate.
  `--mode` và dạng gõ tắt `approve plan <mode>` đều đi qua `normalize_mode`.
- Checklist phase `mode` buộc trình đoạn **"Vì sao đề xuất"** dài 1–3 dòng. Đoạn đó phải
  nêu đủ 4 căn cứ đọc từ chính plan: số task, chuỗi phụ thuộc, số file bị nhiều task cùng
  đụng, có nhãn `(mcp)` không. Kết bằng một câu vì sao không chọn phương án còn lại.
- `skills/tdq-plan/references/mode-gate.md` (mới): khuôn hỏi nguyên văn + luật viết đoạn
  lý do. SKILL.md có trần 100 dòng nên chỉ giữ tóm tắt và link.
- `plan-template.md`, `skills/tdq-build/SKILL.md`: ghi kèm nhãn hiển thị bên cạnh định
  danh máy.
- Hook: `_common.py` in nhãn thay vì định danh máy; `prompt_context.py` nhận `inline`,
  `sub-agent`, biến thể có `implement`, và **chữ cái A/B** đúng như khuôn mời gõ
  (`mode_from_answer`: A = mode plan đề xuất, B = mode còn lại); `edit_gate.py` gợi ý cả
  hai tên.

## 0.13.0 — 2026-08-14

Chốt vai trò graphify thành hai luật rõ: đồ thị CHỈ chứa mã nguồn sản phẩm, và chỉ tra
đồ thị khi cần liên kết hoặc bản đồ tổng thể.

- `.graphifyignore`: liệt kê đủ 8 thư mục (`tests/ docs/ portable/ skills/ agents/
  ClaudeExport/ claude-export/ graphify-out/`), có hiệu lực cả khi chạy `graphify extract`
  không cờ `--code-only`. Node trong đồ thị: 1.421 → 412.
- 6 file `hooks/scripts/` đổi sang `from tdq_state import <tên>` rồi gọi thẳng. Lý do:
  graphify (0.9.28 và 0.9.42) chỉ sinh cạnh `calls` cross-file cho dạng from-import; dạng
  `import M` + `M.f()` không sinh cạnh nào. Cạnh `hooks/* → scripts/tdq_state.py`: 1 → 38,
  `graphify affected "turn_snapshot()"` từ chỗ không ra gì nay ra `prompt_context.py`.
- `skills/tdq-intake/references/analyze-full.md`, `quick-lane.md`: thêm luật ĐỌC — mở đồ
  thị cho câu hỏi liên kết / bản đồ tổng thể, grep cho tìm chuỗi và đọc file cụ thể.
- `scripts/tdq_state.py`: thêm `"graphify-out"` vào `BOOKKEEPING_PATHS`; thư mục do chính
  workflow ghi lại mỗi turn không còn tính vào vân tay repo. Kèm test mới
  `test_digest_ignores_graphify_out`.
- `tests/test_bash_gate.py`: patch `turn_log_read` vào module `_common` (nơi giữ tên đã
  bind) thay vì vào `tdq_state`.

## 0.12.0 — 2026-08-13

Khuôn trình bày thân thiện dùng chung cho mọi chỗ nói với user, và tách bước chọn cách
chạy thành phase `mode` riêng — user chỉ cần nhắn "duyệt plan".

- `skills/tdq-conventions/references/user-facing-block.md` (mới) + bản portable: 5 thành
  phần bắt buộc, cấm emoji, xưng "bạn", luôn có đường dẫn file đầy đủ. Áp cho đủ 7 chỗ
  giao tiếp: hỏi pipeline, interview, duyệt spec, duyệt plan, chọn cách chạy, duyệt chế
  độ nhanh, hỏi commit cuối request.
- `scripts/tdq_state.py`: thêm phase `mode` vào `VALID_PHASES`, `PHASE_ORDER`,
  `PHASE_TABLE`. `approve plan` không kèm `--mode` nay dừng ở phase `mode`; kèm `--mode`
  thì vào thẳng `implement`.
- `hooks/scripts/_common.py`, `prompt_context.py`: khoá `plan` trong `APPROVE_HINTS` bỏ
  phần mode, thêm khoá `mode` giải thích nghĩa `main` và `subagent` ngay tại chỗ.
- Đồng bộ tài liệu: `phases.md` (hai bản), `portable/workflow/03-plan.md`,
  `plan-template.md` (hai bản), `docs/claude-md-mau.md` §6.
- `tests/test_mode_phase.py` (mới) và cập nhật `test_gate_merge`, `test_phase_table`,
  `test_state`, `test_context_hooks`.

## 0.11.13 — 2026-08-13

Bắt chặn của `stop_gate.py` phải ra lệnh in LẠI NGUYÊN VĂN khối chat cuối — lớp vá thứ hai
cho việc focus mode gập ẩn câu hỏi khi turn còn chạy tiếp sau lúc đã in khối user-facing.

- `hooks/scripts/stop_gate.py`: `reason` của cả `[TDQ:LOG]` và `[TDQ:TICK]` nay yêu cầu in
  lại nguyên văn khối chat cuối. `[TDQ:LOG]` bỏ câu bảo tự thêm mục `## HH:MM`, thay bằng
  lệnh `tdq_finish.py`. Sửa kèm lỗi `culprit` lấy từ sổ turn không cắt theo `MAX_PATH_CHARS`
  nên path dài đẩy lời chặn vượt trần 300 ký tự.
- `skills/tdq-conventions/SKILL.md` §1 bước 5: luật in lại nguyên văn 100% khối user-facing,
  đặt ngay sau dòng `✓ [TDQ:<MÃ>]`, áp cho mọi nguyên nhân (hook chặn, sót việc, lỗi tool).
- `skills/tdq-conventions/references/worklog-images.md`: tách phần xử lý ảnh working log ra
  file riêng để `SKILL.md` giữ trong trần 120 dòng của `doc_lint` R6.
- `tests/test_stop_gate.py`: lớp `TestStopGateReprint` — 4 test giữ cụm bắt buộc và trần 300
  ký tự của lời chặn.

## 0.11.12 — 2026-08-13

Đổi nhãn "Năng lực" thành "Ước tính sẽ dùng skill" trong tóm tắt chế độ nhanh, cho thân
thiện người dùng.

- `skills/tdq-intake/SKILL.md`, `references/quick-lane.md`, `references/skill-inventory.md`:
  đổi nhãn dòng `Năng lực: <...>` → `Ước tính sẽ dùng skill: <...>` ở đúng 3 chỗ user-facing
  của chế độ nhanh. Không đụng heading `### Năng lực dùng được` ở brief/spec chuyên sâu.

## 0.11.11 — 2026-08-13

Bắt buộc dùng `tdq_finish.py` (thay Edit tay) và chạy trước đoạn chat cuối turn — sửa gốc
việc câu hỏi/tóm tắt TDQ bị chế độ focus của Claude Code gập ẩn.

- `skills/tdq-conventions/SKILL.md` §1 bước 4: thêm bắt buộc gọi `tdq_finish.py` (cấm
  Edit/Read rồi tự append tay working log). Lệnh đó phải là hành động cuối cùng của turn,
  chạy TRƯỚC đoạn chat kết thúc turn — không gọi thêm tool sau khi đã in đoạn đó.

## 0.11.10 — 2026-08-13

Gắn nhãn khuôn mẫu khi tóm tắt spec/plan trích lại, tránh nhầm là câu hỏi sống.

- `skills/tdq-spec/SKILL.md` bước 4, `skills/tdq-plan/SKILL.md` bước 5: khi đầu ra chính
  là một khuôn/mẫu văn bản và cần trích nguyên khối đó vào tóm tắt duyệt. Gắn nhãn "(khuôn
  mẫu — áp dụng cho các lần hỏi sau, không phải câu hỏi của turn này)" trước đoạn trích.

## 0.11.9 — 2026-08-13

Gọn UX câu hỏi chọn lane, gọi "pipeline" khi hiện với user.

- `skills/tdq-intake/SKILL.md` bước 2: bỏ yêu cầu in dòng `Cỡ:/Cần:` ra chat (giữ làm căn
  cứ nội bộ), đổi câu hỏi user sang "Bạn muốn chạy pipeline nào?".
- `skills/tdq-intake/references/lane-decision.md`: mục "Dòng tự nhận định" thành đánh giá
  nội bộ; "Khuôn câu hỏi" viết lại — bỏ Cỡ/Cần, dùng "pipeline", thêm khối giải thích
  ngắn nghĩa 2 pipeline. Không đổi `interview.md` hay thuật ngữ `lane` nội bộ.

## 0.11.8 — 2026-08-13

Lưu & nhúng ảnh đính kèm vào working log.

- `skills/tdq-conventions/SKILL.md` §6: thêm quy ước — turn có ảnh user gửi kèm + phải
  ghi working log → copy ảnh từ cache session sang `docs/workinglog/assets/<slug>/<n>.<ext>`
  (track git), chèn markdown `![...]` vào chuỗi `--log`. Không sửa `tdq_finish.py`.

## 0.11.7 — 2026-08-13

Bắt buộc rõ hơn việc in tóm tắt spec/plan trước dòng duyệt.

- `skills/tdq-spec/SKILL.md` bước 4, `skills/tdq-plan/SKILL.md` bước 5: thêm câu
  tự-kiểm ngay trước dòng `➤ Duyệt:` — buộc xác nhận tin nhắn CHỨA tóm tắt thật, không
  được thay bằng câu thông báo suông kiểu "đã ghi log, đang chờ duyệt".

## 0.11.6 — 2026-08-13

Thân thiện hơn với người dùng mới ở câu hỏi khuôn A/B/C và dòng duyệt.

- `skills/tdq-intake/references/interview.md`: khối hint cuối mỗi vòng hỏi đổi từ 1 câu
  chung chung sang 2 phần — nguyên tắc (gõ chữ cái hoặc câu tự nhiên) + 1 ví dụ trung tính.
- 3 dòng `➤ Duyệt:` (`tdq-spec`, `tdq-plan`, `tdq-intake` bước duyệt nhanh) thêm vế ngắn
  nói rõ duyệt xong dẫn tới bước gì tiếp theo (viết plan / build / implement ngay).

## 0.11.5 — 2026-08-13

Bịt 3 lỗ hổng tick checkbox ở chế độ chuyên sâu.

- `plan_tick_state` (`scripts/tdq_state.py`) trả thêm `doing_count`.
- `edit_gate.py` chặn khi có ≥2 task cùng `[~]`, và chặn sau 3 lần sửa mã liên tiếp
  mà chưa tick (đếm streak qua sổ turn, reset khi `plan_sha` đổi).
- Luật giao subagent (`tdq-build`/`tdq-plan` SKILL.md, `agents/tdq-implementer.md`)
  đổi xuống đúng 1 task/lần gọi để tick theo kịp tiến độ thật.

## 0.11.4 trở về 0.7.0

Xem [docs/archive/CHANGELOG-0.7-0.11.4.md](docs/archive/CHANGELOG-0.7-0.11.4.md).

## 0.6.2 trở về trước

Xem [docs/archive/CHANGELOG-0.5-0.6.md](docs/archive/CHANGELOG-0.5-0.6.md)
và [docs/archive/CHANGELOG-0.1-0.3.md](docs/archive/CHANGELOG-0.1-0.3.md).
