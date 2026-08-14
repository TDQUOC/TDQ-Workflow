# ĐỀ XUẤT — Cơ chế chống quick-fix phá kiến trúc & sinh nợ kỹ thuật

Ngày: 2026-08-14 · Spec: ../spec/2026-08-14-chong-no-ky-thuat.md · Plan:
../plan/2026-08-14-chong-no-ky-thuat.md · Research: ../research/2026-08-14-chong-no-ky-thuat.md

Ba triệu chứng cần chặn, lấy từ brief:

1. Agent sửa cục bộ cho xanh test, bỏ qua khuôn kiến trúc đang có của project.
2. Agent thêm lớp/hàm/file mới song song với thứ đã tồn tại thay vì dùng lại.
3. Agent chạm vùng ngoài phạm vi và làm hỏng thứ đang chạy mà không ai thấy.

Sáu cơ chế dưới đây đều gắn vào một chỗ neo đã có sẵn của workflow. Không cơ chế nào
thêm cổng duyệt mới.

## Khoảng trống

Số đo lấy bằng lệnh thật trên repo `TDQWorkflow` ngày 2026-08-14.

| # | Khoảng trống | Số đo | Bằng chứng | Triệu chứng lọt |
|---|---|---|---|---|
| K1 | Không có ràng buộc kiến trúc thành văn bản | 1 lần nhắc chữ "kiến trúc" trên 1.844 dòng skill | `grep -rn "kiến trúc" skills/ \| wc -l` → 1, ở `skills/tdq-intake/references/lane-decision.md:27` (bảng chọn lane) | 1 |
| K2 | Không có luật dùng lại trước khi tạo mới | 1 dòng luật code duy nhất, 0 chữ "tái sử dụng" | `skills/tdq-build/SKILL.md:51` — "Code: thay đổi nhỏ nhất mà đủ thoả task. Bám style code sẵn có." | 2 |
| K3 | Không có bước bán kính ảnh hưởng | `god-nodes` xuất hiện 0 lần, `affected` 2 lần và cả 2 chỉ là gợi ý đọc | `grep -rn "god-nodes" skills/ \| wc -l` → 0; `affected` ở `analyze-full.md:18` và `quick-lane.md:26`, đều trong câu "Lệnh: `graphify query\|path\|explain\|affected`" | 3 |
| K4 | QC không bắt được thiệt hại ngoài DoD | luật đóng, 0 hạng mục cố định về hồi quy kiến trúc | `skills/tdq-build/references/qc.md:7` — "Số hạng mục QC = số dòng Definition of Done của plan… Không thêm hạng mục ngoài DoD" | 1, 3 |

Bốn khoảng trống đều là **thiếu một dòng luật ở chỗ đã có**, không phải thiếu hạ tầng:
`graphify affected` và `graphify god-nodes` đã cài sẵn, `edit_gate.py` đã chặn được thao
tác Edit theo điều kiện, `doc_lint.py` đã có 8 rule.

## Cơ chế

Mỗi khối theo đúng khuôn 5 trường. Trường `Nội dung nháp` là văn bản copy dán được;
trường `Cách kiểm` là một lệnh chạy được, exit code có nghĩa.

### M1 — Hồ sơ kiến trúc của project

- Chặn: triệu chứng 1 — agent không có gì để đối chiếu nên sửa theo cảm tính cục bộ.
- Chèn vào: skills/tdq-intake/references/analyze-full.md:bước 2 "Đọc code"
- Mức: A
- Nội dung nháp:

  **Hồ sơ kiến trúc — đọc trước khi phân tích, sinh một lần cho mỗi project.**
  Mở `docs/kien-truc.md`. Đã có → đọc hết trước khi viết bất cứ dòng phân tích nào.
  Chưa có → sinh bản nháp NGAY trong phase này rồi trình user sửa và chốt; user chưa
  chốt thì mọi dòng trong đó là gợi ý, không phải luật. Bản nháp đúng 4 mục:
  1. `## Tầng` — mỗi dòng một tầng/cụm của project kèm trách nhiệm của nó.
  2. `## Luật gọi` — mỗi dòng một luật "tầng X không được gọi tầng Y", kèm lý do.
  3. `## Hub` — 5 node nhiều liên kết nhất kèm số bậc, lấy từ `graphify god-nodes`.
     Sửa một node trong danh sách này là việc rủi ro cao, phải khai ở M4.
  4. `## Đã chốt` — quyết định kiến trúc đã đóng kèm ngày; muốn đổi phải mở request riêng.
  Nguồn sinh nháp: cây thư mục + `graphify god-nodes` + file cấu hình build.
  Ví dụ mục `## Hub` sinh từ repo này ngày 2026-08-14: `Changelog - 28 edges`,
  `main() - 20 edges`, `cli() - 17 edges`, `log() - 17 edges`, `cmd_build() - 17 edges`.

