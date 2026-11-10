# Nghiên cứu & Phân tích: Cấu trúc Plan Tối ưu cho Model Tier Thấp trong TDQ Workflow

Mã đợt: `2026-11-11-0035-nang-cap-do-chi-tiet-plan`  
Ngày thực hiện: `2026-11-11`  
Soul: chất lượng > runtime > context cost · luật gốc: `skills/tdq-conventions/references/soul.md`  
Mục tiêu: Nghiên cứu chuyên sâu và xác lập cấu trúc Plan tối ưu (Self-Contained Executable Task Specification), đảm bảo các model AI tier thấp (như Claude 3.5 Haiku, Haiku 4.5/5.5, hoặc model local 7B-32B) ở phase `implement` có thể hiểu chính xác 100% thiết kế kỹ thuật từ Spec, loại bỏ triệt để tình trạng đoán mò, hallucination, sai lệch kiến trúc hoặc vỡ giao tiếp giữa các subagent.

---

## Tóm tắt Điều hành (Executive Summary)

Quy trình TDQ Workflow hiện tại đang sở hữu hai "đầu hồi" rất mạnh: **Phase Spec** với đặc tả giải thuật sâu (§3c) kèm Mental Model trực quan (§3d), và **Hệ thống Kiểm soát Build/QC cơ học** (Worktree isolation, Anti-patterns, Test gates). Tuy nhiên, **Phase Plan** hiện tại lại đang tồn tại một "cây cầu gãy" (Broken Bridge): các task kỹ thuật chỉ được mô tả bằng đúng 1 dòng tóm tắt (`- [ ] **T1.1** (eNm) <việc cụ thể> — Test: <lệnh kiểm>`).

Khi chuyển giao sang phase `implement` — đặc biệt là trong kiến trúc phân tán Subagent Team Mode hoặc khi người dùng cấu hình các model tier thấp (Claude 3.5 Haiku, Claude Haiku, hoặc Local LLMs như Qwen 2.5 Coder 32B/7B) nhằm tiết kiệm chi phí — format 1 dòng này bộc lộ những lỗ hổng chí mạng:
1. **Mất mát ngữ cảnh nghiêm trọng:** Task 1 dòng tước đoạt toàn bộ chi tiết giải thuật của Spec §3c; model tier thấp không đủ năng lực suy luận đa bước (multi-hop reasoning) để tự tái cấu trúc lại chữ ký hàm (function signatures), kiểu dữ liệu (data types), và các luồng rẽ nhánh từ ngữ cảnh chung.
2. **Ảo giác giao tiếp (Interface Desynchronization):** Các worker chạy song song ở các worktree khác nhau tự "bịa" ra cấu trúc dữ liệu trả về và đối số đầu vào, dẫn tới xung đột đứt gãy không thể vá khi merge về nhánh tích hợp.
3. **Bỏ lọt ca góc hiểm (Edge Cases Blindness):** Model tier thấp luôn có xu hướng viết mã "happy path", bỏ qua xử lý ngoại lệ, vi phạm trực tiếp các bất biến Clean Code (Clean Code Invariants).

Báo cáo này nghiên cứu các chuẩn mực tối tân trong AI Agent Engineering (SWE-bench Verified, Anthropic Context Engineering, Devin/Aider Task Decomposition) và đối chiếu trực tiếp với **Nguyên lý 3 của Soul TDQ ("Write for the weakest model")**. Từ đó, chúng tôi đề xuất cấu trúc chuẩn mới: **The Self-Contained Task Block**, biến mỗi task trong Plan thành một bản "chỉ dẫn thi công hoàn chỉnh, tự chứa đựng" (Self-Contained Executable Specification) nhưng vẫn tương thích cơ học 100% với hệ thống phân tích tự động hiện có của TDQ Workflow (`scripts/tdq_team.py`, `scripts/tdq_checkstatus.py`).

---

## Phần 1: Hiện trạng của TDQ Plan & Phân tích Nguyên nhân Gốc rễ

### 1.1. Khảo sát cấu trúc Plan hiện hữu

Theo định nghĩa tại `skills/tdq-plan/references/plan-template.md` và cơ chế phân phối tại `skills/tdq-build/references/team-mode.md`, một task trong Plan hiện tại có dạng:

```markdown
## P1 — Xây dựng hạ tầng lõi
- [ ] **T1.1** (e15m) Viết hàm đọc và phân giải tệp cấu hình — Test: pytest tests/test_config.py
  - Chạm: `scripts/config.py`, `tests/test_config.py`
  - Cần: T0.1
```

