# Cài tdq-workflow project-level cho Claude Code + Codex

## Nguyên văn

Yêu cầu gốc: "check repo này và cho biết liệu có thể install workflow này ở
project-level và tạo instruction ở project level để hướng Claude Code/Codex hoạt
động theo workflow này không?" — turn đầu chỉ phân tích, không sửa gì.

Sau khi phân tích, user chọn hướng **B: làm cho cả Claude Code lẫn Codex**, huỷ
request cũ (`2026-08-11-fix-loi-import-webm-unity`) để ưu tiên việc này.

Mục tiêu: một project khác (chưa xác định project cụ thể — cần hỏi) có thể bật
tdq-workflow ở project-level (không phải user-level `~/.claude/CLAUDE.md`) cho cả
hai harness: Claude Code và Codex.

Phạm vi đoán (cần xác nhận ở phase phân tích/interview):
- Claude Code: cài plugin scope project (marketplace.json local, không `--scope user`)
  + dán block instruction vào `CLAUDE.md` root project đích.
- Codex: `portable/` đã bị xoá ở bản 0.10.0 (CHANGELOG.md:101-103) — cần viết lại
  tương đương (AGENTS.md + workflow docs cho Codex) vì Codex không có hook, không có
  skill system.
- Cần làm rõ: project đích là project nào (path?), hay chỉ làm tài liệu hướng dẫn
  chung (generic, áp dụng cho bất kỳ project nào)?

## Hiểu & kiến thức

### Năng lực dùng được
`skill_inventory.py` liệt kê toàn skill user-scope (Unity, Adobe, Canva, Cloudflare…) —
không skill nào khớp việc viết tài liệu/portable docs cho chính plugin TDQ. Việc này
dùng công cụ nền tảng (Read/Write/Edit/Bash/git) + `tavily-primary` nếu cần tra cứu
Codex AGENTS.md convention hiện hành. Không cần sub-agent riêng cho research vì phần
"Codex AGENTS.md format" đã đủ rõ từ chính bản `portable/AGENTS.md` cũ (không đổi kể
từ khi Codex hỗ trợ AGENTS.md) — bỏ qua research ngoài, thuần nội bộ.

### Đọc code / lịch sử
- `README.md:38-45`: Claude Code project-level đã có đường sẵn qua `--plugin-dir` hoặc
  marketplace scope project (không cần `--scope user`).
- `docs/notes/user-level-install.md` mục 1 (marketplace), mục 3 (block CLAUDE.md), mục 4
  (Codex — **lỗi thời**, trỏ `portable/AGENTS.md` đã xoá).
- `CHANGELOG.md:101-103` (commit `de76221`, 2026-08-08): xoá `portable/` (18 file) +
  mode `external`. Lấy lại nội dung cũ qua `git show de76221^:portable/AGENTS.md` và
  `git show de76221 --stat` để biết đủ danh sách file gốc.
- Bản `portable/AGENTS.md` cũ (khôi phục từ git) vẫn khớp phần lớn nguyên tắc hiện tại
  (giao thức 1 turn, state CLI, duyệt bằng chat, git naming, working log) — chỉ lệch ở:
  (a) `implement_mode` cũ có `external`, giờ chỉ `main|subagent`; (b) cây tài liệu cũ
  7 thư mục (`requests/questions/research/knowledge/spec/plan/qc/reports/external`),
  giờ gộp còn `brief/` (3 mục) + `research/spec/plan/qc/reports` (README.md:70); (c) lane
  quick giờ có QC bắt buộc mặc định BẬT + `--no-qc` opt-out (0.9.0), bản cũ portable
  không có luật này.
- `scripts/tdq_state.py` không đổi hành vi CLI cốt lõi (`next|get|set|approve|init|reset|
  phases-doc`) — bản portable vẫn gọi được y hệt, chỉ cần đường dẫn tương đối đúng khi
  copy sang project khác (không có `${CLAUDE_PLUGIN_ROOT}`, dùng path tương đối
  `scripts/tdq_state.py` từ root project đích — đúng như bản AGENTS.md cũ đã làm).

### Quyết định đã chốt (từ interview)
1. **Phạm vi**: dựng lại `portable/` NGAY trong repo TDQWorkflow này làm nguồn tham
   chiếu chung — không nhắm 1 project đích cụ thể. User tự copy sang project khác khi
   cần (đúng tinh thần bản cũ: `portable/README.md` hướng dẫn copy `AGENTS.md` +
   `workflow/` + `scripts/tdq_state.py`).
