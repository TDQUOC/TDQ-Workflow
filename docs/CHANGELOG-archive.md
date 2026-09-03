# Changelog — bản lưu trữ

Các bản 0.20.0 trở về trước, tách khỏi `CHANGELOG.md`
để file chính nằm dưới trần R6 500 dòng. Mới nhất trên cùng.

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

Bản 0.18.0 trở về trước: [docs/CHANGELOG-archive.md](docs/CHANGELOG-archive.md).

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
