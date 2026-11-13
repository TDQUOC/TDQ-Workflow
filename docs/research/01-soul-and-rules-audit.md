# Báo cáo Kiểm toán Phần 1: Linh hồn (Soul), Hệ thống Luật & Tương thích Rules Đa Host (Antigravity) của TDQ-Workflow

- ** Kho mã nguồn mục tiêu (Source Repo):** `C:\Users\admin\Documents\Projects\ForAgentCode\TDQ-Workflow` (phiên bản `.claude-plugin/plugin.json`: `0.97.0`, `README.md` badge đang trễ ở `0.89.0`)
- ** Bản cài plugin Antigravity trên máy (Installed AGY Bundle):** `C:\Users\admin\.gemini\config\plugins\tdq-workflow` (phiên bản `plugin.json`: `0.74.0`, trạng thái trong `C:\Users\admin\.gemini\config\config.json`: `{"enabled": false}`)
- ** Ground-truth Antigravity đối chiếu:**
  - `C:\Users\admin\.gemini\antigravity\builtin\skills\agy-customizations\SKILL.md` (106 dòng)
  - `C:\Users\admin\.gemini\antigravity\builtin\skills\agy-customizations\docs\rules.md` (40 dòng)
  - `C:\Users\admin\.gemini\antigravity\builtin\skills\agy-customizations\docs\plugins.md` (112 dòng)
  - `C:\Users\admin\.gemini\antigravity\builtin\skills\agy-customizations\docs\hooks.md` (416 dòng)
  - `C:\Users\admin\.gemini\antigravity\builtin\skills\plugin\SKILL.md` (309 dòng)

---

## PHẦN 1. TOÀN BỘ LINH HỒN & TRIẾT LÝ CỐT LÕI ("LINH HỒN" CỦA TDQ-WORKFLOW)

### 1.1. Luật Tối thượng — `Soul` (`skills/tdq-conventions/references/soul.md`)

Tệp `skills/tdq-conventions/references/soul.md` (146 dòng, `8,296 bytes`, `2,310 tokens` theo `docs/tdq/token-budget.json:126-129`) là **hiến pháp tối cao** đứng trên mọi quy tắc khác của TDQ-Workflow. Sửa `soul.md` bắt buộc phải hỏi và được người dùng duyệt tường minh trước khi chạm vào tệp (`soul.md:9-10`).

#### A. Bốn Nguyên lý Nền tảng (`soul.md:23-67`)
1. **Principle 1 — Purpose (`soul.md:23-29`):**
   - *"Quality over quantity."* Mục tiêu duy nhất của quy trình là tạo ra sản phẩm thực tế chạy được (runnable MVP), dễ đọc, bền vững và đạt kỳ vọng người dùng; số lượng phase hay độ dài tài liệu chỉ là phương tiện.
   - **Chuẩn giọng điệu & trình bày bất biến** (`soul.md:28`, `skills/tdq-conventions/SKILL.md:203`, `scripts/tdq_setup.py:1142`): Luôn **`đơn giản, dễ hiểu, ngắn gọn`** nhưng **`trực quan, đầy đủ thông tin`** để mọi đối tượng đọc đều nắm được bản chất và bằng chứng.
2. **Principle 2 — Strict Priority Hierarchy & Tie-break Law (`soul.md:30-46`):**
   - Thứ bậc ưu tiên bất khả xâm phạm: **`chất lượng > runtime > context cost`** (`Quality > Runtime > Context Cost`).
   - **3 Tầng ưu tiên (3 Tiers):**
     - **Tier 1 — Quality (`soul.md:33-34`):** MVP chạy thật, test đi kèm chứng minh hành vi, đúng kỳ vọng người dùng, **zero undeclared technical debt** (không nợ kỹ thuật giấu giếm).
     - **Tier 2 — Runtime (`soul.md:35-36`):** Tổng số lượt gọi tool / bước thực thi; tránh vòng lặp thừa, tránh đọc đi đọc lại cùng một tệp.
     - **Tier 3 — Context Cost (`soul.md:37-38`):** Dung lượng token nạp vào cửa sổ ngữ cảnh; giữ file gọn nhưng **không bao giờ cắt giảm tới mức model phải đoán mò hoặc hỏi lại**.
   - **Luật phân xử xung đột 3 bước (`soul.md:40-46`):**
     1. Khác tầng → **Tầng cao hơn thắng tuyệt đối** (ví dụ: không được nén luật Tier 1/2 chỉ để vừa trần dòng Tier 3).
     2. Cùng tầng → **Luật nào kiểm chứng tự động được bằng một câu lệnh (command-checkable) thắng** luật phải đọc bằng mắt.
     3. Vẫn hòa → **Dừng hỏi người dùng** và ghi quyết định vào tài liệu request.
3. **Principle 3 — Write for the Weakest Model (`soul.md:47-55`):**
   - Mọi luật phải viết đủ tường minh cho **Haiku** (model yếu nhất còn hỗ trợ), không viết tắt kiểu ngầm hiểu cho Opus (`soul.md:49-50`).
   - Bắt buộc cấu trúc 3 mục cố định (được máy kiểm qua `scripts/doc_lint.py` **R9**, dòng `389-420`):
     1. `## When it applies` — điều kiện kích hoạt kiểm tra được (tên phase, đuôi tệp, sự kiện).
     2. `## What to do` — các bước mệnh lệnh đánh số `1, 2, 3...`.
     3. `## Self-check` — bảng kiểm tự rà trước khi chuyển bước + ví dụ đối chiếu `RIGHT` / `WRONG`.
4. **Principle 4 — Universal Scope & Canonical Header (`soul.md:56-67`):**
   - Áp dụng hồi tố lên toàn bộ `skills/`, `scripts/`, templates và mọi tài liệu request (`brief`, `spec`, `plan`, `qc`, `report`).
   - Dòng mở đầu chuẩn bắt buộc ngay dưới tiêu đề `#` của mọi tài liệu:
     `Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md` (`soul.md:62-66`).

#### B. Luật Đặt chỗ (`Placement Law` — `soul.md:113-116`)
- **Luật Tier 1 (Quality) và Tier 2 (Runtime)** ảnh hưởng trực tiếp tới hành động trong phase **BẮT BUỘC nằm ngay trong thân `SKILL.md`** để được nạp mỗi lượt.
- **Chỉ luật Tier 3** và bảng tra cứu/template mới được tách sang `references/`.
- Nếu `SKILL.md` chạm trần dòng (`SKILL_LINE_LIMITS` — một ràng buộc Tier 3), tác giả **phải nâng trần dòng trong `doc_lint.py`**, tuyệt đối không được cắt xén hay đẩy luật Tier 1/2 sang `references/` (`soul.md:115-116`).

#### C. Bốn Bất biến Clean Code (`Clean Code Invariants` — `soul.md:118-145`)
1. **Immutability by Default (`soul.md:122-125`):** Ưu tiên cấu trúc bất biến (`const`, `readonly`, `frozen`, `final`), hàm thuần trả bản sao mới thay vì mutate tham số đầu vào.
2. **Function Length Ceiling ≤ 50 dòng vật lý (`soul.md:126-128`):** Mọi hàm/phương thức không vượt quá **50 dòng vật lý**. Nếu phình to, tách helper thuần đặt tên theo mục đích.
3. **Strict Test-Driven Development (`soul.md:129-131`):** Viết test chứng minh lỗi/nhu cầu (Red) **trước** khi viết code thực thi (Green), sau đó mới refactor.
4. **Reflective Thought, Hypothesis & Chống "Autoregressive Attractor" (`soul.md:132-139`):**
   - Trước khi đọc file/chạy lệnh phải nêu giả thuyết ngắn; sau khi có kết quả phải tổng hợp lại.
   - **Cấm trượt cửa sổ đọc 30–50 dòng lặp đi lặp lại** (gây hiện tượng *autoregressive attractors* làm mù ngữ cảnh) — phải đọc trọn vẹn khối logic `100–300 dòng` (`soul.md:135-137`).
   - Khi debug phải truy nguyên gốc rễ (**5 Whys / Root Cause Analysis**), cấm vá triệu chứng bề mặt (`soul.md:138-139`).