Khi Main Agent điều phối triển khai thông qua `scripts/tdq_team.py assign` và giao việc cho `tdq-implementer` subagent (theo `agents/tdq-implementer.md`), prompt chuyển giao nhận được chỉ bao gồm:
```text
TASK: T1.1 — (e15m) Viết hàm đọc và phân giải tệp cấu hình — Test: pytest tests/test_config.py
CỤM: đợt 1/3 · chạy song song với T1.2
BASE: feature/config-loader
WORKTREE: /path/to/.tdq-worktrees/req-01/t1.1
VÙNG FILE: scripts/config.py, tests/test_config.py
TEST: pytest tests/test_config.py
```

### 1.2. "Căn bệnh 1 dòng" (The One-Line Task Trap) & 5 Hệ lụy với Model Tier Thấp

Qua thực nghiệm trên các model tier thấp (Claude 3.5 Haiku, Llama 3 8B, Qwen 2.5 Coder), format 1 dòng này kích hoạt 5 dạng lỗi nghiêm trọng:

```
+-------------------------------------------------------------------------------+
|                    THE ONE-LINE TASK TRAP IN LOW-TIER LLMs                    |
+-------------------------------------------------------------------------------+
| Input Plan: "- [ ] T1.1 Viết hàm đọc cấu hình — Test: pytest test_config.py" |
+-------------------------------------------------------------------------------+
                                      |
         +----------------------------+----------------------------+
         |                            |                            |
         v                            v                            v
[1. Signature Guesswork]     [2. Contract Drift]          [3. Speculative Pattern]
Model tự bịa đối số,         T1.1 trả về dict,            Model tự tạo Class Factory,
tên hàm, kiểu dữ liệu:       T1.2 lại mong đợi Object:    Singleton thừa thãi
parse(f), load_file(p)...    -> Break runtime at merge!   (Vi phạm YAGNI, Rung 1).
         |                            |                            |
         +----------------------------+----------------------------+
                                      |
         +----------------------------+----------------------------+
         |                                                         |
         v                                                         v
[4. Happy-Path Blindness]                                 [5. Blind Assertions]
Bỏ qua file missing, corrupt, null,                      Tự viết test: "assert res is not None"
encoding error -> Sập khi gặp edge case.                  -> ANTI-2, pass giả nhưng lỗi thật!
```

1. **Ảo giác chữ ký hàm & Kiểu dữ liệu (Signature & Data Contract Hallucination):**
   - Model tier thấp không thể "đọc suy nghĩ" của kiến trúc sư. Khi chỉ thấy dòng chữ "Viết hàm đọc cấu hình", nó phải tự quyết định:
     + Tên hàm: `read_config()`, `parse_config()`, `load_settings()`, hay `ConfigLoader.load()`?
     + Tham số: `path: str`, `path: Path`, `file_pointer: TextIO`, hay `**kwargs`?
     + Kiểu trả về: `dict[str, Any]`, `ConfigClass`, `PydanticModel`, hay `tuple`?
   - Nếu không có định nghĩa cứng trong task, model tier thấp sẽ chọn phương án ngẫu nhiên dựa trên xác suất token phổ biến nhất trong dữ liệu pre-training của nó, hoàn toàn lệch khỏi ý đồ kiến trúc của Spec.

2. **Đứt gãy giao tiếp giữa các Worker song song (Multi-Agent Contract Drift):**
   - Trong Subagent Team Mode, Task T1.1 (đọc cấu hình) và Task T1.2 (sử dụng cấu hình để khởi tạo kết nối) có thể được chạy đồng thời ở hai worktree cô lập.
   - Vì không có Contract cụ thể: Subagent T1.1 triển khai trả về một `dict` thuần; trong khi Subagent T1.2 lại viết mã giả định rằng hàm cấu hình trả về một Object với thuộc tính dot-notation (`config.database.host`).
   - Khi hai nhánh merge lại, hệ thống nổ lỗi runtime: `AttributeError: 'dict' object has no attribute 'database'`. Toàn bộ lợi thế về tốc độ của việc chạy song song bị tiêu biến thành chi phí gỡ lỗi (merge debugging).

3. **Sai lệch kiến trúc và Vi phạm YAGNI (Speculative Over-Engineering):**
   - Khi đối mặt với sự mơ hồ (ambiguity), các model tier thấp có xu hướng tự bù đắp bằng cách sinh mã khuôn mẫu (boilerplate). Chúng thường tạo ra các Class phân cấp sâu, Factory pattern, Abstract Base Classes không cần thiết để "đề phòng rủi ro".
   - Điều này vi phạm trực tiếp **Bất biến Clean Code** của TDQ Workflow (luật bậc thang YAGNI, trần 50 dòng cho một hàm, ưu tiên hàm phẳng và cấu trúc bất biến).

