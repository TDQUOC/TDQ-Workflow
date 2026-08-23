# PLAN — Skill `tdq-lsp-setup`: nhúng agent-lsp vào bộ workflow

Ngày: 2026-08-23 · Spec: ../spec/2026-08-23-0052-skill-tdq-lsp-setup.md (bản 1.4, ĐÃ DUYỆT) · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Mode thực thi: subagent — mô phỏng trên chính plan này cho 20 task, 5 đợt, đội thắng 12.2 phút (28.6 so với 40.7), giao được 6 task ở P2 và P3 vì vùng file rời nhau
Trạng thái plan: HOÀN THÀNH (còn T4.5/Q12/Q30 treo tới phiên sau) · duyệt (2026-08-23T01:43:44+07:00, user nhắn "duyệt plan") · Mode chốt: main (user chọn "b")

## Mục lục

- Quy tắc thi hành (áp cho mọi task)
- P1 — Script chẩn đoán `tdq_lsp.py`
- P2 — Skill `tdq-lsp-setup`
- P3 — Móc vào 4 skill workflow
- P4 — Dựng môi trường thật trên máy
- P5 — Log & test bắt buộc
- P6 — Chốt sổ
- Cụm song song
- Definition of Done

## Quy tắc thi hành (áp cho mọi task)

1. Thứ tự phase là thứ tự phụ thuộc — không đảo.
2. Mỗi task: đánh `[~]` khi bắt đầu → viết test trước (đỏ) → code → test xanh → đổi sang
   `[x]` NGAY vào file này. Trạng thái checkbox: `[ ]` chưa làm · `[~]` đang làm · `[x]` xong.
3. Sau mỗi phase: chạy toàn bộ test suite, phải xanh mới sang phase sau.
4. Lệnh nào chạm state của workflow phải có `TDQ_PROJECT_DIR=<thư mục tạm>` ngay trên chính lệnh đó.
5. QC FAIL → thêm task fix vào mục QC của file này (không cần duyệt lại), loop đến khi pass.
6. Không commit/push cho đến khi user yêu cầu.
7. **Riêng P4: mọi lệnh cài đặt và mọi lệnh sửa file ngoài repo phải XIN PHÉP user trước khi
   chạy.** Đây là mặt C user chốt ở vòng 1, không có ngoại lệ nào cho "chặn kỹ thuật".

## P1 — Script chẩn đoán `tdq_lsp.py`

- [x] **T1.1** (e25m) Tạo `scripts/tdq_lsp.py`: khung lệnh con, log service có timestamp kèm cờ tắt, và lệnh `kiem` chạy bậc 1–4 (binary `agent-lsp` · MCP `lsp` đã đăng ký · language server theo ngôn ngữ project · quyền tool `mcp__lsp__*`) — Test: `.venv/bin/python scripts/tdq_lsp.py kiem` in 4 bậc, mỗi bậc có nhãn ĐẠT hoặc THIẾU, bậc THIẾU in kèm lệnh cài
  - Chạm: `scripts/tdq_lsp.py` → file mới, chưa node nào phụ thuộc
- [x] **T1.2** (e20m) Thêm bậc 5 (sức khoẻ lumen: phân biệt thiếu ollama · ollama không chạy · thiếu model) và bậc 6 (dò hook plugin đang bật giục thứ tự tìm kiếm khác TDQ, in đường dẫn file hook). Cả hai bậc chỉ CẢNH BÁO, không trả mã chặn — Test: `.venv/bin/python scripts/tdq_lsp.py kiem` in đủ 6 bậc; tắt Ollama vẫn trả mã cho phép làm tiếp
  - Chạm: `scripts/tdq_lsp.py` → sau `T1.1`
  - Cần: T1.1
- [x] **T1.3** (e18m) Thêm lệnh con `danh-thuc` (bật `ollama serve` nền, chờ cổng 11434 trong hạn chờ, đang chạy sẵn thì không bật thêm) và `nha` (gọi `ollama stop` đúng model embedding của lumen; chỉ tắt daemon khi chính script bật nó trong phiên, có ghi dấu) — Test: tắt Ollama → `danh-thuc` làm cổng 11434 trả lời → `nha` làm model biến khỏi `ollama ps`
  - Chạm: `scripts/tdq_lsp.py` → sau `T1.2`
  - Cần: T1.2