- Cách kiểm: `test -f docs/kien-truc.md && test "$(grep -c '^## ' docs/kien-truc.md)" -eq 4`

### M2 — Ô "Ràng buộc kiến trúc phải giữ" trong spec

- Chặn: triệu chứng 1 — hồ sơ kiến trúc có tồn tại nhưng không ai buộc phải đối chiếu
  với đúng việc đang làm.
- Chèn vào: skills/tdq-spec/references/spec-template.md:§5 Ràng buộc & rủi ro
- Mức: A
- Nội dung nháp:

  Mở đầu §5, đặt TRƯỚC bảng rủi ro, bắt buộc có khối sau. Chỉ chép dòng nào việc này
  thật sự chạm tới; chép cả file là sai, chép rỗng cũng sai.

  ```
  Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`):
  - <nguyên văn dòng luật gọi hoặc dòng đã chốt> — việc này chạm ở <file/hàm>
  ```

  Việc không chạm ràng buộc nào → ghi đúng một dòng
  `Ràng buộc kiến trúc phải giữ: không chạm dòng nào — <lý do một câu>`.
  Chưa có `docs/kien-truc.md` → quay lại M1, không được bỏ trống khối này.

- Cách kiểm: `grep -c "^Ràng buộc kiến trúc phải giữ" docs/tdq/spec/<slug>.md` bằng 1

### M3 — Luật tìm rồi mới tạo

- Chặn: triệu chứng 2 — viết đoạn mới rẻ hơn tìm và dùng lại, nên agent luôn chọn viết mới.
- Chèn vào: skills/tdq-build/SKILL.md:Phần A bước 2.4
- Mức: A
- Nội dung nháp:

  Dòng luật cũ bị THAY: `4. Code: thay đổi nhỏ nhất mà đủ thoả task. Bám style code
  sẵn có.` Dòng mới:

  ```
  4. Code: thay đổi nhỏ nhất mà đủ thoả task. Bám style code sẵn có.
     **Tìm rồi mới tạo.** Sắp tạo file, class, hàm, hằng số hay bảng cấu hình MỚI →
     trước đó chạy đúng một lượt tìm thứ đã có: `graphify query "<tên khái niệm>"`,
     hoặc grep tên khái niệm cộng 2 từ đồng nghĩa. Tìm thấy thứ gần giống mà vẫn tạo
     mới → ghi đúng một dòng vào task đó trong plan:
     `Tạo mới thay vì dùng <đường dẫn thứ đã có> vì <lý do>`.
     Không tìm mà tạo mới là lỗi, kể cả khi test xanh.
  ```

- Cách kiểm: `test -z "$(git diff --name-only --diff-filter=A -- scripts hooks src)" || grep -q "Tạo mới thay vì dùng" docs/tdq/plan/<slug>.md`

### M4 — Khai bán kính ảnh hưởng trong plan

- Chặn: triệu chứng 3 — không ai biết một task chạm tới đâu cho tới khi có thứ vỡ.
- Chèn vào: skills/tdq-plan/references/plan-template.md:khuôn task
- Mức: A
- Nội dung nháp:

  Task nào sửa file mã nguồn ĐÃ CÓ (không tính task tạo file mới, không tính task sửa
  tài liệu) → ngay dưới dòng task thêm đúng một dòng:

  ```
    - Chạm: <hàm/file bị sửa> → <danh sách node bị ảnh hưởng>
      (nguồn: graphify affected "<X>" --depth 2)
  ```

  Không node nào phụ thuộc → ghi `Chạm: <X> → không node nào phụ thuộc`. Node bị ảnh
  hưởng nằm trong mục `## Hub` của `docs/kien-truc.md` → task đó phải có thêm một dòng
  Definition of Done kiểm hồi quy riêng cho node ấy.
  Ví dụ chạy thật trên repo này: `graphify affected "payload_cwd" --depth 2` trả về 5
  hook phụ thuộc (`bash_gate.py`, `edit_gate.py`, `prompt_context.py`,
  `session_start.py`, `stop_gate.py`) — sửa hàm này mà không chạy test hook là mù.

- Cách kiểm: `graphify affected "<X>" --depth 2` chạy lại phải ra đúng danh sách đã khai trong plan

### M5 — Ba hạng mục QC cố định chống hồi quy

