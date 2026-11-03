# PLAN — Eval chất lượng skill và plugin TDQ
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Ngày: 2026-11-01 · Spec: ../spec/2026-11-01-1854-eval-chat-luong-skill.md (bản 1.0, ĐÃ DUYỆT) · Lane: full · QC: ultra
Spec được duyệt bằng “duyệt spec”; manifest preview digest `9dc2d3cb0e1099a49caf3320daff5ef80251ed32077afd40a895bdba9ce79aa5`.
Mode thực thi: subagent — ĐÃ CHỌN bằng “1a”; mô phỏng `tdq_bench.py simulate` (hệ số 1.5, 13 task, 8 đợt) cho thấy đội mất 24.5 phút so với `main` 26.5 phút, chênh lệch 1.9 phút
Trạng thái plan: HOÀN THÀNH

## Quy tắc thi hành (áp cho mọi task)
1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Mỗi bước: `tdq_test.py vung-cham`; trọn bộ chỉ ở QC.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. Tuân thủ 6 mã cấm cơ học (`ANTI-1` Fake Red, `ANTI-2` Blind Assertion, `ANTI-3` Dirty State Git, `ANTI-4` Late Tick, `ANTI-5` Raw Dump, `ANTI-6` Broad Area).
8. Giữ nguyên mặc định Ponytail `ultra` và bảo toàn 11 worktree cũ; không tự khởi chạy phiên gọi model trả phí trong lúc chạy test, cổng kiểm hay QC.

Lệnh PowerShell từ gốc repo dùng lại trong các dòng kiểm:

```powershell
$h = 'docs/tdq/artifacts/2026-10-27-1846-kiem-chung-tang-toc/safe_run.py'
$e = 'docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill'
```

## Thiết kế Trước vs Sau
| Khía cạnh | Hiện trạng (Trước) | Thiết kế mới (Sau) |
|---|---|---|
| Luồng thực thi | `scripts/tdq_eval.py` cố định 2 snapshot lịch sử `viet`/`lai`, chỉ gọi Claude CLI, bị loại khỏi gói phát hành plugin; workflow chưa có cổng kiểm kế hoạch/chứng cứ Eval cho thay đổi hành vi skill/hook/plugin | Tách core thuần (`tdq_eval_contract.py`), 2 host adapter Windows (`tdq_eval_hosts.py`) và CLI (`tdq_skill_eval.py`) được đóng gói kèm plugin; gắn cổng kiểm kế hoạch trước `implement` và chứng cứ trước `report` mà không tự gọi model |
| Thành phần chạm | `scripts/tdq_eval.py`, `scripts/tdq_state.py`, `scripts/build_portable.py`, `tests/test_tdq_eval.py`, `tests/test_eval_manifest.py` | Thêm `scripts/tdq_eval_contract.py`, `scripts/tdq_eval_hosts.py`, `scripts/tdq_skill_eval.py`, `evals/skill-quality/`, `skills/tdq-build/references/skill-eval.md` và bộ test/verifier tương ứng |

*Đối chiếu sơ đồ kiến trúc:* Tham chiếu trực tiếp bản xem trước [2026-11-01-1854-eval-chat-luong-skill-preview.html](../spec/2026-11-01-1854-eval-chat-luong-skill-preview.html) và manifest [2026-11-01-1854-eval-chat-luong-skill-preview.manifest.json](../spec/2026-11-01-1854-eval-chat-luong-skill-preview.manifest.json) đã duyệt ở spec §2c.

## P0 — Khóa chứng cứ và cổng kiểm
- [x] **T0.1** (e8m) Tạo verifier fail-closed `verify_scope.py` và `evidence-index.json` ánh xạ `O1`–`O7`, `Q1`–`Q10`, kiểm tra binding Archify preview cùng `analysis-baseline.json`, và tự kiểm phát hiện thiếu chứng cứ, lệch SHA nguồn hoặc false PASS — Test: `python3 docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/verify_scope.py --self-test`
  - Chạm: `docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/verify_scope.py`, `docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/evidence-index.json` → file mới trong thư mục artifact request, chưa node nào phụ thuộc
  - Dùng: `archify`
  - Để: kiểm chứng liên kết preview HTML và manifest digest của spec đã duyệt trước khi triển khai mã nguồn, nạp skill TRƯỚC bước đỏ
  - Ra: kết quả xác thực binding preview trong `docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/evidence-index.json`
  - Kiểm: `python3 docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/verify_scope.py --self-test`
  - Không dùng cho: sinh lại thiết kế kiến trúc khác với spec đã duyệt hoặc thay thế kiểm tra mã nguồn