---

### 1.2. Sáu Trụ cột Kiến trúc (`README.md:28-38`, `docs/tdq/models/master.model.json:49-86`)

| # | Trụ cột | Cơ chế cốt lõi & Tệp thực thi |
|---|---|---|
| **1** | **Tam giác Tìm kiếm 3 Tầng (3-Tier Search Triangle)** | Kết hợp `agent-lsp` (`mcp__lsp__*` — độ chính xác compiler, 0 false positive), `graphify` (đồ thị AST 2 bước / blast radius / kiến trúc), và `grep` (tìm chuỗi/token chính xác tốc độ mili-giây). Thực thi bởi `scripts/search_rules.py`, `hooks/scripts/search_gate.py`, `hooks/scripts/lsp_gate.py`, và quy định tại `skills/tdq-setup/references/uu-tien-tim-kiem.md:18-88`. |
| **2** | **Personal BA & Archify 2 Tầng (2-Tier Archify)** | Mọi cổng duyệt Spec/Plan đều đi kèm bản vẽ tương tác HTML (`bin/archify.mjs`) khóa `sha256` với markdown (`tdq-spec/SKILL.md:20-25`, `tdq-plan/SKILL.md:83-94`). Kiến trúc chia 2 tầng (`README.md:41-58`): **Tầng 2 (Request Diagram)** phục vụ duyệt nhanh từng tính năng; **Tầng 1 (Master Architecture Map)** tại `docs/architecture/` tự động đóng dấu `stale` khi source code đổi và đồng bộ lại ở phase `report`. |
| **3** | **Verify-by-Effect ("Không tin lời khai")** | Hook **không bao giờ đọc transcript chat** và **không tin dòng chữ `✓ [TDQ:...]` do agent tự in** (`skills/tdq-conventions/references/reminder-codes.md:9-11`, `hooks/scripts/stop_gate.py:4-8`). Mọi cổng chặn đối chiếu trực tiếp **hiệu ứng thật trên đĩa/git** qua sổ cái lượt `docs/tdq/.tdq-turn.jsonl` + snapshot SHA-256 đầu lượt (`prompt_context.py:257`, `stop_gate.py:54-118`). |
| **4** | **Kỷ luật Đỏ → Xanh (Red-Green) & Test theo Vùng chạm** | Bắt buộc chứng minh check/test **Đỏ (fail)** trước khi sửa code (`tdq-build/SKILL.md:46-47,117`). Giữa các task chỉ chạy `tdq_test.py vung-cham` (file chạm + vùng nổ lan AST từ Graphify) để giữ tốc độ; bộ full `tdq_test.py tron-bo` chốt ở phase `qc` (`tdq-build/SKILL.md:126-134`). Tick `[ ] → [~] → [x]` ngay khi xong từng task (`edit_gate.py` `STREAK_NGUONG = 3`, `stop_gate.py` `TDQ:TICK`). |
| **5** | **Đội Sub-Agent Cô lập trên Git Worktree** | `scripts/tdq_team.py` cắt sóng song song (waves) dựa trên khai báo vùng chạm `Chạm:` + kiểm va chạm kiểu TCAS (`README.md:36`, `tdq-build/SKILL.md:82-95`). Mỗi `tdq-implementer` chạy trong `.tdq-worktrees/<slug>-<task>` trên nhánh `tdq/<slug>/<task>`; `edit_gate.py:179-225` (`TDQ:TEAM`) khóa cứng không cho agent chạm ngoài danh sách file của task. |
| **6** | **Kiểm thử Thị giác 5 Lớp (5-Layer Visual Testing)** | Với task giao diện, tích hợp Chrome DevTools MCP kiểm 5 lớp (`README.md:37`, `skills/tdq-build/references/vision-test-loop.md`): (1) DOM & Accessibility tree, (2) Layout Desktop/Mobile, (3) Tương tác thật (hover/fill/click), (4) Zero lỗi Console & Network, (5) CSS Cascade. |

---

### 1.3. Quy trình Spec-Driven 3 Làn, Cổng Duyệt Tự nhiên Không Popup & Chống Ăn bớt / Ảo giác

1. **Ba Làn Thực thi (`skills/tdq-intake/SKILL.md:17-148`, `skills/tdq-conventions/references/phases.md:1-37`):**
   - **Tier `nhỏ` (Trivial — 0 state, 0 tài liệu):** Chỉ mở khi thỏa **đồng thời 4 điều kiện** (`tdq-intake/SKILL.md:64-69`): `≤ 2 file`, vùng nổ lan `≤ 5 file` (không đụng entry point/core API/schema), `0 quyết định thiết kế mở`, và chạy trong 1 phiên ngắn.
   - **Lane `quick` (Express — 1 file mini-plan, 1 cổng duyệt):** Luồng phase `quick_analyze → quick [gate] → quick_implement → quick_qc → quick_report → idle` (`phases.md:22-36`).
   - **Lane `full` (Deep — 5 tài liệu tách bạch, 3 cổng duyệt):** Luồng phase `analyze → spec [gate] → plan [gate] → mode [gate] → implement → qc → report → idle` (`phases.md:7-20`).
   - **Lối tắt `_tdq_direct` (`hooks/scripts/prompt_context.py:91,263-268`, `tdq_setup.py:1111`):** Khi prompt có từ khóa `_tdq_direct`, tự động khảo sát mã nguồn, lập mini-plan và chỉ dừng đúng 1 cổng duyệt mini-plan (bỏ qua hỏi chọn làn và phỏng vấn).
2. **Zero-Popup Natural Chat Approval (`skills/tdq-conventions/references/approval.md:6-76`, `user-facing-block.md:102-108`):**
   - **Cấm tuyệt đối** mở popup UI (`AskUserQuestion` trên Claude / `ask_question` trên host khác) và **cấm tuyệt đối** tự bật `EnterPlanMode`/`ExitPlanMode` của harness (`approval.md:48`, `user-facing-block.md:102-105`, `hooks/scripts/ask_gate.py:42-60`).
   - Mọi câu hỏi đánh số `1, 2, 3` với lựa chọn `- A (đề xuất): ...`, người dùng trả lời gộp tự nhiên kiểu `1a 2b 3c` hoặc `"duyệt spec"`, `"duyệt plan"`, `"duyệt nhanh"` (`user-facing-block.md:83-107`).
   - **Khóa duyệt chống giả mạo (`hooks/scripts/prompt_context.py:41-159,360-375`):** Câu duyệt hợp lệ phải có **cả từ đồng thuận lẫn đối tượng/đại từ chỉ định** (`co_y_duyet`), loại trừ câu phủ định (`TU_CHOI_RE`), loại trừ văn bản máy sinh (`NON_HUMAN_RE`: stack trace, git diff, XML system notification) và lời trích dẫn (`QUOTED_SPEECH_RE`), đồng thời đóng dấu `spec_sha256` (nếu `spec.md` bị sửa sau khi duyệt mà lệch hash, hook báo động ngay ở `prompt_context.py:360-375`).
