# SPEC — Đo và đề án tối ưu context cho bộ workflow TDQ

Ngày: 2026-08-17 · Bản: 1.2 · Brief: ../brief/2026-08-17-2121-toi-uu-context-workflow.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- Mục tiêu: trả lời bằng số câu "có tối ưu được context của bộ workflow TDQ không, và
  tối ưu theo hướng nào", rồi giao lại một **thước đo** chạy được cùng một **bộ test
  hành vi** khoá đủ luật hiện có, để request tối ưu sau có căn cứ chấm trước-sau.
- Trong phạm vi:
  - Thước đo token: script đếm token thật cho từng skill, từng reference, từng phase.
  - Bộ test hành vi: trích mọi luật cứng của bộ skill thành checklist máy kiểm được, và
    test khoá lại — mất một luật là test đỏ.
  - Báo cáo đề án: **bốn** hướng tối ưu, lợi ích ước tính bằng số, rủi ro, thứ tự nên làm.
  - Đối chiếu ba bản `skills/`, `portable_claude/`, `portable_codex/` xem có lệch không.
  - **Hướng D — khối mô tả skill trong system prompt** (bổ sung theo câu hỏi vòng 3 của
    user): đo token mô tả của mọi skill ĐANG BẬT, phân theo mục (workflow · code ·
    design · web · dữ liệu · game engine · khác), và giao một file cấu hình
    `skillOverrides` đề xuất cho repo này kèm số tiết kiệm đo được.
  - **Hướng E — kho tìm skill + router** (bổ sung theo câu hỏi vòng 4): dựng NGUYÊN MẪU
    kho tra cứu tên+mô tả skill (BM25, offline), và **đo tỉ lệ trúng** trên một bộ prompt
    mẫu. Mục tiêu của request này là con số tỉ lệ trúng, không phải triển khai router vào
    luồng thật.
- NGOÀI phạm vi (chép từ brief `### Phạm vi đã chốt`, cộng chốt của câu 6):
  - **Sửa file skill.** Request này KHÔNG dịch, KHÔNG cắt, KHÔNG gộp một dòng skill nào.
  - Bảo mật · trải nghiệm người dùng cuối · an toàn dữ liệu · hiệu năng runtime của script.
  - Đổi hook, đổi state schema, đổi luồng phase.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã xong) | cần số về tokenizer và bằng chứng chính thức về progressive disclosure |
