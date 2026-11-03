# Bản chấm workflow TDQ theo hướng LLM đọc & chi phí context

Ngày: 2026-08-14 · Spec: ../spec/2026-08-14-toi-uu-llm-workflow.md · Phạm vi: `skills/` (28
file) · `hooks/` (6 file) · `agents/` (3 file). `scripts/`, `portable/`, `tests/` ngoài phạm vi.

Ràng buộc cứng của bản này: **không luật nào biến mất** và **mức chi tiết đủ để model
hạng thấp vẫn chạy đúng**. Mọi con số dưới đây là output lệnh chạy thật ngày 2026-08-14.

## Thang chấm

Sáu tiêu chí chốt TRƯỚC khi nhìn số đo. Mỗi tiêu chí chấm 0 (hỏng) · 1 (tạm) · 2 (đạt),
tối đa 12 điểm một file.

| Mã | Chấm cái gì | Lệnh đo | Thế nào là 2 điểm |
|---|---|---|---|
| R1 | Tầng nạp: nội dung có nằm đúng tầng `luôn nạp` / `nạp khi gọi` / `đọc khi cần` không | `python3 scripts/context_surface.py --quiet` | thân `SKILL.md` ≤ 2.000 token và không mục nào ≥ 20 dòng chỉ dùng cho một nhánh hiếm |
| R2 | Mật độ luật: bao nhiêu mệnh lệnh tuyệt đối trên 100 dòng | `grep -cEi "cấm\|bắt buộc\|phải \|không được\|luôn \|dừng\|ngay" <file>` chia số dòng | mật độ trong khoảng 10–30 luật/100 dòng |
| R3 | Luật trùng: cùng một luật viết lại ở ≥ 2 file mà không khai là nhắc lại | `grep -rn "<cụm luật>" skills/ \| cut -d: -f1 \| sort -u \| wc -l` | 0 luật trùng nguyên nghĩa, hoặc chỗ trùng có ghi rõ "nhắc lại có chủ ý" |
| R4 | Thuật ngữ: một khái niệm có đúng một tên chính | `grep -roE "lane\|pipeline\|chế độ nhanh\|express" skills/ \| sort \| uniq -c` | mỗi khái niệm 1 tên máy + tối đa 1 nhãn hiển thị, khai ở đúng một chỗ |
| R5 | Sẵn sàng cho model hạng thấp: 5 điều kiện (a) có khối copy được cho mọi đầu ra cần định dạng · (b) không câu điều kiện lồng quá 2 tầng · (c) có tiêu chí "xong khi" · (d) không từ mơ hồ thiếu ngưỡng · (e) bước đánh số tuyến tính | `grep -c '^```' <file>` · `grep -c "Xong khi" <file>` · `grep -cEi "phù hợp\|nếu cần\|tối ưu\|hợp lý\|linh hoạt" <file>` | đạt ≥ 4/5 điều kiện |
| R6 | Runtime: mili-giây mỗi lượt của phần chạy mỗi turn | `python3 scripts/context_surface.py --hooks --runs 9` | trung vị ≤ 150 ms mỗi hook |

Vì sao R5 không phải là "càng ngắn càng tốt": chuẩn viết skill nói mức chi tiết phải nhắm
vào model **yếu nhất** được hỗ trợ, và tài liệu prompt cho model nhỏ nói model nhỏ cần chỉ
dẫn chi tiết hơn, không ngắn hơn. Nên R5 chấm **độ rõ**, R1–R2 chấm **chỗ đặt và mật độ**;
cắt chữ mà làm rơi R5 là cắt sai.

## Bảng chấm skills

Bậc 1 và 0 suy ra máy móc từ ngưỡng "2 điểm" đã chốt ở mục trên: **1** = lệch nhẹ đúng
một điều kiện · **0** = lệch từ hai điều kiện trở lên, hoặc lệch nặng một điều kiện.
Cụ thể: R1 — 1 điểm nếu có đúng 1 mục ≥ 20 dòng chỉ dùng cho một nhánh, 0 nếu ≥ 2 mục ·
R2 — 1 điểm nếu mật độ 5–10 hoặc 30–40, 0 nếu < 5 hoặc > 40 · R3 — 1 nếu 1–2 luật nhắc
lại không khai, 0 nếu ≥ 3 · R4 — 1 nếu file dùng 3–4 biến thể tên, 0 nếu ≥ 5 · R5 — 1
nếu đạt 3/5 điều kiện, 0 nếu ≤ 2/5. R6 ghi `—` vì file `.md` không chạy mỗi turn; tổng
tính trên 10 điểm.

