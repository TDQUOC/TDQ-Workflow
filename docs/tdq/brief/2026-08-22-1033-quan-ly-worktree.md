# BRIEF — Quản lý vòng đời worktree của workflow

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> okay bây giờ tôi muốn mở request thêm update cho tdq workflow là khi mà workflow tạo worktree sẽ có quản lí trong docs/tdq và mỗi worktree được tạo ra khi đã code xong thì sẽ luôn check để ưu tiên merge lại và xóa worktree để tiết kiệm disk usage hẫy mở request check xem có khả thi không report đề xuất phương án cho tôi

**Đọc lần đầu**

- Mục tiêu: mọi worktree do workflow sinh ra (mode `subagent`, agent `tdq-implementer`) đều được ghi sổ trong `docs/tdq`, và khi task code xong thì workflow luôn kiểm tra để ưu tiên merge về rồi xoá worktree, tránh phình disk.
- Phạm vi đoán: sổ đăng ký worktree dưới `docs/tdq/` + điểm ghi sổ lúc tạo worktree + bước kiểm/merge/dọn lúc đóng task hoặc đóng request + có thể thêm lệnh kiểm trong `scripts/`.
- Chỗ chưa rõ:
  1. Sổ đăng ký là file mới (vd `docs/tdq/worktrees.md` / `.json`) hay thêm mục vào `docs/tdq/STATE.md`? Ghi bằng script như `tdq_state.py` hay ghi tay?
  2. "Luôn check" là check ở đâu: cuối mỗi task, cuối phase implement, cuối request, hay bằng hook mỗi turn?
  3. Xoá worktree tự động hay hỏi user? Nhánh git giữ hay xoá theo?
  4. Có xử lý worktree "mồ côi" tạo từ request cũ không (hiện đang có 1 cái: `tdq-ext-2026-07-30-sample-socketio-chat`)?
  5. Merge thất bại (conflict) thì làm gì — giữ worktree, báo user, hay dừng phase?
- Người dùng yêu cầu rõ: **check khả thi + report đề xuất phương án** trước khi làm.

## Hiểu & kiến thức

### Năng lực dùng được

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đang chạy phase analyze |
| tdq-spec | plugin:tdq-workflow | DÙNG | viết spec phase sau |
| tdq-plan | plugin:tdq-workflow | DÙNG | viết plan phase sau |
| tdq-build | plugin:tdq-workflow | DÙNG | implement + QC + report |
| tdq-conventions | plugin:tdq-workflow | NỀN | luật chung, §7 tên nhánh |
| tdq-status | plugin:tdq-workflow | KHÔNG | khác lĩnh vực (chỉ báo trạng thái) |
| Đã xét 280 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

### Hiện trạng đọc từ code

Máy móc worktree ĐÃ CÓ, nằm trọn ở `scripts/tdq_team.py` (7 lệnh):

- `mo <task>` — tạo nhánh `tdq/<slug>/<task>` + worktree tại `.tdq-worktrees/<slug>/<task>`
  (đổi gốc được bằng `TDQ_WORKTREE_DIR`). Thư mục gốc tự ghi `.gitignore` chứa `*`.
- `kiem <task>` — dò xung đột bằng `git merge-tree`, không chạm index/working tree.
- `hop <task>` — merge nhánh task vào nhánh tích hợp `tdq/<slug>/tich-hop`, chặn nếu `kiem` đỏ,
  bật `rerere`.
- `don` — gỡ mọi worktree của slug HIỆN TẠI bằng `git worktree remove --force` rồi `worktree prune`.
- Bản đồ phân công: `docs/tdq/team/<slug>.json` (do `phan-cong` ghi, mỗi task: giao/tự làm,
  lý do, vùng file, đợt).

### Bốn lỗ hổng — đây là phần request này lấp

