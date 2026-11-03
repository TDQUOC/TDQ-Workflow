# SPEC — Nghiên cứu mô hình nhánh git cho vòng đời request

Ngày: 2026-09-05 · Bản: 1.1 · Brief: ../brief/2026-09-05-0037-nghien-cuu-gitflow-branch.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐÃ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- **Mục tiêu:** viết ra một phương án đầy đủ, đủ chi tiết để một request sau có thể thi hành mà
  không phải nghiên cứu lại — mô tả vòng đời nhánh git của một request TDQ: phân loại lúc mở, tên
  nhánh, nhánh gốc được nhớ ở đâu, merge về lúc nào, dọn nhánh và worktree ra sao. Đo "đủ chi tiết"
  bằng: mỗi thay đổi đề xuất chỉ đúng một file + một hàm/mục cụ thể, và mỗi bước vòng đời có lệnh
  git nguyên văn chạy được.

- **Trong phạm vi:**
  - Sáu quyết định user đã chốt ở brief mục `## Hỏi đáp` (bộ loại, ai phân loại, request nào mở
    nhánh, kiểu merge, vị trí nhánh request, dọn worktree ngay sau khi task xong).
  - Sáu khoảng trống G1–G6 ở brief mục `### B4`, mỗi cái một mục trong phương án.
  - Bảng so sánh ba mô hình (Gitflow đầy đủ / GitHub Flow có phân loại / trunk-based thuần) dựa
    trên nguồn N2–N4 của brief, kèm lý do chọn.
  - Lộ trình triển khai chia giai đoạn, mỗi giai đoạn nêu file bị chạm và rủi ro của riêng nó.
  - Bộ test giữ cho các con số và vị trí `file:dòng` trong báo cáo khỏi mục theo thời gian.

- **NGOÀI phạm vi:**
  - **Mọi thay đổi thi hành phương án.** Không sửa `scripts/tdq_state.py`, `scripts/tdq_team.py`,
    `skills/tdq-intake/`, `skills/tdq-build/`, `skills/tdq-conventions/`. User nói nguyên văn:
    "request này là phân tích resreach và báo cáo chưa update ở request này".
  - Không tạo, đổi tên, xoá bất kỳ nhánh hay worktree nào của repo trong lúc chạy request này.
  - Không dựng lại ba bundle, không bump version, không commit khi user chưa yêu cầu.
  - Không đụng nhánh mồ côi `tdq/2026-08-23-1623-mindmap-html-hai-lop/tich-hop` — nó là **bằng
    chứng** của Đ4, xoá nó là xoá bằng chứng; phương án chỉ nêu cách dọn.
  - Không dùng pull request / GitHub API: repo này làm việc local, `origin` chỉ để đẩy khi user bảo.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

`analyze` (xong) → `spec` → `plan` → `implement` → `qc` → `report`. Phase `diagram` đã bị gỡ khỏi
máy trạng thái từ 2026-09-01 (`PHASE_DA_GO` trong `scripts/tdq_state.py`), nên không có mặt.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã xong) | Sáu nguồn N1–N6 ở brief; user yêu cầu nguyên văn "deep resreach" |
| Interview | CÓ (đã xong) | Năm câu, user chốt `1a 2a 3a 4a 5a` cộng một ý bổ sung |
| Diagram | BỎ | Phase đã bị gỡ khỏi máy trạng thái, `set phase=diagram` bị từ chối |
| QC độc lập (agent) | BỎ | Đầu ra là tài liệu, không có runtime; bộ test giữ báo cáo đã kiểm được bằng máy |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Phương án vòng đời nhánh: 6 mục, mỗi mục lấp một khoảng trống G1–G6, mỗi mục nêu đúng một file + một hàm/mục bị chạm | `docs/tdq/report/2026-09-05-0037-nghien-cuu-gitflow-branch-phuong-an.md` | Đếm được đúng 6 mục mã `G1`–`G6`; mỗi mục có dòng `**Chạm:**` trỏ file có thật |
| 2 | Bảng so sánh 3 mô hình nhánh, mỗi dòng kèm link nguồn | cùng file đầu ra 1 | Bảng có đúng 3 dòng mô hình và mỗi dòng chứa một `http` |
| 3 | Vòng đời nhánh viết thành các bước có lệnh git nguyên văn, từ lúc mở request đến lúc dọn xong | cùng file đầu ra 1 | Mỗi bước có ít nhất một khối lệnh bắt đầu bằng `git `; chạy `git check-ref-format` được trên mọi tên nhánh mẫu |
| 4 | Lộ trình triển khai chia giai đoạn, mỗi giai đoạn nêu file bị chạm và rủi ro riêng | cùng file đầu ra 1 | Có ≥3 giai đoạn mã `GĐ1`…; mỗi giai đoạn có dòng file và dòng rủi ro |
| 5 | Bộ test giữ báo cáo khỏi mục: kiểm số mục, kiểm mọi `file:dòng` còn trỏ đúng, kiểm mọi tên nhánh mẫu hợp lệ với git, cấm câu khẳng định đã thi hành | `tests/` | Chạy bộ test đó xanh toàn bộ |
| 6 | Báo cáo TDQ chuẩn của request | `docs/tdq/report/2026-09-05-0037-nghien-cuu-gitflow-branch.md` | Có bảng thời gian, mục quyết định tự chốt, mục tồn đọng |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| `phuong-an` | `docs/tdq/report/2026-09-05-0037-nghien-cuu-gitflow-branch-phuong-an.md` | không | 1, 2, 3, 4 |
| `test-giu-bao-cao` | `tests/` | `phuong-an` | 5 |
| `bao-cao` | `docs/tdq/report/2026-09-05-0037-nghien-cuu-gitflow-branch.md` | `phuong-an` | 6 |

