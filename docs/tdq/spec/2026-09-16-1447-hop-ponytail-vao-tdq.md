# SPEC — Hợp lối code Ponytail vào TDQ-Workflow

Ngày: 2026-09-16 · Bản: 1.0 · Brief: ../brief/2026-09-16-1447-hop-ponytail-vao-tdq.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- **Mục tiêu:** giao ra một *phương án tích hợp* đưa lối code chống-xây-thừa của Ponytail thành
  hướng code chính của TDQ-Workflow ở đủ ba tầng skill / rule / hook, gồm 5 luồng tính năng, mỗi
  luồng là một quyết định người dùng trả lời được có/không; cộng một *report* ≤ 50 dòng. Đo được:
  3 file đầu ra ở §2, mọi trích dẫn code kiểm được bằng máy, 0 bước sửa code thật.
- **Trong phạm vi:**
  - Thiết kế thân luật: Ponytail hoá thành một file luật đúng khuôn 3 mục của `soul.md:39-46`,
    hợp nhất vào tầng `rules/` đang có thay vì dựng tầng luật thứ hai.
  - Thiết kế trục mức gắt `muc_gat` 5 giá trị (`off|lite|full|ultra|review`), mặc định `full`.
  - Thiết kế hook thứ 6 `SubagentStart` để bộ luật tới được `tdq-implementer`.
  - Thiết kế đường xuất một-nguồn-chân-lý bằng cách mở rộng `scripts/build_portable.py`.
  - Hợp nhất hướng thất bại: nêu rõ chỗ nào fail-open, chỗ nào fail-closed.
  - Soạn **nguyên văn một câu** thay cho `chung.md:22`, trình riêng để người dùng duyệt.
  - Bản dự thảo thân luật viết sẵn, tiếng Anh, đúng khuôn, để request sau chép thẳng.
- **NGOÀI phạm vi:**
  - **Không mặt nào của vòng scope bị loại** — người dùng chọn `1abcdf`, tức chọn cả 5 mặt
    A+B+C+D+F. Mặt duy nhất bị bỏ là phương án E "chỉ cần chạy được, không cần bàn kiến trúc".
  - **Sửa code thật**: không chỉnh `hooks/`, `skills/`, `scripts/`, `tests/`, `soul.md`,
    `chung.md`, `clean-code.md` trong request này (người dùng chốt `4a`: dừng ở phương án).
  - Lệnh gom nợ kiểu `/ponytail-debt` và cơ chế comment `ponytail:` để vượt ngưỡng: loại, vì
    người dùng chốt `2a` — thang không được bác ngưỡng đo được, nên không cần cửa lách.
  - Đích xuất thứ tư trở đi (Gemini, Windsurf, Zed…): loại, chỉ 3 đích người dùng chọn.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | **BỎ** | Đã chạy xong ở analyze: `docs/tdq/research/2026-09-16-1447-hop-ponytail-vao-tdq.md`, 4 câu kèm nhãn mức tin cậy |
