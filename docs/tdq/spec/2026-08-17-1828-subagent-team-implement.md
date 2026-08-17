# SPEC — Mode subagent chạy như một đội: main làm leader, nhiều agent song song, merge có kiểm

Ngày: 2026-08-17 · Bản: 1.3 · Brief: ../brief/2026-08-17-1828-subagent-team-implement.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

## 1. Mục tiêu & phạm vi

- **Mục tiêu:** đổi mode `subagent` từ "một agent một task, main chờ tuần tự" thành mô hình
  đội — main agent là leader, chia plan thành các cụm task không đụng file nhau, phát nhiều
  agent CÙNG MỘT LƯỢT, mỗi agent một worktree/nhánh riêng, leader dò xung đột rồi hợp tuần tự
  vào nhánh tích hợp. Đồng thời gỡ nguyên nhân làm phiên "ngưng" giữa plan. Đo được bằng:
  một plan có N cụm độc lập phải phát được N agent trong MỘT response (hiện tại là N lượt), và
  chạy hết plan không cần user gõ câu giục nào.
- **Mode `subagent` KHÔNG có nghĩa là mọi task đều phải giao đi** (user bổ sung 18:53).
  Leader có cả một đội trong tay và tự quyết từng task: task dính chuỗi phụ thuộc, task đụng
  file mà task khác đang giữ, task mang nhãn `(mcp)` → **leader tự làm**; mọi task tách được
  → **ưu tiên tách** để cắt thời gian. Mặc định là TÁCH; giữ lại phải nêu được lý do thuộc
  một trong ba nhóm trên. Điều này áp cho từng task, không phải chọn một lần cho cả plan.
- **Leader phân tích TOÀN BỘ plan trước khi phát đợt đầu tiên** (user bổ sung 18:56). Không
  quyết từng task theo kiểu gặp đâu xử đó: đọc hết plan → lập bản đồ sở hữu file → xếp lịch
  các đợt theo phụ thuộc → mới bắt đầu chạy. Đây là bước 0 bắt buộc của mode `subagent`.
- **Chống lách luật** (user bổ sung 18:56): user chọn `subagent` mà Claude âm thầm tự làm ở
  main là vi phạm, không phải lựa chọn tối ưu. Việc "ưu tiên chia như một leader chuyên
  nghiệp" phải được HỆ THỐNG ép, không trông vào thiện chí của model — mọi task giữ lại phải
  khai lý do bằng máy đọc được, và hook chặn khi main sửa file thuộc task lẽ ra phải giao.
- **Trong phạm vi:** luật của `tdq-plan` (khai `Chạm:` + gom cụm) · luật của `tdq-build`
  (vòng lặp đội) · trạng thái checkbox mới `[>]` và các nơi đọc nó (`tdq_state.py`,
  `hooks/scripts/edit_gate.py`, `tdq_checkstatus.py`) · script điều phối worktree/merge mới ·
  hợp đồng `agents/tdq-implementer.md` · luật một-turn ở `tdq-conventions` §1 · sinh lại hai
  bundle portable.
- **NGOÀI phạm vi:**
  - Không mặt chất lượng nào bị loại ở vòng scope (user chọn cả A+B+C+D) — không có dòng
    "mặt LOẠI" để chép sang đây.
  - Đổi mode `main`: giữ nguyên hành vi tuần tự, chỉ hưởng phần sửa luật chống ngưng.
  - Status line trong ảnh user gửi nằm NGOÀI repo này — spec không sửa nó, chỉ bảo đảm
    `[>]` không làm sai tỉ lệ `[x]/tổng` mà nó đang đếm.
  - Không đặt trần agent cứng (user chốt), nên không có tham số cấu hình trần.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | ĐÃ CHẠY | 2 truy vấn, kết quả ở `docs/tdq/research/2026-08-17-1828-subagent-team-implement.md` |
