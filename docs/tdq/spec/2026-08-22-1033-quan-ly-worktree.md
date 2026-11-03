# SPEC — Quản lý vòng đời worktree của workflow

Ngày: 2026-08-22 · Bản: 1.1 · Brief: ../brief/2026-08-22-1033-quan-ly-worktree.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## Mục lục

- 1. Mục tiêu & phạm vi
- 1b. Lộ trình
- 2. Đầu ra cụ thể
- 2b. Ranh giới module
- 3. Cách tiếp cận & lý do
- 3b. Năng lực & công cụ
- 4. Yêu cầu bắt buộc
- 5. Ràng buộc & rủi ro
- 6. QC & Definition of Done
- 7. Câu hỏi còn mở

## 1. Mục tiêu & phạm vi

- Mục tiêu: mọi worktree do workflow sinh ra dưới `.tdq-worktrees/` đều có một dòng trong sổ
  `docs/tdq/worktrees.json`, và workflow không được rời phase `implement` khi sổ còn dòng chưa
  đóng. Đo bằng: chạy hết một request mode `subagent` xong thì `git worktree list` chỉ còn
  worktree gốc, và sổ có 0 dòng trạng thái `mo`.
- Trong phạm vi:
  - Sổ worktree hai bản: JSON cho máy, Markdown cho người, sống xuyên request.
  - Ghi sổ tự động tại `mo` (mở dòng) và `hop` (đánh dấu đã merge).
  - Lệnh `soat`: liệt kê worktree dưới `.tdq-worktrees/` kèm tuổi, dung lượng, sạch/bẩn,
    đã-merge/chưa; và dọn theo luật ba điều kiện.
  - Gỡ worktree ngay sau `hop` khi đủ ba điều kiện; xoá luôn nhánh task.
  - Chặn `set phase=qc` khi sổ còn dòng `mo`.
  - Một dòng nhắc ở hook `prompt_context.py` khi sổ còn dòng chưa đóng.
  - Cảnh báo ngưỡng disk: tổng `.tdq-worktrees/` > 500 MB, hoặc một worktree tuổi > 7 ngày.
  - **Khối gợi ý xử lý**: worktree CHƯA đủ điều kiện dọn thì không im lặng bỏ qua — máy in ra
    lý do chặn kèm các phương án xử lý ứng với đúng lý do đó, và workflow bắt buộc đặt khối
    này ở CUỐI TURN cho user chọn, để worktree được dọn sớm nhất có thể.
- NGOÀI phạm vi:
  - Mặt "chỉ cần chạy được" — user đã loại; không làm bản rút gọn bỏ ba mặt tin cậy/bảo trì/disk.
  - Worktree nằm NGOÀI `.tdq-worktrees/` (ví dụ
    `/Users/truongdinhquoc/Documents/tdq-ext-2026-07-30-sample-socketio-chat`, 11 MB):
    chỉ được LIỆT KÊ trong mục "ngoài tầm" của `soat`, không bao giờ bị xoá, không vào sổ.
  - Merge nhánh tích hợp `tdq/<slug>/tich-hop` về nhánh làm việc của user — vẫn do user tự làm.
  - Dọn theo lịch chạy nền.

## 1b. Lộ trình

