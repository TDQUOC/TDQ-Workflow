# Mini-spec/plan — 2026-08-09-sua-mo-ta-skill-inventory (lane quick)

## Phạm vi

IN:
- `scripts/skill_inventory.py`: parser frontmatter đọc được YAML block scalar; rút gọn
  description có nhận biết cụm trigger; chống ký tự `|` phá cột.
- `tests/test_skill_inventory.py`: test cho 3 việc trên.

OUT: không đụng `doc_lint.py`, R8, khuôn bảng §3b, hook, state, gate duyệt. Không bump
version. Không sửa lệch tên `data-engineering`/`astronomer-data:` trong `plugin-routing.md`
(việc khác, để request sau).

Năng lực: không có

## Task

- [x] **T1** `_frontmatter` đọc hết khối frontmatter (tới `---` đóng, trần 80 dòng) thay vì
  15 dòng đầu; nhận `description: |`, `|-`, `>` và các dòng thụt vào tiếp theo, nối thành
  một dòng. — Test: `SKILL.md` giả có `description: |` 3 dòng → trả về đủ 3 dòng đã nối.
- [x] **T2** Ký tự `|` trong description đổi thành `/` trước khi in. — Test: description
  chứa `a | b` → dòng in ra vẫn đúng 3 cột khi tách bằng `|`.
- [x] **T3** Thêm `_condense(desc)`: lấy `desc[:60]`; nếu regex trigger
  (`use when|use this|whenever|when the user|trigger`, không phân biệt hoa thường) khớp ở
  vị trí ≥ 60 thì nối thêm ` … ` + 50 ký tự kể từ chỗ khớp. Tổng ≤ 115 ký tự.
  — Test: desc có `Use when` ở vị trí 200 → kết quả chứa `Use when`; desc ngắn 30 ký tự →
  trả nguyên vẹn, không có ` … `.
- [x] **T4** `inventory()` dùng `_condense` thay cho `[:DESC_MAX]`; docstring và hằng số
  cập nhật theo. — Test: `test_scans_user_and_project_dirs` vẫn xanh sau đổi.
- [x] **T5** Chạy toàn bộ suite + `doc_lint.py` + append working log. — Test: xem DoD.

## Definition of Done

Ba dòng đầu dùng chung biến `INV=$(python3 scripts/skill_inventory.py)`; `grep ' | '` lọc
bỏ 2 dòng nhắc built-in ở cuối, chỉ giữ dòng skill.

- [x] `python3 -m unittest discover -s tests -q` → 0 fail, 0 error.
- [x] `echo "$INV" | grep ' | ' | awk -F'|' 'NF!=3' | wc -l` → 0 (mọi dòng skill đúng 3
  cột; hiện tại 18 dòng sai vì `description: |` lọt ra thành ô riêng).
- [x] `echo "$INV" | grep ' | ' | awk -F'|' '$2 ~ /^ *$/' | wc -l` → 0 (không còn skill
  mất description; hiện tại 18).
- [x] `echo "$INV" | grep -ciE 'use when|whenever|when the user'` → ≥ 190 (hiện tại 44).
- [x] `python3 scripts/skill_inventory.py | wc -l` → 270 (268 skill + 2 dòng nhắc), không đổi.
- [x] `python3 scripts/doc_lint.py docs/tdq/plan/2026-08-09-sua-mo-ta-skill-inventory.md`
  → exit 0.
- [x] `docs/workinglog/2026-08-09.md` có mục kết quả của lượt build.

## QC

Chạy 2026-08-09 11:35. Lệnh chung: `INV=$(python3 scripts/skill_inventory.py)`.