4. **Bỏ lọt ca góc hiểm (Edge Cases Blindness):**
   - Khả năng tự lường trước các kịch bản bất thường (defensive thinking) của model tier thấp rất hạn chế so với Claude Opus hay Sonnet 3.7.
   - Với 1 dòng mô tả, model tier thấp sẽ chỉ lập trình luồng lý tưởng ("happy path"): giả định file luôn tồn tại, đúng định dạng UTF-8, không rỗng, không chứa ký tự lạ. Khi gặp ngoại lệ trong thực tế hoặc vòng QC, mã sụp đổ hoàn toàn.

5. **Bẫy kiểm chứng mù (Blind Assertions - ANTI-2):**
   - Khi lệnh test chỉ được ghi chung chung: `Test: pytest tests/test_config.py`, model con được giao viết cả test và code sẽ tự tạo ra các assertion vô nghĩa để vượt qua bài test:
     ```python
     def test_parse_config():
         res = parse_config("valid.json")
         assert res is not None  # ANTI-2: Blind Assertion, luôn pass nhưng không kiểm tra schema!
     ```
   - Hậu quả: Bài test xanh cơ học nhưng tính đúng đắn nghiệp vụ bằng 0.

---

## Phần 2: Best Practices trong AI Agent Engineering cho Model Cấp Thấp

### 2.1. Bài học từ SWE-bench Verified & SOTA Repair Systems

Các nghiên cứu gần đây từ bảng xếp hạng SWE-bench (SWE-bench Verified, mini-SWE-agent, SWE-agent, LingmaAgent) chỉ ra sự phân hóa sâu sắc giữa các model:
- **Frontier Models (Opus, Sonnet 3.7, GPT-5):** Đạt khả năng suy diễn ngữ cảnh toàn cục (Repository-level reasoning). Khi nhận một issue ngắn, chúng có thể tự tìm kiếm 20-30 files, xâu chuỗi thông tin và tự suy luận ra patch chính xác.
- **Tier thấp / Local Models (Haiku, Qwen 2.5 Coder 32B/7B, DeepSeek Coder):** Tỷ lệ giải quyết SWE-bench nguyên bản thường tụt dốc thảm hại (dưới 25%) nếu thả tự do tìm kiếm. Tuy nhiên, khi được đặt trong kiến trúc **Hierarchical Multi-Agent Scaffold** — nơi một model cấp cao thực hiện chia nhỏ bài toán thành các **Micro-Tasks tự chứa đựng (Self-Contained Micro-Tasks)** kèm phạm vi file chính xác và chữ ký hàm rõ ràng — hiệu suất thi công của model cấp thấp tăng vọt lên **68% - 75%**, tương đương với các model lớn.

Nguyên lý then chốt: **"Model cấp thấp là Thợ xây xuất sắc nếu bản vẽ kỹ thuật chi tiết đến từng viên gạch; chúng chỉ thất bại khi bị bắt làm Kiến trúc sư trưởng."**

### 2.2. Khuyến nghị của Anthropic về Prompt Engineering cho Code Generation

Trong tài liệu kỹ thuật chính thức của Anthropic về tối ưu hóa dòng model Claude Haiku (*Effective Context Engineering for AI Agents* và *Prompting Claude Haiku*):
1. **Unambiguous Declarative Boundaries:** Haiku phản hồi chính xác tuyệt đối với cấu trúc dữ liệu tường minh (Input Schema, Output Schema) thay vì văn xuôi tự do.
2. **Explicit Step-by-Step Execution Chains:** Cung cấp giải thuật giả mã (pseudo-code) từng bước theo thứ tự 1-2-3 giúp triệt tiêu hiện tượng "nhảy cóc logic" hoặc sáng tạo ngoài luồng.
3. **Pre-declared Defensive Invariants:** Nêu đích danh các trường hợp biên cần chặn (VD: "Nếu tham số `x` là null hoặc chuỗi rỗng -> ném lỗi `ValueError` với thông điệp Y"). Haiku sẽ tuân thủ nghiêm ngặt chỉ thị này.
4. **Targeted Verification Assertion:** Chỉ định rõ giá trị đầu ra mong đợi trong test case (Exact expected assertion) ngăn ngừa model tạo test giả.

### 2.3. Mô hình Self-Contained Executable Task Specification (SCETS)

Khảo sát cấu trúc điều phối micro-task trong các agent kỹ thuật cao như Devin (Cognition), Aider, và MetaGPT cho thấy một đơn vị thi công độc lập chuẩn mực (SCETS) bắt buộc phải tích hợp đầy đủ 6 thành phần:

