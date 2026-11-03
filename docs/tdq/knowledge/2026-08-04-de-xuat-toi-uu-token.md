# ĐỀ XUẤT — Tối ưu time/token cho TDQ workflow

Ngày: 2026-08-04 · Request: ../requests/2026-08-04-toi-uu-token-workflow.md
Số liệu: ../research/2026-08-04-toi-uu-token-workflow.md (Phần 1b — đo bằng `scripts/token_audit.py`)
Trạng thái: **ĐỀ XUẤT — chưa thực thi.** Muốn làm thì mở request mới và duyệt từng nhóm.

## Mô hình chi phí

```
tổng token ≈ Σ (kích thước context tại mỗi API call)
           = (số API call) × (context nền + Σ tool output đã tích luỹ)
```

Mỗi tool call = 1 API call = model đọc lại TOÀN BỘ context. Vì vậy một output tool `n` ký tự
KHÔNG tốn `n/4` token — nó tốn `n/4 × số API call còn lại`. Gọi là **carry-cost**.

Đo thật (2 session gần nhất, `token_audit.py --sessions 2`):
**1.123 API call · 132,6M cache_read · 795k output · 72,2M carry-cost.**

Ba đòn bẩy, xếp theo hiệu quả đã đo:

| Đòn bẩy | Nội dung | Phần chi phí chạm tới |
|---|---|---|
| **L1** | Bớt thứ ở lại context (subagent, CLI im lặng, đọc từng phần) | 72,2M carry-cost |
| **L2** | Bớt số API call (gộp lệnh, bớt lần chạy test) | nhân tử của mọi thứ |
| **L3** | Bớt context nền (CLAUDE.md, SKILL.md) | ~3k token × MỌI call |

## Nguyên nhân (mỗi dòng có số đo thật)

| # | Nguyên nhân | Số đo | Nguồn |
|---|---|---|---|
| N1 | Đọc lại spec/plan ở mỗi phase (12–16k ký tự/lần) | 30,2M carry-cost, 92 lần Read | audit Phần 1b |
| N2 | Kết quả tavily thô nằm lại context đến hết session | 14,3M carry-cost, 14 lần | audit Phần 1b |
| N3 | Bash ồn (`grep -A5 -B5`, `cat`, `wc` cả cây) | 12,7M carry-cost, 159 lần | audit Phần 1b |
| N4 | Subagent trả report dài về main | 3,55M carry-cost, 6 lần | audit Phần 1b |
| N5 | `doc_lint` in cả khi PASS | 2,60M carry-cost, 37 lần | audit Phần 1b |
| N6 | `tdq_state.py` in nguyên JSON 17 trường mọi lệnh | 2,29M carry-cost, 68 lần | audit Phần 1b |
| N7 | Edit echo lại diff, sửa lắt nhắt nhiều lần | 2,12M carry-cost, 149 lần | audit Phần 1b |
| N8 | Full test suite 462 test chạy quá nhiều lần | 1,99M carry-cost, 44 lần ≈ **31 phút chờ** | audit Phần 1b + 42s/lần |
| N9 | `~/.claude/CLAUDE.md` nằm trong MỌI request | 10.307 ký tự ≈ 3–4k token × 1.123 call | đo file + docs Claude Code |
| N10 | 8 file doc/request, spec 112–122 dòng, plan 90–121 dòng | output 795k token/2 session | audit + `wc -l` |
| N11 | `tdq-build/SKILL.md` nạp trọn kể cả khi không dùng external | 10.936 byte, 150 dòng, ~50 dòng chỉ cho external | `wc` |
| N12 | Compaction giữa request → đọc lại file đã đọc | 1 lần compact trong session B | transcript |

## Nhóm A — Cắt carry-cost của việc đọc và của CLI (L1)

