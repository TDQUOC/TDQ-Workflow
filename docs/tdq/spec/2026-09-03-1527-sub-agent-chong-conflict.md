# SPEC — Chống conflict và chống việc dội ngược cho leader ở mode sub-agent

Ngày: 2026-09-03 · Bản: 1.1 · Brief: ../brief/2026-09-03-1527-sub-agent-chong-conflict.md · Lane: full
Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md
Trạng thái: CHỜ DUYỆT LẠI (bản 1.1 — user bổ sung phạm vi đổi tên lệnh sang tiếng Anh)

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

- **Mục tiêu:** ở mode `subagent`, bịt năm lỗ hở khiến agent con đụng nhau hoặc đẩy việc sửa
  ngược lên leader. Đo được bằng ba số: (a) không một file nào ngoài `Chạm:` được agent con ghi;
  (b) không một nhánh nào merge vào nhánh tích hợp khi test của chính task còn đỏ; (c) conflict
  do base cũ được máy tự gỡ, không cần leader gõ tay.

- **Trong phạm vi:**
  - H1 — kiểm vùng file THẬT lúc agent con ghi, thay vì tin vào lời khai `Chạm:`.
  - H2 — rebase nhánh task lên nhánh tích hợp mới nhất trước khi merge.
  - H3 — phát hiện file nóng lúc phân công và bắt kế hoạch nâng nó lên đợt sớm.
  - H4 — có đường gỡ conflict, không chỉ chặn.
  - H5 — kiểm chứng độc lập kết quả agent con trước khi cho merge.
  - Sửa tài liệu luật (`team-mode.md`, `plan-template.md`, `agents/tdq-implementer.md`) khớp code.
  - **(bản 1.1)** Đổi tên lệnh CLI viết tắt tiếng Việt (`hop`, `kiem`, `mo-phong`, …) sang tiếng
    Anh cho dễ đọc, ở cả 5 script có sub-command; tên cũ giữ làm bí danh để không gãy cái đang chạy.

- **NGOÀI phạm vi:**
  - **Không thực thi.** Request này dừng sau pha `plan` theo yêu cầu của user. Build ở request sau.
  - Mode `main` — không đổi gì. Leader làm tuần tự thì năm lỗ hở này không tồn tại.
  - Trần 4 nhánh song song — giữ nguyên, đã có lý do đo được ghi tại `tdq_team.py` dòng 64.
  - Đổi sang mô hình PR / CI ngoài máy — xem §3 mục đã loại.
  - Xoay khoá Tavily lộ trong lịch sử git — việc khác, user đã nhận tự xử lý.

## 1b. Lộ trình

| Bước/phase | Chạy? | Vì sao |
|---|---|---|
| Research web | CÓ | đã chạy ở analyze, 5 nguồn N1–N5, xác nhận cả 5 lỗ hở là chỗ hỏng kinh điển |
| Interview | CÓ | đã chạy 1 vòng phạm vi; câu trả lời 2 làm lộ ra H5 |
| Phase `spec` | CÓ | đang chạy |
| Phase `plan` | CÓ | user chọn 3A: cần plan đầy đủ để duyệt |
| Phase `implement` | BỎ | user nói rõ "chưa thực thi ở mode này" |
| Phase `qc` / `report` | BỎ | không có code nào được viết thì không có gì để kiểm |
| QC độc lập (agent) | BỎ | cùng lý do |

## 2. Đầu ra cụ thể

