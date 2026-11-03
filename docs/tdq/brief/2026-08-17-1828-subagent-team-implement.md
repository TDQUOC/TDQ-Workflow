# BRIEF — Subagent implement chạy như một team, main agent làm leader

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> ở chế độ subagent hiện tại nó vẫn bị ngưng như này, và việc tổ chức subagent implement
> cảm giác còn lâu hơn main agent, tôi muốn mở request phân tích và tổ chức để subagent
> implement thì claude như là một team và main agent là leader sẽ cố gắng chia task và tách
> nhánh để subagent implement từng module và main agent sẽ check vầ merger lại vô main và
> cứ vậy cố gắng spawn nhiều sub agent để tăng tốc độ xử lí plan nếu có một vài task cần
> main xử lí thì mmain được tồan quyền tự xử lí hoặc chia cho "team" của claude, yêu cầu
> tối ưu tốc độ implement plan và đảm bảo chất lượng project và vẫn tuân thủ soul của
> workflow. mở request lane full cho yêu cầu này

Kèm ảnh chụp màn hình một phiên đang chạy (project R&DDashboard): status line
`Doing P1.6 (7/44 task) eta ≤2h43m`, dòng cuối user phải gõ tay
"bạn toàn quyền implement plan cho đến khi hết plan" — tức phiên đã DỪNG giữa chừng và
phải giục bằng tay.

### Cách hiểu đầu tiên của tôi

**Mục tiêu:** đổi mode `subagent` từ mô hình "một agent một task, main chờ tuần tự" sang
mô hình đội: main agent = leader, chia plan thành các cụm task độc lập theo module, spawn
NHIỀU agent song song, mỗi agent một nhánh/worktree, main review + merge rồi phát đợt kế
tiếp. Mục tiêu kép: nhanh hơn mode `main` VÀ không tụt chất lượng.

**Phạm vi đoán:**
- Sửa `skills/tdq-build/SKILL.md` (Phần A, mode `subagent`), có thể tách reference riêng.
- Sửa `skills/tdq-plan/SKILL.md` + plan-template: plan phải khai được cụm task song song
  được (nhóm theo module, khai file bị chạm để phát hiện đụng độ).
- Có thể sửa `agents/tdq-implementer.md` (hợp đồng đầu ra, luật worktree).
- Có thể đụng hook tick (`[TDQ:TICK]` chỉ cho MỘT `[~]` tại một thời điểm — luật này mâu
  thuẫn trực tiếp với nhiều agent chạy song song).
- Có thể cần script mới để main quản đợt (spawn/merge/check).

**Chỗ chưa rõ:** hai triệu chứng user nêu ("vẫn bị ngưng" và "còn lâu hơn main") có thể có
nguyên nhân khác nhau; cần tìm nguyên nhân thật trước khi thiết kế, không chữa theo cảm giác.

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Nguồn | Phán quyết | Vì sao |
|---|---|---|---|
| `tdq-build` | plugin:tdq-workflow | DÙNG | Phần A mode `subagent` chính là chỗ phải sửa |
| `tdq-plan` | plugin:tdq-workflow | DÙNG | plan phải khai được cụm song song + file bị chạm |
| `tdq-conventions` | plugin:tdq-workflow | DÙNG | §1 giao thức một turn là nghi phạm chính của "ngưng" |
| `tdq-intake` / `tdq-spec` | plugin:tdq-workflow | DÙNG | phase hiện tại và phase kế tiếp |
| `tdq-status` | plugin:tdq-workflow | DÙNG | status line phải đọc được nhiều task chạy song song |
| agent `tdq-implementer` | repo `agents/` | DÙNG | hợp đồng giao việc cho agent con |
| agent `tdq-qc-tester` | repo `agents/` | DÙNG | QC độc lập cuối request |
| Tool `Agent` (built-in) | context | DÙNG | phương tiện spawn thật; nhiều lệnh trong 1 response = chạy đồng thời |
| Tool `Workflow` (built-in) | context | KHÔNG | chỉ có ở harness này, bản portable không có → luật sẽ gãy ở máy khác |
| `tavily-primary` | MCP | ĐÃ DÙNG | research, xem `docs/tdq/research/<slug>.md` |
| `graphify` | CLI | DÙNG | `affected` để suy ra file một task sẽ chạm |