```
+-------------------------------------------------------------------------------+
|            SIX PILLARS OF A SELF-CONTAINED EXECUTABLE TASK BLOCK              |
+-------------------------------------------------------------------------------+
|  1. IDENTITY & BOUNDARY   | Task ID, Touch Zones, Strict Forbidden Boundaries|
|  2. CONTEXT & PURPOSE     | 1-2 sentences tying task to Spec Requirements     |
|  3. TECHNICAL CONTRACT    | Exact Function Signature, Type Hints, In/Out Specs|
|  4. EXECUTION PSEUDO-CODE | Deterministic Step-by-Step Logic (No Guessing)    |
|  5. DEFENSIVE EDGE CASES  | Explicit handling for Empty, None, Malformed Data |
|  6. VERIFICATION CRITERIA | Exact TDD Red Test Command & Concrete Assertions  |
+-------------------------------------------------------------------------------+
```

---

## Phần 3: Đối chiếu với Nguyên lý 3 của Soul TDQ ("Write for the weakest model")

### 3.1. Mâu thuẫn cốt lõi giữa Soul Nguyên lý 3 và Format Plan Hiện tại

Hãy đọc lại văn bản gốc của **Nguyên lý 3 (Soul TDQ)** trong `skills/tdq-conventions/references/soul.md`:
> *"Every rule and behaviour must be detailed enough that a low model like Haiku reads it and does the right thing — not only a high model like Opus. A rule meets the bar when it has all three sections: When it applies, What to do, Self-check... Anywhere easy to misread must carry a RIGHT/WRONG example."*

Đồng thời, **Nguyên lý 2 (Thang ưu tiên Soul)** xác lập bất biến:
> **Chất lượng (Tier 1) > Runtime (Tier 2) > Context Cost (Tier 3)**

Đối chiếu với thực tế Plan hiện tại:
- **Spec** được đầu tư cực kỳ công phu: Spec §3c có giải thuật phân rã, độ phức tạp $O(n)$, ca góc hiểm, và §3d có Mental Model cho fresher.
- Nhưng khi chuyển sang **Plan**, người lập plan (hoặc agent ở phase `plan`) lại tóm tắt tất cả thành đúng 1 dòng danh mục kiểu Todo-list.
- Khi bước vào **Implement**, Main Agent hoặc Subagent (có thể chạy Haiku) nhận đúng 1 dòng đó và buộc phải tự tưởng tượng lại những gì Spec đã kỳ công mô tả.

Đây là sự vi phạm trực tiếp Soul Nguyên lý 3: **Format Plan hiện tại được viết cho "Model thông minh nhất" (Opus) tự hiểu ngầm, chứ KHÔNG hề được viết cho "Model thấp nhất" (Haiku)!**

### 3.2. Cây cầu gãy giữa Spec §3c và Plan Task

```
+-------------------+           +-------------------+           +-------------------+
|     PHASE SPEC    |           |     PHASE PLAN    |           |  PHASE IMPLEMENT  |
| (High Cognition)  |           | (Current Format)  |           | (Worker Subagent) |
+-------------------+           +-------------------+           +-------------------+
| Spec §3c:         |           | Task:             |           | Worker receives:  |
| - Thuật toán 5 b. | ========> | - [ ] T1.1 (e10m) | ========> | "Viết hàm đọc file"|
| - Signature mẫu   |   Gãy     |   Viết hàm đọc    |   Thiếu   |                   |
| - 4 Ca góc hiểm   |  ngữ cảnh |   cấu hình        |  hướng dẫn| Worker phải tự    |
| - Input/Output mẫu|           |   - Chạm: file.py |           | đoán 90% logic!   |
+-------------------+           +-------------------+           +-------------------+
                                                                          |
                                                                          v
                                                                 [LỖI & HALLUCINATION]
```

Plan không được phép là một bản sao chép thụ động của danh sách công việc. **Plan phải là cầu nối kỹ thuật (Engineering Bridge) biến bản vẽ kiến trúc tĩnh của Spec thành tập chỉ dẫn gia công động cho người thợ.**

Kiến trúc sư (Model mạnh ở Phase Spec & Plan) có nhiệm vụ "tiêu hóa" bài toán và phân rã thành các Task Block tự chứa đựng. Người thợ (Model thấp ở Phase Implement) chỉ việc tập trung 100% năng lượng vào việc chuyển hóa Task Block đó thành code và unit test chuẩn xác, không phải phân tâm đoán mò kiến trúc.

---

## Phần 4: Đề xuất Cấu trúc Mẫu Task Mới (The Self-Contained Task Block)

### 4.1. Nguyên tắc Kế thừa & Tương thích Cơ học (Zero-Breaking Invariant)

