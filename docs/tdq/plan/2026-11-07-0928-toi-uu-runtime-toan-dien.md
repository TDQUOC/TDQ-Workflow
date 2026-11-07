# PLAN — Tối ưu thời gian xử lý TDQ Workflow

Ngày: 2026-11-07 · Spec: ../spec/2026-11-07-0928-toi-uu-runtime-toan-dien.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — ĐỀ XUẤT: mô phỏng 9 task main 18,3 phút, đội 10,2 phút (`Winner: đội`, chênh 8,1 phút); 4 task vùng độc lập có thể giao, 5 task leader giữ vì MCP/vùng khóa/phụ thuộc. Người dùng chốt khi duyệt.
Trạng thái plan: HOÀN THÀNH.

## Quy tắc thi hành

- Spec §2 và §6 đứng trên plan; tick `[~]` trước mỗi task, `[x]` ngay sau check xanh. Test đỏ thật trước sửa, không fake red. Mỗi thay đổi source chạy `tdq_test.py vung-cham`; full fresh cuối chỉ ở QC.
- Benchmark serial, nguồn/environment/fingerprint cố định, giữ failed samples; không lấy kết quả fixture thay production. Parity/latency trượt thì `lech add`, giữ default cũ, làm tiếp các task khác. Không cắt gate/HTML/B1, không cài mới hay bật eval. Không commit/push khi chưa được hỏi ở cuối.
- Preview planned `../spec/2026-11-07-0928-toi-uu-runtime-toan-dien-preview.html`: verify binding trước sửa code; sau sửa source kiểm Master freshness, không gán preview planned thành actual.

## Thiết kế Trước vs Sau

| Trước | Sau |
|---|---|
| SessionStart/LSP khởi động/doctor có outlier chưa đo đủ | Instrument cold/warm, proof health và fallback fresh có receipt |
| Finish rebuild Graphify đồng bộ sau code turn | Stale marker/on-demand chỉ khi query/QC freshness giữ nguyên; rollback per-turn |
| Full receipt có thể invalid vì concurrent writer | Fingerprint/barrier fail-closed, một full fresh cuối |
| Workers/cache/ledger/Read/lane dùng đường cũ | Benchmark parity, chỉ promote scope đạt; giảm overhead mà không cắt gate |

## P1 — Baseline và P0

- [x] **T1.1** (e35m) Đo baseline cùng source/env cho SessionStart/LSP/Graphify/full rerun và hook, giữ sample lỗi và nhãn partial — Test: `python -c "import pathlib; p=pathlib.Path('docs/tdq/artifacts/2026-11-07-0928-toi-uu-runtime-toan-dien/baseline.json'); assert p.is_file() and p.stat().st_size>0"` (baseline kèm receipt; span không bao quát ghi unavailable, không fake PASS)
  - Dùng: `LSP, Graphify, Grep` (mcp)
  - Để: pre-flight LSP/Graphify, refs `step_graphify` và `kich_hoat_nen`, map vùng vỡ lan trước sửa.
  - Ra: bảng vùng chạm trong `docs/tdq/brief/2026-11-07-0928-toi-uu-runtime-toan-dien.md` và receipt baseline O1.
  - Kiểm: `python scripts/tdq_lsp.py check`
  - Không dùng cho: thay đo latency bằng timeout hoặc graph stale.
- [x] **T1.2** (e40m) Đo và giảm SessionStart/LSP đường nóng bằng health proof/stamp/fallback fresh sau T1.1 — Test: `python -m unittest tests.test_auto_update_setup tests.test_tdq_lsp`
  - Chạm: `hooks/scripts/session_start.py`, `scripts/tdq_lsp.py`, `scripts/tdq_readiness.py`, `tests/test_auto_update_setup.py`, `tests/test_tdq_lsp.py` → caller `main()` và doctor (Graphify affected `kich_hoat_nen` depth 2, LSP refs).
  - Cần: T1.1
- [x] **T1.3** (e35m) Đo và thử Graphify stale marker/rebuild trước query hoặc QC sau T1.1; nếu không chứng minh freshness thì giữ synchronous — Test: `python -m unittest tests.test_tdq_finish`
  - Chạm: `scripts/tdq_finish.py`, `tests/test_tdq_finish.py` → `main()` gọi `step_graphify` (LSP refs + Graphify affected depth 2).
  - Cần: T1.1
- [x] **T1.4** (e40m) Thử source fingerprint/writer barrier tránh receipt full fresh vô hiệu sau T1.1, failure fail-closed — Test: `pytest tests/test_tdq_test_receipt.py tests/test_tdq_test_process.py`
  - Chạm: `scripts/tdq_test.py`, `scripts/tdq_test_receipt.py`, `tests/test_tdq_test_receipt.py`, `tests/test_tdq_test_process.py` → runner/receipt (LSP refs `run_with_receipt`, Graphify query theo module).
  - Cần: T1.1

## P2 — P1 benchmark và hook I/O

- [x] **T2.1** (e35m) Benchmark ≥3 cặp AB/BA/AB workers và ≥3 triplet off/cold/warm cache sau T1.4, chỉ promote scope hermetic đủ parity — Test: `python -m unittest tests.test_tdq_runtime_bench tests.test_tdq_test_receipt`
  - Chạm: `scripts/tdq_runtime_bench.py`, `tests/test_tdq_runtime_bench.py` → runner/receipt được đọc, không sửa `tdq_test.py` đang do T1.4 làm chủ.
  - Cần: T1.4
  - Dùng: `tdq_runtime_bench.py`, `tdq_test.py`
  - Để: chạy các sample tuần tự, verify parity và giữ receipt/failure O1/O3.
  - Ra: `docs/tdq/artifacts/2026-11-07-0928-toi-uu-runtime-toan-dien/` có sample/result đủ nguồn và bảng promotion.
  - Kiểm: `python scripts/tdq_runtime_bench.py verify docs/tdq/artifacts/2026-11-07-0928-toi-uu-runtime-toan-dien/workers.json`
  - Không dùng cho: coi fixture/historical sample là speedup đã chứng nhận hoặc bỏ full fresh QC.
