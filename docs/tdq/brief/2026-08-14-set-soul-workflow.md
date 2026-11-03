# BRIEF — Set "soul" cho bộ workflow

Ngày: 2026-08-14 · Slug: `2026-08-14-set-soul-workflow`
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> tôi muốn set soul cho bộ workflow này sẽ ưu tiên đầu tiên là chất lượng quality mvp của
> agent code, sau đó đến runtime, context cost và mục đích tạo bộ harness để support dev
> có thể dùng AI để cho kết quả tốt hơn, hoàn thiện, ưu tiên chất lượng hơn số lượng.
> Hãy set soul để từ những bản cũ và cả những bổ sung sau này vẫn giữ tinh thần như trênn

### Cách hiểu đầu tiên

**Mục tiêu.** Bộ TDQ Workflow hiện có luật rất nhiều nhưng chưa có một chỗ phát biểu
*thứ tự ưu tiên* khi hai luật đá nhau. "Soul" = một văn bản hiến pháp ngắn, đặt trên mọi
skill, nói rõ: khi phải đánh đổi thì hy sinh cái nào trước.

**Thứ tự ưu tiên user nêu (nguyên văn, không diễn giải lại):**

1. Chất lượng — cụ thể là "quality MVP của agent code".
2. Runtime.
3. Context cost.

**Mục đích của cả harness:** hỗ trợ dev dùng AI cho ra kết quả tốt hơn và hoàn thiện hơn;
ưu tiên chất lượng hơn số lượng.

**Ràng buộc thời gian:** tinh thần này phải áp ngược cho các bản đã có VÀ áp xuôi cho mọi
bổ sung sau này. Nghĩa là không chỉ viết một file tuyên ngôn — phải có cách giữ cho nó
không bị trôi.

**Phạm vi đoán.** Chạm tới `skills/tdq-conventions/` (nơi đặt luật nền), có thể thêm một
file soul mới, có thể thêm dòng trỏ ở các skill `tdq-*`, có thể thêm phép kiểm bằng máy
(`scripts/doc_lint.py` hoặc test riêng) để chống trôi, và bản `portable/`.

### Chỗ chưa rõ (phải hỏi, chưa tự quyết)

1. "Soul" là văn bản để NGƯỜI đọc, hay là luật để MÁY kiểm, hay cả hai?
2. "Quality MVP của agent code" — đo bằng gì? (test bắt buộc? không placeholder? đã có
   sẵn trong spec §4 — soul chỉ nhắc lại, hay soul định nghĩa chặt hơn?)
3. Thứ tự ưu tiên này dùng ở đâu cụ thể: lúc viết spec, lúc chọn lane, lúc QC, hay lúc
   Claude phải quyết một mình khi gặp chặn kỹ thuật?
4. Có cần cơ chế chống trôi bằng máy không, hay chỉ cần văn bản + dòng trỏ?
5. Áp ngược cho bản cũ nghĩa là gì: rà soát lại toàn bộ luật hiện có xem có luật nào
   nghịch tinh thần này, hay chỉ cần từ nay trở đi?

### Ghi chú phát hiện lúc đọc lại khuôn

`skills/tdq-intake/references/lane-decision.md` dòng 53-54 khoá cứng `A = chế độ nhanh`,
trong khi luật ngay trên đó (dòng 44-45) nói "phương án đề xuất luôn ở A". Hai chỗ này
đá nhau khi phương án đề xuất là chế độ chuyên sâu. Ghi lại để xử sau, ngoài phạm vi
request này.

## Hiểu & kiến thức

### Yêu cầu mở rộng (user nói thêm cùng lượt chốt lane)

