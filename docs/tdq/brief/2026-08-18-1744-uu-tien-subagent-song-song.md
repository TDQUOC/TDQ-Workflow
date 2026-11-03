# BRIEF — Luôn tổ chức modular, luôn ưu tiên sub-agent chạy song song

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

## Nguyên văn

> tôi muốn mở request để phân tích bộ workflow và lên phương án cho việc sau: tôi muốn là
> dù ở mode main hoặc subagent thì claude code luôn luôn tổ chức spec/plan theo dạng
> modular để mà luôn cố gắng để tạo sub-agent implement và ở mọi khi có thể dùng sub-agent
> thì claude code như là một leader giàu kinh nghiệm, chia task cho các sub-agent implement
> nhiều nhánh song song nhất có thể để giảm time implement và cố gắng có chất lượng output
> tốt nhất có thể. Hãy deep sreach để lên bộ rule, phương án để patch vào workflow để dù ở
> quick hay full thì claude code luôn cố gắng tổ chức và ưu tiên sub-agent paralel implement

### Cách hiểu đầu tiên

Mục tiêu: dời "chia việc song song" từ một LỰA CHỌN của user (mode `subagent`) thành
MẶC ĐỊNH của cả bộ workflow. Hai vế:

1. **Modular hoá spec/plan luôn luôn** — spec và plan phải được viết sao cho task tách rời
   được theo vùng file, kể cả khi cuối cùng chạy ở mode `main`. Tức tính modular là thuộc
   tính của TÀI LIỆU, không phải của mode thực thi.
2. **Ưu tiên giao và chạy song song** — ở mọi chỗ dùng được sub-agent thì dùng, main agent
   đóng vai leader chia nhiều nhánh song song nhất có thể, mục tiêu kép: giảm thời gian
   implement VÀ tăng chất lượng output.

Phạm vi mở rộng user nêu rõ: áp cho **cả lane quick lẫn full**.

### Hiện trạng đã có (không phải làm lại)

| Đã có | Nằm ở đâu | Giới hạn hiện tại |
|---|---|---|
| Mode đội: leader phân công cả plan, bảng tra 4 nhóm được giữ task lại | `skills/tdq-build/references/team-mode.md` (115 dòng) | Chỉ chạy khi `implement_mode = subagent`; mode `main` bỏ qua toàn bộ file |
| Bản đồ phân công + hàng rào chống lách luật | `scripts/tdq_team.py` (`phan-cong`, `kiem-ke`), hook `[TDQ:TEAM]` | Chỉ dựng khi vào mode đội |
| Khuôn `## Cụm song song` và dòng `Chạm:` trong plan | `skills/tdq-plan/references/plan-template.md` | Có khuôn nhưng chưa có luật BẮT BUỘC tách modular ở mọi lane |
| Agent thực thi | `tdq-implementer` | — |
| Số đo main vs đội | request `2026-08-17-2001-smoke-test-main-vs-doi` | Cần đọc lại để biết đội có thật sự nhanh hơn không, và nhanh bao nhiêu |

Nói cách khác: bộ máy chia việc đã dựng xong ở 0.25.0. Việc của request này là đổi
**chính sách mặc định** và đẩy tính modular ngược lên phase spec/plan, cộng lane quick.

### Chỗ chưa rõ — phải hỏi user, không tự quyết

1. Cổng hỏi mode (main | subagent) lúc duyệt plan: GIỮ (đổi đề xuất mặc định sang đội)
   hay BỎ HẲN (luôn chạy đội, main chỉ còn là ngoại lệ có lý do)?
2. Lane quick vốn là "rút gọn, một turn": có được phép sinh agent con không, hay chỉ bắt
   buộc viết mini-plan theo dạng modular còn vẫn chạy inline?
3. Trần song song: chạy tối đa mấy nhánh cùng lúc? Có ngưỡng nào để không giao (task quá
   nhỏ thì chi phí dựng worktree + brief cho agent lớn hơn phần tiết kiệm)?

## Hiểu & kiến thức

### Năng lực dùng được