Chép từ brief mục `### Lộ trình`. User duyệt spec là duyệt luôn lộ trình này.

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | BỎ | Không có ẩn số ngoài: máy móc là git chuẩn + code nhà; luật `worktree remove` không `rm -rf` đã có ở research 2026-08-17 |
| Interview | CÓ (xong) | Vòng 1 chốt 6 câu, không còn câu nào đổi được kết quả |
| Chia sub-agent | BỎ | Vùng file chồng nhau nặng và là file luật — `phan-cong` sẽ xếp `tu_lam` gần hết |
| QC độc lập (agent) | CÓ | Việc này xoá thư mục thật; cần người thứ hai dựng repo tạm thử đủ nhánh rẽ của luật ba điều kiện |
| Deep review plan | BỎ | Plan nhỏ (< 15 task), luật đã chốt bằng bảng D1–D7 ở brief |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Module sổ worktree: đọc/ghi/khoá schema | `scripts/tdq_worktree_registry.py` | mở một dòng rồi đọc lại ra đúng 7 trường, file hỏng thì báo lỗi chứ không ghi đè |
| 2 | Bản người đọc của sổ, sinh từ JSON | `docs/tdq/worktrees.md` | sinh lại hai lần cho ra file y hệt nhau |
| 3 | `mo`/`hop` ghi sổ; `hop` gỡ worktree + xoá nhánh task khi đủ ba điều kiện | `scripts/tdq_team.py` | sau `hop`, thư mục worktree không còn, nhánh task không còn, dòng sổ chuyển `dong` |
| 4 | Lệnh `soat` (liệt kê + dọn) | `scripts/tdq_team.py` | in đủ 5 cột cho mỗi worktree; worktree bẩn thì thoát khác 0 và KHÔNG xoá |
| 5 | Chặn `set phase=qc` khi sổ còn dòng `mo` | `scripts/tdq_state.py` | lệnh thoát khác 0, in slug + số dòng còn mở + lệnh gỡ |
| 6 | Dòng nhắc `[TDQ:WORKTREE]` mỗi turn khi sổ còn dòng mở | `hooks/scripts/prompt_context.py` | hook in đúng một dòng khi sổ mở, không in gì khi sổ sạch |
| 8 | Khối gợi ý xử lý cho worktree chưa dọn được, in ở cuối turn | `scripts/tdq_worktree_registry.py` (bảng lý do → phương án), `scripts/tdq_team.py` (in), `skills/tdq-build/references/team-mode.md` (luật đặt cuối turn) | mỗi lý do chặn cho ra ≥ 1 phương án có lệnh chạy được; lý do lạ không bao giờ ra khối rỗng |
| 7 | Luật viết vào skill + bản portable dựng lại | `skills/tdq-build/references/team-mode.md`, `portable_claude/`, `portable_codex/` | `tdq_checkportable.py check` CLEAN cả hai cây |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| M1-so | `scripts/tdq_worktree_registry.py` + file test riêng của module này | không | 1, 2, 8 |
| M2-vong-doi | `scripts/tdq_team.py` + file test của team mode | M1-so | 3, 4 |
| M3-chan | `scripts/tdq_state.py` + file test của state | M1-so | 5 |
| M4-hook | `hooks/scripts/prompt_context.py` + file test của hook ngữ cảnh | M1-so | 6 |
| M5-luat | `skills/tdq-build/references/team-mode.md`, `scripts/build_portable.py` | M2-vong-doi, M3-chan, M4-hook | 7, 8 |

## 3. Cách tiếp cận & lý do

- Chọn: tách một module dữ liệu thuần `tdq_worktree_registry.py` (không gọi git), rồi
  `tdq_team.py`, `tdq_state.py`, hook đều đọc qua nó.
- Vì: ba nơi cùng cần đọc sổ; nếu mỗi nơi tự parse JSON thì schema lệch nhau và không phép
  kiểm nào bắt được. Tách ra cũng giữ đúng luật gọi: hook chỉ đọc `scripts/`, không ngược lại.
- Đã loại: nhét sổ vào `docs/tdq/state.json` — vì `init` xoá sạch state mỗi request, sổ phải
  sống xuyên request mới quản được worktree của request trước.
- Đã loại: nhét sổ vào `docs/tdq/team/<slug>.json` — cùng lý do, bản đồ chết theo slug.
- Đã loại: `git worktree prune --expire` một mình — chỉ dọn bản ghi mồ côi trong
  `.git/worktrees/`, không xoá thư mục còn tồn tại nên không tiết kiệm disk.
- Nguồn: `docs/tdq/research/2026-08-17-1828-subagent-team-implement.md` dòng 28 (dọn bằng
  `git worktree remove`, không `rm -rf`); đọc trực tiếp `scripts/tdq_team.py` 7 lệnh.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-conventions | plugin:tdq-workflow | NỀN | skill khung, luật §7 tên nhánh |