| Vòng scope | CÓ (đã xong) | request gọi tên cả một hệ thống, nhiều mặt chưa nói |
| Interview chi tiết | CÓ (đã xong, 2 vòng) | hai chỗ mơ hồ về phạm vi và cách đo |
| Spec + plan | CÓ | lane full, đối tượng là bộ luật gốc |
| Implement | CÓ | dựng thước đo và bộ test hành vi — KHÔNG sửa skill |
| QC độc lập (agent) | CÓ | request trước cho thấy agent QC bắt được chỗ số bị thổi phồng |
| Review sâu (`tdq-reviewer`) | BỎ | user chưa yêu cầu; QC độc lập đã phủ |
| Chia subagent lúc build | BỎ | phần lớn task cùng đụng hai file mới, chuỗi phụ thuộc thẳng |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Thước đo token cho bộ skill | `scripts/skill_tokens.py` | `python3 scripts/skill_tokens.py --theo-phase` in bảng token từng phase, exit 0 |
| 2 | Bộ luật trích ra từ skill | `docs/tdq/audit/luat-hien-co.md` | mỗi luật một dòng, có mã `L###` và trỏ file:dòng nguồn |
| 3 | Test khoá luật | `tests/test_luat_skill.py` | xoá thử một luật khỏi bản sao skill → test đỏ; nguyên bản → xanh |
| 4 | Báo cáo đề án | `docs/tdq/audit/de-an-toi-uu-context.md` | có bảng 3 hướng kèm token tiết kiệm ước tính, rủi ro, thứ tự làm |
| 5 | Đối chiếu 3 bản | mục trong đầu ra 4 | bảng liệt kê file lệch giữa `skills/`, `portable_claude/`, `portable_codex/` |
| 6 | Bản dịch thử để chốt hệ số | mục trong đầu ra 4 | dịch 1 file skill sang tiếng Anh, đo token thật trước/sau, ghi hệ số đo được |
| 7 | Đo mô tả skill đang bật, phân mục | `scripts/skill_tokens.py --mo-ta` | in bảng token mô tả theo nguồn + theo mục, tổng khớp số đếm skill của `skill_inventory.py` |
| 8 | Cấu hình `skillOverrides` đề xuất | `docs/tdq/audit/skill-overrides-de-xuat.json` | JSON hợp lệ, mỗi khoá là tên skill CÓ THẬT trong inventory, mỗi giá trị thuộc `name-only`/`user-invocable-only`/`off` |
| 9 | Đề án hướng D | mục trong đầu ra 4 | có bảng 3 kịch bản (giữ nguyên · `name-only` · `off`) kèm token còn lại, và mục nêu rõ giới hạn: `skillOverrides` là cấu hình tĩnh, không lắp được vector DB vào chính nó |
| 10 | Kho tra cứu skill | `docs/tdq/audit/skill-index.json` | mỗi bản ghi đủ 4 trường `ten`/`mo_ta`/`nguon`/`duong_dan`; số bản ghi bằng số skill `skill_inventory.py` đếm được |
| 11 | Nguyên mẫu router BM25 | `scripts/skill_router.py --tra "<câu>"` | in top-k skill kèm điểm, exit 0, chạy offline không cần API key |
| 12 | Bộ prompt mẫu + tỉ lệ trúng | `tests/test_skill_router.py` + mục trong đầu ra 4 | ≥ 20 prompt mẫu, mỗi prompt ghi sẵn skill ĐÚNG phải ra; báo cáo in tỉ lệ trúng top-1 và top-5 |
| 13 | Xác nhận `name-only` còn gọi được | mục trong đầu ra 4 | chạy thật một lượt, dán output; nếu KHÔNG gọi được thì ghi rõ và đổi kiến trúc đề xuất |
| 14 | Đề án hướng E — kiến trúc 3 tầng | mục trong đầu ra 4 | có bảng token 4 kiến trúc, tỉ lệ trúng đo được, và mục nêu rõ lỗ hổng "model phải nhớ đi tra" cùng cách bịt bằng hook `UserPromptSubmit` |

## 3. Cách tiếp cận & lý do

- Chọn: **đo trước, đề án sau, không đụng skill.** Dựng thước đo bằng
  `anthropic-tokenizer` chạy offline, trích luật thành checklist máy kiểm, rồi mới ước
  tính lợi ích từng hướng. Hệ số Việt/Anh chốt bằng một bản dịch thử THẬT của đúng một
  file, không suy từ tỉ lệ một câu.
- Vì: request trước cho thấy con số suy ra mà không đo thì bị agent QC bắt ngay. Ở đây
  chính tôi đã hụt một lần: `token_audit.py` xếp nhóm `Skill` chỉ 0,06% carry-cost, nhưng
  đo thẳng ra **61.061 token mỗi request lane full**. Không có thước đo riêng cho skill
  thì mọi kết luận tối ưu đều đứng trên cát.
- Đã loại: **vừa đo vừa sửa skill trong một request** — vì sửa xong mới có thước đo thì
  không còn số "trước" để so, và user đã chốt câu 6 là dừng ở đề án.
- Đã loại: **gọi `count_tokens` của Anthropic** — máy không có `ANTHROPIC_API_KEY`
  (đã kiểm, ba biến đều trống), user chọn hướng offline.
