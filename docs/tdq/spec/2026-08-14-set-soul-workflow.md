# SPEC — Soul cho workflow và thư viện rule kỹ thuật đa ngôn ngữ

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Ngày: 2026-08-14 · Bản: 1.2 · Brief: ../brief/2026-08-14-set-soul-workflow.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: ĐÃ DUYỆT 2026-08-14T22:19 (dòng Soul thêm sau duyệt theo chính đầu ra 15 của spec)

Bản 1.1 thêm nguyên tắc "viết cho model yếu nhất" theo góp ý của user lúc 22:04 — chi tiết
ở §1 mục tiêu 3, §3 khuôn 3 mục bắt buộc, §2 đầu ra 13, §6 hạng mục Q17 và Q18.
Bản 1.2 mở phạm vi soul sang tài liệu của từng request theo góp ý lúc 22:07 — §1 mục tiêu
4, §2 đầu ra 14 và 15, §6 hạng mục Q19 và Q20. Bản 1.1 mới áp soul cho file luật trong
`skills/`, không áp cho brief, spec, plan, qc, report — đó là chỗ thiếu user chỉ ra.

## 1. Mục tiêu & phạm vi

- Mục tiêu: đặt một văn bản gốc phát biểu thứ tự ưu tiên của cả harness — chất lượng MVP
  của code do agent sinh, rồi runtime, rồi context cost — và biến thứ tự đó thành phép
  kiểm chạy được, thay vì một tuyên ngôn nằm im.
- Mục tiêu 2: dựng thư viện rule kỹ thuật cho 7 ngôn ngữ, đọc lúc viết code và kiểm lúc
  QC, cộng cơ chế tự research khi gặp ngôn ngữ chưa có.
- Mục tiêu 3: mọi luật viết ra từ nay — trong soul, trong thư viện rule, trong mọi bổ
  sung sau này — phải đủ chi tiết để một model cấp thấp như Haiku làm theo được trọn vẹn,
  không chỉ model mạnh như Opus mới suy ra được ý.
- Mục tiêu 4: soul áp cho MỌI thứ trong workflow, gồm cả tài liệu của từng request —
  brief, spec, plan, qc, report — kể cả brief của chính request này và mọi brief sau này.

Trong phạm vi:

- File soul và dòng trỏ tới nó ở skill nền cùng bản `portable/AGENTS.md`.
- Rà soát 28 file trong `skills/` đối chiếu soul, sửa luật nào nghịch thứ tự ưu tiên.
- Thư viện rule: 1 file chỉ mục, 1 file trục chung, 7 file ngôn ngữ, 1 file quy trình
  thêm ngôn ngữ mới.
- Script quét rule chạy sau QC, gọi linter đã có sẵn trong máy.
- Câu hỏi bật/tắt cơ chế clean code ở phase `spec`, cùng luật xử cho từng nhánh.
- Năm cơ chế M1–M5 của `docs/tdq/knowledge/2026-08-14-chong-no-ky-thuat.md`.
- Khuôn 3 mục bắt buộc cho mọi file luật mới, cộng một rule lint mới bắt khuôn đó.
- Dòng `Soul:` trong 5 khuôn tài liệu của workflow, cộng phép kiểm bắt request đang mở
  phải có dòng đó ở brief, spec và plan.
- Test tự động giữ cho soul và thư viện rule không trôi.

NGOÀI phạm vi:

- Không mặt nào bị loại ở vòng scope — user chọn cả bốn mặt A B C D.
- M6 (cổng trùng lặp `jscpd`): để dành, vì thêm phụ thuộc `npx` vào mọi lượt QC.
- Chép thư viện rule sang `portable/`: nhân đôi chỗ phải bảo trì, để request riêng.
- Không tự cài linter, không dựng server SonarQube, không đụng `plugin.json`
  hay `CHANGELOG.md` — việc bump bản là lượt riêng do user yêu cầu.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web (bù 3 khoảng trống) | CÓ | TS/JS, HTML, C++ chưa có URL xác thực mà vẫn phải viết rule |