| Interview | ĐÃ CHẠY | vòng scope + vòng chi tiết, 8 câu, đã chốt hết |
| Spec → plan → implement | CÓ | khung bất biến, không được cắt |
| QC độc lập (agent `tdq-qc-tester`) | CÓ | việc này sửa hook chặn và luật chạy của mọi request sau; tự khai "chạy tốt" là đúng kiểu lỗi cần người thứ hai bắt |
| Review sâu spec/plan bằng `tdq-reviewer` | BỎ | user chưa yêu cầu; DoD đã có phép kiểm bằng lệnh cho từng hạng mục |
| Sinh lại 2 bundle portable | CÓ | user chốt câu 4 phương án A |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Script điều phối đội: chia cụm, mở worktree, dò xung đột, hợp nhánh, dọn | `scripts/tdq_team.py` | `python3 scripts/tdq_team.py --help` exit 0; 5 lệnh con chạy được trên repo thật |
| 2 | Trạng thái checkbox `[>]` (đã giao cho agent) được mọi nơi hiểu | `scripts/tdq_state.py` (`_TASK_LINE`, `plan_tick_state`) | plan có 4 `[>]` + 1 `[~]` → `plan_tick_state` trả `doing_count=1`, `dispatched_count=4` |
| 3 | Hook thôi chặn nhiều task chạy song song, vẫn chặn cẩu thả | `hooks/scripts/edit_gate.py` | nhiều `[>]` → không chặn; hai `[~]` → vẫn chặn; không dấu nào → vẫn chặn |
| 4 | Luật đội trong skill build | `skills/tdq-build/SKILL.md` + `references/team-mode.md` | vòng lặp 6 bước có mã lệnh cụ thể; `doc_lint` exit 0 |
| 5 | Plan khai được cụm song song | `skills/tdq-plan/SKILL.md` + `references/plan-template.md` | mỗi task có dòng `Chạm:`; plan có mục `## Cụm song song`; `doc_lint --pair` exit 0 |
| 6 | Hợp đồng agent con khớp mô hình mới | `agents/tdq-implementer.md` | có trường `CỤM`, `BASE`, luật cấm sửa file ngoài vùng được giao |
| 7 | Luật chống ngưng | `skills/tdq-conventions/SKILL.md` §1 | có luật "plan chưa hết task thì không kết thúc turn" kèm 3 ngoại lệ liệt kê rõ |
| 8 | Chẩn đoán `tdq_checkstatus.py` hiểu mô hình đội | `scripts/tdq_checkstatus.py` | nhiều `[>]` không còn bị báo ca D4; thêm ca cho "agent đã giao mà chưa merge" |
| 9 | Test khoá toàn bộ | `tests/test_team_mode.py` | `pytest tests/ -q` xanh, không giảm số test cũ |
| 10 | Bản đồ phân công cả plan, sinh trước đợt đầu tiên | `docs/tdq/team/<slug>.json` | mỗi task có `quyet_dinh` = `giao`/`tu_lam`, `ly_do`, `vung_file`, `dot`; số task = số task trong plan |
| 11 | Hook chặn main lách luật | `hooks/scripts/edit_gate.py`, mã `[TDQ:TEAM]` | mode `subagent` + sửa file thuộc task `giao` mà chưa có nhánh của task đó → CHẶN |
| 12 | Lệnh kiểm kê phân công | `scripts/tdq_team.py kiem-ke` | task `tu_lam` không có `ly_do` thuộc 4 nhóm hợp lệ → exit khác 0, nêu đúng task nào |
| 13 | Hai bundle portable sinh lại | `portable_claude/`, `portable_codex/` | `tdq_checkportable.py check` báo `SẠCH` cho cả hai |

## 3. Cách tiếp cận & lý do

- **Chọn:** đưa phần điều phối ra thành **lệnh chạy được** (`scripts/tdq_team.py`) thay vì
  viết thêm luật cho model tự xoay. Leader gọi lệnh để biết cụm, mở worktree, dò xung đột,
  hợp nhánh; skill chỉ còn mô tả VÒNG LẶP và điều kiện dừng.
- **Vì:** soul nguyên tắc 3 đòi model yếu nhất đọc cũng làm đúng — một câu lệnh có exit code
  làm được điều đó, một đoạn văn mô tả quy trình merge thì không. Soul nguyên tắc 2 tầng 2
  (runtime) cũng chỉ được tối ưu khi không hạ tầng 1: dò xung đột bằng `git merge-tree` và
  hợp tuần tự là cách giữ tầng 1 trong khi vẫn chạy song song. Research chốt: git KHÔNG cảnh
  báo hai worktree sửa cùng file, và "lập bản đồ sở hữu file từ đầu là bước quan trọng nhất".