| Năng lực | Nguồn | Dùng vào việc gì của request này |
|---|---|---|
| Agent `tdq-implementer` + worktree cô lập | plugin tdq-workflow | Nhánh song song thật sự ghi file |
| `scripts/tdq_team.py` (`phan-cong`, `cum`, `mo`, `kiem`, `hop`, `don`) | repo | Bản đồ phân công, chia đợt, kiểm merge |
| `scripts/tdq_bench.py quet` | repo | Tính lại ngưỡng hoà vốn khi đổi chính sách |
| Hook `[TDQ:TEAM]`, `[TDQ:TICK]` | `hooks/scripts/` | Chặn lách luật khi leader tự làm quá phần |
| `doc_lint.py --pair spec plan` | repo | Ép khuôn mới của spec/plan sau khi patch |
| `tavily-primary` | MCP | Đã dùng ở bước research |

### Số đo đã có trong repo — đọc kỹ trước khi chốt chính sách

Nguồn: `docs/tdq/reports/2026-08-17-2001-smoke-test-main-vs-doi.md` và file bench cùng slug.

- Đo thật 3 task rời nhau: mode đội **2,4 phút**. Mode main **6,1 phút** là số SUY RA, không phải lượt chạy thật.
- Mô phỏng 12 task: đội thắng từ **10%** số task tách được, nhưng chỉ khi agent con nhanh ngang leader.
- Agent con chậm gấp rưỡi thì ngưỡng lên **40%**; chậm gấp đôi thì **60%**. Dải nên dùng để quyết định là **30–60%**.
- Ca biên: 6 task cùng đụng một file thì đội **THUA** — 12,3 phút so với 12,2 phút.
- Chất lượng: hoà về kết quả (0 xung đột, 0 làm lại ở cả hai mode). Đội hơn ở chỗ lộ ra 2 lỗi mà 839 test không bắt được.
- Lỗi còn treo: hook `edit_gate` chặn agent con sửa file trong repo tạm. Agent phải lách qua shell.

### Research ngoài — nguồn đầy đủ ở `docs/tdq/research/2026-08-18-1744-uu-tien-subagent-song-song.md`

1. Song song chỉ thắng khi task không chạm chung file và nằm trên nhánh độc lập của critical path.
2. Cùng ngân sách token, single agent bằng hoặc thắng multi-agent trên suy luận nhiều bước.
3. Multi-agent tốn trung bình khoảng **4 lần** token so với single agent trong ca đo thực tế.
4. Số điểm lỗi phối hợp tăng nhanh theo số agent: 4 agent là 6 điểm, 10 agent là 45 điểm.
5. Không chia quyền sở hữu file rõ ràng thì các agent song song ghi đè lẫn nhau và mất việc thật.
6. Chỉ bật worktree cho agent THẬT SỰ ghi file; agent chỉ đọc mà dựng worktree là phí.
7. Context drift qua nhiều lần bàn giao là nguyên nhân gốc phổ biến nhất của lỗi multi-agent.
8. Nên chia theo dependency graph, tách riêng file dùng chung để không kéo dài critical path.

### Khoảng trống đã đo được trong workflow

| Chỗ | Bằng chứng | Thiếu gì |
|---|---|---|
| `skills/tdq-intake/references/quick-lane.md` | `grep -n "subagent\|agent\|song song"` ra 0 dòng | Lane quick không có đường song song nào |
| `skills/tdq-spec/references/spec-template.md` | `grep -n "modul\|song song\|Chạm\|vùng file"` ra 0 dòng | Spec chưa có khái niệm ranh giới module |
| `skills/tdq-build/references/team-mode.md` | Dòng `Khi nào áp dụng` | Cả file bị khoá sau `implement_mode = subagent` |
| `skills/tdq-plan/SKILL.md` bước 1 | Luật "trên 6 task đụng file rời nhau" | Đếm số task thô, không dùng tỉ lệ tách được |

### Căng thẳng phải giải, không được lờ đi

Yêu cầu là "luôn ưu tiên song song". Số đo nói song song chỉ hoà vốn khi đủ tỉ lệ task tách
được. Nghiên cứu ngoài nói thêm agent làm tăng token và tăng điểm lỗi phối hợp. Hai vế của
yêu cầu vì thế tách ra: vế **modular hoá tài liệu** không có mặt trái nào đo được, nên áp
vô điều kiện. Vế **chạy song song** có mặt trái đo được, nên cần ngưỡng.

