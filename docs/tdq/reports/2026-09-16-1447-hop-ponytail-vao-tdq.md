# REPORT — Hợp lối code Ponytail vào TDQ-Workflow (`2026-09-16-1447-hop-ponytail-vao-tdq` · lane full · mode main · 15 task tick đủ)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

**Kết luận:** hợp được, bằng cách **gộp vào tầng luật đang có** chứ không dựng tầng thứ hai. Phần rẻ nhất (luồng 1 + 5) tốn **0 dòng code**, chỉ cần **một câu** trong luật gốc được bạn duyệt. Request dừng ở phương án theo đúng `4a`.
**Đã làm:** P1 phương án 5 luồng (8 task) · P2 dự thảo thân luật tiếng Anh đúng khuôn 3 mục (`docs/tdq/knowledge/2026-09-16-1447-du-thao-luat-ponytail.md`) · P3 report · P4 bốn phép kiểm · QC1.1 một vòng fix.

**Năm luồng** — chi tiết ở `docs/tdq/knowledge/2026-09-16-1447-phuong-an-ponytail-tdq.md`:

| # | Luồng | Giá | Điều cần biết nhất |
|---|---|---|---|
| 1 | Thân luật: câu luật vào thân `tdq-build/SKILL.md`, bảng 7 bậc vào `chung.md` | 0 dòng code | Buộc chia hai chỗ: `skills/tdq-conventions/references/soul.md:99` không cho đẩy luật tier 1 vào reference. `SKILL.md` còn đúng 4 dòng; quá thì nâng trần — `skills/tdq-conventions/references/soul.md:101` cho phép trước |
| 2 | Mức gắt `muc_gat`, 5 giá trị, mặc định `full` | 1 khoá state + 1 nhánh hook | Trục riêng, không trộn vào `implement_mode`. Không có cơ chế tự xuống mode: chỉ bạn hạ được |
| 3 | Hook thứ sáu `SubagentStart` | 1 file hook + 1 mục `hooks.json` | Là **lời nhắc, không phải cổng chặn** — sự kiện không chặn được, `PreToolUse` matcher `Agent` không bắn |
| 4 | Thêm đích Cursor vào `build_portable.py` | 1 hàm sinh | Rẻ hơn dự kiến: script đã sinh 3 đích (`:284`, `:617`, `:937`). Plan tôi viết "hai đích" là sai số đo, đã sửa theo file |
| 5 | Hợp nhất hướng thất bại | 0 dòng code | `muc_gat` đọc lỗi thì **fail-closed về `full`**, không bao giờ về `off` |

**Một chỗ sửa luật gốc — cần bạn duyệt riêng:** `skills/tdq-build/references/rules/chung.md:22`, bỏ "there is no toggle", thay bằng câu nói rõ nút tắt nằm trong tay bạn và mỗi request về lại `full`.
Không phạm soul vì `skills/tdq-conventions/references/soul.md:37` đã đặt bạn trên cả tầng luật từ trước. Không duyệt thì 4 luồng kia vẫn chạy, chỉ mất mức `off`.

**Phát hiện đáng giá nhất:** Ponytail không sinh tự động — 9 bản luật viết tay, 8 bản so byte, riêng `SKILL.md` chỉ canh bằng "câu bất biến" mà chính checker tự gọi là canary.
Canary đã để lọt: bậc 1 lệch chữ giữa `~/Documents/ponytail/skills/ponytail/SKILL.md:36` ("need to **exist**") và `~/Documents/ponytail/AGENTS.md:7` ("need to be **built**"). Chính checker đó ghi sẵn "upgrade path: generate the copies"; TDQ đã ở trên đường đó.

**Cố ý KHÔNG làm:** không comment `ponytail:` xin bỏ qua ngưỡng (bạn chốt `2a`) · không `/ponytail-debt` · không skill thứ chín (skill không có `alwaysApply` `[XÁC THỰC]`) · không dịch thân luật sang tiếng Việt (`docs/kien-truc.md:51`) · không cắt phương án thành 5 file module — bậc 1 áp lên chính nó.

**Kiểm — QC PASS 13/13 (9 DoD + 4 cố định), vòng 1:** 101/101 trích dẫn `đường-dẫn:dòng` mở đúng dòng thật (trình kiểm bắt được 9 trích dẫn sai, đã sửa) · 0 khẳng định cơ chế thiếu nhãn tin cậy · `doc_lint.py` 0 vi phạm trên cả 4 file · `i18n_check.py` exit 0 · mọi thay đổi đều dưới `docs/`. Chi tiết: `docs/tdq/qc/2026-09-16-1447-hop-ponytail-vao-tdq.md`.

**Giới hạn:** chưa sửa dòng code nào — cố ý, theo `4a` · luồng 3 chỉ giảm xác suất sub-agent viết thừa, không cấm được · số 146/150 dòng đúng vào 2026-09-16, phải đo lại trước khi sửa.
**Nợ có sẵn (không thuộc lượt này):** suite repo đỏ 290 fail + 4 error, nhưng baseline trên worktree `main` sạch ra **đúng cùng tập, lệch 0 test**; 284 trong số đó do `docs/tdq/audit/skill-index.json` (commit 2026-08-18) còn ghi home cũ `/Users/truongdinhquoc` — dựng lại kho là hết.
**Spec còn 9/11 trích dẫn ghi tên file trần** (máy không mở được) — cố ý KHÔNG sửa: spec đã duyệt, đổi nội dung spec là bắt duyệt lại; nói một câu là tôi sửa kèm xin duyệt.
**Ba dụng cụ đo của plan bị sửa theo số đo**, có ghi chú ngày tại chỗ: số đích `build_portable.py`, cách đo tiếng Việt ở Q6, và T4.3 vốn vượt-rỗng vì nhánh chưa commit.

**Git:** chưa commit. Nhánh `feature/hop-ponytail-vao-tdq`, hợp về `main`.

## Thời gian

| Phase | Wall clock | Model time | Times entered |
|---|---|---|---|
| idle | 11s | 10s | 1 |
| analyze | 3h 12min | 14 min | 1 |
| spec | 9 min | 4 min | 1 |
| plan | 15 min | 5 min | 1 |
| implement | 26 min | 26 min | 1 |
| qc | 10 min | 10 min | 1 |
| report | 0s | 0s | 1 |
| **Total** | **4h 13min** | **60 min** | |
