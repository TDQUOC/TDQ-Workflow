# Brief — Tổ chức graphify: chỉ source, đọc có chủ đích

## Nguyên văn

> okay bây giờ tôi cũng đã hiểu một chút rồi, okay vậy bây giờ tôi muốn tổ chức graphify
> chỉ đc scan source code của project, không scan test, và không scan doc. và chỉ đọc khi
> cần tìm liên kết hoặc cần "google map" của project

### Cách hiểu đầu tiên

**Mục tiêu.** Chốt lại vai trò của graphify trong repo này thành hai luật rõ ràng:
một luật GHI (quét cái gì) và một luật ĐỌC (tra cứu khi nào).

**Phạm vi đoán.**

- Phía GHI: `.graphifyignore` khoá cứng `tests/` và các thư mục tài liệu, để dù ai chạy
  `graphify extract` bằng tay (không có `--code-only`) thì test và doc vẫn không vào đồ thị.
  Hiện `.graphifyignore` mới chỉ có `tests/`, và việc bỏ doc đang phụ thuộc cờ `--code-only`
  trong `scripts/tdq_finish.py` — không phải luật của repo.
- Phía ĐỌC: thêm luật vào tài liệu workflow — chỉ mở graph khi cần tra **liên kết**
  (ai gọi cái này, đổi chỗ này ảnh hưởng đâu) hoặc cần **bản đồ tổng thể** project;
  việc tìm chuỗi/đọc file cụ thể vẫn dùng grep/read như cũ.

**Chỗ chưa rõ** (chuyển thành câu hỏi ở mục Hỏi đáp):

- Ngoài `tests/` và `docs/`, còn thư mục nào phải loại (`portable/`, `skills/`, `hooks/`,
  `.claude/`, `graphify-out/`)?
- Luật ĐỌC là bắt buộc hay gợi ý, và viết vào file nào?
- Có sửa lối import `hooks/ → tdq_state` để graphify tra được không, hay để riêng?

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Phán quyết | Vì sao |
|---|---|---|
| `graphify` (skill user scope) | DÙNG | Chính là đối tượng của việc này; cần tra CLI surface + hành vi ignore |
| `tavily-primary` | BỎ | Ẩn số ngoài duy nhất (phiên bản graphify mới có sửa lỗi resolve không) đã đo trực tiếp, không cần search |
| `mem0-memory` | DÙNG | Chốt xong ghi 1 fact về luật graphify của repo |
| `superpowers:test-driven-development` | DÙNG | Mọi task đổi mã có test đi kèm |
| Các skill Unity/Figma/Adobe/cloud | BỎ | Không liên quan |

### Sự thật đã đo (không phải phỏng đoán)

1. **Toàn bộ mã nguồn repo nằm ở đúng 3 thư mục**: `scripts/`, `hooks/`, `tests/`.
   `docs/`, `portable/`, `skills/`, `agents/`, `ClaudeExport/`, `claude-export/` có
   **0 file code** (`.py/.js/.ts/.sh`). Nên "chỉ scan source" = giữ `scripts/` + `hooks/`,
   loại `tests/`; phần doc bị loại sẵn nhờ `--code-only` phân loại theo kiểu file.
2. **`.graphifyignore` hoạt động** (cú pháp gitignore, ưu tiên hơn `.gitignore`). Đã thử
   với `tests/`: 1.421 → 412 node, 5,6M → 3,4M, `turn_snapshot` 92,2ms → 66,1ms,
   build `--force` 3,33s → 1,17s.
3. **graphify 0.9.28 chỉ resolve lời gọi cross-file kiểu `from M import f` + `f()`.**
   Kiểu `import M` + `M.f()` KHÔNG sinh cạnh. Bằng chứng: mọi cạnh call cross-file trong
   đồ thị đều đến từ `from _common import ...`; `hooks/` có **58 chỗ gọi `tdq_state.*`**
   nhưng đồ thị chỉ có **1 cạnh** `hooks/* → scripts/tdq_state.py` (chính là cạnh import).