3. **Cơ chế Chống Bỏ cuộc Giữa chừng, Chống Cắt góc & Chống Over-engineering:**
   - **Chống dừng giữa plan (`skills/tdq-conventions/SKILL.md:66-72`, `hooks/scripts/stop_gate.py:154-252`):** Cấm viện cớ *"tiết kiệm token"*, *"session dài"*, *"để phiên sau làm tiếp"*. `stop_gate.py` chặn đứng (`decision: "block"`, mã `[TDQ:UNFINISHED]`) nếu còn task `[ ]`/`[~]`, chưa ghi workinglog, hoặc ở `qc`/`report` mà chưa tạo báo cáo (có cầu chì `MAX_STREAK = 3` để tránh kẹt vô hạn khi gặp lỗi hạ tầng thật).
   - **4 lý do `pause` đóng kín duy nhất (`tdq-conventions/SKILL.md:69`, `stop_gate.py:16`):** `mat-truy-cap` (mất quyền/mạng/tool), `pha-huy` (thao tác xóa/phá hủy cần hỏi), `dau-vao-user` (thiếu thông tin thật từ user), `tran-qc` (lặp sửa lỗi QC chạm trần 2 vòng).
   - **Thang 7 Nấc "Build-Less-Than-Asked" (`skills/tdq-build/references/rules/chung.md:67-197`, bơm đầu phiên qua `TDQ:GON` tại `session_start.py:278-294`) & `tdq-lean`:**
     - Rung 1: `1-line surgical fix` thắng viết lại hàm **3:1** (ngoại lệ duy nhất: khi user chủ động yêu cầu Refactor / Clean Architecture / SOLID — `tdq_setup.py:1112`).
     - Rung 2: `stdlib` thắng thư viện ngoài (`0 new packages`).
     - Rung 3: Cấm tạo lớp bọc (wrapper/abstraction) chỉ có 1 nơi gọi (**Rule of Three** — `clean-code.md:54`: **YAGNI đứng trước SOLID**).
     - Rung 4: Xóa code chết tốt hơn giữ phòng hờ (5 nhãn dọn dẹp của `skills/tdq-lean/SKILL.md`: `delete`, `stdlib`, `native`, `yagni`, `shrink`).
     - Rung 5–7: Tái sử dụng công cụ nền sẵn có, bắt buộc bật **Log Service mặc định** (`chung.md:128-130`, `SKILL.md:208`), cấm mọi placeholder/`TODO`/`FIXME`/mock giả tạo kết quả xanh giả (`SKILL.md:207`).
   - **6 Phản mẫu bị cấm (`ANTI-1..ANTI-6` tại `hooks/scripts/session_start.py:346-347`):** Cấm bỏ qua `tdq-intake`, cấm sửa code trước khi duyệt gate, cấm tự chạy `tdq_state.py approve` không có lệnh thật từ người dùng, cấm thêm `Co-Authored-By`, cấm dừng giữa plan, cấm dùng `Grep` trần khi chưa tra khái niệm qua LSP/Graphify.
4. **Kiểm soát Carry-Cost & Progressive Disclosure (`skills/tdq-conventions/references/context-budget.md:1-131`):**
   - **Mục lục dòng tự động (`scripts/doc_index.py:33-45`):** Mọi file tài liệu dài `≥ 90 dòng` hoặc `≥ 2,000 tokens` đều gắn comment `<!-- muc-luc-dong: ... -->` ở đầu tệp để agent chỉ gọi `Read(offset, limit)` đúng mục cần đọc.
   - **Chặn đọc lặp (`hooks/scripts/read_gate.py:51,143-211` — `TDQ:DOC`):** Cảnh báo ngay khi đọc nguyên file lần 2 (file `≥ 2,048 bytes`) hoặc đọc chồng lấn `≥ 70%` vùng dòng từ 2 lần trở lên.
   - **Chặn xả stdout làm ngập ngữ cảnh (`hooks/scripts/bash_gate.py:55-65,187-195` — `TDQ:OUTPUT`):** Nhắc chặn các lệnh không giới hạn dòng như `cat`, `git log`, `git diff`, `git show`, `ls -R` khi không kèm `-n` / `head` / `tail` / `--stat`.
   - **Luật Gom 1 Đợt Đọc Song song & 6 Trường hợp Cấm Gom (`context-budget.md:29-102`):** Đọc nhiều mục cùng 1 file phải phát song song trong **1 message duy nhất** (carry-cost `1×` thay vì cấp số cộng `k(k+1)/2`), nhưng cấm gom mù khi bước 2 phụ thuộc kết quả bước 1, khi đang chạy Red→Green giữa 2 task khác nhau, hoặc trước cổng duyệt.
   - **Handoff Schema `< 200 tokens` (`skills/tdq-conventions/references/handoff-schema.json:1-50`):** Subagent chỉ trả JSON tóm tắt (`status`, `touched_files`, `red_cmd`, `green_cmd`, `summary`, `blockers`) dưới 200 token để bảo vệ context của agent điều phối.

---

## PHẦN 2. KIỂM KÊ TOÀN DIỆN HỆ THỐNG LUẬT (COMPLETE RULES & LAWS INVENTORY)

### 2.1. Mười Lăm Luật Linter Tài liệu & Quy trình (`R1–R15` trong `scripts/doc_lint.py` + `scripts/token_budget.py`)

Tệp `scripts/doc_lint.py` (913 dòng, `43,932 bytes`) thực thi tự động 15 luật từ **R1** đến **R15**:

| Mã | Hàm & Dòng (`scripts/doc_lint.py`) | Nội dung quy định & Ngưỡng chính xác |
|---|---|---|
| **R1** | `rule_r1` (`199-217`) | Các bước trong mục `Steps` / `Các bước` phải đánh số liên tục `1, 2, 3...` không đứt quãng, không nhảy cóc. |
| **R2** | `rule_r2` (`219-230`) | Mọi lời gọi lệnh (`python3`, `tdq_state.py`...) phải đặt trong code fence, inline backticks `` `...` ``, hoặc ô bảng Markdown `|`. |
| **R3** | `rule_r3` (`236-248`) | Mọi tệp `SKILL.md` bắt buộc có đủ cặp mốc kết thúc: `Done when:` (`Xong khi:`) và `Next step:` (`Bước kế tiếp:`). |
| **R4** | `rule_r4` (`250-266`) | **Cấm từ mơ hồ** (`nếu cần`, `tùy ý`, `tuỳ ý`, `nên cân nhắc`, `linh hoạt`, `tự quyết` — `VAGUE_WORDS`, dòng `130-133`) trong các mục quy tắc nghiêm ngặt, trừ phi trong phạm vi 3 dòng lân cận có bảng điều kiện `|` hoặc mũi tên quyết định `→`. |
| **R5** | `rule_r5` (`269-299`) | Độ dài câu văn xuôi tối đa **`MAX_SENTENCE_WORDS = 40` từ** (dòng `125`). |
| **R6** | `rule_r6` (`36-124`, `302-313`) | Trần dòng chung cho mọi file Markdown là **`MAX_LINES_ANY = 500` dòng** (`dòng 124`). Riêng 11 tệp `SKILL.md` chịu trần riêng trong `SKILL_LINE_LIMITS` (`dòng 36-48`): `tdq-intake`: **148**, `tdq-spec`: **100**, `tdq-plan`: **121**, `tdq-build`: **174**, `tdq-status`: **60**, `tdq-setup`: **132**, `tdq-conventions`: **209**, `tdq-check-status`: **80**, `tdq-lean`: **80**, `tdq-browser-research`: **60**, `tdq-browser-test`: **85**. |
| **R7** | `rule_r7` (`127`, `315-323`) | Các skill trong tập `NEEDS_TEMPLATE = {"tdq-spec", "tdq-plan", "tdq-build"}` bắt buộc dẫn chiếu tới `references/*template*.md`. |
| **R8** | `rule_r8` (`328-382`) & `pair()` (`578-638`) | Tài liệu Spec phải có mục `## 3b. Năng lực & công cụ` với nhãn phán quyết đóng kín (`DÙNG`, `KHÔNG`, `NỀN`); mọi dòng `KHÔNG` phải mở đầu bằng đúng 1 trong 4 tiền tố đóng: `khác lĩnh vực`, `spec §3 đã chọn cách khác tốt hơn`, `thiếu quyền/công cụ`, `user đã cấm`. Khi chạy `--pair` đối chiếu Spec–Plan, Plan bắt buộc có `## Cụm song song` và mọi năng lực `DÙNG` phải có khối hợp đồng 5 trường (`Dùng`, `Để`, `Ra`, `Kiểm`, `Không dùng cho`). |
| **R9** | `rule_r9` (`389-420`) | Các tệp luật gốc (`soul.md`, `clean-code.md`, `skills/tdq-build/references/rules/*.md` trừ `index.md` và `them-ngon-ngu.md`) bắt buộc có đủ 3 tiêu đề `##`: `When it applies`, `What to do`, `Self-check`. |
| **R10** | `rule_r10` (`426-457`) | Mọi bản Spec thuộc làn `full` bắt buộc có mục `## 2b. Ranh giới module` (Module Boundaries). |
| **R11** | `rule_r11` (`464-495`) | Từ mốc slug `2026-08-19` trở đi, Spec **cấm chứa đường dẫn file test cụ thể** (`tests/.../test_*.py`) hoặc cờ `-k` — Spec chỉ nêu điều kiện PASS ở mức hành vi, còn lệnh test/tệp test cụ thể thuộc về Plan. |
| **R12** | `rule_r12` (`649-717`) | Khi `doc_lang == "vi"`, mọi tài liệu đầu ra trong `OUTPUT_DIRS` (`docs/tdq/specs`, `plans`, `reports`, `briefs`, `qc`, `worklogs`) **không được có ≥ 3 dòng văn xuôi liên tiếp** (mỗi dòng `≥ 6 từ`) không dấu tiếng Việt. |
| **R13** | `kiem_tran_token` (`498-522`) & `scripts/token_budget.py` (`40-146`) | Toàn bộ tệp `skills/*/references/**/*.md` phải được khóa băm `sha256` (chuẩn hóa LF) trong `docs/tdq/token-budget.json` và chịu trần cứng **`TRAN_TOKEN = 3500` tokens** (`token_budget.py:25`). Thực đo hiện tại: **62 tệp** được khóa, cao nhất là `skills/tdq-build/references/qc.md` (**`3,496` tokens** — sát trần 4 token), thấp nhất là `worklog-images.md` (**`300` tokens**). |
| **R14** | `rule_r14` (`723-849`) | Từ mốc slug `2026-10-03-0732` trở đi, trong bảng `## 6.` (Tiêu chí nghiệm thu `Q\d+`), mọi dòng có ngưỡng số định lượng bắt buộc điền cột **`Đo trước`** (có chữ số thực đo baseline) và cột **`Dự phòng nếu trượt`** (fallback khi không đạt ngưỡng). |
| **R15** | `rule_r15` (`526-568`) | Mọi task trong Plan có trường `Chạm:` đụng tới đuôi tệp mã nguồn (`.py`, `.ts`, `.tsx`, `.js`, `.jsx`, `.go`, `.rs`, `.c`, `.cpp`, `.cs`, `.rb`, `.php`, `.java`) bắt buộc đính kèm mục đặc tả kỹ thuật (`đặc tả`, `logic`, `giải thuật`, `thuật toán`, hoặc `pseudo-code`). |