| # | Đầu ra | Đường dẫn/vị trí | Đo "xong" bằng |
|---|---|---|---|
| 1 | Cổng chặn ghi ngoài vùng file, áp cho agent con trong worktree | `hooks/scripts/edit_gate.py` | ghi thử một file ngoài `Chạm:` từ trong worktree của task → bị chặn, nêu tên task và vùng cho phép |
| 2 | Hàm quyết định "ghi này có ngoài vùng không" | `scripts/tdq_team.py` | gọi trực tiếp với 1 ca trong vùng và 1 ca ngoài vùng → trả đúng 2 kết quả khác nhau |
| 3 | `kiem` chạy thật lệnh `Test:` của task trong worktree | `scripts/tdq_team.py` | task có test đỏ → `kiem` thoát khác 0 và in tên lệnh đã chạy |
| 4 | `hop` từ chối merge khi đầu ra 3 chưa xanh | `scripts/tdq_team.py` | nhánh có test đỏ → `hop` thoát khác 0, nhánh tích hợp không nhận commit nào |
| 5 | `hop` tự rebase nhánh task lên nhánh tích hợp mới nhất trước khi merge | `scripts/tdq_team.py` | dựng 2 nhánh nối tiếp, merge cái 1 rồi `hop` cái 2 → thành công, không cần thao tác tay |
| 6 | Đường gỡ conflict: lệnh mới `go <task>` | `scripts/tdq_team.py` | conflict dựng sẵn → `go` in ra từng file kẹt kèm hai phía, và trạng thái sau khi gỡ |
| 7 | `phan-cong` phát hiện file nóng và cảnh báo | `scripts/tdq_team.py` | plan có 1 đường dẫn xuất hiện ở ≥ 2 `Chạm:` → in cảnh báo nêu đúng đường dẫn đó và số task |
| 8 | Luật đội hình cập nhật khớp code | `skills/tdq-build/references/team-mode.md` | mỗi đầu ra 1–7 có đúng một mục nói cách dùng |
| 9 | Luật viết plan: file nóng phải nâng lên đợt sớm | `skills/tdq-plan/references/plan-template.md` | mục mới nêu cách nhận diện và cách xử lý |
| 10 | Hợp đồng agent con nêu rõ kết quả sẽ bị kiểm lại | `agents/tdq-implementer.md` | có câu nói `TICK-READY` không còn là lời tự khai |
| 11 | Bộ test khoá cả 7 hành vi máy | một file test mới trong thư mục test của dự án | chạy một lệnh, mọi test xanh |
| 12 | Plan đầy đủ để user duyệt | `docs/tdq/plan/2026-09-03-1527-sub-agent-chong-conflict.md` | `doc_lint.py --pair <spec> <plan>` thoát 0 |
| 13 | Tên lệnh tiếng Anh cho mọi sub-command, tên cũ thành bí danh ẩn | `scripts/tdq_team.py`, `scripts/tdq_bench.py`, `scripts/tdq_eval.py`, `scripts/tdq_lsp.py`, `scripts/tdq_state.py` | gọi tên mới và gọi tên cũ đều chạy đúng cùng một hàm; `--help` chỉ liệt kê tên mới |
| 14 | Bảng đối chiếu tên cũ → tên mới, một nguồn sự thật | `skills/tdq-conventions/references/` | mỗi lệnh cũ có đúng một dòng, không thiếu lệnh nào |
| 15 | Tài liệu, hook, agent, bundle dùng tên mới | `skills/`, `hooks/`, `agents/`, 3 bundle portable | tìm tên cũ trong `skills/` + `hooks/` + `agents/` ra 0 lần, trừ đúng bảng đối chiếu |

## 2b. Ranh giới module

| Module | Vùng file | Phụ thuộc module | Đầu ra §2 nào |
|---|---|---|---|
| M1 lõi đội hình | `scripts/tdq_team.py` | không | 2, 3, 4, 5, 6, 7 |
| M2 cổng ghi | `hooks/scripts/edit_gate.py` | M1 (gọi hàm ở đầu ra 2) | 1 |
| M3 luật đội hình | `skills/tdq-build/references/team-mode.md`, `agents/tdq-implementer.md` | M1 | 8, 10 |
| M4 luật viết plan | `skills/tdq-plan/references/plan-template.md` | M1 | 9 |
| M5 test | một file test mới của riêng việc này, trong thư mục test của dự án | M1, M2 | 11 |
| M6 tên lệnh | lớp phân giải sub-command của 5 script CLI + bảng đối chiếu | không (chạy TRƯỚC M1) | 13, 14, 15 |

**Ghi chú tự soi:** M1 gom 6 đầu ra vào MỘT file. Đó chính là hiện tượng "file nóng" mà đầu ra 7
sinh ra để cảnh báo — `scripts/tdq_team.py` sẽ là file nóng của chính request này. Phase `plan`
phải xếp các task của M1 vào các đợt khác nhau, đúng luật `_dot_som_nhat` đang có.