**Xong P0 khi**: `verify_scope.py --self-test` đạt `0` lỗi và từ chối đúng khi thiếu chứng cứ `Q1`–`Q10`.

## P1 — Contract thuần và Host Adapters Windows
- [x] **T1.1** (e14m) Xây dựng module thuần `scripts/tdq_eval_contract.py` (không I/O tiến trình): classifier target skill/hook/plugin so với docs thuần/code ứng dụng, schema `eval-plan`, validator danh tính đối chứng (`host`, `model`, `permission_profile`, `scorer_version`, `corpus_version`, `check_set`, `tool_aliases`, `cache_profile`), bộ chuẩn hóa 3 nhóm chỉ số giữ `null`/`unavailable` (không quy thiếu thành `0.0`, tách `observed_usage`/`rate_estimate`/`provider_billed`) và hàm khuyến nghị tất định `KEEP`/`TRIM`/`DROP`/`INCONCLUSIVE` theo từng cell — Test: `python3 -m pytest -q tests/test_tdq_eval_contract.py`
  - Chạm: `scripts/tdq_eval_contract.py`, `tests/test_tdq_eval_contract.py` → file mới, cung cấp contract thuần cho `tdq_skill_eval.py`, `tdq_eval.py` và `tdq_state.py`
  - Cần: T0.1
- [x] **T1.2** (e16m) Xây dựng `scripts/tdq_eval_hosts.py` cho hai host Windows (`Claude Code` và `Codex`) tái dùng `scripts/tdq_transcript.py` và `OwnedProcessJob` (`scripts/tdq_test_process.py`): native preflight không gọi model, cô lập `HOME`/workspace/config mỗi trial, kiểm soát timeout/cleanup/retry trong trần đã khóa và chuẩn hóa raw trace streaming kèm hash — Test: `python3 -m pytest -q tests/test_tdq_eval_hosts.py`
  - Chạm: `scripts/tdq_eval_hosts.py`, `tests/test_tdq_eval_hosts.py` → file mới, gọi `tdq_transcript.py` và `tdq_test_process.py` (nguồn: `graphify affected "tdq_test_process" --depth 2`)
  - Cần: T1.1

**Xong P1 khi**: toàn bộ bài kiểm tra đơn vị của `tdq_eval_contract.py` và `tdq_eval_hosts.py` xanh, chặn đủ `4/4` ca lệch danh tính và cô lập/dọn tiến trình fixture trên Windows.

## P2 — CLI Eval mới, tương thích lịch sử và bộ ca chuẩn
- [x] **T2.1** (e15m) Tạo entry point `scripts/tdq_skill_eval.py` (`plan`, `check`, `run`, `report` tách biệt; `plan`/`check`/`report` không gọi model; lập lịch AB/BA cân bằng và báo cáo JSON/Markdown theo từng cell `host`/`model`) và nối `scripts/tdq_eval.py` dùng chung validator/contract mới mà vẫn giữ nguyên tương thích 60 bản ghi lịch sử (`historical_unverified`) cùng `rescore_append_only` — Test: `python3 -m pytest -q tests/test_tdq_skill_eval.py tests/test_tdq_eval.py tests/test_eval_manifest.py`
  - Chạm: `scripts/tdq_skill_eval.py`, `scripts/tdq_eval.py`, `tests/test_tdq_skill_eval.py`, `tests/test_tdq_eval.py`, `tests/test_eval_manifest.py` → ảnh hưởng `chay_phien`, `chay_va_cham`, `chay` (nguồn: `graphify affected "chay_phien" --depth 2`)
  - Cần: T1.1, T1.2
