# SPEC — Thi hành vòng đời nhánh git theo request

Ngày: 2026-09-05 · Bản: 1.0 · Trạng thái: CHỜ DUYỆT · Brief: ../brief/2026-09-05-0833-gitflow-nhanh-theo-request.md
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## 1. Mục tiêu & phạm vi

**Mục tiêu.** Mỗi request TDQ ở lane `full` hoặc `quick` tự phân loại, tự mở nhánh
`<loại>/<mô tả>` từ nhánh user đang đứng, làm trên nhánh đó, và khi tới bước hỏi commit thì
merge `--no-ff` về nhánh gốc rồi xoá nhánh. Đây là hành vi mặc định, không phải tuỳ chọn.

**Trong phạm vi.**

- `scripts/tdq_state.py`: 3 khoá mới + nâng `schema_version` 4 → 5.
- `skills/tdq-intake/SKILL.md`: đề xuất loại request trong chính câu hỏi chọn lane; mở nhánh sau `init`.
- `skills/tdq-build/references/report-template.md`: merge về nhánh gốc ở bước 10.
- `skills/tdq-conventions/SKILL.md`: bổ sung luật hình dạng tên nhánh vào mục `## 7. Git`.
- `scripts/tdq_team.py`: nhánh request thay vai nhánh tích hợp.
- Dựng lại ba bundle `portable_claude/`, `portable_codex/`, `antigravity_portable/`.
- Dọn nhánh mồ côi `tdq/2026-08-23-1623-mindmap-html-hai-lop/tich-hop`, cả local lẫn `origin`.

**Ngoài phạm vi.**

- Tầng `nhỏ` không mở nhánh (chốt G-A) — không sửa gì ở phần mô tả tầng đó.
- Không đụng tới `git push`: luật §7 cấm push khi user chưa bảo, giữ nguyên.
- Không thêm nhóm prefix `claude/`, `codex/` của đặc tả Conventional Branch (đụng luật §7).
- Không đổi bộ phase, không đổi cổng duyệt.
- Không sửa bộ đếm skill của router và các nợ đỏ cũ không liên quan.

## 1b. Lộ trình

| Phase | Chạy | Vì sao |
|---|---|---|
| analyze | xong | 4 điểm mơ hồ đã chốt ở brief mục `## Hỏi đáp` |
| spec | đang | file này |
| plan | có | lane full |
| implement | có | request thi hành |
| qc | có | có mã chạy được |
| report | có | mặc định |

Phase `diagram` không có: `PHASE_DA_GO` của `scripts/tdq_state.py` đã gỡ từ 2026-09-01.

## 2. Đầu ra cụ thể

1. **State nhớ được nhánh.** `default_state()` có `loai_request`, `nhanh_goc`, `nhanh_request`;
   `schema_version` = 5. File state schema 4 cũ đọc lên vẫn chạy, ba khoá mới nhận giá trị mặc định.
2. **Intake mở nhánh.** Câu hỏi chọn lane có thêm dòng đề xuất loại; sau `init`, bước mở nhánh
   chạy ở lane `full` và `quick`, kiểm `git status` trước, ghi nhánh gốc vào state.
3. **Báo cáo merge về.** Bước 10 mô tả rõ hai nhánh trả lời: "commit" thì commit rồi merge
   `--no-ff` về nhánh gốc và `git branch -d`; "chưa" thì vẫn merge phần đã commit về nhánh gốc,
   nhưng working tree còn bẩn thì dừng và hỏi user trước khi chuyển nhánh.
4. **Luật tên nhánh.** Mục `## 7. Git` có thêm hình dạng `<loại>/<mô tả>`, 5 loại, dấu `/` chứ
   không phải `\`, và câu nói rõ vì sao (`git check-ref-format` từ chối dạng kia).
5. **Đội sub-agent bớt một tầng.** Nhánh task base từ nhánh request; nhánh tích hợp riêng không
   còn được tạo; `hop` merge nhánh task về nhánh request.
6. **Ba bundle dựng lại**, cả ba CLEAN.
7. **Nhánh mồ côi biến mất** ở local và `origin`.
8. **Bộ test đi kèm** phủ từng đầu ra trên, chạy trong repo tạm chứ không đụng repo thật.

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc vào |
|---|---|---|
| M1 state | `scripts/tdq_state.py` | không phụ thuộc module nào khác |
| M2 luật & khuôn | `skills/tdq-intake/SKILL.md`, `skills/tdq-build/references/report-template.md`, `skills/tdq-conventions/SKILL.md` | đọc khoá của M1 qua CLI |
| M3 đội | `scripts/tdq_team.py` | đọc `active_request` của M1 qua CLI |
| M4 bundle | `portable_claude/`, `portable_codex/`, `antigravity_portable/` | sinh ra từ M2 và M1, không sửa tay |

M1 phải xong trước M2 và M3; M4 xong sau cùng.

## 3. Cách tiếp cận & lý do

**Ba tầng thành hai tầng.** Hiện là nhánh task → nhánh tích hợp → nhánh user. Sau việc này là
nhánh task → nhánh request → nhánh gốc, trong đó nhánh request đóng luôn vai nhánh tích hợp
(chốt C5 của request nghiên cứu). Tầng bị bỏ chính là tầng đẻ ra nhánh mồ côi.

**Không viết mã chuyển đổi schema.** Đo được ở `scripts/tdq_state.py:334-338`: chỗ nạp state đã
`setdefault` từng khoá mặc định rồi ép `schema_version` về số hiện tại. Thêm khoá là xong.
Cách khác — viết hàm `migrate_4_5()` — bị loại vì thêm mã cho việc mã sẵn có đã làm.

**Mở nhánh ở intake chứ không ở build.** Vì nhánh gốc phải chụp lúc request bắt đầu; đợi tới
phase `implement` thì user có thể đã đổi nhánh và số ghi vào state là số sai.

**Dừng và hỏi khi repo bẩn, không tự stash.** Chốt G-C. `git stash` rồi `pop` có thể đẻ conflict
mà user không hề yêu cầu, và thay đổi chưa commit là của user chứ không phải của workflow.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | plugin:tdq-workflow | NỀN | chứa mục `## 7. Git` được sửa |
| tdq-intake / spec / plan / build | plugin:tdq-workflow | NỀN | pipeline đang chạy, và là đối tượng bị sửa |
| using-git-worktrees | plugin | DÙNG | vòng đời worktree của `tdq_team.py` khi bỏ tầng nhánh tích hợp |
| pr-to-video | plugin | KHÔNG | khác lĩnh vực |
| tavily-primary | plugin | KHÔNG | spec §3 đã chọn cách khác tốt hơn — phần tra ngoài đã xong ở request nghiên cứu |
| Đã xét 205 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu thường trực

