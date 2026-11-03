# Spec — tối ưu token/time workflow (vòng 2)

<!-- doc-lint: allow R10 — spec viết trước khi có luật ranh giới module -->

Slug: `2026-08-05-toi-uu-token-vong-2` · lane full · bản 1
Nguồn: `docs/tdq/knowledge/2026-08-05-toi-uu-token-vong-2.md`

## 1. Mục tiêu & phạm vi

**Mục tiêu:** giảm chi phí token và thời gian mỗi request của TDQ workflow bằng biện pháp
lâu dài (đổi luật/công cụ), **không đánh đổi chất lượng công việc và output**.

Baseline đo được (2 session gần nhất): hóa đơn 14,73M input-token tương đương ·
768 API call · context nền 41k–51k · 733 tool call, 26% là bookkeeping.

**Trong phạm vi:**
- `~/.claude/CLAUDE.md` (cắt lõi) và `~/.claude/plugin-tiers.json` (tier plugin).
- `scripts/` của repo: `tdq_finish.py` (mới), `token_audit.py` (sửa lỗi đếm).
- `skills/tdq-*` + `portable/workflow/*` (luật mới, giữ đồng bộ).
- `agents/*.md` (khai báo effort, quy ước tên).
- `tests/` cho từng phần trên.

**Ngoài phạm vi:**
- `~/.claude/settings.json` phần `hooks`, `env`, `permissions` — chỉ đọc, không sửa
  (mở khoá settings ở interview là để đổi **tier plugin**; đụng hook/env là rủi ro không
  cần thiết cho mục tiêu này).
- Bật/tắt plugin trực tiếp bằng `claude plugin enable` — chỉ sửa danh sách tier.
- Cắt số vòng verify, bớt gate duyệt, rút ngắn spec/plan/report — vi phạm ràng buộc chất lượng.
- Xoay Tavily API key (đã báo user, là việc riêng).

## 1b. Lộ trình

| Bước/phase | CÓ–BỎ | Vì sao |
|---|---|---|
| Phân tích + đo lại | CÓ (xong) | vòng 1 dựa trên số sai |
| Research web đa hướng qua `search-scout` | CÓ (xong) | cần giá cache thật, không đoán |
| Interview 2 vòng | CÓ (xong) | phạm vi + ranh giới chất lượng đổi hẳn kết quả |
| Spec (có bảng duyệt từng mục CLAUDE.md) | CÓ | user yêu cầu soát từng dòng |
| Plan checkbox, mỗi task một test | CÓ | khung bất biến |
| Implement | CÓ | mode do user chốt lúc duyệt plan |
| QC độc lập bằng agent `tdq-qc-tester` | CÓ | sửa chính bộ luật workflow, cần người thứ hai soát |
| Đo lại before/after | CÓ | không có số sau thì không biết có tiết kiệm thật |
| Review sâu `tdq-reviewer` | BỎ | user không yêu cầu, đã có QC agent |
| Mode external (codex/agy) | BỎ | sửa luật workflow cần ngữ cảnh sâu |
| Deep search 2 phase | BỎ | 1 vòng scout đã đủ, nguồn không mâu thuẫn |

## 2. Bảng phán quyết CLAUDE.md (user soát từng dòng)

Hiện 12.245 byte ≈ 3.100 token, nằm trong **mọi** API call của **mọi** phiên.
Mục tiêu: ≤ 3.500 byte. Cột "nơi đến" là file đã tồn tại trừ khi ghi (mới).

