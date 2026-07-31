# SPEC — Audit tổng thể TDQ workflow 0.6.0 (conflict, edge case, robustness model thấp)

Ngày: 2026-07-31 · Bản: 1.1 · Request: ../requests/2026-07-31-audit-full-workflow.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: rà toàn bộ plugin tdq-workflow 0.6.0 theo 3 lớp (review tĩnh chéo →
  2 sample E2E engine thật → fix), ra một sổ audit liệt kê MỌI issue tìm được
  (note → nguyên nhân gốc → trạng thái fix), fix hết issue mức nghiêm trọng/vừa
  trong chính request này, và đóng 2 việc PENDING của 0.6.0.
- Trong phạm vi:
  - Review tĩnh: 6 skill SKILL.md + toàn bộ `skills/*/references/` (13 file),
    7 agent def, 7 script `scripts/*.py` + 2 sample, 5 hook + `_common.py` +
    hooks.json, portable/, CLAUDE.md §10 — chấm theo 3 trục MAST (spec ambiguity /
    coordination / verification gap) + trục "đủ tường minh cho model tham số thấp".
  - Sample E2E S1: lane quick external trọn vòng trong sandbox, engine `agy`,
    model `gpt-oss-120b-medium` (tiêu chí: slug open-weights duy nhất trong list —
    proxy gần nhất cho model local; nếu preflight slug này hỏng → dùng
    `gemini-3.5-flash-low`, slug flash đời thấp nhất).
  - Sample E2E S2: lane full mini mode main trong sandbox + 3 nhánh sự cố:
    approve mơ hồ, init đè request dở, engine hỏng → fallback.
  - PENDING 0.6.0: MỘT run deep search hybrid mới duy nhất phục vụ cả hai việc —
    (a) đo lại token E2E sau fix QC1.1, mục tiêu ≤250k; (b) verify trigger agent
    type `search-scout` (scout chính là slot 2 của run đó; đã thấy xuất hiện sau reload).
  - Fix issue mức S (sai kết quả/kẹt flow) và M (gây hiểu sai/thiếu bằng chứng)
    tìm được, red→green. Issue mức L (cosmetic) chỉ note + đề xuất.
- NGOÀI phạm vi: tích hợp engine local mới (ollama…); đổi kiến trúc state machine;
  viết thêm tính năng mới ngoài fix; sửa các plugin khác ngoài tdq-workflow.

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Sổ audit findings (issue → nguyên nhân → severity S/M/L → fix/đề xuất) | `docs/tdq/qc/2026-07-31-audit-full-workflow.md` (mục Findings) | Mỗi finding có đủ 4 trường; mọi finding S/M có task fix trong plan |
| 2 | Fix issue #1 đã biết: regex `\1` trong `tdq_state.py:576` + regenerate phases.md | `scripts/tdq_state.py`, `skills/tdq-conventions/references/phases.md`, `portable/workflow/phases.md` | `phases-doc` không còn literal `\1`; 3 dòng lệnh analyze/spec/plan đầy đủ; unit test mới xanh |
| 3 | Sample E2E S1 (quick external, agy `gpt-oss-120b-medium`) + log bằng chứng | sandbox `TDQ_PROJECT_DIR` + tóm tắt trong file audit; trích log xong thì XOÁ sandbox | Vòng quick chạy hết: init→mini-plan→approve→worktree→engine→verify→merge; report JSON validate rỗng lỗi; kết luận robustness model thấp có bằng chứng |
| 4 | Sample E2E S2 (full mini mode main + 3 nhánh sự cố) + log bằng chứng | sandbox `TDQ_PROJECT_DIR` + tóm tắt trong file audit; trích log xong thì XOÁ sandbox | Đủ chuỗi phase analyze→…→idle; 3 nhánh sự cố cho kết quả đúng luật (mơ hồ→hỏi, đè→cảnh báo, engine hỏng→fallback ghi nhận) |
| 5 | MỘT run deep search hybrid mới: đo token sau fix QC1.1 + verify trigger `search-scout` (slot 2 gọi qua Agent type `tdq-workflow:search-scout`) | run-dir mới `docs/tdq/research/search/<run-id>/` + bảng token trong file audit | Tổng `<usage>` của MỌI slot thực chạy ≤ 250.000 và agent-2.json đúng format file agent; token vượt → task fix tiếp trong plan |
| 6 | Fix các issue S/M khác từ review tĩnh + E2E | file theo từng issue + test | Suite unittest toàn phần xanh; doc_lint các file sửa exit 0 |
| 7 | Report tổng ≤50 dòng | `docs/tdq/reports/2026-07-31-audit-full-workflow.md` | `wc -l` ≤ 50; doc_lint exit 0 |

