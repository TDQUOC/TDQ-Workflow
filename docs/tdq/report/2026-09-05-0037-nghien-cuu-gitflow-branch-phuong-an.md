# PHƯƠNG ÁN — Vòng đời nhánh git cho một request TDQ

Ngày: 2026-09-05 · Spec: ../spec/2026-09-05-0037-nghien-cuu-gitflow-branch.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐỀ XUẤT — request này chỉ nghiên cứu, chưa sửa một dòng mã nào của workflow.

## Mục lục

- Tóm tắt
- Sáu chốt của user
- Bảng so sánh ba mô hình
- G1 → G6 — sáu khoảng trống và cách lấp
- Vòng đời nhánh, bước B1 → B5
- Lộ trình triển khai, GĐ1 → GĐ3

## Tóm tắt

Cái user mô tả không phải Gitflow của Driessen: không có `develop`, không có nhánh phát hành sống
lâu. Nó là **GitHub Flow có phân loại tên nhánh** — mở nhánh ngắn ngày từ đúng nhánh đang đứng,
làm, rồi merge về đúng nhánh đó và xoá. Phương án này bám nội dung đó, không bám cái tên.

Mô hình đề xuất, một dòng: **một request = một nhánh `<loại>/<mô tả>` = một vòng đời khép kín, mở
lúc `init` và đóng lúc user gõ "commit" ở cuối báo cáo.**

## Sáu chốt của user

Chép từ brief mục `## Hỏi đáp`, không diễn giải thêm.

| # | Nội dung chốt |
|---|---|
| C1 | Bộ loại request lấy theo Conventional Branch: `feature/`, `bugfix/`, `hotfix/`, `chore/`, `docs/` |
| C2 | Claude tự đề xuất loại lúc mở request, gộp vào câu hỏi chọn lane đang có, không thêm lượt hỏi |
| C3 | Lane `full` và `quick` mở nhánh; tầng `nhỏ` làm thẳng trên nhánh hiện tại |
| C4 | Merge bằng `git merge --no-ff`, xong thì `git branch -d` |
| C5 | Nhánh request thay vai nhánh tích hợp hiện có, bớt một tầng |
| C6 | Worktree của sub-agent: xong task là merge vào rồi dọn worktree ngay |

## Bảng so sánh ba mô hình

| Mô hình | Hình dạng | Vì sao chọn hoặc loại | Nguồn |
|---|---|---|---|
| Gitflow đầy đủ | `main` + `develop` + nhánh phát hành và hotfix sống lâu | LOẠI — repo không có lịch phát hành, `main` chính là bản phát hành; nhánh dài ngày gây phân kỳ và merge phức tạp | https://docs.aws.amazon.com/wellarchitected/latest/devops-guidance/dl.scm.2-keep-feature-branches-short-lived.html |
| GitHub Flow có phân loại | một nhánh gốc + nhánh ngắn ngày mang tiền tố loại, merge về rồi xoá | **CHỌN** — đúng thứ user mô tả, và là điểm giữa được khuyến nghị cho đội nhỏ | https://github.com/orgs/community/discussions/180215 |
| Trunk-based thuần | commit thẳng vào nhánh gốc, không mở nhánh | LOẠI — mâu thuẫn thẳng với yêu cầu của user, và mất khả năng vứt bỏ nguyên một request hỏng bằng một lệnh xoá nhánh | https://trunkbaseddevelopment.com |

Đặc tả tên nhánh lấy từ https://conventionalbranch.org — dạng `<type>/<description>`, mô tả chỉ
gồm `a-z0-9-`, nhánh gốc (`main`, `master`, `develop`) không mang tiền tố.

**Cảnh báo va chạm, phải xử lý trước khi thi hành.** Chính đặc tả đó có thêm nhóm "AI Agent Source
Prefixes" gồm `claude/`, `codex/`, `cursor/`. Nhóm này **đụng thẳng** luật §7 của
`skills/tdq-conventions/SKILL.md:133`, câu cấm tên nhánh mở đầu bằng `claude`, `antigravity`,
`gemini`, `codex`. Phương án chốt **lấy tập con năm loại ở C1 và bỏ hẳn nhóm AI prefix**; luật §7
không đổi một chữ.

## G1 — State không có chỗ nhớ nhánh gốc và loại request

`default_state()` trả về 24 khoá, không khoá nào liên quan git. Nghĩa là câu "merge về lại branch
gốc mà request được bắt đầu" hiện không có chỗ nào lưu được "branch gốc" là cái gì.

**Chạm:** `scripts/tdq_state.py` — hàm `default_state()`

Vị trí: `scripts/tdq_state.py:153`.

Cách sửa đề xuất: thêm ba khoá và nâng `schema_version` từ 4 lên 5.

- `loai_request` — một trong năm giá trị của C1, hoặc `null` ở tầng `nhỏ`.
- `nhanh_goc` — tên nhánh đọc được lúc `init`, ví dụ `main`.
- `nhanh_request` — tên nhánh đã mở, ví dụ `feature/login-gui`.