### Phạm vi đã chốt

- Mặt chất lượng: Đúng đắn, Bảo trì được, Hiệu năng.
- Bối cảnh: plan điển hình từ 10 task trở lên.
- Mức đầu tư: **đầy đủ** — ba mặt cùng lúc, quy mô plan lớn, luật đụng cả bốn skill.
- Ưu tiên riêng user nhấn: phân tích để tối ưu runtime của phase implement.

### Lộ trình

| # | Việc | Chạm gì | Vì sao cần |
|---|---|---|---|
| 1 | Thêm mục ranh giới module vào khuôn spec | `skills/tdq-spec/references/spec-template.md` | Plan chỉ tách được nếu spec đã nêu ranh giới |
| 2 | Ép plan luôn khai `Chạm:` và luôn dựng `## Cụm song song` | `skills/tdq-plan/references/plan-template.md` | Modular là thuộc tính tài liệu, không phụ thuộc mode |
| 3 | Đổi luật đề xuất mode sang tỉ lệ tách được | `skills/tdq-plan/SKILL.md` | Đếm task thô không phản ánh ngưỡng hoà vốn đã đo |
| 4 | Nối cổng đề xuất mode vào `tdq_bench.py mo-phong --plan <file>` | `skills/tdq-plan/SKILL.md` | Lệnh đã tính sẵn số đợt và bên thắng; viết lệnh mới là chép luật |
| 5 | Gỡ khoá `team-mode.md` khỏi điều kiện `implement_mode = subagent` | `skills/tdq-build/references/team-mode.md` | Leader doctrine cần áp cả khi chạy main |
| 6 | Cho lane quick sinh agent con khi mini-plan có từ 3 task tách rời | `skills/tdq-intake/references/quick-lane.md` | Lane quick hiện không có đường song song nào |
| 7 | Trần 4 nhánh một đợt, ghi thành luật kiểm được | `scripts/tdq_team.py` + `team-mode.md` | Trên 4 agent thì điểm lỗi phối hợp tăng nhanh |
| 8 | Test khoá hình dạng luật mới | `tests/` | Luật không có test thì trôi mất sau vài request |

## Hỏi đáp

**Vòng 1 — scope (2026-08-18)**

1. Mặt chất lượng: user chọn **A, B, C** — đúng đắn, bảo trì được, hiệu năng.
2. Quy mô plan: **từ 10 task trở lên**.
3. Cổng hỏi mode: **A** — giữ cổng, đảo mặc định sang đội, đề xuất tính bằng tỉ lệ tách được. User nhấn thêm: ưu tiên phân tích để tối ưu runtime implement.
4. Lane quick: **A** — được sinh agent con khi mini-plan có từ 3 task tách rời trở lên.
5. Trần song song: **A** — tối đa 4 nhánh một đợt.
6. Token: **A** — chấp nhận tốn khoảng 4 lần token, đúng thứ tự soul.

**Vòng 2 — chi tiết (2026-08-18)**

Phát hiện khi đọc code: `scripts/tdq_bench.py mo-phong --plan <file>` đã đọc plan thật, đếm
số đợt, tính T_main và T_đội, in ra bên thắng. Không cần viết lệnh mới cho cổng đề xuất mode.

7. Cổng đề xuất mode gọi thẳng `tdq_bench.py mo-phong`: **A** — không viết lệnh thứ hai, tránh chép luật chia đợt ra hai chỗ.
8. Lỗi `edit_gate` chặn agent con trong repo tạm: **A** — vá luôn trong request này.
9. Nghĩa của mode `main` sau khi gỡ khoá: **A** — leader tự làm hết nhưng theo đúng thứ tự cụm, ghi lý do giữ từng task.

**Kiểm cổng analyze**

- Đủ hiểu để viết spec: đúng. Chín câu đã chốt, không còn chỗ đoán.
- Còn câu hỏi nào đổi kết quả: không.
- Nguồn cho mọi khẳng định: file research và file bench trong repo, đã dẫn ở trên.