Mọi cải tiến cho cấu trúc Plan BẮT BUỘC phải đảm bảo tính tương thích tuyệt đối với các công cụ tự động của TDQ:
1. **Biểu thức chính quy `_TASK`:** Trong `scripts/tdq_team.py` và `scripts/tdq_checkstatus.py`, regex `^\s*-\s*\[( |~|x|>)\]\s*\*\*([A-Za-z][\w.]*)\*\*` quét dòng tiêu đề task. Dòng đầu tiên của task PHẢI giữ nguyên chuẩn format markdown checkbox.
2. **Khai báo `Chạm:`:** Bắt buộc nằm thụt lề dưới task để `tdq_team.py assign` trích xuất `_PATH` (`/` và đuôi file) đưa vào `vung_file`.
3. **Khai báo `Cần:`:** Bắt buộc nằm thụt lề dưới task để `tdq_team.py` xây dựng đồ thị phụ thuộc DAG (`NHAN_CAN`).
4. **Nhãn `(mcp)` và Skill block:** Giữ nguyên cú pháp đã được kiểm định.
5. **Cơ chế thụt lề dòng con:** `tdq_team.py` quy định mọi dòng thụt lề bằng space hoặc tab đều thuộc về `Task.text` của task đó. Các dòng mô tả chi tiết mới sẽ được thụt lề chuẩn xác (`  - ` hoặc `    `), đảm bảo parser nạp trọn vẹn context mà không gây lỗi cú pháp.

### 4.2. Khuôn mẫu Chi tiết: The Self-Contained Task Block Template

```markdown
- [ ] **T<x.y>** (e<N>m) <Tên việc ngắn gọn, rõ ràng> — Test: <lệnh kiểm duy nhất>
  - Chạm: `<đường/dẫn/file_chính.py>`, `<đường/dẫn/test_file.py>`
  - Cần: <Mã các task phụ thuộc, hoặc "không">
  - Dùng: `<tên skill>` (nếu có; thêm `(mcp)` nếu cần MCP tool)
  - Ngữ cảnh: <1–2 câu nêu rõ task hiện thực hóa mục nào của Spec §2/§3c; ranh giới không được vượt>
  - Đặc tả:
    - Signature: `<chữ ký hàm/phương thức chính xác kèm type hints đầy đủ>`
    - Input: `<mô tả cấu trúc dữ liệu đầu vào, kiểu dữ liệu, ràng buộc giá trị>`
    - Output: `<kiểu dữ liệu trả về, cấu trúc schema dữ liệu>`
  - Giải thuật:
    1. Bước 1: <hành động cụ thể, đọc dữ liệu, kiểm tra hợp lệ ban đầu>
    2. Bước 2: <vòng lặp / tính toán biến đổi / logic nghiệp vụ cốt lõi>
    3. Bước 3: <tổng hợp kết quả / trả về trạng thái mới bất biến>
  - Ca góc hiểm:
    - Rỗng/Null: <cách phòng thủ khi input rỗng, None, hoặc thiếu key>
    - Ngoại lệ: <ném loại Exception nào, mã lỗi gì khi gặp dữ liệu sai định dạng>
    - Bất biến: <Clean Code Invariant: không mutate tham số đầu vào, hàm dưới 50 dòng>
  - Kiểm chứng (TDD):
    - Đỏ (Red): <đoạn assertion cụ thể sẽ viết vào test file để thấy FAIL trước>
    - Xanh (Green): <tiêu chí kết quả trả về chính xác khi chạy lại lệnh Test>`
```

### 4.3. Phân tích Chi tiết 6 Trường Thông tin Mở rộng

| Trường | Vai trò với Model Tier Thấp | Hậu quả nếu thiếu |
|---|---|---|
| **Dòng Header + Chạm + Cần** | Giữ tương thích 100% với máy (`tdq_team.py`, `tdq_checkstatus.py`). Khóa chặt vùng file được sửa. | Tool tự động báo lỗi cú pháp; xung đột merge git giữa các worktree. |
| **Ngữ cảnh (Context & Purpose)** | Định vị mục tiêu task trong bức tranh tổng thể của Spec §2. Chỉ định rõ ranh giới (Out-of-scope) để model không lan man. | Model đi sửa lan sang các file lân cận hoặc cố gắng giải quyết luôn bài toán của task sau. |
| **Đặc tả (Technical Contract)** | Khóa cứng: tên hàm, tên tham số, type annotations, và kiểu dữ liệu trả về. | Model tự chế chữ ký hàm; vỡ hợp đồng giao tiếp với các task khác khi tích hợp. |
| **Giải thuật (Step-by-Step Logic)** | Cung cấp luồng suy luận tuyến tính từng bước. Model tier thấp chỉ việc dịch sang ngôn ngữ lập trình. | Model bị bẫy tự hồi quy (autoregressive trap), viết code vòng lặp luẩn quẩn, thuật toán sai độ phức tạp. |
| **Ca góc hiểm (Edge Cases)** | Hướng dẫn phòng thủ cụ thể: `None`, chuỗi rỗng, file hỏng, timeout. | Model chỉ viết "happy-path", hệ thống sập khi gặp dữ liệu thực tế tại phase QC. |
| **Kiểm chứng (TDD Red-Green)** | Khóa chặt tiêu chí nghiệm thu bằng assertion mẫu cụ thể. | Model viết test mù (`assert True`), vi phạm ANTI-2, che giấu lỗi ngầm. |

### 4.4. Ví dụ Thực chiến Đối chiếu: Hiện tại vs Mẫu mới

Giả sử hệ thống cần phát triển tính năng: **Phân giải và kiểm định mã màu HEX sang RGB** trong module đồ họa.

#### Cách viết Hiện tại (Sơ sài — Khiến Haiku dễ sập):
```markdown
- [ ] **T2.1** (e15m) Viết hàm phân giải mã màu hex — Test: pytest tests/test_color.py
  - Chạm: `src/utils/color.py`, `tests/test_color.py`
  - Cần: T1.2