> A tôi muốn bạn resreach và có thể tạo bộ rule kĩ thuật cho lập trình yêu cầu bao phủ
> nhiều ngôn ngữ bao gồm C#, C++, python, typescript js, html, go, rust,... và phẩn bổ
> rule trong reference để có thể tổ chức và check sau bước QC để bảo bảo project hạn chế
> tối đa nợ kĩ thuật, và development đúng kĩ thuật, ngắn gọn, đạt chuẩn "clean code" và
> sau này nếu gặp một ngôn ngữ, trường hợp chưa có thì sẽ resreach để get bộ rule tối ưu
> và lưu trong reference user-level

Request thành hai phần dính nhau: (1) soul — thứ tự ưu tiên và mục đích harness;
(2) thư viện rule kỹ thuật đa ngôn ngữ đặt trong `references/`, kiểm sau bước QC, cộng
cơ chế research bổ sung khi gặp ngôn ngữ chưa có. Phần 2 là chỗ soul biến thành phép kiểm
chạy được, nên làm chung một request là hợp lý.

### Năng lực dùng được

| Năng lực | Verdict | Vì sao |
|---|---|---|
| `tavily-primary` search | DÙNG | đã dùng cho lượt research; còn 3 khoảng trống nguồn phải bù |
| plugin `sonarqube` (skill `sonar-*`, agent `sonarqube-reviewer`) | DÙNG khi build | có sẵn taxonomy Clean Code và bộ rule theo ngôn ngữ, khỏi tự bịa |
| `graphify` | DÙNG | đã bắt buộc cuối turn đổi code |
| `context7` | DÙNG khi build | tra doc linter theo phiên bản thay vì nhớ |
| `scripts/doc_lint.py` | DÙNG | chỗ gắn phép kiểm chống trôi bằng máy |
| `tests/` (574 test) | DÙNG | chỗ gắn test chống trôi |
| agent `tdq-qc-tester` | DÙNG khi QC | lượt kiểm độc lập |
| `skill-creator`, `hookify`, `code-review` | KHÔNG | không tạo skill mới ngoài TDQ, không thêm hook |

### Đọc code — hiện trạng

- `skills/` có 28 file, 1.990 dòng. Skill nền là `tdq-conventions/SKILL.md` (120 dòng),
  mục `## 11. Chất lượng` đúng 4 dòng: cấm placeholder, log service, mỗi task một test.
  Đây là chỗ gần "soul" nhất hiện có, và nó không nói gì về thứ tự ưu tiên.
- Không có bất kỳ dòng nào trong `skills/` nhắc "nợ kỹ thuật", "clean code" hay tên một
  linter nào. Thư viện rule là phần hoàn toàn mới.
- Bước QC nằm ở `skills/tdq-build/references/qc.md`. Luật hiện tại đóng cứng:
  "Số hạng mục QC = số dòng Definition of Done… Không thêm hạng mục ngoài DoD". Muốn
  kiểm rule sau QC thì phải nới đúng dòng này, giống cách M5 đã đề xuất.
- `doc_lint.py` có trần R6: mọi file quá 500 dòng là lỗi, riêng SKILL.md còn trần chặt
  hơn. Thư viện rule 7 ngôn ngữ phải tách file, không thể dồn một chỗ.
- `portable/` là bản chép độc lập plugin (`AGENTS.md` + `workflow/` + 5 file reference).
  Sửa luật nền là phải soi lại bản này, nếu không hai bản lệch nhau.
- User-level `~/.claude/skills/` đang có sẵn hơn 20 skill riêng của user (nhóm unity-*,
  ui-*, mem0-memory…). Chỗ này ghi được, và đúng là nơi user muốn lưu rule research thêm.

### Việc cũ dính tới request này

`docs/tdq/knowledge/2026-08-14-chong-no-ky-thuat.md` (cùng ngày, đã báo cáo xong) đề xuất
6 cơ chế M1–M6 chống nợ kỹ thuật, khuyến nghị gói vừa (M1–M5), và **chưa cơ chế nào được
áp vào `skills/`**. M5 đã viết sẵn nguyên văn dòng luật nới `qc.md`, M6 là cổng trùng lặp
`jscpd` đã chạy thử thật. Request này nếu làm phần rule sau QC thì đụng đúng chỗ M5 đụng.
Phải chốt với user: nhập chung hay để hai đường riêng.