*(Bổ trợ thêm: `scripts/doc_dup.py` (239 dòng, `10,000 bytes`) quét trùng lặp đoạn văn giữa các tài liệu `skills/` để chống nhân bản luật vi phạm DRY).*

---

### 2.2. Luật Phân Tầng Ngôn ngữ, Quốc tế hóa (i18n) & Phân loại Neo Luật

1. **Quy ước Ngôn ngữ 3 Tầng (`skills/tdq-conventions/SKILL.md:18-36`):**
   - **Layer 1 — Luật nội bộ & Mã nguồn (`skills/**`, `agents/*.md`, comments/docstrings trong `scripts/` & `hooks/`):** Luôn viết bằng **tiếng Anh (English)** để model suy luận chính xác và tiết kiệm token BPE.
   - **Layer 2 — Chuỗi máy in ra từ Hooks/Scripts (Machine strings):** Luôn bằng **tiếng Anh**.
   - **Layer 3 — Tài liệu hướng người dùng (`brief`, `spec`, `plan`, `qc`, `report`, `workinglog`) & Hội thoại chat:** Viết theo trường **`doc_lang`** trong `docs/tdq/state.json` (mã BCP 47, mặc định `"vi"` — tiếng Việt có dấu đầy đủ).
2. **Kiểm tra Tự động `scripts/i18n_check.py` (192 dòng, `7,257 bytes`):**
   - Quét các tệp `.py`, `.md`, `.json`, `.txt` trong vùng luật để phát hiện ký tự tiếng Việt có dấu rò rỉ vào Layer 1/2, trừ các dòng/khối template mẫu được đánh dấu miễn trừ tường minh bằng `<!-- i18n-allow: ... -->` hoặc `# i18n-allow`.
3. **Phân loại Neo Luật `scripts/luat_phan_loai.py` (153 dòng, `6,876 bytes`):**
   - Phân loại từng mỏ neo luật (`L\d+`) thành 2 nhóm tách biệt: `ly-luan` (luật suy luận nội bộ của model → giữ tiếng Anh) và `user-facing` (nhãn/mẫu hiển thị trực tiếp cho người dùng → theo `doc_lang`).

---

### 2.3. Luật Khối Trình bày Người dùng (`User-Facing Block`) & Whitelist Ký hiệu Unicode

- **Nguồn luật:** `skills/tdq-conventions/references/user-facing-block.md` (`132 dòng`, `8,739 bytes`), `user-facing-block-vi-du.md` (`76 dòng`, `3,045 bytes`), kiểm tự động bởi `scripts/scan_block_symbols.py` (`118 dòng`, `4,954 bytes`).
- **7 cổng bắt buộc xuất User-Facing Block (`user-facing-block.md:26-38`):** Chọn làn (`intake`), Phỏng vấn làm rõ, Duyệt `spec`, Duyệt `plan`, Chọn `mode` thực thi (`single` / `team` / `codex`), Duyệt `quick` mini-plan, và Bàn giao `report`.
- **6 thành phần theo thứ tự cố định (`user-facing-block.md:40-69`):** Dòng trạng thái mở đầu `➤ ...` → Tóm tắt ngữ cảnh → Bảng/danh sách điểm chính → Đường dẫn file & bản vẽ Archify HTML → Câu hỏi đánh số `1, 2, 3` kèm lựa chọn `- A (đề xuất): ...` → Đường kẻ ngang kết lượt `---`. (Nếu sau khi in block mà agent còn gọi thêm tool khiến block bị trôi, bắt buộc **in lại nguyên văn** ở cuối lượt — `user-facing-block.md:96-100`).
- **Whitelist đúng 6 ký tự Unicode phi-ASCII được phép dùng trang trí (`scan_block_symbols.py:29-45`):**
  1. `➤` (`U+27A4`)
  2. `·` (`U+00B7`)
  3. `—` (`U+2014`)
  4. `→` (`U+2192`)
  5. `–` (`U+2013`)
  6. `…` (`U+2026`)
  - **Cấm tuyệt đối mọi emoji** và mọi ký hiệu hộp/trang trí khác ngoài 6 ký tự trên. Dấu hai chấm bắt buộc nằm **bên trong** cặp in đậm: `**Nhãn:**` (không viết `**Nhãn**:` — `user-facing-block.md:75`).

---

### 2.4. Luật Quản trị Nợ Kỹ thuật (`ponytail:`), Độ Phức tạp Code & Luật theo Ngôn ngữ

1. **Luật Đánh dấu Nợ Kỹ thuật `ponytail:` (`scripts/kiem_no_marker.py:1-138`, `skills/tdq-lean/SKILL.md:55-75`):**
   - Cấm để nợ ngầm (`TODO`/`FIXME`/`HACK` trôi nổi). Mọi điểm thỏa hiệp tạm thời trong `scripts/` và `hooks/` bắt buộc ghi marker `ponytail: <trần chịu tải>, <lộ trình nâng cấp>` có **dấu phẩy `,` ngăn cách đủ 2 vế** (trừ dòng có `no-marker: allow`). Thiếu dấu phẩy hoặc rỗng 1 trong 2 vế bị `kiem_no_marker.py` đánh rớt (`exit 1` — "nợ thối").