- Đã loại: **`tiktoken` hay heuristic ký tự/4** — research cho thấy sai 12–20%, tệ hơn
  với văn bản không phải tiếng Anh, tức sai đúng chỗ cần đo nhất.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-intake` | plugin:tdq-workflow | NỀN | skill khung đã chạy phase analyze |
| `tdq-spec` | plugin:tdq-workflow | NỀN | skill khung đang chạy phase này |
| `tdq-plan` | plugin:tdq-workflow | NỀN | viết plan cho request này |
| `tdq-build` | plugin:tdq-workflow | NỀN | thi hành implement, QC, report |
| `tdq-conventions` | plugin:tdq-workflow | DÙNG | vừa là luật thi hành, vừa là đối tượng bị trích luật ở đầu ra 2 |
| `tdq-qc-tester` | plugin:tdq-workflow (agent) | DÙNG | QC độc lập, chấm lại số trong báo cáo đề án |
| `mem0-memory` | plugin (mcp) | DÙNG | ghi một fact về hệ số token Việt/Anh đo được |
| Đã xét 278 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: `scripts/skill_tokens.py` in timestamp ISO + tên lệnh + tham
  số ra stderr, tắt bằng `TDQ_LOG=0` — giống mọi script TDQ khác.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo
  `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong
  `skills/tdq-build/references/rules/python.md`.
- **Cấm đoán số token.** Thiếu thư viện đếm token thì script phải lỗi, không được rơi về
  ước lượng ký tự chia bốn.
- Mọi luật trích ra ở đầu ra 2 phải trỏ được về `file:dòng` nguồn. Luật không trỏ được
  nguồn là luật bịa, không được đưa vào checklist.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ: `docs/kien-truc.md` chưa có trong repo này. Ràng buộc thật