| tdq-spec | plugin:tdq-workflow | NỀN | skill đang chạy |
| tdq-plan | plugin:tdq-workflow | DÙNG | phase plan kế tiếp |
| tdq-build | plugin:tdq-workflow | DÙNG | implement + QC + report |
| Đã xét 281 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config. Việc này CÓ
  runtime → dùng đúng `_log()` sẵn có của `tdq_team.py` (tắt bằng `TDQ_LOG=0`), mọi lần mở/đóng
  /xoá một dòng sổ đều ghi một dòng log có timestamp.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo
  `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong
  `skills/tdq-build/references/rules/`. Luật này luôn áp, không có cổng bật/tắt.
- Ngôn ngữ: code, chú thích, docstring và chuỗi máy in ra viết TIẾNG ANH; tài liệu sinh cho
  user (`docs/tdq/worktrees.md`) viết theo `doc_lang` của request.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md` — chỉ những dòng việc này chạm tới):

- "`hooks/` được gọi `scripts/`; `scripts/` **không** được import `hooks/`" — việc này chạm ở
  `hooks/scripts/prompt_context.py` đọc `scripts/tdq_worktree_registry.py`, đúng chiều cho phép.
- "`skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill" —
  việc này chạm ở `skills/tdq-build/references/team-mode.md`, chỉ nhắc tên `soat`.
- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`" — việc này chạm ở
  `scripts/tdq_state.py`; sổ worktree là file RIÊNG, không đụng `state.json`.
- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — file mới duy nhất là
  `scripts/tdq_worktree_registry.py`.
- Hub `main()` (bậc 20): `tdq_team.py main()` và `tdq_state.py main()` đều bị chạm → DoD có
  dòng kiểm hồi quy riêng cho hai node này.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Worktree chưa dọn được bị bỏ quên vì user không thấy | Đúng thứ request này sinh ra để chặn: worktree nằm lại ăn disk | Tập LÝ DO CHẶN là tập ĐÓNG; mỗi lý do bắt buộc có ≥ 1 phương án kèm lệnh; lý do không nằm trong tập thì máy báo lỗi thay vì in khối rỗng |
| `git worktree remove --force` xoá worktree còn thay đổi chưa commit | Mất việc đã làm, không hoàn lại được | Luật ba điều kiện: `git status --porcelain` rỗng · nhánh nằm trong `git branch --merged <tich-hop>` · `kiem` xanh. Thiếu một điều → dừng, in lý do, không xoá |
| Sổ lệch thực tế (worktree bị xoá tay, sổ vẫn ghi `mo`) | Chặn `phase=qc` sai, user kẹt | `soat` đối chiếu sổ với `git worktree list` thật, dòng trỏ vào thư mục không tồn tại thì tự đóng với lý do `bien-mat` |
| Chặn `phase=qc` làm kẹt request mode `main` (không hề tạo worktree) | Workflow đứng vô cớ | Chỉ chặn khi sổ THẬT SỰ còn dòng `mo`; sổ trống hoặc chưa có file thì không chặn |
| Sổ hỏng JSON | Mọi lệnh gọi sổ chết theo, kể cả hook | Đọc hỏng → trả sổ rỗng + in cảnh báo, KHÔNG ghi đè file hỏng; hook nuốt lỗi, không bao giờ giết turn |
| Xoá nhánh task sớm làm mất lịch sử | Không tra lại được ai làm gì | Chỉ xoá nhánh SAU khi `git branch --merged` xác nhận nó đã nằm trong nhánh tích hợp; nhánh tích hợp luôn giữ |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Sổ mở/đóng đúng | Mở một dòng rồi đọc lại ra đủ 7 trường; đóng rồi đọc lại thấy trạng thái `dong` và mốc thời gian đóng |
| Q2 | Sổ hỏng không phá gì | File JSON hỏng → mọi lệnh vẫn chạy, in cảnh báo, file hỏng còn nguyên trên đĩa |
| Q3 | Bản `.md` sinh ổn định | Sinh hai lần từ cùng JSON cho ra hai file giống hệt nhau từng byte |
| Q4 | `mo` ghi sổ | Sau `mo T1.1`, sổ có đúng một dòng mới trạng thái `mo`, đường dẫn khớp thư mục thật |
| Q5 | `hop` dọn khi sạch | Repo tạm sạch → sau `hop T1.1`: thư mục worktree biến mất, nhánh task biến mất, nhánh tích hợp còn, dòng sổ `dong` |
| Q6 | `hop` KHÔNG dọn khi bẩn | Worktree còn file chưa commit → `hop` giữ nguyên worktree, in lý do, dòng sổ vẫn `mo` |
| Q7 | `hop` KHÔNG dọn khi chưa merge | Nhánh không nằm trong `--merged` → không xoá nhánh, không xoá worktree |
| Q8 | `soat` liệt kê đủ | In cho mỗi worktree: đường dẫn, tuổi theo ngày, dung lượng, sạch/bẩn, đã-merge/chưa |
| Q9 | `soat` không đụng ngoài tầm | Worktree ngoài `.tdq-worktrees/` chỉ xuất hiện ở mục "ngoài tầm", không bị xoá dù chạy dọn |
| Q10 | Ngưỡng disk | Tổng > 500 MB hoặc tuổi > 7 ngày → in cảnh báo có kèm con số thật |
| Q11 | Chặn `phase=qc` | Sổ còn dòng `mo` → `set phase=qc` thoát khác 0, in số dòng còn mở và lệnh gỡ |
| Q12 | Không chặn oan | Sổ trống hoặc chưa có file → `set phase=qc` chạy bình thường |
| Q13 | Hook nhắc | Sổ còn dòng mở → hook in đúng một dòng `[TDQ:WORKTREE]`; sổ sạch → hook không in gì thêm |
| Q14 | Hook không giết turn | Sổ hỏng hoặc thiếu → hook thoát 0, không stack trace |
| Q15 | Hồi quy hub | `main()` của `tdq_team.py` và `tdq_state.py` giữ nguyên tập sub-command cũ, không mất lệnh nào |
| Q16 | Toàn bộ test suite | Số test đỏ không nhiều hơn mốc nền 37, và đều thuộc đúng module định tuyến skill như mốc nền |
| Q19 | Khối gợi ý đủ và đúng | Mỗi lý do chặn trong tập đóng cho ra ≥ 1 phương án, mỗi phương án có một lệnh chạy được; lý do ngoài tập → máy báo lỗi, không in khối rỗng |
| Q20 | Khối gợi ý xuất hiện đúng lúc | Còn worktree chưa dọn được → khối in ra ở cuối kết quả lệnh và skill bắt buộc chép nó xuống cuối turn; dọn sạch hết → không in khối nào |
| Q17 | Luật + bản portable | Skill có mục nói về sổ và lệnh `soat`; hai cây portable CLEAN theo manifest |
| Q18 | Lint tài liệu | Mọi file `.md` sinh ra trong request này không vi phạm rule nào |

DoD:
- Q1–Q3 xanh: module sổ đọc/ghi/sinh `.md` đúng và không tự huỷ khi file hỏng.
- Q4–Q7 xanh: `mo` ghi sổ, `hop` dọn đúng luật ba điều kiện, không dọn khi thiếu điều kiện.
- Q8–Q10 xanh: `soat` liệt kê đủ 5 cột, tôn trọng vùng ngoài tầm, cảnh báo ngưỡng có số thật.
- Q11–Q12 xanh: chặn `phase=qc` đúng lúc và không chặn oan.
- Q13–Q14 xanh: hook nhắc đúng và không bao giờ giết turn.
- Q15 xanh: hai node hub `main()` không mất sub-command nào.
- Q16 xanh: test suite không tệ hơn mốc nền 37 đỏ, không đỏ thêm module nào khác.
- Q19–Q20 xanh: worktree chưa dọn được luôn kèm phương án xử lý, và khối đó nằm ở cuối turn.
- Q17 xanh: luật đã viết vào skill và hai cây portable dựng lại CLEAN.
- Q18 xanh: lint tài liệu 0 vi phạm.

## 7. Câu hỏi còn mở

(rỗng)