| file | tầng nạp | token | R1 | R2 | R3 | R4 | R5 | R6 | tổng | chỗ phí lớn nhất |
|---|---|---|---|---|---|---|---|---|---|---|
| skills/tdq-build/SKILL.md | nạp khi gọi skill | 1.936 | 0 | 2 | 1 | 2 | 2 | — | 7/10 | ba phần A/B/C (31+19+34 dòng) cho ba phase khác nhau nạp chung một lần |
| skills/tdq-build/references/qc.md | đọc khi cần | 697 | 2 | 1 | 2 | 2 | 2 | — | 9/10 | mật độ luật 6,7/100 dòng — phần lớn là văn giải thích |
| skills/tdq-build/references/report-template.md | đọc khi cần | 360 | 2 | 0 | 1 | 2 | 2 | — | 7/10 | 4,2 luật/100 dòng; nhắc lại luật "tiếng Việt" của `tdq-build/SKILL.md:85` |
| skills/tdq-conventions/SKILL.md | nạp khi gọi skill | 1.820 | 2 | 2 | 2 | 2 | 2 | — | 10/10 | không có |
| skills/tdq-conventions/references/approval.md | đọc khi cần | 535 | 2 | 2 | 2 | 2 | 2 | — | 10/10 | không có |
| skills/tdq-conventions/references/context-budget.md | đọc khi cần | 316 | 2 | 2 | 2 | 2 | 2 | — | 10/10 | không có |
| skills/tdq-conventions/references/measure-scenario.md | đọc khi cần | 550 | 2 | 1 | 2 | 2 | 2 | — | 9/10 | 7,5 luật/100 dòng |
| skills/tdq-conventions/references/phases.md | đọc khi cần | 1.302 | 2 | 2 | 2 | 2 | 2 | — | 10/10 | không có |
| skills/tdq-conventions/references/plugin-routing.md | đọc khi cần | 628 | 2 | 0 | 2 | 2 | 2 | — | 8/10 | 4,0 luật/100 dòng — bảng 29 dòng gần như thuần mô tả |
| skills/tdq-conventions/references/reminder-codes.md | đọc khi cần | 967 | 1 | 1 | 2 | 2 | 2 | — | 8/10 | mục "Hook nhìn thấy thay đổi bằng cách nào" 31 dòng thuần giải thích cơ chế |
| skills/tdq-conventions/references/subagent-tuning.md | đọc khi cần | 805 | 2 | 1 | 2 | 2 | 2 | — | 9/10 | 7,0 luật/100 dòng |
| skills/tdq-conventions/references/tavily.md | đọc khi cần | 485 | 2 | 0 | 2 | 2 | 2 | — | 8/10 | 0 mệnh lệnh tuyệt đối trên 27 dòng — toàn bộ là mô tả |
| skills/tdq-conventions/references/user-facing-block.md | đọc khi cần | 619 | 2 | 2 | 2 | 2 | 2 | — | 10/10 | không có |
| skills/tdq-conventions/references/worklog-images.md | đọc khi cần | 302 | 2 | 1 | 2 | 2 | 2 | — | 9/10 | 9,5 luật/100 dòng |
| skills/tdq-intake/SKILL.md | nạp khi gọi skill | 1.844 | 0 | 2 | 1 | 1 | 2 | — | 6/10 | Phần A (35 dòng) và Phần C (32 dòng) là hai nhánh loại trừ nhau nhưng luôn nạp cùng nhau; dòng 86 lọt tên máy `lane deep` vào câu văn |
| skills/tdq-intake/references/analyze-full.md | đọc khi cần | 1.162 | 2 | 1 | 2 | 2 | 2 | — | 9/10 | 8,3 luật/100 dòng; 3 dòng gộp ≥ 2 nhánh `→` trong một câu |
| skills/tdq-intake/references/interview.md | đọc khi cần | 1.178 | 2 | 2 | 2 | 2 | 2 | — | 10/10 | không có |
| skills/tdq-intake/references/issue-triage.md | đọc khi cần | 483 | 2 | 2 | 2 | 2 | 2 | — | 10/10 | không có |
| skills/tdq-intake/references/lane-decision.md | đọc khi cần | 860 | 2 | 1 | 2 | 2 | 2 | — | 9/10 | 8,7 luật/100 dòng |
| skills/tdq-intake/references/quick-lane.md | đọc khi cần | 1.468 | 2 | 1 | 1 | 2 | 2 | — | 8/10 | chép lại quy tắc tick `[~]/[x]` và dòng "Ước tính sẽ dùng skill" của `tdq-intake/SKILL.md` mà không khai là nhắc lại |
| skills/tdq-intake/references/scope-round.md | đọc khi cần | 1.658 | 2 | 1 | 2 | 2 | 1 | — | 8/10 | reference nặng nhất (1.658 token); 2 dòng dùng từ mơ hồ không kèm ngưỡng |
| skills/tdq-intake/references/skill-inventory.md | đọc khi cần | 813 | 2 | 1 | 1 | 2 | 2 | — | 8/10 | 5,8 luật/100 dòng; nhắc lại dòng "Ước tính sẽ dùng skill" |
| skills/tdq-plan/SKILL.md | nạp khi gọi skill | 1.563 | 2 | 2 | 1 | 2 | 1 | — | 8/10 | mục "Các bước" 87 dòng liền một mạch, không khối copy được, có 1 từ mơ hồ thiếu ngưỡng |
| skills/tdq-plan/references/mode-gate.md | đọc khi cần | 528 | 2 | 1 | 2 | 2 | 2 | — | 9/10 | 6,5 luật/100 dòng |
| skills/tdq-plan/references/plan-template.md | đọc khi cần | 1.538 | 2 | 2 | 2 | 2 | 2 | — | 10/10 | không có |
| skills/tdq-spec/SKILL.md | nạp khi gọi skill | 862 | 2 | 2 | 1 | 2 | 2 | — | 9/10 | mục "Các bước" 60 dòng không có khối copy được cho khuôn spec |
| skills/tdq-spec/references/spec-template.md | đọc khi cần | 1.072 | 2 | 1 | 2 | 2 | 1 | — | 8/10 | 8,6 luật/100 dòng, 1 từ mơ hồ thiếu ngưỡng, không bước đánh số |
| skills/tdq-status/SKILL.md | nạp khi gọi skill | 449 | 2 | 1 | 1 | 2 | 2 | — | 8/10 | 5,6 luật/100 dòng; nhắc lại luật "tiếng Việt" |

Tổng: 28 file · 205 mệnh lệnh tuyệt đối · trung bình 8,7/10 (244/280). Thấp nhất là 6/10;
hai file kéo điểm là hai `SKILL.md` lớn nhất (`tdq-intake` 6/10, `tdq-build` 7/10) và cả
hai đều mất điểm ở **R1 tầng nạp**, không phải ở độ rõ.

