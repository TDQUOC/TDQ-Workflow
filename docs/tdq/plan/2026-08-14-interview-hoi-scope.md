# PLAN — Vòng scope: interview đi từ tổng quát đến chi tiết

Ngày: 2026-08-14 · Spec: ../spec/2026-08-14-interview-hoi-scope.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Mode thực thi: main — 12 task nhưng 5 file tài liệu cùng trỏ về một file luật duy nhất, câu chữ phải khớp nhau từng cụm; tách agent song song dễ lệch giọng và lệch tên mục (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: ĐÃ DUYỆT (mode: main — làm trực tiếp (inline implement))

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — file luật viết xong mới nối link vào 4 chỗ gọi.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → sửa → test xanh → đổi `[x]`
   NGAY vào file này.
3. Không đụng khuôn option A/B/C hiện có, không đụng gate duyệt, không thêm rule
   `doc_lint`.

## Phase 1 — File luật `scope-round.md`

- [x] **T1.1** (n4 e14m) Viết `skills/tdq-intake/references/scope-round.md` mục 1
  "Khi nào chạy": danh sách đóng 4 dấu hiệu kích hoạt, luật áp cho cả hai lane, và luật
  BỎ phải ghi một dòng `Vòng scope: BỎ — <lý do>` vào brief — Test:
  `grep -c "Vòng scope: BỎ" skills/tdq-intake/references/scope-round.md` ≥ 1 và
  `python3 scripts/doc_lint.py` file đó exit 0.
- [x] **T1.2** (n4 e12m) Viết mục 2 "Câu 1 — mặt scope": khung 9 mặt ISO/IEC 25010 dùng
  NỘI BỘ để soát, chỉ trình 3–5 mặt hợp lĩnh vực, mỗi mặt một dòng theo khuôn option,
  cho chọn nhiều, luôn có option "chỉ cần chạy được" — Test:
  `grep -c "25010" scope-round.md` ≥ 1 và `grep -c "3–5"` ≥ 1.
- [x] **T1.3** (n4 e12m) Viết mục 3 "Câu 2 — bối cảnh bằng số": bộ mẫu 5 nhóm câu (môi
  trường + phiên bản target, CCU/RPS/số bản ghi, R&D hay product, vòng đời & người bảo
  trì, ràng buộc nền tảng), trần 4 câu, kèm dòng CẤM hỏi "gọn hay đầy đủ chuyên nghiệp" —
  Test: `grep -c "CCU" scope-round.md` ≥ 1 và `grep -ci "cấm"` ≥ 1.
- [x] **T1.4** (n3 e10m) Viết mục 4 "Suy ra mức đầu tư" (bảng ánh xạ bối cảnh → mức, kèm
  dòng bắt buộc `Tôi hiểu là: <mức> vì <bối cảnh>`, không thêm gate) và mục 5 "Ghi lại"
  (brief `### Phạm vi đã chốt` 4 dòng, spec §1 chép mặt bị loại) — Test:
  `grep -c "^## " scope-round.md` ≥ 5 và `grep -c "Tôi hiểu là"` ≥ 1.
- [x] **T1.5** (n3 e10m) `tests/test_scope_round.py`: file tồn tại, đủ 5 mục `##`, có
  danh sách dấu hiệu kích hoạt, có luật ghi lý do khi BỎ, có cấm hỏi mức độ trừu tượng,
  và mọi link trong file trỏ tới file có thật — Test:
  `python3 -m pytest tests/test_scope_round.py -q` xanh.

## Phase 2 — Nối vào các chỗ đang gọi interview

- [x] **T2.1** (n3 e10m) `skills/tdq-intake/references/interview.md`: thêm mục "Hai tầng
  câu hỏi" ở đầu (tầng 1 scope → tầng 2 chi tiết), nói rõ 7 hạng mục chi tiết chỉ hỏi
  trong các mặt user đã chọn, link `scope-round.md`; giữ nguyên khuôn option và câu hỏi
  mở cuối vòng — Test: `python3 -m pytest tests/test_gate_merge.py
  tests/test_user_facing_block.py tests/test_skill_shape.py -q` xanh và
  `grep -c "scope-round.md" interview.md` ≥ 1.
- [x] **T2.2** (n2 e6m) `references/analyze-full.md` bước 4: interview = vòng scope
  (có điều kiện) trước, rồi vòng chi tiết — Test: `grep -c "scope-round" analyze-full.md`
  ≥ 1, doc_lint exit 0.
- [x] **T2.3** (n2 e6m) `references/quick-lane.md`: thêm dòng "Vòng scope" vào bảng so
  sánh Full/Quick và một câu ở bước 1 — Test: `grep -c "scope-round" quick-lane.md` ≥ 1,
  doc_lint exit 0.
- [x] **T2.4** (n3 e8m) `skills/tdq-intake/SKILL.md`: Phần B bước 4 và Phần C bước 1 đều
  nhắc vòng scope + link, tối đa 4 dòng thêm — Test: `grep -ci "vòng scope" SKILL.md` ≥ 2
  và `wc -l < SKILL.md` ≤ 120, doc_lint exit 0.
  Làm thêm trong task này: `tests/test_scope_round.py` có lớp `ScopeRoundIsWiredTest` kiểm
  cả 4 chỗ gọi đều trỏ `scope-round.md` — grep ở DoD chỉ chạy một lần, test thì giữ mãi.

## Phase 3 — Neo kết quả scope vào spec và state

- [x] **T3.1** (n2 e8m) `skills/tdq-spec/references/spec-template.md`: §1 buộc chép các
  mặt bị loại ở vòng scope vào `NGOÀI phạm vi`, và thêm một dòng vào "Checklist scope" —
  Test: `grep -c "mặt bị loại" spec-template.md` ≥ 1, doc_lint exit 0.
- [x] **T3.2** (n2 e6m) `scripts/tdq_state.py`: `PHASE_GUIDE["analyze"]` thêm một dòng
  checklist về vòng scope (chạy hoặc ghi lý do BỎ), đặt TRƯỚC dòng "Hỏi user mọi điểm
  chưa rõ" — Test: `python3 -m pytest tests/test_next.py -q` xanh và
  `python3 scripts/tdq_state.py next` ở phase `analyze` in ra chữ "scope".

## Phase 4 — Kiểm cuối

- [x] **T4.1** (n1 e3m) Log service còn nguyên sau khi sửa `tdq_state.py` — Test: gọi
  `_warn` mặc định ra 1 dòng có timestamp, `TDQ_LOG=0` ra 0 dòng.
- [x] **T4.2** (n1 e5m) Full suite một lần cộng `doc_lint` mọi file `.md` đã sửa — Test:
  `python3 -m pytest tests/ -q` không có `failed` (≥ 552 test); `doc_lint.py` exit 0.
- [x] **T4.3** (n1 e4m) Ghi quy ước vòng scope vào bộ nhớ dài hạn — Test:
  `search_memories("vòng scope interview", project="TDQWorkflow")` trả về fact vừa ghi.
  - Dùng: `mem0-memory` (mcp)
  - Để: ghi đúng 1 fact ngắn "interview TDQ có vòng scope chạy có điều kiện trước vòng
    chi tiết: chọn mặt theo khung ISO 25010 + hỏi bối cảnh bằng số, bỏ thì phải ghi lý
    do", nạp skill TRƯỚC bước kiểm.
  - Ra: một memory trong project `TDQWorkflow`, nội dung như trên.
  - Kiểm: `search_memories` với truy vấn "vòng scope interview" trả về đúng fact đó.
  - Không dùng cho: chép nội dung spec/plan hay log phiên làm việc vào mem0.
- [x] **T4.4** (n1 e3m) Cập nhật đồ thị mã nguồn sau khi sửa `scripts/tdq_state.py` —
  Test: `graphify extract . --code-only` chạy xong, `graphify-out/manifest.json` có mốc
  thời gian mới.
  - Dùng: `graphify`
  - Để: đồng bộ đồ thị với file mã nguồn vừa đổi, chạy ở cuối turn build.
  - Ra: `graphify-out/graph.json` và `manifest.json` cập nhật.
  - Kiểm: lệnh thoát 0 và `manifest.json` đổi mốc thời gian.
  - Không dùng cho: quét tài liệu hay thư mục `tests/` (đã bị `.graphifyignore` loại).

Tổng: 4 phase · 15 task · ước tính 117 phút.

## Definition of Done

Trỏ về §6 của spec, mỗi dòng một lệnh kiểm:

- Q1 `grep -c "^## " skills/tdq-intake/references/scope-round.md` ≥ 5.
- Q2 `grep -c "Vòng scope: BỎ" scope-round.md` ≥ 1.
- Q3 `grep -c "CCU" scope-round.md` ≥ 1 và có dòng cấm hỏi mức độ trừu tượng.
- Q4 `grep -c "scope-round.md" skills/tdq-intake/references/interview.md` ≥ 1.
- Q5 `grep -l "scope-round" analyze-full.md quick-lane.md` ra đủ 2 file.
- Q6 `grep -ci "vòng scope" skills/tdq-intake/SKILL.md` ≥ 2 và `wc -l` ≤ 120.
- Q7 `grep -c "mặt bị loại" skills/tdq-spec/references/spec-template.md` ≥ 1.
- Q8 `python3 scripts/tdq_state.py next` ở phase `analyze` in ra chữ "scope".
- Q9 `_warn` mặc định in 1 dòng timestamp, `TDQ_LOG=0` in 0 dòng.
- Q10 `python3 -m pytest tests/ -q` không có `failed`, số test ≥ 552.
- Q11 `python3 scripts/doc_lint.py <các file .md đã sửa>` exit 0.
