# SPEC — Đề xuất cơ chế chống quick-fix phá kiến trúc

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-14 · Bản: 1.0 · Brief: ../brief/2026-08-14-chong-no-ky-thuat.md · Lane: full
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: giao đúng một tài liệu đề xuất, trong đó mỗi cơ chế chống quick-fix có bản
  nháp copy được (chèn vào file nào, chỗ nào, nguyên văn dòng luật, cách kiểm), gom
  thành 3 gói theo mức chi phí, kèm khuyến nghị đúng một gói. Request sau chỉ việc dán.

- Trong phạm vi:
  - Bốn mặt user chọn: ràng buộc kiến trúc thành văn bản · dùng lại trước khi tạo mới ·
    bán kính ảnh hưởng · cổng QC chống hồi quy.
  - Cơ chế thiết kế cho **mọi project dùng plugin**, không riêng repo này.
  - Áp cho **cả hai pipeline**; bản express là bản rút gọn của cùng cơ chế.
  - Trần chi phí là **mức B**: luật văn bản bắt buộc, được phép kèm script kiểm khi cơ
    chế đó thật sự cần máy kiểm.

- NGOÀI phạm vi:
  - **Thực thi cơ chế vào workflow** — không sửa file `skills/`, `scripts/`, `hooks/`
    nào trong request này. User chọn 5B: dừng ở bản đề xuất, việc làm thật mở request
    riêng. Đây là mặt LOẠI duy nhất của vòng scope.
  - Cổng duyệt mới. Trần là mức B, mức C bị user loại ở vòng chi tiết câu 1.
  - Plan phác thảo cho request sau. User chọn 2A, không chọn 2C.
  - Chạy thử cơ chế trên một request cũ để đo hiệu quả. Không có trong phạm vi user chốt.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ | Đã chạy, 6 hướng, kết quả ở `../research/2026-08-14-chong-no-ky-thuat.md` |
| Interview | CÓ | Đã chạy 2 vòng: scope và chi tiết, hết câu hỏi đổi kết quả |
| QC độc lập bằng agent | BỎ | Đầu ra là một tài liệu, DoD kiểm hết bằng `grep` và `doc_lint` |
| Review sâu bằng `tdq-reviewer` | BỎ | Request `2026-08-08-giam-over-engineer-workflow` đã chốt: thêm lớp review cho việc nội bộ là lặp lại đúng lỗi đang sửa |
| Chia sub-agent implement | BỎ | Một tài liệu duy nhất, tách agent làm lệch giọng và lệch tên mục |
| Spec, plan, implement, report | CÓ | Khung bất biến |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | File đề xuất, 6 mục cố định | `docs/tdq/knowledge/2026-08-14-chong-no-ky-thuat.md` | Q1, Q9, Q10 |
| 2 | Bảng khoảng trống hiện tại, mỗi dòng kèm số đo và vị trí file | mục `## Khoảng trống` của đầu ra #1 | Q2 |
| 3 | Khối cơ chế, mỗi khối đủ 5 trường cố định | mục `## Cơ chế` của đầu ra #1 | Q3, Q4, Q5 |
| 4 | 3 gói theo mức chi phí, kèm đúng 1 dòng khuyến nghị | mục `## Gói` của đầu ra #1 | Q6, Q7 |
| 5 | Bản rút gọn cho pipeline express | mục `## Express` của đầu ra #1 | Q8 |
| 6 | Report ngắn | `docs/tdq/reports/2026-08-14-chong-no-ky-thuat.md` | Q11 |

Khuôn 5 trường của một khối cơ chế ở đầu ra #3 — đây là **khuôn mẫu áp cho file đề xuất
sẽ viết ở phase implement, không phải nội dung của turn này**:

```
### M<n> — <tên cơ chế>
- Chặn: <triệu chứng cụ thể trong 3 triệu chứng của brief>
- Chèn vào: <đường dẫn file>:<mục nào>
- Mức: <A|B>
- Nội dung nháp:
  <nguyên văn dòng luật, copy dán được>
- Cách kiểm: <một lệnh chạy được>
```

## 3. Cách tiếp cận & lý do

- Chọn: gắn mọi cơ chế vào **chỗ neo đã có sẵn** của workflow — khuôn spec, khuôn plan,
  bước implement của `tdq-build`, `doc_lint.py`, `edit_gate.py`, `graphify` — thay vì
  dựng bộ máy song song. Mỗi cơ chế nêu đúng một chỗ chèn.
- Vì: bốn khoảng trống đo được ở brief đều là **thiếu một dòng luật ở chỗ đã có**, không
  phải thiếu hạ tầng. `graphify affected` và `god-nodes` đã cài sẵn mà chưa chỗ nào gọi;
  `edit_gate.py` đã chặn được Edit theo điều kiện; `doc_lint.py` đã có 8 rule. Nguồn:
  research 6 hướng, mục "Ứng viên cơ chế" — 6 trên 8 ứng viên không cần script mới.
- Đã loại: **fitness function CI theo stack** (ArchUnit, dependency-cruiser) — vì workflow
  này áp cho mọi project ở mọi ngôn ngữ, không chọn được một tool. Vẫn nhắc trong đề xuất
  như tuỳ chọn của từng project, không đưa vào gói khuyến nghị.