2. **Ngưỡng Độ Phức tạp & Quy tắc Chung (`skills/tdq-build/references/rules/chung.md:1-233`):**
   - **Cyclomatic Complexity:** `≤ 10` mỗi hàm (`chung.md:58`).
   - **Cognitive Complexity:** `≤ 15` mỗi hàm; ngoại lệ duy nhất cho C/C++/Objective-C là `≤ 25` (`chung.md:59-61`).
   - **Chiều dài hàm:** `≤ 50` dòng vật lý (`soul.md:126-128`).
   - **3 câu hỏi Intentionality trước khi nộp code (`chung.md:29-40`):** (1) Tên thực thể có nói đúng công việc nó làm không? (2) Mỗi đường lỗi đã được bắt đúng loại, ghi log và xử lý chủ đích chưa? (3) Có dòng code/import/tham số thừa nào xóa đi mà vẫn xanh không?
3. **Bộ Luật Chuyên biệt theo Ngôn ngữ (`skills/tdq-build/references/rules/index.md` + 7 ngôn ngữ):**
   - **Python (`python.md:1-70`):** Chuẩn PEP 8 (`snake_case`, `PascalCase`, `UPPER_CASE`), 3 nhóm import (`stdlib → third-party → local`), cấm mutable default args (`xs=[]`), cấm bare `except:` / `except Exception: pass`, bắt buộc chạy `ruff check` (nhóm F/E/B), Cyclomatic `≤ 10`, Cognitive `≤ 15`.
   - **TypeScript / JavaScript (`typescript-js.md:1-68`):** Tối thiểu gói `recommended` của ESLint + `typescript-eslint`, cấm bare `any` (`no-explicit-any` → dùng kiểu cụ thể hoặc `unknown` thu hẹp dần), cấm floating Promise (`no-floating-promises`, `await-thenable`), cấm `@ts-ignore`/`@ts-expect-error` không kèm lý do (`ban-ts-comment`), hạ `complexity` của ESLint từ mặc định `20` xuống **`10`**.
   - Các tệp ngôn ngữ khác cùng cấu trúc R9 trong `skills/tdq-build/references/rules/`: `go.md` (`901 tokens`), `rust.md` (`844 tokens`), `cpp.md` (`894 tokens`), `csharp.md` (`831 tokens`), `html.md` (`927 tokens`), cùng `cookbooks/python-cookbook.md` và `cookbooks/typescript-js-cookbook.md`. Hook `edit_gate.py` tự động bơm mã nhắc `TDQ:RULE:PY`, `TDQ:RULE:TS`, `TDQ:RULE:JS` lần đầu sửa file ngôn ngữ tương ứng trong phiên.

---

### 2.5. Luật Tìm kiếm 3 Tầng & Cổng Chặn `search_rules.py` / `search_gate.py` / `lsp_gate.py`

1. **Cửa sổ Quota Grep (`scripts/search_rules.py:26-1126`, `hooks/scripts/search_gate.py:33-198`):**
   - Ở các phase thực thi (`implement`, `quick_implement`, `qc`...), agent không được dùng `Grep` mò mẫm thay cho công cụ ngữ nghĩa. Mỗi lần gọi truy vấn khái niệm qua LSP (allowlist `LSP_HOI` gồm `mcp__lsp__find_symbol`, `find_references`, `go_to_definition`, `list_symbols`, `hover`...) hoặc `graphify` (`query`, `explain`, `path`, `god-nodes`, `affected`) sẽ **mở khóa cửa sổ `CUA_SO = 10` lượt Grep** (`search_rules.py:145-168`).
   - **4 trường hợp miễn quota Grep tự do:** (a) Đang ở phase khảo sát `analyze` / `quick_analyze` / `spec`; (b) Từ khóa tìm kiếm xuất hiện nguyên văn trong prompt của người dùng; (c) Lệnh chỉ liệt kê tên tệp (`files_with_matches` / glob); (d) Chỉ quét trong thư mục tài liệu (`docs/`, `*.md`).
   - **Ngân sách an toàn bộ phân tích shell AST (`NganSach` tại `search_rules.py:39-45`):** Giới hạn cứng chống treo parser: `max_input = 32,768` ký tự, `max_work = 262,144` bước, `max_depth = 8`, `max_output = 1,024` mục.
   - **Cầu chì hạ vũ khí (`BREAKER_CHAN = 3` tại `search_gate.py`):** Nếu máy chưa có dấu sẵn sàng LSP/Graphify sau 3 lần nhắc chặn, cổng tự động hạ xuống cho phép Grep để không làm kẹt phiên.
2. **Luật Cổng LSP (`hooks/scripts/lsp_gate.py:33-159`):**
   - Bắt buộc khởi tạo `mcp__lsp__start_lsp(root_dir, language_id)` trước khi tra symbol (với TS/JS cần `open_document` 1 tệp để TSServer nhận project — `tdq_setup.py:1098`).
   - Giới hạn hàm tốn tài nguyên `blast_radius`: chỉ cho phép tối đa **`≤ 3` tệp**, `scope="exported"`, `include_transitive=false`. Có cầu chì ngắt sau **2 lần lỗi LSP liên tiếp** (`lsp_gate.py:42-155`).

---

### 2.6. Luật Đặt tên, Nhánh Git, Commit, Workinglog, Bảo vệ Trạng thái & Vòng đời Tri thức

1. **Đặt tên Request Slug, Nhánh Git & Worktree (`skills/tdq-conventions/SKILL.md:124-128,139-152`, `hooks/scripts/bash_gate.py:30-41`):**
   - **Request slug:** `YYYY-MM-DD-HHMM-<kebab-ascii-toi-da-5-tu>`.
   - **Nhánh request:** `<feature|bugfix|hotfix|chore|docs>/<kebab>` (chỉ dùng dấu gạch chéo xuôi `/`; hợp nhất về nhánh gốc bằng `git merge --no-ff`).
   - **Nhánh worktree đội sub-agent:** `tdq/<slug>/<task>` đặt trong `.tdq-worktrees/`.
   - **Cấm định danh AI (`SKILL.md:145-151`, `bash_gate.py:30-41`, `tdq_setup.py:1137`):** Tên nhánh, worktree, commit **TUYỆT ĐỐI CẤM** bắt đầu bằng `claude`, `antigravity`, `gemini`, `codex`; nội dung commit/PR **TUYỆT ĐỐI CẤM** chứa `Generated with ...` hay `Co-Authored-By: ...`.
   - **Quyền Commit/Push (`SKILL.md:141-144`, `bash_gate.py` `TDQ:GIT`):** Không bao giờ tự `git commit` hoặc `git push` khi người dùng chưa yêu cầu rõ ràng trong phiên (ngoại lệ kỹ thuật duy nhất: commit nội bộ cần thiết để mở/gộp worktree, tuyệt đối không push).
   - **Vùng Dirty tự động mang theo (`tdq_setup.py:1138`, `skills/tdq-intake/SKILL.md:89-92`):** Khi chuyển/hợp nhất nhánh mà working tree chỉ bẩn ở `docs/**`, `*.md`, `logs/**`, `*.log`, `graphify-out/**`, agent **tự động mang theo** không dừng hỏi người dùng; chỉ dừng hỏi khi bẩn ở mã nguồn (`scripts/`, `src/`, `hooks/`, `tests/`).
2. **Bảo vệ `state.json`, Workinglog & Sổ cái Hiệu ứng (`SKILL.md:45-65,115-123`, `hooks/scripts/edit_gate.py`, `bash_gate.py`):**
   - **Cấm sửa tay `docs/tdq/state.json`** bằng công cụ `Edit`/`Write` hoặc script ngoài — mọi chuyển đổi trạng thái bắt buộc đi qua CLI `scripts/tdq_state.py` (`edit_gate.py` & `bash_gate.py` chặn bằng mã `TDQ:STATE`).
   - **Workinglog (`docs/tdq/worklogs/<slug>.md`):** Phải ghi nhận quyết định, lệnh kiểm thử, sai lệch (`lech add`) xuyên suốt phiên; `stop_gate.py` kiểm tra mtime/hash workinglog trước khi cho kết thúc phase (`TDQ:LOG`). Ảnh chụp minh chứng lưu cục bộ, dẫn link tương đối theo `skills/tdq-conventions/references/worklog-images.md:1-21` (cấm nhúng base64 làm phình tài liệu).