| § | Nội dung | Byte | Phán quyết | Nơi đến / lý do |
|---|---|---|---|---|
| — | tiêu đề file | 36 | GIỮ | |
| 1 | Quy trình xử lý task chung | 1.029 | **CẮT còn ~250** | 4/5 gạch đầu dòng (interview, tổng hợp plan, chờ duyệt, không tự vào plan mode) đã có nguyên văn trong `tdq-intake` + `tdq-spec`. Giữ 2 dòng: "chuyên gia kỹ tính, research trước khi kết luận" + "chờ user duyệt, không tự vào plan mode" |
| 2 | Git & Worktree | 652 | **GIỮ nguyên** | hậu quả không phục hồi được (tên branch/commit, cấm commit tự ý). Luật loại này phải luôn trong context |
| 3 | Research & độ tin cậy | 1.295 | **CHUYỂN, giữ ~180** | `tdq-conventions` §8 đã có nguyên văn luật Tavily primary→backup→WebSearch. Giữ 2 dòng bất biến: "không bịa, mọi khẳng định có nguồn" + "không đưa API key vào câu trả lời/log/lệnh/prompt" |
| 4 | Phong cách trình bày | 120 | **GIỮ** | rẻ, chi phối mọi câu trả lời |
| 5 | Logging khi phát triển | 188 | **GIỮ** | chi phối sản phẩm build ra, không có nơi nào khác luôn-load |
| 6 | Working log theo ngày | 833 | **CHUYỂN, giữ ~120** | `tdq-conventions` §6 đã có; hook `stop_gate.py` đã chặn cứng khi thiếu log. Giữ 1 dòng nhắc |
| 7 | Xử lý issue/lỗi user báo | 428 | **CHUYỂN hết** | → `skills/tdq-intake/references/issue-triage.md` (mới). Chỉ dùng khi đúng loại việc đó |
| 8 | Checklist khi lập spec | 232 | **CHUYỂN hết** | → `skills/tdq-spec/references/spec-template.md` (kiểm: nếu chưa có thì bổ sung vào template) |
| 9 | TDQ Workflow | 5.500 | **CẮT còn ~900** | chi tiết external/deep-search/lộ trình/sub-agent đã nằm nguyên trong `tdq-plan`, `tdq-build`, `deep-search.md`. GIỮ 5 luật kích hoạt: ① mọi prompt mới → `tdq-intake`; ② chỉ USER duyệt, mơ hồ thì hỏi; ③ state chỉ ghi qua `tdq_state.py`; ④ gộp gate (duyệt spec → viết plan ngay; duyệt plan kèm mode → build ngay); ⑤ spec/plan/report tiếng Việt, report ≤50 dòng |
| 10 | Năng lực & plugin | 1.932 | **CHUYỂN bảng, giữ ~300** | bảng định tuyến 17 dòng → `skills/tdq-conventions/references/plugin-routing.md` (mới). Giữ: nguyên tắc "hỏi user trước khi bật", lệnh `plugin_tiers.py enable`, trỏ tới file bảng |

Ước tính sau cắt: **~2.900–3.400 byte** (giảm 72–76%), tiết kiệm ~2.300 token mỗi API call.

**Cơ chế chống bỏ sót (bắt buộc, không có thì không được cắt):**
1. Bản lõi được viết vào repo tại `portable/claude-md/CLAUDE.md` (nguồn sự thật, có git),
   rồi mới cài sang `~/.claude/CLAUDE.md`.
2. Backup `~/.claude/CLAUDE.md` → `~/.claude/CLAUDE.md.bak-<YYYYMMDD-HHMM>` TRƯỚC khi ghi đè.
3. Test `tests/test_claude_md_core.py`: (a) mỗi luật trong bảng "CHUYỂN" phải tìm được ở
   đúng file đích; (b) 5 luật kích hoạt của §9 + toàn bộ §2/§4/§5 vẫn còn trong bản lõi;
   (c) bản lõi ≤ 3.500 byte; (d) bản trong repo và bản đã cài giống nhau (lệch thì FAIL,
   nêu rõ đường dẫn).

## 3. Cách tiếp cận + lý do

Mô hình chi phí đã hiệu chỉnh: `cache_read×0,1 + cache_write×1,25 + input×1 + output×5`.
Vì mọi thứ trong context bị nhân với **số API call còn lại**, thứ tự ưu tiên là:
**① cắt context nền → ② cắt số API call → ③ cắt độ dài từng output**.
Vòng 1 chỉ làm ③. Vòng này làm ① và ②, vốn lớn hơn nhiều.

Phương án loại bỏ (chi tiết + lý do ở knowledge §5): context editing API (Claude Code không
expose, lại phá cache prefix) · luật tự compact (user loại vì mất chi tiết) · cắt verify/gate
(vi phạm ràng buộc chất lượng).

## 3b. Năng lực & công cụ

| Năng lực | Loại | Phán quyết | Lý do |
|---|---|---|---|
| `tdq-conventions`, `tdq-spec`, `tdq-plan`, `tdq-build` | skill | DÙNG | khung workflow của chính request này |
| `search-scout` | agent | DÙNG | đã chạy research 6 hướng, digest 1.418 ký tự |
| `tdq-qc-tester` | agent | DÙNG | QC độc lập cuối lộ trình, bắt buộc theo §7 |
| `claude-md-management` (claude-md-improver) | plugin | DÙNG | có rubric chấm CLAUDE.md khi viết bản lõi |
| `skill-creator` | plugin | DÙNG | tách nội dung sang `references/` đúng chuẩn |
| `scripts/token_audit.py` | script | DÙNG | công cụ đo before/after, phải sửa lỗi đếm (E1) |
| `scripts/plugin_tiers.py` | script | DÙNG | chuyển 10 LSP sang tier on_demand (A3) |
| `scripts/doc_lint.py` | script | DÙNG | kiểm spec/plan/report |
| `graphify` | CLI | DÙNG | có sửa `scripts/*.py`, phải rebuild code graph |
| `tdq-reviewer` | agent | KHÔNG | user đã cấm — luật hiện hành chỉ gọi khi user yêu cầu review sâu |
| mode external (`codex-runner`, `agy-runner`) | agent | KHÔNG | spec §3 đã chọn cách khác tốt hơn — sửa luật workflow cần ngữ cảnh sâu của chính repo |
| `code-review`, `hookify`, `feature-dev` | plugin | KHÔNG | khác lĩnh vực — không phải review code hay tạo hook |

