# REPORT — Mở nhánh git theo từng request (`2026-09-05-0833-gitflow-nhanh-theo-request` · lane full · mode main · 13 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 nâng `schema_version` 4 → 5 với ba khoá `loai_request`/`nhanh_goc`/`nhanh_request` ·
P2 viết luật văn bản: bước 3b mở nhánh trong `tdq-intake`, file luật `references/nhanh-request.md`,
bước 11 gộp nhánh về trong khuôn báo cáo, luật tên nhánh trong `## 7. Git` ·
P3 bỏ tầng nhánh tích hợp của `tdq_team.py`, nhánh request thay chỗ nó (3 tầng → 2) ·
P4 dựng lại ba bundle và dọn nhánh mồ côi · P5 chạy suite, đối chiếu mốc nhánh/worktree.
**Kết quả:** tầng nhánh mode đội 3 → 2 · schema state 4 → 5 · nhánh mồ côi 1 → 0 (local và `origin`) ·
suite 112 failed/1539 passed (mốc đỏ `HEAD`) → 105 failed/1590 passed.
**Kiểm:** `pytest` ba file gitflow 18 passed/54 subtests · `pytest -q` toàn repo 105 failed/1590 passed
(hai ca đỏ còn lại có sẵn từ trước, không dính việc này) · `doc_lint.py` exit 0 trên brief/spec/plan/qc ·
ba bundle CLEAN 94/145/87 file · QC PASS 22/22 (18 dòng DoD + QC-F1..F4), 1 defect đã sửa trong vòng 1.
**Đầu ra:** `scripts/tdq_state.py` · `scripts/tdq_team.py` · `skills/tdq-intake/SKILL.md` +
`references/nhanh-request.md` · `skills/tdq-build/references/report-template.md` ·
`skills/tdq-conventions/SKILL.md` · ba file test `tests/test_gitflow_*.py`. Backup: không sửa file ngoài repo.
**Giới hạn:** luật mới là luật VĂN BẢN — nó chỉ có hiệu lực từ request kế tiếp, và test khoá được
"chữ có nằm đúng chỗ", không khoá được "Claude đã làm theo". Request này cố ý không tự mở nhánh
(user chốt làm trên `main`), nên vòng đời thật mới chỉ được kiểm trong repo tạm, chưa chạy trên repo này.
Hai ca đỏ có sẵn chưa xử lý: `index.md` thư viện rule thiếu `bash.md`; kho router ghi 224 bản
trong khi máy này quét ra 284 skill.
**Git:** chưa commit gì. Một thao tác ghi ra ngoài đã chạy sau khi user duyệt "1a":
`git push origin --delete tdq/2026-08-23-1623-mindmap-html-hai-lop/tich-hop` (sha `f051548`, đã nằm trong `main`).

## Quyết định ngoài plan

- **`doc_lint.py` nâng trần dòng SKILL.md hai lần**: `tdq-intake` 120 → 135 và `tdq-conventions`
  177 → 183. Lý do ghi ngay tại chỗ trong mã: đây là luật tầng runtime, đọc ở MỌI request, nên bản
  ngắn phải nằm trong thân skill; bản dài đã nằm ở `references/nhanh-request.md`.
- **Sửa hồi quy do chính lượt này gây ra**: bản nén luật đầu tiên đã xoá nhầm mục 8–11 của
  `tdq-conventions/SKILL.md` (34 dòng: research, sub-agent, one-batch, quality). Suite bắt được,
  đã khôi phục nguyên văn. Kèm theo: bỏ ghim `schema_version=4` ở `test_state.py`/`test_state_file.py`,
  cập nhật neo L016 và dựng lại cột số dòng của `docs/tdq/audit/luat-hien-co.md` (QC1.1),
  thêm `## Table of contents` cho `report-template.md`, cập nhật chữ "nhánh tích hợp" đã cũ ở
  `team-mode.md` và `bang-lech.md`.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 0s | 0s | 1 |
| analyze | 4 min | 4 min | 1 |
| spec | 3h 09min | 4 min | 1 |
| plan | 8 min | 3 min | 1 |
| implement | 28 min | 28 min | 1 |
| qc | 5 min | 5 min | 1 |
| report | 4s | 3s | 1 |
| **Total** | **3h 55min** | **44 min** | |

Wall clock của phase `spec` lớn hơn model time gần 3 giờ vì đó là thời gian CHỜ user duyệt, không phải máy chạy.
