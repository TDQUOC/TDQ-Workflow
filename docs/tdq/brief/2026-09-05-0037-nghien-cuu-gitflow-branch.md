# BRIEF — Nghiên cứu gitflow cho vòng đời request
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay bây giờ tôi muốn mở request nghiên cứu về gitflow, nghĩa là khi mở request thì sẽ phân
> biệt xem nó là feature, hya bugfix hay update, .... và khi xử lí sẽ tạo ra có prefix đó \ tên
> tính năng ví dụ feature\loginGUI nghĩa là khi bắt đầu ở request nào thì khi report xong và đc
> confirm xong sẽ commit và merge vào lại branch gốc mà request đc bắt đầu, và luôn giữ git
> worktree sạch sẽ luôn merge vào khi done hãy deep resreach giúp tôi và đề xuất phương án.
> request này là phân tích resreach và báo cáo chưa update ở request này

Câu trước đó của user trong cùng phiên (chốt phạm vi state): "1a" — đồng ý xoá request
`2026-09-04-2233-sua-man-check-diem` (mở nhầm, không để lại dấu vết trong repo) để mở request này.

**Đọc lần đầu của tôi**

- **Mục tiêu:** nghiên cứu và ĐỀ XUẤT phương án đưa mô hình nhánh kiểu gitflow vào vòng đời
  request của TDQ: phân loại request (feature / bugfix / update / …) ngay lúc mở, tạo nhánh
  `<loại>/<tên tính năng>`, làm việc trên nhánh đó, và khi report xong + user confirm thì commit
  và merge ngược về đúng nhánh gốc nơi request bắt đầu; worktree luôn sạch.
- **Phạm vi đoán:** `skills/tdq-intake` (chỗ mở request), `skills/tdq-build` (chỗ report + hỏi
  commit), `skills/tdq-conventions/references/git.md` (luật git hiện hành), `scripts/tdq_state.py`
  (state phải nhớ nhánh gốc), `scripts/tdq_team.py` (đã có sẵn worktree cho sub-agent).
- **Chỗ chưa rõ:**
  1. Bộ loại request gồm đúng những loại nào, và ai chọn — Claude tự phân loại hay hỏi user?
  2. Dấu phân cách: user viết `feature\loginGUI` (backslash). Git dùng `/`. Chốt cái nào?
  3. Nhánh mới cho MỌI request hay chỉ từ một cỡ việc nào đó (tầng `nhỏ`, lane quick)?
  4. Merge kiểu gì khi done: fast-forward, `--no-ff` giữ vết, hay squash? Có xoá nhánh sau merge?
  5. Quan hệ với worktree sẵn có của `tdq_team.py` (mode sub-agent đã tạo nhánh + worktree
     riêng mỗi task) — nhánh request nằm ở đâu trong sơ đồ đó?

## Hiểu & kiến thức

### B0 — Kiểm kê năng lực

| Năng lực | Nguồn | Phán quyết | Lý do |
|---|---|---|---|
| `using-git-worktrees` | plugin:superpowers | DÙNG | có sẵn trên đĩa, nói đúng chủ đề cô lập nhánh bằng worktree — đọc để đối chiếu với `tdq_team.py` |
| `tavily-primary` (mcp) | plugin | DÙNG | lớp research web, đã chạy 3 lượt ở B2 |
| `mcp__lsp__*` + lumen | plugin | DÙNG | tra ký hiệu `_ten_nhanh`, `default_state` thay vì đoán |
| `conventional-branch` | không có trên đĩa | KHÔNG | chỉ tồn tại ở thư viện ngoài; lấy phần đặc tả qua research, không cài plugin mới |
| `pr-to-video` | plugin:hyperframes | KHÔNG | khớp chữ "git" nhưng không liên quan |

Kiểm kê đầy đủ: `python3 scripts/skill_inventory.py --loc git` — giữ 2, ẩn 222.

### B1 — Đã đọc gì trong repo

- `skills/tdq-conventions/SKILL.md` §7 (dòng 131–137) — **toàn bộ luật git hiện hành**. Đoán ban
  đầu của tôi (`references/git.md`) là SAI: file đó không tồn tại. Luật hiện có đúng 4 ý: cấm tên
  nhánh/commit/worktree mở đầu bằng `claude|antigravity|gemini|codex`; cấm dấu vết AI trong commit
  message; cấm commit/push trước khi user yêu cầu (trừ commit gỡ kẹt khi build, không push, phải
  ghi vào report); repo chưa có git thì được init và phải kiểm nhánh merge về được.
