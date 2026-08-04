# Kiến thức chốt — tối ưu token/time workflow (vòng 2)

Slug: `2026-08-05-toi-uu-token-vong-2` · lane full · phase analyze
Nối tiếp: `2026-08-04-toi-uu-token-workflow` (phân tích) + `2026-08-04-thuc-thi-p0-token` (5 task P0).

## Năng lực dùng được (B0)

| Năng lực | Phán quyết | Vì sao |
|---|---|---|
| skill `tdq-*` (6) | DÙNG | khung workflow của chính request này |
| agent `search-scout` | ĐÃ DÙNG | research 6 hướng, trả digest 1.418 ký tự |
| plugin `claude-md-management` (skill claude-md-improver) | DÙNG | có rubric chấm CLAUDE.md, đã dùng ở vòng 1 |
| plugin `skill-creator` | DÙNG | tách SKILL.md → `references/` khi chuyển luật |
| `scripts/token_audit.py` | DÙNG (phải sửa) | công cụ đo — đang đếm sai, xem N7 |
| `scripts/plugin_tiers.py` | DÙNG | chuyển 10 LSP sang tier on_demand |
| `graphify` | DÙNG cuối turn | có sửa `scripts/*.py` |
| plugin `code-review`, `hookify`, `feature-dev` | BỎ | không phải việc review code / tạo hook |
| agent `tdq-reviewer` | BỎ | user không yêu cầu review sâu |

## 1. Mô hình chi phí đã hiệu chỉnh

Vòng 1 dùng "carry-cost" = `ký tự/4 × số API call còn lại`. Đúng về hướng nhưng **thiếu giá**:
ba loại token có đơn giá khác nhau. Quy hết về "input-token tương đương" (nguồn:
platform.claude.com/docs/en/about-claude/pricing, agent research xác nhận):

```
chi phí ≈ cache_read×0,1 + cache_write×1,25 + input×1 + output×5
cache_read mỗi call = context nền + mọi thứ đã tích luỹ trong phiên
```

Hệ quả: **mọi ký tự vào context bị nhân với số API call còn lại, rồi mới nhân 0,1**.
Cắt một call rẻ hơn cắt output của call đó, vì cắt call cắt luôn cả context nền.

## 2. Số liệu đo (2 session gần nhất, đã khử trùng lặp)

| chỉ số | giá trị |
|---|---|
| API call thực | 768 |
| cache_read | 90,07M · cache_write 2,55M · output 506k |
| **hóa đơn quy đổi** | **14,73M input-token tương đương** |
| chia phần | cache_read 61% · cache_write 22% · output 17% |
| context/call | đầu phiên 41k–51k · median 127,5k · p90 157k · max 167k |
| tool call | 733 |

Phân bổ tool call: Bash 378 (khác 167 · tdq_state 82 · doc_lint 48 · test 48 · git 20 ·
graphify 13) · Edit 158 · Read 92 · Write 50 · tavily 15 · AskUserQuestion 12 · Agent 7.

Kích thước CLAUDE.md theo mục (byte): §9 TDQ 5.500 · §10 plugin 1.932 · §3 research 1.295 ·
§1 quy trình 1.029 · §6 working log 833 · §2 git 652 · §7 issue 428 · §8 checklist 232 ·
§5 logging 188 · §4 trình bày 120. Tổng **12.245 byte ≈ 3.100 token**.

## 3. Nguyên nhân (đã đo, không suy đoán)

| # | Nguyên nhân | Số đo | Ước tính phần hóa đơn |
|---|---|---|---|
| N1 | Context nền quá nặng | 41k–51k token × 768 call = 35,3M cache_read | **24%** |
| N2 | Bookkeeping chiếm 1/4 số call | 191/733 tool call (state 82, lint 48, test 48, graphify 13) | ~11% |
| N3 | Read nguyên file + đọc lại | 92 lần, tb 4.160 ký tự; 15 file đọc lại thừa 156k ký tự (working log 8 lần = 55k) | ~5% |
| N4 | Không song song hoá tool call | 8/768 message có >1 tool call (1%) | ~7% |
| N5 | Digest subagent quá dài | 7 lần, tb 3.331 ký tự, cực đại 13.160 | ~1% |
| N6 | Output của model | 506k token thinking+text | 17% (khó cắt) |
| N7 | **Công cụ đo sai** | token_audit cộng usage theo dòng JSONL, một message nằm nhiều dòng → API call +60%, cache_read +62% | không phải tiền, nhưng làm sai mọi quyết định |
| N8 | Đổi model/effort giữa phiên huỷ cache | phiên này đổi 3 lần; mỗi lần re-cache ≈ context×1,25 | ~3% khi xảy ra |
| N9 | Script chưa "agent-friendly" | doc_lint 607 ký tự/lần · test 1.037 · Bash khác 1.128 | ~2% |
| N10 | tavily thô (đã fix vòng 1) | cũ 8.056 ký tự/lần × 15; nay qua search-scout còn 1.418 ký tự/lần (−82%) | đã thu |

## 4. Quyết định đã chốt (interview 00:52 + 00:58)

1. **Mở khoá phạm vi**: được sửa `~/.claude/CLAUDE.md` và `~/.claude/settings.json`.
2. **Gộp bookkeeping** về một lệnh `tdq_finish.py` chạy cuối turn (state + lint file vừa
   sửa + append working log + graphify), in 1 dòng.