3. **Vòng đời Tri thức (`skills/tdq-conventions/references/knowledge-template.md:1-58`):**
   - Gồm 4 trạng thái đóng: `candidate` (mặc định khi mới rút trích, bắt buộc `auto_policy: false` để chưa tự thành luật cứng), `reviewed`, `rejected`, `superseded`, kèm bước quét lọc bí mật/token trước khi lưu.
4. **Danh mục Đóng 22 Mã Hook (`skills/tdq-conventions/references/reminder-codes.md:15-50` + `hooks/scripts/*.py`):**
   - `TDQ:NEXT`, `TDQ:INTAKE`, `TDQ:APPROVE`, `TDQ:LOG`, `TDQ:STATE`, `TDQ:GIT`, `TDQ:DOC`, `TDQ:SEARCH`, `TDQ:ASK`, `TDQ:LSP`, `TDQ:TICK`, `TDQ:TEAM`, `TDQ:UNFINISHED`, `TDQ:STUCK`, `TDQ:DOD`, `TDQ:WORKTREE`, `TDQ:GON`, `TDQ:QC`, `TDQ:ANCHOR`, `TDQ:OUTPUT`, `TDQ:SETUP`, `TDQ:RULE:<LANG>`.

---

## PHẦN 3. KIỂM TOÁN TƯƠNG THÍCH RULES TRÊN ANTIGRAVITY (100% BẰNG CHỨNG ĐỐI CHIẾU GROUND-TRUTH)

### 3.1. Chuẩn Ground-Truth Chính thức của Antigravity về Rules & Plugins

Đối chiếu trực tiếp từ bộ tài liệu nội tại của Antigravity:
1. **Cấu trúc thư mục Rules của Plugin (`plugin/SKILL.md:205,210-211`, `agy-customizations/docs/plugins.md:20-21,73-75`):**
   - Một plugin Antigravity tại `~/.gemini/config/plugins/<plugin_name>/` đóng gói rules trong thư mục con **`rules/`**, khuyến nghị hợp nhất vào **`rules/AGENTS.md`** (hoặc `GEMINI.md`).
   - **Định dạng Plugin Rules (`plugin/SKILL.md:210-211`, `docs/plugins.md:74-75`):** Là tệp **Plain Markdown KHÔNG có YAML frontmatter** (`no frontmatter`), và **luôn hoạt động (`always active`)** chừng nào plugin đang bật (`enabled: true`).
   - *(Lưu ý phân biệt: Chỉ các tệp `.agents/rules/*.md` cấp workspace/global mới dùng frontmatter `trigger: always_on | model_decision | glob | manual`; còn standalone `GEMINI.md` / `AGENTS.md` và plugin `rules/AGENTS.md` là plain Markdown không frontmatter — `agy-customizations/SKILL.md:48-52,93-95`, `docs/rules.md:5-22`).*
2. **Giới hạn Dung lượng Tệp & Ngân sách Token (`agy-customizations/docs/rules.md:31-40`, `SKILL.md:89`):**
   - **Trần mỗi tệp Rule (Per-file byte cap):** **`24,000 bytes`** sau khi đã bung (expand) toàn bộ liên kết nhúng `@[label](relative/or/abs/path)`. Nếu vượt `24,000 bytes`, Antigravity **cắt cụt (truncate) theo ranh giới dòng** (`docs/rules.md:31-33`).
   - **Cú pháp nhúng tệp (`docs/rules.md:26-29`):** Antigravity dùng cú pháp Markdown link có tiền tố `@`: **`@[nhãn](đường_dẫn)`** (ví dụ `@[soul](../skills/tdq-conventions/references/soul.md)`), **KHÔNG phải** cú pháp `@path/to/file` trần của Claude Code.
   - **Tổng ngân sách Token Rules (`defaultRulesBudget` — `docs/rules.md:34-40`):** **`20,000 tokens`** dùng chung cho toàn bộ always-on rules cấp workspace, global user và **mọi user plugin trong `~/.gemini/config/plugins/`** (chỉ `/builtin/plugins/` của hệ thống mới được miễn). Nếu tổng vượt `20,000 tokens`, các rule vượt ngân sách **bị giáng cấp thành con trỏ đường dẫn tệp (demoted to file-path pointers)** thay vì được bơm nội dung vào system prompt!
3. **Cơ chế Nạp Skills trên Antigravity (`agy-customizations/SKILL.md:85-87`, `docs/skills.md:1-40`):**
   - Skills tuân theo **Progressive Disclosure**: Đầu phiên agent **chỉ nhìn thấy `name` và `description`** trong YAML frontmatter; toàn bộ thân `SKILL.md` **chưa được nạp** cho tới khi model chủ động đọc `SKILL.md` của skill đó.

---

### 3.2. Kiểm tra Thực địa `C:\Users\admin\.gemini\config\plugins\tdq-workflow\rules\` & Hệ thống Rules Hiện tại

Kết quả quét trực tiếp trên đĩa (xác minh bằng Python script, exit code `0`):