| # | Lỗ hổng | Bằng chứng |
|---|---|---|
| G1 | Không có SỔ worktree trong `docs/tdq`. Bản đồ `team/<slug>.json` ghi phân công task, KHÔNG ghi đường dẫn worktree, thời điểm tạo, trạng thái merge, dung lượng | đọc `lenh_phan_cong`/`lenh_mo`: `mo` chỉ `print`, không ghi lại vào bản đồ |
| G2 | Không có gì BẮT phải dọn. `don` chỉ là một dòng chữ trong checklist `IMPLEMENT_SUBAGENT_ROW` và mục `## Self-check` của team-mode.md — không hook nào chặn, không lệnh nào kiểm | `grep -rn "don"` trong `hooks/` = 0 kết quả liên quan |
| G3 | `don` chỉ dọn worktree của slug ĐANG mở. Worktree của request cũ thành mồ côi vĩnh viễn — không lệnh nào quét được | `lenh_don` lấy `goc = .tdq-worktrees/<slug>` từ `_boi_canh(project)` |
| G4 | Nhánh tích hợp `tdq/<slug>/tich-hop` gộp xong nằm đó; merge nó về nhánh làm việc của user KHÔNG được tự động hoá, cũng không được kiểm | `team-mode.md` mục Self-check chỉ kiểm `git worktree list` sạch, không kiểm nhánh tích hợp đã về đâu |

Bằng chứng trôi thật đang có trên máy: `git worktree list` cho ra
`/Users/truongdinhquoc/Documents/tdq-ext-2026-07-30-sample-socketio-chat` (11 MB), tạo từ
2026-07-30, không nằm dưới `.tdq-worktrees/` nên `don` không đụng tới được.

### Kết luận khả thi

**KHẢ THI, độ rủi ro thấp.** Không cần thư viện mới, không cần model, không cần tải gì.
Ba trong bốn lỗ hổng lấp bằng cách mở rộng `scripts/tdq_team.py` sẵn có; lỗ hổng G2 cần
thêm một điểm chặn (hook hoặc điều kiện `done_when` máy kiểm được ở `tdq_state.py`).
Rủi ro chính là `git worktree remove --force` XOÁ THẬT: worktree còn thay đổi chưa commit
sẽ mất. Vì vậy luật xoá phải có bước kiểm sạch trước, và đó là câu hỏi cần user chốt.

### Phạm vi đã chốt

- Mặt CHỌN: độ tin cậy (không xoá nhầm), bảo trì (sổ đọc được + lệnh báo cáo), tiết kiệm disk (dung lượng + ngưỡng cảnh báo)
- Mặt LOẠI: "chỉ cần chạy được" (bỏ hết ba mặt trên); worktree nằm NGOÀI `.tdq-worktrees/` (coi là của user, workflow không đụng)
- Bối cảnh: repo cá nhân một người giữ, đã có test suite 1198 test, việc này chạm file luật/hook của chính workflow
- Mức đầu tư suy ra: vừa — vì chạm luật/hook nên cần test hồi quy và một vòng QC riêng, nhưng không có user ngoài, không có dữ liệu tiền bạc

### Quyết định đã chốt

| # | Quyết định | Nguồn |
|---|---|---|
| D1 | Sổ là `docs/tdq/worktrees.json` (máy đọc) + `docs/tdq/worktrees.md` (người đọc), sống XUYÊN request, `tdq_state.py init` không được xoá | user chọn 2A |
| D2 | Ghi sổ CHỈ qua `scripts/tdq_team.py`, không sửa tay — cùng luật với `state.json` | CLAUDE.md §6 |
| D3 | Check ở ba chỗ: (a) `hop <task>` xong gỡ luôn worktree task đó, (b) chặn `phase=qc` khi còn worktree bẩn, (c) hook nhắc mỗi turn khi sổ còn dòng chưa đóng | user chọn 3A |
| D4 | Xoá tự động chỉ khi đủ 3 điều kiện: working tree sạch · nhánh đã merge vào tích hợp · `kiem` xanh. Thiếu một điều → DỪNG, in lý do, hỏi user | user chọn 4A |
| D5 | Merge xong xoá nhánh task, GIỮ nhánh tích hợp | user chọn 5A |
| D6 | `soat` chỉ quét trong `.tdq-worktrees/`; worktree ngoài đó chỉ được LIỆT KÊ để biết, không bao giờ xoá | user chọn 6B |
| D7 | Ngưỡng cảnh báo disk: tổng `.tdq-worktrees/` > 500 MB, hoặc một worktree tuổi > 7 ngày. Hai con số này là ĐỀ XUẤT, user chốt lúc duyệt spec | Claude đề xuất |