| DoD | Lệnh | Kết quả |
|---|---|---|
| Suite xanh | `python3 -m unittest discover -s tests -q` | **Ran 417 tests — OK** (405 → 417, thêm 5 test mới ở `DescriptionTest`; 412 con số cũ trong log là của lần chạy trước) |
| Đúng 3 cột | `echo "$INV" \| grep ' \| ' \| awk -F'\|' 'NF!=3' \| wc -l` | **0** (nền: 18) |
| Không ô mô tả rỗng | `echo "$INV" \| grep ' \| ' \| awk -F'\|' '$2 ~ /^ *$/' \| wc -l` | **0** (nền: 18) |
| Giữ cụm trigger | `echo "$INV" \| grep -ciE 'use when\|whenever\|when the user'` | **195** ≥ 190 (nền: 44) |
| Tổng dòng không đổi | `echo "$INV" \| wc -l` | **270** (268 skill + 2 dòng nhắc) |
| doc_lint plan | `python3 scripts/doc_lint.py docs/tdq/plan/2026-08-09-sua-mo-ta-skill-inventory.md` | **exit 0** |
| Working log | mục `## 11:35` trong `docs/workinglog/2026-08-09.md` | có |

Kiểm thêm ngoài DoD: ô mô tả dài nhất **113 ký tự** (trần thiết kế 60 + ` … ` + 50 = 113,
không vượt). Output script **24.639 → 36.231 ký tự** (~6.2k → ~9.1k token), tăng ~2.9k
token mỗi lần kiểm kê — đúng mức đã trình khi duyệt.

Không có vòng fix: QC 7/7 PASS ngay vòng 1.

Ghi chú: `tests/test_docs_consistency.py` FAIL một lần vì 7 file `.DS_Store` do Finder sinh
(không thuộc phạm vi request). Đã `find . -name .DS_Store -delete` rồi chạy lại — xanh.


## QC vòng 2 — validate lại sau khi user restart Claude Code

Chạy 2026-08-09 11:36, session mới, không có vòng fix (vòng 1 đã PASS, đây là chạy lại
để xác nhận trạng thái trên đĩa).

| Hạng mục | Kết quả |
|---|---|
| `python3 -m unittest discover -s tests -q` | Ran 417 tests — **OK** |
| Đúng 3 cột / không ô rỗng / giữ trigger / tổng dòng | **0 · 0 · 195 · 270** — trùng vòng 1 |
| `doc_lint.py` trên plan | exit 0 |
| `doc_lint.py docs/` | exit 1, **25 lỗi đều nằm trong `docs/archive/v0.1/`** (R5/R2 di sản, không phải file của request này) |
| stderr của script | 0 dòng cảnh báo |
| Danh sách tên skill trước vs sau sửa (`git stash` bản cũ rồi diff) | **giống hệt** — không mất/thêm skill nào |
| Chạy 2 lần liên tiếp | output byte-identical (deterministic) |
| Ô mô tả dài nhất | 113 ký tự, đúng trần 60 + ` … ` + 50 |
| Số ô có dấu nối ` … ` | 164/268 |
| Ô còn chứa ký tự `\|` | 0 |

Kiểm biên bằng SKILL.md giả (5 ca, thư mục tạm):

| Ca | Kết quả |
|---|---|
| Không có frontmatter | mô tả rỗng, lấy tên theo thư mục, không crash |
| Frontmatter không đóng `---` | vẫn đọc được mô tả |
| `description: >-` (folded) + `allowed-tools` phía dưới | đọc đúng, không nuốt `allowed-tools` |
| Mô tả bọc `"..."` | nháy kép đã bóc |
| `description:` nằm sau dòng thứ 80 | **mô tả rỗng** — đúng thiết kế trần `FRONTMATTER_MAX_LINES` |

Giới hạn đã biết (ghi rõ, không phải bug): mốc "0 ô mô tả rỗng" đúng với 268 SKILL.md hiện
có trên máy, không phải bất biến của code — SKILL.md thiếu frontmatter hoặc có
`description:` sau dòng 80 vẫn cho ô rỗng.

## Đo A/B bản cũ vs bản mới

Chạy 2026-08-09 11:38. Cách đo: lấy bản cũ bằng `git stash push scripts/skill_inventory.py`,
chạy cả hai, đối chiếu với description ĐẦY ĐỦ đọc từ 268 `SKILL.md` bằng **parser độc lập**
(không dùng lại code đang đo, để phép đo không tự chấm điểm mình). Script:
`scratchpad/ab.py`.

