# BRIEF — Cắt token thừa trong TDQ workflow

Ngày: 2026-08-09 · Lane: full · Slug: 2026-08-09-cat-token-thua-workflow

## Nguyên văn

Yêu cầu user (3 lượt, gộp lại):

> bây giờ tôi muôn bạn recheck tổng thể claude code instruction và cả bộ workflow xem có gì
> đã là điểm nghẽn có thể gây tốn time và tốn token implemenr có thể tối ưu và vẫn đảm bảo
> chất lượng output tốt không. Đồng thời check xem claude code soul và workflow có đang đi
> theo hướng đơn giản nhất có thể, không trình bày quá dư thừa, tập trung vào điểm chính,
> không code cũng như làm những step không cần thiết. Có check và suy nghĩ kĩ trước khi đưa
> step và spec vào impllement chưa? ngoài ra liệu có còn giữ là khi task có thêm xóa sửa thì
> luôn trình bày plan báo cáo chờ review trước khi làm không? hãy check và trình bày báo cáo lại cho tôi

> tôi muốn biết điểm nghẽn nào có ích và có giá trị trong quá trình làm vệc thì giữ chỉ list
> ra những điểm nghẽn gây ra tốn kém mà hiệu quả thấp hoặc không có, hãy check lại và báo cáo lại cho tôi

> B  (= mở request lane full làm cả C1–C6)

**Cách hiểu đầu tiên.**
- Mục tiêu: cắt 6 điểm nghẽn C1–C6 đã chốt ở báo cáo audit, giảm token/turn của lane full
  mà KHÔNG đụng tới bất kỳ gate duyệt nào.
- Phạm vi đoán: sửa file hướng dẫn trong `skills/`, `scripts/doc_lint.py`,
  `scripts/tdq_state.py` (hằng `PHASE_TABLE`), và `~/.claude/CLAUDE.md`.
- Chỗ chưa rõ: xem mục `## Hỏi đáp`.

### Sáu điểm nghẽn phải cắt (C1–C6)

| Mã | Chỗ nghẽn | Chi phí đo được | File dự kiến đụng |
|---|---|---|---|
| C1 | Bảng phán quyết toàn bộ 242 skill trong brief, chép nguyên sang spec §3b | `skill_inventory.py` in 242 dòng / 22.154 ký tự (~5,5k token); bảng bị ghi 2 lần | `skills/tdq-intake/references/skill-inventory.md`, `skills/tdq-spec/references/spec-template.md` |
| C2 | Bảng `## Năng lực → task` trong plan = bản chép lần 3 | Viết lại toàn bộ dòng DÙNG lần thứ ba | `skills/tdq-plan/references/plan-template.md` |
| C3 | Phase `Log & test bắt buộc` + spec §4 "log service" ép vào MỌI plan | 1–2 task rác mỗi plan, kể cả việc không có runtime | `spec-template.md`, `plan-template.md` |
| C4 | `phases.md` mục chi tiết từng phase (dòng 33–90) lặp SKILL.md | ~58 dòng lặp mỗi lần đọc file | `scripts/tdq_state.py` (`PHASE_TABLE` / `phases-doc`), `skills/tdq-conventions/references/phases.md` |
| C5 | Câu bắt buộc "Bạn muốn bổ sung thêm gì không?" cuối mỗi vòng interview quick | +1 round-trip user mỗi vòng, kể cả vòng không có câu hỏi | `scripts/tdq_state.py` (`PHASE_TABLE` quick), `skills/tdq-intake/references/interview.md` |
| C6 | `CLAUDE.md` chép lại chi tiết spec/plan/QC của `tdq-conventions` | 2 nguồn sự thật, đã lệch thật (mục external mode) | `~/.claude/CLAUDE.md` |

### Ranh giới — KHÔNG đụng (đã xác định là có giá trị)

2 gate duyệt lane full + 1 gate quick · trường `Ra`/`Kiểm`/`Không dùng cho` của khối hợp
đồng · chép `### Lộ trình` brief → spec §1b · QC = đúng số dòng DoD · trần 3 vòng fix ·
`doc_lint` R4 · hook `[TDQ:NEXT] --brief` · `tdq_finish.py`.

## Hiểu & kiến thức

### Năng lực dùng được