3. **Plugin**: chuyển 10 LSP không dùng sang tier `on_demand`, giữ `pyright-lsp`.
4. **CLAUDE.md**: spec phải đưa **bảng từng mục** kèm phán quyết GIỮ/CẮT/CHUYỂN + nơi đến
   + cơ chế chống bỏ sót; user soát từng dòng rồi mới duyệt.
5. **Việc dài**: plan > 6 task → giao phase cho subagent (context riêng, trả digest);
   không dùng luật tự compact.
6. **Tên sub-agent** mở đầu bằng model + think level: `<model>-<effort>_ <mô tả>`
   (ví dụ `sonnet-low_ research doc`). Vì `effort` chỉ đọc từ frontmatter, phải khai báo
   `effort` tường minh cho cả 7 agent để nhãn nói đúng sự thật.
7. **Ràng buộc chặn: không đánh đổi chất lượng công việc và output.** Task tối ưu nào làm
   giảm độ tin cậy thì loại khỏi spec, không "cân nhắc".

## 5. Phương án đã loại

| Phương án | Vì sao loại |
|---|---|
| Bật context editing `clear_tool_uses_20250919` | là tính năng API, Claude Code không expose qua settings; và xoá tool result phá cache prefix tại điểm xoá → có thể lỗ |
| Luật tự `/compact` khi context > 120k | user loại: compact làm mất chi tiết → rủi ro chất lượng |
| Cắt số vòng verify / bớt gate duyệt | vi phạm ràng buộc "không đánh đổi chất lượng" |
| Rút ngắn spec/plan/report | như trên; report vốn đã ≤50 dòng |
| Đổi TTL cache thủ công | không có knob trong Claude Code |

## 6. Nguồn

Chi tiết trong `docs/tdq/research/2026-08-05-toi-uu-token-vong-2.md`. Chính:
platform.claude.com/docs/en/about-claude/pricing (giá cache) ·
platform.claude.com/docs/en/build-with-claude/context-editing ·
anthropic.com/engineering/code-execution-with-mcp (case −98,7%) ·
anthropic.com/engineering/effective-context-engineering-for-ai-agents ·
speakeasy.com/blog/engineering-agent-friendly-cli · boringbot.substack.com (path-scoped rule −41%).

## Lộ trình

| Bước/phase | CÓ–BỎ | Vì sao |
|---|---|---|
| Phân tích + đo lại | CÓ (xong) | vòng 1 dựa trên số sai, phải đo lại trước khi đề xuất |
| Research web đa hướng | CÓ (xong) | cần giá cache thật + cơ chế chính thức, không đoán |
| Interview | CÓ (xong, 2 vòng) | phạm vi CLAUDE.md/settings và ranh giới chất lượng đổi hẳn kết quả |
| Spec + bảng duyệt từng mục CLAUDE.md | CÓ | user yêu cầu soát từng dòng |
| Plan checkbox, mỗi task một test | CÓ | khung bất biến |
| Implement | CÓ | |
| QC độc lập bằng agent `tdq-qc-tester` | CÓ | request này sửa chính bộ luật workflow — cần người thứ hai soát, đúng ràng buộc "không đánh đổi chất lượng" |
| Đo lại sau khi áp dụng (before/after) | CÓ | không có số sau thì không biết có thật sự tiết kiệm |
| Review sâu bằng `tdq-reviewer` | BỎ | user không yêu cầu; đã có QC agent |
| Mode external (codex/agy) | BỎ | việc sửa luật workflow cần hiểu ngữ cảnh sâu, engine ngoài không có |
| Deep search 2 phase | BỎ | 1 vòng search-scout đã đủ, không có mâu thuẫn nguồn |

## Đo before (công cụ đã sửa)

Đo lúc 2026-08-05 01:36 bằng `token_audit.py` sau khi sửa lỗi đếm (task T1.3–T1.4).
Mốc so sánh chuẩn = session `0f97200f` — session HOÀN CHỈNH cuối cùng chạy toàn bộ
luật cũ (6,7 MB transcript).

| Chỉ số | Session `0f97200f` (baseline) | 2 session mới nhất lúc 01:35 |
|---|---|---|
| API call | 416 | 821 |
| tool call | 397 | 793 |
| cache_read | 51,70M | 97,09M |
| cache_write | 1,63M | 2,85M |
| input | 3.482 | 4.248 |
| output | 292k | 601k |
| **chi phí quy đổi (TTL 1h)** | **9,90M** | **18,42M** |
| chia phần | cache_read 52% · cache_write 33% · output 15% | 53% · 31% · 16% |

Nhóm tốn nhất trên 2 session: Read file 22,14M carry-cost (100 lần) · Bash khác 11,09M
(199 lần) · tavily 9,38M (15 lần) · test 2,30M · `tdq_state` 2,29M (89 lần) ·
Agent 2,03M · doc_lint 1,82M (45 lần).

**Đính chính mục 1 và 2 ở trên:** hệ số cache_write đúng cho phiên Claude Code là **2,0**
(TTL 1 giờ), không phải 1,25 (TTL 5 phút) — xem `research/…#Đơn giá xác nhận`. Vì vậy
con số 14,73M ghi ở mục 2 là đo với hệ số 1,25; cùng cách đo, tỷ trọng cache_write tăng
từ 22% lên ~31%. Kết luận thứ tự ưu tiên không đổi: context nền vẫn là khoản lớn nhất.