Ghi chú R4: đếm thô ra 8 biến thể tên cho khái niệm lane, nhưng đọc kỹ thì `pipeline` là
nhãn hiển thị đã khai tường minh ở `skills/tdq-intake/references/lane-decision.md:45`
(*gọi "lane" là "pipeline" khi hỏi user*), còn `(express)`/`(deep)` chỉ là chú trong
chính nhãn `chế độ nhanh (express)`. Đúng khuôn "1 tên máy + 1 nhãn hiển thị". Chỉ còn
đúng một chỗ lọt: `skills/tdq-intake/SKILL.md:86` viết `lane deep` trong câu văn. Bảng
trên đã chấm theo cách hiểu này, không theo số đếm thô.

## Bảng chấm hooks & agents

Hook chạy mỗi turn nên chấm bằng hai số: mili-giây (`context_surface.py --hooks --runs 9`,
trung vị 9 lần) và **byte đổ vào context**. Byte đo lại bằng chính bộ tình huống của
`context_surface.py`, chạy trên project tạm rỗng.

| file | vai trò | trung vị ms | byte ra context | dòng mã | R6 | ghi chú |
|---|---|---|---|---|---|---|
| hooks/scripts/_common.py | thư viện dùng chung | không chạy trực tiếp | 0 | 183 | — | chỉ được các hook khác import |
| hooks/scripts/session_start.py | nạp lời nhắc đầu phiên | 31,7 (startup) · 28,9 (compact) | 566 ≈ 142 token | 40 | 2 | mỗi phiên 1 lần |
| hooks/scripts/prompt_context.py | chèn `[TDQ:NEXT]` mỗi prompt | 56,2 | 129 ≈ 32 token | 236 | 2 | hook chậm nhất nhưng vẫn dưới 1/2 ngưỡng |
| hooks/scripts/edit_gate.py | chặn sửa mã khi plan chưa `[~]` | 30,9 (mã) · 29,1 (tài liệu) | 402 khi chặn · 0 khi cho qua | 145 | 2 | chỉ tốn byte ở đúng lần bị chặn |
| hooks/scripts/bash_gate.py | soi lệnh bash | 32,1 | 0 | 133 | 2 | im lặng khi hợp lệ |
| hooks/scripts/stop_gate.py | chặn kết thúc turn khi thiếu sổ | 35,9 | 412 khi chặn · 0 khi sạch | 202 | 2 | |
| agents/tdq-implementer.md | agent con làm 1 task | không chạy mỗi turn | 51 (description) + 556 (thân) | 20 dòng | — | R1 2 · R2 1 (5,0 luật/100 dòng) · R3 2 · R4 2 · R5 1 → 8/10 |
| agents/tdq-qc-tester.md | agent con kiểm DoD | không chạy mỗi turn | 64 + 338 | 18 dòng | — | R1 2 · R2 1 (5,6) · R3 2 · R4 2 · R5 1 → 8/10 |
| agents/tdq-reviewer.md | agent con soát spec/plan | không chạy mỗi turn | 58 + 323 | 20 dòng | — | R1 2 · R2 1 (5,0) · R3 2 · R4 2 · R5 1 → 8/10 |

Kết luận vùng runtime: **hook không phải chỗ phí**. Trung vị cao nhất 56,2 ms, thấp hơn
ngưỡng 150 ms của R6; tổng byte tối đa một turn khi mọi hook đều chặn là 2.075 byte
≈ 520 token, và trong turn bình thường (không bị chặn) chỉ còn 129 byte.

Cả ba agent đều mất điểm R5 ở cùng một chỗ: phần "Return"/"Report" tả bằng văn xuôi,
không có khối định dạng copy được, và toàn bộ ba file viết tiếng Anh trong khi mọi
đầu ra của workflow là tiếng Việt.

## Chỗ phí

Tám mục, xếp theo lượng token cắt được. Cột cuối đối chiếu với hai vòng tối ưu gần nhất
(`2026-08-05-toi-uu-token-vong-2`, `2026-08-08-giam-over-engineer-workflow`) để không đề
xuất lại thứ đã cắt.