4. **Nâng phiên bản KHÔNG chữa được.** Cài 0.9.42 (bản mới nhất trên PyPI, hiện dùng
   0.9.28) vào venv riêng, extract cùng repo: y hệt 412 node, cùng 12 cặp cạnh cross-file,
   `turn_snapshot` vẫn chỉ có cạnh từ chính `tdq_state.py`. Vậy muốn graphify nhìn thấy
   chuỗi `hooks → tdq_state` thì phải đổi lối import trong mã, không có đường tắt.
5. **Phía đọc hiện là số không.** Không chỗ nào trong `skills/`, `hooks/`, `scripts/`,
   `agents/` gọi `graphify query|path|explain|affected` hay đọc `graphify-out/graph.json`.
   4 chỗ nhắc tên graphify đều là phía GHI: `docs/claude-md-mau.md:38`,
   `~/.claude/CLAUDE.md:39`, `skills/tdq-conventions/SKILL.md:22`, `skills/tdq-build/SKILL.md:58,88`.
6. **`graphify-out/` vẫn nằm trong pathspec của `turn_snapshot`** → `git diff HEAD` mỗi
   prompt vẫn ~5,1 MB. Thêm `"graphify-out"` vào `BOOKKEEPING_PATHS`
   (`scripts/tdq_state.py:287`) đưa về 0 byte.

### Lộ trình

| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Phân tích | CÓ (xong) | 6 sự thật đã đo, không còn chỗ đoán |
| Research thêm (tavily) | BỎ | Ẩn số ngoài duy nhất — bản graphify mới — đã đo trực tiếp, kết quả âm tính |
| Spec + plan | CÓ | Khung bất biến |
| Implement | CÓ | Khung bất biến |
| Chia subagent | BỎ | 4 phase nối tiếp nhau, phase 2 đụng 6 file cùng lúc, tách ra tốn hơn lợi |
| QC bám DoD | CÓ | Đổi lối import 58 chỗ — phải có bằng chứng từng dòng DoD |
| Review sâu | CÓ (gộp QC) | Rủi ro tập trung ở đúng 1 chỗ đã biết (mock.patch), không cần vòng riêng |
| Report | CÓ | Khung bất biến |

## Hỏi đáp

### Vòng 1

**Q1. `.graphifyignore` khoá tới đâu?** → **B**: liệt kê đủ `tests/` + `docs/` +
`portable/` + `skills/` + `agents/` + `ClaudeExport/` + `claude-export/` + `graphify-out/`.
Thừa so với hiện trạng nhưng chống được trường hợp chạy `graphify extract` không cờ
`--code-only`, và chống file code lọt vào các thư mục đó sau này.

**Q2. Có sửa lối import `hooks/ → tdq_state` không?** → **A**: CÓ, làm trong request này.
Đổi `import tdq_state` + `tdq_state.f()` thành `from tdq_state import f` + `f()` ở 6 file
`hooks/scripts/`, 58 chỗ gọi.

**Q3. Luật ĐỌC viết ở đâu?** → **A**: thêm vào `skills/tdq-intake/references/analyze-full.md`
(bước 2 "Đọc code") và `references/quick-lane.md` (bước 1), dạng **gợi ý có điều kiện** —
mở graph khi câu hỏi là "ai gọi X / sửa X ảnh hưởng đâu / cấu trúc tổng thể"; tìm chuỗi
và đọc file cụ thể thì grep. Không ép tra graph mỗi lần analyze.

**Q4. Gộp việc loại `graphify-out/` khỏi pathspec?** → **A**: CÓ, cùng request.

### Rủi ro phát hiện khi chốt (không cần hỏi thêm)

`tests/test_bash_gate.py:185` dùng `mock.patch.object(tdq_state, "turn_log_read", ...)`.
Sau khi `bash_gate.py` chuyển sang `from tdq_state import turn_log_read`, tên đã bind lúc
import nên patch trên module KHÔNG còn tác dụng → test sẽ đỏ. Cách xử lý đã chốt: sửa test
patch vào chính module hook (`mock.patch.object(<bash_gate_mod>, "turn_log_read", ...)`),
giữ nguyên ý nghĩa phép kiểm. Đây là task trong plan, không phải câu hỏi cho user.
