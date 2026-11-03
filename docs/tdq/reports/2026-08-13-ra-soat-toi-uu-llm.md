# BÁO CÁO — Rà soát mức tối ưu cho LLM của tdq-workflow

Ngày: 2026-08-13 · Lane: full · Mode: main · Spec+plan: `docs/tdq/{spec,plan}/2026-08-13-ra-soat-toi-uu-llm.md`

## Kết luận trước

Bộ tài liệu đã tối ưu tốt hơn mặt bằng chung: phần luôn nằm trong context chỉ 5.520 ký tự, phần trùng lặp giữa các `SKILL.md` chỉ 998 ký tự. Giả thuyết "skill chép luật của nhau" ở brief KHÔNG đứng vững sau khi đo.
Chỗ đáng sửa nhất lại nằm ở tốc độ hook. Mỗi lượt gõ prompt, `prompt_context.py` chạy `git diff HEAD` trên toàn worktree, mà repo này luôn có `graphify-out/` bẩn nên lệnh đó trả 7,07 MB và tốn 102ms. Loại thư mục đó khỏi pathspec thì còn 9,0ms, không đụng luật nào.

## Đo bề mặt

`python3 scripts/context_surface.py` — bảng dưới là 35 dòng đầu, đã lược `portable/`, `hooks/scripts/`, `plugin.json`; chạy lệnh để xem đủ 58 dòng.
Cột token ước tính theo 4 byte/token, cùng hệ số cho mọi file nên so sánh vẫn công bằng.

| file | tầng nạp | ký tự (wc -c) | token ước tính | tần suất vào context |
|---|---|---|---|---|
| skills/tdq-build/SKILL.md (description) | luôn nạp | 209 | 52 | mọi phiên |
| skills/tdq-build/SKILL.md (thân) | nạp khi gọi skill | 7.616 | 1.904 | mỗi lần gọi skill |
| skills/tdq-conventions/SKILL.md (description) | luôn nạp | 249 | 62 | mọi phiên |
| skills/tdq-conventions/SKILL.md (thân) | nạp khi gọi skill | 7.278 | 1.820 | mỗi lần gọi skill |
| skills/tdq-intake/SKILL.md (description) | luôn nạp | 222 | 56 | mọi phiên |
| skills/tdq-intake/SKILL.md (thân) | nạp khi gọi skill | 6.922 | 1.730 | mỗi lần gọi skill |
| skills/tdq-plan/SKILL.md (description) | luôn nạp | 226 | 56 | mọi phiên |
| skills/tdq-plan/SKILL.md (thân) | nạp khi gọi skill | 5.922 | 1.480 | mỗi lần gọi skill |
| skills/tdq-spec/SKILL.md (description) | luôn nạp | 224 | 56 | mọi phiên |
| skills/tdq-spec/SKILL.md (thân) | nạp khi gọi skill | 3.448 | 862 | mỗi lần gọi skill |
| skills/tdq-status/SKILL.md (description) | luôn nạp | 219 | 55 | mọi phiên |
| skills/tdq-status/SKILL.md (thân) | nạp khi gọi skill | 1.797 | 449 | mỗi lần gọi skill |
| skills/tdq-build/references/qc.md | đọc khi cần | 2.788 | 697 | khi thân file trỏ tới |
| skills/tdq-build/references/report-template.md | đọc khi cần | 1.439 | 360 | khi thân file trỏ tới |
| skills/tdq-conventions/references/approval.md | đọc khi cần | 2.140 | 535 | khi thân file trỏ tới |
| skills/tdq-conventions/references/context-budget.md | đọc khi cần | 1.265 | 316 | khi thân file trỏ tới |
| skills/tdq-conventions/references/measure-scenario.md | đọc khi cần | 2.198 | 550 | khi thân file trỏ tới |
| skills/tdq-conventions/references/phases.md | đọc khi cần | 5.206 | 1.302 | khi thân file trỏ tới |
| skills/tdq-conventions/references/plugin-routing.md | đọc khi cần | 2.514 | 628 | khi thân file trỏ tới |
| skills/tdq-conventions/references/reminder-codes.md | đọc khi cần | 3.867 | 967 | khi thân file trỏ tới |
| skills/tdq-conventions/references/subagent-tuning.md | đọc khi cần | 3.219 | 805 | khi thân file trỏ tới |
| skills/tdq-conventions/references/tavily.md | đọc khi cần | 1.941 | 485 | khi thân file trỏ tới |
| skills/tdq-conventions/references/user-facing-block.md | đọc khi cần | 2.477 | 619 | khi thân file trỏ tới |
| skills/tdq-conventions/references/worklog-images.md | đọc khi cần | 1.208 | 302 | khi thân file trỏ tới |
| skills/tdq-intake/references/analyze-full.md | đọc khi cần | 3.460 | 865 | khi thân file trỏ tới |
| skills/tdq-intake/references/interview.md | đọc khi cần | 4.064 | 1.016 | khi thân file trỏ tới |
| skills/tdq-intake/references/issue-triage.md | đọc khi cần | 1.931 | 483 | khi thân file trỏ tới |
| skills/tdq-intake/references/lane-decision.md | đọc khi cần | 3.440 | 860 | khi thân file trỏ tới |
| skills/tdq-intake/references/quick-lane.md | đọc khi cần | 5.100 | 1.275 | khi thân file trỏ tới |
| skills/tdq-intake/references/skill-inventory.md | đọc khi cần | 3.251 | 813 | khi thân file trỏ tới |
| skills/tdq-plan/references/plan-template.md | đọc khi cần | 5.924 | 1.481 | khi thân file trỏ tới |
| skills/tdq-spec/references/spec-template.md | đọc khi cần | 4.080 | 1.020 | khi thân file trỏ tới |
| agents/tdq-implementer.md (description) | luôn nạp | 204 | 51 | mọi phiên |
| agents/tdq-implementer.md | đọc khi cần | 2.224 | 556 | khi chạy agent con |
| agents/tdq-qc-tester.md (description) | luôn nạp | 257 | 64 | mọi phiên |