| Mã | Chỗ phí | Số đo | Vị trí | So với vòng trước |
|---|---|---|---|---|
| F1 | `skill_inventory.py` in nguyên bảng kiểm kê vào context ở bước B0 | 39.722 byte (39.097 ký tự) ≈ 9.774 token mỗi lần chạy, 89 ms · 286 dòng, 31 nguồn skill, trong đó `plugin:tdq-workflow` chỉ chiếm 6 dòng/930 ký tự | `scripts/skill_inventory.py` gọi từ `skills/tdq-intake/references/analyze-full.md` | mới — vòng 2026-08-05 chỉ đo `doc_lint` 607 ký tự và test 1.037 ký tự, chưa soi script này |
| F2 | Thân `tdq-intake/SKILL.md` nạp cả hai nhánh loại trừ nhau | 1.844 token/lần gọi, trong đó Phần C (chế độ nhanh) 32 dòng ≈ 611 token không dùng khi chạy chế độ chuyên sâu, và Phần B 16 dòng không dùng khi chạy chế độ nhanh | `skills/tdq-intake/SKILL.md:78-109` | mới — vòng 2026-08-08 gộp thư mục output, không đụng cấu trúc thân skill |
| F3 | Thân `tdq-build/SKILL.md` gộp ba phase vào một lần nạp | 1.936 token nạp lại ở cả `implement`, `qc`, `report`; mỗi lần chỉ dùng 1 trong 3 mục — Phần A 538 · Phần B 255 · Phần C 361 token, tức ~616 token chết mỗi lần nạp | `skills/tdq-build/SKILL.md` | mới |
| F4 | Mục thuần giải thích nằm trong reference đang được đọc thật | `reminder-codes.md` mục "Hook nhìn thấy thay đổi bằng cách nào" 31 dòng ≈ 500 token · `plugin-routing.md` bảng 29 dòng ở mật độ 4,0 luật/100 dòng ≈ 628 token · `tavily.md` 27 dòng, 0 mệnh lệnh tuyệt đối ≈ 485 token | `skills/tdq-conventions/references/reminder-codes.md:29`, `plugin-routing.md`, `tavily.md` | mới |
| F5 | `scope-round.md` là reference nặng nhất và có từ mơ hồ thiếu ngưỡng | 1.658 token, 115 dòng, mật độ 7,0 luật/100 dòng; 2 dòng mơ hồ (dòng 35, dòng 88) | `skills/tdq-intake/references/scope-round.md` | mới — file sinh ra ở vòng 2026-08-08 nên chưa qua đợt rà nào |
| F6 | Luật nhắc lại giữa các file mà không khai là nhắc lại | "tiếng Việt" ở 7 file · `tdq_state.py` ở 13 file · tick `[~]` ở 5 file · "Ước tính sẽ dùng skill" ở 3 file · luật "nhãn hiển thị" khai 3 lần rời nhau; 0 chỗ nào ghi "nhắc lại có chủ ý" | `skills/tdq-conventions/SKILL.md:10` + 6 file nhắc lại; `skills/tdq-plan/SKILL.md:90` và `skills/tdq-plan/references/mode-gate.md:44` khai trùng luật nhãn | mới |
| F7 | Ba file agent không có khối định dạng đầu ra copy được | 3/3 file, 0 khối ```; phần trả kết quả tả bằng văn xuôi; mật độ luật 5,0–5,6/100 dòng | `agents/tdq-implementer.md:20`, `agents/tdq-qc-tester.md`, `agents/tdq-reviewer.md` | đã cắt một phần ở 2026-08-05 (mục 6: đặt tên agent theo `<model>-<effort>`), còn dư phần định dạng đầu ra |
| F8 | Thiếu bảng thuật ngữ dùng chung; một chỗ lọt tên máy ra câu văn | luật nhãn hiển thị khai ở 3 chỗ khác nhau (`lane-decision.md:45`, `tdq-plan/SKILL.md:90`, `mode-gate.md:44`); 1 chỗ lọt `lane deep` | `skills/tdq-intake/SKILL.md:86` | mới — chưa vòng nào chuẩn hoá thuật ngữ |

Một ghi chú đối chiếu nằm ngoài phạm vi: quyết định số 9 của vòng 2026-08-08 ("xoá hẳn
`portable/`") không còn đúng với hiện trạng — `portable/` vẫn còn 12 file, 13.075 token
ở tầng `đọc khi cần`. Việc này thuộc request riêng, xem mục `## Nguồn`.

## Đề xuất

Bảy đề xuất, mỗi đề xuất đủ 7 trường. `- Mức:` chỉ nhận hai giá trị: `thuần văn bản`
(chỉ sửa `.md`) hoặc `đụng script` (phải sửa file `.py`). Hai trường cuối là cổng loại:
đề xuất nào làm **xấu** cột "tác động model hạng thấp" thì bị loại ngay, không đưa vào gói.
Quy ước đọc: trong khối `Nội dung nháp`, dòng tiêu đề Markdown được thụt 2 space để không
lẫn với mục của chính tài liệu này — khi dán vào file thật thì bỏ 2 space đầu dòng.

### Đ1 — Cho `skill_inventory.py` một chế độ lọc, giữ nguyên đường xem đủ

- Chặn: F1
- Chèn vào: `scripts/skill_inventory.py` (thêm cờ) · `skills/tdq-intake/references/analyze-full.md:7` và `skills/tdq-intake/references/skill-inventory.md:10` (đổi lệnh gọi)
- Mức: đụng script
- Nội dung nháp:

```
# analyze-full.md bước 1, thay dòng lệnh hiện tại:
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/skill_inventory.py" --loc "<3-6 từ khoá của request>"
# In ra: các dòng khớp từ khoá + luôn in đủ nguồn `project` và `plugin:tdq-workflow`,
# rồi một dòng cuối bắt buộc:
#   (đã ẩn N skill không khớp — BẮT BUỘC chạy lại với --tat-ca nếu chưa đủ căn cứ phán quyết)
```

- Cách kiểm: `python3 scripts/skill_inventory.py --loc "workflow" | wc -c` nhỏ hơn `python3 scripts/skill_inventory.py | wc -c`; và `--tat-ca` cho ra đúng output hiện nay (so bằng `diff`)
- Tác động token: từ 39.722 byte ≈ 9.774 token xuống còn phần khớp + 6 dòng `plugin:tdq-workflow` + 33 dòng `user`; với một request thuần workflow ước còn ≈ 1.500–2.500 token, tiết kiệm ≈ 7.000 token mỗi lần chạy analyze
- Tác động model hạng thấp: **tốt hơn** — model hạng thấp phải đọc 286 dòng rồi tự lọc là chỗ dễ bỏ sót nhất; bản lọc đưa thẳng danh sách ngắn, và dòng cuối là một mệnh lệnh tuyệt đối chỉ đúng lệnh phải chạy khi chưa đủ căn cứ, nên đường xem đủ không mất

### Đ2 — Đưa Phần C của `tdq-intake/SKILL.md` về `references/quick-lane.md`

- Chặn: F2 · F8 (chỗ lọt tên máy `lane deep` ở `tdq-intake/SKILL.md:86` nằm trong Phần C bị xoá, nên biến mất kèm theo)
- Chèn vào: `skills/tdq-intake/SKILL.md:78-109` (cắt đi) · `skills/tdq-intake/references/quick-lane.md` (nhận vào)
- Mức: thuần văn bản
- Nội dung nháp:

