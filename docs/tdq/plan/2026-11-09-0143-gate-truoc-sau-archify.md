# PLAN — Gate cứng cho Trước/Sau + sơ đồ Archify ở spec và report

Ngày: 2026-11-09 · Spec: ../spec/2026-11-09-0143-gate-truoc-sau-archify.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main
Trạng thái plan: HOÀN THÀNH.

## Quy tắc thi hành

- Spec §2/§6 đứng trên plan. Tick `[~]` trước khi sửa, `[x]` ngay khi test xanh. Test đỏ thật trước sửa.
- Mỗi task chạy test vùng chạm; full fresh `tdq_test.py --workers 1 --fresh --reuse off` chỉ ở QC.
- Report HTML render **sau cùng** (sau timing + mọi chỉnh `.md`), rồi mới `set phase=idle`.

## Thiết kế Trước vs Sau

| Trước | Sau |
|---|---|
| `approve spec`: chỉ `_r14_gate` | + `_archify_gate`: preview manifest `current` |
| `approve quick`: không kiểm | `_archify_gate`: flow manifest `current` |
| `set phase=idle`: không kiểm report | `_chan_report_thieu`: 4 mục + report manifest `current` |

## P1 — Gate CLI

- [x] **T1** (e20m) `_archify_bat_buoc`, `_archify_gate` (spec full + quick, fail-open khi import/verify lỗi) gọi sau `_r14_gate` trong `_cli_approve` — Test: `python -m unittest tests.test_archify_gate`
  - Dùng: Python unittest + `tdq_test.py`
  - Để: đỏ trước rồi xanh.
  - Ra: tests.test_archify_gate xanh.
  - Kiểm: unittest.
  - Không dùng cho: thay full fresh ở QC.
- [x] **T2** (e10m) Cờ `--bo-qua-archify "<lý do>"` trong `_parse_approve_args` (lý do rỗng → fail), khóa `archify_bo_qua` trong `default_state` — Test: `python -m unittest tests.test_archify_gate tests.test_approve_do_truoc`
- [x] **T3** (e20m) `_chan_report_thieu` trong nhánh `set phase=idle`: bỏ khi slug cũ hoặc chưa duyệt gate nào; đòi 4 nhãn; manifest report `current` trừ khi `archify_bo_qua` — Test: `python -m unittest tests.test_archify_gate tests.test_state tests.test_search_observe tests.test_quick_qc`
  - Chạm: `scripts/tdq_state.py` → nhánh `set` (dòng `phase=idle`); test hiện có gọi `set phase=idle`: `tests/test_state.py`, `tests/test_search_observe.py`.
  - Cần: T2

## P2 — Luật

- [x] **T4** (e10m) Ghi gate vào luật: `archify-ba.md` (approve spec chặn khi manifest không current, lối thoát), `archify-quick.md` (luôn render, tính năng mới ghi `Hiện trạng: chưa có`; approve quick chặn), `report-template.md` bước 7b (render sau cùng; idle chặn) + `PHASE_TABLE["report"]` checklist — Test: `python scripts/doc_lint.py skills/tdq-spec/references/archify-ba.md skills/tdq-intake/references/archify-quick.md skills/tdq-build/references/report-template.md`
  - Chạm: `skills/tdq-spec/references/archify-ba.md`, `skills/tdq-intake/references/archify-quick.md`, `skills/tdq-build/references/report-template.md`, `scripts/tdq_state.py` (`PHASE_TABLE`), `skills/tdq-conventions/references/phases.md` (sinh lại).
  - Cần: T3

## P3 — QC & report

- [x] **T5** (e25m) QC Q1–Q8: full fresh, doc_lint, chỉ mục dòng/token-budget nếu lệch; report MD 4 mục + render Archify report; `set phase=idle` qua gate thật (Q7) — Test: `python scripts/tdq_test.py --workers 1 --fresh --reuse off`
  - Cần: T4
  - Dùng: Archify CLI (`tdq_archify.py`)
  - Để: render report Trước/Sau từ kết quả test thật, verify `current` trước `set phase=idle`.
  - Ra: `docs/tdq/reports/2026-11-09-0143-gate-truoc-sau-archify.md` + `.html` + `.manifest.json`, `docs/tdq/qc/2026-11-09-0143-gate-truoc-sau-archify.md`.
  - Kiểm: `python scripts/tdq_archify.py verify --document docs/tdq/reports/2026-11-09-0143-gate-truoc-sau-archify.md --manifest docs/tdq/reports/2026-11-09-0143-gate-truoc-sau-archify.manifest.json`
  - Không dùng cho: kiểm hình ảnh HTML bằng trình duyệt.

## Cụm song song & file nóng

- Một cụm tuần tự: T1–T4 cùng chạm `scripts/tdq_state.py`. Leader làm cả.

## Px — Log & test bắt buộc

- `_warn` khi chặn/bỏ qua (cổng, file, status verify). Test đỏ thật trước sửa; vùng chạm mỗi task; full fresh một lần ở QC. Working log mỗi mốc qua `tdq_finish.py`.

## Definition of Done

- [x] Q1 approve spec slug mới thiếu/stale manifest → exit ≠ 0, chưa duyệt — `python -m unittest tests.test_archify_gate`
- [x] Q2 approve spec có manifest current → qua — `python -m unittest tests.test_archify_gate`
- [x] Q3 approve quick thiếu / có flow manifest → chặn / qua — `python -m unittest tests.test_archify_gate`
- [x] Q4 `--bo-qua-archify` ghi `archify_bo_qua`; lý do rỗng bị từ chối — `python -m unittest tests.test_archify_gate`
- [x] Q5 idle: report thiếu mục / thiếu manifest / đủ → chặn / chặn / qua — `python -m unittest tests.test_archify_gate`
- [x] Q6 slug trước mốc hoặc chưa duyệt gate nào → không gate — `python -m unittest tests.test_archify_gate`
- [x] Q7 Request này `set phase=idle` qua gate thật không lối thoát — `python scripts/tdq_state.py get archify_bo_qua`
- [x] Q8 Full fresh xanh, doc_lint 0 lỗi — `python scripts/tdq_test.py --workers 1 --fresh --reuse off`

Ước tính 85 phút agent + thời gian full suite, không gồm chờ duyệt.