### Kiến thức từ research

Nguồn đầy đủ: `docs/tdq/research/2026-08-14-set-soul-workflow.md`.

- Mỗi ngôn ngữ có hai lớp tách biệt — style guide bằng văn bản và linter thực thi:
  C# (Coding Conventions + Roslyn, 8 category qua `.editorconfig`) · Python (PEP 8 + ruff) ·
  Go (Effective Go + golangci-lint) · Rust (không có "Core Guidelines", triết lý là để
  clippy/rustfmt thực thi) · C++ (Core Guidelines + clang-tidy `cppcoreguidelines-*`).
  TS/JS và HTML **chưa có nguồn xác thực** — còn thiếu một lượt search riêng.
- Khung đo nợ kỹ thuật thực dụng nhất là taxonomy Clean Code của SonarQube: 4 thuộc tính
  Consistent · Intentional · Adaptable · Responsible.
- Số liệu quan trọng nhất cho request này: đo trên 1.848 issue của code do LLM sinh
  (arXiv 2411.10656), **59,6% lỗi rơi vào Intentionality** — đặt tên mờ, code chết, logic
  hụt. Bộ rule nên dồn sức vào nhóm này thay vì trải đều.
- Trục chung mọi ngôn ngữ: cyclomatic ≤ 10 (gốc McCabe 1976) và cognitive ≤ 15 (≤ 25 cho
  họ C), cộng checklist OWASP Secure Coding (ngôn ngữ-trung lập). Ngưỡng này **không thống
  nhất giữa các tool** (ESLint mặc định 20, Microsoft CA1502 mặc định 25) nên phải tự chốt
  một mặc định và cho phép project ghi đè.
- Rule viết cho agent đọc phải cụ thể và verify được bằng lệnh. Rule định tính kiểu
  "improve codebase" nên đẩy sang config linter thay vì viết thành chữ. Đồng thuận mạnh về
  progressive disclosure 2–3 tầng, đúng cấu trúc `SKILL.md` + `references/` đang có.
- SOLID không có ngưỡng đo tự động — là nguyên tắc định tính, không nên thành rule cứng.

### Phạm vi đã chốt

- Mặt CHỌN: chống trôi bằng máy · bao phủ ngôn ngữ · cơ chế tự bổ sung ngôn ngữ mới ·
  chi phí context (đo token trước/sau).
