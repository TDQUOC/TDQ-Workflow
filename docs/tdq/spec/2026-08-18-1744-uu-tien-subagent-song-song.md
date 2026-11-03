# SPEC — Luôn tổ chức modular, ưu tiên sub-agent chạy song song

Ngày: 2026-08-18 · Bản: 1.1 · Brief: ../brief/2026-08-18-1744-uu-tien-subagent-song-song.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT

Đổi so với bản 1.0: thêm phần LỊCH TRÌNH (phụ thuộc tường minh, phát liên tục, ưu tiên
đường găng, hợp đồng dùng chung), nới trần 4 thành trần trên thay vì chỉ tiêu, và thêm
ranh giới ba tầng vào prompt giao việc. Căn cứ ở `## 3. Cách tiếp cận & lý do`.

## 1. Mục tiêu & phạm vi

- Mục tiêu: đưa tính modular thành thuộc tính bắt buộc của spec và plan ở mọi lane, và
  rút số đợt thi hành xuống đúng mức mà phụ thuộc thật đòi hỏi. Đo được: `doc_lint.py`
  từ chối plan thiếu khối cụm, và số đợt của plan mẫu giảm so với luật chia đợt hiện tại.
- Trong phạm vi:
  - Mục ranh giới module mới trong khuôn spec, bắt buộc lane full.
  - Khối `## Cụm song song` bắt buộc luôn có trong plan, kể cả khi kết luận là một cụm.
  - Trường `Cần:` khai phụ thuộc tường minh giữa các task, thay cho việc suy từ tên phase.
  - Phát liên tục: task nào sẵn sàng thì giao ngay, không chờ cả đợt trước hợp xong.
  - Ưu tiên đường găng khi chọn task giao trước cho agent rảnh.
  - Lý do giữ task thứ năm: hợp đồng dùng chung phải làm tuần tự trước.
  - Cổng đề xuất mode chạy `tdq_bench.py mo-phong --plan` với hệ số agent 1.5.
  - Gỡ khoá `team-mode.md` khỏi điều kiện `implement_mode = subagent`.
  - Lane quick được sinh agent con khi mini-plan có từ 3 task tách rời trở lên.
  - Trần trên 4 nhánh cùng lúc, không ép đủ 4 khi độ rộng đồ thị nhỏ hơn.
  - Ranh giới ba tầng và phép tự kiểm trong prompt giao việc cho agent con.
  - Vá hook `edit_gate` để agent con sửa được file ngoài project dir của state.
  - Sinh lại `portable_claude/` và `portable_codex/` cho khớp `skills/`.
- NGOÀI phạm vi:
  - Sáu mặt chất lượng ISO còn lại ngoài Đúng đắn, Bảo trì được, Hiệu năng.
  - Đo lại benchmark main so với đội. Dùng lại số của request `2026-08-17-2001`.
  - Panel nhiều giám khảo hay tranh luận nhiều vòng khi QC. Nguồn đo được cho thấy tốn
    khoảng 11 lần token mà chỉ thêm 3,3 điểm, còn đổi vai thì giảm 4,2 điểm.
  - Đồ thị task tự phình lúc chạy (thêm task giữa chừng). Giữ đồ thị tĩnh theo plan đã duyệt.
  - Đổi giao diện hay số lượng phase của workflow.
  - Đổi agent `tdq-implementer` và `tdq-qc-tester`.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ (đã xong 2 vòng) | Vòng 1 về mặt trái multi-agent, vòng 2 về lịch trình và chất lượng |
| Interview | CÓ (đã xong) | Chín câu đã chốt ở brief mục `## Hỏi đáp` |
| QC độc lập (agent) | CÓ | Luật đổi ở bốn skill cộng hai script, dễ sót chỗ đá nhau |