| # | Task | Cách làm | Tiết kiệm ước tính | Rủi ro & cách giảm |
|---|---|---|---|---|
| A1 | Không đọc lại spec/plan ở phase sau | Khi chốt plan, sinh "hợp đồng gọn" ≤30 dòng (DoD + danh sách task + đường dẫn) vào đầu file plan; phase sau chỉ `sed -n '1,30p'` | ~12M (40% của N1) | Mất chi tiết → hợp đồng bắt buộc chứa đủ DoD; cần sâu thì đọc đúng đoạn |
| A2 | Read theo `offset/limit`, không đọc cả file | Luật: mặc định ≤120 dòng/lần, cần thêm thì đọc tiếp | ~6M (20% của N1) | Đọc thiếu ngữ cảnh → dùng `grep -n` định vị trước |
| A3 | Bash im lặng | Cấm `grep -A5 -B5` khi chỉ cần `-c`/`-l`; cấm `cat` file (dùng Read); gộp `wc` | ~6M (50% của N3) | Khó debug → cho phép mở lại khi đang truy lỗi |
| A4 | `tdq_state.py` mặc định in 1 dòng | In `phase=X lane=Y request=Z`; thêm cờ `--json` mới in đầy đủ | ~2,0M (N6) | Mất khả năng soi state → `--json` vẫn còn |
| A5 | `doc_lint` im khi PASS | Không output khi exit 0 | ~2,1M (N5) | Không biết đã chạy → in đúng 1 dòng tóm tắt |
| A6 | Gộp sửa lặp thành 1 script | ≥3 sửa cùng dạng → viết 1 đoạn python thay vì 3–10 lần Edit | ~1,0M + giảm ~40 API call | Sai hàng loạt → chạy test ngay sau đó |

## Nhóm B — Đẩy việc nặng sang subagent (L1)

Căn cứ: docs Claude Code — "Each subagent starts with a fresh, isolated context window…
returns only the summary" (../research/… Phần 4, khẳng định 2).

| # | Task | Cách làm | Tiết kiệm ước tính | Rủi ro & cách giảm |
|---|---|---|---|---|
| B1 | Research LUÔN chạy trong subagent | `search-scout`/`Explore` gọi tavily, tự ghi `research/<slug>.md`, trả về digest ≤1.500 ký tự cho main | ~12,8M (90% của N2) | Mất nguồn thô → subagent bắt buộc ghi file đầy đủ trước khi trả lời |
| B2 | Phase analyze đọc code bằng subagent | Giao `Explore` khi phải mở ≥4 file; main chỉ nhận bản đồ + đường dẫn | ~5M (17% của N1) | Bỏ sót chi tiết → nêu rõ câu hỏi cần trả lời trong prompt giao việc |
| B3 | QC chạy bằng `tdq-qc-tester` khi DoD ≥5 hạng mục | Output test dài nằm ở subagent, main nhận bảng PASS/FAIL | ~2M (N4 + phần N8) | Mất bằng chứng → subagent ghi thẳng `qc/<slug>.md` |

## Nhóm C — Cắt context nền (L3)

Audit `~/.claude/CLAUDE.md` — 94 dòng, **10.307 ký tự** (≈3–4k token, nằm trong **mọi** request):

| Mục | Ký tự | Phán quyết | Vì sao |
|---|---|---|---|
| 1. Quy trình xử lý task chung | 814 | CẮT còn ~250 | Trùng mục 9 — workflow TDQ đã bắt buộc intake/interview/duyệt |
| 2. Git & Worktree | 534 | **GIỮ** | Luật cứng, ngắn, áp dụng mọi lúc |
| 3. Research & độ tin cậy | 1.029 | CHUYỂN | Chi tiết failover Tavily đã có ở `tdq-conventions/references/tavily.md`; giữ 3 dòng |
| 4. Phong cách trình bày | 92 | **GIỮ** | Ngắn nhất, ảnh hưởng mọi câu trả lời |
| 5. Logging khi phát triển | 152 | **GIỮ** | Ngắn, là luật chất lượng |
| 6. Working log theo ngày | 672 | CHUYỂN | Quy ước chi tiết sang references; giữ 2 dòng luật |
| 7. Xử lý issue/lỗi | 339 | CHUYỂN | Chỉ cần khi có issue → thành skill nạp lười |
| 8. Checklist khi lập spec | 196 | CẮT | Đã nằm trong `tdq-spec/references/spec-template.md` |
| 9. TDQ Workflow | 4.701 | CẮT còn ~900 | Giữ: bắt buộc intake, 2 gate duyệt, cấm sửa state tay. Bỏ: chi tiết external/deep-search/lộ trình — đã có nguyên văn trong skill |
| 10. Năng lực & plugin | 1.717 | CHUYỂN | Bảng định tuyến 20 dòng → references; giữ 3 dòng + đường dẫn |