| Interview | **BỎ** | Đã chạy 2 vòng (scope + chi tiết), 8 câu, 0 câu treo; kiểm cổng ĐẠT cả 3 |
| `spec` | **CÓ** | Chính là "phương án đề xuất" người dùng yêu cầu |
| `plan` | **CÓ** | Plan **viết tài liệu**: mỗi task là một phần của phương án/report, DoD chấm trên tài liệu |
| `implement` | **CÓ** | "Implement" ở đây = viết 3 file `.md` ở §2; không sửa `hooks/`, `rules/`, `soul.md` |
| `qc` | **CÓ** | 9 hạng mục ở §6, mỗi dòng DoD một lệnh kiểm |
| QC độc lập (agent) | **BỎ** | §3 chọn trình kiểm bằng máy (so số dòng trích dẫn) — chặt hơn agent đọc bằng mắt |
| `report` | **CÓ** | ≤ 50 dòng, là đầu ra thứ hai người dùng nêu tên |
| Sửa code thật (luật/hook/test) | **BỎ khỏi request này** | Người dùng chốt `4a`; mở request riêng sau khi duyệt phương án |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Phương án tích hợp (tiếng Việt) — 5 luồng, mỗi luồng một quyết định có/không, kèm giá phải trả và thứ tự triển khai | `docs/tdq/knowledge/2026-09-16-1447-phuong-an-ponytail-tdq.md` | Có đủ 5 mục luồng đánh số; mỗi mục có dòng quyết định và dòng giá phải trả; có nguyên văn câu thay `chung.md:22` |
| 2 | Dự thảo thân luật (tiếng Anh, đúng khuôn 3 mục, sẵn sàng chép) | `docs/tdq/knowledge/2026-09-16-1447-du-thao-luat-ponytail.md` | Có đủ 3 mục bắt buộc + dòng `Soul:`; có ví dụ RIGHT/WRONG; không chứa ký tự tiếng Việt có dấu |
| 3 | Report cuối | `docs/tdq/reports/2026-09-16-1447-hop-ponytail-vao-tdq.md` | ≤ 50 dòng; nêu được kết luận mà không cần đọc hai file kia |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| `phuong-an` | `docs/tdq/knowledge/2026-09-16-1447-phuong-an-ponytail-tdq.md` | không | 1 |
| `du-thao-luat` | `docs/tdq/knowledge/2026-09-16-1447-du-thao-luat-ponytail.md` | không | 2 |
| `bao-cao` | `docs/tdq/reports/2026-09-16-1447-hop-ponytail-vao-tdq.md` | `phuong-an`, `du-thao-luat` | 3 |

Ba module, ba đường dẫn rời nhau, không đường nào khai hai lần.

**Vì sao KHÔNG cắt thành 5 module theo 5 luồng:** cắt thế sẽ có 5 file cùng phải đọc mới hiểu một
phương án, và bậc 1 của thang Ponytail ("việc này có cần tồn tại không") trả lời là không. Chính
bộ luật đang được đề xuất phủ quyết cách cắt đó — spec này tuân nó luôn, không chỉ nói về nó.

## 3. Cách tiếp cận & lý do

- **Chọn: HỢP NHẤT vào tầng luật đang có, không dựng tầng luật thứ hai.** TDQ đã có 5 tầng luật
  (`soul.md` → `clean-code.md` → `rules/chung.md` → `rules/index.md` → 7 file ngôn ngữ). Thân luật
  Ponytail viết lại theo khuôn 3 mục của `soul.md:39-46` rồi hợp vào tầng `rules/`, tầng hook chỉ
  chở *con trỏ* và *đổi mức gắt*.
- **Vì:**
  - Trần hook đã đo: `session_start.py:18-19` = 12 dòng / 600 ký tự; `prompt_context.py:28-29`
    = 3 dòng / 240 ký tự. 121 dòng SKILL.md của Ponytail không nhét vào 240 ký tự → tầng hook
    *không thể* chở thân luật, dù Ponytail đang làm đúng thế.
  - `soul.md:99-102`: luật tier 1–2 phải nằm trong chỗ nạp mỗi lượt, chỉ tier 3 mới đẩy ra file
    reference. Luật chống-xây-thừa sửa tính đúng của đầu ra → tier 1.
  - Docs Claude Code nói skill *chỉ* nạp khi được gọi hoặc khi model tự thấy liên quan, và không
    có field `alwaysApply`; rule không có `paths` thì nạp mỗi phiên ngang `CLAUDE.md`, rule **có**
    `paths:` glob thì chỉ nạp khi chạm file khớp — đúng khuôn "luật code chỉ bật khi đang viết
    code" [XÁC THỰC, research §Câu 3].
  - Dựng tầng luật thứ hai song song chính là kiểu xây thừa mà bộ luật này cấm; và docs nói rule
    mâu thuẫn thì Claude "pick one arbitrarily" [XÁC THỰC], nên hai tầng sẽ tự phá nhau.