- [x] **T2.2** (e12m) Xây dựng bộ ca chuẩn `evals/skill-quality/corpus.json` (tách tập `dev` và `holdout`, ca dương kích hoạt skill, ca âm không kích hoạt, ca sửa docs thuần/code app ngoài scope, fixture trace lỗi/thiếu usage) kèm bài kiểm tra tính toàn vẹn, phân tách `mechanism` với `agent-effectiveness` và không mớm đáp án trong prompt — Test: `python3 -m pytest -q tests/test_skill_quality_corpus.py`
  - Chạm: `evals/skill-quality/corpus.json`, `tests/test_skill_quality_corpus.py` → file mới cho bộ ca mẫu và kiểm định grader
  - Cần: T1.1
  - Dùng: `skill-creator`
  - Để: rà soát ranh giới trigger dương/âm, tính bất biến của rubric và nguyên tắc forward-test không mớm đáp án trong bộ ca `evals/skill-quality/`, nạp skill TRƯỚC bước đỏ
  - Ra: bộ ca `evals/skill-quality/corpus.json` và bài kiểm tra `tests/test_skill_quality_corpus.py`
  - Kiểm: `python3 -m pytest -q tests/test_skill_quality_corpus.py`
  - Không dùng cho: thay thế kiểm chứng runtime hoặc tự động gọi LLM-as-judge

**Xong P2 khi**: `tdq_skill_eval.py` chạy trọn vẹn `plan`/`check`/`run` (fixture)/`report`, các bài test cũ của `tdq_eval.py` và `test_eval_manifest.py` xanh, và bộ ca `evals/skill-quality/` đạt chuẩn.

## P3 — Cổng kiểm Workflow, tài liệu và Đóng gói plugin
- [x] **T3.1** (e14m) Tích hợp cổng kiểm Eval vào `scripts/tdq_state.py` (kiểm `eval-plan` hợp lệ trước khi qua `implement` khi chạm target hành vi skill/hook/plugin; kiểm chứng cứ khớp source hash và danh tính trước `report`; hỗ trợ `WAIVED_USER` có lý do/nguồn/phạm vi qua CLI tách biệt với `PASS`), cập nhật hướng dẫn tại `skills/tdq-intake/SKILL.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-spec/references/spec-template.md`, `skills/tdq-plan/SKILL.md`, `skills/tdq-build/SKILL.md`, `skills/tdq-build/references/qc.md` — Test: `python3 -m pytest -q tests/test_eval_workflow_gate.py`
  - Chạm: `scripts/tdq_state.py`, `skills/tdq-intake/SKILL.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-spec/references/spec-template.md`, `skills/tdq-plan/SKILL.md`, `skills/tdq-build/SKILL.md`, `skills/tdq-build/references/qc.md`, `tests/test_eval_workflow_gate.py` → ảnh hưởng các caller của `tdq_state` (nguồn: `graphify affected "tdq_state" --depth 2`)
  - Cần: T2.1, T2.2
- [x] **T3.2** (e12m) Cập nhật `scripts/build_portable.py` và viết `skills/tdq-build/references/skill-eval.md` để đóng gói `tdq_eval_contract.py`, `tdq_eval_hosts.py`, `tdq_skill_eval.py` vào bản phát hành plugin (giữ loại trừ `tdq_eval.py` lịch sử, `evals/` và `tests/`), cập nhật khóa `docs/tdq/token-budget.json` và kiểm chứng chạy CLI từ gói cài đặt sạch ngoài repo — Test: `python3 -m pytest -q tests/test_build_portable.py`
  - Chạm: `scripts/build_portable.py`, `skills/tdq-build/references/skill-eval.md`, `docs/tdq/token-budget.json`, `tests/test_build_portable.py` → đóng gói bundle phát hành và khóa ngân sách token tài liệu
  - Cần: T3.1

**Xong P3 khi**: cổng state chặn đúng các ca thiếu/stale `eval-plan` hoặc chứng cứ, `doc_lint.py` và `token_budget.py --kiem` đạt `0` lỗi, và gói plugin chạy được `tdq_skill_eval.py` độc lập ngoài repo.

## P4 — Log & test bắt buộc
- [x] **T4.1** (e6m) Log service bật mặc định (ISO timestamp, mức log, `experiment`/`cell`/`trial`/`reason`/`cleanup`, tắt sạch qua `TDQ_LOG=0` hoặc `TDQ_EVAL_LOG=0`, không ghi lộ prompt/payload/token/secret) — Test: `python3 -m pytest -q tests/test_eval_logging.py`
  - Chạm: `tests/test_eval_logging.py` → file test mới kiểm định hợp đồng log của `tdq_eval_contract.py`, `tdq_eval_hosts.py`, `tdq_skill_eval.py`
  - Cần: T3.2