```
  ## Phần C — Chế độ nhanh (express)

Chế độ nhanh = rút gọn, KHÔNG cắt bước tư duy. Chốt lane `quick` xong, BẮT BUỘC đọc
[references/quick-lane.md](references/quick-lane.md) và làm đúng 9 bước trong đó trước
khi sửa bất kỳ file nào. Cấm làm chế độ nhanh bằng trí nhớ.

Xong khi: `quick_approved = true`, log đã ghi, mục `## QC` đã có, không còn test đỏ.
```

- Cách kiểm: `grep -c "" skills/tdq-intake/SKILL.md` giảm ≈ 26 dòng; `grep -c "^[0-9]\. " skills/tdq-intake/references/quick-lane.md` vẫn đủ 9 bước; đếm mệnh lệnh của **cặp hai file** không giảm (xem `## Đối chiếu luật`)
- Tác động token: −611 token mỗi lần gọi `tdq-intake` ở chế độ chuyên sâu, cộng thêm 4 dòng trỏ (≈ 60 token) → net ≈ −550 token/lần
- Tác động model hạng thấp: **tốt hơn** — bước 9 của chế độ nhanh vốn đã nằm đầy đủ ở `quick-lane.md`; bản rút gọn trong thân skill hiện là bản tóm tắt song song, tức hai nguồn cho cùng một quy trình. Bỏ bản tóm tắt để chỉ còn một nguồn duy nhất, cộng một mệnh lệnh tuyệt đối bắt phải mở file đó

### Đ3 — Đưa Phần B và Phần C của `tdq-build/SKILL.md` về hai reference đã có

- Chặn: F3
- Chèn vào: `skills/tdq-build/SKILL.md:64-116` (cắt đi) · `skills/tdq-build/references/qc.md` và `skills/tdq-build/references/report-template.md` (nhận vào)
- Mức: thuần văn bản
- Nội dung nháp:

```
  ## Phần B — QC (phase `qc`)
BẮT BUỘC đọc [references/qc.md](references/qc.md) rồi làm đúng từng dòng DoD của plan.
Xong khi: mọi dòng DoD có bằng chứng, không dòng nào FAIL.

  ## Phần C — Report (phase `report`)
BẮT BUỘC đọc [references/report-template.md](references/report-template.md) rồi viết
`docs/tdq/reports/<slug>.md`. Xong khi: report tồn tại và `doc_lint.py` exit 0.
```

- Cách kiểm: `python3 scripts/context_surface.py --quiet | grep "tdq-build/SKILL.md (thân)"` cho token < 1.400; đếm mệnh lệnh của **cụm ba file** không giảm
- Tác động token: thân từ 1.936 xuống ≈ 1.320 token; phase `implement` (chiếm nhiều lượt gọi nhất) tiết kiệm ≈ 616 token mỗi lần nạp
- Tác động model hạng thấp: **giữ nguyên** — hai reference nhận nội dung vốn đã là file được trỏ tới ở đúng hai phase đó; mỗi mục cắt đi đều để lại một mệnh lệnh "BẮT BUỘC đọc" cộng một dòng "Xong khi", tức thêm tiêu chí dừng mà trước đây Phần B không có

### Đ4 — Cắt mục thuần giải thích, đẩy xuống cuối file dưới nhãn phụ lục

- Chặn: F4
- Chèn vào: `skills/tdq-conventions/references/reminder-codes.md:29-60` · `skills/tdq-conventions/references/plugin-routing.md` · `skills/tdq-conventions/references/tavily.md`
- Mức: thuần văn bản
- Nội dung nháp:

```
  ## Phụ lục — cơ chế (không cần đọc để làm đúng)

Mục dưới đây giải thích hook nhìn thấy thay đổi bằng cách nào. KHÔNG có luật nào ở đây.
Chỉ đọc khi đang sửa chính hook; làm workflow bình thường thì dừng ở trên.
```

- Cách kiểm: `grep -cEi "cấm|bắt buộc|phải |không được|luôn |dừng|ngay" <file>` giữ nguyên số trước/sau ở cả ba file; `grep -c "^## Phụ lục" skills/tdq-conventions/references/reminder-codes.md` = 1
- Tác động token: không giảm token của file, nhưng dựng ranh giới đọc rõ ràng — người/model đọc reference có thể dừng sớm ≈ 500 token ở `reminder-codes.md`. Đây là đề xuất **rẻ nhất và ít lợi nhất** trong bảy
- Tác động model hạng thấp: **tốt hơn** — một dòng nói thẳng "không có luật nào ở đây" loại được rủi ro model hạng thấp đọc văn giải thích rồi suy ra luật không tồn tại

### Đ5 — Thay 2 dòng mơ hồ của `scope-round.md` bằng ngưỡng đếm được

- Chặn: F5
- Chèn vào: `skills/tdq-intake/references/scope-round.md:35` và `:88`
- Mức: thuần văn bản
- Nội dung nháp:

```
# Dòng 35 hiện tại (nguyên văn):
#   bảo mật · bảo trì · linh hoạt (mở rộng, đa nền tảng) · an toàn. Khung này chỉ để bạn
# Thay bằng:
    bảo mật · bảo trì · mở rộng (thêm nền tảng/tính năng mà không sửa lõi) · an toàn.
    Khung này chỉ để bạn

# Dòng 88 hiện tại (nguyên văn):
#   | Prototype/R&D, quy mô nhỏ, một người giữ | lõi | làm đúng luồng chính, không tối ưu sớm, DoD gọn |
# Thay bằng:
    | Prototype/R&D, quy mô nhỏ, một người giữ | lõi | làm đúng luồng chính, cấm thêm
    nhánh chưa có người dùng thật, DoD ≤ 5 dòng |
```