## 3. Cách tiếp cận & lý do

- **Chọn:** nâng cấp tại chỗ bộ `tdq_team.py` + `edit_gate.py` đang chạy, theo bốn nguyên tắc rút
  từ nghiên cứu, mỗi nguyên tắc bịt đúng một lỗ hở:

  | Nguyên tắc | Bịt | Nguồn |
  |---|---|---|
  | Miền file không giao nhau phải được **cưỡng chế**, không chỉ khai báo | H1 | N1 — worktree không có cơ chế cảnh báo, phải tự phân miền trước |
  | **Rebase lên bản mới nhất rồi mới merge**, từng nhánh một | H2 | N2 — mẫu lock → rebase → merge |
  | File dùng chung tách thành **một bước riêng chạy trước** | H3 | N3, N4 — một người ghi duy nhất cho file nóng |
  | Kết quả phải **được kiểm trước khi gộp**, không tin lời tự khai | H5 | N5 — điều kiện để chạy êm là task độc lập VÀ kết quả được kiểm |
  | Tên lệnh **đọc là hiểu**, đổi có bí danh chứ không đổi gãy | dễ đọc | user yêu cầu trực tiếp ở bản 1.1 |

- **Đổi tên chạy TRƯỚC mọi việc khác** (bản 1.1): mọi hành vi máy mới ở đầu ra 1–11 và mọi câu
  tài liệu ở đầu ra 8–10 đều nhắc tên lệnh. Đổi tên sau nghĩa là viết một lần bằng tên cũ rồi
  sửa lại lần nữa — vừa tốn, vừa dễ sót.

- **Vì:**
  1. Hệ hiện có đã đúng hướng — nhánh riêng, worktree riêng, chia đợt theo file, dò conflict
     bằng `merge-tree`, `rerere`. Đập đi xây lại là vứt bỏ phần đã đúng.
  2. Cưỡng chế đặt ở **điểm ghi file** vì đó là chỗ duy nhất không lách được. Luật viết trong
     prompt giao việc (`VÙNG FILE: … CẤM sửa file ngoài danh sách này`) đã tồn tại, và conflict
     vẫn xảy ra — bằng chứng tại chỗ rằng lời dặn không thay được cổng chặn.
  3. H5 là lỗ hở nặng nhất theo `soul.md` (chất lượng đứng trên runtime): merge code chưa kiểm
     làm hỏng nhánh tích hợp, và cái giá phải trả rơi hết lên leader.

- **Đã loại:**
  - **Chuyển sang mô hình PR + CI ngoài máy** — vì vòng đời một request TDQ tính bằng phút, còn
    vòng PR tính bằng giờ; và nó buộc phải có mạng, trong khi `tdq_team.py` hiện chạy hoàn toàn
    cục bộ.
  - **Bỏ song song, ép mọi việc về mode `main`** — vì giết đúng lý do mode `subagent` tồn tại.
    Nguồn N5 cho thấy 5 nhánh song song chạy hàng tuần chỉ dưới 3 conflict khi task được phân rã
    đúng; vấn đề nằm ở phân rã và kiểm, không ở tính song song.
  - **Khoá file bằng lock file dùng chung giữa các worktree** — vì lock cần tiến trình còn sống
    để nhả; agent con chết giữa chừng là khoá kẹt vĩnh viễn. Chia đợt theo file đạt cùng mục tiêu
    mà không có trạng thái phải dọn.
  - **Đổi tên mà xoá luôn tên cũ** — vì tên cũ nằm rải trong `skills/`, `hooks/`, `agents/`, 3
    bundle portable và bộ test; xoá thẳng là một cú gãy lớn không cần thiết. Giữ bí danh ẩn
    (không hiện trong `--help`) cho chi phí gần bằng 0 mà an toàn.
  - **Cho agent con tự rebase** — vì nó không thấy nhánh tích hợp đã đi tới đâu, và hai agent
    cùng rebase một lúc là đúng cảnh chạy đua. Rebase phải do leader làm, tuần tự, lúc `hop`.

## 3b. Năng lực & công cụ