- [x] **T2.2** (e25m) Đo và giảm parse ledger theo tail/index, replay decision gate 100% so baseline; mismatch quay full parse — Test: `python -m unittest tests.test_search_observe tests.test_read_gate tests.test_search_gate`
  - Chạm: `hooks/scripts/search_observe.py`, `hooks/scripts/read_gate.py`, `tests/test_search_observe.py`, `tests/test_read_gate.py`, `tests/test_search_gate.py` → ledger phục vụ search/read gate (LSP refs `ghi_so`, Graphify query hook).
  - Cần: T1.1

## P3 — P2 luồng đọc và lane

- [x] **T3.1** (e20m) Khóa batch chỉ cho Read độc lập, giữ mutation/approval tuần tự và test luật — Test: `python scripts/doc_lint.py skills/tdq-build/references/runtime-speed.md`
  - Chạm: `skills/tdq-build/references/runtime-speed.md`, `tests/test_compliance_protocol.py` → policy được build và QC dùng.
  - Cần: T1.1
- [x] **T3.2** (e25m) So route tier `nhỏ`/quick/deep với bốn điều kiện và B1, giữ route cũ khi cohort <10/bucket — Test: `python scripts/doc_lint.py skills/tdq-intake/SKILL.md skills/tdq-intake/references/quick-lane.md`
  - Chạm: `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/quick-lane.md` → intake route; `tests/test_compliance_protocol.py` do T3.1 làm chủ, T3.2 không sửa.
  - Cần: T3.1

## P4 — QC và report

- [x] **T4.1** (e25m) Tổng hợp O1–O4 và QC Q1–Q5: kiểm nguồn, full fresh cuối, lint và render report Markdown + Archify HTML — Test: `python scripts/doc_lint.py docs/tdq/reports/2026-11-07-0928-toi-uu-runtime-toan-dien.md`
  - Cần: T1.2, T1.3, T2.1, T2.2, T3.2
  - Dùng: `Archify`
  - Để: render report Trước/Sau theo receipt thật với working-tree binding.
  - Ra: `docs/tdq/reports/2026-11-07-0928-toi-uu-runtime-toan-dien.md` và `.html`, manifest, QC.
  - Kiểm: `python scripts/tdq_archify.py verify --document docs/tdq/reports/2026-11-07-0928-toi-uu-runtime-toan-dien.md --manifest docs/tdq/reports/2026-11-07-0928-toi-uu-runtime-toan-dien.manifest.json`
  - Không dùng cho: chứng nhận latency chưa đo hay browser native.

## Cụm song song & file nóng

- Sau baseline T1.1: T1.2/T1.3/T1.4 và T2.2 dùng vùng riêng nên có thể song song; T2.1 chờ T1.4; T3.1/T3.2 tuần tự, T4.1 hội tụ. `tests/test_compliance_protocol.py` là file nóng của T3.1/T3.2: một chủ ghi T3.1, T3.2 đọc kết quả và không sửa file này.
- `scripts/tdq_test.py` do T1.4 sở hữu; T2.1 chỉ đọc runner. Docs report do một chủ ghi; không giao hai agent ghi cùng file.

## Px — Log & test bắt buộc

- Log: giữ log timestamp hiện có, `TDQ_LOG=0` chỉ tắt diagnostics; không thêm service mới nếu không cần. Test đỏ thật, xanh vùng chạm mỗi task; full fresh `--workers 1 --fresh --reuse off` cuối ở QC, benchmark riêng không thay QC.

## Definition of Done

- [x] Q1 Baseline receipts, source/env fingerprint, failed sample và nhãn partial rõ — `python -c "import json,pathlib; p=pathlib.Path('docs/tdq/artifacts/2026-11-07-0928-toi-uu-runtime-toan-dien/baseline.json'); x=json.loads(p.read_text(encoding='utf-8')); assert x.get('source_fingerprint') and x.get('environment') and x.get('samples')"` (điều chỉnh schema theo receipt thực, không bỏ điều kiện)
- [x] Q2 P0 health, graph freshness, receipt invalidation với fallback và p95 không xấu đi khi đủ sample — `python -m unittest tests.test_auto_update_setup tests.test_tdq_lsp tests.test_tdq_finish tests.test_tdq_test_receipt`
- [x] Q3 P1 parity workers/cache và semantic hook; không đạt thì serial/off/full parse — `python -m unittest tests.test_tdq_runtime_bench tests.test_search_observe tests.test_read_gate tests.test_search_gate`
- [x] Q4 P2 batch read/route giữ gate và cohort, không tự công bố savings khi thiếu mẫu — `python scripts/doc_lint.py skills/tdq-intake/SKILL.md skills/tdq-intake/references/quick-lane.md skills/tdq-build/references/runtime-speed.md`
- [x] Q5 Full fresh cuối và report MD/HTML binding — `python scripts/tdq_archify.py verify --document docs/tdq/reports/2026-11-07-0928-toi-uu-runtime-toan-dien.md --manifest docs/tdq/reports/2026-11-07-0928-toi-uu-runtime-toan-dien.manifest.json`

Ước tính 280 phút agent thực thi + thời gian benchmark/full suite thật, không gồm chờ duyệt. Không báo PASS performance chỉ vì test unit xanh.