- [x] **T1.4** (e8m) Lỗi phát hiện khi chạy thử T1.3: trên macOS, `ollama stop` làm Ollama.app TỰ BẬT server nếu nó đang tắt — đúng thứ ta muốn giữ ngủ. Chặn `nha` gọi `ollama stop` khi cổng 11434 không trả lời — Test: máy đang tắt Ollama, chạy `nha` xong `pgrep -f "ollama serve"` vẫn rỗng
  - Chạm: `scripts/tdq_lsp.py` → sau `T1.3`
  - Cần: T1.3

**Xong P1 khi**: `tdq_lsp.py kiem` in đủ 6 bậc, `danh-thuc` và `nha` chạy thật được trên máy.

## P2 — Skill `tdq-lsp-setup`

- [x] **T2.1** (e18m) Viết `skills/tdq-lsp-setup/SKILL.md`: link repo `https://github.com/blackwell-systems/agent-lsp`, thang kiểm 6 bậc, cách dựng lại từ số 0 trên máy mới, luật "thấy hook xung đột thì nêu đường dẫn và xin phép user, cấm tự sửa file plugin". Chỉ NHẮC TÊN lệnh của `tdq_lsp.py`, không chép nội dung script — Test: file có link repo, có đủ 6 bậc, không chứa khối mã Python nào
  - Chạm: `skills/tdq-lsp-setup/SKILL.md` → file mới, chưa node nào phụ thuộc
- [x] **T2.2** (e15m) Viết `skills/tdq-lsp-setup/references/languages.md`: bảng 30 ngôn ngữ chép từ `docs/reference/language-support.md` của repo agent-lsp, mỗi dòng đủ tên language server và lệnh cài — Test: đếm được đúng 30 dòng ngôn ngữ, mỗi dòng có cả tên server lẫn lệnh cài
  - Chạm: `skills/tdq-lsp-setup/references/languages.md` → file mới, chưa node nào phụ thuộc
- [x] **T2.3** (e20m) Viết `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md` — file luật GỐC, 4 chỗ móc ở P3 chỉ trỏ về đây. Gồm: thứ tự `agent-lsp` chạy trước, `lumen` chỉ khi LSP trả rỗng, grep lớp cuối · bảng so agent-lsp với lumen (việc nào thay được, việc nào không) · vòng đời Ollama 4 bước (LSP rỗng → đánh thức → tìm → nhả model ngay) · luật đối trọng hook plugin lumen — Test: file có đủ 4 mục, thứ tự ưu tiên viết đúng, có nhánh lumen hỏng thì bỏ qua lumen
  - Chạm: `skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md` → file mới, chưa node nào phụ thuộc

**Xong P2 khi**: 3 file skill tồn tại, `doc_lint.py` trên cả 3 exit 0.

## P3 — Móc vào 4 skill workflow

- [x] **T3.1** (e15m) Móc `tdq-intake`: `SKILL.md` thêm bước chạy `tdq_lsp.py kiem` lúc mở request kèm câu bắt buộc xin phép trước khi cài; `references/analyze-full.md` bước 2 "đọc code" thêm dòng bắt buộc dùng LSP trước grep, kèm tên tool và ví dụ. Cả hai dòng trỏ về `uu-tien-tim-kiem.md` — Test: hai file đều có dòng luật LSP và đều trỏ về file luật gốc
  - Chạm: `skills/tdq-intake/SKILL.md`, `skills/tdq-intake/references/analyze-full.md`
  - Cần: T2.3
- [x] **T3.2** (e10m) Móc `tdq-spec` bước 1: vùng file của §2b Ranh giới module dựng từ ngữ nghĩa LSP, không đoán theo tên thư mục; dòng trỏ về `uu-tien-tim-kiem.md` — Test: file có dòng luật LSP trỏ về file luật gốc
  - Chạm: `skills/tdq-spec/SKILL.md`
  - Cần: T2.3
- [x] **T3.3** (e10m) Móc `tdq-plan` bước 2: dòng `Chạm:` dựng từ kết quả "ai gọi hàm này" của LSP trước khi bổ sung bằng grep; dòng trỏ về `uu-tien-tim-kiem.md` — Test: file có dòng luật LSP trỏ về file luật gốc
  - Chạm: `skills/tdq-plan/SKILL.md`
  - Cần: T2.3
  - Dùng: `tdq-plan`
  - Để: đọc khuôn hiện hành của chính skill này trước bước đỏ, chèn dòng luật LSP vào đúng
    bước 2 mà không phá thứ tự 6 bước. Agent ngoài không có skill system: đọc
    `skills/tdq-plan/SKILL.md` rồi làm theo.
  - Ra: `skills/tdq-plan/SKILL.md` có dòng luật LSP trong bước 2
  - Kiểm: `grep -n "uu-tien-tim-kiem" skills/tdq-plan/SKILL.md` ra ít nhất 1 dòng
  - Không dùng cho: đổi nội dung 6 bước sẵn có, đổi khuôn `Chạm:` hay luật `(mcp)`