### Đọc code — trạng thái hiện tại

- `skills/tdq-build/SKILL.md` Phần A mode `subagent`: **"mỗi lần gọi agent giao ĐÚNG 1 task
  (không giao cả phase/nhóm task)"**, main nhận báo cáo → tick `[x]` → mới gọi agent kế tiếp.
  Lý do ghi trong skill: nền tảng không báo cáo giữa chừng nên đơn vị giao việc phải nhỏ
  bằng nhịp tick. **Hệ quả: mode `subagent` hiện tại chạy TUẦN TỰ, cộng thêm chi phí dựng
  worktree và chi phí nạp lại ngữ cảnh cho mỗi agent → chậm hơn mode `main` đúng như user
  cảm nhận.** Đây là nguyên nhân gốc của triệu chứng 2, không phải cảm giác.
- `skills/tdq-plan/references/mode-gate.md` mô tả option B cho user là "chia việc cho **nhiều
  trợ lý chạy song song**" — MÂU THUẪN với luật một-task-một-agent ở `tdq-build`. Luật hiện
  hành không thực hiện được điều đã hứa với user.
- `hooks/scripts/edit_gate.py:118` **CHẶN CỨNG** khi plan có >1 task mang `[~]`
  ("đóng task cũ trước khi mở task mới"). Chạy 4 agent song song đòi 4 task `[~]` cùng lúc →
  luật này chặn thẳng mô hình đội. Đây là xung đột kiến trúc bắt buộc phải giải, không né được.
- `hooks/scripts/edit_gate.py:128-141` còn chặn khi "sửa N lần liên tiếp mà plan chưa tick" —
  cùng họ vấn đề: mọi hàng rào tick đều giả định MỘT dòng thi công.
- `skills/tdq-conventions/SKILL.md` §1.4: turn có đổi repo thì `tdq_finish.py` phải là **hành
  động cuối**, "sau khi in đoạn chat đó không gọi thêm tool nào nữa". §1.5 bắt in lại nguyên
  văn khối user-facing. **Đây là nghi phạm chính của triệu chứng "ngưng"**: luật đóng sổ mỗi
  turn kéo model về trạng thái kết thúc turn, plan 44 task vì thế đứt thành hàng chục lượt và
  user phải gõ tay "toàn quyền implement tiếp".
- `agents/tdq-implementer.md`: hợp đồng đã có `BRANCH` + `MERGE-READY` + digest ≤ 1.500 ký tự
  — phần khung cho mô hình đội đã có sẵn, thiếu là tầng ĐIỀU PHỐI ở main agent.
- Chưa có script nào lo worktree: không có chỗ tạo/dọn worktree, không có dò xung đột trước
  merge, không có hàng đợi merge. Toàn bộ việc đó hiện là "model tự xoay".

### Hai triệu chứng, hai nguyên nhân khác nhau

1. **"Vẫn bị ngưng"** — do giao thức một turn (§1.4/§1.5) + hàng rào tick, KHÔNG do mode.
   Ảnh user gửi là phiên mode `main` (7/44 task) mà vẫn ngưng → sửa riêng mode `subagent`
   sẽ KHÔNG chữa được triệu chứng này.
2. **"Subagent còn lâu hơn main"** — do luật một-task-một-agent làm mode `subagent` thành
   tuần tự có thêm phụ phí.

Hai cái phải chữa bằng hai nhóm thay đổi khác nhau. Gộp làm một là chữa nhầm.

### Phạm vi đã chốt

- Mặt CHỌN: tốc độ thi hành plan · độ tin cậy khi hợp nhánh · chạy liền mạch không ngưng ·
  quan sát được tiến độ
- Mặt LOẠI: không mặt nào bị loại (user chọn A+B+C+D, bỏ option "chỉ cần chạy được")
- Bối cảnh: plan điển hình 40+ task nhiều module · KHÔNG đặt trần agent cứng, leader tự
  quyết theo số cụm độc lập · áp cho chính repo bộ workflow này rồi sinh lại hai bundle