TỔNG: `đọc khi cần` 160.645 ký tự ≈ 40.161 token · `nạp khi gọi skill` 32.983 ≈ 8.246 · `luôn nạp` 5.520 ≈ 1.380.

## Tốc độ hook

`python3 scripts/context_surface.py --hooks` — mỗi tình huống 5 lần trên project tạm rỗng, lấy trung vị; khoảng 15ms mỗi dòng là chi phí khởi động Python.

| hook | tình huống | trung vị |
|---|---|---|
| session_start.py | startup | 29,5ms |
| session_start.py | compact | 30,8ms |
| prompt_context.py | prompt thường | 53,3ms |
| edit_gate.py | sửa mã nguồn | 27,9ms |
| edit_gate.py | sửa tài liệu | 28,5ms |
| bash_gate.py | chạy lệnh | 28,7ms |
| stop_gate.py | kết thúc turn | 28,2ms |

Trên repo THẬT, `prompt_context.py` xấu hơn nhiều: riêng `git diff HEAD` đã 102,3ms và 7.072.647 byte, đo 7 lần lấy trung vị.

## Trùng lặp

So khớp dòng đã chuẩn hoá, chỉ tính dòng dài từ 40 ký tự. Bảng phân loại 5 nhóm của SkillReducer nằm ở mục Q10 của `docs/tdq/qc/2026-08-13-ra-soat-toi-uu-llm.md`.

- Trong `skills/`: tổng 998 ký tự. Nặng nhất là `skills/tdq-spec/SKILL.md:36-49` chép
  nguyên khối trình bày của `skills/tdq-conventions/references/user-facing-block.md:37-49`.