| # | Việc | Chạm gì |
|---|---|---|
| 1 | Mục ranh giới module trong khuôn spec | `skills/tdq-spec/references/spec-template.md` |
| 2 | Trường `Cần:` và khối cụm bắt buộc trong plan | `skills/tdq-plan/references/plan-template.md` |
| 3 | Chia đợt theo phụ thuộc khai báo, không theo tên phase | `scripts/tdq_team.py` |
| 4 | Phát liên tục và ưu tiên đường găng | `scripts/tdq_team.py` |
| 5 | Trần trên 4 nhánh cùng lúc | `scripts/tdq_team.py` |
| 6 | Cổng đề xuất mode chạy bằng lệnh | `skills/tdq-plan/SKILL.md` |
| 7 | Gỡ khoá doctrine leader, thêm lý do giữ thứ năm, ranh giới ba tầng | `skills/tdq-build/references/team-mode.md` |
| 8 | Lane quick có đường song song | `skills/tdq-intake/references/quick-lane.md` |
| 9 | Vá hook chặn nhầm agent con | `hooks/scripts/edit_gate.py` |
| 10 | Test khoá hình dạng luật mới | `tests/` |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Mục `## 2b. Ranh giới module` trong khuôn spec | `skills/tdq-spec/references/spec-template.md` | `grep -c "2b. Ranh giới module"` ra 1 |
| 2 | Luật R10 của linter: spec lane full phải có mục ranh giới module | `scripts/doc_lint.py` | Test đỏ trước, xanh sau, trong `tests/test_doc_lint.py` |
| 3 | Khối `## Cụm song song` bắt buộc trong mọi plan | `skills/tdq-plan/references/plan-template.md` | `doc_lint.py --pair` từ chối plan thiếu khối |
| 4 | Trường `Cần:` khai phụ thuộc tường minh | `plan-template.md` + `scripts/tdq_team.py` | Test: plan khai `Cần:` thì đợt xếp theo nó, không theo tên phase |
| 5 | Chia đợt bỏ luật "phase sau chạy sau phase trước" | `scripts/tdq_team.py` hàm `chia_dot` | Test: 4 plan thật trong `docs/tdq/plan/` đều ra số đợt nhỏ hơn hoặc bằng bản cũ |
| 6 | Phát liên tục theo danh sách sẵn sàng | `scripts/tdq_team.py` lệnh `cum` | Test: task đợt sau có vùng file rảnh và phụ thuộc đã xong thì được phát ngay |
| 7 | Ưu tiên đường găng khi xếp thứ tự phát | `scripts/tdq_team.py` | Test: task có b-level lớn hơn đứng trước trong danh sách in ra |
| 8 | Trần trên 4 nhánh cùng lúc | `scripts/tdq_team.py` | Test: 9 task rời nhau thì đợt đầu in đúng 4 task; 2 task rời nhau thì in 2 |
| 9 | Cổng đề xuất mode dựa trên lệnh, hệ số agent 1.5 | `skills/tdq-plan/SKILL.md` bước 1 | `grep -c "mo-phong --plan"` ra ít nhất 1 |
| 10 | Doctrine leader áp cả mode `main`, cộng lý do giữ thứ năm | `skills/tdq-build/references/team-mode.md` | `grep -c "hop-dong"` ra ít nhất 1 và bảng lý do có 5 dòng |
| 11 | Ranh giới ba tầng và phép tự kiểm trong prompt giao việc | `team-mode.md` khuôn prompt | `grep -c "Luôn được"` và `grep -c "Cấm"` đều ra ít nhất 1 |
| 12 | Đường song song cho lane quick | `skills/tdq-intake/references/quick-lane.md` | `grep -c "agent con"` ra ít nhất 1 |
| 13 | Hook không chặn sửa file ngoài project dir của state | `hooks/scripts/edit_gate.py` | Test: target ngoài project dir thì không `block` |
| 14 | Bản portable khớp bản gốc | `portable_claude/`, `portable_codex/` | `python3 scripts/build_portable.py` rồi `git status --short` sạch |
| 15 | Bộ test khoá hình dạng luật mới | `tests/test_uu_tien_song_song.py` | `python3 -m pytest tests/test_uu_tien_song_song.py -q` xanh |

## 2b. Ranh giới module