- Mức đầu tư suy ra: **đầy đủ** — vì đây là hạ tầng dùng cho mọi request về sau, plan 40+
  task, và sai một luật ở đây thì mọi project dùng bộ workflow đều lãnh hậu quả

### Nguồn ngoài

Xem `docs/tdq/research/2026-08-17-1828-subagent-team-implement.md`. Ba điều chốt được:
không có trần song song do nền tảng đặt (phải tự đặt, chi phí token tuyến tính theo số agent) ·
phân vùng file trước khi giao việc là bước quan trọng nhất · merge phải hợp tuần tự + dò
trước bằng `git merge-tree`, không merge mù.

## Hỏi đáp

### Vòng scope (18:32)

- Q1 request bao quanh mặt nào → **A+B+C+D**: tốc độ · độ tin cậy khi merge · chạy liền
  mạch · quan sát tiến độ. Không bỏ mặt nào.
- Q2 cỡ plan điển hình → **C**: 40+ task, nhiều module.
- Q3 trần agent song song → **C**: không đặt trần cứng, leader tự quyết theo số cụm độc lập.
- Q4 sản phẩm cuối → **A**: repo TDQ này rồi sinh lại hai bundle portable. User nói thêm:
  "áp dụng cho bộ workflow này".

Hệ quả của Q3 phải ghi rõ: research cho thấy nền tảng KHÔNG có trần, đã có ca 24 agent làm
treo máy. "Không trần cứng" vì vậy được hiểu là **leader tự quyết số agent theo số cụm độc
lập của plan**, kèm hàng rào an toàn bắt buộc (dừng phát đợt mới khi có agent hỏng, không
phát đợt vượt số cụm không đụng file nhau) — không phải "spawn thoải mái không giới hạn".

### Vòng chi tiết (18:40)

- Q5 ai chia cụm → **A**: plan khai sẵn, mỗi task có dòng `Chạm:`, `tdq-plan` gom thành cụm.
- Q6 đánh dấu khi nhiều agent chạy → **A**: thêm trạng thái `[>]` = đã giao cho agent;
  `[~]` giữ nghĩa "main đang tự làm"; hook cho nhiều `[>]`, vẫn chỉ một `[~]`.
- Q7 merge về đâu → **A**: nhánh tích hợp riêng của request, hợp tuần tự, nhánh còn lại
  rebase sau mỗi lần merge; hết plan mới đưa một lần về nhánh user đang làm.
- Q8 luật chống ngưng → **A**: cho đóng sổ nhiều lần trong một turn, chỉ bắt buộc là hành
  động cuối khi thật sự kết thúc lượt; thêm luật cứng "plan chưa hết task thì không kết
  thúc turn".
- Mặc định tôi tự chốt, user không phản đối: trước khi merge, leader đọc diff và chạy test
  của module đó, không merge chỉ vì agent báo xanh.

### Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | ĐÃ CHẠY | 2 truy vấn, file research đã ghi |
| Interview | ĐÃ CHẠY | vòng scope + vòng chi tiết, 8 câu, hết câu hỏi |
| Spec → plan → implement | CÓ | khung bất biến |
| QC độc lập bằng agent | CÓ | việc này sửa hook chặn và luật chạy của MỌI request sau |
| Review sâu spec/plan | BỎ | user chưa yêu cầu; DoD đã có lệnh kiểm cho từng hạng mục |
| Sinh lại 2 bundle portable | CÓ | user chốt câu 4 phương án A |

### Kiểm cổng

- Phạm vi cuối: 10 đầu ra ở spec §2, gồm 1 script mới, 1 trạng thái checkbox mới, 4 file
  luật, 1 hợp đồng agent, 1 file test, 2 bundle sinh lại.
- Model / download / cài đặt: KHÔNG cần gì thêm — chỉ `git` và Python stdlib đã có.
- Phạm vi QC: 13 hạng mục ở spec §6, mỗi hạng mục một lệnh.
