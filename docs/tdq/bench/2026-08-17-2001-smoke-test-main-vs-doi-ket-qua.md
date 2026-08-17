# KẾT QUẢ — mode `main` so với mode đội (subagent)

Soul: chất lượng > runtime > context cost · luật gốc: skills/tdq-conventions/references/soul.md

Request: `2026-08-17-2001-smoke-test-main-vs-doi` · ngày 2026-08-17.
Hằng số: `2026-08-17-2001-smoke-test-main-vs-doi-thuc-do.json`.
Mọi số dưới đây đo được hoặc tính từ số đo được. Chỗ nào là giả định thì ghi rõ.

## 1. Lượt chạy THẬT — chỗ nào bấm giờ, chỗ nào suy ra

Bài thi: repo git tạm, plan mẫu 3 task rời nhau, 3 agent `tdq-implementer` phát trong
MỘT lượt. Mỗi agent viết test trước, code sau, chạy `pytest`, rồi commit trong worktree
riêng của nó. **Chỉ mode đội thực sự chạy.** Mode main KHÔNG chạy lượt nào trên bài thi
này, nên mọi số của nó dưới đây là số suy ra, đánh dấu riêng.

Đo được — đồng hồ bấm trên lượt chạy đội:

| Chặng | Số đo |
|---|---|
| T1.1 (agent 1) | 133,753 giây |
| T1.2 (agent 2) | 141,045 giây |
| T1.3 (agent 3) | 91,682 giây |
| Task chậm nhất của đợt | 141,045 giây |
| Phát đợt (`phan-cong` + `kiem-ke` + `cum` + 3 lần `mo`) | 0,405 giây |
| Dò xung đột (`kiem` × 3) | 0,291 giây |
| Hợp nhánh (`hop` × 3) | 0,513 giây |
| Dọn (`don`) | 0,107 giây |
| **Mode đội — treo tường cả đợt** | **142,4 giây ≈ 2,4 phút** |

Suy ra — số của mode main, tính chứ không đo:

| Đại lượng | Giá trị | Suy ra thế nào |
|---|---|---|
| Tổng ba task | 366,480 giây | cộng ba số bấm giờ ở bảng trên |
| Mode main trên cùng khối việc | 366,5 giây ≈ 6,1 phút | tổng ba task, **giả định leader làm mỗi task đúng bằng thời gian agent con làm** |
| Tỉ số đội so với main | 2,57 lần | 366,5 chia 142,4 |

Giả định gạch chân ở trên là chỗ yếu nhất của con số 2,57. Nó ứng với `he_so_agent = 1`
ở mục 5. Leader làm trong ngữ cảnh sẵn có thường nhanh hơn agent con phải đọc lại từ
đầu; agent con chậm hơn bao nhiêu thì tỉ số này rơi đúng bấy nhiêu. Ba nhánh hợp vào
nhánh tích hợp sạch, không một xung đột. Chạy `pytest` trên nhánh tích hợp: 9 test xanh.

Ghi chú đọc số: `t_task` là thời gian treo tường của agent con tính từ lúc leader phát
việc tới lúc nhận báo cáo. Nó đã gồm cả phần khởi động agent. Thời gian agent tự bấm
giờ bên trong nhỏ hơn (63–133 giây), chênh 8–28 giây mỗi agent.

## 2. Bảng chất lượng — 6 chỉ số, cả hai mode

| Chỉ số | mode `main` | mode đội |
|---|---|---|
| Test pass | 874 test của repo xanh, 0 đỏ (868 trước vòng fix 1) | 9/9 test do 3 agent viết xanh trên nhánh tích hợp |
| `doc_lint` | exit 0 trên mọi file sửa, kể cả cặp spec-plan | exit 0 trên plan mẫu do `dung-plan` sinh |
| Số lần merge xung đột | 0 (không mở nhánh nào) | 0/3 nhánh — `kiem` báo sạch cả ba |
| Số task phải làm lại | 0/15 task | 0/3 task |
| Số defect QC độc lập bắt | 8 defect (agent QC chấm 15 task làm ở mode main) | 2 defect (lượt chạy đội, mục 3) |
| Tỉ lệ giao/tổng | 0/15 = 0% | 3/3 = 100% |

## 3. Hai defect mà chỉ lượt chạy THẬT mới lộ ra

1. **`kiem` chết bằng `UnicodeDecodeError`.** `git merge-tree` in cả nội dung object ra
   stdout. Gặp file văn bản không giải mã được bằng UTF-8 là cả lệnh văng traceback,
   không phải báo lỗi. Đã vá: `_git` đọc output với `errors="replace"`. Test khoá lại:
   `test_kiem_khong_chet_khi_git_in_byte_khong_phai_utf8`.
2. **Hook `edit_gate` chặn agent con sửa file trong repo khác.** Cả ba agent bị `TDQ:TICK`
   chặn Edit/Write vì hook đọc state của repo TDQWorkflow thật, không phải repo tạm nơi
   chúng đang làm. Chúng tự vòng qua bằng cách ghi file qua shell. Việc vẫn xong, nhưng
   đó là phí phải trả và là một cửa lách luật có thật. Chưa vá trong request này.

Đây chính là giá trị của lượt chạy thật: 839 test của mode đội không bắt được cả hai.

## 4. Mô phỏng — điểm hoà nằm ở đâu

Quét plan 12 task, thay đổi tỉ lệ task tách được (task khai vùng file riêng, không đụng
task khác). Hằng số lấy từ file thực đo.