Bảy module, vùng file không giao nhau. Đây là đường cắt mà plan dùng để chia task.

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| khuôn tài liệu | `skills/tdq-spec/references/spec-template.md`, `skills/tdq-spec/SKILL.md`, `skills/tdq-plan/references/plan-template.md` | không | 1, 3, 4 |
| linter | `scripts/doc_lint.py`, `tests/test_doc_lint.py` | khuôn tài liệu | 2 |
| lịch trình | `scripts/tdq_team.py`, `tests/test_team_mode.py` | khuôn tài liệu | 4, 5, 6, 7, 8 |
| luật skill | `skills/tdq-plan/SKILL.md`, `skills/tdq-build/references/team-mode.md`, `skills/tdq-intake/references/quick-lane.md` | không | 9, 10, 11, 12 |
| hook | `hooks/scripts/edit_gate.py`, `tests/test_edit_gate.py` | không | 13 |
| bản ngoài | `portable_claude/`, `portable_codex/` | khuôn tài liệu, luật skill | 14 |
| test tổng | `tests/test_uu_tien_song_song.py` | lịch trình, luật skill | 15 |

Bốn module không phụ thuộc gì — khuôn tài liệu, luật skill, hook, và phần mở đầu của lịch
trình — nên mở được bốn nhánh song song ngay từ đầu.

## 3. Cách tiếp cận & lý do

- Chọn: tách yêu cầu thành hai vế và áp hai chế độ khác nhau. Vế modular hoá tài liệu áp
  **vô điều kiện** mọi lane. Vế chạy song song áp **mặc định có ngưỡng đo được**.
- Vì: số đo trong repo cho thấy đội chỉ hoà vốn khi từ 30% đến 60% số task tách rời được,
  và thua khi plan không tách được. Nguồn: `docs/tdq/reports/2026-08-17-2001-smoke-test-main-vs-doi.md`.
- Vì: spec modular có bằng chứng làm điểm sinh mã tăng tới 30 phần trăm. Nguồn: bài của
  Harvard trong file research vòng 2.
- Chọn: khai phụ thuộc tường minh bằng trường `Cần:`, thay luật "phase sau chạy sau phase
  trước" trong `chia_dot`.
- Vì: đo trên 4 plan thật trong repo, luật cũ đội số đợt lên nhiều lần so với mức mà xung
  đột file đòi hỏi — 5 đợt so với 2, 6 so với 1, 13 so với 10, 10 so với 3.
- Nhưng số đợt giảm KHÔNG tự động thành thời gian giảm. Chạy `mo-phong` với hằng số thực
  đo trên 3 plan cho kết quả không đều: `toi-uu-context-workflow` 9 đợt còn 3 và thời gian
  đội 27,6 phút còn 18,4 phút; `codex-native-layers` 3 đợt còn 1 mà thời gian gần như
  không đổi; `subagent-team-implement` 5 đợt còn 1 cũng gần như không đổi.
- Lý do hai ca sau không lợi: đường găng bị một task dài chi phối, gộp đợt không rút ngắn
  được task đó. Kết luận trung thực: việc này lãi tới một phần ba ở plan nhiều task ngắn,
  và hoà ở plan có task dài chi phối. Nó không bao giờ làm chậm đi, và là điều kiện cần
  để phát liên tục có chỗ mà lấp.
- Chọn: phát liên tục theo danh sách sẵn sàng, giữ điểm đồng bộ chỉ ở chỗ có vùng file
  chung hoặc hợp đồng chung.
- Vì: lệnh `cum` hiện chỉ phát đợt nhỏ nhất và in `HOÃN` cho phần còn lại. Nguồn ngoài coi
  barrier là mốc so sánh chứ không phải đích, và mỗi điểm barrier ăn mất phần tăng tốc.
- Chọn: ưu tiên đường găng khi chọn task giao trước, phần còn lại theo kết thúc sớm nhất.
- Vì: đây là luật xếp lịch chuẩn cho đồ thị 10 đến 20 nút, không cần bộ giải.
- Chọn: 4 là trần TRÊN, không phải chỉ tiêu. Độ rộng đồ thị nhỏ hơn thì phát ít hơn.
- Vì: một nguồn ủng hộ trần nhỏ cố định, ba nguồn khác nói xếp theo độ rộng thật của đồ thị.
- Chọn: thêm lý do giữ task thứ năm là `hop-dong` — hợp đồng dùng chung (kiểu dữ liệu,
  khuôn thông báo, hằng số, sổ đăng ký) do leader làm tuần tự trước khi tách.
- Vì: có ghi nhận thực tế ba agent song song vẫn xung đột trên file sổ đăng ký chung dù
  logic nằm ở file riêng.
- Chọn: prompt giao việc thêm ranh giới ba tầng (luôn được làm, phải hỏi trước, cấm) và
  một phép tự kiểm chạy được.