- Cách kiểm: `grep -cEi "phù hợp|nếu cần|tối ưu|hợp lý|linh hoạt" skills/tdq-intake/references/scope-round.md` = 0 (trước: 2)
- Tác động token: ≈ 0 (đổi chữ, không đổi độ dài đáng kể)
- Tác động model hạng thấp: **tốt hơn** — "không tối ưu sớm" và "DoD gọn" là hai chỉ dẫn model hạng thấp không đo được; bản thay có ngưỡng đếm được (`≤ 5 dòng`) và một mệnh lệnh tuyệt đối, nâng R5 của file từ 1 lên 2

### Đ6 — Khai "nhắc lại có chủ ý" tại mọi chỗ luật được nói lại

- Chặn: F6 · F8 (phần "luật nhãn hiển thị khai ở 3 chỗ" — khai nguồn gốc xong chỉ còn 1 bản gốc)
- Chèn vào: `skills/tdq-build/SKILL.md:85` · `skills/tdq-build/references/report-template.md:3` · `skills/tdq-spec/SKILL.md:8` · `skills/tdq-plan/SKILL.md:8` · `skills/tdq-status/SKILL.md:8` · `skills/tdq-intake/references/quick-lane.md` · `skills/tdq-intake/references/skill-inventory.md` · `skills/tdq-plan/references/mode-gate.md:44`
- Mức: thuần văn bản
- Nội dung nháp:

```
# Khuôn cố định, dán vào cuối dòng nhắc lại:
    (nhắc lại có chủ ý — nguồn gốc: skills/tdq-conventions/SKILL.md:10)
# Áp cho 4 cụm luật đang bị nhắc lại: "tiếng Việt" (7 file), tick `[~]/[x]` (5 file),
# "Ước tính sẽ dùng skill" (3 file), luật nhãn hiển thị (3 file).
```

- Cách kiểm: `grep -rc "nhắc lại có chủ ý" skills/ | grep -v ":0" | wc -l` ≥ 8; và với mỗi cụm luật, `grep -rl "<cụm>" skills/` trừ đi file nguồn phải bằng số file có ghi chú
- Tác động token: **tăng** ≈ 60 ký tự × 8 chỗ ≈ +120 token tổng, phân bổ trên các file `đọc khi cần`
- Tác động model hạng thấp: **tốt hơn** — model hạng thấp gặp cùng một luật ở hai file dễ suy ra "hai luật khác nhau" hoặc "bản sau ghi đè bản trước"; câu khai nguồn gốc chặn đúng suy diễn đó. Đây là chỗ **chấp nhận tốn thêm token để giữ tuân thủ**, đúng thứ tự ưu tiên đã chốt ở spec

### Đ7 — Thêm khối định dạng đầu ra copy được cho ba agent

- Chặn: F7
- Chèn vào: `agents/tdq-implementer.md:20` · `agents/tdq-qc-tester.md` · `agents/tdq-reviewer.md`
- Mức: thuần văn bản
- Nội dung nháp:

```
# Dòng 20 hiện tại của tdq-implementer.md (nguyên văn):
#   Return (as your final message): status (done/blocked) for your one task ID, files
#   changed, test command + actual result, notes. Plus the branch name and whether the
#   worktree is merge-ready.
# Thay bằng: giữ nguyên câu trên, rồi thêm khối BẮT BUỘC theo đúng khuôn này:

    Task: <mã task>
    Trạng thái: done | blocked
    File đã sửa: <đường dẫn, mỗi dòng một file>
    Lệnh test: <lệnh>
    Kết quả: <1 dòng, dán đúng dòng kết luận của test>
    Branch: <tên branch> · merge-ready: có | không
    Ghi chú: <≤ 2 dòng, hoặc "không">
```

- Cách kiểm: `grep -c '^```' agents/*.md` ≥ 2 mỗi file; chạy thử một task nhỏ bằng `tdq-implementer` và đối chiếu final message với khuôn
- Tác động token: **tăng** ≈ 90 token mỗi file agent ở tầng `đọc khi cần` (chỉ nạp khi thật sự chạy agent con), tổng +270 token; bù lại digest trả về ngắn và cố định, ước cắt được phần lớn khoản "digest subagent quá dài" mà vòng 2026-08-05 đo là trung bình 3.331 ký tự, cực đại 13.160
- Tác động model hạng thấp: **tốt hơn** — đây là chỗ hỏng rõ nhất cho model hạng thấp: đầu ra bắt buộc đang được tả bằng văn xuôi tiếng Anh, không có khuôn để chép. Có khối copy được thì agent hạng thấp chỉ cần điền chỗ trống

## Đối chiếu luật

Đếm mệnh lệnh tuyệt đối trước và sau khi áp nháp, bằng
`grep -cEi "cấm|bắt buộc|phải |không được|luôn |dừng|ngay" <file>`. Đề xuất nào **dời**
nội dung giữa hai file thì đếm theo **cụm file** — vì luật đi cùng đoạn văn, tách ra đếm
riêng sẽ báo sai. Cột "sau" không dòng nào được nhỏ hơn cột "trước".

| Đề xuất | File / cụm file bị đụng | luật trước | luật sau | chênh |
|---|---|---|---|---|
| Đ1 | `skills/tdq-intake/references/analyze-full.md` | 5 | 6 | +1 |
| Đ1 | `skills/tdq-intake/references/skill-inventory.md` | 4 | 5 | +1 |
| Đ2 | `skills/tdq-intake/SKILL.md` + `references/quick-lane.md` (đếm luật riêng biệt, xem chú thích) | 17 | 19 | +2 |
| Đ3 | `skills/tdq-build/SKILL.md` + `references/qc.md` + `references/report-template.md` | 23 | 25 | +2 |
| Đ4 | `skills/tdq-conventions/references/reminder-codes.md` | 5 | 6 | +1 |
| Đ4 | `skills/tdq-conventions/references/plugin-routing.md` | 2 | 2 | 0 |
| Đ4 | `skills/tdq-conventions/references/tavily.md` | 0 | 0 | 0 |
| Đ5 | `skills/tdq-intake/references/scope-round.md` | 8 | 9 | +1 |
| Đ6 | 8 file nhắc lại (build/SKILL, report-template, spec/SKILL, plan/SKILL, status/SKILL, quick-lane, skill-inventory, mode-gate) | 72 | 72 | 0 |
| Đ7 | `agents/tdq-implementer.md` + `tdq-qc-tester.md` + `tdq-reviewer.md` | 3 | 6 | +3 |

