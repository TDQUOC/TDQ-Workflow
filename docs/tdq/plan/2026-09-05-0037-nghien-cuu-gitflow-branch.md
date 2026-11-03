# PLAN — Nghiên cứu mô hình nhánh git cho vòng đời request

Ngày: 2026-09-05 · Spec: ../spec/2026-09-05-0037-nghien-cuu-gitflow-branch.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — đo bằng `tdq_bench.py mo-phong` trên chính plan này (hệ số agent 1.5): 7 task, 2 đợt, main 14.3 phút / đội 10.2 phút, `Winner: đội` cách 4.0 phút. **Đề xuất vẫn là `main`, ngược với số đo**, vì mode `subagent` bắt buộc tạo nhánh task và worktree qua `tdq_team.py` — đúng thứ quy tắc thi hành số 5 và DoD dòng 12 của plan này cấm. Chạy đội là tự làm FAIL hạng mục kiểm phạm vi của chính request. Bốn task T2.1–T2.4 lại cùng ghi một file nên phần giao ra được cũng mỏng. (ĐỀ XUẤT, user chốt lúc duyệt)

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Bộ kiểm viết trước
- P2 — Phương án
- P3 — Báo cáo & đóng sổ
- Cụm song song
- Definition of Done
- Ước tính

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → test đỏ trước → viết → test xanh → đổi `[x]` NGAY vào file
   này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy bộ test của request, phải xanh mới sang phase sau.
4. **Cấm sửa mọi file trong `scripts/`, `skills/`, `portable_claude/`, `portable_codex/`,
   `antigravity_portable/`** — spec §1 NGOÀI phạm vi. Vi phạm là FAIL Q11.
5. **Cấm tạo, đổi tên, xoá nhánh hoặc worktree.** Mốc so sánh đã chụp trước khi làm:
   `<scratchpad>/nhanh-truoc.txt` (12 dòng) và `<scratchpad>/worktree-truoc.txt` (2 dòng).
6. Mọi con số và mọi vị trí `file:dòng` viết vào phương án phải đo lại bằng lệnh ngay lúc viết.
7. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
8. Không commit/push cho đến khi user yêu cầu.

## P1 — Bộ kiểm viết trước

- [x] **T1.1** (e22m) Viết bộ test đọc file phương án, gồm 9 nhóm ca: đếm đúng 6 mục mã `G1`–`G6`;
  mỗi mục có dòng `**Chạm:**` và mọi đường dẫn nêu ở đó tồn tại trên đĩa; bảng so sánh có đúng 3
  dòng mô hình, mỗi dòng chứa một `http`; mỗi bước vòng đời có ít nhất một khối lệnh mở đầu bằng
  `git `; mọi tên nhánh mẫu qua được `git check-ref-format --branch`; không tên nhánh mẫu nào mở
  đầu bằng `claude|antigravity|gemini|codex`; có ≥3 giai đoạn mã `GĐ1`… mỗi cái có dòng file và
  dòng rủi ro; mọi `file:dòng` trỏ file có thật và số dòng không vượt độ dài file; không câu nào
  trong hai file báo cáo nói phương án đã được thi hành — Test: `python3 -m pytest tests/test_bao_cao_gitflow.py -q` ĐỎ toàn bộ vì file phương án chưa tồn tại
  - Chạm: `tests/test_bao_cao_gitflow.py` → file mới, chưa node nào phụ thuộc

**Xong P1 khi**: bộ test tồn tại và đỏ vì thiếu file phương án, không đỏ vì lỗi cú pháp.

## P2 — Phương án

- [x] **T2.1** (e20m) Dựng khung file phương án: tiêu đề, dòng Soul, mục lục, bảng so sánh 3 mô
  hình (Gitflow đầy đủ / GitHub Flow có phân loại / trunk-based thuần) mỗi dòng kèm link nguồn
  N2–N4, và bảng chép nguyên 6 chốt của user từ brief mục `## Hỏi đáp` — Test: ca bảng so sánh và ca 6 chốt chuyển XANH
  - Chạm: `docs/tdq/report/2026-09-05-0037-nghien-cuu-gitflow-branch-phuong-an.md` → file mới

  - Dùng: `tavily-primary` (mcp)
  - Để: dẫn lại đúng link nguồn cho ba dòng của bảng so sánh, không viết link từ trí nhớ
  - Ra: ba link `http` nằm trong bảng so sánh của file phương án
  - Kiểm: ca test bảng so sánh xanh
  - Không dùng cho: tra thêm chủ đề mới ngoài ba mô hình nhánh; research đã đóng ở phase analyze

- [x] **T2.2** (e32m) Viết 6 mục `G1`–`G6` lấp 6 khoảng trống của spec §1: mỗi mục nêu vấn đề,
  cách sửa đề xuất, dòng `**Chạm:**` trỏ đúng một file + một hàm/mục, và vị trí `file:dòng` đo lại
  bằng lệnh ngay lúc viết. `G1` phải nói rõ trường state mới chỉ được ghi qua `tdq_state.py` (ràng
  buộc kiến trúc ở spec §5) — Test: ca đếm 6 mục, ca `**Chạm:**`, ca `file:dòng` chuyển XANH
  - Chạm: `docs/tdq/report/2026-09-05-0037-nghien-cuu-gitflow-branch-phuong-an.md` → file nóng, tạo ở T2.1

