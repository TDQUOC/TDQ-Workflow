# PLAN — Spec có sơ đồ Trước/Sau, subagent chỉ đọc, DoD bám nghiệp vụ

Ngày: 2026-11-02 · Spec: ../spec/2026-11-02-1157-nang-cap-spec-subagent.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — `tdq_bench.py simulate` đo main 20,4 phút = subagent 20,4 phút (chênh 0); main ít chi phí khởi tạo worktree hơn (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- Thiết kế Trước vs Sau
- Eval-plan (đổi hành vi skill/hook)
- P1 — Nhánh chặn subagent trong hook
- P2 — Luật trong skills
- P3 — QC
- Cụm song song
- Luật file nóng
- Px — Log & test bắt buộc
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → sửa → test xanh → đổi sang `[x]` NGAY vào file này.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Tuân thủ 6 mã cấm cơ học (ANTI-1 Fake Red, ANTI-2 Blind Assertion, ANTI-3 Dirty State Git, ANTI-4 Late Tick, ANTI-5 Raw Dump, ANTI-6 Broad Area).
8. Chỉ thêm, không sửa assert test cũ; không đụng dòng nào ngoài vùng `Chạm:`.

## Thiết kế Trước vs Sau

| Khía cạnh | Hiện trạng (Trước) | Thiết kế mới (Sau) |
|---|---|---|
| Luồng thực thi | Spec: 1 sơ đồ thiết kế mới; subagent ghi được mọi file trước implement | Spec: 1 HTML Trước + Sau; subagent ghi ngoài `docs/` trước implement bị chặn |
| Thành phần chạm | `edit_gate.py` (miễn docs, rào `Chạm:`), 6 file luật | Thêm 1 nhánh `if` trong `edit_gate.main`; thêm câu luật vào 7 file sẵn có |

*Đối chiếu sơ đồ kiến trúc:* HTML và manifest đã duyệt: `docs/tdq/spec/2026-11-02-1157-nang-cap-spec-subagent-preview.html`, `docs/tdq/spec/2026-11-02-1157-nang-cap-spec-subagent-preview.manifest.json`. Node `phase` ("Đã tới implement?") của sơ đồ `sub-sau-flow` = T1.1; các node `before`/`after`/`page` của `spec-sau-flow` = T2.1–T2.2. Kiểm binding trước code bằng `verify`.

## Eval-plan (đổi hành vi skill/hook)

- Baseline: chạy các test khoá mới trên mã gốc → phải ĐỎ (luật chưa có). Candidate: sau sửa → XANH. Cùng máy, cùng lệnh.
- Hành vi hook: payload mô phỏng đúng dạng tài liệu Claude Code (`agent_id`, `agent_type`) qua `run_hook`; không chạy phiên live vì hook đang nạp từ cache plugin 0.85.1, không từ repo — ghi vào report.
- Thước đo: số test đỏ → xanh; trọn bộ test cũ không đổi số PASS; không file `scripts/` nào đổi.

## P1 — Nhánh chặn subagent trong hook

- [x] **T1.1** (e15m) Thêm test đỏ 4 ca rồi thêm nhánh chặn trong `edit_gate.main` ngay sau dòng miễn `docs/**`: `agent_id` là chuỗi khác rỗng + file trong project + phase ∉ {implement, qc} → `block(..., "TDQ:TEAM", ...)`; kèm comment `ponytail:` về giới hạn ghi qua shell — Test: `python -m pytest tests/test_edit_gate.py -q -k subagent` (đỏ trước, xanh sau)
  - Chạm: `hooks/scripts/edit_gate.py`, `tests/test_edit_gate.py` → `codex_edit_gate.py` chuyển tiếp sang (payload Codex không có `agent_id`, không đổi)

**Xong P1 khi**: 4 ca subagent xanh và `tests/test_edit_gate.py` cũ vẫn xanh.

## P2 — Luật trong skills

- [x] **T2.1** (e12m) Spec template: §2c thêm khối "Cơ chế hiện tại vs Sau" (HTML Trước/Sau là nội dung chính, bảng chữ phụ trợ, dựng mới ghi "Hiện trạng: chưa có"); §6 thêm câu "mỗi dòng truy về một hành vi nghiệp vụ hoặc luồng cũ phải giữ, test viết đỏ trước"; checklist hướng dẫn thêm dòng HTML Trước/Sau — Test: `python -m pytest tests/test_spec_template.py -q`
  - Chạm: `skills/tdq-spec/references/spec-template.md`, `skills/tdq-spec/references/spec-template-huong-dan.md`, `tests/test_spec_template.py` → không node code nào phụ thuộc
- [x] **T2.2** (e12m) Archify: `archify-ba.md` đổi sang một `explainer` có sơ đồ Trước (evidence) + Sau (planned), render/bind bằng lệnh có sẵn; `archify-quick.md` + dòng 65 `quick-lane.md` bỏ ngưỡng "≥ 2 module", áp cho mọi mini-plan sửa thứ đã có — Test: `python -m pytest tests/test_archify_workflow_contract.py -q`
  - Chạm: `skills/tdq-spec/references/archify-ba.md`, `skills/tdq-intake/references/archify-quick.md`, `skills/tdq-intake/references/quick-lane.md`, `skills/tdq-intake/SKILL.md`, `tests/test_archify_workflow_contract.py` → không node code nào phụ thuộc
  - Ghi chú: archify-ba + archify-quick xong; còn câu ngưỡng cũ ở quick-lane dòng 65 và tdq-intake/SKILL.md dòng 132 (thêm vào Chạm).
  - Dùng: `archify (local)`
  - Để: đối chiếu cú pháp `explainer` (`@workflow`, tối đa 4 sơ đồ) khi viết luật; nạp `explainer-authoring.md` trước bước đỏ
  - Ra: `skills/tdq-spec/references/archify-ba.md` nêu đúng dạng explainer Trước/Sau
  - Kiểm: `node <archify>/bin/archify.mjs validate explainer docs/tdq/artifacts/2026-11-02-1157-nang-cap-spec-subagent/truoc-sau.archify.md` báo `ok`
  - Không dùng cho: sửa `scripts/tdq_archify.py` hay bộ cài Archify
- [x] **T2.3** (e8m) Conventions §9: mở subagent ở mọi phase, mỗi con một việc, trả report vào `docs/`, trước implement không sửa project; `reminder-codes.md` mục `TDQ:TEAM` thêm ca này — Test: `python -m pytest tests/test_luat_subagent_pr.py -q -k subagent`
  - Chạm: `skills/tdq-conventions/SKILL.md`, `skills/tdq-conventions/references/reminder-codes.md`, `tests/test_luat_subagent_pr.py` → `tests/test_token_budget.py` đo cỡ SKILL.md
- [x] **T2.4** (e6m) Report template thêm khối "Thân PR (soạn sẵn)": tóm tắt · Trước/Sau (link HTML) · test đã chạy · rủi ro hồi quy; ghi rõ không tự tạo PR — Test: `python -m pytest tests/test_luat_subagent_pr.py -q -k pr`
  - Chạm: `skills/tdq-build/references/report-template.md`, `tests/test_luat_subagent_pr.py`

**Xong P2 khi**: 4 lệnh test trên xanh và `doc_lint.py` trên 7 file luật exit 0.

- [x] **T2.5** (e6m) Fix lint: `tdq-conventions/SKILL.md` 198 > 192 dòng (R6) và `spec-template.md` 3865 > 3500 token (R13) — dời đoạn subagent sang `subagent-tuning.md`, rút gọn 2 câu luật trong template — Test: `python scripts/doc_lint.py` trên 9 file luật exit 0
  - Chạm: `skills/tdq-conventions/SKILL.md`, `skills/tdq-conventions/references/subagent-tuning.md`, `skills/tdq-spec/references/spec-template.md`, `tests/test_luat_subagent_pr.py`
  - Ghi chú: R6 xanh; R13 còn 3587 > 3500 — gộp mục mới vào câu bảng Trước/Sau cũ, rút câu §6.

## P3 — QC

- [x] **T3.1** (e10m) Trọn bộ test + lint + `tdq_test.py vung-cham` — Test: `python scripts/tdq_test.py tron-bo` exit 0
- [x] **T3.2** (e8m) Chụp ảnh HTML mẫu Trước/Sau, kiểm đủ 4 sơ đồ có nhãn — Test: ảnh lưu ở `docs/tdq/qc/` và mô tả thấy 4 sơ đồ
  - Dùng: `tdq-browser-test` (mcp)
  - Để: mở HTML preview, chụp ảnh desktop; probe cổng 9222 trước, thiếu thì báo user bật
  - Ra: `docs/tdq/qc/2026-11-02-1157-nang-cap-spec-subagent-preview.png`
  - Kiểm: file ảnh tồn tại, mô tả liệt kê 4 tiêu đề sơ đồ
  - Không dùng cho: sửa HTML hay candidate
- [x] **T3.3** (e6m) Soát diff theo Ponytail ultra — Test: `tdq-lean` không nêu phần xoá được; `git diff --stat -- scripts/` rỗng
  - Dùng: `tdq-lean`
  - Để: review diff của request
  - Ra: kết luận ghi vào file qc
  - Kiểm: `git diff --stat dev -- scripts/` không có dòng nào
  - Không dùng cho: sửa code ngoài vùng `Chạm:`
- [x] **T3.4** (e10m) QC độc lập (`muc_qc=ultra`) — Test: agent `tdq-qc-tester` trả PASS có bằng chứng

## Cụm song song

Cụm A: T1.1 (hook). Cụm B: T2.1, T2.2, T2.3, T2.4 (luật) — không chung file với cụm A, các task trong cụm B cũng không chung file trừ `tests/test_luat_subagent_pr.py` (T2.3, T2.4). P3 chạy sau cả hai cụm.

## Luật file nóng

`tests/test_luat_subagent_pr.py` do T2.3 và T2.4 cùng chạm → một chủ ghi duy nhất: cùng một người làm T2.3 rồi T2.4.

## Px — Log & test bắt buộc

Log: BỎ — nhánh chặn ghi qua `block()` có sẵn (sổ turn + lý do trả về host), không thêm kênh log.

- [x] **Tx.2** (e2m) Unit test từng thành phần chạy bằng một lệnh — Test: `python -m pytest tests/test_edit_gate.py tests/test_spec_template.py tests/test_archify_workflow_contract.py tests/test_luat_subagent_pr.py -q`

## Definition of Done

Trỏ về §6 của spec:

- [x] Q1 Spec template buộc mục Trước/Sau do sơ đồ dẫn — `python -m pytest tests/test_spec_template.py -q`
- [x] Q2 Pipeline chuyên sâu ra 1 HTML Trước/Sau và binding hiện hành — `python scripts/tdq_archify.py verify --document docs/tdq/spec/2026-11-02-1157-nang-cap-spec-subagent.md --manifest docs/tdq/spec/2026-11-02-1157-nang-cap-spec-subagent-preview.manifest.json`
- [x] Q3 Pipeline nhanh cùng luật — `python -m pytest tests/test_archify_workflow_contract.py -q`
- [x] Q4 Subagent ghi src trước implement bị chặn — `python -m pytest tests/test_edit_gate.py -q -k subagent_spec_src`
- [x] Q5 Subagent vẫn ghi được report/log — `python -m pytest tests/test_edit_gate.py -q -k subagent_docs`
- [x] Q6 Luồng cũ giữ nguyên — `python scripts/tdq_test.py tron-bo`
- [x] Q7 Luật subagent và luật DoD có mặt — `python -m pytest tests/test_luat_subagent_pr.py tests/test_spec_template.py -q -k "subagent or dod"`
- [x] Q8 Report có thân PR soạn sẵn — `python -m pytest tests/test_luat_subagent_pr.py -q -k pr`
- [x] Q9 HTML mẫu đọc được bằng mắt — ảnh `docs/tdq/qc/2026-11-02-1157-nang-cap-spec-subagent-preview.png` tồn tại, mô tả đủ 4 sơ đồ
- [x] Q10 Diff tối thiểu — `git diff --stat dev -- scripts/` rỗng và `tdq-lean` không nêu phần xoá được

## QC vòng 1 — fix

- [x] **QC1.1** (e8m) Q9 FAIL: sơ đồ có `lane` render SVG 0×0 và giao diện mặc định `zh-CN`. Bỏ `lane` khỏi candidate, thêm `@meta locale=en`; ghi 2 điều này vào `archify-ba.md`; render + bind lại — Test: ảnh chụp thấy 4 sơ đồ có kích thước > 0 và `document.documentElement.lang == "en"`; test khoá `locale=en` trong `archify-ba.md`
  - Chạm: `skills/tdq-spec/references/archify-ba.md`, `tests/test_archify_workflow_contract.py`
- [x] **QC1.2** (e5m) QC độc lập D2 + D4: §2c template còn "Bắt buộc có sơ đồ Mermaid" (nay Mermaid là dự phòng); docstring `edit_gate.py` còn "blocks exactly 1 case" — Test: test khoá "Mermaid dự phòng" trong template; `python -m pytest tests/test_spec_template.py tests/test_edit_gate.py -q`; token template ≤ 3500
  - Chạm: `skills/tdq-spec/references/spec-template.md`, `hooks/scripts/edit_gate.py`, `tests/test_spec_template.py`

## QC vòng 2 — fix

QC-F1 `tron-bo`: 9 failed, 3954 passed, 10 skipped (17:18). 7 lỗi do request này, 2 lỗi `test_archify_e2e` do browser-check native.

- [x] **QC2.1** (e10m) Sửa 4 lỗi do request: (a) `muc-luc-dong` cũ ở `report-template.md`, `spec-template-huong-dan.md` → `doc_index.py`; (b) marker `ponytail:` thiếu dấu phẩy ceiling/upgrade; (c) câu §6 đặt giữa tiêu đề và bảng làm `test_luat_dung` đọc sai dòng → dời xuống dưới bảng; (d) neo L140 khoá câu cũ của §9 → trả câu cũ nguyên văn, câu mới thành dòng riêng — Test: `python -m pytest tests/test_doc_index.py tests/test_kiem_no_marker.py tests/test_luat_dung.py tests/test_luat_skill.py -q`
  - Chạm: `skills/tdq-build/references/report-template.md`, `skills/tdq-spec/references/spec-template-huong-dan.md`, `skills/tdq-spec/references/spec-template.md`, `skills/tdq-conventions/SKILL.md`, `hooks/scripts/edit_gate.py`, `docs/tdq/audit/luat-hien-co.md`
  - Ghi chú: (a)(b)(c) xong, luat-hien-co cập nhật 26 số dòng neo; còn R6 SKILL.md 193 > 192 → gộp con trỏ vào dòng L140 cũ.
