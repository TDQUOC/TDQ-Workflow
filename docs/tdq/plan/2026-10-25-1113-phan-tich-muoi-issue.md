# PLAN — Phân tích và đề xuất 10 issue nền

Ngày: 2026-10-25 · Spec: ../spec/2026-10-25-1113-phan-tich-muoi-issue.md (bản 1.0, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: main — ĐỀ XUẤT theo simulate: main 10.2 so với team 15.3 phút model time, công cụ báo chênh 5.2 phút, hệ số agent 1.5; 5 tasks phụ thuộc tuần tự và dùng chung report/QC. Đây là mô hình calibration cũ, không phải đo runtime request này; user chọn sau duyệt plan.
Trạng thái plan: HOÀN THÀNH ĐẦU RA TÀI LIỆU — 5 tasks và6 DoD đã kiểm; QC toàn repo FAIL, lifecycle paused vì6worktrees Archify cũ. Không sửa code, không coi request Archify đã nghiệm thu. Mode main do user chọn `1a`.

## Quy tắc thi hành

1. Chỉ viết báo cáo/QC/bằng chứng dưới docs/tdq; không fix scripts/hooks/tests/skills. Những file được đề xuất sửa trong báo cáo là phạm vi tương lai, không phải quyền sửa của plan này.
2. Giữ nguyên mọi dirty source kế thừa Archify và 6 worktree. Không commit/push/merge, reset/clean hoặc khôi phục state Archify khi chưa được yêu cầu. Snapshot resume cũ chỉ đọc.
3. Mỗi task [ ] → [~] → kiểm đầu ra → [x]. Không có code mới nên không tạo unit test giả để đạt RED. Test sản phẩm hiện đỏ dùng làm chứng cứ chẩn đoán; đầu ra tài liệu thiếu nội dung được bổ sung rồi kiểm lại, không gọi import/file-not-found là behavioral RED.
4. Mỗi luận điểm phân biệt ĐÃ XÁC MINH / GIẢ THUYẾT / ĐỀ XUẤT. Lệnh chưa chạy ghi rõ kỳ vọng, không in PASS như số đo thật. Không tăng cap/bỏ assertion để che lỗi.
5. Không chạy đồng thời suite có ghi ledger/state. Chỉ một lượt full suite tại cổng QC vì không có vòng sửa production. Nếu hạ tầng runner lỗi, ghi lỗi và chẩn đoán, không chạy lại mù quáng.
6. State chỉ ghi qua tdq_state.py. Lệnh tái hiện hook dùng project fixture tạm; không reset request thật. Sau mỗi mốc dùng tdq_finish.py để ghi nhật ký, không viết tay workinglog.
7. Python/node/browser dùng dependency đã có. Full suite có E2E native kế thừa: chạy trong subprocess non-elevated như bằng chứng Archify trước, giữ sandbox; không thay gate/skips và không phát sinh browser audit mới.

## Trước vs Sau

| Vùng | Trước | Sau request tài liệu |
|---|---|---|
| 10 issue | Log lỗi + phân tích sơ bộ trong brief | Hồ sơ truy nguyên, phương án chọn/loại và test bảo vệ |
| Quyết định sửa | Chưa rõ lỗi test hay production | Có thứ tự triển khai và điểm cần duyệt riêng |
| Source/runtime | Dirty Archify kế thừa | Không thay đổi bởi request này |
| Archify | Paused, chưa nghiệm thu | Giữ nguyên snapshot và hướng dẫn continue |

Không tạo lại preview HTML: spec đã xác định báo cáo Markdown và sơ đồ quy trình là đủ. Không thay đổi thiết kế đã duyệt.

## P1 — Khóa bằng chứng và hoàn thiện chẩn đoán

- [x] **T1.1** (e5m) Lưu mốc nguồn và inventory I01–I10, tách số đo kế thừa khỏi phép kiểm mới — Test: đọc lại JSON snapshot, đối chiếu đủ source paths và HEAD; mọi issue có test ID và nguồn log
  - Chạm: `docs/tdq/qc/2026-10-25-1113-phan-tich-muoi-issue.md`, `docs/tdq/2026-10-25-1113-phan-tich-muoi-issue.source-before.json`
  - O3/Q4/Q5. Snapshot SHA-256 bằng hashlib cho file tracked/untracked trong scripts/hooks/tests/skills và .env.example, không chỉ git diff; không lưu secret/env thực. Snapshot chứa paths+hash, HEAD và thời điểm. Tệp sinh bởi test phải được giải thích riêng, không lẫn source edits. Đối chiếu trạng thái resume Archify và liên kết trước khi thực hiện.

- [x] **T1.2** (e14m) Viết hồ sơ nguyên nhân cho đủ 10 issue từ phân tích đã có, xác minh chỗ còn nghi ngờ — Test: mỗi I01–I10 có đủ 8 trường theo C1 và đối chiếu dẫn nguồn thủ công
  - Chạm: `docs/tdq/reports/2026-10-25-1113-phan-tich-muoi-issue.md`, `docs/tdq/qc/2026-10-25-1113-phan-tich-muoi-issue.md`
  - Cần: T1.1
  - O1/Q1/Q2. Không lặp đối chứng hai baseline đã có. Đọc nguồn hiện tại cho line anchors, ghi uncertainty ở scanner/quote/encoding. I07 kiểm tất cả file trong danh sách wiring, không dừng tại assertion đầu. I06 phân biệt bootstrap thiếu và crash Unicode thực; không suy mọi Windows dùng cp1252. LSP pre-flight trước tra references; graph stale ghi giới hạn và đối chiếu text, không semantic extraction mới.

## P2 — Phương án và lộ trình đề xuất

- [x] **T2.1** (e12m) Hoàn thiện phương án chọn/loại, test bảo vệ, thứ tự phụ thuộc và đường continue Archify — Test: C1, C2, C3 và kiểm nội dung theo Q3/Q5
  - Chạm: `docs/tdq/reports/2026-10-25-1113-phan-tich-muoi-issue.md`
  - Cần: T1.2
  - Dùng: `dataviz`
  - Để: Trình bày thứ tự xử lý bằng sơ đồ Mermaid có nhãn và bảng tương đương
  - Ra: `docs/tdq/reports/2026-10-25-1113-phan-tich-muoi-issue.md`
  - Kiểm: `python scripts/doc_lint.py docs/tdq/reports/2026-10-25-1113-phan-tich-muoi-issue.md`
  - Không dùng cho: Tạo dashboard/HTML, sửa renderer hoặc triển khai fix
  - O1/O2/O4. I05 phải có câu description ứng viên thật và số ký tự đo trên chuỗi, giữ tổng1800; không sửa SKILL.md. I04 đề xuất registry/cap mới có lý do, không tự phê duyệt con số. I09 ưu tiên giữ selector bảo thủ, so sánh fixture ổn định với lọc AST và nguy cơ bỏ sót dynamic references. I10 phân biệt parsing Windows/POSIX, không dùng strip quote tùy tiện như giải pháp mọi shell. Mọi phương án có ca hợp lệ/bất hợp lệ, hồi quy caller và rollback tương lai.

## P3 — Kiểm chứng và bàn giao

Log: BỎ — không có runtime mới; dùng logger, log test và workinglog sẵn có.

- [x] **T3.1** (e12m) Chạy kiểm mục tiêu và full suite tại cổng, ghi QC trung thực — Test: C4 và các checks C1–C6, không còn tiến trình kiểm đang chạy
  - Chạm: `docs/tdq/qc/2026-10-25-1113-phan-tich-muoi-issue.md`, `docs/tdq/2026-10-25-1113-phan-tich-muoi-issue-tests.log`
  - Cần: T2.1
  - O3/Q4/Q6. Test vùng liên quan dùng `python -m pytest tests/test_luat_gate_chat.py tests/test_reference_mot_tang.py tests/test_skill_shape.py tests/test_token_budget.py tests/test_utf8_io.py tests/test_vision_test_loop_doc.py tests/test_reminder_contract.py tests/test_tdq_test.py tests/test_tuong_thich_host.py -q --tb=short`; exit1 baseline là evidence, không PASS sản phẩm. Full runner: `python scripts/tdq_test.py tron-bo`, lưu stdout và stderr đầy đủ dưới tên bằng chứng request mới; sau đó `python scripts/tdq_test.py so`. Không ghi đè log Archify. Unittest không thu hàm pytest artifacts: dùng bằng chứng riêng đã có hoặc chạy nhóm đó nếu snapshot thay đổi, ghi rõ coverage. Không chạy `vung-cham` trên toàn docs nếu nó rơi về full suite trùng; mapping test nguồn ở trên là QC-F2 cho request chỉ phân tích.
  - QC-F3: không source delta, không ghi state trực tiếp, không đổi snapshot/approval Archify. QC-F4: KHÔNG ÁP DỤNG với source mới; kiểm rõ ràng, trùng lặp và dẫn nguồn của tài liệu. Lỗi baseline không mở vòng fix source trong request này; báo cáo tách kết luận đạt nội dung và repo còn đỏ.

- [x] **T3.2** (e4m) Chốt báo cáo, giới hạn và hướng dẫn bước kế tiếp; lưu số đo thời gian thật — Test: C5, C6, `python scripts/tdq_timing.py show` và self-check không gọi đề xuất là đã fix
  - Chạm: `docs/tdq/reports/2026-10-25-1113-phan-tich-muoi-issue.md`, `docs/tdq/qc/2026-10-25-1113-phan-tich-muoi-issue.md`
  - Cần: T3.1
  - O1–O4. Đối chiếu source-before; user có thể continue Archify sau khi yêu cầu, không tự restore state. Không báo 10 lỗi đã sửa hoặc toàn repo PASS. Không tự commit các nguồn kế thừa; bàn giao ghi rõ nội dung mới chỉ là tài liệu và evidence. Nếu gate bị chặn do worktree cũ thì báo đúng chặn, không cleanup phá hủy hay sửa hook.

## Các lệnh kiểm tài liệu (C1–C6)

Lệnh dưới đây chạy từ root repo. Chúng chỉ đọc; không thêm validator production chỉ phục vụ request này. Mechanical checks không thay kiểm nội dung ở T1.2/T2.1.

### C1 — Inventory và các trường bắt buộc

Báo cáo dùng heading `## I01` ... `## I10`, mỗi mục có các nhãn `Triệu chứng:`, `Nguyên nhân:`, `Bằng chứng:`, `Phân loại:`, `Phương án chọn:`, `Phương án loại:`, `Vùng ảnh hưởng:`, `Test bảo vệ:`.

```sh
python -c "from pathlib import Path; import re; s=Path('docs/tdq/reports/2026-10-25-1113-phan-tich-muoi-issue.md').read_text(encoding='utf-8'); blocks=dict(re.findall(r'^## (I\d{2})[^\n]*\n(.*?)(?=^## |\Z)',s,re.M|re.S)); assert set(blocks)=={f'I{i:02d}' for i in range(1,11)}; fields=['Triệu chứng:','Nguyên nhân:','Bằng chứng:','Phân loại:','Phương án chọn:','Phương án loại:','Vùng ảnh hưởng:','Test bảo vệ:']; assert all(all(f in b for f in fields) for b in blocks.values()); print('10 issue records complete')"
```

### C2 — Dẫn nguồn có thật

Trong báo cáo, source citations theo `scripts/file.py:123`, `hooks/scripts/file.py:123`, `skills/.../file.md:123` hoặc `tests/file.py:123`.

```sh
python -c "from pathlib import Path; import re; s=Path('docs/tdq/reports/2026-10-25-1113-phan-tich-muoi-issue.md').read_text(encoding='utf-8'); refs=re.findall(r'((?:scripts|hooks|skills|tests)/[A-Za-z0-9_./-]+):(\d+)',s); assert refs; assert all(Path(p).is_file() and 1<=int(n)<=len(Path(p).read_text(encoding='utf-8-sig').splitlines()) for p,n in refs); print('Source citations resolve')"
```

### C3 — Phương án và thứ tự

```sh
python -c "from pathlib import Path; s=Path('docs/tdq/reports/2026-10-25-1113-phan-tich-muoi-issue.md').read_text(encoding='utf-8'); assert all(x in s for x in ['## Lộ trình xử lý đề xuất','## Giới hạn và quyết định','chưa fix']); print('Proposal sections present; semantic review still required')"
```

### C4 — Kết quả suite có bằng chứng

`python scripts/tdq_test.py tron-bo` — chỉ chạy trong T3.1, không gọi lại ở từng tick DoD. Mã thoát đỏ phải được lưu và phân loại, không đổi thành PASS. Kèm `python scripts/tdq_test.py so` để ghi số lượt/misses thực tế. QC ghi rõ kết luận kiểm chứng báo cáo riêng với kết luận toàn repo.

### C5 — Bảo toàn nguồn và resume

```sh
python -c "from pathlib import Path; import hashlib,json; b=json.loads(Path('docs/tdq/2026-10-25-1113-phan-tich-muoi-issue.source-before.json').read_text(encoding='utf-8')); paths={p.as_posix() for d in ('scripts','hooks','tests','skills') for p in Path(d).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pyc','.pyo')}; paths.add('.env.example'); now={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in sorted(paths)}; assert now==b['files'],'Source delta detected'; a=json.loads(Path('docs/tdq/2026-10-24-2348-hoan-thien-archify.resume.json').read_text(encoding='utf-8')); assert a['active_request']=='2026-10-24-2348-hoan-thien-archify' and a['spec_approved'] and a['plan_approved']; assert Path('docs/tdq/reports/2026-10-24-2348-hoan-thien-archify-resume.md').is_file(); print('Source preserved; resume snapshot present')"
```

T1.1 phải tạo `files` với đúng phép chọn paths trên để không nhầm file cache do test sinh. Không chỉnh snapshot để che source delta; nếu có thay đổi từ bên ngoài thì báo và đối soát.

### C6 — Lint tài liệu

`python scripts/doc_lint.py docs/tdq/reports/2026-10-25-1113-phan-tich-muoi-issue.md docs/tdq/qc/2026-10-25-1113-phan-tich-muoi-issue.md`

## Cụm song song và luật file nóng

Một chuỗi T1.1 → T1.2 → T2.1 → T3.1 → T3.2. Hai file report/QC dùng chung, một chủ ghi; không fan-out writer và không tạo thêm worktree để viết cùng báo cáo. Kết quả agent khảo sát ở analyze chỉ là đầu vào, không được coi như task đã hoàn thành. Không có MCP task thực thi bắt buộc; LSP chỉ dùng khi cần xác minh source chưa rõ và phải pre-flight.

## Definition of Done

- [x] Q1 Đủ 10 hồ sơ issue và trường bắt buộc — C1 (lệnh Python ở trên).
- [x] Q2 Dẫn nguồn thật, fact/giả thuyết/đề xuất tách rõ — C2 và self-review từng citation đã ghi trong QC.
- [x] Q3 Phương án không làm yếu contract, có thứ tự và test âm/dương — C3 và bảng review nội dung tại QC.
- [x] Q4 QC full có kết quả thật, baseline tách rõ và không còn tác vụ nền — C4, `python scripts/tdq_test.py so`; đỏ baseline không là xanh toàn repo.
- [x] Q5 Không fix source và có đường continue Archify — C5.
- [x] Q6 Báo cáo/QC dùng được, lint sạch — C6.

Tổng 5 tasks / 3 phases / 47 phút ước tính thực thi; không gồm chờ duyệt. Simulation là mô hình dự báo từ calibration cũ, không là số đo runtime thực tế. Không tự chọn mode thay user.