- Chặn: triệu chứng 1 và 3 — QC bám đúng DoD nên thiệt hại ngoài DoD không có ai bắt.
- Chèn vào: skills/tdq-build/references/qc.md:mục "Chạy cái gì"
- Mức: A
- Nội dung nháp:

  Dòng luật cũ bị NỚI: `**Số hạng mục QC = số dòng Definition of Done của plan.**` và
  `Không thêm hạng mục ngoài DoD, không bớt dòng DoD nào.` Dòng mới:

  ```
  **Số hạng mục QC = số dòng Definition of Done của plan, cộng ba hạng mục cố định.**
  Ba hạng mục cố định luôn chạy, không phụ thuộc DoD:
  - QC-F1 toàn bộ test suite (hạng mục cố định cũ, giữ nguyên).
  - QC-F2 hồi quy vùng chạm: với mỗi dòng `Chạm:` trong plan, chạy test của module
    chứa node bị ảnh hưởng. Node không có test → ghi `KHÔNG CÓ TEST: <node>` vào file
    QC; đó là nợ kỹ thuật phải nêu trong report, không được tính là PASS.
  - QC-F3 ràng buộc kiến trúc: mỗi dòng trong khối "Ràng buộc kiến trúc phải giữ" ở
    spec §5 là một phép kiểm rằng bản thay đổi không phá dòng đó.
  Ngoài ba hạng mục này, vẫn không thêm hạng mục nào ngoài DoD.
  ```

- Cách kiểm: `test "$(grep -c '^| QC-F[123] ' docs/tdq/qc/<slug>.md)" -eq 3`

### M6 — Cổng trùng lặp chạy bằng máy

- Chặn: triệu chứng 2 — M3 là luật cho agent tự giác; cần một phép đo khách quan bắt
  bản sao mà agent không tự khai.
- Chèn vào: skills/tdq-build/references/qc.md:mục "Các thứ dưới đây chỉ kiểm khi DoD chạm tới"
- Mức: B
- Nội dung nháp:

  ```
  - Trùng lặp: chỉ chạy khi turn này có thêm hoặc sửa từ 2 file mã nguồn trở lên.
    Lệnh: `npx jscpd --min-lines 8 --threshold 3 --reporters console <thư mục code>`.
    Vượt ngưỡng → không tự sửa ngay, mà ghi từng cặp block trùng vào file QC kèm một
    dòng quyết định: gộp lại bây giờ, hay để lại và nêu trong report như nợ kỹ thuật.
    False positive quen mặt (khai báo lặp hợp lệ, chuỗi cấu hình) → thêm vào
    `.jscpd.json` phần `ignore`, ghi lý do ngay trong file đó.
  ```

  Đã kiểm ngày 2026-08-14: `jscpd` bản 5.0.15, chạy CLI không cần server, `jscpd --list`
  trả 224 định dạng ngôn ngữ — nên hợp với việc workflow áp cho mọi project. Ba cờ dùng
  trong lệnh trên (`--min-lines`, `--threshold`, `--reporters`) đều có thật trong
  `jscpd --help` của bản này. Chạy thử trên chính repo TDQWorkflow: 574 file, 72 cặp
  trùng, 1.82% token trùng, dưới ngưỡng 3% nên exit 0.
  Project đã có SonarQube thì thay bằng Quality Gate trùng lặp trên new code (ngưỡng mặc
  định 3%), không chạy hai tool song song.

- Cách kiểm: `npx --yes jscpd --min-lines 8 --threshold 3 --reporters console .` trả exit 0

## Gói

Ba gói cộng dồn: gói sau chứa trọn gói trước.

### Gói tối thiểu — hai dòng luật, không script

Gồm M2 và M3. Thuần văn bản, sửa đúng 2 file trong `skills/`. Chi phí mỗi request:
một khối 1–3 dòng trong spec §5, cộng một lượt `graphify query` hoặc grep trước khi tạo
thứ mới. Chặn được triệu chứng 1 phần nào và triệu chứng 2. Không chặn triệu chứng 3.
Nhược: M2 chép từ `docs/kien-truc.md` mà gói này chưa có M1 nên chưa có file nguồn —
phải viết ràng buộc bằng tay từ hiểu biết của agent, dễ lệch.

### Gói vừa — luật đầy đủ, vẫn không script

Gồm M1, M2, M3, M4, M5. Tất cả đều mức A, không thêm file thực thi nào, không thêm cổng
duyệt. Chi phí một lần cho mỗi project: sinh `docs/kien-truc.md` (một lần, user chốt).
Chi phí mỗi request: khối ràng buộc trong spec, một dòng `Chạm:` cho mỗi task sửa code
có sẵn, ba hạng mục QC cố định. Chặn đủ cả ba triệu chứng. Nhược: mọi phép kiểm đều dựa
vào agent khai đúng, không có máy bắt lỗi khai thiếu.

### Gói đầy đủ — thêm cổng máy