- [x] **T3.4** (e15m) Móc `tdq-build`: mục `## Hard rules` thêm luật mềm "ký hiệu code thì thử LSP trước grep"; Part A bước 2.4 "Search before creating" đặt LSP đứng trước `graphify query` và grep. Cả hai trỏ về `uu-tien-tim-kiem.md` — Test: file có hai dòng luật LSP, LSP đứng trước `graphify query` trong bước 2.4
  - Chạm: `skills/tdq-build/SKILL.md`
  - Cần: T2.3
  - Dùng: `tdq-build`
  - Để: đọc mục `## Hard rules` và bước 2.4 hiện hành trước bước đỏ, chèn luật LSP đúng chỗ
    mà không phá luật tick và luật đỏ-xanh. Agent ngoài không có skill system: đọc
    `skills/tdq-build/SKILL.md` rồi làm theo.
  - Ra: `skills/tdq-build/SKILL.md` có luật LSP ở `## Hard rules` và ở bước 2.4
  - Kiểm: `grep -c "uu-tien-tim-kiem" skills/tdq-build/SKILL.md` ra ít nhất 2
  - Không dùng cho: đổi luật tick, luật đỏ-xanh, hay phần mode đội
- [x] **T3.5** (e20m) Viết test khoá luật: xoá dòng luật LSP ở bất kỳ file nào trong 5 file móc (`tdq-intake` SKILL + analyze-full, `tdq-spec`, `tdq-plan`, `tdq-build`) thì ĐỎ; và kiểm câu luật ở các chỗ móc khớp câu gốc trong `uu-tien-tim-kiem.md`, không lệch nhau — Test: chạy chu trình đỏ-xanh thật cho từng file, xoá thì ĐỎ, khôi phục thì XANH
  - Chạm: `tests/test_tdq_lsp_skill.py` → file mới, chưa node nào phụ thuộc
  - Cần: T3.1, T3.2, T3.3, T3.4

**Xong P3 khi**: 5 file móc đều có luật LSP, test khoá luật xanh và đã chứng minh đỏ được.

## P4 — Dựng môi trường thật trên máy

Mọi task phase này phải xin phép user trước từng lệnh. Task nào user không duyệt thì ghi lại
lý do vào report và bỏ qua, không tự làm thay bằng đường khác.

- [x] **T4.1** (e12m) Sao lưu `~/.claude.json`, chạy `agent-lsp init` để đăng ký MCP `lsp`, rồi so lại — Test: `claude mcp list` có `lsp` ở trạng thái Connected, tổng số server là 16
- [x] **T4.2** (e20m) Cài 4 language server: `npm i -g pyright` · `npm i -g typescript-language-server typescript` · `dotnet tool install -g csharp-ls` · `brew install lua-language-server` — Test: `agent-lsp doctor` báo trạng thái ok cho python, typescript, javascript, csharp, lua
- [x] **T4.3** (e8m) Sao lưu `~/.claude/settings.json` rồi thêm `mcp__lsp__*` vào allow list — Test: file có mục allow khớp `mcp__lsp__*`
  - Cần: T4.1
- [x] **T4.4** (e10m) Sao lưu `hooks/hooks.json` của plugin lumen kèm số bản, rồi gỡ khối `PreToolUse`, giữ nguyên khối `SessionStart` — Test: file không còn khối `PreToolUse`, còn khối `SessionStart`, bản sao lưu tồn tại; chạy một lệnh Bash bất kỳ không còn dòng giục dùng lumen
- [ ] **T4.5** (e10m) Gọi thật một tool `mcp__lsp__*` trên một hàm có thật của repo này và đối chiếu vị trí — Test: trả về đúng file và đúng dòng của hàm đó
  - Cần: T4.1, T4.2, T4.3

- [x] **T4.6** (e12m) Ghi nguyên trình tự P4 vừa chạy thành mục runbook trong `skills/tdq-lsp-setup/SKILL.md`: từng bước, lệnh thật, file sao lưu, cách hoàn tác — để lần sau đổi máy hoặc đổi cấu hình thì đọc lại mà làm, không phải mở plan cũ (user yêu cầu ở lượt duyệt P4) — Test: skill có mục runbook liệt kê đủ 5 bước kèm lệnh và đường dẫn sao lưu; `doc_lint.py` exit 0
  - Chạm: `skills/tdq-lsp-setup/SKILL.md`
  - Cần: T4.1, T4.2, T4.3, T4.4

