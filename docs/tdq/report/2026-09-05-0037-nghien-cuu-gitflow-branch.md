# BÁO CÁO — Nghiên cứu mô hình nhánh git cho vòng đời request

Ngày: 2026-09-05 · Slug: `2026-09-05-0037-nghien-cuu-gitflow-branch` · Lane: full · Mode: main
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Spec: ../spec/2026-09-05-0037-nghien-cuu-gitflow-branch.md · Plan: ../plan/2026-09-05-0037-nghien-cuu-gitflow-branch.md

## Đã làm gì

Request này chỉ nghiên cứu và đề xuất; không một dòng mã hay luật nào của workflow bị sửa.

- Đọc lại mã đang chạy để đo hiện trạng: `scripts/tdq_state.py`, `scripts/tdq_team.py`,
  `skills/tdq-intake/SKILL.md`, `skills/tdq-build/references/report-template.md`,
  `skills/tdq-conventions/SKILL.md`.
- Tra ngoài về Gitflow, GitHub Flow, trunk-based và đặc tả Conventional Branch, mỗi kết luận kèm
  link nguồn trong file phương án.
- Viết bộ test giữ báo cáo khỏi mục theo thời gian TRƯỚC khi viết báo cáo:
  `tests/test_bao_cao_gitflow.py`, 13 ca, ban đầu đỏ 12 ca vì file phương án chưa tồn tại.
- Viết phương án: `docs/tdq/report/2026-09-05-0037-nghien-cuu-gitflow-branch-phuong-an.md`
  — bảng so sánh ba mô hình, sáu chốt của user, sáu khoảng trống G1–G6, vòng đời năm bước
  B1–B5 kèm lệnh git nguyên văn, lộ trình ba giai đoạn GĐ1–GĐ3.

## Kết luận một dòng

Thứ user mô tả không phải Gitflow mà là GitHub Flow có phân loại tên nhánh; TDQ hiện thiếu đúng
sáu mảnh để chạy được nó, và mảnh khó nhất là gộp nhánh tích hợp của mode `subagent`.

## Quyết định tự chốt trong lúc làm

| # | Quyết định | Lý do |
|---|---|---|
| 1 | Giữ mode `main` dù `tdq_bench.py` cho `Winner: đội` cách 4.0 phút | mode `subagent` bắt buộc tạo nhánh task và worktree, đúng thứ DoD dòng 12 của chính request này cấm |
| 2 | Bỏ nhóm "AI Agent Source Prefixes" của Conventional Branch, chỉ lấy 5 loại | nhóm đó chứa `claude/` và `codex/`, đụng thẳng câu cấm ở `skills/tdq-conventions/SKILL.md:133` |
| 3 | Không xoá nhánh mồ côi phát hiện được | nó là bằng chứng sống của khoảng trống G4; xoá đi là mất chứng cứ và cũng vi phạm quy tắc cấm đụng nhánh của plan |

## Một điểm phải nói lại cho đúng

Brief mục `## Hỏi đáp` ghi rằng việc dọn worktree của sub-agent "không gắn cứng vào mốc task
xong". Đo lại mã thì câu đó chỉ đúng một nửa và tôi nêu ra ở đây thay vì để im:

`lenh_hop` gọi `_thu_don` ngay sau khi merge nhánh task (`scripts/tdq_team.py:1058`), hàm này gỡ
worktree, `git worktree prune`, rồi xoá nhánh task. Nghĩa là **chốt bổ sung số 6 của bạn, ở mức
task, mã hiện tại đáp ứng rồi.** Khoảng trống thật nằm cao hơn một tầng: nhánh tích hợp của request
không ai merge về và không ai xoá. Mục G4 của phương án viết theo cách hiểu đã sửa này.

## Bảng thời gian

| Phase | Việc | Kết quả |
|---|---|---|
| analyze | B0 kiểm kê năng lực, đọc mã, tra ngoài, phỏng vấn | 6 chốt trong 1 lượt trả lời của user |
| spec | viết + tự soát | bản 1.1, `doc_lint` 0 lỗi |
| plan | viết + đo mode bằng `tdq_bench.py` | 7 task, `doc_lint --pair` thoát 0 |
| implement | 7 task, đỏ trước rồi xanh | `tests/test_bao_cao_gitflow.py` xanh toàn bộ |
| qc | 15 dòng DoD + 4 hạng mục cố định | 19/19 PASS, không vòng fix nào |

## Một con số cần nói rõ

Suite toàn repo lượt này là `107 failed, 1570 passed, 1 skipped`, cao hơn mốc đỏ ghi ở QC ngày
2026-09-03 (`100 failed, 1559 passed`). Bảy đỏ chênh không do request này: sáu nằm trong
`tests/test_skill_router.py` — file đối chiếu số skill có trên đĩa nên đổi theo plugin cài trên
máy, không theo repo; một là ca bench đỏ vì nhánh mồ côi còn đó, mà nhánh ấy có từ 2026-08-23 và
ca test có từ 2026-08-17. File mã duy nhất lượt này thêm vào chạy riêng ra 11 passed. Chi tiết
trong mục bằng chứng Q14 của `docs/tdq/qc/2026-09-05-0037-nghien-cuu-gitflow-branch.md`.

## Tồn đọng, không nằm trong phạm vi request này

- **Nhánh mồ côi.** `tdq/2026-08-23-1623-mindmap-html-hai-lop/tich-hop` còn ở cả local lẫn
  `origin`. Cố ý giữ làm bằng chứng cho G4. Dọn hay không là quyết định của bạn.
- **Chữ cũ về phase `diagram`.** `skills/tdq-intake/SKILL.md` và `skills/tdq-spec/SKILL.md` vẫn mô
  tả phase `diagram` như bắt buộc, trong khi `PHASE_DA_GO` của `scripts/tdq_state.py` đã gỡ phase
  đó từ 2026-09-01. Văn bản lệch mã, nên sửa ở một request riêng.
- **Sáu khoảng trống G1–G6 vẫn còn nguyên.** Đây là kết quả mong muốn: request này là nghiên cứu.
  Muốn lấp thì mở request mới theo lộ trình GĐ1 → GĐ2 → GĐ3 trong file phương án.
- **Hai MCP server chưa uỷ quyền** (claude.ai Google Drive, plugin:canva:canva) — cần một phiên
  tương tác để chạy OAuth. Không liên quan request này, chỉ báo để bạn biết.

## Đọc tiếp

Nội dung chính nằm ở `docs/tdq/report/2026-09-05-0037-nghien-cuu-gitflow-branch-phuong-an.md`.