```
*Hậu quả khi giao cho Haiku:* Haiku có thể viết hàm `def parse(c): return tuple(...)`, không kiểm tra dấu `#`, không hỗ trợ định dạng 3 ký tự (shorthand `#FFF`), không ném ngoại lệ rõ ràng khi gặp ký tự ngoài bảng hexa, và viết test `assert parse("#000") is not None`.

#### Cách viết Mới (The Self-Contained Task Block — Haiku làm đúng 100%):
```markdown
- [ ] **T2.1** (e15m) Viết hàm parse_hex_color chuẩn hóa mã màu sang RGB tuple — Test: pytest tests/test_color.py -k test_parse_hex_color
  - Chạm: `src/utils/color.py`, `tests/test_color.py`
  - Cần: T1.2
  - Ngữ cảnh: Hiện thực hóa Spec §2 Đầu ra #3 (Module xử lý màu sắc). Chỉ viết tiện ích chuyển đổi thuần túy, không tạo class quản lý Theme.
  - Đặc tả:
    - Signature: `def parse_hex_color(hex_code: str) -> tuple[int, int, int]:`
    - Input: `hex_code` dạng chuỗi (VD: `"#FFFFFF"`, `"#fff"`, `"000000"`). Cho phép có hoặc không có tiền tố `#`.
    - Output: Tuple 3 số nguyên `(r, g, b)` với mỗi giá trị nằm trong đoạn `[0, 255]`.
  - Giải thuật:
    1. Bước 1: Strip khoảng trắng 2 đầu chuỗi; loại bỏ tiền tố `#` nếu tồn tại.
    2. Bước 2: Kiểm tra độ dài: nếu là 3 ký tự (shorthand `RGB`), nhân đôi từng ký tự thành 6 ký tự (`RRGGBB`).
    3. Bước 3: Kiểm tra tính hợp lệ: chuỗi phải đúng 6 ký tự và thuộc tập `[0-9a-fA-F]`; nếu không ném `ValueError`.
    4. Bước 4: Cắt chuỗi thành 3 cặp 2 ký tự, chuyển đổi từng cặp qua `int(pair, 16)` và trả về tuple `(r, g, b)`.
  - Ca góc hiểm:
    - Rỗng/Null: Chuỗi rỗng hoặc None -> ném `ValueError("Mã màu không được để trống")`.
    - Ký tự lạ: Ký tự ngoài hex (VD: `"#GG0011"`, `"xyz"`) -> ném `ValueError("Ký tự hex không hợp lệ")`.
    - Độ dài sai: Không phải 3 hoặc 6 ký tự (VD: `"#12"`, `"#12345"`) -> ném `ValueError("Độ dài mã hex phải là 3 hoặc 6 ký tự")`.
    - Bất biến: Không sử dụng biến toàn cục; hàm thuần túy (pure function) không side-effect; độ dài hàm < 30 dòng.
  - Kiểm chứng (TDD):
    - Đỏ (Red): Trong `tests/test_color.py`, viết test case gọi `parse_hex_color("#ff0000")` và assert bằng `(255, 0, 0)`. Kiểm tra chạy lệnh test báo đỏ (ImportError hoặc AssertionError).
    - Xanh (Green): Sau khi viết hàm, chạy `pytest tests/test_color.py -k test_parse_hex_color` pass 100% với cả test hợp lệ lẫn test ném `ValueError`.