Ba module không khai chung đường dẫn nào.

## 3. Cách tiếp cận & lý do

- **Chọn:** viết phương án theo mô hình **GitHub Flow có phân loại tên nhánh** — nhánh ngắn ngày
  mang prefix loại, mở từ nhánh user đang đứng, merge `--no-ff` về đúng nhánh đó rồi xoá; nhánh
  request thay luôn vai nhánh tích hợp hiện có của `tdq_team.py`; dọn worktree ngay khi task xong.

- **Vì:**
  - Đúng thứ user mô tả: user nói "merge vào lại branch gốc mà request đc bắt đầu", tức không có
    `develop`, không có nhánh `release` sống lâu — đó là định nghĩa của GitHub Flow, không phải
    Gitflow của Driessen.
  - Nguồn N2 (AWS Well-Architected [DL.SCM.2],
    https://docs.aws.amazon.com/wellarchitected/latest/devops-guidance/dl.scm.2-keep-feature-branches-short-lived.html):
    gitflow nghiêng về nhánh dài ngày gây merge phức tạp và phân kỳ; khuyến nghị nhánh ngắn ngày.
  - Nguồn N3 (https://github.com/orgs/community/discussions/180215): chỉ dùng Git Flow khi có
    release đóng hộp theo lịch. Repo này không có.
  - Nguồn N1 (https://conventionalbranch.org) cho sẵn dạng `<type>/<description>` và bộ type, khỏi
    tự chế — trừ nhóm "AI Agent Source Prefixes" phải bỏ, xem §5.
  - Nguồn N5 (https://www.gitworktree.org/guides/workflow): trình tự dọn đúng là
    `git worktree remove` → `git worktree prune` → `git branch -d`; xoá thư mục bằng tay để lại
    metadata mồ côi.

- **Đã loại:**
  - **Gitflow đầy đủ** (thêm nhánh `develop`, nhánh `release` sống lâu) — vì N2, N3; và repo không
    có lịch release, `main` chính là nhánh phát hành.
  - **Trunk-based thuần** (commit thẳng vào nhánh gốc, không mở nhánh) — vì mâu thuẫn thẳng với
    yêu cầu của user; và mất khả năng vứt bỏ nguyên một request hỏng bằng cách xoá một nhánh.
  - **Giữ 3 tầng nhánh** (task → tích hợp → request → gốc) — user chốt phương án A ở câu 5, và
    tầng tích hợp hiện tại chính là chỗ đẻ ra nhánh mồ côi Đ4.

## 3b. Năng lực & công cụ

Chép từ brief mục `### B0`.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-intake` | plugin:tdq-workflow | NỀN | skill khung đang chạy phase analyze/spec |
| `using-git-worktrees` | plugin:superpowers | DÙNG | đầu ra 3 — đối chiếu trình tự dọn worktree của nó với `tdq_team.py` trước khi viết vòng đời |
| `tavily-primary` | plugin (mcp) | DÙNG | đầu ra 2 — lấy và dẫn nguồn ba mô hình nhánh |
| Đã xét 224 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service: BỎ — request này không đẻ ra runtime, đầu ra là tài liệu cộng một bộ test đọc tài liệu.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh: đầu ra 5 là bộ test đó, phủ đầu ra 1–4.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`, và
  bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`.
- **Mọi con số và mọi vị trí `file:dòng` trong phương án phải đo được lại bằng lệnh.** Không có
  con số nào đến từ trí nhớ.
- **Mọi tên nhánh mẫu viết trong phương án phải qua được `git check-ref-format --branch`.**

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ dòng việc này chạm tới):

- `Dữ liệu request | docs/tdq/ | brief, spec, plan, qc, report, state — dữ liệu, không phải code`
  — việc này chạm ở hai file mới trong `docs/tdq/report/`.
- `Chỉ scripts/tdq_state.py được ghi docs/tdq/state.json; mọi nơi khác chỉ đọc qua CLI.`
  — phương án đề xuất thêm trường vào state, nên phải nói rõ trường đó ghi qua `tdq_state.py`,
  không ai ghi thẳng file.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Đặc tả Conventional Branch có nhóm prefix `claude/`, `codex/` — đụng luật §7 của `tdq-conventions` cấm tên nhánh mở đầu bằng đúng những chữ đó | Chép nguyên đặc tả vào là sinh ra luật tự mâu thuẫn | Phương án phải nêu thẳng va chạm này và chốt lấy tập con 5 loại, bỏ nhóm AI prefix; bộ test đầu ra 5 kiểm không tên nhánh mẫu nào mở đầu bằng 4 chữ bị cấm |
| Nhánh request thay vai nhánh tích hợp là thay đổi hành vi `tdq_team.py`, chạm mode `subagent` đang chạy được | Làm hỏng luồng sub-agent ở request sau | Phương án tách giai đoạn: giai đoạn đụng `tdq_team.py` đứng sau cùng và nêu rủi ro riêng; request này không sửa dòng nào |
| Request đang chạy dở mà user đổi nhánh bằng tay | Nhánh gốc lưu trong state không còn khớp thực tế | Phương án phải có mục xử lý lệch: kiểm nhánh hiện tại so với nhánh đã lưu trước khi merge, lệch thì dừng và hỏi user |
| Repo có thay đổi chưa commit lúc mở request | `git switch -c` kéo theo thay đổi lạ sang nhánh mới | Phương án phải nêu bước kiểm `git status` trước khi mở nhánh và cách xử lý khi bẩn |
| Vị trí `file:dòng` trong phương án mục theo thời gian | Báo cáo dẫn sai chỗ | Đầu ra 5 mở từng vị trí, kiểm file có thật và số dòng nằm trong file |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Phương án lấp đủ khoảng trống | Đếm được đúng 6 mục mã `G1`–`G6` trong file phương án |
| Q2 | Mỗi mục trỏ chỗ sửa cụ thể | Mỗi mục `G1`–`G6` có dòng `**Chạm:**`, và mọi đường dẫn nêu ở đó tồn tại trên đĩa |
| Q3 | Bảng so sánh có nguồn | Bảng 3 mô hình có đúng 3 dòng mô hình, mỗi dòng chứa một link `http` |
| Q4 | Vòng đời có lệnh chạy được | Mỗi bước vòng đời có ít nhất một khối lệnh mở đầu bằng `git ` |
| Q5 | Tên nhánh mẫu hợp lệ | Mọi tên nhánh mẫu trong phương án được `git check-ref-format --branch` chấp nhận |
| Q6 | Tên nhánh mẫu không phạm luật §7 | Không tên nhánh mẫu nào mở đầu bằng `claude`, `antigravity`, `gemini`, `codex` |
| Q7 | Lộ trình chia giai đoạn | Có ≥3 giai đoạn mã `GĐ1`…, mỗi giai đoạn có dòng file bị chạm và dòng rủi ro riêng |
| Q8 | Sáu quyết định của user có mặt nguyên vẹn | Cả 6 chốt ở brief mục `## Hỏi đáp` xuất hiện trong phương án, không cái nào bị đổi ý ngầm |
| Q9 | Không khẳng định quá tay | Không câu nào trong hai file báo cáo nói phương án đã được thi hành hay đã chạy thật |
| Q10 | Vị trí dẫn còn đúng | Mọi vị trí `file:dòng` trong phương án trỏ file có thật và số dòng không vượt độ dài file |
| Q11 | Không đụng vùng ngoài phạm vi | `git status` không cho thấy thay đổi nào trong `scripts/`, `skills/`, ba bundle |
| Q12 | Không đụng nhánh và worktree | Danh sách nhánh và danh sách worktree sau khi làm xong trùng khớp danh sách trước khi làm |
| Q13 | Bộ test giữ báo cáo xanh | Bộ test của request chạy xanh toàn bộ |
| Q14 | Suite không xấu đi | Toàn bộ suite không vượt mốc đỏ có sẵn |
| Q15 | Tài liệu sạch lint | `doc_lint.py` thoát 0 trên brief, spec, plan, qc và hai file báo cáo |

**DoD:** đủ 15 hạng mục Q1–Q15 PASS, kèm bằng chứng là output thật dán vào file QC; hai file báo
cáo và bộ test tồn tại; không một file nào trong `scripts/`, `skills/` hay ba bundle bị đổi.

## 7. Câu hỏi còn mở

(Rỗng.)