| Interview | CÓ (đã xong 2 vòng) | không còn câu hỏi làm đổi kết quả |
| Spec + plan | CÓ | khung bất biến |
| Chia subagent lúc implement | user quyết ở cổng mode | 10 file rule là việc song song được |
| QC độc lập bằng agent `tdq-qc-tester` | CÓ | chạm luật nền và bước QC của mọi request sau |
| Review sâu bằng `tdq-reviewer` | BỎ | user chưa yêu cầu; QC độc lập đã là một lượt mắt ngoài |
| Đồng bộ `portable/` | CÓ, một phần | chỉ soul và dòng luật QC |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | File soul | `skills/tdq-conventions/references/soul.md` | test đọc được 3 tầng ưu tiên đúng thứ tự |
| 2 | Dòng trỏ soul | `skills/tdq-conventions/SKILL.md` §11 · `portable/AGENTS.md` | `grep -c 'soul.md'` ≥ 1 ở cả hai file |
| 3 | Biên bản rà soát luật cũ | `docs/tdq/knowledge/2026-08-14-ra-soat-luat-theo-soul.md` | bảng có đủ 28 file, mỗi dòng có phán quyết |
| 4 | Chỉ mục thư viện rule | `skills/tdq-build/references/rules/index.md` | test: mọi file trong `rules/` đều có dòng trong chỉ mục |
| 5 | Trục chung mọi ngôn ngữ | `skills/tdq-build/references/rules/chung.md` | test: có đủ 4 thuộc tính Clean Code và 2 ngưỡng số |
| 6 | 7 file rule ngôn ngữ | `rules/{csharp,cpp,python,typescript-js,html,go,rust}.md` | test: mỗi file đủ 7 mục của khuôn |
| 7 | Quy trình thêm ngôn ngữ mới | `skills/tdq-build/references/rules/them-ngon-ngu.md` | test: có bước trình nháp trước khi ghi user-level |
| 8 | Script quét rule | `scripts/code_rule_scan.py` | chạy trên repo này ra bảng, exit 0 hoặc 1 đúng nghĩa |
| 9 | Câu hỏi bật clean code | `skills/tdq-spec/SKILL.md` · `references/spec-template.md` | test: khuôn spec có dòng `Clean code:` |
| 10 | Luật QC mới | `skills/tdq-build/references/qc.md` · `portable/workflow/references/qc.md` | test: hai bản có cùng số hạng mục cố định |
| 11 | Cơ chế M1–M4 | `tdq-intake`, `tdq-spec`, `tdq-build`, `tdq-plan` | `grep` thấy đúng dòng luật của từng cơ chế |
| 12 | Test giữ soul và rule | `tests/test_soul_rules.py` | `pytest` xanh, và đỏ khi cố tình phá |
| 13 | Rule lint R9 bắt khuôn 3 mục | `scripts/doc_lint.py` | chạy trên file rule thiếu mục → exit 1, đủ mục → exit 0 |
| 14 | Dòng `Soul:` trong 5 khuôn tài liệu | `tdq-intake/SKILL.md` (brief) · `spec-template.md` · `plan-template.md` · `qc.md` · `report-template.md` | `grep -c '^Soul:'` ≥ 1 ở mỗi khuôn |
| 15 | Dòng `Soul:` trong tài liệu request đang mở | `docs/tdq/{brief,spec,plan}/<slug hiện hành>.md` | test đọc `state.json` rồi soi đúng các file đó, gồm cả brief của chính request này |

## 3. Cách tiếp cận & lý do

- Chọn: tách ba tầng nạp cho thư viện rule — chỉ mục mỏng, file ngôn ngữ nạp khi đụng
  đúng ngôn ngữ đó, nguồn ngoài mạng chỉ mở khi cần trích. Vì đây đúng mô hình progressive
  disclosure mà nguồn về viết rule cho agent đồng thuận, và vì context cost là ưu tiên thứ
  ba của chính soul.
- Chọn: bộ rule dồn sức vào nhóm Intentionality (đặt tên rõ, không code chết, logic đủ).
  Vì đo trên 1.848 issue của code do LLM sinh, 59,6% lỗi rơi đúng nhóm này
  (arXiv 2411.10656).
- Chọn: ngưỡng mặc định cyclomatic ≤ 10 và cognitive ≤ 15, riêng họ C ≤ 25, theo mặc định
  SonarQube. Các tool khác đặt khác nhau (ESLint 20, Microsoft CA1502 25) nên phải chốt
  một số làm gốc và cho project ghi đè bằng file cấu hình.
- Chọn: script quét gọi linter đã có trong máy, thiếu thì in tên gói và lệnh cài rồi đánh
  dấu "chưa kiểm được". Vì user chốt không tự cài, và vì một lượt cài ngầm phá luôn ưu
  tiên runtime.
- Chọn: mặc định script chỉ quét file đã đổi trong request, cờ `--tat-ca` mới quét toàn
  repo. Vì quality gate của Sonar cũng chỉ áp cho code mới, và vì quét cả repo mỗi lượt QC
  là chi phí runtime không đáng.
- Chọn: mọi file luật mới viết theo đúng 3 mục — `## Khi nào áp dụng` (dấu hiệu nhận ra
  được bằng mắt hoặc bằng lệnh), `## Làm gì` (các bước đánh số, mỗi bước một hành động,
  câu mệnh lệnh), `## Tự kiểm` (một lệnh hoặc một câu hỏi có/không). Luật nào dễ hiểu
  nhầm thì thêm một cặp ví dụ ĐÚNG và SAI. Vì model cấp thấp làm theo được khi luật nói
  rõ làm gì theo thứ tự nào, và trượt khi luật chỉ nêu nguyên tắc.