- **Đã loại:**
  - *Bê nguyên 121 dòng SKILL.md vào làm skill thứ 9* — vì khuôn 3 mục của `soul.md:39-46` đang
    được bộ test của repo ép chứ không phải khuyến nghị, thiếu khuôn là test đỏ; và vì skill không
    luôn-bật nên luật sẽ vắng mặt đúng lúc cần nhất.
  - *Bơm thân luật qua hook mỗi lượt như Ponytail* — vì hai trần ký tự ở trên, và vì nội dung dài
    bị đẩy ra file tạm rồi model không đọc [BÊN-THỨ-BA, issue #51537/#65385 — không có nguồn
    chính thức, nên phương án không được dựa vào con số này mà chỉ dùng nó làm cảnh báo].
  - *Chặn sub-agent bằng `PreToolUse` matcher `Agent`* — vì `PreToolUse(Agent)` không fire
    [BÊN-THỨ-BA, issue #69545]; và `SubagentStart` là *context only*, `decision:"block"` bị bỏ
    qua [XÁC THỰC]. Nên hook thứ 6 là *lời nhắc*, không phải *cổng chặn* — phương án phải nói
    đúng thế, không được hứa quá.
  - *Viết script sinh bản đa nền tảng mới* — vì `scripts/build_portable.py` đã sinh sẵn
    `portable_claude/` (`:11,285`) và `portable_codex/` kèm `AGENTS.md` (`:17,618,681`); chỉ thiếu
    đích Cursor. Viết mới là xây thừa.
  - *Copy tay 7 bản kèm script canh trôi như Ponytail* — vì chính
    `scripts/check-rule-copies.js:77` của Ponytail tự chú thích `// ponytail: canary, not full
    equality`, tức chỉ bắt được trôi chứ không ngăn được trôi.
  - *Sửa `soul.md:34-37` cho YAGNI thắng ngưỡng* — người dùng chốt `2a`: ngưỡng là sàn, thang chỉ
    chọn giữa các phương án đã đạt sàn.
  - *Viết lại dòng SRP `clean-code.md:55`* — người dùng chốt `3a`: chỉ thêm thứ tự hai lượt.

## 3b. Năng lực & công cụ

Chép từ brief mục `### Năng lực dùng được`. Phân vân → DÙNG.

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| `tdq-intake` | plugin:tdq-workflow | NỀN | Khung đang chạy — đã sinh brief, chạy B0/B1/B2, 2 vòng interview, kiểm cổng |
| `tdq-spec` | plugin:tdq-workflow | NỀN | Đang sinh chính file này |
| `tdq-plan` | plugin:tdq-workflow | DÙNG | Sinh plan viết tài liệu cho 3 đầu ra §2 |
| `tdq-build` | plugin:tdq-workflow | DÙNG | Viết 3 file đầu ra §2, chạy QC §6, viết report |
| `tdq-conventions` | plugin:tdq-workflow | DÙNG | Nguồn khuôn luật (`soul.md`, `clean-code.md`, `reminder-codes.md`) mà đầu ra 1 và 2 phải bám |
| `tdq-lsp-setup` | plugin:tdq-workflow | DÙNG | Đã chạy kiểm 7 bậc + kiểm hiệu ứng ở bước 1b; còn dùng để tra ký hiệu khi kiểm trích dẫn |
| `tdq-reviewer` | plugin:tdq-workflow | KHÔNG | spec §3 đã chọn cách khác tốt hơn — trình kiểm bằng máy so từng số dòng trích dẫn, chặt hơn agent đọc bằng mắt |
| Đã xét 3 skill khác | user/plugin | KHÔNG | khác lĩnh vực — chỉ đọc trạng thái hoặc truy vấn đồ thị, không liên quan tầng luật |

## 4. Yêu cầu bắt buộc

- **Log service: BỎ** — request này không có runtime, cả 3 đầu ra đều là file `.md`, không có
  task nào tạo hay sửa file mã nguồn chạy được.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- **Mọi khẳng định về code phải kèm `đường-dẫn:dòng` tồn tại thật** và kiểm được bằng máy (mở
  file, so số dòng trích với số dòng thật) — đúng trình kiểm đã dùng ở request
  `2026-09-16-1129-phan-tich-repo-ponytail`, khi đó bắt được 13/37 trích dẫn sai.
- **Mọi khẳng định về cơ chế Claude Code phải mang đúng một nhãn** `[XÁC THỰC]` (docs chính thức)
  / `[SUY-CODE]` (đọc từ file local, kèm `đường-dẫn:dòng`) / `[BÊN-THỨ-BA]` (issue tracker, blog).
- Đầu ra 2 (dự thảo thân luật) phải thoả đúng khuôn file luật mà bộ test của repo đang ép theo
  `soul.md:39-46`: đủ 3 mục bắt buộc + dòng `Soul:`, và viết tiếng Anh theo tầng ngôn ngữ đã chốt
  2026-08-22 ở `docs/kien-truc.md:51-55`.
- Câu thay `chung.md:22` phải xuất hiện **nguyên văn, một câu**, và được trình như một cổng duyệt
  RIÊNG — không gộp vào việc duyệt phương án, vì `docs/kien-truc.md:49-50` chốt rằng đổi luật gốc
  phải có người dùng duyệt.
- Phương án không được chứa bước nào sửa `hooks/`, `skills/`, `scripts/`, `tests/` trong request
  này; các bước đó chỉ được mô tả như nội dung của request tiếp theo.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ những dòng việc này chạm tới).