Ba khoá này chỉ được ghi qua `tdq_state.py set`, không nơi nào ghi thẳng `docs/tdq/state.json` —
giữ nguyên ràng buộc kiến trúc ở `docs/kien-truc.md`.

## G2 — Mở request không chạm git

Phần A của intake hiện chỉ gọi `tdq_state.py init`; không lệnh git nào chạy, nên request bắt đầu
ngay trên nhánh user đang đứng.

**Chạm:** `skills/tdq-intake/SKILL.md` — Phần A, bước 3

Vị trí: `skills/tdq-intake/SKILL.md:71`.

Cách sửa đề xuất: thêm bước 3b ngay sau `init`, chạy bước B1 của vòng đời bên dưới. Bước này chỉ
chạy ở lane `full` và `quick` (chốt C3).

## G3 — Báo cáo dừng ở commit, không có bước merge về

Bước 10 của khuôn báo cáo bắt buộc hỏi user "Bạn có muốn tôi commit phần thay đổi này không?" và
cấm tự commit. Câu trả lời "commit" chính là mốc "được confirm" mà user mô tả — không cần phát
minh cổng mới. Nhưng sau khi commit thì hết, không ai merge về nhánh gốc.

**Chạm:** `skills/tdq-build/references/report-template.md` — bước 10

Vị trí: `skills/tdq-build/references/report-template.md:25`.

Cách sửa đề xuất: mở rộng hành động sau câu trả lời "commit" thành bước B3 và B4 của vòng đời.
Câu hỏi giữ nguyên chữ, chỉ thêm một dòng nói rõ commit xong sẽ merge về nhánh nào.

## G4 — Nhánh tích hợp không bao giờ về đích

Đây là chỗ tôi đo lại và phải sửa cách hiểu ban đầu ở brief. Ở mức TASK, máy đã chạy đúng: `hop`
merge nhánh task vào nhánh tích hợp rồi gọi ngay `_thu_don`, hàm này `git worktree remove`,
`git worktree prune` và xoá nhánh task. Nghĩa là **chốt C6 của user ở mức task thì mã hiện tại đã
làm rồi**, không phải khoảng trống.

Khoảng trống nằm cao hơn đúng một tầng: nhánh tích hợp `tdq/<slug>/tich-hop` và worktree của nó
không ai merge về nhánh gốc, không ai xoá. Bằng chứng còn nằm trong repo lúc viết báo cáo này:
nhánh `tdq/2026-08-23-1623-mindmap-html-hai-lop/tich-hop` vẫn có mặt ở cả local lẫn `origin`, dù
nội dung của nó đã vào `main` bằng đường khác. Request này cố ý không xoá nó — nó là bằng chứng.

**Chạm:** `scripts/tdq_team.py` — hàm `_bao_dam_tich_hop`

Vị trí: `scripts/tdq_team.py:619` (tạo nhánh tích hợp), `scripts/tdq_team.py:1058` (chỗ dọn cấp
task đã chạy đúng), `scripts/tdq_team.py:1204` (lệnh dọn cuối đợt).

Cách sửa đề xuất theo chốt C5: bỏ hẳn nhánh tích hợp riêng, cho **nhánh request đóng luôn vai đó**.
Nhánh task merge thẳng vào nhánh request, và nhánh request đã có sẵn đường về nhánh gốc ở B3.
Ba tầng thay vì bốn, và cái tầng từng đẻ ra nhánh mồ côi biến mất.

## G5 — Không có chỗ phân loại request

Phân loại feature / bugfix / update chưa tồn tại ở bất kỳ đâu: không trong state, không trong
brief, không trong câu hỏi chọn lane.

**Chạm:** `skills/tdq-intake/SKILL.md` — Phần A, bước 2

Vị trí: `skills/tdq-intake/SKILL.md:60`.

Cách sửa đề xuất theo chốt C2: giữ nguyên câu hỏi chọn lane, thêm vào ngay trên hai lựa chọn một
dòng `Loại: <loại đề xuất> — <lý do một câu>`. User im lặng là nhận loại đó; user gõ tên loại khác
thì lấy loại user gõ. Không thêm lượt hỏi thứ hai.

## G6 — Luật §7 chưa có mục tên nhánh

Mục `## 7. Git` hiện có đúng bốn ý, và không ý nào nói tên nhánh phải có hình dạng gì.

**Chạm:** `skills/tdq-conventions/SKILL.md` — mục `## 7. Git`

Vị trí: `skills/tdq-conventions/SKILL.md:131`.

Cách sửa đề xuất: thêm hai gạch đầu dòng, không đụng bốn ý cũ.

- Tên nhánh request có dạng `<loại>/<mô tả>`, loại thuộc đúng năm giá trị của C1, mô tả chỉ gồm
  `a-z`, `0-9` và dấu `-`. Ví dụ hợp lệ: `feature/login-gui`, `bugfix/state-mat-nhanh-goc`,
  `hotfix/hook-treo-turn`, `chore/bump-phien-ban`, `docs/kien-truc-module`.