- Chọn: kiểm khuôn đó bằng máy qua rule mới R9 của `doc_lint.py`, chỉ áp cho `soul.md` và
  `skills/tdq-build/references/rules/`. Vì áp cho toàn kho sẽ làm đỏ hàng loạt file cũ
  viết theo khuôn khác, mà request này không nhận việc viết lại toàn bộ tài liệu.
- Chọn: nghiệm thu bằng thử nghiệm thật — giao một agent chạy model Haiku đọc đúng một
  file rule rồi làm theo, không được hỏi lại. Vì đó là phép đo trực tiếp cho yêu cầu
  "model cấp thấp cũng làm được", thay vì tự chấm bằng cảm nhận.
- Chọn: mỗi tài liệu của request mang đúng một dòng cố định ngay dưới dòng ngày tháng —
  `Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md`.
  Vì soul chỉ có hiệu lực khi nó nằm trong ngữ cảnh lúc agent đang viết tài liệu đó, chứ
  không phải khi nó nằm yên trong một file không ai mở.
- Chọn: phép kiểm dòng `Soul:` đặt trong bộ test và soi theo `active_request` của
  `state.json`, không đặt thành rule của `doc_lint.py`. Vì `doc_lint` miễn cho `docs/tdq/`
  gần hết các rule, còn nếu áp cho cả thư mục thì hơn 20 tài liệu của các request đã đóng
  sẽ đỏ, mà viết lại tài liệu cũ không nằm trong request này.
- Chọn: test chỉ soi file đang có thật, thiếu file thì bỏ qua. Vì giữa request thì plan
  chưa sinh ra, và một phép kiểm đỏ oan sẽ bị người ta tắt đi.
- Đã loại: nhét soul vào `SKILL.md` — vì SKILL.md là tầng luôn nạp, phình ra là mọi
  request sau phải trả tiền context.
- Đã loại: chỉ viết luật bằng chữ trong `qc.md` (phương án 2B) — vì không có máy nào bắt
  được lời khai sai của agent.
