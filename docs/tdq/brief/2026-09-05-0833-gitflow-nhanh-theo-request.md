# BRIEF — Thi hành vòng đời nhánh git theo request

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> 1b 2b và tôi muốn là tdq-workflow sẽ tuân theo và luôn mở nhánh git cho phù hợp với request

Trả lời hai câu hỏi cuối lượt trước: **1b** = mở request mới làm cả ba giai đoạn GĐ1–GĐ3 trong
một lượt; **2b** = chưa commit request nghiên cứu `2026-09-05-0037-nghien-cuu-gitflow-branch`.

**Đọc lần đầu.** Thi hành phương án đã nghiên cứu và đã được user chốt sáu điểm ở request trước:
mỗi request TDQ tự phân loại (`feature`/`bugfix`/`hotfix`/`chore`/`docs`), tự mở nhánh
`<loại>/<mô tả>` từ nhánh đang đứng, làm trên nhánh đó, và khi user xác nhận ở bước hỏi commit
thì `git merge --no-ff` về nhánh gốc rồi `git branch -d`. Câu "luôn mở nhánh cho phù hợp" là yêu
cầu về mức ràng buộc: đây thành hành vi mặc định của workflow, không phải tuỳ chọn.

**Phạm vi đoán.** Ba giai đoạn của phương án cũ, gộp một request:
GĐ1 `scripts/tdq_state.py` (3 khoá mới + `schema_version` 4→5) ·
GĐ2 `skills/tdq-intake/SKILL.md`, `skills/tdq-build/references/report-template.md`,
`skills/tdq-conventions/SKILL.md` + dựng lại ba bundle ·
GĐ3 `scripts/tdq_team.py` (nhánh request thay vai nhánh tích hợp).

**Chỗ chưa rõ, phải hỏi.**

1. Lane nào (và loại request nào, gộp cùng một câu hỏi).
2. "Luôn mở nhánh" áp cho cả tầng `nhỏ` hay giữ chốt C3 cũ (chỉ `full` và `quick`).
3. Request này có tự mở nhánh cho chính nó không — dogfood ngay, hay chạy trên `main` rồi mới bật.
4. File state schema 4 đang tồn tại xử lý ra sao khi nâng lên 5.
5. Nhánh mồ côi `tdq/2026-08-23-1623-mindmap-html-hai-lop/tich-hop` dọn luôn trong request này hay giữ.

## Hiểu & kiến thức

### B0 — Kiểm kê năng lực

`skill_inventory.py --loc git` — giữ 2, ẩn 222.

| Skill | Nguồn | Phán quyết |
|---|---|---|
| `using-git-worktrees` | plugin | DÙNG |
| `pr-to-video` | plugin | KHÔNG |
| `tavily-primary` | plugin (mcp) | KHÔNG |

`tavily-primary` để KHÔNG vì phần tra ngoài đã làm xong ở request
`2026-09-05-0037-nghien-cuu-gitflow-branch`; việc này là thi hành, không nghiên cứu lại.

### B1 — Đã đọc gì

- `scripts/tdq_state.py` — `default_state()` (dòng 153) và chỗ nạp state (dòng 334–338).
- `scripts/tdq_team.py` — `_ten_nhanh` (588), `_nhanh_tich_hop` (595), `_bao_dam_tich_hop` (619),
  `lenh_mo` (792), `_thu_don` (763), `lenh_hop` (1005), `lenh_don` (1204).
- `skills/tdq-intake/SKILL.md` — Phần A bước 2 (60) và bước 3 (71).
- `skills/tdq-build/references/report-template.md` — bước 10 (25).
- `skills/tdq-conventions/SKILL.md` — mục `## 7. Git` (131).

### B2 — Đo được gì