**Xong P4 khi**: MCP `lsp` Connected, `doctor` xanh cho 5 ngôn ngữ, hook lumen đã gỡ, tool LSP gọi thật ra kết quả đúng.

## P5 — Log & test bắt buộc

- [x] **T5.1** (e8m) Log service của `tdq_lsp.py` bật mặc định: timestamp, đủ chi tiết debug, tắt được bằng cờ dòng lệnh — Test: chạy script thấy dòng log có timestamp; chạy với cờ tắt thì không còn dòng log
  - Chạm: `scripts/tdq_lsp.py`
  - Cần: T1.3
- [x] **T5.2** (e25m) Unit test cho `tdq_lsp.py`, chạy bằng một lệnh, phủ cả 6 bậc, cả nhánh không có binary `agent-lsp`, cả nhánh đánh thức Ollama quá hạn, và ca user tự bật Ollama thì `nha` không giết daemon — Test: suite của script xanh toàn bộ
  - Chạm: `tests/test_tdq_lsp.py` → file mới, chưa node nào phụ thuộc
  - Cần: T5.1

## P6 — Chốt sổ

- [x] **T6.1** (e8m) Chạy `python3 scripts/build_portable.py` sinh lại hai bản portable — Test: `portable_claude/` và `portable_codex/` đều chứa skill `tdq-lsp-setup` và `tdq_lsp.py`
  - Cần: T2.1, T2.2, T2.3, T3.4, T5.1
- [x] **T6.2** (e10m) Chạy `doc_lint.py` trên spec, plan và 3 file skill mới, kèm kiểm cặp spec–plan; rồi chạy toàn bộ suite đúng một lần — Test: lint exit 0; số test đỏ toàn suite đúng bằng mốc nền 37
  - Cần: T6.1

## Cụm song song

- **Đợt 1** — P1 chạy tuần tự một mình: T1.1 → T1.2 → T1.3 đều chạm `scripts/tdq_lsp.py`,
  không tách được. Leader tự làm.
- **Đợt 2** — P2 ba task ba file rời nhau: T2.1, T2.2, T2.3 chạy song song được.
- **Đợt 3** — P3 bốn task bốn vùng file rời nhau: T3.1, T3.2, T3.3, T3.4 chạy song song được,
  cả bốn đều `Cần: T2.3` nên phải chờ đợt 2 xong.
- **Đợt 4** — T3.5 một mình, vì nó đọc kết quả của cả bốn task đợt 3.
- **Đợt 5** — P4 phải leader tự làm hết: mỗi task là một lệnh xin phép user, sub-agent không
  hỏi user được. T4.2 chạy song song với T4.1 được về mặt file, nhưng vẫn là leader.
- **Đợt 6** — T5.1 rồi T5.2, rồi T6.1 rồi T6.2, tuần tự theo `Cần:`.

Trần tốc độ của mode đội: 4 task song song ở đợt 3.

## Definition of Done