Không dòng nào có "sau" < "trước": 7/10 dòng tăng, 3 dòng giữ nguyên, 0 dòng giảm. Không
cộng tổng toàn bảng vì các cụm file giao nhau (`build/SKILL.md` vừa nằm ở Đ3 vừa nằm ở Đ6),
cộng lại sẽ đếm trùng. Nói gọn: gói đề xuất này **cắt token mà tăng số luật**, đúng ràng
buộc "không luật nào biến mất" và đúng thứ tự ưu tiên "tuân thủ thắng khi xung đột".

Ba chỗ chênh 0 là cố ý: Đ4 chỉ dựng ranh giới đọc, Đ6 chỉ dán chú nguồn gốc — cả hai
không đụng câu luật nào, nên số đếm phải bằng nhau; nếu số đổi thì tức là đã sửa nhầm luật.

Chú thích cách đếm của Đ2. Đếm thô ra 11 (thân `tdq-intake`) + 10 (`quick-lane.md`) = 21,
nhưng cả 4 mệnh lệnh trong Phần C đều đã có bản đầy đủ trong `quick-lane.md`, đối chiếu
từng dòng: tick `[~]`→`[x]` ngay (`quick-lane.md:80,123`) · cấm gom tick cuối turn
(`:82`) · dòng `➤ Duyệt: …` nguyên văn (`:71`) · trần 3 vòng rồi DỪNG (`:125`). Vậy số
luật RIÊNG BIỆT trước khi sửa là 17. Sau khi sửa: 7 (thân, đã bỏ 4 dòng trùng) + 10
(`quick-lane.md`, giữ nguyên) + 2 mệnh lệnh mới ở khối trỏ = 19. Đây chính là lý do Đ2
an toàn: nó xoá **bản sao**, không xoá luật.

## Gói

Ba gói dưới đây là ba mức đầu tư, không phải ba phương án loại trừ nhau — gói sau chứa
trọn gói trước. Con số "chi phí" là ước tính công sửa tay.

### Gói tối thiểu — Đ2 + Đ3

Chỉ hai đề xuất chuyển chỗ, cả hai thuần văn bản, không đụng `scripts/`, không đụng test.

- Đụng: `tdq-intake/SKILL.md`, `tdq-build/SKILL.md`, `references/quick-lane.md`,
  `references/qc.md`, `references/report-template.md`.
- Được: thân `tdq-intake` từ 1.844 → ≈ 1.290 token · thân `tdq-build` từ 1.936 → ≈ 1.320
  token. Cộng lại **≈ 1.170 token mỗi lần gọi skill**, và đây là hai skill được gọi nhiều
  nhất trong một request `full`.
- Luật: 17 → 19 (Đ2) và 23 → 25 (Đ3). Không luật nào mất.
- Chi phí: ước tính 40–60 phút; rủi ro thấp nhất trong ba gói vì chỉ cắt–dán nguyên khối.
- Bỏ lại: toàn bộ phần phục vụ độ tuân thủ của model hạng thấp (Đ5, Đ6, Đ7).

### Gói vừa — Đ2 + Đ3 + Đ5 + Đ6 + Đ7

Toàn bộ đề xuất **thuần văn bản**. Đây là ranh giới tự nhiên: đúng bằng phần làm được mà
không chạm một dòng mã nào, nên không cần thêm test và không có rủi ro hồi quy runtime.

- Thêm so với gói tối thiểu: 2 dòng mơ hồ của `scope-round.md` thành ngưỡng đếm được (Đ5) ·
  8 chỗ nhắc lại luật được khai nguồn gốc (Đ6) · 3 file agent có khối đầu ra copy được (Đ7).
- Token: **−1.170** ở tầng `nạp khi gọi skill`, **+390** ở tầng `đọc khi cần` (Đ6 +120,
  Đ7 +270). Net vẫn âm, và khoản âm nằm ở tầng đắt hơn — tầng `nạp khi gọi` vào context
  mỗi lần gọi skill, tầng `đọc khi cần` chỉ vào khi có ai đọc thật.
- Luật: tăng ở 5/5 nhóm, không nhóm nào giảm — xem `## Đối chiếu luật`.
- Chi phí: ước tính 2–3 giờ.
- Bỏ lại: khoản tiết kiệm lớn nhất (Đ1) và việc dựng ranh giới đọc trong reference (Đ4).

### Gói đầy đủ — cả bảy đề xuất

Gói vừa cộng Đ1 (`skill_inventory.py` có chế độ lọc) và Đ4 (đẩy mục thuần giải thích
xuống phụ lục).

- Thêm: **≈ 7.000 token mỗi lần chạy analyze** nhờ Đ1 — một mình nó lớn hơn sáu đề xuất
  còn lại cộng lại.
- Nhưng Đ1 là đề xuất DUY NHẤT sửa mã: cần một cờ mới, một test cho cờ đó, và một test
  giữ nguyên hành vi mặc định. Đó là lý do nó không nằm trong gói vừa.
- Chi phí: ước tính 4–6 giờ, Đ1 chiếm quá nửa.

Khuyến nghị: Gói vừa — rồi mở một request riêng chỉ cho Đ1.