- **Đ1 — Nâng schema không cần viết mã chuyển đổi.** Chỗ nạp state đã làm sẵn:
  `state.update(data)` rồi `setdefault` từng khoá mặc định, cuối cùng ép
  `state["schema_version"]` về số hiện tại (`scripts/tdq_state.py:334-338`). Thêm khoá mới vào
  `default_state()` là file state cũ tự có khoá đó với giá trị mặc định. Điều chưa rõ số 4 ở mục
  `## Nguyên văn` khép lại tại đây, và một rủi ro của phương án cũ biến mất.
- **Đ2 — Nhánh task hiện base từ nhánh tích hợp**, không phải từ nhánh user
  (`scripts/tdq_team.py:813`). Bỏ nhánh tích hợp là đổi đúng một đối số của lệnh đó thành nhánh
  request, cộng với gỡ `_bao_dam_tich_hop` khỏi `lenh_mo`.
- **Đ3 — Bước 10 của báo cáo đã có sẵn hai nhánh trả lời** "commit" và "chưa"
  (`skills/tdq-build/references/report-template.md:40`). Chỗ móc việc merge vào là nhánh
  "commit"; nhánh "chưa" hiện không làm gì, và đó là chỗ phải chốt thêm.
- **Đ4 — Luật §7 có đúng 4 gạch đầu dòng** (`skills/tdq-conventions/SKILL.md:133-136`), trong đó
  dòng cuối đã nói tới worktree phải merge về — tinh thần đã có, chỉ thiếu hình dạng tên nhánh.

### B3 — Nguồn ngoài

Không tra mới. Toàn bộ nguồn N1–N6 và bảng so sánh ba mô hình nằm ở
`docs/tdq/report/2026-09-05-0037-nghien-cuu-gitflow-branch-phuong-an.md`, request liền trước.

### B4 — Còn thiếu gì, phải hỏi user

- G-A: tầng `nhỏ` có mở nhánh không — chốt C3 cũ nói không, nhưng câu "luôn mở nhánh" lượt này
  có thể đã đổi ý.
- G-B: user trả lời "chưa" ở bước hỏi commit thì nhánh request xử lý ra sao.
- G-C: repo bẩn lúc mở request thì dừng hỏi hay tự xử.
- G-D: nhánh mồ côi đang có dọn luôn hay giữ.

### Lộ trình

| Phase | Chạy | Vì sao |
|---|---|---|
| analyze | có | đụng schema state và mã sub-agent, phải hỏi cho hết mơ hồ |
| spec | có | lane full |
| plan | có | lane full |
| implement | có | đây là request thi hành |
| qc | có | có mã chạy được, phải đo |
| report | có | mặc định |

Phase `diagram` không có trong lộ trình: `PHASE_DA_GO` của `scripts/tdq_state.py` đã gỡ phase đó
từ 2026-09-01.

## Hỏi đáp

User trả lời `1a 2b 3a 4a`:

| Mã | Câu hỏi | Chốt |
|---|---|---|
| G-A | Tầng `nhỏ` có mở nhánh không | KHÔNG — giữ chốt C3 cũ, chỉ lane `full` và `quick` mở nhánh |
| G-B | Trả lời "chưa" ở bước hỏi commit thì nhánh xử lý sao | VẪN merge về nhánh gốc, chỉ là không tạo commit mới |
| G-C | Repo bẩn lúc mở request | DỪNG, in ra file đang bẩn, hỏi user |
| G-D | Nhánh mồ côi `tdq/2026-08-23-1623-mindmap-html-hai-lop/tich-hop` | DỌN trong request này, cả local lẫn origin |

**Một hệ quả của G-B phải xử lý, không được để mờ.** "Chưa commit" mà "vẫn merge" thì phần chưa
commit không có gì để merge — nó nằm ở working tree và sẽ đi theo sang nhánh gốc lúc
`git switch`. Đúng thứ nguy hiểm mà G-C vừa chốt là phải dừng và hỏi. Cách xử lý viết vào spec:
merge phần ĐÃ commit, còn nếu working tree vẫn bẩn thì in cảnh báo và hỏi user trước khi chuyển
nhánh, dùng chung một khuôn với G-C.