- Đã loại: **cổng duyệt kiến trúc riêng** — user chốt trần mức B ở vòng chi tiết câu 1.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| graphify | user | DÙNG | `graphify god-nodes` lấy số hub thật của repo, làm ví dụ trong cơ chế bán kính ảnh hưởng |
| tavily-search | plugin:tavily | DÙNG | research phương án, đã chạy xong qua sub-agent ở phase analyze |
| sonar-duplication | plugin:sonarqube | DÙNG | ứng viên cổng kiểm trùng lặp, nêu trong khối cơ chế tương ứng |
| mem0-memory | user | DÙNG | ghi một fact về quyết định cơ chế sau khi user chốt gói |
| tdq-conventions | plugin:tdq-workflow | NỀN | file luật chung, là chỗ chèn của nhiều cơ chế |
| tdq-intake | plugin:tdq-workflow | NỀN | phase analyze, chỗ chèn của cơ chế bán kính ảnh hưởng |
| tdq-spec | plugin:tdq-workflow | NỀN | khuôn spec, chỗ chèn của cơ chế ràng buộc kiến trúc |
| tdq-plan | plugin:tdq-workflow | NỀN | khuôn plan, chỗ chèn của cơ chế khai vùng chạm |
| tdq-build | plugin:tdq-workflow | NỀN | bước implement và QC, chỗ chèn của cơ chế dùng lại và cổng hồi quy |
| Đã xét 274 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service: BỎ — request này không tạo hay sửa file mã nguồn chạy được, đầu ra là tài
  liệu Markdown.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật. Mọi số đo
  trong đề xuất phải lấy từ lệnh chạy thật, mọi khẳng định phải có nguồn.
- Mỗi thành phần có cách kiểm riêng, chạy được bằng một lệnh — xem §6.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Đề xuất phình thành bộ máy nặng, lặp lại đúng lỗi mà `2026-08-08-giam-over-engineer-workflow` vừa cắt | Workflow chậm lại, user bỏ dùng | Trần mức B ghi thành hạng mục QC Q5; gói tối thiểu bắt buộc phải là gói thuần luật văn bản |
| Bản nháp trỏ vào file hay mục không tồn tại | Request sau dán vào chỗ sai | Q4 kiểm mọi đường dẫn nêu trong đề xuất có thật trên đĩa |
| Cơ chế chỉ hợp repo Python này, không hợp project Unity hay game | Vô dụng ở đúng chỗ user cần nhất | Mỗi khối cơ chế nêu rõ phần nào không phụ thuộc ngôn ngữ; loại sẵn fitness function theo stack ở §3 |
| Luật mới mâu thuẫn luật đang có (vd "QC = số dòng DoD") | Agent gặp hai luật trái nhau, làm bừa | Khối cơ chế nào sửa luật cũ phải ghi rõ dòng luật cũ bị thay, kiểm ở Q3 |

## 6. QC & Definition of Done

Đặt `F=docs/tdq/knowledge/2026-08-14-chong-no-ky-thuat.md`.

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | File đề xuất đủ 6 mục cố định | `grep -c "^## " $F` | `= 6` |
| Q2 | Bảng khoảng trống có đủ 4 dòng, mỗi dòng có số đo | `grep -c "^| K[1-4] " $F` | `= 4` |
| Q3 | Mỗi khối cơ chế đủ 5 trường | `grep -c "^### M" $F` bằng `grep -c "^- Chèn vào:" $F` bằng `grep -c "^- Nội dung nháp:" $F` bằng `grep -c "^- Cách kiểm:" $F` bằng `grep -c "^- Chặn:" $F` | 5 số bằng nhau và `>= 6` |
| Q4 | Mọi đường dẫn file nêu trong trường `Chèn vào` đều có thật | trích đường dẫn rồi `test -f` từng cái | mọi đường dẫn tồn tại, 0 lỗi |
| Q5 | Không cơ chế nào vượt trần B | `grep -c "^- Mức: C" $F` | `= 0` |
| Q6 | Có đúng 3 gói | `grep -c "^### Gói" $F` | `= 3` |
| Q7 | Có đúng một dòng khuyến nghị | `grep -c "^Khuyến nghị: " $F` | `= 1` |
| Q8 | Có bản rút gọn cho express | `grep -c "^## Express" $F` | `= 1` |
| Q9 | Phủ đủ 4 mặt user chọn | `grep -ci "ràng buộc kiến trúc" $F`, `grep -ci "dùng lại" $F`, `grep -ci "bán kính ảnh hưởng" $F`, `grep -ci "hồi quy" $F` | cả 4 đều `>= 1` |
| Q10 | `doc_lint` sạch | `python3 scripts/doc_lint.py $F docs/tdq/spec/2026-08-14-chong-no-ky-thuat.md docs/tdq/plan/2026-08-14-chong-no-ky-thuat.md` | `exit 0` |
| Q11 | Không đụng mã nguồn, workflow còn nguyên | `git status --porcelain -- skills scripts hooks` rỗng; `python3 -m pytest tests/ -q` | 0 file thay đổi và không có `failed`, số test `>= 563` |

DoD: 11 hạng mục Q1–Q11 trên đều PASS, file đề xuất và report đã ghi, working log đã
append, và không có file nào trong `skills/`, `scripts/`, `hooks/` bị sửa.

## 7. Câu hỏi còn mở

(Rỗng.)