## 4. Nhóm việc & đầu ra đo đếm được

### Nhóm A — Cắt context nền (nguyên nhân N1, ~24% hóa đơn)
- **A1.** Viết bản lõi CLAUDE.md theo bảng §2 → `portable/claude-md/CLAUDE.md`, backup rồi
  cài. **Đo:** ≤ 3.500 byte (từ 12.245).
- **A2.** Tạo 2 file đích mới: `skills/tdq-intake/references/issue-triage.md`,
  `skills/tdq-conventions/references/plugin-routing.md`; bổ sung checklist §8 vào
  `spec-template.md` nếu thiếu. **Đo:** 3 file có đủ nội dung đã chuyển.
- **A3.** Chuyển 10 LSP (clangd, csharp, gopls, jdtls, kotlin, lua, php, ruby,
  rust-analyzer, swift) sang `on_demand` trong `~/.claude/plugin-tiers.json`; giữ `pyright-lsp`.
  **Đo:** `plugin_tiers.py reset` xong, 10 plugin đó `false` trong settings.
- **A4.** `tests/test_claude_md_core.py` theo 4 điều kiện ở §2.

### Nhóm B — Cắt số API call (N2 ~11%, N4 ~7%)
- **B1.** `scripts/tdq_finish.py`: một lệnh cuối turn làm 4 việc theo thứ tự
  (doc_lint file vừa sửa → append working log → set phase → graphify nếu có cài),
  chạy hết mọi bước kể cả khi một bước fail, in **1 dòng** tổng kết + exit code tổng hợp.
  Có `--dry-run`, `--verbose`, và log service (timestamp) bật mặc định, tắt qua
  `TDQ_LOG=0`. **Đo:** thay 4–6 call/turn bằng 1; output ≤ 200 ký tự khi mọi bước pass.
- **B2.** Luật "song song hoá tool call độc lập" vào `tdq-conventions` §10 + `portable`:
  biết trước 2–5 tool call không phụ thuộc nhau → phát trong CÙNG một lượt.
  **Đo:** hiện 8/768 message có >1 tool call (1%); test kiểm luật có mặt trong skill.
- **B3.** Luật: đầu turn KHÔNG chạy `tdq_state.py next` khi hook đã in `[TDQ:NEXT]`
  (trùng lặp); chỉ chạy khi cần checklist đầy đủ. Sửa `tdq-conventions` §1 + `portable`.
  **Đo:** `tdq_state` từ 82 call/2 session giảm ≥40%.

### Nhóm C — Cắt đọc lại (N3, ~5%)
- **C1.** Luật: append working log qua `tdq_finish.py`, **cấm Read lại file để append**.
  **Đo:** working log hiện bị đọc 8 lần/phiên (thừa 55k ký tự) → mục tiêu ≤ 1.
- **C2.** Luật: file > 200 dòng thì định vị bằng `grep -n` rồi Read theo `offset/limit`;
  cấm Read nguyên file khi chỉ cần một mục. **Đo:** trung bình ký tự/lần Read từ 4.160
  xuống ≤ 2.500.

### Nhóm D — Sub-agent (N5, quyết định 5–6 của user)
- **D1.** Quy ước tên: mọi lần gọi Agent đặt `description` dạng `<model>-<effort>_ <mô tả>`
  (ví dụ `sonnet-low_ research doc`). Ghi vào `tdq-conventions` §9 + `portable`.
- **D2.** Khai báo `effort` tường minh trong frontmatter cả 7 agent (hiện đã có đủ 7/7 —
  task này **xác minh + khoá bằng test**, để nhãn ở D1 luôn nói đúng sự thật).
- **D3.** Ngưỡng cứng: mọi agent trả digest ≤ 1.500 ký tự, cấm dán kết quả tool thô.
  Ghi vào frontmatter/thân của 7 agent + `tdq-conventions`. **Đo:** hiện tb 3.331 ký tự.