| Skill | Nguồn | Phán quyết | Dùng ở đâu / Lý do loại |
|---|---|---|---|
| tdq-intake | project | NỀN | skill khung đang chạy, sở hữu pha analyze |
| tdq-spec | project | NỀN | skill khung đang chạy, sở hữu pha spec |
| tdq-plan | project | NỀN | skill khung đang chạy, sẽ sở hữu pha plan |
| tdq-conventions | project | NỀN | luật gốc nạp cho mọi pha |
| tdq-build | project | DÙNG | đối tượng bị sửa: `references/team-mode.md`, đầu ra 8 |
| tdq-lsp-setup | project | DÙNG | luật thứ tự tìm kiếm khi đọc `tdq_team.py` ở pha plan |
| Đã xét 2 skill khác | project | KHÔNG | khác lĩnh vực |

## 4. Yêu cầu bắt buộc

- Log service bật mặc định: timestamp, đủ chi tiết debug, tắt/giảm được qua config. Việc này CÓ
  runtime — `tdq_team.py` và `edit_gate.py` đều là mã chạy được, và cả hai đã có sẵn `_log`.
- Không placeholder, không TODO stub, không mock trình bày như dữ liệu thật.
- Mỗi thành phần có unit test riêng, chạy được bằng một lệnh.
- Code viết ra bám 5 nguyên tắc SOLID theo `skills/tdq-conventions/references/clean-code.md`,
  và bám rule ngôn ngữ trong `skills/tdq-build/references/rules/`.

## 5. Ràng buộc & rủi ro

Ràng buộc kiến trúc phải giữ (chép từ `docs/kien-truc.md`, chỉ dòng việc này chạm tới):

- `hooks/` được gọi `scripts/`; `scripts/` **không** được import `hooks/` — việc này chạm ở
  `edit_gate.py` gọi hàm mới trong `tdq_team.py`, đúng chiều cho phép; cấm chiều ngược lại.
- `skills/` chỉ được **nhắc tên lệnh** của `scripts/`, cấm chép nội dung script vào skill —
  việc này chạm ở `team-mode.md` và `plan-template.md`.
- Chỉ `scripts/tdq_state.py` được ghi `docs/tdq/state.json` — việc này chạm ở chỗ `kiem`/`hop`
  đọc state; chỉ đọc, không ghi.
- File code MỚI bắt buộc nằm trong `scripts/` hoặc `hooks/` — việc này không tạo file code mới
  ngoài hai thư mục đó.
- 2026-07-29: hook chỉ nhắc và kiểm bằng hiệu ứng thật — cổng ở đầu ra 1 chặn dựa trên đường dẫn
  file THẬT sắp bị ghi, không dựa trên trạng thái duyệt, nên nằm trong luật.

| Rủi ro | Ảnh hưởng | Cách giảm |
|---|---|---|
| Cổng vùng file chặn nhầm việc chính đáng (agent con cần sửa file kề bên) | agent con kẹt, phải hỏi leader — đúng thứ ta đang muốn giảm | cổng in kèm đường thoát: nêu tên task, vùng cho phép, và câu "báo leader để mở rộng `Chạm:`" thay vì chỉ nói không |
| Chạy test lúc `kiem` làm chậm mỗi vòng merge | mất lợi thế tốc độ của mode song song | chỉ chạy ĐÚNG lệnh `Test:` của task, không chạy full suite; luật full-suite-một-lần ở pha QC giữ nguyên |
| Rebase tự động viết lại lịch sử nhánh task | mất dấu vết ai làm gì | nhánh task bị xoá sau merge dù sao; nhánh tích hợp dùng `--no-ff` nên vẫn thấy ranh giới từng task |
| Rebase gặp conflict giữa chừng để lại worktree dở dang | worktree bẩn, `soat` không dọn được | rebase thất bại thì `git rebase --abort` ngay, trả worktree về đúng trạng thái trước đó rồi mới báo lỗi |
| Lệnh `Test:` trong plan viết sai cú pháp hoặc không chạy được | `kiem` đỏ oan, chặn nhầm | phân biệt hai ca: lệnh không tồn tại → báo lỗi plan và nêu task; lệnh chạy nhưng đỏ → báo lỗi code |
| `tdq_team.py` là file nóng của chính request này | các task M1 đụng nhau | plan xếp task M1 vào các đợt khác nhau; chính `_dot_som_nhat` sẵn có làm việc đó |
| Đổi tên sót một chỗ trong hook hoặc bundle → lệnh gọi hỏng lúc chạy thật | mode `subagent` gãy giữa chừng | bí danh giữ tên cũ chạy được, nên chỗ sót vẫn chạy; và có hạng mục QC tìm tên cũ trên toàn repo |
| Bí danh ẩn khiến hai tên cùng tồn tại lâu dài, tài liệu trôi về tên cũ | quay lại đúng chỗ khó đọc | `--help` chỉ in tên mới; QC bắt `skills/`+`hooks/`+`agents/` không còn tên cũ |