| Chỉ số | Cũ | Mới | Đổi |
|---|---|---|---|
| Giữ được cụm trigger (trên 211 skill có trigger) | 52 = **24,6%** | 210 = **99,5%** | **+303,8%** (+74,9 điểm) |
| Ô mô tả vô nghĩa (rỗng hoặc chỉ là ký tự đánh dấu YAML) | **56/268 = 20,9%** | **0** | **−100%** |
| Dòng sai số cột | 18 | 0 | −100% |
| % ký tự mô tả gốc giữ lại (trung bình) | 18,1% | 28,5% | +57,2% |
| Chi phí output | ~6.199 token | ~9.192 token | +48,3% |

Hiệu quả trên mỗi token: cũ 52 skill có trigger / 6.199 token = 8,4 skill/1k token;
mới 210 / 9.192 = 22,8 skill/1k token → **+171%**.

Đính chính con số đã báo trước đó: mốc "18 ô mất mô tả" là **thiếu**. 18 là số ô chứa dấu
`|`; đếm đủ cả `>` (17 ô, cụm adobe) và `>-` (21 ô, cụm base44/datarobot) thì bản cũ có
**56 ô vô nghĩa**, không phải 18. Bản mới xử lý cả ba dạng đánh dấu.

Khiếm khuyết còn lại (1/211 = 0,5%): `huggingface-trackio` có cụm `Use when` bắt đầu ở ký
tự 58 — nằm vắt qua ngưỡng 60 nên `TRIGGER_RE.search(text, DESC_MAX)` không thấy, ô bị cắt
giữa chữ `Us`. Sửa được bằng cách tìm từ `DESC_MAX - 15`; chưa làm vì nằm ngoài phạm vi
plan đã duyệt.

## QC vòng 3 — fix ca vắt ngưỡng

- [x] **T6** Thêm `TRIGGER_LOOKBACK = 15`, dò trigger từ `DESC_MAX - TRIGGER_LOOKBACK`.
  — Test: `test_trigger_straddling_cutoff_kept` — mô tả có `Use when` ở ký tự 58 → ô giữ
  đủ cụm.
- [x] **T7** Trigger vắt ngưỡng thì cắt phần đầu ngay TRƯỚC nó, khỏi lặp cụm ở hai bên dấu
  nối. — Test: cùng test trên, thêm `assertEqual(row.count("use when"), 1)`.

| Hạng mục | Kết quả |
|---|---|
| `python3 -m unittest discover -s tests -q` | Ran **418** tests — OK (+1 test) |
| Giữ cụm trigger | 210/211 → **211/211 = 100%** |
| Ô lặp cụm trigger hai bên dấu nối | 24 → **11** |
| Sai cột · ô rỗng · tổng dòng · stderr | 0 · 0 · 270 · 0 |
| Ô dài nhất | 113 ký tự, không đổi |
| Chạy 2 lần | byte-identical |

11 ô còn "lặp" là thật, không phải lỗi: description gốc có hai cụm khác nhau — ví dụ
`datarobot-workload-api` mở đầu `Use when the user wants to…` rồi cuối có
`Triggers include:…`. Đầu giữ cụm một, đuôi ghép cụm hai, đúng ý muốn.

### Hiệu quả chốt (bản cũ → bản cuối)

| Chỉ số | Cũ | Cuối | Đổi |
|---|---|---|---|
| Giữ cụm trigger (211 skill có trigger) | 24,6% | **100%** | **+305,8%** |
| Ô mô tả vô nghĩa | 56 | 0 | −100% |
| Dòng sai số cột | 18 | 0 | −100% |
| % ký tự gốc giữ lại | 18,1% | 29,0% | +60,0% |
| Chi phí | 6.199 token | 9.264 token | +49,4% |
| Skill-có-trigger trên mỗi 1k token | 8,4 | **22,8** | **+171%** |