- [x] **T4.2** (e8m) Unit test và regression xuyên tầng cho từng thành phần `O1`–`O7` và các biên (nonfinite, duplicate trial, path traversal/symlink, branch di chuyển, alias model chưa phân giải, lệch quyền/cache, sửa holdout, lỗi transport có usage dở dang, vượt trần kích thước event, ô model chưa đo) — Test: `python3 -m pytest -q tests/test_eval_contracts_e2e.py`
  - Chạm: `tests/test_eval_contracts_e2e.py` → file test mới kiểm định tích hợp xuyên suốt các module Eval
  - Cần: T4.1

**Xong P4 khi**: cả `tests/test_eval_logging.py` và `tests/test_eval_contracts_e2e.py` đều PASS cùng vùng chạm.

## P5 — QC ultra, runtime smoke và báo cáo nghiệm thu
- [x] **T5.1** (e18m) Chạy bộ kiểm tra trọn bộ (`tdq_test.py tron-bo`) trên mã nguồn cuối sau khi đồng bộ trạng thái kiến trúc nếu cần, lưu receipt và kết quả vào thư mục artifact của request — Test: `python3 scripts/tdq_test.py tron-bo --repo . --workers 1 --fresh --reuse off --timeout-seconds 1800`
  - Cần: T4.2
  - Tiến độ: tron-bo đang chạy nền (ID: bv1ak5kds); hoàn thiện các kịch bản kiểm chứng runtime.
- [x] **T5.2** (e10m) Tạo và chạy kịch bản smoke/runtime hữu hạn `runtime_checks.py` (mỗi kịch bản trần `120s`, không gọi LLM trả phí): preflight thực tế 2 host Windows, process fixture kiểm timeout/cleanup/descendant kill, lập lịch AB/BA, xuất report mẫu JSON/MD ghi rõ `synthetic/offline` và chạy CLI từ gói plugin tách rời — Test: `python3 docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/runtime_checks.py --scenario-timeout 120 --output docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/runtime.json`
  - Chạm: `docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/runtime_checks.py` → script kiểm chứng runtime trong artifact request
  - Cần: T5.1
- [x] **T5.3** (e8m) Chạy reviewer độc lập (`tdq-reviewer`) đối chiếu diff, source, DoD `Q1`–`Q10`, kiến trúc và ranh giới module; xử lý triệt để mọi finding correctness nếu có và lưu biên bản review — Test: `python3 docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/verify_scope.py Q9`
  - Cần: T5.2
- [x] **T5.4** (e8m) Viết biên bản QC `docs/tdq/qc/2026-11-01-1854-eval-chat-luong-skill.md` và báo cáo nghiệm thu `docs/tdq/reports/2026-11-01-1854-eval-chat-luong-skill.md` (ghi rõ provenance, coverage, comparability, giới hạn `synthetic/offline` và khuyến nghị), xác nhận toàn bộ `Q1`–`Q10` — Test: `python3 docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/verify_scope.py --all`
  - Cần: T5.3

**Xong P5 khi**: `verify_scope.py --all` báo PASS toàn bộ `Q1`–`Q10` và hồ sơ QC/report hoàn chỉnh.

## Ánh xạ đầu ra và preview
| Spec §2 | Task | Module §2b |
|---|---|---|
| O1 | T1.1, T4.2 | Contract thuần (`scripts/tdq_eval_contract.py`) |
| O2 | T2.1, T4.1 | CLI và compatibility (`scripts/tdq_skill_eval.py`) |
| O3 | T1.2, T5.2 | Host I/O (`scripts/tdq_eval_hosts.py`) |
| O4 | T3.1 | Workflow (`scripts/tdq_state.py`, `skills/tdq-*`) |
| O5 | T2.1, T2.2 | CLI và compatibility (`scripts/tdq_eval.py`, `evals/skill-quality/`) |
| O6 | T3.2, T5.2 | Packaging (`scripts/build_portable.py`, `skills/tdq-build/references/skill-eval.md`) |
| O7 | T0.1, T5.1–T5.4 | Chứng cứ (`docs/tdq/artifacts/`, `qc/`, `reports/`) |