- [x] Q1 Skill tồn tại và đúng luật — `grep -c "github.com/blackwell-systems/agent-lsp" skills/tdq-lsp-setup/SKILL.md` ra 1, và `grep -c '```python' skills/tdq-lsp-setup/SKILL.md` ra 0
- [x] Q2 Bảng ngôn ngữ đủ 30 — `grep -cE "^\| " skills/tdq-lsp-setup/references/languages.md` trừ dòng tiêu đề ra 30
- [x] Q3 Script in đủ 6 bậc — `.venv/bin/python scripts/tdq_lsp.py kiem | grep -cE "^Bậc [1-6]"` ra 6
- [x] Q4 Script không tự cài — `grep -nE "npm i|npm install|brew install|dotnet tool install" scripts/tdq_lsp.py` không có dòng nào nằm trong lệnh gọi tiến trình con
- [x] Q5 Script có log timestamp và cờ tắt — `.venv/bin/python scripts/tdq_lsp.py kiem` có dòng timestamp; chạy với cờ tắt log thì không có
- [x] Q6 Test script xanh — `.venv/bin/python -m pytest tests/test_tdq_lsp.py -q`
- [x] Q7 Móc intake — `grep -n "tdq_lsp.py" skills/tdq-intake/SKILL.md` và `grep -in "xin phép" skills/tdq-intake/SKILL.md`
- [x] Q8 Luật mềm ở build — `grep -n "LSP" skills/tdq-build/SKILL.md` có dòng trong mục `## Hard rules`
- [x] Q9 Luật được khoá thật — `.venv/bin/python -m pytest tests/test_tdq_lsp_skill.py -q` xanh, và chu trình xoá-dòng-luật cho từng file trong 5 file móc đều ĐỎ
- [x] Q10 MCP đăng ký thật — `claude mcp list | grep -c lsp` ra ít nhất 1 và dòng đó có Connected
- [x] Q11 4 server cài thật — `agent-lsp doctor` không còn warning cho python, typescript, javascript, csharp; `which lua-language-server` ra đường dẫn
- [ ] Q12 Tool LSP gọi được thật — gọi `mcp__lsp__go_to_definition` trên một hàm có thật của repo, đối chiếu đúng file và đúng dòng
- [x] Q13 Quyền tool — `grep -n "mcp__lsp__" ~/.claude/settings.json`
- [x] Q14 Portable đủ — `ls portable_claude/skills/tdq-lsp-setup portable_codex/skills/tdq-lsp-setup` và `ls portable_claude/scripts/tdq_lsp.py portable_codex/scripts/tdq_lsp.py`
- [x] Q15 Lint tài liệu — `python3 scripts/doc_lint.py docs/tdq/spec/2026-08-23-0052-skill-tdq-lsp-setup.md docs/tdq/plan/2026-08-23-0052-skill-tdq-lsp-setup.md skills/tdq-lsp-setup/SKILL.md skills/tdq-lsp-setup/references/languages.md skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md` exit 0, và `--pair` trên cặp spec-plan exit 0
- [x] Q16 Suite tổng giữ mốc — `.venv/bin/python -m pytest tests/ -q` cho đúng 37 đỏ
- [x] Q17 Móc bước đọc code — `grep -n "LSP" skills/tdq-intake/references/analyze-full.md` có dòng ở bước 2
- [x] Q18 Móc spec và plan — `grep -n "LSP" skills/tdq-spec/SKILL.md skills/tdq-plan/SKILL.md`, mỗi file ít nhất 1 dòng và đều nhắc `uu-tien-tim-kiem.md`
- [x] Q19 Móc tìm-trước-khi-tạo — trong `skills/tdq-build/SKILL.md` bước 2.4, số dòng của LSP nhỏ hơn số dòng của `graphify query`
- [x] Q20 Bốn chỗ móc không lệch nhau — `.venv/bin/python -m pytest tests/test_tdq_lsp_skill.py -q -k khop` xanh
- [x] Q21 Thứ tự ưu tiên ghi rõ — `grep -n "agent-lsp" skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md` có dòng nêu thứ tự và dòng nêu nhánh lumen hỏng
- [x] Q22 Bậc lumen không chặn — tắt Ollama rồi `.venv/bin/python scripts/tdq_lsp.py kiem; echo $?` ra mã cho phép làm tiếp
- [x] Q23 Luật đối trọng hook lumen — `grep -in "hook" skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md` có dòng nói hook plugin là gợi ý
- [x] Q24 Lumen chỉ chạy khi LSP rỗng — `grep -in "rỗng" skills/tdq-lsp-setup/references/uu-tien-tim-kiem.md` có dòng nêu điều kiện kích hoạt
- [x] Q25 Đánh thức Ollama chạy thật — tắt Ollama, chạy `.venv/bin/python scripts/tdq_lsp.py danh-thuc`, rồi `curl -s localhost:11434/api/tags` trả lời
- [x] Q26 Nhả model chạy thật — sau `.venv/bin/python scripts/tdq_lsp.py nha`, `ollama ps` không còn model embedding của lumen
- [x] Q27 Không tắt nhầm của user — user tự bật Ollama rồi chạy `nha`: `curl -s localhost:11434/api/tags` vẫn trả lời
- [x] Q28 Đánh thức quá hạn không chặn — ép hạn chờ về mức rất nhỏ, `danh-thuc` báo THIẾU và trả mã cho phép làm tiếp
- [x] Q29 Hook lumen đã gỡ thật — `grep -c PreToolUse` trên `hooks.json` của plugin lumen ra 0, `grep -c SessionStart` ra ít nhất 1, và file sao lưu tồn tại
- [ ] Q30 Hết chèn dòng giục — chạy một lệnh Bash bất kỳ, đầu ra không còn dòng giục dùng lumen thay Grep
- [x] Q31 Bậc 6 bắt được hook xung đột — khôi phục tạm khối `PreToolUse` rồi `tdq_lsp.py kiem` báo bậc 6 THIẾU kèm đúng đường dẫn; gỡ lại thì báo ĐẠT
- [x] Q32 Bậc 6 không tự sửa — `grep -nE "open\(.*w|write_text|unlink|rename" scripts/tdq_lsp.py` không có dòng nào nhắm vào thư mục cache plugin
