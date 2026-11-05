# Báo cáo — Eval theo yêu cầu, không tự bật {#tong-quan}

@meta locale=vi

Gate eval chỉ bật khi người dùng yêu cầu và đồng ý. Bản HTML này minh họa luồng; kết quả test lấy từ receipt full fresh và vùng chạm, không phải kết quả thử nghiệm hiệu quả model.

## 1. Trước request: eval tự chặn {#truoc}

@workflow id=luong-truoc title="Trước: đổi skill thì eval tự chặn"
| plan | Plan chạm skill/hook/plugin | backend |
| gate | Gate implement/report tự chạy | security |
| ket | Thiếu plan/chứng cứ: bị chặn | backend |
| mien | Cần eval-waive để miễn | frontend |
| plan > gate | tự động |
| gate > ket | không có eval-plan |
| ket > mien | muốn tiếp tục |

Mã cũ buộc eval-plan hoặc miễn thủ công dù người dùng không yêu cầu eval.

## 2. Sau request: người dùng bật mới kiểm {#sau}

@workflow id=luong-sau title="Sau: chỉ kiểm khi đã đồng ý"
| yeu | Người dùng yêu cầu và đồng ý | frontend |
| bat | eval-enable ghi by + at | backend |
| gate2 | Gate implement/report chạy như cũ | security |
| tat | Chưa bật: không chặn phase | backend |
| yeu > bat | xác nhận |
| bat > gate2 | đã kích hoạt |
| tat > gate2 | mặc định |

`eval-waive` bị bỏ; state cũ có `eval_waiver` vẫn đọc nhưng không miễn gate. Không thêm phụ thuộc, không đổi CI hoặc bộ kiểm hợp đồng eval.

## 3. Đã test gì? {#kiem}

| Phép kiểm | Mục tiêu |
|---|---|
| 10 test gate | Chưa bật: qua implement/report; đã bật: thiếu plan/chứng cứ thì chặn; lệnh cũ bị bỏ; state cũ vẫn đọc |
| Vùng chạm 2.070 case ID | Hồi quy phần nguồn/luật có liên quan, gồm test luật và chỉ mục |
| Full fresh 4.175 case ID | Kiểm toàn repo trên nguồn ổn định; không dùng lại kết quả cũ |

## 4. Kết quả test {#ket-qua}

**Gate: 10/10 đạt.** Vùng chạm: **2.068 đạt, 2 bỏ qua**, 1.150 subtests đạt; receipt complete. Full fresh: **4.168 đạt, 7 bỏ qua**, 2.724 subtests đạt/788,96 giây; receipt complete, nguồn trước/sau trùng. Không cộng subtests vào 4.175 case ID.

Một lượt vùng chạm trước đó FAIL do `qc.md` vượt ngân sách token và nguồn thay đổi trong lúc chạy; đã sửa rồi chạy lại PASS. Eval hiệu quả model **chưa kích hoạt (opt-in)**, 0 model trials; không gọi full pytest là chứng cứ hiệu quả model. Bán kính test chưa đầy đủ (`radius_complete=false`), dù sổ ghi `bo_sot=0`.