Gồm cả sáu, tức gói vừa cộng M6. Thêm phụ thuộc ngoài (`npx jscpd`, hoặc SonarQube nếu
project đã có) và thêm thời gian chạy vào mỗi lượt QC có sửa từ 2 file trở lên. Bù lại
đây là cơ chế duy nhất không tin vào lời khai của agent. Nhược: false positive cần tinh
chỉnh `.jscpd.json` ban đầu, và project không có Node phải cài thêm.

Khuyến nghị: Gói vừa — chặn đủ ba triệu chứng, không thêm phụ thuộc ngoài nào, không
cổng duyệt mới, và giữ đúng tinh thần request `2026-08-08-giam-over-engineer-workflow`
là không dựng thêm bộ máy cho việc nội bộ. M6 để dành, bật riêng cho project nào đã đo
thấy trùng lặp thật.

## Express

Pipeline express dùng chung sáu cơ chế nhưng rút gọn, vì express chỉ có một file
mini-spec/plan gộp và trần 40 dòng.

- M1 — GIỮ phần đọc, BỎ phần sinh. Express đọc `docs/kien-truc.md` nếu có; không có thì
  ghi một dòng `Không có hồ sơ kiến trúc — làm theo style file đang sửa` và đi tiếp.
  Sinh hồ sơ là việc của lane full, vì nó cần user chốt.
- M2 — GIỮ, rút thành một dòng trong mục phạm vi của mini-plan thay vì một khối.
- M3 — GIỮ nguyên. Đây là luật rẻ nhất và đúng chỗ express hay hỏng nhất.
- M4 — GIỮ có điều kiện: chỉ khai `Chạm:` khi task sửa file mã nguồn đã có; express sửa
  tài liệu hay cấu hình thì bỏ.
- M5 — GIỮ QC-F1 và QC-F2, BỎ QC-F3. Express không có spec §5 nên không có khối ràng
  buộc để đối chiếu. `quick_qc_skipped = true` thì bỏ cả ba, đúng như luật hiện hành.
- M6 — BỎ. Express là đường nhanh, không gánh thêm phụ thuộc ngoài.

## Áp cho project khác

Phần độc lập ngôn ngữ, dùng nguyên cho mọi project kể cả Unity hay game:

- Toàn bộ M2, M3, M5 — chỉ là luật văn bản và quy ước ghi chép, không giả định ngôn ngữ.
- Khung 4 mục của M1. Nội dung từng mục thì mỗi project tự viết: project Unity ghi tầng
  theo assembly definition và luật gọi giữa `Scripts/Runtime` với `Scripts/Editor`;
  project web ghi theo tầng route/service/repository.

Phần phải chỉnh theo từng project:

- M1 mục `## Hub` và M4 — phụ thuộc `graphify` phân tích được ngôn ngữ đó. Không phân
  tích được thì thay bằng nguồn khác cho cùng thông tin: IDE find-usages, `rg` theo tên
  ký hiệu, hoặc bảng phụ thuộc của build system. Dòng `Chạm:` vẫn bắt buộc, chỉ đổi
  cách lấy dữ liệu; ghi rõ nguồn trong ngoặc như khuôn M4 yêu cầu.
- M6 — `jscpd` chạy qua `npx` nên project không có Node phải cài Node hoặc đổi sang
  công cụ trùng lặp của stack mình.

Cố ý KHÔNG đề xuất: fitness function theo stack (ArchUnit cho Java, PyTestArch cho
Python, dependency-cruiser cho JS). Chúng mạnh hơn M1+M2 nhiều nhưng mỗi ngôn ngữ một
tool và một cú pháp rule riêng, không viết được một dòng luật chung cho mọi project.
Project nào đã đứng yên một stack thì nên tự thêm, coi như bản nâng cấp của M2.

## Nguồn

- https://www.gitclear.com/ai_assistant_code_quality_2025_research
- https://gitclear-public.s3.us-west-2.amazonaws.com/GitClear-AI-Copilot-Code-Quality-2025.pdf
- https://github.com/github/spec-kit/blob/main/spec-driven.md
- https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit
- https://blog.thestateofme.com/2025/07/10/using-architecture-decision-records-adrs-with-ai-coding-assistants
- https://github.com/me2resh/agent-decision-record
- https://www.archunit.org/userguide/html/000_Index.html
- https://handsonarchitects.com/blog/2026/protecting-architecture-with-automated-tests-in-python
- https://www.infoq.com/articles/fitness-functions-architecture
- https://github.com/kucherenko/jscpd
- https://www.npmjs.com/package/jscpd
- https://community.sonarsource.com/t/code-duplication-quality-gate-and-default-branch/26999
- https://arxiv.org/html/2601.20404v1