## Cụm song song
Nếu chạy mode `subagent`: `T0.1` chạy đầu tiên; sau `T0.1` đến `T1.1`; sau `T1.1` thì `T1.2` và `T2.2` không giao nhau về vùng file (`scripts/tdq_eval_hosts.py` so với `evals/skill-quality/corpus.json`) nên chạy song song cùng một đợt; `T2.1` chạy sau khi cả `T1.1` và `T1.2` hoàn tất; tiếp theo chuỗi `T3.1` → `T3.2` → `T4.1` → `T4.2` → `T5.1` → `T5.2` → `T5.3` → `T5.4` chạy tuần tự để giữ một chủ ghi cho `docs/tdq/token-budget.json` và không chạy chồng các bước chứng nhận Full/runtime.

## Luật file nóng
Không có file nóng (mỗi file mã nguồn và file test trong `Chạm:` chỉ thuộc đúng một task duy nhất). Riêng `docs/tdq/token-budget.json` được gom về một chủ ghi duy nhất ở `T3.2` (chạy sau `T3.1`) sau khi mọi chỉnh sửa dưới `skills/` đã hoàn tất.

## Definition of Done
Trỏ về §6 của spec (`Q1`–`Q10`), mỗi dòng kiểm bằng một lệnh tất định đọc chứng cứ đã khóa:

- [x] Q1 Plan và classifier nhận diện đúng thay đổi hành vi skill/hook/plugin trong repo và project, phát hiện thiếu/stale `eval-plan` và miễn đúng docs thuần/code app ngoài scope — `python3 docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/verify_scope.py Q1`
- [x] Q2 Danh tính đối chứng từ chối đủ 4/4 ca lệch `host`/`model`/`permission_profile`/`scorer_version` cùng `corpus`/`check_set`/`cache` và gắn nhãn `historical_unverified` cho bản ghi cũ — `python3 docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/verify_scope.py Q2`
- [x] Q3 Ba nhóm metrics (trigger, outcome quality, usage/time/retry/intervention) tách biệt, giữ `null`/`unavailable` thay vì `0.0` và phân biệt `observed_usage`/`rate_estimate`/`provider_billed` — `python3 docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/verify_scope.py Q3`
- [x] Q4 Hai adapter Windows (`Claude Code` và `Codex`) có preflight không gọi model, cô lập môi trường và quản lý timeout/cleanup/descendant bằng process fixture — `python3 docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/verify_scope.py Q4`
- [x] Q5 Lập lịch AB/BA cân bằng, resume/skip theo hash thí nghiệm, retry không vượt trần quota/trial và giữ nguyên raw trace append-only — `python3 docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/verify_scope.py Q5`
- [x] Q6 Báo cáo JSON/Markdown tách riêng từng cell `host`/`model` kèm khuyến nghị `KEEP`/`TRIM`/`DROP`/`INCONCLUSIVE` có guardrail và không tự sửa luật — `python3 docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/verify_scope.py Q6`
- [x] Q7 Gói phát hành plugin chạy được `tdq_skill_eval.py` ngoài repo nguồn mà không cần `tests/`/`evals/`/`tdq_eval.py` và vẫn giữ tương thích CLI/record lịch sử — `python3 docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/verify_scope.py Q7`
- [x] Q8 Cổng workflow trong `tdq_state.py` chỉ kiểm chứng cứ (không gọi model), log bật/tắt sạch và `WAIVED_USER` tách biệt với `PASS` — `python3 docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/verify_scope.py Q8`
- [x] Q9 Bộ test trọn bộ (`QC-F1`), hồi quy vùng chạm, runtime smoke và reviewer độc lập hoàn tất không còn lỗi correctness tồn đọng — `python3 docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/verify_scope.py Q9`
- [x] Q10 Tài liệu `skills/`, hướng dẫn `skill-eval.md`, binding Archify preview và kiểm tra fresher đạt `0` vi phạm `doc_lint.py` — `python3 docs/tdq/artifacts/2026-11-01-1854-eval-chat-luong-skill/verify_scope.py Q10`