- **D4.** Luật: plan > 6 task → mặc định **đề xuất** mode subagent, giao theo phase
  (user vẫn là người chốt mode). Ghi vào `tdq-plan`.

### Nhóm E — Công cụ đo (N7) & luật cache (N8)
- **E1.** Sửa `scripts/token_audit.py`: gom block theo `message.id` (một message có thể
  nằm nhiều dòng JSONL), dedup `tool_use.id`, thêm cột **chi phí quy đổi**
  (`cache_read×0,1 + cache_write×1,25 + input + output×5`). **Đo:** transcript giả có 3
  dòng cùng `message.id` → đếm đúng 1 API call (hiện đếm 3).
- **E2.** Luật: không đổi model/effort giữa chừng một phase build (huỷ cache toàn bộ);
  chốt từ đầu. Ghi vào `tdq-conventions` §9.
- **E3.** Đo lại before/after bằng `token_audit.py` đã sửa, đưa bảng vào report.

## 5. Yêu cầu bắt buộc

- `tdq_finish.py` có log service bật mặc định (timestamp, đủ chi tiết debug, tắt bằng `TDQ_LOG=0`).
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi task có test riêng, đi red → green; tick `[x]` ngay khi task đó pass.
- Sửa skill nào thì đồng bộ `portable/workflow/*` tương ứng (test `test_portable_sync` bắt buộc pass).
- Mọi thay đổi ngoài repo (`~/.claude/*`) phải backup trước và ghi đường dẫn backup vào report.

## 6. Ràng buộc & rủi ro

| Rủi ro | Mức | Cách chặn |
|---|---|---|
| Cắt CLAUDE.md làm mất luật → Claude bỏ bước | **Cao** | user duyệt từng dòng ở §2; test A4 kiểm nơi đến + luật bất biến; backup + bản trong repo để hoàn nguyên |
| `tdq_finish.py` gộp lệnh, một bước fail thì nuốt lỗi | Trung bình | chạy hết mọi bước, in trạng thái từng bước khi có lỗi, exit code tổng hợp ≠ 0 |
| Tắt LSP làm mất gợi ý khi cần | Thấp | bật lại 1 lệnh + `/reload-plugins`; giữ `pyright-lsp` cho Python |
| Sửa file ngoài git (`~/.claude/*`) | Trung bình | backup có timestamp + nguồn sự thật đặt trong repo |
| Luật mới (B2/C2/D3) chỉ là văn bản, có thể bị lờ | Trung bình | test contract kiểm luật tồn tại; đo lại E3 để biết luật có hiệu lực thật |
| Đo before/after lẫn lộn phiên cũ/mới | Trung bình | E3 đo theo từng session id, ghi rõ session nào trước/sau |

**Ràng buộc chất lượng (chặn cứng):** giữ nguyên 2 gate duyệt, interview đến hết mơ hồ,
mỗi task một test, full suite ở QC, verify 3 tầng của mode external, research đa hướng có
nguồn. Task nào đụng vào các mục này sẽ bị loại khỏi plan.

## 7. Phạm vi QC & Definition of Done

**QC chạy bởi agent `tdq-qc-tester` (độc lập), phải PASS hết:**
1. `cd tests && python3 -m unittest discover -s . -p "test_*.py"` — 0 fail, số test ≥ 482 + số test mới.
2. `~/.claude/CLAUDE.md` ≤ 3.500 byte; giống hệt `portable/claude-md/CLAUDE.md`; tồn tại file backup.
3. Mỗi luật cột "CHUYỂN" ở §2 tìm được ở đúng file đích (grep chứng minh).
4. 5 luật kích hoạt §9 + §2 + §4 + §5 còn nguyên trong bản lõi.
5. `tdq_finish.py`: chạy thật trong project rác (`TDQ_PROJECT_DIR=<temp>`) → 4 việc đều
   xảy ra, output ≤ 200 ký tự, exit 0; ép 1 bước fail → exit ≠ 0 và báo đúng bước fail.
6. `token_audit.py` đếm đúng trên transcript giả (3 dòng cùng `message.id` → 1 API call).
7. `plugin_tiers.py reset` → 10 LSP tắt, `pyright-lsp` còn bật.
8. 7 agent có `effort` tường minh + ngưỡng digest ≤1.500 ký tự.
9. `doc_lint.py` exit 0 trên spec, plan, report của request này.
10. Bảng before/after trong report có số thật, ghi rõ session id.

**DoD:** 10 mục QC trên PASS · plan tick đủ `[x]` · working log có entry · report ≤ 50 dòng
nêu rõ số before/after và đường dẫn backup · không commit/push khi user chưa yêu cầu.

## 8. Câu hỏi còn mở

Không còn.