sự của request: **không được sửa file trong `skills/`, `portable_claude/`,
`portable_codex/`** — đó là ranh giới do user chốt ở câu 6, và cũng là điều kiện để còn
số "trước" mà so.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| `anthropic-tokenizer` là vocab đời cũ, lệch với tokenizer Claude 5 | số tuyệt đối sai vài phần trăm | chỉ dùng để so TƯƠNG ĐỐI trước/sau bằng cùng một thước; ghi rõ sai số trong báo cáo |
| Gói `ctoc` research nhắc không tồn tại trên PyPI | phương án user chọn không chạy được nguyên văn | đã thay bằng `anthropic-tokenizer` 0.1.0, cùng ý đồ offline, đã thử cài được |
| Cài gói mới vào máy user | rác môi trường | cài vào venv riêng của repo (`.venv-tokens/`), thêm vào `.gitignore`, không đụng python hệ thống |
| Trích luật sót | test hành vi tưởng đủ mà hụt, request sau cắt nhầm | đếm chéo: số luật trích ra phải ≥ số dòng mệnh lệnh mà `doc_lint` đếm được; chênh phải giải trình từng dòng |
| Bản dịch thử ở đầu ra 6 làm lộ chuyện dịch tiếng Anh có hại | kết luận đổi chiều giữa chừng | đó là kết quả hợp lệ; báo cáo phải ghi cả chiều xấu, không giấu |
| `skillOverrides` tắt nhầm skill repo này vẫn cần | mất năng lực giữa chừng, phải mở phiên mới mới lấy lại | đề xuất mặc định là `name-only` (model còn thấy tên) chứ không `off`; chỉ `off` cho nhóm chắc chắn lạc mục; file đề xuất KHÔNG được tự áp vào settings — user tự bật |
| Sửa `~/.claude/settings.json` là đụng môi trường ngoài repo | ảnh hưởng mọi dự án khác của user | request này CHỈ sinh file đề xuất trong `docs/`; cấm ghi vào bất kỳ file settings nào |
| Chuỗi mô tả `skillOverrides` đọc từ binary có thể đổi ở bản Claude Code sau | đề án lỗi thời | báo cáo ghi rõ số phiên bản binary đã đọc, và cách đọc lại |
| Router BM25 tra TRƯỢT skill lẽ ra phải dùng | mất năng lực âm thầm — hại hơn tốn token | đầu ra 12 bắt buộc đo tỉ lệ trúng trên ≥ 20 prompt mẫu; tỉ lệ top-5 dưới 90% thì báo cáo phải khuyến nghị KHÔNG chuyển sang router |
| Nguyên mẫu router bị hiểu nhầm là đã triển khai | user bật nhầm rồi mất skill | `skill_router.py` KHÔNG được đăng ký vào hook nào trong request này; báo cáo ghi rõ "nguyên mẫu, chưa lắp" |
| Suy luận `name-only` vẫn gọi được chỉ dựa trên chuỗi trong binary | kiến trúc 3 tầng đứng trên giả định sai | đầu ra 13 bắt buộc chạy thật một lượt để xác nhận, không chấp nhận suy từ chuỗi |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Test suite không đỏ | `python3 -m pytest tests/ -q` | xanh, số test ≥ 874 |
| Q2 | Thước đo chạy được | `python3 scripts/skill_tokens.py --theo-phase` | exit 0, in bảng đủ 6 khối phase |
| Q3 | Cấm đoán token | gỡ thư viện khỏi venv rồi chạy lại | exit khác 0, stderr nêu cách cài, KHÔNG in bảng |
| Q4 | Luật trích có nguồn | `grep -c "^| L" docs/tdq/audit/luat-hien-co.md` và soi 5 dòng bất kỳ | mọi dòng có mã `L###` và `file:dòng` mở được |
| Q5 | Test khoá luật thật sự khoá | xoá một luật khỏi bản sao skill trong thư mục tạm rồi chạy test | test đỏ đúng luật đó; nguyên bản thì xanh |
| Q6 | Ba bản không lệch ngầm | mục đối chiếu trong báo cáo | mọi file lệch đều liệt kê, hoặc ghi rõ "không lệch" |
| Q7 | Hệ số Việt/Anh là số ĐO | mục bản dịch thử trong báo cáo | có token trước, token sau, tên file đã dịch |
| Q8 | Báo cáo trả lời đúng câu user hỏi | đọc `de-an-toi-uu-context.md` | có kết luận "tối ưu được / không" kèm số, và thứ tự làm ba hướng |
| Q9 | Không sửa skill | `git status --short skills portable_claude portable_codex` | rỗng |
| Q10 | Log service | chạy 1 lệnh có và không `TDQ_LOG=0` | stderr có dòng ISO khi bật, rỗng khi tắt |
| Q11 | doc_lint | `python3 scripts/doc_lint.py` trên 2 file audit | exit 0 |
| Q12 | Đo mô tả skill khớp inventory | `python3 scripts/skill_tokens.py --mo-ta` so với `python3 scripts/skill_inventory.py --tat-ca` | số skill hai bên bằng nhau; bảng có cột token và cột mục |
| Q13 | File `skillOverrides` đề xuất hợp lệ | `python3 -c "import json;json.load(open(...))"` + đối chiếu tên với inventory | JSON parse được; 100% khoá có trong inventory; 100% giá trị thuộc 3 mức hợp lệ |
| Q14 | Không đụng settings của user | `git status --short` + `md5` của `~/.claude/settings.json` trước/sau | md5 không đổi; không file settings nào nằm trong diff |
| Q15 | Kho tra cứu khớp inventory | `python3 -c` đếm bản ghi `skill-index.json` so với `skill_inventory.py --tat-ca` | bằng nhau; mọi `duong_dan` mở được |
| Q16 | Router chạy offline | ngắt mạng (hoặc `unset` mọi biến API key) rồi `skill_router.py --tra "sửa lỗi unity shader"` | exit 0, in top-k, không gọi mạng |
| Q17 | Tỉ lệ trúng có số | `python3 -m pytest tests/test_skill_router.py -q` + mục trong báo cáo | ≥ 20 prompt mẫu; báo cáo in cả top-1 và top-5 bằng số thật, không làm tròn giấu |
| Q18 | Router chưa lắp vào luồng | `grep -r "skill_router" .claude/settings*.json hooks/ 2>/dev/null` | không khớp dòng nào |
| Q19 | QC độc lập | agent `tdq-qc-tester` chạy lại Q1–Q18 | có verdict kèm output agent tự chạy |

DoD: 19 hạng mục trên PASS · mọi task trong plan tick `[x]` · `skills/` và hai bản
portable không đổi một byte · file settings của user không đổi một byte · router chưa
lắp vào hook nào · báo cáo đề án có đủ **năm** hướng kèm số tiết kiệm đo được và thứ tự
nên làm.

## 7. Câu hỏi còn mở

(rỗng)