- Vì: hướng dẫn viết spec cho agent nêu đúng ba thành phần này là phần chống lạc việc.
- Đã loại: viết lệnh tính tỉ lệ tách được mới trong `tdq_team.py` — vì phải chép lại luật
  chia đợt ra hai chỗ, vi phạm DIP trong `clean-code.md`.
- Đã loại: bỏ hẳn cổng hỏi mode và luôn chạy đội — vì trái số đo ở ca plan không tách được,
  và trái luật conventions §4 rằng mode luôn do user chọn.
- Đã loại: panel nhiều giám khảo lúc QC — tốn khoảng 11 lần token cho 3,3 điểm.
- Đã loại: đồ thị task sửa được lúc chạy — trái luật plan đã duyệt thì không tự đổi.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | plugin:tdq-workflow | NỀN | Skill khung đang chạy phase analyze |
| tdq-spec | plugin:tdq-workflow | NỀN | Skill khung của phase spec |
| tdq-plan | plugin:tdq-workflow | DÙNG | Đầu ra 3, 4 và 9 sửa thẳng vào skill này |
| tdq-build | plugin:tdq-workflow | DÙNG | Đầu ra 10 và 11 sửa `references/team-mode.md` |
| tdq-conventions | plugin:tdq-workflow | NỀN | Luật chung nạp mỗi turn |
| mem0-memory | user | KHÔNG | khác lĩnh vực |
| Đã xét 278 skill khác | user/plugin/built-in | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt hoặc giảm được qua config.
  Áp cho `scripts/tdq_team.py`, `scripts/doc_lint.py` và `hooks/scripts/edit_gate.py` — cả
  ba đều có runtime và đều đã có hàm log sẵn, phải dùng lại chứ không tự cài lại.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo
  `skills/tdq-conventions/references/clean-code.md`, và bám rule ngôn ngữ trong
  `skills/tdq-build/references/rules/`. Luật này luôn áp, không có cổng bật hoặc tắt.