- [x] **T2.3** (e24m) Viết vòng đời nhánh thành các bước có lệnh git nguyên văn: mở request (kiểm
  `git status` bẩn/sạch, ghi nhánh gốc, `git switch -c <loại>/<mô tả>`), làm việc, user confirm ở
  bước hỏi commit của report, merge `--no-ff` về nhánh gốc, `git branch -d`, và với mode
  `subagent` là dọn worktree ngay sau khi hợp task theo trình tự `git worktree remove` →
  `git worktree prune` → `git branch -d`. Kèm mục xử lý lệch nhánh (nhánh hiện tại khác nhánh đã
  lưu → dừng, hỏi user). Mọi tên nhánh mẫu chạy `git check-ref-format --branch` để xác nhận trước
  khi viết vào — Test: ca lệnh git, ca `check-ref-format`, ca cấm bốn chữ mở đầu chuyển XANH
  - Chạm: `docs/tdq/report/2026-09-05-0037-nghien-cuu-gitflow-branch-phuong-an.md` → file nóng, tạo ở T2.1

  - Dùng: `using-git-worktrees`
  - Để: đối chiếu trình tự tạo và dọn worktree của skill này với `tdq_team.py` trước khi chốt
    trình tự dọn viết vào phương án
  - Ra: mục dọn worktree trong vòng đời, nêu đủ ba lệnh theo thứ tự
  - Kiểm: ca test lệnh git xanh
  - Không dùng cho: chạy thật bất kỳ lệnh worktree nào trên repo — quy tắc thi hành số 5

- [x] **T2.4** (e16m) Viết lộ trình triển khai ≥3 giai đoạn `GĐ1`–`GĐ3`, xếp giai đoạn đụng
  `tdq_team.py` sau cùng theo spec §5; mỗi giai đoạn có dòng file bị chạm và dòng rủi ro riêng.
  Nêu thẳng va chạm giữa nhóm "AI Agent Source Prefixes" của Conventional Branch và luật §7 của
  `tdq-conventions`, chốt lấy tập con 5 loại — Test: ca giai đoạn chuyển XANH, bộ test của request xanh toàn bộ
  - Chạm: `docs/tdq/report/2026-09-05-0037-nghien-cuu-gitflow-branch-phuong-an.md` → file nóng, tạo ở T2.1

**Xong P2 khi**: bộ test của request xanh toàn bộ và `doc_lint.py` thoát 0 trên file phương án.

## P3 — Báo cáo & đóng sổ

- [x] **T3.1** (e14m) Viết báo cáo TDQ chuẩn: đã làm gì, quyết định tự chốt, bảng thời gian, tồn
  đọng (nhánh mồ côi cố ý giữ, chữ cũ về phase `diagram` trong `tdq-intake`) — Test: `python3 scripts/doc_lint.py` thoát 0 trên brief, spec, plan, QC và hai file báo cáo; ca cấm khẳng định quá tay xanh trên cả hai file
  - Chạm: `docs/tdq/report/2026-09-05-0037-nghien-cuu-gitflow-branch.md` → file mới

- [x] **T3.2** (e10m) Kiểm phạm vi rồi đóng sổ: `git status --short` không có dòng nào trong
  `scripts/`, `skills/` hay ba bundle; `git branch -a` và `git worktree list` khớp từng dòng với
  hai file mốc đã chụp; chạy toàn bộ suite đúng MỘT lần đối chiếu mốc đỏ có sẵn; chạy
  `tdq_finish.py` — Test: suite không vượt mốc đỏ có sẵn; `tdq_finish.py` in `lint=ok · worklog=ok`

**Xong P3 khi**: hai file báo cáo tồn tại, phạm vi sạch, suite không xấu đi, sổ đã ghi.

## Cụm song song

Không cụm nào chạy song song được. Bốn task T2.1–T2.4 cùng ghi một file phương án; T1.1 phải
xong trước để có test đỏ; T3.1 đọc lại kết quả của P2. Đây là lý do của dòng `Mode thực thi`.

## Definition of Done

Chiếu thẳng §6 của spec, 15 dòng, mỗi dòng một lệnh kiểm:

1. Phương án có đúng 6 mục `G1`–`G6` — `pytest -k dem_sau_muc`.
2. Mỗi mục có `**Chạm:**` và đường dẫn nêu ở đó tồn tại — `pytest -k cham_tro_dung`.
3. Bảng so sánh có 3 dòng mô hình, mỗi dòng một link — `pytest -k bang_so_sanh`.
4. Mỗi bước vòng đời có khối lệnh mở đầu bằng `git ` — `pytest -k co_lenh_git`.
5. Mọi tên nhánh mẫu hợp lệ với git — `pytest -k ten_nhanh_hop_le`.
6. Không tên nhánh mẫu nào phạm luật §7 — `pytest -k khong_pham_luat_bay`.
7. Có ≥3 giai đoạn, mỗi cái có dòng file và dòng rủi ro — `pytest -k giai_doan`.
8. Sáu chốt của user có mặt nguyên vẹn — `pytest -k sau_chot_user`.
9. Không câu nào khẳng định phương án đã thi hành — `pytest -k khong_khang_dinh_qua_tay`.
10. Mọi `file:dòng` trỏ đúng file và số dòng hợp lệ — `pytest -k vi_tri_that`.
11. Không thay đổi nào trong `scripts/`, `skills/`, ba bundle — `git status --short` rồi lọc, dán output.
12. Nhánh và worktree khớp mốc trước khi làm — `diff <(git branch -a) <mốc>` và `diff <(git worktree list) <mốc>`.
13. Bộ test của request xanh toàn bộ — `python3 -m pytest tests/test_bao_cao_gitflow.py -q`.
14. Suite không vượt mốc đỏ có sẵn — `python3 -m pytest -q`, chạy một lần ở T3.2.
15. `doc_lint.py` thoát 0 trên 6 file tài liệu — `python3 scripts/doc_lint.py <6 file>`.

## Ước tính

6 task, tổng `(e118m)`.
