# PLAN — Chế độ _tdq_direct tự động phân tích và chỉ có 1 cổng duyệt mini-plan

Ngày: 2026-10-14 · Spec: ../spec/2026-10-14-1022-che-do-tdq-direct.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — mô phỏng tdq_bench đội thắng main 6,1 phút (2 đợt, hệ số agent 1.5) (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: CHỜ DUYỆT

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- Cụm song song
- P1 — Hook nhận diện _tdq_direct & unit test
- P2 — Tài liệu hướng dẫn skill tdq-intake & quick-lane
- P3 — Khối ghim instruction trong setup
- P4 — Log & test bắt buộc
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.

## Cụm song song

Theo mô phỏng `tdq_bench` chia làm 2 đợt:
- Đợt 1: T1.1 (`tests/test_prompt_context.py`), T2.1 (`skills/tdq-intake/SKILL.md`), T3.1 (`scripts/tdq_setup.py`, `docs/claude-md-mau.md`) chạy song song trên các vùng file độc lập.
- Đợt 2: T1.2 (`hooks/scripts/prompt_context.py` sau T1.1) và T2.2 (`skills/tdq-intake/references/quick-lane.md`).
- Leader tự làm: T4.2 (kiểm thử hồi quy tổng hợp).

## P1 — Hook nhận diện _tdq_direct & unit test
- [x] **T1.1** (e5m) Viết test đỏ trong `tests/test_prompt_context.py` kiểm tra nhận diện `_tdq_direct`:
  - prompt có `_tdq_direct` (không phân biệt hoa thường, ranh giới từ `(?:^|\s|[^\w])_tdq_direct(?:\s|[^\w]|$)`) khi state None hoặc chưa có active_request hoặc phase idle -> phát dòng `[TDQ:INTAKE]` direct;
  - dòng `[TDQ:INTAKE]` direct không bị cắt đuôi và độ dài dòng ≤ 240 ký tự;
  - prompt bình thường không có `_tdq_direct` -> vẫn phát dòng `[TDQ:INTAKE]` tiêu chuẩn cũ;
  - prompt có active_request và phase != idle -> không phát dòng `[TDQ:INTAKE]`.
  - Test: `python3 -c "import tests.test_prompt_context as t; assert hasattr(t, 'TestIntakeDirectReminder') and t.TestIntakeDirectReminder.DONG_DIRECT_LEN <= 240"`
  - Chạm: `tests/test_prompt_context.py`
- [x] **T1.2** (e6m) Cập nhật `hooks/scripts/prompt_context.py` để test xanh:
  - Thêm regex `RE_DIRECT = re.compile(r"(?:^|\s|[^\w])_tdq_direct(?:\s|[^\w]|$)", re.IGNORECASE)`;
  - Trong logic kiểm tra không có request mở (`state is None or not state.get("active_request")` hoặc `phase_key(state) == "idle"`), kiểm tra `RE_DIRECT.search(prompt)`:
    Nếu khớp, gán dòng `intake`:
    `"[TDQ:INTAKE] Yêu cầu chứa '_tdq_direct' → chạy chế độ direct: tự động phân tích & tìm kiếm, lập mini-plan và chỉ dừng ở 1 cổng duyệt mini-plan (không hỏi chọn pipeline, không phỏng vấn)."` (174 ký tự ≤ 240);
    Nếu không khớp, giữ nguyên câu nhắc cũ.
  - Test: `python -m unittest tests/test_prompt_context.py`
  - Chạm: `hooks/scripts/prompt_context.py`
  - Cần: T1.1

**Xong P1 khi**: Toàn bộ unit test trong `tests/test_prompt_context.py` đều xanh.

## P2 — Tài liệu hướng dẫn skill tdq-intake & quick-lane
- [x] **T2.1** (e5m) Cập nhật `skills/tdq-intake/SKILL.md` (Part A Step 2 & 3):
  - Bổ sung quy tắc: nếu prompt chứa từ khóa `_tdq_direct` (không phân biệt hoa thường) → bỏ qua Step 2 (hỏi chọn pipeline), tự động khởi tạo lane `quick` với `init <slug> quick`, mở branch git `feature/...` (Step 3b) và chuyển thẳng sang Part C (express pipeline).
  - Test: `python3 scripts/doc_lint.py skills/tdq-intake/SKILL.md`
  - Chạm: `skills/tdq-intake/SKILL.md`
  - Dùng: `tdq-intake`
  - Để: quy định luồng nhận diện `_tdq_direct` bỏ qua hỏi lane, vào thẳng phân tích + mini-plan, nạp skill TRƯỚC bước đỏ
  - Ra: `skills/tdq-intake/SKILL.md` có hướng dẫn luồng `_tdq_direct`
  - Kiểm: `python3 scripts/doc_lint.py skills/tdq-intake/SKILL.md`
  - Không dùng cho: tự ý thay đổi schema state trong `scripts/tdq_state.py`
- [x] **T2.2** (e5m) Cập nhật `skills/tdq-intake/references/quick-lane.md`:
  - Thêm mục/chỉ dẫn cho luồng `_tdq_direct`: khi vào express qua `_tdq_direct`, tự động thực hiện B1 tìm kiếm và phân tích mã nguồn (LSP/graphify/grep), lập mini-plan ≤ 40 dòng trong `docs/tdq/plan/<slug>.md`, chỉ dừng ở 1 cổng duyệt mini-plan duy nhất (`quick_approved`), sau đó implement nhanh.
  - Test: `python3 scripts/doc_lint.py skills/tdq-intake/references/quick-lane.md`
  - Chạm: `skills/tdq-intake/references/quick-lane.md`

**Xong P2 khi**: `doc_lint.py` xanh cho cả hai file tài liệu của `tdq-intake`.

## P3 — Khối ghim instruction trong setup
- [x] **T3.1** (e6m) Cập nhật `KHOI_HUONG_DAN` trong `scripts/tdq_setup.py` và đồng bộ sang `docs/claude-md-mau.md`:
  - Thêm một gạch đầu dòng vào mục `## Nguyên tắc TDQ Workflow bắt buộc` trong `KHOI_HUONG_DAN`:
    `- Yêu cầu chứa '_tdq_direct' → tự động phân tích & tìm kiếm mã nguồn, lập mini-plan và chỉ dừng ở 1 cổng duyệt mini-plan (không hỏi chọn pipeline, không phỏng vấn).`
  - Đồng bộ nguyên văn sang khối tương ứng trong `docs/claude-md-mau.md`.
  - Đảm bảo độ dài dòng chỉ dẫn ≤ 300 ký tự và kích thước `docs/claude-md-mau.md` ≤ trần `MAX_BYTES`.
  - Test: `python -m pytest tests/test_claude_md_core.py -q`
  - Chạm: `scripts/tdq_setup.py`, `docs/claude-md-mau.md`
  - Dùng: `tdq-setup`
  - Để: cập nhật khối hướng dẫn ghim toàn cục cho chế độ `_tdq_direct`, nạp skill TRƯỚC bước đỏ
  - Ra: `scripts/tdq_setup.py` và `docs/claude-md-mau.md` có khối ghim đồng bộ
  - Kiểm: `python -m pytest tests/test_claude_md_core.py -q`
  - Không dùng cho: can thiệp vào các bậc cài đặt bên ngoài của setup

**Xong P3 khi**: `test_claude_md_core.py` xanh 100%, bản mẫu khớp nguyên văn hằng số code.

## P4 — Log & test bắt buộc
Log: BỎ — Việc này chỉ sửa logic kiểm tra chuỗi trong hook, cập nhật tài liệu hướng dẫn và bổ sung test, không tạo runtime service hay background process mới.
- [x] **T4.2** (e4m) Chạy toàn bộ kiểm thử đơn vị và kiểm tra hồi quy các vùng chạm:
  - Test: `python -m pytest tests/test_prompt_context.py tests/test_claude_md_core.py tests/test_tdq_setup.py tests/test_doc_lint.py -q`
  - Chạm: `tests/test_prompt_context.py`

**Xong P4 khi**: Trọn bộ test hồi quy vùng chạm đều pass.

## Definition of Done
- [x] Q1 Hook nhận diện `_tdq_direct` — `python -m unittest tests/test_prompt_context.py -k Direct` xanh.
- [x] Q2 Độ dài dòng nhắc direct — `python3 -c "import tests.test_prompt_context as t; assert t.TestIntakeDirectReminder.DONG_DIRECT_LEN <= 240"` thoát 0.
- [x] Q3 Dòng ghim instruction trong setup — `python -m pytest tests/test_claude_md_core.py -k test_khoi_trong_ban_mau_khop_nguyen_van_voi_hang_so -q` xanh và dòng direct ≤ 300 ký tự.
- [x] Q4 Hồi quy và nhất quán template — `python -m pytest tests/test_prompt_context.py tests/test_claude_md_core.py tests/test_tdq_setup.py tests/test_doc_lint.py -q` xanh.
- [x] Q5 Hướng dẫn skill tdq-intake — `python3 scripts/doc_lint.py skills/tdq-intake/SKILL.md skills/tdq-intake/references/quick-lane.md` thoát 0.