Vì sao không khuyến nghị thẳng gói đầy đủ dù nó tiết kiệm nhiều nhất: request này đã chốt
phạm vi "dừng ở đề xuất, không đụng `scripts/`", nên Đ1 chưa từng đi qua một spec nào cân
phần rủi ro của nó — lọc bớt đầu ra kiểm kê nghĩa là chấp nhận nguy cơ giấu mất một năng
lực đáng dùng ở bước B0. Rủi ro đó phải được nêu và kiểm bằng test riêng, không nên đi kèm
một đợt sửa tài liệu. Gói vừa lấy trọn phần không rủi ro; Đ1 không mất đi đâu cả.

Vì sao không khuyến nghị gói tối thiểu: nó bỏ đúng ba đề xuất phục vụ mục tiêu thứ hai của
request — model hạng thấp vẫn tuân đủ rule. Cắt 1.170 token mà bỏ Đ6/Đ7 là tối ưu sai trục.

## Công cụ đo lại

Bản chấm này sẽ cũ đi sau vài lần sửa skill. Dưới đây là nháp mở rộng
`scripts/context_surface.py` để chấm lại bằng lệnh thay vì đọc tay. **Chỉ là nháp —
request này không sửa file script.**

Thêm một hàm và hai cờ:

```python
# Nháp — thêm vào scripts/context_surface.py, KHÔNG áp trong request này.
import re
IMPERATIVE = re.compile(r"cấm|bắt buộc|phải |không được|luôn |dừng|ngay", re.I)
VAGUE      = re.compile(r"phù hợp|nếu cần|tối ưu|hợp lý|linh hoạt", re.I)

def rule_stats(path):
    """Trả về (số dòng, số mệnh lệnh tuyệt đối, mật độ /100 dòng, số từ mơ hồ)."""
    lines = path.read_text().splitlines()
    imp   = sum(1 for l in lines if IMPERATIVE.search(l))
    vague = sum(1 for l in lines if VAGUE.search(l))
    return len(lines), imp, round(imp * 100 / max(len(lines), 1), 1), vague

# --rules : in bảng file · dòng · luật · mật độ · từ mơ hồ, sắp theo mật độ tăng dần.
#           Đây là cột chấm R2 và một phần R5.
# --bytes : với mỗi hook, in len(stdout)+len(stderr) cạnh cột ms đã có sẵn.
#           Byte mới là thứ vào context; ms chỉ là độ trễ. Hôm nay tổng là 2.075 B/lượt.
```

Vì sao hai cột này chứ không phải "tổng token": tổng token đã có sẵn ở bảng bề mặt, nhưng
bảng đó không nói *token đó đang mua được bao nhiêu luật*. R2 và R5 cần đúng hai con số
trên, và cả hai đếm được bằng regex — không cần model đọc, nên chấm lại gần như miễn phí.

Lệnh chạy được ngay hôm nay, không cần sửa script. Đã chạy thật: exit 0, in đúng tổng
28 file / 205 luật, khớp với `## Bảng chấm skills`.

```bash
python3 -c '
import re, pathlib
IMP = re.compile(r"cấm|bắt buộc|phải |không được|luôn |dừng|ngay", re.I)
rows = []
for f in sorted(pathlib.Path("skills").rglob("*.md")):
    L = f.read_text().splitlines()
    n = sum(1 for l in L if IMP.search(l))
    rows.append((str(f), len(L), n, round(n * 100 / max(len(L), 1), 1)))
rows.sort(key=lambda r: r[3])
for path, nl, n, d in rows:
    print(f"{d:5}  {n:3}/{nl:3}  {path}")
print("tong file:", len(rows), "tong luat:", sum(r[2] for r in rows))
'
```

Cách dùng: chạy trước và sau khi áp một gói rồi `diff` hai đầu ra. Dòng nào có cột "luật"
**giảm** là dấu hiệu đã làm rơi một luật — dừng lại và kiểm, vì ràng buộc của bản này là
không luật nào biến mất. Cột mật độ tăng mà số luật giữ nguyên là dấu hiệu tốt: cắt đúng
phần văn giải thích.

## Nguồn

Chuẩn viết skill cho agent — nạp theo tầng, một khái niệm một tên, mỗi đoạn phải tự trả
giá token của nó (dùng cho R1, R3, R4):

- https://github.com/obra/superpowers/blob/main/skills/writing-skills/anthropic-best-practices.md
- https://generativeprogrammer.com/p/skill-authoring-patterns-from-anthropics
- https://medium.com/@nimritakoul01/anthropics-agent-skills-0ef767d72b0f

Model hạng thấp và độ tuân thủ chỉ dẫn — chi tiết hơn chứ không ngắn hơn, bước tuần tự,
checklist copy được (dùng cho R5 và cho quy tắc "tuân thủ thắng khi xung đột"):

- https://web.dev/articles/practical-prompt-engineering
- https://pub.towardsai.net/ultimate-guide-to-prompt-engineering-940d463ba0e5
- https://cameronrwolfe.substack.com/p/modern-advances-in-prompt-engineering

Nguồn nội bộ, dùng để không đề xuất lại thứ đã cắt: `docs/tdq/knowledge/2026-08-05-toi-uu-token-vong-2.md` ·
`docs/tdq/knowledge/2026-08-08-giam-over-engineer-workflow.md` ·
`docs/tdq/research/2026-08-14-toi-uu-llm-workflow.md`.

Ngoài phạm vi: `portable/` (12 file, 13.075 token — đường dành cho agent ngoài Claude)
KHÔNG được chấm trong bản này. Áp cùng sáu tiêu chí R1–R6 cho `portable/` là **một request
riêng**, và nó đáng mở: `portable/` chính là chỗ model hạng thấp chạy nhiều nhất, nên R5
ở đó còn quan trọng hơn ở `skills/`.