| Tách được | Số đợt | T_main (phút) | T_đội (phút) | Thắng |
|---|---|---|---|---|
| 0% | 12 | 24,4 | 24,6 | main |
| 10% | 11 | 24,4 | 22,5 | đội |
| 30% | 8 | 24,4 | 16,4 | đội |
| 50% | 6 | 24,4 | 12,3 | đội |
| 70% | 4 | 24,4 | 8,2 | đội |
| 100% | 1 | 24,4 | 2,1 | đội |

Ca biên: 6 task cùng đụng một file → 6 đợt, T_main 12,2 phút, T_đội 12,3 phút. Mode đội
thua. Đúng như dự đoán: plan không tách được thì mỗi đợt chỉ có một task, phí đợt trả
đủ mà không mua được gì.

Chính plan của request này: 15 task, 13 giao được, nhưng 11 đợt vì 9 task cùng đụng
`scripts/tdq_bench.py`. Mô hình cho 30,5 phút (main) so với 22,5 phút (đội).

## 5. Công thức có thiên vị mode đội không

Có, ba chỗ — nêu ra để người đọc trừ hao, không giấu:

1. **`t_phat` chỉ đo phần cơ học** (0,45 giây cho lệnh `cum` và `mo`). Nó KHÔNG gồm thời
   gian leader viết prompt cho từng agent. Đó là phần đắt nhất của việc phát đợt.
2. **Công thức không tính `t_tick` cho mode đội** dù leader vẫn phải tick từng task ở cả
   hai mode. Đo được `t_tick` ≈ 0,0001 giây nên chỗ lệch này không đổi kết luận.
3. **Giả định `t_task` bằng nhau ở hai mode.** Leader làm trong ngữ cảnh sẵn có có thể
   nhanh hơn agent con phải đọc lại từ đầu.

Độ nhạy theo `t_phat` — ngưỡng tỉ lệ tách được mà từ đó mode đội bắt đầu thắng:

| `t_phat` | 0,45 giây (đo) | 15 giây | 30 giây | 60 giây | 120 giây | 300 giây |
|---|---|---|---|---|---|---|
| Ngưỡng | 10% | 20% | 30% | 30% | 50% | 80% |

Đọc bảng này: kể cả khi phát một đợt tốn 2 phút của leader, plan có một nửa số task tách
được là mode đội vẫn thắng. Chỉ khi phát đợt tốn tới 5 phút thì ngưỡng mới lên 80%.

Độ nhạy theo `he_so_agent` — agent con chậm hơn leader bao nhiêu lần. Đây là trục quan
trọng hơn `t_phat`, và là chỗ con số 10% ở trên mỏng nhất:

| `he_so_agent` | 1 (giả định) | 1,25 | 1,5 | 2 | 3 |
|---|---|---|---|---|---|
| Ngưỡng tách được | 10% | 30% | 40% | 60% | 80% |

Lệnh sinh bảng: `python3 scripts/tdq_bench.py quet --thuc-do <file> --task 12 --buoc 10
--he-so-agent <K>`. Đọc bảng này: nếu agent con chậm gấp rưỡi leader — con số dễ tin
hơn giả định bằng nhau — thì phải có 40% số task tách được mode đội mới hoàn vốn.

## Kết luận

**nhanh hơn: mode đội**, nhưng có điều kiện, và điều kiện đo được.

- Đo thật trên 3 task rời nhau: đội **2,4 phút** (bấm giờ). Main trên cùng khối việc:
  **6,1 phút** — số này SUY RA từ tổng ba task, không phải lượt chạy thật, và đứng trên
  giả định leader làm nhanh ngang agent con. Tỉ số 2,57 lần chỉ đúng dưới giả định đó.
- Mô phỏng 12 task: đội thắng khi **từ 10% số task trở lên tách được** — nhưng đó vẫn là
  con số của `he_so_agent = 1`. Agent con chậm gấp rưỡi thì ngưỡng lên **40%**, gấp đôi
  thì **60%**. Trừ hao thêm `t_phat` tới 2 phút thì ngưỡng của `he_so_agent = 1` là 50%.
- Con số đáng dùng để quyết định là **30–60%**, không phải 10%: nó là dải ngưỡng khi
  `he_so_agent` nằm trong 1,25–2, khoảng thực tế nhất.
- Đội THUA khi plan không tách được: 6 task cùng một file → 12,3 phút so với 12,2 phút.
  Ngưỡng an toàn để chọn `main`: **số đợt xấp xỉ số task**, tức gần như không song song
  được gì.

**chất lượng: hoà về kết quả, đội hơn về khả năng phát hiện lỗi.**

- Test pass: 874/874 (main) so với 9/9 (đội) — cả hai không có test đỏ.
- Merge xung đột: 0 lần ở cả hai mode. Task phải làm lại: 0 ở cả hai.
- Chênh lệch thật nằm ở chỗ khác: lượt chạy đội bắt được **2 defect** mà 839 test của
  chính mode đội không bắt được. Ba agent chạy song song trên ba worktree là một phép
  thử khắc nghiệt hơn mọi unit test đã viết.
- Cái giá: mode đội cần plan khai `Chạm:` đầy đủ. Thiếu dòng đó thì task rơi vào
  `vung-khoa`, leader phải tự làm, và mọi lợi thế tốc độ biến mất.

**Khuyến nghị dùng:** plan trên 6 task mà **quá 40% số task đụng file rời nhau** thì chọn
mode đội — lấy mốc 40% chứ không lấy 10%, vì 40% là ngưỡng khi agent con chậm gấp rưỡi
leader, giả định an toàn hơn giả định hai bên nhanh bằng nhau. Plan mà phần lớn task cùng
sửa một mô-đun thì chọn `main` — như chính plan của request này, nơi 9 trong 15 task cùng
đụng một file.