## 3. Cách tiếp cận & lý do

- Chọn: audit 3 lớp (tĩnh → động → fix) với khung chấm MAST + trục model-thấp;
  sample động chạy engine thật trong sandbox cách ly bằng `TDQ_PROJECT_DIR`.
- Vì: MAST (NeurIPS 2025) chỉ ra 3 nhóm gốc lỗi hệ đa agent — spec ambiguity 33%,
  coordination breakdown, verification gap (nguồn: research/ cùng slug); review
  tĩnh bắt nhóm 1, E2E thật bắt nhóm 2–3; prompt cho model thấp phải "lệnh cụ thể,
  format output tường minh" (web.dev, thirdeyedata — research/ cùng slug).
- Đã loại: chỉ review tĩnh (không lộ issue động, user yêu cầu sample thật);
  mock engine (không đo được model thấp thật); thêm engine local (user chốt tách
  request riêng).

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | plugin:tdq-workflow | NỀN | Khung luật đang chạy + đối tượng audit lớp 1 |
| tdq-intake | plugin:tdq-workflow | NỀN | Khung request này + đối tượng audit lớp 1 |
| tdq-spec | plugin:tdq-workflow | NỀN | Khung spec này + đối tượng audit lớp 1 |
| tdq-plan | plugin:tdq-workflow | NỀN | Khung plan sắp tới + đối tượng audit lớp 1 |
| tdq-build | plugin:tdq-workflow | NỀN | Khung build/QC/report + đối tượng audit lớp 1 |
| tdq-status | plugin:tdq-workflow | KHÔNG | spec §3 đã chọn cách khác tốt hơn — trạng thái đọc thẳng qua `tdq_state.py next`; file SKILL.md của nó vẫn bị audit ở lớp 1 |
| tavily-best-practices | plugin:tavily | DÙNG | Đầu ra 5: deep search E2E (scout dùng tavily) + spot-check URL khi cần |
| graphify | user | DÙNG | Cuối turn đổi code: `graphify extract . --code-only` |
| skill-creator | plugin:skill-creator | KHÔNG | khác lĩnh vực — không tạo skill mới |
| plugin-dev (7 skill) | plugin:plugin-dev | KHÔNG | khác lĩnh vực — không scaffold plugin/hook mới, chỉ fix file có sẵn |
| hookify | plugin:hookify | KHÔNG | khác lĩnh vực — hook plugin đã có sẵn khung riêng |
| playground / frontend-design / dataviz | plugin khác | KHÔNG | khác lĩnh vực — không có UI |
| remember / claude-md-management | plugin khác | KHÔNG | khác lĩnh vực — không thuộc đầu ra audit |
| mcp-server-dev (3 skill) | plugin:mcp-server-dev | KHÔNG | khác lĩnh vực — không xây MCP server |

Agent dùng: `search-runner`, `search-scout` (đầu ra 5), `agy-runner` (đầu ra 3),
`tdq-reviewer` (review spec/plan), `tdq-qc-tester` (QC độc lập nếu cần).

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: sample E2E dùng log sẵn có của wrapper
  (`run.log`, `agent-*.log`, external `run.log`); bằng chứng audit trích từ log thật.
- Không placeholder: mọi finding phải có bằng chứng (lệnh + output hoặc trích file).
- Mỗi fix có unit test riêng (red→green), chạy được bằng
  `python3 -m unittest discover -s tests`.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Sample E2E đụng nhầm state/doc thật | Hỏng request đang chạy | Mọi lệnh state trong sample đặt `TDQ_PROJECT_DIR=<sandbox>` ngay trên lệnh; sandbox là git repo riêng trong scratchpad |