| Đường dẫn kiểm tra | Tồn tại trên đĩa? | Kích thước / Chi tiết thực tế |
|---|---|---|
| `C:\Users\admin\.gemini\config\plugins\tdq-workflow\rules\` | **KHÔNG (`False`)** | **0 tệp, 0 bytes** — thư mục `rules/` hoàn toàn chưa được tạo! |
| `C:\Users\admin\.gemini\config\plugins\tdq-workflow\AGENTS.md` / `GEMINI.md` | **KHÔNG (`False`)** | Không tồn tại. |
| `C:\Users\admin\.gemini\config\rules\` / `AGENTS.md` / `GEMINI.md` | **KHÔNG (`False`)** | Không có rule toàn cục nào của người dùng cho Antigravity. |
| `C:\Users\admin\.gemini\AGENTS.md` / `GEMINI.md` | **KHÔNG (`False`)** | Không tồn tại. |
| `TDQ-Workflow\CLAUDE.md` / `AGENTS.md` / `.claude\rules` / `.agents\rules` / `portable_src\rules` | **KHÔNG (`False`)** | Repo gốc cũng không có thư mục `rules/` đóng gói sẵn. |
| `C:\Users\admin\.claude\CLAUDE.md` (Claude Code host) | **CÓ (`True`)** | **`8,504 bytes`** (55 dòng) — chứa khối ghim `<!-- TDQ:TOOLS --> ... <!-- /TDQ:TOOLS -->`. |
| `C:\Users\admin\.codex\AGENTS.md` (Codex host) | **CÓ (`True`)** | **`6,082 bytes`** (40 dòng) — chứa khối ghim `<!-- TDQ:TOOLS --> ... <!-- /TDQ:TOOLS -->`. |
| `C:\Users\admin\.gemini\config\config.json` → `plugins."tdq-workflow"` | **CÓ (`True`)** | Giá trị hiện tại: **`{"enabled": false}`** (plugin đang bị tắt!). |

---

### 3.3. Sáu Phát hiện Nghiêm trọng (Critical Findings) Làm Đứt gãy "Linh hồn" TDQ-Workflow trên Antigravity

#### Phát hiện #1 (CRITICAL): Khoảng trống Luật Thường trực (`0 Always-On Rules`) trên Antigravity
- **Bằng chứng so sánh đa host:**
  1. **Trên Claude Code:** `scripts/tdq_setup.py:1086-1201` ghim khối `KHOI_HUONG_DAN` (`<!-- TDQ:TOOLS -->`) vào `C:\Users\admin\.claude\CLAUDE.md` (`8,504 B`), **cộng thêm** hook `SessionStart` (`hooks/scripts/session_start.py` bơm `TDQ:GON` + `ANTI-1..ANTI-6`) và `UserPromptSubmit` (`hooks/scripts/prompt_context.py` bơm `[TDQ:INTAKE]` vào từng tin nhắn).
  2. **Trên Codex:** Có `C:\Users\admin\.codex\AGENTS.md` (`6,082 B`) ghim khối `TDQ:TOOLS` + `.codex/hooks.json` có cả `SessionStart` và `UserPromptSubmit`.
  3. **Trên OpenCode:** `.opencode/plugins/tdq-workflow.js:117-127` dùng `ctx.session.hook('context')` bơm `<TDQ_WORKFLOW> Mọi yêu cầu mới đều mở bằng skill tdq-intake... </TDQ_WORKFLOW>` ngay tin nhắn đầu tiên.
  4. **Trên Antigravity (`scripts/build_portable.py:639-731`):** Hàm xuất gói Antigravity chỉ chép `skills/`, `scripts/`, `hooks/`, `plugin.json`, `hooks.json`, `mcp_config.json`, `manifest.json`, `README.md` — **hoàn toàn bỏ quên `rules/AGENTS.md`**, trong khi Antigravity cũng **không có sự kiện `SessionStart` hay `UserPromptSubmit`** trong `hooks.json` của gói cài!
- **Hệ quả trực tiếp:** Vì Antigravity chỉ hiển thị `name` + `description` của skills theo cơ chế Progressive Disclosure, khi người dùng gửi một yêu cầu code bình thường trên Antigravity (kể cả khi bật plugin `tdq-workflow`), **không có bất kỳ dòng luật always-on nào** ra lệnh cho Antigravity phải:
  - Bắt buộc mở mọi yêu cầu mới qua `tdq-intake`;
  - Tuân thủ thứ tự `chất lượng > runtime > context cost` và thang 7 nấc `TDQ:GON`;
  - Chạy tam giác tìm kiếm 3 tầng (LSP → Graphify → Grep);
  - Cấm gọi công cụ hỏi trắc nghiệm popup (`ask_question` của Antigravity — tương đương `AskUserQuestion` của Claude);
  - Cấm thêm `Co-Authored-By` khi commit và tự mang theo vùng dirty `docs/**`.

#### Phát hiện #2 (CRITICAL): Lệch Phiên bản Lớn (`0.74.0` vs `0.97.0`) & Thiếu Hẳn Skills / Subagents trong `build_portable.py`
- Bản cài tại `C:\Users\admin\.gemini\config\plugins\tdq-workflow\plugin.json` đang ở **`0.74.0`**, tụt **23 bản phát hành** so với repo nguồn `0.97.0` (`.claude-plugin/plugin.json:4`).
- Ngay cả trong code mới nhất `0.97.0`, danh sách cứng `THU_TU_SKILL` tại `scripts/build_portable.py:206-220` chỉ liệt kê **10 skills**, **bỏ sót 2 skills mới** có trong `skills/` và `doc_lint.py:46-47` là **`tdq-browser-research`** (`51 dòng`, `2,864 B`) và **`tdq-browser-test`** (`77 dòng`, `3,993 B`).
- Đồng thời `build_portable.py` không xuất thư mục `agents/` sang gói Antigravity, dù chuẩn plugin của Antigravity **hỗ trợ chính thức `plugins/<name>/agents/<agent>.md`** (`plugin/SKILL.md:204`, `docs/plugins.md:19,65-71`).

#### Phát hiện #3 (CRITICAL): Sai Lệch Schema `hooks.json` & Payload Stdin Giữa Claude Code và Antigravity
Đối chiếu `C:\Users\admin\.gemini\config\plugins\tdq-workflow\hooks.json` (và hàm sinh tại `scripts/build_portable.py:424-465`) với tài liệu chuẩn `agy-customizations/docs/hooks.md:15-193`:
1. **Sai cấu trúc JSON gốc (`docs/hooks.md:15-55`):**
   - `hooks.json` của gói `tdq-workflow` đang xuất theo schema Claude Code: `{"description": "...", "hooks": {"PreToolUse": [...], "Stop": [...]}}`.
   - Trong khi đó, schema `hooks.json` của Antigravity quy định **khóa cấp cao nhất (top-level keys) là tên định danh nhóm hook**, bên trong mới là tên sự kiện (`{"tdq-workflow-gates": {"PreToolUse": [...], "Stop": [...]}}`), và sự kiện `Stop` trên Antigravity dùng **mảng phẳng (Flat handler array)** `[{"type": "command", "command": "..."}]` chứ không bọc thêm lớp `{"hooks": [...]}` như `PreToolUse` (`docs/hooks.md:62-75,92-119`)! (Xem đối chứng thực tế ngay tại `C:\Users\admin\.gemini\config\hooks.json` trên cùng máy).
2. **Thiếu `matcher` và lệch khóa JSON stdin trong `agy_pretooluse_gate.py` & `read_gate.py` (`docs/hooks.md:149,183-193`):**
   - Payload `PreToolUse` của Antigravity truyền trên `stdin` là:
     `{"toolCall": {"name": "run_command", "args": {"CommandLine": "..."}}}` (hoặc `"read_file"` với `args.Path`, `"edit_file"` / `"write_file"` với `args.Path`).
   - Thế nhưng `hooks/scripts/agy_pretooluse_gate.py:57-63` chỉ dò `tool_input.command`, `toolInput.command`, `input.command`, `arguments.command`, `command` — **hoàn toàn không đọc `toolCall.args.CommandLine`**, khiến cổng chặn lệnh Bash trên Antigravity **luôn nhận chuỗi rỗng `""` và cho qua 100% (dead gate)**!
   - Tương tự, `read_gate.py` dò `tool_name == "Read"` và `tool_input.file_path` (chuẩn Claude) và xuất JSON `hookSpecificOutput` thay vì tên tool `"read_file"`, khóa `toolCall.args.Path` và phản hồi `{"decision": "allow"}` của Antigravity (`docs/hooks.md:209-231`).
3. **Ngộ nhận về biến môi trường Hook (`build_portable.py:112-115` vs `docs/hooks.md:135-140`):**
   - Comment trong `build_portable.py:112-115` ghi rằng Antigravity không cấp biến môi trường thư mục plugin nên phải hardcode đường dẫn máy cài vào `hooks.json`. Thực tế `docs/hooks.md:135-140` xác nhận Antigravity **CÓ cấp sẵn `PLUGIN_ROOT` và `PLUGIN_DATA`** cho mọi plugin hook và đặt `cwd` của hook ngay tại thư mục chứa `hooks.json`.

#### Phát hiện #4 (HIGH): Lỗi Đường dẫn Hỗn hợp (`\` + `/`) & Lệnh `python3` trên Windows trong Bản Xuất Antigravity
- Quét trên `C:\Users\admin\.gemini\config\plugins\tdq-workflow\` phát hiện:
  - **`357` vị trí vẫn gọi `python3`** (ví dụ `skills/tdq-conventions/SKILL.md:45`, `hooks/scripts/_common.py:179`), dù trên Windows `python3` mặc định trỏ vào stub Microsoft Store gây lỗi `Python was not found` (chính `README.md` của bản xuất AGY cũng cảnh báo điều này nhưng nội dung các `SKILL.md` lại chưa được chuyển sang `python` / `py -3`).
  - **`158` vị trí bị nối đường dẫn hỗn hợp gạch ngược + gạch xuôi** kiểu `` `C:\Users\admin\.gemini\config\plugins\tdq-workflow/hooks/` `` hoặc `` `.../tdq-workflow/scripts/tdq_state.py` `` (do regex `_sua_duong_dan_tuong_doi_agy` tại `scripts/build_portable.py:330-360` thay thế cả danh từ thư mục văn xuôi `` `hooks/` ``, `` `scripts/` ``).

#### Phát hiện #5 (HIGH): Tham chiếu Đặc thù Claude Code Gây Nhiễu hoặc Sai Công cụ trên Antigravity
Quét toàn bộ gói `C:\Users\admin\.gemini\config\plugins\tdq-workflow\` ghi nhận:
- **`at_include_agy` (`@[label](path)`):** `0` kết quả; **`at_path_claude` (`@skills/...`):** `0` kết quả; **`CLAUDE_PLUGIN_ROOT`:** `0` kết quả (đã được `build_portable.py` thay bằng đường dẫn tuyệt đối).
- **Tên công cụ & chế độ của Claude Code còn nguyên trong Skills/Scripts:**
  - `AskUserQuestion` (**5 vị trí**, vd `skills/tdq-conventions/references/user-facing-block.md:103`) — trên Antigravity công cụ tương ứng tên là **`ask_question`**! Nếu luật chỉ cấm tên `AskUserQuestion`, model trên Antigravity vẫn có thể gọi `ask_question` mở UI trắc nghiệm vi phạm triết lý Zero-Popup.
  - `EnterPlanMode` / `ExitPlanMode` (**4 vị trí**, vd `approval.md:48`) — khái niệm riêng của Claude Code (trên Antigravity là `/plan` hoặc artifact `RequestFeedback`).
  - Tên tool `Bash`, `Read`, `Edit`, `Write`, `Grep`, `Task`/`Agent`, `WebSearch` xuyên suốt `SKILL.md` — trên Antigravity lần lượt là `run_command`, `read_file`, `edit_file`, `write_file`, `invoke_subagent`, `search_web`.
  - Tiền tố MCP `mcp__lsp__*` (**27 vị trí**, sử dụng dấu gạch dưới kép `__` của Claude Code) — trong khi Antigravity đăng ký eager MCP tools theo định dạng **`mcp_<serverName>_<toolName>`** (ví dụ nếu server trong `mcp_config.json` tên là `lsp`, tên tool trên Antigravity sẽ là **`mcp_lsp_start_lsp`**, chỉ có **1 dấu gạch dưới `_`** ngăn cách!).
  - Đường dẫn cứng `~/.claude/` (**50 vị trí**, vd `~/.claude/image-cache/`, `~/.claude/plugin-tiers.json`, `~/.claude/projects/`).
- **YAML Frontmatter lạ trong `SKILL.md`:**
  - `skills/tdq-conventions/SKILL.md` dùng `user-invocable: false` và `skills/tdq-lean/SKILL.md` dùng `argument-hint: ...` — đây là các trường frontmatter của Claude Code, không nằm trong chuẩn frontmatter `SKILL.md` của Antigravity (`name`, `description` — `agy-customizations/docs/skills.md:12-28`). Đặc biệt vì `tdq-conventions` là kho luật nền (không phải lệnh người dùng gọi), việc đặt nó làm Skill thay vì `rules/AGENTS.md` khiến nó không tự động nạp trên Antigravity.

#### Phát hiện #6 (MEDIUM — Thiết kế Kiến trúc): Tính toán Dung lượng Byte & Ngân sách Token cho `rules/AGENTS.md` trên Antigravity
Đối chiếu số đo thực tế với **trần `24,000 bytes`/file** và **ngân sách `20,000 tokens` `defaultRulesBudget`** của Antigravity (`docs/rules.md:31-40`):

| Phương án đóng gói vào `plugins/tdq-workflow/rules/AGENTS.md` | Dung lượng Byte thực tế | So với trần `24,000 B`/tệp | Ước tính Token | So với `defaultRulesBudget` (`20,000 tok`) | Đánh giá tương thích |
|---|---|---|---|---|---|
| **PA 1 (Gộp thô):** Nhét nguyên `tdq-conventions/SKILL.md` (`15,976 B`) + `soul.md` (`8,296 B`) + `chung.md` (`12,348 B`) (hoặc dùng `@[...](...)` bung tại chỗ) | **`36,620 bytes`** | **VƯỢT TRẦN `+12,620 B` (152.6%) → BỊ CẮT CỤT (TRUNCATED)!** | `~9,530 tokens` | Chiếm `47.7%` tổng ngân sách toàn máy | **KHÔNG HỢP LỆ** — vi phạm trần `24,000 B` sau khi expand `@[label](path)`. |
| **PA 2 (Chuẩn hóa từ `TDQ:TOOLS` + Core Soul + AGY Tool Mapping):** Bản tương đương `KHOI_HUONG_DAN` (`tdq_setup.py:1096-1143`, `~5,200 B`) + tóm tắt `Soul` Tier 1–3 + bảng ánh xạ tool Antigravity (`run_command`, `ask_question`, `mcp_lsp_*`) | **`~7,500 – 10,500 bytes`** | **An toàn tuyệt đối (`31% – 44%` trần `24,000 B`)** | **`~2,000 – 2,800 tokens`** | Chỉ chiếm **`10% – 14%`** ngân sách `20,000 tokens` | **TỐI ƯU NHẤT** — giữ trọn "Linh hồn" luôn bật (always-on), không bị cắt cụt, không đẩy các rule khác của user xuống thành file-path pointers, và trỏ sang `skills/tdq-intake/SKILL.md` + `skills/tdq-conventions/SKILL.md` theo đúng Progressive Disclosure. |

---

## PHẦN 4. BẢNG TỔNG HỢP CHẨN ĐOÁN & KHUYẾN NGHỊ KỸ THUẬT CHO BẢN CHUYỂN ĐỔI ANTIGRAVITY

1. **Tạo `plugins/tdq-workflow/rules/AGENTS.md` (Plain Markdown, không frontmatter, `~8–10 KB` < `24,000 B`):**
   - Đóng vai trò tương đương khối `<!-- TDQ:TOOLS -->` trong `~/.claude/CLAUDE.md` + phần nhắc đầu phiên của `session_start.py` (`TDQ:GON`, `ANTI-1..ANTI-6`), đảm bảo ngay khi bật plugin `tdq-workflow`, Antigravity luôn nạp luật tối thượng `Soul`, bắt buộc kích hoạt `tdq-intake` cho yêu cầu mới, cấm `ask_question` ở các cổng duyệt TDQ (chỉ hỏi số `1a 2b` trong chat), tuân thủ tam giác tìm kiếm 3 tầng và quy tắc Git.
   - Không dùng `@[label](path)` để nhúng tràn các file lớn vào `rules/AGENTS.md` (vì Antigravity tính trần `24,000 bytes` **sau khi đã expand** `@[label](path)` — `docs/rules.md:31-32`); thay vào đó dùng liên kết đường dẫn chuẩn để model gọi `read_file` khi vào phase tương ứng.
2. **Chuẩn hóa Bảng Ánh xạ Công cụ & MCP cho Antigravity:**
   - Ánh xạ rõ: `AskUserQuestion` → `ask_question`, `Bash` → `run_command`, `Read` → `read_file`, `Edit` → `edit_file`, `Write` → `write_file`, `Task`/`Agent` → `invoke_subagent`, `mcp__lsp__*` → `mcp_lsp_*` (1 dấu gạch dưới theo chuẩn `mcp_<serverName>_<toolName>` của Antigravity).
   - Thay `python3` bằng `python` (hoặc trình thông dịch phát hiện lúc cài) và chuẩn hóa dấu gạch chéo đường dẫn trong `build_portable.py`.
3. **Cập nhật `hooks.json` & Hook Gate Scripts đúng chuẩn Antigravity (`agy-customizations/docs/hooks.md`):**
   - Đổi cấu trúc `hooks.json` sang khóa định danh cấp cao nhất, thêm `"matcher": "run_command"` / `"read_file"` / `"edit_file|write_file"`, phẳng hóa mảng `Stop`, dùng biến `${PLUGIN_ROOT}` chính thức, và đọc đúng `toolCall.name` + `toolCall.args.CommandLine` / `toolCall.args.Path` kèm output `{"decision": "allow" | "block"}`.
   - Tận dụng thêm sự kiện `PreInvocation` / `PostInvocation` của Antigravity nếu cần kiểm soát vòng đời lượt chat tương đương `UserPromptSubmit`.
4. **Đồng bộ Đủ 12 Skills & Thư mục `agents/` lên `v0.97.0+`:**
   - Bổ sung `tdq-browser-research`, `tdq-browser-test` vào `THU_TU_SKILL` trong `scripts/build_portable.py:206-220` và xuất các định nghĩa subagent trong `agents/*.md` sang `plugins/tdq-workflow/agents/`.