- Đã loại: M6 cổng trùng lặp `jscpd` — thêm phụ thuộc ngoài vào mọi lượt QC.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-intake` | plugin:tdq-workflow | NỀN | skill khung đang chạy phase analyze |
| `tavily-primary` | plugin | DÙNG | bù 3 khoảng trống nguồn trước khi viết file rule TS/JS, HTML, C++ |
| `graphify` | plugin | DÙNG | cuối turn có đổi mã nguồn, cập nhật đồ thị |
| `tdq-qc-tester` | plugin:tdq-workflow | DÙNG | lượt QC độc lập ở phase qc |
| `sonarqube` | plugin | KHÔNG | spec §3 đã chọn cách khác tốt hơn — dùng linter sẵn có thay vì dựng server Sonar |
| `context7` | plugin | KHÔNG | spec §3 đã chọn cách khác tốt hơn — rule trích thẳng style guide chính thống |
| Đã xét 36 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: `scripts/code_rule_scan.py` in log có timestamp cho từng bước
  (dò ngôn ngữ, tìm linter, chạy linter, kết luận), tắt bằng cờ `--im`, chi tiết hơn bằng
  `--chi-tiet`.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật. Rule nào chưa
  có nguồn xác thực thì ghi "chưa có nguồn", cấm bịa URL.
- Mỗi thành phần có unit test riêng, chạy được bằng `python3 -m pytest tests/ -q`.

## 5. Ràng buộc & rủi ro

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Ghi file vào `~/.claude` là ngoài git, không hoàn tác được | mất hoặc đè rule user-level | luật bắt trình nháp trong chat và chờ user duyệt mới ghi |
| Sửa `qc.md` đụng cùng dòng luật với M5 | hai request đá nhau | user đã chốt gộp M1–M5 vào request này, sửa một lần |
| Thư viện 10 file làm phình context | mọi request sau đắt hơn | tầng nạp có điều kiện, cộng một hạng mục QC đo token |
| Máy thiếu linter của 7 ngôn ngữ | quét ra kết quả rỗng mà tưởng sạch | script phân biệt rõ PASS với "chưa kiểm được", và in lệnh cài |
| Ngưỡng complexity không thống nhất giữa tool | rule bị cãi là sai | ghi rõ nguồn của từng ngưỡng và cách ghi đè trong file cấu hình |
| Rà soát 28 file có thể lộ luật cũ nghịch soul | phải sửa thêm ngoài dự tính | biên bản rà soát ghi cả dòng KHÔNG SỬA kèm lý do, không sửa lén |
| R9 áp nhầm phạm vi làm đỏ file cũ | lint chặn cả những lượt không liên quan | R9 chỉ soi `soul.md` và thư mục `rules/`, có test khoá đúng phạm vi đó |
| Viết đủ chi tiết cho model yếu làm file dài ra | đụng trần 500 dòng và ăn context | mỗi file rule giữ dưới 150 dòng, chi tiết dồn vào bước và ví dụ chứ không vào văn xuôi |
| Test soi theo `state.json` đỏ oan lúc chưa có plan | người ta tắt luôn phép kiểm | chỉ soi file đã tồn tại; không có request mở thì test tự bỏ qua |
| Dòng `Soul:` thành nghi thức chép máy móc | có dòng chữ mà không đổi hành vi | soul nêu rõ dùng thứ tự ưu tiên để phân xử ở đâu, và §5 của spec phải ghi bên nào thua khi đánh đổi |

Ràng buộc cứng:

- Không cài gói mới, không chạy `npx`, không gọi dịch vụ ngoài để ghi.
- `doc_lint.py` chặn mọi file quá 500 dòng, nên mỗi file rule phải nằm dưới trần đó.
- Bộ test hiện có 574 test phải còn xanh nguyên.

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Soul có đủ 3 tầng ưu tiên đúng thứ tự | `pytest tests/test_soul_rules.py -k thu_tu` | 1 passed |
| Q2 | Skill nền và bản portable đều trỏ soul | `grep -c 'soul' skills/tdq-conventions/SKILL.md portable/AGENTS.md` | cả hai ≥ 1 |
| Q3 | Rà soát đủ 28 file skill | đếm dòng bảng trong biên bản rà soát | 28 dòng, mỗi dòng có phán quyết |
| Q4 | Chỉ mục khớp đúng số file rule | `pytest -k chi_muc` | 1 passed |
| Q5 | 7 file ngôn ngữ đủ 7 mục khuôn | `pytest -k khuon_ngon_ngu` | 7 subtest passed |
| Q6 | Mọi URL trong file rule có thật | `pytest -k nguon` (kiểm dạng URL) cộng đối chiếu file research | 0 URL bịa |
| Q7 | Script quét chạy thật trên repo này | `python3 scripts/code_rule_scan.py --tat-ca` | in bảng, phân biệt PASS với chưa kiểm được |
| Q8 | Script không tự cài gì | `grep -E 'pip install\|npm i\|apt-get' scripts/code_rule_scan.py` | 0 kết quả |
| Q9 | Log service của script | chạy có và không có `--im` | có `--im` thì 0 dòng log, không có thì mỗi dòng có timestamp |
| Q10 | Câu hỏi clean code vào đúng khuôn spec | `pytest -k clean_code_gate` | 1 passed |
| Q11 | Luật QC hai bản khớp nhau | `pytest -k qc_dong_bo` | 1 passed |
| Q12 | M1–M5 có mặt đủ | `pytest -k co_che_m` | 5 subtest passed |
| Q13 | Test mới đỏ được khi phá | tự tay phá 1 chỗ, chạy lại, khôi phục | ít nhất 3 test chuyển đỏ |
| Q14 | Không phình context tầng luôn nạp | `python3 scripts/token_audit.py` trước và sau | tổng token của 6 file SKILL.md tăng ≤ 200 |
| Q15 | Toàn bộ test suite | `python3 -m pytest tests/ -q` | 574 test cũ còn xanh, 0 failed |
| Q16 | Lint tài liệu | `python3 scripts/doc_lint.py <mọi file đã sửa>` | exit 0 |
| Q17 | R9 bắt đúng khuôn 3 mục và đúng phạm vi | `pytest -k r9` | file rule thiếu mục → lỗi R9; file ngoài phạm vi → không bị soi |
| Q18 | Model cấp thấp làm theo được | giao agent chạy Haiku đọc `rules/python.md` rồi soát một đoạn code mẫu có sẵn 5 lỗi | agent nêu đúng ≥ 4/5 lỗi và không hỏi lại câu nào |
| Q19 | 5 khuôn tài liệu đều có dòng `Soul:` | `pytest -k khuon_tai_lieu` | 5 subtest passed |
| Q20 | Tài liệu request đang mở có dòng `Soul:` | `pytest -k soul_request_dang_mo` | brief, spec và plan của slug hiện hành đều đạt; brief của chính request này nằm trong số đó |

DoD: đủ 20 hạng mục trên PASS có bằng chứng · 15 đầu ra ở §2 tồn tại đúng đường dẫn ·
mọi file luật mới đủ 3 mục khuôn và dưới 150 dòng · brief, spec và plan của chính request
này mang dòng `Soul:` · biên bản rà soát nêu rõ luật nào đã sửa và luật nào giữ nguyên kèm
lý do · một lượt QC độc lập bằng agent `tdq-qc-tester` cho kết quả PASS.

## 7. Câu hỏi còn mở

(rỗng)
