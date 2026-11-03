# REPORT — Tối ưu context của tdq-workflow (`2026-09-28-2324-toi-uu-context-workflow` · lane full · mode main · 27/29 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Đã làm:** P1 cổng nhắc đọc lại (`hooks/scripts/read_gate.py`, chỉ nhắc, một lần mỗi file, có sổ
riêng theo phiên) · P2 chỉ mục dòng tự sinh (`scripts/doc_index.py`, 25 file) + 7 file em TẦNG 1 ·
P3 dedup câu luật tìm kiếm 6 bản → 1 bản + 5 con trỏ, gỡ 4 câu ép đọc trọn file · P4 trần 3.500
token/file cưỡng chế qua tệp khoá hash (`scripts/token_budget.py` + rule R13 của `doc_lint` +
bước `khoa-token` của `tdq_finish`) · P5 CI in bảng bề mặt · P6-P7 log/test/ba hệ · P8 hai agent
soát lỗi (14 phát hiện, sửa hết) + một agent rút gọn (9 chỗ, không đổi hành vi).

**Kết quả:** sàn tuân thủ lane `full` **55.439 → 49.531 token (−10,7%)**, mục tiêu cam kết ≤ 52.500 ·
số mục luật `##`+`###` **334 → 342 (+8)**, không mục nào mất · ba file vượt trần về dưới trần
(`plan-template` 5.067 → 3.493, `quick-lane` 4.356 → 3.419, `team-mode` 3.652 → 3.313) · tổng vùng
`references/` TĂNG 72.680 → 77.519 (43 → 50 file) vì tách file thêm tiêu đề/con trỏ/chỉ mục — đó là
cái giá đã biết trước, và nó được trả bằng phần KHÔNG còn phải nạp.

**Kiểm:** trọn bộ `python -m unittest discover tests` → `Ran 2142 tests · OK (skipped=9)` trên
Windows 3.13 · macOS thật pyenv 3.13.15 và brew 3.14.7 → `Ran 2101 · OK (skipped=34)` mỗi bản ·
`doc_lint skills/` exit 0 · `doc_index --kiem --tat-ca` exit 0 · `token_budget --kiem` exit 0 ·
QC **19/20 hạng mục DoD PASS** (Q20 partial), **15 phát hiện của `code-review`/`simplify` đều đã sửa**, không
phát hiện nào bị bác bỏ.

**Đầu ra:** `hooks/scripts/read_gate.py` · `scripts/doc_index.py` · `scripts/token_budget.py` ·
`docs/tdq/token-budget.json` · 7 file em trong `skills/*/references/` · `.github/workflows/test.yml` ·
QC: `docs/tdq/qc/2026-09-28-2324-toi-uu-context-workflow.md`. Không sửa gì ngoài repo, không cần
backup.

**Giới hạn:**
- **Linux chưa chạy trọn bộ test trên máy thật** — máy `tdq-nuc12dcmv7` đang tắt (tailscale:
  offline 2h). Job `ubuntu-latest` × 2 bản Python ở CI che phần Linux, nhưng đó là máy sạch của
  GitHub. Mở lại khi máy bật (T7.4 và Q20 để ngỏ, có ghi lý do tại chỗ).
- **Nợ ngôn ngữ:** `skills/` còn 129 dòng tiếng Việt (HEAD: 57). 65 dòng trong số đó ở
  `plan-template-co-che.md` là văn bản ở HEAD nằm TRONG fence `i18n-allow` và lượt này chỉ DỜI chỗ
  — lý do đã ghi ngay đầu file. Dịch phần đó thuộc luồng i18n, nơi mỗi luật được khoá qua cột
  `neo bản mới`.
- **Cổng nhắc chỉ đo được bằng hiệu ứng thật qua một phiên dài** — unit test khoá đủ 4 hành vi,
  nhưng con số "đã cắt được bao nhiêu lần đọc lại" chỉ biết sau khi dùng thật vài phiên.

**Git:** chưa commit — đang ở nhánh `feature/toi-uu-context`, 73 đường dẫn đổi/thêm. Bản plugin
đã bump **0.53.0 → 0.54.0** kèm mục CHANGELOG.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 5 min | — | 1 |
| analyze | 38 min | — | 1 |
| spec | 5 min | — | 1 |
| plan | 27 min | — | 1 |
| implement | 6h 09min | — | 1 |
| **Total** | **7h 23min** | **—** | |

Cột `Model time` là `—`: `tdq_timing.py` dò thư mục transcript theo đường dẫn POSIX
(`-Users-admin-…`) nên không đọc được transcript của phiên Windows này. Số wall clock lấy nguyên
từ output của `tdq_timing.py show`, không ước lượng.