Lưu ý: `docs/kien-truc.md:3` ghi hồ sơ đang **NHÁP, chờ user chốt**, nên chỉ mục `## Đã chốt`
(có ngày) được coi là ràng buộc; phần mô tả tầng chỉ là gợi ý.

- `:49-50` — "2026-08-14: `skills/tdq-conventions/references/soul.md` là luật gốc đứng trên mọi
  luật; đổi soul phải có user duyệt." → việc này chạm ở chỗ đề xuất sửa `chung.md:22`, nên câu sửa
  đó đi qua một cổng duyệt riêng.
- `:51-55` — "2026-08-22: ngôn ngữ chia 3 tầng — luật trong `skills/` … viết TIẾNG ANH cố định;
  tài liệu sinh cho user … viết theo `doc_lang`." → việc này chạm ở đầu ra 2 (tiếng Anh) so với
  đầu ra 1 và 3 (tiếng Việt).
- `:13` (mô tả tầng, mức gợi ý) — `portable_claude/`, `portable_codex/` là **SINH** bằng
  `scripts/build_portable.py`, không sửa tay. → phương án cho mặt B phải đi qua script đó, không
  được đề xuất copy tay.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Con số "vượt ~10.000 ký tự thì model không đọc" chỉ có nguồn issue tracker, không có trong docs | Nếu phương án dựa vào nó mà nó sai, cả lập luận "luật dài = luật không tồn tại" sụp | Gắn nhãn `[BÊN-THỨ-BA]`; phương án chỉ dùng nó làm cảnh báo, và đặt một task *tự benchmark* vào request sau, không vào request này |