- Plan cũ không khai `Cần:` vẫn phải chạy được: thiếu trường đó thì lùi về luật cũ theo
  tên phase, không báo lỗi.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`):

- "Hook được gọi `scripts/`, `scripts/` không được gọi ngược `hooks/`" — việc này chạm ở
  `hooks/scripts/edit_gate.py` khi vá phần so sánh đường dẫn.
- "`skills/` chỉ được nêu TÊN LỆNH của `scripts/`" — việc này chạm ở `skills/tdq-plan/SKILL.md`
  khi thêm lệnh `mo-phong`.
- "File mã nguồn MỚI phải nằm trong `scripts/` hoặc `hooks/`" — việc này không tạo file mã
  nguồn mới, chỉ tạo file test.
- "`portable_claude/` và `portable_codex/` do `scripts/build_portable.py` sinh ra, cấm sửa
  tay" — việc này chạm ở đầu ra 14.
- "Chỉ `tdq_state.py` được ghi `state.json`" — việc này không ghi state.
- `scripts/tdq_bench.py` chỉ được ĐỌC luật chia đợt của `tdq_team.py`, cấm chép lại — đổi
  `chia_dot` phải giữ nguyên điểm vào mà bench đang gọi.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Bỏ luật phase làm hai task phụ thuộc thật chạy song song | Kết quả sai, phải làm lại | Trường `Cần:` bắt buộc với task đọc đầu ra của task khác; thiếu thì lùi về luật phase cũ |
| Phát liên tục làm khó theo dõi tiến độ | Leader mất dấu đang ở đâu | Giữ nguyên ba dấu tick, mỗi lần phát in rõ task nào đang bay |
| Trần trên 4 làm chậm plan 12 task rời nhau | Mất một phần lợi ích tốc độ | Phát liên tục bù lại: chỗ trống được lấp ngay khi một agent xong |
| Luật ranh giới module làm phình spec của việc nhỏ | Tốn thời gian phase spec | Chỉ bắt buộc lane full; lane quick dùng dòng `Chạm:` trong mini-plan |
| Vá `edit_gate` nới lỏng quá tay, mất tác dụng chặn | Model lách luật tick | Chỉ bỏ chặn khi target nằm NGOÀI project dir của state, giữ nguyên mọi ca trong repo |
| Bốn skill và hai script đổi cùng lúc, luật đá nhau | Model đọc luật mâu thuẫn | QC độc lập bằng agent, cộng test khoá hình dạng |
| Trần dòng skill vượt `SKILL_LINE_LIMITS` | Lint đỏ, phải nén luật | Nới trần theo soul, cấm nén luật tầng 2 cho vừa trần |
| Chia quá nhỏ, phí bàn giao vượt phần tiết kiệm | Tốn khoảng 3,5 lần token vô ích | Luật không tách: subtask không mô tả nổi trong hai câu thì gộp lại |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Lệnh/cách kiểm | Điều kiện PASS |
|---|---|---|---|
| Q1 | Khuôn spec có mục ranh giới module | `grep -c "2b. Ranh giới module" skills/tdq-spec/references/spec-template.md` | ra 1 |
| Q2 | Linter chặn spec lane full thiếu mục đó | `python3 -m pytest tests/test_doc_lint.py -q` | xanh, có test của R10 |
| Q3 | Khuôn plan bắt buộc khối cụm | `python3 -m pytest tests/test_team_mode.py -q -k khai_vung_file` | xanh |
| Q4 | Trường `Cần:` đổi được thứ tự đợt | `python3 -m pytest tests/test_team_mode.py -q -k phu_thuoc` | xanh |
| Q5 | Số đợt của 4 plan thật giảm hoặc bằng bản cũ | `python3 -m pytest tests/test_uu_tien_song_song.py -q -k so_dot` | xanh, có in số đợt trước và sau |
| Q6 | Phát liên tục, không chờ hết đợt | `python3 -m pytest tests/test_team_mode.py -q -k lien_tuc` | xanh |
| Q7 | Ưu tiên đường găng | `python3 -m pytest tests/test_team_mode.py -q -k duong_gang` | xanh |
| Q8 | Trần trên 4, không ép đủ 4 | `python3 -m pytest tests/test_team_mode.py -q -k tran` | xanh, phủ cả ca 9 task và ca 2 task |
| Q9 | Cổng mode nêu lệnh và hệ số 1.5 | `grep -c "he-so-agent 1.5" skills/tdq-plan/SKILL.md` | ra ít nhất 1 |
| Q10 | Doctrine leader không còn khoá theo mode | `grep -c "implement_mode = subagent" skills/tdq-build/references/team-mode.md` | ra 0 |
| Q11 | Bảng lý do giữ task có đúng 5 dòng | `python3 -m pytest tests/test_uu_tien_song_song.py -q -k ly_do` | xanh |
| Q12 | Prompt giao việc có ranh giới ba tầng | `python3 -m pytest tests/test_uu_tien_song_song.py -q -k ranh_gioi` | xanh |
| Q13 | Lane quick có đường sinh agent con | `grep -c "agent con" skills/tdq-intake/references/quick-lane.md` | ra ít nhất 1 |
| Q14 | Hook không chặn file ngoài project dir | `python3 -m pytest tests/test_edit_gate.py -q -k ngoai_project` | xanh |
| Q15 | Plan cũ thiếu `Cần:` vẫn chạy được | `python3 scripts/tdq_bench.py mo-phong --plan docs/tdq/plan/2026-08-17-1139-codex-native-layers.md --thuc-do docs/tdq/bench/2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json` | exit 0, in được bảng |
| Q16 | Bản portable khớp bản gốc | `python3 scripts/build_portable.py && git status --short portable_claude portable_codex` | không in dòng nào |
| Q17 | Lint mọi file tài liệu đã sửa | `python3 scripts/doc_lint.py <danh sách file đã sửa>` | exit 0 |
| Q18 | Toàn bộ suite | `python3 -m pytest -q` | 0 đỏ, số test tăng so với 704 |
| Q19 | Kiểm độc lập | agent `tdq-qc-tester` chạy lại Q1 đến Q18 | không defect mức chặn |

DoD: đủ mười lăm đầu ra ở §2 · Q1 đến Q19 PASS có bằng chứng · suite xanh · `doc_lint`
exit 0 trên mọi file tài liệu đã sửa · bản portable khớp bản gốc · số đợt của 4 plan thật
trong `docs/tdq/plan/` giảm hoặc bằng bản cũ, có bảng số trong file qc.

## 7. Câu hỏi còn mở

(rỗng)