| # | Task | Cách làm | Tiết kiệm ước tính | Rủi ro & cách giảm |
|---|---|---|---|---|
| C1 | CLAUDE.md còn bản lõi ~2.600 ký tự | Theo bảng trên; phần cắt đi phải nằm sẵn trong skill/references trước khi cắt | ~2.500 token × mọi call ≈ **2,8M/2 session**, và áp cho MỌI project | Claude quên luật → chỉ cắt thứ đã có bản sao trong skill; giữ nguyên luật bất biến |
| C2 | Chia `tdq-build/SKILL.md` | ~50 dòng nhánh external → `references/external.md`, chỉ nạp khi `implement_mode=external` | ~1.200 token mỗi lần nạp build | Quên nạp lúc cần → dòng trỏ file đặt ngay ở bước chọn mode |

## Nhóm D — Giảm số API call (L2)

| # | Task | Cách làm | Tiết kiệm ước tính | Rủi ro & cách giảm |
|---|---|---|---|---|
| D1 | Gộp lệnh Bash độc lập vào 1 call | Dùng `&&`/heredoc; luật: đã biết trước 2–5 lệnh không phụ thuộc nhau thì gộp | ~150 call ≈ **16,5M** (150 × ~110k context) | Lỗi khó khoanh vùng → tách lại khi có lệnh fail |
| D2 | Test theo module lúc implement, full suite 1 lần ở QC | 44 lần → ~8 lần | ~36 call ≈ 4M + **~25 phút/request** | Vỡ test module khác → full suite ở QC vẫn bắt được |
| D3 | Gộp Edit cùng file | Nhiều sửa nhỏ cùng file → 1 lượt; sửa lặp → script (A6) | ~60 call ≈ 6,6M | Diff to khó soi → chạy test ngay sau |
| D4 | `graphify` chỉ chạy cuối request | Hook post-commit đã tự rebuild; 12 lần → 2 | ~10 call ≈ 1,1M | Graph cũ giữa chừng → không ai đọc graph giữa build |

## Nhóm E — Giảm output token & vệ sinh session (L2 + L3)

| # | Task | Cách làm | Tiết kiệm ước tính | Rủi ro & cách giảm |
|---|---|---|---|---|
| E1 | Gộp `questions`+`research`+`knowledge` → `notes/<slug>.md` | 8 file/request còn 6; mỗi mục là một heading | ~15% output token (~60k/2 session) | Khó tra cứu → heading cố định, `doc_lint` kiểm |
| E2 | Cap dòng: spec ≤80, plan ≤80, entry log ≤8 | Thêm rule vào `doc_lint.py` | ~20% output token (~80k/2 session) | Thiếu chi tiết → phần dài đẩy vào references |
| E3 | 1 request = 1 session, xong thì `/clear` | Tránh compaction giữa chừng (compact = viết summary dài + đọc lại file) | tránh ~1–2M mỗi lần compact | Mất mạch → report + working log là điểm nối |
| E4 | Lane quick mặc định mạnh hơn | Đề xuất quick khi việc chạm ≤3 file và không có ẩn số ngoài | ~30% số request đi lane nhẹ | Việc lớn lọt lane quick → tiêu chí đo được, user vẫn chốt |

## Thứ tự làm (P0 = làm trước)