### Cách tiếp cận & lý do

- Chọn: mở rộng `scripts/tdq_team.py` sẵn có (thêm `soat`, thêm ghi sổ vào `mo`/`hop`/`don`)
  + một điểm chặn ở `tdq_state.py` khi đổi sang phase `qc` + một dòng nhắc ở hook.
- Vì: bốn lệnh vòng đời đã đúng và đã có test; vấn đề là KHÔNG AI GHI SỔ và KHÔNG AI BẮT DỌN.
  Viết tool mới song song sẽ đẻ ra hai nguồn sự thật về worktree.
- Đã loại: script dọn chạy nền theo lịch — vì nó xoá lúc user không nhìn, đúng thứ D4 cấm.
- Đã loại: dùng `git worktree prune --expire` một mình — chỉ dọn bản ghi mồ côi trong
  `.git/worktrees/`, KHÔNG xoá thư mục còn tồn tại, nên không tiết kiệm được disk.
- Nguồn: đọc trực tiếp `scripts/tdq_team.py` (7 lệnh), `scripts/tdq_state.py`
  (`IMPLEMENT_SUBAGENT_ROW`), `skills/tdq-build/references/team-mode.md`;
  research cũ `docs/tdq/research/2026-08-17-1828-subagent-team-implement.md` dòng 28
  (dọn bằng `git worktree remove`, không `rm -rf`).

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Không có ẩn số ngoài: máy móc là git chuẩn + code nhà; luật `worktree remove` không `rm -rf` đã có ở research 2026-08-17 |
| Interview | CÓ (xong) | Vòng 1 đã chốt 6 câu, không còn câu nào đổi được kết quả |
| Chia sub-agent | BỎ | Vùng file chồng nhau nặng (`tdq_team.py` bị hầu hết task chạm), lại là file luật — `phan-cong` sẽ xếp `tu_lam` gần hết |
| QC độc lập (agent) | CÓ | Việc này xoá thư mục thật; cần người thứ hai dựng repo tạm thử đủ nhánh rẽ của D4 |
| Deep review plan | BỎ | Plan sẽ nhỏ (< 15 task), luật đã chốt bằng bảng D1–D7 |

## Hỏi đáp

**Vòng 1 (2026-08-22)** — user trả lời `1abc 2a 3a 4a 5a 6b`:

| # | Câu hỏi | Trả lời |
|---|---|---|
| 1 | Request bao quanh mặt nào? | A+B+C: độ tin cậy, bảo trì, tiết kiệm disk. LOẠI D ("chỉ cần chạy được") |
| 2 | Sổ worktree nằm ở đâu? | A: `docs/tdq/worktrees.json` + `worktrees.md`, sống xuyên request |
| 3 | "Luôn check" ở đâu? | A: ba chỗ — sau `hop`, chặn sang `qc`, hook nhắc mỗi turn |
| 4 | Xoá tự động hay hỏi? | A: tự xoá khi đủ 3 điều kiện, thiếu một điều thì dừng và hỏi |
| 5 | Nhánh git sau merge? | A: xoá nhánh task, giữ nhánh tích hợp |
| 6 | Worktree mồ côi ngoài `.tdq-worktrees/`? | B: chỉ quét trong `.tdq-worktrees/`, ngoài đó không đụng |

Không còn câu hỏi nào đổi được kết quả → đóng vòng interview.