- **Bốn quyết định user đã chốt** (brief `## Hỏi đáp` vòng chi tiết):
  1. Cụm do **plan khai sẵn** — mỗi task thêm dòng `Chạm:`, `tdq-plan` gom thành mục
     `## Cụm song song`; user duyệt plan là duyệt luôn cách chia.
  2. Thêm trạng thái **`[>]` = đã giao cho agent**; `[~]` giữ nguyên nghĩa "main đang tự làm".
     Hook cho nhiều `[>]`, vẫn chỉ một `[~]`.
  3. Merge về **nhánh tích hợp riêng của request**, hợp tuần tự, nhánh còn lại rebase sau mỗi
     lần merge; hết plan mới đưa một lần về nhánh user đang làm.
  4. Luật một-turn: **cho phép đóng sổ nhiều lần trong một turn**, chỉ bắt buộc `tdq_finish.py`
     là hành động cuối khi thật sự kết thúc lượt; thêm luật cứng "plan chưa hết task thì không
     được kết thúc turn".
  5. **Mode `subagent` là mô hình LAI, không phải "giao hết"** (user bổ sung 18:53). Leader
     duyệt từng task theo đúng thứ tự trong plan và xếp vào một trong hai ngăn:
     **TỰ LÀM** khi task phụ thuộc kết quả của task chưa xong · khi file nó chạm đang nằm
     trong vùng một agent đang giữ · khi task mang nhãn `(mcp)` (agent con không có MCP) ·
     khi task sửa chính file luật/hook mà leader đang dùng để điều phối.
     **GIAO ĐI** cho mọi trường hợp còn lại — đây là mặc định, không phải ngoại lệ.
     Ngăn TỰ LÀM và các đợt agent chạy XEN KẼ được: leader làm task tuần tự của mình TRONG
     LÚC đợi đợt agent trả về, miễn file không giao nhau với vùng đã giao.
  6. **Phân tích cả plan trước, rồi mới chạy** (user bổ sung 18:56). Bước 0 của mode
     `subagent`: `tdq_team.py phan-cong` đọc TOÀN BỘ plan, dựng bản đồ sở hữu file từ các
     dòng `Chạm:`, suy chuỗi phụ thuộc, rồi ghi `docs/tdq/team/<slug>.json` — mỗi task một
     bản ghi `{quyet_dinh, ly_do, vung_file, dot}`. Leader chỉ được phát agent theo bản đồ
     này. Bản đồ sinh MỘT lần trước đợt đầu, cập nhật khi có agent hỏng hoặc plan đổi.
  7. **Ép bằng máy, không bằng thiện chí** (user bổ sung 18:56). Ba lớp:
     (a) mọi task `tu_lam` phải mang `ly_do` thuộc đúng 4 nhóm hợp lệ ở quyết định 5 —
     `tdq_team.py kiem-ke` exit khác 0 nếu có task giữ lại mà không khai được lý do;
     (b) hook `edit_gate.py` thêm mã `[TDQ:TEAM]`: `implement_mode = subagent` mà main đang
     sửa file nằm trong `vung_file` của một task `giao` chưa có nhánh → **CHẶN**;
     (c) report bắt buộc in tỉ lệ `giao/tổng` cùng danh sách task giữ lại kèm lý do, để chỗ
     lách luật nếu có thì lộ ra trên giấy trắng mực đen.
- **Mặc định tôi tự chốt (user không phản đối):** trước khi merge, leader **đọc diff và chạy
  test của module đó**, không merge chỉ vì agent báo xanh.
- **Đã loại:** dùng tool `Workflow` của harness này để điều phối — vì nó không tồn tại ở
  Codex CLI và các harness khác, luật sẽ gãy ngay khi chạy bản portable.
- **Đã loại:** nới hook cho nhiều `[~]` khi `implement_mode=subagent` (phương án 2B) — vì
  `[~]` khi đó mang hai nghĩa tuỳ mode, và mọi công cụ đọc plan phải biết mode mới hiểu đúng.
- **Đã loại:** mỗi agent một PR để user tự merge (3C) — user chốt 3A, và PR thủ công đưa
  người vào giữa mọi vòng lặp, đúng thứ request này muốn bỏ.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | skill khung đang chạy phase analyze |
| tdq-spec | plugin:tdq-workflow | NỀN | skill khung viết chính file này |
| tdq-plan | plugin:tdq-workflow | DÙNG | đầu ra #5 — khai `Chạm:` và gom cụm |
| tdq-build | plugin:tdq-workflow | DÙNG | đầu ra #4 — vòng lặp đội |
| tdq-conventions | plugin:tdq-workflow | DÙNG | đầu ra #7 — luật một-turn |
| tdq-status | plugin:tdq-workflow | DÙNG | đầu ra #8 — chẩn đoán hiểu `[>]` |
| tdq-checkportable | project (portable_src) | DÙNG | đầu ra #10 — kiểm hai bundle sau khi sinh |
| tdq-qc-tester (agent) | project `agents/` | DÙNG | QC độc lập cuối request theo lộ trình §1b |
| tdq-implementer (agent) | project `agents/` | DÙNG | đầu ra #6 — chính hợp đồng bị sửa |
| Đã xét 278 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