| `SubagentStart` là context-only, không chặn được gì | Phương án dễ bị đọc thành "đã có cổng gác sub-agent" — hứa quá | Đầu ra 1 phải có một câu nói thẳng: hook thứ 6 là lời nhắc, cổng chặn duy nhất vẫn là `edit_gate.py`/`bash_gate.py`/`stop_gate.py` |
| Mở `reminder-codes.md:13` "danh sách 5 mã đóng" | Mất một bất biến đang được giữ, mở đường cho mã thứ 7, 8 | Mặc định **không** mã mới: hook thứ 6 nhắc qua mã sẵn có. Chỉ đề xuất mở nếu chứng minh được không mã nào hiện có chở được việc, và khi đó là một quyết định có/không riêng |
| Người dùng chỉ nhận một phần trong 5 luồng | Phương án viết dính nhau sẽ không dùng được từng phần | Mỗi luồng viết độc lập, có giá phải trả riêng, xếp theo thứ tự rẻ → đắt, và ghi rõ luồng nào phụ thuộc luồng nào |
| Mode `off` bị hiểu thành "Claude được tự hạ chất lượng" | Phá tier 1 của soul | Đầu ra 1 phải ghi: `muc_gat` mặc định `full`; `off` chỉ vào được bằng một yêu cầu tường minh của người dùng, không bao giờ do Claude suy luận; và không có cơ chế tự xuống mode |
| Khoá state mới đụng tên `implement_mode` | Hai trục khác nhau bị trộn, state hỏng | Dùng tên `muc_gat`; `implement_mode` tồn tại thật ở `scripts/tdq_state.py:186` kèm `MODE_LABELS`/`MODE_ALIASES` (`:56,65`) cho trục `main/subagent/codex` — phương án phải nêu cả hai để thấy rõ chúng rời nhau |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Ba đầu ra §2 tồn tại | Cả 3 đường dẫn ở §2 đều là file thật, không rỗng |
| Q2 | Phương án phủ đủ 5 luồng | Đầu ra 1 có đúng 5 mục luồng đánh số, mỗi mục có một dòng quyết định có/không và một dòng giá phải trả |
| Q3 | Mọi trích dẫn code kiểm được bằng máy | Số trích dẫn `đường-dẫn:dòng` sai = 0 khi mở từng file và so với số dòng thật |
| Q4 | Mọi khẳng định về cơ chế Claude Code có nhãn | Số khẳng định thiếu nhãn `[XÁC THỰC]`/`[SUY-CODE]`/`[BÊN-THỨ-BA]` = 0 |
| Q5 | Dự thảo thân luật đúng khuôn luật | Đầu ra 2 có đủ 3 mục bắt buộc + dòng `Soul:` + ít nhất một cặp ví dụ RIGHT/WRONG |
| Q6 | Dự thảo thân luật đúng tầng ngôn ngữ | Đầu ra 2 không chứa ký tự tiếng Việt có dấu |
| Q7 | Câu thay `chung.md:22` được trình riêng | Đầu ra 1 chứa nguyên văn câu đề xuất, gói trong một mục cổng duyệt riêng, và giữ được tính chất "chỉ người dùng tắt được" |
| Q8 | Request không sửa code thật | `hooks/`, `skills/`, `scripts/`, `tests/`, `docs/kien-truc.md` không có file nào bị đổi so với lúc mở nhánh |
| Q9 | Report đủ ngắn và tự đứng được | Đầu ra 3 ≤ 50 dòng và nêu được kết luận không cần đọc hai file kia |

**DoD** — tuyên bố xong khi **đủ cả 9**:

1. Ba file §2 tồn tại và không rỗng.
2. Đầu ra 1 có đúng 5 mục luồng, mỗi mục có dòng quyết định và dòng giá phải trả.
3. Số trích dẫn `đường-dẫn:dòng` sai bằng 0.
4. Số khẳng định về cơ chế Claude Code thiếu nhãn tin cậy bằng 0.
5. Đầu ra 2 có đủ 3 mục bắt buộc, dòng `Soul:`, và cặp ví dụ RIGHT/WRONG.
6. Đầu ra 2 không chứa ký tự tiếng Việt có dấu.
7. Đầu ra 1 chứa nguyên văn câu thay `chung.md:22` trong một mục cổng duyệt riêng.
8. Không file nào ngoài `docs/` bị đổi trong nhánh này.
9. Đầu ra 3 ≤ 50 dòng.

## 7. Câu hỏi còn mở

(Rỗng — 2 vòng interview đã đóng cả 8 câu, kiểm cổng ĐẠT cả 3.)