- `skills/tdq-spec/SKILL.md:25` và `skills/tdq-plan/SKILL.md:42` — cùng câu gọi `tdq-reviewer`.
- `skills/tdq-intake/SKILL.md:69-71` và `skills/tdq-intake/references/analyze-full.md:43-45`.
- Với `portable/`: 9.547 ký tự, cao nhất `skills/tdq-build/SKILL.md:22` với `portable/workflow/04-build.md:16`.
  Đây là bản sao CỐ Ý cho môi trường ngoài Claude Code, không vào context, nên là rủi ro lệch bản chứ không phải chi phí token.

## Xếp hạng

Nguồn đối chiếu: <https://arxiv.org/html/2603.29919v1> — SkillReducer, kiểm lại 2026-08-13: nén description 48%, thân 39%, đầu-cuối 26,8%.
Nghiên cứu đó đo hơn 60% thân skill ngoài đời là phần không hành động được; ở đây con số đó chỉ 12-19%.

| # | Cơ hội | Tiết kiệm đo được | Luật bị đụng | Cách chứng minh giữ nguyên |
|---|---|---|---|---|
| 1 | Loại `graphify-out/` khỏi pathspec git của `turn_snapshot` | 93ms mỗi prompt, 7,07 MB mỗi lượt | Luật "turn có đổi repo phải ghi working log" — dấu bẩn của repo là căn cứ nhắc | Chạy `tests/test_turn_snapshot.py` và `tests/test_stop_gate.py`, thêm ca: sửa file mã khi `graphify-out/` bẩn vẫn phải bị nhắc |
| 2 | `tdq-spec` trỏ sang `user-facing-block.md` thay vì chép khối | 422 ký tự mỗi lần gọi skill spec | Luật khuôn khối user-facing của conventions | Chạy `tests/test_user_facing_block.py`; khối vẫn còn nguyên ở file reference |
| 3 | Nén `description` 6 skill theo tầng 1 SkillReducer | Trần lý thuyết 48% của 1.359 ký tự luôn nạp | Luật định tuyến skill: mô tả phải đủ để chọn đúng skill | Giữ `tests/test_token_budget.py`, thêm bộ ca định tuyến 6 tình huống, cắt tới đâu vẫn chọn đúng skill tới đó |
| 4 | Sinh `portable/` từ `skills/` thay vì chép tay | 0 token context, bớt 9.547 ký tự phải sửa hai nơi | Không luật nào — chỉ đổi cách sinh file | `diff` bản sinh với bản đang có phải trống |

Nên làm 1 và 2. Cơ hội 3 lợi ít mà rủi ro định tuyến cao, chỉ làm khi có bộ ca định tuyến trước. Cơ hội 4 là việc bảo trì.

## Bản vá mẫu

Chưa áp vào file thật: `git status --short` không có file sản phẩm nào bị sửa.

Bản vá 1 — `scripts/tdq_state.py`, hằng `BOOKKEEPING_PATHS` (cơ hội #1):

```
- BOOKKEEPING_PATHS = ("docs/tdq", "docs/workinglog")
+ # `graphify-out/` là ĐẦU RA do `tdq_finish.py` sinh lại mỗi turn nên bẩn gần như suốt
+ # phiên; để nó trong pathspec thì `git diff HEAD` phải dựng 7 MB mỗi lượt prompt
+ # (đo 2026-08-13: 102,3ms, so với 9,0ms khi loại ra).
+ BOOKKEEPING_PATHS = ("docs/tdq", "docs/workinglog", "graphify-out")
```

Bản vá 2 — `skills/tdq-spec/SKILL.md` bước 4 (cơ hội #2):

```
- 4. **Trình bày & DỪNG.** Viết khối trình spec theo [user-facing-block.md](...)
-    ... 13 dòng khuôn chép nguyên từ user-facing-block.md ...
+ 4. **Trình bày & DỪNG.** Đọc [user-facing-block.md](../tdq-conventions/references/user-facing-block.md)
+    rồi viết khối trình spec theo đúng khuôn "spec" ở đó — đủ 5 thành phần, duyệt ở cuối.
```