### 4a. Viết đủ chi tiết cho MỌI model (user bổ sung 19:03)

Yêu cầu này áp cho từng chữ của mọi file luật request này sinh ra hoặc sửa
(`team-mode.md`, `tdq-build`, `tdq-plan`, `plan-template.md`, `tdq-conventions`,
`agents/tdq-implementer.md`) — không phải lời khuyên, mà là điều kiện PASS ở §6.

1. **Khuôn ba mục bắt buộc** theo soul nguyên tắc 3: mỗi luật mới có `## Khi nào áp dụng`
   (dấu hiệu nhận ra bằng mắt hoặc bằng lệnh) · `## Làm gì` (các bước ĐÁNH SỐ, mỗi bước
   đúng một hành động, viết câu mệnh lệnh) · `## Tự kiểm` (một lệnh hoặc một câu hỏi có/không).
2. **Quyết định phải tra được bằng bảng, không bằng suy luận.** Việc "task này giao hay tự
   làm" là một BẢNG TRA đủ 4 nhóm giữ lại + dòng mặc định GIAO, kèm cột "dấu hiệu nhận ra"
   và cột "lệnh kiểm". Cấm để model tự cân nhắc.
3. **Ví dụ ĐÚNG/SAI cho mọi chỗ dễ nhầm**, tối thiểu 4 cặp: task nào được giao · task nào
   phải giữ · thế nào là vùng file bị khoá · thế nào là "đã hết plan" (được kết thúc turn).
4. **Prompt giao cho agent con là KHUÔN ĐIỀN CHỖ TRỐNG**, chép nguyên trong reference, có
   sẵn đủ trường (task ID, cụm, nhánh, base, vùng file được phép sửa, đường dẫn spec+plan,
   lệnh test). Leader chỉ điền, không tự nghĩ ra cách viết prompt.
5. **Mọi lệnh viết nguyên văn, copy là chạy được** — không viết `<đường dẫn của bạn>` mà
   không kèm ví dụ có thật.
6. **Mỗi thông điệp lỗi của `tdq_team.py` nêu đúng việc phải làm tiếp theo**, không chỉ báo
   sai ở đâu. Ví dụ ĐÚNG: `LỖI T2.3 giữ lại mà không khai lý do — thêm "Giữ: <1 trong 4
   nhóm>" vào task rồi chạy lại`. Ví dụ SAI: `invalid assignment map`.
7. **Không dùng từ mơ hồ** ("phù hợp", "tối ưu", "nếu cần", "hạn chế") mà không kèm ngưỡng
   số hoặc lệnh kiểm.

- **Log service bật mặc định:** `scripts/tdq_team.py` là mã chạy được → log ra stderr kèm
  timestamp ISO, tắt bằng `TDQ_LOG=0`, giống mọi script khác trong `scripts/`.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md` và rule
  ngôn ngữ trong `skills/tdq-build/references/rules/`.
- **Không lệnh nào trong request này được ghi vào repo THẬT khi đang thử nghiệm** — mọi test
  worktree/merge chạy trên repo git tạm dựng trong `tempfile.TemporaryDirectory()`.
- Tên nhánh/worktree không bắt đầu bằng `claude`, `antigravity`, `gemini`, `codex`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`, chỉ dòng việc này chạm):

- "`hooks/` được gọi `scripts/`; `scripts/` **không** được import `hooks/`" — việc này chạm ở
  `edit_gate.py` (đọc `plan_tick_state` của `tdq_state.py`), chiều gọi giữ nguyên.
- "Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json`" — `tdq_team.py` chỉ ĐỌC state,
  mọi ghi đi qua `tdq_state.py`.
- "File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/`" — `tdq_team.py` nằm ở `scripts/`.
- "`skills/` chỉ được nhắc TÊN LỆNH của `scripts/`, cấm chép nội dung script vào skill" —
  `team-mode.md` nêu lệnh `tdq_team.py`, không chép logic merge.
- Hub `main()`, `cli()`, `log()` (bảng `## Hub`) bị chạm khi thêm script mới → khai ở dòng
  `Chạm:` của plan.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Hai agent cùng sửa một file dù đã chia cụm (plan khai `Chạm:` thiếu) | merge xung đột giữa chừng, mất công một agent | `tdq_team.py cum` từ chối xếp chung đợt khi giao nhau; leader chạy `kiem` bằng `git merge-tree` TRƯỚC khi merge |
