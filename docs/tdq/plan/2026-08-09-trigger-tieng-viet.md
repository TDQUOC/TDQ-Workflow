# Mini-spec/plan — 2026-08-09-trigger-tieng-viet (lane quick)

## Phạm vi

IN:
- `scripts/skill_inventory.py`: nối nhánh tiếng Việt vào `TRIGGER_RE`.
- `skills/tdq-{build,plan,spec}/SKILL.md`: viết lại câu điều kiện dùng theo khuôn
  "Dùng khi …" thay vì "Lane full." cụt.
- `tests/test_skill_inventory.py`: test mô tả tiếng Việt có cụm trigger sau ký tự 60.

OUT: không đụng `doc_lint.py`, khuôn bảng §3b, hook, state, gate duyệt. Không bump version.

Năng lực: không có

### Chốt thiết kế (đo trên 274 skill)

Hai cách đạt cùng kết quả 5/5 skill tdq giữ được tín hiệu:

- Nhánh chung `dùng khi|dùng cho|gọi khi|áp dụng khi|khi cần|khi user` → bắt 2/5.
- Cộng thêm `lane full|lane quick` → bắt 5/5, nhưng nhét từ riêng của TDQ vào một regex
  dùng chung cho mọi skill của mọi plugin.

Chọn cách một, và sửa mô tả 3 skill `tdq-build/plan/spec` cho theo đúng khuôn
"câu 1 = nó là gì, câu 2 = dùng khi nào" — cùng khuôn mà 211 skill tiếng Anh đang dùng.
Regex sạch, mô tả skill nhà cũng chuẩn hơn. Cả hai bộ cụm đều **0 khớp nhầm** trên 274 skill.

## Task

- [x] **T1** Nối `|dùng khi|dùng cho|gọi khi|áp dụng khi|khi cần|khi user` vào `TRIGGER_RE`,
  ghi chú vì sao có nhánh tiếng Việt. — Test: mô tả tiếng Việt 200 ký tự có `Dùng khi` ở cuối
  → ô chứa `Dùng khi` và có ` … `.
- [x] **T2** Mô tả 3 skill `tdq-build`, `tdq-plan`, `tdq-spec` đổi câu chốt `Lane full…`
  thành câu mở bằng `Dùng khi …`, giữ nguyên nghĩa và độ dài xấp xỉ. — Test: DoD dòng 3.
- [x] **T3** Chạy suite + `doc_lint.py` + working log. — Test: xem DoD.

## Definition of Done

- [x] `python3 -m unittest discover -s tests -q` → 0 fail, 0 error.
- [x] `python3 scripts/skill_inventory.py | grep -c 'tdq-'` → **6** (không mất skill nào).
- [x] 5/6 skill tdq giữ được cụm điều kiện — đo bằng `_frontmatter` + `_condense` đọc
  thẳng file trong repo (`tdq-conventions` không có câu điều kiện nên không tính).
  KHÔNG đo qua `skill_inventory.py` chạy thẳng: xem ghi chú cache ở mục QC.
- [x] `python3 scripts/skill_inventory.py | grep ' | ' | awk -F'|' 'NF!=3 || $2 ~ /^ *$/' | wc -l`
  → **0** (không phá cột, không ô rỗng).
- [x] `python3 scripts/skill_inventory.py | wc -l` → **276**, không đổi.
- [x] `python3 scripts/doc_lint.py docs/tdq/plan/2026-08-09-trigger-tieng-viet.md` → exit 0.
- [x] `docs/workinglog/2026-08-09.md` có mục kết quả của lượt build.

## QC

Chạy 2026-08-09 12:57.

| DoD | Kết quả |
|---|---|
| Suite | `python3 -m unittest discover -s tests -q` → Ran **419** tests — OK (+1 test) |
| 5/6 skill tdq giữ cụm điều kiện | **5/6** (`build`, `intake`, `plan`, `spec`, `status`) |
| Tổng description 6 skill | **892** ký tự, dưới trần 900 của `test_token_budget` |
| Không mất skill tdq | `grep -c 'tdq-'` → **6** |
| Không phá cột / không ô rỗng | 0 · 0 |
| Tổng dòng | **276**, không đổi |
| `doc_lint.py` trên plan | exit 0 |
| Working log | có mục của lượt build |

Kiểm thêm ngoài DoD: nhánh tiếng Việt **0 khớp nhầm** vào mô tả thuần ASCII trên 274 skill
(các cụm đều có dấu). Dòng giữ cụm tiếng Anh vẫn **196**, không đổi.

### Vòng fix trong lúc build (không phải QC FAIL sau khi xong)

Bản nháp T2 làm tổng description lên **963** ký tự, vỡ trần 900 của
`test_token_budget.test_skill_descriptions_total` (nền cũ 899 — sát trần). Đã rút gọn 3 mô
tả (`Definition of Done` → `DoD`, bỏ `tiếng Việt` thừa ở `tdq-plan`, gộp `đề xuất mode` vào
`duyệt kèm mode`) → **892**. Nghĩa giữ nguyên, cụm `Dùng khi` vẫn nằm sau ký tự 60.

### Phát hiện: bảng kiểm kê đọc bản CACHE, không đọc repo

`skill_inventory.py` duyệt plugin theo `installPath` trong `installed_plugins.json`, mà
`/plugin` update lúc 12:02 đã **copy thật** repo sang
`~/.claude/plugins/cache/tdq-local/tdq-workflow/0.11.1` (inode khác, không phải symlink).
Nên chạy `skill_inventory.py` ngay bây giờ vẫn thấy mô tả CŨ của 3 skill vừa sửa — bảng chỉ
đổi sau khi user chạy `/plugin` update lần nữa.

Đính chính báo cáo trước đó: câu "Claude Code nạp plugin trực tiếp từ working tree" chỉ đúng
khi cache chưa tồn tại. Sau lần update 12:02 đã có bản copy thật, nên **sửa file trong repo
không tự có hiệu lực** cho tới lần `/plugin` update kế tiếp.