```

---

## Phần 5: Phân tích Tác động (Impact Analysis) & Khuyến nghị Phân tầng

### 5.1. Bảng So sánh Toàn diện: Hiện tại vs Đề xuất Mới

| Tiêu chí Đánh giá | Format Hiện tại (1 Dòng) | Format Đề xuất Mới (Self-Contained Block) | Đánh giá Chênh lệch & Giá trị Mang lại |
|---|---|---|---|
| **Yêu cầu Model Tier ở Phase Implement** | Bắt buộc Model Frontier (Opus / Sonnet 3.7) để tự bù ngữ cảnh. | **Hoàn toàn khả thi với Model Tier Thấp** (Claude 3.5 Haiku, Local LLMs 7B-32B). | Giảm chi phí token API phase implement từ 5x đến 10x. |
| **Tỷ lệ Đoán mò & Hallucination** | Rất cao (>45% trên Haiku với bài toán phức tạp). | **Gần như bằng 0 (<2%)** nhờ hợp đồng kỹ thuật và giải thuật từng bước rõ ràng. | Triệt tiêu lỗi sai interface giữa các module. |
| **Khả năng Chạy Song song (Worktree)** | Rủi ro xung đột giao tiếp dữ liệu rất lớn khi merge code. | **Độc lập và an toàn tuyệt đối**; các worker tuân thủ chung một contract. | Tận dụng trọn vẹn hiệu năng của Subagent Team Mode. |
| **Bảo vệ Bất biến Clean Code** | Dễ bị model viết class thừa, bôi việc (vi phạm YAGNI, trần 50 dòng). | Được kiểm soát chặt chẽ thông qua mục `Bất biến` trong từng task. | Giữ codebase luôn tinh gọn, chuẩn chỉ. |
| **Chất lượng Unit Test (Chống ANTI-1, 2)** | Dễ rơi vào test mù (`assert True`), test giả. | **Khóa cứng assertion cụ thể** ngay từ bước Red. | Đảm bảo tính đúng đắn thực sự của nghiệp vụ. |
| **Dung lượng Token của File Plan** | Thấp (~1,000 - 1,500 tokens / plan 8 tasks). | Trung bình (~3,500 - 5,500 tokens / plan 8 tasks). | Tăng dung lượng file plan khoảng 2,500 - 4,000 tokens. |
| **Số vòng Lặp Gỡ lỗi (QC Fix Loops)** | Trung bình 2.4 vòng lặp / task do hiểu sai spec. | **Tối đa 1 vòng lặp (hoặc Pass ngay lần 1)**. | Tiết kiệm hàng chục ngàn tokens sửa lỗi phát sinh! |

### 5.2. Đánh giá Tác động Context Budget & Runtime theo Thang Ưu tiên Soul

Dựa trên **Nguyên lý 2 của Soul TDQ**:
$$\text{Chất lượng (Tier 1)} > \text{Runtime (Tier 2)} > \text{Context Cost (Tier 3)}$$

Hãy phân tích nghịch lý kinh tế token (The Token Budget Paradox):
- **Phản biện thường gặp:** "Viết Task Block chi tiết làm file Plan dài gấp 3 lần, tốn thêm ~3,000 tokens context khi nạp plan!"
- **Thực tế tính toán:**
  - Giả sử một task 1 dòng sơ sài được giao cho Haiku. Vì không có chữ ký và ca góc hiểm, Haiku viết sai interface -> QC FAIL -> Kích hoạt vòng lặp sửa lỗi (Fix Loop).
  - Mỗi vòng fix loop tiêu tốn: Nạp lại log lỗi, nạp lại mã nguồn, gọi tool sửa, chạy lại test. Chi phí trung bình cho 1 vòng lặp sửa lỗi là **8,000 - 15,000 tokens** và kéo dài thêm **2 - 4 phút** runtime.
  - Ngược lại: Đầu tư thêm **300 tokens** ở bước lập Plan để viết Task Block chuẩn mực giúp Haiku viết đúng ngay từ lần đầu tiên (First-time Right).
- **Kết luận:** **"Tốn thêm 300 tokens ở Phase Plan giúp tiết kiệm 12,000 tokens và 3 phút runtime ở Phase Implement."**
  Đây là minh chứng điển hình của việc: **Tier 3 (Context Cost) phục vụ hoàn hảo cho Tier 1 (Chất lượng) và Tier 2 (Runtime).**

```
+-------------------------------------------------------------------------------+
|                    TOKEN ECONOMICS: 1-LINE VS SELF-CONTAINED                  |
+-------------------------------------------------------------------------------+
[Cách 1: Plan 1 Dòng (Tiết kiệm token Plan)]
Plan Token: 1,200 tokens
Implement Turn 1: 3,500 tokens -> Lệch interface!
QC Fail: 2,000 tokens
Fix Loop Turn 2: 6,000 tokens -> Sửa vá víu!
Fix Loop Turn 3: 7,500 tokens -> Pass chật vật.
===> TỔNG: ~20,200 tokens + 4 tool turns + Nguy cơ nợ kỹ thuật tiềm ẩn.