- Dấu phân cách là `/`, không phải `\`. Đây là ràng buộc của git chứ không phải phong cách:
  `git check-ref-format --branch 'feature\loginGUI'` trả về mã lỗi, `feature/loginGUI` thì không.

## Vòng đời nhánh

Năm bước dưới đây là toàn bộ vòng đời. Mỗi bước kèm lệnh chạy được.

### B1 — Mở request, mở nhánh

Chạy ngay sau `tdq_state.py init`, chỉ ở lane `full` và `quick`.

```
git status --porcelain
git rev-parse --abbrev-ref HEAD
git switch -c feature/login-gui
```

Lệnh đầu để kiểm chỗ làm việc có bẩn không. Bẩn thì **dừng và hỏi user**, không tự stash: thay đổi
chưa commit là của user, `switch -c` sẽ kéo nó sang nhánh mới và trộn vào việc khác. Lệnh thứ hai
lấy tên nhánh gốc, ghi vào `nhanh_goc`. Lệnh thứ ba mở nhánh, tên ghi vào `nhanh_request`.

### B2 — Làm việc trên nhánh

Không có gì mới ở mức lệnh: các phase `spec` → `plan` → `implement` → `qc` → `report` chạy y như
hiện nay, chỉ khác là chúng đứng trên nhánh request. Mode `subagent` thì nhánh task mở từ nhánh
request và merge về nó:

```
git merge --no-ff tdq/<slug>/t1-1
```

### B3 — User confirm rồi merge về nhánh gốc

Chạy sau khi user trả lời "commit" ở bước 10 của báo cáo.

```
git add -A && git commit -m "<mô tả thay đổi>"
git switch main
git merge --no-ff feature/login-gui
```

`--no-ff` theo chốt C4: giữ lại vết một request là một cụm commit, đọc lịch sử vẫn thấy ranh giới.
Không push — luật §7 vẫn cấm push khi user chưa bảo.

### B4 — Dọn, không để lại gì

```
git branch -d feature/login-gui
git worktree remove <đường dẫn worktree>
git worktree prune
```

Dùng `-d` chứ không `-d` viết hoa: `-d` để git tự từ chối khi nhánh chưa merge thật, đó là lớp bảo
hiểm cuối. Với mode `subagent` thì hai lệnh worktree chạy ngay khi từng task xong, theo chốt C6 —
mã hiện tại đã làm đúng phần này. Xoá thư mục worktree bằng tay là sai: git vẫn giữ metadata và
lần sau báo `fatal: ... is already checked out` cho một nhánh tưởng như không ai dùng.

### B5 — Xử lý lệch nhánh

Trường hợp user tự `switch` sang nhánh khác giữa chừng. Kiểm trước mọi lần merge:

```
git rev-parse --abbrev-ref HEAD
```

Kết quả khác `nhanh_request` đang lưu trong state → **dừng, in cả hai tên, hỏi user**. Cấm tự
đoán ý và cấm tự chuyển nhánh: chuyển nhầm là mang thay đổi của user đi chỗ khác.

## Lộ trình triển khai

Ba giai đoạn, xếp theo mức rủi ro tăng dần. Giai đoạn đụng `tdq_team.py` đứng sau cùng.

### GĐ1 — Nền: state nhớ được nhánh và loại

Lấp G1. Không đổi hành vi nào, chỉ thêm khoá và nâng schema.

- Chạm: `scripts/tdq_state.py`
- Rủi ro: file state cũ ở schema 4 phải đọc được sau khi nâng lên 5 — cần đường nâng cấp và test
  đọc file cũ, nếu không mọi request đang dở sẽ vỡ.

### GĐ2 — Vòng đời cơ bản cho mode `main`

Lấp G2, G3, G5, G6. Đây là phần cho ra giá trị lớn nhất và không đụng mã sub-agent.

- Chạm: `skills/tdq-intake/SKILL.md`, `skills/tdq-build/references/report-template.md`,
  `skills/tdq-conventions/SKILL.md`
- Rủi ro: ba bundle portable là bản sinh ra từ `scripts/build_portable.py`; sửa skill mà quên dựng
  lại thì bản chạy trên host khác vẫn là luật cũ.

### GĐ3 — Gộp tầng nhánh của mode `subagent`

Lấp G4. Để sau cùng vì đây là chỗ duy nhất đụng mã đang chạy được.

- Chạm: `scripts/tdq_team.py`
- Rủi ro: bỏ nhánh tích hợp là đổi hành vi của `hop` và `don` — hỏng chỗ này là hỏng cả luồng
  sub-agent; cần chạy thử trọn một request nhiều task trong repo nháp trước khi chốt.

### Ghi chú về độ tươi của báo cáo

Mọi vị trí `file:dòng` ở trên được đo lúc 2026-09-05. Bộ test đi kèm request này mở lại từng vị
trí mỗi lần chạy, nên nếu mã nguồn đổi thì test đỏ và báo cáo phải sửa.
