# PLAN — Thi hành vòng đời nhánh git theo request

Ngày: 2026-09-05 · Spec: ../spec/2026-09-05-0833-gitflow-nhanh-theo-request.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — đo bằng `tdq_bench.py mo-phong` trên chính plan này (hệ số agent 1.5): 12 task, 4 đợt, giao ra 6 / leader giữ 6, main 24.4 phút / đội 12.3 phút, `Winner: đội` cách 12.2 phút. Khoảng cách rộng vì ba bộ test tách theo module nên P1–P3 không còn file nóng. (ĐỀ XUẤT, user chốt lúc duyệt)
Trạng thái plan: HOÀN THÀNH · Mode thực thi đã chốt: main (user nhắn "1b") · QC 22/22 PASS

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — State nhớ nhánh
- P2 — Luật & khuôn văn bản
- P3 — Đội sub-agent bớt một tầng
- P4 — Bundle & dọn nhánh mồ côi
- P5 — Log & test bắt buộc
- Cụm song song
- Definition of Done
- Ước tính

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy test của module, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. **Mọi test chạm git chạy trong `tempfile.TemporaryDirectory`.** Cấm test nào mọc nhánh
   hay worktree trong repo thật — spec §5.
8. **Cấm sửa tay file trong ba bundle**; bundle chỉ sinh ra từ `build_portable.py`.

## P1 — State nhớ nhánh

- [x] **T1.1** (e10m) Viết bộ test state: `default_state()` có `loai_request`/`nhanh_goc`/`nhanh_request`; `schema_version` = 5; dựng tay một file state schema 4 trong thư mục tạm rồi nạp, khẳng định không mất khoá nào và ba khoá mới nhận mặc định; ghi ba khoá qua CLI `set` rồi đọc lại — Test: `python3 -m pytest tests/test_gitflow_state.py -q` ĐỎ đúng 4 ca
  - Chạm: `tests/test_gitflow_state.py` → file mới, chưa node nào phụ thuộc

- [x] **T1.2** (e12m) Thêm ba khoá vào `default_state()` và nâng `schema_version` 4 → 5; KHÔNG viết hàm chuyển đổi (spec §3: chỗ nạp state đã `setdefault` từng khoá) — Test: 4 ca của T1.1 chuyển XANH
  - Chạm: `scripts/tdq_state.py` → mọi script trong `scripts/` và mọi hook đọc state qua module này
  - Cần: T1.1

**Xong P1 khi**: 4 ca state xanh và `python3 scripts/tdq_state.py show` in ra ba khoá mới.

## P2 — Luật & khuôn văn bản

- [x] **T2.1** (e14m) Viết bộ test văn bản luật: intake có dòng đề xuất loại nằm trong chính câu hỏi chọn lane; intake có bước mở nhánh nêu rõ chỉ lane `full`/`quick`; intake nêu bước kiểm `git status` và cách xử lý khi bẩn; bước 10 của khuôn báo cáo mô tả đủ hai nhánh trả lời, mỗi nhánh có lệnh git; `## 7. Git` có luật hình dạng tên nhánh đủ 5 loại và giữ nguyên 4 gạch đầu dòng cũ; mọi tên nhánh mẫu qua được `git check-ref-format --branch`; không tên nhánh mẫu nào mở đầu bằng tiền tố bị cấm — Test: `python3 -m pytest tests/test_gitflow_van_ban.py -q` ĐỎ đúng 7 ca
  - Chạm: `tests/test_gitflow_van_ban.py` → file mới, chưa node nào phụ thuộc

- [x] **T2.2** (e16m) Sửa `tdq-intake`: thêm dòng đề xuất loại request vào câu hỏi chọn lane ở Part A bước 2; thêm bước mở nhánh ngay sau `init` ở bước 3, gồm kiểm `git status`, ghi `nhanh_goc`/`nhanh_request`/`loai_request` qua CLI, và luật dừng-hỏi khi repo bẩn — Test: 3 ca intake của T2.1 chuyển XANH
  - Chạm: `skills/tdq-intake/SKILL.md` → mọi request đi qua file này; ba bundle chép lại nó
  - Cần: T1.2, T2.1

- [x] **T2.3** (e12m) Sửa bước 10 của khuôn báo cáo: trả lời "commit" thì commit rồi `git merge --no-ff` về `nhanh_goc` và `git branch -d`; trả lời "chưa" thì vẫn merge phần đã commit về nhánh gốc, còn working tree bẩn thì in file bẩn và hỏi user trước khi chuyển nhánh — Test: ca bước 10 của T2.1 chuyển XANH
  - Chạm: `skills/tdq-build/references/report-template.md` → `tdq-build` Part C đọc file này; ba bundle chép lại nó
  - Cần: T2.1