| Hạng | Task | Tiết kiệm | Công sức | Vì sao hạng này |
|---|---|---|---|---|
| **P0** | A4 `tdq_state.py` im lặng | 2,0M | ~30 phút | sửa 1 hàm in, rủi ro gần 0 |
| **P0** | A5 `doc_lint` im khi PASS | 2,1M | ~15 phút | sửa 1 chỗ, rủi ro gần 0 |
| **P0** | D2 test theo module | 4M + 25 phút | ~1 giờ (sửa prose skill) | đổi luật, không đổi code |
| **P0** | B1 research trong subagent | 12,8M | ~2 giờ | agent `search-scout` đã có sẵn |
| **P0** | D1 gộp lệnh Bash | 16,5M | ~30 phút (thêm luật) | tiết kiệm lớn nhất trên mỗi giờ bỏ ra |
| **P1** | C1 CLAUDE.md bản lõi | 2,8M + mọi project | ~2 giờ | phải chuyển nội dung sang skill trước |
| **P1** | A1 hợp đồng gọn thay đọc lại spec/plan | 12M | ~3 giờ | đụng khuôn plan + `doc_lint` |
| **P1** | A3 Bash im lặng | 6M | ~30 phút | luật prose, cần kỷ luật khi chạy |
| **P1** | D3 gộp Edit | 6,6M | ~15 phút | luật prose |
| **P1** | A6 gộp sửa lặp thành script | 1,0M | ~15 phút | luật prose |
| **P1** | E2 cap dòng spec/plan/log | 80k output | ~1 giờ | thêm rule `doc_lint` + test |
| **P2** | A2 Read theo offset/limit | 6M | ~30 phút | dễ đọc thiếu, cần kỷ luật |
| **P2** | B2 đọc code bằng subagent | 5M | ~1 giờ | chỉ lợi khi phải mở ≥4 file |
| **P2** | B3 QC bằng subagent | 2M | ~1 giờ | chỉ lợi khi DoD lớn |
| **P2** | C2 chia `tdq-build/SKILL.md` | 1,2M/lần nạp | ~1 giờ | đụng `test_portable_sync` |
| **P2** | D4 `graphify` cuối request | 1,1M | ~15 phút | lợi nhỏ |
| **P2** | E1 gộp doc thành `notes/` | 60k output | ~3 giờ | đụng nhiều test + portable |
| **P2** | E3 1 request = 1 session | ~1–2M/lần compact | 0 (thói quen) | phụ thuộc người dùng |
| **P2** | E4 lane quick mạnh hơn | ~30% request nhẹ đi | ~1 giờ | cần tiêu chí đo được |

**Tổng ước tính nếu làm hết:** carry-cost 72,2M → **~28M (giảm ~61%)**; số API call 1.123 →
**~750 (giảm ~33%)**; context nền giảm ~2.500 token mỗi call; thời gian giảm **~25 phút/request**.
Chỉ làm 5 task P0 đã cắt ~37M (≈51%) với khoảng 4–5 giờ công.

## Giả định & cách kiểm chứng lại

| Ước lượng | Công thức / giả định | Cách đo lại |
|---|---|---|
| carry-cost mỗi nhóm | `ký tự/4 × số API call còn lại`, 4 ký tự/token | `python3 scripts/token_audit.py --sessions N` |
| A1 cắt 40% của N1 | giả định 2/5 lần Read spec/plan là đọc lại thuần | so nhóm "Read file" trước/sau khi đổi |
| A3 cắt 50% của N3 | giả định nửa số lệnh Bash đang in dư | so nhóm "Bash khác" trước/sau |
| B1 cắt 90% của N2 | digest 1.500 ký tự thay cho ~10.000 ký tự raw | so nhóm "tavily search" trước/sau |
| D1 tiết kiệm 150 call | 308 lệnh Bash gộp trung bình 2 lệnh/call | so `api_calls` của `usage_totals` |
| C1 giảm 2.500 token/call | 10.307 → ~2.600 ký tự, ~3 ký tự/token cho tiếng Việt | đếm ký tự file sau khi sửa |
| Thời gian test | 42s/lần × số lần chạy | `time` khi chạy suite |

**Lưu ý về đơn vị:** tiếng Việt có dấu tốn nhiều token hơn tiếng Anh trên cùng số ký tự
(≈2–3 ký tự/token thay vì 4). Mọi con số trên dùng 4 ký tự/token nên là ước lượng **thấp**;
chi phí thật của phần văn bản tiếng Việt còn cao hơn.

**Cách kiểm chứng tổng thể:** chạy `token_audit.py` trước và sau mỗi nhóm, so
`carry-cost tổng` và `api_calls` trên số request tương đương.