- Log service: BẬT. Mọi lệnh git mà workflow tự chạy phải in ra một dòng nói nó vừa làm gì,
  qua đúng cơ chế log sẵn có của `scripts/`.
- Không placeholder, không `TODO` để lại.
- Mỗi đầu ra có test riêng; test chạm git phải dựng repo trong thư mục tạm.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`, chỉ dòng việc này chạm tới):

- `CLI | scripts/ | ...` — mã mới nằm trong `scripts/`, không đẻ tầng mới.
- `Chỉ scripts/tdq_state.py được ghi docs/tdq/state.json; mọi nơi khác chỉ đọc qua CLI.`
  — ba khoá mới chỉ ghi qua `tdq_state.py`.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Sửa `tdq_team.py` làm hỏng luồng sub-agent | Mọi request dùng mode đội sau này hỏng | Module M3 làm sau cùng; test dựng repo tạm chạy trọn vòng `mo` → `hop` → `don` trước khi chốt |
| Test chạm nhầm repo thật, mọc nhánh hoặc worktree | Bẩn repo của user, và làm đỏ ca kiểm "không mọc nhánh" có sẵn | Mọi test git chạy trong `tempfile.TemporaryDirectory`; QC đối chiếu `git branch -a` và `git worktree list` với mốc chụp trước khi làm |
| Sửa skill mà quên dựng lại bundle | Host khác vẫn chạy luật cũ | M4 là module riêng, có hạng mục QC riêng cho cả ba bundle |
| Trả lời "chưa" ở bước 10 mà working tree còn bẩn | `git switch` kéo thay đổi chưa commit sang nhánh gốc | Bước 10 dùng chung khuôn với G-C: bẩn thì dừng, in file bẩn, hỏi user, không tự chuyển nhánh |
| Xoá nhánh mồ côi trên `origin` là thao tác ghi ra dịch vụ ngoài | Không lùi lại được bằng một lệnh | Hỏi user xác nhận ngay trước khi chạy lệnh xoá remote, kèm sha của nhánh để khôi phục được |
| Nâng `schema_version` lúc có request đang dở | Request dở mất trạng thái | Đã đo: chỗ nạp state `setdefault` nên không mất khoá nào; có test đọc file schema 4 dựng tay |

## 6. QC & Definition of Done

1. `default_state()` có đủ ba khoá mới và `schema_version` = 5.
2. File state schema 4 dựng tay đọc lên không mất khoá nào, ba khoá mới nhận mặc định.
3. Ba khoá mới ghi được qua CLI `tdq_state.py set` và đọc lại đúng.
4. Văn bản intake có dòng đề xuất loại request nằm trong chính câu hỏi chọn lane.
5. Văn bản intake có bước mở nhánh, nêu rõ chỉ chạy ở lane `full` và `quick`.
6. Văn bản intake nêu bước kiểm `git status` trước khi mở nhánh và cách xử lý khi bẩn.
7. Bước 10 của khuôn báo cáo mô tả đủ hai nhánh trả lời, mỗi nhánh có lệnh git cụ thể.
8. Mục `## 7. Git` có luật hình dạng tên nhánh, đủ 5 loại, và giữ nguyên 4 gạch đầu dòng cũ.
9. Mọi tên nhánh mẫu trong văn bản qua được `git check-ref-format --branch`.
10. Không tên nhánh mẫu nào mở đầu bằng `claude`, `antigravity`, `gemini`, `codex`.
11. `tdq_team.py` không còn tạo nhánh tích hợp riêng; nhánh task base từ nhánh request.
12. Chạy trọn vòng `mo` → `hop` → `don` trong repo tạm: nhánh task được merge, worktree được gỡ,
    không sót nhánh nào ngoài nhánh request.
13. Ba bundle CLEAN.
14. Repo thật không mọc nhánh hay worktree nào so với mốc chụp trước khi làm.
15. Nhánh mồ côi không còn ở local và không còn ở `origin`.
16. Bộ test của request xanh toàn bộ.
17. Suite toàn repo không vượt mốc đỏ có sẵn, tính cả ca `test_bench` sẽ chuyển xanh nhờ hạng mục 15.
18. `doc_lint.py` thoát 0 trên brief, spec, plan, qc, report.

## 7. Câu hỏi mở

Không còn.