- [x] **T2.4** (e10m) Thêm luật hình dạng tên nhánh vào `## 7. Git`: `<loại>/<mô tả>`, 5 loại `feature`/`bugfix`/`hotfix`/`chore`/`docs`, dấu `/` chứ không phải `\`, kèm lý do (`git check-ref-format` từ chối dạng kia); giữ nguyên 4 gạch đầu dòng sẵn có — Test: 3 ca luật tên nhánh của T2.1 chuyển XANH
  - Chạm: `skills/tdq-conventions/SKILL.md` → mọi skill `tdq-*` nạp file này đầu tiên; ba bundle chép lại nó
  - Cần: T2.1

**Xong P2 khi**: 7 ca văn bản xanh và `doc_lint.py` không kêu trên ba file vừa sửa.

## P3 — Đội sub-agent bớt một tầng

- [x] **T3.1** (e18m) Viết bộ test đội trong repo tạm: chạy trọn vòng `mo` → `hop` → `don` cho một task, khẳng định nhánh task base từ nhánh request chứ không từ nhánh tích hợp, nhánh task được merge, worktree được gỡ, và sau `don` không sót nhánh nào ngoài nhánh request; thêm ca khẳng định không có nhánh nào mang đuôi `tich-hop` được tạo — Test: `python3 -m pytest tests/test_gitflow_doi.py -q` ĐỎ đúng 3 ca
  - Chạm: `tests/test_gitflow_doi.py` → file mới, chưa node nào phụ thuộc

- [x] **T3.2** (e20m) Sửa `tdq_team.py`: `lenh_mo` không gọi `_bao_dam_tich_hop` nữa mà base nhánh task từ `nhanh_request` đọc trong state; `lenh_hop` merge nhánh task về nhánh request; gỡ `_nhanh_tich_hop`/`_bao_dam_tich_hop` nếu không còn ai gọi, giữ nguyên `assert not ten.startswith(TEN_CAM)` — Test: 3 ca của T3.1 chuyển XANH và bộ test đội sẵn có không đỏ thêm ca nào
  - Chạm: `scripts/tdq_team.py` → `tdq-build` mode `subagent` và agent `tdq-implementer` gọi script này
  - Cần: T1.2, T3.1

  - Dùng: `using-git-worktrees`
  - Để: giữ đúng vòng đời worktree khi bỏ tầng nhánh tích hợp — thứ tự `add` → merge → `remove` → `prune` và cách gỡ worktree còn dính nhánh. Agent ngoài không có skill system: đọc `SKILL.md` của skill này trong thư mục plugin rồi làm theo.
  - Ra: phần sửa `lenh_mo`/`lenh_hop`/`_thu_don` của `scripts/tdq_team.py`
  - Kiểm: `python3 -m pytest tests/test_gitflow_doi.py -q` xanh cả 3 ca
  - Không dùng cho: dựng worktree trong repo thật lúc chạy test; đổi khuôn tên nhánh task

**Xong P3 khi**: 3 ca đội xanh và không nhánh nào mang đuôi `tich-hop` sinh ra trong repo tạm.

## P4 — Bundle & dọn nhánh mồ côi

- [x] **T4.1** (e10m) Dựng lại ba bundle rồi kiểm — Test: `python3 scripts/build_portable.py` chạy sạch, `python3 scripts/tdq_checkportable.py check --root <mỗi bundle>` in CLEAN cho cả ba
  - Chạm: `portable_claude/`, `portable_codex/`, `antigravity_portable/` → sinh ra từ `build_portable.py`, không sửa tay
  - Cần: T2.2, T2.3, T2.4

- [x] **T4.2** (e6m) Thêm ca test khẳng định luật tên nhánh mới CÓ MẶT trong bundle đã dựng (ít nhất bản `portable_claude`), để lần sau ai quên dựng lại thì test bắt được — Test: ca mới xanh sau khi T4.1 xong
  - Chạm: `tests/test_gitflow_van_ban.py` → file nóng, đã tạo ở T2.1
  - Cần: T4.1

- [x] **T4.3** (e8m) Dọn nhánh mồ côi `tdq/2026-08-23-1623-mindmap-html-hai-lop/tich-hop`: in sha của nó ra trước, xoá local bằng `git branch -D`, rồi HỎI user xác nhận trước khi xoá trên `origin` (thao tác ghi ra dịch vụ ngoài, spec §5) — Test: `git branch -a | grep tich-hop` không còn dòng nào
  - Trạng thái: local ĐÃ xoá (`f051548`, đã gộp vào `main` nên dùng `git branch -d`).
    Origin: user duyệt "1a" → `git push origin --delete` đã chạy; `git branch -a | grep tich-hop` còn 0 dòng.

**Xong P4 khi**: ba bundle CLEAN, ca bundle xanh, nhánh mồ côi biến mất ở local và `origin`.

## P5 — Log & test bắt buộc

- [x] **T5.1** (e8m) Chạy toàn bộ suite đúng MỘT lần, đối chiếu mốc đỏ có sẵn, đối chiếu `git branch -a` và `git worktree list` với mốc chụp trước khi làm, rồi đóng sổ lượt bằng `tdq_finish.py` — Test: `python3 -m pytest -q` không vượt mốc đỏ có sẵn; `tdq_finish.py` in `lint=ok · worklog=ok`

**Xong P5 khi**: suite không xấu đi, repo thật không mọc nhánh/worktree nào, và sổ công việc đã ghi.

## Cụm song song

Ba bộ test tách theo module nên không có file nóng ở P1–P3: `tests/test_gitflow_state.py`,
`tests/test_gitflow_van_ban.py`, `tests/test_gitflow_doi.py` mỗi file một chủ. Cụm chạy song
song được là T1.1 + T2.1 + T3.1 (ba file test mới, không giao nhau). Sau đó T2.2/T2.3/T2.4
cũng chạy song song được vì mỗi task một file skill khác nhau. Phần thắt cổ chai là T1.2 —
T2.2 và T3.2 đều `Cần:` nó, nên nó phải xong trước. `tests/test_gitflow_van_ban.py` bị T2.1
và T4.2 cùng ghi, nhưng T4.2 nằm ở phase sau nên xử lý theo cách "nâng lên đợt sớm": file đã
ổn định từ P2 rồi T4.2 mới thêm ca.

## Definition of Done

Chiếu thẳng §6 của spec, 18 dòng, mỗi dòng một lệnh kiểm:

1. `default_state()` có đủ ba khoá mới và `schema_version` = 5 — `pytest -k ba_khoa_moi`.
2. File state schema 4 dựng tay nạp lên không mất khoá nào — `pytest -k doc_schema_4`.
3. Ba khoá mới ghi/đọc được qua CLI — `pytest -k ghi_doc_qua_cli`.
4. Intake có dòng đề xuất loại trong chính câu hỏi chọn lane — `pytest -k de_xuat_loai`.
5. Intake có bước mở nhánh, chỉ lane `full`/`quick` — `pytest -k mo_nhanh_dung_lane`.
6. Intake nêu bước kiểm `git status` và cách xử lý khi bẩn — `pytest -k repo_ban`.
7. Bước 10 mô tả đủ hai nhánh trả lời, mỗi nhánh có lệnh git — `pytest -k buoc_muoi`.
8. `## 7. Git` có luật tên nhánh đủ 5 loại, giữ nguyên 4 gạch đầu dòng cũ — `pytest -k luat_ten_nhanh`.
9. Mọi tên nhánh mẫu qua `git check-ref-format --branch` — `pytest -k ten_nhanh_hop_le`.
10. Không tên nhánh mẫu nào mở đầu bằng tiền tố bị cấm — `pytest -k khong_tien_to_cam`.
11. `tdq_team.py` không còn tạo nhánh tích hợp riêng — `pytest -k khong_nhanh_tich_hop`.
12. Vòng `mo` → `hop` → `don` trong repo tạm sạch hết nhánh và worktree — `pytest -k vong_doi_day_du`.
13. Ba bundle CLEAN — `tdq_checkportable.py check --root <mỗi bundle>`.
14. Repo thật không mọc nhánh hay worktree nào — `diff` `git branch -a` và `git worktree list` với mốc chụp trước khi làm.
15. Nhánh mồ côi không còn ở local và ở `origin` — `git branch -a | grep tich-hop` rỗng.
16. Bộ test của request xanh toàn bộ — `python3 -m pytest tests/test_gitflow_state.py tests/test_gitflow_van_ban.py tests/test_gitflow_doi.py -q`.
17. Suite toàn repo không vượt mốc đỏ có sẵn — chạy một lần ở T5.1.
18. `doc_lint.py` exit 0 trên brief, spec, plan, qc, report — `python3 scripts/doc_lint.py <5 file>`.

## QC vòng 1 — fix

- [x] **QC1.1** Dựng lại cột số dòng của `docs/tdq/audit/luat-hien-co.md`: các sửa đổi ở
  `tdq-conventions/SKILL.md` và `tdq-build/SKILL.md` đẩy độ lệch từ 111/329 lên 122/329, vượt
  ngưỡng 5% của lưới khoá luật — Test: `python3 -m pytest -q tests/test_luat_skill.py` xanh cả 11 ca
  - Chạm: `docs/tdq/audit/luat-hien-co.md` → chỉ `tests/test_luat_skill.py` đọc file này

## Ước tính

12 task, tổng `(e144m)`.