2. **Cấu trúc**: gộp gọn theo skills/ hiện tại — bỏ hẳn phần external/deep-search.
   File cần dựng: `portable/AGENTS.md`, `portable/README.md`,
   `portable/workflow/{01-intake,02-spec,03-plan,04-build,phases}.md`,
   `portable/workflow/references/{analyze-full,approval,plan-template,qc,quick-lane}.md`.
   Nội dung dịch từ `skills/tdq-{intake,spec,plan,build}/SKILL.md` +
   `skills/tdq-intake/references/*` + `skills/tdq-build/references/qc.md` hiện hành
   (không phải bản cũ) — vì bản cũ đã lệch (thiếu brief gộp 3 mục, thiếu QC quick bắt
   buộc, còn nhắc external).
3. **Claude Code project-level**: chỉ sửa tài liệu, không thêm script tự động hoá.
   Sửa `docs/notes/user-level-install.md`: mục 4 thay bằng hướng dẫn portable mới; mục 1
   làm rõ "scope project" là dùng chung cấu trúc (chỉ bỏ `--scope user`); mục 3 giữ
   nguyên (đã đúng, chỉ cần ghi rõ áp dụng được cả project-level). Có thể đổi tên file
   vì giờ không chỉ "user-level" nữa — nhưng đổi tên file gây phá link từ README/skills
   khác → **giữ nguyên tên file**, chỉ sửa nội dung + tiêu đề đầu file cho đúng phạm vi
   (user-level VÀ project-level).
4. **QC**: agent tự đối chiếu nội dung mới với `scripts/tdq_state.py`
   (`PHASE_TABLE`, `VALID_MODES`, lệnh CLI) + `skills/tdq-*/SKILL.md` hiện hành, không
   cần môi trường Codex thật.

### Phương án đã loại
- Giữ nguyên cấu trúc 9+ file cũ nguyên bản (loại — trùng lặp nội dung với skills/,
  lệch schema hiện tại, đúng thứ over-engineer mà 0.8.0/0.9.0 đã cắt).
- Thêm script tự động hoá cài đặt project-level (loại — README/CHANGELOG cho thấy xu
  hướng rõ ràng của repo là cắt giảm, không thêm bề mặt mới khi tài liệu tay đã đủ).

### Lộ trình
| Bước/phase | CÓ-BỎ | Vì sao |
|---|---|---|
| Phân tích | CÓ | đã xong (brief này) |
| Spec | CÓ | việc có ảnh hưởng cấu trúc (thêm thư mục mới `portable/`), cần user duyệt rõ trước khi viết 10 file |
| Plan | CÓ | full lane bắt buộc, mỗi task 1 test/kiểm được |
| Research thêm ngoài | BỎ | thuần nội bộ, đã có đủ nguồn từ git history + skills/ hiện tại |
| Interview thêm | BỎ | đã hết câu hỏi làm đổi kết quả (4 câu, đều A) |
| QC độc lập bằng agent riêng | BỎ | việc là tài liệu, tự đối chiếu bằng cách đọc lại là đủ, không cần agent thứ 2 |
| Implement | CÓ | tạo/sửa file thật |
| Report | CÓ | bắt buộc theo quy trình full |

## Hỏi đáp

**1. Sản phẩm build ra để dùng ở đâu?**
- A (đề xuất): Xây lại `portable/` ngay trong repo này làm nguồn chung.
- B: Có 1 project đích cụ thể khác.
→ User chọn: **A** ("1A, 2A, 3A, 4A" — 2026-08-11 20:25).

**2. Cấu trúc `portable/` khôi phục lại: giữ 9+ file cũ hay gộp gọn theo skills/ hiện tại?**
- A (đề xuất): Gộp gọn, bỏ external/deep-search.
- B: Giữ nguyên 9+ file cũ.
→ User chọn: **A**.

**3. Claude Code project-level: có cần thêm script tự động hoá cài đặt không?**
- A (đề xuất): Chỉ tài liệu, không thêm script.
- B: Thêm script.
→ User chọn: **A**.

**4. QC cho request này xác nhận đạt bằng cách nào?**
- A (đề xuất): Tự đối chiếu tài liệu mới với `scripts/tdq_state.py`/`skills/` hiện hành,
  không cần Codex thật.
- B: Test thật bằng Codex trên project mẫu.
→ User chọn: **A**.