| Engine ngoài (agy/codex) chậm/hết quota giữa sample | S1/đầu ra 5 kẹt | Timeout sẵn có của wrapper (540s/attempt, ≤3 attempt); hỏng ≥3 → ghi nhận finding + fallback Claude đúng luật rồi đi tiếp |
| Model thấp nhất làm sai task S1 | Không phải bug workflow | Phân biệt rõ trong finding: lỗi CONTRACT (fix) vs lỗi NĂNG LỰC model (ghi nhận + kiểm fallback hoạt động) |
| Token deep search vẫn >250k sau fix | DoD đầu ra 5 fail | QC-loop: thêm task fix (giảm verbosity contract) ngay trong plan, không cần duyệt lại |
| Audit tự sửa file khung đang chạy (skill/hook) | Hành vi phiên đổi giữa chừng | Fix file skill/agent chỉ có hiệu lực phiên sau — note rõ "PENDING reload" trong QC như tiền lệ 0.5.0/0.6.0, không tự nhận là đã verify |
| Sổ findings phình to, fix lan man | Vượt 1 turn build | Chỉ fix S/M; L note lại; plan chốt số task cứng, phát sinh thì QC-loop |
| Tổng wall-clock (S1 external ≤3×540s + S2 + 1 run deep search + suite) vượt 1 turn | Build kẹt giữa chừng | Chạy S1/deep-search bằng agent nền/song song ngay đầu build; ngân sách cứng: S1 ≤ 30 phút, run deep search ≤ 25 phút; quá ngân sách → ghi finding, chuyển nhánh degrade/fallback theo luật sẵn có rồi đi tiếp |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Suite toàn phần | `python3 -m unittest discover -s tests` | OK, 0 fail; số test ≥ 338 + số test mới |
| Q2 | Doc lint | `doc_lint.py` từng file docs sửa + `--pair spec plan` | exit 0 |
| Q3 | Sổ findings đủ trường | đọc `qc/<slug>.md` mục Findings | 100% finding có note/nguyên nhân/severity/trạng thái; mọi S/M có task fix đã tick |
| Q4 | Fix `\1` phases.md | `python3 scripts/tdq_state.py phases-doc \| ! grep -q '\\1'` + test mới | Chuỗi lệnh exit 0 (không còn literal `\1`); test xanh |
| Q5 | S1 quick external model thấp | log + report JSON trong sandbox; validate: `python3 -c "import sys,json; sys.path.insert(0,'scripts'); from external_task import validate_report; print(validate_report(json.load(open('<report>'))))"` | Vòng quick external hoàn chỉnh; validate in `[]` (rỗng lỗi); kết luận contract-vs-năng-lực có bằng chứng |
| Q6 | S2 full mini + 3 nhánh sự cố | log sandbox | Chuỗi phase đi hết đến idle; 3 nhánh sự cố ra đúng hành vi luật |
| Q7 | Token deep search ≤250k | tổng `<usage>` của MỌI slot thực chạy trong run-dir mới | ≤ 250.000 |
| Q8 | Trigger search-scout | slot 2 của run Q7 gọi qua Agent type `tdq-workflow:search-scout` | agent chạy, agent-2.json đúng format file agent |
| Q9 | Log service các sample | kiểm file log sinh ra + thử `TDQ_SEARCH_LOG=0`/`TDQ_EXTERNAL_LOG=0` một nhánh | Log bật mặc định đủ trường ISO; biến tắt hoạt động |
| Q10 | Report | `wc -l reports/<slug>.md` | ≤ 50 dòng, doc_lint exit 0 |

DoD: Q1–Q10 PASS có bằng chứng trong `qc/<slug>.md`; mọi finding S/M đã fix + tick
(tick = unit test/file-level pass; fix vào skill/agent/hook đang chạy thì verify
hành vi runtime ghi "PENDING reload" như tiền lệ 0.5.0/0.6.0, không tính fail DoD);
finding L có ghi chú đề xuất; sandbox đã xoá sau khi trích bằng chứng; working log
đã append; user đã được hỏi về commit.

## 7. Câu hỏi còn mở

(RỖNG — 3 quyết định scope đã chốt ở questions/ cùng slug vòng 1.)