## 6. QC & Definition of Done

| # | Hạng mục kiểm | Điều kiện PASS |
|---|---|---|
| Q1 | Cổng vùng file chặn ghi ngoài `Chạm:` | ghi từ trong worktree của một task ra file không nằm trong vùng của task đó bị từ chối, và thông báo nêu đủ ba thứ: mã task, vùng cho phép, đường thoát |
| Q2 | Cổng vùng file KHÔNG chặn ghi trong vùng | ghi vào một file thuộc vùng của task đó đi qua bình thường |
| Q3 | Cổng vùng file không đụng gì tới mode `main` | ở mode `main`, mọi ghi hợp lệ hôm nay vẫn hợp lệ |
| Q4 | `kiem` chạy thật lệnh kiểm của task | đầu ra của `kiem` nêu tên lệnh đã chạy và kết quả thật của nó |
| Q5 | `hop` chặn khi test của task đỏ | nhánh tích hợp không nhận thêm commit nào, và mã thoát khác 0 |
| Q6 | `hop` tự rebase khi base đã cũ | hai nhánh nối tiếp merge được liên tiếp mà không cần thao tác tay nào |
| Q7 | Rebase hỏng thì trả worktree về nguyên trạng | sau khi rebase thất bại, worktree sạch và ở đúng commit trước lúc rebase |
| Q8 | Lệnh gỡ conflict nêu đủ thông tin để gỡ | in ra từng file kẹt kèm nội dung hai phía |
| Q9 | `phan-cong` cảnh báo file nóng | plan có đường dẫn xuất hiện ở ≥ 2 `Chạm:` thì cảnh báo nêu đúng đường dẫn và số task chạm |
| Q10 | Ba file luật khớp code | mỗi hành vi máy mới có đúng một mục tài liệu mô tả cách dùng |
| Q11 | Không phá hành vi cũ | bộ test hiện có của đội hình không thêm ca đỏ nào |
| Q12 | Mốc đỏ toàn bộ không tăng | số ca đỏ của cả bộ test không vượt mốc ghi trong plan |
| Q13 | Tên lệnh mới chạy đúng | với mỗi sub-command của 5 script, gọi tên tiếng Anh cho ra đúng kết quả như tên cũ |
| Q14 | Bí danh cũ vẫn chạy | gọi mọi tên cũ đều không lỗi "unknown sub-command" |
| Q15 | Không còn tên cũ trong tài liệu | tìm tên cũ trong `skills/`, `hooks/`, `agents/` ra 0 lần, trừ bảng đối chiếu |

DoD:

- Đủ 15 đầu ra ở §2, mỗi đầu ra có ít nhất một hạng mục Q tương ứng ở §6.
- Q1–Q15 đều PASS, bằng chứng dán vào file QC.
- Bộ test mới chạy được bằng một lệnh và xanh hết.
- Số ca đỏ toàn bộ không vượt mốc đỏ ghi trong plan.
- `doc_lint.py` thoát 0 trên mọi `.md` đã sửa.
- Ba file luật (`team-mode.md`, `plan-template.md`, `agents/tdq-implementer.md`) không còn câu
  nào mô tả hành vi máy đã bị thay.
- Ràng buộc kiến trúc ở §5 giữ nguyên: không có chiều import `scripts/` → `hooks/`.

## 7. Câu hỏi còn mở

(rỗng)