Phân vân → DÙNG. Kiểm kê chạy ngày 2026-08-09: 242 skill trên đĩa
(`scripts/skill_inventory.py`) + ~30 skill built-in trong context. Áp luật gom của
`skill-inventory.md` (trên 20 skill): giữ riêng dòng DÙNG/NỀN, gom dòng KHÔNG theo lý do.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake, tdq-spec, tdq-plan, tdq-build, tdq-conventions, tdq-status | project | NỀN | chính workflow đang chạy — cũng là đối tượng bị sửa |
| graphify | user | DÙNG | chạy `graphify extract . --code-only` cuối turn có đổi code (`tdq_finish.py` đã gọi sẵn) |
| mem0-memory | user | DÙNG | chốt quyết định lâu dài về hình dạng workflow sau khi cắt |
| 240 skill còn lại (figma-*, canva-*, mongodb-*, cloudflare-*, postman-*, hyperframes-*, huggingface-*, adobe-*, qt-*, astronomer-*, unreal-*, datarobot-*, base44-*, tavily-*, firecrawl-*, chrome-devtools-*, playwright, dataviz, frontend-design, artifact-*, …) | user/plugin/built-in | KHÔNG | khác lĩnh vực — việc này chỉ sửa file markdown và 2 script Python nội bộ |

### Đọc code — hiện trạng đã xác minh

- `doc_lint.py` R8 (dòng 251) **chỉ kiểm tính hợp lệ của các dòng CÓ trong bảng §3b**,
  không đòi bảng phải đủ 242 skill → C1 làm được thuần bằng sửa markdown, không đụng code.
- `doc_lint.py pair()` (dòng 306) đối chiếu dòng `DÙNG` ở spec §3b với khối `- Dùng:`
  trong plan; **không đọc** bảng `## Năng lực → task` → C2 cũng thuần markdown.
- `CONTRACT_FIELDS` (dòng 226) = `Nạp, Để, Ra, Kiểm, Không dùng cho`. Bỏ trường `Nạp`
  buộc phải sửa hằng này + `plan-template.md`.
- `phases.md` là file **tự sinh** từ `PHASE_TABLE` bằng `tdq_state.py phases-doc`; sửa tay
  bị cấm → C4 và C5 phải sửa trong `tdq_state.py` rồi sinh lại file.
- `~/.claude/CLAUDE.md` nằm **ngoài repo này** (61 dòng, global cho mọi project).

### Research web

BỎ. Việc thuần nội bộ: chỉ sửa file markdown và script Python của chính repo này, không có
ẩn số về thư viện/API/phiên bản bên ngoài.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | thuần nội bộ, không có ẩn số bên ngoài (xem trên) |
| Interview | CÓ | 4 câu còn mở ở mục Hỏi đáp, đều làm đổi kết quả |
| Spec + plan (2 gate duyệt) | CÓ | khung bất biến, và chính user yêu cầu giữ gate |
| Chia subagent | BỎ (đề xuất) | 6 hạng mục đụng chồng lên 4 file chung (`spec-template`, `plan-template`, `tdq_state.py`) — song song sẽ xung đột |
| QC độc lập (agent `tdq-qc-tester`) | BỎ | DoD đều là lệnh chạy được (`doc_lint`, `pytest`, `phases-doc` diff), không cần góc nhìn thứ hai |
| Review sâu (agent `tdq-reviewer`) | BỎ | phạm vi nhỏ và đã đọc hết file liên quan; user yêu cầu thì bật lại |

## Hỏi đáp

Vòng 1 — hỏi 2026-08-09 00:51, user trả lời nguyên văn `1A 2A 3A 4A`.

| # | Câu hỏi | Phương án đã chốt |
|---|---|---|
| 1 | C1 bỏ bảng 242 dòng thì thay bằng gì? | A — vẫn CHẠY `skill_inventory.py` để rà một lượt, nhưng chỉ GHI dòng DÙNG và NỀN, cộng 1 dòng tổng `Đã xét N skill khác — khác lĩnh vực` |
| 2 | C6 cắt `CLAUDE.md` tới đâu? | A — cắt phần chi tiết trùng conventions (git, working log, research, chi tiết spec/plan/QC), thay bằng 1 dòng trỏ về `tdq-conventions`; GIỮ mục 1, luật "mọi prompt mới → tdq-intake", mục 8, mục 9 |
| 3 | Trường `Nạp` trong hợp đồng skill? | A — cắt, hợp đồng còn 5 trường `Dùng/Để/Ra/Kiểm/Không dùng cho`; phải sửa `CONTRACT_FIELDS` trong `doc_lint.py` |
| 4 | Tương thích ngược spec/plan cũ? | A — không sửa file cũ, chỉ áp luật mới từ request này trở đi |

Giả định đã nêu và user không phản đối:

- C3: "có runtime" = plan có ít nhất một task tạo hoặc sửa file mã nguồn chạy được.
  Không có → spec §4 và phase `Log & test` ghi đúng 1 dòng lý do bỏ.
- C5: câu "Bạn muốn bổ sung thêm gì không?" chỉ hỏi khi vòng interview đó có ≥ 1 câu hỏi.
- Mode thực thi sẽ ĐỀ XUẤT `main`; user chốt lúc duyệt plan.

Phát hiện thêm khi viết spec: `docs/claude-md-mau.md` (3.463 byte) và `~/.claude/CLAUDE.md`
(4.243 byte) đã LỆCH nhau — xác nhận đúng vấn đề 2 nguồn sự thật của C6.