- Mặt LOẠI: không có mặt nào bị loại — user chọn A B C D, bỏ option "chỉ cần chạy được".
- Bối cảnh: bản đầu phủ đủ 7 ngôn ngữ (C#, C++, Python, TS/JS, HTML, Go, Rust), ngôn ngữ
  ngoài danh sách do cơ chế research tự sinh khi gặp · thư viện gốc nằm trong plugin
  `skills/*/references/`, bản research thêm ghi ở user-level `~/.claude` · chạy linter sẵn
  có của máy, thiếu thì báo chứ không tự cài · vi phạm rule là CHẶN, chưa sửa xong thì
  không sang report.
- Mức đầu tư suy ra: đầy đủ — vì bộ rule chặn cổng report của MỌI request sau này và áp
  cho mọi project dùng harness, nên sai một dòng luật là hỏng dây chuyền.

### Chỗ research còn nợ

Ba khoảng trống, phải bù bằng một lượt search riêng ở phase build: (a) nguồn xác thực
ESLint/typescript-eslint và HTML; (b) URL chính thức C++ Core Guidelines; (c) mapping
CISQ/ISO 25010 sang phép đo cụ thể.

## Hỏi đáp

### Vòng scope — 2026-08-14 21:48

| # | Câu hỏi | Phương án | User chọn (nguyên văn) |
|---|---|---|---|
| 1 | Request bao quanh những mặt nào | A chống trôi bằng máy · B bao phủ ngôn ngữ · C cơ chế tự bổ sung · D chi phí context · E chỉ cần chạy được | `1abcd` |
| 2 | Bản đầu phủ bao nhiêu ngôn ngữ | A đủ 7 · B chỉ ngôn ngữ đang dùng · C tự gõ | `2a và những ngôn ngữ khác sẽ có cơ chế resreach tự sinh khi gặp` |
| 3 | Thư viện rule gốc đặt ở đâu | A trong plugin · B user-level · C cả hai · D tự gõ | `3a` |
| 4 | Kiểm rule sau QC bằng gì | A linter sẵn có · B tự cài khi thiếu · C checklist bằng mắt · D tự gõ | `4a` |
| 5 | Vi phạm rule xử ra sao | A chặn · B ghi nhận · C chặn nhóm Intentionality · D tự gõ | `5a` |

Yêu cầu bổ sung của user cùng lượt trả lời, nguyên văn:

> tôi muốn bổ sung là ở bước lập spec sẽ có câu hỏi hỏi người dùng có ưu tiên chống nợ
> kĩ thuật và clean code không (giải thích sẽ có cơ chế tổ chức clean code và scaner, fix
> ở cuối request )

Nghĩa là thêm một câu hỏi vào phase `spec`: hỏi user có bật cơ chế clean code hay không,
kèm lời giải thích rằng bật thì cuối request sẽ có bước scan và fix. Câu hỏi chưa trả lời
từ khối trước — gộp M1–M5 hay để riêng — hỏi lại ở vòng chi tiết.

### Vòng chi tiết — 2026-08-14 21:58

| # | Câu hỏi | Phương án | User chọn (nguyên văn) |
|---|---|---|---|
| 1 | Chọn "không bật" ở câu hỏi spec thì xử ra sao | A bỏ hẳn · B scan nhưng ghi nhận · C chặn nhóm Intentionality · D tự gõ | `1A không scan, fix ở cuôi request nhưng vãn cố gắng tổ chức clean code theo đúng ngôn ngữ, tình huống` |
| 2 | Bộ scan chạy bằng gì | A script mới · B luật bằng chữ · C script chỉ gợi ý lệnh · D tự gõ | `2A` |
| 3 | "Áp ngược cho bản cũ" nghĩa là gì | A rà soát 28 file ngay · B chỉ từ nay · C test tự động · D tự gõ | `3A` |
| 4 | Ghi rule ngôn ngữ mới vào `~/.claude` kiểu nào | A trình nháp rồi duyệt · B ghi thẳng · C ghi repo trước · D tự gõ | `4A` |
| 5 | Gộp M1–M5 vào request này | A gộp · B để riêng · C chỉ gộp M5 · D tự gõ | `5A` |
| 6 | Bổ sung gì không | A không · B có | `6a` |

**Điểm quan trọng ở câu 1.** TẮT không có nghĩa là buông. TẮT chỉ bỏ bước scan và fix ở
cuối request; lúc implement agent VẪN phải tổ chức code theo đúng rule của ngôn ngữ và
tình huống. Nghĩa là thư viện rule có hai vai: vai đọc lúc viết code (luôn có hiệu lực) và
vai kiểm lúc QC (chỉ khi BẬT).

### Góp ý ở cổng spec — 2026-08-14 22:04

> bổ sung thêm vào soul và mọi tính năng, rule từ nay về sau đều luôn phải tổ chức đủ chi
> tiết, đầy đủ để mà dù là model cao như opus hoặc model cấp thấp như haiku đều có thể dễ
> dàng tuân theo và thực hiển đầy đủ rule, behavior để có thể đem lại output clean và hoàn
> chỉnh nhất có thể

Thành nguyên tắc thứ tư của soul: viết luật cho model yếu nhất đọc được. Cụ thể hoá bằng
khuôn 3 mục bắt buộc (`## Khi nào áp dụng`, `## Làm gì`, `## Tự kiểm`), một rule lint mới
R9 bắt khuôn đó, và một phép nghiệm thu bằng agent chạy Haiku thật. Spec lên bản 1.1.

### Góp ý thứ hai ở cổng spec — 2026-08-14 22:07

> bắt buộc là soul sẽ áp dụng cho mọi thứ trong workflow kể cải brief này và tất cả những
> breif về sau nha, hãy check đã có chưa?

Đã kiểm: bản 1.1 CHƯA có. Bản 1.1 chỉ áp soul cho file luật trong `skills/` (soul.md, thư
viện rule, R9 soi đúng hai chỗ đó); brief, spec, plan, qc, report đứng ngoài hoàn toàn.
Bổ sung ở spec 1.2: dòng `Soul:` cố định trong 5 khuôn tài liệu, cộng một test soi theo
`active_request` của `state.json` để mọi request sau — và chính brief này — đều phải có.

### Quyết định đã chốt

- Soul là một file riêng `skills/tdq-conventions/references/soul.md`, không nhét vào
  `SKILL.md`. Lý do: SKILL.md là tầng luôn nạp, mà soul là văn bản đọc khi phân xử. Chỉ
  thêm một dòng trỏ ở `## 11. Chất lượng`.
- Thư viện rule đặt ở `skills/tdq-build/references/rules/`. Lý do: rule dùng ở hai chỗ —
  lúc implement và lúc QC — cả hai đều thuộc skill `tdq-build`.
- Ba tầng nạp: `index.md` (bảng ngôn ngữ, mỏng) → `chung.md` cộng file ngôn ngữ đang đụng
  (chỉ nạp file khớp) → nguồn gốc ngoài mạng (chỉ khi cần trích).
- Bộ rule dồn sức vào nhóm Intentionality vì đó là 59,6% lỗi của code do LLM sinh.
- Ngưỡng mặc định chốt theo SonarQube: cyclomatic ≤ 10, cognitive ≤ 15 (≤ 25 cho họ C).
  Project ghi đè được bằng file cấu hình riêng.
- Rule ngôn ngữ mới lưu thành skill user-level `~/.claude/skills/tdq-rules/` (có
  `SKILL.md` cộng `references/<ngôn-ngữ>.md`). Lý do chọn dạng skill thay vì thư mục trần:
  thư mục nằm dưới `~/.claude/skills/` mà thiếu `SKILL.md` sẽ thành skill hỏng.
- Bản `portable/` lượt này chỉ nhận soul và dòng luật QC, KHÔNG chép thư viện rule. Lý do:
  chép 10 file rule sang bản thứ hai là nhân đôi chỗ phải bảo trì; để request riêng.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web (bù 3 khoảng trống) | CÓ | TS/JS, HTML, C++ chưa có URL xác thực mà phải viết rule cho chúng |
| Interview | CÓ (xong) | hai vòng, không còn câu hỏi làm đổi kết quả |
| Spec + plan | CÓ | khung bất biến |
| Chia subagent lúc implement | HỎI user ở cổng mode | 10 file rule là việc song song được, để user quyết |
| QC độc lập bằng agent `tdq-qc-tester` | CÓ | sửa luật nền, chạm cả 6 skill và bước QC |
| Review sâu bằng `tdq-reviewer` | BỎ | user chưa yêu cầu; QC độc lập đã có một lượt mắt ngoài |
| Đồng bộ `portable/` | CÓ, một phần | chỉ soul và dòng luật QC, không chép thư viện rule |

### Kiểm cổng

- Làm ra gì: 1 file soul · 10 file thư viện rule · 1 script scan · 1 file test · sửa 6 file
  luật sẵn có · 1 file rà soát luật cũ.
- Cần model/cài đặt: KHÔNG cài gì. Script chỉ gọi linter đã có sẵn trong máy; thiếu thì
  báo tên và lệnh cài, không tự cài.
- Phạm vi QC: có, gồm test tự động, `doc_lint`, chạy thử script scan trên chính repo này.