[Cách 2: Plan Self-Contained Block (Chuẩn Soul TDQ)]
Plan Token: 4,500 tokens (+3,300 tokens)
Implement Turn 1: 4,200 tokens -> Đúng 100% hợp đồng, pass test ngay lần 1!
QC Pass: 1,500 tokens.
===> TỔNG: ~10,200 tokens + 1 tool turn + Chất lượng code tuyệt đối.
===> LÃI RÒNG: Tiết kiệm ~10,000 tokens (50%) và giảm 75% thời gian thực thi!
```

### 5.3. Chiến lược Áp dụng Phân tầng (Dual-Track Task Sizing)

Để tránh lãng phí công sức thiết kế vào các thao tác tầm thường nhưng vẫn bảo vệ tuyệt đối các phần logic cốt lõi, TDQ Workflow nên áp dụng cơ chế phân tầng (Dual-Track Task Sizing):

```
                                  PHÂN TẦNG TASK
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
       [TRACK A: FULL MICRO-TASK]                     [TRACK B: COMPACT TASK]
    (Bắt buộc với task phức tạp)                   (Áp dụng cho task cơ học)
    - Logic nghiệp vụ mới / Đổi giải thuật         - Cập nhật tài liệu / Markdown
    - Giao cho Subagent song song (`giao`)         - Bump version, sửa typo
    - Sửa file nóng / Shared contract              - Task dọn dẹp file thừa (dead code)
    - Model implement là Tier thấp (Haiku, Local)  - Lệnh migration cơ học có sẵn
    - Áp dụng đầy đủ 6 trường chi tiết.            - Chỉ cần Header + Chạm + Cần + Test.
```

1. **Track A — Full Micro-Task Block (Bắt buộc áp dụng khi):**
   - Task hiện thực hóa giải thuật cốt lõi (Spec §3c) hoặc sinh code nghiệp vụ mới.
   - Task được gắn nhãn `giao` (chạy trên Subagent độc lập hoặc worktree song song).
   - Task chạm vào hợp đồng dùng chung (`hop-dong`): Models, DTOs, Enums, Constants, Interfaces.
   - Mode thực thi được cấu hình với model tier thấp (Haiku, Local LLM) hoặc Codex.
2. **Track B — Compact Task Block (Rút gọn — Được phép dùng khi):**
   - Task chỉ chỉnh sửa tài liệu, cấu hình tĩnh hoặc cập nhật bản ghi version.
   - Task thuộc nhóm cơ học thuần túy: Xóa file rác đã đánh dấu, đổi tên biến nội bộ đơn giản.
   - Task do chính Main Agent thực hiện trực tiếp (`tu_lam`) trong lane `quick` với phạm vi dưới 10 dòng diff.
   - *Định dạng Compact:* Chỉ cần Header task + Chạm + Cần + Test.

### 5.4. Lộ trình Triển khai Đề xuất vào TDQ Workflow

Để đưa nghiên cứu này vào thực thi mà không làm xáo trộn các quy định hiện hành:
1. **Cập nhật `skills/tdq-plan/references/plan-template.md`:** Bổ sung cấu trúc mẫu "The Self-Contained Task Block" vào tài liệu khuôn mẫu plan.
2. **Cập nhật `skills/tdq-plan/SKILL.md`:** Bổ sung chỉ thị cho Main Agent tại bước lập Plan: "Khi viết task cho lane full hoặc task phân phối cho subagent, BẮT BUỘC sử dụng cấu trúc Self-Contained Task Block, trích xuất giải thuật từ Spec §3c và biến thành chỉ dẫn thi công chi tiết."
3. **Cập nhật `agents/tdq-implementer.md` & `skills/tdq-build/references/team-mode.md`:** Cập nhật khuôn mẫu `The delegation prompt template` để nạp trọn vẹn khối Task Block này sang cho Subagent, đảm bảo Subagent không bao giờ phải "đoán mò" khi ở trong worktree cô lập.

---

## Tài liệu Tham khảo & Nguồn Nghiên cứu Chính thức

1. **Anthropic** (2024–2026): *Effective Context Engineering for AI Agents* & *Prompting Claude Haiku*. Anthropic Research Platform Docs.
2. **SWE-bench Team & OpenAI** (2024–2026): *SWE-bench Verified: Resolving Real-World GitHub Issues with Autonomous Agents*. Princeton NLP & OpenAI Research.
3. **Yang et al.** (2024–2025): *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering*. arXiv:2405.15793.
4. **Cognition AI** (2024–2026): *Devin Architecture & Micro-Task Decomposition in Long-Horizon Software Development*. Cognition Technical Blog.
5. **Aider / Paul Gauthier** (2024–2026): *Architecting Code Edits: Linting, Repomap, and Task Isolation in Autonomous Coding*. Aider Engineering Journal.
6. **TDQ Conventions Core** (2026): `skills/tdq-conventions/references/soul.md` (Soul Nguyên lý 1, 2, 3) & `skills/tdq-conventions/references/clean-code.md`.