| Nới hook `[>]` làm lọt cẩu thả thật (agent không tick gì) | plan không phản ánh việc đang làm, mất khả năng theo dõi | giữ nguyên cả 3 chặn cũ cho `[~]`; thêm chặn mới: có `[>]` mà nhánh tương ứng không tồn tại |
| Luật "không kết thúc turn khi plan chưa xong" biến thành vòng lặp vô hạn khi gặp lỗi thật | phiên treo, đốt token | 3 ngoại lệ liệt kê rõ: bị hook chặn · cần user quyết · một task fail 3 vòng fix. Có ngoại lệ nào → dừng và nói |
| Chi phí token nhân theo số agent (research: tuyến tính, có ca 24 agent treo máy) | đốt quota nhanh | leader chỉ phát tối đa bằng SỐ CỤM ĐỘC LẬP của plan, không phát thừa; agent hỏng thì dừng phát đợt mới |
| Status line ngoài repo không hiểu `[>]` | user nhìn thấy tiến độ sai | `[>]` không đổi tử số `[x]` lẫn mẫu số tổng; test khoá đúng điều đó |
| Model lách luật: user chọn `subagent` nhưng main tự làm gần hết plan | mất đúng thứ user mua, mà nhìn từ ngoài vẫn "chạy xong" | ba lớp ép ở quyết định 7: `kiem-ke` exit khác 0 · hook `[TDQ:TEAM]` chặn tại chỗ sửa · report in tỉ lệ `giao/tổng` |
| Bản đồ phân công sinh một lần rồi lạc hậu khi plan đổi giữa chừng | leader phát agent theo bản đồ cũ, đụng file | `phan-cong` ghi sha của plan; `cum`/`kiem-ke` từ chối chạy khi sha lệch, buộc sinh lại |
| Leader tách quá tay: giao cả task lẽ ra phải tuần tự | agent làm trên nền cũ, kết quả sai dù test xanh | `tdq_team.py cum` chỉ xếp vào đợt những task KHÔNG phụ thuộc task chưa xong; task bị giữ lại phải in rõ lý do thuộc nhóm nào |
| Leader vừa tự làm vừa điều phối, sửa file trùng vùng đã giao agent | xung đột tự gây ra, mất công cả hai bên | vùng file đã giao bị KHOÁ tới khi merge xong; leader chỉ được tự làm task nằm ngoài vùng khoá |
| Luật viết cho Opus hiểu nhưng Haiku đọc ra nghĩa khác | model yếu chạy sai mà không ai biết cho tới lúc merge | §4a ép khuôn ba mục + bảng tra + ví dụ ĐÚNG/SAI; Q18–Q22 kiểm bằng test, không kiểm bằng cảm nhận |
| Tách nhỏ làm rơi chất lượng: agent chỉ thấy 1 task, không thấy ý đồ spec | code chạy nhưng lệch spec, nợ kỹ thuật không khai | hợp đồng agent con bắt kèm đường dẫn spec + plan; leader đọc diff đối chiếu spec trước khi merge (đã chốt ở §3) |
| Worktree rác đọng lại `.git/worktrees/` | repo bẩn dần | `tdq_team.py don` dùng `git worktree remove` + `prune`, không `rm -rf`; DoD có hạng mục kiểm |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Test suite không đỏ | `python3 -m pytest tests/ -q` | pass, số test ≥ số hiện tại (767) |
| Q2 | `[>]` được đọc đúng | `pytest tests/test_team_mode.py -q` | plan 4 `[>]` + 1 `[~]` → `doing_count=1`, `dispatched_count=4` |
| Q3 | Hook nới đúng chỗ, chặt đúng chỗ | bơm payload vào `edit_gate.py` 3 tình huống | nhiều `[>]` KHÔNG chặn · hai `[~]` CHẶN · không dấu nào CHẶN |
| Q4 | Chia cụm từ chối cụm giao nhau | `tdq_team.py cum` trên plan mẫu có 2 task chung file | hai task đó nằm khác đợt, exit 0, in rõ lý do |
| Q5 | Dò xung đột trước merge chạy thật | dựng repo git tạm, 2 nhánh sửa cùng file, chạy `tdq_team.py kiem` | báo XUNG ĐỘT, exit khác 0, repo không bị đổi |
| Q6 | Hợp tuần tự vào nhánh tích hợp | repo git tạm, 3 nhánh rời nhau | cả 3 vào nhánh tích hợp, `git log` đủ 3 commit, nhánh user không đổi |
| Q7 | Dọn worktree sạch | `tdq_team.py don` rồi `git worktree list` | không còn worktree của request; `.git/worktrees/` không còn thư mục rác |
| Q8 | Log service | chạy 1 lệnh với và không `TDQ_LOG=0` | có timestamp ISO ở stderr; `TDQ_LOG=0` im hoàn toàn |
| Q9 | Luật chống ngưng có mặt và đủ ngoại lệ | `grep` trong `tdq-conventions/SKILL.md` | có luật + đúng 3 ngoại lệ được liệt kê |
| Q10 | Cặp spec-plan và mọi doc hợp lệ | `doc_lint.py --pair <spec> <plan>` và `doc_lint.py` từng file | exit 0 |
| Q11 | Hai bundle portable còn sạch | `build_portable.py` rồi `tdq_checkportable.py check` cho cả hai | cả hai báo `SẠCH`, khớp manifest |
| Q12 | Repo thật không bị đụng khi test | `git status --short` trước/sau khi chạy test | không xuất hiện nhánh/worktree lạ |
| Q13 | Quyết định tách/giữ đúng luật | plan mẫu có 1 task phụ thuộc, 1 task `(mcp)`, 3 task rời nhau → `tdq_team.py cum` | 3 task rời vào cùng đợt; 2 task kia bị giữ lại kèm đúng lý do nhóm |
| Q14 | Vùng file đã giao bị khoá | `tdq_team.py cum` khi đang có agent giữ vùng | task chạm vùng đó không được xếp đợt, in rõ vùng đang khoá |
| Q15 | Bản đồ phân công sinh đúng | `tdq_team.py phan-cong` trên plan mẫu 8 task | file json có đủ 8 bản ghi, mỗi bản ghi đủ 4 trường, số đợt khớp chuỗi phụ thuộc |
| Q16 | Kiểm kê bắt được task giữ lại vô cớ | `tdq_team.py kiem-ke` trên bản đồ có 1 task `tu_lam` thiếu lý do | exit khác 0, in đúng mã task đó |
| Q17 | Hook chặn main lách luật | mode `subagent`, bơm payload sửa file thuộc task `giao` chưa có nhánh | CHẶN kèm mã `[TDQ:TEAM]`; cùng file đó khi task là `tu_lam` thì KHÔNG chặn |
| Q18 | Mọi file luật mới đủ khuôn ba mục | `pytest tests/test_team_mode.py -k khuon -q` | mỗi file luật mới/sửa có đủ `## Khi nào áp dụng`, `## Làm gì`, `## Tự kiểm` |
| Q19 | Bảng tra quyết định đầy đủ | test đọc `references/team-mode.md` | bảng có đủ 4 nhóm giữ lại + dòng mặc định GIAO, mỗi dòng có cột dấu hiệu và cột lệnh kiểm |
| Q20 | Ví dụ ĐÚNG/SAI và khuôn prompt có mặt | test đọc `references/team-mode.md` | ≥ 4 cặp ĐÚNG/SAI; khuôn prompt agent có đủ 7 trường |
| Q21 | Lệnh nêu trong skill là lệnh có thật | test quét mọi `python3 scripts/*.py <lệnh con>` trong file luật | mọi lệnh con tồn tại trong CLI, exit 0 với `--help` |
| Q22 | Thông điệp lỗi nêu việc phải làm | chạy `tdq_team.py kiem-ke` trên bản đồ hỏng | stderr chứa cả mã task lẫn câu lệnh sửa |
| Q23 | QC độc lập | agent `tdq-qc-tester` chạy lại Q1–Q22 | kết luận PASS kèm output thật cho từng hạng mục |

**DoD:** Q1–Q23 đều PASS · mọi task trong plan tick `[x]` · một lần chạy thử mô hình đội trên
plan mẫu cho thấy N cụm độc lập được phát trong MỘT response và merge về nhánh tích hợp không
xung đột · một plan trộn (có task phải tuần tự) chạy được theo mô hình lai mà không xung đột ·
bản đồ phân công có mặt trước đợt đầu tiên · mọi file luật đạt khuôn ba mục và có bảng tra
quyết định · hai bundle portable đã sinh lại · report ghi rõ mọi chỗ lệch so với spec.

## 7. Câu hỏi còn mở

(rỗng)