- `scripts/tdq_state.py` — `default_state()` (dòng 154+), schema v4, 24 khoá. `VALID_LANES` dòng 33.
- `scripts/tdq_team.py` — `_ten_nhanh`, `_nhanh_tich_hop`, `_thu_muc_goc_worktree`, `lenh_hop`.
- `skills/tdq-build/references/report-template.md` bước 10 — chỗ duy nhất hỏi user về commit.
- `skills/tdq-intake/SKILL.md` Phần A — chỗ mở request, hiện chỉ chạm state, không chạm git.

### B2 — Đo được gì (không đoán)

**Đ1 — Dấu `\` mà user viết KHÔNG hợp lệ với git.** Đo bằng `git check-ref-format --branch`
(git 2.50.1):

| Chuỗi thử | Kết quả |
|---|---|
| `feature\loginGUI` | **REJECT** |
| `feature/loginGUI` | OK |
| `tdq/feature/login-gui` | OK |

Đây là ràng buộc cứng của git, không phải lựa chọn phong cách: phải dùng `/`.

**Đ2 — State hiện không nhớ nhánh nào cả.** 24 khoá của `default_state()` không có khoá nào liên
quan git. Nghĩa là "merge về đúng nhánh gốc nơi request bắt đầu" hiện KHÔNG có chỗ nào lưu được
"nhánh gốc" — phải thêm trường mới.

**Đ3 — Máy nhánh sẵn có chỉ chạy ở mode `subagent`, và cụt một đầu.** `tdq_team.py` tạo nhánh
task `tdq/<slug>/<task>` và nhánh tích hợp `tdq/<slug>/tich-hop`, worktree dưới `.tdq-worktrees/`,
`hop` = rebase rồi `git merge --no-ff` vào nhánh tích hợp. **Không lệnh nào merge nhánh tích hợp
ngược về nhánh user đang đứng.** Ở mode `main` thì không có nhánh nào cả — leader sửa thẳng checkout
của user.

**Đ4 — Hậu quả của Đ3 còn nằm trong repo.** `tdq/2026-08-23-1623-mindmap-html-hai-lop/tich-hop`
vẫn còn ở cả local lẫn origin dù nội dung đã vào `main` bằng đường khác. Đúng thứ user gọi là
"worktree không sạch".

**Đ5 — Chỗ "confirm xong" đã có sẵn.** `report-template.md` bước 10 bắt buộc hỏi user
"Bạn có muốn tôi commit phần thay đổi này không?" và cấm tự commit. Câu trả lời "commit" của user
chính là mốc confirm mà user mô tả — không cần phát minh gate mới, chỉ mở rộng hành động sau nó.

### B3 — Research ngoài (nguồn dẫn đầy đủ)

**N1 — Đặc tả tên nhánh đã có chuẩn công khai.** Conventional Branch: dạng `<type>/<description>`,
bộ type `feature|feat`, `bugfix|fix`, `hotfix`, `release`, `chore`; mô tả chỉ `a-z0-9-`; `main`,
`master`, `develop` là nhánh gốc, không mang prefix. Nguồn: https://conventionalbranch.org

**N1b — Cảnh báo va luật nội bộ.** Chính đặc tả đó có nhóm "AI Agent Source Prefixes" gồm
`claude/`, `codex/`, `cursor/`. **Xung đột trực tiếp** với luật §7 của repo (cấm tên nhánh mở đầu
bằng `claude|codex|...`). Nếu chọn Conventional Branch thì phải chọn tập con, bỏ nhóm AI prefix.
Nguồn: cùng trang trên.

**N2 — Ngành đang khuyên nhánh NGẮN NGÀY, không khuyên gitflow đầy đủ.** AWS Well-Architected
DevOps Guidance [DL.SCM.2] "Keep feature branches short-lived": gitflow nghiêng về nhánh dài ngày
→ merge phức tạp, code base phân kỳ; khuyến nghị trunk-based + PR với nhánh feature ngắn ngày.
Nguồn: https://docs.aws.amazon.com/wellarchitected/latest/devops-guidance/dl.scm.2-keep-feature-branches-short-lived.html

**N3 — Gitflow chỉ đáng dùng khi có release có lịch.** Thảo luận cộng đồng GitHub: đội nhỏ–vừa nên
GitHub Flow hoặc trunk-based; chỉ dùng Git Flow khi cần release đóng hộp theo lịch hoặc nhánh
release/hotfix sống lâu. Nguồn: https://github.com/orgs/community/discussions/180215

**N4 — GitHub Flow là điểm giữa.** Trunk-based nhưng có nhánh rất ngắn ngày + PR làm cổng.
Nguồn: https://shipyard.build/blog/gitflow-to-trunk-based-development

**N5 — Vệ sinh worktree là quy trình, không phải thói quen.** Xoá thư mục worktree bằng tay mà
không báo git sẽ để lại metadata mồ côi → `fatal: '<branch>' is already checked out` cho nhánh
tưởng như không ai dùng. Trình tự đúng: `git worktree remove` → `git worktree prune` → `git branch -d`
(chỉ `-d`, để git từ chối khi chưa merge). Nguồn: https://www.gitworktree.org/guides/workflow và
https://arbitlab.com/blog/git-worktree-cleanup

**N6 — Mô hình một-nhánh-một-worktree-một-task là mô hình được khuyên cho agent.** Nguồn:
https://aridanemartin.dev/blog/git-worktrees-ai-agents

**Kết luận research:** cái user mô tả KHÔNG phải Gitflow của Driessen (không có `develop`, không
có nhánh `release` sống lâu). Nó là **GitHub Flow có phân loại tên nhánh** — nhánh ngắn ngày mở từ
nhánh hiện tại, merge về đúng nhánh đó khi xong. Đó cũng là thứ N2–N4 khuyên. Tên gọi trong request
là "gitflow" nhưng nội dung là GitHub Flow; phương án sẽ bám nội dung.

### B4 — Khoảng trống phải lấp (đầu vào cho spec)

- **G1 — Không có nơi lưu nhánh gốc.** Thêm trường vào `default_state()` (kèm nâng schema).
- **G2 — Không có bước tạo nhánh lúc mở request.** `tdq-intake` Phần A hiện không chạm git.
- **G3 — Không có bước merge-về khi done.** `report-template.md` bước 10 dừng ở commit.
- **G4 — Không có bước dọn.** Không lệnh nào chạy `worktree prune` + `branch -d` sau khi merge;
  bằng chứng là Đ4.
- **G5 — Không có nơi lưu loại request.** Phân loại feature/bugfix/update chưa tồn tại ở bất kỳ
  đâu trong state hay brief.
- **G6 — Luật §7 chưa có mục tên nhánh.** Phải viết thêm, và phải tránh nhóm AI prefix của N1b.

### Lộ trình

`analyze` (đang chạy) → `spec` → `plan` → `implement` → `qc` → `report`. Phase `diagram` đã bị gỡ
khỏi máy trạng thái từ 2026-09-01 (`PHASE_DA_GO` trong `scripts/tdq_state.py`), nên không có trong
lộ trình này dù văn bản `tdq-intake` còn nhắc — đó là chữ cũ chưa cập nhật, đã ghi vào mục tồn đọng.

**Request này KHÔNG sửa code.** Đầu ra duy nhất là báo cáo phân tích + phương án đề xuất
(`docs/tdq/report/<slug>.md`). `implement` chỉ viết file báo cáo; mọi thay đổi vào `tdq_state.py`,
`tdq-intake`, `tdq-build`, `tdq_team.py` thuộc về một request SAU, mở riêng khi user duyệt phương án.

## Hỏi đáp

Câu trả lời của user (nguyên văn): `1a 2a 3a 4a 5a và bổ sung và worktree của subagent khi làm
xong nên đc merge vào và dọn workftree nha`

| # | Câu hỏi | Chốt |
|---|---|---|
| 1 | Bộ loại request | 5 loại theo Conventional Branch: `feature` / `bugfix` / `hotfix` / `chore` / `docs` |
| 2 | Ai phân loại | Claude tự đề xuất loại lúc mở request, **gộp vào câu hỏi chọn lane đang có**, không thêm lượt hỏi |
| 3 | Request nào mở nhánh | Lane `full` và `quick` mở nhánh; tầng `nhỏ` làm thẳng trên nhánh hiện tại |
| 4 | Kiểu merge | `git merge --no-ff` rồi `git branch -d`, xoá nhánh sau khi merge |
| 5 | Vị trí nhánh request | Nhánh request **thay vai** nhánh tích hợp hiện tại: nhánh task → nhánh request → nhánh gốc (3 tầng, bớt 1 so với hiện nay) |
| 6 (user bổ sung) | Worktree của sub-agent | Làm xong task là merge vào ngay rồi **dọn worktree ngay**, không để tồn đến cuối request |

**Đọc ý bổ sung của user:** hiện `tdq_team.py` có lệnh `don`/`don-dep` nhưng việc dọn không gắn
cứng vào mốc "task xong". Ý user là biến nó thành bước bắt buộc ngay sau `hop`, theo đúng trình tự
N5: `git worktree remove` → `git worktree prune` → `git branch -d`. Đây là một mục của phương án,
không phải request riêng.

**Không còn câu hỏi mở.**
